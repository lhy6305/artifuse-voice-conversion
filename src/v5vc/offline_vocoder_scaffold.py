from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch
from torch import nn


SUPPORTED_TEACHER_VOCODER_SCAFFOLD_VERSIONS = {
    "offline_teacher_vocoder_input_scaffold_v1",
    "offline_teacher_vocoder_input_scaffold_v2",
    "offline_teacher_vocoder_input_scaffold_v3",
    "streaming_student_vocoder_input_scaffold_v1",
}
SUPPORTED_WAVEFORM_DECODER_MODES = {
    "fused_single",
    "dual_branch_mix",
    "periodic_plus_noise_residual",
    "periodic_plus_noise_residual_shape",
    "periodic_plus_noise_factorized_residual",
    "periodic_plus_noise_residual_shape_temporal",
    "periodic_plus_noise_residual_shape_recurrent",
}
SUPPORTED_FUSION_MODES = {
    "plain",
    "branch_mean_residual_v1",
    "periodic_residual_v1",
    "branch_mean_contrast_residual_v1",
}


class NoResidualSourceFilterVocoderScaffold(nn.Module):
    def __init__(
        self,
        periodic_input_dim: int,
        noise_input_dim: int,
        hidden_dim: int,
        harmonic_bins: int,
        noise_bins: int,
        frame_length: int | None = None,
        fusion_mode: str = "plain",
        waveform_decoder_mode: str = "fused_single",
        use_decoder_branch_condition_adapter: bool = False,
        use_residual_shape_branch_condition_adapter: bool = False,
    ) -> None:
        super().__init__()
        self.frame_length = int(frame_length) if frame_length is not None and int(frame_length) > 0 else None
        self.fusion_mode = normalize_fusion_mode(fusion_mode)
        self.waveform_decoder_mode = normalize_waveform_decoder_mode(waveform_decoder_mode)
        self.use_decoder_branch_condition_adapter = bool(use_decoder_branch_condition_adapter)
        self.use_residual_shape_branch_condition_adapter = bool(use_residual_shape_branch_condition_adapter)
        self.periodic_encoder = build_mlp(periodic_input_dim, hidden_dim, hidden_dim)
        self.noise_encoder = build_mlp(noise_input_dim, hidden_dim, hidden_dim)
        self.periodic_gate = nn.Linear(hidden_dim, 1)
        self.noise_gate = nn.Linear(hidden_dim, 1)
        self.harmonic_envelope = nn.Linear(hidden_dim, harmonic_bins)
        self.noise_envelope = nn.Linear(hidden_dim, noise_bins)
        self.fusion = None
        self.fusion_branch_mean_residual = None
        self.fusion_periodic_residual_adapter = None
        self.fusion_periodic_residual_gate = None
        self.fusion_periodic_residual_proj = None
        self.fusion_branch_mean_contrast_norm = None
        self.fusion_branch_mean_contrast_gate = None
        self.fusion_branch_mean_contrast_proj = None
        if self.fusion_mode == "plain":
            self.fusion = nn.Sequential(
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.GELU(),
                nn.LayerNorm(hidden_dim),
                nn.Linear(hidden_dim, hidden_dim),
            )
        elif self.fusion_mode == "branch_mean_residual_v1":
            self.fusion_branch_mean_residual = nn.Sequential(
                nn.Linear(hidden_dim * 3, hidden_dim),
                nn.GELU(),
                nn.LayerNorm(hidden_dim),
                nn.Linear(hidden_dim, hidden_dim),
            )
            nn.init.zeros_(self.fusion_branch_mean_residual[-1].weight)
            nn.init.zeros_(self.fusion_branch_mean_residual[-1].bias)
        elif self.fusion_mode == "periodic_residual_v1":
            self.fusion_periodic_residual_adapter = nn.Sequential(
                nn.Linear(hidden_dim * 3, hidden_dim),
                nn.GELU(),
                nn.LayerNorm(hidden_dim),
            )
            self.fusion_periodic_residual_gate = nn.Linear(hidden_dim, 1)
            self.fusion_periodic_residual_proj = nn.Linear(hidden_dim, hidden_dim)
            nn.init.zeros_(self.fusion_periodic_residual_gate.weight)
            nn.init.constant_(self.fusion_periodic_residual_gate.bias, -2.0)
            nn.init.zeros_(self.fusion_periodic_residual_proj.weight)
            nn.init.zeros_(self.fusion_periodic_residual_proj.bias)
        elif self.fusion_mode == "branch_mean_contrast_residual_v1":
            self.fusion_branch_mean_contrast_norm = nn.LayerNorm(hidden_dim)
            self.fusion_branch_mean_contrast_gate = nn.Linear(hidden_dim, 1)
            self.fusion_branch_mean_contrast_proj = nn.Linear(hidden_dim, hidden_dim)
            nn.init.zeros_(self.fusion_branch_mean_contrast_gate.weight)
            nn.init.constant_(self.fusion_branch_mean_contrast_gate.bias, -2.0)
            nn.init.zeros_(self.fusion_branch_mean_contrast_proj.weight)
            nn.init.zeros_(self.fusion_branch_mean_contrast_proj.bias)
        else:
            raise ValueError(f"Unsupported fusion_mode for no-residual vocoder scaffold: {self.fusion_mode!r}")
        self.waveform_decoder = None
        self.periodic_waveform_decoder = None
        self.noise_waveform_decoder = None
        self.waveform_frame_mixer = None
        self.noise_residual_decoder = None
        self.noise_residual_gate_head = None
        self.noise_residual_shape_head = None
        self.noise_residual_gain_head = None
        self.noise_residual_scale = None
        self.periodic_temporal_refiner = None
        self.noise_temporal_refiner = None
        self.periodic_temporal_gru = None
        self.noise_temporal_gru = None
        self.decoder_branch_condition_adapter = None
        self.decoder_branch_condition_gate = None
        self.decoder_fused_condition_proj = None
        self.decoder_periodic_condition_proj = None
        self.decoder_noise_condition_proj = None
        self.residual_shape_branch_condition_adapter = None
        self.residual_shape_branch_condition_gate = None
        self.residual_shape_branch_condition_proj = None
        if self.use_decoder_branch_condition_adapter:
            self.decoder_branch_condition_adapter = nn.Sequential(
                nn.Linear(hidden_dim * 3, hidden_dim),
                nn.GELU(),
                nn.LayerNorm(hidden_dim),
                nn.Linear(hidden_dim, hidden_dim),
            )
            self.decoder_branch_condition_gate = nn.Linear(hidden_dim, 1)
            self.decoder_fused_condition_proj = nn.Linear(hidden_dim, hidden_dim)
            self.decoder_periodic_condition_proj = nn.Linear(hidden_dim, hidden_dim)
            self.decoder_noise_condition_proj = nn.Linear(hidden_dim, hidden_dim)
            nn.init.zeros_(self.decoder_branch_condition_gate.weight)
            nn.init.constant_(self.decoder_branch_condition_gate.bias, -2.0)
            nn.init.zeros_(self.decoder_fused_condition_proj.weight)
            nn.init.zeros_(self.decoder_fused_condition_proj.bias)
            nn.init.zeros_(self.decoder_periodic_condition_proj.weight)
            nn.init.zeros_(self.decoder_periodic_condition_proj.bias)
            nn.init.zeros_(self.decoder_noise_condition_proj.weight)
            nn.init.zeros_(self.decoder_noise_condition_proj.bias)
        if self.frame_length is not None:
            if self.use_residual_shape_branch_condition_adapter:
                self.residual_shape_branch_condition_adapter = nn.Sequential(
                    nn.Linear(hidden_dim * 3, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, hidden_dim),
                )
                self.residual_shape_branch_condition_gate = nn.Linear(hidden_dim, 1)
                self.residual_shape_branch_condition_proj = nn.Linear(hidden_dim, int(self.frame_length))
                nn.init.zeros_(self.residual_shape_branch_condition_gate.weight)
                nn.init.constant_(self.residual_shape_branch_condition_gate.bias, -2.0)
                nn.init.zeros_(self.residual_shape_branch_condition_proj.weight)
                nn.init.zeros_(self.residual_shape_branch_condition_proj.bias)
            if self.waveform_decoder_mode == "fused_single":
                self.waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
            elif self.waveform_decoder_mode == "dual_branch_mix":
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.waveform_frame_mixer = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, 1),
                )
            elif self.waveform_decoder_mode == "periodic_plus_noise_residual":
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_gate_head = nn.Sequential(
                    nn.Linear(hidden_dim + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, 1),
                )
                # Start with a conservative residual magnitude so the periodic path stays dominant.
                self.noise_residual_scale = nn.Parameter(torch.tensor(0.25, dtype=torch.float32))
            elif self.waveform_decoder_mode == "periodic_plus_noise_residual_shape":
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_shape_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_scale = nn.Parameter(torch.tensor(0.25, dtype=torch.float32))
            elif self.waveform_decoder_mode == "periodic_plus_noise_factorized_residual":
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_shape_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_gain_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, 1),
                )
                self.noise_residual_scale = nn.Parameter(torch.tensor(0.25, dtype=torch.float32))
            elif self.waveform_decoder_mode == "periodic_plus_noise_residual_shape_temporal":
                self.periodic_temporal_refiner = build_temporal_refiner(hidden_dim)
                self.noise_temporal_refiner = build_temporal_refiner(hidden_dim)
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_shape_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_scale = nn.Parameter(torch.tensor(0.25, dtype=torch.float32))
            elif self.waveform_decoder_mode == "periodic_plus_noise_residual_shape_recurrent":
                self.periodic_temporal_gru = nn.GRU(
                    input_size=hidden_dim,
                    hidden_size=hidden_dim,
                    batch_first=True,
                )
                self.noise_temporal_gru = nn.GRU(
                    input_size=hidden_dim,
                    hidden_size=hidden_dim,
                    batch_first=True,
                )
                self.periodic_waveform_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_decoder = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_shape_head = nn.Sequential(
                    nn.Linear(hidden_dim * 2 + 2, hidden_dim),
                    nn.GELU(),
                    nn.LayerNorm(hidden_dim),
                    nn.Linear(hidden_dim, int(self.frame_length)),
                )
                self.noise_residual_scale = nn.Parameter(torch.tensor(0.25, dtype=torch.float32))
            else:
                raise ValueError(
                    f"Unsupported waveform decoder mode for frame_length-backed scaffold: {self.waveform_decoder_mode!r}"
                )

    def forward(
        self,
        periodic_branch_features: torch.Tensor,
        noise_branch_features: torch.Tensor,
        decoder_branch_mean_mix_alpha: float = 0.0,
    ) -> dict[str, torch.Tensor]:
        resolved_decoder_branch_mean_mix_alpha = float(decoder_branch_mean_mix_alpha)
        if resolved_decoder_branch_mean_mix_alpha < 0.0 or resolved_decoder_branch_mean_mix_alpha > 1.0:
            raise ValueError("decoder_branch_mean_mix_alpha must be within [0.0, 1.0].")
        periodic_hidden = self.periodic_encoder(periodic_branch_features)
        noise_hidden = self.noise_encoder(noise_branch_features)
        branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
        branch_difference_hidden = periodic_hidden - noise_hidden
        fusion_residual_hidden = None
        fusion_residual_gate = None
        if self.fusion_mode == "plain":
            if self.fusion is None:
                raise RuntimeError("fusion is not initialized for plain fusion mode.")
            fused_hidden = self.fusion(torch.cat([periodic_hidden, noise_hidden], dim=-1))
        elif self.fusion_mode == "branch_mean_residual_v1":
            if self.fusion_branch_mean_residual is None:
                raise RuntimeError("fusion_branch_mean_residual is not initialized for branch_mean_residual_v1.")
            fusion_residual_hidden = self.fusion_branch_mean_residual(
                torch.cat(
                    [
                        periodic_hidden,
                        noise_hidden,
                        branch_difference_hidden,
                    ],
                    dim=-1,
                )
            )
            fused_hidden = branch_mean_hidden + fusion_residual_hidden
        elif self.fusion_mode == "periodic_residual_v1":
            if (
                self.fusion_periodic_residual_adapter is None
                or self.fusion_periodic_residual_gate is None
                or self.fusion_periodic_residual_proj is None
            ):
                raise RuntimeError("fusion_periodic_residual modules are not initialized for periodic_residual_v1.")
            fusion_residual_context = self.fusion_periodic_residual_adapter(
                torch.cat(
                    [
                        periodic_hidden,
                        noise_hidden,
                        branch_difference_hidden,
                    ],
                    dim=-1,
                )
            )
            fusion_residual_gate = torch.sigmoid(self.fusion_periodic_residual_gate(fusion_residual_context))
            fusion_residual_hidden = fusion_residual_gate * torch.tanh(
                self.fusion_periodic_residual_proj(fusion_residual_context)
            )
            fused_hidden = periodic_hidden + fusion_residual_hidden
        elif self.fusion_mode == "branch_mean_contrast_residual_v1":
            if (
                self.fusion_branch_mean_contrast_norm is None
                or self.fusion_branch_mean_contrast_gate is None
                or self.fusion_branch_mean_contrast_proj is None
            ):
                raise RuntimeError(
                    "fusion_branch_mean_contrast modules are not initialized for branch_mean_contrast_residual_v1."
                )
            contrast_hidden = self.fusion_branch_mean_contrast_norm(branch_difference_hidden)
            fusion_residual_gate = torch.sigmoid(self.fusion_branch_mean_contrast_gate(contrast_hidden))
            fusion_residual_hidden = fusion_residual_gate * torch.tanh(
                self.fusion_branch_mean_contrast_proj(contrast_hidden)
            )
            fused_hidden = branch_mean_hidden + fusion_residual_hidden
        else:
            raise RuntimeError(f"Unsupported fusion_mode at forward dispatch: {self.fusion_mode!r}")
        decoder_hidden = (
            fused_hidden
            if resolved_decoder_branch_mean_mix_alpha <= 0.0
            else fused_hidden * float(1.0 - resolved_decoder_branch_mean_mix_alpha)
            + branch_mean_hidden * resolved_decoder_branch_mean_mix_alpha
        )
        branch_condition_gate = None
        fused_condition = None
        periodic_condition = None
        noise_condition = None
        residual_shape_branch_condition_gate = None
        residual_shape_branch_condition_delta = None
        if self.use_decoder_branch_condition_adapter:
            if (
                self.decoder_branch_condition_adapter is None
                or self.decoder_branch_condition_gate is None
                or self.decoder_fused_condition_proj is None
                or self.decoder_periodic_condition_proj is None
                or self.decoder_noise_condition_proj is None
            ):
                raise RuntimeError("Decoder branch-condition adapter modules are not initialized.")
            branch_condition_features = torch.cat(
                [
                    fused_hidden,
                    branch_mean_hidden,
                    fused_hidden - branch_mean_hidden,
                ],
                dim=-1,
            )
            branch_condition_context = self.decoder_branch_condition_adapter(branch_condition_features)
            branch_condition_gate = torch.sigmoid(self.decoder_branch_condition_gate(branch_condition_context))
            fused_condition = torch.tanh(self.decoder_fused_condition_proj(branch_condition_context))
            periodic_condition = torch.tanh(self.decoder_periodic_condition_proj(branch_condition_context))
            noise_condition = torch.tanh(self.decoder_noise_condition_proj(branch_condition_context))
            decoder_hidden = decoder_hidden + branch_condition_gate * fused_condition
        if self.use_residual_shape_branch_condition_adapter:
            if (
                self.residual_shape_branch_condition_adapter is None
                or self.residual_shape_branch_condition_gate is None
                or self.residual_shape_branch_condition_proj is None
            ):
                raise RuntimeError("Residual-shape branch-condition adapter modules are not initialized.")
            residual_shape_branch_condition_features = torch.cat(
                [
                    fused_hidden,
                    branch_mean_hidden,
                    fused_hidden - branch_mean_hidden,
                ],
                dim=-1,
            )
            residual_shape_branch_condition_context = self.residual_shape_branch_condition_adapter(
                residual_shape_branch_condition_features
            )
            residual_shape_branch_condition_gate = torch.sigmoid(
                self.residual_shape_branch_condition_gate(residual_shape_branch_condition_context)
            )
            residual_shape_branch_condition_delta = torch.tanh(
                self.residual_shape_branch_condition_proj(residual_shape_branch_condition_context)
            )
        outputs = {
            "periodic_hidden": periodic_hidden,
            "noise_hidden": noise_hidden,
            "fused_hidden": fused_hidden,
            "branch_mean_hidden": branch_mean_hidden,
            "decoder_hidden": decoder_hidden,
            "periodic_gate": torch.sigmoid(self.periodic_gate(periodic_hidden)),
            "noise_gate": torch.sigmoid(self.noise_gate(noise_hidden)),
            "harmonic_envelope": self.harmonic_envelope(periodic_hidden),
            "noise_envelope": self.noise_envelope(noise_hidden),
        }
        if fusion_residual_hidden is not None:
            outputs["fusion_residual_hidden"] = fusion_residual_hidden
        if fusion_residual_gate is not None:
            outputs["fusion_residual_gate"] = fusion_residual_gate
        if branch_condition_gate is not None:
            outputs["decoder_branch_condition_gate"] = branch_condition_gate
            outputs["decoder_fused_condition"] = fused_condition
            outputs["decoder_periodic_condition"] = periodic_condition
            outputs["decoder_noise_condition"] = noise_condition
        if residual_shape_branch_condition_gate is not None:
            outputs["residual_shape_branch_condition_gate"] = residual_shape_branch_condition_gate
            outputs["residual_shape_branch_condition_delta"] = residual_shape_branch_condition_delta
        if self.frame_length is None:
            return outputs
        if self.waveform_decoder_mode == "fused_single":
            if self.waveform_decoder is None:
                raise RuntimeError("waveform_decoder is not initialized for fused_single mode.")
            outputs["waveform_frames"] = torch.tanh(self.waveform_decoder(decoder_hidden))
            return outputs
        if resolved_decoder_branch_mean_mix_alpha > 1.0e-9:
            raise ValueError("decoder_branch_mean_mix_alpha is only supported for fused_single waveform decoder mode.")
        if self.waveform_decoder_mode == "dual_branch_mix":
            if (
                self.periodic_waveform_decoder is None
                or self.noise_waveform_decoder is None
                or self.waveform_frame_mixer is None
            ):
                raise RuntimeError("Dual-branch waveform decoder modules are not initialized.")
            conditioned_periodic_hidden = apply_decoder_branch_condition(
                periodic_hidden,
                branch_condition_gate,
                periodic_condition,
            )
            conditioned_noise_hidden = apply_decoder_branch_condition(
                noise_hidden,
                branch_condition_gate,
                noise_condition,
            )
            periodic_frames = self.periodic_waveform_decoder(conditioned_periodic_hidden)
            noise_frames = self.noise_waveform_decoder(conditioned_noise_hidden)
            mixer_features = torch.cat(
                [
                    conditioned_periodic_hidden,
                    conditioned_noise_hidden,
                    outputs["periodic_gate"],
                    outputs["noise_gate"],
                ],
                dim=-1,
            )
            waveform_mix_gate = torch.sigmoid(self.waveform_frame_mixer(mixer_features))
            mixed_frames = periodic_frames * waveform_mix_gate + noise_frames * (1.0 - waveform_mix_gate)
            outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
            outputs["noise_waveform_frames"] = torch.tanh(noise_frames)
            outputs["waveform_mix_gate"] = waveform_mix_gate
            outputs["waveform_frames"] = torch.tanh(mixed_frames)
            return outputs
        if self.waveform_decoder_mode == "periodic_plus_noise_residual":
            if (
                self.periodic_waveform_decoder is None
                or self.noise_residual_decoder is None
                or self.noise_residual_gate_head is None
                or self.noise_residual_scale is None
            ):
                raise RuntimeError("Periodic-plus-noise-residual decoder modules are not initialized.")
            conditioned_periodic_hidden = apply_decoder_branch_condition(
                periodic_hidden,
                branch_condition_gate,
                periodic_condition,
            )
            conditioned_noise_hidden = apply_decoder_branch_condition(
                noise_hidden,
                branch_condition_gate,
                noise_condition,
            )
            periodic_frames = self.periodic_waveform_decoder(conditioned_periodic_hidden)
            noise_residual = self.noise_residual_decoder(conditioned_noise_hidden)
            residual_gate_features = torch.cat(
                [
                    conditioned_noise_hidden,
                    outputs["periodic_gate"],
                    outputs["noise_gate"],
                ],
                dim=-1,
            )
            noise_residual_gate = torch.sigmoid(self.noise_residual_gate_head(residual_gate_features))
            residual_scale = self.noise_residual_scale.to(
                device=periodic_frames.device,
                dtype=periodic_frames.dtype,
            ).clamp(0.0, 2.0)
            waveform_frames = periodic_frames + residual_scale * noise_residual_gate * noise_residual
            outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
            outputs["noise_residual_frames"] = torch.tanh(noise_residual)
            outputs["noise_residual_gate"] = noise_residual_gate
            outputs["noise_residual_scale"] = residual_scale.view(1, 1, 1)
            outputs["waveform_frames"] = torch.tanh(waveform_frames)
            return outputs
        if (
            self.periodic_waveform_decoder is None
            or self.noise_residual_decoder is None
            or self.noise_residual_shape_head is None
            or self.noise_residual_scale is None
        ):
            raise RuntimeError("Periodic-plus-noise-residual-shape decoder modules are not initialized.")
        if self.waveform_decoder_mode == "periodic_plus_noise_residual_shape":
            conditioned_periodic_hidden = apply_decoder_branch_condition(
                periodic_hidden,
                branch_condition_gate,
                periodic_condition,
            )
            conditioned_noise_hidden = apply_decoder_branch_condition(
                noise_hidden,
                branch_condition_gate,
                noise_condition,
            )
            periodic_frames = self.periodic_waveform_decoder(conditioned_periodic_hidden)
            noise_residual = self.noise_residual_decoder(conditioned_noise_hidden)
            residual_shape_features = torch.cat(
                [
                    conditioned_periodic_hidden,
                    conditioned_noise_hidden,
                    outputs["periodic_gate"],
                    outputs["noise_gate"],
                ],
                dim=-1,
            )
            noise_residual_shape_logits = self.noise_residual_shape_head(residual_shape_features)
            if residual_shape_branch_condition_gate is not None and residual_shape_branch_condition_delta is not None:
                noise_residual_shape_logits = (
                    noise_residual_shape_logits
                    + residual_shape_branch_condition_gate * residual_shape_branch_condition_delta
                )
            noise_residual_shape = torch.sigmoid(noise_residual_shape_logits)
            residual_scale = self.noise_residual_scale.to(
                device=periodic_frames.device,
                dtype=periodic_frames.dtype,
            ).clamp(0.0, 2.0)
            waveform_frames = periodic_frames + residual_scale * noise_residual_shape * noise_residual
            outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
            outputs["noise_residual_frames"] = torch.tanh(noise_residual)
            outputs["noise_residual_shape"] = noise_residual_shape
            outputs["noise_residual_scale"] = residual_scale.view(1, 1, 1)
            outputs["waveform_frames"] = torch.tanh(waveform_frames)
            return outputs
        if self.waveform_decoder_mode == "periodic_plus_noise_factorized_residual":
            if (
                self.periodic_waveform_decoder is None
                or self.noise_residual_decoder is None
                or self.noise_residual_shape_head is None
                or self.noise_residual_gain_head is None
                or self.noise_residual_scale is None
            ):
                raise RuntimeError("Periodic-plus-noise-factorized-residual decoder modules are not initialized.")
            conditioned_periodic_hidden = apply_decoder_branch_condition(
                periodic_hidden,
                branch_condition_gate,
                periodic_condition,
            )
            conditioned_noise_hidden = apply_decoder_branch_condition(
                noise_hidden,
                branch_condition_gate,
                noise_condition,
            )
            periodic_frames = self.periodic_waveform_decoder(conditioned_periodic_hidden)
            noise_residual_shape_source = self.noise_residual_decoder(conditioned_noise_hidden)
            residual_features = torch.cat(
                [
                    conditioned_periodic_hidden,
                    conditioned_noise_hidden,
                    outputs["periodic_gate"],
                    outputs["noise_gate"],
                ],
                dim=-1,
            )
            noise_residual_envelope_logits = self.noise_residual_shape_head(residual_features)
            if residual_shape_branch_condition_gate is not None and residual_shape_branch_condition_delta is not None:
                noise_residual_envelope_logits = (
                    noise_residual_envelope_logits
                    + residual_shape_branch_condition_gate * residual_shape_branch_condition_delta
                )
            noise_residual_envelope = torch.sigmoid(noise_residual_envelope_logits)
            noise_residual_gain = torch.sigmoid(self.noise_residual_gain_head(residual_features))
            residual_scale = self.noise_residual_scale.to(
                device=periodic_frames.device,
                dtype=periodic_frames.dtype,
            ).clamp(0.0, 2.0)
            normalized_noise_shape = normalize_frames_unit_rms_local(noise_residual_shape_source)
            waveform_frames = (
                periodic_frames
                + residual_scale * noise_residual_gain * noise_residual_envelope * normalized_noise_shape
            )
            outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
            outputs["noise_residual_frames"] = torch.tanh(normalized_noise_shape)
            outputs["noise_residual_shape"] = noise_residual_envelope
            outputs["noise_residual_gain"] = noise_residual_gain
            outputs["noise_residual_scale"] = residual_scale.view(1, 1, 1)
            outputs["waveform_frames"] = torch.tanh(waveform_frames)
            return outputs
        if self.waveform_decoder_mode == "periodic_plus_noise_residual_shape_temporal":
            if (
                self.periodic_temporal_refiner is None
                or self.noise_temporal_refiner is None
                or self.periodic_waveform_decoder is None
                or self.noise_residual_decoder is None
                or self.noise_residual_shape_head is None
                or self.noise_residual_scale is None
            ):
                raise RuntimeError("Periodic-plus-noise-residual-shape-temporal decoder modules are not initialized.")
            temporal_periodic_hidden = periodic_hidden + apply_temporal_refiner(periodic_hidden, self.periodic_temporal_refiner)
            temporal_noise_hidden = noise_hidden + apply_temporal_refiner(noise_hidden, self.noise_temporal_refiner)
            temporal_periodic_hidden = apply_decoder_branch_condition(
                temporal_periodic_hidden,
                branch_condition_gate,
                periodic_condition,
            )
            temporal_noise_hidden = apply_decoder_branch_condition(
                temporal_noise_hidden,
                branch_condition_gate,
                noise_condition,
            )
            periodic_frames = self.periodic_waveform_decoder(temporal_periodic_hidden)
            noise_residual = self.noise_residual_decoder(temporal_noise_hidden)
            residual_features = torch.cat(
                [
                    temporal_periodic_hidden,
                    temporal_noise_hidden,
                    outputs["periodic_gate"],
                    outputs["noise_gate"],
                ],
                dim=-1,
            )
            noise_residual_envelope_logits = self.noise_residual_shape_head(residual_features)
            if residual_shape_branch_condition_gate is not None and residual_shape_branch_condition_delta is not None:
                noise_residual_envelope_logits = (
                    noise_residual_envelope_logits
                    + residual_shape_branch_condition_gate * residual_shape_branch_condition_delta
                )
            noise_residual_envelope = torch.sigmoid(noise_residual_envelope_logits)
            residual_scale = self.noise_residual_scale.to(
                device=periodic_frames.device,
                dtype=periodic_frames.dtype,
            ).clamp(0.0, 2.0)
            waveform_frames = periodic_frames + residual_scale * noise_residual_envelope * noise_residual
            outputs["temporal_periodic_hidden"] = temporal_periodic_hidden
            outputs["temporal_noise_hidden"] = temporal_noise_hidden
            outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
            outputs["noise_residual_frames"] = torch.tanh(noise_residual)
            outputs["noise_residual_shape"] = noise_residual_envelope
            outputs["noise_residual_scale"] = residual_scale.view(1, 1, 1)
            outputs["waveform_frames"] = torch.tanh(waveform_frames)
            return outputs
        if self.waveform_decoder_mode != "periodic_plus_noise_residual_shape_recurrent":
            raise RuntimeError(f"Unsupported waveform decoder mode at forward dispatch: {self.waveform_decoder_mode!r}")
        if (
            self.periodic_temporal_gru is None
            or self.noise_temporal_gru is None
            or self.periodic_waveform_decoder is None
            or self.noise_residual_decoder is None
            or self.noise_residual_shape_head is None
            or self.noise_residual_scale is None
        ):
            raise RuntimeError("Periodic-plus-noise-residual-shape-recurrent decoder modules are not initialized.")
        temporal_periodic_hidden = periodic_hidden + apply_gru_temporal_refiner(periodic_hidden, self.periodic_temporal_gru)
        temporal_noise_hidden = noise_hidden + apply_gru_temporal_refiner(noise_hidden, self.noise_temporal_gru)
        temporal_periodic_hidden = apply_decoder_branch_condition(
            temporal_periodic_hidden,
            branch_condition_gate,
            periodic_condition,
        )
        temporal_noise_hidden = apply_decoder_branch_condition(
            temporal_noise_hidden,
            branch_condition_gate,
            noise_condition,
        )
        periodic_frames = self.periodic_waveform_decoder(temporal_periodic_hidden)
        noise_residual = self.noise_residual_decoder(temporal_noise_hidden)
        residual_features = torch.cat(
            [
                temporal_periodic_hidden,
                temporal_noise_hidden,
                outputs["periodic_gate"],
                outputs["noise_gate"],
            ],
            dim=-1,
        )
        noise_residual_envelope_logits = self.noise_residual_shape_head(residual_features)
        if residual_shape_branch_condition_gate is not None and residual_shape_branch_condition_delta is not None:
            noise_residual_envelope_logits = (
                noise_residual_envelope_logits
                + residual_shape_branch_condition_gate * residual_shape_branch_condition_delta
            )
        noise_residual_envelope = torch.sigmoid(noise_residual_envelope_logits)
        residual_scale = self.noise_residual_scale.to(
            device=periodic_frames.device,
            dtype=periodic_frames.dtype,
        ).clamp(0.0, 2.0)
        waveform_frames = periodic_frames + residual_scale * noise_residual_envelope * noise_residual
        outputs["temporal_periodic_hidden"] = temporal_periodic_hidden
        outputs["temporal_noise_hidden"] = temporal_noise_hidden
        outputs["periodic_waveform_frames"] = torch.tanh(periodic_frames)
        outputs["noise_residual_frames"] = torch.tanh(noise_residual)
        outputs["noise_residual_shape"] = noise_residual_envelope
        outputs["noise_residual_scale"] = residual_scale.view(1, 1, 1)
        outputs["waveform_frames"] = torch.tanh(waveform_frames)
        return outputs


