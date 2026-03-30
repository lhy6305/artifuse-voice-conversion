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
    select_streaming_student_batch_records,
    slice_streaming_student_batch_records,
)
from v5vc.streaming_student.checkpoint_init import (
    load_streaming_student_init_checkpoint,
)
from v5vc.streaming_student.losses import (
    apply_teacher_supervision_weight_schedule,
    compute_streaming_student_teacher_supervision_loss,
    resolve_semantic_supervision_config,
    resolve_teacher_supervision_weight_schedule,
    resolve_teacher_supervision_weights,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold
from v5vc.streaming_student.pitch_provider import (
    build_stage3_pitch_provider_model_inputs_from_batch,
    resolve_stage3_pitch_provider_request,
)
from v5vc.streaming_student.training_freeze import (
    apply_streaming_student_training_freeze,
)


def run_streaming_student_training_loop(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
    validation_batch_size: int,
    num_steps: int,
    validation_interval: int,
    checkpoint_interval: int,
    validation_batches: int,
    validation_mode: str,
    learning_rate: float,
    max_grad_norm: float,
    experiment_id: str,
    use_teacher_confidence: bool,
    loss_weight_overrides_path: Path | None,
    init_checkpoint_path: Path | None,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] training_loop_started "
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
    resolved_init_checkpoint_path = None
    init_checkpoint_step = 0
    if init_checkpoint_path is not None:
        resolved_init_checkpoint_path = init_checkpoint_path.resolve()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    torch.manual_seed(int(config.get("training", {}).get("seed", 20260317)))
    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    base_loss_weights = resolve_teacher_supervision_weights(
        overrides_path=resolved_loss_weight_overrides_path,
    )
    semantic_supervision = resolve_semantic_supervision_config(
        config=config.get("semantic_supervision"),
        overrides_path=resolved_loss_weight_overrides_path,
    )
    loss_weight_schedule = resolve_teacher_supervision_weight_schedule(
        overrides_path=resolved_loss_weight_overrides_path,
    )
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    pitch_provider_request = resolve_stage3_pitch_provider_request(
        dict(config["model"]),
        config_path=config_path,
    )
    init_checkpoint_summary = None
    if resolved_init_checkpoint_path is not None:
        init_payload, init_checkpoint_summary = load_streaming_student_init_checkpoint(
            model=model,
            checkpoint_path=resolved_init_checkpoint_path,
            allow_partial=bool(config.get("training", {}).get("allow_partial_init_checkpoint", False)),
        )
        init_checkpoint_step = int(init_payload.get("step", 0))
    trainable_parameters, training_freeze_summary = apply_streaming_student_training_freeze(
        model=model,
        training_config=config.get("training"),
    )
    optimizer = torch.optim.Adam(trainable_parameters, lr=float(learning_rate))

    step_history: list[dict[str, object]] = []
    validation_history: list[dict[str, object]] = []
    checkpoint_paths: list[str] = []

    effective_num_steps = max(1, int(num_steps))
    effective_validation_interval = max(1, int(validation_interval))
    effective_checkpoint_interval = max(1, int(checkpoint_interval))
    effective_validation_batches = max(1, int(validation_batches))
    effective_validation_mode = str(validation_mode).strip().lower()
    if effective_validation_mode not in {"sampled", "full"}:
        raise ValueError(f"Unsupported validation_mode: {validation_mode}")

    for step_index in range(effective_num_steps):
        current_step = step_index + 1
        step_started_at = datetime.now()
        step_started_perf = perf_counter()
        step_loss_weights = apply_teacher_supervision_weight_schedule(
            base_weights=base_loss_weights,
            schedule=loss_weight_schedule,
            step=current_step,
        )
        train_records = select_streaming_student_batch_records(
            records=records_by_split["target_train"],
            batch_size=batch_size,
            batch_index=step_index,
        )
        train_examples = load_streaming_student_target_examples_from_records(
            train_records,
            frame_length=int(config["model"]["frame_length"]),
            hop_length=int(config["model"]["hop_length"]),
            include_target_acoustic_state=True,
            pitch_provider_request=pitch_provider_request,
        )
        train_batch = collate_streaming_student_batch(
            examples=train_examples,
            conditioning_asset=conditioning_asset,
        )
        train_pitch_provider_inputs = build_stage3_pitch_provider_model_inputs_from_batch(
            train_batch,
            pitch_provider_mode=config["model"].get("pitch_provider_mode"),
            audio_lengths=train_batch["audio_lengths"],
            frame_length=int(config["model"]["frame_length"]),
            hop_length=int(config["model"]["hop_length"]),
        )

        model.train()
        train_outputs = model(
            waveform=train_batch["waveform"],
            lengths=train_batch["audio_lengths"],
            speaker_embedding=train_batch["speaker_embedding"],
            geom_embedding=train_batch["geom_embedding"],
            **train_pitch_provider_inputs,
        )
        train_loss, train_metrics = compute_streaming_student_teacher_supervision_loss(
            outputs=train_outputs,
            batch=train_batch,
            weights=step_loss_weights,
            use_teacher_confidence=use_teacher_confidence,
            semantic_supervision=semantic_supervision,
        )
        optimizer.zero_grad(set_to_none=True)
        train_loss.backward()
        grad_norm = float(clip_grad_norm_(trainable_parameters, float(max_grad_norm)).item())
        optimizer.step()

        step_ended_at = datetime.now()
        step_duration_sec = perf_counter() - step_started_perf
        step_payload = {
            "step": current_step,
            "started_at": step_started_at.isoformat(timespec="seconds"),
            "ended_at": step_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(step_duration_sec, 6),
            "record_ids": list(train_batch["record_ids"]),
            "loss_metrics": train_metrics,
            "effective_loss_weights": {key: round(value, 6) for key, value in step_loss_weights.items()},
            "grad_norm": round(grad_norm, 6),
            "status": "step_completed",
        }
        step_history.append(step_payload)
        (logs_dir / f"{experiment_id}.step{current_step}.json").write_text(
            json.dumps(
                {
                    "experiment_id": experiment_id,
                    "created_at": step_ended_at.isoformat(timespec="seconds"),
                    "step_metrics": step_payload,
                    "status": "step_completed",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            "[stage3] training_loop_step_completed "
            f"step={current_step} ended_at={step_ended_at.isoformat(timespec='seconds')} "
            f"duration_sec={round(step_duration_sec, 6)} loss_total={train_metrics['loss_total']}"
        )

        if current_step % effective_validation_interval == 0 or current_step == effective_num_steps:
            validation_payload = run_validation_pass(
                model=model,
                records=records_by_split["target_validation"],
                conditioning_asset=conditioning_asset,
                base_loss_weights=base_loss_weights,
                semantic_supervision=semantic_supervision,
                loss_weight_schedule=loss_weight_schedule,
                use_teacher_confidence=use_teacher_confidence,
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
                batch_size=validation_batch_size,
                validation_batches=effective_validation_batches,
                validation_mode=effective_validation_mode,
                step=current_step,
                pitch_provider_request=pitch_provider_request,
            )
            validation_history.append(validation_payload)

        if current_step % effective_checkpoint_interval == 0 or current_step == effective_num_steps:
            checkpoint_path = checkpoints_dir / f"{experiment_id}.step{current_step}.pt"
            torch.save(
                {
                    "experiment_id": experiment_id,
                    "step": current_step,
                    "config": config,
                    "config_path": config_path.as_posix(),
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "conditioning_summary": conditioning_asset["summary"],
                    "training": {
                        "batch_size": max(1, int(batch_size)),
                        "validation_batch_size": max(1, int(validation_batch_size)),
                        "num_steps": effective_num_steps,
                        "validation_interval": effective_validation_interval,
                        "checkpoint_interval": effective_checkpoint_interval,
                        "validation_batches": effective_validation_batches,
                        "validation_mode": effective_validation_mode,
                        "learning_rate": float(learning_rate),
                        "max_grad_norm": float(max_grad_norm),
                        "use_teacher_confidence": bool(use_teacher_confidence),
                        "loss_weights": base_loss_weights,
                        "semantic_supervision": semantic_supervision,
                        "loss_weight_schedule": loss_weight_schedule,
                        "loss_weight_overrides_path": (
                            None
                            if resolved_loss_weight_overrides_path is None
                            else resolved_loss_weight_overrides_path.as_posix()
                        ),
                        "training_freeze": training_freeze_summary,
                        "init_checkpoint_path": (
                            None
                            if resolved_init_checkpoint_path is None
                            else resolved_init_checkpoint_path.as_posix()
                        ),
                        "init_checkpoint_step": int(init_checkpoint_step),
                    },
                    "step_metrics": step_payload,
                    "validation_metrics": None if not validation_history else validation_history[-1],
                },
                checkpoint_path,
            )
            checkpoint_paths.append(checkpoint_path.as_posix())

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
            "batch_size": max(1, int(batch_size)),
            "validation_batch_size": max(1, int(validation_batch_size)),
            "num_steps": effective_num_steps,
            "validation_interval": effective_validation_interval,
            "checkpoint_interval": effective_checkpoint_interval,
            "validation_batches": effective_validation_batches,
            "validation_mode": effective_validation_mode,
            "learning_rate": float(learning_rate),
            "max_grad_norm": float(max_grad_norm),
            "use_teacher_confidence": bool(use_teacher_confidence),
            "loss_weights": base_loss_weights,
            "semantic_supervision": semantic_supervision,
            "loss_weight_schedule": loss_weight_schedule,
            "loss_weight_overrides_path": (
                None if resolved_loss_weight_overrides_path is None else resolved_loss_weight_overrides_path.as_posix()
            ),
            "init_checkpoint": init_checkpoint_summary,
            "training_freeze": training_freeze_summary,
            "init_checkpoint_path": (
                None if resolved_init_checkpoint_path is None else resolved_init_checkpoint_path.as_posix()
            ),
            "init_checkpoint_step": int(init_checkpoint_step),
        },
        "step_history": step_history,
        "validation_history": validation_history,
        "artifacts": {
            "checkpoint_paths": checkpoint_paths,
            "latest_checkpoint_path": None if not checkpoint_paths else checkpoint_paths[-1],
            "best_checkpoint": select_best_checkpoint(
                checkpoint_paths=checkpoint_paths,
                validation_history=validation_history,
            ),
        },
        "notes": [
            "This is a minimal multi-step Stage3 training loop scaffold built on top of the new teacher-supervised contract.",
            (
                "Validation currently averages a small sampled subset of target_validation batches for speed; "
                "it is not a full-slice evaluation."
                if effective_validation_mode == "sampled"
                else "Validation now walks the full target_validation slice sequentially inside the training loop."
            ),
            "The purpose is to expose step-wise loss, grad_norm, validation, and checkpoint behavior before adding richer supervision or r_res.",
        ],
        "next_steps": [
            (
                "Decide whether sampled validation should remain the default quick-check mode or whether fuller validation should become the default before larger runs."
                if effective_validation_mode == "sampled"
                else "Use this fuller validation mode to compare future short-horizon runs without relying on a separate checkpoint-eval pass for every checkpoint."
            ),
            "Tune learning rate, loss weights, and teacher confidence usage based on short-horizon trajectories instead of a single step.",
            "Keep hidden distillation and r_res disabled until the base multi-step route is stable.",
        ],
        "status": "training_loop_scaffold_completed",
    }

    summary_json_path = logs_dir / f"{experiment_id}.summary.json"
    summary_md_path = output_dir / f"{experiment_id}.summary.md"
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
    )
    print(
        "[stage3] training_loop_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"latest_checkpoint={summary['artifacts']['latest_checkpoint_path']}"
    )


