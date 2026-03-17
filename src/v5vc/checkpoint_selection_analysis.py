from __future__ import annotations

import math
import shutil
from pathlib import Path

from v5vc.ablation_eval import load_experiment_metrics_payload
from v5vc.data_scan import write_json


def analyze_offline_mvp_checkpoint_selection(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
    late_step_ratio: float,
    validation_guard_ratio: float,
    min_positive_control_delta: float,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")
    if late_step_ratio <= 0.0 or late_step_ratio > 1.0:
        raise ValueError("late_step_ratio must be within (0.0, 1.0].")
    if validation_guard_ratio < 1.0:
        raise ValueError("validation_guard_ratio must be >= 1.0.")
    if min_positive_control_delta < 0.0:
        raise ValueError("min_positive_control_delta must be >= 0.0.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    experiments = [
        analyze_single_experiment(
            experiment_metrics_path=path,
            late_step_ratio=late_step_ratio,
            validation_guard_ratio=validation_guard_ratio,
            min_positive_control_delta=min_positive_control_delta,
        )
        for path in resolved_paths
    ]
    summary = {
        "experiment_metrics_paths": [path.as_posix() for path in resolved_paths],
        "output_dir": output_dir.as_posix(),
        "late_step_ratio": late_step_ratio,
        "validation_guard_ratio": validation_guard_ratio,
        "min_positive_control_delta": min_positive_control_delta,
        "experiment_count": len(experiments),
        "experiments": experiments,
        "cross_experiment_summary": build_cross_experiment_summary(experiments),
        "notes": [
            "This report merges special_eval_series and checkpoint_series_eval from existing experiment metrics.",
            "late_step_ratio defines the checkpoint window considered late enough for checkpoint-selection discussion.",
            "validation_guard_ratio compares a checkpoint against that experiment's best target validation loss.",
            "min_positive_control_delta is the minimum zero_z_art / zero_e_evt delta required by the positive-control selector.",
        ],
    }
    write_json(output_dir / "checkpoint_selection_analysis.json", summary)
    (output_dir / "checkpoint_selection_analysis.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def analyze_single_experiment(
    experiment_metrics_path: Path,
    late_step_ratio: float,
    validation_guard_ratio: float,
    min_positive_control_delta: float,
) -> dict[str, object]:
    payload = load_experiment_metrics_payload(experiment_metrics_path)
    metrics = payload.get("metrics", {})
    special_series = metrics.get("special_eval_series")
    checkpoint_series = metrics.get("checkpoint_series_eval")
    if not isinstance(special_series, dict) or not isinstance(checkpoint_series, dict):
        raise ValueError(
            f"{experiment_metrics_path.as_posix()} is missing special_eval_series or checkpoint_series_eval."
        )

    special_checkpoints = special_series.get("checkpoints", [])
    checkpoint_checkpoints = checkpoint_series.get("checkpoints", [])
    if not isinstance(special_checkpoints, list) or not isinstance(checkpoint_checkpoints, list):
        raise ValueError(f"{experiment_metrics_path.as_posix()} has malformed checkpoint series payloads.")

    special_by_step = {
        int(item["step"]): item
        for item in special_checkpoints
        if isinstance(item, dict) and "step" in item
    }
    ablation_by_step = {
        int(item["step"]): item
        for item in checkpoint_checkpoints
        if isinstance(item, dict) and "step" in item
    }
    shared_steps = sorted(set(special_by_step) & set(ablation_by_step))
    if not shared_steps:
        raise ValueError(f"{experiment_metrics_path.as_posix()} has no overlapping checkpoint steps to compare.")

    rows: list[dict[str, float | int | str]] = []
    for step in shared_steps:
        special_item = special_by_step[step]
        ablation_item = ablation_by_step[step]
        comparisons = ablation_item["comparisons"]
        rows.append(
            {
                "step": step,
                "checkpoint_path": str(special_item["checkpoint_path"]),
                "target_validation_loss_total": float(special_item["target_validation_loss_total"]),
                "target_special_eval_loss_total": float(special_item["target_special_eval_loss_total"]),
                "delta_loss_total": float(special_item["delta_loss_total"]),
                "zero_e_evt_delta_target_loss_total": float(comparisons["zero_e_evt"]["delta_target_loss_total"]),
                "zero_z_art_delta_target_loss_total": float(comparisons["zero_z_art"]["delta_target_loss_total"]),
            }
        )

    max_step = max(shared_steps)
    late_min_step = max(shared_steps[0], int(math.ceil(max_step * late_step_ratio)))
    late_rows = [row for row in rows if int(row["step"]) >= late_min_step]
    if not late_rows:
        late_rows = rows[-1:]

    best_validation = min(
        rows,
        key=lambda row: (
            float(row["target_validation_loss_total"]),
            float(row["delta_loss_total"]),
            -float(row["zero_e_evt_delta_target_loss_total"]),
        ),
    )
    best_special = min(
        rows,
        key=lambda row: (
            float(row["delta_loss_total"]),
            float(row["target_validation_loss_total"]),
            -float(row["zero_e_evt_delta_target_loss_total"]),
        ),
    )
    best_e_evt = max(
        rows,
        key=lambda row: (
            float(row["zero_e_evt_delta_target_loss_total"]),
            -float(row["target_validation_loss_total"]),
        ),
    )
    best_late_special = min(
        late_rows,
        key=lambda row: (
            float(row["delta_loss_total"]),
            float(row["target_validation_loss_total"]),
        ),
    )
    best_late_e_evt = max(
        late_rows,
        key=lambda row: (
            float(row["zero_e_evt_delta_target_loss_total"]),
            -float(row["target_validation_loss_total"]),
        ),
    )

    validation_guard_threshold = float(best_validation["target_validation_loss_total"]) * validation_guard_ratio
    validation_guard_rows = [
        row for row in late_rows if float(row["target_validation_loss_total"]) <= validation_guard_threshold
    ]
    positive_control_rows = [
        row
        for row in late_rows
        if float(row["zero_z_art_delta_target_loss_total"]) >= min_positive_control_delta
        and float(row["zero_e_evt_delta_target_loss_total"]) >= min_positive_control_delta
    ]
    validation_guard_positive_control_rows = [
        row
        for row in validation_guard_rows
        if float(row["zero_z_art_delta_target_loss_total"]) >= min_positive_control_delta
        and float(row["zero_e_evt_delta_target_loss_total"]) >= min_positive_control_delta
    ]

    final_checkpoint = rows[-1]
    return {
        "experiment_id": str(payload.get("experiment_id", experiment_metrics_path.stem.replace(".metrics", ""))),
        "experiment_metrics_path": experiment_metrics_path.as_posix(),
        "status": str(payload.get("status", "")),
        "late_min_step": late_min_step,
        "validation_guard_threshold": round(validation_guard_threshold, 6),
        "final_checkpoint": build_candidate(final_checkpoint, final_checkpoint),
        "best_validation_checkpoint": build_candidate(best_validation, final_checkpoint),
        "best_special_checkpoint": build_candidate(best_special, final_checkpoint),
        "best_e_evt_checkpoint": build_candidate(best_e_evt, final_checkpoint),
        "best_late_special_checkpoint": build_candidate(best_late_special, final_checkpoint),
        "best_late_e_evt_checkpoint": build_candidate(best_late_e_evt, final_checkpoint),
        "best_validation_guarded_checkpoint": build_optional_candidate(
            validation_guard_rows,
            final_checkpoint,
            key=lambda row: (
                float(row["delta_loss_total"]),
                float(row["target_validation_loss_total"]),
                -float(row["zero_e_evt_delta_target_loss_total"]),
            ),
        ),
        "best_positive_control_late_checkpoint": build_optional_candidate(
            positive_control_rows,
            final_checkpoint,
            key=lambda row: (
                float(row["delta_loss_total"]),
                float(row["target_validation_loss_total"]),
                -float(row["zero_e_evt_delta_target_loss_total"]),
            ),
        ),
        "best_validation_guarded_positive_control_checkpoint": build_optional_candidate(
            validation_guard_positive_control_rows,
            final_checkpoint,
            key=lambda row: (
                float(row["delta_loss_total"]),
                float(row["target_validation_loss_total"]),
                -float(row["zero_e_evt_delta_target_loss_total"]),
            ),
        ),
        "late_window": {
            "checkpoint_count": len(late_rows),
            "checkpoints": [round_checkpoint_row(row) for row in late_rows],
        },
        "trajectory_flags": {
            "final_special_positive": float(final_checkpoint["delta_loss_total"]) > 0.0,
            "late_window_contains_negative_special": any(float(row["delta_loss_total"]) < 0.0 for row in late_rows),
            "late_best_e_evt_has_low_z_art": (
                float(best_late_e_evt["zero_z_art_delta_target_loss_total"]) < min_positive_control_delta
            ),
            "validation_guard_excludes_positive_control_special": (
                bool(positive_control_rows) and not bool(validation_guard_positive_control_rows)
            ),
        },
    }


def build_optional_candidate(
    rows: list[dict[str, float | int | str]],
    final_checkpoint: dict[str, float | int | str],
    key,
) -> dict[str, object] | None:
    if not rows:
        return None
    selected = min(rows, key=key)
    return build_candidate(selected, final_checkpoint)


def build_candidate(
    row: dict[str, float | int | str],
    final_checkpoint: dict[str, float | int | str],
) -> dict[str, object]:
    return {
        **round_checkpoint_row(row),
        "delta_vs_final": {
            "target_validation_loss_total": round(
                float(row["target_validation_loss_total"]) - float(final_checkpoint["target_validation_loss_total"]),
                6,
            ),
            "delta_loss_total": round(
                float(row["delta_loss_total"]) - float(final_checkpoint["delta_loss_total"]),
                6,
            ),
            "zero_e_evt_delta_target_loss_total": round(
                float(row["zero_e_evt_delta_target_loss_total"])
                - float(final_checkpoint["zero_e_evt_delta_target_loss_total"]),
                6,
            ),
            "zero_z_art_delta_target_loss_total": round(
                float(row["zero_z_art_delta_target_loss_total"])
                - float(final_checkpoint["zero_z_art_delta_target_loss_total"]),
                6,
            ),
        },
    }


def round_checkpoint_row(row: dict[str, float | int | str]) -> dict[str, object]:
    return {
        "step": int(row["step"]),
        "checkpoint_path": str(row["checkpoint_path"]),
        "target_validation_loss_total": round(float(row["target_validation_loss_total"]), 6),
        "target_special_eval_loss_total": round(float(row["target_special_eval_loss_total"]), 6),
        "delta_loss_total": round(float(row["delta_loss_total"]), 6),
        "zero_e_evt_delta_target_loss_total": round(float(row["zero_e_evt_delta_target_loss_total"]), 6),
        "zero_z_art_delta_target_loss_total": round(float(row["zero_z_art_delta_target_loss_total"]), 6),
    }


def build_cross_experiment_summary(experiments: list[dict[str, object]]) -> dict[str, object]:
    final_checkpoints = [
        {
            "experiment_id": experiment["experiment_id"],
            **experiment["final_checkpoint"],
        }
        for experiment in experiments
    ]
    positive_control_candidates = [
        {
            "experiment_id": experiment["experiment_id"],
            **experiment["best_positive_control_late_checkpoint"],
        }
        for experiment in experiments
        if experiment["best_positive_control_late_checkpoint"] is not None
    ]
    validation_guard_candidates = [
        {
            "experiment_id": experiment["experiment_id"],
            **experiment["best_validation_guarded_checkpoint"],
        }
        for experiment in experiments
        if experiment["best_validation_guarded_checkpoint"] is not None
    ]
    return {
        "best_final_validation_experiment": min(
            final_checkpoints,
            key=lambda item: (
                float(item["target_validation_loss_total"]),
                float(item["delta_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
            ),
        ),
        "best_final_special_experiment": min(
            final_checkpoints,
            key=lambda item: (
                float(item["delta_loss_total"]),
                float(item["target_validation_loss_total"]),
            ),
        ),
        "best_final_e_evt_experiment": max(
            final_checkpoints,
            key=lambda item: (
                float(item["zero_e_evt_delta_target_loss_total"]),
                -float(item["target_validation_loss_total"]),
            ),
        ),
        "best_positive_control_late_special_experiment": (
            min(
                positive_control_candidates,
                key=lambda item: (
                    float(item["delta_loss_total"]),
                    float(item["target_validation_loss_total"]),
                ),
            )
            if positive_control_candidates
            else None
        ),
        "best_validation_guarded_special_experiment": (
            min(
                validation_guard_candidates,
                key=lambda item: (
                    float(item["delta_loss_total"]),
                    float(item["target_validation_loss_total"]),
                ),
            )
            if validation_guard_candidates
            else None
        ),
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP checkpoint 选择分析",
        "",
        f"- experiment_count: {summary['experiment_count']}",
        f"- late_step_ratio: {summary['late_step_ratio']}",
        f"- validation_guard_ratio: {summary['validation_guard_ratio']}",
        f"- min_positive_control_delta: {summary['min_positive_control_delta']}",
        "",
        "## cross experiment summary",
    ]
    cross_summary = summary["cross_experiment_summary"]
    lines.extend(
        [
            format_cross_summary_line("best_final_validation_experiment", cross_summary["best_final_validation_experiment"]),
            format_cross_summary_line("best_final_special_experiment", cross_summary["best_final_special_experiment"]),
            format_cross_summary_line("best_final_e_evt_experiment", cross_summary["best_final_e_evt_experiment"]),
            format_cross_summary_line(
                "best_positive_control_late_special_experiment",
                cross_summary["best_positive_control_late_special_experiment"],
            ),
            format_cross_summary_line(
                "best_validation_guarded_special_experiment",
                cross_summary["best_validation_guarded_special_experiment"],
            ),
            "",
            "## experiments",
        ]
    )
    for experiment in summary["experiments"]:
        lines.extend(
            [
                f"### {experiment['experiment_id']}",
                f"- experiment_metrics_path: {experiment['experiment_metrics_path']}",
                f"- late_min_step: {experiment['late_min_step']}",
                f"- validation_guard_threshold: {experiment['validation_guard_threshold']}",
                f"- trajectory_flags: {experiment['trajectory_flags']}",
                format_candidate_line("final_checkpoint", experiment["final_checkpoint"]),
                format_candidate_line("best_validation_checkpoint", experiment["best_validation_checkpoint"]),
                format_candidate_line("best_special_checkpoint", experiment["best_special_checkpoint"]),
                format_candidate_line("best_e_evt_checkpoint", experiment["best_e_evt_checkpoint"]),
                format_candidate_line("best_late_special_checkpoint", experiment["best_late_special_checkpoint"]),
                format_candidate_line("best_late_e_evt_checkpoint", experiment["best_late_e_evt_checkpoint"]),
                format_candidate_line(
                    "best_validation_guarded_checkpoint",
                    experiment["best_validation_guarded_checkpoint"],
                ),
                format_candidate_line(
                    "best_positive_control_late_checkpoint",
                    experiment["best_positive_control_late_checkpoint"],
                ),
                format_candidate_line(
                    "best_validation_guarded_positive_control_checkpoint",
                    experiment["best_validation_guarded_positive_control_checkpoint"],
                ),
                "- late_window:",
            ]
        )
        for checkpoint in experiment["late_window"]["checkpoints"]:
            lines.append(
                "  "
                + format_candidate_line(
                    f"step{checkpoint['step']}",
                    checkpoint,
                    include_delta=False,
                )
            )
        lines.append("")
    lines.extend(["## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_cross_summary_line(label: str, payload: dict[str, object] | None) -> str:
    if payload is None:
        return f"- {label}: null"
    return (
        f"- {label}: {payload['experiment_id']} @ step {payload['step']} "
        f"(val={payload['target_validation_loss_total']}, special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )


def format_candidate_line(
    label: str,
    payload: dict[str, object] | None,
    include_delta: bool = True,
) -> str:
    if payload is None:
        return f"- {label}: null"
    line = (
        f"- {label}: step {payload['step']} "
        f"(val={payload['target_validation_loss_total']}, special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )
    if include_delta and "delta_vs_final" in payload:
        delta = payload["delta_vs_final"]
        line += (
            " "
            f"[vs final: val={delta['target_validation_loss_total']}, "
            f"special_delta={delta['delta_loss_total']}, "
            f"zero_e_evt={delta['zero_e_evt_delta_target_loss_total']}, "
            f"zero_z_art={delta['zero_z_art_delta_target_loss_total']}]"
        )
    return line
