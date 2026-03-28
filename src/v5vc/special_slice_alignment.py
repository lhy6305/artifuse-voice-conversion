from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import statistics
from collections import Counter
from pathlib import Path

from v5vc.data_scan import write_json
from v5vc.manifest_builder import load_jsonl


DISTANCE_FEATURES = (
    "duration_sec",
    "lexical_char_count",
    "pause_boundary_count",
    "terminal_boundary_count",
    "clause_count",
    "clause_span_count",
)


def analyze_offline_mvp_special_slice_alignment(
    split_dir: Path,
    weak_event_hints_path: Path,
    target_special_supervision_path: Path,
    output_dir: Path,
    top_nearest: int,
) -> None:
    if top_nearest <= 0:
        raise ValueError("top_nearest must be positive.")

    split_dir = split_dir.resolve()
    weak_event_hints_path = weak_event_hints_path.resolve()
    target_special_supervision_path = target_special_supervision_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    rows = load_merged_rows(
        split_dir=split_dir,
        weak_event_hints_path=weak_event_hints_path,
        target_special_supervision_path=target_special_supervision_path,
    )
    special_rows = [row for row in rows if row["split_name"] == "target_special_eval"]
    train_rows = [row for row in rows if row["split_name"] == "target_train"]
    validation_rows = [row for row in rows if row["split_name"] == "target_validation"]

    special_profile = build_special_profile(special_rows)
    reference = build_feature_reference(special_rows)
    assign_special_distance(rows=rows, reference=reference)

    split_signature_coverage = build_split_signature_coverage(
        train_rows=train_rows,
        validation_rows=validation_rows,
        special_rows=special_rows,
    )
    pool_alignment = build_pool_alignment(train_rows=train_rows)
    nearest_train_records = build_nearest_records(train_rows=train_rows, top_nearest=top_nearest)
    heuristic_cohorts = build_heuristic_cohorts(train_rows=train_rows)
    next_step_recommendation = build_next_step_recommendation(
        split_signature_coverage=split_signature_coverage,
        heuristic_cohorts=heuristic_cohorts,
    )

    summary = {
        "split_dir": split_dir.as_posix(),
        "weak_event_hints_path": weak_event_hints_path.as_posix(),
        "target_special_supervision_path": target_special_supervision_path.as_posix(),
        "special_profile": special_profile,
        "feature_reference": reference,
        "split_signature_coverage": split_signature_coverage,
        "existing_pool_alignment": pool_alignment,
        "nearest_train_records": nearest_train_records,
        "heuristic_cohorts": heuristic_cohorts,
        "next_step_recommendation": next_step_recommendation,
        "notes": [
            "special_signature is defined as nonverbal_only plus zero lexical, pause, terminal, clause, and clause-span support.",
            "special_distance is a simple normalized distance to the target_special_eval profile over duration and sparse-structure features.",
            "This report is diagnostic; it does not modify training sidecars or manifests.",
        ],
    }

    write_json(output_dir / "special_slice_alignment_summary.json", summary)
    (output_dir / "special_slice_alignment_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )



def load_merged_rows(
    split_dir: Path,
    weak_event_hints_path: Path,
    target_special_supervision_path: Path,
) -> list[dict[str, object]]:
    hint_map = {
        str(row["record_id"]): row
        for row in load_jsonl(weak_event_hints_path)
    }
    supervision_map = {
        str(row["record_id"]): row
        for row in load_jsonl(target_special_supervision_path)
    }
    merged_rows: list[dict[str, object]] = []
    for split_name in ("target_train", "target_validation", "target_special_eval"):
        for record in load_jsonl(split_dir / f"{split_name}.jsonl"):
            record_id = str(record["record_id"])
            hints = hint_map.get(record_id)
            supervision = supervision_map.get(record_id)
            if hints is None:
                raise ValueError(f"Missing weak_event_hints row for {record_id}.")
            if supervision is None:
                raise ValueError(f"Missing target_special_supervision row for {record_id}.")
            clause_spans = hints.get("clause_spans")
            clause_transition_markers = hints.get("clause_transition_markers")
            pool_memberships = dict(supervision.get("pool_memberships", {}))
            merged_rows.append(
                {
                    "record_id": record_id,
                    "split_name": split_name,
                    "text_clean": str(hints.get("text_clean", record["text"]["clean"] or "")),
                    "duration_sec": round(float(hints["duration_sec"]), 6),
                    "lexical_char_count": int(hints["lexical_char_count"]),
                    "pause_boundary_count": int(hints["pause_boundary_count"]),
                    "terminal_boundary_count": int(hints["terminal_boundary_count"]),
                    "clause_count": int(hints["clause_count"]),
                    "utterance_structure_type": str(hints["utterance_structure_type"]),
                    "final_terminal_type": str(hints["final_terminal_type"]),
                    "nonverbal_only": bool(hints["nonverbal_only"]),
                    "clause_span_count": len(clause_spans or []),
                    "clause_transition_count": (
                        len(clause_transition_markers)
                        if isinstance(clause_transition_markers, list)
                        else 0
                    ),
                    "within_special_duration_ceiling": bool(
                        supervision.get("within_special_duration_ceiling", False)
                    ),
                    "special_proximity_score": round(
                        float(supervision.get("special_proximity_score", 0.0)),
                        6,
                    ),
                    "pool_memberships": {
                        str(key): bool(value)
                        for key, value in pool_memberships.items()
                    },
                }
            )
    return merged_rows


def build_special_profile(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        raise ValueError("target_special_eval rows are required.")
    return {
        "record_count": len(rows),
        "duration_sec": build_numeric_summary(float(row["duration_sec"]) for row in rows),
        "lexical_char_count": build_numeric_summary(int(row["lexical_char_count"]) for row in rows),
        "pause_boundary_count": build_numeric_summary(int(row["pause_boundary_count"]) for row in rows),
        "terminal_boundary_count": build_numeric_summary(int(row["terminal_boundary_count"]) for row in rows),
        "clause_count": build_numeric_summary(int(row["clause_count"]) for row in rows),
        "clause_span_count": build_numeric_summary(int(row["clause_span_count"]) for row in rows),
        "clause_transition_count": build_numeric_summary(
            int(row["clause_transition_count"]) for row in rows
        ),
        "utterance_structure_type_counts": dict(
            sorted(Counter(str(row["utterance_structure_type"]) for row in rows).items())
        ),
        "final_terminal_type_counts": dict(
            sorted(Counter(str(row["final_terminal_type"]) for row in rows).items())
        ),
        "nonverbal_only_count": sum(bool(row["nonverbal_only"]) for row in rows),
        "within_special_duration_ceiling_count": sum(
            bool(row["within_special_duration_ceiling"]) for row in rows
        ),
    }


def build_feature_reference(rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    reference: dict[str, dict[str, float]] = {}
    for feature_name in DISTANCE_FEATURES:
        values = [float(row[feature_name]) for row in rows]
        mean_value = sum(values) / len(values)
        std_value = statistics.pstdev(values) if len(values) > 1 else 0.0
        reference[feature_name] = {
            "mean": round(mean_value, 6),
            "std": round(std_value, 6),
            "effective_std": round(max(std_value, 1.0), 6),
        }
    return reference


def assign_special_distance(
    rows: list[dict[str, object]],
    reference: dict[str, dict[str, float]],
) -> None:
    for row in rows:
        squared_distance = 0.0
        for feature_name in DISTANCE_FEATURES:
            feature_reference = reference[feature_name]
            delta = float(row[feature_name]) - float(feature_reference["mean"])
            squared_distance += (delta / float(feature_reference["effective_std"])) ** 2
        row["special_distance"] = round(squared_distance ** 0.5, 6)


def build_split_signature_coverage(
    train_rows: list[dict[str, object]],
    validation_rows: list[dict[str, object]],
    special_rows: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    return {
        "target_train": build_signature_bucket(train_rows),
        "target_validation": build_signature_bucket(validation_rows),
        "target_special_eval": build_signature_bucket(special_rows),
    }


def build_signature_bucket(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "record_count": len(rows),
        "nonverbal_only_count": sum(bool(row["nonverbal_only"]) for row in rows),
        "lexical_char_count_zero": sum(int(row["lexical_char_count"]) == 0 for row in rows),
        "pause_boundary_count_zero": sum(int(row["pause_boundary_count"]) == 0 for row in rows),
        "terminal_boundary_count_zero": sum(int(row["terminal_boundary_count"]) == 0 for row in rows),
        "clause_count_zero": sum(int(row["clause_count"]) == 0 for row in rows),
        "clause_span_count_zero": sum(int(row["clause_span_count"]) == 0 for row in rows),
        "special_signature_count": sum(is_special_signature(row) for row in rows),
    }


def is_special_signature(row: dict[str, object]) -> bool:
    return (
        bool(row["nonverbal_only"])
        and int(row["lexical_char_count"]) == 0
        and int(row["pause_boundary_count"]) == 0
        and int(row["terminal_boundary_count"]) == 0
        and int(row["clause_count"]) == 0
        and int(row["clause_span_count"]) == 0
    )


def build_pool_alignment(train_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    pool_names = sorted(
        {
            pool_name
            for row in train_rows
            for pool_name in dict(row["pool_memberships"]).keys()
        }
    )
    alignment_rows: list[dict[str, object]] = []
    for pool_name in pool_names:
        pool_rows = [
            row
            for row in train_rows
            if bool(dict(row["pool_memberships"]).get(pool_name, False))
        ]
        if not pool_rows:
            continue
        alignment_rows.append(
            {
                "pool_name": pool_name,
                "record_count": len(pool_rows),
                "special_distance": build_numeric_summary(float(row["special_distance"]) for row in pool_rows),
                "nonverbal_only_count": sum(bool(row["nonverbal_only"]) for row in pool_rows),
                "lexical_char_count": build_numeric_summary(int(row["lexical_char_count"]) for row in pool_rows),
                "pause_boundary_count": build_numeric_summary(
                    int(row["pause_boundary_count"]) for row in pool_rows
                ),
                "terminal_boundary_count": build_numeric_summary(
                    int(row["terminal_boundary_count"]) for row in pool_rows
                ),
                "clause_count": build_numeric_summary(int(row["clause_count"]) for row in pool_rows),
                "clause_span_count": build_numeric_summary(int(row["clause_span_count"]) for row in pool_rows),
                "top_examples": build_examples(pool_rows, limit=8),
            }
        )
    alignment_rows.sort(
        key=lambda item: (
            float(item["special_distance"]["mean"] or 999999.0),
            -int(item["record_count"]),
            str(item["pool_name"]),
        )
    )
    return alignment_rows


def build_nearest_records(
    train_rows: list[dict[str, object]],
    top_nearest: int,
) -> list[dict[str, object]]:
    return build_examples(
        sorted(
            train_rows,
            key=lambda row: (
                float(row["special_distance"]),
                int(row["lexical_char_count"]),
                float(row["duration_sec"]),
                str(row["record_id"]),
            ),
        ),
        limit=top_nearest,
    )


def build_heuristic_cohorts(train_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    cohort_specs = [
        {
            "cohort_name": "micro_pause_none_singleton_strict",
            "description": "duration <= special ceiling, lexical <= 1, single pause, no terminal, clause = 1, final none",
            "predicate": lambda row: (
                float(row["duration_sec"]) <= 2.114989
                and int(row["lexical_char_count"]) <= 1
                and int(row["pause_boundary_count"]) == 1
                and int(row["terminal_boundary_count"]) == 0
                and int(row["clause_count"]) == 1
                and str(row["final_terminal_type"]) == "none"
            ),
        },
        {
            "cohort_name": "micro_pause_none_singleton_relaxed",
            "description": "duration <= 2.2, lexical <= 2, single pause, no terminal, clause = 1, final none",
            "predicate": lambda row: (
                float(row["duration_sec"]) <= 2.2
                and int(row["lexical_char_count"]) <= 2
                and int(row["pause_boundary_count"]) == 1
                and int(row["terminal_boundary_count"]) == 0
                and int(row["clause_count"]) == 1
                and str(row["final_terminal_type"]) == "none"
            ),
        },
        {
            "cohort_name": "micro_singleton_anypunct_relaxed",
            "description": "duration <= 2.2, lexical <= 2, pause <= 1, terminal <= 1, clause = 1",
            "predicate": lambda row: (
                float(row["duration_sec"]) <= 2.2
                and int(row["lexical_char_count"]) <= 2
                and int(row["pause_boundary_count"]) <= 1
                and int(row["terminal_boundary_count"]) <= 1
                and int(row["clause_count"]) == 1
            ),
        },
        {
            "cohort_name": "micro_no_terminal_singleton_relaxed",
            "description": "duration <= 2.2, lexical <= 2, no terminal, clause = 1",
            "predicate": lambda row: (
                float(row["duration_sec"]) <= 2.2
                and int(row["lexical_char_count"]) <= 2
                and int(row["terminal_boundary_count"]) == 0
                and int(row["clause_count"]) == 1
            ),
        },
        {
            "cohort_name": "micro_terminal_singleton_strict",
            "description": "duration <= special ceiling, lexical <= 1, no pause, single terminal, clause = 1",
            "predicate": lambda row: (
                float(row["duration_sec"]) <= 2.114989
                and int(row["lexical_char_count"]) <= 1
                and int(row["pause_boundary_count"]) == 0
                and int(row["terminal_boundary_count"]) == 1
                and int(row["clause_count"]) == 1
            ),
        },
    ]

    cohorts: list[dict[str, object]] = []
    for cohort_spec in cohort_specs:
        cohort_rows = [
            row
            for row in train_rows
            if cohort_spec["predicate"](row)
        ]
        cohorts.append(
            {
                "cohort_name": str(cohort_spec["cohort_name"]),
                "description": str(cohort_spec["description"]),
                "record_count": len(cohort_rows),
                "special_distance": build_numeric_summary(
                    float(row["special_distance"]) for row in cohort_rows
                ),
                "lexical_char_count": build_numeric_summary(
                    int(row["lexical_char_count"]) for row in cohort_rows
                ),
                "pause_boundary_count": build_numeric_summary(
                    int(row["pause_boundary_count"]) for row in cohort_rows
                ),
                "terminal_boundary_count": build_numeric_summary(
                    int(row["terminal_boundary_count"]) for row in cohort_rows
                ),
                "clause_count": build_numeric_summary(
                    int(row["clause_count"]) for row in cohort_rows
                ),
                "clause_span_count": build_numeric_summary(
                    int(row["clause_span_count"]) for row in cohort_rows
                ),
                "top_examples": build_examples(cohort_rows, limit=8),
            }
        )
    cohorts.sort(
        key=lambda item: (
            float(item["special_distance"]["mean"] or 999999.0),
            -int(item["record_count"]),
            str(item["cohort_name"]),
        )
    )
    return cohorts


def build_examples(
    rows: list[dict[str, object]],
    limit: int,
) -> list[dict[str, object]]:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            float(row["special_distance"]),
            int(row["lexical_char_count"]),
            float(row["duration_sec"]),
            str(row["record_id"]),
        ),
    )
    return [
        {
            "record_id": str(row["record_id"]),
            "split_name": str(row["split_name"]),
            "text_clean": str(row["text_clean"]),
            "duration_sec": round(float(row["duration_sec"]), 6),
            "lexical_char_count": int(row["lexical_char_count"]),
            "pause_boundary_count": int(row["pause_boundary_count"]),
            "terminal_boundary_count": int(row["terminal_boundary_count"]),
            "clause_count": int(row["clause_count"]),
            "clause_span_count": int(row["clause_span_count"]),
            "utterance_structure_type": str(row["utterance_structure_type"]),
            "final_terminal_type": str(row["final_terminal_type"]),
            "nonverbal_only": bool(row["nonverbal_only"]),
            "special_distance": round(float(row["special_distance"]), 6),
            "pool_memberships": [
                pool_name
                for pool_name, enabled in dict(row["pool_memberships"]).items()
                if bool(enabled)
            ],
        }
        for row in sorted_rows[:limit]
    ]


def build_next_step_recommendation(
    split_signature_coverage: dict[str, dict[str, object]],
    heuristic_cohorts: list[dict[str, object]],
) -> dict[str, object]:
    exact_train_signature_count = int(split_signature_coverage["target_train"]["special_signature_count"])
    train_clause_span_zero_count = int(split_signature_coverage["target_train"]["clause_span_count_zero"])
    recommended_cohort = next(
        (
            cohort
            for cohort in heuristic_cohorts
            if int(cohort["record_count"]) > 0
        ),
        None,
    )
    principle_change_required = exact_train_signature_count == 0 and train_clause_span_zero_count == 0
    return {
        "continue_training": True,
        "continue_current_d58_d59_line": False,
        "principle_change_required": principle_change_required,
        "reason": (
            "No train-side record matches the target_special_eval special signature, and train-side clause-span support never drops to zero."
            if principle_change_required
            else "There is at least partial train-side structural support for the special signature."
        ),
        "recommended_proxy_cohort": None if recommended_cohort is None else recommended_cohort["cohort_name"],
        "recommended_proxy_cohort_count": None if recommended_cohort is None else recommended_cohort["record_count"],
        "recommended_supervision_direction": (
            "Pivot from clause-shape supervision to clause-free singleton sparse-frame supervision over the closest micro-utterance cohort."
            if principle_change_required
            else "Refine the existing clause-aware supervision over the closest available proxy cohort."
        ),
    }


def build_numeric_summary(values: object) -> dict[str, object]:
    materialized = list(values)
    if not materialized:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
        }
    numeric_values = [float(item) for item in materialized]
    return {
        "count": len(numeric_values),
        "min": round(min(numeric_values), 6),
        "max": round(max(numeric_values), 6),
        "mean": round(sum(numeric_values) / len(numeric_values), 6),
        "median": round(statistics.median(numeric_values), 6),
    }


def build_markdown(summary: dict[str, object]) -> str:
    special_profile = summary["special_profile"]
    split_coverage = summary["split_signature_coverage"]
    recommendation = summary["next_step_recommendation"]
    nearest_records = summary["nearest_train_records"]
    heuristic_cohorts = summary["heuristic_cohorts"]
    pool_alignment = summary["existing_pool_alignment"]

    lines = [
        "# Special Slice Alignment Summary",
        "",
        "## Goal",
        "- Quantify how `target_special_eval` differs from train-side candidate cohorts.",
        "- Decide whether the next step should keep training or first change the proxy-supervision principle.",
        "",
        "## Special Signature",
        "- Definition: `nonverbal_only` plus zero lexical, pause, terminal, clause, and clause-span support.",
        f"- target_special_eval record_count: {special_profile['record_count']}",
        f"- target_special_eval nonverbal_only_count: {special_profile['nonverbal_only_count']}",
        f"- target_special_eval duration_sec: {special_profile['duration_sec']}",
        f"- target_special_eval lexical_char_count: {special_profile['lexical_char_count']}",
        f"- target_special_eval clause_span_count: {special_profile['clause_span_count']}",
        "",
        "## Split Coverage",
        f"- target_train: {split_coverage['target_train']}",
        f"- target_validation: {split_coverage['target_validation']}",
        f"- target_special_eval: {split_coverage['target_special_eval']}",
        "",
        "## Existing Pools",
    ]
    for row in pool_alignment[:5]:
        lines.append(
            f"- {row['pool_name']}: count={row['record_count']}, mean_special_distance={row['special_distance']['mean']}, min_special_distance={row['special_distance']['min']}"
        )
    lines.extend(
        [
            "",
            "## Heuristic Cohorts",
        ]
    )
    for cohort in heuristic_cohorts:
        lines.append(
            f"- {cohort['cohort_name']}: count={cohort['record_count']}, mean_special_distance={cohort['special_distance']['mean']}, min_special_distance={cohort['special_distance']['min']}"
        )
    lines.extend(
        [
            "",
            "## Nearest Train Records",
        ]
    )
    for row in nearest_records[:12]:
        lines.append(
            f"- {row['record_id']}: distance={row['special_distance']}, text={row['text_clean']}, lexical={row['lexical_char_count']}, pause={row['pause_boundary_count']}, terminal={row['terminal_boundary_count']}, clause={row['clause_count']}, clause_spans={row['clause_span_count']}"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            f"- continue_training: {recommendation['continue_training']}",
            f"- continue_current_d58_d59_line: {recommendation['continue_current_d58_d59_line']}",
            f"- principle_change_required: {recommendation['principle_change_required']}",
            f"- reason: {recommendation['reason']}",
            f"- recommended_proxy_cohort: {recommendation['recommended_proxy_cohort']}",
            f"- recommended_proxy_cohort_count: {recommendation['recommended_proxy_cohort_count']}",
            f"- recommended_supervision_direction: {recommendation['recommended_supervision_direction']}",
            "",
            "## Notes",
        ]
    )
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
