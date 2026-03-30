from __future__ import annotations

import math
import torch
from torch import nn

from v5vc.offline_mvp.model import frame_waveform
from v5vc.streaming_student.pitch_provider import (
    DEFAULT_STAGE3_PITCH_PROVIDER_MODE,
    normalize_stage3_pitch_provider_mode,
    probability_to_logits,
)


DEFAULT_STREAMING_STUDENT_F0_FLOOR_HZ = 50.0
DEFAULT_STREAMING_STUDENT_F0_CEIL_HZ = 550.0


class UnifiedStreamingFrontend(nn.Module):
    def __init__(
        self,
        shared_dim: int,
        frontend_dim: int,
        frontend_layers: int,
        frame_length: int,
        hop_length: int,
        event_prior_dim: int,
        teacher_hidden_projection_dim: int,
        timing_aux_enabled: bool = False,
        named_control_branch_mode: str = "shared_hidden_v1",
        named_control_branch_layers: int | None = None,
        f0_parameterization_mode: str = "unbounded_log_v1",
        f0_floor_hz: float = DEFAULT_STREAMING_STUDENT_F0_FLOOR_HZ,
        f0_ceil_hz: float = DEFAULT_STREAMING_STUDENT_F0_CEIL_HZ,
        pitch_provider_mode: str = DEFAULT_STAGE3_PITCH_PROVIDER_MODE,
    ) -> None:
        super().__init__()
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.timing_aux_enabled = bool(timing_aux_enabled)
        self.named_control_branch_mode = str(named_control_branch_mode).strip().lower()
        if self.named_control_branch_mode not in {"shared_hidden_v1", "parallel_control_encoder_v1"}:
            raise ValueError(
                "named_control_branch_mode must be one of: "
                "shared_hidden_v1, parallel_control_encoder_v1."
            )
        self.f0_parameterization_mode = str(f0_parameterization_mode).strip().lower()
        if self.f0_parameterization_mode not in {"unbounded_log_v1", "bounded_log2_hz_v1"}:
            raise ValueError(
                "f0_parameterization_mode must be one of: "
                "unbounded_log_v1, bounded_log2_hz_v1."
            )
        self.f0_floor_hz = max(float(f0_floor_hz), 1.0)
        self.f0_ceil_hz = max(float(f0_ceil_hz), self.f0_floor_hz + 1.0)
        self.f0_log2_floor = math.log2(self.f0_floor_hz)
        self.f0_log2_ceil = math.log2(self.f0_ceil_hz)
        self.pitch_provider_mode = normalize_stage3_pitch_provider_mode(pitch_provider_mode)
        self.pitch_provider_confidence_enabled = self.pitch_provider_mode == "rmvpe_split_confidence_v1"
        self.input_proj = nn.Linear(2, frontend_dim)
        self.input_norm = nn.LayerNorm(frontend_dim)
        self.encoder = build_mlp(
            input_dim=frontend_dim,
            hidden_dim=frontend_dim,
            output_dim=shared_dim,
            num_layers=frontend_layers,
        )
        resolved_named_control_branch_layers = (
            frontend_layers
            if named_control_branch_layers is None
            else max(1, int(named_control_branch_layers))
        )
        self.control_encoder = (
            build_mlp(
                input_dim=frontend_dim,
                hidden_dim=frontend_dim,
                output_dim=shared_dim,
                num_layers=resolved_named_control_branch_layers,
            )
            if self.named_control_branch_mode == "parallel_control_encoder_v1"
            else None
        )
        self.log_f0_head = nn.Linear(shared_dim, 1)
        self.vuv_head = nn.Linear(shared_dim, 1)
        self.aper_head = nn.Linear(shared_dim, 1)
        self.energy_head = nn.Linear(shared_dim, 1)
        self.event_prior_head = nn.Linear(shared_dim, event_prior_dim)
        self.teacher_hidden_projection_head = nn.Linear(shared_dim, teacher_hidden_projection_dim)
        self.timing_pause_boundary_head = (
            nn.Linear(shared_dim, 1) if self.timing_aux_enabled else None
        )
        self.timing_terminal_boundary_head = (
            nn.Linear(shared_dim, 1) if self.timing_aux_enabled else None
        )
        self.timing_final_clause_head = (
            nn.Linear(shared_dim, 1) if self.timing_aux_enabled else None
        )

    def forward(
        self,
        waveform: torch.Tensor,
        lengths: torch.Tensor,
        pitch_provider_log2_f0: torch.Tensor | None = None,
        pitch_provider_vuv: torch.Tensor | None = None,
        pitch_provider_confidence: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        frames, frame_mask = frame_waveform(
            waveform=waveform,
            lengths=lengths,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
        )
        hidden = self.input_norm(self.input_proj(frames))
        shared_hidden = self.encoder(hidden)
        control_hidden = (
            self.control_encoder(hidden)
            if self.control_encoder is not None
            else shared_hidden
        )
        raw_coarse_log_f0 = self.log_f0_head(control_hidden)
        if self.f0_parameterization_mode == "bounded_log2_hz_v1":
            coarse_log_f0 = (
                self.f0_log2_floor
                + torch.sigmoid(raw_coarse_log_f0) * (self.f0_log2_ceil - self.f0_log2_floor)
            )
        else:
            coarse_log_f0 = raw_coarse_log_f0
        vuv_logits = self.vuv_head(control_hidden)
        explicit_pitch_provider_log2_f0 = None
        explicit_pitch_provider_vuv = None
        explicit_pitch_provider_confidence = None
        if self.pitch_provider_mode != DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
            if isinstance(pitch_provider_log2_f0, torch.Tensor):
                explicit_pitch_provider_log2_f0 = pitch_provider_log2_f0.to(
                    device=control_hidden.device,
                    dtype=control_hidden.dtype,
                )
                coarse_log_f0 = explicit_pitch_provider_log2_f0
                raw_coarse_log_f0 = explicit_pitch_provider_log2_f0
            if isinstance(pitch_provider_vuv, torch.Tensor):
                explicit_pitch_provider_vuv = pitch_provider_vuv.to(
                    device=control_hidden.device,
                    dtype=control_hidden.dtype,
                )
                vuv_logits = probability_to_logits(explicit_pitch_provider_vuv).to(
                    device=control_hidden.device,
                    dtype=control_hidden.dtype,
                )
            if isinstance(pitch_provider_confidence, torch.Tensor):
                explicit_pitch_provider_confidence = pitch_provider_confidence.to(
                    device=control_hidden.device,
                    dtype=control_hidden.dtype,
                )
        outputs = {
            "frame_mask": frame_mask,
            "frame_features": frames,
            "shared_hidden": shared_hidden,
            "control_hidden": control_hidden,
            "coarse_log_f0": coarse_log_f0,
            "raw_coarse_log_f0": raw_coarse_log_f0,
            "vuv_logits": vuv_logits,
            "aperiodicity": self.aper_head(control_hidden),
            "energy": self.energy_head(control_hidden),
            "event_prior_logits": self.event_prior_head(shared_hidden),
            "teacher_hidden_projection": self.teacher_hidden_projection_head(shared_hidden),
        }
        if explicit_pitch_provider_log2_f0 is not None:
            outputs["pitch_provider_log2_f0"] = explicit_pitch_provider_log2_f0
        if explicit_pitch_provider_vuv is not None:
            outputs["pitch_provider_vuv"] = explicit_pitch_provider_vuv
        if explicit_pitch_provider_confidence is not None:
            outputs["pitch_provider_confidence"] = explicit_pitch_provider_confidence
        if self.timing_pause_boundary_head is None:
            zero_aux = shared_hidden.new_zeros((shared_hidden.shape[0], shared_hidden.shape[1], 0))
            outputs["timing_pause_boundary_logits"] = zero_aux
            outputs["timing_terminal_boundary_logits"] = zero_aux
            outputs["timing_final_clause_logits"] = zero_aux
        else:
            outputs["timing_pause_boundary_logits"] = self.timing_pause_boundary_head(shared_hidden)
            outputs["timing_terminal_boundary_logits"] = self.timing_terminal_boundary_head(shared_hidden)
            outputs["timing_final_clause_logits"] = self.timing_final_clause_head(shared_hidden)
        return outputs


class StudentControlHeads(nn.Module):
    def __init__(
        self,
        shared_dim: int,
        event_prior_dim: int,
        student_dim: int,
        student_layers: int,
        z_art_dim: int,
        event_dim: int,
        speaker_embed_dim: int,
        geom_embed_dim: int,
        conditioning_dim: int,
        teacher_fused_hidden_projection_dim: int,
        r_res_dim: int,
        r_res_enabled: bool,
        f0_correction_enabled: bool,
        aper_correction_enabled: bool,
        detach_frontend_named_controls_for_student: bool,
        detach_shared_hidden_for_student: bool,
        f0_control_branch_mode: str,
        f0_control_branch_layers: int | None,
        energy_control_branch_mode: str,
        energy_control_branch_layers: int | None,
        energy_control_branch_hidden_dim: int | None,
        f0_correction_parameterization_mode: str,
        f0_correction_limit_log2: float,
        pitch_provider_confidence_enabled: bool,
        provider_confidence_gate_mode: str,
    ) -> None:
        super().__init__()
        self.r_res_enabled = r_res_enabled
        self.f0_correction_enabled = f0_correction_enabled
        self.aper_correction_enabled = aper_correction_enabled
        self.detach_frontend_named_controls_for_student = bool(
            detach_frontend_named_controls_for_student
        )
        self.detach_shared_hidden_for_student = bool(detach_shared_hidden_for_student)
        self.f0_control_branch_mode = str(f0_control_branch_mode).strip().lower()
        if self.f0_control_branch_mode not in {
            "shared_student_v1",
            "explicit_state_branch_v1",
            "explicit_named_control_family_v1",
        }:
            raise ValueError(
                "f0_control_branch_mode must be one of: "
                "shared_student_v1, explicit_state_branch_v1, explicit_named_control_family_v1."
            )
        self.energy_control_branch_mode = str(energy_control_branch_mode).strip().lower()
        if self.energy_control_branch_mode not in {
            "shared_f0_branch_v1",
            "dedicated_energy_branch_v1",
        }:
            raise ValueError(
                "energy_control_branch_mode must be one of: "
                "shared_f0_branch_v1, dedicated_energy_branch_v1."
            )
        if (
            self.energy_control_branch_mode != "shared_f0_branch_v1"
            and self.f0_control_branch_mode != "explicit_named_control_family_v1"
        ):
            raise ValueError(
                "dedicated_energy_branch_v1 requires "
                "f0_control_branch_mode=explicit_named_control_family_v1."
            )
        self.f0_correction_parameterization_mode = str(
            f0_correction_parameterization_mode
        ).strip().lower()
        if self.f0_correction_parameterization_mode not in {
            "linear_unbounded_v1",
            "bounded_tanh_log2_delta_v1",
        }:
            raise ValueError(
                "f0_correction_parameterization_mode must be one of: "
                "linear_unbounded_v1, bounded_tanh_log2_delta_v1."
            )
        self.f0_correction_limit_log2 = max(float(f0_correction_limit_log2), 1.0e-3)
        self.pitch_provider_confidence_enabled = bool(pitch_provider_confidence_enabled)
        self.provider_confidence_gate_mode = str(provider_confidence_gate_mode).strip().lower()
        if self.provider_confidence_gate_mode not in {
            "none",
            "confidence_only_v1",
            "hard_vuv_times_confidence_v1",
        }:
            raise ValueError(
                "provider_confidence_gate_mode must be one of: "
                "none, confidence_only_v1, hard_vuv_times_confidence_v1."
            )
        if self.provider_confidence_gate_mode != "none" and not self.pitch_provider_confidence_enabled:
            raise ValueError(
                "provider_confidence_gate_mode requires pitch_provider_confidence_enabled=true."
            )
        self.condition_proj = nn.Sequential(
            nn.Linear(speaker_embed_dim + geom_embed_dim, conditioning_dim),
            nn.GELU(),
            nn.LayerNorm(conditioning_dim),
        )
        control_dim = event_prior_dim + 4
        self.student_input_proj = nn.Linear(shared_dim + conditioning_dim + control_dim, student_dim)
        self.student_norm = nn.LayerNorm(student_dim)
        self.student_encoder = build_mlp(
            input_dim=student_dim,
            hidden_dim=student_dim,
            output_dim=student_dim,
            num_layers=student_layers,
        )
        self.teacher_fused_hidden_projection_head = nn.Linear(
            student_dim,
            teacher_fused_hidden_projection_dim,
        )
        self.z_art_head = nn.Linear(student_dim, z_art_dim)
        self.event_head = nn.Linear(student_dim, event_dim)
        self.r_res_head = nn.Linear(student_dim, r_res_dim) if r_res_enabled else None
        self.f0_delta_head = (
            nn.Linear(student_dim, 1)
            if f0_correction_enabled and self.f0_control_branch_mode == "shared_student_v1"
            else None
        )
        resolved_f0_control_branch_layers = (
            student_layers
            if f0_control_branch_layers is None
            else max(1, int(f0_control_branch_layers))
        )
        resolved_energy_control_branch_layers = (
            student_layers
            if energy_control_branch_layers is None
            else max(1, int(energy_control_branch_layers))
        )
        resolved_energy_control_branch_hidden_dim = (
            student_dim
            if energy_control_branch_hidden_dim is None
            else max(1, int(energy_control_branch_hidden_dim))
        )
        self.energy_control_branch_hidden_dim = resolved_energy_control_branch_hidden_dim
        f0_branch_input_dim = (
            shared_dim
            + conditioning_dim
            + event_prior_dim
            + 3
            + (1 if self.pitch_provider_confidence_enabled else 0)
        )
        self.f0_branch_input_proj = (
            nn.Linear(f0_branch_input_dim, student_dim)
            if self.f0_control_branch_mode
            in {"explicit_state_branch_v1", "explicit_named_control_family_v1"}
            else None
        )
        self.f0_branch_norm = (
            nn.LayerNorm(student_dim)
            if self.f0_control_branch_mode
            in {"explicit_state_branch_v1", "explicit_named_control_family_v1"}
            else None
        )
        self.f0_branch_encoder = (
            build_mlp(
                input_dim=student_dim,
                hidden_dim=student_dim,
                output_dim=student_dim,
                num_layers=resolved_f0_control_branch_layers,
            )
            if self.f0_control_branch_mode
            in {"explicit_state_branch_v1", "explicit_named_control_family_v1"}
            else None
        )
        self.f0_branch_delta_head = (
            nn.Linear(student_dim, 1)
            if f0_correction_enabled
            and self.f0_control_branch_mode
            in {"explicit_state_branch_v1", "explicit_named_control_family_v1"}
            else None
        )
        self.vuv_branch_delta_head = (
            nn.Linear(student_dim, 1)
            if self.f0_control_branch_mode == "explicit_named_control_family_v1"
            else None
        )
        self.aper_branch_delta_head = (
            nn.Linear(student_dim, 1)
            if aper_correction_enabled
            and self.f0_control_branch_mode == "explicit_named_control_family_v1"
            else None
        )
        self.energy_branch_delta_head = (
            nn.Linear(
                resolved_energy_control_branch_hidden_dim
                if self.energy_control_branch_mode == "dedicated_energy_branch_v1"
                else student_dim,
                1,
            )
            if self.f0_control_branch_mode == "explicit_named_control_family_v1"
            else None
        )
        energy_branch_input_dim = shared_dim + conditioning_dim + event_prior_dim + 4
        self.energy_branch_input_proj = (
            nn.Linear(energy_branch_input_dim, resolved_energy_control_branch_hidden_dim)
            if self.energy_control_branch_mode == "dedicated_energy_branch_v1"
            else None
        )
        self.energy_branch_norm = (
            nn.LayerNorm(resolved_energy_control_branch_hidden_dim)
            if self.energy_control_branch_mode == "dedicated_energy_branch_v1"
            else None
        )
        self.energy_branch_encoder = (
            build_mlp(
                input_dim=resolved_energy_control_branch_hidden_dim,
                hidden_dim=resolved_energy_control_branch_hidden_dim,
                output_dim=resolved_energy_control_branch_hidden_dim,
                num_layers=resolved_energy_control_branch_layers,
            )
            if self.energy_control_branch_mode == "dedicated_energy_branch_v1"
            else None
        )
        self.aper_delta_head = nn.Linear(student_dim, 1) if aper_correction_enabled else None

    def forward(
        self,
        frontend_outputs: dict[str, torch.Tensor],
        speaker_embedding: torch.Tensor,
        geom_embedding: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        shared_hidden = frontend_outputs["shared_hidden"]
        shared_hidden_for_student = (
            shared_hidden.detach() if self.detach_shared_hidden_for_student else shared_hidden
        )
        batch_size, frame_count, _ = shared_hidden.shape
        conditioning = self.condition_proj(torch.cat([speaker_embedding, geom_embedding], dim=-1))
        conditioning = conditioning.unsqueeze(1).expand(batch_size, frame_count, conditioning.shape[-1])
        frontend_named_controls = torch.cat(
            [
                frontend_outputs["coarse_log_f0"],
                torch.sigmoid(frontend_outputs["vuv_logits"]),
                frontend_outputs["aperiodicity"],
                frontend_outputs["energy"],
            ],
            dim=-1,
        )
        if self.detach_frontend_named_controls_for_student:
            frontend_named_controls = frontend_named_controls.detach()
        frontend_controls = torch.cat(
            [
                frontend_named_controls,
                torch.sigmoid(frontend_outputs["event_prior_logits"]),
            ],
            dim=-1,
        )
        student_input = torch.cat([shared_hidden_for_student, conditioning, frontend_controls], dim=-1)
        student_hidden = self.student_encoder(self.student_norm(self.student_input_proj(student_input)))
        event_logits = self.event_head(student_hidden)
        outputs = {
            "student_hidden": student_hidden,
            "conditioning": conditioning,
            "teacher_fused_hidden_projection": self.teacher_fused_hidden_projection_head(student_hidden),
            "z_art": self.z_art_head(student_hidden),
            "event_logits": event_logits,
            "event_probs": torch.sigmoid(event_logits),
            "energy_branch_hidden": student_hidden.new_zeros(
                (batch_size, frame_count, 0)
            ),
        }
        correction_gate = None
        if self.provider_confidence_gate_mode != "none":
            provider_confidence = frontend_outputs.get("pitch_provider_confidence")
            if not isinstance(provider_confidence, torch.Tensor):
                raise ValueError(
                    "provider_confidence_gate_mode requires frontend_outputs['pitch_provider_confidence']."
                )
            correction_gate = provider_confidence
            if self.provider_confidence_gate_mode == "hard_vuv_times_confidence_v1":
                provider_vuv = frontend_outputs.get("pitch_provider_vuv")
                if isinstance(provider_vuv, torch.Tensor):
                    correction_gate = correction_gate * provider_vuv
                else:
                    correction_gate = correction_gate * torch.sigmoid(frontend_outputs["vuv_logits"])
            outputs["f0_correction_gate"] = correction_gate
        if self.r_res_head is None:
            outputs["r_res"] = student_hidden.new_zeros((batch_size, frame_count, 0))
        else:
            outputs["r_res"] = self.r_res_head(student_hidden)
        if self.f0_control_branch_mode in {
            "explicit_state_branch_v1",
            "explicit_named_control_family_v1",
        }:
            f0_branch_features = [
                frontend_outputs["control_hidden"],
                conditioning,
                frontend_outputs["coarse_log_f0"],
                torch.sigmoid(frontend_outputs["vuv_logits"]),
                frontend_outputs["energy"],
                torch.sigmoid(frontend_outputs["event_prior_logits"]),
            ]
            if self.pitch_provider_confidence_enabled:
                provider_confidence = frontend_outputs.get("pitch_provider_confidence")
                if not isinstance(provider_confidence, torch.Tensor):
                    raise ValueError(
                        "pitch_provider_confidence_enabled requires frontend_outputs['pitch_provider_confidence']."
                    )
                f0_branch_features.insert(5, provider_confidence)
            f0_branch_input = torch.cat(f0_branch_features, dim=-1)
            f0_branch_hidden = self.f0_branch_encoder(
                self.f0_branch_norm(self.f0_branch_input_proj(f0_branch_input))
            )
            outputs["f0_branch_hidden"] = f0_branch_hidden
            if self.f0_branch_delta_head is None:
                f0_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            else:
                f0_delta = self.f0_branch_delta_head(f0_branch_hidden)
            if self.vuv_branch_delta_head is None:
                vuv_logit_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            else:
                vuv_logit_delta = torch.tanh(self.vuv_branch_delta_head(f0_branch_hidden)) * 2.0
            if self.aper_branch_delta_head is None:
                aper_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            else:
                aper_delta = torch.tanh(self.aper_branch_delta_head(f0_branch_hidden)) * 0.75
            if self.energy_branch_delta_head is None:
                energy_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            elif self.energy_control_branch_mode == "dedicated_energy_branch_v1":
                energy_branch_input = torch.cat(
                    [
                        frontend_outputs["control_hidden"],
                        conditioning,
                        frontend_outputs["coarse_log_f0"],
                        torch.sigmoid(frontend_outputs["vuv_logits"]),
                        frontend_outputs["aperiodicity"],
                        frontend_outputs["energy"],
                        torch.sigmoid(frontend_outputs["event_prior_logits"]),
                    ],
                    dim=-1,
                )
                energy_branch_hidden = self.energy_branch_encoder(
                    self.energy_branch_norm(self.energy_branch_input_proj(energy_branch_input))
                )
                outputs["energy_branch_hidden"] = energy_branch_hidden
                energy_delta = torch.tanh(self.energy_branch_delta_head(energy_branch_hidden)) * 0.5
            else:
                energy_delta = torch.tanh(self.energy_branch_delta_head(f0_branch_hidden)) * 0.5
        else:
            outputs["f0_branch_hidden"] = student_hidden.new_zeros((batch_size, frame_count, 0))
            if self.f0_delta_head is None:
                f0_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            else:
                f0_delta = self.f0_delta_head(student_hidden)
            vuv_logit_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
            aper_delta = (
                student_hidden.new_zeros((batch_size, frame_count, 1))
                if self.aper_delta_head is not None
                else student_hidden.new_zeros((batch_size, frame_count, 1))
            )
            energy_delta = student_hidden.new_zeros((batch_size, frame_count, 1))
        if isinstance(correction_gate, torch.Tensor):
            f0_delta = f0_delta * correction_gate
            vuv_logit_delta = vuv_logit_delta * correction_gate
        if self.f0_correction_parameterization_mode == "bounded_tanh_log2_delta_v1":
            outputs["log_f0_correction"] = torch.tanh(f0_delta) * self.f0_correction_limit_log2
        else:
            outputs["log_f0_correction"] = f0_delta
        outputs["vuv_logit_correction"] = vuv_logit_delta
        if self.f0_control_branch_mode == "explicit_named_control_family_v1":
            outputs["aper_correction"] = aper_delta
            outputs["energy_correction"] = energy_delta
        elif self.aper_delta_head is None:
            outputs["aper_correction"] = student_hidden.new_zeros((batch_size, frame_count, 1))
            outputs["energy_correction"] = student_hidden.new_zeros((batch_size, frame_count, 1))
        else:
            outputs["aper_correction"] = self.aper_delta_head(student_hidden)
            outputs["energy_correction"] = student_hidden.new_zeros((batch_size, frame_count, 1))
        return outputs


class StreamingStudentScaffold(nn.Module):
    def __init__(
        self,
        shared_dim: int,
        frontend_dim: int,
        frontend_layers: int,
        student_dim: int,
        student_layers: int,
        z_art_dim: int,
        event_dim: int,
        event_prior_dim: int,
        speaker_embed_dim: int,
        geom_embed_dim: int,
        conditioning_dim: int,
        teacher_hidden_projection_dim: int,
        teacher_fused_hidden_projection_dim: int,
        r_res_dim: int,
        frame_length: int,
        hop_length: int,
        r_res_enabled: bool,
        f0_correction_enabled: bool,
        aper_correction_enabled: bool,
        timing_aux_enabled: bool = False,
        detach_frontend_named_controls_for_student: bool = False,
        detach_shared_hidden_for_student: bool = False,
        named_control_branch_mode: str = "shared_hidden_v1",
        named_control_branch_layers: int | None = None,
        f0_parameterization_mode: str = "unbounded_log_v1",
        f0_floor_hz: float = DEFAULT_STREAMING_STUDENT_F0_FLOOR_HZ,
        f0_ceil_hz: float = DEFAULT_STREAMING_STUDENT_F0_CEIL_HZ,
        pitch_provider_mode: str = DEFAULT_STAGE3_PITCH_PROVIDER_MODE,
        f0_control_branch_mode: str = "shared_student_v1",
        f0_control_branch_layers: int | None = None,
        energy_control_branch_mode: str = "shared_f0_branch_v1",
        energy_control_branch_layers: int | None = None,
        energy_control_branch_hidden_dim: int | None = None,
        f0_correction_parameterization_mode: str = "linear_unbounded_v1",
        f0_correction_limit_log2: float = 0.5,
        provider_confidence_gate_mode: str = "none",
    ) -> None:
        super().__init__()
        self.frontend = UnifiedStreamingFrontend(
            shared_dim=shared_dim,
            frontend_dim=frontend_dim,
            frontend_layers=frontend_layers,
            frame_length=frame_length,
            hop_length=hop_length,
            event_prior_dim=event_prior_dim,
            teacher_hidden_projection_dim=teacher_hidden_projection_dim,
            timing_aux_enabled=timing_aux_enabled,
            named_control_branch_mode=named_control_branch_mode,
            named_control_branch_layers=named_control_branch_layers,
            f0_parameterization_mode=f0_parameterization_mode,
            f0_floor_hz=f0_floor_hz,
            f0_ceil_hz=f0_ceil_hz,
            pitch_provider_mode=pitch_provider_mode,
        )
        self.student = StudentControlHeads(
            shared_dim=shared_dim,
            event_prior_dim=event_prior_dim,
            student_dim=student_dim,
            student_layers=student_layers,
            z_art_dim=z_art_dim,
            event_dim=event_dim,
            speaker_embed_dim=speaker_embed_dim,
            geom_embed_dim=geom_embed_dim,
            conditioning_dim=conditioning_dim,
            teacher_fused_hidden_projection_dim=teacher_fused_hidden_projection_dim,
            r_res_dim=r_res_dim,
            r_res_enabled=r_res_enabled,
            f0_correction_enabled=f0_correction_enabled,
            aper_correction_enabled=aper_correction_enabled,
            detach_frontend_named_controls_for_student=detach_frontend_named_controls_for_student,
            detach_shared_hidden_for_student=detach_shared_hidden_for_student,
            f0_control_branch_mode=f0_control_branch_mode,
            f0_control_branch_layers=f0_control_branch_layers,
            energy_control_branch_mode=energy_control_branch_mode,
            energy_control_branch_layers=energy_control_branch_layers,
            energy_control_branch_hidden_dim=energy_control_branch_hidden_dim,
            f0_correction_parameterization_mode=f0_correction_parameterization_mode,
            f0_correction_limit_log2=f0_correction_limit_log2,
            pitch_provider_confidence_enabled=(
                normalize_stage3_pitch_provider_mode(pitch_provider_mode)
                == "rmvpe_split_confidence_v1"
            ),
            provider_confidence_gate_mode=provider_confidence_gate_mode,
        )

    def forward(
        self,
        waveform: torch.Tensor,
        lengths: torch.Tensor,
        speaker_embedding: torch.Tensor,
        geom_embedding: torch.Tensor,
        pitch_provider_log2_f0: torch.Tensor | None = None,
        pitch_provider_vuv: torch.Tensor | None = None,
        pitch_provider_confidence: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        frontend_outputs = self.frontend(
            waveform=waveform,
            lengths=lengths,
            pitch_provider_log2_f0=pitch_provider_log2_f0,
            pitch_provider_vuv=pitch_provider_vuv,
            pitch_provider_confidence=pitch_provider_confidence,
        )
        student_outputs = self.student(
            frontend_outputs=frontend_outputs,
            speaker_embedding=speaker_embedding,
            geom_embedding=geom_embedding,
        )
        outputs = dict(frontend_outputs)
        outputs.update(student_outputs)
        return outputs


def build_mlp(
    input_dim: int,
    hidden_dim: int,
    output_dim: int,
    num_layers: int,
) -> nn.Sequential:
    if num_layers < 1:
        raise ValueError("num_layers must be >= 1")
    layers: list[nn.Module] = []
    current_dim = input_dim
    for _ in range(num_layers - 1):
        layers.extend(
            [
                nn.Linear(current_dim, hidden_dim),
                nn.GELU(),
                nn.LayerNorm(hidden_dim),
            ]
        )
        current_dim = hidden_dim
    layers.append(nn.Linear(current_dim, output_dim))
    return nn.Sequential(*layers)
