from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import math
from pathlib import Path

from v5vc.ablation_eval import load_experiment_metrics_payload
from v5vc.data_scan import write_json


def analyze_offline_mvp_checkpoint_gates(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
    late_step_ratio: float,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")
    if late_step_ratio <= 0.0 or late_step_ratio > 1.0:
        raise ValueError("late_step_ratio must be within (0.0, 1.0].")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    experiments = [load_experiment_checkpoint_rows(path, late_step_ratio) for path in resolved_paths]
    anchor_experiment = min(
        experiments,
        key=lambda item: (
            float(item["final_checkpoint"]["target_validation_loss_total"]),
            float(item["final_checkpoint"]["delta_loss_total"]),
            -float(item["final_checkpoint"]["zero_e_evt_delta_target_loss_total"]),
        ),
    )
    anchor = {
        "experiment_id": anchor_experiment["experiment_id"],
        **anchor_experiment["final_checkpoint"],
    }

    gate_specs = build_gate_specs()
    gate_results = [evaluate_gate(gate_spec=gate_spec, experiments=experiments, anchor=anchor) for gate_spec in gate_specs]
    summary = {
        "experiment_metrics_paths": [path.as_posix() for path in resolved_paths],
        "output_dir": output_dir.as_posix(),
        "late_step_ratio": late_step_ratio,
        "anchor_final_checkpoint": anchor,
        "experiment_count": len(experiments),
        "gate_count": len(gate_results),
        "gates": gate_results,
        "recommendation": build_recommendation(gate_results),
        "notes": [
            "This report replays several interpretable checkpoint-gate prototypes over the late-window checkpoints.",
            "Each gate either optimizes validation, optimizes special behavior, or constrains dual-control behavior before selecting the best special checkpoint.",
            "anchor_final_checkpoint is the strongest final checkpoint among the compared experiments and is used as the current default reference.",
        ],
    }
    write_json(output_dir / "checkpoint_gate_replay.json", summary)
    (output_dir / "checkpoint_gate_replay.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )



def load_experiment_checkpoint_rows(
    experiment_metrics_path: Path,
    late_step_ratio: float,
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
        raise ValueError(f"{experiment_metrics_path.as_posix()} has no overlapping checkpoint steps.")

    rows: list[dict[str, object]] = []
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
    return {
        "experiment_id": str(payload.get("experiment_id", experiment_metrics_path.stem.replace(".metrics", ""))),
        "experiment_metrics_path": experiment_metrics_path.as_posix(),
        "best_validation_loss_total": float(best_validation["target_validation_loss_total"]),
        "late_min_step": late_min_step,
        "rows": rows,
        "late_rows": late_rows,
        "final_checkpoint": round_checkpoint(rows[-1]),
    }


def build_gate_specs() -> list[dict[str, object]]:
    return [
        {
            "name": "final_validation",
            "description": "Pick the best validation checkpoint across the whole trajectory.",
            "late_only": False,
            "objective": "validation",
        },
        {
            "name": "late_special_unconstrained",
            "description": "Pick the best special checkpoint in the late window without any guard.",
            "late_only": True,
            "objective": "special",
        },
        {
            "name": "late_special_validation_guard_1p25",
            "description": "Late-window special gate with a 1.25x validation guard relative to the experiment's best validation.",
            "late_only": True,
            "validation_guard_ratio": 1.25,
            "objective": "special",
        },
        {
            "name": "late_special_event_priority",
            "description": "Late-window special gate with validation guard 1.25x and strong e_evt floor 1.0.",
            "late_only": True,
            "validation_guard_ratio": 1.25,
            "min_zero_e_evt_delta": 1.0,
            "objective": "special",
        },
        {
            "name": "late_special_dual_control_relaxed",
            "description": "Late-window special gate with relaxed 1.5x validation guard plus dual-control floors z_art>=0.3 and e_evt>=0.5.",
            "late_only": True,
            "validation_guard_ratio": 1.5,
            "min_zero_z_art_delta": 0.3,
            "min_zero_e_evt_delta": 0.5,
            "objective": "special",
        },
        {
            "name": "late_special_strict_positive_control",
            "description": "Late-window special gate with 1.25x validation guard and positive-control floors z_art>=0.1 and e_evt>=0.5.",
            "late_only": True,
            "validation_guard_ratio": 1.25,
            "min_zero_z_art_delta": 0.1,
            "min_zero_e_evt_delta": 0.5,
            "objective": "special",
        },
    ]


def evaluate_gate(
    gate_spec: dict[str, object],
    experiments: list[dict[str, object]],
    anchor: dict[str, object],
) -> dict[str, object]:
    selections: list[dict[str, object]] = []
    for experiment in experiments:
        selected = select_checkpoint_for_gate(experiment=experiment, gate_spec=gate_spec)
        final_checkpoint = experiment["final_checkpoint"]
        selection_payload = {
            "experiment_id": experiment["experiment_id"],
            "selected": None if selected is None else build_delta_payload(selected, final_checkpoint, anchor),
            "final_checkpoint": final_checkpoint,
            "selected_is_final": (
                None
                if selected is None
                else int(selected["step"]) == int(final_checkpoint["step"])
            ),
            "candidate_pool_size": count_candidate_pool(experiment=experiment, gate_spec=gate_spec),
        }
        selections.append(selection_payload)

    selected_payloads = [item["selected"] for item in selections if item["selected"] is not None]
    non_anchor_selected_payloads = [
        item["selected"]
        for item in selections
        if item["selected"] is not None and str(item["experiment_id"]) != str(anchor["experiment_id"])
    ]
    return {
        "name": str(gate_spec["name"]),
        "description": str(gate_spec["description"]),
        "parameters": {
            "late_only": bool(gate_spec.get("late_only", False)),
            "validation_guard_ratio": gate_spec.get("validation_guard_ratio"),
            "min_zero_z_art_delta": gate_spec.get("min_zero_z_art_delta"),
            "min_zero_e_evt_delta": gate_spec.get("min_zero_e_evt_delta"),
            "objective": str(gate_spec["objective"]),
        },
        "selection_count": len(selected_payloads),
        "selections": selections,
        "aggregate": build_gate_aggregate(
            selected_payloads=selected_payloads,
            non_anchor_selected_payloads=non_anchor_selected_payloads,
        ),
    }


def count_candidate_pool(
    experiment: dict[str, object],
    gate_spec: dict[str, object],
) -> int:
    return len(filter_rows_for_gate(experiment=experiment, gate_spec=gate_spec))


def select_checkpoint_for_gate(
    experiment: dict[str, object],
    gate_spec: dict[str, object],
) -> dict[str, object] | None:
    candidate_rows = filter_rows_for_gate(experiment=experiment, gate_spec=gate_spec)
    if not candidate_rows:
        return None
    objective = str(gate_spec["objective"])
    if objective == "validation":
        row = min(
            candidate_rows,
            key=lambda item: (
                float(item["target_validation_loss_total"]),
                float(item["delta_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
            ),
        )
    elif objective == "special":
        row = min(
            candidate_rows,
            key=lambda item: (
                float(item["delta_loss_total"]),
                float(item["target_validation_loss_total"]),
                -float(item["zero_e_evt_delta_target_loss_total"]),
            ),
        )
    else:
        raise ValueError(f"Unsupported gate objective: {objective}")
    return round_checkpoint(row)


def filter_rows_for_gate(
    experiment: dict[str, object],
    gate_spec: dict[str, object],
) -> list[dict[str, object]]:
    rows = experiment["late_rows"] if bool(gate_spec.get("late_only", False)) else experiment["rows"]
    filtered: list[dict[str, object]] = []
    validation_guard_ratio = gate_spec.get("validation_guard_ratio")
    min_zero_z_art_delta = gate_spec.get("min_zero_z_art_delta")
    min_zero_e_evt_delta = gate_spec.get("min_zero_e_evt_delta")
    best_validation_loss_total = float(experiment["best_validation_loss_total"])
    for row in rows:
        if validation_guard_ratio is not None:
            if float(row["target_validation_loss_total"]) > best_validation_loss_total * float(validation_guard_ratio):
                continue
        if min_zero_z_art_delta is not None:
            if float(row["zero_z_art_delta_target_loss_total"]) < float(min_zero_z_art_delta):
                continue
        if min_zero_e_evt_delta is not None:
            if float(row["zero_e_evt_delta_target_loss_total"]) < float(min_zero_e_evt_delta):
                continue
        filtered.append(row)
    return filtered


def build_delta_payload(
    selected: dict[str, object],
    final_checkpoint: dict[str, object],
    anchor: dict[str, object],
) -> dict[str, object]:
    payload = dict(selected)
    payload["delta_vs_final"] = {
        "target_validation_loss_total": round(
            float(selected["target_validation_loss_total"]) - float(final_checkpoint["target_validation_loss_total"]),
            6,
        ),
        "delta_loss_total": round(
            float(selected["delta_loss_total"]) - float(final_checkpoint["delta_loss_total"]),
            6,
        ),
        "zero_e_evt_delta_target_loss_total": round(
            float(selected["zero_e_evt_delta_target_loss_total"])
            - float(final_checkpoint["zero_e_evt_delta_target_loss_total"]),
            6,
        ),
        "zero_z_art_delta_target_loss_total": round(
            float(selected["zero_z_art_delta_target_loss_total"])
            - float(final_checkpoint["zero_z_art_delta_target_loss_total"]),
            6,
        ),
    }
    payload["delta_vs_anchor_final"] = {
        "target_validation_loss_total": round(
            float(selected["target_validation_loss_total"]) - float(anchor["target_validation_loss_total"]),
            6,
        ),
        "delta_loss_total": round(
            float(selected["delta_loss_total"]) - float(anchor["delta_loss_total"]),
            6,
        ),
        "zero_e_evt_delta_target_loss_total": round(
            float(selected["zero_e_evt_delta_target_loss_total"])
            - float(anchor["zero_e_evt_delta_target_loss_total"]),
            6,
        ),
        "zero_z_art_delta_target_loss_total": round(
            float(selected["zero_z_art_delta_target_loss_total"])
            - float(anchor["zero_z_art_delta_target_loss_total"]),
            6,
        ),
    }
    payload["beats_anchor_on_validation"] = (
        float(selected["target_validation_loss_total"]) <= float(anchor["target_validation_loss_total"])
    )
    payload["beats_anchor_on_special"] = float(selected["delta_loss_total"]) <= float(anchor["delta_loss_total"])
    payload["beats_anchor_on_e_evt"] = (
        float(selected["zero_e_evt_delta_target_loss_total"]) >= float(anchor["zero_e_evt_delta_target_loss_total"])
    )
    payload["beats_anchor_on_z_art"] = (
        float(selected["zero_z_art_delta_target_loss_total"]) >= float(anchor["zero_z_art_delta_target_loss_total"])
    )
    payload["beats_anchor_jointly"] = (
        payload["beats_anchor_on_validation"]
        and payload["beats_anchor_on_special"]
        and payload["beats_anchor_on_e_evt"]
        and payload["beats_anchor_on_z_art"]
    )
    return payload


def round_checkpoint(row: dict[str, object]) -> dict[str, object]:
    return {
        "step": int(row["step"]),
        "checkpoint_path": str(row["checkpoint_path"]),
        "target_validation_loss_total": round(float(row["target_validation_loss_total"]), 6),
        "target_special_eval_loss_total": round(float(row["target_special_eval_loss_total"]), 6),
        "delta_loss_total": round(float(row["delta_loss_total"]), 6),
        "zero_e_evt_delta_target_loss_total": round(float(row["zero_e_evt_delta_target_loss_total"]), 6),
        "zero_z_art_delta_target_loss_total": round(float(row["zero_z_art_delta_target_loss_total"]), 6),
    }


def build_gate_aggregate(
    selected_payloads: list[dict[str, object]],
    non_anchor_selected_payloads: list[dict[str, object]],
) -> dict[str, object]:
    if not selected_payloads:
        return {
            "mean_delta_vs_final_validation": None,
            "mean_delta_vs_final_special": None,
            "mean_delta_vs_final_e_evt": None,
            "mean_delta_vs_final_z_art": None,
            "improved_special_vs_final_count": 0,
            "improved_validation_vs_final_count": 0,
            "joint_anchor_beating_count": 0,
            "non_anchor_joint_beating_count": 0,
        }
    count = len(selected_payloads)
    return {
        "mean_delta_vs_final_validation": round(
            sum(float(item["delta_vs_final"]["target_validation_loss_total"]) for item in selected_payloads) / count,
            6,
        ),
        "mean_delta_vs_final_special": round(
            sum(float(item["delta_vs_final"]["delta_loss_total"]) for item in selected_payloads) / count,
            6,
        ),
        "mean_delta_vs_final_e_evt": round(
            sum(float(item["delta_vs_final"]["zero_e_evt_delta_target_loss_total"]) for item in selected_payloads)
            / count,
            6,
        ),
        "mean_delta_vs_final_z_art": round(
            sum(float(item["delta_vs_final"]["zero_z_art_delta_target_loss_total"]) for item in selected_payloads)
            / count,
            6,
        ),
        "improved_special_vs_final_count": sum(
            1 for item in selected_payloads if float(item["delta_vs_final"]["delta_loss_total"]) < 0.0
        ),
        "improved_validation_vs_final_count": sum(
            1 for item in selected_payloads if float(item["delta_vs_final"]["target_validation_loss_total"]) < 0.0
        ),
        "joint_anchor_beating_count": sum(1 for item in selected_payloads if bool(item["beats_anchor_jointly"])),
        "non_anchor_joint_beating_count": sum(
            1 for item in non_anchor_selected_payloads if bool(item["beats_anchor_jointly"])
        ),
    }


def build_recommendation(gate_results: list[dict[str, object]]) -> dict[str, object]:
    strongest_special = min(
        gate_results,
        key=lambda gate: (
            float("inf")
            if gate["aggregate"]["mean_delta_vs_final_special"] is None
            else float(gate["aggregate"]["mean_delta_vs_final_special"]),
            float("inf")
            if gate["aggregate"]["mean_delta_vs_final_validation"] is None
            else float(gate["aggregate"]["mean_delta_vs_final_validation"]),
        ),
    )
    most_conservative = min(
        gate_results,
        key=lambda gate: (
            float("inf")
            if gate["aggregate"]["mean_delta_vs_final_validation"] is None
            else abs(float(gate["aggregate"]["mean_delta_vs_final_validation"])),
            float("inf")
            if gate["aggregate"]["mean_delta_vs_final_special"] is None
            else abs(float(gate["aggregate"]["mean_delta_vs_final_special"])),
        ),
    )
    strict_feasible = next(
        (gate for gate in gate_results if gate["name"] == "late_special_strict_positive_control"),
        None,
    )
    return {
        "strongest_special_gate": {
            "name": strongest_special["name"],
            "aggregate": strongest_special["aggregate"],
        },
        "most_conservative_gate": {
            "name": most_conservative["name"],
            "aggregate": most_conservative["aggregate"],
        },
        "strict_positive_control_gate": None
        if strict_feasible is None
        else {
            "name": strict_feasible["name"],
            "aggregate": strict_feasible["aggregate"],
        },
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP checkpoint gate replay",
        "",
        f"- experiment_count: {summary['experiment_count']}",
        f"- gate_count: {summary['gate_count']}",
        f"- late_step_ratio: {summary['late_step_ratio']}",
        "",
        "## anchor",
        format_checkpoint_line("anchor_final_checkpoint", summary["anchor_final_checkpoint"]),
        "",
        "## recommendation",
        f"- strongest_special_gate: {summary['recommendation']['strongest_special_gate']}",
        f"- most_conservative_gate: {summary['recommendation']['most_conservative_gate']}",
        f"- strict_positive_control_gate: {summary['recommendation']['strict_positive_control_gate']}",
        "",
        "## gates",
    ]
    for gate in summary["gates"]:
        lines.extend(
            [
                f"### {gate['name']}",
                f"- description: {gate['description']}",
                f"- parameters: {gate['parameters']}",
                f"- aggregate: {gate['aggregate']}",
                "- selections:",
            ]
        )
        for selection in gate["selections"]:
            if selection["selected"] is None:
                lines.append(
                    f"  - {selection['experiment_id']}: null (candidate_pool_size={selection['candidate_pool_size']})"
                )
                continue
            lines.append(
                "  - "
                + format_selection_line(
                    experiment_id=str(selection["experiment_id"]),
                    selected=selection["selected"],
                    selected_is_final=selection["selected_is_final"],
                    candidate_pool_size=int(selection["candidate_pool_size"]),
                )
            )
        lines.append("")
    lines.extend(["## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_checkpoint_line(label: str, payload: dict[str, object]) -> str:
    return (
        f"- {label}: step {payload['step']} "
        f"(val={payload['target_validation_loss_total']}, special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )


def format_selection_line(
    experiment_id: str,
    selected: dict[str, object],
    selected_is_final: bool | None,
    candidate_pool_size: int,
) -> str:
    return (
        f"{experiment_id}: step {selected['step']} "
        f"(val={selected['target_validation_loss_total']}, special_delta={selected['delta_loss_total']}, "
        f"zero_e_evt={selected['zero_e_evt_delta_target_loss_total']}, zero_z_art={selected['zero_z_art_delta_target_loss_total']}, "
        f"selected_is_final={selected_is_final}, candidate_pool_size={candidate_pool_size}, "
        f"delta_vs_final={selected['delta_vs_final']}, beats_anchor_jointly={selected['beats_anchor_jointly']})"
    )
