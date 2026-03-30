from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.data_scan import summarize_numeric
from v5vc.streaming_student.data import (
    collate_streaming_student_batch,
    collate_streaming_student_paired_batch,
    load_streaming_student_conditioning_asset,
    load_streaming_student_paired_examples_from_records,
    load_streaming_student_paired_records_by_split,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold
from v5vc.streaming_student.pitch_provider import (
    DEFAULT_STAGE3_PITCH_PROVIDER_MODE,
    build_stage3_pitch_provider_model_inputs_from_batch,
    resolve_stage3_pitch_provider_request,
)


def prepare_streaming_student_training_data(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] training_data_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')}"
    )
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    teacher_label_index_path = teacher_label_index_path.resolve()
    calibration_asset_path = calibration_asset_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.eval()
    pitch_provider_request = resolve_stage3_pitch_provider_request(
        dict(config["model"]),
        config_path=config_path,
    )
    pitch_provider_mode = str(pitch_provider_request.get("mode", DEFAULT_STAGE3_PITCH_PROVIDER_MODE))

    dry_run_slices: dict[str, object] = {}
    with torch.no_grad():
        for split_name, records in records_by_split.items():
            batch_records = list(records[: max(1, min(int(batch_size), len(records)))])
            examples = load_streaming_student_target_examples_from_records(
                batch_records,
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
                include_target_acoustic_state=(pitch_provider_mode != DEFAULT_STAGE3_PITCH_PROVIDER_MODE),
                pitch_provider_request=pitch_provider_request,
            )
            batch = collate_streaming_student_batch(
                examples=examples,
                conditioning_asset=conditioning_asset,
            )
            pitch_provider_inputs = build_stage3_pitch_provider_model_inputs_from_batch(
                batch,
                pitch_provider_mode=pitch_provider_mode,
                audio_lengths=batch["audio_lengths"],
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
            )
            outputs = model(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
                speaker_embedding=batch["speaker_embedding"],
                geom_embedding=batch["geom_embedding"],
                **pitch_provider_inputs,
            )
            dry_run_slices[split_name] = build_slice_dry_run_summary(
                split_name=split_name,
                records=records,
                batch=batch,
                outputs=outputs,
            )

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": teacher_label_index_path.as_posix(),
        "calibration_asset_path": calibration_asset_path.as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "conditioning": conditioning_asset["summary"],
        "global_contract": {
            "frame_length": int(config["model"]["frame_length"]),
            "hop_length": int(config["model"]["hop_length"]),
            "r_res_enabled": bool(config["model"].get("r_res_enabled", False)),
            "available_target_sidecars": [
                "weak_event_hints",
                "target_special_supervision",
                "target_event_semantic_sidecar",
                "target_event_timing_semantic_sidecar",
            ],
            "teacher_label_required_keys": [
                "teacher_hidden",
                "teacher_fused_hidden",
                "teacher_z_art",
                "teacher_event_logits",
                "teacher_event_probs",
                "teacher_e_evt",
                "teacher_acoustic",
                "teacher_frame_confidence",
            ],
        },
        "slices": dry_run_slices,
        "notes": [
            "This stage wires split records, sidecars, teacher-label assets, and conditioning assets into a reusable Stage3 batch contract.",
            "Current dry-run keeps full audio intact so the waveform-to-frame contract stays aligned with exported teacher labels.",
            "The output is a data-layer contract check, not a real Student training loop.",
        ],
        "next_steps": [
            "Use teacher_frame_confidence explicitly for weighting or filtering instead of treating it as an always-on final confidence target.",
            "Add Stage3 loss definitions on top of this batch contract without reusing offline_mvp training steps directly.",
            "Keep r_res disabled until the base Student supervision path is stable.",
        ],
    }

    json_path = output_dir / "streaming_student_training_data_plan.json"
    md_path = output_dir / "streaming_student_training_data_plan.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary=summary),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage3] training_data_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"plan={json_path.as_posix()}"
    )


