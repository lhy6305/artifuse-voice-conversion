from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

from pathlib import Path

from v5vc.anchor_selection_analysis import load_anchor_candidate, round_anchor
from v5vc.data_scan import write_json
from v5vc.final_experiment_comparison import build_summary as build_final_comparison_summary
from v5vc.final_experiment_comparison import load_route_context


def recap_offline_mvp_route_context(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
    route_selection_path: Path,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    experiments = [round_anchor(load_anchor_candidate(path.resolve())) for path in experiment_metrics_paths]
    route_context = load_route_context(route_selection_path)
    if route_context is None:
        raise ValueError("route_selection_path is required for route recap.")
    comparison_summary = build_final_comparison_summary(
        experiments=experiments,
        route_context=route_context,
        output_dir=output_dir,
    )
    recap = build_recap(comparison_summary)
    write_json(output_dir / "route_recap.json", recap)
    (output_dir / "route_recap.md").write_text(
        build_markdown(recap),
        encoding="utf-8",
        newline="\n",
    )



def build_recap(comparison_summary: dict[str, object]) -> dict[str, object]:
    route_context = comparison_summary["route_context"]
    rows = comparison_summary["rows"]
    route_anchor = next((row for row in rows if bool(row["is_route_anchor"])), None)
    if route_anchor is None:
        raise ValueError("Could not locate route anchor in comparison summary.")

    alternatives = [row for row in rows if not bool(row["is_route_anchor"])]
    best_validation_alt = min(
        alternatives,
        key=lambda item: (
            float(item["delta_vs_route_anchor"]["target_validation_loss_total"]),
            float(item["delta_vs_route_anchor"]["delta_loss_total"]),
        ),
    )
    best_special_alt = min(
        alternatives,
        key=lambda item: (
            float(item["delta_vs_route_anchor"]["delta_loss_total"]),
            float(item["delta_vs_route_anchor"]["target_validation_loss_total"]),
        ),
    )
    best_e_evt_alt = max(
        alternatives,
        key=lambda item: (
            float(item["delta_vs_route_anchor"]["zero_e_evt_delta_target_loss_total"]),
            -float(item["delta_vs_route_anchor"]["target_validation_loss_total"]),
        ),
    )
    best_z_art_alt = max(
        alternatives,
        key=lambda item: (
            float(item["delta_vs_route_anchor"]["zero_z_art_delta_target_loss_total"]),
            -float(item["delta_vs_route_anchor"]["target_validation_loss_total"]),
        ),
    )
    return {
        "route_context": route_context,
        "route_anchor": route_anchor,
        "leaders": comparison_summary["leaders"],
        "recommended_language": {
            "summary_line": build_summary_line(route_context=route_context, route_anchor=route_anchor),
            "tradeoff_line": build_tradeoff_line(
                route_anchor=route_anchor,
                best_validation_alt=best_validation_alt,
                best_special_alt=best_special_alt,
            ),
        },
        "alternatives": {
            "best_validation_alternative": best_validation_alt,
            "best_special_alternative": best_special_alt,
            "best_e_evt_alternative": best_e_evt_alt,
            "best_z_art_alternative": best_z_art_alt,
        },
        "notes": [
            "This recap is route-aware: all alternative deltas are relative to the currently selected route anchor.",
            "Use summary_line and tradeoff_line directly in phase summaries or experiment reviews when helpful.",
        ],
    }


def build_summary_line(route_context: dict[str, object], route_anchor: dict[str, object]) -> str:
    return (
        f"Current route is {route_context['selected_policy']}, so the active reference anchor is "
        f"{route_anchor['experiment_id']} "
        f"(val={route_anchor['target_validation_loss_total']}, special_delta={route_anchor['delta_loss_total']}, "
        f"zero_e_evt={route_anchor['zero_e_evt_delta_target_loss_total']}, zero_z_art={route_anchor['zero_z_art_delta_target_loss_total']})."
    )


def build_tradeoff_line(
    route_anchor: dict[str, object],
    best_validation_alt: dict[str, object],
    best_special_alt: dict[str, object],
) -> str:
    return (
        f"Relative to {route_anchor['experiment_id']}, the strongest validation alternative is "
        f"{best_validation_alt['experiment_id']} "
        f"(val={best_validation_alt['delta_vs_route_anchor']['target_validation_loss_total']}, "
        f"special={best_validation_alt['delta_vs_route_anchor']['delta_loss_total']}, "
        f"zero_e_evt={best_validation_alt['delta_vs_route_anchor']['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={best_validation_alt['delta_vs_route_anchor']['zero_z_art_delta_target_loss_total']}), "
        f"while the strongest special alternative is {best_special_alt['experiment_id']} "
        f"(val={best_special_alt['delta_vs_route_anchor']['target_validation_loss_total']}, "
        f"special={best_special_alt['delta_vs_route_anchor']['delta_loss_total']}, "
        f"zero_e_evt={best_special_alt['delta_vs_route_anchor']['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={best_special_alt['delta_vs_route_anchor']['zero_z_art_delta_target_loss_total']})."
    )


def build_markdown(recap: dict[str, object]) -> str:
    lines = [
        "# offline MVP route recap",
        "",
        f"- route_context: {recap['route_context']}",
        format_row("route_anchor", recap["route_anchor"]),
        "",
        "## recommended language",
        f"- summary_line: {recap['recommended_language']['summary_line']}",
        f"- tradeoff_line: {recap['recommended_language']['tradeoff_line']}",
        "",
        "## alternatives",
        format_row("best_validation_alternative", recap["alternatives"]["best_validation_alternative"]),
        format_row("best_special_alternative", recap["alternatives"]["best_special_alternative"]),
        format_row("best_e_evt_alternative", recap["alternatives"]["best_e_evt_alternative"]),
        format_row("best_z_art_alternative", recap["alternatives"]["best_z_art_alternative"]),
        "",
        "## notes",
    ]
    for note in recap["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_row(label: str, payload: dict[str, object]) -> str:
    suffix = ""
    if payload.get("delta_vs_route_anchor") is not None:
        suffix = f" [vs_route={payload['delta_vs_route_anchor']}]"
    return (
        f"- {label}: {payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']}){suffix}"
    )
