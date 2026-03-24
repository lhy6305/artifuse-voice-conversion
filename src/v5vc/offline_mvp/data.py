from __future__ import annotations

import json
import random
import wave
from dataclasses import dataclass
from pathlib import Path

import torch


TEXT_FEATURE_VERSION_LEGACY_V0 = "legacy_v0"
TEXT_FEATURE_VERSION_B1_PUNCT_V1 = "b1_punct_v1"
TEXT_FEATURE_VERSION_B1_1_STATS_V2 = "b1_1_stats_v2"

PAUSE_PUNCTUATION = "，、；："
TERMINAL_PUNCTUATION = "。？！"
ALL_PUNCTUATION = PAUSE_PUNCTUATION + TERMINAL_PUNCTUATION


@dataclass
class TargetExample:
    record_id: str
    audio_path: Path
    sample_rate: int
    waveform: torch.Tensor
    text: str
    token_ids: torch.Tensor
    text_features: torch.Tensor
    weak_event_hints: dict[str, object] | None
    target_special_supervision: dict[str, object] | None
    target_event_semantic_sidecar: dict[str, object] | None


@dataclass
class SourceExample:
    record_id: str
    audio_path: Path
    sample_rate: int
    waveform: torch.Tensor


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_target_weak_event_hint_map(path: Path) -> dict[str, dict[str, object]]:
    hint_rows = load_jsonl(path)
    return {
        str(row["record_id"]): row
        for row in hint_rows
    }


def load_target_special_supervision_map(path: Path) -> dict[str, dict[str, object]]:
    supervision_rows = load_jsonl(path)
    return {
        str(row["record_id"]): row
        for row in supervision_rows
    }


def load_target_event_semantic_sidecar_map(path: Path) -> dict[str, dict[str, object]]:
    semantic_rows = load_jsonl(path)
    return {
        str(row["record_id"]): row
        for row in semantic_rows
    }


def attach_target_weak_event_hints(
    records: list[dict[str, object]],
    hint_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    attached_records: list[dict[str, object]] = []
    for record in records:
        updated = dict(record)
        record_id = str(record["record_id"])
        updated["weak_event_hints"] = hint_map.get(record_id)
        attached_records.append(updated)
    return attached_records


def attach_target_special_supervision(
    records: list[dict[str, object]],
    supervision_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    attached_records: list[dict[str, object]] = []
    for record in records:
        updated = dict(record)
        record_id = str(record["record_id"])
        updated["target_special_supervision"] = supervision_map.get(record_id)
        attached_records.append(updated)
    return attached_records


def attach_target_event_semantic_sidecar(
    records: list[dict[str, object]],
    semantic_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    attached_records: list[dict[str, object]] = []
    for record in records:
        updated = dict(record)
        record_id = str(record["record_id"])
        updated["target_event_semantic_sidecar"] = semantic_map.get(record_id)
        attached_records.append(updated)
    return attached_records


def infer_target_event_semantic_sidecar_path(split_dir: Path | None) -> Path | None:
    if split_dir is None:
        return None
    split_dir = split_dir.resolve()
    if split_dir.parent == split_dir:
        return None
    round_dir = split_dir.parent.parent
    candidate = round_dir / "target_event_semantic_sidecar" / "target_event_semantic_sidecar.jsonl"
    if candidate.exists():
        return candidate.resolve()
    return None


def build_record_semantic_overview(record: dict[str, object]) -> dict[str, object]:
    semantic_sidecar = record.get("target_event_semantic_sidecar")
    weak_event_hints = record.get("weak_event_hints")
    target_special_supervision = record.get("target_special_supervision")

    if isinstance(semantic_sidecar, dict):
        utterance_semantics = (
            dict(semantic_sidecar.get("utterance_structure_semantics", {}))
            if isinstance(semantic_sidecar.get("utterance_structure_semantics"), dict)
            else {}
        )
        boundary_semantics = (
            dict(semantic_sidecar.get("boundary_semantics", {}))
            if isinstance(semantic_sidecar.get("boundary_semantics"), dict)
            else {}
        )
        text_semantics = (
            dict(semantic_sidecar.get("text_semantics", {}))
            if isinstance(semantic_sidecar.get("text_semantics"), dict)
            else {}
        )
        upgrade_status = (
            dict(semantic_sidecar.get("upgrade_status", {}))
            if isinstance(semantic_sidecar.get("upgrade_status"), dict)
            else {}
        )
        semantic_scope = (
            dict(semantic_sidecar.get("semantic_scope", {}))
            if isinstance(semantic_sidecar.get("semantic_scope"), dict)
            else {}
        )
        return {
            "semantic_source": "target_event_semantic_sidecar",
            "semantic_contract_version": str(semantic_sidecar.get("semantic_contract_version", "")) or None,
            "semantic_label_space_version": str(semantic_sidecar.get("semantic_label_space_version", "")) or None,
            "semantic_inventory_status": str(semantic_sidecar.get("inventory_status", "unknown")),
            "semantic_label_status": str(upgrade_status.get("label_status", "unknown")),
            "semantic_utterance_structure_type": str(
                utterance_semantics.get("utterance_structure_type", "unknown")
            ),
            "semantic_final_terminal_type": str(
                utterance_semantics.get("final_terminal_type", "unknown")
            ),
            "semantic_clause_count": int(utterance_semantics.get("clause_count", 0)),
            "semantic_pause_boundary_count": int(boundary_semantics.get("pause_boundary_count", 0)),
            "semantic_terminal_boundary_count": int(boundary_semantics.get("terminal_boundary_count", 0)),
            "semantic_nonverbal_only": bool(text_semantics.get("nonverbal_only", False)),
            "semantic_clean_text_available": bool(semantic_scope.get("clean_text_available", False)),
            "semantic_phone_sequence_available": bool(semantic_scope.get("phone_sequence_available", False)),
            "semantic_manner_sequence_available": bool(semantic_scope.get("manner_sequence_available", False)),
            "semantic_place_sequence_available": bool(semantic_scope.get("place_sequence_available", False)),
            "semantic_forced_alignment_available": bool(semantic_scope.get("forced_alignment_available", False)),
        }

    if not isinstance(weak_event_hints, dict):
        weak_event_hints = {}
    if not isinstance(target_special_supervision, dict):
        target_special_supervision = {}
    return {
        "semantic_source": "weak_event_hints_fallback" if weak_event_hints else "missing",
        "semantic_contract_version": None,
        "semantic_label_space_version": None,
        "semantic_inventory_status": "missing",
        "semantic_label_status": "missing",
        "semantic_utterance_structure_type": str(weak_event_hints.get("utterance_structure_type", "unknown")),
        "semantic_final_terminal_type": str(
            weak_event_hints.get(
                "final_terminal_type",
                target_special_supervision.get("final_terminal_type", "unknown"),
            )
        ),
        "semantic_clause_count": int(weak_event_hints.get("clause_count", 0)),
        "semantic_pause_boundary_count": int(weak_event_hints.get("pause_boundary_count", 0)),
        "semantic_terminal_boundary_count": int(weak_event_hints.get("terminal_boundary_count", 0)),
        "semantic_nonverbal_only": bool(weak_event_hints.get("nonverbal_only", False)),
        "semantic_clean_text_available": False,
        "semantic_phone_sequence_available": False,
        "semantic_manner_sequence_available": False,
        "semantic_place_sequence_available": False,
        "semantic_forced_alignment_available": False,
    }


def build_char_vocab(target_records: list[dict[str, object]]) -> dict[str, int]:
    vocab = {
        "<pad>": 0,
        "<bos>": 1,
        "<eos>": 2,
        "<unk>": 3,
    }
    for record in target_records:
        text = str(record["text"]["clean"])
        for char in text:
            if char not in vocab:
                vocab[char] = len(vocab)
    return vocab


def split_records(
    records: list[dict[str, object]],
    validation_count: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if validation_count <= 0 or len(records) <= 1:
        return records, []
    effective_validation_count = min(validation_count, len(records) - 1)
    return records[:-effective_validation_count], records[-effective_validation_count:]


def select_batch_records(
    records: list[dict[str, object]],
    batch_size: int,
    batch_index: int,
) -> list[dict[str, object]]:
    if not records:
        return []
    effective_batch_size = min(batch_size, len(records))
    start_index = (batch_index * effective_batch_size) % len(records)
    return [
        records[(start_index + offset) % len(records)]
        for offset in range(effective_batch_size)
    ]


def build_training_batch_plan(
    records: list[dict[str, object]],
    batch_size: int,
    num_steps: int,
    shuffle: bool,
    seed: int,
    sampling_config: dict[str, object] | None = None,
) -> list[list[dict[str, object]]]:
    if num_steps <= 0:
        return []
    if not records:
        return [[] for _ in range(num_steps)]

    effective_batch_size = min(batch_size, len(records))
    if not shuffle:
        return [
            select_batch_records(records, batch_size=effective_batch_size, batch_index=batch_index)
            for batch_index in range(num_steps)
        ]

    if isinstance(sampling_config, dict) and bool(sampling_config.get("enabled", False)):
        mode = str(sampling_config.get("mode", "priority_interleave"))
        if mode != "priority_interleave":
            raise ValueError(f"Unsupported targeted sampling mode: {mode}")
        return build_priority_interleave_batch_plan(
            records=records,
            batch_size=effective_batch_size,
            num_steps=num_steps,
            seed=seed,
            sampling_config=sampling_config,
        )

    rng = random.Random(seed)
    pending_records: list[dict[str, object]] = []
    batch_plan: list[list[dict[str, object]]] = []

    while len(batch_plan) < num_steps:
        if len(pending_records) < effective_batch_size:
            epoch_records = list(records)
            rng.shuffle(epoch_records)
            pending_records.extend(epoch_records)
        batch_plan.append(pending_records[:effective_batch_size])
        del pending_records[:effective_batch_size]

    return batch_plan


def build_priority_interleave_batch_plan(
    records: list[dict[str, object]],
    batch_size: int,
    num_steps: int,
    seed: int,
    sampling_config: dict[str, object],
) -> list[list[dict[str, object]]]:
    rng = random.Random(seed)
    forced_pending_by_pool: dict[str, list[dict[str, object]]] = {}
    priority_pending_by_pool: dict[str, list[dict[str, object]]] = {}
    secondary_pending_by_pool: dict[str, list[dict[str, object]]] = {}
    priority_union_pending_by_pool: dict[str, list[dict[str, object]]] = {}
    background_pending_by_pool: dict[str, list[dict[str, object]]] = {}
    full_pending: list[dict[str, object]] = []
    batch_plan: list[list[dict[str, object]]] = []

    for step_index in range(num_steps):
        step_sampling_config = resolve_priority_sampling_config_for_step(
            step_index=step_index,
            num_steps=num_steps,
            sampling_config=sampling_config,
        )
        if step_sampling_config is None:
            batch_plan.append(
                draw_records_from_pool(
                    pool_records=records,
                    pending_records=full_pending,
                    batch_size=batch_size,
                    rng=rng,
                )
            )
            continue
        current_priority_slots = compute_priority_slots(
            batch_size=batch_size,
            priority_ratio=float(step_sampling_config.get("priority_ratio", 0.0)),
        )
        if current_priority_slots <= 0:
            batch_plan.append(
                draw_records_from_pool(
                    pool_records=records,
                    pending_records=full_pending,
                    batch_size=batch_size,
                    rng=rng,
                )
            )
            continue
        priority_groups = build_priority_record_groups(records=records, sampling_config=step_sampling_config)
        forced_records = priority_groups["forced_records"]
        priority_records = priority_groups["primary_records"]
        secondary_records = priority_groups["secondary_records"]
        priority_union_records = priority_groups["priority_union_records"]
        background_records = priority_groups["background_records"]
        if not priority_union_records:
            batch_plan.append(
                draw_records_from_pool(
                    pool_records=records,
                    pending_records=full_pending,
                    batch_size=batch_size,
                    rng=rng,
                )
            )
            continue
        pool_key = build_priority_pool_key(step_sampling_config)
        forced_pending = forced_pending_by_pool.setdefault(f"forced::{pool_key}", [])
        priority_pending = priority_pending_by_pool.setdefault(pool_key, [])
        secondary_pending = secondary_pending_by_pool.setdefault(f"secondary::{pool_key}", [])
        priority_union_pending = priority_union_pending_by_pool.setdefault(f"union::{pool_key}", [])
        background_pending = background_pending_by_pool.setdefault(pool_key, [])
        batch_records: list[dict[str, object]] = []
        if forced_records:
            batch_records.extend(
                draw_records_from_pool(
                    pool_records=forced_records,
                    pending_records=forced_pending,
                    batch_size=current_priority_slots,
                    rng=rng,
                )
            )
        remaining_priority_slots = current_priority_slots - len(batch_records)
        secondary_sampling_config = resolve_secondary_priority_sampling_config(step_sampling_config)
        if remaining_priority_slots > 0 and secondary_sampling_config is not None and secondary_records:
            secondary_max_slots = int(secondary_sampling_config.get("max_slots", current_priority_slots))
            secondary_max_slots = max(0, min(remaining_priority_slots, secondary_max_slots))
            if secondary_max_slots > 0:
                batch_records.extend(
                    draw_records_from_pool(
                        pool_records=secondary_records,
                        pending_records=secondary_pending,
                        batch_size=secondary_max_slots,
                        rng=rng,
                    )
                )
        remaining_priority_slots = current_priority_slots - len(batch_records)
        if remaining_priority_slots > 0 and priority_records:
            batch_records.extend(
                draw_records_from_pool(
                    pool_records=priority_records,
                    pending_records=priority_pending,
                    batch_size=remaining_priority_slots,
                    rng=rng,
                    excluded_record_ids={str(record["record_id"]) for record in batch_records},
                )
            )
        if len(batch_records) < current_priority_slots:
            batch_records.extend(
                draw_records_from_pool(
                    pool_records=priority_union_records,
                    pending_records=priority_union_pending,
                    batch_size=current_priority_slots - len(batch_records),
                    rng=rng,
                    excluded_record_ids={str(record["record_id"]) for record in batch_records},
                )
            )
        remaining_slots = batch_size - len(batch_records)
        if remaining_slots > 0:
            background_pool = background_records if background_records else records
            background_batch = draw_records_from_pool(
                pool_records=background_pool,
                pending_records=background_pending,
                batch_size=remaining_slots,
                rng=rng,
                excluded_record_ids={str(record["record_id"]) for record in batch_records},
            )
            batch_records.extend(background_batch)
        if len(batch_records) < batch_size:
            batch_records.extend(
                draw_records_from_pool(
                    pool_records=records,
                    pending_records=full_pending,
                    batch_size=batch_size - len(batch_records),
                    rng=rng,
                    excluded_record_ids={str(record["record_id"]) for record in batch_records},
                )
            )
        batch_plan.append(batch_records[:batch_size])

    return batch_plan


def resolve_priority_sampling_config_for_step(
    step_index: int,
    num_steps: int,
    sampling_config: dict[str, object],
    ) -> dict[str, object] | None:
    schedule_phases = list(sampling_config.get("schedule_phases", []))
    if schedule_phases:
        for phase in schedule_phases:
            if not isinstance(phase, dict):
                continue
            active_until_step = int(phase.get("active_until_step", 0))
            active_until_step = max(0, min(num_steps, active_until_step))
            if step_index >= active_until_step:
                continue
            merged = dict(sampling_config)
            merged.pop("schedule_phases", None)
            for key, value in phase.items():
                if key == "active_until_step":
                    continue
                merged[key] = value
            return merged
        return None
    active_until_step = int(sampling_config.get("active_until_step", num_steps))
    active_until_step = max(0, min(num_steps, active_until_step))
    if step_index >= active_until_step:
        return None
    return dict(sampling_config)


def compute_priority_slots(batch_size: int, priority_ratio: float) -> int:
    priority_ratio = max(0.0, min(1.0, priority_ratio))
    priority_slots = int(round(batch_size * priority_ratio))
    if priority_ratio > 0.0:
        priority_slots = max(1, priority_slots)
    return min(batch_size, priority_slots)


def build_priority_pool_key(sampling_config: dict[str, object]) -> str:
    return json.dumps(
        {
            "min_clause_count": int(sampling_config.get("min_clause_count", 0)),
            "min_pause_boundary_count": int(sampling_config.get("min_pause_boundary_count", 0)),
            "min_terminal_boundary_count": int(sampling_config.get("min_terminal_boundary_count", 0)),
            "required_within_special_duration_ceiling": sampling_config.get(
                "required_within_special_duration_ceiling"
            ),
            "min_special_proximity_score": float(sampling_config.get("min_special_proximity_score", 0.0)),
            "max_special_proximity_score": float(sampling_config.get("max_special_proximity_score", 1.0)),
            "required_final_terminal_types": list(sampling_config.get("required_final_terminal_types", [])),
            "required_utterance_structure_types": list(
                sampling_config.get("required_utterance_structure_types", [])
            ),
            "priority_structure_types": list(sampling_config.get("priority_structure_types", [])),
            "exclude_structure_types": list(sampling_config.get("exclude_structure_types", [])),
            "priority_pool_memberships": list(sampling_config.get("priority_pool_memberships", [])),
            "priority_record_ids": list(sampling_config.get("priority_record_ids", [])),
            "exclude_pool_memberships": list(sampling_config.get("exclude_pool_memberships", [])),
            "secondary_sampling": normalize_secondary_sampling_summary(
                resolve_secondary_priority_sampling_config(sampling_config)
            ),
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def build_priority_record_groups(
    records: list[dict[str, object]],
    sampling_config: dict[str, object],
) -> dict[str, list[dict[str, object]]]:
    forced_record_ids = {
        str(value)
        for value in list(sampling_config.get("priority_record_ids", []))
        if str(value)
    }
    forced_records = [
        record
        for record in records
        if str(record["record_id"]) in forced_record_ids
    ]
    forced_ids = {str(record["record_id"]) for record in forced_records}
    primary_records = [
        record
        for record in records
        if is_priority_target_record(record=record, sampling_config=sampling_config)
        and str(record["record_id"]) not in forced_ids
    ]
    primary_ids = {str(record["record_id"]) for record in primary_records}
    secondary_records: list[dict[str, object]] = []
    secondary_sampling_config = resolve_secondary_priority_sampling_config(sampling_config)
    if secondary_sampling_config is not None:
        secondary_records = [
            record
            for record in records
            if is_priority_target_record(record=record, sampling_config=secondary_sampling_config)
        ]
        if bool(secondary_sampling_config.get("exclude_primary_matches", False)):
            secondary_records = [
                record
                for record in secondary_records
                if str(record["record_id"]) not in (primary_ids | forced_ids)
            ]
    secondary_ids = {str(record["record_id"]) for record in secondary_records}
    priority_ids = forced_ids | primary_ids | secondary_ids
    background_records = [
        record
        for record in records
        if str(record["record_id"]) not in priority_ids
    ]
    priority_union_records = forced_records + primary_records + [
        record
        for record in secondary_records
        if str(record["record_id"]) not in (forced_ids | primary_ids)
    ]
    return {
        "forced_records": forced_records,
        "primary_records": primary_records,
        "secondary_records": secondary_records,
        "priority_union_records": priority_union_records,
        "background_records": background_records,
    }


def resolve_secondary_priority_sampling_config(
    sampling_config: dict[str, object],
) -> dict[str, object] | None:
    raw = sampling_config.get("secondary_sampling")
    if not isinstance(raw, dict) or not bool(raw.get("enabled", False)):
        return None
    return raw


def normalize_secondary_sampling_summary(
    sampling_config: dict[str, object] | None,
) -> dict[str, object] | None:
    if sampling_config is None:
        return None
    summary: dict[str, object] = {
        "enabled": True,
        "max_slots": int(sampling_config.get("max_slots", 0)),
        "priority_structure_types": list(sampling_config.get("priority_structure_types", [])),
        "exclude_structure_types": list(sampling_config.get("exclude_structure_types", [])),
        "priority_pool_memberships": list(sampling_config.get("priority_pool_memberships", [])),
        "priority_record_ids": list(sampling_config.get("priority_record_ids", [])),
        "exclude_pool_memberships": list(sampling_config.get("exclude_pool_memberships", [])),
        "exclude_primary_matches": bool(sampling_config.get("exclude_primary_matches", False)),
        "min_special_proximity_score": float(sampling_config.get("min_special_proximity_score", 0.0)),
        "max_special_proximity_score": float(sampling_config.get("max_special_proximity_score", 1.0)),
        "required_final_terminal_types": list(sampling_config.get("required_final_terminal_types", [])),
        "required_utterance_structure_types": list(
            sampling_config.get("required_utterance_structure_types", [])
        ),
    }
    if "min_clause_count" in sampling_config:
        summary["min_clause_count"] = int(sampling_config.get("min_clause_count", 0))
    if "min_pause_boundary_count" in sampling_config:
        summary["min_pause_boundary_count"] = int(sampling_config.get("min_pause_boundary_count", 0))
    if "min_terminal_boundary_count" in sampling_config:
        summary["min_terminal_boundary_count"] = int(sampling_config.get("min_terminal_boundary_count", 0))
    if "required_within_special_duration_ceiling" in sampling_config:
        summary["required_within_special_duration_ceiling"] = bool(
            sampling_config.get("required_within_special_duration_ceiling", False)
        )
    return summary


def draw_records_from_pool(
    pool_records: list[dict[str, object]],
    pending_records: list[dict[str, object]],
    batch_size: int,
    rng: random.Random,
    excluded_record_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    if batch_size <= 0 or not pool_records:
        return []
    excluded_record_ids = excluded_record_ids or set()
    selected: list[dict[str, object]] = []
    max_cycles = max(2, len(pool_records) * 2)
    cycles = 0

    while len(selected) < batch_size and cycles < max_cycles:
        if not pending_records:
            epoch_records = list(pool_records)
            rng.shuffle(epoch_records)
            pending_records.extend(epoch_records)
        record = pending_records.pop(0)
        record_id = str(record["record_id"])
        if record_id in excluded_record_ids:
            cycles += 1
            continue
        selected.append(record)
        excluded_record_ids.add(record_id)
        cycles += 1

    if len(selected) >= batch_size:
        return selected

    for record in pool_records:
        record_id = str(record["record_id"])
        if record_id in excluded_record_ids:
            continue
        selected.append(record)
        excluded_record_ids.add(record_id)
        if len(selected) >= batch_size:
            break
    return selected


def is_priority_target_record(
    record: dict[str, object],
    sampling_config: dict[str, object],
) -> bool:
    record_id = str(record["record_id"])
    semantic_overview = build_record_semantic_overview(record)
    target_special_supervision = record.get("target_special_supervision")
    pool_memberships: dict[str, bool] = {}
    special_proximity_score = 0.0
    final_terminal_type = str(semantic_overview["semantic_final_terminal_type"])
    if isinstance(target_special_supervision, dict):
        raw_pool_memberships = target_special_supervision.get("pool_memberships")
        if isinstance(raw_pool_memberships, dict):
            pool_memberships = {
                str(key): bool(value)
                for key, value in raw_pool_memberships.items()
            }
        special_proximity_score = float(target_special_supervision.get("special_proximity_score", 0.0))
        if final_terminal_type in {"", "unknown"}:
            final_terminal_type = str(target_special_supervision.get("final_terminal_type", "none"))
        if "within_special_duration_ceiling" in target_special_supervision:
            within_special_duration_ceiling = bool(
                target_special_supervision.get("within_special_duration_ceiling", False)
            )
        else:
            within_special_duration_ceiling = None
    else:
        within_special_duration_ceiling = None

    clause_count = int(semantic_overview["semantic_clause_count"])
    pause_boundary_count = int(semantic_overview["semantic_pause_boundary_count"])
    terminal_boundary_count = int(semantic_overview["semantic_terminal_boundary_count"])
    utterance_structure_type = str(semantic_overview["semantic_utterance_structure_type"])
    excluded_pool_memberships = {
        str(value)
        for value in list(sampling_config.get("exclude_pool_memberships", []))
    }
    if any(pool_memberships.get(pool_name, False) for pool_name in excluded_pool_memberships):
        return False
    required_within_special_duration_ceiling = sampling_config.get("required_within_special_duration_ceiling")
    if isinstance(required_within_special_duration_ceiling, bool):
        if within_special_duration_ceiling is None:
            return False
        if within_special_duration_ceiling != required_within_special_duration_ceiling:
            return False
    min_special_proximity_score = float(sampling_config.get("min_special_proximity_score", 0.0))
    max_special_proximity_score = float(sampling_config.get("max_special_proximity_score", 1.0))
    if special_proximity_score < min_special_proximity_score:
        return False
    if special_proximity_score > max_special_proximity_score:
        return False
    required_final_terminal_types = {
        str(value)
        for value in list(sampling_config.get("required_final_terminal_types", []))
        if str(value)
    }
    if required_final_terminal_types and final_terminal_type not in required_final_terminal_types:
        return False
    required_utterance_structure_types = {
        str(value)
        for value in list(sampling_config.get("required_utterance_structure_types", []))
        if str(value)
    }
    if required_utterance_structure_types and utterance_structure_type not in required_utterance_structure_types:
        return False
    priority_pool_memberships = {
        str(value)
        for value in list(sampling_config.get("priority_pool_memberships", []))
    }
    priority_record_ids = {
        str(value)
        for value in list(sampling_config.get("priority_record_ids", []))
        if str(value)
    }
    if record_id in priority_record_ids:
        return True
    if any(pool_memberships.get(pool_name, False) for pool_name in priority_pool_memberships):
        return True
    excluded_structure_types = {
        str(value)
        for value in list(sampling_config.get("exclude_structure_types", []))
    }
    if utterance_structure_type in excluded_structure_types:
        return False
    structure_types = {
        str(value)
        for value in list(sampling_config.get("priority_structure_types", []))
    }

    if clause_count >= int(sampling_config.get("min_clause_count", 9999)):
        return True
    if pause_boundary_count >= int(sampling_config.get("min_pause_boundary_count", 9999)):
        return True
    if terminal_boundary_count >= int(sampling_config.get("min_terminal_boundary_count", 9999)):
        return True
    if utterance_structure_type in structure_types:
        return True
    return False


def encode_text(text: str, vocab: dict[str, int]) -> torch.Tensor:
    ids = [vocab["<bos>"]]
    ids.extend(vocab.get(char, vocab["<unk>"]) for char in text)
    ids.append(vocab["<eos>"])
    return torch.tensor(ids, dtype=torch.long)


def build_text_statistics(text: str) -> dict[str, float]:
    lexical_char_count = sum(1 for char in text if char not in ALL_PUNCTUATION)
    pause_count = sum(1 for char in text if char in PAUSE_PUNCTUATION)
    terminal_count = sum(1 for char in text if char in TERMINAL_PUNCTUATION)
    question_count = sum(1 for char in text if char == "？")
    exclamation_count = sum(1 for char in text if char == "！")

    clause_lengths: list[int] = []
    current_clause_length = 0
    for char in text:
        if char in ALL_PUNCTUATION:
            if current_clause_length > 0:
                clause_lengths.append(current_clause_length)
                current_clause_length = 0
            continue
        current_clause_length += 1
    if current_clause_length > 0:
        clause_lengths.append(current_clause_length)

    if not clause_lengths and lexical_char_count > 0:
        clause_lengths.append(lexical_char_count)

    clause_count = len(clause_lengths)
    avg_clause_chars = (sum(clause_lengths) / clause_count) if clause_count > 0 else 0.0

    return {
        "lexical_char_count": float(lexical_char_count),
        "pause_count": float(pause_count),
        "terminal_count": float(terminal_count),
        "question_count": float(question_count),
        "exclamation_count": float(exclamation_count),
        "clause_count": float(clause_count),
        "avg_clause_chars": float(avg_clause_chars),
    }


def build_text_features(
    text: str,
    token_ids: torch.Tensor,
    duration_sec: float,
    feature_version: str,
) -> torch.Tensor:
    if feature_version == TEXT_FEATURE_VERSION_LEGACY_V0:
        char_count = max(1, len(text))
        punctuation_count = sum(1 for char in text if char in "，。？！；：、")
        comma_like_count = sum(1 for char in text if char in "，、；：")
        return torch.tensor(
            [
                min(token_ids.numel() / 128.0, 1.0),
                punctuation_count / char_count,
                comma_like_count / char_count,
            ],
            dtype=torch.float32,
        )
    if feature_version == TEXT_FEATURE_VERSION_B1_PUNCT_V1:
        stats = build_text_statistics(text)
        lexical_char_count = stats["lexical_char_count"]
        pause_count = stats["pause_count"]
        terminal_count = stats["terminal_count"]
        question_count = stats["question_count"]
        exclamation_count = stats["exclamation_count"]
        punctuation_total = pause_count + terminal_count
        duration = max(duration_sec, 1e-6)
        return torch.tensor(
            [
                min(token_ids.numel() / 128.0, 1.0),
                min(lexical_char_count / duration / 8.0, 1.0),
                min(pause_count / duration / 2.0, 1.0),
                min(terminal_count / duration / 1.0, 1.0),
                0.0 if punctuation_total == 0 else question_count / punctuation_total,
                0.0 if punctuation_total == 0 else exclamation_count / punctuation_total,
                1.0 if lexical_char_count == 0 else 0.0,
            ],
            dtype=torch.float32,
        )
    if feature_version == TEXT_FEATURE_VERSION_B1_1_STATS_V2:
        stats = build_text_statistics(text)
        lexical_char_count = stats["lexical_char_count"]
        pause_count = stats["pause_count"]
        terminal_count = stats["terminal_count"]
        question_count = stats["question_count"]
        exclamation_count = stats["exclamation_count"]
        clause_count = stats["clause_count"]
        avg_clause_chars = stats["avg_clause_chars"]
        duration = max(duration_sec, 1e-6)
        terminal_total = max(1.0, terminal_count)
        return torch.tensor(
            [
                min(token_ids.numel() / 128.0, 1.0),
                min(lexical_char_count / duration / 8.0, 1.0),
                min(pause_count / duration / 2.0, 1.0),
                min(terminal_count / duration / 1.0, 1.0),
                question_count / terminal_total,
                exclamation_count / terminal_total,
                1.0 if lexical_char_count == 0 else 0.0,
                min(clause_count / 6.0, 1.0),
                min(avg_clause_chars / 20.0, 1.0),
                1.0 if 0 < lexical_char_count <= 6 else 0.0,
                1.0 if lexical_char_count >= 30 else 0.0,
                1.0 if pause_count >= 2 else 0.0,
                1.0 if terminal_count >= 2 else 0.0,
            ],
            dtype=torch.float32,
        )
    raise ValueError(f"Unsupported text feature version: {feature_version}")


def load_waveform(
    path: Path,
    max_duration_sec: float | None = None,
) -> tuple[torch.Tensor, int]:
    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()
        if max_duration_sec is not None:
            frame_count = min(frame_count, int(sample_rate * max_duration_sec))
        raw = wav_file.readframes(frame_count)

    if sample_width != 2:
        raise ValueError(f"Unsupported sample width in {path}: {sample_width}")

    waveform = torch.frombuffer(bytearray(raw), dtype=torch.int16).to(torch.float32)
    if channels > 1:
        waveform = waveform.view(-1, channels).mean(dim=1)
    waveform = waveform / 32768.0
    return waveform.clone(), sample_rate


def load_target_examples(
    manifest_path: Path,
    batch_size: int,
    max_duration_sec: float | None,
    text_feature_version: str = TEXT_FEATURE_VERSION_LEGACY_V0,
) -> tuple[list[TargetExample], dict[str, int]]:
    records = load_jsonl(manifest_path)
    vocab = build_char_vocab(records)
    selected = select_batch_records(records, batch_size=batch_size, batch_index=0)
    return load_target_examples_from_records(
        selected,
        vocab=vocab,
        max_duration_sec=max_duration_sec,
        text_feature_version=text_feature_version,
    ), vocab


def load_target_examples_from_records(
    records: list[dict[str, object]],
    vocab: dict[str, int],
    max_duration_sec: float | None,
    text_feature_version: str = TEXT_FEATURE_VERSION_LEGACY_V0,
) -> list[TargetExample]:
    examples: list[TargetExample] = []
    for record in records:
        audio_path = Path(record["audio_path"])
        waveform, sample_rate = load_waveform(audio_path, max_duration_sec=max_duration_sec)
        text = str(record["text"]["clean"])
        token_ids = encode_text(text, vocab)
        text_features = build_text_features(
            text=text,
            token_ids=token_ids,
            duration_sec=float(record["audio"]["duration_sec"]),
            feature_version=text_feature_version,
        )
        examples.append(
            TargetExample(
                record_id=str(record["record_id"]),
                audio_path=audio_path,
                sample_rate=sample_rate,
                waveform=waveform,
                text=text,
                token_ids=token_ids,
                text_features=text_features,
                weak_event_hints=record.get("weak_event_hints"),
                target_special_supervision=record.get("target_special_supervision"),
                target_event_semantic_sidecar=record.get("target_event_semantic_sidecar"),
            )
        )
    return examples


def load_source_examples(
    manifest_path: Path,
    batch_size: int,
    max_duration_sec: float | None,
) -> list[SourceExample]:
    records = load_jsonl(manifest_path)
    selected = select_batch_records(records, batch_size=batch_size, batch_index=0)
    return load_source_examples_from_records(selected, max_duration_sec=max_duration_sec)


def load_source_examples_from_records(
    records: list[dict[str, object]],
    max_duration_sec: float | None,
) -> list[SourceExample]:
    examples: list[SourceExample] = []
    for record in records:
        audio_path = Path(record["audio_path"])
        waveform, sample_rate = load_waveform(audio_path, max_duration_sec=max_duration_sec)
        examples.append(
            SourceExample(
                record_id=str(record["record_id"]),
                audio_path=audio_path,
                sample_rate=sample_rate,
                waveform=waveform,
            )
        )
    return examples


def collate_source_batch(examples: list[SourceExample]) -> dict[str, torch.Tensor | list[str]]:
    lengths = torch.tensor([example.waveform.numel() for example in examples], dtype=torch.long)
    max_length = int(lengths.max().item()) if examples else 0
    batch = torch.zeros((len(examples), max_length), dtype=torch.float32)
    for index, example in enumerate(examples):
        batch[index, : example.waveform.numel()] = example.waveform
    return {
        "record_ids": [example.record_id for example in examples],
        "waveform": batch,
        "lengths": lengths,
    }


def collate_target_batch(
    examples: list[TargetExample],
) -> dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]]:
    audio_lengths = torch.tensor([example.waveform.numel() for example in examples], dtype=torch.long)
    token_lengths = torch.tensor([example.token_ids.numel() for example in examples], dtype=torch.long)
    max_audio_length = int(audio_lengths.max().item()) if examples else 0
    max_token_length = int(token_lengths.max().item()) if examples else 0

    audio_batch = torch.zeros((len(examples), max_audio_length), dtype=torch.float32)
    token_batch = torch.zeros((len(examples), max_token_length), dtype=torch.long)
    text_feature_batch = torch.stack([example.text_features for example in examples], dim=0)
    for index, example in enumerate(examples):
        audio_batch[index, : example.waveform.numel()] = example.waveform
        token_batch[index, : example.token_ids.numel()] = example.token_ids

    return {
        "record_ids": [example.record_id for example in examples],
        "waveform": audio_batch,
        "audio_lengths": audio_lengths,
        "token_ids": token_batch,
        "token_lengths": token_lengths,
        "text_features": text_feature_batch,
        "texts": [example.text for example in examples],
        "weak_event_hints": [example.weak_event_hints for example in examples],
        "target_special_supervision": [example.target_special_supervision for example in examples],
        "target_event_semantic_sidecar": [example.target_event_semantic_sidecar for example in examples],
    }
