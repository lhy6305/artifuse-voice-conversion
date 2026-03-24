from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import infer_target_event_semantic_sidecar_path
from v5vc.streaming_student.model import StreamingStudentScaffold
from v5vc.train_entry import load_training_split, resolve_experiment_metrics_path


def prepare_streaming_student_stage(
    config_path: Path,
    output_dir: Path,
    experiment_id: str = "streaming_student_stage_scaffold",
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage3] scaffold_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} experiment_id={experiment_id}"
    )
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_streaming_student_config(config=config)

    training_config = dict(config["training"])
    data_config = dict(config["data"])
    model_config = dict(config["model"])
    planning_config = dict(config.get("planning", {}))

    manifest_dir = (config_path.parent.parent / data_config["manifest_dir"]).resolve()
    split_dir_raw = data_config.get("split_dir")
    split_dir = None if split_dir_raw in {None, ""} else (config_path.parent.parent / str(split_dir_raw)).resolve()
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
        training_config={
            "target_validation_count": int(data_config.get("target_validation_count", 0)),
            "source_validation_count": int(data_config.get("source_validation_count", 0)),
        },
    )

    target_weak_event_hints_path = resolve_optional_path(config_path=config_path, raw_value=data_config.get("target_weak_event_hints_path"))
    target_special_supervision_path = resolve_optional_path(
        config_path=config_path,
        raw_value=data_config.get("target_special_supervision_path"),
    )
    target_event_semantic_sidecar_path = resolve_target_event_semantic_sidecar_path(
        config_path=config_path,
        data_config=data_config,
    )
    if target_weak_event_hints_path is not None and not target_weak_event_hints_path.exists():
        raise ValueError(f"target_weak_event_hints_path not found: {target_weak_event_hints_path}")
    if target_special_supervision_path is not None and not target_special_supervision_path.exists():
        raise ValueError(f"target_special_supervision_path not found: {target_special_supervision_path}")
    if target_event_semantic_sidecar_path is not None and not target_event_semantic_sidecar_path.exists():
        raise ValueError(f"target_event_semantic_sidecar_path not found: {target_event_semantic_sidecar_path}")

    seed = int(training_config.get("seed", 20260317))
    torch.manual_seed(seed)
    synthetic_batch_size = int(planning_config.get("synthetic_batch_size", 2))
    synthetic_waveform_length = int(planning_config.get("synthetic_waveform_length", 6400))
    waveform = torch.randn(synthetic_batch_size, synthetic_waveform_length)
    lengths = torch.full((synthetic_batch_size,), synthetic_waveform_length, dtype=torch.long)
    speaker_embedding = torch.randn(synthetic_batch_size, int(model_config["speaker_embed_dim"]))
    geom_embedding = torch.randn(synthetic_batch_size, int(model_config["geom_embed_dim"]))

    model = instantiate_streaming_student_scaffold(model_config=model_config)
    with torch.no_grad():
        outputs = model(
            waveform=waveform,
            lengths=lengths,
            speaker_embedding=speaker_embedding,
            geom_embedding=geom_embedding,
        )

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    plan = {
        "experiment_id": experiment_id,
        "created_at": run_ended_at.isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "phase": {
            "name": "stage3_streaming_student_scaffold",
            "mode": training_config["mode"],
            "run_stage": training_config["run_stage"],
            "teacher_required": bool(training_config.get("teacher_required", True)),
            "student_required": bool(training_config.get("student_required", True)),
            "vocoder_required": bool(training_config.get("vocoder_required", False)),
        },
        "data": {
            "manifest_dir": manifest_dir.as_posix(),
            "split_dir": None if split_dir is None else split_dir.as_posix(),
            "split": split_summary,
            "target_manifest_count": len(target_manifest_records),
            "source_manifest_count": len(source_manifest_records),
            "target_train_count": len(target_train_records),
            "target_validation_count": len(target_validation_records),
            "target_special_eval_count": len(target_special_eval_records),
            "source_train_count": len(source_train_records),
            "source_validation_count": len(source_validation_records),
            "target_weak_event_hints_path": (
                None if target_weak_event_hints_path is None else target_weak_event_hints_path.as_posix()
            ),
            "target_special_supervision_path": (
                None if target_special_supervision_path is None else target_special_supervision_path.as_posix()
            ),
            "target_event_semantic_sidecar_path": (
                None
                if target_event_semantic_sidecar_path is None
                else target_event_semantic_sidecar_path.as_posix()
            ),
        },
        "model": model_config,
        "contracts": build_contract_summary(model_config=model_config),
        "dry_run": {
            "synthetic_batch_size": synthetic_batch_size,
            "synthetic_waveform_length": synthetic_waveform_length,
            "input_shapes": {
                "waveform": list(waveform.shape),
                "lengths": list(lengths.shape),
                "speaker_embedding": list(speaker_embedding.shape),
                "geom_embedding": list(geom_embedding.shape),
            },
            "output_shapes": {key: list(value.shape) for key, value in outputs.items() if isinstance(value, torch.Tensor)},
            "status": "scaffold_ready",
        },
        "next_steps": [
            "Add teacher-label dataset wiring for frontend/student supervision without reusing offline_mvp training loops directly.",
            "Define calibration asset format for s_spk_target, s_geom_target, and alpha before any real student training.",
            "Build a stage3 eval bridge that maps scaffold outputs into offline_mvp-compatible control summaries before opening new experiments.",
        ],
        "notes": [str(note) for note in list(planning_config.get("notes", [])) if str(note)],
    }

    plan_json_path = output_dir / f"{experiment_id}.plan.json"
    plan_md_path = output_dir / f"{experiment_id}.plan.md"
    plan_json_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    plan_md_path.write_text(render_streaming_student_plan_markdown(plan=plan), encoding="utf-8", newline="\n")
    update_streaming_student_experiment_metrics(
        output_dir=output_dir,
        experiment_id=experiment_id,
        plan=plan,
        plan_json_path=plan_json_path,
        plan_md_path=plan_md_path,
    )
    print(
        "[stage3] scaffold_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} duration_sec={round(duration_sec, 6)} "
        f"plan={plan_json_path.as_posix()}"
    )


def validate_streaming_student_config(config: dict[str, object]) -> None:
    if str(config.get("training", {}).get("mode")) != "streaming_student_stage":
        raise ValueError("training.mode must be 'streaming_student_stage'.")
    if str(config.get("training", {}).get("run_stage")) != "scaffold_bootstrap":
        raise ValueError("training.run_stage must be 'scaffold_bootstrap'.")
    if bool(config.get("model", {}).get("r_res_enabled", False)):
        raise ValueError("Stage3 scaffold bootstrap must keep model.r_res_enabled=false.")


def resolve_optional_path(config_path: Path, raw_value: object) -> Path | None:
    if raw_value in {None, ""}:
        return None
    return (config_path.parent.parent / str(raw_value)).resolve()


def resolve_target_event_semantic_sidecar_path(
    config_path: Path,
    data_config: dict[str, object],
) -> Path | None:
    resolved = resolve_optional_path(
        config_path=config_path,
        raw_value=data_config.get("target_event_semantic_sidecar_path"),
    )
    if resolved is not None:
        return resolved
    split_dir = resolve_optional_path(config_path=config_path, raw_value=data_config.get("split_dir"))
    return infer_target_event_semantic_sidecar_path(split_dir)


def instantiate_streaming_student_scaffold(model_config: dict[str, object]) -> StreamingStudentScaffold:
    return StreamingStudentScaffold(
        shared_dim=int(model_config["shared_dim"]),
        frontend_dim=int(model_config["frontend_dim"]),
        frontend_layers=int(model_config["frontend_layers"]),
        student_dim=int(model_config["student_dim"]),
        student_layers=int(model_config["student_layers"]),
        z_art_dim=int(model_config["z_art_dim"]),
        event_dim=int(model_config["event_dim"]),
        event_prior_dim=int(model_config["event_prior_dim"]),
        speaker_embed_dim=int(model_config["speaker_embed_dim"]),
        geom_embed_dim=int(model_config["geom_embed_dim"]),
        conditioning_dim=int(model_config["conditioning_dim"]),
        r_res_dim=int(model_config["r_res_dim"]),
        frame_length=int(model_config["frame_length"]),
        hop_length=int(model_config["hop_length"]),
        r_res_enabled=bool(model_config.get("r_res_enabled", False)),
        f0_correction_enabled=bool(model_config.get("f0_correction_enabled", True)),
        aper_correction_enabled=bool(model_config.get("aper_correction_enabled", True)),
    )


