from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from v5vc.streaming_student.proxy_acoustic import build_streaming_student_proxy_acoustic


RESERVED_SUPERVISION_PAYLOAD_KEYS = {
    "loss_weights",
    "loss_weight_schedule",
    "semantic_supervision",
}


def build_default_teacher_supervision_weights() -> dict[str, float]:
    return {
        "teacher_z_art": 1.0,
        "teacher_event": 1.0,
        "teacher_event_prior": 0.5,
        "teacher_energy_proxy": 0.25,
        "teacher_vuv_proxy": 0.15,
        "teacher_aper_proxy": 0.1,
        "teacher_proxy_acoustic": 0.0,
        "teacher_proxy_temporal": 0.0,
        "log_f0_correction_l1": 0.01,
        "aper_correction_l1": 0.01,
    }


def resolve_teacher_supervision_weights(
    overrides: Mapping[str, object] | None = None,
    overrides_path: Path | None = None,
) -> dict[str, float]:
    effective_weights = build_default_teacher_supervision_weights()
    merged_overrides: dict[str, object] = {}
    if overrides_path is not None:
        payload = load_teacher_supervision_payload(overrides_path)
        raw_overrides = payload.get("loss_weights")
        if raw_overrides is None:
            raw_overrides = {
                str(key): value
                for key, value in payload.items()
                if str(key) not in RESERVED_SUPERVISION_PAYLOAD_KEYS
            }
        if not isinstance(raw_overrides, dict):
            raise ValueError(
                "Loss weight override payload must be a flat object or contain a 'loss_weights' object: "
                f"{overrides_path}"
            )
        merged_overrides.update(raw_overrides)
    if overrides is not None:
        merged_overrides.update(dict(overrides))

    unknown_keys = sorted({str(key) for key in merged_overrides.keys()} - set(effective_weights.keys()))
    if unknown_keys:
        raise ValueError(f"Unknown Stage3 loss weight keys: {unknown_keys}")

    for key, value in merged_overrides.items():
        effective_weights[str(key)] = float(value)
    return effective_weights


def load_teacher_supervision_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Loss weight payload must be a JSON object: {path}")
    return payload


def build_default_semantic_supervision_config() -> dict[str, object]:
    return {
        "enabled": False,
        "required_contract_version": "target_event_semantic_sidecar_v1",
        "clean_text_bonus": 0.08,
        "multi_clause_bonus": 0.08,
        "multi_terminal_bonus": 0.10,
        "clause_ge4_bonus": 0.08,
        "pause_multi_bonus": 0.05,
        "terminal_present_bonus": 0.05,
        "nonverbal_penalty": 0.20,
        "event_prior_alpha": 1.0,
        "event_alpha": 0.35,
        "z_art_alpha": 0.20,
        "min_multiplier": 0.75,
        "max_multiplier": 1.45,
    }


def resolve_semantic_supervision_config(
    config: Mapping[str, object] | None = None,
    overrides: Mapping[str, object] | None = None,
    overrides_path: Path | None = None,
) -> dict[str, object]:
    effective = build_default_semantic_supervision_config()
    merged: dict[str, object] = {}
    if config is not None:
        if not isinstance(config, Mapping):
            raise ValueError("Stage3 semantic supervision config must be a mapping object.")
        merged.update(dict(config))
    if overrides_path is not None:
        payload = load_teacher_supervision_payload(overrides_path)
        raw_config = payload.get("semantic_supervision", {})
        if not isinstance(raw_config, dict):
            raise ValueError(
                "Loss weight payload field 'semantic_supervision' must be a JSON object: "
                f"{overrides_path}"
            )
        merged.update(raw_config)
    if overrides is not None:
        if not isinstance(overrides, Mapping):
            raise ValueError("Stage3 semantic supervision overrides must be a mapping object.")
        merged.update(dict(overrides))

    unknown_keys = sorted({str(key) for key in merged.keys()} - set(effective.keys()))
    if unknown_keys:
        raise ValueError(f"Unknown Stage3 semantic supervision keys: {unknown_keys}")

    for key, value in merged.items():
        normalized_key = str(key)
        if normalized_key == "enabled":
            effective[normalized_key] = bool(value)
        elif normalized_key == "required_contract_version":
            effective[normalized_key] = None if value in {None, ""} else str(value)
        else:
            effective[normalized_key] = float(value)
    if float(effective["min_multiplier"]) <= 0.0:
        raise ValueError("Stage3 semantic supervision min_multiplier must be > 0.")
    if float(effective["max_multiplier"]) < float(effective["min_multiplier"]):
        raise ValueError("Stage3 semantic supervision max_multiplier must be >= min_multiplier.")
    return effective


def resolve_teacher_supervision_weight_schedule(
    overrides_path: Path | None = None,
    overrides: Mapping[str, object] | None = None,
) -> dict[str, dict[str, float | str | int]]:
    known_weight_keys = set(build_default_teacher_supervision_weights().keys())
    merged_schedule: dict[str, object] = {}
    if overrides_path is not None:
        payload = load_teacher_supervision_payload(overrides_path)
        raw_schedule = payload.get("loss_weight_schedule", {})
        if not isinstance(raw_schedule, dict):
            raise ValueError(
                "Loss weight payload field 'loss_weight_schedule' must be a JSON object: "
                f"{overrides_path}"
            )
        merged_schedule.update(raw_schedule)
    if overrides is not None:
        merged_schedule.update(dict(overrides))

    resolved: dict[str, dict[str, float | str | int]] = {}
    for key, raw_spec in merged_schedule.items():
        normalized_key = str(key)
        if normalized_key not in known_weight_keys:
            raise ValueError(f"Unknown Stage3 loss weight schedule key: {normalized_key}")
        if not isinstance(raw_spec, dict):
            raise ValueError(
                f"Stage3 loss weight schedule for '{normalized_key}' must be a JSON object."
            )
        schedule_type = str(raw_spec.get("type", "linear_warmup_hold")).strip().lower()
        if schedule_type != "linear_warmup_hold":
            raise ValueError(
                f"Unsupported Stage3 loss weight schedule type for '{normalized_key}': {schedule_type}"
            )
        warmup_steps = int(raw_spec.get("warmup_steps", 1))
        if warmup_steps < 1:
            raise ValueError(
                f"Stage3 loss weight schedule warmup_steps must be >= 1 for '{normalized_key}'."
            )
        resolved[normalized_key] = {
            "type": "linear_warmup_hold",
            "start_weight": float(raw_spec.get("start_weight", 0.0)),
            "warmup_steps": warmup_steps,
        }
    return resolved


def apply_teacher_supervision_weight_schedule(
    base_weights: Mapping[str, float],
    schedule: Mapping[str, Mapping[str, float | str | int]] | None,
    step: int,
) -> dict[str, float]:
    effective_weights = {str(key): float(value) for key, value in base_weights.items()}
    if not schedule:
        return effective_weights

    current_step = max(1, int(step))
    for key, raw_spec in schedule.items():
        target_weight = float(effective_weights[str(key)])
        schedule_type = str(raw_spec.get("type", "linear_warmup_hold")).strip().lower()
        if schedule_type != "linear_warmup_hold":
            raise ValueError(f"Unsupported Stage3 loss weight schedule type for '{key}': {schedule_type}")
        start_weight = float(raw_spec.get("start_weight", 0.0))
        warmup_steps = max(1, int(raw_spec.get("warmup_steps", 1)))
        if warmup_steps == 1:
            effective_weights[str(key)] = target_weight
            continue
        progress = min(max((current_step - 1) / float(warmup_steps - 1), 0.0), 1.0)
        effective_weights[str(key)] = start_weight + (target_weight - start_weight) * progress
    return effective_weights


def compute_streaming_student_teacher_supervision_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    weights: dict[str, float] | None = None,
    use_teacher_confidence: bool = True,
    semantic_supervision: Mapping[str, object] | None = None,
) -> tuple[torch.Tensor, dict[str, float | bool]]:
    default_weights = build_default_teacher_supervision_weights()
    effective_weights = resolve_teacher_supervision_weights(overrides=weights)
    semantic_config = resolve_semantic_supervision_config(config=semantic_supervision)

    frame_mask = batch["teacher_frame_mask"]
    frame_weight = build_frame_weight(
        frame_mask=frame_mask,
        teacher_frame_confidence=batch["teacher_frame_confidence"],
        use_teacher_confidence=use_teacher_confidence,
    )
    semantic_loss_multipliers, semantic_metrics = build_semantic_loss_multipliers(
        batch=batch,
        semantic_supervision=semantic_config,
        device=frame_weight.device,
        dtype=frame_weight.dtype,
    )

    teacher_event_probs = batch["teacher_event_probs"]
    teacher_acoustic = batch["teacher_acoustic"]
    student_proxy_acoustic = build_streaming_student_proxy_acoustic(outputs)

    z_art_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["z_art"],
        target=batch["teacher_z_art"],
        frame_weight=frame_weight,
    )
    event_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["event_logits"],
        target=teacher_event_probs,
        frame_weight=frame_weight,
    )
    event_prior_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["event_prior_logits"],
        target=teacher_event_probs,
        frame_weight=frame_weight,
    )
    energy_proxy_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["energy"],
        target=teacher_acoustic[..., 0:1],
        frame_weight=frame_weight,
    )
    vuv_proxy_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["vuv_logits"],
        target=teacher_event_probs[..., 3:4],
        frame_weight=frame_weight,
    )
    aper_proxy_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["aperiodicity"],
        target=teacher_event_probs[..., 2:3],
        frame_weight=frame_weight,
    )
    proxy_acoustic_loss_per_sample = masked_mse_per_sample(
        prediction=student_proxy_acoustic,
        target=teacher_acoustic,
        frame_weight=frame_weight,
    )
    proxy_temporal_loss_per_sample = masked_temporal_mse_per_sample(
        prediction=student_proxy_acoustic,
        target=teacher_acoustic,
        frame_weight=frame_weight,
    )
    log_f0_correction_l1_per_sample = masked_l1_per_sample(
        prediction=outputs["log_f0_correction"],
        frame_weight=frame_weight,
    )
    aper_correction_l1_per_sample = masked_l1_per_sample(
        prediction=outputs["aper_correction"],
        frame_weight=frame_weight,
    )
    z_art_loss = reduce_weighted_sample_loss(
        z_art_loss_per_sample,
        semantic_loss_multipliers["teacher_z_art"],
    )
    event_loss = reduce_weighted_sample_loss(
        event_loss_per_sample,
        semantic_loss_multipliers["teacher_event"],
    )
    event_prior_loss = reduce_weighted_sample_loss(
        event_prior_loss_per_sample,
        semantic_loss_multipliers["teacher_event_prior"],
    )
    energy_proxy_loss = reduce_weighted_sample_loss(energy_proxy_loss_per_sample)
    vuv_proxy_loss = reduce_weighted_sample_loss(vuv_proxy_loss_per_sample)
    aper_proxy_loss = reduce_weighted_sample_loss(aper_proxy_loss_per_sample)
    proxy_acoustic_loss = reduce_weighted_sample_loss(proxy_acoustic_loss_per_sample)
    proxy_temporal_loss = reduce_weighted_sample_loss(proxy_temporal_loss_per_sample)
    log_f0_correction_l1 = reduce_weighted_sample_loss(log_f0_correction_l1_per_sample)
    aper_correction_l1 = reduce_weighted_sample_loss(aper_correction_l1_per_sample)
    z_art_loss_reference = reduce_weighted_sample_loss(z_art_loss_per_sample)
    event_loss_reference = reduce_weighted_sample_loss(event_loss_per_sample)
    event_prior_loss_reference = reduce_weighted_sample_loss(event_prior_loss_per_sample)

    total_loss = (
        z_art_loss * effective_weights["teacher_z_art"]
        + event_loss * effective_weights["teacher_event"]
        + event_prior_loss * effective_weights["teacher_event_prior"]
        + energy_proxy_loss * effective_weights["teacher_energy_proxy"]
        + vuv_proxy_loss * effective_weights["teacher_vuv_proxy"]
        + aper_proxy_loss * effective_weights["teacher_aper_proxy"]
        + proxy_acoustic_loss * effective_weights["teacher_proxy_acoustic"]
        + proxy_temporal_loss * effective_weights["teacher_proxy_temporal"]
        + log_f0_correction_l1 * effective_weights["log_f0_correction_l1"]
        + aper_correction_l1 * effective_weights["aper_correction_l1"]
    )
    default_reference_total = (
        z_art_loss * default_weights["teacher_z_art"]
        + event_loss * default_weights["teacher_event"]
        + event_prior_loss * default_weights["teacher_event_prior"]
        + energy_proxy_loss * default_weights["teacher_energy_proxy"]
        + vuv_proxy_loss * default_weights["teacher_vuv_proxy"]
        + aper_proxy_loss * default_weights["teacher_aper_proxy"]
        + proxy_acoustic_loss * default_weights["teacher_proxy_acoustic"]
        + proxy_temporal_loss * default_weights["teacher_proxy_temporal"]
        + log_f0_correction_l1 * default_weights["log_f0_correction_l1"]
        + aper_correction_l1 * default_weights["aper_correction_l1"]
    )
    semantic_disabled_reference_total = (
        z_art_loss_reference * effective_weights["teacher_z_art"]
        + event_loss_reference * effective_weights["teacher_event"]
        + event_prior_loss_reference * effective_weights["teacher_event_prior"]
        + energy_proxy_loss * effective_weights["teacher_energy_proxy"]
        + vuv_proxy_loss * effective_weights["teacher_vuv_proxy"]
        + aper_proxy_loss * effective_weights["teacher_aper_proxy"]
        + proxy_acoustic_loss * effective_weights["teacher_proxy_acoustic"]
        + proxy_temporal_loss * effective_weights["teacher_proxy_temporal"]
        + log_f0_correction_l1 * effective_weights["log_f0_correction_l1"]
        + aper_correction_l1 * effective_weights["aper_correction_l1"]
    )
    metrics = {
        "loss_total": round(float(total_loss.detach().cpu().item()), 6),
        "loss_total_default_reference": round(float(default_reference_total.detach().cpu().item()), 6),
        "loss_total_semantic_disabled_reference": round(
            float(semantic_disabled_reference_total.detach().cpu().item()),
            6,
        ),
        "loss_teacher_z_art": round(float(z_art_loss.detach().cpu().item()), 6),
        "loss_teacher_event": round(float(event_loss.detach().cpu().item()), 6),
        "loss_teacher_event_prior": round(float(event_prior_loss.detach().cpu().item()), 6),
        "loss_teacher_energy_proxy": round(float(energy_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_vuv_proxy": round(float(vuv_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_aper_proxy": round(float(aper_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_proxy_acoustic": round(float(proxy_acoustic_loss.detach().cpu().item()), 6),
        "loss_teacher_proxy_temporal": round(float(proxy_temporal_loss.detach().cpu().item()), 6),
        "loss_log_f0_correction_l1": round(float(log_f0_correction_l1.detach().cpu().item()), 6),
        "loss_aper_correction_l1": round(float(aper_correction_l1.detach().cpu().item()), 6),
        "teacher_confidence_weighted": bool(use_teacher_confidence),
        "effective_weight_sum": round(float(frame_weight.sum().detach().cpu().item()), 6),
    }
    metrics.update(semantic_metrics)
    return total_loss, metrics


def build_semantic_loss_multipliers(
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    semantic_supervision: Mapping[str, object],
    device: torch.device,
    dtype: torch.dtype,
) -> tuple[dict[str, torch.Tensor], dict[str, float | bool]]:
    sidecars = batch.get("target_event_semantic_sidecar")
    if not isinstance(sidecars, list):
        sidecars = []
    batch_size = len(sidecars)
    if batch_size <= 0:
        unit = torch.ones((0, 1, 1), dtype=dtype, device=device)
        return {
            "teacher_z_art": unit,
            "teacher_event": unit,
            "teacher_event_prior": unit,
        }, {
            "semantic_supervision_enabled": bool(semantic_supervision.get("enabled", False)),
            "semantic_sidecar_present_ratio": 0.0,
            "semantic_weight_applied_ratio": 0.0,
            "semantic_clean_text_sample_ratio": 0.0,
            "semantic_nonverbal_sample_ratio": 0.0,
            "semantic_base_multiplier_mean": 1.0,
            "semantic_event_prior_multiplier_mean": 1.0,
            "semantic_event_multiplier_mean": 1.0,
            "semantic_z_art_multiplier_mean": 1.0,
        }

    base_multiplier = torch.ones((batch_size, 1, 1), dtype=dtype, device=device)
    present_count = 0
    applied_count = 0
    clean_text_count = 0
    nonverbal_count = 0
    enabled = bool(semantic_supervision.get("enabled", False))
    required_contract_version = semantic_supervision.get("required_contract_version")
    required_contract_version = None if required_contract_version in {None, ""} else str(required_contract_version)

    for index, row in enumerate(sidecars):
        if not isinstance(row, dict):
            continue
        present_count += 1
        if required_contract_version is not None:
            if str(row.get("semantic_contract_version", "")) != required_contract_version:
                continue
        semantic_scope = dict(row.get("semantic_scope", {})) if isinstance(row.get("semantic_scope"), dict) else {}
        text_semantics = dict(row.get("text_semantics", {})) if isinstance(row.get("text_semantics"), dict) else {}
        boundary_semantics = (
            dict(row.get("boundary_semantics", {}))
            if isinstance(row.get("boundary_semantics"), dict)
            else {}
        )
        utterance_semantics = (
            dict(row.get("utterance_structure_semantics", {}))
            if isinstance(row.get("utterance_structure_semantics"), dict)
            else {}
        )
        multiplier = 1.0
        clean_text_available = bool(semantic_scope.get("clean_text_available", False))
        nonverbal_only = bool(text_semantics.get("nonverbal_only", False))
        if clean_text_available and not nonverbal_only:
            multiplier += float(semantic_supervision["clean_text_bonus"])
            clean_text_count += 1
        if nonverbal_only:
            multiplier -= float(semantic_supervision["nonverbal_penalty"])
            nonverbal_count += 1
        utterance_structure_type = str(utterance_semantics.get("utterance_structure_type", "unknown"))
        if utterance_structure_type == "multi_clause_single_terminal":
            multiplier += float(semantic_supervision["multi_clause_bonus"])
        if utterance_structure_type == "multi_terminal":
            multiplier += float(semantic_supervision["multi_terminal_bonus"])
        if int(utterance_semantics.get("clause_count", 0)) >= 4:
            multiplier += float(semantic_supervision["clause_ge4_bonus"])
        if int(boundary_semantics.get("pause_boundary_count", 0)) >= 2:
            multiplier += float(semantic_supervision["pause_multi_bonus"])
        if int(boundary_semantics.get("terminal_boundary_count", 0)) >= 1:
            multiplier += float(semantic_supervision["terminal_present_bonus"])
        if enabled:
            applied_count += 1
            base_multiplier[index, 0, 0] = float(
                max(
                    float(semantic_supervision["min_multiplier"]),
                    min(float(semantic_supervision["max_multiplier"]), multiplier),
                )
            )

    event_prior_multiplier = 1.0 + (base_multiplier - 1.0) * float(semantic_supervision["event_prior_alpha"])
    event_multiplier = 1.0 + (base_multiplier - 1.0) * float(semantic_supervision["event_alpha"])
    z_art_multiplier = 1.0 + (base_multiplier - 1.0) * float(semantic_supervision["z_art_alpha"])
    metrics: dict[str, float | bool] = {
        "semantic_supervision_enabled": enabled,
        "semantic_sidecar_present_ratio": round(present_count / max(1, batch_size), 6),
        "semantic_weight_applied_ratio": round(applied_count / max(1, batch_size), 6),
        "semantic_clean_text_sample_ratio": round(clean_text_count / max(1, batch_size), 6),
        "semantic_nonverbal_sample_ratio": round(nonverbal_count / max(1, batch_size), 6),
        "semantic_base_multiplier_mean": round(float(base_multiplier.mean().detach().cpu().item()), 6),
        "semantic_event_prior_multiplier_mean": round(
            float(event_prior_multiplier.mean().detach().cpu().item()),
            6,
        ),
        "semantic_event_multiplier_mean": round(float(event_multiplier.mean().detach().cpu().item()), 6),
        "semantic_z_art_multiplier_mean": round(float(z_art_multiplier.mean().detach().cpu().item()), 6),
    }
    return {
        "teacher_z_art": z_art_multiplier,
        "teacher_event": event_multiplier,
        "teacher_event_prior": event_prior_multiplier,
    }, metrics


def build_frame_weight(
    frame_mask: torch.Tensor,
    teacher_frame_confidence: torch.Tensor,
    use_teacher_confidence: bool,
) -> torch.Tensor:
    frame_weight = frame_mask.to(torch.float32).unsqueeze(-1)
    if use_teacher_confidence:
        frame_weight = frame_weight * teacher_frame_confidence.to(torch.float32).clamp_min(0.0)
    return frame_weight


def masked_mse(
    prediction: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (((prediction - target) ** 2) * frame_weight).sum()
    denominator = frame_weight.sum().clamp_min(1.0)
    return numerator / denominator


def masked_mse_per_sample(
    prediction: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (((prediction - target) ** 2) * frame_weight).sum(dim=tuple(range(1, prediction.ndim)))
    denominator = frame_weight.sum(dim=tuple(range(1, frame_weight.ndim))).clamp_min(1.0)
    return numerator / denominator


def masked_l1(
    prediction: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (prediction.abs() * frame_weight).sum()
    denominator = frame_weight.sum().clamp_min(1.0)
    return numerator / denominator


def masked_l1_per_sample(
    prediction: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (prediction.abs() * frame_weight).sum(dim=tuple(range(1, prediction.ndim)))
    denominator = frame_weight.sum(dim=tuple(range(1, frame_weight.ndim))).clamp_min(1.0)
    return numerator / denominator


def masked_bce_with_logits(
    logits: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (F.binary_cross_entropy_with_logits(logits, target, reduction="none") * frame_weight).sum()
    denominator = frame_weight.sum().clamp_min(1.0)
    return numerator / denominator


def masked_bce_with_logits_per_sample(
    logits: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (
        F.binary_cross_entropy_with_logits(logits, target, reduction="none") * frame_weight
    ).sum(dim=tuple(range(1, logits.ndim)))
    denominator = frame_weight.sum(dim=tuple(range(1, frame_weight.ndim))).clamp_min(1.0)
    return numerator / denominator


def masked_temporal_mse(
    prediction: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    if prediction.shape[1] <= 1 or target.shape[1] <= 1:
        return prediction.new_tensor(0.0)
    prediction_delta = prediction[:, 1:] - prediction[:, :-1]
    target_delta = target[:, 1:] - target[:, :-1]
    temporal_weight = torch.minimum(frame_weight[:, 1:], frame_weight[:, :-1]).expand_as(prediction_delta)
    numerator = (((prediction_delta - target_delta) ** 2) * temporal_weight).sum()
    denominator = temporal_weight.sum().clamp_min(1.0)
    return numerator / denominator


def masked_temporal_mse_per_sample(
    prediction: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    if prediction.shape[1] <= 1 or target.shape[1] <= 1:
        return prediction.new_zeros((prediction.shape[0],))
    prediction_delta = prediction[:, 1:] - prediction[:, :-1]
    target_delta = target[:, 1:] - target[:, :-1]
    temporal_weight = torch.minimum(frame_weight[:, 1:], frame_weight[:, :-1]).expand_as(prediction_delta)
    numerator = (((prediction_delta - target_delta) ** 2) * temporal_weight).sum(
        dim=tuple(range(1, prediction_delta.ndim))
    )
    denominator = temporal_weight.sum(dim=tuple(range(1, temporal_weight.ndim))).clamp_min(1.0)
    return numerator / denominator


def reduce_weighted_sample_loss(
    loss_per_sample: torch.Tensor,
    sample_weight: torch.Tensor | None = None,
) -> torch.Tensor:
    if loss_per_sample.numel() <= 0:
        return loss_per_sample.new_tensor(0.0)
    if sample_weight is None:
        return loss_per_sample.mean()
    normalized_sample_weight = sample_weight.to(loss_per_sample.device, dtype=loss_per_sample.dtype).reshape(-1)
    if normalized_sample_weight.numel() != loss_per_sample.numel():
        raise ValueError("Sample weight size mismatch for Stage3 semantic supervision.")
    return (loss_per_sample * normalized_sample_weight).mean()