def prepare_streaming_student_paired_training_data(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    train_pair_spec_path: Path,
    validation_pair_spec_path: Path | None,
    batch_size: int,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] paired_training_data_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')}"
    )
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    teacher_label_index_path = teacher_label_index_path.resolve()
    calibration_asset_path = calibration_asset_path.resolve()
    train_pair_spec_path = train_pair_spec_path.resolve()
    resolved_validation_pair_spec_path = (
        None if validation_pair_spec_path is None else validation_pair_spec_path.resolve()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    records_by_split, split_summary = load_streaming_student_paired_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        train_pair_spec_path=train_pair_spec_path,
        validation_pair_spec_path=resolved_validation_pair_spec_path,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.eval()
    if model.frontend.pitch_provider_mode != DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
        raise ValueError(
            "prepare_streaming_student_paired_training_data does not support explicit pitch_provider_mode yet."
        )

    dry_run_slices: dict[str, object] = {}
    with torch.no_grad():
        for split_name, records in records_by_split.items():
            batch_records = list(records[: max(1, min(int(batch_size), len(records)))])
            if not batch_records:
                dry_run_slices[split_name] = build_empty_paired_slice_summary(
                    split_name=split_name,
                    records=records,
                )
                continue
            examples = load_streaming_student_paired_examples_from_records(batch_records)
            batch = collate_streaming_student_paired_batch(
                examples=examples,
                conditioning_asset=conditioning_asset,
            )
            outputs = model(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
                speaker_embedding=batch["speaker_embedding"],
                geom_embedding=batch["geom_embedding"],
            )
            dry_run_slices[split_name] = build_paired_slice_dry_run_summary(
                split_name=split_name,
                records=records,
                batch_records=batch_records,
                examples=examples,
                batch=batch,
                outputs=outputs,
            )

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": teacher_label_index_path.as_posix(),
        "calibration_asset_path": calibration_asset_path.as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "conditioning": conditioning_asset["summary"],
        "global_contract": {
            "record_mode": "paired_source_to_target_stage3_contract",
            "frame_length": int(config["model"]["frame_length"]),
            "hop_length": int(config["model"]["hop_length"]),
            "r_res_enabled": bool(config["model"].get("r_res_enabled", False)),
            "available_source_sidecars": [
                "source_semantic_parity_sidecar",
            ],
            "available_target_sidecars": [
                "target_event_timing_semantic_sidecar",
            ],
            "teacher_label_required_keys": [
                "teacher_hidden",
                "teacher_fused_hidden",
                "teacher_z_art",
                "teacher_event_logits",
                "teacher_event_probs",
                "teacher_e_evt",
                "teacher_acoustic",
                "teacher_frame_confidence",
            ],
        },
        "slices": dry_run_slices,
        "notes": [
            "This paired Stage3 dry-run uses source waveform as Student input and target teacher labels as supervision assets.",
            "The goal is to quantify source-target duration and frame-count mismatch honestly before proposing any paired Stage3 training route.",
            "Current output is a contract audit, not a claim that source-side parity is already train-ready supervision.",
        ],
        "next_steps": [
            "If source model frames and target teacher frames mismatch materially, add an explicit source-target frame bridge instead of forcing direct supervision.",
            "Keep source_semantic_parity_sidecar attached by source_record_id only; do not remap it onto target ids.",
            "Do not start paired Stage3 training loops until this contract summary is accepted as the current ground truth.",
        ],
    }

    json_path = output_dir / "streaming_student_paired_training_data_plan.json"
    md_path = output_dir / "streaming_student_paired_training_data_plan.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_paired_markdown(summary=summary),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage3] paired_training_data_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"plan={json_path.as_posix()}"
    )


