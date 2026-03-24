from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

from v5vc.manifest_builder import load_jsonl


CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION = "offline_mvp_heuristic_event_target_v1"
TARGET_EVENT_SEMANTIC_SIDECAR_VERSION = "target_event_semantic_sidecar_v1"
TARGET_EVENT_SEMANTIC_LABEL_SPACE_VERSION = "target_lexical_structure_semantics_v1"

CURRENT_RUNTIME_EVENT_DIMENSIONS = (
    {
        "index": 0,
        "name": "energy_gate",
        "category": "heuristic_frame_target",
        "description": "基于能量阈值的启发式活动门，不是设计态 fric/closure/burst 语义。",
    },
    {
        "index": 1,
        "name": "abs_delta_gate",
        "category": "heuristic_frame_target",
        "description": "基于帧间幅度变化的启发式变化门，不是显式事件类别。",
    },
    {
        "index": 2,
        "name": "high_zero_cross",
        "category": "heuristic_frame_target",
        "description": "基于过零率的高噪声启发式指标，不等价于设计态 fric 类别。",
    },
    {
        "index": 3,
        "name": "low_zero_cross_voiced_like",
        "category": "heuristic_frame_target",
        "description": "基于低过零率的浊音倾向启发式指标，不是设计态 p_voicing。",
    },
    {
        "index": 4,
        "name": "high_zero_cross_voiced_like",
        "category": "heuristic_frame_target",
        "description": "带 voiced-like 门的高过零率启发式指标，不是命名辅音语义。",
    },
    {
        "index": 5,
        "name": "delta_energy_rise",
        "category": "heuristic_frame_target",
        "description": "基于能量上升的启发式变化指标，不是显式 burst 标签。",
    },
    {
        "index": 6,
        "name": "delta_energy_fall",
        "category": "heuristic_frame_target",
        "description": "基于能量下降的启发式变化指标，不是显式 closure 标签。",
    },
    {
        "index": 7,
        "name": "energy_norm",
        "category": "heuristic_frame_target",
        "description": "归一化能量启发式指标，不是设计态 event semantic。",
    },
)


def build_current_runtime_event_semantics_meta() -> dict[str, object]:
    return {
        "event_probs_version": CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION,
        "event_prob_dimensions": [dimension["name"] for dimension in CURRENT_RUNTIME_EVENT_DIMENSIONS],
        "event_prob_dimension_specs": [dict(dimension) for dimension in CURRENT_RUNTIME_EVENT_DIMENSIONS],
        "semantic_status": "heuristic_frame_targets_not_design_e_evt",
        "recommended_contract_interpretation": (
            "当前 event_probs 只能解释为旧 offline MVP 启发式帧级事件目标，"
            "不能再当作设计稿中的命名 e_evt 语义。"
        ),
    }


def build_target_event_semantic_sidecar(
    weak_event_hints_path: Path,
    target_supervision_inventory_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
) -> dict[str, object]:
    weak_event_hints_path = weak_event_hints_path.resolve()
    target_supervision_inventory_path = target_supervision_inventory_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    weak_event_rows = load_jsonl(weak_event_hints_path)
    inventory_rows = load_jsonl(target_supervision_inventory_path)
    inventory_by_record_id = {
        str(row["record_id"]): row
        for row in inventory_rows
    }
    semantic_rows = [
        build_target_event_semantic_row(
            weak_event_row=weak_event_row,
            inventory_row=inventory_by_record_id.get(str(weak_event_row["record_id"])),
        )
        for weak_event_row in weak_event_rows
    ]
    summary = build_target_event_semantic_summary(
        weak_event_hints_path=weak_event_hints_path,
        target_supervision_inventory_path=target_supervision_inventory_path,
        semantic_rows=semantic_rows,
    )

    semantic_path = data_output_dir / "target_event_semantic_sidecar.jsonl"
    summary_json_path = report_output_dir / "target_event_semantic_sidecar_summary.json"
    summary_md_path = report_output_dir / "target_event_semantic_sidecar_summary.md"
    write_jsonl(semantic_path, semantic_rows)
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        render_target_event_semantic_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_target_event_semantic_row(
    weak_event_row: dict[str, object],
    inventory_row: dict[str, object] | None,
) -> dict[str, object]:
    inventory_text = (
        dict(inventory_row.get("text", {}))
        if isinstance(inventory_row, dict) and isinstance(inventory_row.get("text"), dict)
        else {}
    )
    supervision_sources = (
        dict(inventory_row.get("supervision_sources", {}))
        if isinstance(inventory_row, dict) and isinstance(inventory_row.get("supervision_sources"), dict)
        else {}
    )
    future_label_slots = (
        dict(inventory_row.get("future_label_slots", {}))
        if isinstance(inventory_row, dict) and isinstance(inventory_row.get("future_label_slots"), dict)
        else {
            "phone_sequence": None,
            "manner_sequence": None,
            "place_sequence": None,
            "boundary_alignment": None,
            "label_status": "pending_upgrade",
        }
    )
    punctuation_sequence = (
        list(inventory_row.get("punctuation_sequence", []))
        if isinstance(inventory_row, dict) and isinstance(inventory_row.get("punctuation_sequence"), list)
        else []
    )
    lexical_char_count = int(inventory_text.get("lexical_char_count", weak_event_row.get("lexical_char_count", 0)))
    nonverbal_only = bool(inventory_text.get("nonverbal_only", weak_event_row.get("nonverbal_only", False)))
    clean_text_available = bool(supervision_sources.get("clean_text_available", lexical_char_count > 0))
    punctuation_boundary_hints_available = bool(
        supervision_sources.get(
            "punctuation_boundary_hints_available",
            int(weak_event_row.get("pause_boundary_count", 0)) + int(weak_event_row.get("terminal_boundary_count", 0)) > 0,
        )
    )
    utterance_level_text_aux_available = bool(
        supervision_sources.get("utterance_level_text_aux_available", clean_text_available and not nonverbal_only)
    )
    phone_sequence_available = bool(supervision_sources.get("phone_sequence_available", False))
    manner_sequence_available = bool(supervision_sources.get("manner_sequence_available", False))
    place_sequence_available = bool(supervision_sources.get("place_sequence_available", False))
    forced_alignment_available = bool(supervision_sources.get("forced_alignment_available", False))
    audio_heuristic_event_target_available = bool(
        supervision_sources.get("audio_heuristic_event_target_available", True)
    )
    inventory_status = "matched_inventory" if isinstance(inventory_row, dict) else "weak_event_only_fallback"

    return {
        "record_id": str(weak_event_row["record_id"]),
        "split": str(weak_event_row.get("split", "unknown")),
        "audio_path": str(weak_event_row.get("audio_path", "")),
        "semantic_contract_version": TARGET_EVENT_SEMANTIC_SIDECAR_VERSION,
        "semantic_label_space_version": TARGET_EVENT_SEMANTIC_LABEL_SPACE_VERSION,
        "inventory_status": inventory_status,
        "semantic_scope": {
            "target_side_only": True,
            "boundary_semantics_available": True,
            "utterance_structure_semantics_available": True,
            "clean_text_available": clean_text_available,
            "punctuation_boundary_hints_available": punctuation_boundary_hints_available,
            "utterance_level_text_aux_available": utterance_level_text_aux_available,
            "phone_sequence_available": phone_sequence_available,
            "manner_sequence_available": manner_sequence_available,
            "place_sequence_available": place_sequence_available,
            "forced_alignment_available": forced_alignment_available,
            "audio_heuristic_event_target_available": audio_heuristic_event_target_available,
            "source_side_semantic_parity_available": False,
        },
        "current_runtime_event_probs": build_current_runtime_event_semantics_meta(),
        "text_semantics": {
            "text_clean": str(weak_event_row.get("text_clean", inventory_text.get("clean", ""))),
            "lexical_char_count": lexical_char_count,
            "nonverbal_only": nonverbal_only,
            "punctuation_sequence": punctuation_sequence,
            "punctuation_counts": dict(inventory_text.get("punctuation_counts", {})),
        },
        "boundary_semantics": {
            "pause_boundary_count": int(weak_event_row.get("pause_boundary_count", 0)),
            "terminal_boundary_count": int(weak_event_row.get("terminal_boundary_count", 0)),
            "pause_boundaries": list(weak_event_row.get("pause_boundaries", [])),
            "terminal_boundaries": list(weak_event_row.get("terminal_boundaries", [])),
        },
        "utterance_structure_semantics": {
            "clause_count": int(weak_event_row.get("clause_count", 0)),
            "clause_spans": list(weak_event_row.get("clause_spans", [])),
            "utterance_structure_type": str(weak_event_row.get("utterance_structure_type", "unknown")),
            "final_terminal_type": str(weak_event_row.get("final_terminal_type", "unknown")),
            "structure_flags": dict(weak_event_row.get("structure_flags", {})),
        },
        "future_label_slots": future_label_slots,
        "upgrade_status": {
            "label_status": str(future_label_slots.get("label_status", "unknown")),
            "semantic_ready_for_target_side_bootstrap": clean_text_available,
            "semantic_ready_for_source_side_bootstrap": False,
            "design_gap": (
                "当前可用的是 target-side lexical/structure semantic hints；"
                "phone/manner/place 与 source-side 对称语义仍未具备。"
            ),
        },
    }


