from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path

from v5vc.data_scan import write_json
from v5vc.nores_vocoder_checkpoint_review import build_checkpoint_rows, build_pairwise_reviews

DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS = {
    "mean_activity_alignment_mae": 0.35,
    "mean_activity_excess_mean": 0.35,
    "mean_active_fraction": 0.2,
    "mean_fragmentation_score": 0.1,
}

LOW_ACTIVITY_TIE_EPSILON = 1e-9


def select_offline_mvp_nores_vocoder_checkpoint(
    summary_path: Path,
    output_dir: Path,
    late_step_ratio: float,
    validation_guard_ratio: float,
    max_pairwise_worsened_ratio: float,
    max_rms_ratio_deviation: float,
    low_activity_probe_path: Path | None = None,
    low_activity_audio_source: str = "decoded",
    low_activity_soft_validation_ratio: float = 1.05,
) -> None:
    if late_step_ratio <= 0.0 or late_step_ratio > 1.0:
        raise ValueError("late_step_ratio must be within (0.0, 1.0].")
    if validation_guard_ratio < 1.0:
        raise ValueError("validation_guard_ratio must be >= 1.0.")
    if max_pairwise_worsened_ratio < 0.0 or max_pairwise_worsened_ratio > 1.0:
        raise ValueError("max_pairwise_worsened_ratio must be within [0.0, 1.0].")
    if max_rms_ratio_deviation < 0.0:
        raise ValueError("max_rms_ratio_deviation must be >= 0.0.")
    if low_activity_soft_validation_ratio < 1.0:
        raise ValueError("low_activity_soft_validation_ratio must be >= 1.0.")

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
    low_activity_probe_analysis = load_low_activity_probe_analysis(
        low_activity_probe_path=low_activity_probe_path,
        audio_source=low_activity_audio_source,
    )
    low_activity_metrics_by_step = {}
    if low_activity_probe_analysis is not None:
        low_activity_metrics_by_step = dict(low_activity_probe_analysis["checkpoint_metrics_by_step"])

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
            "low_activity_metrics": build_low_activity_candidate_metrics(
                low_activity_metrics_by_step=low_activity_metrics_by_step,
                step=step,
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
    low_activity_soft_rerank = build_low_activity_soft_rerank(
        late_candidates=late_candidates,
        best_validation_loss_total=float(best_validation_checkpoint["loss_metrics"]["loss_total"]),
        max_pairwise_worsened_ratio=float(max_pairwise_worsened_ratio),
        soft_validation_ratio=float(low_activity_soft_validation_ratio),
    )
    if isinstance(low_activity_soft_rerank, dict):
        rerank_candidates = low_activity_soft_rerank.get("all_candidates", [])
        if isinstance(rerank_candidates, list):
            rerank_by_step = {
                int(item["step"]): item
                for item in rerank_candidates
                if isinstance(item, dict) and item.get("step") is not None
            }
            late_candidates = [
                rerank_by_step.get(int(candidate["step"]), candidate)
                for candidate in late_candidates
            ]

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
            "low_activity_soft_validation_ratio": float(low_activity_soft_validation_ratio),
        },
        "best_validation_checkpoint": build_checkpoint_selection_row(
            best_validation_checkpoint,
            low_activity_metrics_by_step=low_activity_metrics_by_step,
        ),
        "best_rms_checkpoint": build_checkpoint_selection_row(
            best_rms_checkpoint,
            low_activity_metrics_by_step=low_activity_metrics_by_step,
        ),
        "late_candidates": late_candidates,
        "selected_stable_late_stop": annotate_selected_candidate_with_low_activity(
            selected_stable_late_stop,
            low_activity_metrics_by_step=low_activity_metrics_by_step,
        ),
        "low_activity_probe_analysis": low_activity_probe_analysis,
        "low_activity_soft_rerank": low_activity_soft_rerank,
        "notes": [
            "best_validation_checkpoint is the recorded checkpoint with minimum validation loss_total.",
            "best_rms_checkpoint prefers decoded_to_target_rms_ratio closest to 1.0, then lower validation loss_total.",
            "selected_stable_late_stop keeps only late-window checkpoints that stay within the validation guard, keep pairwise worsened_ratio under the configured cap, and keep RMS ratio deviation under the configured cap.",
            "When low_activity_probe_analysis is present, it is a governance sidecar only: it annotates local low-activity tradeoffs but does not override the selector's hard policy.",
            "low_activity_soft_rerank is a secondary governance recommendation among near-best late candidates only; it does not override best_validation_checkpoint or selected_stable_late_stop.",
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


def load_low_activity_probe_analysis(
    low_activity_probe_path: Path | None,
    audio_source: str,
) -> dict[str, object] | None:
    if low_activity_probe_path is None:
        return None
    payload = json.loads(low_activity_probe_path.resolve().read_text(encoding="utf-8"))
    analysis_sources = payload.get("analysis_sources", {})
    if not isinstance(analysis_sources, dict):
        raise ValueError("low_activity_probe json does not contain analysis_sources.")
    source_payload = analysis_sources.get(str(audio_source))
    if not isinstance(source_payload, dict):
        raise ValueError(f"low_activity_probe json does not contain audio source {audio_source!r}.")
    branch_aggregates = source_payload.get("branch_aggregates", {})
    if not isinstance(branch_aggregates, dict) or not branch_aggregates:
        raise ValueError("low_activity_probe json does not contain branch_aggregates for the selected source.")

    checkpoint_metrics_by_step: dict[int, dict[str, object]] = {}
    compact_aggregates: dict[str, dict[str, object]] = {}
    for branch_label, aggregate in branch_aggregates.items():
        if not isinstance(aggregate, dict):
            continue
        compact_aggregate = {
            "record_count": int(aggregate.get("record_count", 0)),
            "mean_segment_count": round(float(aggregate.get("mean_segment_count", 0.0)), 6),
            "mean_fragmentation_score": round(float(aggregate.get("mean_fragmentation_score", 0.0)), 6),
            "mean_active_fraction": round(float(aggregate.get("mean_active_fraction", 0.0)), 6),
            "mean_activity_alignment_mae": round(float(aggregate.get("mean_activity_alignment_mae", 0.0)), 6),
            "mean_activity_excess_mean": round(float(aggregate.get("mean_activity_excess_mean", 0.0)), 6),
            "mean_waveform_rms": round(float(aggregate.get("mean_waveform_rms", 0.0)), 6),
            "mean_sample_delta_peak": round(float(aggregate.get("mean_sample_delta_peak", 0.0)), 6),
        }
        compact_aggregates[str(branch_label)] = compact_aggregate
        step = infer_step_from_branch_label(str(branch_label))
        if step is not None:
            checkpoint_metrics_by_step[step] = {
                "branch_label": str(branch_label),
                **compact_aggregate,
            }

    if not compact_aggregates:
        return None

    best_fragmentation_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_fragmentation_score",
        mode="min",
    )
    best_alignment_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_activity_alignment_mae",
        mode="min",
    )
    best_low_activity_quietness_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_activity_excess_mean",
        mode="min",
    )
    best_low_activity_leakage_strength_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_waveform_rms",
        mode="min",
    )
    worst_floor_leakage_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_active_fraction",
        mode="max",
    )
    worst_floor_leakage_strength_ranking = rank_branch_labels_by_metric(
        compact_aggregates=compact_aggregates,
        branch_labels=worst_floor_leakage_branches,
        metric_name="mean_waveform_rms",
        mode="min",
    )
    best_low_activity_smoothness_branches = collect_tied_branch_labels(
        compact_aggregates=compact_aggregates,
        metric_name="mean_sample_delta_peak",
        mode="min",
    )
    worst_floor_leakage_smoothness_ranking = rank_branch_labels_by_metric(
        compact_aggregates=compact_aggregates,
        branch_labels=worst_floor_leakage_branches,
        metric_name="mean_sample_delta_peak",
        mode="min",
    )
    ranking = {
        "best_fragmentation_score_branch": best_fragmentation_branches[0],
        "best_fragmentation_score_branches": best_fragmentation_branches,
        "best_alignment_branch": best_alignment_branches[0],
        "best_alignment_branches": best_alignment_branches,
        "best_low_activity_quietness_branch": best_low_activity_quietness_branches[0],
        "best_low_activity_quietness_branches": best_low_activity_quietness_branches,
        "best_low_activity_leakage_strength_branch": best_low_activity_leakage_strength_branches[0],
        "best_low_activity_leakage_strength_branches": best_low_activity_leakage_strength_branches,
        "worst_floor_leakage_branch": worst_floor_leakage_branches[0],
        "worst_floor_leakage_branches": worst_floor_leakage_branches,
        "worst_floor_leakage_strength_ranking": worst_floor_leakage_strength_ranking,
        "best_low_activity_smoothness_branch": best_low_activity_smoothness_branches[0],
        "best_low_activity_smoothness_branches": best_low_activity_smoothness_branches,
        "worst_floor_leakage_smoothness_ranking": worst_floor_leakage_smoothness_ranking,
    }
    governance_template = build_dual_axis_governance_template(ranking)
    top_windows = []
    source_top_windows = source_payload.get("top_windows", [])
    if isinstance(source_top_windows, list):
        for item in source_top_windows[:3]:
            if not isinstance(item, dict):
                continue
            top_windows.append(
                {
                    "record_id": str(item.get("record_id", "")),
                    "segment_index": int(item.get("segment_index", 0)),
                    "delta_fragmentation_score": round(float(item.get("delta_fragmentation_score", 0.0)), 6),
                    "worst_branch": str(dict(item.get("worst_branch", {})).get("branch_label", "")),
                    "best_branch": str(dict(item.get("best_branch", {})).get("branch_label", "")),
                    "target_context_toggle_mean": round(
                        float(dict(item.get("worst_branch", {})).get("target_context_toggle_mean", 0.0)),
                        6,
                    ),
                    "target_boundary_jump_max": round(
                        float(dict(item.get("worst_branch", {})).get("target_boundary_jump_max", 0.0)),
                        6,
                    ),
                }
            )

    fragmentation_axis = dict(governance_template["fragmentation_axis"])
    leakage_strength_axis = dict(governance_template["leakage_strength_axis"])
    summary_lines = [
        (
            f"low_activity/{audio_source} fragmentation_axis: "
            f"best_fragmentation={format_branch_label_group(fragmentation_axis['best_fragmentation_branches'])}, "
            f"best_alignment={format_branch_label_group(fragmentation_axis['best_alignment_branches'])}, "
            f"best_quietness={format_branch_label_group(fragmentation_axis['best_quietness_branches'])}"
        ),
        (
            f"low_activity/{audio_source} leakage_strength_axis: "
            f"best_leakage_strength={format_branch_label_group(leakage_strength_axis['best_leakage_strength_branches'])}, "
            f"worst_floor_leakage={format_branch_label_group(leakage_strength_axis['worst_floor_leakage_branches'])}, "
            f"best_smoothness={format_branch_label_group(ranking['best_low_activity_smoothness_branches'])}"
        ),
        str(governance_template["cross_axis_note"]),
        (
            "Guardrail: low-activity fragmentation is a local-risk indicator only; "
            "interpret it together with activity_alignment_mae and activity_excess_mean before treating a checkpoint as globally worse."
        ),
    ]
    if len(worst_floor_leakage_strength_ranking) > 1:
        summary_lines.append(
            "Within the worst_floor_leakage tie group, mean_waveform_rms orders weaker residual leakage strength as: "
            + " < ".join(item["branch_label"] for item in worst_floor_leakage_strength_ranking)
        )
    if len(worst_floor_leakage_smoothness_ranking) > 1:
        summary_lines.append(
            "Within the worst_floor_leakage tie group, mean_sample_delta_peak orders smoother decoded edges as: "
            + " < ".join(item["branch_label"] for item in worst_floor_leakage_smoothness_ranking)
        )
    return {
        "probe_path": low_activity_probe_path.resolve().as_posix(),
        "audio_source": str(audio_source),
        "branch_aggregates": compact_aggregates,
        "checkpoint_metrics_by_step": checkpoint_metrics_by_step,
        "ranking": ranking,
        "governance_template": governance_template,
        "top_windows": top_windows,
        "summary_lines": summary_lines,
    }


