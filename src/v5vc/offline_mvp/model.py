from __future__ import annotations

import torch
from torch import nn


class OfflineMVPNoResidualModel(nn.Module):
    def __init__(
        self,
        hidden_dim: int,
        z_art_dim: int,
        event_dim: int,
        acoustic_dim: int,
        frame_length: int,
        hop_length: int,
        text_aux_dim: int = 3,
        text_aux_head_config: dict[str, object] | None = None,
    ) -> None:
        super().__init__()
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.text_aux_dim = text_aux_dim
        self.input_proj = nn.Linear(2, hidden_dim)
        self.encoder = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.z_art_head = nn.Linear(hidden_dim, z_art_dim)
        self.event_head = nn.Linear(hidden_dim, event_dim)
        self.z_art_to_hidden = nn.Linear(z_art_dim, hidden_dim)
        self.event_to_hidden = nn.Linear(event_dim, hidden_dim)
        self.fusion = nn.Sequential(
            nn.LayerNorm(hidden_dim * 3),
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.acoustic_head = nn.Linear(hidden_dim, acoustic_dim)
        self.text_aux_head_config = normalize_text_aux_head_config(
            text_aux_head_config=text_aux_head_config,
            text_aux_dim=text_aux_dim,
        )
        if self.text_aux_head_config is None:
            self.text_aux_head = nn.Linear(hidden_dim, text_aux_dim)
            self.text_aux_structural_head = None
            self.text_aux_lexical_head = None
        else:
            self.text_aux_head = None
            structural_dim_count = len(self.text_aux_head_config["structural_dimensions"])
            lexical_dim_count = len(self.text_aux_head_config["lexical_dimensions"])
            self.text_aux_structural_head = (
                nn.Linear(hidden_dim, structural_dim_count) if structural_dim_count > 0 else None
            )
            self.text_aux_lexical_head = (
                nn.Linear(hidden_dim, lexical_dim_count) if lexical_dim_count > 0 else None
            )

    def forward(
        self,
        waveform: torch.Tensor,
        lengths: torch.Tensor,
        ablation_mode: str = "none",
    ) -> dict[str, torch.Tensor]:
        frames, frame_mask = frame_waveform(
            waveform=waveform,
            lengths=lengths,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
        )
        hidden = self.input_proj(frames)
        hidden = self.encoder(hidden)
        z_art = self.z_art_head(hidden)
        event_logits = self.event_head(hidden)
        event_probs = torch.sigmoid(event_logits)
        z_art_hidden = self.z_art_to_hidden(z_art)
        event_hidden = self.event_to_hidden(event_probs)
        zero_z_art_hidden = torch.zeros_like(z_art_hidden)
        zero_event_hidden = torch.zeros_like(event_hidden)
        fused_hidden_with_z_art = fuse_control_hidden(
            fusion=self.fusion,
            hidden=hidden,
            z_art_hidden=z_art_hidden,
            event_hidden=event_hidden,
        )
        fused_hidden_zero_z_art = fuse_control_hidden(
            fusion=self.fusion,
            hidden=hidden,
            z_art_hidden=zero_z_art_hidden,
            event_hidden=event_hidden,
        )
        fused_hidden_zero_e_evt = fuse_control_hidden(
            fusion=self.fusion,
            hidden=hidden,
            z_art_hidden=z_art_hidden,
            event_hidden=zero_event_hidden,
        )
        fused_hidden_zero_both = fuse_control_hidden(
            fusion=self.fusion,
            hidden=hidden,
            z_art_hidden=zero_z_art_hidden,
            event_hidden=zero_event_hidden,
        )
        fused_hidden = select_fused_hidden_for_ablation(
            ablation_mode=ablation_mode,
            fused_hidden_with_z_art=fused_hidden_with_z_art,
            fused_hidden_zero_z_art=fused_hidden_zero_z_art,
            fused_hidden_zero_e_evt=fused_hidden_zero_e_evt,
            fused_hidden_zero_both=fused_hidden_zero_both,
        )
        acoustic = self.acoustic_head(fused_hidden)
        pooled_hidden = masked_mean(fused_hidden, frame_mask)
        text_aux = build_text_aux_output(
            pooled_hidden=pooled_hidden,
            text_aux_dim=self.text_aux_dim,
            default_head=self.text_aux_head,
            structural_head=self.text_aux_structural_head,
            lexical_head=self.text_aux_lexical_head,
            head_config=self.text_aux_head_config,
        )
        return {
            "frame_mask": frame_mask,
            "hidden": hidden,
            "fused_hidden": fused_hidden,
            "fused_hidden_with_z_art": fused_hidden_with_z_art,
            "fused_hidden_zero_z_art": fused_hidden_zero_z_art,
            "fused_hidden_zero_e_evt": fused_hidden_zero_e_evt,
            "z_art": z_art,
            "event_logits": event_logits,
            "event_probs": event_probs,
            "acoustic": acoustic,
            "text_aux": text_aux,
            "ablation_mode": ablation_mode,
        }


def normalize_text_aux_head_config(
    text_aux_head_config: dict[str, object] | None,
    text_aux_dim: int,
) -> dict[str, object] | None:
    if not isinstance(text_aux_head_config, dict) or not bool(text_aux_head_config.get("enabled", False)):
        return None
    mode = str(text_aux_head_config.get("mode", "split_heads"))
    if mode != "split_heads":
        raise ValueError(f"Unsupported text_aux_head_config.mode: {mode}")
    structural_dimensions = normalize_dimension_list(
        raw_dimensions=text_aux_head_config.get("structural_dimensions"),
        text_aux_dim=text_aux_dim,
        field_name="model.text_aux_head_config.structural_dimensions",
    )
    lexical_dimensions = normalize_dimension_list(
        raw_dimensions=text_aux_head_config.get("lexical_dimensions"),
        text_aux_dim=text_aux_dim,
        field_name="model.text_aux_head_config.lexical_dimensions",
    )
    overlap = set(structural_dimensions) & set(lexical_dimensions)
    if overlap:
        raise ValueError(f"text_aux_head_config dimensions overlap: {sorted(overlap)}")
    if len(structural_dimensions) + len(lexical_dimensions) != text_aux_dim:
        raise ValueError(
            "text_aux_head_config dimensions must cover the full text_aux output: "
            f"{len(structural_dimensions) + len(lexical_dimensions)} != {text_aux_dim}"
        )
    return {
        "mode": mode,
        "structural_dimensions": structural_dimensions,
        "lexical_dimensions": lexical_dimensions,
        "structural_detach_shared_input": bool(
            text_aux_head_config.get("structural_detach_shared_input", False)
        ),
        "lexical_detach_shared_input": bool(text_aux_head_config.get("lexical_detach_shared_input", False)),
    }


def normalize_dimension_list(
    raw_dimensions: object,
    text_aux_dim: int,
    field_name: str,
) -> list[int]:
    if not isinstance(raw_dimensions, list) or not raw_dimensions:
        raise ValueError(f"{field_name} must be a non-empty list.")
    normalized: list[int] = []
    seen: set[int] = set()
    for raw_value in raw_dimensions:
        index = int(raw_value)
        if index < 0 or index >= text_aux_dim:
            raise ValueError(f"{field_name} contains out-of-range index: {index}")
        if index in seen:
            continue
        normalized.append(index)
        seen.add(index)
    return normalized


def build_text_aux_output(
    pooled_hidden: torch.Tensor,
    text_aux_dim: int,
    default_head: nn.Linear | None,
    structural_head: nn.Linear | None,
    lexical_head: nn.Linear | None,
    head_config: dict[str, object] | None,
) -> torch.Tensor:
    if head_config is None:
        if default_head is None:
            raise ValueError("text_aux default head is missing.")
        return default_head(pooled_hidden)
    text_aux = torch.zeros(
        (pooled_hidden.shape[0], text_aux_dim),
        device=pooled_hidden.device,
        dtype=pooled_hidden.dtype,
    )
    structural_dimensions = list(head_config["structural_dimensions"])
    if structural_dimensions:
        if structural_head is None:
            raise ValueError("text_aux structural head is missing.")
        structural_input = pooled_hidden.detach() if bool(head_config["structural_detach_shared_input"]) else pooled_hidden
        structural_output = structural_head(structural_input)
        text_aux[:, structural_dimensions] = structural_output
    lexical_dimensions = list(head_config["lexical_dimensions"])
    if lexical_dimensions:
        if lexical_head is None:
            raise ValueError("text_aux lexical head is missing.")
        lexical_input = pooled_hidden.detach() if bool(head_config["lexical_detach_shared_input"]) else pooled_hidden
        lexical_output = lexical_head(lexical_input)
        text_aux[:, lexical_dimensions] = lexical_output
    return text_aux


def frame_waveform(
    waveform: torch.Tensor,
    lengths: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if waveform.ndim != 2:
        raise ValueError(f"Expected waveform shape [B, T], got {tuple(waveform.shape)}")
    padded = waveform
    total_length = padded.shape[1]
    if total_length < frame_length:
        pad = frame_length - total_length
        padded = torch.nn.functional.pad(padded, (0, pad))
        total_length = padded.shape[1]

    frames = padded.unfold(dimension=1, size=frame_length, step=hop_length)
    energy = frames.pow(2).mean(dim=-1).clamp_min(1e-8).log10()
    abs_mean = frames.abs().mean(dim=-1)
    features = torch.stack([energy, abs_mean], dim=-1)

    frame_lengths = ((lengths - frame_length).clamp_min(0) // hop_length) + 1
    max_frames = features.shape[1]
    frame_mask = (
        torch.arange(max_frames, device=waveform.device)[None, :]
        < frame_lengths[:, None]
    )
    return features, frame_mask


def masked_mean(hidden: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    weights = mask.to(hidden.dtype).unsqueeze(-1)
    summed = (hidden * weights).sum(dim=1)
    denom = weights.sum(dim=1).clamp_min(1.0)
    return summed / denom


def fuse_control_hidden(
    fusion: nn.Sequential,
    hidden: torch.Tensor,
    z_art_hidden: torch.Tensor,
    event_hidden: torch.Tensor,
) -> torch.Tensor:
    return fusion(torch.cat([hidden, z_art_hidden, event_hidden], dim=-1))


def select_fused_hidden_for_ablation(
    ablation_mode: str,
    fused_hidden_with_z_art: torch.Tensor,
    fused_hidden_zero_z_art: torch.Tensor,
    fused_hidden_zero_e_evt: torch.Tensor,
    fused_hidden_zero_both: torch.Tensor,
) -> torch.Tensor:
    if ablation_mode == "none":
        return fused_hidden_with_z_art
    if ablation_mode == "zero_z_art":
        return fused_hidden_zero_z_art
    if ablation_mode == "zero_e_evt":
        return fused_hidden_zero_e_evt
    if ablation_mode == "zero_both":
        return fused_hidden_zero_both
    raise ValueError(f"Unsupported ablation_mode: {ablation_mode}")


def apply_control_ablation(
    z_art: torch.Tensor,
    event_probs: torch.Tensor,
    ablation_mode: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    if ablation_mode == "none":
        return z_art, event_probs
    if ablation_mode == "zero_z_art":
        return torch.zeros_like(z_art), event_probs
    if ablation_mode == "zero_e_evt":
        return z_art, torch.zeros_like(event_probs)
    if ablation_mode == "zero_both":
        return torch.zeros_like(z_art), torch.zeros_like(event_probs)
    raise ValueError(f"Unsupported ablation_mode: {ablation_mode}")
