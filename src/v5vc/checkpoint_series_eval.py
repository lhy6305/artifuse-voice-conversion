from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
from pathlib import Path

from v5vc.ablation_eval import (
    build_ablation_result,
    load_experiment_metrics_payload,
    resolve_split_dir,
)
from v5vc.data_scan import write_json


def evaluate_offline_mvp_checkpoint_series(
    config_path: Path,
    experiment_metrics_path: Path,
    output_dir: Path,
    split_dir: Path | None,
) -> None:
    config_path = config_path.resolve()
    experiment_metrics_path = experiment_metrics_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    metrics_payload = load_experiment_metrics_payload(experiment_metrics_path)
    project_root = config_path.parent.parent
    resolved_split_dir = resolve_split_dir(project_root=project_root, config=config, split_dir=split_dir)
    checkpoint_paths = resolve_checkpoint_paths(metrics_payload)

    checkpoint_results: list[dict[str, object]] = []
    for checkpoint_path in checkpoint_paths:
        checkpoint_result = build_ablation_result(
            config_path=config_path,
            config=config,
            split_dir=resolved_split_dir,
            checkpoint_path=checkpoint_path,
        )
        checkpoint_results.append(
            {
                "checkpoint_path": checkpoint_path.as_posix(),
                "step": infer_checkpoint_step(checkpoint_path),
                "comparisons": checkpoint_result["comparisons"],
                "baseline": {
                    "target_loss_total": checkpoint_result["ablation_modes"]["none"]["target"]["loss_total"],
                    "source_loss_total": checkpoint_result["ablation_modes"]["none"]["source"]["loss_total"],
                },
            }
        )

    checkpoint_results.sort(key=lambda item: item["step"])
    summary = {
        "config_path": config_path.as_posix(),
        "experiment_metrics_path": experiment_metrics_path.as_posix(),
        "split_dir": resolved_split_dir.as_posix(),
        "checkpoint_count": len(checkpoint_results),
        "checkpoints": checkpoint_results,
        "trends": build_trends(checkpoint_results),
        "notes": [
            "Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.",
            "Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.",
        ],
    }

    write_json(output_dir / "checkpoint_series_eval.json", summary)
    (output_dir / "checkpoint_series_eval.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )

    update_experiment_metrics(experiment_metrics_path, summary)



def resolve_checkpoint_paths(metrics_payload: dict[str, object]) -> list[Path]:
    checkpoint_refs = (
        metrics_payload.get("metrics", {})
        .get("training_run", {})
        .get("artifacts", {})
        .get("checkpoint_paths", [])
    )
    if not checkpoint_refs:
        raise ValueError("No checkpoint_paths found in experiment metrics.")
    return [Path(str(checkpoint_ref)).resolve() for checkpoint_ref in checkpoint_refs]


def infer_checkpoint_step(path: Path) -> int:
    stem = path.stem
    marker = ".step"
    if marker not in stem:
        return -1
    suffix = stem.split(marker, 1)[1]
    return int(suffix)


def build_trends(checkpoints: list[dict[str, object]]) -> dict[str, object]:
    return {
        "zero_z_art_target_loss_deltas": [
            {
                "step": checkpoint["step"],
                "value": checkpoint["comparisons"]["zero_z_art"]["delta_target_loss_total"],
            }
            for checkpoint in checkpoints
        ],
        "zero_e_evt_target_loss_deltas": [
            {
                "step": checkpoint["step"],
                "value": checkpoint["comparisons"]["zero_e_evt"]["delta_target_loss_total"],
            }
            for checkpoint in checkpoints
        ],
        "zero_z_art_source_loss_deltas": [
            {
                "step": checkpoint["step"],
                "value": checkpoint["comparisons"]["zero_z_art"]["delta_source_loss_total"],
            }
            for checkpoint in checkpoints
        ],
        "zero_e_evt_source_loss_deltas": [
            {
                "step": checkpoint["step"],
                "value": checkpoint["comparisons"]["zero_e_evt"]["delta_source_loss_total"],
            }
            for checkpoint in checkpoints
        ],
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP checkpoint 系列消融汇总",
        "",
        f"- config_path: {summary['config_path']}",
        f"- experiment_metrics_path: {summary['experiment_metrics_path']}",
        f"- split_dir: {summary['split_dir']}",
        f"- checkpoint_count: {summary['checkpoint_count']}",
        "",
        "## checkpoints",
    ]
    for checkpoint in summary["checkpoints"]:
        lines.extend(
            [
                f"### step {checkpoint['step']}",
                f"- checkpoint_path: {checkpoint['checkpoint_path']}",
                f"- baseline.target_loss_total: {checkpoint['baseline']['target_loss_total']}",
                f"- baseline.source_loss_total: {checkpoint['baseline']['source_loss_total']}",
                f"- zero_z_art.delta_target_loss_total: {checkpoint['comparisons']['zero_z_art']['delta_target_loss_total']}",
                f"- zero_z_art.delta_source_loss_total: {checkpoint['comparisons']['zero_z_art']['delta_source_loss_total']}",
                f"- zero_e_evt.delta_target_loss_total: {checkpoint['comparisons']['zero_e_evt']['delta_target_loss_total']}",
                f"- zero_e_evt.delta_source_loss_total: {checkpoint['comparisons']['zero_e_evt']['delta_source_loss_total']}",
                "",
            ]
        )
    lines.extend(["## notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def update_experiment_metrics(path: Path, result: dict[str, object]) -> None:
    payload = load_experiment_metrics_payload(path)
    payload.setdefault("metrics", {})
    payload["metrics"]["checkpoint_series_eval"] = result
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