def build_target_event_semantic_summary(
    weak_event_hints_path: Path,
    target_supervision_inventory_path: Path,
    semantic_rows: list[dict[str, object]],
) -> dict[str, object]:
    split_counter = Counter(str(row["split"]) for row in semantic_rows)
    inventory_status_counter = Counter(str(row["inventory_status"]) for row in semantic_rows)
    structure_type_counter = Counter(
        str(row["utterance_structure_semantics"]["utterance_structure_type"])
        for row in semantic_rows
    )
    final_terminal_counter = Counter(
        str(row["utterance_structure_semantics"]["final_terminal_type"])
        for row in semantic_rows
    )
    label_status_counter = Counter(
        str(row["upgrade_status"]["label_status"])
        for row in semantic_rows
    )
    lexical_char_counts = [
        int(row["text_semantics"]["lexical_char_count"])
        for row in semantic_rows
    ]
    clause_counts = [
        int(row["utterance_structure_semantics"]["clause_count"])
        for row in semantic_rows
    ]
    pause_counts = [
        int(row["boundary_semantics"]["pause_boundary_count"])
        for row in semantic_rows
    ]
    terminal_counts = [
        int(row["boundary_semantics"]["terminal_boundary_count"])
        for row in semantic_rows
    ]
    clean_text_available_count = sum(
        1
        for row in semantic_rows
        if bool(row["semantic_scope"]["clean_text_available"])
    )
    phone_sequence_available_count = sum(
        1
        for row in semantic_rows
        if bool(row["semantic_scope"]["phone_sequence_available"])
    )
    manner_sequence_available_count = sum(
        1
        for row in semantic_rows
        if bool(row["semantic_scope"]["manner_sequence_available"])
    )
    place_sequence_available_count = sum(
        1
        for row in semantic_rows
        if bool(row["semantic_scope"]["place_sequence_available"])
    )
    forced_alignment_available_count = sum(
        1
        for row in semantic_rows
        if bool(row["semantic_scope"]["forced_alignment_available"])
    )
    return {
        "weak_event_hints_path": weak_event_hints_path.as_posix(),
        "target_supervision_inventory_path": target_supervision_inventory_path.as_posix(),
        "semantic_contract_version": TARGET_EVENT_SEMANTIC_SIDECAR_VERSION,
        "semantic_label_space_version": TARGET_EVENT_SEMANTIC_LABEL_SPACE_VERSION,
        "record_count": len(semantic_rows),
        "split_counts": dict(sorted(split_counter.items())),
        "inventory_status_counts": dict(sorted(inventory_status_counter.items())),
        "utterance_structure_type_counts": dict(sorted(structure_type_counter.items())),
        "final_terminal_type_counts": dict(sorted(final_terminal_counter.items())),
        "future_label_status_counts": dict(sorted(label_status_counter.items())),
        "clean_text_available_count": clean_text_available_count,
        "phone_sequence_available_count": phone_sequence_available_count,
        "manner_sequence_available_count": manner_sequence_available_count,
        "place_sequence_available_count": place_sequence_available_count,
        "forced_alignment_available_count": forced_alignment_available_count,
        "lexical_char_count_stats": build_numeric_summary(lexical_char_counts),
        "clause_count_stats": build_numeric_summary(clause_counts),
        "pause_boundary_count_stats": build_numeric_summary(pause_counts),
        "terminal_boundary_count_stats": build_numeric_summary(terminal_counts),
        "current_runtime_event_probs": build_current_runtime_event_semantics_meta(),
        "notes": [
            "这份 sidecar 的目标是把 target-side lexical/structure 语义和当前 heuristic frame event targets 明确拆开。",
            "当前 semantic sidecar 只覆盖 target 侧可离线获得的文本、标点、分句结构，不假装已拥有 source-side phone/manner/place 对齐标签。",
            "后续若进入真正的 contract/semantic 升级，应优先消费这份独立 sidecar，而不是继续把旧 event_probs 当设计态 e_evt。",  # noqa: E501
        ],
    }


