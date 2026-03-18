from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from v5vc.data_scan import write_json
from v5vc.nores_vocoder_checkpoint_review import build_checkpoint_rows, build_pairwise_reviews


def select_offline_mvp_nores_vocoder_checkpoint(
    summary_path: Path,
    output_dir: Path,
    late_step_ratio: float,
    validation_guard_ratio: float,
    max_pairwise_worsened_ratio: float,
    max_rms_ratio_deviation: float,
) -> None:
    if late_step_ratio <= 0.0 or late_step_ratio > 1.0:
        raise ValueError("late_step_ratio must be within (0.0, 1.0].")
    if validation_guard_ratio < 1.0:
        raise ValueError("validation_guard_ratio must be >= 1.0.")
    if max_pairwise_worsened_ratio < 0.0 or max_pairwise_worsened_ratio > 1.0:
        raise ValueError("max_pairwise_worsened_ratio must be within [0.0, 1.0].")
    if max_rms_ratio_deviation < 0.0:
        raise ValueError("max_rms_ratio_deviation must be >= 0.0.")

    summary_path = summary_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    validation_history = payload.get("validation_history", [])
    if not isinstance(validation_history, list) or not validation_history:
        raise ValueError("Dataset loop summary does not contain validation_history.")

    checkpoints = build_checkpoint_rows(validation_history)
    pairwise_reviews = build_pairwise_reviews(checkpoints, top_k=10)
    pairwise_review_by_to_step = {
        int(item["to_step"]): item
        for item in pairwise_reviews
    }

    max_step = max(int(item["step"]) for item in checkpoints)
    late_min_step = max(
        min(int(item["step"]) for item in checkpoints),
        int(math.ceil(max_step * late_step_ratio)),
    )
    late_checkpoints = [item for item in checkpoints if int(item["step"]) >= late_min_step]
    if not late_checkpoints:
        late_checkpoints = checkpoints[-1:]

    best_validation_checkpoint = min(
        checkpoints,
        key=lambda item: (
            float(item["loss_metrics"]["loss_total"]),
            abs(float(item["loss_metrics"].get("decoded_to_target_rms_ratio", 0.0)) - 1.0),
            int(item["step"]),
        ),
    )
    best_rms_checkpoint = min(
        checkpoints,
        key=lambda item: (
            abs(float(item["loss_metrics"].get("decoded_to_target_rms_ratio", 0.0)) - 1.0),
            float(item["loss_metrics"]["loss_total"]),
            -int(item["step"]),
        ),
    )

    validation_guard_threshold = (
        float(best_validation_checkpoint["loss_metrics"]["loss_total"]) * float(validation_guard_ratio)
    )
    late_candidates = []
    for checkpoint in late_checkpoints:
        step = int(checkpoint["step"])
        pairwise_review = pairwise_review_by_to_step.get(step)
        rms_ratio = float(checkpoint["loss_metrics"].get("decoded_to_target_rms_ratio", 0.0))
        candidate = {
            "step": step,
            "loss_total": round(float(checkpoint["loss_metrics"]["loss_total"]), 6),
            "decoded_to_target_rms_ratio": round(rms_ratio, 6),
            "rms_ratio_deviation": round(abs(rms_ratio - 1.0), 6),
            "within_validation_guard": float(checkpoint["loss_metrics"]["loss_total"]) <= validation_guard_threshold,
            "pairwise_review": (
                None
                if pairwise_review is None
                else {
                    "from_step": int(pairwise_review["from_step"]),
                    "to_step": int(pairwise_review["to_step"]),
                    "improved_count": int(pairwise_review["improved_count"]),
                    "worsened_count": int(pairwise_review["worsened_count"]),
                    "record_count": int(pairwise_review["record_count"]),
                    "worsened_ratio": round(float(pairwise_review["worsened_ratio"]), 6),
                    "average_delta_loss_total": round(float(pairwise_review["average_delta_loss_total"]), 6),
                }
            ),
        }
        pairwise_worsened_ratio = (
            0.0 if pairwise_review is None else float(pairwise_review["worsened_ratio"])
        )
        candidate["qualifies_as_stable_late_stop"] = bool(
            candidate["within_validation_guard"]
            and pairwise_worsened_ratio <= float(max_pairwise_worsened_ratio)
            and abs(rms_ratio - 1.0) <= float(max_rms_ratio_deviation)
        )
        late_candidates.append(candidate)

    stable_late_candidates = [item for item in late_candidates if bool(item["qualifies_as_stable_late_stop"])]
    selected_stable_late_stop = (
        None
        if not stable_late_candidates
        else max(
            stable_late_candidates,
            key=lambda item: (
                int(item["step"]),
                -float(item["loss_total"]),
            ),
        )
    )

    summary = {
        "summary_path": summary_path.as_posix(),
        "output_dir": output_dir.as_posix(),
        "dataset": payload.get("dataset", {}),
        "runtime": payload.get("runtime", {}),
        "training": payload.get("training", {}),
        "selection_policy": {
            "late_step_ratio": float(late_step_ratio),
            "late_min_step": int(late_min_step),
            "validation_guard_ratio": float(validation_guard_ratio),
            "validation_guard_threshold": round(validation_guard_threshold, 6),
            "max_pairwise_worsened_ratio": float(max_pairwise_worsened_ratio),
            "max_rms_ratio_deviation": float(max_rms_ratio_deviation),
        },
        "best_validation_checkpoint": build_checkpoint_selection_row(best_validation_checkpoint),
        "best_rms_checkpoint": build_checkpoint_selection_row(best_rms_checkpoint),
        "late_candidates": late_candidates,
        "selected_stable_late_stop": selected_stable_late_stop,
        "notes": [
            "best_validation_checkpoint is the recorded checkpoint with minimum validation loss_total.",
            "best_rms_checkpoint prefers decoded_to_target_rms_ratio closest to 1.0, then lower validation loss_total.",
            "selected_stable_late_stop keeps only late-window checkpoints that stay within the validation guard, keep pairwise worsened_ratio under the configured cap, and keep RMS ratio deviation under the configured cap.",
        ],
    }
    write_json(output_dir / "nores_vocoder_checkpoint_selection.json", summary)
    (output_dir / "nores_vocoder_checkpoint_selection.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_checkpoint_selection_row(checkpoint: dict[str, object]) -> dict[str, object]:
    loss_metrics = dict(checkpoint["loss_metrics"])
    rms_ratio = float(loss_metrics.get("decoded_to_target_rms_ratio", 0.0))
    return {
        "step": int(checkpoint["step"]),
        "loss_total": round(float(loss_metrics["loss_total"]), 6),
        "loss_waveform": round(float(loss_metrics.get("loss_waveform", 0.0)), 6),
        "loss_stft": round(float(loss_metrics.get("loss_stft", 0.0)), 6),
        "loss_rms_guard": round(float(loss_metrics.get("loss_rms_guard", 0.0)), 6),
        "decoded_to_target_rms_ratio": round(rms_ratio, 6),
        "rms_ratio_deviation": round(abs(rms_ratio - 1.0), 6),
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Checkpoint Selection",
        "",
        f"- summary_path: {summary['summary_path']}",
        f"- dataset: {json.dumps(summary['dataset'], ensure_ascii=False)}",
        f"- runtime: {json.dumps(summary['runtime'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        f"- selection_policy: {json.dumps(summary['selection_policy'], ensure_ascii=False)}",
        f"- best_validation_checkpoint: {json.dumps(summary['best_validation_checkpoint'], ensure_ascii=False)}",
        f"- best_rms_checkpoint: {json.dumps(summary['best_rms_checkpoint'], ensure_ascii=False)}",
        f"- selected_stable_late_stop: {json.dumps(summary['selected_stable_late_stop'], ensure_ascii=False)}",
        "",
        "## Late Candidates",
    ]
    for candidate in summary["late_candidates"]:
        pairwise_review = candidate.get("pairwise_review")
        pairwise_text = "pairwise_review=null"
        if pairwise_review is not None:
            pairwise_text = (
                f"pairwise={pairwise_review['from_step']}->{pairwise_review['to_step']} "
                f"worsened_ratio={pairwise_review['worsened_ratio']} "
                f"avg_delta={pairwise_review['average_delta_loss_total']}"
            )
        lines.append(
            f"- step={candidate['step']} loss_total={candidate['loss_total']} "
            f"rms_ratio={candidate['decoded_to_target_rms_ratio']} "
            f"rms_ratio_deviation={candidate['rms_ratio_deviation']} "
            f"within_validation_guard={candidate['within_validation_guard']} "
            f"qualifies_as_stable_late_stop={candidate['qualifies_as_stable_late_stop']} "
            f"{pairwise_text}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
