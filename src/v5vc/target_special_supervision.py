from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import statistics
from collections import Counter
from pathlib import Path

from v5vc.data_scan import write_json, write_manifest
from v5vc.manifest_builder import load_jsonl


def analyze_round1_target_special_supervision(
    split_dir: Path,
    weak_event_hints_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
    proxy_core_top_k: int,
    proxy_relaxed_top_k: int,
) -> None:
    if proxy_core_top_k <= 0:
        raise ValueError("proxy_core_top_k must be positive.")
    if proxy_relaxed_top_k < proxy_core_top_k:
        raise ValueError("proxy_relaxed_top_k must be greater than or equal to proxy_core_top_k.")

    split_dir = split_dir.resolve()
    weak_event_hints_path = weak_event_hints_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    merged_rows = load_merged_target_rows(split_dir=split_dir, weak_event_hints_path=weak_event_hints_path)
    special_rows = [row for row in merged_rows if row["split_name"] == "target_special_eval"]
    candidate_rows = [row for row in merged_rows if row["split_name"] != "target_special_eval"]
    special_profile = build_special_profile(special_rows)

    enrich_candidate_rows(candidate_rows=candidate_rows, special_profile=special_profile)
    sorted_candidates = sorted(
        candidate_rows,
        key=lambda row: (
            -float(row["special_proximity_score"]),
            int(row["lexical_char_count"]),
            float(row["duration_sec"]),
            int(row["terminal_boundary_count"]),
            int(row["pause_boundary_count"]),
            str(row["record_id"]),
        ),
    )
    core_ids = {str(row["record_id"]) for row in sorted_candidates[:proxy_core_top_k]}
    relaxed_ids = {str(row["record_id"]) for row in sorted_candidates[:proxy_relaxed_top_k]}

    all_rows = []
    for row in merged_rows:
        row_copy = dict(row)
        pool_memberships = build_pool_memberships(
            row=row_copy,
            core_ids=core_ids,
            relaxed_ids=relaxed_ids,
        )
        row_copy["pool_memberships"] = pool_memberships
        all_rows.append(row_copy)

    pool_order = [
        "challenge_anchor",
        "challenge_proxy_core",
        "challenge_proxy_relaxed",
        "micro_pause_none_singleton_strict",
        "micro_pause_none_singleton_relaxed",
        "micro_singleton_anypunct_relaxed",
        "micro_singleton_anypunct_expansion",
        "short_pause_no_terminal",
        "short_terminal_burst",
        "structural_clause_ge4_no_final_terminal",
        "structural_multi_terminal",
        "structural_question_exclaim",
        "structural_clause_ge4",
        "structural_no_final_terminal",
    ]
    pool_summaries = {
        pool_name: build_pool_summary(rows=all_rows, pool_name=pool_name)
        for pool_name in pool_order
    }

    summary = {
        "split_dir": split_dir.as_posix(),
        "weak_event_hints_path": weak_event_hints_path.as_posix(),
        "data_output_dir": data_output_dir.as_posix(),
        "report_output_dir": report_output_dir.as_posix(),
        "proxy_core_top_k": proxy_core_top_k,
        "proxy_relaxed_top_k": proxy_relaxed_top_k,
        "special_profile": special_profile,
        "pool_summaries": pool_summaries,
        "recommended_focus": build_recommended_focus(pool_summaries=pool_summaries),
        "notes": [
            "challenge_anchor corresponds to the true target_special_eval slice and must remain evaluation-only.",
            "special_proximity_score is a heuristic discovery score for proxy-pool construction, not a training or evaluation metric.",
            "The structural pools are intended to expose supervision axes that generic utterance-level aux losses were flattening together.",
        ],
    }

    write_manifest(data_output_dir / "target_special_supervision_sidecar.jsonl", all_rows)
    write_json(data_output_dir / "target_special_supervision_pools.json", pool_summaries)
    write_json(report_output_dir / "target_special_supervision_summary.json", summary)
    (report_output_dir / "target_special_supervision_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )



def load_merged_target_rows(
    split_dir: Path,
    weak_event_hints_path: Path,
) -> list[dict[str, object]]:
    hint_map = {
        str(row["record_id"]): row
        for row in load_jsonl(weak_event_hints_path)
    }
    merged_rows: list[dict[str, object]] = []
    for split_name in ("target_train", "target_validation", "target_special_eval"):
        for record in load_jsonl(split_dir / f"{split_name}.jsonl"):
            record_id = str(record["record_id"])
            hints = hint_map.get(record_id)
            if hints is None:
                raise ValueError(f"Missing weak_event_hints row for {record_id}.")
            merged_rows.append(
                {
                    "record_id": record_id,
                    "split_name": split_name,
                    "audio_path": str(record["audio_path"]),
                    "text_clean": str(record["text"]["clean"] or ""),
                    "duration_sec": round(float(hints["duration_sec"]), 6),
                    "lexical_char_count": int(hints["lexical_char_count"]),
                    "pause_boundary_count": int(hints["pause_boundary_count"]),
                    "terminal_boundary_count": int(hints["terminal_boundary_count"]),
                    "clause_count": int(hints["clause_count"]),
                    "utterance_structure_type": str(hints["utterance_structure_type"]),
                    "final_terminal_type": str(hints["final_terminal_type"]),
                    "structure_flags": dict(hints["structure_flags"]),
                    "nonverbal_only": bool(hints["nonverbal_only"]),
                }
            )
    return merged_rows


def build_special_profile(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        raise ValueError("target_special_eval rows are required to build the special profile.")
    duration_values = [float(row["duration_sec"]) for row in rows]
    return {
        "record_count": len(rows),
        "duration_sec": build_numeric_summary(duration_values),
        "lexical_char_count_values": sorted(int(row["lexical_char_count"]) for row in rows),
        "pause_boundary_count_values": sorted(int(row["pause_boundary_count"]) for row in rows),
        "terminal_boundary_count_values": sorted(int(row["terminal_boundary_count"]) for row in rows),
        "clause_count_values": sorted(int(row["clause_count"]) for row in rows),
        "utterance_structure_type_counts": dict(
            sorted(Counter(str(row["utterance_structure_type"]) for row in rows).items())
        ),
        "final_terminal_type_counts": dict(
            sorted(Counter(str(row["final_terminal_type"]) for row in rows).items())
        ),
        "duration_ceiling_sec": round(max(duration_values), 6),
        "duration_median_sec": round(statistics.median(duration_values), 6),
    }


def enrich_candidate_rows(
    candidate_rows: list[dict[str, object]],
    special_profile: dict[str, object],
) -> None:
    lexical_values = [int(row["lexical_char_count"]) for row in candidate_rows]
    duration_values = [float(row["duration_sec"]) for row in candidate_rows]
    clause_values = [int(row["clause_count"]) for row in candidate_rows]
    pause_values = [int(row["pause_boundary_count"]) for row in candidate_rows]
    terminal_values = [int(row["terminal_boundary_count"]) for row in candidate_rows]
    duration_ceiling_sec = float(special_profile["duration_ceiling_sec"])

    for row in candidate_rows:
        lexical_closeness = 1.0 - percentile_rank(lexical_values, int(row["lexical_char_count"]))
        duration_closeness = 1.0 - percentile_rank(duration_values, float(row["duration_sec"]))
        clause_closeness = 1.0 - percentile_rank(clause_values, int(row["clause_count"]))
        pause_closeness = 1.0 - percentile_rank(pause_values, int(row["pause_boundary_count"]))
        terminal_closeness = 1.0 - percentile_rank(terminal_values, int(row["terminal_boundary_count"]))
        final_none_bonus = 1.0 if str(row["final_terminal_type"]) == "none" else 0.0
        no_terminal_bonus = 1.0 if int(row["terminal_boundary_count"]) == 0 else 0.0
        within_special_duration_ceiling = float(row["duration_sec"]) <= duration_ceiling_sec
        duration_ceiling_bonus = 1.0 if within_special_duration_ceiling else 0.0
        score = (
            0.35 * lexical_closeness
            + 0.2 * duration_closeness
            + 0.15 * clause_closeness
            + 0.1 * pause_closeness
            + 0.05 * terminal_closeness
            + 0.05 * final_none_bonus
            + 0.05 * no_terminal_bonus
            + 0.05 * duration_ceiling_bonus
        )
        row["within_special_duration_ceiling"] = within_special_duration_ceiling
        row["special_proximity_score"] = round(score, 6)


def percentile_rank(values: list[int] | list[float], value: int | float) -> float:
    if len(values) <= 1:
        return 0.0
    less_or_equal = sum(1 for item in values if item <= value)
    return (less_or_equal - 1) / (len(values) - 1)


def build_pool_memberships(
    row: dict[str, object],
    core_ids: set[str],
    relaxed_ids: set[str],
) -> dict[str, bool]:
    lexical_char_count = int(row["lexical_char_count"])
    duration_sec = float(row["duration_sec"])
    pause_boundary_count = int(row["pause_boundary_count"])
    terminal_boundary_count = int(row["terminal_boundary_count"])
    clause_count = int(row["clause_count"])
    final_terminal_type = str(row["final_terminal_type"])
    structure_flags = dict(row["structure_flags"])
    record_id = str(row["record_id"])
    within_special_duration_ceiling = bool(row.get("within_special_duration_ceiling", False))
    return {
        "challenge_anchor": str(row["split_name"]) == "target_special_eval",
        "challenge_proxy_core": record_id in core_ids,
        "challenge_proxy_relaxed": record_id in relaxed_ids,
        "micro_pause_none_singleton_strict": (
            str(row["split_name"]) != "target_special_eval"
            and within_special_duration_ceiling
            and lexical_char_count <= 1
            and pause_boundary_count == 1
            and terminal_boundary_count == 0
            and clause_count == 1
            and final_terminal_type == "none"
        ),
        "micro_pause_none_singleton_relaxed": (
            str(row["split_name"]) != "target_special_eval"
            and duration_sec <= 2.2
            and lexical_char_count <= 2
            and pause_boundary_count == 1
            and terminal_boundary_count == 0
            and clause_count == 1
            and final_terminal_type == "none"
        ),
        "micro_singleton_anypunct_relaxed": (
            str(row["split_name"]) != "target_special_eval"
            and duration_sec <= 2.2
            and lexical_char_count <= 2
            and pause_boundary_count <= 1
            and terminal_boundary_count <= 1
            and clause_count == 1
        ),
        "micro_singleton_anypunct_expansion": (
            str(row["split_name"]) != "target_special_eval"
            and duration_sec <= 2.2
            and lexical_char_count <= 2
            and pause_boundary_count <= 1
            and terminal_boundary_count <= 1
            and clause_count == 1
            and not (
                within_special_duration_ceiling
                and lexical_char_count <= 1
                and pause_boundary_count == 1
                and terminal_boundary_count == 0
                and final_terminal_type == "none"
            )
        ),
        "short_pause_no_terminal": (
            str(row["split_name"]) != "target_special_eval"
            and lexical_char_count <= 8
            and duration_sec <= 2.2
            and pause_boundary_count >= 1
            and terminal_boundary_count == 0
        ),
        "short_terminal_burst": (
            str(row["split_name"]) != "target_special_eval"
            and lexical_char_count <= 8
            and duration_sec <= 2.2
            and terminal_boundary_count >= 1
        ),
        "structural_multi_terminal": bool(structure_flags.get("multi_terminal")),
        "structural_question_exclaim": bool(
            structure_flags.get("question_utterance") or structure_flags.get("exclamation_utterance")
        ),
        "structural_clause_ge4_no_final_terminal": clause_count >= 4 and final_terminal_type == "none",
        "structural_clause_ge4": clause_count >= 4,
        "structural_no_final_terminal": lexical_char_count > 0 and final_terminal_type == "none",
    }


def build_pool_summary(
    rows: list[dict[str, object]],
    pool_name: str,
) -> dict[str, object]:
    pool_rows = [row for row in rows if bool(row["pool_memberships"][pool_name])]
    split_counts = Counter(str(row["split_name"]) for row in pool_rows)
    structure_counts = Counter(str(row["utterance_structure_type"]) for row in pool_rows)
    final_terminal_counts = Counter(str(row["final_terminal_type"]) for row in pool_rows)
    return {
        "pool_name": pool_name,
        "record_count": len(pool_rows),
        "split_counts": dict(sorted(split_counts.items())),
        "duration_sec": build_numeric_summary(float(row["duration_sec"]) for row in pool_rows),
        "lexical_char_count": build_numeric_summary(int(row["lexical_char_count"]) for row in pool_rows),
        "clause_count": build_numeric_summary(int(row["clause_count"]) for row in pool_rows),
        "pause_boundary_count": build_numeric_summary(int(row["pause_boundary_count"]) for row in pool_rows),
        "terminal_boundary_count": build_numeric_summary(int(row["terminal_boundary_count"]) for row in pool_rows),
        "special_proximity_score": build_numeric_summary(
            float(row["special_proximity_score"]) for row in pool_rows if "special_proximity_score" in row
        ),
        "utterance_structure_type_counts": dict(sorted(structure_counts.items())),
        "final_terminal_type_counts": dict(sorted(final_terminal_counts.items())),
        "examples": [
            {
                "record_id": str(row["record_id"]),
                "split_name": str(row["split_name"]),
                "duration_sec": round(float(row["duration_sec"]), 6),
                "lexical_char_count": int(row["lexical_char_count"]),
                "pause_boundary_count": int(row["pause_boundary_count"]),
                "terminal_boundary_count": int(row["terminal_boundary_count"]),
                "clause_count": int(row["clause_count"]),
                "final_terminal_type": str(row["final_terminal_type"]),
                "special_proximity_score": round(float(row.get("special_proximity_score", 0.0)), 6),
                "text_clean": str(row["text_clean"]),
            }
            for row in sorted(
                pool_rows,
                key=lambda item: (
                    -float(item.get("special_proximity_score", 0.0)),
                    int(item["lexical_char_count"]),
                    float(item["duration_sec"]),
                    str(item["record_id"]),
                ),
            )[:12]
        ],
    }


def build_numeric_summary(values: list[int] | list[float] | Counter | object) -> dict[str, object]:
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


def build_recommended_focus(pool_summaries: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "bucket": "micro_pause_none_singleton_strict",
            "reason": (
                "Closest currently available train-side proxy to the nonverbal special slice. "
                "Use this as the first clause-free singleton supervision pool before revisiting any "
                "multi-clause formal proxy."
            ),
            "record_count": int(pool_summaries["micro_pause_none_singleton_strict"]["record_count"]),
        },
        {
            "bucket": "challenge_proxy_core",
            "reason": (
                "Closest train/validation proxy to target_special_eval. Use this for special-adjacent "
                "sampling or supervision stress without leaking the eval slice."
            ),
            "record_count": int(pool_summaries["challenge_proxy_core"]["record_count"]),
        },
        {
            "bucket": "micro_singleton_anypunct_expansion",
            "reason": (
                "Outer-ring micro-utterance cohort formed by the records that sit just outside the strict "
                "singleton sparse proxy. Useful when the next probe needs punctuation-aware or z_art-facing "
                "restoration without reusing the exact same strict samples."
            ),
            "record_count": int(pool_summaries["micro_singleton_anypunct_expansion"]["record_count"]),
        },
        {
            "bucket": "structural_clause_ge4_no_final_terminal",
            "reason": (
                "A narrower clause-rich pool that keeps long structural complexity without forcing a final "
                "terminal shape. Useful when full clause_ge4 supervision starts to fight the challenge-adjacent "
                "late trajectory."
            ),
            "record_count": int(pool_summaries["structural_clause_ge4_no_final_terminal"]["record_count"]),
        },
        {
            "bucket": "structural_multi_terminal",
            "reason": (
                "Largest direct terminal-shape pool. Suitable when the next experiment needs explicit "
                "multi-terminal supervision instead of another global aux loss."
            ),
            "record_count": int(pool_summaries["structural_multi_terminal"]["record_count"]),
        },
        {
            "bucket": "structural_clause_ge4",
            "reason": (
                "Captures long clause-rich utterances that current compact supervision may be flattening. "
                "Useful for a separate complexity-aware structural objective."
            ),
            "record_count": int(pool_summaries["structural_clause_ge4"]["record_count"]),
        },
        {
            "bucket": "structural_question_exclaim",
            "reason": (
                "Provides a stable expressive-terminal pool for question/exclamation behavior, which should "
                "stay separated from the near-nonverbal challenge proxy."
            ),
            "record_count": int(pool_summaries["structural_question_exclaim"]["record_count"]),
        },
    ]


def build_markdown(summary: dict[str, object]) -> str:
    special_profile = summary["special_profile"]
    pool_summaries = summary["pool_summaries"]
    lines = [
        "# round1 target-side special supervision blueprint",
        "",
        "## 目的",
        "- 把 `target_special_eval` 的真实边界、训练/验证中的近邻 proxy 样本、以及更大规模的结构型 supervision pool 统一整理成正式 sidecar。",
        "- 这一步只做数据/监督底账，不改训练逻辑。",
        "",
        "先说人话：",
        "- 现在需要先知道模型下一轮该重点看哪几类样本，而不是继续在全量数据上堆一个更聪明的小 loss。",
        "",
        "## special slice 当前画像",
        f"- `target_special_eval` 记录数: `{special_profile['record_count']}`",
        f"- 时长范围: `{special_profile['duration_sec']['min']} ~ {special_profile['duration_sec']['max']}` 秒",
        f"- 时长中位数: `{special_profile['duration_median_sec']}` 秒",
        f"- lexical char: `{special_profile['lexical_char_count_values']}`",
        f"- pause boundary: `{special_profile['pause_boundary_count_values']}`",
        f"- terminal boundary: `{special_profile['terminal_boundary_count_values']}`",
        f"- clause count: `{special_profile['clause_count_values']}`",
        f"- structure counts: `{special_profile['utterance_structure_type_counts']}`",
        f"- final terminal counts: `{special_profile['final_terminal_type_counts']}`",
        "",
        "结论：",
        "- `round1.1` 的 special slice 仍然是纯 nonverbal challenge。它不能被拿去训练，但它可以明确告诉我们：",
        "  下一轮应该先找“更像它的训练代理样本”和“更明确的结构监督池”。",
        "",
        "## 关键 supervision pools",
    ]

    for pool_name in (
        "challenge_proxy_core",
        "challenge_proxy_relaxed",
        "micro_pause_none_singleton_strict",
        "micro_pause_none_singleton_relaxed",
        "micro_singleton_anypunct_relaxed",
        "micro_singleton_anypunct_expansion",
        "short_pause_no_terminal",
        "short_terminal_burst",
        "structural_multi_terminal",
        "structural_question_exclaim",
        "structural_clause_ge4_no_final_terminal",
        "structural_clause_ge4",
        "structural_no_final_terminal",
    ):
        pool = pool_summaries[pool_name]
        lines.extend(
            [
                f"### `{pool_name}`",
                f"- 记录数: `{pool['record_count']}`",
                f"- split counts: `{pool['split_counts']}`",
                f"- lexical char 中位数: `{pool['lexical_char_count']['median']}`",
                f"- 时长中位数: `{pool['duration_sec']['median']}` 秒",
                f"- clause 中位数: `{pool['clause_count']['median']}`",
                f"- pause / terminal 中位数: `{pool['pause_boundary_count']['median']} / {pool['terminal_boundary_count']['median']}`",
                f"- structure counts: `{pool['utterance_structure_type_counts']}`",
                f"- final terminal counts: `{pool['final_terminal_type_counts']}`",
            ]
        )
        if pool["examples"]:
            lines.append("- 示例:")
            for example in pool["examples"][:6]:
                lines.append(
                    "  - "
                    f"`{example['record_id']}` | "
                    f"score `{example['special_proximity_score']}` | "
                    f"lex `{example['lexical_char_count']}` | "
                    f"dur `{example['duration_sec']}` | "
                    f"text `{example['text_clean']}`"
                )
        lines.append("")

    lines.extend(
        [
            "## 当前建议",
            "- `challenge_anchor` 继续严格保持 eval-only。",
            "- 下一轮数据/监督实验应优先从 `micro_pause_none_singleton_strict` 入手，把 special supervision 从 `clause-shape` 转到 clause-free singleton proxy。",
            "- `challenge_proxy_core` 继续保留为 special-adjacent stress pool，但不再默认它就是最贴近 final challenge 的第一代理。",
            "- `micro_singleton_anypunct_expansion` 适合作为 strict singleton 之外的差分 outer pool，用于更外层的 punctuation / `z_art` restoration 探针。",
            "- `structural_multi_terminal / structural_question_exclaim / structural_clause_ge4` 应视为三条独立 supervision 轴，不要再混成一个统称的 structural proxy。",
            "- 若需要更稳的样本量，可以把 `micro_pause_none_singleton_relaxed` 作为第二层 singleton proxy pool，但不要直接替代 strict pool。",
            "",
            "## 产物",
            f"- `data_output_dir`: `{summary['data_output_dir']}`",
            f"- `report_output_dir`: `{summary['report_output_dir']}`",
            "- sidecar:",
            "  - `target_special_supervision_sidecar.jsonl`",
            "  - `target_special_supervision_pools.json`",
            "- reports:",
            "  - `target_special_supervision_summary.json`",
            "  - `target_special_supervision_summary.md`",
        ]
    )
    return "\n".join(lines) + "\n"