def build_numeric_summary(values: list[int]) -> dict[str, object]:
    if not values:
        return {
            "count": 0,
            "min": 0,
            "max": 0,
            "mean": 0.0,
        }
    total = sum(values)
    count = len(values)
    return {
        "count": count,
        "min": min(values),
        "max": max(values),
        "mean": round(total / max(1, count), 6),
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def render_target_event_semantic_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# target event semantic sidecar 摘要",
        "",
        "## 总览",
        f"- semantic_contract_version: `{summary['semantic_contract_version']}`",
        f"- semantic_label_space_version: `{summary['semantic_label_space_version']}`",
        f"- weak_event_hints_path: `{summary['weak_event_hints_path']}`",
        f"- target_supervision_inventory_path: `{summary['target_supervision_inventory_path']}`",
        f"- record_count: `{summary['record_count']}`",
        f"- split_counts: `{summary['split_counts']}`",
        f"- inventory_status_counts: `{summary['inventory_status_counts']}`",
        "",
        "## 当前 semantic 可用性",
        f"- clean_text_available_count: `{summary['clean_text_available_count']}`",
        f"- phone_sequence_available_count: `{summary['phone_sequence_available_count']}`",
        f"- manner_sequence_available_count: `{summary['manner_sequence_available_count']}`",
        f"- place_sequence_available_count: `{summary['place_sequence_available_count']}`",
        f"- forced_alignment_available_count: `{summary['forced_alignment_available_count']}`",
        f"- future_label_status_counts: `{summary['future_label_status_counts']}`",
        "",
        "## 结构分布",
        f"- utterance_structure_type_counts: `{summary['utterance_structure_type_counts']}`",
        f"- final_terminal_type_counts: `{summary['final_terminal_type_counts']}`",
        f"- lexical_char_count_stats: `{summary['lexical_char_count_stats']}`",
        f"- clause_count_stats: `{summary['clause_count_stats']}`",
        f"- pause_boundary_count_stats: `{summary['pause_boundary_count_stats']}`",
        f"- terminal_boundary_count_stats: `{summary['terminal_boundary_count_stats']}`",
        "",
        "## 当前 runtime event_probs 元数据",
        f"- event_probs_version: `{summary['current_runtime_event_probs']['event_probs_version']}`",
        f"- event_prob_dimensions: `{summary['current_runtime_event_probs']['event_prob_dimensions']}`",
        f"- semantic_status: `{summary['current_runtime_event_probs']['semantic_status']}`",
        "",
        "## 说明",
        "- 当前 8 维 `event_probs` 仍是旧 heuristic frame targets，不是假定为设计稿里的命名 `e_evt`。",
        "- 这份 sidecar 把 target-side lexical / punctuation / clause 语义独立落盘，供后续 contract/semantic 升级直接消费。",
        "- source-side 仍没有文本、phone、manner、place 或 forced alignment；这条 semantic 线当前只能先做 target-side bootstrap。",
    ]
    return "\n".join(lines) + "\n"