def build_contract_summary(model_config: dict[str, object]) -> dict[str, object]:
    return {
        "frontend_outputs": {
            "shared_hidden": {"feature_dim": int(model_config["shared_dim"])},
            "coarse_log_f0": {"feature_dim": 1},
            "vuv_logits": {"feature_dim": 1},
            "aperiodicity": {"feature_dim": 1},
            "energy": {"feature_dim": 1},
            "event_prior_logits": {"feature_dim": int(model_config["event_prior_dim"])},
        },
        "student_outputs": {
            "z_art": {"feature_dim": int(model_config["z_art_dim"])},
            "event_logits": {"feature_dim": int(model_config["event_dim"])},
            "r_res": {"feature_dim": 0 if not bool(model_config.get("r_res_enabled", False)) else int(model_config["r_res_dim"])},
            "log_f0_correction": {"feature_dim": 1 if bool(model_config.get("f0_correction_enabled", True)) else 0},
            "aper_correction": {"feature_dim": 1 if bool(model_config.get("aper_correction_enabled", True)) else 0},
        },
        "conditioning_inputs": {
            "speaker_embedding": {"feature_dim": int(model_config["speaker_embed_dim"])},
            "geom_embedding": {"feature_dim": int(model_config["geom_embed_dim"])},
            "conditioning_hidden": {"feature_dim": int(model_config["conditioning_dim"])},
        },
        "offline_mvp_eval_bridge": {
            "stable_keys": [
                "frame_mask",
                "z_art",
                "event_logits",
                "coarse_log_f0",
                "vuv_logits",
                "aperiodicity",
                "energy",
            ],
            "notes": [
                "Keep frame_length and hop_length aligned with offline_mvp to preserve frame-level comparability.",
                "Treat r_res as disabled during scaffold bootstrap; do not let new eval tooling depend on it yet.",
                "Bridge layer should summarize stage3 outputs into offline_mvp-style control tables before real evaluation reuse.",
            ],
        },
    }


def render_streaming_student_plan_markdown(plan: dict[str, object]) -> str:
    data = plan["data"]
    dry_run = plan["dry_run"]
    contracts = plan["contracts"]
    lines = [
        "# Stage3 Streaming Student Scaffold Plan",
        "",
        "## Status",
        f"- experiment_id: {plan['experiment_id']}",
        f"- created_at: {plan['created_at']}",
        f"- mode: {plan['phase']['mode']}",
        f"- run_stage: {plan['phase']['run_stage']}",
        f"- status: {dry_run['status']}",
        "",
        "## Data",
        f"- manifest_dir: {data['manifest_dir']}",
        f"- split_dir: {data['split_dir']}",
        f"- target_train_count: {data['target_train_count']}",
        f"- target_validation_count: {data['target_validation_count']}",
        f"- target_special_eval_count: {data['target_special_eval_count']}",
        f"- source_train_count: {data['source_train_count']}",
        f"- source_validation_count: {data['source_validation_count']}",
        f"- target_weak_event_hints_path: {data['target_weak_event_hints_path']}",
        f"- target_special_supervision_path: {data['target_special_supervision_path']}",
        f"- target_event_semantic_sidecar_path: {data['target_event_semantic_sidecar_path']}",
        "",
        "## Contract",
        f"- shared_hidden_dim: {contracts['frontend_outputs']['shared_hidden']['feature_dim']}",
        f"- z_art_dim: {contracts['student_outputs']['z_art']['feature_dim']}",
        f"- event_dim: {contracts['student_outputs']['event_logits']['feature_dim']}",
        f"- r_res_dim: {contracts['student_outputs']['r_res']['feature_dim']}",
        "",
        "## Dry Run Shapes",
    ]
    for key, shape in dry_run["output_shapes"].items():
        lines.append(f"- {key}: {shape}")
    lines.extend(
        [
            "",
            "## Next Steps",
        ]
    )
    for item in plan["next_steps"]:
        lines.append(f"- {item}")
    if plan["notes"]:
        lines.extend(
            [
                "",
                "## Notes",
            ]
        )
        for note in plan["notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def update_streaming_student_experiment_metrics(
    output_dir: Path,
    experiment_id: str,
    plan: dict[str, object],
    plan_json_path: Path,
    plan_md_path: Path,
) -> None:
    experiments_dir = output_dir.parent.parent / "experiments"
    metrics_path = resolve_experiment_metrics_path(experiments_dir=experiments_dir, experiment_id=experiment_id)
    if metrics_path is None:
        return
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    payload.setdefault("metrics", {})
    payload["metrics"]["next_stage_scaffold"] = {
        "timing": plan["timing"],
        "phase": plan["phase"],
        "data": plan["data"],
        "contracts": plan["contracts"],
        "dry_run": plan["dry_run"],
        "artifacts": {
            "plan_json_path": plan_json_path.as_posix(),
            "plan_md_path": plan_md_path.as_posix(),
        },
        "status": plan["dry_run"]["status"],
    }
    payload["status"] = plan["dry_run"]["status"]
    metrics_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
