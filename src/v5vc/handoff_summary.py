from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from v5vc.anchor_selection_analysis import load_anchor_candidate, round_anchor
from v5vc.data_scan import write_json
from v5vc.final_experiment_comparison import build_summary as build_final_comparison_summary
from v5vc.final_experiment_comparison import load_route_context
from v5vc.route_governance import annotate_anchor
from v5vc.route_governance import build_alternative_reference_line
from v5vc.route_governance import build_route_governance_summary
from v5vc.route_governance import infer_reference_horizon
from v5vc.route_recap import build_recap


def build_offline_mvp_route_handoff(
    experiment_metrics_paths: list[Path],
    route_selection_path: Path,
    output_dir: Path,
    stage_label: str | None = None,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    experiments = [round_anchor(load_anchor_candidate(path.resolve())) for path in experiment_metrics_paths]
    route_context = load_route_context(route_selection_path)
    if route_context is None:
        raise ValueError("route_selection_path is required for handoff summary.")
    comparison_summary = build_final_comparison_summary(
        experiments=experiments,
        route_context=route_context,
        output_dir=output_dir,
    )
    recap = build_recap(comparison_summary)
    summary = build_handoff_summary(
        comparison_summary=comparison_summary,
        recap=recap,
        stage_label=stage_label,
        route_selection_path=route_selection_path.resolve(),
        output_dir=output_dir,
    )
    write_json(output_dir / "route_handoff.json", summary)
    (output_dir / "route_handoff.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_handoff_summary(
    comparison_summary: dict[str, object],
    recap: dict[str, object],
    stage_label: str | None,
    route_selection_path: Path,
    output_dir: Path | None = None,
) -> dict[str, object]:
    route_context = recap["route_context"]
    reference_horizon_completed_steps = infer_reference_horizon(list(comparison_summary["rows"]))
    route_anchor = annotate_anchor(
        recap["route_anchor"],
        reference_horizon_completed_steps=reference_horizon_completed_steps,
    )
    alternatives = {
        label: annotate_anchor(
            payload,
            reference_horizon_completed_steps=reference_horizon_completed_steps,
        )
        for label, payload in dict(recap["alternatives"]).items()
    }
    best_validation_alternative = alternatives["best_validation_alternative"]
    best_special_alternative = alternatives["best_special_alternative"]
    route_governance = build_route_governance_summary(
        route_anchor=route_anchor,
        alternatives=alternatives,
        reference_horizon_completed_steps=reference_horizon_completed_steps,
    )
    stage_label = stage_label or "offline_mvp_route_handoff"
    next_step_guidance = build_next_step_guidance(
        selected_policy=str(route_context["selected_policy"]),
        route_anchor=route_anchor,
        best_validation_alternative=best_validation_alternative,
        best_special_alternative=best_special_alternative,
    )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "stage_label": stage_label,
        "output_dir": output_dir.as_posix() if output_dir is not None else None,
        "route_context": route_context,
        "route_anchor": route_anchor,
        "recommended_language": recap["recommended_language"],
        "alternatives": alternatives,
        "route_governance": route_governance,
        "leaders": comparison_summary["leaders"],
        "artifact_bundle": {
            "route_selection_path": route_selection_path.as_posix(),
            "experiment_metrics_paths": [Path(item["experiment_metrics_path"]).as_posix() for item in comparison_summary["rows"]],
        },
        "copy_ready_handoff": [
            recap["recommended_language"]["summary_line"],
            recap["recommended_language"]["tradeoff_line"],
            route_governance["summary_line"],
            route_governance["guardrail_line"],
            next_step_guidance,
        ],
        "next_step_guidance": next_step_guidance,
        "notes": [
            "This handoff is route-aware and should be preferred over manual anchor summaries.",
            "Synthetic checkpoint anchors are classified before they enter handoff wording so shadow tools and formal defaults do not get mixed.",
            "copy_ready_handoff can be pasted into a phase summary, handoff note, or experiment update with minimal editing.",
        ],
    }


def build_next_step_guidance(
    selected_policy: str,
    route_anchor: dict[str, object],
    best_validation_alternative: dict[str, object],
    best_special_alternative: dict[str, object],
) -> str:
    if selected_policy == "default_minimax":
        return (
            f"Keep {route_anchor['experiment_id']} as the default reference; "
            f"{build_alternative_reference_line(best_validation_alternative, 'validation-first routing')}, "
            f"and {build_alternative_reference_line(best_special_alternative, 'special/z_art-first routing')}."
        )
    if selected_policy == "validation_strict":
        return (
            f"Keep {route_anchor['experiment_id']} as the active validation-first reference; "
            f"{build_alternative_reference_line(best_special_alternative, 'special/z_art-side tradeoff exploration')}."
        )
    if selected_policy in {"special_push", "z_art_push"}:
        return (
            f"Keep {route_anchor['experiment_id']} as the active special-first reference; "
            f"{build_alternative_reference_line(best_validation_alternative, 'validation-first fallback')}."
        )
    return f"Keep {route_anchor['experiment_id']} as the active reference unless the route policy changes."


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP route handoff",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- stage_label: {summary['stage_label']}",
        f"- output_dir: {summary['output_dir']}",
        f"- route_context: {summary['route_context']}",
        format_row("route_anchor", summary["route_anchor"]),
        "",
        "## copy_ready_handoff",
    ]
    for line in summary["copy_ready_handoff"]:
        lines.append(f"- {line}")
    lines.extend(
        [
            "",
            "## route_governance",
            f"- {summary['route_governance']['summary_line']}",
            f"- {summary['route_governance']['guardrail_line']}",
            "",
            "## alternatives",
            format_row("best_validation_alternative", summary["alternatives"]["best_validation_alternative"]),
            format_row("best_special_alternative", summary["alternatives"]["best_special_alternative"]),
            format_row("best_e_evt_alternative", summary["alternatives"]["best_e_evt_alternative"]),
            format_row("best_z_art_alternative", summary["alternatives"]["best_z_art_alternative"]),
            "",
            "## artifact_bundle",
            f"- {summary['artifact_bundle']}",
            "",
            "## notes",
        ]
    )
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_row(label: str, payload: dict[str, object]) -> str:
    suffix = ""
    if payload.get("delta_vs_route_anchor") is not None:
        suffix = f" [vs_route={payload['delta_vs_route_anchor']}]"
    governance_suffix = ""
    governance = payload.get("governance")
    if isinstance(governance, dict):
        governance_suffix = f" [governance={governance['anchor_class']}]"
    return (
        f"- {label}: {payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']}){suffix}{governance_suffix}"
    )
