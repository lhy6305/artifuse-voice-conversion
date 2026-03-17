from __future__ import annotations

import torch
from torch import nn

from v5vc.offline_mvp.model import frame_waveform


class UnifiedStreamingFrontend(nn.Module):
    def __init__(
        self,
        shared_dim: int,
        frontend_dim: int,
        frontend_layers: int,
        frame_length: int,
        hop_length: int,
        event_prior_dim: int,
    ) -> None:
        super().__init__()
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.input_proj = nn.Linear(2, frontend_dim)
        self.input_norm = nn.LayerNorm(frontend_dim)
        self.encoder = build_mlp(
            input_dim=frontend_dim,
            hidden_dim=frontend_dim,
            output_dim=shared_dim,
            num_layers=frontend_layers,
        )
        self.log_f0_head = nn.Linear(shared_dim, 1)
        self.vuv_head = nn.Linear(shared_dim, 1)
        self.aper_head = nn.Linear(shared_dim, 1)
        self.energy_head = nn.Linear(shared_dim, 1)
        self.event_prior_head = nn.Linear(shared_dim, event_prior_dim)

    def forward(
        self,
        waveform: torch.Tensor,
        lengths: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        frames, frame_mask = frame_waveform(
            waveform=waveform,
            lengths=lengths,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
        )
        hidden = self.input_norm(self.input_proj(frames))
        shared_hidden = self.encoder(hidden)
        return {
            "frame_mask": frame_mask,
            "frame_features": frames,
            "shared_hidden": shared_hidden,
            "coarse_log_f0": self.log_f0_head(shared_hidden),
            "vuv_logits": self.vuv_head(shared_hidden),
            "aperiodicity": self.aper_head(shared_hidden),
            "energy": self.energy_head(shared_hidden),
            "event_prior_logits": self.event_prior_head(shared_hidden),
        }


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
        r_res_dim: int,
        r_res_enabled: bool,
        f0_correction_enabled: bool,
        aper_correction_enabled: bool,
    ) -> None:
        super().__init__()
        self.r_res_enabled = r_res_enabled
        self.f0_correction_enabled = f0_correction_enabled
        self.aper_correction_enabled = aper_correction_enabled
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
        self.z_art_head = nn.Linear(student_dim, z_art_dim)
        self.event_head = nn.Linear(student_dim, event_dim)
        self.r_res_head = nn.Linear(student_dim, r_res_dim) if r_res_enabled else None
        self.f0_delta_head = nn.Linear(student_dim, 1) if f0_correction_enabled else None
        self.aper_delta_head = nn.Linear(student_dim, 1) if aper_correction_enabled else None

    def forward(
        self,
        frontend_outputs: dict[str, torch.Tensor],
        speaker_embedding: torch.Tensor,
        geom_embedding: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        shared_hidden = frontend_outputs["shared_hidden"]
        batch_size, frame_count, _ = shared_hidden.shape
        conditioning = self.condition_proj(torch.cat([speaker_embedding, geom_embedding], dim=-1))
        conditioning = conditioning.unsqueeze(1).expand(batch_size, frame_count, conditioning.shape[-1])
        frontend_controls = torch.cat(
            [
                frontend_outputs["coarse_log_f0"],
                torch.sigmoid(frontend_outputs["vuv_logits"]),
                frontend_outputs["aperiodicity"],
                frontend_outputs["energy"],
                torch.sigmoid(frontend_outputs["event_prior_logits"]),
            ],
            dim=-1,
        )
        student_input = torch.cat([shared_hidden, conditioning, frontend_controls], dim=-1)
        student_hidden = self.student_encoder(self.student_norm(self.student_input_proj(student_input)))
        event_logits = self.event_head(student_hidden)
        outputs = {
            "student_hidden": student_hidden,
            "conditioning": conditioning,
            "z_art": self.z_art_head(student_hidden),
            "event_logits": event_logits,
            "event_probs": torch.sigmoid(event_logits),
        }
        if self.r_res_head is None:
            outputs["r_res"] = student_hidden.new_zeros((batch_size, frame_count, 0))
        else:
            outputs["r_res"] = self.r_res_head(student_hidden)
        if self.f0_delta_head is None:
            outputs["log_f0_correction"] = student_hidden.new_zeros((batch_size, frame_count, 1))
        else:
            outputs["log_f0_correction"] = self.f0_delta_head(student_hidden)
        if self.aper_delta_head is None:
            outputs["aper_correction"] = student_hidden.new_zeros((batch_size, frame_count, 1))
        else:
            outputs["aper_correction"] = self.aper_delta_head(student_hidden)
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
        r_res_dim: int,
        frame_length: int,
        hop_length: int,
        r_res_enabled: bool,
        f0_correction_enabled: bool,
        aper_correction_enabled: bool,
    ) -> None:
        super().__init__()
        self.frontend = UnifiedStreamingFrontend(
            shared_dim=shared_dim,
            frontend_dim=frontend_dim,
            frontend_layers=frontend_layers,
            frame_length=frame_length,
            hop_length=hop_length,
            event_prior_dim=event_prior_dim,
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
            r_res_dim=r_res_dim,
            r_res_enabled=r_res_enabled,
            f0_correction_enabled=f0_correction_enabled,
            aper_correction_enabled=aper_correction_enabled,
        )

    def forward(
        self,
        waveform: torch.Tensor,
        lengths: torch.Tensor,
        speaker_embedding: torch.Tensor,
        geom_embedding: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        frontend_outputs = self.frontend(waveform=waveform, lengths=lengths)
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
