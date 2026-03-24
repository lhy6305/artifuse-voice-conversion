from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.streaming_student.data import (
    collate_streaming_student_batch,
    load_streaming_student_conditioning_asset,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


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

    dry_run_slices: dict[str, object] = {}
    with torch.no_grad():
        for split_name, records in records_by_split.items():
            batch_records = list(records[: max(1, min(int(batch_size), len(records)))])
            examples = load_streaming_student_target_examples_from_records(batch_records)
            batch = collate_streaming_student_batch(
                examples=examples,
                conditioning_asset=conditioning_asset,
            )
            outputs = model(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
                speaker_embedding=batch["speaker_embedding"],
                geom_embedding=batch["geom_embedding"],
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
            ],
            "teacher_label_required_keys": [
                "teacher_hidden",
                "teacher_fused_hidden",
                "teacher_z_art",
                "teacher_event_logits",
                "teacher_event_probs",
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
        "frame_alignment": frame_alignment,
        "status": "frame_contract_aligned" if frame_alignment["all_equal"] else "frame_contract_mismatch",
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
