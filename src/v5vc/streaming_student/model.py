from __future__ import annotations

import math
import torch
from torch import nn
import torch.nn.functional as F

from v5vc.offline_mvp.model import frame_waveform
from v5vc.streaming_student.fine_structure import build_batched_unit_rms_waveform_frames
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
        aper_control_branch_mode: str,
        aper_control_branch_layers: int | None,
        aper_control_branch_hidden_dim: int | None,
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
        self.aper_control_branch_mode = str(aper_control_branch_mode).strip().lower()
        if self.aper_control_branch_mode not in {
            "shared_f0_branch_v1",
            "dedicated_aper_branch_v1",
        }:
            raise ValueError(
                "aper_control_branch_mode must be one of: "
                "shared_f0_branch_v1, dedicated_aper_branch_v1."
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
            self.aper_control_branch_mode != "shared_f0_branch_v1"
            and self.f0_control_branch_mode != "explicit_named_control_family_v1"
        ):
            raise ValueError(
                "dedicated_aper_branch_v1 requires "
                "f0_control_branch_mode=explicit_named_control_family_v1."
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
        resolved_aper_control_branch_layers = (
            student_layers
            if aper_control_branch_layers is None
            else max(1, int(aper_control_branch_layers))
        )
        resolved_energy_control_branch_hidden_dim = (
            student_dim
            if energy_control_branch_hidden_dim is None
            else max(1, int(energy_control_branch_hidden_dim))
        )
        resolved_aper_control_branch_hidden_dim = (
            student_dim
            if aper_control_branch_hidden_dim is None
            else max(1, int(aper_control_branch_hidden_dim))
        )
        self.energy_control_branch_hidden_dim = resolved_energy_control_branch_hidden_dim
        self.aper_control_branch_hidden_dim = resolved_aper_control_branch_hidden_dim
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
            nn.Linear(
                resolved_aper_control_branch_hidden_dim
                if self.aper_control_branch_mode == "dedicated_aper_branch_v1"
                else student_dim,
                1,
            )
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
        aper_branch_input_dim = shared_dim + conditioning_dim + event_prior_dim + 4
        self.aper_branch_input_proj = (
            nn.Linear(aper_branch_input_dim, resolved_aper_control_branch_hidden_dim)
            if self.aper_control_branch_mode == "dedicated_aper_branch_v1"
            else None
        )
        self.aper_branch_norm = (
            nn.LayerNorm(resolved_aper_control_branch_hidden_dim)
            if self.aper_control_branch_mode == "dedicated_aper_branch_v1"
            else None
        )
        self.aper_branch_encoder = (
            build_mlp(
                input_dim=resolved_aper_control_branch_hidden_dim,
                hidden_dim=resolved_aper_control_branch_hidden_dim,
                output_dim=resolved_aper_control_branch_hidden_dim,
                num_layers=resolved_aper_control_branch_layers,
            )
            if self.aper_control_branch_mode == "dedicated_aper_branch_v1"
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
            "aper_branch_hidden": student_hidden.new_zeros(
                (batch_size, frame_count, 0)
            ),
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
            elif self.aper_control_branch_mode == "dedicated_aper_branch_v1":
                aper_branch_input = torch.cat(
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
                aper_branch_hidden = self.aper_branch_encoder(
                    self.aper_branch_norm(self.aper_branch_input_proj(aper_branch_input))
                )
                outputs["aper_branch_hidden"] = aper_branch_hidden
                aper_delta = torch.tanh(self.aper_branch_delta_head(aper_branch_hidden)) * 0.75
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
        aper_control_branch_mode: str = "shared_f0_branch_v1",
        aper_control_branch_layers: int | None = None,
        aper_control_branch_hidden_dim: int | None = None,
        energy_control_branch_mode: str = "shared_f0_branch_v1",
        energy_control_branch_layers: int | None = None,
        energy_control_branch_hidden_dim: int | None = None,
        f0_correction_parameterization_mode: str = "linear_unbounded_v1",
        f0_correction_limit_log2: float = 0.5,
        provider_confidence_gate_mode: str = "none",
        fine_structure_code_dim: int = 0,
        fine_structure_code_source_mode: str = "none",
        fine_structure_code_detach_source: bool = False,
        fine_structure_waveform_encoder_dim: int | None = None,
        fine_structure_waveform_encoder_layers: int = 2,
        fine_structure_code_predictor_mode: str = "linear_v1",
        fine_structure_code_context_layers: int = 0,
        fine_structure_code_context_kernel_size: int = 1,
    ) -> None:
        super().__init__()
        self.frame_length = int(frame_length)
        self.hop_length = int(hop_length)
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
            aper_control_branch_mode=aper_control_branch_mode,
            aper_control_branch_layers=aper_control_branch_layers,
            aper_control_branch_hidden_dim=aper_control_branch_hidden_dim,
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
        self.fine_structure_code_dim = max(0, int(fine_structure_code_dim))
        self.fine_structure_code_source_mode = str(fine_structure_code_source_mode).strip().lower()
        self.fine_structure_code_detach_source = bool(fine_structure_code_detach_source)
        self.fine_structure_waveform_encoder_dim = max(
            1,
            int(
                shared_dim
                if fine_structure_waveform_encoder_dim in {None, ""}
                else fine_structure_waveform_encoder_dim
            ),
        )
        self.fine_structure_waveform_encoder_layers = max(1, int(fine_structure_waveform_encoder_layers))
        self.fine_structure_code_predictor_mode = str(fine_structure_code_predictor_mode).strip().lower()
        self.fine_structure_code_context_layers = max(0, int(fine_structure_code_context_layers))
        self.fine_structure_code_context_kernel_size = max(1, int(fine_structure_code_context_kernel_size))
        if self.fine_structure_code_source_mode not in {
            "none",
            "shared_hidden_v1",
            "control_hidden_v1",
            "student_hidden_v1",
            "waveform_frame_encoder_v1",
        }:
            raise ValueError(
                "fine_structure_code_source_mode must be one of: "
                "none, shared_hidden_v1, control_hidden_v1, student_hidden_v1, "
                "waveform_frame_encoder_v1."
            )
        if self.fine_structure_code_predictor_mode not in {"linear_v1", "temporal_conv_v1"}:
            raise ValueError(
                "fine_structure_code_predictor_mode must be one of: "
                "linear_v1, temporal_conv_v1."
            )
        if self.fine_structure_code_predictor_mode == "temporal_conv_v1":
            if self.fine_structure_code_context_layers <= 0:
                raise ValueError(
                    "fine_structure_code_predictor_mode=temporal_conv_v1 requires "
                    "fine_structure_code_context_layers > 0."
                )
            if self.fine_structure_code_context_kernel_size % 2 == 0:
                raise ValueError(
                    "fine_structure_code_context_kernel_size must be odd for temporal_conv_v1."
                )
        if self.fine_structure_code_dim > 0 and self.fine_structure_code_source_mode == "none":
            raise ValueError(
                "fine_structure_code_dim > 0 requires fine_structure_code_source_mode != 'none'."
            )
        if self.fine_structure_code_dim <= 0:
            self.fine_structure_waveform_encoder = None
            self.fine_structure_code_context = None
            self.fine_structure_code_head = None
            self.fine_structure_waveform_decoder = None
        else:
            source_dim = {
                "shared_hidden_v1": int(shared_dim),
                "control_hidden_v1": int(shared_dim),
                "student_hidden_v1": int(student_dim),
                "waveform_frame_encoder_v1": int(self.fine_structure_waveform_encoder_dim),
            }[self.fine_structure_code_source_mode]
            self.fine_structure_waveform_encoder = (
                build_mlp(
                    input_dim=self.frame_length,
                    hidden_dim=self.fine_structure_waveform_encoder_dim,
                    output_dim=self.fine_structure_waveform_encoder_dim,
                    num_layers=self.fine_structure_waveform_encoder_layers,
                )
                if self.fine_structure_code_source_mode == "waveform_frame_encoder_v1"
                else None
            )
            if self.fine_structure_code_predictor_mode == "temporal_conv_v1":
                self.fine_structure_code_context = TemporalConvContextStack(
                    channel_dim=source_dim,
                    num_layers=self.fine_structure_code_context_layers,
                    kernel_size=self.fine_structure_code_context_kernel_size,
                )
            else:
                self.fine_structure_code_context = None
            self.fine_structure_code_head = nn.Linear(source_dim, self.fine_structure_code_dim)
            self.fine_structure_waveform_decoder = nn.Linear(self.fine_structure_code_dim, self.frame_length)

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
        outputs["frame_length"] = self.frame_length
        outputs["hop_length"] = self.hop_length
        fine_structure_code = None
        if self.fine_structure_code_head is not None and self.fine_structure_waveform_decoder is not None:
            if self.fine_structure_code_source_mode == "waveform_frame_encoder_v1":
                if self.fine_structure_waveform_encoder is None:
                    raise ValueError("waveform_frame_encoder_v1 requires fine_structure_waveform_encoder.")
                frame_lengths = frontend_outputs["frame_mask"].to(torch.long).sum(dim=1)
                unit_rms_waveform_frames = build_batched_unit_rms_waveform_frames(
                    waveform_batch=waveform,
                    frame_lengths=frame_lengths,
                    frame_length=self.frame_length,
                    hop_length=self.hop_length,
                ).to(
                    device=frontend_outputs["shared_hidden"].device,
                    dtype=frontend_outputs["shared_hidden"].dtype,
                )
                source_hidden = self.fine_structure_waveform_encoder(unit_rms_waveform_frames)
            else:
                source_hidden = {
                    "shared_hidden_v1": frontend_outputs["shared_hidden"],
                    "control_hidden_v1": frontend_outputs["control_hidden"],
                    "student_hidden_v1": student_outputs["student_hidden"],
                }.get(self.fine_structure_code_source_mode)
            if not isinstance(source_hidden, torch.Tensor):
                raise ValueError(
                    "fine_structure_code_source_mode resolved to a missing hidden source: "
                    f"{self.fine_structure_code_source_mode!r}"
                )
            if self.fine_structure_code_detach_source:
                source_hidden = source_hidden.detach()
            if self.fine_structure_code_context is not None:
                source_hidden = self.fine_structure_code_context(source_hidden)
            fine_structure_code = self.fine_structure_code_head(source_hidden)
            outputs["fine_structure_code"] = fine_structure_code
            outputs["fine_structure_waveform_reconstruction"] = self.fine_structure_waveform_decoder(
                fine_structure_code
            )
        else:
            frame_mask = frontend_outputs["frame_mask"]
            batch_size, frame_count = int(frame_mask.shape[0]), int(frame_mask.shape[1])
            zero_code = frontend_outputs["shared_hidden"].new_zeros((batch_size, frame_count, 0))
            outputs["fine_structure_code"] = zero_code
            outputs["fine_structure_waveform_reconstruction"] = frontend_outputs["shared_hidden"].new_zeros(
                (batch_size, frame_count, 0)
            )
        outputs["fine_structure_code_dim"] = self.fine_structure_code_dim
        outputs["fine_structure_code_source_mode"] = self.fine_structure_code_source_mode
        outputs["fine_structure_code_detach_source"] = self.fine_structure_code_detach_source
        outputs["fine_structure_waveform_encoder_dim"] = self.fine_structure_waveform_encoder_dim
        outputs["fine_structure_waveform_encoder_layers"] = self.fine_structure_waveform_encoder_layers
        outputs["fine_structure_code_predictor_mode"] = self.fine_structure_code_predictor_mode
        return outputs


class TemporalConvContextStack(nn.Module):
    def __init__(self, channel_dim: int, num_layers: int, kernel_size: int) -> None:
        super().__init__()
        resolved_layers = max(1, int(num_layers))
        resolved_kernel_size = max(1, int(kernel_size))
        padding = resolved_kernel_size // 2
        self.layers = nn.ModuleList(
            [
                nn.Conv1d(
                    in_channels=int(channel_dim),
                    out_channels=int(channel_dim),
                    kernel_size=resolved_kernel_size,
                    padding=padding,
                )
                for _ in range(resolved_layers)
            ]
        )
        self.norms = nn.ModuleList([nn.LayerNorm(int(channel_dim)) for _ in range(resolved_layers)])

    def forward(self, sequence: torch.Tensor) -> torch.Tensor:
        hidden = sequence
        for conv, norm in zip(self.layers, self.norms, strict=False):
            conv_hidden = conv(hidden.transpose(1, 2)).transpose(1, 2)
            hidden = norm(hidden + F.gelu(conv_hidden))
        return hidden


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
