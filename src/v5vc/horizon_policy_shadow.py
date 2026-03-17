from __future__ import annotations

import shutil
from pathlib import Path

from v5vc.anchor_route_analysis import analyze_offline_mvp_anchor_routes
from v5vc.anchor_route_selector import select_offline_mvp_anchor_route
from v5vc.checkpoint_anchor_materializer import materialize_offline_mvp_checkpoint_anchor
from v5vc.data_scan import write_json
from v5vc.final_experiment_comparison import compare_offline_mvp_final_experiments
from v5vc.route_recap import recap_offline_mvp_route_context


def build_offline_mvp_matched_horizon_shadow(
    experiment_metrics_paths: list[Path],
    checkpoint_anchor_experiment_metrics_path: Path,
    checkpoint_anchor_step: int,
    validation_budgets: list[float],
    output_dir: Path,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one matched-horizon experiment metrics path is required.")
    if checkpoint_anchor_step <= 0:
        raise ValueError("checkpoint_anchor_step must be > 0.")
    if not validation_budgets:
        raise ValueError("At least one validation budget is required.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    checkpoint_anchor_experiment_metrics_path = checkpoint_anchor_experiment_metrics_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    materialized_anchor_path = (
        output_dir
        / "materialized_anchor"
        / f"{checkpoint_anchor_experiment_metrics_path.stem}.checkpoint-step{checkpoint_anchor_step}-anchor.metrics.json"
    )
    materialize_offline_mvp_checkpoint_anchor(
        experiment_metrics_path=checkpoint_anchor_experiment_metrics_path,
        step=checkpoint_anchor_step,
        output_path=materialized_anchor_path,
    )

    matched_paths = [resolved_paths[0], materialized_anchor_path, *resolved_paths[1:]]
    route_analysis_dir = output_dir / "anchor_routes"
    analyze_offline_mvp_anchor_routes(
        experiment_metrics_paths=matched_paths,
        output_dir=route_analysis_dir,
    )

    budget_runs: list[dict[str, object]] = []
    for budget in validation_budgets:
        budget_token = format_budget_token(budget)
        selector_dir = output_dir / f"anchor_route_selection_budget_{budget_token}"
        comparison_dir = output_dir / f"final_comparison_budget_{budget_token}"
        recap_dir = output_dir / f"route_recap_budget_{budget_token}"

        select_offline_mvp_anchor_route(
            experiment_metrics_paths=matched_paths,
            output_dir=selector_dir,
            max_validation_budget_over_best=budget,
            special_priority=False,
            z_art_priority=False,
            require_best_e_evt_floor=False,
            require_best_z_art_floor=False,
        )
        route_selection_path = selector_dir / "anchor_route_selection.json"
        compare_offline_mvp_final_experiments(
            experiment_metrics_paths=matched_paths,
            output_dir=comparison_dir,
            route_selection_path=route_selection_path,
        )
        recap_offline_mvp_route_context(
            experiment_metrics_paths=matched_paths,
            output_dir=recap_dir,
            route_selection_path=route_selection_path,
        )
        budget_runs.append(
            {
                "validation_budget": round(float(budget), 6),
                "selector_dir": selector_dir.as_posix(),
                "comparison_dir": comparison_dir.as_posix(),
                "recap_dir": recap_dir.as_posix(),
            }
        )

    summary = {
        "output_dir": output_dir.as_posix(),
        "matched_experiment_metrics_paths": [path.as_posix() for path in resolved_paths],
        "checkpoint_anchor_experiment_metrics_path": checkpoint_anchor_experiment_metrics_path.as_posix(),
        "checkpoint_anchor_step": checkpoint_anchor_step,
        "materialized_anchor_path": materialized_anchor_path.as_posix(),
        "route_analysis_dir": route_analysis_dir.as_posix(),
        "validation_budgets": [round(float(budget), 6) for budget in validation_budgets],
        "budget_runs": budget_runs,
        "notes": [
            "This bundle materializes one checkpoint anchor, then runs matched-horizon route-analysis, selector, final comparison, and route recap for each requested validation budget.",
            "Budget runs always use default_minimax inputs with no special/z_art/e_evt override flags.",
        ],
    }
    write_json(output_dir / "matched_horizon_shadow_bundle.json", summary)
    (output_dir / "matched_horizon_shadow_bundle.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def format_budget_token(value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    return text.replace(".", "p")


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP matched-horizon shadow bundle",
        "",
        f"- output_dir: {summary['output_dir']}",
        f"- checkpoint_anchor_experiment_metrics_path: {summary['checkpoint_anchor_experiment_metrics_path']}",
        f"- checkpoint_anchor_step: {summary['checkpoint_anchor_step']}",
        f"- materialized_anchor_path: {summary['materialized_anchor_path']}",
        f"- route_analysis_dir: {summary['route_analysis_dir']}",
        f"- validation_budgets: {summary['validation_budgets']}",
        "",
        "## matched inputs",
    ]
    for path in summary["matched_experiment_metrics_paths"]:
        lines.append(f"- {path}")
    lines.extend(["", "## budget runs"])
    for run in summary["budget_runs"]:
        lines.append(
            f"- budget={run['validation_budget']}: selector={run['selector_dir']}, comparison={run['comparison_dir']}, recap={run['recap_dir']}"
        )
    lines.extend(["", "## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
