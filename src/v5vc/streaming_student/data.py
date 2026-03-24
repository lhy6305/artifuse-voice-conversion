from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import torch

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    attach_target_event_semantic_sidecar,
    attach_target_special_supervision,
    attach_target_weak_event_hints,
    infer_target_event_semantic_sidecar_path,
    load_target_event_semantic_sidecar_map,
    load_target_special_supervision_map,
    load_target_weak_event_hint_map,
    load_waveform,
)
from v5vc.train_entry import load_training_split


@dataclass
class StreamingStudentTargetExample:
    record_id: str
    split_name: str
    audio_path: Path
    sample_rate: int
    waveform: torch.Tensor
    weak_event_hints: dict[str, object] | None
    target_special_supervision: dict[str, object] | None
    target_event_semantic_sidecar: dict[str, object] | None
    teacher_label_path: Path
    teacher_frame_mask: torch.Tensor
    teacher_hidden: torch.Tensor
    teacher_fused_hidden: torch.Tensor
    teacher_z_art: torch.Tensor
    teacher_event_logits: torch.Tensor
    teacher_event_probs: torch.Tensor
    teacher_acoustic: torch.Tensor
    teacher_frame_confidence: torch.Tensor
    teacher_confidence_mean: float
    teacher_low_confidence_frame_ratio: float


def load_streaming_student_target_records_by_split(
    config_path: Path,
    config: dict[str, object],
    teacher_label_index_path: Path,
    split_dir: Path | None,
) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    config_path = config_path.resolve()
    teacher_label_index_path = teacher_label_index_path.resolve()
    manifest_dir = (config_path.parent.parent / str(config["data"]["manifest_dir"])).resolve()
    resolved_split_dir = resolve_split_dir(config_path=config_path, config=config, split_dir=split_dir)
    (
        target_train_records,
        target_validation_records,
        target_special_eval_records,
        _source_train_records,
        _source_validation_records,
        split_summary,
    ) = load_training_split(
        manifest_dir=manifest_dir,
        split_dir=resolved_split_dir,
        training_config={
            "target_validation_count": int(config.get("data", {}).get("target_validation_count", 0)),
            "source_validation_count": int(config.get("data", {}).get("source_validation_count", 0)),
        },
    )
    target_train_records = attach_sidecars_if_available(
        config_path=config_path,
        config=config,
        records=target_train_records,
    )
    target_validation_records = attach_sidecars_if_available(
        config_path=config_path,
        config=config,
        records=target_validation_records,
    )
    target_special_eval_records = attach_sidecars_if_available(
        config_path=config_path,
        config=config,
        records=target_special_eval_records,
    )
    teacher_index_rows = load_jsonl(teacher_label_index_path)
    teacher_index_map = {
        str(row["record_id"]): dict(row)
        for row in teacher_index_rows
    }
    records_by_split = {
        "target_train": attach_teacher_label_index(
            records=target_train_records,
            teacher_index_map=teacher_index_map,
            split_name="target_train",
        ),
        "target_validation": attach_teacher_label_index(
            records=target_validation_records,
            teacher_index_map=teacher_index_map,
            split_name="target_validation",
        ),
        "target_special_eval": attach_teacher_label_index(
            records=target_special_eval_records,
            teacher_index_map=teacher_index_map,
            split_name="target_special_eval",
        ),
    }
    return records_by_split, split_summary


def resolve_split_dir(
    config_path: Path,
    config: dict[str, object],
    split_dir: Path | None,
) -> Path:
    if split_dir is not None:
        return split_dir.resolve()
    raw_value = config.get("data", {}).get("split_dir")
    if raw_value in {None, ""}:
        raise ValueError("Stage3 training data wiring requires a materialized split_dir.")
    return (config_path.parent.parent / str(raw_value)).resolve()


def attach_sidecars_if_available(
    config_path: Path,
    config: dict[str, object],
    records: list[dict[str, object]],
) -> list[dict[str, object]]:
    attached_records = list(records)
    weak_event_hints_path = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("target_weak_event_hints_path"),
    )
    if weak_event_hints_path is not None and weak_event_hints_path.exists():
        attached_records = attach_target_weak_event_hints(
            attached_records,
            load_target_weak_event_hint_map(weak_event_hints_path),
        )
    special_supervision_path = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("target_special_supervision_path"),
    )
    if special_supervision_path is not None and special_supervision_path.exists():
        attached_records = attach_target_special_supervision(
            attached_records,
            load_target_special_supervision_map(special_supervision_path),
        )
    semantic_sidecar_path = resolve_target_event_semantic_sidecar_path(
        config_path=config_path,
        config=config,
    )
    if semantic_sidecar_path is not None and semantic_sidecar_path.exists():
        attached_records = attach_target_event_semantic_sidecar(
            attached_records,
            load_target_event_semantic_sidecar_map(semantic_sidecar_path),
        )
    return attached_records


def resolve_optional_path(config_path: Path, raw_value: object) -> Path | None:
    if raw_value in {None, ""}:
        return None
    return (config_path.parent.parent / str(raw_value)).resolve()


def resolve_target_event_semantic_sidecar_path(
    config_path: Path,
    config: dict[str, object],
) -> Path | None:
    resolved = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("target_event_semantic_sidecar_path"),
    )
    if resolved is not None:
        return resolved
    split_dir = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("split_dir"),
    )
    return infer_target_event_semantic_sidecar_path(split_dir)


def attach_teacher_label_index(
    records: list[dict[str, object]],
    teacher_index_map: dict[str, dict[str, object]],
    split_name: str,
) -> list[dict[str, object]]:
    attached_records: list[dict[str, object]] = []
    missing_record_ids: list[str] = []
    split_mismatch_ids: list[str] = []
    for record in records:
        record_id = str(record["record_id"])
        teacher_row = teacher_index_map.get(record_id)
        if teacher_row is None:
            missing_record_ids.append(record_id)
            continue
        teacher_split_name = str(teacher_row.get("split_name", ""))
        if teacher_split_name != split_name:
            split_mismatch_ids.append(record_id)
            continue
        updated = dict(record)
        updated["teacher_label_index"] = teacher_row
        attached_records.append(updated)
    if missing_record_ids:
        preview = ", ".join(missing_record_ids[:8])
        raise ValueError(
            f"Teacher-label index missing {len(missing_record_ids)} records for {split_name}: {preview}"
        )
    if split_mismatch_ids:
        preview = ", ".join(split_mismatch_ids[:8])
        raise ValueError(
            f"Teacher-label split mismatch for {len(split_mismatch_ids)} records in {split_name}: {preview}"
        )
    return attached_records


def load_streaming_student_target_examples_from_records(
    records: list[dict[str, object]],
) -> list[StreamingStudentTargetExample]:
    examples: list[StreamingStudentTargetExample] = []
    for record in records:
        teacher_row = dict(record.get("teacher_label_index", {}))
        teacher_label_path = Path(str(teacher_row["teacher_label_path"])).resolve()
        teacher_payload = torch.load(teacher_label_path, map_location="cpu", weights_only=False)
        waveform, sample_rate = load_waveform(Path(record["audio_path"]), max_duration_sec=None)
        record_id = str(record["record_id"])
        teacher_record_id = str(teacher_payload.get("record_id"))
        if teacher_record_id != record_id:
            raise ValueError(
                f"Teacher-label record_id mismatch: manifest={record_id} teacher={teacher_record_id}"
            )
        examples.append(
            StreamingStudentTargetExample(
                record_id=record_id,
                split_name=str(teacher_row["split_name"]),
                audio_path=Path(record["audio_path"]),
                sample_rate=sample_rate,
                waveform=waveform,
                weak_event_hints=record.get("weak_event_hints"),
                target_special_supervision=record.get("target_special_supervision"),
                target_event_semantic_sidecar=record.get("target_event_semantic_sidecar"),
                teacher_label_path=teacher_label_path,
                teacher_frame_mask=teacher_payload["frame_mask"].to(torch.bool),
                teacher_hidden=teacher_payload["hidden"].to(torch.float32),
                teacher_fused_hidden=teacher_payload["fused_hidden"].to(torch.float32),
                teacher_z_art=teacher_payload["z_art"].to(torch.float32),
                teacher_event_logits=teacher_payload["event_logits"].to(torch.float32),
                teacher_event_probs=teacher_payload["event_probs"].to(torch.float32),
                teacher_acoustic=teacher_payload["acoustic"].to(torch.float32),
                teacher_frame_confidence=teacher_payload["frame_confidence"].to(torch.float32),
                teacher_confidence_mean=float(teacher_row.get("confidence_mean", 0.0)),
                teacher_low_confidence_frame_ratio=float(teacher_row.get("low_confidence_frame_ratio", 0.0)),
            )
        )
    return examples


