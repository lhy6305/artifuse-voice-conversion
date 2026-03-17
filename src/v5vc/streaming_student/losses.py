from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from v5vc.streaming_student.proxy_acoustic import build_streaming_student_proxy_acoustic


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
        raw_overrides = payload.get("loss_weights", payload)
        if "loss_weight_schedule" in payload and raw_overrides is payload and len(payload) == 1:
            raw_overrides = {}
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
) -> tuple[torch.Tensor, dict[str, float]]:
    default_weights = build_default_teacher_supervision_weights()
    effective_weights = resolve_teacher_supervision_weights(overrides=weights)

    frame_mask = batch["teacher_frame_mask"]
    frame_weight = build_frame_weight(
        frame_mask=frame_mask,
        teacher_frame_confidence=batch["teacher_frame_confidence"],
        use_teacher_confidence=use_teacher_confidence,
    )

    teacher_event_probs = batch["teacher_event_probs"]
    teacher_acoustic = batch["teacher_acoustic"]
    student_proxy_acoustic = build_streaming_student_proxy_acoustic(outputs)

    z_art_loss = masked_mse(
        prediction=outputs["z_art"],
        target=batch["teacher_z_art"],
        frame_weight=frame_weight,
    )
    event_loss = masked_bce_with_logits(
        logits=outputs["event_logits"],
        target=teacher_event_probs,
        frame_weight=frame_weight,
    )
    event_prior_loss = masked_bce_with_logits(
        logits=outputs["event_prior_logits"],
        target=teacher_event_probs,
        frame_weight=frame_weight,
    )
    energy_proxy_loss = masked_mse(
        prediction=outputs["energy"],
        target=teacher_acoustic[..., 0:1],
        frame_weight=frame_weight,
    )
    vuv_proxy_loss = masked_bce_with_logits(
        logits=outputs["vuv_logits"],
        target=teacher_event_probs[..., 3:4],
        frame_weight=frame_weight,
    )
    aper_proxy_loss = masked_mse(
        prediction=outputs["aperiodicity"],
        target=teacher_event_probs[..., 2:3],
        frame_weight=frame_weight,
    )
    proxy_acoustic_loss = masked_mse(
        prediction=student_proxy_acoustic,
        target=teacher_acoustic,
        frame_weight=frame_weight,
    )
    proxy_temporal_loss = masked_temporal_mse(
        prediction=student_proxy_acoustic,
        target=teacher_acoustic,
        frame_weight=frame_weight,
    )
    log_f0_correction_l1 = masked_l1(
        prediction=outputs["log_f0_correction"],
        frame_weight=frame_weight,
    )
    aper_correction_l1 = masked_l1(
        prediction=outputs["aper_correction"],
        frame_weight=frame_weight,
    )

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
    metrics = {
        "loss_total": round(float(total_loss.detach().cpu().item()), 6),
        "loss_total_default_reference": round(float(default_reference_total.detach().cpu().item()), 6),
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
    return total_loss, metrics


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


def masked_l1(
    prediction: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (prediction.abs() * frame_weight).sum()
    denominator = frame_weight.sum().clamp_min(1.0)
    return numerator / denominator


def masked_bce_with_logits(
    logits: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    numerator = (F.binary_cross_entropy_with_logits(logits, target, reduction="none") * frame_weight).sum()
    denominator = frame_weight.sum().clamp_min(1.0)
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