def run_validation_pass(
    model: torch.nn.Module,
    records: list[dict[str, object]],
    conditioning_asset: dict[str, object],
    base_loss_weights: dict[str, float],
    semantic_supervision: dict[str, object],
    loss_weight_schedule: dict[str, dict[str, float | str | int]],
    use_teacher_confidence: bool,
    frame_length: int,
    hop_length: int,
    batch_size: int,
    validation_batches: int,
    validation_mode: str,
    step: int,
    pitch_provider_request: dict[str, object],
) -> dict[str, object]:
    model.eval()
    batch_metrics: list[dict[str, float]] = []
    sampled_record_ids: list[list[str]] = []
    effective_validation_mode = str(validation_mode).strip().lower()
    if effective_validation_mode == "full":
        batch_count = (len(records) + max(1, int(batch_size)) - 1) // max(1, int(batch_size))
        batch_selector = lambda batch_index: slice_streaming_student_batch_records(
            records=records,
            batch_size=batch_size,
            batch_index=batch_index,
        )
        effective_validation_batches = batch_count
    elif effective_validation_mode == "sampled":
        batch_selector = lambda batch_index: select_streaming_student_batch_records(
            records=records,
            batch_size=batch_size,
            batch_index=(step - 1) * validation_batches + batch_index,
        )
        effective_validation_batches = max(1, int(validation_batches))
    else:
        raise ValueError(f"Unsupported validation_mode: {validation_mode}")
    with torch.no_grad():
        for validation_batch_index in range(effective_validation_batches):
            batch_records = batch_selector(validation_batch_index)
            if not batch_records:
                continue
            examples = load_streaming_student_target_examples_from_records(
                batch_records,
                frame_length=int(frame_length),
                hop_length=int(hop_length),
                include_target_acoustic_state=True,
                pitch_provider_request=pitch_provider_request,
            )
            batch = collate_streaming_student_batch(
                examples=examples,
                conditioning_asset=conditioning_asset,
            )
            pitch_provider_inputs = build_stage3_pitch_provider_model_inputs_from_batch(
                batch,
                pitch_provider_mode=model.frontend.pitch_provider_mode,
                audio_lengths=batch["audio_lengths"],
                frame_length=int(model.frontend.frame_length),
                hop_length=int(model.frontend.hop_length),
            )
            outputs = model(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
                speaker_embedding=batch["speaker_embedding"],
                geom_embedding=batch["geom_embedding"],
                **pitch_provider_inputs,
            )
            effective_loss_weights = apply_teacher_supervision_weight_schedule(
                base_weights=base_loss_weights,
                schedule=loss_weight_schedule,
                step=step,
            )
            _loss, metrics = compute_streaming_student_teacher_supervision_loss(
                outputs=outputs,
                batch=batch,
                weights=effective_loss_weights,
                use_teacher_confidence=use_teacher_confidence,
                semantic_supervision=semantic_supervision,
            )
            batch_metrics.append(metrics)
            sampled_record_ids.append(list(batch["record_ids"]))
    averaged_metrics = average_metric_dicts(batch_metrics)
    return {
        "step": int(step),
        "validation_mode": effective_validation_mode,
        "validation_batches": int(effective_validation_batches),
        "record_count": len(records),
        "effective_loss_weights": {
            key: round(value, 6)
            for key, value in apply_teacher_supervision_weight_schedule(
                base_weights=base_loss_weights,
                schedule=loss_weight_schedule,
                step=step,
            ).items()
        },
        "sampled_record_ids": sampled_record_ids,
        "loss_metrics": averaged_metrics,
    }


