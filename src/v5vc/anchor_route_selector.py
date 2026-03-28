from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

from pathlib import Path

from v5vc.anchor_route_analysis import build_route_summary
from v5vc.anchor_selection_analysis import build_summary, load_anchor_candidate
from v5vc.data_scan import write_json


def select_offline_mvp_anchor_route(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
    max_validation_budget_over_best: float,
    special_priority: bool,
    z_art_priority: bool,
    require_best_e_evt_floor: bool,
    require_best_z_art_floor: bool,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")
    if max_validation_budget_over_best < 0.0:
        raise ValueError("max_validation_budget_over_best must be >= 0.0.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    anchors = [load_anchor_candidate(path) for path in resolved_paths]
    selection_summary = build_summary(anchors=anchors, output_dir=output_dir)
    route_summary = build_route_summary(selection_summary)
    selector_summary = build_selector_summary(
        route_summary=route_summary,
        max_validation_budget_over_best=max_validation_budget_over_best,
        special_priority=special_priority,
        z_art_priority=z_art_priority,
        require_best_e_evt_floor=require_best_e_evt_floor,
        require_best_z_art_floor=require_best_z_art_floor,
    )
    write_json(output_dir / "anchor_route_selection.json", selector_summary)
    (output_dir / "anchor_route_selection.md").write_text(
        build_markdown(selector_summary),
        encoding="utf-8",
        newline="\n",
    )



def build_selector_summary(
    route_summary: dict[str, object],
    max_validation_budget_over_best: float,
    special_priority: bool,
    z_art_priority: bool,
    require_best_e_evt_floor: bool,
    require_best_z_art_floor: bool,
) -> dict[str, object]:
    policies = {policy["policy_name"]: policy for policy in route_summary["policies"]}
    thresholds = route_summary["derived_thresholds"]
    reasons: list[str] = []
    intent_flags = {
        "special_priority": special_priority,
        "z_art_priority": z_art_priority,
        "require_best_e_evt_floor": require_best_e_evt_floor,
        "require_best_z_art_floor": require_best_z_art_floor,
    }

    if require_best_e_evt_floor and policy_is_available(policies["e_evt_guard"]):
        selected_policy = policies["e_evt_guard"]
        reasons.append("require_best_e_evt_floor=true, so only the e_evt guard route is considered.")
    elif require_best_z_art_floor:
        if (
            max_validation_budget_over_best + 1e-9 >= float(thresholds["budget_to_special_anchor"])
            and policy_is_available(policies["z_art_push"])
        ):
            selected_policy = policies["z_art_push"]
            reasons.append("require_best_z_art_floor=true and budget is sufficient for the z_art route.")
        else:
            selected_policy = fallback_policy(
                policies=policies,
                max_validation_budget_over_best=max_validation_budget_over_best,
            )
            reasons.append(
                "require_best_z_art_floor=true but budget is insufficient for z_art_push; falling back to the strongest feasible default route."
            )
    elif (
        (special_priority or z_art_priority)
        and max_validation_budget_over_best + 1e-9 >= float(thresholds["budget_to_special_anchor"])
        and policy_is_available(policies["special_push"])
    ):
        selected_policy = policies["special_push"]
        reasons.append("special/z_art priority is enabled and budget is sufficient for the special route.")
    elif max_validation_budget_over_best + 1e-9 < float(thresholds["budget_to_minimax_anchor"]):
        selected_policy = policies["validation_strict"]
        reasons.append("budget is below the minimax threshold, so only the strict validation route is feasible.")
    else:
        selected_policy = policies["default_minimax"]
        reasons.append("budget allows the minimax route and no stronger special route is both requested and feasible.")

    unmet_intents = []
    if (special_priority or z_art_priority) and selected_policy["policy_name"] != "special_push":
        unmet_intents.append("special_or_z_art_priority_not_fully_honored")
    if require_best_z_art_floor and selected_policy["policy_name"] != "z_art_push":
        unmet_intents.append("best_z_art_floor_not_honored")
    if require_best_e_evt_floor and selected_policy["policy_name"] != "e_evt_guard":
        unmet_intents.append("best_e_evt_floor_not_honored")

    return {
        "route_summary_ref": route_summary["anchor_selection_summary_ref"],
        "inputs": {
            "max_validation_budget_over_best": round(max_validation_budget_over_best, 6),
            **intent_flags,
        },
        "derived_thresholds": dict(thresholds),
        "selected_policy": selected_policy,
        "selected_anchor": dict(selected_policy["selected_anchor"]),
        "reasons": reasons,
        "unmet_intents": unmet_intents,
        "notes": [
            "This selector resolves one concrete route decision from the current three-anchor policy set.",
            "If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.",
        ],
    }


def fallback_policy(
    policies: dict[str, dict[str, object]],
    max_validation_budget_over_best: float,
) -> dict[str, object]:
    guarded_budget = policies["guarded_default"]["constraints"]["max_validation_budget_over_best"]
    if max_validation_budget_over_best + 1e-9 < float(guarded_budget):
        return policies["validation_strict"]
    return policies["default_minimax"]


def policy_is_available(policy: dict[str, object]) -> bool:
    return bool(policy.get("selected_anchor"))


def build_markdown(summary: dict[str, object]) -> str:
    selected_policy = summary["selected_policy"]
    selected_anchor = summary["selected_anchor"]
    lines = [
        "# offline MVP anchor route selection",
        "",
        f"- inputs: {summary['inputs']}",
        f"- derived_thresholds: {summary['derived_thresholds']}",
        f"- selected_policy: {selected_policy['policy_name']}",
        format_anchor_line("selected_anchor", selected_anchor),
        f"- unmet_intents: {summary['unmet_intents']}",
        "",
        "## reasons",
    ]
    for reason in summary["reasons"]:
        lines.append(f"- {reason}")
    lines.extend(["", "## notes"])
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