def prepare_offline_mvp_nores_vocoder_scaffold(
    scaffold_path: Path,
    output_dir: Path,
    hidden_dim: int,
    harmonic_bins: int,
    noise_bins: int,
) -> None:
    scaffold_path = scaffold_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = torch.load(scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported scaffold payload type: {type(payload)!r}")
    scaffold_version = str(payload.get("scaffold_version"))
    if scaffold_version not in SUPPORTED_TEACHER_VOCODER_SCAFFOLD_VERSIONS:
        raise ValueError(
            "Unsupported scaffold_version for no-residual vocoder scaffold: "
            f"{payload.get('scaffold_version')!r}"
        )

    branch_scaffold = dict(payload["branch_scaffold"])
    periodic_branch_features = branch_scaffold["periodic_branch_features"].to(torch.float32)
    noise_branch_features = branch_scaffold["noise_branch_features"].to(torch.float32)
    source_runtime = dict(payload.get("source_runtime", {}))
    frame_count = int(payload["frame_count"])
    decoder_frame_length = resolve_optional_positive_int(source_runtime.get("frame_length"))

    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(periodic_branch_features.shape[-1]),
        noise_input_dim=int(noise_branch_features.shape[-1]),
        hidden_dim=int(hidden_dim),
        harmonic_bins=int(harmonic_bins),
        noise_bins=int(noise_bins),
        frame_length=decoder_frame_length,
    )
    model.eval()
    with torch.no_grad():
        outputs = model(
            periodic_branch_features=periodic_branch_features,
            noise_branch_features=noise_branch_features,
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_scaffold_path": scaffold_path.as_posix(),
        "model": {
            "name": "no_residual_source_filter_vocoder_scaffold",
            "hidden_dim": int(hidden_dim),
            "harmonic_bins": int(harmonic_bins),
            "noise_bins": int(noise_bins),
            "decoder_frame_length": decoder_frame_length,
            "fusion_mode": model.fusion_mode,
            "waveform_decoder_mode": model.waveform_decoder_mode,
        },
        "input_contract": {
            "frame_count": frame_count,
            "periodic_input_dim": int(periodic_branch_features.shape[-1]),
            "noise_input_dim": int(noise_branch_features.shape[-1]),
            "missing_periodic_design_keys": list(branch_scaffold.get("missing_periodic_design_keys", [])),
            "missing_noise_design_keys": list(branch_scaffold.get("missing_noise_design_keys", [])),
        },
        "output_shapes": {
            key: list(value.shape)
            for key, value in outputs.items()
        },
        "notes": (
            [
                "This scaffold is a shape-verified Stage5 code anchor, not a trained vocoder.",
                "The periodic branch now consumes explicit f0_hz / vuv / E controls from the C-prime v2-core contract.",
                (
                    "The noise branch now consumes explicit bootstrap e_evt while still omitting r_res by construction, so this remains the no-residual baseline route."
                    if scaffold_version in {
                        "offline_teacher_vocoder_input_scaffold_v3",
                        "streaming_student_vocoder_input_scaffold_v1",
                    }
                    else "The noise branch still omits r_res by construction and should be treated as the no-residual baseline route."
                ),
                "When source_runtime.frame_length is available, the scaffold also exposes a minimal per-frame waveform decoder head for later waveform/STFT bootstrap experiments.",
            ]
            if scaffold_version in {
                "offline_teacher_vocoder_input_scaffold_v2",
                "offline_teacher_vocoder_input_scaffold_v3",
                "streaming_student_vocoder_input_scaffold_v1",
            }
            else [
                "This scaffold is a shape-verified Stage5 code anchor, not a trained vocoder.",
                "The periodic branch currently consumes proxy voiced/energy features because explicit f0_hz is still unavailable in the teacher-first path.",
                "The noise branch currently omits r_res by construction and should be treated as the no-residual baseline route.",
                "When source_runtime.frame_length is available, the scaffold also exposes a minimal per-frame waveform decoder head for later waveform/STFT bootstrap experiments.",
            ]
        ),
    }

    pt_path = output_dir / "offline_mvp_nores_vocoder_scaffold.pt"
    json_path = output_dir / "offline_mvp_nores_vocoder_scaffold.json"
    md_path = output_dir / "offline_mvp_nores_vocoder_scaffold.md"
    torch.save(
        {
            "scaffold_version": "offline_mvp_nores_vocoder_scaffold_v1",
            "model_state_dict": model.state_dict(),
            "summary": summary,
            "outputs": {key: value.detach().cpu() for key, value in outputs.items()},
        },
        pt_path,
    )
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_mlp(input_dim: int, hidden_dim: int, output_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.GELU(),
        nn.LayerNorm(hidden_dim),
        nn.Linear(hidden_dim, output_dim),
    )


def infer_waveform_decoder_mode_from_state_dict(state_dict: dict[str, torch.Tensor]) -> str:
    if "periodic_temporal_gru.weight_ih_l0" in state_dict:
        return "periodic_plus_noise_residual_shape_recurrent"
    if "periodic_temporal_refiner.0.weight" in state_dict:
        return "periodic_plus_noise_residual_shape_temporal"
    if "noise_residual_gain_head.0.weight" in state_dict:
        return "periodic_plus_noise_factorized_residual"
    if "noise_residual_shape_head.0.weight" in state_dict:
        return "periodic_plus_noise_residual_shape"
    if "noise_residual_decoder.0.weight" in state_dict:
        return "periodic_plus_noise_residual"
    if "periodic_waveform_decoder.0.weight" in state_dict:
        return "dual_branch_mix"
    return "fused_single"


def infer_fusion_mode_from_state_dict(state_dict: dict[str, torch.Tensor]) -> str:
    if "fusion_branch_mean_contrast_norm.weight" in state_dict:
        return "branch_mean_contrast_residual_v1"
    if "fusion_periodic_residual_adapter.0.weight" in state_dict:
        return "periodic_residual_v1"
    if "fusion_branch_mean_residual.0.weight" in state_dict:
        return "branch_mean_residual_v1"
    return "plain"


def infer_decoder_branch_condition_adapter_from_state_dict(state_dict: dict[str, torch.Tensor]) -> bool:
    return "decoder_branch_condition_adapter.0.weight" in state_dict


def infer_residual_shape_branch_condition_adapter_from_state_dict(state_dict: dict[str, torch.Tensor]) -> bool:
    return "residual_shape_branch_condition_adapter.0.weight" in state_dict


def build_nores_vocoder_scaffold_from_state_dict(
    *,
    state_dict: dict[str, torch.Tensor],
    periodic_input_dim: int,
    noise_input_dim: int,
    frame_length: int,
) -> NoResidualSourceFilterVocoderScaffold:
    hidden_dim = int(state_dict["periodic_encoder.0.weight"].shape[0])
    harmonic_bins = int(state_dict["harmonic_envelope.weight"].shape[0])
    noise_bins = int(state_dict["noise_envelope.weight"].shape[0])
    return NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(periodic_input_dim),
        noise_input_dim=int(noise_input_dim),
        hidden_dim=hidden_dim,
        harmonic_bins=harmonic_bins,
        noise_bins=noise_bins,
        frame_length=int(frame_length),
        fusion_mode=infer_fusion_mode_from_state_dict(state_dict),
        waveform_decoder_mode=infer_waveform_decoder_mode_from_state_dict(state_dict),
        use_decoder_branch_condition_adapter=infer_decoder_branch_condition_adapter_from_state_dict(state_dict),
        use_residual_shape_branch_condition_adapter=infer_residual_shape_branch_condition_adapter_from_state_dict(
            state_dict
        ),
    )


def apply_decoder_branch_condition(
    base_hidden: torch.Tensor,
    branch_condition_gate: torch.Tensor | None,
    branch_condition_hidden: torch.Tensor | None,
) -> torch.Tensor:
    if branch_condition_gate is None or branch_condition_hidden is None:
        return base_hidden
    return base_hidden + branch_condition_gate * branch_condition_hidden


def normalize_waveform_decoder_mode(waveform_decoder_mode: str) -> str:
    resolved = str(waveform_decoder_mode).strip().lower()
    if resolved not in SUPPORTED_WAVEFORM_DECODER_MODES:
        raise ValueError(
            "Unsupported waveform_decoder_mode for no-residual vocoder scaffold: "
            f"{waveform_decoder_mode!r}"
        )
    return resolved


def normalize_fusion_mode(fusion_mode: str) -> str:
    resolved = str(fusion_mode).strip().lower()
    if resolved not in SUPPORTED_FUSION_MODES:
        raise ValueError(
            "Unsupported fusion_mode for no-residual vocoder scaffold: "
            f"{fusion_mode!r}"
        )
    return resolved


def normalize_frames_unit_rms_local(frames: torch.Tensor) -> torch.Tensor:
    frames_tensor = frames.to(torch.float32)
    centered = frames_tensor - frames_tensor.mean(dim=-1, keepdim=True)
    frame_rms = centered.pow(2).mean(dim=-1, keepdim=True).sqrt().clamp_min(1.0e-6)
    return centered / frame_rms


