from __future__ import annotations

from copy import deepcopy

import torch
import torch.nn.functional as F

from v5vc.offline_mvp.model import frame_waveform

PUNCTUATION_PROFILE_SET = "\uFF0C\u3002\uFF1F\uFF01\uFF1B\uFF1A\u3001"
BOUNDARY_SYMBOL_TYPES = (
    "pause_comma",
    "pause_enumeration",
    "pause_semicolon",
    "pause_colon",
    "terminal_period",
    "terminal_question",
    "terminal_exclamation",
)
CLAUSE_ROLES = (
    "single",
    "initial",
    "middle",
    "final",
)
UTTERANCE_STRUCTURE_TYPES = (
    "nonverbal",
    "single_clause_terminal",
    "multi_clause_single_terminal",
    "multi_terminal",
    "other",
)


def build_frame_targets(
    waveform: torch.Tensor,
    lengths: torch.Tensor,
    frame_length: int,
    hop_length: int,
    weak_event_hints: list[dict[str, object] | None] | None = None,
) -> dict[str, torch.Tensor]:
    features, frame_mask = frame_waveform(
        waveform=waveform,
        lengths=lengths,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    energy = features[..., 0]
    abs_mean = features[..., 1]
    delta_energy = torch.zeros_like(energy)
    delta_energy[:, 1:] = energy[:, 1:] - energy[:, :-1]
    zero_cross = estimate_zero_cross_rate(
        waveform=waveform,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    energy_norm = torch.sigmoid((energy + 4.0) * 2.0)
    acoustic_target = torch.stack(
        [
            energy,
            abs_mean,
            zero_cross,
            delta_energy,
        ],
        dim=-1,
    )
    event_target = torch.stack(
        [
            (energy > -3.5).to(torch.float32),
            (delta_energy.abs() > 0.12).to(torch.float32),
            (zero_cross > 0.18).to(torch.float32),
            ((zero_cross < 0.1) & (energy > -3.8)).to(torch.float32),
            ((zero_cross >= 0.1) & (energy > -3.8)).to(torch.float32),
            torch.sigmoid(delta_energy * 5.0),
            torch.sigmoid(-delta_energy * 5.0),
            energy_norm,
        ],
        dim=-1,
    )
    result = {
        "frame_mask": frame_mask,
        "acoustic_target": acoustic_target,
        "event_target": event_target,
    }
    if weak_event_hints is not None:
        (
            weak_event_target,
            weak_event_weight,
            pause_boundary_strength,
            terminal_boundary_strength,
            boundary_type_strengths,
            clause_role_strengths,
            clause_transition_strengths,
            utterance_structure_strengths,
        ) = build_weak_event_boundary_targets(
            weak_event_hints=weak_event_hints,
            frame_mask=frame_mask,
        )
        result["weak_event_target"] = weak_event_target
        result["weak_event_weight"] = weak_event_weight
        result["pause_boundary_strength"] = pause_boundary_strength
        result["terminal_boundary_strength"] = terminal_boundary_strength
        result["boundary_type_strengths"] = boundary_type_strengths
        result["clause_role_strengths"] = clause_role_strengths
        result["clause_transition_strengths"] = clause_transition_strengths
        result["utterance_structure_strengths"] = utterance_structure_strengths
    return result


def estimate_zero_cross_rate(
    waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    padded = waveform
    total_length = padded.shape[1]
    if total_length < frame_length:
        pad = frame_length - total_length
        padded = F.pad(padded, (0, pad))
    frames = padded.unfold(dimension=1, size=frame_length, step=hop_length)
    signs = torch.sign(frames)
    signs[signs == 0] = 1
    zero_cross = (signs[..., 1:] != signs[..., :-1]).to(torch.float32).mean(dim=-1)
    return zero_cross


def compute_offline_mvp_loss(
    outputs: dict[str, torch.Tensor],
    acoustic_target: torch.Tensor,
    event_target: torch.Tensor,
    frame_mask: torch.Tensor,
    text_aux_target: torch.Tensor | None,
    texts: list[str] | None,
    weights: dict[str, object],
    target_special_supervision: list[dict[str, object] | None] | None = None,
    weak_event_target: torch.Tensor | None = None,
    weak_event_weight: torch.Tensor | None = None,
    pause_boundary_strength: torch.Tensor | None = None,
    terminal_boundary_strength: torch.Tensor | None = None,
    boundary_type_strengths: dict[str, torch.Tensor] | None = None,
    clause_role_strengths: dict[str, torch.Tensor] | None = None,
    clause_transition_strengths: dict[str, torch.Tensor] | None = None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    mask = frame_mask.to(outputs["acoustic"].dtype).unsqueeze(-1)
    frame_count = mask.sum().clamp_min(1.0)

    acoustic_loss = (((outputs["acoustic"] - acoustic_target) ** 2) * mask).sum() / frame_count
    event_target, event_loss_bias = apply_event_boundary_bias(
        event_target=event_target,
        weights=weights,
        pause_boundary_strength=pause_boundary_strength,
        terminal_boundary_strength=terminal_boundary_strength,
        boundary_type_strengths=boundary_type_strengths,
        clause_role_strengths=clause_role_strengths,
        clause_transition_strengths=clause_transition_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
    )
    event_loss_raw = F.binary_cross_entropy_with_logits(
        outputs["event_logits"],
        event_target,
        reduction="none",
    )
    event_dimension_weights = build_event_dimension_weights(
        weights=weights,
        event_logits=outputs["event_logits"],
    )
    if event_loss_bias is None:
        event_loss = ((event_loss_raw * event_dimension_weights) * mask).sum() / frame_count
    else:
        event_loss = ((event_loss_raw * event_dimension_weights * event_loss_bias) * mask).sum() / frame_count
    z_art = outputs["z_art"]
    if z_art.shape[1] > 1:
        smooth_mask = (frame_mask[:, 1:] & frame_mask[:, :-1]).to(z_art.dtype).unsqueeze(-1)
        smooth_count = smooth_mask.sum().clamp_min(1.0)
        z_smooth_loss = ((z_art[:, 1:] - z_art[:, :-1]).abs() * smooth_mask).sum() / smooth_count
    else:
        z_smooth_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)

    if text_aux_target is not None:
        text_aux_loss_raw = F.mse_loss(outputs["text_aux"], text_aux_target)
        text_aux_split_config = build_text_aux_split_config(
            weights=weights,
            text_aux_target=text_aux_target,
        )
        if text_aux_split_config is not None:
            structural_loss, lexical_loss, text_aux_loss = compute_text_aux_split_losses(
                outputs=outputs,
                text_aux_target=text_aux_target,
                split_config=text_aux_split_config,
            )
        else:
            structural_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)
            lexical_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)
            text_aux_dimension_weights = build_text_aux_dimension_weights(
                weights=weights,
                text_aux_target=text_aux_target,
            )
            if text_aux_dimension_weights is None:
                text_aux_loss = text_aux_loss_raw
            else:
                squared_error = (outputs["text_aux"] - text_aux_target) ** 2
                normalized_weights = text_aux_dimension_weights / text_aux_dimension_weights.sum().clamp_min(1.0e-8)
                text_aux_loss = (squared_error * normalized_weights.unsqueeze(0)).sum(dim=-1).mean()
    else:
        text_aux_loss_raw = torch.zeros((), device=z_art.device, dtype=z_art.dtype)
        structural_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)
        lexical_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)
        text_aux_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)

    if weak_event_target is not None and weak_event_weight is not None:
        event_presence = torch.amax(torch.sigmoid(outputs["event_logits"]), dim=-1)
        effective_weight = weak_event_weight * frame_mask.to(event_presence.dtype)
        positive_count = effective_weight.sum().clamp_min(1.0)
        weak_event_loss = (((1.0 - event_presence) ** 2) * effective_weight).sum() / positive_count
    else:
        weak_event_loss = torch.zeros((), device=z_art.device, dtype=z_art.dtype)

    clause_transition_aux_loss = compute_clause_transition_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        clause_transition_strengths=clause_transition_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
        weights=weights,
    )
    structural_clause_transition_aux_loss = compute_structural_clause_transition_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        clause_transition_strengths=clause_transition_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    boundary_contrast_aux_loss = compute_boundary_contrast_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        pause_boundary_strength=pause_boundary_strength,
        terminal_boundary_strength=terminal_boundary_strength,
        weights=weights,
    )
    punctuation_profile_aux_loss = compute_punctuation_profile_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        texts=texts,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    structural_clause_profile_aux_loss = compute_structural_clause_profile_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    challenge_proxy_profile_aux_loss = compute_challenge_proxy_profile_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    singleton_sparse_proxy_aux_loss = compute_singleton_sparse_proxy_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    z_art_influence_aux_loss = compute_z_art_influence_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        target_special_supervision=target_special_supervision,
        weights=weights,
    )
    formal_special_clause_shape_aux_loss = compute_formal_special_clause_shape_aux_loss(
        outputs=outputs,
        frame_mask=frame_mask,
        target_special_supervision=target_special_supervision,
        clause_role_strengths=clause_role_strengths,
        clause_transition_strengths=clause_transition_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
        weights=weights,
    )
    clause_transition_aux_config = weights.get("clause_transition_aux")
    clause_transition_aux_weight = 0.0
    if isinstance(clause_transition_aux_config, dict):
        clause_transition_aux_weight = float(clause_transition_aux_config.get("weight", 0.0))
    structural_clause_transition_aux_config = weights.get("structural_clause_transition_aux")
    structural_clause_transition_aux_weight = 0.0
    if isinstance(structural_clause_transition_aux_config, dict):
        structural_clause_transition_aux_weight = float(structural_clause_transition_aux_config.get("weight", 0.0))
    boundary_contrast_aux_config = weights.get("boundary_contrast_aux")
    boundary_contrast_aux_weight = 0.0
    if isinstance(boundary_contrast_aux_config, dict):
        boundary_contrast_aux_weight = float(boundary_contrast_aux_config.get("weight", 0.0))
    punctuation_profile_aux_config = weights.get("punctuation_profile_aux")
    punctuation_profile_aux_weight = 0.0
    if isinstance(punctuation_profile_aux_config, dict):
        punctuation_profile_aux_weight = float(punctuation_profile_aux_config.get("weight", 0.0))
    structural_clause_profile_aux_config = weights.get("structural_clause_profile_aux")
    structural_clause_profile_aux_weight = 0.0
    if isinstance(structural_clause_profile_aux_config, dict):
        structural_clause_profile_aux_weight = float(structural_clause_profile_aux_config.get("weight", 0.0))
    challenge_proxy_profile_aux_config = weights.get("challenge_proxy_profile_aux")
    challenge_proxy_profile_aux_weight = 0.0
    if isinstance(challenge_proxy_profile_aux_config, dict):
        challenge_proxy_profile_aux_weight = float(challenge_proxy_profile_aux_config.get("weight", 0.0))
    singleton_sparse_proxy_aux_config = weights.get("singleton_sparse_proxy_aux")
    singleton_sparse_proxy_aux_weight = 0.0
    if isinstance(singleton_sparse_proxy_aux_config, dict):
        singleton_sparse_proxy_aux_weight = float(singleton_sparse_proxy_aux_config.get("weight", 0.0))
    z_art_influence_aux_config = weights.get("z_art_influence_aux")
    z_art_influence_aux_weight = 0.0
    if isinstance(z_art_influence_aux_config, dict):
        z_art_influence_aux_weight = float(z_art_influence_aux_config.get("weight", 0.0))
    formal_special_clause_shape_aux_config = weights.get("formal_special_clause_shape_aux")
    formal_special_clause_shape_aux_weight = 0.0
    if isinstance(formal_special_clause_shape_aux_config, dict):
        formal_special_clause_shape_aux_weight = float(formal_special_clause_shape_aux_config.get("weight", 0.0))

    total_loss = (
        acoustic_loss * weights["acoustic"]
        + event_loss * weights["event"]
        + z_smooth_loss * weights["z_smooth"]
        + text_aux_loss * weights["text_aux"]
        + weak_event_loss * float(weights.get("weak_event", 0.0))
        + clause_transition_aux_loss * clause_transition_aux_weight
        + structural_clause_transition_aux_loss * structural_clause_transition_aux_weight
        + boundary_contrast_aux_loss * boundary_contrast_aux_weight
        + punctuation_profile_aux_loss * punctuation_profile_aux_weight
        + structural_clause_profile_aux_loss * structural_clause_profile_aux_weight
        + challenge_proxy_profile_aux_loss * challenge_proxy_profile_aux_weight
        + singleton_sparse_proxy_aux_loss * singleton_sparse_proxy_aux_weight
        + z_art_influence_aux_loss * z_art_influence_aux_weight
        + formal_special_clause_shape_aux_loss * formal_special_clause_shape_aux_weight
    )

    metrics = {
        "loss_total": float(total_loss.detach().cpu().item()),
        "loss_acoustic": float(acoustic_loss.detach().cpu().item()),
        "loss_event": float(event_loss.detach().cpu().item()),
        "loss_z_smooth": float(z_smooth_loss.detach().cpu().item()),
        "loss_text_aux": float(text_aux_loss_raw.detach().cpu().item()),
        "loss_text_aux_effective": float(text_aux_loss.detach().cpu().item()),
        "loss_text_aux_structural": float(structural_loss.detach().cpu().item()),
        "loss_text_aux_lexical": float(lexical_loss.detach().cpu().item()),
        "loss_weak_event": float(weak_event_loss.detach().cpu().item()),
        "loss_clause_transition_aux": float(clause_transition_aux_loss.detach().cpu().item()),
        "loss_structural_clause_transition_aux": float(structural_clause_transition_aux_loss.detach().cpu().item()),
        "loss_boundary_contrast_aux": float(boundary_contrast_aux_loss.detach().cpu().item()),
        "loss_punctuation_profile_aux": float(punctuation_profile_aux_loss.detach().cpu().item()),
        "loss_structural_clause_profile_aux": float(structural_clause_profile_aux_loss.detach().cpu().item()),
        "loss_challenge_proxy_profile_aux": float(challenge_proxy_profile_aux_loss.detach().cpu().item()),
        "loss_singleton_sparse_proxy_aux": float(singleton_sparse_proxy_aux_loss.detach().cpu().item()),
        "loss_z_art_influence_aux": float(z_art_influence_aux_loss.detach().cpu().item()),
        "loss_formal_special_clause_shape_aux": float(
            formal_special_clause_shape_aux_loss.detach().cpu().item()
        ),
    }
    return total_loss, metrics


