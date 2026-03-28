from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
from pathlib import Path

from v5vc.data_scan import write_json


def review_offline_mvp_nores_vocoder_checkpoints(
    summary_path: Path,
    output_dir: Path,
    top_k: int,
) -> None:
    summary_path = summary_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    validation_history = payload.get("validation_history", [])
    if not isinstance(validation_history, list) or not validation_history:
        raise ValueError("Dataset loop summary does not contain validation_history.")

    checkpoints = build_checkpoint_rows(validation_history)
    if len(checkpoints) < 2:
        raise ValueError("Checkpoint review requires at least two validation checkpoints.")

    pairwise_reviews = build_pairwise_reviews(checkpoints, top_k=max(1, int(top_k)))
    overall_review = build_overall_review(checkpoints, top_k=max(1, int(top_k)))
    summary = {
        "summary_path": summary_path.as_posix(),
        "output_dir": output_dir.as_posix(),
        "dataset": payload.get("dataset", {}),
        "runtime": payload.get("runtime", {}),
        "training": payload.get("training", {}),
        "checkpoint_count": len(checkpoints),
        "checkpoints": [build_checkpoint_output_row(checkpoint) for checkpoint in checkpoints],
        "pairwise_reviews": pairwise_reviews,
        "overall_review": overall_review,
        "notes": [
            "This review is derived from the dataset-loop summary validation_history payload.",
            "Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.",
            "Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.",
        ],
    }
    write_json(output_dir / "nores_vocoder_checkpoint_review.json", summary)
    (output_dir / "nores_vocoder_checkpoint_review.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )



def build_checkpoint_rows(validation_history: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous_loss_total: float | None = None
    first_loss_total: float | None = None
    for item in sorted(validation_history, key=lambda entry: int(entry["step"])):
        step = int(item["step"])
        loss_metrics = dict(item.get("loss_metrics", {}))
        loss_total = float(loss_metrics.get("loss_total", 0.0))
        if first_loss_total is None:
            first_loss_total = loss_total
        row = {
            "step": step,
            "validation_source": str(item.get("validation_source", "")),
            "package_count": int(item.get("package_count", 0)),
            "loss_metrics": round_loss_metrics(loss_metrics),
            "package_metrics": normalize_package_metrics(item.get("package_metrics", [])),
            "delta_vs_previous_loss_total": (
                None
                if previous_loss_total is None
                else round(loss_total - previous_loss_total, 6)
            ),
            "delta_vs_first_loss_total": round(loss_total - float(first_loss_total), 6),
        }
        rows.append(row)
        previous_loss_total = loss_total
    return rows


def build_pairwise_reviews(
    checkpoints: list[dict[str, object]],
    top_k: int,
) -> list[dict[str, object]]:
    reviews: list[dict[str, object]] = []
    for index in range(1, len(checkpoints)):
        previous = checkpoints[index - 1]
        current = checkpoints[index]
        reviews.append(
            build_record_delta_review(
                previous_step=int(previous["step"]),
                current_step=int(current["step"]),
                previous_package_metrics=extract_package_metrics(previous),
                current_package_metrics=extract_package_metrics(current),
                top_k=top_k,
            )
        )
    return reviews


def build_overall_review(
    checkpoints: list[dict[str, object]],
    top_k: int,
) -> dict[str, object]:
    first = checkpoints[0]
    last = checkpoints[-1]
    return build_record_delta_review(
        previous_step=int(first["step"]),
        current_step=int(last["step"]),
        previous_package_metrics=extract_package_metrics(first),
        current_package_metrics=extract_package_metrics(last),
        top_k=top_k,
    )


def extract_package_metrics(checkpoint: dict[str, object]) -> dict[str, dict[str, float]]:
    package_metrics = checkpoint.get("package_metrics", {})
    if isinstance(package_metrics, dict):
        return package_metrics
    raise TypeError("checkpoint package_metrics must be a dict")


def normalize_package_metrics(package_metrics: object) -> dict[str, dict[str, float]]:
    if not isinstance(package_metrics, list):
        return {}
    normalized: dict[str, dict[str, float]] = {}
    for item in package_metrics:
        if not isinstance(item, dict):
            continue
        record_id = str(item.get("record_id", "")).strip()
        if not record_id:
            continue
        loss_metrics = item.get("loss_metrics", {})
        if not isinstance(loss_metrics, dict):
            continue
        normalized[record_id] = round_loss_metrics(loss_metrics)
    return normalized


def build_record_delta_review(
    previous_step: int,
    current_step: int,
    previous_package_metrics: dict[str, dict[str, float]],
    current_package_metrics: dict[str, dict[str, float]],
    top_k: int,
) -> dict[str, object]:
    shared_record_ids = sorted(set(previous_package_metrics) & set(current_package_metrics))
    deltas: list[dict[str, object]] = []
    for record_id in shared_record_ids:
        previous_loss_total = float(previous_package_metrics[record_id]["loss_total"])
        current_loss_total = float(current_package_metrics[record_id]["loss_total"])
        deltas.append(
            {
                "record_id": record_id,
                "previous_loss_total": round(previous_loss_total, 6),
                "current_loss_total": round(current_loss_total, 6),
                "delta_loss_total": round(current_loss_total - previous_loss_total, 6),
            }
        )

    improved = [item for item in deltas if float(item["delta_loss_total"]) < 0.0]
    worsened = [item for item in deltas if float(item["delta_loss_total"]) > 0.0]
    unchanged = [item for item in deltas if float(item["delta_loss_total"]) == 0.0]
    deltas_sorted = sorted(deltas, key=lambda item: float(item["delta_loss_total"]))
    average_delta = (
        round(sum(float(item["delta_loss_total"]) for item in deltas) / len(deltas), 6)
        if deltas
        else 0.0
    )
    return {
        "from_step": int(previous_step),
        "to_step": int(current_step),
        "record_count": len(deltas),
        "average_delta_loss_total": average_delta,
        "improved_count": len(improved),
        "worsened_count": len(worsened),
        "unchanged_count": len(unchanged),
        "improved_ratio": round((len(improved) / len(deltas)) if deltas else 0.0, 6),
        "worsened_ratio": round((len(worsened) / len(deltas)) if deltas else 0.0, 6),
        "top_improved_records": deltas_sorted[:top_k],
        "top_worsened_records": list(reversed(deltas_sorted[-top_k:])),
    }


def round_loss_metrics(loss_metrics: dict[str, object]) -> dict[str, object]:
    rounded: dict[str, object] = {}
    for key, value in loss_metrics.items():
        if isinstance(value, bool):
            rounded[str(key)] = bool(value)
        elif isinstance(value, (int, float)):
            rounded[str(key)] = round(float(value), 6)
        else:
            rounded[str(key)] = str(value)
    return rounded


def build_checkpoint_output_row(checkpoint: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in checkpoint.items()
        if key != "package_metrics"
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Checkpoint Review",
        "",
        f"- summary_path: {summary['summary_path']}",
        f"- checkpoint_count: {summary['checkpoint_count']}",
        f"- dataset: {json.dumps(summary['dataset'], ensure_ascii=False)}",
        f"- runtime: {json.dumps(summary['runtime'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        "",
        "## Checkpoints",
    ]
    for checkpoint in summary["checkpoints"]:
        lines.append(
            f"- step={checkpoint['step']} loss_total={checkpoint['loss_metrics']['loss_total']} "
            f"delta_vs_previous={checkpoint['delta_vs_previous_loss_total']} "
            f"delta_vs_first={checkpoint['delta_vs_first_loss_total']}"
        )
    lines.extend(["", "## Pairwise Reviews"])
    for review in summary["pairwise_reviews"]:
        lines.extend(build_review_lines(review))
    lines.extend(["", "## Overall Review"])
    lines.extend(build_review_lines(summary["overall_review"]))
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_review_lines(review: dict[str, object]) -> list[str]:
    secondary_label = (
        "top_worsened_records"
        if int(review["worsened_count"]) > 0
        else "least_improved_records"
    )
    lines = [
        (
            f"- step{review['from_step']} -> step{review['to_step']}: "
            f"avg_delta={review['average_delta_loss_total']} "
            f"improved={review['improved_count']}/{review['record_count']} "
            f"worsened={review['worsened_count']}/{review['record_count']}"
        ),
        "  top_improved_records:",
    ]
    for item in review["top_improved_records"]:
        lines.append(
            "  "
            f"- {item['record_id']}: {item['previous_loss_total']} -> {item['current_loss_total']} "
            f"(delta={item['delta_loss_total']})"
        )
    lines.append(f"  {secondary_label}:")
    for item in review["top_worsened_records"]:
        lines.append(
            "  "
            f"- {item['record_id']}: {item['previous_loss_total']} -> {item['current_loss_total']} "
            f"(delta={item['delta_loss_total']})"
        )
    return lines
