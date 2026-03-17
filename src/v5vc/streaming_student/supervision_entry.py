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
from v5vc.streaming_student.losses import (
    compute_streaming_student_teacher_supervision_loss,
    resolve_teacher_supervision_weights,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


def prepare_streaming_student_supervision(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
    use_teacher_confidence: bool,
    loss_weight_overrides_path: Path | None,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] supervision_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')}"
    )
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_loss_weight_overrides_path = None
    if loss_weight_overrides_path is not None:
        resolved_loss_weight_overrides_path = loss_weight_overrides_path.resolve()

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
    effective_weights = resolve_teacher_supervision_weights(
        overrides_path=resolved_loss_weight_overrides_path,
    )

    slice_summaries: dict[str, object] = {}
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
            total_loss, metrics = compute_streaming_student_teacher_supervision_loss(
                outputs=outputs,
                batch=batch,
                weights=effective_weights,
                use_teacher_confidence=use_teacher_confidence,
            )
            slice_summaries[split_name] = {
                "record_count": len(records),
                "dry_run_batch_size": len(batch["record_ids"]),
                "sample_record_ids": list(batch["record_ids"]),
                "loss_metrics": metrics,
                "loss_total_tensor": round(float(total_loss.detach().cpu().item()), 6),
            }

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "conditioning": conditioning_asset["summary"],
        "loss_weights": effective_weights,
        "loss_weight_overrides_path": (
            None if resolved_loss_weight_overrides_path is None else resolved_loss_weight_overrides_path.as_posix()
        ),
        "use_teacher_confidence": bool(use_teacher_confidence),
        "slices": slice_summaries,
        "notes": [
            "This stage defines only the minimum teacher-supervised dry-run losses needed to move beyond pure data wiring.",
            "Current supervision intentionally avoids forcing a hidden-state distillation term because Stage3 and offline_mvp hidden dimensions are not yet aligned.",
            "Frontend proxy terms are heuristic and should be treated as bootstrap supervision, not final semantic commitments.",
        ],
        "next_steps": [
            "Decide which teacher_frame_confidence behaviors become actual weighting or filtering policy in real training.",
            "Add explicit Stage3 hidden-space projection only if hidden distillation is still needed after the base loss route is validated.",
            "Build a real training loop on top of this dry-run contract without opening r_res yet.",
        ],
    }

    json_path = output_dir / "streaming_student_supervision_plan.json"
    md_path = output_dir / "streaming_student_supervision_plan.md"
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
    print(
        "[stage3] supervision_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"plan={json_path.as_posix()}"
    )


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Supervision Plan",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- loss_weights: {json.dumps(summary['loss_weights'], ensure_ascii=False)}",
        f"- loss_weight_overrides_path: {summary['loss_weight_overrides_path']}",
        f"- use_teacher_confidence: {summary['use_teacher_confidence']}",
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
                f"- loss_metrics: {json.dumps(payload['loss_metrics'], ensure_ascii=False)}",
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