def build_slice_dry_run_summary(
    split_name: str,
    records: list[dict[str, object]],
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    outputs: dict[str, torch.Tensor],
) -> dict[str, object]:
    teacher_frame_lengths = batch["teacher_frame_lengths"]
    model_frame_lengths = outputs["frame_mask"].to(torch.long).sum(dim=1)
    frame_alignment = {
        "all_equal": bool(torch.equal(model_frame_lengths.cpu(), teacher_frame_lengths.cpu())),
        "teacher_frame_lengths": teacher_frame_lengths.tolist(),
        "model_frame_lengths": model_frame_lengths.tolist(),
        "delta_per_sample": (model_frame_lengths - teacher_frame_lengths).tolist(),
    }
    return {
        "record_count": len(records),
        "dry_run_batch_size": int(len(batch["record_ids"])),
        "sample_record_ids": list(batch["record_ids"]),
        "sample_teacher_label_paths": list(batch["teacher_label_paths"]),
        "waveform_shape": list(batch["waveform"].shape),
        "audio_lengths": batch["audio_lengths"].tolist(),
        "teacher_shapes": {
            "teacher_hidden": list(batch["teacher_hidden"].shape),
            "teacher_fused_hidden": list(batch["teacher_fused_hidden"].shape),
            "teacher_z_art": list(batch["teacher_z_art"].shape),
            "teacher_event_logits": list(batch["teacher_event_logits"].shape),
            "teacher_e_evt": list(batch["teacher_e_evt"].shape),
            "teacher_acoustic": list(batch["teacher_acoustic"].shape),
            "teacher_frame_confidence": list(batch["teacher_frame_confidence"].shape),
        },
        "student_shapes": {
            "shared_hidden": list(outputs["shared_hidden"].shape),
            "z_art": list(outputs["z_art"].shape),
            "event_logits": list(outputs["event_logits"].shape),
            "coarse_log_f0": list(outputs["coarse_log_f0"].shape),
            "aperiodicity": list(outputs["aperiodicity"].shape),
            "energy": list(outputs["energy"].shape),
            "log_f0_correction": list(outputs["log_f0_correction"].shape),
            "aper_correction": list(outputs["aper_correction"].shape),
            "r_res": list(outputs["r_res"].shape),
        },
        "conditioning_shapes": {
            "speaker_embedding": list(batch["speaker_embedding"].shape),
            "geom_embedding": list(batch["geom_embedding"].shape),
            "alpha": list(batch["alpha"].shape),
        },
        "teacher_confidence": {
            "mean_of_means": round(float(batch["teacher_confidence_means"].mean().item()), 6),
            "mean_low_confidence_frame_ratio": round(
                float(batch["teacher_low_confidence_frame_ratios"].mean().item()),
                6,
            ),
        },
        "semantic_sidecar_summary": summarize_semantic_sidecars(batch["target_event_semantic_sidecar"]),
        "timing_semantic_sidecar_summary": summarize_timing_semantic_sidecars(
            batch["target_event_timing_semantic_sidecar"]
        ),
        "frame_alignment": frame_alignment,
        "status": "frame_contract_aligned" if frame_alignment["all_equal"] else "frame_contract_mismatch",
        "split_name": split_name,
    }