def build_temporal_refiner(hidden_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, padding=2),
        nn.GELU(),
        nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
    )


def apply_temporal_refiner(sequence: torch.Tensor, refiner: nn.Module) -> torch.Tensor:
    if sequence.dim() == 2:
        sequence_batched = sequence.unsqueeze(0)
        refined = refiner(sequence_batched.transpose(1, 2)).transpose(1, 2)
        return refined.squeeze(0)
    if sequence.dim() == 3:
        return refiner(sequence.transpose(1, 2)).transpose(1, 2)
    raise ValueError(f"Unsupported sequence rank for temporal refinement: {tuple(sequence.shape)}")


def apply_gru_temporal_refiner(sequence: torch.Tensor, gru: nn.GRU) -> torch.Tensor:
    if sequence.dim() == 2:
        refined, _ = gru(sequence.unsqueeze(0))
        return refined.squeeze(0)
    if sequence.dim() == 3:
        refined, _ = gru(sequence)
        return refined
    raise ValueError(f"Unsupported sequence rank for GRU temporal refinement: {tuple(sequence.shape)}")


def resolve_optional_positive_int(value: object) -> int | None:
    if value in {None, ""}:
        return None
    resolved = int(value)
    if resolved <= 0:
        return None
    return resolved


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Scaffold",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- input_scaffold_path: {summary['input_scaffold_path']}",
        f"- model: {json.dumps(summary['model'], ensure_ascii=False)}",
        f"- input_contract: {json.dumps(summary['input_contract'], ensure_ascii=False)}",
        f"- output_shapes: {json.dumps(summary['output_shapes'], ensure_ascii=False)}",
        "",
        "## Notes",
    ]
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