def infer_step_from_branch_label(branch_label: str) -> int | None:
    match = re.search(r"step(\d+)\s*$", str(branch_label))
    if match is None:
        return None
    return int(match.group(1))


def collect_tied_branch_labels(
    compact_aggregates: dict[str, dict[str, object]],
    metric_name: str,
    mode: str,
) -> list[str]:
    values = [
        float(aggregate[metric_name])
        for aggregate in compact_aggregates.values()
    ]
    if not values:
        return []
    if mode == "min":
        target_value = min(values)
    elif mode == "max":
        target_value = max(values)
    else:
        raise ValueError(f"Unsupported tie-collection mode: {mode}")
    tied_labels = [
        str(branch_label)
        for branch_label, aggregate in compact_aggregates.items()
        if abs(float(aggregate[metric_name]) - target_value) <= LOW_ACTIVITY_TIE_EPSILON
    ]
    tied_labels.sort()
    return tied_labels


def rank_branch_labels_by_metric(
    compact_aggregates: dict[str, dict[str, object]],
    branch_labels: list[str],
    metric_name: str,
    mode: str,
) -> list[dict[str, object]]:
    rows = [
        {
            "branch_label": str(branch_label),
            "metric_name": str(metric_name),
            "metric_value": round(float(compact_aggregates[branch_label][metric_name]), 6),
        }
        for branch_label in branch_labels
        if branch_label in compact_aggregates
    ]
    if mode == "min":
        rows.sort(key=lambda item: (float(item["metric_value"]), str(item["branch_label"])))
    elif mode == "max":
        rows.sort(key=lambda item: (-float(item["metric_value"]), str(item["branch_label"])))
    else:
        raise ValueError(f"Unsupported branch-ranking mode: {mode}")
    return rows


def format_branch_label_group(branch_labels: list[str]) -> str:
    if not branch_labels:
        return "[]"
    if len(branch_labels) == 1:
        return branch_labels[0]
    return "[" + ", ".join(branch_labels) + "]"


def build_dual_axis_governance_template(
    ranking: dict[str, object],
) -> dict[str, object]:
    fragmentation_branches = list(ranking["best_fragmentation_score_branches"])
    leakage_branches = list(ranking["best_low_activity_leakage_strength_branches"])
    fragmentation_set = set(fragmentation_branches)
    leakage_set = set(leakage_branches)
    if fragmentation_set == leakage_set:
        mode = "convergent"
        cross_axis_note = (
            "Cross-axis note: fragmentation axis and leakage-strength axis currently point to the same branch/group."
        )
    elif fragmentation_set.intersection(leakage_set):
        mode = "partial_overlap"
        cross_axis_note = (
            "Cross-axis note: fragmentation axis and leakage-strength axis partially overlap; keep both axes visible."
        )
    else:
        mode = "tradeoff"
        cross_axis_note = (
            "Cross-axis note: fragmentation axis and leakage-strength axis point to different branch/groups; "
            "treat this as a dual-axis tradeoff instead of forcing a single winner."
        )
    return {
        "mode": mode,
        "fragmentation_axis": {
            "best_fragmentation_branches": fragmentation_branches,
            "best_alignment_branches": list(ranking["best_alignment_branches"]),
            "best_quietness_branches": list(ranking["best_low_activity_quietness_branches"]),
            "note": "Use this axis when burst/toggle risk and local structural safety are the primary question.",
        },
        "leakage_strength_axis": {
            "best_leakage_strength_branches": leakage_branches,
            "worst_floor_leakage_branches": list(ranking["worst_floor_leakage_branches"]),
            "worst_floor_leakage_strength_ranking": list(ranking["worst_floor_leakage_strength_ranking"]),
            "worst_floor_leakage_smoothness_ranking": list(ranking["worst_floor_leakage_smoothness_ranking"]),
            "note": "Use this axis when comparing residual leakage strength inside a leakage cluster or choosing a fallback after fragmentation has already tied.",
        },
        "cross_axis_note": cross_axis_note,
    }


