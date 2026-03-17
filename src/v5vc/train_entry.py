from __future__ import annotations

from copy import deepcopy
import json
import random
from datetime import datetime
from pathlib import Path
from time import perf_counter

import torch
from torch.nn.utils import clip_grad_norm_

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    TEXT_FEATURE_VERSION_LEGACY_V0,
    attach_target_special_supervision,
    attach_target_weak_event_hints,
    build_training_batch_plan,
    build_char_vocab,
    load_source_examples_from_records,
    load_target_special_supervision_map,
    load_target_weak_event_hint_map,
    load_target_examples_from_records,
    collate_source_batch,
    collate_target_batch,
    select_batch_records,
    split_records,
)
from v5vc.offline_mvp.losses import (
    build_special_supervision_sample_weights,
    build_effective_loss_weights,
    build_frame_targets,
    compute_offline_mvp_loss,
    resolve_scalar_weight_schedule,
)
from v5vc.offline_mvp.model import OfflineMVPNoResidualModel


def prepare_offline_mvp_training(
    config_path: Path,
    experiment_id: str,
    output_dir: Path,
    dry_run: bool,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(f"[train] run_started_at={run_started_at.isoformat(timespec='seconds')} experiment_id={experiment_id}")
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = output_dir / "checkpoints"
    logs_dir = output_dir / "logs"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    reproducibility = setup_reproducibility(config["training"])
    manifest_dir = (config_path.parent.parent / config["data"]["manifest_dir"]).resolve()
    split_dir_config = config["data"].get("split_dir")
    split_dir = None if split_dir_config in {None, ""} else (config_path.parent.parent / split_dir_config).resolve()
    enforce_run_stage_requirements(output_dir=output_dir, config=config)
    if not dry_run and not bool(config["training"]["single_step_validation_enabled"]):
        raise ValueError("single_step_validation_enabled is false; non-dry-run execution is blocked.")
    target_manifest_records = load_jsonl(manifest_dir / "target_train.jsonl")
    source_manifest_records = load_jsonl(manifest_dir / "source_train.jsonl")
    (
        target_train_records,
        target_validation_records,
        target_special_eval_records,
        source_train_records,
        source_validation_records,
        split_summary,
    ) = load_training_split(
        manifest_dir=manifest_dir,
        split_dir=split_dir,
        training_config=config["training"],
    )
    vocab = build_char_vocab(target_train_records or target_manifest_records)
    max_audio_sec = float(config["data"]["max_audio_sec"])
    text_feature_version = str(config["data"].get("target_text_feature_version", TEXT_FEATURE_VERSION_LEGACY_V0))
    target_batch_size = int(config["data"]["target_batch_size"])
    source_batch_size = int(config["data"]["source_batch_size"])
    target_weak_event_hints_path = resolve_target_weak_event_hints_path(config_path=config_path, config=config)
    if target_weak_event_hints_path is not None:
        hint_map = load_target_weak_event_hint_map(target_weak_event_hints_path)
        target_train_records = attach_target_weak_event_hints(target_train_records, hint_map)
        target_validation_records = attach_target_weak_event_hints(target_validation_records, hint_map)
        target_special_eval_records = attach_target_weak_event_hints(target_special_eval_records, hint_map)
    target_special_supervision_path = resolve_target_special_supervision_path(config_path=config_path, config=config)
    if target_special_supervision_path is not None:
        supervision_map = load_target_special_supervision_map(target_special_supervision_path)
        target_train_records = attach_target_special_supervision(target_train_records, supervision_map)
        target_validation_records = attach_target_special_supervision(target_validation_records, supervision_map)
        target_special_eval_records = attach_target_special_supervision(target_special_eval_records, supervision_map)
    training_steps = int(config["training"].get("num_steps", 1))
    validation_interval = max(1, int(config["training"].get("validation_interval", training_steps)))
    checkpoint_interval = max(1, int(config["training"].get("checkpoint_interval", training_steps)))
    target_train_batch_plan = build_training_batch_plan(
        records=target_train_records,
        batch_size=target_batch_size,
        num_steps=max(1, training_steps),
        shuffle=reproducibility["shuffle_train_records"],
        seed=reproducibility["target_sampler_seed"],
        sampling_config=resolve_target_sampling_config(config["training"]),
    )
    source_train_batch_plan = build_training_batch_plan(
        records=source_train_records,
        batch_size=source_batch_size,
        num_steps=max(1, training_steps),
        shuffle=reproducibility["shuffle_train_records"],
        seed=reproducibility["source_sampler_seed"],
    )
    train_target_examples = load_target_examples_from_records(
        target_train_batch_plan[0],
        vocab=vocab,
        max_duration_sec=max_audio_sec,
        text_feature_version=text_feature_version,
    )
    train_source_examples = load_source_examples_from_records(
        source_train_batch_plan[0],
        max_duration_sec=max_audio_sec,
    )
    target_batch = collate_target_batch(train_target_examples)
    source_batch = collate_source_batch(train_source_examples)
    model = OfflineMVPNoResidualModel(
        hidden_dim=int(config["model"]["hidden_dim"]),
        z_art_dim=int(config["model"]["z_art_dim"]),
        event_dim=int(config["model"]["event_dim"]),
        acoustic_dim=int(config["model"]["acoustic_dim"]),
        frame_length=int(config["model"]["frame_length"]),
        hop_length=int(config["model"]["hop_length"]),
        text_aux_dim=int(config["model"].get("text_aux_dim", 3)),
        text_aux_head_config=config["model"].get("text_aux_head_config"),
    )
    init_checkpoint_path = resolve_init_checkpoint_path(config_path=config_path, config=config)
    if init_checkpoint_path is not None:
        load_checkpoint_into_model(model=model, checkpoint_path=init_checkpoint_path)
    teacher_runtime = build_teacher_consistency_runtime(config_path=config_path, config=config)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["training"]["learning_rate"]))
    frame_length = int(config["model"]["frame_length"])
    hop_length = int(config["model"]["hop_length"])
    initial_learning_rate = float(config["training"]["learning_rate"])

    dry_run_step = compute_training_step(
        model=model,
        target_batch=target_batch,
        source_batch=source_batch,
        frame_length=frame_length,
        hop_length=hop_length,
        loss_weights=build_effective_loss_weights(
            loss_config=config["losses"],
            step=1,
            total_steps=max(1, training_steps),
        ),
        teacher_consistency=resolve_teacher_consistency_config(
            teacher_runtime=teacher_runtime,
            step=1,
            total_steps=max(1, training_steps),
        ),
    )
    dry_run_learning_rate = resolve_learning_rate(
        training_config=config["training"],
        step=1,
        total_steps=max(1, training_steps),
    )
    target_outputs = dry_run_step["target_outputs"]
    source_outputs = dry_run_step["source_outputs"]
    total_loss = dry_run_step["total_loss"]

    step_history: list[dict[str, object]] = []
    validation_history: list[dict[str, object]] = []
    checkpoint_paths: list[str] = []
    latest_checkpoint_path = None

    if not dry_run:
        for step_index in range(training_steps):
            step_started_at = datetime.now()
            step_started_perf = perf_counter()
            current_step = step_index + 1
            print(
                f"[train] step_started step={current_step} started_at={step_started_at.isoformat(timespec='seconds')}"
            )
            step_target_examples = load_target_examples_from_records(
                target_train_batch_plan[step_index],
                vocab=vocab,
                max_duration_sec=max_audio_sec,
                text_feature_version=text_feature_version,
            )
            step_source_examples = load_source_examples_from_records(
                source_train_batch_plan[step_index],
                max_duration_sec=max_audio_sec,
            )
            step_target_batch = collate_target_batch(step_target_examples)
            step_source_batch = collate_source_batch(step_source_examples)
            step_result = compute_training_step(
                model=model,
                target_batch=step_target_batch,
                source_batch=step_source_batch,
                frame_length=frame_length,
                hop_length=hop_length,
                loss_weights=build_effective_loss_weights(
                    loss_config=config["losses"],
                    step=current_step,
                    total_steps=max(1, training_steps),
                ),
                teacher_consistency=resolve_teacher_consistency_config(
                    teacher_runtime=teacher_runtime,
                    step=current_step,
                    total_steps=max(1, training_steps),
                ),
            )
            current_learning_rate = resolve_learning_rate(
                training_config=config["training"],
                step=current_step,
                total_steps=max(1, training_steps),
            )
            set_optimizer_learning_rate(optimizer=optimizer, learning_rate=current_learning_rate)
            optimizer.zero_grad(set_to_none=True)
            step_result["total_loss"].backward()
            grad_norm = float(
                clip_grad_norm_(model.parameters(), float(config["training"]["max_grad_norm"])).item()
            )
            optimizer.step()
            step_ended_at = datetime.now()
            step_duration_sec = perf_counter() - step_started_perf
            step_payload = {
                "step": current_step,
                "started_at": step_started_at.isoformat(timespec="seconds"),
                "ended_at": step_ended_at.isoformat(timespec="seconds"),
                "duration_sec": round(step_duration_sec, 6),
                "target_record_ids": step_target_batch["record_ids"],
                "source_record_ids": step_source_batch["record_ids"],
                "target": step_result["target_metrics"],
                "source": step_result["source_metrics"],
                "effective_loss_weights": step_result["effective_loss_weights"],
                "effective_teacher_consistency": step_result["effective_teacher_consistency"],
                "effective_learning_rate": current_learning_rate,
                "loss_total": float(step_result["total_loss"].detach().cpu().item()),
                "grad_norm": grad_norm,
            }
            step_history.append(step_payload)
            print(
                "[train] step_completed "
                f"step={current_step} ended_at={step_ended_at.isoformat(timespec='seconds')} "
                f"duration_sec={step_payload['duration_sec']} loss_total={step_payload['loss_total']}"
            )
            step_log_path = logs_dir / f"{experiment_id}.step{current_step}.json"
            step_log_path.write_text(
                json.dumps(
                    {
                        "experiment_id": experiment_id,
                        "created_at": step_ended_at.isoformat(timespec="seconds"),
                        "dry_run": False,
                        "run_stage": config["training"]["run_stage"],
                        "step_metrics": step_payload,
                        "status": "step_completed",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
                newline="\n",
            )
            if current_step % checkpoint_interval == 0 or current_step == training_steps:
                checkpoint_path = checkpoints_dir / f"{experiment_id}.step{current_step}.pt"
                torch.save(
                    {
                        "experiment_id": experiment_id,
                        "model_state_dict": model.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "config": config,
                        "step": current_step,
                    },
                    checkpoint_path,
                )
                latest_checkpoint_path = checkpoint_path
                checkpoint_paths.append(checkpoint_path.as_posix())
            if target_validation_records and source_validation_records:
                if current_step % validation_interval == 0 or current_step == training_steps:
                    validation_history.append(
                        run_validation_step(
                            model=model,
                            target_records=target_validation_records,
                            source_records=source_validation_records,
                            vocab=vocab,
                            max_audio_sec=max_audio_sec,
                            target_batch_size=target_batch_size,
                            source_batch_size=source_batch_size,
                            frame_length=frame_length,
                            hop_length=hop_length,
                            loss_config=config["losses"],
                            training_config=config["training"],
                            total_steps=max(1, training_steps),
                            step=current_step,
                            text_feature_version=text_feature_version,
                        )
                    )
    else:
        dry_run_ended_at = datetime.now()
        dry_run_duration_sec = perf_counter() - run_started_perf
        print(
            "[train] dry_run_completed "
            f"ended_at={dry_run_ended_at.isoformat(timespec='seconds')} duration_sec={round(dry_run_duration_sec, 6)}"
        )
        step_history.append(
            {
                "step": 0,
                "started_at": run_started_at.isoformat(timespec="seconds"),
                "ended_at": dry_run_ended_at.isoformat(timespec="seconds"),
                "duration_sec": round(dry_run_duration_sec, 6),
                "target_record_ids": target_batch["record_ids"],
                "source_record_ids": source_batch["record_ids"],
                "target": dry_run_step["target_metrics"],
                "source": dry_run_step["source_metrics"],
                "effective_loss_weights": dry_run_step["effective_loss_weights"],
                "effective_teacher_consistency": dry_run_step["effective_teacher_consistency"],
                "effective_learning_rate": dry_run_learning_rate,
                "loss_total": float(total_loss.detach().cpu().item()),
                "grad_norm": 0.0,
            }
        )

    run_ended_at = datetime.now()
    total_duration_sec = perf_counter() - run_started_perf
    print(
        "[train] run_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(total_duration_sec, 6)} "
        f"status={'dry_run_ready' if dry_run else 'training_run_completed'}"
    )
    plan = {
        "experiment_id": experiment_id,
        "created_at": run_ended_at.isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "config_path": config_path.as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(total_duration_sec, 6),
        },
        "data": {
            "manifest_dir": manifest_dir.as_posix(),
            "split_dir": None if split_dir is None else split_dir.as_posix(),
            "split_strategy": split_summary["strategy"],
            "target_manifest_count": len(target_manifest_records),
            "source_manifest_count": len(source_manifest_records),
            "target_train_count": len(target_train_records),
            "target_validation_count": len(target_validation_records),
            "target_special_eval_count": len(target_special_eval_records),
            "source_train_count": len(source_train_records),
            "source_validation_count": len(source_validation_records),
            "dry_run_target_count": len(train_target_examples),
            "dry_run_source_count": len(train_source_examples),
            "target_batch_audio_shape": list(target_batch["waveform"].shape),
            "target_batch_token_shape": list(target_batch["token_ids"].shape),
            "target_batch_text_feature_shape": list(target_batch["text_features"].shape),
            "target_text_feature_version": text_feature_version,
            "target_weak_event_hints_path": None if target_weak_event_hints_path is None else target_weak_event_hints_path.as_posix(),
            "target_special_supervision_path": (
                None if target_special_supervision_path is None else target_special_supervision_path.as_posix()
            ),
            "source_batch_audio_shape": list(source_batch["waveform"].shape),
            "vocab_size": len(vocab),
            "target_priority_record_count": count_priority_target_records(
                target_train_records,
                config["training"],
            ),
        },
        "model": config["model"],
        "training": config["training"],
        "execution_guard": {
            "run_stage": config["training"]["run_stage"],
            "requires_small_scale_prerequisite": config["training"]["run_stage"] == "large_scale",
            "prerequisite_experiment_id": config["training"].get("prerequisite_experiment_id"),
            "init_checkpoint_path": None if init_checkpoint_path is None else init_checkpoint_path.as_posix(),
        },
        "reproducibility": reproducibility,
        "split": split_summary,
        "targeted_sampling": summarize_targeted_sampling(
            training_config=config["training"],
            target_train_records=target_train_records,
        ),
        "gates": {
            "requires_r_res_disabled": not bool(config["model"]["r_res_enabled"]),
            "requires_text_for_training": bool(config["model"]["uses_text_in_training"]),
            "requires_text_for_runtime": bool(config["model"]["uses_text_in_runtime"]),
        },
        "dry_run_validation": {
            "source_record_ids": source_batch["record_ids"],
            "target_record_ids": target_batch["record_ids"],
            "forward_shapes": {
                "source_z_art": list(source_outputs["z_art"].shape),
                "source_event_logits": list(source_outputs["event_logits"].shape),
                "source_acoustic": list(source_outputs["acoustic"].shape),
                "source_frame_mask": list(source_outputs["frame_mask"].shape),
                "target_z_art": list(target_outputs["z_art"].shape),
                "target_event_logits": list(target_outputs["event_logits"].shape),
                "target_acoustic": list(target_outputs["acoustic"].shape),
                "target_frame_mask": list(target_outputs["frame_mask"].shape),
            },
        },
        "step_metrics": step_history[-1],
        "validation": {
            "enabled": bool(target_validation_records and source_validation_records),
            "history": validation_history,
        },
        "artifacts": {
            "checkpoint_path": None if latest_checkpoint_path is None else latest_checkpoint_path.as_posix(),
            "checkpoint_paths": checkpoint_paths,
            "logs_dir": logs_dir.as_posix(),
        },
        "training_run": {
            "num_steps": training_steps,
            "completed_steps": 0 if dry_run else len(step_history),
            "validation_interval": validation_interval,
            "checkpoint_interval": checkpoint_interval,
            "initial_learning_rate": initial_learning_rate,
            "learning_rate_schedule": summarize_learning_rate_schedule(config["training"]),
            "teacher_consistency": summarize_teacher_consistency_runtime(teacher_runtime),
            "sampler_mode": resolve_sampler_mode(
                shuffle_train_records=reproducibility["shuffle_train_records"],
                training_config=config["training"],
            ),
            "history": step_history,
        },
        "status": "dry_run_ready" if dry_run else "training_run_completed",
    }

    plan_json_path = output_dir / f"{experiment_id}.train_plan.json"
    plan_md_path = output_dir / f"{experiment_id}.train_plan.md"
    plan_json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    plan_md_path.write_text(build_markdown(plan), encoding="utf-8", newline="\n")
    if dry_run:
        step_log_path = logs_dir / f"{experiment_id}.step0.json"
        step_log_path.write_text(
            json.dumps(
                {
                    "experiment_id": experiment_id,
                    "created_at": run_ended_at.isoformat(timespec="seconds"),
                    "dry_run": True,
                    "run_stage": config["training"]["run_stage"],
                    "timing": plan["timing"],
                    "step_metrics": plan["step_metrics"],
                    "status": plan["status"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
            newline="\n",
        )
    update_experiment_metrics(output_dir=output_dir, experiment_id=experiment_id, plan=plan)


def enforce_run_stage_requirements(output_dir: Path, config: dict[str, object]) -> None:
    training_config = config["training"]
    run_stage = str(training_config.get("run_stage", "small_scale_validation"))
    if run_stage not in {"small_scale_validation", "large_scale"}:
        raise ValueError(f"Unsupported training.run_stage: {run_stage}")
    if run_stage != "large_scale":
        return
    prerequisite_experiment_id = training_config.get("prerequisite_experiment_id")
    if not prerequisite_experiment_id:
        raise ValueError(
            "Large-scale training requires training.prerequisite_experiment_id referencing a successful small-scale run."
        )
    metrics_path = output_dir.parent.parent / "experiments" / f"{prerequisite_experiment_id}.metrics.json"
    if not metrics_path.exists():
        raise ValueError(f"Prerequisite experiment metrics not found: {metrics_path}")
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    training_run_metrics = payload.get("metrics", {}).get("training_run", {})
    if payload.get("status") not in {"single_step_completed", "training_run_completed"}:
        raise ValueError(
            f"Prerequisite experiment status is not successful: {payload.get('status')!r}"
        )
    if training_run_metrics.get("status") not in {"single_step_completed", "training_run_completed"}:
        raise ValueError(
            "Prerequisite experiment does not contain a successful training_run/training_step result."
        )


def setup_reproducibility(training_config: dict[str, object]) -> dict[str, object]:
    seed = int(training_config.get("seed", 20260314))
    shuffle_train_records = bool(training_config.get("shuffle_train_records", False))
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    return {
        "seed": seed,
        "shuffle_train_records": shuffle_train_records,
        "target_sampler_seed": seed,
        "source_sampler_seed": seed + 1,
    }


def load_training_split(
    manifest_dir: Path,
    split_dir: Path | None,
    training_config: dict[str, object],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    if split_dir is not None:
        target_train_records = load_jsonl(split_dir / "target_train.jsonl")
        target_validation_records = load_jsonl(split_dir / "target_validation.jsonl")
        target_special_eval_records = load_jsonl(split_dir / "target_special_eval.jsonl")
        source_train_records = load_jsonl(split_dir / "source_train.jsonl")
        source_validation_records = load_jsonl(split_dir / "source_validation.jsonl")
        split_summary = json.loads((split_dir / "split_summary.json").read_text(encoding="utf-8"))
        return (
            target_train_records,
            target_validation_records,
            target_special_eval_records,
            source_train_records,
            source_validation_records,
            {
                "strategy": "materialized_split",
                "split_dir": split_dir.as_posix(),
                "option_name": split_summary["option_name"],
                "description": split_summary["description"],
                "counts": split_summary["counts"],
            },
        )

    target_manifest_records = load_jsonl(manifest_dir / "target_train.jsonl")
    source_manifest_records = load_jsonl(manifest_dir / "source_train.jsonl")
    target_train_records, target_validation_records = split_records(
        target_manifest_records,
        validation_count=int(training_config.get("target_validation_count", 0)),
    )
    source_train_records, source_validation_records = split_records(
        source_manifest_records,
        validation_count=int(training_config.get("source_validation_count", 0)),
    )
    return (
        target_train_records,
        target_validation_records,
        [],
        source_train_records,
        source_validation_records,
        {
            "strategy": "fallback_tail_split",
            "split_dir": None,
            "option_name": None,
            "description": "fallback to tail split from training config",
            "counts": {
                "target_train": len(target_train_records),
                "target_validation": len(target_validation_records),
                "target_special_eval": 0,
                "source_train": len(source_train_records),
                "source_validation": len(source_validation_records),
            },
        },
    )


def compute_training_step(
    model: OfflineMVPNoResidualModel,
    target_batch: dict[str, torch.Tensor | list[str]],
    source_batch: dict[str, torch.Tensor | list[str]],
    frame_length: int,
    hop_length: int,
    loss_weights: dict[str, object],
    teacher_consistency: dict[str, object] | None = None,
) -> dict[str, object]:
    target_outputs = model(
        waveform=target_batch["waveform"],
        lengths=target_batch["audio_lengths"],
    )
    source_outputs = model(
        waveform=source_batch["waveform"],
        lengths=source_batch["lengths"],
    )
    target_targets = build_frame_targets(
        waveform=target_batch["waveform"],
        lengths=target_batch["audio_lengths"],
        frame_length=frame_length,
        hop_length=hop_length,
        weak_event_hints=target_batch.get("weak_event_hints"),
    )
    source_targets = build_frame_targets(
        waveform=source_batch["waveform"],
        lengths=source_batch["lengths"],
        frame_length=frame_length,
        hop_length=hop_length,
    )
    target_loss, target_metrics = compute_offline_mvp_loss(
        outputs=target_outputs,
        acoustic_target=target_targets["acoustic_target"],
        event_target=target_targets["event_target"],
        frame_mask=target_targets["frame_mask"],
        text_aux_target=target_batch["text_features"],
        texts=target_batch["texts"],
        weights=loss_weights,
        target_special_supervision=target_batch.get("target_special_supervision"),
        weak_event_target=target_targets.get("weak_event_target"),
        weak_event_weight=target_targets.get("weak_event_weight"),
        pause_boundary_strength=target_targets.get("pause_boundary_strength"),
        terminal_boundary_strength=target_targets.get("terminal_boundary_strength"),
        boundary_type_strengths=target_targets.get("boundary_type_strengths"),
        clause_role_strengths=target_targets.get("clause_role_strengths"),
        clause_transition_strengths=target_targets.get("clause_transition_strengths"),
        utterance_structure_strengths=target_targets.get("utterance_structure_strengths"),
    )
    source_loss, source_metrics = compute_offline_mvp_loss(
        outputs=source_outputs,
        acoustic_target=source_targets["acoustic_target"],
        event_target=source_targets["event_target"],
        frame_mask=source_targets["frame_mask"],
        text_aux_target=None,
        texts=None,
        weights=loss_weights,
    )
    teacher_consistency_loss, teacher_consistency_metrics = compute_teacher_consistency_loss(
        student_outputs=target_outputs,
        target_batch=target_batch,
        teacher_consistency=teacher_consistency,
    )
    target_metrics.update(teacher_consistency_metrics)
    return {
        "target_outputs": target_outputs,
        "source_outputs": source_outputs,
        "target_metrics": target_metrics,
        "source_metrics": source_metrics,
        "effective_loss_weights": summarize_effective_loss_weights(loss_weights),
        "effective_teacher_consistency": summarize_effective_teacher_consistency(teacher_consistency),
        "total_loss": target_loss + source_loss + teacher_consistency_loss,
    }


def run_validation_step(
    model: OfflineMVPNoResidualModel,
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
    vocab: dict[str, int],
    max_audio_sec: float,
    target_batch_size: int,
    source_batch_size: int,
    frame_length: int,
    hop_length: int,
    loss_config: dict[str, object],
    training_config: dict[str, object],
    total_steps: int,
    step: int,
    text_feature_version: str,
) -> dict[str, object]:
    target_examples = load_target_examples_from_records(
        select_batch_records(target_records, batch_size=target_batch_size, batch_index=0),
        vocab=vocab,
        max_duration_sec=max_audio_sec,
        text_feature_version=text_feature_version,
    )
    source_examples = load_source_examples_from_records(
        select_batch_records(source_records, batch_size=source_batch_size, batch_index=0),
        max_duration_sec=max_audio_sec,
    )
    target_batch = collate_target_batch(target_examples)
    source_batch = collate_source_batch(source_examples)
    effective_loss_weights = build_effective_loss_weights(
        loss_config=loss_config,
        step=step,
        total_steps=total_steps,
    )
    with torch.no_grad():
        validation_result = compute_training_step(
            model=model,
            target_batch=target_batch,
            source_batch=source_batch,
            frame_length=frame_length,
            hop_length=hop_length,
            loss_weights=effective_loss_weights,
        )
    return {
        "step": step,
        "target_record_ids": target_batch["record_ids"],
        "source_record_ids": source_batch["record_ids"],
        "target": validation_result["target_metrics"],
        "source": validation_result["source_metrics"],
        "effective_loss_weights": validation_result["effective_loss_weights"],
        "effective_learning_rate": resolve_learning_rate(
            training_config=training_config,
            step=step,
            total_steps=total_steps,
        ),
        "loss_total": float(validation_result["total_loss"].detach().cpu().item()),
    }


def summarize_effective_loss_weights(loss_weights: dict[str, object]) -> dict[str, object]:
    summary = {
        "acoustic": float(loss_weights["acoustic"]),
        "event": float(loss_weights["event"]),
        "z_smooth": float(loss_weights["z_smooth"]),
        "text_aux": float(loss_weights["text_aux"]),
        "weak_event": float(loss_weights.get("weak_event", 0.0)),
    }
    if "event_dimension_weights" in loss_weights:
        summary["event_dimension_weights"] = [
            float(value) for value in list(loss_weights["event_dimension_weights"])
        ]
    if "event_boundary_bias" in loss_weights:
        summary["event_boundary_bias"] = loss_weights["event_boundary_bias"]
    if "clause_transition_aux" in loss_weights:
        summary["clause_transition_aux"] = loss_weights["clause_transition_aux"]
    if "structural_clause_transition_aux" in loss_weights:
        summary["structural_clause_transition_aux"] = loss_weights["structural_clause_transition_aux"]
    if "boundary_contrast_aux" in loss_weights:
        summary["boundary_contrast_aux"] = loss_weights["boundary_contrast_aux"]
    if "punctuation_profile_aux" in loss_weights:
        summary["punctuation_profile_aux"] = loss_weights["punctuation_profile_aux"]
    if "structural_clause_profile_aux" in loss_weights:
        summary["structural_clause_profile_aux"] = loss_weights["structural_clause_profile_aux"]
    if "challenge_proxy_profile_aux" in loss_weights:
        summary["challenge_proxy_profile_aux"] = loss_weights["challenge_proxy_profile_aux"]
    if "singleton_sparse_proxy_aux" in loss_weights:
        summary["singleton_sparse_proxy_aux"] = loss_weights["singleton_sparse_proxy_aux"]
    if "z_art_influence_aux" in loss_weights:
        summary["z_art_influence_aux"] = loss_weights["z_art_influence_aux"]
    if "formal_special_clause_shape_aux" in loss_weights:
        summary["formal_special_clause_shape_aux"] = loss_weights["formal_special_clause_shape_aux"]
    if "text_aux_reweight" in loss_weights:
        summary["text_aux_reweight"] = loss_weights["text_aux_reweight"]
    if "text_aux_split" in loss_weights:
        summary["text_aux_split"] = loss_weights["text_aux_split"]
    return summary


def resolve_target_sampling_config(training_config: dict[str, object]) -> dict[str, object] | None:
    raw = training_config.get("targeted_sampling")
    if not isinstance(raw, dict) or not bool(raw.get("enabled", False)):
        return None
    return raw


def count_priority_target_records(
    target_train_records: list[dict[str, object]],
    training_config: dict[str, object],
) -> int:
    sampling_config = resolve_target_sampling_config(training_config)
    if sampling_config is None:
        return 0
    return count_priority_target_records_from_sampling_config(
        target_train_records=target_train_records,
        sampling_config=sampling_config,
    )


def count_priority_target_records_from_sampling_config(
    target_train_records: list[dict[str, object]],
    sampling_config: dict[str, object],
) -> int:
    from v5vc.offline_mvp.data import build_priority_record_groups

    groups = build_priority_record_groups(records=target_train_records, sampling_config=sampling_config)
    return len(groups["priority_union_records"])


def summarize_targeted_sampling(
    training_config: dict[str, object],
    target_train_records: list[dict[str, object]],
) -> dict[str, object]:
    sampling_config = resolve_target_sampling_config(training_config)
    if sampling_config is None:
        return {
            "enabled": False,
            "priority_record_count": 0,
        }
    return {
        "enabled": True,
        "mode": str(sampling_config.get("mode", "priority_interleave")),
        "active_until_step": int(sampling_config.get("active_until_step", 0)),
        "priority_ratio": float(sampling_config.get("priority_ratio", 0.0)),
        "schedule_phases": normalize_target_sampling_schedule_phases(sampling_config),
        "phase_priority_record_counts": summarize_target_sampling_phase_record_counts(
            sampling_config=sampling_config,
            target_train_records=target_train_records,
        ),
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
        "priority_record_count": count_priority_target_records(target_train_records, training_config),
    }


def resolve_sampler_mode(
    shuffle_train_records: bool,
    training_config: dict[str, object],
) -> str:
    if not shuffle_train_records:
        return "sequential_wrap"
    sampling_config = resolve_target_sampling_config(training_config)
    if sampling_config is None:
        return "seeded_shuffle"
    return str(sampling_config.get("mode", "priority_interleave"))


def set_optimizer_learning_rate(
    optimizer: torch.optim.Optimizer,
    learning_rate: float,
) -> None:
    for param_group in optimizer.param_groups:
        param_group["lr"] = learning_rate


def resolve_learning_rate(
    training_config: dict[str, object],
    step: int,
    total_steps: int,
) -> float:
    base_learning_rate = float(training_config["learning_rate"])
    schedule = training_config.get("learning_rate_schedule")
    if not isinstance(schedule, dict) or not bool(schedule.get("enabled", False)):
        return base_learning_rate
    mode = str(schedule.get("mode", "linear_ramp"))
    if mode != "linear_ramp":
        raise ValueError(f"Unsupported training.learning_rate_schedule.mode: {mode}")
    start_step = int(schedule.get("start_step", 1))
    end_step = int(schedule.get("end_step", max(start_step, total_steps)))
    start_learning_rate = float(schedule.get("start_learning_rate", base_learning_rate))
    end_learning_rate = float(schedule.get("end_learning_rate", base_learning_rate))
    if step <= start_step:
        return start_learning_rate
    if step >= end_step:
        return end_learning_rate
    progress = (step - start_step) / max(1, end_step - start_step)
    return start_learning_rate + (end_learning_rate - start_learning_rate) * progress


def summarize_learning_rate_schedule(training_config: dict[str, object]) -> dict[str, object]:
    schedule = training_config.get("learning_rate_schedule")
    if not isinstance(schedule, dict):
        return {"enabled": False}
    return {
        "enabled": bool(schedule.get("enabled", False)),
        "mode": str(schedule.get("mode", "linear_ramp")),
        "start_step": int(schedule.get("start_step", 1)),
        "end_step": int(schedule.get("end_step", 1)),
        "start_learning_rate": float(schedule.get("start_learning_rate", training_config["learning_rate"])),
        "end_learning_rate": float(schedule.get("end_learning_rate", training_config["learning_rate"])),
    }


def normalize_target_sampling_schedule_phases(
    sampling_config: dict[str, object],
) -> list[dict[str, object]]:
    phases = sampling_config.get("schedule_phases")
    if not isinstance(phases, list):
        return []
    normalized: list[dict[str, object]] = []
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        normalized_phase: dict[str, object] = {
            "active_until_step": int(phase.get("active_until_step", 0)),
            "priority_ratio": float(phase.get("priority_ratio", 0.0)),
            "priority_structure_types": list(
                phase.get("priority_structure_types", sampling_config.get("priority_structure_types", []))
            ),
            "exclude_structure_types": list(
                phase.get("exclude_structure_types", sampling_config.get("exclude_structure_types", []))
            ),
            "priority_pool_memberships": list(
                phase.get("priority_pool_memberships", sampling_config.get("priority_pool_memberships", []))
            ),
            "priority_record_ids": list(
                phase.get("priority_record_ids", sampling_config.get("priority_record_ids", []))
            ),
            "exclude_pool_memberships": list(
                phase.get("exclude_pool_memberships", sampling_config.get("exclude_pool_memberships", []))
            ),
        }
        if "min_clause_count" in phase or "min_clause_count" in sampling_config:
            normalized_phase["min_clause_count"] = int(
                phase.get("min_clause_count", sampling_config.get("min_clause_count", 0))
            )
        if "min_pause_boundary_count" in phase or "min_pause_boundary_count" in sampling_config:
            normalized_phase["min_pause_boundary_count"] = int(
                phase.get(
                    "min_pause_boundary_count",
                    sampling_config.get("min_pause_boundary_count", 0),
                )
            )
        if "min_terminal_boundary_count" in phase or "min_terminal_boundary_count" in sampling_config:
            normalized_phase["min_terminal_boundary_count"] = int(
                phase.get(
                    "min_terminal_boundary_count",
                    sampling_config.get("min_terminal_boundary_count", 0),
                )
            )
        if (
            "required_within_special_duration_ceiling" in phase
            or "required_within_special_duration_ceiling" in sampling_config
        ):
            normalized_phase["required_within_special_duration_ceiling"] = bool(
                phase.get(
                    "required_within_special_duration_ceiling",
                    sampling_config.get("required_within_special_duration_ceiling", False),
                )
            )
        if "min_special_proximity_score" in phase or "min_special_proximity_score" in sampling_config:
            normalized_phase["min_special_proximity_score"] = float(
                phase.get(
                    "min_special_proximity_score",
                    sampling_config.get("min_special_proximity_score", 0.0),
                )
            )
        if "max_special_proximity_score" in phase or "max_special_proximity_score" in sampling_config:
            normalized_phase["max_special_proximity_score"] = float(
                phase.get(
                    "max_special_proximity_score",
                    sampling_config.get("max_special_proximity_score", 1.0),
                )
            )
        if "required_final_terminal_types" in phase or "required_final_terminal_types" in sampling_config:
            normalized_phase["required_final_terminal_types"] = list(
                phase.get(
                    "required_final_terminal_types",
                    sampling_config.get("required_final_terminal_types", []),
                )
            )
        if "required_utterance_structure_types" in phase or "required_utterance_structure_types" in sampling_config:
            normalized_phase["required_utterance_structure_types"] = list(
                phase.get(
                    "required_utterance_structure_types",
                    sampling_config.get("required_utterance_structure_types", []),
                )
            )
        secondary_sampling = phase.get("secondary_sampling", sampling_config.get("secondary_sampling"))
        if isinstance(secondary_sampling, dict) and bool(secondary_sampling.get("enabled", False)):
            normalized_phase["secondary_sampling"] = {
                "enabled": True,
                "max_slots": int(secondary_sampling.get("max_slots", 0)),
                "priority_structure_types": list(secondary_sampling.get("priority_structure_types", [])),
                "exclude_structure_types": list(secondary_sampling.get("exclude_structure_types", [])),
                "priority_pool_memberships": list(secondary_sampling.get("priority_pool_memberships", [])),
                "priority_record_ids": list(secondary_sampling.get("priority_record_ids", [])),
                "exclude_pool_memberships": list(secondary_sampling.get("exclude_pool_memberships", [])),
                "exclude_primary_matches": bool(secondary_sampling.get("exclude_primary_matches", False)),
                "min_clause_count": int(secondary_sampling.get("min_clause_count", 0)),
                "min_pause_boundary_count": int(secondary_sampling.get("min_pause_boundary_count", 0)),
                "min_terminal_boundary_count": int(secondary_sampling.get("min_terminal_boundary_count", 0)),
                "required_within_special_duration_ceiling": secondary_sampling.get(
                    "required_within_special_duration_ceiling"
                ),
                "min_special_proximity_score": float(secondary_sampling.get("min_special_proximity_score", 0.0)),
                "max_special_proximity_score": float(secondary_sampling.get("max_special_proximity_score", 1.0)),
                "required_final_terminal_types": list(secondary_sampling.get("required_final_terminal_types", [])),
                "required_utterance_structure_types": list(
                    secondary_sampling.get("required_utterance_structure_types", [])
                ),
            }
        normalized.append(normalized_phase)
    normalized.sort(key=lambda item: int(item["active_until_step"]))
    return normalized


def summarize_target_sampling_phase_record_counts(
    sampling_config: dict[str, object],
    target_train_records: list[dict[str, object]],
) -> list[dict[str, object]]:
    phase_counts: list[dict[str, object]] = []
    raw_phases = sampling_config.get("schedule_phases")
    if not isinstance(raw_phases, list):
        return phase_counts
    for phase in raw_phases:
        if not isinstance(phase, dict):
            continue
        phase_sampling_config = dict(sampling_config)
        phase_sampling_config.pop("schedule_phases", None)
        for key, value in phase.items():
            if key == "active_until_step":
                continue
            phase_sampling_config[key] = value
        phase_counts.append(
            {
                "active_until_step": int(phase.get("active_until_step", 0)),
                "priority_ratio": float(phase.get("priority_ratio", 0.0)),
                "priority_record_count": count_priority_target_records_from_sampling_config(
                    target_train_records=target_train_records,
                    sampling_config=phase_sampling_config,
                ),
            }
        )
    return phase_counts


def resolve_target_weak_event_hints_path(
    config_path: Path,
    config: dict[str, object],
) -> Path | None:
    hint_path_config = config["data"].get("target_weak_event_hints_path")
    if hint_path_config in {None, ""}:
        return None
    return (config_path.parent.parent / hint_path_config).resolve()


def resolve_target_special_supervision_path(
    config_path: Path,
    config: dict[str, object],
) -> Path | None:
    supervision_path_config = config["data"].get("target_special_supervision_path")
    if supervision_path_config in {None, ""}:
        return None
    return (config_path.parent.parent / supervision_path_config).resolve()


def build_markdown(plan: dict[str, object]) -> str:
    return "\n".join(
        [
            "# offline MVP 训练计划",
            "",
            f"- experiment_id: {plan['experiment_id']}",
            f"- dry_run: {plan['dry_run']}",
            f"- config_path: {plan['config_path']}",
            "",
            "## 时间",
            f"- started_at: {plan['timing']['started_at']}",
            f"- ended_at: {plan['timing']['ended_at']}",
            f"- duration_sec: {plan['timing']['duration_sec']}",
            "",
            "## 数据",
            f"- manifest_dir: {plan['data']['manifest_dir']}",
            f"- split_dir: {plan['data']['split_dir']}",
            f"- split_strategy: {plan['data']['split_strategy']}",
            f"- target_manifest_count: {plan['data']['target_manifest_count']}",
            f"- source_manifest_count: {plan['data']['source_manifest_count']}",
            f"- target_train_count: {plan['data']['target_train_count']}",
            f"- target_validation_count: {plan['data']['target_validation_count']}",
            f"- target_special_eval_count: {plan['data']['target_special_eval_count']}",
            f"- source_train_count: {plan['data']['source_train_count']}",
            f"- source_validation_count: {plan['data']['source_validation_count']}",
            f"- dry_run_target_count: {plan['data']['dry_run_target_count']}",
            f"- dry_run_source_count: {plan['data']['dry_run_source_count']}",
            f"- target_batch_audio_shape: {plan['data']['target_batch_audio_shape']}",
            f"- target_batch_token_shape: {plan['data']['target_batch_token_shape']}",
            f"- target_batch_text_feature_shape: {plan['data']['target_batch_text_feature_shape']}",
            f"- target_text_feature_version: {plan['data']['target_text_feature_version']}",
            f"- target_weak_event_hints_path: {plan['data']['target_weak_event_hints_path']}",
            f"- target_special_supervision_path: {plan['data']['target_special_supervision_path']}",
            f"- source_batch_audio_shape: {plan['data']['source_batch_audio_shape']}",
            f"- vocab_size: {plan['data']['vocab_size']}",
            "",
            "## 模型门槛",
            f"- run_stage: {plan['execution_guard']['run_stage']}",
            f"- requires_small_scale_prerequisite: {plan['execution_guard']['requires_small_scale_prerequisite']}",
            f"- prerequisite_experiment_id: {plan['execution_guard']['prerequisite_experiment_id']}",
            f"- init_checkpoint_path: {plan['execution_guard']['init_checkpoint_path']}",
            f"- split_option_name: {plan['split']['option_name']}",
            f"- requires_r_res_disabled: {plan['gates']['requires_r_res_disabled']}",
            f"- requires_text_for_training: {plan['gates']['requires_text_for_training']}",
            f"- requires_text_for_runtime: {plan['gates']['requires_text_for_runtime']}",
            "",
            "## 可复现性",
            f"- seed: {plan['reproducibility']['seed']}",
            f"- shuffle_train_records: {plan['reproducibility']['shuffle_train_records']}",
            f"- target_sampler_seed: {plan['reproducibility']['target_sampler_seed']}",
            f"- source_sampler_seed: {plan['reproducibility']['source_sampler_seed']}",
            "",
            "## Targeted Sampling",
            f"- enabled: {plan['targeted_sampling']['enabled']}",
            f"- priority_record_count: {plan['targeted_sampling']['priority_record_count']}",
            f"- mode: {plan['targeted_sampling'].get('mode')}",
            f"- active_until_step: {plan['targeted_sampling'].get('active_until_step')}",
            f"- priority_ratio: {plan['targeted_sampling'].get('priority_ratio')}",
            f"- schedule_phases: {plan['targeted_sampling'].get('schedule_phases')}",
            f"- phase_priority_record_counts: {plan['targeted_sampling'].get('phase_priority_record_counts')}",
            f"- min_clause_count: {plan['targeted_sampling'].get('min_clause_count')}",
            f"- required_within_special_duration_ceiling: {plan['targeted_sampling'].get('required_within_special_duration_ceiling')}",
            f"- priority_structure_types: {plan['targeted_sampling'].get('priority_structure_types')}",
            f"- min_special_proximity_score: {plan['targeted_sampling'].get('min_special_proximity_score')}",
            f"- max_special_proximity_score: {plan['targeted_sampling'].get('max_special_proximity_score')}",
            f"- required_final_terminal_types: {plan['targeted_sampling'].get('required_final_terminal_types')}",
            f"- required_utterance_structure_types: {plan['targeted_sampling'].get('required_utterance_structure_types')}",
            f"- exclude_structure_types: {plan['targeted_sampling'].get('exclude_structure_types')}",
            f"- priority_pool_memberships: {plan['targeted_sampling'].get('priority_pool_memberships')}",
            f"- priority_record_ids: {plan['targeted_sampling'].get('priority_record_ids')}",
            f"- exclude_pool_memberships: {plan['targeted_sampling'].get('exclude_pool_memberships')}",
            "",
            "## dry-run 前向形状",
            f"- source_z_art: {plan['dry_run_validation']['forward_shapes']['source_z_art']}",
            f"- source_event_logits: {plan['dry_run_validation']['forward_shapes']['source_event_logits']}",
            f"- source_acoustic: {plan['dry_run_validation']['forward_shapes']['source_acoustic']}",
            f"- source_frame_mask: {plan['dry_run_validation']['forward_shapes']['source_frame_mask']}",
            f"- target_z_art: {plan['dry_run_validation']['forward_shapes']['target_z_art']}",
            f"- target_event_logits: {plan['dry_run_validation']['forward_shapes']['target_event_logits']}",
            f"- target_acoustic: {plan['dry_run_validation']['forward_shapes']['target_acoustic']}",
            f"- target_frame_mask: {plan['dry_run_validation']['forward_shapes']['target_frame_mask']}",
            "",
            "## 训练摘要",
            f"- num_steps: {plan['training_run']['num_steps']}",
            f"- completed_steps: {plan['training_run']['completed_steps']}",
            f"- validation_interval: {plan['training_run']['validation_interval']}",
            f"- checkpoint_interval: {plan['training_run']['checkpoint_interval']}",
            f"- initial_learning_rate: {plan['training_run']['initial_learning_rate']}",
            f"- learning_rate_schedule: {plan['training_run']['learning_rate_schedule']}",
            f"- teacher_consistency: {plan['training_run']['teacher_consistency']}",
            f"- sampler_mode: {plan['training_run']['sampler_mode']}",
            "",
            "## 最新 step 指标",
            f"- step: {plan['step_metrics']['step']}",
            f"- effective_learning_rate: {plan['step_metrics']['effective_learning_rate']}",
            f"- loss_total: {plan['step_metrics']['loss_total']}",
            f"- target.loss_total: {plan['step_metrics']['target']['loss_total']}",
            f"- source.loss_total: {plan['step_metrics']['source']['loss_total']}",
            f"- grad_norm: {plan['step_metrics']['grad_norm']}",
            f"- checkpoint_path: {plan['artifacts']['checkpoint_path']}",
            f"- validation_enabled: {plan['validation']['enabled']}",
            f"- validation_runs: {len(plan['validation']['history'])}",
            "",
            "## 状态",
            f"- status: {plan['status']}",
        ]
    ) + "\n"


def resolve_experiment_metrics_path(experiments_dir: Path, experiment_id: str) -> Path | None:
    direct_path = experiments_dir / f"{experiment_id}.metrics.json"
    if direct_path.exists():
        return direct_path
    matches = sorted(experiments_dir.glob(f"{experiment_id}-*.metrics.json"))
    if len(matches) == 1:
        return matches[0]
    return None


def update_experiment_metrics(output_dir: Path, experiment_id: str, plan: dict[str, object]) -> None:
    experiments_dir = output_dir.parent.parent / "experiments"
    metrics_path = resolve_experiment_metrics_path(experiments_dir=experiments_dir, experiment_id=experiment_id)
    if metrics_path is None:
        return
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    payload.setdefault("metrics", {})
    payload["metrics"]["training_run"] = {
        "dry_run": plan["dry_run"],
        "timing": plan["timing"],
        "execution_guard": plan["execution_guard"],
        "split": plan["split"],
        "training_run": plan["training_run"],
        "step_metrics": plan["step_metrics"],
        "validation": plan["validation"],
        "status": plan["status"],
        "artifacts": plan["artifacts"],
    }
    payload["status"] = plan["status"]
    metrics_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )


def resolve_init_checkpoint_path(
    config_path: Path,
    config: dict[str, object],
) -> Path | None:
    raw = config["training"].get("init_checkpoint_path")
    if raw in {None, ""}:
        return None
    return (config_path.parent.parent / str(raw)).resolve()


def instantiate_offline_mvp_model(model_config: dict[str, object]) -> OfflineMVPNoResidualModel:
    return OfflineMVPNoResidualModel(
        hidden_dim=int(model_config["hidden_dim"]),
        z_art_dim=int(model_config["z_art_dim"]),
        event_dim=int(model_config["event_dim"]),
        acoustic_dim=int(model_config["acoustic_dim"]),
        frame_length=int(model_config["frame_length"]),
        hop_length=int(model_config["hop_length"]),
        text_aux_dim=int(model_config.get("text_aux_dim", 3)),
        text_aux_head_config=model_config.get("text_aux_head_config"),
    )


def load_checkpoint_into_model(
    model: OfflineMVPNoResidualModel,
    checkpoint_path: Path,
) -> dict[str, object]:
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    model.load_state_dict(payload["model_state_dict"])
    return payload


def build_teacher_consistency_runtime(
    config_path: Path,
    config: dict[str, object],
) -> dict[str, object] | None:
    raw = config["training"].get("teacher_consistency")
    if not isinstance(raw, dict) or not bool(raw.get("enabled", False)):
        return None
    teacher_checkpoint_paths = resolve_teacher_checkpoint_paths(
        config_path=config_path,
        teacher_consistency_config=raw,
    )
    if not teacher_checkpoint_paths:
        raise ValueError("training.teacher_consistency.teacher_checkpoint_path is required when enabled.")
    teacher_models: dict[str, OfflineMVPNoResidualModel] = {}
    for teacher_checkpoint_path in teacher_checkpoint_paths:
        payload = torch.load(teacher_checkpoint_path, map_location="cpu", weights_only=False)
        teacher_config = payload.get("config")
        if not isinstance(teacher_config, dict) or not isinstance(teacher_config.get("model"), dict):
            raise ValueError("Teacher checkpoint does not contain a valid config.model payload.")
        teacher_model = instantiate_offline_mvp_model(teacher_config["model"])
        teacher_model.load_state_dict(payload["model_state_dict"])
        teacher_model.eval()
        for parameter in teacher_model.parameters():
            parameter.requires_grad_(False)
        teacher_models[teacher_checkpoint_path.as_posix()] = teacher_model
    return {
        "config": deepcopy(raw),
        "teacher_checkpoint_paths": [path.as_posix() for path in teacher_checkpoint_paths],
        "teacher_models": teacher_models,
        "workspace_root": config_path.parent.parent.resolve().as_posix(),
    }


def resolve_teacher_consistency_config(
    teacher_runtime: dict[str, object] | None,
    step: int,
    total_steps: int,
) -> dict[str, object] | None:
    if teacher_runtime is None:
        return None
    config = resolve_teacher_consistency_phase_config(
        raw_config=teacher_runtime["config"],
        step=step,
    )
    base_weight = float(config.get("weight", 0.0))
    config["weight"] = resolve_scalar_weight_schedule(
        schedule=config.get("weight_schedule"),
        base_weight=base_weight,
        step=step,
        total_steps=total_steps,
        field_name="training.teacher_consistency.weight_schedule",
    )
    config["event_weight"] = float(config.get("event_weight", 1.0))
    config["z_art_weight"] = float(config.get("z_art_weight", 1.0))
    config["acoustic_weight"] = float(config.get("acoustic_weight", 0.0))
    config["fused_hidden_weight"] = float(config.get("fused_hidden_weight", 0.0))
    config["pool_memberships"] = [str(value) for value in list(config.get("pool_memberships", [])) if str(value)]
    config["teacher_checkpoint_path"] = resolve_active_teacher_checkpoint_path(
        raw_config=config,
        teacher_runtime=teacher_runtime,
    )
    config["teacher_model"] = teacher_runtime["teacher_models"][config["teacher_checkpoint_path"]]
    config["min_special_proximity_score"] = float(config.get("min_special_proximity_score", 0.0))
    config["max_special_proximity_score"] = float(config.get("max_special_proximity_score", 1.0))
    config["required_final_terminal_types"] = [
        str(value)
        for value in list(config.get("required_final_terminal_types", []))
        if str(value)
    ]
    config["required_utterance_structure_types"] = [
        str(value)
        for value in list(config.get("required_utterance_structure_types", []))
        if str(value)
    ]
    config["min_clause_count"] = int(config.get("min_clause_count", 0))
    config["min_pause_boundary_count"] = int(config.get("min_pause_boundary_count", 0))
    config["min_terminal_boundary_count"] = int(config.get("min_terminal_boundary_count", 0))
    if "required_within_special_duration_ceiling" in config:
        config["required_within_special_duration_ceiling"] = bool(
            config.get("required_within_special_duration_ceiling", False)
        )
    config["base_sample_weight"] = float(config.get("base_sample_weight", 1.0))
    config["proximity_weight_scale"] = float(config.get("proximity_weight_scale", 0.0))
    config["final_terminal_type_weight_overrides"] = {
        str(key): float(value)
        for key, value in dict(config.get("final_terminal_type_weight_overrides", {})).items()
        if str(key)
    }
    config["utterance_structure_type_weight_overrides"] = {
        str(key): float(value)
        for key, value in dict(config.get("utterance_structure_type_weight_overrides", {})).items()
        if str(key)
    }
    return config


def resolve_teacher_checkpoint_paths(
    config_path: Path,
    teacher_consistency_config: dict[str, object],
) -> list[Path]:
    checkpoint_paths: list[Path] = []
    raw_paths: list[object] = [teacher_consistency_config.get("teacher_checkpoint_path")]
    schedule_phases = teacher_consistency_config.get("schedule_phases")
    if isinstance(schedule_phases, list):
        for phase in schedule_phases:
            if isinstance(phase, dict):
                raw_paths.append(phase.get("teacher_checkpoint_path"))
    for raw_path in raw_paths:
        if raw_path in {None, ""}:
            continue
        resolved_path = (config_path.parent.parent / str(raw_path)).resolve()
        if resolved_path not in checkpoint_paths:
            checkpoint_paths.append(resolved_path)
    return checkpoint_paths


def resolve_active_teacher_checkpoint_path(
    raw_config: dict[str, object],
    teacher_runtime: dict[str, object],
) -> str:
    teacher_checkpoint_raw = raw_config.get("teacher_checkpoint_path")
    if teacher_checkpoint_raw in {None, ""}:
        available_paths = list(teacher_runtime["teacher_checkpoint_paths"])
        if not available_paths:
            raise ValueError("Teacher consistency requires at least one resolved teacher checkpoint.")
        return str(available_paths[0])
    resolved_path = (Path(str(teacher_runtime["workspace_root"])) / str(teacher_checkpoint_raw)).resolve().as_posix()
    if resolved_path in teacher_runtime["teacher_models"]:
        return resolved_path
    raise ValueError(f"Resolved teacher checkpoint not loaded: {resolved_path}")


def resolve_teacher_consistency_phase_config(
    raw_config: dict[str, object],
    step: int,
) -> dict[str, object]:
    config = deepcopy(raw_config)
    raw_phases = config.pop("schedule_phases", None)
    if not isinstance(raw_phases, list):
        return config
    selected_phase: dict[str, object] | None = None
    normalized_phases = sorted(
        (phase for phase in raw_phases if isinstance(phase, dict)),
        key=lambda item: int(item.get("active_until_step", 0)),
    )
    for phase in normalized_phases:
        if step <= int(phase.get("active_until_step", 0)):
            selected_phase = phase
            break
    if selected_phase is None:
        return config
    for key, value in selected_phase.items():
        if key == "active_until_step":
            continue
        config[key] = deepcopy(value)
    return config


def normalize_teacher_consistency_schedule_phases(
    raw_config: dict[str, object],
) -> list[dict[str, object]]:
    raw_phases = raw_config.get("schedule_phases")
    if not isinstance(raw_phases, list):
        return []
    normalized: list[dict[str, object]] = []
    for phase in raw_phases:
        if not isinstance(phase, dict):
            continue
        phase_config = resolve_teacher_consistency_phase_config(
            raw_config={**deepcopy(raw_config), "schedule_phases": [phase]},
            step=int(phase.get("active_until_step", 0)),
        )
        normalized_phase: dict[str, object] = {
            "active_until_step": int(phase.get("active_until_step", 0)),
            "weight": float(phase_config.get("weight", 0.0)),
            "event_weight": float(phase_config.get("event_weight", 1.0)),
            "z_art_weight": float(phase_config.get("z_art_weight", 1.0)),
            "acoustic_weight": float(phase_config.get("acoustic_weight", 0.0)),
            "fused_hidden_weight": float(phase_config.get("fused_hidden_weight", 0.0)),
            "pool_memberships": [str(value) for value in list(phase_config.get("pool_memberships", [])) if str(value)],
            "teacher_checkpoint_path": str(phase_config.get("teacher_checkpoint_path", "")),
            "min_clause_count": int(phase_config.get("min_clause_count", 0)),
            "min_pause_boundary_count": int(phase_config.get("min_pause_boundary_count", 0)),
            "min_terminal_boundary_count": int(phase_config.get("min_terminal_boundary_count", 0)),
            "required_within_special_duration_ceiling": phase_config.get(
                "required_within_special_duration_ceiling"
            ),
            "min_special_proximity_score": float(phase_config.get("min_special_proximity_score", 0.0)),
            "max_special_proximity_score": float(phase_config.get("max_special_proximity_score", 1.0)),
            "required_final_terminal_types": list(phase_config.get("required_final_terminal_types", [])),
            "required_utterance_structure_types": list(
                phase_config.get("required_utterance_structure_types", [])
            ),
            "base_sample_weight": float(phase_config.get("base_sample_weight", 1.0)),
            "proximity_weight_scale": float(phase_config.get("proximity_weight_scale", 0.0)),
            "final_terminal_type_weight_overrides": {
                str(key): float(value)
                for key, value in dict(phase_config.get("final_terminal_type_weight_overrides", {})).items()
                if str(key)
            },
            "utterance_structure_type_weight_overrides": {
                str(key): float(value)
                for key, value in dict(phase_config.get("utterance_structure_type_weight_overrides", {})).items()
                if str(key)
            },
        }
        weight_schedule = phase_config.get("weight_schedule")
        if isinstance(weight_schedule, dict):
            normalized_phase["weight_schedule"] = deepcopy(weight_schedule)
        normalized.append(normalized_phase)
    normalized.sort(key=lambda item: int(item["active_until_step"]))
    return normalized


def summarize_teacher_consistency_runtime(
    teacher_runtime: dict[str, object] | None,
) -> dict[str, object] | None:
    if teacher_runtime is None:
        return None
    config = deepcopy(teacher_runtime["config"])
    config["teacher_checkpoint_paths"] = list(teacher_runtime["teacher_checkpoint_paths"])
    config["schedule_phases"] = normalize_teacher_consistency_schedule_phases(teacher_runtime["config"])
    return config


def summarize_effective_teacher_consistency(
    teacher_consistency: dict[str, object] | None,
) -> dict[str, object] | None:
    if teacher_consistency is None:
        return None
    return {
        "enabled": bool(teacher_consistency.get("enabled", False)),
        "teacher_checkpoint_path": str(teacher_consistency.get("teacher_checkpoint_path")),
        "weight": float(teacher_consistency.get("weight", 0.0)),
        "event_weight": float(teacher_consistency.get("event_weight", 1.0)),
        "z_art_weight": float(teacher_consistency.get("z_art_weight", 1.0)),
        "acoustic_weight": float(teacher_consistency.get("acoustic_weight", 0.0)),
        "fused_hidden_weight": float(teacher_consistency.get("fused_hidden_weight", 0.0)),
        "pool_memberships": list(teacher_consistency.get("pool_memberships", [])),
        "min_clause_count": int(teacher_consistency.get("min_clause_count", 0)),
        "min_pause_boundary_count": int(teacher_consistency.get("min_pause_boundary_count", 0)),
        "min_terminal_boundary_count": int(teacher_consistency.get("min_terminal_boundary_count", 0)),
        "required_within_special_duration_ceiling": teacher_consistency.get(
            "required_within_special_duration_ceiling"
        ),
        "min_special_proximity_score": float(teacher_consistency.get("min_special_proximity_score", 0.0)),
        "max_special_proximity_score": float(teacher_consistency.get("max_special_proximity_score", 1.0)),
        "required_final_terminal_types": list(teacher_consistency.get("required_final_terminal_types", [])),
        "required_utterance_structure_types": list(
            teacher_consistency.get("required_utterance_structure_types", [])
        ),
        "base_sample_weight": float(teacher_consistency.get("base_sample_weight", 1.0)),
        "proximity_weight_scale": float(teacher_consistency.get("proximity_weight_scale", 0.0)),
        "final_terminal_type_weight_overrides": {
            str(key): float(value)
            for key, value in dict(teacher_consistency.get("final_terminal_type_weight_overrides", {})).items()
            if str(key)
        },
        "utterance_structure_type_weight_overrides": {
            str(key): float(value)
            for key, value in dict(teacher_consistency.get("utterance_structure_type_weight_overrides", {})).items()
            if str(key)
        },
    }


def compute_teacher_consistency_loss(
    student_outputs: dict[str, torch.Tensor],
    target_batch: dict[str, torch.Tensor | list[str]],
    teacher_consistency: dict[str, object] | None,
) -> tuple[torch.Tensor, dict[str, float]]:
    student_event_logits = student_outputs["event_logits"]
    zero = torch.zeros((), device=student_event_logits.device, dtype=student_event_logits.dtype)
    metrics = {
        "loss_teacher_consistency": float(zero.detach().cpu().item()),
        "loss_teacher_event_consistency": float(zero.detach().cpu().item()),
        "loss_teacher_z_art_consistency": float(zero.detach().cpu().item()),
        "loss_teacher_acoustic_consistency": float(zero.detach().cpu().item()),
        "loss_teacher_fused_hidden_consistency": float(zero.detach().cpu().item()),
    }
    if teacher_consistency is None or float(teacher_consistency.get("weight", 0.0)) <= 0.0:
        return zero, metrics
    teacher_model = teacher_consistency.get("teacher_model")
    if not isinstance(teacher_model, OfflineMVPNoResidualModel):
        raise ValueError("Teacher consistency requires a resolved teacher_model.")
    with torch.no_grad():
        teacher_outputs = teacher_model(
            waveform=target_batch["waveform"],
            lengths=target_batch["audio_lengths"],
        )
    frame_mask = student_outputs["frame_mask"]
    sample_weight = build_special_supervision_sample_weights(
        target_special_supervision=target_batch.get("target_special_supervision"),
        batch_size=int(frame_mask.shape[0]),
        pool_memberships=list(teacher_consistency.get("pool_memberships", [])),
        device=frame_mask.device,
        min_special_proximity_score=float(teacher_consistency.get("min_special_proximity_score", 0.0)),
        max_special_proximity_score=float(teacher_consistency.get("max_special_proximity_score", 1.0)),
        required_final_terminal_types=list(teacher_consistency.get("required_final_terminal_types", [])),
        required_utterance_structure_types=list(
            teacher_consistency.get("required_utterance_structure_types", [])
        ),
        min_clause_count=int(teacher_consistency.get("min_clause_count", 0)),
        min_pause_boundary_count=int(teacher_consistency.get("min_pause_boundary_count", 0)),
        min_terminal_boundary_count=int(teacher_consistency.get("min_terminal_boundary_count", 0)),
        required_within_special_duration_ceiling=teacher_consistency.get(
            "required_within_special_duration_ceiling"
        ),
        base_sample_weight=float(teacher_consistency.get("base_sample_weight", 1.0)),
        proximity_weight_scale=float(teacher_consistency.get("proximity_weight_scale", 0.0)),
        final_terminal_type_weight_overrides=dict(
            teacher_consistency.get("final_terminal_type_weight_overrides", {})
        ),
        utterance_structure_type_weight_overrides=dict(
            teacher_consistency.get("utterance_structure_type_weight_overrides", {})
        ),
    )
    if float(sample_weight.sum().item()) <= 0.0:
        return zero, metrics
    event_loss = compute_samplewise_masked_mse(
        student=student_outputs["event_logits"],
        teacher=teacher_outputs["event_logits"],
        frame_mask=frame_mask,
        sample_weight=sample_weight,
    )
    z_art_loss = compute_samplewise_masked_mse(
        student=student_outputs["z_art"],
        teacher=teacher_outputs["z_art"],
        frame_mask=frame_mask,
        sample_weight=sample_weight,
    )
    acoustic_loss = compute_samplewise_masked_mse(
        student=student_outputs["acoustic"],
        teacher=teacher_outputs["acoustic"],
        frame_mask=frame_mask,
        sample_weight=sample_weight,
    )
    fused_hidden_loss = compute_samplewise_masked_mse(
        student=student_outputs["fused_hidden"],
        teacher=teacher_outputs["fused_hidden"],
        frame_mask=frame_mask,
        sample_weight=sample_weight,
    )
    total_loss = (
        event_loss * float(teacher_consistency.get("event_weight", 1.0))
        + z_art_loss * float(teacher_consistency.get("z_art_weight", 1.0))
        + acoustic_loss * float(teacher_consistency.get("acoustic_weight", 0.0))
        + fused_hidden_loss * float(teacher_consistency.get("fused_hidden_weight", 0.0))
    )
    weighted_loss = total_loss * float(teacher_consistency.get("weight", 0.0))
    metrics["loss_teacher_consistency"] = float(total_loss.detach().cpu().item())
    metrics["loss_teacher_event_consistency"] = float(event_loss.detach().cpu().item())
    metrics["loss_teacher_z_art_consistency"] = float(z_art_loss.detach().cpu().item())
    metrics["loss_teacher_acoustic_consistency"] = float(acoustic_loss.detach().cpu().item())
    metrics["loss_teacher_fused_hidden_consistency"] = float(fused_hidden_loss.detach().cpu().item())
    return weighted_loss, metrics


def compute_samplewise_masked_mse(
    student: torch.Tensor,
    teacher: torch.Tensor,
    frame_mask: torch.Tensor,
    sample_weight: torch.Tensor,
) -> torch.Tensor:
    frame_weights = frame_mask.to(student.dtype).unsqueeze(-1)
    per_frame = ((student - teacher) ** 2) * frame_weights
    per_sample = per_frame.sum(dim=(1, 2)) / frame_weights.sum(dim=(1, 2)).clamp_min(1.0)
    effective_weight = sample_weight.to(student.dtype).clamp_min(0.0)
    active_weight = effective_weight.sum().clamp_min(1.0)
    return (per_sample * effective_weight).sum() / active_weight