def select_streaming_student_batch_records(
    records: list[dict[str, object]],
    batch_size: int,
    batch_index: int,
) -> list[dict[str, object]]:
    if not records:
        return []
    effective_batch_size = max(1, min(int(batch_size), len(records)))
    start_index = (int(batch_index) * effective_batch_size) % len(records)
    return [
        records[(start_index + offset) % len(records)]
        for offset in range(effective_batch_size)
    ]


def slice_streaming_student_batch_records(
    records: list[dict[str, object]],
    batch_size: int,
    batch_index: int,
) -> list[dict[str, object]]:
    if not records:
        return []
    effective_batch_size = max(1, int(batch_size))
    start_index = int(batch_index) * effective_batch_size
    end_index = min(len(records), start_index + effective_batch_size)
    if start_index >= len(records):
        return []
    return list(records[start_index:end_index])


def load_streaming_student_conditioning_asset(
    calibration_asset_path: Path,
) -> dict[str, object]:
    calibration_asset_path = calibration_asset_path.resolve()
    payload = json.loads(calibration_asset_path.read_text(encoding="utf-8"))
    conditioning_assets = dict(payload.get("conditioning_assets", {}))
    speaker_assets = dict(conditioning_assets.get("s_spk_target", {}))
    geom_assets = dict(conditioning_assets.get("s_geom_target", {}))
    alpha_assets = dict(conditioning_assets.get("alpha", {}))
    speaker_vector = torch.tensor(list(speaker_assets.get("vector", [])), dtype=torch.float32)
    geom_vector = torch.tensor(list(geom_assets.get("vector", [])), dtype=torch.float32)
    alpha_value = float(alpha_assets.get("value", 1.0))
    if speaker_vector.ndim != 1 or speaker_vector.numel() <= 0:
        raise ValueError(f"Invalid speaker conditioning vector in {calibration_asset_path}")
    if geom_vector.ndim != 1 or geom_vector.numel() <= 0:
        raise ValueError(f"Invalid geometry conditioning vector in {calibration_asset_path}")
    return {
        "speaker_embedding": speaker_vector,
        "geom_embedding": geom_vector,
        "alpha": alpha_value,
        "summary": {
            "asset_version": str(payload.get("asset_version", "unknown")),
            "asset_status": str(payload.get("status", "unknown")),
            "speaker_dim": int(speaker_vector.numel()),
            "geom_dim": int(geom_vector.numel()),
            "alpha_value": alpha_value,
            "source": calibration_asset_path.as_posix(),
        },
    }


