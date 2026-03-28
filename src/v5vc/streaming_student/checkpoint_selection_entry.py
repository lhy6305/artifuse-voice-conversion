from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.managed_paths import resolve_managed_output_dir
from v5vc.streaming_student.checkpoint_eval_entry import evaluate_split
from v5vc.streaming_student.data import (
    load_streaming_student_conditioning_asset,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.losses import resolve_semantic_supervision_config
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


POSTHOC_TEACHER_LOSS_SELECTOR_VERSION = "stage3_posthoc_teacher_loss_checkpoint_selector_v1"


def select_streaming_student_best_checkpoint(
    checkpoint_paths: list[Path],
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    batch_size: int,
    include_special_eval: bool,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    requested_output_dir = output_dir.resolve()
    output_dir = resolve_managed_output_dir(
        requested_output_dir,
        default_stem="ss_ckpt_sel_posthoc",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_checkpoint_paths = [path.resolve() for path in checkpoint_paths]
    if not resolved_checkpoint_paths:
        raise ValueError("At least one checkpoint path is required.")

    first_payload = torch.load(resolved_checkpoint_paths[0], map_location="cpu", weights_only=False)
    config = first_payload.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"Checkpoint missing config payload: {resolved_checkpoint_paths[0]}")
    config_path = Path(str(first_payload.get("config_path", "configs/streaming_student_stage_template.json")))
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()

    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)

    evaluations: list[dict[str, object]] = []
    for checkpoint_path in resolved_checkpoint_paths:
        payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        checkpoint_config = payload.get("config")
        if not isinstance(checkpoint_config, dict):
            raise ValueError(f"Checkpoint missing config payload: {checkpoint_path}")
        training_summary = dict(payload.get("training", {}))
        loss_weights = {
            str(key): float(value)
            for key, value in dict(training_summary.get("loss_weights", {})).items()
        }
        use_teacher_confidence = bool(training_summary.get("use_teacher_confidence", True))
        semantic_supervision = resolve_semantic_supervision_config(
            config=training_summary.get("semantic_supervision", checkpoint_config.get("semantic_supervision")),
        )

        model = instantiate_streaming_student_scaffold(model_config=dict(checkpoint_config["model"]))
        model.load_state_dict(payload["model_state_dict"])
        model.eval()
        with torch.no_grad():
            validation_summary = evaluate_split(
                model=model,
                records=records_by_split["target_validation"],
                conditioning_asset=conditioning_asset,
                loss_weights=loss_weights,
                use_teacher_confidence=use_teacher_confidence,
                semantic_supervision=semantic_supervision,
                batch_size=batch_size,
            )
            special_summary = None
            if include_special_eval:
                special_summary = evaluate_split(
                    model=model,
                    records=records_by_split["target_special_eval"],
                    conditioning_asset=conditioning_asset,
                    loss_weights=loss_weights,
                    use_teacher_confidence=use_teacher_confidence,
                    semantic_supervision=semantic_supervision,
                    batch_size=batch_size,
                )
        step = int(payload.get("step", 0))
        evaluations.append(
            {
                "checkpoint_path": checkpoint_path.as_posix(),
                "step": step,
                "training": {
                    "use_teacher_confidence": use_teacher_confidence,
                    "loss_weights": loss_weights,
                    "semantic_supervision": semantic_supervision,
                    "loss_weight_overrides_path": training_summary.get("loss_weight_overrides_path"),
                },
                "target_validation": validation_summary,
                "target_special_eval": special_summary,
            }
        )

    ranked = rank_checkpoint_evaluations(evaluations=evaluations, include_special_eval=include_special_eval)
    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "selector_version": POSTHOC_TEACHER_LOSS_SELECTOR_VERSION,
        "selection_objective": "posthoc_teacher_supervised_loss",
        "requested_output_dir": requested_output_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "checkpoint_paths": [path.as_posix() for path in resolved_checkpoint_paths],
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "conditioning": conditioning_asset["summary"],
        "selection_rule": (
            "min_target_validation_loss_total"
            if not include_special_eval
            else "lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)"
        ),
        "include_special_eval": bool(include_special_eval),
        "evaluations": evaluations,
        "ranking": ranked,
        "best_checkpoint_by_posthoc_teacher_loss": None if not ranked else ranked[0],
        "best_checkpoint": None if not ranked else ranked[0],
        "notes": [
            "This report compares already-produced Stage3 checkpoints using post-hoc full-slice teacher-supervised checkpoint evaluation.",
            "The ranking objective is posthoc_teacher_supervised_loss, not packet-aware downstream screening and not the in-loop training trajectory validation record.",
            "The current ranking rule is validation-first; special_eval is a tiebreaker when requested.",
            "These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.",
            "best_checkpoint is kept as a legacy alias for best_checkpoint_by_posthoc_teacher_loss.",
        ],
    }

    json_path = output_dir / "streaming_student_checkpoint_selection.json"
    md_path = output_dir / "streaming_student_checkpoint_selection.md"
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


def rank_checkpoint_evaluations(
    evaluations: list[dict[str, object]],
    include_special_eval: bool,
) -> list[dict[str, object]]:
    ranked_rows: list[dict[str, object]] = []
    for payload in evaluations:
        validation_loss = float(payload["target_validation"]["loss_metrics"]["loss_total"])
        special_loss = (
            None
            if not include_special_eval or payload.get("target_special_eval") is None
            else float(payload["target_special_eval"]["loss_metrics"]["loss_total"])
        )
        ranked_rows.append(
            {
                "checkpoint_path": str(payload["checkpoint_path"]),
                "step": int(payload["step"]),
                "target_validation_loss_total": round(validation_loss, 6),
                "target_special_eval_loss_total": None if special_loss is None else round(special_loss, 6),
            }
        )
    ranked_rows.sort(
        key=lambda item: (
            float(item["target_validation_loss_total"]),
            float("inf") if item["target_special_eval_loss_total"] is None else float(item["target_special_eval_loss_total"]),
            int(item["step"]),
        )
    )
    return ranked_rows


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Post-Hoc Teacher-Loss Checkpoint Selection",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- selector_version: {summary['selector_version']}",
        f"- selection_objective: {summary['selection_objective']}",
        f"- checkpoint_paths: {summary['checkpoint_paths']}",
        f"- include_special_eval: {summary['include_special_eval']}",
        f"- selection_rule: {summary['selection_rule']}",
        f"- best_checkpoint_by_posthoc_teacher_loss: {json.dumps(summary['best_checkpoint_by_posthoc_teacher_loss'], ensure_ascii=False)}",
        "",
        "## Ranking",
    ]
    for row in summary["ranking"]:
        lines.append(
            f"- step={row['step']} target_validation_loss_total={row['target_validation_loss_total']} "
            f"target_special_eval_loss_total={row['target_special_eval_loss_total']} checkpoint_path={row['checkpoint_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
