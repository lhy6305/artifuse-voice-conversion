from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path

import torch
import torch.nn.functional as F

from v5vc.event_semantics import (
    CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION,
    DESIGN_STATE_E_EVT_V1_CONTRACT_VERSION,
    DESIGN_STATE_E_EVT_V1_LABEL_SPACE_VERSION,
)
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
        "teacher_timing_pause_boundary": 0.0,
        "teacher_timing_terminal_boundary": 0.0,
        "teacher_timing_final_clause": 0.0,
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
        "event_target_family": "teacher_e_evt_v1",
        "required_contract_version": "target_event_semantic_sidecar_v1",
        "required_timing_contract_version": "target_event_timing_semantic_sidecar_v1",
        "timing_frame_routing_enabled": True,
        "clean_text_bonus": 0.08,
        "multi_clause_bonus": 0.08,
        "multi_terminal_bonus": 0.10,
        "clause_ge4_bonus": 0.08,
        "pause_multi_bonus": 0.05,
        "terminal_present_bonus": 0.05,
        "timing_ready_bonus": 0.04,
        "timing_multi_clause_bonus": 0.04,
        "timing_pause_present_bonus": 0.03,
        "timing_terminal_present_bonus": 0.03,
        "timing_nonboundary_scale": 0.92,
        "timing_pause_boundary_boost": 1.20,
        "timing_terminal_boundary_boost": 1.35,
        "timing_final_clause_boost": 1.05,
        "timing_event_prior_mask_alpha": 1.0,
        "timing_event_mask_alpha": 0.35,
        "timing_z_art_mask_alpha": 0.20,
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
        if normalized_key in {"enabled", "timing_frame_routing_enabled"}:
            effective[normalized_key] = bool(value)
        elif normalized_key in {
            "event_target_family",
            "required_contract_version",
            "required_timing_contract_version",
        }:
            effective[normalized_key] = None if value in {None, ""} else str(value)
        else:
            effective[normalized_key] = float(value)
    event_target_family = str(effective["event_target_family"]).strip().lower()
    if event_target_family not in {"legacy_event_probs", "teacher_e_evt_v1"}:
        raise ValueError(
            "Stage3 semantic supervision event_target_family must be one of: "
            "legacy_event_probs, teacher_e_evt_v1."
        )
    effective["event_target_family"] = event_target_family
    if float(effective["min_multiplier"]) <= 0.0:
        raise ValueError("Stage3 semantic supervision min_multiplier must be > 0.")
    if float(effective["max_multiplier"]) < float(effective["min_multiplier"]):
        raise ValueError("Stage3 semantic supervision max_multiplier must be >= min_multiplier.")
    return effective


def resolve_teacher_event_supervision_targets(
    batch: Mapping[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    semantic_supervision: Mapping[str, object],
) -> dict[str, torch.Tensor | str]:
    event_target_family = str(semantic_supervision.get("event_target_family", "teacher_e_evt_v1")).strip().lower()
    teacher_e_evt = batch["teacher_e_evt"]
    teacher_event_probs = batch["teacher_event_probs"]
    if not isinstance(teacher_e_evt, torch.Tensor):
        raise ValueError("Stage3 batch is missing tensor teacher_e_evt.")
    if not isinstance(teacher_event_probs, torch.Tensor):
        raise ValueError("Stage3 batch is missing tensor teacher_event_probs.")

    if event_target_family == "teacher_e_evt_v1":
        return {
            "event_target_family": "teacher_e_evt_v1",
            "event_target": teacher_e_evt,
            "event_contract_version": DESIGN_STATE_E_EVT_V1_CONTRACT_VERSION,
            "event_label_space_version": DESIGN_STATE_E_EVT_V1_LABEL_SPACE_VERSION,
            # Keep proxy targets fixed on named e_evt dims so A/B only changes event supervision family.
            "proxy_target_family": "teacher_e_evt_v1",
            "proxy_target": teacher_e_evt,
            "proxy_contract_version": DESIGN_STATE_E_EVT_V1_CONTRACT_VERSION,
            "proxy_label_space_version": DESIGN_STATE_E_EVT_V1_LABEL_SPACE_VERSION,
        }
    if event_target_family == "legacy_event_probs":
        return {
            "event_target_family": "legacy_event_probs",
            "event_target": teacher_event_probs,
            "event_contract_version": CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION,
            "event_label_space_version": CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION,
            # Keep proxy targets fixed on named e_evt dims so A/B only changes event supervision family.
            "proxy_target_family": "teacher_e_evt_v1",
            "proxy_target": teacher_e_evt,
            "proxy_contract_version": DESIGN_STATE_E_EVT_V1_CONTRACT_VERSION,
            "proxy_label_space_version": DESIGN_STATE_E_EVT_V1_LABEL_SPACE_VERSION,
        }
    raise ValueError(
        "Unsupported Stage3 event_target_family resolved at loss time: "
        f"{event_target_family}"
    )


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
) -> tuple[torch.Tensor, dict[str, float | bool | str]]:
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
    timing_frame_multipliers, timing_frame_metrics = build_timing_frame_loss_multipliers(
        batch=batch,
        semantic_supervision=semantic_config,
        teacher_frame_mask=frame_mask,
        device=frame_weight.device,
        dtype=frame_weight.dtype,
    )

    event_target_bundle = resolve_teacher_event_supervision_targets(
        batch=batch,
        semantic_supervision=semantic_config,
    )
    teacher_event_target = event_target_bundle["event_target"]
    teacher_proxy_target = event_target_bundle["proxy_target"]
    if not isinstance(teacher_event_target, torch.Tensor):
        raise ValueError("Resolved Stage3 teacher event target must be a torch Tensor.")
    if not isinstance(teacher_proxy_target, torch.Tensor):
        raise ValueError("Resolved Stage3 proxy event target must be a torch Tensor.")
    teacher_acoustic = batch["teacher_acoustic"]
    student_proxy_acoustic = build_streaming_student_proxy_acoustic(outputs)

    z_art_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["z_art"],
        target=batch["teacher_z_art"],
        frame_weight=frame_weight * timing_frame_multipliers["teacher_z_art"],
    )
    event_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["event_logits"],
        target=teacher_event_target,
        frame_weight=frame_weight * timing_frame_multipliers["teacher_event"],
    )
    event_prior_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["event_prior_logits"],
        target=teacher_event_target,
        frame_weight=frame_weight * timing_frame_multipliers["teacher_event_prior"],
    )
    timing_aux_targets, timing_aux_metrics = build_timing_auxiliary_targets(
        batch=batch,
        teacher_frame_mask=frame_mask,
        device=frame_weight.device,
        dtype=frame_weight.dtype,
    )
    timing_pause_boundary_loss_per_sample = masked_optional_bce_with_logits_per_sample(
        logits=outputs["timing_pause_boundary_logits"],
        target=timing_aux_targets["pause_boundary"],
        frame_weight=frame_weight,
    )
    timing_terminal_boundary_loss_per_sample = masked_optional_bce_with_logits_per_sample(
        logits=outputs["timing_terminal_boundary_logits"],
        target=timing_aux_targets["terminal_boundary"],
        frame_weight=frame_weight,
    )
    timing_final_clause_loss_per_sample = masked_optional_bce_with_logits_per_sample(
        logits=outputs["timing_final_clause_logits"],
        target=timing_aux_targets["final_clause"],
        frame_weight=frame_weight,
    )
    energy_proxy_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["energy"],
        target=teacher_acoustic[..., 0:1],
        frame_weight=frame_weight,
    )
    vuv_proxy_loss_per_sample = masked_bce_with_logits_per_sample(
        logits=outputs["vuv_logits"],
        target=teacher_proxy_target[..., 3:4],
        frame_weight=frame_weight,
    )
    aper_proxy_loss_per_sample = masked_mse_per_sample(
        prediction=outputs["aperiodicity"],
        target=teacher_proxy_target[..., 4:5],
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
    timing_pause_boundary_loss = reduce_weighted_sample_loss(timing_pause_boundary_loss_per_sample)
    timing_terminal_boundary_loss = reduce_weighted_sample_loss(timing_terminal_boundary_loss_per_sample)
    timing_final_clause_loss = reduce_weighted_sample_loss(timing_final_clause_loss_per_sample)
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
        + timing_pause_boundary_loss * effective_weights["teacher_timing_pause_boundary"]
        + timing_terminal_boundary_loss * effective_weights["teacher_timing_terminal_boundary"]
        + timing_final_clause_loss * effective_weights["teacher_timing_final_clause"]
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
        + timing_pause_boundary_loss * default_weights["teacher_timing_pause_boundary"]
        + timing_terminal_boundary_loss * default_weights["teacher_timing_terminal_boundary"]
        + timing_final_clause_loss * default_weights["teacher_timing_final_clause"]
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
        + timing_pause_boundary_loss * effective_weights["teacher_timing_pause_boundary"]
        + timing_terminal_boundary_loss * effective_weights["teacher_timing_terminal_boundary"]
        + timing_final_clause_loss * effective_weights["teacher_timing_final_clause"]
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
        "loss_teacher_timing_pause_boundary": round(float(timing_pause_boundary_loss.detach().cpu().item()), 6),
        "loss_teacher_timing_terminal_boundary": round(
            float(timing_terminal_boundary_loss.detach().cpu().item()),
            6,
        ),
        "loss_teacher_timing_final_clause": round(float(timing_final_clause_loss.detach().cpu().item()), 6),
        "loss_teacher_energy_proxy": round(float(energy_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_vuv_proxy": round(float(vuv_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_aper_proxy": round(float(aper_proxy_loss.detach().cpu().item()), 6),
        "loss_teacher_proxy_acoustic": round(float(proxy_acoustic_loss.detach().cpu().item()), 6),
        "loss_teacher_proxy_temporal": round(float(proxy_temporal_loss.detach().cpu().item()), 6),
        "loss_log_f0_correction_l1": round(float(log_f0_correction_l1.detach().cpu().item()), 6),
        "loss_aper_correction_l1": round(float(aper_correction_l1.detach().cpu().item()), 6),
        "teacher_confidence_weighted": bool(use_teacher_confidence),
        "effective_weight_sum": round(float(frame_weight.sum().detach().cpu().item()), 6),
        "teacher_event_target_family": str(event_target_bundle["event_target_family"]),
        "teacher_event_contract_version": str(event_target_bundle["event_contract_version"]),
        "teacher_event_label_space_version": str(event_target_bundle["event_label_space_version"]),
        "teacher_event_proxy_target_family": str(event_target_bundle["proxy_target_family"]),
        "teacher_event_proxy_contract_version": str(event_target_bundle["proxy_contract_version"]),
        "teacher_event_proxy_label_space_version": str(
            event_target_bundle["proxy_label_space_version"]
        ),
    }
    metrics.update(semantic_metrics)
    metrics.update(timing_frame_metrics)
    metrics.update(timing_aux_metrics)
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
    timing_sidecars = batch.get("target_event_timing_semantic_sidecar")
    if not isinstance(timing_sidecars, list):
        timing_sidecars = []
    record_ids = batch.get("record_ids")
    batch_size = len(record_ids) if isinstance(record_ids, list) else max(len(sidecars), len(timing_sidecars))
    if batch_size <= 0:
        unit = torch.ones((0, 1, 1), dtype=dtype, device=device)
        return {
            "teacher_z_art": unit,
            "teacher_event": unit,
            "teacher_event_prior": unit,
        }, {
            "semantic_supervision_enabled": bool(semantic_supervision.get("enabled", False)),
            "semantic_sidecar_present_ratio": 0.0,
            "timing_sidecar_present_ratio": 0.0,
            "semantic_weight_applied_ratio": 0.0,
            "semantic_clean_text_sample_ratio": 0.0,
            "semantic_nonverbal_sample_ratio": 0.0,
            "semantic_timing_ready_sample_ratio": 0.0,
            "semantic_timing_multi_clause_sample_ratio": 0.0,
            "semantic_timing_pause_present_sample_ratio": 0.0,
            "semantic_timing_terminal_present_sample_ratio": 0.0,
            "semantic_base_multiplier_mean": 1.0,
            "semantic_event_prior_multiplier_mean": 1.0,
            "semantic_event_multiplier_mean": 1.0,
            "semantic_z_art_multiplier_mean": 1.0,
        }

    base_multiplier = torch.ones((batch_size, 1, 1), dtype=dtype, device=device)
    present_count = 0
    timing_present_count = 0
    applied_count = 0
    clean_text_count = 0
    nonverbal_count = 0
    timing_ready_count = 0
    timing_multi_clause_count = 0
    timing_pause_present_count = 0
    timing_terminal_present_count = 0
    enabled = bool(semantic_supervision.get("enabled", False))
    required_contract_version = semantic_supervision.get("required_contract_version")
    required_contract_version = None if required_contract_version in {None, ""} else str(required_contract_version)
    required_timing_contract_version = semantic_supervision.get("required_timing_contract_version")
    required_timing_contract_version = (
        None
        if required_timing_contract_version in {None, ""}
        else str(required_timing_contract_version)
    )

    for index in range(batch_size):
        row = sidecars[index] if index < len(sidecars) else None
        timing_row = timing_sidecars[index] if index < len(timing_sidecars) else None
        semantic_row_valid = isinstance(row, dict)
        timing_row_valid = isinstance(timing_row, dict)
        if semantic_row_valid:
            present_count += 1
        if timing_row_valid:
            timing_present_count += 1
        if not semantic_row_valid:
            continue
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
        if timing_row_valid:
            if required_timing_contract_version is None or (
                str(timing_row.get("semantic_contract_version", "")) == required_timing_contract_version
            ):
                timing_alignment = (
                    dict(timing_row.get("timing_alignment", {}))
                    if isinstance(timing_row.get("timing_alignment"), dict)
                    else {}
                )
                timing_semantics = (
                    dict(timing_row.get("time_aware_semantics", {}))
                    if isinstance(timing_row.get("time_aware_semantics"), dict)
                    else {}
                )
                coverage_summary = (
                    dict(timing_semantics.get("coverage_summary", {}))
                    if isinstance(timing_semantics.get("coverage_summary"), dict)
                    else {}
                )
                alignment_type = str(timing_alignment.get("alignment_type", "unknown"))
                clause_region_count = int(coverage_summary.get("clause_region_count", 0))
                pause_boundary_event_count = int(coverage_summary.get("pause_boundary_event_count", 0))
                terminal_boundary_event_count = int(coverage_summary.get("terminal_boundary_event_count", 0))
                if alignment_type not in {"", "unknown"}:
                    multiplier += float(semantic_supervision["timing_ready_bonus"])
                    timing_ready_count += 1
                if clause_region_count >= 2:
                    multiplier += float(semantic_supervision["timing_multi_clause_bonus"])
                    timing_multi_clause_count += 1
                if pause_boundary_event_count >= 1:
                    multiplier += float(semantic_supervision["timing_pause_present_bonus"])
                    timing_pause_present_count += 1
                if terminal_boundary_event_count >= 1:
                    multiplier += float(semantic_supervision["timing_terminal_present_bonus"])
                    timing_terminal_present_count += 1
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
        "timing_sidecar_present_ratio": round(timing_present_count / max(1, batch_size), 6),
        "semantic_weight_applied_ratio": round(applied_count / max(1, batch_size), 6),
        "semantic_clean_text_sample_ratio": round(clean_text_count / max(1, batch_size), 6),
        "semantic_nonverbal_sample_ratio": round(nonverbal_count / max(1, batch_size), 6),
        "semantic_timing_ready_sample_ratio": round(timing_ready_count / max(1, batch_size), 6),
        "semantic_timing_multi_clause_sample_ratio": round(
            timing_multi_clause_count / max(1, batch_size),
            6,
        ),
        "semantic_timing_pause_present_sample_ratio": round(
            timing_pause_present_count / max(1, batch_size),
            6,
        ),
        "semantic_timing_terminal_present_sample_ratio": round(
            timing_terminal_present_count / max(1, batch_size),
            6,
        ),
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


def build_timing_frame_loss_multipliers(
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    semantic_supervision: Mapping[str, object],
    teacher_frame_mask: torch.Tensor,
    device: torch.device,
    dtype: torch.dtype,
) -> tuple[dict[str, torch.Tensor], dict[str, float | bool]]:
    batch_size, max_frames = teacher_frame_mask.shape
    unit = torch.ones((batch_size, max_frames, 1), dtype=dtype, device=device)
    sidecars = batch.get("target_event_timing_semantic_sidecar")
    if not isinstance(sidecars, list):
        sidecars = []
    enabled = bool(semantic_supervision.get("enabled", False))
    routing_enabled = bool(semantic_supervision.get("timing_frame_routing_enabled", False))
    required_timing_contract_version = semantic_supervision.get("required_timing_contract_version")
    required_timing_contract_version = (
        None
        if required_timing_contract_version in {None, ""}
        else str(required_timing_contract_version)
    )
    if batch_size <= 0:
        return {
            "teacher_z_art": unit,
            "teacher_event": unit,
            "teacher_event_prior": unit,
        }, {
            "timing_frame_routing_enabled": enabled and routing_enabled,
            "timing_frame_mask_applied_ratio": 0.0,
            "timing_boundary_frame_ratio": 0.0,
            "timing_terminal_boundary_frame_ratio": 0.0,
            "timing_final_clause_frame_ratio": 0.0,
            "timing_event_prior_frame_multiplier_mean": 1.0,
            "timing_event_frame_multiplier_mean": 1.0,
            "timing_z_art_frame_multiplier_mean": 1.0,
        }

    base_multiplier = torch.ones((batch_size, max_frames, 1), dtype=dtype, device=device)
    if not enabled or not routing_enabled:
        return {
            "teacher_z_art": unit,
            "teacher_event": unit,
            "teacher_event_prior": unit,
        }, {
            "timing_frame_routing_enabled": False,
            "timing_frame_mask_applied_ratio": 0.0,
            "timing_boundary_frame_ratio": 0.0,
            "timing_terminal_boundary_frame_ratio": 0.0,
            "timing_final_clause_frame_ratio": 0.0,
            "timing_event_prior_frame_multiplier_mean": 1.0,
            "timing_event_frame_multiplier_mean": 1.0,
            "timing_z_art_frame_multiplier_mean": 1.0,
        }

    nonboundary_scale = float(semantic_supervision["timing_nonboundary_scale"])
    pause_boundary_boost = float(semantic_supervision["timing_pause_boundary_boost"])
    terminal_boundary_boost = float(semantic_supervision["timing_terminal_boundary_boost"])
    final_clause_boost = float(semantic_supervision["timing_final_clause_boost"])
    event_prior_mask_alpha = float(semantic_supervision["timing_event_prior_mask_alpha"])
    event_mask_alpha = float(semantic_supervision["timing_event_mask_alpha"])
    z_art_mask_alpha = float(semantic_supervision["timing_z_art_mask_alpha"])

    applied_count = 0
    total_valid_frame_count = 0
    boundary_frame_count = 0
    terminal_boundary_frame_count = 0
    final_clause_frame_count = 0

    for index in range(batch_size):
        valid_frame_count = int(teacher_frame_mask[index].to(torch.long).sum().item())
        total_valid_frame_count += valid_frame_count
        if valid_frame_count <= 0:
            continue
        row = sidecars[index] if index < len(sidecars) else None
        if not isinstance(row, dict):
            continue
        if required_timing_contract_version is not None:
            if str(row.get("semantic_contract_version", "")) != required_timing_contract_version:
                continue
        time_aware_semantics = (
            dict(row.get("time_aware_semantics", {}))
            if isinstance(row.get("time_aware_semantics"), dict)
            else {}
        )
        boundary_events = (
            list(time_aware_semantics.get("boundary_events", []))
            if isinstance(time_aware_semantics.get("boundary_events"), list)
            else []
        )
        clause_regions = (
            list(time_aware_semantics.get("clause_regions", []))
            if isinstance(time_aware_semantics.get("clause_regions"), list)
            else []
        )
        if not boundary_events and not clause_regions:
            continue

        pause_boundary_mask = torch.zeros((valid_frame_count,), dtype=torch.bool, device=device)
        terminal_boundary_mask = torch.zeros((valid_frame_count,), dtype=torch.bool, device=device)
        final_clause_mask = torch.zeros((valid_frame_count,), dtype=torch.bool, device=device)

        for event in boundary_events:
            frame_start_index = max(0, min(valid_frame_count - 1, int(event.get("frame_start_index", 0))))
            frame_end_index = max(0, min(valid_frame_count - 1, int(event.get("frame_end_index", frame_start_index))))
            if frame_end_index < frame_start_index:
                continue
            event_type = str(event.get("event_type", "unknown"))
            if event_type == "pause_boundary_window":
                pause_boundary_mask[frame_start_index : frame_end_index + 1] = True
            elif event_type == "terminal_boundary_window":
                terminal_boundary_mask[frame_start_index : frame_end_index + 1] = True

        for region in clause_regions:
            clause_role = str(region.get("clause_role", "unknown"))
            if clause_role not in {"final", "single"}:
                continue
            frame_start_index = max(0, min(valid_frame_count - 1, int(region.get("frame_start_index", 0))))
            frame_end_index = max(0, min(valid_frame_count - 1, int(region.get("frame_end_index", frame_start_index))))
            if frame_end_index < frame_start_index:
                continue
            final_clause_mask[frame_start_index : frame_end_index + 1] = True

        sample_multiplier = torch.full((valid_frame_count, 1), nonboundary_scale, dtype=dtype, device=device)
        pause_boundary_mask_2d = pause_boundary_mask.unsqueeze(-1)
        terminal_boundary_mask_2d = terminal_boundary_mask.unsqueeze(-1)
        final_clause_nonboundary_mask_2d = (final_clause_mask & ~pause_boundary_mask & ~terminal_boundary_mask).unsqueeze(-1)
        sample_multiplier = torch.where(
            pause_boundary_mask_2d,
            sample_multiplier.new_full((valid_frame_count, 1), pause_boundary_boost),
            sample_multiplier,
        )
        sample_multiplier = torch.where(
            terminal_boundary_mask_2d,
            sample_multiplier.new_full((valid_frame_count, 1), terminal_boundary_boost),
            sample_multiplier,
        )
        sample_multiplier = torch.where(
            final_clause_nonboundary_mask_2d,
            sample_multiplier * final_clause_boost,
            sample_multiplier,
        )
        base_multiplier[index, :valid_frame_count] = sample_multiplier
        applied_count += 1
        boundary_frame_count += int((pause_boundary_mask | terminal_boundary_mask).to(torch.long).sum().item())
        terminal_boundary_frame_count += int(terminal_boundary_mask.to(torch.long).sum().item())
        final_clause_frame_count += int(final_clause_mask.to(torch.long).sum().item())

    valid_frame_mask = teacher_frame_mask.to(dtype=dtype).unsqueeze(-1)
    base_multiplier = torch.where(valid_frame_mask > 0.0, base_multiplier, torch.ones_like(base_multiplier))
    event_prior_multiplier = 1.0 + (base_multiplier - 1.0) * event_prior_mask_alpha
    event_multiplier = 1.0 + (base_multiplier - 1.0) * event_mask_alpha
    z_art_multiplier = 1.0 + (base_multiplier - 1.0) * z_art_mask_alpha
    metrics: dict[str, float | bool] = {
        "timing_frame_routing_enabled": True,
        "timing_frame_mask_applied_ratio": round(applied_count / max(1, batch_size), 6),
        "timing_boundary_frame_ratio": round(boundary_frame_count / max(1, total_valid_frame_count), 6),
        "timing_terminal_boundary_frame_ratio": round(
            terminal_boundary_frame_count / max(1, total_valid_frame_count),
            6,
        ),
        "timing_final_clause_frame_ratio": round(final_clause_frame_count / max(1, total_valid_frame_count), 6),
        "timing_event_prior_frame_multiplier_mean": round(
            float(masked_tensor_mean(event_prior_multiplier, valid_frame_mask).detach().cpu().item()),
            6,
        ),
        "timing_event_frame_multiplier_mean": round(
            float(masked_tensor_mean(event_multiplier, valid_frame_mask).detach().cpu().item()),
            6,
        ),
        "timing_z_art_frame_multiplier_mean": round(
            float(masked_tensor_mean(z_art_multiplier, valid_frame_mask).detach().cpu().item()),
            6,
        ),
    }
    return {
        "teacher_z_art": z_art_multiplier,
        "teacher_event": event_multiplier,
        "teacher_event_prior": event_prior_multiplier,
    }, metrics


def build_timing_auxiliary_targets(
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    teacher_frame_mask: torch.Tensor,
    device: torch.device,
    dtype: torch.dtype,
) -> tuple[dict[str, torch.Tensor], dict[str, float | bool]]:
    batch_size, max_frames = teacher_frame_mask.shape
    pause_boundary_target = torch.zeros((batch_size, max_frames, 1), dtype=dtype, device=device)
    terminal_boundary_target = torch.zeros((batch_size, max_frames, 1), dtype=dtype, device=device)
    final_clause_target = torch.zeros((batch_size, max_frames, 1), dtype=dtype, device=device)
    sidecars = batch.get("target_event_timing_semantic_sidecar")
    if not isinstance(sidecars, list):
        sidecars = []
    present_count = 0
    for index in range(batch_size):
        valid_frame_count = int(teacher_frame_mask[index].to(torch.long).sum().item())
        if valid_frame_count <= 0:
            continue
        row = sidecars[index] if index < len(sidecars) else None
        if not isinstance(row, dict):
            continue
        present_count += 1
        time_aware_semantics = (
            dict(row.get("time_aware_semantics", {}))
            if isinstance(row.get("time_aware_semantics"), dict)
            else {}
        )
        boundary_events = (
            list(time_aware_semantics.get("boundary_events", []))
            if isinstance(time_aware_semantics.get("boundary_events"), list)
            else []
        )
        clause_regions = (
            list(time_aware_semantics.get("clause_regions", []))
            if isinstance(time_aware_semantics.get("clause_regions"), list)
            else []
        )
        for event in boundary_events:
            frame_start_index = max(0, min(valid_frame_count - 1, int(event.get("frame_start_index", 0))))
            frame_end_index = max(0, min(valid_frame_count - 1, int(event.get("frame_end_index", frame_start_index))))
            if frame_end_index < frame_start_index:
                continue
            event_type = str(event.get("event_type", "unknown"))
            if event_type == "pause_boundary_window":
                pause_boundary_target[index, frame_start_index : frame_end_index + 1, 0] = 1.0
            elif event_type == "terminal_boundary_window":
                terminal_boundary_target[index, frame_start_index : frame_end_index + 1, 0] = 1.0
        for region in clause_regions:
            clause_role = str(region.get("clause_role", "unknown"))
            if clause_role not in {"final", "single"}:
                continue
            frame_start_index = max(0, min(valid_frame_count - 1, int(region.get("frame_start_index", 0))))
            frame_end_index = max(0, min(valid_frame_count - 1, int(region.get("frame_end_index", frame_start_index))))
            if frame_end_index < frame_start_index:
                continue
            final_clause_target[index, frame_start_index : frame_end_index + 1, 0] = 1.0

    valid_frame_mask = teacher_frame_mask.to(dtype=dtype).unsqueeze(-1)
    valid_frame_count = float(valid_frame_mask.sum().detach().cpu().item())
    metrics: dict[str, float | bool] = {
        "timing_aux_target_present_ratio": round(present_count / max(1, batch_size), 6),
        "timing_aux_pause_boundary_frame_ratio": round(
            float((pause_boundary_target * valid_frame_mask).sum().detach().cpu().item()) / max(1.0, valid_frame_count),
            6,
        ),
        "timing_aux_terminal_boundary_frame_ratio": round(
            float((terminal_boundary_target * valid_frame_mask).sum().detach().cpu().item()) / max(1.0, valid_frame_count),
            6,
        ),
        "timing_aux_final_clause_frame_ratio": round(
            float((final_clause_target * valid_frame_mask).sum().detach().cpu().item()) / max(1.0, valid_frame_count),
            6,
        ),
    }
    return {
        "pause_boundary": pause_boundary_target,
        "terminal_boundary": terminal_boundary_target,
        "final_clause": final_clause_target,
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


def masked_optional_bce_with_logits_per_sample(
    logits: torch.Tensor,
    target: torch.Tensor,
    frame_weight: torch.Tensor,
) -> torch.Tensor:
    if logits.shape[-1] <= 0:
        return frame_weight.new_zeros((frame_weight.shape[0],))
    return masked_bce_with_logits_per_sample(
        logits=logits,
        target=target,
        frame_weight=frame_weight,
    )


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


def masked_tensor_mean(
    tensor: torch.Tensor,
    mask: torch.Tensor,
) -> torch.Tensor:
    weighted = tensor * mask.to(device=tensor.device, dtype=tensor.dtype)
    denominator = mask.to(device=tensor.device, dtype=tensor.dtype).sum().clamp_min(1.0)
    return weighted.sum() / denominator
