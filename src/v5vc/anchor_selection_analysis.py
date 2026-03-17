from __future__ import annotations

import shutil
from pathlib import Path

from v5vc.ablation_eval import load_experiment_metrics_payload
from v5vc.data_scan import write_json


def analyze_offline_mvp_anchor_selection(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    anchors = [load_anchor_candidate(path) for path in resolved_paths]
    summary = build_summary(anchors=anchors, output_dir=output_dir)
    write_json(output_dir / "anchor_selection_analysis.json", summary)
    (output_dir / "anchor_selection_analysis.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_anchor_candidate(experiment_metrics_path: Path) -> dict[str, object]:
    payload = load_experiment_metrics_payload(experiment_metrics_path)
    metrics = payload.get("metrics", {})
    special_eval = metrics.get("target_special_eval_model")
    ablation_eval = metrics.get("ablation_eval")
    training_run = metrics.get("training_run", {})
    if not isinstance(special_eval, dict) or not isinstance(ablation_eval, dict):
        raise ValueError(
            f"{experiment_metrics_path.as_posix()} is missing target_special_eval_model or ablation_eval."
        )

    target_validation = special_eval.get("target_validation", {})
    target_special = special_eval.get("target_special_eval", {})
    comparisons = special_eval.get("comparisons", {})
    ablation_comparisons = ablation_eval.get("comparisons", {})
    zero_e_evt = ablation_comparisons.get("zero_e_evt", {})
    zero_z_art = ablation_comparisons.get("zero_z_art", {})

    return {
        "experiment_id": str(payload.get("experiment_id", experiment_metrics_path.stem.replace(".metrics", ""))),
        "experiment_metrics_path": experiment_metrics_path.as_posix(),
        "checkpoint_path": str(special_eval.get("checkpoint_path", "")),
        "completed_steps": int(training_run.get("training_run", {}).get("completed_steps", 0)),
        "target_validation_loss_total": float(target_validation.get("metrics", {}).get("loss_total", 0.0)),
        "target_special_eval_loss_total": float(target_special.get("metrics", {}).get("loss_total", 0.0)),
        "delta_loss_total": float(comparisons.get("delta_loss_total", 0.0)),
        "zero_e_evt_delta_target_loss_total": float(zero_e_evt.get("delta_target_loss_total", 0.0)),
        "zero_z_art_delta_target_loss_total": float(zero_z_art.get("delta_target_loss_total", 0.0)),
    }


def build_summary(anchors: list[dict[str, object]], output_dir: Path) -> dict[str, object]:
    anchors = [round_anchor(anchor) for anchor in anchors]
    best_validation = min(anchors, key=lambda item: float(item["target_validation_loss_total"]))
    best_special = min(anchors, key=lambda item: float(item["delta_loss_total"]))
    best_e_evt = max(anchors, key=lambda item: float(item["zero_e_evt_delta_target_loss_total"]))
    best_z_art = max(anchors, key=lambda item: float(item["zero_z_art_delta_target_loss_total"]))
    ranges = build_metric_ranges(anchors)
    anchors_with_regret = [attach_normalized_regret(anchor, ranges) for anchor in anchors]
    minimax_anchor = min(
        anchors_with_regret,
        key=lambda item: (
            float(item["normalized_regret"]["max_regret"]),
            float(item["normalized_regret"]["mean_regret"]),
            float(item["delta_loss_total"]),
        ),
    )
    validation_budget_sweep = build_validation_budget_sweep(anchors=anchors_with_regret, best_validation=best_validation)
    dual_control_floor_sweep = build_dual_control_floor_sweep(anchors=anchors_with_regret)
    pairwise = build_pairwise_deltas(anchors_with_regret)
    recommendation = {
        "best_validation_anchor": best_validation["experiment_id"],
        "best_special_anchor": best_special["experiment_id"],
        "best_e_evt_anchor": best_e_evt["experiment_id"],
        "best_z_art_anchor": best_z_art["experiment_id"],
        "minimax_regret_anchor": minimax_anchor["experiment_id"],
        "has_joint_final_winner": bool(
            best_validation["experiment_id"] == best_special["experiment_id"] == best_e_evt["experiment_id"] == best_z_art["experiment_id"]
        ),
        "validation_switchpoints": summarize_validation_switchpoints(validation_budget_sweep),
    }
    return {
        "output_dir": output_dir.as_posix(),
        "anchor_count": len(anchors_with_regret),
        "anchors": anchors_with_regret,
        "metric_leaders": {
            "validation": best_validation,
            "special": best_special,
            "zero_e_evt": best_e_evt,
            "zero_z_art": best_z_art,
        },
        "metric_ranges": ranges,
        "minimax_regret_anchor": minimax_anchor,
        "validation_budget_sweep": validation_budget_sweep,
        "dual_control_floor_sweep": dual_control_floor_sweep,
        "pairwise_deltas": pairwise,
        "recommendation": recommendation,
        "notes": [
            "This report compares final anchors only; it does not re-open hidden checkpoint search.",
            "Lower target_validation_loss_total and delta_loss_total are better.",
            "Higher zero_e_evt_delta_target_loss_total and zero_z_art_delta_target_loss_total are better.",
            "normalized_regret rescales each metric to the observed anchor range so the minimax anchor is the least-worst final reference across all tracked axes.",
        ],
    }


def round_anchor(anchor: dict[str, object]) -> dict[str, object]:
    rounded = dict(anchor)
    for key in (
        "target_validation_loss_total",
        "target_special_eval_loss_total",
        "delta_loss_total",
        "zero_e_evt_delta_target_loss_total",
        "zero_z_art_delta_target_loss_total",
    ):
        rounded[key] = round(float(anchor[key]), 6)
    return rounded


def build_metric_ranges(anchors: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    metric_values = {
        "target_validation_loss_total": [float(anchor["target_validation_loss_total"]) for anchor in anchors],
        "delta_loss_total": [float(anchor["delta_loss_total"]) for anchor in anchors],
        "zero_e_evt_delta_target_loss_total": [float(anchor["zero_e_evt_delta_target_loss_total"]) for anchor in anchors],
        "zero_z_art_delta_target_loss_total": [float(anchor["zero_z_art_delta_target_loss_total"]) for anchor in anchors],
    }
    return {
        metric: {
            "min": round(min(values), 6),
            "max": round(max(values), 6),
            "range": round(max(values) - min(values), 6),
        }
        for metric, values in metric_values.items()
    }


def attach_normalized_regret(
    anchor: dict[str, object],
    ranges: dict[str, dict[str, float]],
) -> dict[str, object]:
    validation_regret = normalize_lower_is_better(
        value=float(anchor["target_validation_loss_total"]),
        metric_range=ranges["target_validation_loss_total"],
    )
    special_regret = normalize_lower_is_better(
        value=float(anchor["delta_loss_total"]),
        metric_range=ranges["delta_loss_total"],
    )
    e_evt_regret = normalize_higher_is_better(
        value=float(anchor["zero_e_evt_delta_target_loss_total"]),
        metric_range=ranges["zero_e_evt_delta_target_loss_total"],
    )
    z_art_regret = normalize_higher_is_better(
        value=float(anchor["zero_z_art_delta_target_loss_total"]),
        metric_range=ranges["zero_z_art_delta_target_loss_total"],
    )
    regrets = {
        "validation": validation_regret,
        "special": special_regret,
        "zero_e_evt": e_evt_regret,
        "zero_z_art": z_art_regret,
    }
    payload = dict(anchor)
    payload["normalized_regret"] = {
        **regrets,
        "max_regret": round(max(regrets.values()), 6),
        "mean_regret": round(sum(regrets.values()) / len(regrets), 6),
    }
    return payload


def normalize_lower_is_better(value: float, metric_range: dict[str, float]) -> float:
    observed_range = float(metric_range["range"])
    if observed_range <= 0.0:
        return 0.0
    return round((value - float(metric_range["min"])) / observed_range, 6)


def normalize_higher_is_better(value: float, metric_range: dict[str, float]) -> float:
    observed_range = float(metric_range["range"])
    if observed_range <= 0.0:
        return 0.0
    return round((float(metric_range["max"]) - value) / observed_range, 6)


def build_validation_budget_sweep(
    anchors: list[dict[str, object]],
    best_validation: dict[str, object],
) -> list[dict[str, object]]:
    base_validation = float(best_validation["target_validation_loss_total"])
    budgets = sorted(
        {
            round(float(anchor["target_validation_loss_total"]) - base_validation, 6)
            for anchor in anchors
        }
    )
    rows: list[dict[str, object]] = []
    for budget in budgets:
        eligible = [
            anchor
            for anchor in anchors
            if float(anchor["target_validation_loss_total"]) <= base_validation + float(budget) + 1e-9
        ]
        best_special = min(
            eligible,
            key=lambda item: (
                float(item["delta_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
                -float(item["zero_z_art_delta_target_loss_total"]),
            ),
        )
        best_e_evt = max(
            eligible,
            key=lambda item: (
                float(item["zero_e_evt_delta_target_loss_total"]),
                -float(item["target_validation_loss_total"]),
            ),
        )
        best_z_art = max(
            eligible,
            key=lambda item: (
                float(item["zero_z_art_delta_target_loss_total"]),
                -float(item["target_validation_loss_total"]),
            ),
        )
        best_minimax = min(
            eligible,
            key=lambda item: (
                float(item["normalized_regret"]["max_regret"]),
                float(item["normalized_regret"]["mean_regret"]),
                float(item["delta_loss_total"]),
            ),
        )
        rows.append(
            {
                "validation_budget_over_best": round(float(budget), 6),
                "eligible_anchor_ids": [str(anchor["experiment_id"]) for anchor in eligible],
                "best_special_anchor": str(best_special["experiment_id"]),
                "best_e_evt_anchor": str(best_e_evt["experiment_id"]),
                "best_z_art_anchor": str(best_z_art["experiment_id"]),
                "best_minimax_anchor": str(best_minimax["experiment_id"]),
            }
        )
    return rows


def build_dual_control_floor_sweep(anchors: list[dict[str, object]]) -> list[dict[str, object]]:
    floor_specs = sorted(
        [
            {
                "floor_anchor_id": str(anchor["experiment_id"]),
                "min_zero_e_evt_delta_target_loss_total": round(float(anchor["zero_e_evt_delta_target_loss_total"]), 6),
                "min_zero_z_art_delta_target_loss_total": round(float(anchor["zero_z_art_delta_target_loss_total"]), 6),
            }
            for anchor in anchors
        ],
        key=lambda item: (
            -float(item["min_zero_e_evt_delta_target_loss_total"]),
            -float(item["min_zero_z_art_delta_target_loss_total"]),
        ),
    )
    rows: list[dict[str, object]] = []
    for spec in floor_specs:
        eligible = [
            anchor
            for anchor in anchors
            if float(anchor["zero_e_evt_delta_target_loss_total"]) >= float(spec["min_zero_e_evt_delta_target_loss_total"]) - 1e-9
            and float(anchor["zero_z_art_delta_target_loss_total"]) >= float(spec["min_zero_z_art_delta_target_loss_total"]) - 1e-9
        ]
        best_validation = min(
            eligible,
            key=lambda item: (
                float(item["target_validation_loss_total"]),
                float(item["delta_loss_total"]),
            ),
        )
        best_special = min(
            eligible,
            key=lambda item: (
                float(item["delta_loss_total"]),
                float(item["target_validation_loss_total"]),
            ),
        )
        rows.append(
            {
                **spec,
                "eligible_anchor_ids": [str(anchor["experiment_id"]) for anchor in eligible],
                "best_validation_anchor": str(best_validation["experiment_id"]),
                "best_special_anchor": str(best_special["experiment_id"]),
            }
        )
    return rows


def build_pairwise_deltas(anchors: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for left in anchors:
        for right in anchors:
            if str(left["experiment_id"]) == str(right["experiment_id"]):
                continue
            rows.append(
                {
                    "from_anchor_id": str(left["experiment_id"]),
                    "to_anchor_id": str(right["experiment_id"]),
                    "delta_target_validation_loss_total": round(
                        float(right["target_validation_loss_total"]) - float(left["target_validation_loss_total"]),
                        6,
                    ),
                    "delta_delta_loss_total": round(
                        float(right["delta_loss_total"]) - float(left["delta_loss_total"]),
                        6,
                    ),
                    "delta_zero_e_evt_delta_target_loss_total": round(
                        float(right["zero_e_evt_delta_target_loss_total"])
                        - float(left["zero_e_evt_delta_target_loss_total"]),
                        6,
                    ),
                    "delta_zero_z_art_delta_target_loss_total": round(
                        float(right["zero_z_art_delta_target_loss_total"])
                        - float(left["zero_z_art_delta_target_loss_total"]),
                        6,
                    ),
                }
            )
    return rows


def summarize_validation_switchpoints(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summarized: list[dict[str, object]] = []
    previous_signature: tuple[str, str, str, str] | None = None
    for row in rows:
        signature = (
            str(row["best_special_anchor"]),
            str(row["best_e_evt_anchor"]),
            str(row["best_z_art_anchor"]),
            str(row["best_minimax_anchor"]),
        )
        if signature == previous_signature:
            continue
        summarized.append(
            {
                "validation_budget_over_best": row["validation_budget_over_best"],
                "best_special_anchor": row["best_special_anchor"],
                "best_e_evt_anchor": row["best_e_evt_anchor"],
                "best_z_art_anchor": row["best_z_art_anchor"],
                "best_minimax_anchor": row["best_minimax_anchor"],
            }
        )
        previous_signature = signature
    return summarized


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP anchor selection analysis",
        "",
        f"- anchor_count: {summary['anchor_count']}",
        "",
        "## metric leaders",
        format_anchor_line("best_validation", summary["metric_leaders"]["validation"]),
        format_anchor_line("best_special", summary["metric_leaders"]["special"]),
        format_anchor_line("best_zero_e_evt", summary["metric_leaders"]["zero_e_evt"]),
        format_anchor_line("best_zero_z_art", summary["metric_leaders"]["zero_z_art"]),
        format_anchor_line("minimax_regret_anchor", summary["minimax_regret_anchor"]),
        "",
        "## anchors",
    ]
    for anchor in summary["anchors"]:
        lines.extend(
            [
                f"### {anchor['experiment_id']}",
                f"- experiment_metrics_path: {anchor['experiment_metrics_path']}",
                f"- checkpoint_path: {anchor['checkpoint_path']}",
                f"- completed_steps: {anchor['completed_steps']}",
                format_anchor_line("final_metrics", anchor),
                f"- normalized_regret: {anchor['normalized_regret']}",
                "",
            ]
        )
    lines.extend(["## validation budget sweep"])
    for row in summary["validation_budget_sweep"]:
        lines.append(
            f"- budget={row['validation_budget_over_best']}: eligible={row['eligible_anchor_ids']}, "
            f"best_special={row['best_special_anchor']}, best_e_evt={row['best_e_evt_anchor']}, "
            f"best_z_art={row['best_z_art_anchor']}, best_minimax={row['best_minimax_anchor']}"
        )
    lines.extend(["", "## dual control floor sweep"])
    for row in summary["dual_control_floor_sweep"]:
        lines.append(
            f"- floor_anchor={row['floor_anchor_id']}: e_evt>={row['min_zero_e_evt_delta_target_loss_total']}, "
            f"z_art>={row['min_zero_z_art_delta_target_loss_total']}, eligible={row['eligible_anchor_ids']}, "
            f"best_validation={row['best_validation_anchor']}, best_special={row['best_special_anchor']}"
        )
    lines.extend(["", "## recommendation", f"- {summary['recommendation']}", "", "## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_anchor_line(label: str, payload: dict[str, object]) -> str:
    return (
        f"- {label}: {payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )
