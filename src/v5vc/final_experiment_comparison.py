from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.anchor_selection_analysis import load_anchor_candidate, round_anchor
from v5vc.data_scan import write_json


def compare_offline_mvp_final_experiments(
    experiment_metrics_paths: list[Path],
    output_dir: Path,
    route_selection_path: Path | None = None,
) -> None:
    if not experiment_metrics_paths:
        raise ValueError("At least one experiment metrics path is required.")

    resolved_paths = [path.resolve() for path in experiment_metrics_paths]
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    experiments = [round_anchor(load_anchor_candidate(path)) for path in resolved_paths]
    route_context = load_route_context(route_selection_path)
    summary = build_summary(experiments=experiments, route_context=route_context, output_dir=output_dir)
    write_json(output_dir / "final_experiment_comparison.json", summary)
    (output_dir / "final_experiment_comparison.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_route_context(route_selection_path: Path | None) -> dict[str, object] | None:
    if route_selection_path is None:
        return None
    payload = json.loads(route_selection_path.resolve().read_text(encoding="utf-8"))
    selected_anchor = payload.get("selected_anchor", {})
    return {
        "route_selection_path": route_selection_path.resolve().as_posix(),
        "inputs": payload.get("inputs", {}),
        "selected_policy": payload.get("selected_policy", {}).get("policy_name", ""),
        "selected_anchor_id": selected_anchor.get("experiment_id", ""),
    }


def build_summary(
    experiments: list[dict[str, object]],
    route_context: dict[str, object] | None,
    output_dir: Path,
) -> dict[str, object]:
    by_validation = sorted(
        experiments,
        key=lambda item: (
            float(item["target_validation_loss_total"]),
            float(item["delta_loss_total"]),
            -float(item["zero_e_evt_delta_target_loss_total"]),
        ),
    )
    by_special = sorted(
        experiments,
        key=lambda item: (
            float(item["delta_loss_total"]),
            float(item["target_validation_loss_total"]),
            -float(item["zero_z_art_delta_target_loss_total"]),
        ),
    )
    route_anchor = None
    if route_context is not None:
        route_anchor = next(
            (experiment for experiment in experiments if str(experiment["experiment_id"]) == str(route_context["selected_anchor_id"])),
            None,
        )
    rows = [build_row(experiment=experiment, route_anchor=route_anchor) for experiment in by_validation]
    return {
        "output_dir": output_dir.as_posix(),
        "experiment_count": len(experiments),
        "route_context": route_context,
        "leaders": {
            "validation": by_validation[0],
            "special": by_special[0],
            "zero_e_evt": max(experiments, key=lambda item: float(item["zero_e_evt_delta_target_loss_total"])),
            "zero_z_art": max(experiments, key=lambda item: float(item["zero_z_art_delta_target_loss_total"])),
        },
        "rows": rows,
        "notes": [
            "Rows are sorted by final target validation loss, then special delta, then e_evt.",
            "When route_context is present, delta_vs_route_anchor compares each final experiment against the selected route anchor.",
        ],
    }


def build_row(
    experiment: dict[str, object],
    route_anchor: dict[str, object] | None,
) -> dict[str, object]:
    row = dict(experiment)
    row["is_route_anchor"] = bool(
        route_anchor is not None and str(experiment["experiment_id"]) == str(route_anchor["experiment_id"])
    )
    if route_anchor is None:
        row["delta_vs_route_anchor"] = None
    else:
        row["delta_vs_route_anchor"] = {
            "target_validation_loss_total": round(
                float(experiment["target_validation_loss_total"]) - float(route_anchor["target_validation_loss_total"]),
                6,
            ),
            "delta_loss_total": round(
                float(experiment["delta_loss_total"]) - float(route_anchor["delta_loss_total"]),
                6,
            ),
            "zero_e_evt_delta_target_loss_total": round(
                float(experiment["zero_e_evt_delta_target_loss_total"])
                - float(route_anchor["zero_e_evt_delta_target_loss_total"]),
                6,
            ),
            "zero_z_art_delta_target_loss_total": round(
                float(experiment["zero_z_art_delta_target_loss_total"])
                - float(route_anchor["zero_z_art_delta_target_loss_total"]),
                6,
            ),
        }
    return row


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP final experiment comparison",
        "",
        f"- experiment_count: {summary['experiment_count']}",
    ]
    if summary["route_context"] is not None:
        lines.append(f"- route_context: {summary['route_context']}")
    lines.extend(
        [
            "",
            "## leaders",
            format_experiment_line("validation", summary["leaders"]["validation"]),
            format_experiment_line("special", summary["leaders"]["special"]),
            format_experiment_line("zero_e_evt", summary["leaders"]["zero_e_evt"]),
            format_experiment_line("zero_z_art", summary["leaders"]["zero_z_art"]),
            "",
            "## rows",
        ]
    )
    for row in summary["rows"]:
        suffix = ""
        if row["is_route_anchor"]:
            suffix = " [route_anchor]"
        line = format_experiment_line(str(row["experiment_id"]), row) + suffix
        if row["delta_vs_route_anchor"] is not None:
            line += f" [vs_route={row['delta_vs_route_anchor']}]"
        lines.append(line)
    lines.extend(["", "## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def format_experiment_line(label: str, payload: dict[str, object]) -> str:
    return (
        f"- {label}: {payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )
