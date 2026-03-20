from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.data_scan import write_json
from v5vc.nores_vocoder_checkpoint_selection import (
    DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS,
    build_low_activity_soft_rerank,
    normalize_low_activity_metric_weights,
)


def analyze_offline_mvp_nores_vocoder_low_activity_sensitivity(
    checkpoint_selection_path: Path,
    output_dir: Path,
    weight_step: float,
) -> None:
    if weight_step <= 0.0 or weight_step > 1.0:
        raise ValueError("weight_step must be within (0.0, 1.0].")
    units = int(round(1.0 / float(weight_step)))
    if abs(float(units) * float(weight_step) - 1.0) > 1e-9:
        raise ValueError("weight_step must divide 1.0 exactly, for example 0.2, 0.1, or 0.05.")

    checkpoint_selection_path = checkpoint_selection_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    payload = json.loads(checkpoint_selection_path.read_text(encoding="utf-8"))
    late_candidates = payload.get("late_candidates", [])
    best_validation_checkpoint = payload.get("best_validation_checkpoint", {})
    selection_policy = payload.get("selection_policy", {})
    current_soft_rerank = payload.get("low_activity_soft_rerank", {})
    if not isinstance(late_candidates, list) or not late_candidates:
        raise ValueError("checkpoint selection payload does not contain late_candidates.")
    if not isinstance(best_validation_checkpoint, dict) or "loss_total" not in best_validation_checkpoint:
        raise ValueError("checkpoint selection payload does not contain best_validation_checkpoint.loss_total.")
    if not isinstance(selection_policy, dict):
        raise ValueError("checkpoint selection payload does not contain selection_policy.")
    if not isinstance(current_soft_rerank, dict):
        raise ValueError("checkpoint selection payload does not contain low_activity_soft_rerank.")

    best_validation_loss_total = float(best_validation_checkpoint["loss_total"])
    max_pairwise_worsened_ratio = float(selection_policy.get("max_pairwise_worsened_ratio", 0.0))
    current_soft_validation_ratio = float(selection_policy.get("low_activity_soft_validation_ratio", 1.0))
    current_metric_weights = dict(current_soft_rerank.get("metric_weights", DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS))

    eligible_metric_candidates = build_metric_ready_candidate_rows(
        late_candidates=late_candidates,
        best_validation_loss_total=best_validation_loss_total,
        max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
    )
    if not eligible_metric_candidates:
        raise ValueError("No late candidates carry low_activity_metrics while satisfying the pairwise cap.")

    current_rerank = build_low_activity_soft_rerank(
        late_candidates=late_candidates,
        best_validation_loss_total=best_validation_loss_total,
        max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
        soft_validation_ratio=current_soft_validation_ratio,
        metric_weights=current_metric_weights,
    )
    if not isinstance(current_rerank, dict) or not bool(current_rerank.get("enabled")):
        raise ValueError("Current low_activity_soft_rerank is not enabled; sensitivity analysis has no active baseline.")

    ratio_sweep = build_soft_validation_ratio_sweep(
        late_candidates=late_candidates,
        eligible_metric_candidates=eligible_metric_candidates,
        best_validation_loss_total=best_validation_loss_total,
        max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
        current_metric_weights=current_metric_weights,
        current_soft_validation_ratio=current_soft_validation_ratio,
    )
    fragmentation_sweep = build_fragmentation_emphasis_sweep(
        late_candidates=late_candidates,
        best_validation_loss_total=best_validation_loss_total,
        max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
        current_metric_weights=current_metric_weights,
        current_soft_validation_ratio=current_soft_validation_ratio,
        units=units,
    )
    weight_grid = build_weight_grid_summary(
        late_candidates=late_candidates,
        best_validation_loss_total=best_validation_loss_total,
        max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
        current_soft_validation_ratio=current_soft_validation_ratio,
        units=units,
    )

    summary = {
        "checkpoint_selection_path": checkpoint_selection_path.as_posix(),
        "output_dir": output_dir.as_posix(),
        "weight_step": round(float(weight_step), 6),
        "best_validation_loss_total": round(best_validation_loss_total, 6),
        "max_pairwise_worsened_ratio": round(max_pairwise_worsened_ratio, 6),
        "current_soft_validation_ratio": round(current_soft_validation_ratio, 6),
        "current_metric_weights": {
            field_name: round(float(weight), 6)
            for field_name, weight in normalize_low_activity_metric_weights(current_metric_weights)
        },
        "metric_ready_late_candidates": eligible_metric_candidates,
        "current_soft_rerank": summarize_rerank(current_rerank),
        "soft_validation_ratio_sweep": ratio_sweep,
        "fragmentation_emphasis_sweep": fragmentation_sweep,
        "weight_grid_summary": weight_grid,
        "notes": [
            "This analysis reuses the existing late_candidates payload and does not reopen the main selector policy.",
            "Only candidates that already carry low_activity_metrics and satisfy the pairwise cap can participate in the soft rerank sensitivity scan.",
            build_locality_note(eligible_metric_candidates),
        ],
    }
    write_json(output_dir / "nores_vocoder_low_activity_sensitivity.json", summary)
    (output_dir / "nores_vocoder_low_activity_sensitivity.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_metric_ready_candidate_rows(
    late_candidates: list[dict[str, object]],
    best_validation_loss_total: float,
    max_pairwise_worsened_ratio: float,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate in late_candidates:
        low_activity_metrics = candidate.get("low_activity_metrics")
        if not isinstance(low_activity_metrics, dict):
            continue
        pairwise_review = candidate.get("pairwise_review")
        worsened_ratio = 0.0 if not isinstance(pairwise_review, dict) else float(pairwise_review["worsened_ratio"])
        if worsened_ratio > float(max_pairwise_worsened_ratio) + 1e-9:
            continue
        entry_ratio = float(candidate["loss_total"]) / float(best_validation_loss_total)
        rows.append(
            {
                "step": int(candidate["step"]),
                "loss_total": round(float(candidate["loss_total"]), 6),
                "entry_soft_validation_ratio": round(entry_ratio, 6),
                "rms_ratio_deviation": round(float(candidate["rms_ratio_deviation"]), 6),
                "low_activity_metrics": {
                    key: round(float(value), 6) if isinstance(value, (int, float)) else value
                    for key, value in low_activity_metrics.items()
                },
            }
        )
    rows.sort(
        key=lambda item: (
            float(item["entry_soft_validation_ratio"]),
            float(item["loss_total"]),
            int(item["step"]),
        )
    )
    return rows


def build_soft_validation_ratio_sweep(
    late_candidates: list[dict[str, object]],
    eligible_metric_candidates: list[dict[str, object]],
    best_validation_loss_total: float,
    max_pairwise_worsened_ratio: float,
    current_metric_weights: dict[str, float],
    current_soft_validation_ratio: float,
) -> dict[str, object]:
    ratio_values = sorted(
        {
            round(float(item["entry_soft_validation_ratio"]), 6)
            for item in eligible_metric_candidates
        }
        | {round(float(current_soft_validation_ratio), 6)}
    )
    rows: list[dict[str, object]] = []
    previous_selected_step: int | None = None
    previous_eligible_steps: list[int] | None = None
    switchpoints: list[dict[str, object]] = []
    for ratio in ratio_values:
        rerank = build_low_activity_soft_rerank(
            late_candidates=late_candidates,
            best_validation_loss_total=best_validation_loss_total,
            max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
            soft_validation_ratio=float(ratio),
            metric_weights=current_metric_weights,
        )
        selected_step = None
        eligible_steps: list[int] = []
        if isinstance(rerank, dict):
            selected_candidate = rerank.get("selected_candidate")
            if isinstance(selected_candidate, dict):
                selected_step = int(selected_candidate["step"])
            eligible_steps = [
                int(item["step"])
                for item in rerank.get("ranked_candidates", [])
                if isinstance(item, dict)
            ]
        row = {
            "soft_validation_ratio": round(float(ratio), 6),
            "eligible_candidate_steps": eligible_steps,
            "selected_step": selected_step,
            "eligible_candidate_count": len(eligible_steps),
        }
        rows.append(row)
        if previous_selected_step != selected_step or previous_eligible_steps != eligible_steps:
            switchpoints.append(row)
        previous_selected_step = selected_step
        previous_eligible_steps = eligible_steps
    return {
        "rows": rows,
        "switchpoints": switchpoints,
    }


def build_fragmentation_emphasis_sweep(
    late_candidates: list[dict[str, object]],
    best_validation_loss_total: float,
    max_pairwise_worsened_ratio: float,
    current_metric_weights: dict[str, float],
    current_soft_validation_ratio: float,
    units: int,
) -> dict[str, object]:
    normalized_current_weights = dict(normalize_low_activity_metric_weights(current_metric_weights))
    fragmentation_field = "mean_fragmentation_score"
    non_fragmentation_total = 1.0 - float(normalized_current_weights[fragmentation_field])
    rows: list[dict[str, object]] = []
    current_selected_step: int | None = None
    switch_weight: float | None = None
    previous_selected_step: int | None = None
    for fragmentation_units in range(units + 1):
        fragmentation_weight = float(fragmentation_units) / float(units)
        remaining_weight = 1.0 - fragmentation_weight
        metric_weights: dict[str, float] = {}
        for field_name, field_weight in normalized_current_weights.items():
            if field_name == fragmentation_field:
                metric_weights[field_name] = fragmentation_weight
                continue
            redistributed_weight = 0.0
            if non_fragmentation_total > 0.0:
                redistributed_weight = remaining_weight * float(field_weight) / non_fragmentation_total
            metric_weights[field_name] = redistributed_weight
        rerank = build_low_activity_soft_rerank(
            late_candidates=late_candidates,
            best_validation_loss_total=best_validation_loss_total,
            max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
            soft_validation_ratio=current_soft_validation_ratio,
            metric_weights=metric_weights,
        )
        selected_step = None
        selected_score = None
        runner_up_step = None
        runner_up_score = None
        score_gap = None
        ranked_candidates = []
        if isinstance(rerank, dict):
            ranked_candidates = [
                item
                for item in rerank.get("ranked_candidates", [])
                if isinstance(item, dict)
            ]
        if ranked_candidates:
            selected_step = int(ranked_candidates[0]["step"])
            selected_score = round(float(ranked_candidates[0]["low_activity_governance_score"]), 6)
            if len(ranked_candidates) > 1:
                runner_up_step = int(ranked_candidates[1]["step"])
                runner_up_score = round(float(ranked_candidates[1]["low_activity_governance_score"]), 6)
                score_gap = round(float(runner_up_score) - float(selected_score), 6)
        row = {
            "fragmentation_weight": round(fragmentation_weight, 6),
            "metric_weights": {
                field_name: round(float(weight), 6)
                for field_name, weight in normalize_low_activity_metric_weights(metric_weights)
            },
            "selected_step": selected_step,
            "selected_score": selected_score,
            "runner_up_step": runner_up_step,
            "runner_up_score": runner_up_score,
            "score_gap_to_runner_up": score_gap,
        }
        rows.append(row)
        if current_selected_step is None:
            current_selected_step = selected_step
        elif switch_weight is None and selected_step != current_selected_step:
            switch_weight = row["fragmentation_weight"]
        previous_selected_step = selected_step
    return {
        "rows": rows,
        "first_selected_step": current_selected_step,
        "selection_flip_fragmentation_weight": switch_weight,
        "notes": [
            "This sweep only changes mean_fragmentation_score weight; the other three weights keep their current relative ratios.",
        ],
    }


def build_weight_grid_summary(
    late_candidates: list[dict[str, object]],
    best_validation_loss_total: float,
    max_pairwise_worsened_ratio: float,
    current_soft_validation_ratio: float,
    units: int,
) -> dict[str, object]:
    metric_fields = tuple(DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS.keys())
    selection_counts: dict[int, int] = {}
    representative_weights: dict[int, dict[str, float]] = {}
    total_weight_configs = 0
    for weight_a in range(units + 1):
        for weight_b in range(units - weight_a + 1):
            for weight_c in range(units - weight_a - weight_b + 1):
                weight_d = units - weight_a - weight_b - weight_c
                raw_weights = (weight_a, weight_b, weight_c, weight_d)
                metric_weights = {
                    field_name: float(raw_weight) / float(units)
                    for field_name, raw_weight in zip(metric_fields, raw_weights)
                }
                rerank = build_low_activity_soft_rerank(
                    late_candidates=late_candidates,
                    best_validation_loss_total=best_validation_loss_total,
                    max_pairwise_worsened_ratio=max_pairwise_worsened_ratio,
                    soft_validation_ratio=current_soft_validation_ratio,
                    metric_weights=metric_weights,
                )
                if not isinstance(rerank, dict) or not bool(rerank.get("enabled")):
                    continue
                selected_candidate = rerank.get("selected_candidate")
                if not isinstance(selected_candidate, dict):
                    continue
                selected_step = int(selected_candidate["step"])
                selection_counts[selected_step] = int(selection_counts.get(selected_step, 0)) + 1
                total_weight_configs += 1
                if selected_step not in representative_weights:
                    representative_weights[selected_step] = {
                        field_name: round(float(weight), 6)
                        for field_name, weight in normalize_low_activity_metric_weights(metric_weights)
                    }
    selection_breakdown = []
    for step, count in sorted(selection_counts.items(), key=lambda item: (-int(item[1]), int(item[0]))):
        share = 0.0 if total_weight_configs <= 0 else float(count) / float(total_weight_configs)
        selection_breakdown.append(
            {
                "step": int(step),
                "selected_count": int(count),
                "selected_share": round(share, 6),
                "representative_metric_weights": representative_weights.get(int(step)),
            }
        )
    return {
        "weight_step": round(1.0 / float(units), 6),
        "total_weight_configs": int(total_weight_configs),
        "selection_breakdown": selection_breakdown,
    }


def summarize_rerank(rerank: dict[str, object]) -> dict[str, object]:
    selected_candidate = dict(rerank.get("selected_candidate", {}))
    ranked_candidates = [
        item
        for item in rerank.get("ranked_candidates", [])
        if isinstance(item, dict)
    ]
    return {
        "soft_validation_ratio": round(float(rerank.get("soft_validation_ratio", 0.0)), 6),
        "soft_validation_threshold": round(float(rerank.get("soft_validation_threshold", 0.0)), 6),
        "eligible_candidate_count": int(rerank.get("eligible_candidate_count", 0)),
        "selected_candidate": {
            "step": int(selected_candidate.get("step", 0)),
            "low_activity_governance_score": round(float(selected_candidate.get("low_activity_governance_score", 0.0)), 6),
        },
        "ranked_candidates": [
            {
                "step": int(item["step"]),
                "score": round(float(item["low_activity_governance_score"]), 6),
                "breakdown": {
                    field_name: {
                        "raw_value": round(float(details["raw_value"]), 6),
                        "normalized_penalty": round(float(details["normalized_penalty"]), 6),
                        "weight": round(float(details["weight"]), 6),
                        "weighted_penalty": round(float(details["weighted_penalty"]), 6),
                    }
                    for field_name, details in dict(item.get("low_activity_governance_breakdown", {})).items()
                },
            }
            for item in ranked_candidates
        ],
    }


def build_locality_note(eligible_metric_candidates: list[dict[str, object]]) -> str:
    covered_steps = [
        int(item["step"])
        for item in eligible_metric_candidates
    ]
    covered_steps.sort()
    if not covered_steps:
        return "The current checkpoint-selection payload does not expose any low-activity metric-ready late candidates."
    covered_text = ", ".join(str(step) for step in covered_steps)
    return (
        "These conclusions are local to the current low-activity comparison set, "
        f"which currently covers late candidates at steps [{covered_text}]."
    )


def build_markdown(summary: dict[str, object]) -> str:
    current_soft_rerank = dict(summary["current_soft_rerank"])
    selected_candidate = dict(current_soft_rerank["selected_candidate"])
    lines = [
        "# Stage5 No-Residual Vocoder Low-Activity Soft-Rerank Sensitivity",
        "",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- current_soft_validation_ratio: {summary['current_soft_validation_ratio']}",
        f"- current_metric_weights: {json.dumps(summary['current_metric_weights'], ensure_ascii=False)}",
        f"- current_selected_step: {selected_candidate['step']}",
        f"- current_selected_score: {selected_candidate['low_activity_governance_score']}",
        "",
        "## Metric-Ready Late Candidates",
    ]
    for candidate in summary["metric_ready_late_candidates"]:
        lines.append(
            f"- step={candidate['step']} loss_total={candidate['loss_total']} "
            f"entry_soft_validation_ratio={candidate['entry_soft_validation_ratio']} "
            f"fragmentation={candidate['low_activity_metrics']['mean_fragmentation_score']} "
            f"active_fraction={candidate['low_activity_metrics']['mean_active_fraction']} "
            f"alignment_mae={candidate['low_activity_metrics']['mean_activity_alignment_mae']} "
            f"activity_excess={candidate['low_activity_metrics']['mean_activity_excess_mean']}"
        )
    lines.extend(["", "## Current Breakdown"])
    for candidate in current_soft_rerank["ranked_candidates"]:
        breakdown = candidate["breakdown"]
        lines.append(
            f"- step={candidate['step']} score={candidate['score']} "
            f"alignment_penalty={breakdown['mean_activity_alignment_mae']['normalized_penalty']} "
            f"excess_penalty={breakdown['mean_activity_excess_mean']['normalized_penalty']} "
            f"active_fraction_penalty={breakdown['mean_active_fraction']['normalized_penalty']} "
            f"fragmentation_penalty={breakdown['mean_fragmentation_score']['normalized_penalty']}"
        )
    lines.extend(["", "## Soft-Validation Ratio Sweep"])
    for row in summary["soft_validation_ratio_sweep"]["rows"]:
        lines.append(
            f"- ratio={row['soft_validation_ratio']} eligible_steps={row['eligible_candidate_steps']} "
            f"selected_step={row['selected_step']}"
        )
    lines.extend(["", "## Fragmentation Emphasis Sweep"])
    for row in summary["fragmentation_emphasis_sweep"]["rows"]:
        lines.append(
            f"- fragmentation_weight={row['fragmentation_weight']} selected_step={row['selected_step']} "
            f"selected_score={row['selected_score']} runner_up_step={row['runner_up_step']} "
            f"score_gap_to_runner_up={row['score_gap_to_runner_up']}"
        )
    lines.extend(
        [
            (
                f"- selection_flip_fragmentation_weight: "
                f"{summary['fragmentation_emphasis_sweep']['selection_flip_fragmentation_weight']}"
            ),
            "",
            "## Weight Grid Summary",
        ]
    )
    for item in summary["weight_grid_summary"]["selection_breakdown"]:
        lines.append(
            f"- step={item['step']} selected_count={item['selected_count']} "
            f"selected_share={item['selected_share']} "
            f"representative_metric_weights={json.dumps(item['representative_metric_weights'], ensure_ascii=False)}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