def average_metric_dicts(
    metrics_list: list[dict[str, float | bool | str]],
) -> dict[str, float | bool | str | list[str]]:
    if not metrics_list:
        return {}
    keys = metrics_list[0].keys()
    averaged: dict[str, float | bool | str | list[str]] = {}
    for key in keys:
        first_value = metrics_list[0][key]
        if isinstance(first_value, bool):
            averaged[key] = bool(all(bool(metrics[key]) for metrics in metrics_list))
            continue
        if isinstance(first_value, (int, float)):
            averaged[key] = round(
                sum(float(metrics[key]) for metrics in metrics_list) / len(metrics_list),
                6,
            )
            continue
        unique_values = sorted({str(metrics[key]) for metrics in metrics_list})
        averaged[key] = unique_values[0] if len(unique_values) == 1 else unique_values
    return averaged


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Training Loop Scaffold",
        "",
        f"- experiment_id: {summary['experiment_id']}",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        "",
        "## Step History",
    ]
    for step_payload in summary["step_history"]:
        lines.append(
            f"- step={step_payload['step']} loss_total={step_payload['loss_metrics']['loss_total']} "
            f"grad_norm={step_payload['grad_norm']} "
            f"effective_loss_weights={json.dumps(step_payload['effective_loss_weights'], ensure_ascii=False)} "
            f"record_ids={step_payload['record_ids']}"
        )
    lines.extend(["", "## Validation History"])
    for validation_payload in summary["validation_history"]:
        lines.append(
            f"- step={validation_payload['step']} "
            f"loss_total={validation_payload['loss_metrics'].get('loss_total')} "
            f"validation_mode={validation_payload['validation_mode']} "
            f"validation_batches={validation_payload['validation_batches']} "
            f"effective_loss_weights={json.dumps(validation_payload.get('effective_loss_weights', {}), ensure_ascii=False)} "
            f"sampled_record_ids={validation_payload['sampled_record_ids']}"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            f"- checkpoint_paths: {summary['artifacts']['checkpoint_paths']}",
            f"- latest_checkpoint_path: {summary['artifacts']['latest_checkpoint_path']}",
            f"- best_checkpoint: {json.dumps(summary['artifacts']['best_checkpoint'], ensure_ascii=False)}",
            "",
            "## Notes",
        ]
    )
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Next Steps"])
    for item in summary["next_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def select_best_checkpoint(
    checkpoint_paths: list[str],
    validation_history: list[dict[str, object]],
) -> dict[str, object] | None:
    if not checkpoint_paths or not validation_history:
        return None
    checkpoint_by_step: dict[int, str] = {}
    for checkpoint_path in checkpoint_paths:
        name = Path(checkpoint_path).stem
        if ".step" not in name:
            continue
        try:
            step = int(name.rsplit(".step", 1)[1])
        except ValueError:
            continue
        checkpoint_by_step[step] = checkpoint_path
    best_payload: dict[str, object] | None = None
    for validation_payload in validation_history:
        step = int(validation_payload["step"])
        checkpoint_path = checkpoint_by_step.get(step)
        if checkpoint_path is None:
            continue
        loss_total = float(validation_payload.get("loss_metrics", {}).get("loss_total", float("inf")))
        candidate = {
            "selection_rule": "min_validation_loss_total_over_recorded_checkpoints",
            "step": step,
            "validation_mode": str(validation_payload.get("validation_mode", "unknown")),
            "loss_total": round(loss_total, 6),
            "checkpoint_path": checkpoint_path,
        }
        if best_payload is None or float(candidate["loss_total"]) < float(best_payload["loss_total"]):
            best_payload = candidate
    return best_payload
