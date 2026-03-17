from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.ablation_eval import load_experiment_metrics_payload, resolve_split_dir
from v5vc.checkpoint_series_eval import infer_checkpoint_step, resolve_checkpoint_paths
from v5vc.data_scan import write_json
from v5vc.special_eval import build_model_markdown, build_model_special_eval_result


def evaluate_offline_mvp_special_eval_series(
    config_path: Path,
    experiment_metrics_path: Path,
    output_dir: Path,
    split_dir: Path | None,
    steps: list[int] | None,
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
    selected_checkpoints = select_checkpoints(checkpoint_paths, steps)

    checkpoint_results: list[dict[str, object]] = []
    checkpoints_dir = output_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    for checkpoint_path in selected_checkpoints:
        result = build_model_special_eval_result(
            config_path=config_path,
            config=config,
            split_dir=resolved_split_dir,
            checkpoint_path=checkpoint_path,
        )
        step = infer_checkpoint_step(checkpoint_path)
        checkpoint_results.append(
            {
                "step": step,
                "checkpoint_path": checkpoint_path.as_posix(),
                "result": result,
            }
        )
        step_dir = checkpoints_dir / f"step{step}"
        step_dir.mkdir(parents=True, exist_ok=True)
        write_json(step_dir / "special_eval_model.json", result)
        (step_dir / "special_eval_model.md").write_text(
            build_model_markdown(result),
            encoding="utf-8",
            newline="\n",
        )

    checkpoint_results.sort(key=lambda item: item["step"])
    summary = {
        "config_path": config_path.as_posix(),
        "experiment_metrics_path": experiment_metrics_path.as_posix(),
        "split_dir": resolved_split_dir.as_posix(),
        "selected_steps": [item["step"] for item in checkpoint_results],
        "checkpoint_count": len(checkpoint_results),
        "checkpoints": [
            {
                "step": item["step"],
                "checkpoint_path": item["checkpoint_path"],
                "target_validation_loss_total": item["result"]["target_validation"]["metrics"]["loss_total"],
                "target_special_eval_loss_total": item["result"]["target_special_eval"]["metrics"]["loss_total"],
                "delta_loss_total": item["result"]["comparisons"]["delta_loss_total"],
                "delta_loss_text_aux": item["result"]["comparisons"]["delta_loss_text_aux"],
                "delta_loss_text_aux_effective": item["result"]["comparisons"]["delta_loss_text_aux_effective"],
                "delta_loss_text_aux_structural": item["result"]["comparisons"]["delta_loss_text_aux_structural"],
                "delta_loss_text_aux_lexical": item["result"]["comparisons"]["delta_loss_text_aux_lexical"],
                "delta_loss_structural_clause_transition_aux": item["result"]["comparisons"][
                    "delta_loss_structural_clause_transition_aux"
                ],
                "delta_loss_boundary_contrast_aux": item["result"]["comparisons"]["delta_loss_boundary_contrast_aux"],
                "delta_loss_punctuation_profile_aux": item["result"]["comparisons"]["delta_loss_punctuation_profile_aux"],
                "delta_loss_structural_clause_profile_aux": item["result"]["comparisons"][
                    "delta_loss_structural_clause_profile_aux"
                ],
                "delta_loss_challenge_proxy_profile_aux": item["result"]["comparisons"][
                    "delta_loss_challenge_proxy_profile_aux"
                ],
                "delta_loss_z_art_influence_aux": item["result"]["comparisons"]["delta_loss_z_art_influence_aux"],
                "delta_loss_formal_special_clause_shape_aux": item["result"]["comparisons"][
                    "delta_loss_formal_special_clause_shape_aux"
                ],
                "target_validation_event_prob_mean": item["result"]["target_validation"]["output_stats"]["event_prob_mean"],
                "target_special_eval_event_prob_mean": item["result"]["target_special_eval"]["output_stats"]["event_prob_mean"],
                "delta_event_presence_prob_mean": item["result"]["comparisons"]["delta_event_presence_prob_mean"],
                "delta_event_fall_prob_mean": item["result"]["comparisons"]["delta_event_fall_prob_mean"],
                "delta_event_energy_prob_mean": item["result"]["comparisons"]["delta_event_energy_prob_mean"],
                "delta_event_presence_peak_ratio": item["result"]["comparisons"]["delta_event_presence_peak_ratio"],
                "delta_z_art_delta_abs_mean": item["result"]["comparisons"]["delta_z_art_delta_abs_mean"],
                "delta_acoustic_energy_mean": item["result"]["comparisons"]["delta_acoustic_energy_mean"],
                "delta_acoustic_delta_abs_mean": item["result"]["comparisons"]["delta_acoustic_delta_abs_mean"],
            }
            for item in checkpoint_results
        ],
        "notes": [
            "Special-eval series summarizes challenge-slice behavior across selected checkpoints.",
            "Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.",
        ],
    }

    write_json(output_dir / "special_eval_series.json", summary)
    (output_dir / "special_eval_series.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    update_experiment_metrics(experiment_metrics_path, summary)


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def select_checkpoints(checkpoint_paths: list[Path], steps: list[int] | None) -> list[Path]:
    if not steps:
        return checkpoint_paths
    step_set = set(steps)
    selected = [path for path in checkpoint_paths if infer_checkpoint_step(path) in step_set]
    if len(selected) != len(step_set):
        found_steps = {infer_checkpoint_step(path) for path in selected}
        missing = sorted(step_set - found_steps)
        raise ValueError(f"Requested special-eval series steps not found in checkpoint paths: {missing}")
    return selected


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP special_eval checkpoint 系列汇总",
        "",
        f"- config_path: {summary['config_path']}",
        f"- experiment_metrics_path: {summary['experiment_metrics_path']}",
        f"- split_dir: {summary['split_dir']}",
        f"- selected_steps: {summary['selected_steps']}",
        f"- checkpoint_count: {summary['checkpoint_count']}",
        "",
        "## checkpoints",
    ]
    for checkpoint in summary["checkpoints"]:
        lines.extend(
            [
                f"### step {checkpoint['step']}",
                f"- checkpoint_path: {checkpoint['checkpoint_path']}",
                f"- target_validation.loss_total: {checkpoint['target_validation_loss_total']}",
                f"- target_special_eval.loss_total: {checkpoint['target_special_eval_loss_total']}",
                f"- delta_loss_total: {checkpoint['delta_loss_total']}",
                f"- delta_loss_text_aux: {checkpoint['delta_loss_text_aux']}",
                f"- delta_loss_text_aux_effective: {checkpoint['delta_loss_text_aux_effective']}",
                f"- delta_loss_text_aux_structural: {checkpoint['delta_loss_text_aux_structural']}",
                f"- delta_loss_text_aux_lexical: {checkpoint['delta_loss_text_aux_lexical']}",
                f"- delta_loss_structural_clause_transition_aux: {checkpoint['delta_loss_structural_clause_transition_aux']}",
                f"- delta_loss_boundary_contrast_aux: {checkpoint['delta_loss_boundary_contrast_aux']}",
                f"- delta_loss_punctuation_profile_aux: {checkpoint['delta_loss_punctuation_profile_aux']}",
                f"- delta_loss_structural_clause_profile_aux: {checkpoint['delta_loss_structural_clause_profile_aux']}",
                f"- delta_loss_challenge_proxy_profile_aux: {checkpoint['delta_loss_challenge_proxy_profile_aux']}",
                f"- delta_loss_z_art_influence_aux: {checkpoint['delta_loss_z_art_influence_aux']}",
                f"- delta_loss_formal_special_clause_shape_aux: {checkpoint['delta_loss_formal_special_clause_shape_aux']}",
                f"- target_validation.event_prob_mean: {checkpoint['target_validation_event_prob_mean']}",
                f"- target_special_eval.event_prob_mean: {checkpoint['target_special_eval_event_prob_mean']}",
                f"- delta_event_presence_prob_mean: {checkpoint['delta_event_presence_prob_mean']}",
                f"- delta_event_fall_prob_mean: {checkpoint['delta_event_fall_prob_mean']}",
                f"- delta_event_energy_prob_mean: {checkpoint['delta_event_energy_prob_mean']}",
                f"- delta_event_presence_peak_ratio: {checkpoint['delta_event_presence_peak_ratio']}",
                f"- delta_z_art_delta_abs_mean: {checkpoint['delta_z_art_delta_abs_mean']}",
                f"- delta_acoustic_energy_mean: {checkpoint['delta_acoustic_energy_mean']}",
                f"- delta_acoustic_delta_abs_mean: {checkpoint['delta_acoustic_delta_abs_mean']}",
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
    payload["metrics"]["special_eval_series"] = result
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