def build_empty_paired_slice_summary(
    split_name: str,
    records: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "record_count": len(records),
        "dry_run_batch_size": 0,
        "sample_pair_record_ids": [],
        "sample_source_record_ids": [],
        "sample_target_record_ids": [],
        "sample_teacher_label_paths": [],
        "waveform_shape": [0, 0],
        "audio_lengths": [],
        "teacher_shapes": {},
        "student_shapes": {},
        "conditioning_shapes": {},
        "teacher_confidence": {},
        "teacher_split_name_counts": {},
        "source_sample_rate_counts": {},
        "source_semantic_parity_sidecar_summary": {
            "present_count": 0,
            "missing_count": 0,
        },
        "source_parity_alignment": {
            "source_parity_duration_sec": [],
            "source_parity_estimated_frame_counts": [],
            "source_parity_duration_metadata_drift_sec": [],
            "source_parity_frame_delta_per_sample": [],
            "source_parity_duration_metadata_drift_stats": summarize_numeric([]),
            "source_parity_frame_delta_stats": summarize_numeric([]),
        },
        "timing_semantic_sidecar_summary": {
            "present_count": 0,
            "missing_count": 0,
        },
        "duration_alignment": {
            "source_duration_sec_stats_actual": summarize_numeric([]),
            "source_duration_sec_stats_pair_spec": summarize_numeric([]),
            "target_duration_sec_stats_actual": summarize_numeric([]),
            "target_duration_sec_stats_pair_spec": summarize_numeric([]),
            "source_to_target_duration_ratio_stats": summarize_numeric([]),
            "source_duration_metadata_drift_stats": summarize_numeric([]),
            "target_duration_metadata_drift_stats": summarize_numeric([]),
            "source_longer_than_target_count": 0,
        },
        "frame_alignment": {
            "all_equal": True,
            "teacher_frame_lengths": [],
            "model_frame_lengths": [],
            "delta_per_sample": [],
            "abs_delta_stats": summarize_numeric([]),
            "model_to_teacher_frame_ratio_stats": summarize_numeric([]),
            "model_longer_than_teacher_count": 0,
        },
        "status": "no_records",
        "split_name": split_name,
    }


def build_paired_slice_dry_run_summary(
    split_name: str,
    records: list[dict[str, object]],
    batch_records: list[dict[str, object]],
    examples: list[object],
    batch: dict[str, torch.Tensor | list[str] | list[dict[str, object] | None]],
    outputs: dict[str, torch.Tensor],
) -> dict[str, object]:
    teacher_frame_lengths = batch["teacher_frame_lengths"]
    model_frame_lengths = outputs["frame_mask"].to(torch.long).sum(dim=1)
    frame_deltas = (model_frame_lengths - teacher_frame_lengths).tolist()
    model_to_teacher_frame_ratio = [
        round(float(model_frames) / float(teacher_frames), 6)
        for model_frames, teacher_frames in zip(
            model_frame_lengths.tolist(),
            teacher_frame_lengths.tolist(),
        )
        if teacher_frames > 0
    ]
    source_durations_actual = [
        round(float(example.waveform.numel()) / float(example.sample_rate), 6)
        for example in examples
    ]
    source_durations_spec = [extract_duration_sec(record=record, key="source_audio") for record in batch_records]
    target_durations_actual = [
        float(dict(record.get("teacher_label_index", {})).get("duration_sec", extract_duration_sec(record=record, key="target_audio")))
        for record in batch_records
    ]
    target_durations = [
        extract_duration_sec(record=record, key="target_audio")
        for record in batch_records
    ]
    source_to_target_duration_ratio = [
        round(source_duration / target_duration, 6)
        for source_duration, target_duration in zip(source_durations_actual, target_durations_actual)
        if target_duration > 0.0
    ]
    source_duration_metadata_drift_sec = [
        round(spec_duration - actual_duration, 6)
        for spec_duration, actual_duration in zip(source_durations_spec, source_durations_actual)
    ]
    target_duration_metadata_drift_sec = [
        round(spec_duration - actual_duration, 6)
        for spec_duration, actual_duration in zip(target_durations, target_durations_actual)
    ]
    parity_sidecars = batch["source_semantic_parity_sidecar"]
    source_parity_estimated_frame_counts = [
        int(sidecar.get("source_estimated_frame_count", 0)) if isinstance(sidecar, dict) else 0
        for sidecar in parity_sidecars
    ]
    source_parity_duration_sec = [
        float(sidecar.get("source_duration_sec", 0.0)) if isinstance(sidecar, dict) else 0.0
        for sidecar in parity_sidecars
    ]
    source_parity_frame_deltas = [
        int(model_frame_length) - int(estimated_frame_count)
        for model_frame_length, estimated_frame_count in zip(
            model_frame_lengths.tolist(),
            source_parity_estimated_frame_counts,
        )
    ]
    frame_alignment = {
        "all_equal": bool(torch.equal(model_frame_lengths.cpu(), teacher_frame_lengths.cpu())),
        "teacher_frame_lengths": teacher_frame_lengths.tolist(),
        "model_frame_lengths": model_frame_lengths.tolist(),
        "delta_per_sample": frame_deltas,
        "abs_delta_stats": summarize_numeric([abs(int(delta)) for delta in frame_deltas]),
        "model_to_teacher_frame_ratio": model_to_teacher_frame_ratio,
        "model_to_teacher_frame_ratio_stats": summarize_numeric(model_to_teacher_frame_ratio),
        "model_longer_than_teacher_count": sum(1 for delta in frame_deltas if delta > 0),
    }
    duration_alignment = {
        "source_audio_duration_sec_actual": source_durations_actual,
        "source_audio_duration_sec_pair_spec": [round(value, 6) for value in source_durations_spec],
        "target_audio_duration_sec_actual": [round(value, 6) for value in target_durations_actual],
        "target_audio_duration_sec_pair_spec": [round(value, 6) for value in target_durations],
        "source_to_target_duration_ratio": source_to_target_duration_ratio,
        "source_duration_sec_stats_actual": summarize_numeric(source_durations_actual),
        "source_duration_sec_stats_pair_spec": summarize_numeric(source_durations_spec),
        "target_duration_sec_stats_actual": summarize_numeric(target_durations_actual),
        "target_duration_sec_stats_pair_spec": summarize_numeric(target_durations),
        "source_to_target_duration_ratio_stats": summarize_numeric(source_to_target_duration_ratio),
        "source_duration_metadata_drift_sec": source_duration_metadata_drift_sec,
        "target_duration_metadata_drift_sec": target_duration_metadata_drift_sec,
        "source_duration_metadata_drift_stats": summarize_numeric(source_duration_metadata_drift_sec),
        "target_duration_metadata_drift_stats": summarize_numeric(target_duration_metadata_drift_sec),
        "source_longer_than_target_count": sum(
            1
            for source_duration, target_duration in zip(source_durations_actual, target_durations_actual)
            if source_duration > target_duration
        ),
    }
    return {
        "record_count": len(records),
        "dry_run_batch_size": int(len(batch["pair_record_ids"])),
        "sample_pair_record_ids": list(batch["pair_record_ids"]),
        "sample_source_record_ids": list(batch["source_record_ids"]),
        "sample_target_record_ids": list(batch["target_record_ids"]),
        "sample_teacher_label_paths": list(batch["teacher_label_paths"]),
        "waveform_shape": list(batch["waveform"].shape),
        "audio_lengths": batch["audio_lengths"].tolist(),
        "teacher_shapes": {
            "teacher_hidden": list(batch["teacher_hidden"].shape),
            "teacher_fused_hidden": list(batch["teacher_fused_hidden"].shape),
            "teacher_z_art": list(batch["teacher_z_art"].shape),
            "teacher_event_logits": list(batch["teacher_event_logits"].shape),
            "teacher_e_evt": list(batch["teacher_e_evt"].shape),
            "teacher_acoustic": list(batch["teacher_acoustic"].shape),
            "teacher_frame_confidence": list(batch["teacher_frame_confidence"].shape),
        },
        "student_shapes": {
            "shared_hidden": list(outputs["shared_hidden"].shape),
            "z_art": list(outputs["z_art"].shape),
            "event_logits": list(outputs["event_logits"].shape),
            "coarse_log_f0": list(outputs["coarse_log_f0"].shape),
            "aperiodicity": list(outputs["aperiodicity"].shape),
            "energy": list(outputs["energy"].shape),
            "log_f0_correction": list(outputs["log_f0_correction"].shape),
            "aper_correction": list(outputs["aper_correction"].shape),
            "r_res": list(outputs["r_res"].shape),
        },
        "conditioning_shapes": {
            "speaker_embedding": list(batch["speaker_embedding"].shape),
            "geom_embedding": list(batch["geom_embedding"].shape),
            "alpha": list(batch["alpha"].shape),
        },
        "teacher_confidence": {
            "mean_of_means": round(float(batch["teacher_confidence_means"].mean().item()), 6),
            "mean_low_confidence_frame_ratio": round(
                float(batch["teacher_low_confidence_frame_ratios"].mean().item()),
                6,
            ),
        },
        "teacher_split_name_counts": count_string_values(batch["teacher_split_names"]),
        "source_sample_rate_counts": count_string_values([example.sample_rate for example in examples]),
        "source_semantic_parity_sidecar_summary": summarize_source_semantic_parity_sidecars(
            batch["source_semantic_parity_sidecar"],
            batch["source_semantic_parity_overview"],
        ),
        "source_parity_alignment": {
            "source_parity_duration_sec": [round(value, 6) for value in source_parity_duration_sec],
            "source_parity_estimated_frame_counts": source_parity_estimated_frame_counts,
            "source_parity_duration_metadata_drift_sec": [
                round(metadata_duration - actual_duration, 6)
                for metadata_duration, actual_duration in zip(source_parity_duration_sec, source_durations_actual)
            ],
            "source_parity_frame_delta_per_sample": source_parity_frame_deltas,
            "source_parity_duration_metadata_drift_stats": summarize_numeric(
                [
                    round(metadata_duration - actual_duration, 6)
                    for metadata_duration, actual_duration in zip(source_parity_duration_sec, source_durations_actual)
                ]
            ),
            "source_parity_frame_delta_stats": summarize_numeric(source_parity_frame_deltas),
        },
        "timing_semantic_sidecar_summary": summarize_timing_semantic_sidecars(
            batch["target_event_timing_semantic_sidecar"]
        ),
        "duration_alignment": duration_alignment,
        "frame_alignment": frame_alignment,
        "status": (
            "paired_source_target_frame_contract_aligned"
            if frame_alignment["all_equal"]
            else "paired_source_target_frame_contract_mismatch"
        ),
        "split_name": split_name,
    }


def summarize_semantic_sidecars(
    sidecars: list[dict[str, object] | None],
) -> dict[str, object]:
    contract_counts: dict[str, int] = {}
    label_status_counts: dict[str, int] = {}
    structure_counts: dict[str, int] = {}
    present_count = 0
    for row in sidecars:
        if not isinstance(row, dict):
            continue
        present_count += 1
        contract_key = str(row.get("semantic_contract_version", "unknown"))
        contract_counts[contract_key] = contract_counts.get(contract_key, 0) + 1
        upgrade_status = row.get("upgrade_status")
        if isinstance(upgrade_status, dict):
            label_key = str(upgrade_status.get("label_status", "unknown"))
            label_status_counts[label_key] = label_status_counts.get(label_key, 0) + 1
        utterance_semantics = row.get("utterance_structure_semantics")
        if isinstance(utterance_semantics, dict):
            structure_key = str(utterance_semantics.get("utterance_structure_type", "unknown"))
            structure_counts[structure_key] = structure_counts.get(structure_key, 0) + 1
    return {
        "present_count": present_count,
        "missing_count": max(0, len(sidecars) - present_count),
        "semantic_contract_version_counts": dict(sorted(contract_counts.items())),
        "semantic_label_status_counts": dict(sorted(label_status_counts.items())),
        "semantic_utterance_structure_type_counts": dict(sorted(structure_counts.items())),
    }


def summarize_timing_semantic_sidecars(
    sidecars: list[dict[str, object] | None],
) -> dict[str, object]:
    contract_counts: dict[str, int] = {}
    label_status_counts: dict[str, int] = {}
    alignment_type_counts: dict[str, int] = {}
    present_count = 0
    multi_clause_count = 0
    pause_present_count = 0
    terminal_present_count = 0
    for row in sidecars:
        if not isinstance(row, dict):
            continue
        present_count += 1
        contract_key = str(row.get("semantic_contract_version", "unknown"))
        contract_counts[contract_key] = contract_counts.get(contract_key, 0) + 1
        upgrade_status = row.get("upgrade_status")
        if isinstance(upgrade_status, dict):
            label_key = str(upgrade_status.get("label_status", "unknown"))
            label_status_counts[label_key] = label_status_counts.get(label_key, 0) + 1
        timing_alignment = row.get("timing_alignment")
        if isinstance(timing_alignment, dict):
            alignment_key = str(timing_alignment.get("alignment_type", "unknown"))
            alignment_type_counts[alignment_key] = alignment_type_counts.get(alignment_key, 0) + 1
        coverage_summary = {}
        time_aware_semantics = row.get("time_aware_semantics")
        if isinstance(time_aware_semantics, dict) and isinstance(time_aware_semantics.get("coverage_summary"), dict):
            coverage_summary = dict(time_aware_semantics["coverage_summary"])
        if int(coverage_summary.get("clause_region_count", 0)) >= 2:
            multi_clause_count += 1
        if int(coverage_summary.get("pause_boundary_event_count", 0)) >= 1:
            pause_present_count += 1
        if int(coverage_summary.get("terminal_boundary_event_count", 0)) >= 1:
            terminal_present_count += 1
    return {
        "present_count": present_count,
        "missing_count": max(0, len(sidecars) - present_count),
        "timing_contract_version_counts": dict(sorted(contract_counts.items())),
        "timing_label_status_counts": dict(sorted(label_status_counts.items())),
        "timing_alignment_type_counts": dict(sorted(alignment_type_counts.items())),
        "timing_multi_clause_count": multi_clause_count,
        "timing_pause_present_count": pause_present_count,
        "timing_terminal_present_count": terminal_present_count,
    }


def summarize_source_semantic_parity_sidecars(
    sidecars: list[dict[str, object] | None],
    overviews: list[dict[str, object]],
) -> dict[str, object]:
    contract_counts: dict[str, int] = {}
    parity_status_counts: dict[str, int] = {}
    label_status_counts: dict[str, int] = {}
    utterance_structure_counts: dict[str, int] = {}
    present_count = 0
    semantic_ready_count = 0
    for sidecar, overview in zip(sidecars, overviews):
        if not isinstance(sidecar, dict):
            continue
        present_count += 1
        contract_key = str(sidecar.get("semantic_contract_version", "unknown"))
        contract_counts[contract_key] = contract_counts.get(contract_key, 0) + 1
        parity_key = str(sidecar.get("parity_status", "unknown"))
        parity_status_counts[parity_key] = parity_status_counts.get(parity_key, 0) + 1
        upgrade_status = sidecar.get("upgrade_status")
        if isinstance(upgrade_status, dict):
            if bool(upgrade_status.get("semantic_ready_for_source_side_bootstrap", False)):
                semantic_ready_count += 1
        if isinstance(overview, dict):
            label_key = str(overview.get("parity_label_status", "unknown"))
            label_status_counts[label_key] = label_status_counts.get(label_key, 0) + 1
            structure_key = str(overview.get("parity_utterance_structure_type", "unknown"))
            utterance_structure_counts[structure_key] = utterance_structure_counts.get(structure_key, 0) + 1
    return {
        "present_count": present_count,
        "missing_count": max(0, len(sidecars) - present_count),
        "semantic_ready_for_source_side_bootstrap_count": semantic_ready_count,
        "parity_contract_version_counts": dict(sorted(contract_counts.items())),
        "parity_status_counts": dict(sorted(parity_status_counts.items())),
        "semantic_label_status_counts": dict(sorted(label_status_counts.items())),
        "semantic_utterance_structure_type_counts": dict(sorted(utterance_structure_counts.items())),
    }


def extract_duration_sec(record: dict[str, object], key: str) -> float:
    payload = record.get(key)
    if isinstance(payload, dict):
        raw_value = payload.get("duration_sec")
        if raw_value is not None:
            return float(raw_value)
    audio_payload = record.get("audio")
    if isinstance(audio_payload, dict):
        raw_value = audio_payload.get("duration_sec")
        if raw_value is not None:
            return float(raw_value)
    return 0.0


def count_string_values(values: list[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Training Data Plan",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- frame_contract: {json.dumps(summary['global_contract'], ensure_ascii=False)}",
        "",
    ]
    for split_name in ("target_train", "target_validation", "target_special_eval"):
        payload = summary["slices"][split_name]
        lines.extend(
            [
                f"## {split_name}",
                f"- record_count: {payload['record_count']}",
                f"- dry_run_batch_size: {payload['dry_run_batch_size']}",
                f"- sample_record_ids: {payload['sample_record_ids']}",
                f"- waveform_shape: {payload['waveform_shape']}",
                f"- teacher_shapes: {json.dumps(payload['teacher_shapes'], ensure_ascii=False)}",
                f"- student_shapes: {json.dumps(payload['student_shapes'], ensure_ascii=False)}",
                f"- conditioning_shapes: {json.dumps(payload['conditioning_shapes'], ensure_ascii=False)}",
                f"- teacher_confidence: {json.dumps(payload['teacher_confidence'], ensure_ascii=False)}",
                f"- semantic_sidecar_summary: {json.dumps(payload['semantic_sidecar_summary'], ensure_ascii=False)}",
                f"- timing_semantic_sidecar_summary: {json.dumps(payload['timing_semantic_sidecar_summary'], ensure_ascii=False)}",
                f"- frame_alignment: {json.dumps(payload['frame_alignment'], ensure_ascii=False)}",
                f"- status: {payload['status']}",
                "",
            ]
        )
    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Next Steps")
    for item in summary["next_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def build_paired_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Paired Streaming Student Training Data Plan",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- frame_contract: {json.dumps(summary['global_contract'], ensure_ascii=False)}",
        f"- split: {json.dumps(summary['split'], ensure_ascii=False)}",
        "",
    ]
    for split_name in ("train", "validation"):
        payload = summary["slices"][split_name]
        lines.extend(
            [
                f"## {split_name}",
                f"- record_count: {payload['record_count']}",
                f"- dry_run_batch_size: {payload['dry_run_batch_size']}",
                f"- sample_pair_record_ids: {payload['sample_pair_record_ids']}",
                f"- sample_source_record_ids: {payload['sample_source_record_ids']}",
                f"- sample_target_record_ids: {payload['sample_target_record_ids']}",
                f"- waveform_shape: {payload['waveform_shape']}",
                f"- teacher_shapes: {json.dumps(payload['teacher_shapes'], ensure_ascii=False)}",
                f"- student_shapes: {json.dumps(payload['student_shapes'], ensure_ascii=False)}",
                f"- conditioning_shapes: {json.dumps(payload['conditioning_shapes'], ensure_ascii=False)}",
                f"- teacher_confidence: {json.dumps(payload['teacher_confidence'], ensure_ascii=False)}",
                f"- teacher_split_name_counts: {json.dumps(payload['teacher_split_name_counts'], ensure_ascii=False)}",
                f"- source_sample_rate_counts: {json.dumps(payload['source_sample_rate_counts'], ensure_ascii=False)}",
                f"- source_semantic_parity_sidecar_summary: {json.dumps(payload['source_semantic_parity_sidecar_summary'], ensure_ascii=False)}",
                f"- source_parity_alignment: {json.dumps(payload['source_parity_alignment'], ensure_ascii=False)}",
                f"- timing_semantic_sidecar_summary: {json.dumps(payload['timing_semantic_sidecar_summary'], ensure_ascii=False)}",
                f"- duration_alignment: {json.dumps(payload['duration_alignment'], ensure_ascii=False)}",
                f"- frame_alignment: {json.dumps(payload['frame_alignment'], ensure_ascii=False)}",
                f"- status: {payload['status']}",
                "",
            ]
        )
    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Next Steps")
    for item in summary["next_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