def build_effective_loss_weights(
    loss_config: dict[str, object],
    step: int,
    total_steps: int,
) -> dict[str, object]:
    effective = deepcopy(loss_config)
    effective["acoustic"] = float(loss_config["acoustic"])
    effective["event"] = resolve_event_weight(loss_config=loss_config, step=step, total_steps=total_steps)
    effective["z_smooth"] = resolve_z_smooth_weight(loss_config=loss_config, step=step, total_steps=total_steps)
    effective["text_aux"] = float(loss_config["text_aux"])
    effective["weak_event"] = float(loss_config.get("weak_event", 0.0))
    if "event_dimension_weights" in loss_config:
        effective["event_dimension_weights"] = [
            float(value) for value in list(loss_config["event_dimension_weights"])
        ]
    if "event_boundary_bias" in loss_config:
        effective["event_boundary_bias"] = deepcopy(loss_config["event_boundary_bias"])
    if "clause_transition_aux" in loss_config:
        effective["clause_transition_aux"] = deepcopy(loss_config["clause_transition_aux"])
    if "structural_clause_transition_aux" in loss_config:
        effective["structural_clause_transition_aux"] = resolve_structural_clause_transition_aux(
            structural_clause_transition_aux_config=loss_config["structural_clause_transition_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "boundary_contrast_aux" in loss_config:
        effective["boundary_contrast_aux"] = deepcopy(loss_config["boundary_contrast_aux"])
    if "punctuation_profile_aux" in loss_config:
        effective["punctuation_profile_aux"] = resolve_punctuation_profile_aux(
            punctuation_profile_aux_config=loss_config["punctuation_profile_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "structural_clause_profile_aux" in loss_config:
        effective["structural_clause_profile_aux"] = resolve_structural_clause_profile_aux(
            structural_clause_profile_aux_config=loss_config["structural_clause_profile_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "challenge_proxy_profile_aux" in loss_config:
        effective["challenge_proxy_profile_aux"] = deepcopy(loss_config["challenge_proxy_profile_aux"])
    if "singleton_sparse_proxy_aux" in loss_config:
        effective["singleton_sparse_proxy_aux"] = resolve_singleton_sparse_proxy_aux(
            singleton_sparse_proxy_aux_config=loss_config["singleton_sparse_proxy_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "z_art_influence_aux" in loss_config:
        effective["z_art_influence_aux"] = resolve_z_art_influence_aux(
            z_art_influence_aux_config=loss_config["z_art_influence_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "formal_special_clause_shape_aux" in loss_config:
        effective["formal_special_clause_shape_aux"] = resolve_formal_special_clause_shape_aux(
            formal_special_clause_shape_aux_config=loss_config["formal_special_clause_shape_aux"],
            step=step,
            total_steps=total_steps,
        )
    if "text_aux_reweight" in loss_config:
        effective["text_aux_reweight"] = resolve_text_aux_reweight(
            text_aux_reweight_config=loss_config["text_aux_reweight"],
            step=step,
            total_steps=total_steps,
        )
    if "text_aux_split" in loss_config:
        effective["text_aux_split"] = deepcopy(loss_config["text_aux_split"])
    return effective


def build_text_aux_split_config(
    weights: dict[str, object],
    text_aux_target: torch.Tensor,
) -> dict[str, object] | None:
    split_config = weights.get("text_aux_split")
    if not isinstance(split_config, dict) or not bool(split_config.get("enabled", False)):
        return None
    if "text_aux_reweight" in weights and isinstance(weights["text_aux_reweight"], dict):
        if bool(weights["text_aux_reweight"].get("enabled", False)):
            raise ValueError("losses.text_aux_split and losses.text_aux_reweight cannot both be enabled.")
    target_dim = int(text_aux_target.shape[-1])
    structural_dimensions = normalize_text_aux_dimension_list(
        raw_dimensions=split_config.get("structural_dimensions"),
        target_dim=target_dim,
        field_name="losses.text_aux_split.structural_dimensions",
    )
    lexical_dimensions = normalize_text_aux_dimension_list(
        raw_dimensions=split_config.get("lexical_dimensions"),
        target_dim=target_dim,
        field_name="losses.text_aux_split.lexical_dimensions",
    )
    overlap = set(structural_dimensions) & set(lexical_dimensions)
    if overlap:
        raise ValueError(f"losses.text_aux_split dimensions overlap: {sorted(overlap)}")
    structural_weight = float(split_config.get("structural_weight", 0.0))
    lexical_weight = float(split_config.get("lexical_weight", 0.0))
    if structural_weight < 0.0 or lexical_weight < 0.0:
        raise ValueError("losses.text_aux_split weights must be non-negative.")
    if not structural_dimensions and not lexical_dimensions:
        raise ValueError("losses.text_aux_split requires at least one non-empty dimension group.")
    if (structural_dimensions and structural_weight > 0.0) or (lexical_dimensions and lexical_weight > 0.0):
        pass
    else:
        raise ValueError("losses.text_aux_split requires at least one active group weight.")
    return {
        "structural_dimensions": structural_dimensions,
        "lexical_dimensions": lexical_dimensions,
        "structural_weight": structural_weight,
        "lexical_weight": lexical_weight,
    }


def normalize_text_aux_dimension_list(
    raw_dimensions: object,
    target_dim: int,
    field_name: str,
) -> list[int]:
    if raw_dimensions is None:
        return []
    if isinstance(raw_dimensions, list) and not raw_dimensions:
        return []
    if not isinstance(raw_dimensions, list):
        raise ValueError(f"{field_name} must be a list.")
    normalized: list[int] = []
    seen: set[int] = set()
    for raw_value in raw_dimensions:
        index = int(raw_value)
        if index < 0 or index >= target_dim:
            raise ValueError(f"{field_name} contains out-of-range index: {index}")
        if index in seen:
            continue
        seen.add(index)
        normalized.append(index)
    return normalized


def compute_text_aux_split_losses(
    outputs: dict[str, torch.Tensor],
    text_aux_target: torch.Tensor,
    split_config: dict[str, object],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    squared_error = (outputs["text_aux"] - text_aux_target) ** 2
    structural_loss = compute_text_aux_group_loss(
        squared_error=squared_error,
        dimensions=list(split_config["structural_dimensions"]),
    )
    lexical_loss = compute_text_aux_group_loss(
        squared_error=squared_error,
        dimensions=list(split_config["lexical_dimensions"]),
    )
    numerator = torch.zeros((), device=text_aux_target.device, dtype=text_aux_target.dtype)
    denominator = 0.0
    structural_weight = float(split_config["structural_weight"])
    lexical_weight = float(split_config["lexical_weight"])
    if list(split_config["structural_dimensions"]) and structural_weight > 0.0:
        numerator = numerator + structural_loss * structural_weight
        denominator += structural_weight
    if list(split_config["lexical_dimensions"]) and lexical_weight > 0.0:
        numerator = numerator + lexical_loss * lexical_weight
        denominator += lexical_weight
    text_aux_loss = numerator / max(denominator, 1.0e-8)
    return structural_loss, lexical_loss, text_aux_loss


def compute_text_aux_group_loss(
    squared_error: torch.Tensor,
    dimensions: list[int],
) -> torch.Tensor:
    if not dimensions:
        return torch.zeros((), device=squared_error.device, dtype=squared_error.dtype)
    index_tensor = torch.tensor(dimensions, device=squared_error.device, dtype=torch.long)
    selected_error = torch.index_select(squared_error, dim=-1, index=index_tensor)
    return selected_error.mean()


def build_text_aux_dimension_weights(
    weights: dict[str, object],
    text_aux_target: torch.Tensor,
) -> torch.Tensor | None:
    reweight_config = weights.get("text_aux_reweight")
    if not isinstance(reweight_config, dict) or not bool(reweight_config.get("enabled", False)):
        return None
    raw_dimension_weights = reweight_config.get("dimension_weights")
    if not isinstance(raw_dimension_weights, list):
        raise ValueError("losses.text_aux_reweight.dimension_weights must be a list when enabled.")
    target_dim = int(text_aux_target.shape[-1])
    if len(raw_dimension_weights) != target_dim:
        raise ValueError(
            "losses.text_aux_reweight.dimension_weights length does not match text_aux target dim: "
            f"{len(raw_dimension_weights)} != {target_dim}"
        )
    dimension_weights = torch.tensor(
        [float(value) for value in raw_dimension_weights],
        device=text_aux_target.device,
        dtype=text_aux_target.dtype,
    )
    if bool(torch.any(dimension_weights < 0.0).item()):
        raise ValueError("losses.text_aux_reweight.dimension_weights must be non-negative.")
    if float(dimension_weights.sum().item()) <= 0.0:
        raise ValueError("losses.text_aux_reweight.dimension_weights must contain a positive total weight.")
    reweight_strength = float(reweight_config.get("reweight_strength", 1.0))
    if reweight_strength <= 0.0:
        return None
    if reweight_strength < 1.0:
        uniform_weights = torch.ones_like(dimension_weights)
        dimension_weights = (
            dimension_weights * reweight_strength
            + uniform_weights * (1.0 - reweight_strength)
        )
    return dimension_weights


def resolve_text_aux_reweight(
    text_aux_reweight_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(text_aux_reweight_config, dict):
        raise ValueError("losses.text_aux_reweight must be a dict when provided.")
    effective = deepcopy(text_aux_reweight_config)
    effective["enabled"] = bool(text_aux_reweight_config.get("enabled", False))
    if not effective["enabled"]:
        effective["reweight_strength"] = 0.0
        return effective
    effective["reweight_strength"] = resolve_text_aux_reweight_strength(
        text_aux_reweight_config=text_aux_reweight_config,
        step=step,
        total_steps=total_steps,
    )
    return effective


def resolve_text_aux_reweight_strength(
    text_aux_reweight_config: dict[str, object],
    step: int,
    total_steps: int,
) -> float:
    schedule = text_aux_reweight_config.get("strength_schedule")
    if not isinstance(schedule, dict) or not bool(schedule.get("enabled", False)):
        return 1.0
    mode = str(schedule.get("mode", "linear_ramp"))
    if mode != "linear_ramp":
        raise ValueError(f"Unsupported text_aux_reweight.strength_schedule.mode: {mode}")
    start_step = int(schedule.get("start_step", 1))
    end_step = int(schedule.get("end_step", max(start_step, total_steps)))
    start_strength = float(schedule.get("start_strength", 1.0))
    end_strength = float(schedule.get("end_strength", 1.0))
    if step <= start_step:
        return max(0.0, start_strength)
    if step >= end_step:
        return max(0.0, end_strength)
    progress = (step - start_step) / max(1, end_step - start_step)
    strength = start_strength + (end_strength - start_strength) * progress
    return max(0.0, strength)


def resolve_z_art_influence_aux(
    z_art_influence_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(z_art_influence_aux_config, dict):
        raise ValueError("losses.z_art_influence_aux must be a dict when provided.")
    effective = deepcopy(z_art_influence_aux_config)
    effective["enabled"] = bool(z_art_influence_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(z_art_influence_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=z_art_influence_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="z_art_influence_aux.weight_schedule",
    )
    return effective


def resolve_formal_special_clause_shape_aux(
    formal_special_clause_shape_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(formal_special_clause_shape_aux_config, dict):
        raise ValueError("losses.formal_special_clause_shape_aux must be a dict when provided.")
    effective = deepcopy(formal_special_clause_shape_aux_config)
    effective["enabled"] = bool(formal_special_clause_shape_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(formal_special_clause_shape_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=formal_special_clause_shape_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="formal_special_clause_shape_aux.weight_schedule",
    )
    return effective


def resolve_punctuation_profile_aux(
    punctuation_profile_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(punctuation_profile_aux_config, dict):
        raise ValueError("losses.punctuation_profile_aux must be a dict when provided.")
    effective = deepcopy(punctuation_profile_aux_config)
    effective["enabled"] = bool(punctuation_profile_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(punctuation_profile_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=punctuation_profile_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="punctuation_profile_aux.weight_schedule",
    )
    return effective


def resolve_structural_clause_profile_aux(
    structural_clause_profile_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(structural_clause_profile_aux_config, dict):
        raise ValueError("losses.structural_clause_profile_aux must be a dict when provided.")
    effective = deepcopy(structural_clause_profile_aux_config)
    effective["enabled"] = bool(structural_clause_profile_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(structural_clause_profile_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=structural_clause_profile_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="structural_clause_profile_aux.weight_schedule",
    )
    return effective


def resolve_singleton_sparse_proxy_aux(
    singleton_sparse_proxy_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(singleton_sparse_proxy_aux_config, dict):
        raise ValueError("losses.singleton_sparse_proxy_aux must be a dict when provided.")
    effective = deepcopy(singleton_sparse_proxy_aux_config)
    effective["enabled"] = bool(singleton_sparse_proxy_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(singleton_sparse_proxy_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=singleton_sparse_proxy_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="singleton_sparse_proxy_aux.weight_schedule",
    )
    return effective


def resolve_structural_clause_transition_aux(
    structural_clause_transition_aux_config: object,
    step: int,
    total_steps: int,
) -> dict[str, object]:
    if not isinstance(structural_clause_transition_aux_config, dict):
        raise ValueError("losses.structural_clause_transition_aux must be a dict when provided.")
    effective = deepcopy(structural_clause_transition_aux_config)
    effective["enabled"] = bool(structural_clause_transition_aux_config.get("enabled", False))
    if not effective["enabled"]:
        effective["weight"] = 0.0
        return effective
    base_weight = float(structural_clause_transition_aux_config.get("weight", 0.0))
    effective["weight"] = resolve_scalar_weight_schedule(
        schedule=structural_clause_transition_aux_config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="structural_clause_transition_aux.weight_schedule",
    )
    return effective


def resolve_event_weight(
    loss_config: dict[str, object],
    step: int,
    total_steps: int,
) -> float:
    base_weight = float(loss_config["event"])
    return resolve_scalar_weight_schedule(
        schedule=loss_config.get("event_weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="event_weight_schedule",
    )


def resolve_z_smooth_weight(
    loss_config: dict[str, object],
    step: int,
    total_steps: int,
) -> float:
    base_weight = float(loss_config["z_smooth"])
    return resolve_scalar_weight_schedule(
        schedule=loss_config.get("z_smooth_weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="z_smooth_weight_schedule",
    )


def resolve_scalar_weight_schedule(
    schedule: object,
    base_weight: float,
    step: int,
    total_steps: int,
    field_name: str,
) -> float:
    if not isinstance(schedule, dict) or not bool(schedule.get("enabled", False)):
        return base_weight
    mode = str(schedule.get("mode", "linear_ramp"))
    if mode != "linear_ramp":
        raise ValueError(f"Unsupported {field_name}.mode: {mode}")
    start_step = int(schedule.get("start_step", 1))
    end_step = int(schedule.get("end_step", max(start_step, total_steps)))
    start_weight = float(schedule.get("start_weight", base_weight))
    end_weight = float(schedule.get("end_weight", base_weight))
    if step <= start_step:
        return start_weight
    if step >= end_step:
        return end_weight
    progress = (step - start_step) / max(1, end_step - start_step)
    return start_weight + (end_weight - start_weight) * progress


def build_event_dimension_weights(
    weights: dict[str, object],
    event_logits: torch.Tensor,
) -> torch.Tensor:
    event_dim = event_logits.shape[-1]
    raw_weights = weights.get("event_dimension_weights")
    if raw_weights is None:
        return torch.ones((1, 1, event_dim), device=event_logits.device, dtype=event_logits.dtype)
    dimension_weights = torch.tensor(
        [float(value) for value in list(raw_weights)],
        device=event_logits.device,
        dtype=event_logits.dtype,
    )
    if dimension_weights.numel() != event_dim:
        raise ValueError(
            f"event_dimension_weights length {dimension_weights.numel()} does not match event_dim {event_dim}"
        )
    return dimension_weights.view(1, 1, event_dim)


def compute_z_art_influence_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    aux_config = weights.get("z_art_influence_aux")
    if not isinstance(aux_config, dict) or not bool(aux_config.get("enabled", False)):
        return torch.zeros((), device=frame_mask.device, dtype=torch.float32)
    fused_hidden_with_z_art = outputs.get("fused_hidden_with_z_art")
    fused_hidden_zero_z_art = outputs.get("fused_hidden_zero_z_art")
    if fused_hidden_with_z_art is None or fused_hidden_zero_z_art is None:
        raise ValueError("z_art_influence_aux requires fused_hidden_with_z_art and fused_hidden_zero_z_art outputs.")
    sample_mask = build_special_supervision_sample_mask(
        target_special_supervision=target_special_supervision,
        batch_size=int(frame_mask.shape[0]),
        pool_memberships=list(aux_config.get("pool_memberships", [])),
        device=frame_mask.device,
        min_clause_count=int(aux_config.get("min_clause_count", 0)),
        min_pause_boundary_count=int(aux_config.get("min_pause_boundary_count", 0)),
        min_terminal_boundary_count=int(aux_config.get("min_terminal_boundary_count", 0)),
        required_within_special_duration_ceiling=aux_config.get("required_within_special_duration_ceiling"),
    )
    if float(sample_mask.sum().item()) <= 0.0:
        return torch.zeros((), device=frame_mask.device, dtype=fused_hidden_with_z_art.dtype)
    influence = (fused_hidden_with_z_art - fused_hidden_zero_z_art).abs().mean(dim=-1)
    sample_influence = masked_sample_mean(influence, frame_mask)
    min_influence = torch.tensor(
        float(aux_config.get("min_influence", 0.0)),
        device=sample_influence.device,
        dtype=sample_influence.dtype,
    )
    shortfall = torch.relu(min_influence - sample_influence)
    active_count = sample_mask.sum().clamp_min(1.0)
    return (shortfall * sample_mask).sum() / active_count


def compute_formal_special_clause_shape_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    target_special_supervision: list[dict[str, object] | None] | None,
    clause_role_strengths: dict[str, torch.Tensor] | None,
    clause_transition_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("formal_special_clause_shape_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not target_special_supervision or not clause_role_strengths or not clause_transition_strengths:
        return zero

    role_overrides = config.get("role_overrides")
    if not isinstance(role_overrides, dict):
        return zero

    event_probs = torch.sigmoid(event_logits)
    sample_weights = build_special_supervision_sample_weights(
        target_special_supervision=target_special_supervision,
        batch_size=int(frame_mask.shape[0]),
        pool_memberships=list(config.get("pool_memberships", [])),
        device=frame_mask.device,
        min_special_proximity_score=float(config.get("min_special_proximity_score", 0.0)),
        max_special_proximity_score=float(config.get("max_special_proximity_score", 1.0)),
        required_final_terminal_types=list(config.get("required_final_terminal_types", [])),
        required_utterance_structure_types=list(config.get("required_utterance_structure_types", [])),
        min_clause_count=int(config.get("min_clause_count", 0)),
        min_pause_boundary_count=int(config.get("min_pause_boundary_count", 0)),
        min_terminal_boundary_count=int(config.get("min_terminal_boundary_count", 0)),
        required_within_special_duration_ceiling=config.get("required_within_special_duration_ceiling"),
        base_sample_weight=float(config.get("base_sample_weight", 1.0)),
        proximity_weight_scale=float(config.get("proximity_weight_scale", 0.0)),
        final_terminal_type_weight_overrides=dict(config.get("final_terminal_type_weight_overrides", {})),
        utterance_structure_type_weight_overrides=dict(config.get("utterance_structure_type_weight_overrides", {})),
    )
    if float(sample_weights.sum().item()) <= 0.0:
        return zero

    frame_weight = frame_mask.to(event_probs.dtype) * sample_weights.unsqueeze(1)
    presence_dimension = int(config.get("presence_dimension", 0))
    delta_dimension = int(config.get("delta_dimension", 1))
    fall_dimension = int(config.get("fall_dimension", 6))
    energy_dimension = int(config.get("energy_dimension", 7))
    boundary_neighbor_suppression = float(config.get("boundary_neighbor_suppression", 0.7))
    boundary_center_suppression = float(config.get("boundary_center_suppression", 1.0))

    total_loss = zero
    total_weight = zero

    for role, override in role_overrides.items():
        if not isinstance(override, dict):
            continue
        role_strength_map = clause_role_strengths.get(str(role))
        transition_strength_map = clause_transition_strengths.get(str(role))
        if role_strength_map is None or transition_strength_map is None:
            continue
        role_strength_map = apply_structure_type_gate(
            strength_map=role_strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        transition_strength_map = apply_structure_type_gate(
            strength_map=transition_strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        if float(role_strength_map.max().item()) <= 0.0 and float(transition_strength_map.max().item()) <= 0.0:
            continue

        pre_transition_strength = shift_strength_map(transition_strength_map, offset=-1)
        post_transition_strength = shift_strength_map(transition_strength_map, offset=1)
        body_strength_map = torch.clamp(
            role_strength_map
            - transition_strength_map * boundary_center_suppression
            - pre_transition_strength * boundary_neighbor_suppression
            - post_transition_strength * boundary_neighbor_suppression,
            min=0.0,
        )
        body_weight = body_strength_map * frame_weight * float(override.get("body_weight", 1.0))
        boundary_weight = transition_strength_map * frame_weight * float(override.get("boundary_weight", 1.0))
        post_weight = post_transition_strength * frame_weight * float(override.get("post_weight", 1.0))

        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=body_weight,
            target_value=override.get("body_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=body_weight,
            target_value=override.get("body_energy_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., delta_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_delta_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., fall_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_fall_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=post_weight,
            target_value=override.get("post_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=post_weight,
            target_value=override.get("post_energy_target"),
        )

    if float(total_weight.detach().cpu().item()) <= 0.0:
        return zero
    return total_loss / total_weight.clamp_min(1.0)


def build_special_supervision_sample_mask(
    target_special_supervision: list[dict[str, object] | None] | None,
    batch_size: int,
    pool_memberships: list[object],
    device: torch.device,
    min_special_proximity_score: float = 0.0,
    max_special_proximity_score: float = 1.0,
    required_final_terminal_types: list[object] | None = None,
    required_utterance_structure_types: list[object] | None = None,
    min_clause_count: int = 0,
    min_pause_boundary_count: int = 0,
    min_terminal_boundary_count: int = 0,
    required_within_special_duration_ceiling: bool | None = None,
) -> torch.Tensor:
    sample_weights = build_special_supervision_sample_weights(
        target_special_supervision=target_special_supervision,
        batch_size=batch_size,
        pool_memberships=pool_memberships,
        device=device,
        min_special_proximity_score=min_special_proximity_score,
        max_special_proximity_score=max_special_proximity_score,
        required_final_terminal_types=required_final_terminal_types,
        required_utterance_structure_types=required_utterance_structure_types,
        min_clause_count=min_clause_count,
        min_pause_boundary_count=min_pause_boundary_count,
        min_terminal_boundary_count=min_terminal_boundary_count,
        required_within_special_duration_ceiling=required_within_special_duration_ceiling,
    )
    return (sample_weights > 0.0).to(torch.float32)


def build_special_supervision_sample_weights(
    target_special_supervision: list[dict[str, object] | None] | None,
    batch_size: int,
    pool_memberships: list[object],
    device: torch.device,
    min_special_proximity_score: float = 0.0,
    max_special_proximity_score: float = 1.0,
    required_final_terminal_types: list[object] | None = None,
    required_utterance_structure_types: list[object] | None = None,
    min_clause_count: int = 0,
    min_pause_boundary_count: int = 0,
    min_terminal_boundary_count: int = 0,
    required_within_special_duration_ceiling: bool | None = None,
    base_sample_weight: float = 1.0,
    proximity_weight_scale: float = 0.0,
    final_terminal_type_weight_overrides: dict[object, object] | None = None,
    utterance_structure_type_weight_overrides: dict[object, object] | None = None,
) -> torch.Tensor:
    if not target_special_supervision:
        if pool_memberships:
            return torch.zeros((batch_size,), device=device, dtype=torch.float32)
        return torch.full(
            (batch_size,),
            fill_value=max(0.0, float(base_sample_weight)),
            device=device,
            dtype=torch.float32,
        )
    normalized_pool_memberships = {
        str(value)
        for value in pool_memberships
        if str(value)
    }
    normalized_required_final_terminal_types = {
        str(value)
        for value in (required_final_terminal_types or [])
        if str(value)
    }
    normalized_required_utterance_structure_types = {
        str(value)
        for value in (required_utterance_structure_types or [])
        if str(value)
    }
    normalized_terminal_weight_overrides = {
        str(key): float(value)
        for key, value in (final_terminal_type_weight_overrides or {}).items()
        if str(key)
    }
    normalized_structure_weight_overrides = {
        str(key): float(value)
        for key, value in (utterance_structure_type_weight_overrides or {}).items()
        if str(key)
    }
    sample_weights = torch.zeros((batch_size,), device=device, dtype=torch.float32)
    for index in range(min(batch_size, len(target_special_supervision))):
        supervision_row = target_special_supervision[index]
        if not isinstance(supervision_row, dict):
            continue
        special_proximity_score = float(supervision_row.get("special_proximity_score", 0.0))
        if special_proximity_score < float(min_special_proximity_score):
            continue
        if special_proximity_score > float(max_special_proximity_score):
            continue
        clause_count = int(supervision_row.get("clause_count", 0))
        if clause_count < int(min_clause_count):
            continue
        pause_boundary_count = int(supervision_row.get("pause_boundary_count", 0))
        if pause_boundary_count < int(min_pause_boundary_count):
            continue
        terminal_boundary_count = int(supervision_row.get("terminal_boundary_count", 0))
        if terminal_boundary_count < int(min_terminal_boundary_count):
            continue
        if isinstance(required_within_special_duration_ceiling, bool):
            if bool(supervision_row.get("within_special_duration_ceiling", False)) != required_within_special_duration_ceiling:
                continue
        final_terminal_type = str(supervision_row.get("final_terminal_type", "none"))
        if normalized_required_final_terminal_types and final_terminal_type not in normalized_required_final_terminal_types:
            continue
        utterance_structure_type = str(supervision_row.get("utterance_structure_type", "other"))
        if (
            normalized_required_utterance_structure_types
            and utterance_structure_type not in normalized_required_utterance_structure_types
        ):
            continue
        raw_pool_memberships = supervision_row.get("pool_memberships")
        if not normalized_pool_memberships:
            pool_match = True
        elif not isinstance(raw_pool_memberships, dict):
            continue
        else:
            pool_match = any(bool(raw_pool_memberships.get(pool_name, False)) for pool_name in normalized_pool_memberships)
        if not pool_match:
            continue
        weight = float(base_sample_weight)
        weight += special_proximity_score * float(proximity_weight_scale)
        weight += float(normalized_terminal_weight_overrides.get(final_terminal_type, 0.0))
        weight += float(normalized_structure_weight_overrides.get(utterance_structure_type, 0.0))
        sample_weights[index] = max(0.0, weight)
    return sample_weights


def masked_sample_mean(
    tensor: torch.Tensor,
    frame_mask: torch.Tensor,
) -> torch.Tensor:
    weights = frame_mask.to(tensor.dtype)
    numerator = (tensor * weights).sum(dim=1)
    denominator = weights.sum(dim=1).clamp_min(1.0)
    return numerator / denominator


def build_weak_event_boundary_targets(
    weak_event_hints: list[dict[str, object] | None],
    frame_mask: torch.Tensor,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    dict[str, torch.Tensor],
    dict[str, torch.Tensor],
    dict[str, torch.Tensor],
    dict[str, torch.Tensor],
]:
    batch_size, frame_count = frame_mask.shape
    target = torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
    weight = torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
    pause_boundary_strength = torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
    terminal_boundary_strength = torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
    boundary_type_strengths = {
        symbol_type: torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
        for symbol_type in BOUNDARY_SYMBOL_TYPES
    }
    clause_role_strengths = {
        role: torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
        for role in CLAUSE_ROLES
    }
    clause_transition_strengths = {
        role: torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
        for role in CLAUSE_ROLES
    }
    utterance_structure_strengths = {
        structure_type: torch.zeros((batch_size, frame_count), dtype=torch.float32, device=frame_mask.device)
        for structure_type in UTTERANCE_STRUCTURE_TYPES
    }
    for batch_index, hints in enumerate(weak_event_hints):
        if not isinstance(hints, dict):
            continue
        utterance_structure_type = str(hints.get("utterance_structure_type", "other"))
        if utterance_structure_type in utterance_structure_strengths:
            utterance_structure_strengths[utterance_structure_type][batch_index] = frame_mask[batch_index].to(
                torch.float32
            )
        for boundary in list(hints.get("pause_boundaries", [])):
            symbol_type = str(boundary.get("symbol_type", ""))
            mark_boundary_window(
                target=target,
                weight=weight,
                batch_index=batch_index,
                frame_index=int(boundary["frame_index"]),
                frame_count=frame_count,
                center_weight=0.75,
            )
            mark_boundary_strength(
                strength_map=pause_boundary_strength,
                batch_index=batch_index,
                frame_index=int(boundary["frame_index"]),
                frame_count=frame_count,
                center_weight=0.75,
            )
            if symbol_type in boundary_type_strengths:
                mark_boundary_strength(
                    strength_map=boundary_type_strengths[symbol_type],
                    batch_index=batch_index,
                    frame_index=int(boundary["frame_index"]),
                    frame_count=frame_count,
                    center_weight=0.75,
                )
        for boundary in list(hints.get("terminal_boundaries", [])):
            symbol_type = str(boundary.get("symbol_type", ""))
            mark_boundary_window(
                target=target,
                weight=weight,
                batch_index=batch_index,
                frame_index=int(boundary["frame_index"]),
                frame_count=frame_count,
                center_weight=1.0,
            )
            mark_boundary_strength(
                strength_map=terminal_boundary_strength,
                batch_index=batch_index,
                frame_index=int(boundary["frame_index"]),
                frame_count=frame_count,
                center_weight=1.0,
            )
            if symbol_type in boundary_type_strengths:
                mark_boundary_strength(
                    strength_map=boundary_type_strengths[symbol_type],
                    batch_index=batch_index,
                    frame_index=int(boundary["frame_index"]),
                    frame_count=frame_count,
                    center_weight=1.0,
                )
        for clause in list(hints.get("clause_spans", [])):
            role = str(clause.get("role", ""))
            if role not in clause_role_strengths:
                continue
            mark_span_strength(
                strength_map=clause_role_strengths[role],
                batch_index=batch_index,
                frame_start_index=int(clause["frame_start_index"]),
                frame_end_index=int(clause["frame_end_index"]),
                frame_count=frame_count,
                body_weight=0.35,
                edge_weight=0.55,
            )
            mark_boundary_strength(
                strength_map=clause_transition_strengths[role],
                batch_index=batch_index,
                frame_index=int(clause["frame_end_index"]),
                frame_count=frame_count,
                center_weight=1.0,
            )
    return (
        target,
        weight,
        pause_boundary_strength,
        terminal_boundary_strength,
        boundary_type_strengths,
        clause_role_strengths,
        clause_transition_strengths,
        utterance_structure_strengths,
    )


def mark_boundary_window(
    target: torch.Tensor,
    weight: torch.Tensor,
    batch_index: int,
    frame_index: int,
    frame_count: int,
    center_weight: float,
) -> None:
    for offset, offset_weight in ((0, center_weight), (-1, center_weight * 0.6), (1, center_weight * 0.6)):
        current = frame_index + offset
        if 0 <= current < frame_count:
            target[batch_index, current] = 1.0
            weight[batch_index, current] = max(weight[batch_index, current].item(), float(offset_weight))


def mark_boundary_strength(
    strength_map: torch.Tensor,
    batch_index: int,
    frame_index: int,
    frame_count: int,
    center_weight: float,
) -> None:
    for offset, offset_weight in ((0, center_weight), (-1, center_weight * 0.6), (1, center_weight * 0.6)):
        current = frame_index + offset
        if 0 <= current < frame_count:
            strength_map[batch_index, current] = max(
                strength_map[batch_index, current].item(),
                float(offset_weight),
            )


def mark_span_strength(
    strength_map: torch.Tensor,
    batch_index: int,
    frame_start_index: int,
    frame_end_index: int,
    frame_count: int,
    body_weight: float,
    edge_weight: float,
) -> None:
    start_index = max(0, min(frame_count - 1, frame_start_index))
    end_index = max(0, min(frame_count - 1, frame_end_index))
    if end_index < start_index:
        start_index, end_index = end_index, start_index
    for frame_index in range(start_index, end_index + 1):
        strength_map[batch_index, frame_index] = max(
            strength_map[batch_index, frame_index].item(),
            float(body_weight),
        )
    for frame_index in (start_index, end_index):
        strength_map[batch_index, frame_index] = max(
            strength_map[batch_index, frame_index].item(),
            float(edge_weight),
        )


def apply_event_boundary_bias(
    event_target: torch.Tensor,
    weights: dict[str, object],
    pause_boundary_strength: torch.Tensor | None,
    terminal_boundary_strength: torch.Tensor | None,
    boundary_type_strengths: dict[str, torch.Tensor] | None,
    clause_role_strengths: dict[str, torch.Tensor] | None,
    clause_transition_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
) -> tuple[torch.Tensor, torch.Tensor | None]:
    config = weights.get("event_boundary_bias")
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return event_target, None
    if pause_boundary_strength is None or terminal_boundary_strength is None:
        return event_target, None

    delta_dimension = int(config.get("delta_dimension", 1))
    rise_dimension = int(config.get("rise_dimension", 5))
    fall_dimension = int(config.get("fall_dimension", 6))
    presence_dimension = int(config.get("presence_dimension", 0))
    energy_dimension = int(config.get("energy_dimension", 7))
    pause_boost = float(config.get("pause_boost", 0.0))
    terminal_boost = float(config.get("terminal_boost", 0.0))
    pause_fall_target = float(config.get("pause_fall_target", 0.75))
    terminal_fall_target = float(config.get("terminal_fall_target", 1.0))
    apply_override = bool(config.get("apply_override", True))

    bias = torch.ones_like(event_target)
    if pause_boost != 0.0:
        bias[..., delta_dimension] += pause_boundary_strength * pause_boost
        bias[..., fall_dimension] += pause_boundary_strength * pause_boost
    if terminal_boost != 0.0:
        bias[..., delta_dimension] += terminal_boundary_strength * terminal_boost
        bias[..., fall_dimension] += terminal_boundary_strength * terminal_boost

    if not apply_override:
        return event_target, bias

    adjusted_target = event_target.clone()
    any_boundary_mask = (pause_boundary_strength > 0) | (terminal_boundary_strength > 0)
    adjusted_target[..., delta_dimension] = torch.where(
        any_boundary_mask,
        torch.ones_like(adjusted_target[..., delta_dimension]),
        adjusted_target[..., delta_dimension],
    )
    adjusted_target[..., fall_dimension] = torch.maximum(
        adjusted_target[..., fall_dimension],
        pause_boundary_strength * pause_fall_target,
    )
    adjusted_target[..., fall_dimension] = torch.maximum(
        adjusted_target[..., fall_dimension],
        terminal_boundary_strength * terminal_fall_target,
    )

    pause_pre_strength = shift_strength_map(pause_boundary_strength, offset=-1)
    terminal_pre_strength = shift_strength_map(terminal_boundary_strength, offset=-1)
    pause_post_strength = shift_strength_map(pause_boundary_strength, offset=1)
    terminal_post_strength = shift_strength_map(terminal_boundary_strength, offset=1)

    adjusted_target[..., presence_dimension] = blend_event_channel(
        channel=adjusted_target[..., presence_dimension],
        strength_map=pause_pre_strength,
        target_value=float(config.get("pause_pre_presence_target", 0.9)),
    )
    adjusted_target[..., presence_dimension] = blend_event_channel(
        channel=adjusted_target[..., presence_dimension],
        strength_map=terminal_pre_strength,
        target_value=float(config.get("terminal_pre_presence_target", 0.95)),
    )
    adjusted_target[..., presence_dimension] = blend_event_channel(
        channel=adjusted_target[..., presence_dimension],
        strength_map=pause_post_strength,
        target_value=float(config.get("pause_post_presence_target", 0.45)),
    )
    adjusted_target[..., presence_dimension] = blend_event_channel(
        channel=adjusted_target[..., presence_dimension],
        strength_map=terminal_post_strength,
        target_value=float(config.get("terminal_post_presence_target", 0.15)),
    )

    adjusted_target[..., energy_dimension] = blend_event_channel(
        channel=adjusted_target[..., energy_dimension],
        strength_map=pause_pre_strength,
        target_value=float(config.get("pause_pre_energy_target", 0.85)),
    )
    adjusted_target[..., energy_dimension] = blend_event_channel(
        channel=adjusted_target[..., energy_dimension],
        strength_map=terminal_pre_strength,
        target_value=float(config.get("terminal_pre_energy_target", 0.9)),
    )
    adjusted_target[..., energy_dimension] = blend_event_channel(
        channel=adjusted_target[..., energy_dimension],
        strength_map=pause_post_strength,
        target_value=float(config.get("pause_post_energy_target", 0.3)),
    )
    adjusted_target[..., energy_dimension] = blend_event_channel(
        channel=adjusted_target[..., energy_dimension],
        strength_map=terminal_post_strength,
        target_value=float(config.get("terminal_post_energy_target", 0.08)),
    )
    adjusted_target, bias = apply_type_specific_boundary_bias(
        adjusted_target=adjusted_target,
        bias=bias,
        boundary_type_strengths=boundary_type_strengths,
        config=config,
        delta_dimension=delta_dimension,
        rise_dimension=rise_dimension,
        fall_dimension=fall_dimension,
        presence_dimension=presence_dimension,
        energy_dimension=energy_dimension,
    )
    adjusted_target, bias = apply_clause_transition_bias(
        adjusted_target=adjusted_target,
        bias=bias,
        clause_transition_strengths=clause_transition_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
        config=config,
        delta_dimension=delta_dimension,
        rise_dimension=rise_dimension,
        fall_dimension=fall_dimension,
        presence_dimension=presence_dimension,
        energy_dimension=energy_dimension,
    )
    adjusted_target, bias = apply_clause_role_bias(
        adjusted_target=adjusted_target,
        bias=bias,
        clause_role_strengths=clause_role_strengths,
        utterance_structure_strengths=utterance_structure_strengths,
        config=config,
        presence_dimension=presence_dimension,
        energy_dimension=energy_dimension,
    )
    return adjusted_target, bias


def apply_type_specific_boundary_bias(
    adjusted_target: torch.Tensor,
    bias: torch.Tensor,
    boundary_type_strengths: dict[str, torch.Tensor] | None,
    config: dict[str, object],
    delta_dimension: int,
    rise_dimension: int,
    fall_dimension: int,
    presence_dimension: int,
    energy_dimension: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if not boundary_type_strengths:
        return adjusted_target, bias
    raw_overrides = config.get("type_target_overrides")
    if not isinstance(raw_overrides, dict):
        return adjusted_target, bias

    for symbol_type, override in raw_overrides.items():
        if not isinstance(override, dict):
            continue
        strength_map = boundary_type_strengths.get(str(symbol_type))
        if strength_map is None:
            continue
        if float(strength_map.max().item()) <= 0.0:
            continue

        delta_boost = float(override.get("delta_boost", 0.0))
        rise_boost = float(override.get("rise_boost", 0.0))
        fall_boost = float(override.get("fall_boost", 0.0))
        if delta_boost != 0.0:
            bias[..., delta_dimension] += strength_map * delta_boost
        if rise_boost != 0.0:
            bias[..., rise_dimension] += strength_map * rise_boost
        if fall_boost != 0.0:
            bias[..., fall_dimension] += strength_map * fall_boost

        if "boundary_rise_target" in override:
            adjusted_target[..., rise_dimension] = torch.maximum(
                adjusted_target[..., rise_dimension],
                strength_map * float(override["boundary_rise_target"]),
            )
        if "boundary_fall_target" in override:
            adjusted_target[..., fall_dimension] = torch.maximum(
                adjusted_target[..., fall_dimension],
                strength_map * float(override["boundary_fall_target"]),
            )
        if "boundary_delta_target" in override:
            adjusted_target[..., delta_dimension] = torch.maximum(
                adjusted_target[..., delta_dimension],
                strength_map * float(override["boundary_delta_target"]),
            )

        pre_strength = shift_strength_map(strength_map, offset=-1)
        post_strength = shift_strength_map(strength_map, offset=1)
        if "pre_presence_target" in override:
            adjusted_target[..., presence_dimension] = blend_event_channel(
                channel=adjusted_target[..., presence_dimension],
                strength_map=pre_strength,
                target_value=float(override["pre_presence_target"]),
            )
        if "post_presence_target" in override:
            adjusted_target[..., presence_dimension] = blend_event_channel(
                channel=adjusted_target[..., presence_dimension],
                strength_map=post_strength,
                target_value=float(override["post_presence_target"]),
            )
        if "pre_energy_target" in override:
            adjusted_target[..., energy_dimension] = blend_event_channel(
                channel=adjusted_target[..., energy_dimension],
                strength_map=pre_strength,
                target_value=float(override["pre_energy_target"]),
            )
        if "post_energy_target" in override:
            adjusted_target[..., energy_dimension] = blend_event_channel(
                channel=adjusted_target[..., energy_dimension],
                strength_map=post_strength,
                target_value=float(override["post_energy_target"]),
            )

    return adjusted_target, bias


def apply_clause_transition_bias(
    adjusted_target: torch.Tensor,
    bias: torch.Tensor,
    clause_transition_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
    config: dict[str, object],
    delta_dimension: int,
    rise_dimension: int,
    fall_dimension: int,
    presence_dimension: int,
    energy_dimension: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if not clause_transition_strengths:
        return adjusted_target, bias
    raw_overrides = config.get("clause_transition_target_overrides")
    if not isinstance(raw_overrides, dict):
        return adjusted_target, bias

    for role, override in raw_overrides.items():
        if not isinstance(override, dict):
            continue
        strength_map = clause_transition_strengths.get(str(role))
        if strength_map is None:
            continue
        strength_map = apply_structure_type_gate(
            strength_map=strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        if float(strength_map.max().item()) <= 0.0:
            continue

        delta_boost = float(override.get("delta_boost", 0.0))
        rise_boost = float(override.get("rise_boost", 0.0))
        fall_boost = float(override.get("fall_boost", 0.0))
        presence_boost = float(override.get("presence_boost", 0.0))
        energy_boost = float(override.get("energy_boost", 0.0))
        if delta_boost != 0.0:
            bias[..., delta_dimension] += strength_map * delta_boost
        if rise_boost != 0.0:
            bias[..., rise_dimension] += strength_map * rise_boost
        if fall_boost != 0.0:
            bias[..., fall_dimension] += strength_map * fall_boost
        if presence_boost != 0.0:
            bias[..., presence_dimension] += strength_map * presence_boost
        if energy_boost != 0.0:
            bias[..., energy_dimension] += strength_map * energy_boost

        if "boundary_delta_target" in override:
            adjusted_target[..., delta_dimension] = torch.maximum(
                adjusted_target[..., delta_dimension],
                strength_map * float(override["boundary_delta_target"]),
            )
        if "boundary_rise_target" in override:
            adjusted_target[..., rise_dimension] = torch.maximum(
                adjusted_target[..., rise_dimension],
                strength_map * float(override["boundary_rise_target"]),
            )
        if "boundary_fall_target" in override:
            adjusted_target[..., fall_dimension] = torch.maximum(
                adjusted_target[..., fall_dimension],
                strength_map * float(override["boundary_fall_target"]),
            )

        pre_strength = shift_strength_map(strength_map, offset=-1)
        post_strength = shift_strength_map(strength_map, offset=1)
        if "pre_presence_target" in override:
            adjusted_target[..., presence_dimension] = blend_event_channel(
                channel=adjusted_target[..., presence_dimension],
                strength_map=pre_strength,
                target_value=float(override["pre_presence_target"]),
            )
        if "post_presence_target" in override:
            adjusted_target[..., presence_dimension] = blend_event_channel(
                channel=adjusted_target[..., presence_dimension],
                strength_map=post_strength,
                target_value=float(override["post_presence_target"]),
            )
        if "pre_energy_target" in override:
            adjusted_target[..., energy_dimension] = blend_event_channel(
                channel=adjusted_target[..., energy_dimension],
                strength_map=pre_strength,
                target_value=float(override["pre_energy_target"]),
            )
        if "post_energy_target" in override:
            adjusted_target[..., energy_dimension] = blend_event_channel(
                channel=adjusted_target[..., energy_dimension],
                strength_map=post_strength,
                target_value=float(override["post_energy_target"]),
            )

    return adjusted_target, bias


def compute_clause_transition_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    clause_transition_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("clause_transition_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not clause_transition_strengths:
        return zero

    raw_overrides = config.get("role_overrides")
    if not isinstance(raw_overrides, dict):
        return zero

    event_probs = torch.sigmoid(event_logits)
    frame_weight = frame_mask.to(event_probs.dtype)
    delta_dimension = int(config.get("delta_dimension", 1))
    rise_dimension = int(config.get("rise_dimension", 5))
    fall_dimension = int(config.get("fall_dimension", 6))
    presence_dimension = int(config.get("presence_dimension", 0))
    energy_dimension = int(config.get("energy_dimension", 7))

    total_loss = zero
    total_weight = zero

    for role, override in raw_overrides.items():
        if not isinstance(override, dict):
            continue
        strength_map = clause_transition_strengths.get(str(role))
        if strength_map is None:
            continue
        strength_map = apply_structure_type_gate(
            strength_map=strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        if float(strength_map.max().item()) <= 0.0:
            continue

        boundary_weight = strength_map * frame_weight * float(override.get("boundary_weight", 1.0))
        pre_weight = shift_strength_map(strength_map, offset=-1) * frame_weight * float(override.get("pre_weight", 1.0))
        post_weight = shift_strength_map(strength_map, offset=1) * frame_weight * float(override.get("post_weight", 1.0))

        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., delta_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_delta_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., rise_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_rise_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., fall_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_fall_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=pre_weight,
            target_value=override.get("pre_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=pre_weight,
            target_value=override.get("pre_energy_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=post_weight,
            target_value=override.get("post_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=post_weight,
            target_value=override.get("post_energy_target"),
        )

    if float(total_weight.detach().cpu().item()) <= 0.0:
        return zero
    return total_loss / total_weight.clamp_min(1.0)


def compute_structural_clause_transition_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    clause_transition_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("structural_clause_transition_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not clause_transition_strengths:
        return zero

    raw_overrides = config.get("role_overrides")
    if not isinstance(raw_overrides, dict):
        return zero

    sample_mask = build_special_supervision_sample_mask(
        target_special_supervision=target_special_supervision,
        batch_size=int(frame_mask.shape[0]),
        pool_memberships=list(config.get("pool_memberships", [])),
        device=frame_mask.device,
        min_clause_count=int(config.get("min_clause_count", 0)),
        min_pause_boundary_count=int(config.get("min_pause_boundary_count", 0)),
        min_terminal_boundary_count=int(config.get("min_terminal_boundary_count", 0)),
        required_within_special_duration_ceiling=config.get("required_within_special_duration_ceiling"),
    )
    if float(sample_mask.sum().item()) <= 0.0:
        return zero

    event_probs = torch.sigmoid(event_logits)
    frame_weight = frame_mask.to(event_probs.dtype) * sample_mask.unsqueeze(1)
    delta_dimension = int(config.get("delta_dimension", 1))
    rise_dimension = int(config.get("rise_dimension", 5))
    fall_dimension = int(config.get("fall_dimension", 6))
    presence_dimension = int(config.get("presence_dimension", 0))
    energy_dimension = int(config.get("energy_dimension", 7))

    total_loss = zero
    total_weight = zero

    for role, override in raw_overrides.items():
        if not isinstance(override, dict):
            continue
        strength_map = clause_transition_strengths.get(str(role))
        if strength_map is None:
            continue
        strength_map = apply_structure_type_gate(
            strength_map=strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        if float(strength_map.max().item()) <= 0.0:
            continue

        boundary_weight = strength_map * frame_weight * float(override.get("boundary_weight", 1.0))
        pre_weight = shift_strength_map(strength_map, offset=-1) * frame_weight * float(override.get("pre_weight", 1.0))
        post_weight = shift_strength_map(strength_map, offset=1) * frame_weight * float(override.get("post_weight", 1.0))

        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., delta_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_delta_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., rise_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_rise_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., fall_dimension],
            weight_map=boundary_weight,
            target_value=override.get("boundary_fall_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=pre_weight,
            target_value=override.get("pre_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=pre_weight,
            target_value=override.get("pre_energy_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., presence_dimension],
            weight_map=post_weight,
            target_value=override.get("post_presence_target"),
        )
        total_loss, total_weight = accumulate_aux_channel_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            channel=event_probs[..., energy_dimension],
            weight_map=post_weight,
            target_value=override.get("post_energy_target"),
        )

    if float(total_weight.detach().cpu().item()) <= 0.0:
        return zero
    return total_loss / total_weight.clamp_min(1.0)


def compute_boundary_contrast_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    pause_boundary_strength: torch.Tensor | None,
    terminal_boundary_strength: torch.Tensor | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("boundary_contrast_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if pause_boundary_strength is None or terminal_boundary_strength is None:
        return zero

    event_probs = torch.sigmoid(event_logits)
    frame_weight = frame_mask.to(event_probs.dtype)
    presence_dimension = int(config.get("presence_dimension", 0))
    energy_dimension = int(config.get("energy_dimension", 7))
    total_loss = zero
    total_weight = zero

    for prefix, strength_map in (
        ("pause", pause_boundary_strength),
        ("terminal", terminal_boundary_strength),
    ):
        if float(strength_map.max().item()) <= 0.0:
            continue
        pair_weight = strength_map * frame_weight
        total_loss, total_weight = accumulate_margin_aux_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            pre_channel=event_probs[..., presence_dimension],
            post_channel=event_probs[..., presence_dimension],
            pre_weight=shift_strength_map(strength_map, offset=-1) * frame_weight,
            post_weight=shift_strength_map(strength_map, offset=1) * frame_weight,
            pair_weight=pair_weight,
            margin=float(config.get(f"{prefix}_pre_post_presence_margin", 0.0)),
        )
        total_loss, total_weight = accumulate_margin_aux_loss(
            total_loss=total_loss,
            total_weight=total_weight,
            pre_channel=event_probs[..., energy_dimension],
            post_channel=event_probs[..., energy_dimension],
            pre_weight=shift_strength_map(strength_map, offset=-1) * frame_weight,
            post_weight=shift_strength_map(strength_map, offset=1) * frame_weight,
            pair_weight=pair_weight,
            margin=float(config.get(f"{prefix}_pre_post_energy_margin", 0.0)),
        )

    if float(total_weight.detach().cpu().item()) <= 0.0:
        return zero
    return total_loss / total_weight.clamp_min(1.0)


def compute_punctuation_profile_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    texts: list[str] | None,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("punctuation_profile_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not texts:
        return zero

    event_probs = torch.sigmoid(event_logits)
    presence_dimension = int(config.get("presence_dimension", 0))
    energy_dimension = int(config.get("energy_dimension", 7))
    peak_threshold = float(config.get("peak_threshold", 0.5))
    min_ratio = float(config.get("min_punctuation_ratio", 0.0))

    presence_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
    )
    energy_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., energy_dimension],
        frame_mask=frame_mask,
    )
    peak_ratio = masked_threshold_ratio_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
        threshold=peak_threshold,
    )

    punctuation_ratio_target = torch.zeros((len(texts),), device=event_probs.device, dtype=event_probs.dtype)
    punctuation_only_target = torch.zeros((len(texts),), device=event_probs.device, dtype=event_probs.dtype)
    for index, text in enumerate(texts):
        ratio, is_punctuation_only = compute_punctuation_profile(str(text))
        punctuation_ratio_target[index] = ratio
        punctuation_only_target[index] = 1.0 if is_punctuation_only else 0.0
    active_mask = (punctuation_ratio_target >= min_ratio).to(event_probs.dtype)
    if any(str(value) for value in list(config.get("pool_memberships", []))):
        supervision_mask = build_special_supervision_sample_mask(
            target_special_supervision=target_special_supervision,
            batch_size=int(frame_mask.shape[0]),
            pool_memberships=list(config.get("pool_memberships", [])),
            device=event_probs.device,
            min_special_proximity_score=float(config.get("min_special_proximity_score", 0.0)),
            max_special_proximity_score=float(config.get("max_special_proximity_score", 1.0)),
            required_final_terminal_types=list(config.get("required_final_terminal_types", [])),
            required_utterance_structure_types=list(config.get("required_utterance_structure_types", [])),
            min_clause_count=int(config.get("min_clause_count", 0)),
            min_pause_boundary_count=int(config.get("min_pause_boundary_count", 0)),
            min_terminal_boundary_count=int(config.get("min_terminal_boundary_count", 0)),
            required_within_special_duration_ceiling=config.get("required_within_special_duration_ceiling"),
        ).to(event_probs.dtype)
        active_mask = active_mask * supervision_mask
    if float(active_mask.sum().item()) <= 0.0:
        return zero

    target_presence = torch.clamp(
        float(config.get("base_presence_target", 0.66))
        - punctuation_ratio_target * float(config.get("punctuation_ratio_presence_scale", 0.06))
        - punctuation_only_target * float(config.get("punctuation_only_presence_offset", 0.03)),
        min=0.0,
        max=1.0,
    )
    target_energy = torch.clamp(
        float(config.get("base_energy_target", 0.64))
        - punctuation_ratio_target * float(config.get("punctuation_ratio_energy_scale", 0.05))
        - punctuation_only_target * float(config.get("punctuation_only_energy_offset", 0.03)),
        min=0.0,
        max=1.0,
    )
    target_peak = torch.clamp(
        float(config.get("base_peak_target", 0.76))
        + punctuation_ratio_target * float(config.get("punctuation_ratio_peak_scale", 0.12))
        + punctuation_only_target * float(config.get("punctuation_only_peak_offset", 0.08)),
        min=0.0,
        max=1.0,
    )

    total_loss = (
        ((presence_mean - target_presence) ** 2) * active_mask
        + ((energy_mean - target_energy) ** 2) * active_mask
        + ((peak_ratio - target_peak) ** 2) * active_mask
    ).sum()
    total_weight = (active_mask * 3.0).sum().clamp_min(1.0)
    return total_loss / total_weight


def compute_challenge_proxy_profile_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("challenge_proxy_profile_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not target_special_supervision:
        return zero

    event_probs = torch.sigmoid(event_logits)
    presence_dimension = int(config.get("presence_dimension", 0))
    fall_dimension = int(config.get("fall_dimension", 6))
    energy_dimension = int(config.get("energy_dimension", 7))

    presence_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
    )
    fall_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., fall_dimension],
        frame_mask=frame_mask,
    )
    energy_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., energy_dimension],
        frame_mask=frame_mask,
    )

    batch_size = int(frame_mask.shape[0])
    active_mask = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    sample_weight = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_presence = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_fall = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_energy = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    pool_memberships = [str(value) for value in list(config.get("pool_memberships", [])) if str(value)]
    min_proximity = float(config.get("min_special_proximity_score", 0.0))

    for index in range(min(batch_size, len(target_special_supervision))):
        supervision_row = target_special_supervision[index]
        if not isinstance(supervision_row, dict):
            continue
        raw_pool_memberships = supervision_row.get("pool_memberships")
        if pool_memberships:
            if not isinstance(raw_pool_memberships, dict):
                continue
            if not any(bool(raw_pool_memberships.get(pool_name, False)) for pool_name in pool_memberships):
                continue
        proximity_score = float(supervision_row.get("special_proximity_score", 0.0))
        if proximity_score < min_proximity:
            continue
        active_mask[index] = 1.0
        no_terminal_bonus = 1.0 if str(supervision_row.get("final_terminal_type", "")) == "none" else 0.0
        terminal_count = float(supervision_row.get("terminal_boundary_count", 0.0))
        terminal_penalty = 1.0 if terminal_count <= 0.0 else 0.0
        proximity_weight = float(config.get("base_sample_weight", 0.4)) + proximity_score * float(
            config.get("proximity_weight_scale", 0.6)
        )
        sample_weight[index] = max(0.0, proximity_weight)
        target_presence[index] = clamp01(
            float(config.get("base_presence_target", 0.46))
            - proximity_score * float(config.get("proximity_presence_scale", 0.10))
            - no_terminal_bonus * float(config.get("no_terminal_presence_offset", 0.03))
        )
        target_fall[index] = clamp01(
            float(config.get("base_fall_target", 0.44))
            + proximity_score * float(config.get("proximity_fall_scale", 0.05))
            + terminal_penalty * float(config.get("no_terminal_fall_offset", 0.01))
        )
        target_energy[index] = clamp01(
            float(config.get("base_energy_target", 0.58))
            - proximity_score * float(config.get("proximity_energy_scale", 0.08))
            - no_terminal_bonus * float(config.get("no_terminal_energy_offset", 0.03))
        )

    if float(active_mask.sum().item()) <= 0.0:
        return zero

    effective_weight = (active_mask * sample_weight).clamp_min(0.0)
    if float(effective_weight.sum().item()) <= 0.0:
        return zero

    total_loss = (
        ((presence_mean - target_presence) ** 2) * effective_weight
        + ((fall_mean - target_fall) ** 2) * effective_weight
        + ((energy_mean - target_energy) ** 2) * effective_weight
    ).sum()
    total_weight = (effective_weight * 3.0).sum().clamp_min(1.0)
    return total_loss / total_weight


def compute_singleton_sparse_proxy_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("singleton_sparse_proxy_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not target_special_supervision:
        return zero

    event_probs = torch.sigmoid(event_logits)
    presence_dimension = int(config.get("presence_dimension", 0))
    fall_dimension = int(config.get("fall_dimension", 6))
    energy_dimension = int(config.get("energy_dimension", 7))
    peak_threshold = float(config.get("presence_peak_threshold", 0.5))

    presence_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
    )
    fall_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., fall_dimension],
        frame_mask=frame_mask,
    )
    energy_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., energy_dimension],
        frame_mask=frame_mask,
    )
    peak_ratio = masked_threshold_ratio_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
        threshold=peak_threshold,
    )

    batch_size = int(frame_mask.shape[0])
    sample_weights = build_special_supervision_sample_weights(
        target_special_supervision=target_special_supervision,
        batch_size=batch_size,
        pool_memberships=list(config.get("pool_memberships", [])),
        device=frame_mask.device,
        min_special_proximity_score=float(config.get("min_special_proximity_score", 0.0)),
        max_special_proximity_score=float(config.get("max_special_proximity_score", 1.0)),
        required_final_terminal_types=list(config.get("required_final_terminal_types", [])),
        required_utterance_structure_types=list(config.get("required_utterance_structure_types", [])),
        min_clause_count=int(config.get("min_clause_count", 0)),
        min_pause_boundary_count=int(config.get("min_pause_boundary_count", 0)),
        min_terminal_boundary_count=int(config.get("min_terminal_boundary_count", 0)),
        required_within_special_duration_ceiling=config.get("required_within_special_duration_ceiling"),
        base_sample_weight=float(config.get("base_sample_weight", 1.0)),
        proximity_weight_scale=float(config.get("proximity_weight_scale", 0.0)),
        final_terminal_type_weight_overrides=dict(config.get("final_terminal_type_weight_overrides", {})),
        utterance_structure_type_weight_overrides=dict(config.get("utterance_structure_type_weight_overrides", {})),
    )
    if float(sample_weights.sum().item()) <= 0.0:
        return zero

    active_mask = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_presence = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_fall = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_energy = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_peak_ratio = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)

    for index in range(min(batch_size, len(target_special_supervision))):
        supervision_row = target_special_supervision[index]
        if not isinstance(supervision_row, dict):
            continue
        if float(sample_weights[index].item()) <= 0.0:
            continue
        active_mask[index] = 1.0
        proximity_score = float(supervision_row.get("special_proximity_score", 0.0))
        no_terminal_bonus = 1.0 if str(supervision_row.get("final_terminal_type", "")) == "none" else 0.0
        within_special_duration_ceiling = (
            1.0 if bool(supervision_row.get("within_special_duration_ceiling", False)) else 0.0
        )
        pause_boundary_count = min(2.0, float(supervision_row.get("pause_boundary_count", 0.0)))

        target_presence[index] = clamp01(
            float(config.get("base_presence_target", 0.24))
            - proximity_score * float(config.get("proximity_presence_scale", 0.08))
            - within_special_duration_ceiling * float(config.get("duration_ceiling_presence_offset", 0.03))
        )
        target_fall[index] = clamp01(
            float(config.get("base_fall_target", 0.38))
            + proximity_score * float(config.get("proximity_fall_scale", 0.03))
            + pause_boundary_count * float(config.get("pause_fall_scale", 0.02))
        )
        target_energy[index] = clamp01(
            float(config.get("base_energy_target", 0.28))
            - proximity_score * float(config.get("proximity_energy_scale", 0.06))
            - no_terminal_bonus * float(config.get("no_terminal_energy_offset", 0.03))
        )
        target_peak_ratio[index] = clamp01(
            float(config.get("base_peak_ratio_target", 0.08))
            - proximity_score * float(config.get("proximity_peak_ratio_scale", 0.03))
            - within_special_duration_ceiling * float(config.get("duration_ceiling_peak_ratio_offset", 0.015))
        )

    if float(active_mask.sum().item()) <= 0.0:
        return zero

    effective_weight = (sample_weights * active_mask).clamp_min(0.0)
    if float(effective_weight.sum().item()) <= 0.0:
        return zero

    total_loss = (
        ((presence_mean - target_presence) ** 2) * effective_weight
        + ((fall_mean - target_fall) ** 2) * effective_weight
        + ((energy_mean - target_energy) ** 2) * effective_weight
        + ((peak_ratio - target_peak_ratio) ** 2) * effective_weight
    ).sum()
    total_weight = (effective_weight * 4.0).sum().clamp_min(1.0)
    return total_loss / total_weight


def compute_structural_clause_profile_aux_loss(
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
    target_special_supervision: list[dict[str, object] | None] | None,
    weights: dict[str, object],
) -> torch.Tensor:
    config = weights.get("structural_clause_profile_aux")
    event_logits = outputs["event_logits"]
    zero = torch.zeros((), device=event_logits.device, dtype=event_logits.dtype)
    if not isinstance(config, dict) or not bool(config.get("enabled", False)):
        return zero
    if not target_special_supervision:
        return zero

    event_probs = torch.sigmoid(event_logits)
    delta_dimension = int(config.get("delta_dimension", 1))
    fall_dimension = int(config.get("fall_dimension", 6))
    energy_dimension = int(config.get("energy_dimension", 7))
    presence_dimension = int(config.get("presence_dimension", 0))
    peak_threshold = float(config.get("presence_peak_threshold", 0.55))

    delta_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., delta_dimension],
        frame_mask=frame_mask,
    )
    fall_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., fall_dimension],
        frame_mask=frame_mask,
    )
    energy_mean = masked_frame_channel_mean_tensor(
        tensor=event_probs[..., energy_dimension],
        frame_mask=frame_mask,
    )
    peak_ratio = masked_threshold_ratio_tensor(
        tensor=event_probs[..., presence_dimension],
        frame_mask=frame_mask,
        threshold=peak_threshold,
    )

    batch_size = int(frame_mask.shape[0])
    active_mask = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    sample_weight = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_delta = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_fall = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_energy = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    target_peak_ratio = torch.zeros((batch_size,), device=event_probs.device, dtype=event_probs.dtype)
    pool_memberships = [str(value) for value in list(config.get("pool_memberships", [])) if str(value)]
    min_clause_count = int(config.get("min_clause_count", 4))

    for index in range(min(batch_size, len(target_special_supervision))):
        supervision_row = target_special_supervision[index]
        if not isinstance(supervision_row, dict):
            continue
        raw_pool_memberships = supervision_row.get("pool_memberships")
        if pool_memberships:
            if not isinstance(raw_pool_memberships, dict):
                continue
            if not any(bool(raw_pool_memberships.get(pool_name, False)) for pool_name in pool_memberships):
                continue
        clause_count = int(supervision_row.get("clause_count", 0))
        if clause_count < min_clause_count:
            continue
        active_mask[index] = 1.0
        clause_excess = max(0, clause_count - min_clause_count)
        pause_count = float(supervision_row.get("pause_boundary_count", 0.0))
        terminal_count = float(supervision_row.get("terminal_boundary_count", 0.0))
        final_none_bonus = 1.0 if str(supervision_row.get("final_terminal_type", "")) == "none" else 0.0
        sample_weight[index] = max(
            0.0,
            float(config.get("base_sample_weight", 0.5))
            + clause_excess * float(config.get("clause_weight_scale", 0.08))
            + min(pause_count, 6.0) * float(config.get("pause_weight_scale", 0.02)),
        )
        target_delta[index] = clamp01(
            float(config.get("base_delta_target", 0.46))
            + clause_excess * float(config.get("clause_delta_scale", 0.04))
            + min(pause_count, 6.0) * float(config.get("pause_delta_scale", 0.015))
        )
        target_fall[index] = clamp01(
            float(config.get("base_fall_target", 0.5))
            + clause_excess * float(config.get("clause_fall_scale", 0.035))
            + min(terminal_count, 3.0) * float(config.get("terminal_fall_scale", 0.02))
        )
        target_energy[index] = clamp01(
            float(config.get("base_energy_target", 0.62))
            - clause_excess * float(config.get("clause_energy_scale", 0.015))
            - min(pause_count, 6.0) * float(config.get("pause_energy_scale", 0.015))
            - final_none_bonus * float(config.get("no_terminal_energy_offset", 0.02))
        )
        target_peak_ratio[index] = clamp01(
            float(config.get("base_peak_ratio_target", 0.48))
            + clause_excess * float(config.get("clause_peak_ratio_scale", 0.03))
            + min(terminal_count, 3.0) * float(config.get("terminal_peak_ratio_scale", 0.015))
        )

    if float(active_mask.sum().item()) <= 0.0:
        return zero

    effective_weight = (active_mask * sample_weight).clamp_min(0.0)
    if float(effective_weight.sum().item()) <= 0.0:
        return zero

    total_loss = (
        ((delta_mean - target_delta) ** 2) * effective_weight
        + ((fall_mean - target_fall) ** 2) * effective_weight
        + ((energy_mean - target_energy) ** 2) * effective_weight
        + ((peak_ratio - target_peak_ratio) ** 2) * effective_weight
    ).sum()
    total_weight = (effective_weight * 4.0).sum().clamp_min(1.0)
    return total_loss / total_weight


def accumulate_aux_channel_loss(
    total_loss: torch.Tensor,
    total_weight: torch.Tensor,
    channel: torch.Tensor,
    weight_map: torch.Tensor,
    target_value: object,
) -> tuple[torch.Tensor, torch.Tensor]:
    if target_value is None:
        return total_loss, total_weight
    if float(weight_map.max().item()) <= 0.0:
        return total_loss, total_weight
    target_tensor = torch.full_like(channel, float(target_value))
    weighted_error = ((channel - target_tensor) ** 2) * weight_map
    return total_loss + weighted_error.sum(), total_weight + weight_map.sum()


def accumulate_margin_aux_loss(
    total_loss: torch.Tensor,
    total_weight: torch.Tensor,
    pre_channel: torch.Tensor,
    post_channel: torch.Tensor,
    pre_weight: torch.Tensor,
    post_weight: torch.Tensor,
    pair_weight: torch.Tensor,
    margin: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    if margin <= 0.0:
        return total_loss, total_weight
    effective_weight = torch.minimum(torch.minimum(pre_weight, post_weight), pair_weight)
    if float(effective_weight.max().item()) <= 0.0:
        return total_loss, total_weight
    violation = torch.relu(margin - (pre_channel - post_channel))
    weighted_error = (violation ** 2) * effective_weight
    return total_loss + weighted_error.sum(), total_weight + effective_weight.sum()


def masked_frame_channel_mean_tensor(
    tensor: torch.Tensor,
    frame_mask: torch.Tensor,
) -> torch.Tensor:
    weights = frame_mask.to(tensor.dtype)
    numerator = (tensor * weights).sum(dim=1)
    denominator = weights.sum(dim=1).clamp_min(1.0)
    return numerator / denominator


def masked_threshold_ratio_tensor(
    tensor: torch.Tensor,
    frame_mask: torch.Tensor,
    threshold: float,
) -> torch.Tensor:
    weights = frame_mask.to(tensor.dtype)
    positives = ((tensor >= threshold).to(tensor.dtype) * weights).sum(dim=1)
    denominator = weights.sum(dim=1).clamp_min(1.0)
    return positives / denominator


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_punctuation_profile(text: str) -> tuple[float, bool]:
    if not text:
        return 0.0, False
    punctuation_count = sum(1 for char in text if char in PUNCTUATION_PROFILE_SET)
    punctuation_ratio = punctuation_count / max(1, len(text))
    punctuation_only = punctuation_count == len(text)
    return punctuation_ratio, punctuation_only


def apply_clause_role_bias(
    adjusted_target: torch.Tensor,
    bias: torch.Tensor,
    clause_role_strengths: dict[str, torch.Tensor] | None,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
    config: dict[str, object],
    presence_dimension: int,
    energy_dimension: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if not clause_role_strengths:
        return adjusted_target, bias
    raw_overrides = config.get("clause_role_target_overrides")
    if not isinstance(raw_overrides, dict):
        return adjusted_target, bias

    for role, override in raw_overrides.items():
        if not isinstance(override, dict):
            continue
        strength_map = clause_role_strengths.get(str(role))
        if strength_map is None:
            continue
        strength_map = apply_structure_type_gate(
            strength_map=strength_map,
            structure_types=override.get("structure_types"),
            utterance_structure_strengths=utterance_structure_strengths,
        )
        if float(strength_map.max().item()) <= 0.0:
            continue

        presence_boost = float(override.get("presence_boost", 0.0))
        energy_boost = float(override.get("energy_boost", 0.0))
        if presence_boost != 0.0:
            bias[..., presence_dimension] += strength_map * presence_boost
        if energy_boost != 0.0:
            bias[..., energy_dimension] += strength_map * energy_boost
        if "presence_floor_target" in override:
            adjusted_target[..., presence_dimension] = torch.maximum(
                adjusted_target[..., presence_dimension],
                strength_map * float(override["presence_floor_target"]),
            )
        if "energy_floor_target" in override:
            adjusted_target[..., energy_dimension] = torch.maximum(
                adjusted_target[..., energy_dimension],
                strength_map * float(override["energy_floor_target"]),
            )

    return adjusted_target, bias


def apply_structure_type_gate(
    strength_map: torch.Tensor,
    structure_types: object,
    utterance_structure_strengths: dict[str, torch.Tensor] | None,
) -> torch.Tensor:
    if not isinstance(structure_types, list) or not utterance_structure_strengths:
        return strength_map
    structure_gate = torch.zeros_like(strength_map)
    for structure_type in structure_types:
        structure_strength = utterance_structure_strengths.get(str(structure_type))
        if structure_strength is None:
            continue
        structure_gate = torch.maximum(structure_gate, structure_strength)
    return strength_map * structure_gate


def shift_strength_map(
    strength_map: torch.Tensor,
    offset: int,
) -> torch.Tensor:
    shifted = torch.zeros_like(strength_map)
    if offset == 0:
        shifted.copy_(strength_map)
        return shifted
    if offset > 0:
        shifted[:, offset:] = strength_map[:, :-offset]
        return shifted
    positive_offset = -offset
    shifted[:, :-positive_offset] = strength_map[:, positive_offset:]
    return shifted


def blend_event_channel(
    channel: torch.Tensor,
    strength_map: torch.Tensor,
    target_value: float,
) -> torch.Tensor:
    blend = strength_map.clamp(0.0, 1.0)
    target_tensor = torch.full_like(channel, float(target_value))
    return channel * (1.0 - blend) + target_tensor * blend
