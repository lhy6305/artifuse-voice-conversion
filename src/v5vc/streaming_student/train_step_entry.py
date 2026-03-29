from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch
from torch.nn.utils import clip_grad_norm_

from v5vc.streaming_student.data import (
    collate_streaming_student_batch,
    load_streaming_student_conditioning_asset,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.losses import (
    compute_streaming_student_teacher_supervision_loss,
    resolve_semantic_supervision_config,
    resolve_teacher_supervision_weights,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


def run_streaming_student_training_step(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
    learning_rate: float,
    max_grad_norm: float,
    experiment_id: str,
    use_teacher_confidence: bool,
    loss_weight_overrides_path: Path | None,
    init_checkpoint_path: Path | None = None,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] training_step_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} experiment_id={experiment_id}"
    )
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = output_dir / "checkpoints"
    logs_dir = output_dir / "logs"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    resolved_loss_weight_overrides_path = None
    if loss_weight_overrides_path is not None:
        resolved_loss_weight_overrides_path = loss_weight_overrides_path.resolve()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    torch.manual_seed(int(config.get("training", {}).get("seed", 20260317)))
    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    loss_weights = resolve_teacher_supervision_weights(
        overrides_path=resolved_loss_weight_overrides_path,
    )
    semantic_supervision = resolve_semantic_supervision_config(
        config=config.get("semantic_supervision"),
        overrides_path=resolved_loss_weight_overrides_path,
    )

    train_examples = load_streaming_student_target_examples_from_records(
        list(records_by_split["target_train"][: max(1, min(int(batch_size), len(records_by_split["target_train"])))]),
        frame_length=int(config["model"]["frame_length"]),
        hop_length=int(config["model"]["hop_length"]),
        include_target_acoustic_state=True,
    )
    train_batch = collate_streaming_student_batch(
        examples=train_examples,
        conditioning_asset=conditioning_asset,
    )

    validation_examples = load_streaming_student_target_examples_from_records(
        list(
            records_by_split["target_validation"][
                : max(1, min(int(batch_size), len(records_by_split["target_validation"])))
            ]
        ),
        frame_length=int(config["model"]["frame_length"]),
        hop_length=int(config["model"]["hop_length"]),
        include_target_acoustic_state=True,
    )
    validation_batch = collate_streaming_student_batch(
        examples=validation_examples,
        conditioning_asset=conditioning_asset,
    )

    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    resolved_init_checkpoint_path = None if init_checkpoint_path is None else init_checkpoint_path.resolve()
    if resolved_init_checkpoint_path is not None:
        init_payload = torch.load(resolved_init_checkpoint_path, map_location='cpu', weights_only=False)
        model.load_state_dict(init_payload['model_state_dict'])
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))

    model.train()
    train_outputs = model(
        waveform=train_batch["waveform"],
        lengths=train_batch["audio_lengths"],
        speaker_embedding=train_batch["speaker_embedding"],
        geom_embedding=train_batch["geom_embedding"],
    )
    train_loss, train_metrics = compute_streaming_student_teacher_supervision_loss(
        outputs=train_outputs,
        batch=train_batch,
        weights=loss_weights,
        use_teacher_confidence=use_teacher_confidence,
        semantic_supervision=semantic_supervision,
    )
    optimizer.zero_grad(set_to_none=True)
    train_loss.backward()
    grad_norm = float(clip_grad_norm_(model.parameters(), float(max_grad_norm)).item())
    optimizer.step()

    model.eval()
    with torch.no_grad():
        validation_outputs = model(
            waveform=validation_batch["waveform"],
            lengths=validation_batch["audio_lengths"],
            speaker_embedding=validation_batch["speaker_embedding"],
            geom_embedding=validation_batch["geom_embedding"],
        )
        validation_loss, validation_metrics = compute_streaming_student_teacher_supervision_loss(
            outputs=validation_outputs,
            batch=validation_batch,
            weights=loss_weights,
            use_teacher_confidence=use_teacher_confidence,
            semantic_supervision=semantic_supervision,
        )

    checkpoint_path = checkpoints_dir / f"{experiment_id}.step1.pt"
    torch.save(
        {
            "experiment_id": experiment_id,
            "step": 1,
            "config": config,
            "config_path": config_path.as_posix(),
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "conditioning_summary": conditioning_asset["summary"],
            "training": {
                "batch_size": len(train_batch["record_ids"]),
                "learning_rate": float(learning_rate),
                "max_grad_norm": float(max_grad_norm),
                "use_teacher_confidence": bool(use_teacher_confidence),
                "loss_weights": loss_weights,
                "semantic_supervision": semantic_supervision,
                "loss_weight_overrides_path": (
                    None
                    if resolved_loss_weight_overrides_path is None
                    else resolved_loss_weight_overrides_path.as_posix()
                ),
                "grad_norm": round(grad_norm, 6),
            },
            "train_metrics": train_metrics,
            "validation_metrics": validation_metrics,
        },
        checkpoint_path,
    )

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "experiment_id": experiment_id,
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
        "training": {
            "batch_size": len(train_batch["record_ids"]),
            "learning_rate": float(learning_rate),
            "max_grad_norm": float(max_grad_norm),
            "use_teacher_confidence": bool(use_teacher_confidence),
            "loss_weights": loss_weights,
            "semantic_supervision": semantic_supervision,
            "loss_weight_overrides_path": (
                None if resolved_loss_weight_overrides_path is None else resolved_loss_weight_overrides_path.as_posix()
            ),
            "grad_norm": round(grad_norm, 6),
        },
        "train_step": {
            "record_ids": list(train_batch["record_ids"]),
            "loss_metrics": train_metrics,
        },
        "validation_step": {
            "record_ids": list(validation_batch["record_ids"]),
            "loss_metrics": validation_metrics,
        },
        "artifacts": {
            "checkpoint_path": checkpoint_path.as_posix(),
        },
        "notes": [
            "This is a one-step Stage3 training scaffold, not a full training loop.",
            "The goal is to verify forward, loss, backward, optimizer, and checkpoint plumbing on top of the new Stage3 batch contract.",
            "The checkpoint should be interpreted as a wiring artifact, not as a meaningful trained model milestone.",
        ],
        "next_steps": [
            "Extend this scaffold into a multi-step training loop with periodic validation and log writing.",
            "Decide whether teacher_frame_confidence stays as weighting only or also becomes a filtering or curriculum signal.",
            "Keep r_res disabled while the base Stage3 supervision route is still stabilizing.",
        ],
        "status": "training_step_scaffold_completed",
    }

    log_json_path = logs_dir / f"{experiment_id}.step1.json"
    log_md_path = output_dir / f"{experiment_id}.step1.md"
    log_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log_md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
    )
    print(
        "[stage3] training_step_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"checkpoint={checkpoint_path.as_posix()}"
    )


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Training Step Scaffold",
        "",
        f"- experiment_id: {summary['experiment_id']}",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        "",
        "## Train Step",
        f"- record_ids: {summary['train_step']['record_ids']}",
        f"- loss_metrics: {json.dumps(summary['train_step']['loss_metrics'], ensure_ascii=False)}",
        "",
        "## Validation Step",
        f"- record_ids: {summary['validation_step']['record_ids']}",
        f"- loss_metrics: {json.dumps(summary['validation_step']['loss_metrics'], ensure_ascii=False)}",
        "",
        "## Artifacts",
        f"- checkpoint_path: {summary['artifacts']['checkpoint_path']}",
        "",
        "## Notes",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Next Steps"])
    for item in summary["next_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
