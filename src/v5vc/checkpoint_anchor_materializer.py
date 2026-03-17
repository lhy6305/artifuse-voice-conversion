from __future__ import annotations

from datetime import datetime
from pathlib import Path

from v5vc.ablation_eval import load_experiment_metrics_payload
from v5vc.data_scan import write_json


def materialize_offline_mvp_checkpoint_anchor(
    experiment_metrics_path: Path,
    step: int,
    output_path: Path,
) -> None:
    if step <= 0:
        raise ValueError("step must be > 0.")

    experiment_metrics_path = experiment_metrics_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = load_experiment_metrics_payload(experiment_metrics_path)
    checkpoint_anchor = build_checkpoint_anchor_payload(
        payload=payload,
        experiment_metrics_path=experiment_metrics_path,
        step=step,
    )
    write_json(output_path, checkpoint_anchor)
    output_path.with_suffix(".md").write_text(
        build_markdown(checkpoint_anchor),
        encoding="utf-8",
        newline="\n",
    )


def build_checkpoint_anchor_payload(
    payload: dict[str, object],
    experiment_metrics_path: Path,
    step: int,
) -> dict[str, object]:
    metrics = payload.get("metrics", {})
    special_eval_series = expect_dict(metrics.get("special_eval_series"), "metrics.special_eval_series")
    checkpoint_series_eval = expect_dict(metrics.get("checkpoint_series_eval"), "metrics.checkpoint_series_eval")

    special_checkpoint = find_step_entry(
        items=special_eval_series.get("checkpoints", []),
        step=step,
        field_name="metrics.special_eval_series.checkpoints",
    )
    ablation_checkpoint = find_step_entry(
        items=checkpoint_series_eval.get("checkpoints", []),
        step=step,
        field_name="metrics.checkpoint_series_eval.checkpoints",
    )

    experiment_id = str(payload.get("experiment_id", experiment_metrics_path.stem.replace(".metrics", "")))
    checkpoint_path = str(special_checkpoint.get("checkpoint_path", ""))
    if not checkpoint_path:
        raise ValueError(f"{experiment_metrics_path.as_posix()} step {step} is missing checkpoint_path.")

    zero_e_evt = expect_dict(ablation_checkpoint.get("comparisons", {}).get("zero_e_evt"), "zero_e_evt")
    zero_z_art = expect_dict(ablation_checkpoint.get("comparisons", {}).get("zero_z_art"), "zero_z_art")

    return {
        "experiment_id": f"{experiment_id}-checkpoint-step{step}-anchor",
        "status": "checkpoint_anchor_materialized",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "metrics": {
            "training_run": {
                "training_run": {
                    "completed_steps": step,
                },
                "artifacts": {
                    "checkpoint_path": checkpoint_path,
                },
            },
            "target_special_eval_model": {
                "checkpoint_path": checkpoint_path,
                "target_validation": {
                    "metrics": {
                        "loss_total": float(special_checkpoint["target_validation_loss_total"]),
                    }
                },
                "target_special_eval": {
                    "metrics": {
                        "loss_total": float(special_checkpoint["target_special_eval_loss_total"]),
                    }
                },
                "comparisons": {
                    "delta_loss_total": float(special_checkpoint["delta_loss_total"]),
                },
            },
            "ablation_eval": {
                "checkpoint_path": checkpoint_path,
                "comparisons": {
                    "zero_e_evt": {
                        "delta_target_loss_total": float(zero_e_evt["delta_target_loss_total"]),
                    },
                    "zero_z_art": {
                        "delta_target_loss_total": float(zero_z_art["delta_target_loss_total"]),
                    },
                },
            },
        },
        "notes": [
            "This is a synthetic anchor metrics payload materialized from a checkpoint series entry.",
            f"source_experiment_id={experiment_id}",
            f"source_experiment_metrics_path={experiment_metrics_path.as_posix()}",
            f"selected_step={step}",
        ],
    }


def expect_dict(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} is missing or malformed.")
    return value


def find_step_entry(
    items: object,
    step: int,
    field_name: str,
) -> dict[str, object]:
    if not isinstance(items, list):
        raise ValueError(f"{field_name} is missing or malformed.")
    for item in items:
        if isinstance(item, dict) and int(item.get("step", -1)) == step:
            return item
    raise ValueError(f"{field_name} does not contain step={step}.")


def build_markdown(payload: dict[str, object]) -> str:
    metrics = payload["metrics"]
    special_eval = metrics["target_special_eval_model"]
    ablation_eval = metrics["ablation_eval"]
    lines = [
        "# offline MVP checkpoint anchor",
        "",
        f"- experiment_id: {payload['experiment_id']}",
        f"- checkpoint_path: {special_eval['checkpoint_path']}",
        f"- target_validation_loss_total: {special_eval['target_validation']['metrics']['loss_total']}",
        f"- delta_loss_total: {special_eval['comparisons']['delta_loss_total']}",
        f"- zero_e_evt_delta_target_loss_total: {ablation_eval['comparisons']['zero_e_evt']['delta_target_loss_total']}",
        f"- zero_z_art_delta_target_loss_total: {ablation_eval['comparisons']['zero_z_art']['delta_target_loss_total']}",
        "",
        "## notes",
    ]
    for note in payload.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