def collate_streaming_student_batch(
    examples: list[StreamingStudentTargetExample],
    conditioning_asset: dict[str, object],
) -> dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]]:
    if not examples:
        raise ValueError("Stage3 collate received an empty example list.")
    audio_lengths = torch.tensor([example.waveform.numel() for example in examples], dtype=torch.long)
    max_audio_length = int(audio_lengths.max().item())
    audio_batch = torch.zeros((len(examples), max_audio_length), dtype=torch.float32)
    for index, example in enumerate(examples):
        audio_batch[index, : example.waveform.numel()] = example.waveform

    teacher_frame_lengths = torch.tensor(
        [int(example.teacher_frame_mask.sum().item()) for example in examples],
        dtype=torch.long,
    )
    max_teacher_frames = int(teacher_frame_lengths.max().item())
    hidden_dim = int(examples[0].teacher_hidden.shape[-1])
    fused_hidden_dim = int(examples[0].teacher_fused_hidden.shape[-1])
    z_art_dim = int(examples[0].teacher_z_art.shape[-1])
    event_dim = int(examples[0].teacher_event_logits.shape[-1])
    acoustic_dim = int(examples[0].teacher_acoustic.shape[-1])

    teacher_frame_mask = torch.zeros((len(examples), max_teacher_frames), dtype=torch.bool)
    teacher_hidden = torch.zeros((len(examples), max_teacher_frames, hidden_dim), dtype=torch.float32)
    teacher_fused_hidden = torch.zeros((len(examples), max_teacher_frames, fused_hidden_dim), dtype=torch.float32)
    teacher_z_art = torch.zeros((len(examples), max_teacher_frames, z_art_dim), dtype=torch.float32)
    teacher_event_logits = torch.zeros((len(examples), max_teacher_frames, event_dim), dtype=torch.float32)
    teacher_event_probs = torch.zeros((len(examples), max_teacher_frames, event_dim), dtype=torch.float32)
    teacher_acoustic = torch.zeros((len(examples), max_teacher_frames, acoustic_dim), dtype=torch.float32)
    teacher_frame_confidence = torch.zeros((len(examples), max_teacher_frames, 1), dtype=torch.float32)

    for index, example in enumerate(examples):
        frame_count = int(example.teacher_frame_mask.sum().item())
        teacher_frame_mask[index, :frame_count] = example.teacher_frame_mask[:frame_count]
        teacher_hidden[index, :frame_count] = example.teacher_hidden[:frame_count]
        teacher_fused_hidden[index, :frame_count] = example.teacher_fused_hidden[:frame_count]
        teacher_z_art[index, :frame_count] = example.teacher_z_art[:frame_count]
        teacher_event_logits[index, :frame_count] = example.teacher_event_logits[:frame_count]
        teacher_event_probs[index, :frame_count] = example.teacher_event_probs[:frame_count]
        teacher_acoustic[index, :frame_count] = example.teacher_acoustic[:frame_count]
        teacher_frame_confidence[index, :frame_count] = example.teacher_frame_confidence[:frame_count]

    speaker_embedding = conditioning_asset["speaker_embedding"].to(torch.float32)
    geom_embedding = conditioning_asset["geom_embedding"].to(torch.float32)
    speaker_embedding_batch = speaker_embedding.unsqueeze(0).expand(len(examples), -1).clone()
    geom_embedding_batch = geom_embedding.unsqueeze(0).expand(len(examples), -1).clone()
    alpha = float(conditioning_asset["alpha"])
    alpha_batch = torch.full((len(examples), 1), alpha, dtype=torch.float32)

    return {
        "record_ids": [example.record_id for example in examples],
        "split_names": [example.split_name for example in examples],
        "waveform": audio_batch,
        "audio_lengths": audio_lengths,
        "teacher_label_paths": [example.teacher_label_path.as_posix() for example in examples],
        "teacher_frame_lengths": teacher_frame_lengths,
        "teacher_frame_mask": teacher_frame_mask,
        "teacher_hidden": teacher_hidden,
        "teacher_fused_hidden": teacher_fused_hidden,
        "teacher_z_art": teacher_z_art,
        "teacher_event_logits": teacher_event_logits,
        "teacher_event_probs": teacher_event_probs,
        "teacher_acoustic": teacher_acoustic,
        "teacher_frame_confidence": teacher_frame_confidence,
        "teacher_confidence_means": torch.tensor(
            [example.teacher_confidence_mean for example in examples],
            dtype=torch.float32,
        ),
        "teacher_low_confidence_frame_ratios": torch.tensor(
            [example.teacher_low_confidence_frame_ratio for example in examples],
            dtype=torch.float32,
        ),
        "speaker_embedding": speaker_embedding_batch,
        "geom_embedding": geom_embedding_batch,
        "alpha": alpha_batch,
        "weak_event_hints": [example.weak_event_hints for example in examples],
        "target_special_supervision": [example.target_special_supervision for example in examples],
        "target_event_semantic_sidecar": [example.target_event_semantic_sidecar for example in examples],
        "conditioning_summary": dict(conditioning_asset["summary"]),
    }