def build_low_activity_candidate_metrics(
    low_activity_metrics_by_step: dict[int, dict[str, object]],
    step: int,
) -> dict[str, object] | None:
    metrics = low_activity_metrics_by_step.get(int(step))
    if metrics is None:
        return None
    return dict(metrics)


def annotate_selected_candidate_with_low_activity(
    candidate: dict[str, object] | None,
    low_activity_metrics_by_step: dict[int, dict[str, object]],
) -> dict[str, object] | None:
    if candidate is None:
        return None
    annotated = dict(candidate)
    annotated["low_activity_metrics"] = build_low_activity_candidate_metrics(
        low_activity_metrics_by_step=low_activity_metrics_by_step,
        step=int(candidate["step"]),
    )
    return annotated


def build_low_activity_soft_rerank(
    late_candidates: list[dict[str, object]],
    best_validation_loss_total: float,
    max_pairwise_worsened_ratio: float,
    soft_validation_ratio: float,
    metric_weights: dict[str, float] | None = None,
) -> dict[str, object] | None:
    scored_candidates: list[dict[str, object]] = []
    eligible_candidates: list[dict[str, object]] = []
    soft_validation_threshold = float(best_validation_loss_total) * float(soft_validation_ratio)
    normalized_metric_weights = normalize_low_activity_metric_weights(metric_weights)

    for candidate in late_candidates:
        low_activity_metrics = candidate.get("low_activity_metrics")
        pairwise_review = candidate.get("pairwise_review")
        worsened_ratio = 0.0 if not isinstance(pairwise_review, dict) else float(pairwise_review["worsened_ratio"])
        is_eligible = bool(
            isinstance(low_activity_metrics, dict)
            and float(candidate["loss_total"]) <= soft_validation_threshold + 1e-9
            and worsened_ratio <= float(max_pairwise_worsened_ratio) + 1e-9
        )
        if is_eligible:
            eligible_candidates.append(candidate)

    if not eligible_candidates:
        return {
            "enabled": False,
            "selection_mode": "late_candidate_soft_rerank",
            "soft_validation_ratio": round(float(soft_validation_ratio), 6),
            "soft_validation_threshold": round(float(soft_validation_threshold), 6),
            "eligible_candidate_count": 0,
            "selected_candidate": None,
            "notes": [
                "No late candidates satisfied the near-best validation budget and pairwise cap while also carrying low-activity metrics.",
            ],
        }

    normalization_ranges = {}
    for field_name, _weight in normalized_metric_weights:
        values = [
            float(dict(candidate["low_activity_metrics"])[field_name])
            for candidate in eligible_candidates
        ]
        normalization_ranges[field_name] = {
            "min": min(values),
            "max": max(values),
        }

    for candidate in late_candidates:
        annotated = dict(candidate)
        low_activity_metrics = annotated.get("low_activity_metrics")
        if candidate not in eligible_candidates or not isinstance(low_activity_metrics, dict):
            annotated["qualifies_for_low_activity_soft_rerank"] = False
            annotated["low_activity_governance_score"] = None
            annotated["low_activity_governance_breakdown"] = None
            scored_candidates.append(annotated)
            continue

        breakdown: dict[str, dict[str, float]] = {}
        total_score = 0.0
        for field_name, weight in normalized_metric_weights:
            field_value = float(low_activity_metrics[field_name])
            field_range = normalization_ranges[field_name]
            denominator = float(field_range["max"]) - float(field_range["min"])
            normalized_penalty = 0.0 if abs(denominator) <= 1e-9 else (field_value - float(field_range["min"])) / denominator
            weighted_penalty = normalized_penalty * float(weight)
            total_score += weighted_penalty
            breakdown[field_name] = {
                "raw_value": round(field_value, 6),
                "normalized_penalty": round(normalized_penalty, 6),
                "weight": round(float(weight), 6),
                "weighted_penalty": round(weighted_penalty, 6),
            }
        annotated["qualifies_for_low_activity_soft_rerank"] = True
        annotated["low_activity_governance_score"] = round(total_score, 6)
        annotated["low_activity_governance_breakdown"] = breakdown
        scored_candidates.append(annotated)

    eligible_scored_candidates = [
        item for item in scored_candidates
        if bool(item.get("qualifies_for_low_activity_soft_rerank"))
    ]
    eligible_scored_candidates.sort(
        key=lambda item: (
            float(item["low_activity_governance_score"]),
            float(item["loss_total"]),
            float(item["rms_ratio_deviation"]),
            -int(item["step"]),
        )
    )
    for rank, candidate in enumerate(eligible_scored_candidates, start=1):
        candidate["low_activity_soft_rerank_rank"] = int(rank)
    step_to_rank = {
        int(candidate["step"]): int(candidate["low_activity_soft_rerank_rank"])
        for candidate in eligible_scored_candidates
    }
    for candidate in scored_candidates:
        if bool(candidate.get("qualifies_for_low_activity_soft_rerank")):
            candidate["low_activity_soft_rerank_rank"] = int(step_to_rank[int(candidate["step"])])
        else:
            candidate["low_activity_soft_rerank_rank"] = None

    selected_candidate = dict(eligible_scored_candidates[0])
    return {
        "enabled": True,
        "selection_mode": "late_candidate_soft_rerank",
        "soft_validation_ratio": round(float(soft_validation_ratio), 6),
        "soft_validation_threshold": round(float(soft_validation_threshold), 6),
        "eligible_candidate_count": len(eligible_scored_candidates),
        "metric_weights": {
            field_name: round(float(weight), 6)
            for field_name, weight in normalized_metric_weights
        },
        "selected_candidate": selected_candidate,
        "all_candidates": scored_candidates,
        "ranked_candidates": eligible_scored_candidates,
        "notes": [
            "Only late candidates within the near-best validation budget and pairwise cap are eligible for low-activity soft rerank.",
            "Lower low_activity_governance_score is better.",
            "This is a governance recommendation only; it does not replace best_validation_checkpoint or selected_stable_late_stop.",
        ],
    }


def normalize_low_activity_metric_weights(
    metric_weights: dict[str, float] | None,
) -> tuple[tuple[str, float], ...]:
    weights = dict(DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS if metric_weights is None else metric_weights)
    expected_fields = tuple(DEFAULT_LOW_ACTIVITY_METRIC_WEIGHTS.keys())
    unknown_fields = sorted(set(weights.keys()) - set(expected_fields))
    missing_fields = [field_name for field_name in expected_fields if field_name not in weights]
    if unknown_fields:
        raise ValueError(f"Unknown low-activity metric weights: {unknown_fields}")
    if missing_fields:
        raise ValueError(f"Missing low-activity metric weights: {missing_fields}")
    total_weight = 0.0
    normalized_fields: list[tuple[str, float]] = []
    for field_name in expected_fields:
        value = float(weights[field_name])
        if value < 0.0:
            raise ValueError("low-activity metric weights must be >= 0.0.")
        total_weight += value
        normalized_fields.append((field_name, value))
    if total_weight <= 0.0:
        raise ValueError("At least one low-activity metric weight must be > 0.0.")
    return tuple(
        (field_name, float(weight) / total_weight)
        for field_name, weight in normalized_fields
    )


def build_checkpoint_selection_row(
    checkpoint: dict[str, object],
    low_activity_metrics_by_step: dict[int, dict[str, object]] | None = None,
) -> dict[str, object]:
    loss_metrics = dict(checkpoint["loss_metrics"])
    rms_ratio = float(loss_metrics.get("decoded_to_target_rms_ratio", 0.0))
    row = {
        "step": int(checkpoint["step"]),
        "loss_total": round(float(loss_metrics["loss_total"]), 6),
        "loss_waveform": round(float(loss_metrics.get("loss_waveform", 0.0)), 6),
        "loss_stft": round(float(loss_metrics.get("loss_stft", 0.0)), 6),
        "loss_rms_guard": round(float(loss_metrics.get("loss_rms_guard", 0.0)), 6),
        "decoded_to_target_rms_ratio": round(rms_ratio, 6),
        "rms_ratio_deviation": round(abs(rms_ratio - 1.0), 6),
    }
    if low_activity_metrics_by_step is not None:
        row["low_activity_metrics"] = build_low_activity_candidate_metrics(
            low_activity_metrics_by_step=low_activity_metrics_by_step,
            step=int(checkpoint["step"]),
        )
    return row


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
    ]
    low_activity_probe_analysis = summary.get("low_activity_probe_analysis")
    if isinstance(low_activity_probe_analysis, dict):
        governance_template = low_activity_probe_analysis.get("governance_template", {})
        lines.extend(
            [
                "## Low-Activity Governance",
                f"- probe_path: {low_activity_probe_analysis['probe_path']}",
                f"- audio_source: {low_activity_probe_analysis['audio_source']}",
            ]
        )
        for item in low_activity_probe_analysis.get("summary_lines", []):
            lines.append(f"- {item}")
        if isinstance(governance_template, dict) and governance_template:
            fragmentation_axis = governance_template.get("fragmentation_axis", {})
            leakage_strength_axis = governance_template.get("leakage_strength_axis", {})
            lines.append("### Dual-Axis Governance Template")
            lines.append(f"- mode: {governance_template.get('mode', 'unavailable')}")
            if isinstance(fragmentation_axis, dict):
                lines.append(
                    "- fragmentation_axis: "
                    f"best_fragmentation={format_branch_label_group(fragmentation_axis.get('best_fragmentation_branches', []))} "
                    f"best_alignment={format_branch_label_group(fragmentation_axis.get('best_alignment_branches', []))} "
                    f"best_quietness={format_branch_label_group(fragmentation_axis.get('best_quietness_branches', []))}"
                )
                note = fragmentation_axis.get("note")
                if isinstance(note, str) and note.strip():
                    lines.append(f"- fragmentation_note: {note}")
            if isinstance(leakage_strength_axis, dict):
                lines.append(
                    "- leakage_strength_axis: "
                    f"best_leakage_strength={format_branch_label_group(leakage_strength_axis.get('best_leakage_strength_branches', []))} "
                    f"worst_floor_leakage={format_branch_label_group(leakage_strength_axis.get('worst_floor_leakage_branches', []))}"
                )
                note = leakage_strength_axis.get("note")
                if isinstance(note, str) and note.strip():
                    lines.append(f"- leakage_note: {note}")
            cross_axis_note = governance_template.get("cross_axis_note")
            if isinstance(cross_axis_note, str) and cross_axis_note.strip():
                lines.append(f"- {cross_axis_note}")
        lines.append("### Branch Aggregates")
        for branch_label, aggregate in low_activity_probe_analysis.get("branch_aggregates", {}).items():
            lines.append(
                f"- {branch_label}: "
                f"fragmentation={aggregate['mean_fragmentation_score']} "
                f"active_fraction={aggregate['mean_active_fraction']} "
                f"alignment_mae={aggregate['mean_activity_alignment_mae']} "
                f"activity_excess={aggregate['mean_activity_excess_mean']} "
                f"waveform_rms={aggregate['mean_waveform_rms']} "
                f"sample_delta_peak={aggregate['mean_sample_delta_peak']}"
            )
        leakage_strength_ranking = low_activity_probe_analysis.get("ranking", {}).get(
            "worst_floor_leakage_strength_ranking",
            [],
        )
        if isinstance(leakage_strength_ranking, list) and leakage_strength_ranking:
            lines.append("### Worst-Floor-Leakage Strength Tie-Break")
            for item in leakage_strength_ranking:
                lines.append(
                    f"- branch={item['branch_label']} "
                    f"{item['metric_name']}={item['metric_value']}"
                )
        leakage_smoothness_ranking = low_activity_probe_analysis.get("ranking", {}).get(
            "worst_floor_leakage_smoothness_ranking",
            [],
        )
        if isinstance(leakage_smoothness_ranking, list) and leakage_smoothness_ranking:
            lines.append("### Worst-Floor-Leakage Tie-Break")
            for item in leakage_smoothness_ranking:
                lines.append(
                    f"- branch={item['branch_label']} "
                    f"{item['metric_name']}={item['metric_value']}"
                )
        lines.append("### Top Windows")
        for item in low_activity_probe_analysis.get("top_windows", []):
            lines.append(
                f"- record_id={item['record_id']} segment_index={item['segment_index']} "
                f"delta_fragmentation_score={item['delta_fragmentation_score']} "
                f"worst_branch={item['worst_branch']} best_branch={item['best_branch']} "
                f"target_context_toggle_mean={item['target_context_toggle_mean']} "
                f"target_boundary_jump_max={item['target_boundary_jump_max']}"
            )
        lines.append("")
    low_activity_soft_rerank = summary.get("low_activity_soft_rerank")
    if isinstance(low_activity_soft_rerank, dict):
        lines.extend(
            [
                "## Low-Activity Soft Rerank",
                f"- enabled: {low_activity_soft_rerank['enabled']}",
                f"- selection_mode: {low_activity_soft_rerank['selection_mode']}",
                f"- soft_validation_ratio: {low_activity_soft_rerank['soft_validation_ratio']}",
                f"- soft_validation_threshold: {low_activity_soft_rerank['soft_validation_threshold']}",
                f"- eligible_candidate_count: {low_activity_soft_rerank['eligible_candidate_count']}",
            ]
        )
        selected_candidate = low_activity_soft_rerank.get("selected_candidate")
        if isinstance(selected_candidate, dict):
            lines.append(
                "- selected_candidate: "
                f"step={selected_candidate['step']} "
                f"score={selected_candidate['low_activity_governance_score']} "
                f"loss_total={selected_candidate['loss_total']} "
                f"rms_ratio_deviation={selected_candidate['rms_ratio_deviation']}"
            )
        metric_weights = low_activity_soft_rerank.get("metric_weights")
        if isinstance(metric_weights, dict):
            lines.append(f"- metric_weights: {json.dumps(metric_weights, ensure_ascii=False)}")
        lines.append("### Ranked Candidates")
        for candidate in low_activity_soft_rerank.get("ranked_candidates", []):
            lines.append(
                f"- rank={candidate['low_activity_soft_rerank_rank']} step={candidate['step']} "
                f"score={candidate['low_activity_governance_score']} "
                f"loss_total={candidate['loss_total']} "
                f"fragmentation={candidate['low_activity_metrics']['mean_fragmentation_score']} "
                f"active_fraction={candidate['low_activity_metrics']['mean_active_fraction']} "
                f"alignment_mae={candidate['low_activity_metrics']['mean_activity_alignment_mae']} "
                f"activity_excess={candidate['low_activity_metrics']['mean_activity_excess_mean']} "
                f"waveform_rms={candidate['low_activity_metrics']['mean_waveform_rms']}"
            )
        for note in low_activity_soft_rerank.get("notes", []):
            lines.append(f"- {note}")
        lines.append("")
    lines.extend([
        "## Late Candidates",
    ])
    for candidate in summary["late_candidates"]:
        pairwise_review = candidate.get("pairwise_review")
        pairwise_text = "pairwise_review=null"
        if pairwise_review is not None:
            pairwise_text = (
                f"pairwise={pairwise_review['from_step']}->{pairwise_review['to_step']} "
                f"worsened_ratio={pairwise_review['worsened_ratio']} "
                f"avg_delta={pairwise_review['average_delta_loss_total']}"
            )
        low_activity_text = ""
        low_activity_metrics = candidate.get("low_activity_metrics")
        if isinstance(low_activity_metrics, dict):
            low_activity_text = (
                " "
                f"low_activity(fragmentation={low_activity_metrics['mean_fragmentation_score']} "
                f"active_fraction={low_activity_metrics['mean_active_fraction']} "
                f"alignment_mae={low_activity_metrics['mean_activity_alignment_mae']} "
                f"activity_excess={low_activity_metrics['mean_activity_excess_mean']} "
                f"waveform_rms={low_activity_metrics['mean_waveform_rms']} "
                f"sample_delta_peak={low_activity_metrics['mean_sample_delta_peak']})"
            )
        soft_rerank_text = ""
        if candidate.get("low_activity_governance_score") is not None:
            soft_rerank_text = (
                " "
                f"soft_rerank(score={candidate['low_activity_governance_score']} "
                f"rank={candidate['low_activity_soft_rerank_rank']})"
            )
        lines.append(
            f"- step={candidate['step']} loss_total={candidate['loss_total']} "
            f"rms_ratio={candidate['decoded_to_target_rms_ratio']} "
            f"rms_ratio_deviation={candidate['rms_ratio_deviation']} "
            f"within_validation_guard={candidate['within_validation_guard']} "
            f"qualifies_as_stable_late_stop={candidate['qualifies_as_stable_late_stop']} "
            f"{pairwise_text}{low_activity_text}{soft_rerank_text}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
