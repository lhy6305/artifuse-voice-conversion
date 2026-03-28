from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

from pathlib import Path

from v5vc.anchor_selection_analysis import build_summary, load_anchor_candidate
from v5vc.data_scan import write_json


def analyze_offline_mvp_anchor_routes(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    anchors = [load_anchor_candidate(path) for path in resolved_paths]
    selection_summary = build_summary(anchors=anchors, output_dir=output_dir)
    route_summary = build_route_summary(selection_summary)
    write_json(output_dir / "anchor_route_analysis.json", route_summary)
    (output_dir / "anchor_route_analysis.md").write_text(
        build_markdown(route_summary),
        encoding="utf-8",
        newline="\n",
    )



def build_route_summary(selection_summary: dict[str, object]) -> dict[str, object]:
    anchors = [dict(anchor) for anchor in selection_summary["anchors"]]
    best_validation = dict(selection_summary["metric_leaders"]["validation"])
    best_special = dict(selection_summary["metric_leaders"]["special"])
    best_e_evt = dict(selection_summary["metric_leaders"]["zero_e_evt"])
    best_z_art = dict(selection_summary["metric_leaders"]["zero_z_art"])
    minimax_anchor = dict(selection_summary["minimax_regret_anchor"])

    budget_to_minimax = round(
        float(minimax_anchor["target_validation_loss_total"]) - float(best_validation["target_validation_loss_total"]),
        6,
    )
    budget_to_special = round(
        float(best_special["target_validation_loss_total"]) - float(best_validation["target_validation_loss_total"]),
        6,
    )

    policies = [
        evaluate_policy(
            anchors=anchors,
            policy_name="validation_strict",
            description="Use the strongest validation anchor with zero extra validation budget.",
            objective="validation",
            max_validation_budget_over_best=0.0,
        ),
        evaluate_policy(
            anchors=anchors,
            policy_name="default_minimax",
            description="Use the least-worst final anchor without extra route constraints.",
            objective="minimax",
        ),
        evaluate_policy(
            anchors=anchors,
            policy_name="guarded_default",
            description="Allow just enough validation budget to include the minimax anchor, then keep minimax selection.",
            objective="minimax",
            max_validation_budget_over_best=budget_to_minimax,
        ),
        evaluate_policy(
            anchors=anchors,
            policy_name="e_evt_guard",
            description="Require the current best e_evt floor and select the least-worst eligible anchor.",
            objective="minimax",
            min_zero_e_evt_delta_target_loss_total=float(best_e_evt["zero_e_evt_delta_target_loss_total"]),
            min_zero_z_art_delta_target_loss_total=float(minimax_anchor["zero_z_art_delta_target_loss_total"]),
        ),
        evaluate_policy(
            anchors=anchors,
            policy_name="special_push",
            description="Allow enough validation budget to include the special/z_art leader and pick the best special eligible anchor.",
            objective="special",
            max_validation_budget_over_best=budget_to_special,
        ),
        evaluate_policy(
            anchors=anchors,
            policy_name="z_art_push",
            description="Require the current best z_art floor and enough validation budget to include that anchor, then pick the best special eligible anchor.",
            objective="special",
            max_validation_budget_over_best=budget_to_special,
            min_zero_z_art_delta_target_loss_total=float(best_z_art["zero_z_art_delta_target_loss_total"]),
        ),
    ]

    recommended_policy = {
        "default_policy": "default_minimax",
        "route_switch_rules": [
            {
                "when": f"max_validation_budget_over_best < {budget_to_minimax}",
                "use_policy": "validation_strict",
                "selected_anchor_id": policies[0]["selected_anchor"]["experiment_id"],
            },
            {
                "when": (
                    f"max_validation_budget_over_best >= {budget_to_minimax} and "
                    f"(special_priority is false and z_art_priority is false)"
                ),
                "use_policy": "default_minimax",
                "selected_anchor_id": policies[1]["selected_anchor"]["experiment_id"],
            },
            {
                "when": (
                    f"max_validation_budget_over_best >= {budget_to_special} and "
                    f"(special_priority is true or z_art_priority is true)"
                ),
                "use_policy": "special_push",
                "selected_anchor_id": policies[4]["selected_anchor"]["experiment_id"],
            },
        ],
    }

    return {
        "anchor_selection_summary_ref": str(selection_summary["output_dir"]),
        "anchor_count": len(anchors),
        "anchors": anchors,
        "leaders": {
            "validation": best_validation,
            "special": best_special,
            "zero_e_evt": best_e_evt,
            "zero_z_art": best_z_art,
            "minimax": minimax_anchor,
        },
        "derived_thresholds": {
            "budget_to_minimax_anchor": budget_to_minimax,
            "budget_to_special_anchor": budget_to_special,
            "best_e_evt_floor": round(float(best_e_evt["zero_e_evt_delta_target_loss_total"]), 6),
            "minimax_z_art_floor": round(float(minimax_anchor["zero_z_art_delta_target_loss_total"]), 6),
            "best_z_art_floor": round(float(best_z_art["zero_z_art_delta_target_loss_total"]), 6),
        },
        "policies": policies,
        "recommended_policy": recommended_policy,
        "notes": [
            "Policies operate on final anchors only and are intended for route/reporting decisions, not new training.",
            "validation_strict picks D29-like anchors whenever no extra validation budget is allowed.",
            "default_minimax picks D22-like anchors when a single least-worst default is needed.",
            "special_push picks D26-like anchors only after enough validation budget is explicitly granted.",
        ],
    }


def evaluate_policy(
    anchors: list[dict[str, object]],
    policy_name: str,
    description: str,
    objective: str,
    max_validation_budget_over_best: float | None = None,
    min_zero_e_evt_delta_target_loss_total: float | None = None,
    min_zero_z_art_delta_target_loss_total: float | None = None,
) -> dict[str, object]:
    best_validation = min(anchors, key=lambda item: float(item["target_validation_loss_total"]))
    eligible = []
    for anchor in anchors:
        if max_validation_budget_over_best is not None:
            if (
                float(anchor["target_validation_loss_total"])
                > float(best_validation["target_validation_loss_total"]) + float(max_validation_budget_over_best) + 1e-9
            ):
                continue
        if min_zero_e_evt_delta_target_loss_total is not None:
            if float(anchor["zero_e_evt_delta_target_loss_total"]) < float(min_zero_e_evt_delta_target_loss_total) - 1e-9:
                continue
        if min_zero_z_art_delta_target_loss_total is not None:
            if float(anchor["zero_z_art_delta_target_loss_total"]) < float(min_zero_z_art_delta_target_loss_total) - 1e-9:
                continue
        eligible.append(anchor)
    if not eligible:
        return {
            "policy_name": policy_name,
            "description": description,
            "objective": objective,
            "constraints": {
                "max_validation_budget_over_best": max_validation_budget_over_best,
                "min_zero_e_evt_delta_target_loss_total": min_zero_e_evt_delta_target_loss_total,
                "min_zero_z_art_delta_target_loss_total": min_zero_z_art_delta_target_loss_total,
            },
            "eligible_anchor_ids": [],
            "selected_anchor": None,
            "is_feasible": False,
            "infeasible_reason": "no_eligible_anchors",
        }
    selected = select_anchor(eligible=eligible, objective=objective)
    return {
        "policy_name": policy_name,
        "description": description,
        "objective": objective,
        "constraints": {
            "max_validation_budget_over_best": max_validation_budget_over_best,
            "min_zero_e_evt_delta_target_loss_total": min_zero_e_evt_delta_target_loss_total,
            "min_zero_z_art_delta_target_loss_total": min_zero_z_art_delta_target_loss_total,
        },
        "eligible_anchor_ids": [str(anchor["experiment_id"]) for anchor in eligible],
        "selected_anchor": strip_anchor_for_policy(selected),
        "is_feasible": True,
        "infeasible_reason": None,
    }


def select_anchor(
    eligible: list[dict[str, object]],
    objective: str,
) -> dict[str, object]:
    if objective == "validation":
        return min(
            eligible,
            key=lambda item: (
                float(item["target_validation_loss_total"]),
                float(item["delta_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
                -float(item["zero_z_art_delta_target_loss_total"]),
            ),
        )
    if objective == "special":
        return min(
            eligible,
            key=lambda item: (
                float(item["delta_loss_total"]),
                -float(item["zero_z_art_delta_target_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
                float(item["target_validation_loss_total"]),
            ),
        )
    if objective == "minimax":
        return min(
            eligible,
            key=lambda item: (
                float(item["normalized_regret"]["max_regret"]),
                float(item["normalized_regret"]["mean_regret"]),
                float(item["delta_loss_total"]),
            ),
        )
    raise ValueError(f"Unsupported objective: {objective}")


def strip_anchor_for_policy(anchor: dict[str, object]) -> dict[str, object]:
    return {
        "experiment_id": str(anchor["experiment_id"]),
        "target_validation_loss_total": round(float(anchor["target_validation_loss_total"]), 6),
        "delta_loss_total": round(float(anchor["delta_loss_total"]), 6),
        "zero_e_evt_delta_target_loss_total": round(float(anchor["zero_e_evt_delta_target_loss_total"]), 6),
        "zero_z_art_delta_target_loss_total": round(float(anchor["zero_z_art_delta_target_loss_total"]), 6),
        "normalized_regret": dict(anchor["normalized_regret"]),
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP anchor route analysis",
        "",
        f"- anchor_count: {summary['anchor_count']}",
        f"- derived_thresholds: {summary['derived_thresholds']}",
        "",
        "## leaders",
        format_anchor_line("validation", summary["leaders"]["validation"]),
        format_anchor_line("special", summary["leaders"]["special"]),
        format_anchor_line("zero_e_evt", summary["leaders"]["zero_e_evt"]),
        format_anchor_line("zero_z_art", summary["leaders"]["zero_z_art"]),
        format_anchor_line("minimax", summary["leaders"]["minimax"]),
        "",
        "## policies",
    ]
    for policy in summary["policies"]:
        lines.extend(
            [
                f"### {policy['policy_name']}",
                f"- description: {policy['description']}",
                f"- objective: {policy['objective']}",
                f"- constraints: {policy['constraints']}",
                f"- is_feasible: {policy.get('is_feasible', True)}",
                f"- eligible_anchor_ids: {policy['eligible_anchor_ids']}",
                format_anchor_line("selected_anchor", policy.get("selected_anchor")),
                "",
            ]
        )
    lines.extend(["## recommended policy", f"- {summary['recommended_policy']}", "", "## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_anchor_line(label: str, payload: dict[str, object]) -> str:
    if not payload:
        return f"- {label}: unavailable"
    return (
        f"- {label}: {payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )
