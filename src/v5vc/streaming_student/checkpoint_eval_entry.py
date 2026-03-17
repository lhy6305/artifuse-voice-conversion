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
    slice_streaming_student_batch_records,
)
from v5vc.streaming_student.losses import (
    build_default_teacher_supervision_weights,
    compute_streaming_student_teacher_supervision_loss,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


def evaluate_streaming_student_checkpoint(
    checkpoint_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
    include_special_eval: bool,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    checkpoint_path = checkpoint_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = payload.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"Checkpoint missing config payload: {checkpoint_path}")
    experiment_id = str(payload.get("experiment_id", checkpoint_path.stem))
    config_path = Path(str(payload.get("config_path", "configs/streaming_student_stage_template.json")))
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()
    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.load_state_dict(payload["model_state_dict"])
    model.eval()

    training_summary = dict(payload.get("training", {}))
    loss_weights = dict(training_summary.get("loss_weights", {})) or build_default_teacher_supervision_weights()
    use_teacher_confidence = bool(training_summary.get("use_teacher_confidence", True))

    evaluation_slices = ["target_validation"]
    if include_special_eval:
        evaluation_slices.append("target_special_eval")

    slice_summaries: dict[str, object] = {}
    with torch.no_grad():
        for split_name in evaluation_slices:
            slice_summaries[split_name] = evaluate_split(
                model=model,
                records=records_by_split[split_name],
                conditioning_asset=conditioning_asset,
                loss_weights=loss_weights,
                use_teacher_confidence=use_teacher_confidence,
                batch_size=batch_size,
            )

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "experiment_id": experiment_id,
        "checkpoint_path": checkpoint_path.as_posix(),
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "conditioning": conditioning_asset["summary"],
        "training": {
            "batch_size": int(batch_size),
            "loss_weights": loss_weights,
            "loss_weight_overrides_path": training_summary.get("loss_weight_overrides_path"),
            "use_teacher_confidence": use_teacher_confidence,
        },
        "slices": slice_summaries,
        "notes": [
            "This evaluation uses the stored Stage3 checkpoint with the current teacher-label and calibration assets.",
            "Unlike the in-loop sampled validation, this report walks the full selected slice sequentially.",
            "These losses are still teacher-supervised proxy losses, not final user-facing quality metrics.",
        ],
    }

    json_path = output_dir / f"{experiment_id}.checkpoint_eval.json"
    md_path = output_dir / f"{experiment_id}.checkpoint_eval.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def evaluate_split(
    model: torch.nn.Module,
    records: list[dict[str, object]],
    conditioning_asset: dict[str, object],
    loss_weights: dict[str, float],
    use_teacher_confidence: bool,
    batch_size: int,
) -> dict[str, object]:
    effective_batch_size = max(1, int(batch_size))
    batch_count = (len(records) + effective_batch_size - 1) // effective_batch_size
    batch_metrics: list[dict[str, float]] = []
    sampled_record_ids: list[list[str]] = []
    for batch_index in range(batch_count):
        batch_records = slice_streaming_student_batch_records(
            records=records,
            batch_size=effective_batch_size,
            batch_index=batch_index,
        )
        if not batch_records:
            continue
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
        _loss, metrics = compute_streaming_student_teacher_supervision_loss(
            outputs=outputs,
            batch=batch,
            weights=loss_weights,
            use_teacher_confidence=use_teacher_confidence,
        )
        batch_metrics.append(metrics)
        sampled_record_ids.append(list(batch["record_ids"]))
    return {
        "record_count": len(records),
        "batch_count": batch_count,
        "loss_metrics": average_metric_dicts(batch_metrics),
        "sample_record_id_batches": sampled_record_ids[:4],
    }


def average_metric_dicts(metrics_list: list[dict[str, float]]) -> dict[str, float]:
    if not metrics_list:
        return {}
    keys = metrics_list[0].keys()
    averaged: dict[str, float] = {}
    for key in keys:
        first_value = metrics_list[0][key]
        if isinstance(first_value, bool):
            averaged[key] = bool(all(bool(metrics[key]) for metrics in metrics_list))
            continue
        averaged[key] = round(
            sum(float(metrics[key]) for metrics in metrics_list) / len(metrics_list),
            6,
        )
    return averaged


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Checkpoint Eval",
        "",
        f"- experiment_id: {summary['experiment_id']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        "",
    ]
    for split_name, payload in dict(summary["slices"]).items():
        lines.extend(
            [
                f"## {split_name}",
                f"- record_count: {payload['record_count']}",
                f"- batch_count: {payload['batch_count']}",
                f"- loss_metrics: {json.dumps(payload['loss_metrics'], ensure_ascii=False)}",
                f"- sample_record_id_batches: {payload['sample_record_id_batches']}",
                "",
            ]
        )
    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
