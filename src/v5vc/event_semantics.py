from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path
import wave

from v5vc.c1_weak_event_hints import estimate_frame_count
from v5vc.manifest_builder import load_jsonl


CURRENT_RUNTIME_EVENT_SEMANTICS_VERSION = "offline_mvp_heuristic_event_target_v1"
TARGET_EVENT_SEMANTIC_SIDECAR_VERSION = "target_event_semantic_sidecar_v1"
TARGET_EVENT_SEMANTIC_LABEL_SPACE_VERSION = "target_lexical_structure_semantics_v1"
TARGET_EVENT_TIMING_SEMANTIC_SIDECAR_VERSION = "target_event_timing_semantic_sidecar_v1"
TARGET_EVENT_TIMING_SEMANTIC_LABEL_SPACE_VERSION = "target_weak_time_aligned_semantics_v1"
TARGET_EVENT_TIMING_ALIGNMENT_TYPE = "weak_punctuation_lexical_progress_v1"
DEFAULT_TARGET_EVENT_TIMING_BOUNDARY_HALF_WIDTH_FRAMES = 2
PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_SIDECAR_VERSION = "paired_parallel_source_semantic_parity_sidecar_v1"
PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_LABEL_SPACE_VERSION = "source_paired_parallel_bootstrap_semantics_v1"
PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_TRANSFER_TYPE = "paired_parallel_target_to_source_same_content_v1"

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


def build_target_event_timing_semantic_sidecar(
    weak_event_hints_path: Path,
    target_event_semantic_sidecar_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
    boundary_half_width_frames: int = DEFAULT_TARGET_EVENT_TIMING_BOUNDARY_HALF_WIDTH_FRAMES,
) -> dict[str, object]:
    weak_event_hints_path = weak_event_hints_path.resolve()
    target_event_semantic_sidecar_path = target_event_semantic_sidecar_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    normalized_half_width = max(0, int(boundary_half_width_frames))
    weak_event_rows = load_jsonl(weak_event_hints_path)
    semantic_rows = load_jsonl(target_event_semantic_sidecar_path)
    semantic_by_record_id = {
        str(row["record_id"]): row
        for row in semantic_rows
    }
    timing_rows = [
        build_target_event_timing_semantic_row(
            weak_event_row=weak_event_row,
            semantic_row=semantic_by_record_id.get(str(weak_event_row["record_id"])),
            boundary_half_width_frames=normalized_half_width,
        )
        for weak_event_row in weak_event_rows
    ]
    summary = build_target_event_timing_semantic_summary(
        weak_event_hints_path=weak_event_hints_path,
        target_event_semantic_sidecar_path=target_event_semantic_sidecar_path,
        timing_rows=timing_rows,
        boundary_half_width_frames=normalized_half_width,
    )

    timing_path = data_output_dir / "target_event_timing_semantic_sidecar.jsonl"
    summary_json_path = report_output_dir / "target_event_timing_semantic_sidecar_summary.json"
    summary_md_path = report_output_dir / "target_event_timing_semantic_sidecar_summary.md"
    write_jsonl(timing_path, timing_rows)
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        render_target_event_timing_semantic_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def build_paired_parallel_source_semantic_parity_sidecar(
    pair_spec_paths: list[Path],
    target_event_semantic_sidecar_path: Path,
    target_event_timing_semantic_sidecar_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
) -> dict[str, object]:
    resolved_pair_spec_paths = [path.resolve() for path in pair_spec_paths]
    if not resolved_pair_spec_paths:
        raise ValueError("pair_spec_paths must contain at least one paired source-to-target jsonl.")
    target_event_semantic_sidecar_path = target_event_semantic_sidecar_path.resolve()
    target_event_timing_semantic_sidecar_path = target_event_timing_semantic_sidecar_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    semantic_map = {
        str(row["record_id"]): row
        for row in load_jsonl(target_event_semantic_sidecar_path)
    }
    timing_map = {
        str(row["record_id"]): row
        for row in load_jsonl(target_event_timing_semantic_sidecar_path)
    }
    grouped_sources = group_parallel_pair_rows_by_source_record_id(resolved_pair_spec_paths)
    parity_rows = [
        build_paired_parallel_source_semantic_parity_row(
            grouped_pair_row=grouped_pair_row,
            target_semantic_row=semantic_map.get(str(grouped_pair_row["target_record_id"])),
            target_timing_row=timing_map.get(str(grouped_pair_row["target_record_id"])),
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            sample_rate=int(sample_rate),
        )
        for grouped_pair_row in grouped_sources
    ]
    summary = build_paired_parallel_source_semantic_parity_summary(
        pair_spec_paths=resolved_pair_spec_paths,
        target_event_semantic_sidecar_path=target_event_semantic_sidecar_path,
        target_event_timing_semantic_sidecar_path=target_event_timing_semantic_sidecar_path,
        parity_rows=parity_rows,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        sample_rate=int(sample_rate),
    )

    parity_path = data_output_dir / "paired_parallel_source_semantic_parity_sidecar.jsonl"
    summary_json_path = report_output_dir / "paired_parallel_source_semantic_parity_sidecar_summary.json"
    summary_md_path = report_output_dir / "paired_parallel_source_semantic_parity_sidecar_summary.md"
    write_jsonl(parity_path, parity_rows)
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        render_paired_parallel_source_semantic_parity_markdown(summary),
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


def build_target_event_timing_semantic_row(
    weak_event_row: dict[str, object],
    semantic_row: dict[str, object] | None,
    boundary_half_width_frames: int,
) -> dict[str, object]:
    estimated_frame_count = max(1, int(weak_event_row.get("estimated_frame_count", 1)))
    semantic_scope = (
        dict(semantic_row.get("semantic_scope", {}))
        if isinstance(semantic_row, dict) and isinstance(semantic_row.get("semantic_scope"), dict)
        else {}
    )
    text_semantics = (
        dict(semantic_row.get("text_semantics", {}))
        if isinstance(semantic_row, dict) and isinstance(semantic_row.get("text_semantics"), dict)
        else {}
    )
    utterance_semantics = (
        dict(semantic_row.get("utterance_structure_semantics", {}))
        if isinstance(semantic_row, dict) and isinstance(semantic_row.get("utterance_structure_semantics"), dict)
        else {}
    )
    upgrade_status = (
        dict(semantic_row.get("upgrade_status", {}))
        if isinstance(semantic_row, dict) and isinstance(semantic_row.get("upgrade_status"), dict)
        else {}
    )
    pause_boundaries = list(weak_event_row.get("pause_boundaries", []))
    terminal_boundaries = list(weak_event_row.get("terminal_boundaries", []))
    clause_spans = list(weak_event_row.get("clause_spans", []))
    boundary_events = build_boundary_timing_events(
        pause_boundaries=pause_boundaries,
        terminal_boundaries=terminal_boundaries,
        frame_count=estimated_frame_count,
        boundary_half_width_frames=boundary_half_width_frames,
    )
    clause_regions = build_clause_timing_regions(
        clause_spans=clause_spans,
        frame_count=estimated_frame_count,
    )
    timeline_events = sorted(
        boundary_events + clause_regions,
        key=lambda item: (
            int(item.get("frame_start_index", 0)),
            int(item.get("frame_end_index", 0)),
            str(item.get("event_type", "")),
        ),
    )
    inventory_status = "matched_semantic_sidecar" if isinstance(semantic_row, dict) else "weak_event_only_fallback"
    clean_text_available = bool(semantic_scope.get("clean_text_available", int(weak_event_row.get("lexical_char_count", 0)) > 0))
    nonverbal_only = bool(text_semantics.get("nonverbal_only", weak_event_row.get("nonverbal_only", False)))
    clause_count = int(weak_event_row.get("clause_count", len(clause_spans)))
    pause_event_count = sum(1 for event in boundary_events if str(event.get("event_type")) == "pause_boundary_window")
    terminal_event_count = sum(1 for event in boundary_events if str(event.get("event_type")) == "terminal_boundary_window")
    clause_coverage_frames = sum(int(event.get("frame_count", 0)) for event in clause_regions)
    pause_coverage_frames = sum(
        int(event.get("frame_count", 0))
        for event in boundary_events
        if str(event.get("event_type")) == "pause_boundary_window"
    )
    terminal_coverage_frames = sum(
        int(event.get("frame_count", 0))
        for event in boundary_events
        if str(event.get("event_type")) == "terminal_boundary_window"
    )

    return {
        "record_id": str(weak_event_row["record_id"]),
        "split": str(weak_event_row.get("split", "unknown")),
        "audio_path": str(weak_event_row.get("audio_path", "")),
        "estimated_frame_count": estimated_frame_count,
        "semantic_contract_version": TARGET_EVENT_TIMING_SEMANTIC_SIDECAR_VERSION,
        "semantic_label_space_version": TARGET_EVENT_TIMING_SEMANTIC_LABEL_SPACE_VERSION,
        "inventory_status": inventory_status,
        "timing_alignment": {
            "alignment_type": TARGET_EVENT_TIMING_ALIGNMENT_TYPE,
            "boundary_half_width_frames": boundary_half_width_frames,
            "time_aware_semantics_available": True,
            "timing_source": "target_weak_event_hints",
            "source_side_semantic_parity_available": False,
        },
        "utterance_semantic_overview": {
            "clean_text_available": clean_text_available,
            "nonverbal_only": nonverbal_only,
            "lexical_char_count": int(weak_event_row.get("lexical_char_count", text_semantics.get("lexical_char_count", 0))),
            "utterance_structure_type": str(
                utterance_semantics.get(
                    "utterance_structure_type",
                    weak_event_row.get("utterance_structure_type", "unknown"),
                )
            ),
            "final_terminal_type": str(
                utterance_semantics.get(
                    "final_terminal_type",
                    weak_event_row.get("final_terminal_type", "unknown"),
                )
            ),
            "label_status": str(upgrade_status.get("label_status", "pending_upgrade")),
        },
        "frame_event_label_space": {
            "timeline_event_types": [
                "clause_region",
                "pause_boundary_window",
                "terminal_boundary_window",
            ],
            "clause_roles": ["single", "initial", "middle", "final"],
            "boundary_symbol_types": [
                "pause_colon",
                "pause_comma",
                "pause_enumeration",
                "pause_semicolon",
                "terminal_exclamation",
                "terminal_period",
                "terminal_question",
            ],
        },
        "time_aware_semantics": {
            "boundary_events": boundary_events,
            "clause_regions": clause_regions,
            "timeline_events": timeline_events,
            "coverage_summary": {
                "clause_region_count": clause_count,
                "pause_boundary_event_count": pause_event_count,
                "terminal_boundary_event_count": terminal_event_count,
                "clause_region_coverage_frames": clause_coverage_frames,
                "pause_boundary_window_coverage_frames": pause_coverage_frames,
                "terminal_boundary_window_coverage_frames": terminal_coverage_frames,
            },
        },
        "upgrade_status": {
            "label_status": str(upgrade_status.get("label_status", "pending_upgrade")),
            "weak_time_alignment_ready_for_target_side_bootstrap": clean_text_available and not nonverbal_only,
            "ready_for_design_state_e_evt": False,
            "source_side_semantic_parity_available": False,
            "design_gap": (
                "当前资产已提供 target-side 弱时序 boundary/clause 结构，但仍不是 design-state e_evt；"
                "source-side parity、phone/manner/place 与强制对齐仍缺失。"
            ),
        },
    }


def group_parallel_pair_rows_by_source_record_id(pair_spec_paths: list[Path]) -> list[dict[str, object]]:
    grouped_by_source: dict[str, dict[str, object]] = {}
    for pair_spec_path in pair_spec_paths:
        for row in load_jsonl(pair_spec_path):
            source_record_id = str(row.get("source_record_id") or "")
            target_record_id = str(row.get("target_record_id") or "")
            if not source_record_id or not target_record_id:
                raise ValueError(f"Pair spec row missing source_record_id/target_record_id: {pair_spec_path}")
            source_audio_path = str(row.get("source_audio_path") or "")
            target_audio_path = str(row.get("target_audio_path") or "")
            if not source_audio_path or not target_audio_path:
                raise ValueError(f"Pair spec row missing source_audio_path/target_audio_path: {pair_spec_path}")
            source_duration_sec_pair_spec = resolve_pair_duration_sec(row=row, field_name="source_audio")
            target_duration_sec_pair_spec = resolve_pair_duration_sec(row=row, field_name="target_audio")
            source_duration_sec = read_wave_duration_sec(Path(source_audio_path))
            target_duration_sec = read_wave_duration_sec(Path(target_audio_path))
            grouped = grouped_by_source.get(source_record_id)
            if grouped is None:
                grouped = {
                    "record_id": source_record_id,
                    "source_record_id": source_record_id,
                    "target_record_id": target_record_id,
                    "source_audio_path": source_audio_path,
                    "target_audio_path": target_audio_path,
                    "source_duration_sec": source_duration_sec,
                    "target_duration_sec": target_duration_sec,
                    "source_duration_sec_pair_spec": source_duration_sec_pair_spec,
                    "target_duration_sec_pair_spec": target_duration_sec_pair_spec,
                    "pair_record_ids": [str(row.get("record_id") or source_record_id)],
                    "split_memberships": [str(row.get("split", "unknown"))],
                    "pair_spec_paths": [pair_spec_path.as_posix()],
                }
                grouped_by_source[source_record_id] = grouped
                continue
            if str(grouped["target_record_id"]) != target_record_id:
                raise ValueError(
                    "Conflicting target_record_id for source semantic parity bootstrap: "
                    f"source={source_record_id} existing_target={grouped['target_record_id']} new_target={target_record_id}"
                )
            if str(grouped["source_audio_path"]) != source_audio_path or str(grouped["target_audio_path"]) != target_audio_path:
                raise ValueError(
                    "Conflicting audio paths for source semantic parity bootstrap: "
                    f"source={source_record_id}"
                )
            if abs(float(grouped["source_duration_sec"]) - float(source_duration_sec)) > 1e-6:
                raise ValueError(
                    "Conflicting source_duration_sec for source semantic parity bootstrap: "
                    f"source={source_record_id}"
                )
            if abs(float(grouped["target_duration_sec"]) - float(target_duration_sec)) > 1e-6:
                raise ValueError(
                    "Conflicting target_duration_sec for source semantic parity bootstrap: "
                    f"source={source_record_id}"
                )
            if abs(float(grouped["source_duration_sec_pair_spec"]) - float(source_duration_sec_pair_spec)) > 1e-6:
                raise ValueError(
                    "Conflicting source_duration_sec pair-spec metadata for source semantic parity bootstrap: "
                    f"source={source_record_id}"
                )
            if abs(float(grouped["target_duration_sec_pair_spec"]) - float(target_duration_sec_pair_spec)) > 1e-6:
                raise ValueError(
                    "Conflicting target_duration_sec pair-spec metadata for source semantic parity bootstrap: "
                    f"source={source_record_id}"
                )
            pair_record_id = str(row.get("record_id") or source_record_id)
            if pair_record_id not in grouped["pair_record_ids"]:
                grouped["pair_record_ids"].append(pair_record_id)
            split_name = str(row.get("split", "unknown"))
            if split_name not in grouped["split_memberships"]:
                grouped["split_memberships"].append(split_name)
            pair_spec_path_str = pair_spec_path.as_posix()
            if pair_spec_path_str not in grouped["pair_spec_paths"]:
                grouped["pair_spec_paths"].append(pair_spec_path_str)
    return [
        grouped_by_source[key]
        for key in sorted(grouped_by_source.keys())
    ]


def resolve_pair_duration_sec(
    row: dict[str, object],
    field_name: str,
) -> float:
    payload = dict(row.get(field_name, {}))
    if "duration_sec" in payload:
        return float(payload["duration_sec"])
    direct_audio = dict(row.get("audio", {}))
    if "duration_sec" in direct_audio:
        return float(direct_audio["duration_sec"])
    raise ValueError(f"Pair spec row missing duration_sec for {field_name}.")


def read_wave_duration_sec(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        frame_count = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
    if sample_rate <= 0:
        raise ValueError(f"Invalid sample_rate in {path}")
    return round(frame_count / sample_rate, 6)


def build_paired_parallel_source_semantic_parity_row(
    grouped_pair_row: dict[str, object],
    target_semantic_row: dict[str, object] | None,
    target_timing_row: dict[str, object] | None,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
) -> dict[str, object]:
    source_duration_sec = float(grouped_pair_row["source_duration_sec"])
    target_duration_sec = float(grouped_pair_row["target_duration_sec"])
    source_frame_count = estimate_frame_count(
        duration_sec=source_duration_sec,
        sample_rate=int(sample_rate),
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    source_semantic_status = "matched_target_semantic_and_timing"
    if not isinstance(target_semantic_row, dict):
        source_semantic_status = "missing_target_semantic"
    elif not isinstance(target_timing_row, dict):
        source_semantic_status = "missing_target_timing"

    target_text_semantics = (
        dict(target_semantic_row.get("text_semantics", {}))
        if isinstance(target_semantic_row, dict) and isinstance(target_semantic_row.get("text_semantics"), dict)
        else {}
    )
    target_boundary_semantics = (
        dict(target_semantic_row.get("boundary_semantics", {}))
        if isinstance(target_semantic_row, dict) and isinstance(target_semantic_row.get("boundary_semantics"), dict)
        else {}
    )
    target_utterance_semantics = (
        dict(target_semantic_row.get("utterance_structure_semantics", {}))
        if isinstance(target_semantic_row, dict) and isinstance(target_semantic_row.get("utterance_structure_semantics"), dict)
        else {}
    )
    target_upgrade_status = (
        dict(target_semantic_row.get("upgrade_status", {}))
        if isinstance(target_semantic_row, dict) and isinstance(target_semantic_row.get("upgrade_status"), dict)
        else {}
    )
    timing_alignment = (
        dict(target_timing_row.get("timing_alignment", {}))
        if isinstance(target_timing_row, dict) and isinstance(target_timing_row.get("timing_alignment"), dict)
        else {}
    )
    boundary_half_width_frames = int(
        timing_alignment.get("boundary_half_width_frames", DEFAULT_TARGET_EVENT_TIMING_BOUNDARY_HALF_WIDTH_FRAMES)
    )
    time_aware_semantics = (
        dict(target_timing_row.get("time_aware_semantics", {}))
        if isinstance(target_timing_row, dict) and isinstance(target_timing_row.get("time_aware_semantics"), dict)
        else {}
    )
    target_clause_regions = (
        list(time_aware_semantics.get("clause_regions", []))
        if isinstance(time_aware_semantics.get("clause_regions"), list)
        else []
    )
    target_boundary_events = (
        list(time_aware_semantics.get("boundary_events", []))
        if isinstance(time_aware_semantics.get("boundary_events"), list)
        else []
    )
    source_clause_regions = build_source_clause_regions_from_target_timing(
        target_clause_regions=target_clause_regions,
        frame_count=source_frame_count,
    )
    source_boundary_events = build_source_boundary_events_from_target_timing(
        target_boundary_events=target_boundary_events,
        frame_count=source_frame_count,
        boundary_half_width_frames=boundary_half_width_frames,
    )
    source_timeline_events = sorted(
        source_clause_regions + source_boundary_events,
        key=lambda item: (
            int(item.get("frame_start_index", 0)),
            int(item.get("frame_end_index", 0)),
            str(item.get("event_type", "")),
        ),
    )
    source_pause_boundary_count = sum(
        1 for item in source_boundary_events if str(item.get("event_type")) == "pause_boundary_window"
    )
    source_terminal_boundary_count = sum(
        1 for item in source_boundary_events if str(item.get("event_type")) == "terminal_boundary_window"
    )
    source_clause_coverage_frames = sum(int(item.get("frame_count", 0)) for item in source_clause_regions)
    source_pause_coverage_frames = sum(
        int(item.get("frame_count", 0))
        for item in source_boundary_events
        if str(item.get("event_type")) == "pause_boundary_window"
    )
    source_terminal_coverage_frames = sum(
        int(item.get("frame_count", 0))
        for item in source_boundary_events
        if str(item.get("event_type")) == "terminal_boundary_window"
    )

    return {
        "record_id": str(grouped_pair_row["source_record_id"]),
        "source_record_id": str(grouped_pair_row["source_record_id"]),
        "target_record_id": str(grouped_pair_row["target_record_id"]),
        "pair_record_ids": list(grouped_pair_row["pair_record_ids"]),
        "split_memberships": list(grouped_pair_row["split_memberships"]),
        "source_audio_path": str(grouped_pair_row["source_audio_path"]),
        "target_audio_path": str(grouped_pair_row["target_audio_path"]),
        "source_duration_sec": round(source_duration_sec, 6),
        "target_duration_sec": round(target_duration_sec, 6),
        "source_duration_sec_pair_spec": round(float(grouped_pair_row["source_duration_sec_pair_spec"]), 6),
        "target_duration_sec_pair_spec": round(float(grouped_pair_row["target_duration_sec_pair_spec"]), 6),
        "source_duration_metadata_drift_sec": round(
            float(grouped_pair_row["source_duration_sec_pair_spec"]) - source_duration_sec,
            6,
        ),
        "target_duration_metadata_drift_sec": round(
            float(grouped_pair_row["target_duration_sec_pair_spec"]) - target_duration_sec,
            6,
        ),
        "source_estimated_frame_count": int(source_frame_count),
        "semantic_contract_version": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_SIDECAR_VERSION,
        "semantic_label_space_version": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_LABEL_SPACE_VERSION,
        "parity_status": source_semantic_status,
        "semantic_transfer": {
            "transfer_type": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_TRANSFER_TYPE,
            "source_side_semantic_parity_available": source_semantic_status == "matched_target_semantic_and_timing",
            "native_source_text_available": False,
            "native_source_phone_sequence_available": False,
            "timing_projection_basis": "target_lexical_ratio_to_source_frame_index_v1",
            "frame_length": int(frame_length),
            "hop_length": int(hop_length),
            "sample_rate": int(sample_rate),
            "boundary_half_width_frames": int(boundary_half_width_frames),
        },
        "source_semantic_bootstrap": {
            "clean_text_available": False,
            "paired_target_clean_text_available": bool(
                isinstance(target_semantic_row, dict)
                and bool(dict(target_semantic_row.get("semantic_scope", {})).get("clean_text_available", False))
            ),
            "lexical_char_count": int(target_text_semantics.get("lexical_char_count", 0)),
            "nonverbal_only": bool(target_text_semantics.get("nonverbal_only", False)),
            "utterance_structure_type": str(
                target_utterance_semantics.get("utterance_structure_type", "unknown")
            ),
            "final_terminal_type": str(target_utterance_semantics.get("final_terminal_type", "unknown")),
            "clause_count": len(source_clause_regions),
            "pause_boundary_count": source_pause_boundary_count,
            "terminal_boundary_count": source_terminal_boundary_count,
            "label_status": str(target_upgrade_status.get("label_status", "unknown")),
            "text_clean_unavailable_on_source": True,
        },
        "frame_event_label_space": {
            "timeline_event_types": [
                "clause_region",
                "pause_boundary_window",
                "terminal_boundary_window",
            ],
            "clause_roles": ["single", "initial", "middle", "final"],
            "boundary_symbol_types": [
                "pause_colon",
                "pause_comma",
                "pause_enumeration",
                "pause_semicolon",
                "terminal_exclamation",
                "terminal_period",
                "terminal_question",
            ],
        },
        "source_time_aware_semantics": {
            "boundary_events": source_boundary_events,
            "clause_regions": source_clause_regions,
            "timeline_events": source_timeline_events,
            "coverage_summary": {
                "clause_region_count": len(source_clause_regions),
                "pause_boundary_event_count": source_pause_boundary_count,
                "terminal_boundary_event_count": source_terminal_boundary_count,
                "clause_region_coverage_frames": source_clause_coverage_frames,
                "pause_boundary_window_coverage_frames": source_pause_coverage_frames,
                "terminal_boundary_window_coverage_frames": source_terminal_coverage_frames,
            },
        },
        "paired_target_reference": {
            "target_record_id": str(grouped_pair_row["target_record_id"]),
            "target_audio_path": str(grouped_pair_row["target_audio_path"]),
            "target_event_semantic_contract_version": (
                None
                if not isinstance(target_semantic_row, dict)
                else str(target_semantic_row.get("semantic_contract_version", "")) or None
            ),
            "target_event_timing_contract_version": (
                None
                if not isinstance(target_timing_row, dict)
                else str(target_timing_row.get("semantic_contract_version", "")) or None
            ),
            "target_pause_boundary_count": int(target_boundary_semantics.get("pause_boundary_count", 0)),
            "target_terminal_boundary_count": int(target_boundary_semantics.get("terminal_boundary_count", 0)),
        },
        "upgrade_status": {
            "semantic_ready_for_source_side_bootstrap": source_semantic_status == "matched_target_semantic_and_timing",
            "native_source_semantic_available": False,
            "paired_target_transfer_available": source_semantic_status == "matched_target_semantic_and_timing",
            "design_gap": (
                "当前 source-side 语义来自 paired parallel target 的同内容转写，"
                "不是 native source text/phone/forced alignment，也还不是 design-state e_evt。"
            ),
        },
    }


def build_source_clause_regions_from_target_timing(
    target_clause_regions: list[dict[str, object]],
    frame_count: int,
) -> list[dict[str, object]]:
    sorted_regions = sorted(
        target_clause_regions,
        key=lambda item: (
            float(item.get("lexical_start_ratio", 0.0)),
            int(item.get("clause_index", 0)),
        ),
    )
    source_regions: list[dict[str, object]] = []
    for index, clause in enumerate(sorted_regions):
        lexical_start_ratio = float(clause.get("lexical_start_ratio", 0.0))
        lexical_end_ratio = float(clause.get("lexical_end_ratio", lexical_start_ratio))
        frame_start_index = lexical_ratio_to_frame_index(lexical_start_ratio, frame_count)
        raw_frame_end_index = lexical_ratio_to_frame_index(lexical_end_ratio, frame_count)
        next_frame_start_index = None
        if index + 1 < len(sorted_regions):
            next_frame_start_index = lexical_ratio_to_frame_index(
                float(sorted_regions[index + 1].get("lexical_start_ratio", lexical_end_ratio)),
                frame_count,
            )
        if next_frame_start_index is not None and next_frame_start_index > frame_start_index:
            frame_end_index = min(raw_frame_end_index, next_frame_start_index - 1)
        else:
            frame_end_index = max(frame_start_index, raw_frame_end_index)
        source_regions.append(
            {
                "event_type": "clause_region",
                "clause_index": int(clause.get("clause_index", index)),
                "clause_role": str(clause.get("clause_role", "unknown")),
                "closing_symbol": str(clause.get("closing_symbol", "")),
                "closing_symbol_type": str(clause.get("closing_symbol_type", "none")),
                "frame_start_index": frame_start_index,
                "frame_end_index": frame_end_index,
                "frame_count": max(0, frame_end_index - frame_start_index + 1),
                "lexical_start_index": int(clause.get("lexical_start_index", 0)),
                "lexical_end_index": int(clause.get("lexical_end_index", 0)),
                "lexical_char_count": int(clause.get("lexical_char_count", 0)),
                "lexical_start_ratio": round(lexical_start_ratio, 6),
                "lexical_end_ratio": round(lexical_end_ratio, 6),
            }
        )
    return source_regions


def build_source_boundary_events_from_target_timing(
    target_boundary_events: list[dict[str, object]],
    frame_count: int,
    boundary_half_width_frames: int,
) -> list[dict[str, object]]:
    source_events: list[dict[str, object]] = []
    for event in target_boundary_events:
        lexical_ratio = float(event.get("lexical_ratio", 0.0))
        center_frame_index = lexical_ratio_to_frame_index(lexical_ratio, frame_count)
        frame_start_index = max(0, center_frame_index - max(0, int(boundary_half_width_frames)))
        frame_end_index = min(frame_count - 1, center_frame_index + max(0, int(boundary_half_width_frames)))
        source_events.append(
            {
                "event_type": str(event.get("event_type", "unknown")),
                "symbol": str(event.get("symbol", "")),
                "symbol_type": str(event.get("symbol_type", "unknown")),
                "char_index": int(event.get("char_index", 0)),
                "lexical_index": int(event.get("lexical_index", 0)),
                "lexical_ratio": round(lexical_ratio, 6),
                "center_frame_index": center_frame_index,
                "frame_start_index": frame_start_index,
                "frame_end_index": frame_end_index,
                "frame_count": max(0, frame_end_index - frame_start_index + 1),
            }
        )
    return source_events


def lexical_ratio_to_frame_index(
    lexical_ratio: float,
    frame_count: int,
) -> int:
    resolved_frame_count = max(1, int(frame_count))
    return min(
        resolved_frame_count - 1,
        max(0, int(round(float(lexical_ratio) * max(0, resolved_frame_count - 1)))),
    )


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


def build_target_event_timing_semantic_summary(
    weak_event_hints_path: Path,
    target_event_semantic_sidecar_path: Path,
    timing_rows: list[dict[str, object]],
    boundary_half_width_frames: int,
) -> dict[str, object]:
    split_counter = Counter(str(row["split"]) for row in timing_rows)
    inventory_status_counter = Counter(str(row["inventory_status"]) for row in timing_rows)
    structure_type_counter = Counter(
        str(row["utterance_semantic_overview"]["utterance_structure_type"])
        for row in timing_rows
    )
    label_status_counter = Counter(
        str(row["upgrade_status"]["label_status"])
        for row in timing_rows
    )
    clause_role_counter: Counter[str] = Counter()
    boundary_symbol_type_counter: Counter[str] = Counter()
    clause_region_counts: list[int] = []
    pause_event_counts: list[int] = []
    terminal_event_counts: list[int] = []
    timeline_event_counts: list[int] = []
    estimated_frame_counts: list[int] = []
    clause_coverage_frames: list[int] = []
    pause_coverage_frames: list[int] = []
    terminal_coverage_frames: list[int] = []
    ready_for_target_bootstrap_count = 0

    for row in timing_rows:
        coverage_summary = (
            dict(row["time_aware_semantics"]["coverage_summary"])
            if isinstance(row.get("time_aware_semantics"), dict)
            and isinstance(row["time_aware_semantics"].get("coverage_summary"), dict)
            else {}
        )
        boundary_events = (
            list(row["time_aware_semantics"]["boundary_events"])
            if isinstance(row.get("time_aware_semantics"), dict)
            and isinstance(row["time_aware_semantics"].get("boundary_events"), list)
            else []
        )
        clause_regions = (
            list(row["time_aware_semantics"]["clause_regions"])
            if isinstance(row.get("time_aware_semantics"), dict)
            and isinstance(row["time_aware_semantics"].get("clause_regions"), list)
            else []
        )
        timeline_events = (
            list(row["time_aware_semantics"]["timeline_events"])
            if isinstance(row.get("time_aware_semantics"), dict)
            and isinstance(row["time_aware_semantics"].get("timeline_events"), list)
            else []
        )
        for event in boundary_events:
            boundary_symbol_type_counter[str(event.get("symbol_type", "unknown"))] += 1
        for region in clause_regions:
            clause_role_counter[str(region.get("clause_role", "unknown"))] += 1
        clause_region_counts.append(int(coverage_summary.get("clause_region_count", len(clause_regions))))
        pause_event_counts.append(int(coverage_summary.get("pause_boundary_event_count", 0)))
        terminal_event_counts.append(int(coverage_summary.get("terminal_boundary_event_count", 0)))
        timeline_event_counts.append(len(timeline_events))
        estimated_frame_counts.append(int(row.get("estimated_frame_count", 0)))
        clause_coverage_frames.append(int(coverage_summary.get("clause_region_coverage_frames", 0)))
        pause_coverage_frames.append(int(coverage_summary.get("pause_boundary_window_coverage_frames", 0)))
        terminal_coverage_frames.append(int(coverage_summary.get("terminal_boundary_window_coverage_frames", 0)))
        if bool(row["upgrade_status"].get("weak_time_alignment_ready_for_target_side_bootstrap")):
            ready_for_target_bootstrap_count += 1

    return {
        "weak_event_hints_path": weak_event_hints_path.as_posix(),
        "target_event_semantic_sidecar_path": target_event_semantic_sidecar_path.as_posix(),
        "semantic_contract_version": TARGET_EVENT_TIMING_SEMANTIC_SIDECAR_VERSION,
        "semantic_label_space_version": TARGET_EVENT_TIMING_SEMANTIC_LABEL_SPACE_VERSION,
        "timing_alignment_type": TARGET_EVENT_TIMING_ALIGNMENT_TYPE,
        "boundary_half_width_frames": boundary_half_width_frames,
        "record_count": len(timing_rows),
        "split_counts": dict(sorted(split_counter.items())),
        "inventory_status_counts": dict(sorted(inventory_status_counter.items())),
        "utterance_structure_type_counts": dict(sorted(structure_type_counter.items())),
        "future_label_status_counts": dict(sorted(label_status_counter.items())),
        "clause_role_counts": dict(sorted(clause_role_counter.items())),
        "boundary_symbol_type_counts": dict(sorted(boundary_symbol_type_counter.items())),
        "weak_time_alignment_ready_for_target_side_bootstrap_count": ready_for_target_bootstrap_count,
        "estimated_frame_count_stats": build_numeric_summary(estimated_frame_counts),
        "clause_region_count_stats": build_numeric_summary(clause_region_counts),
        "pause_boundary_event_count_stats": build_numeric_summary(pause_event_counts),
        "terminal_boundary_event_count_stats": build_numeric_summary(terminal_event_counts),
        "timeline_event_count_stats": build_numeric_summary(timeline_event_counts),
        "clause_region_coverage_frames_stats": build_numeric_summary(clause_coverage_frames),
        "pause_boundary_window_coverage_frames_stats": build_numeric_summary(pause_coverage_frames),
        "terminal_boundary_window_coverage_frames_stats": build_numeric_summary(terminal_coverage_frames),
        "notes": [
            "这份 timing sidecar 只把现有 target-side 弱边界与 clause spans 组织成稀疏时序资产，不生成逐帧 dense float 数组。",
            "当前 frame 索引仍来自文本标点与 lexical progress 的弱估计，不是 forced alignment。",
            "它的定位是 design-state e_evt 之前的 target-side time-aware bridge，不应误写成完整 e_evt 合同已完成。",
        ],
    }


def build_paired_parallel_source_semantic_parity_summary(
    pair_spec_paths: list[Path],
    target_event_semantic_sidecar_path: Path,
    target_event_timing_semantic_sidecar_path: Path,
    parity_rows: list[dict[str, object]],
    frame_length: int,
    hop_length: int,
    sample_rate: int,
) -> dict[str, object]:
    split_counter: Counter[str] = Counter()
    parity_status_counter = Counter(str(row["parity_status"]) for row in parity_rows)
    structure_type_counter = Counter(
        str(row["source_semantic_bootstrap"]["utterance_structure_type"])
        for row in parity_rows
    )
    label_status_counter = Counter(
        str(row["source_semantic_bootstrap"]["label_status"])
        for row in parity_rows
    )
    source_frame_counts = [int(row["source_estimated_frame_count"]) for row in parity_rows]
    lexical_char_counts = [int(row["source_semantic_bootstrap"]["lexical_char_count"]) for row in parity_rows]
    clause_counts = [
        int(row["source_time_aware_semantics"]["coverage_summary"]["clause_region_count"])
        for row in parity_rows
    ]
    pause_counts = [
        int(row["source_time_aware_semantics"]["coverage_summary"]["pause_boundary_event_count"])
        for row in parity_rows
    ]
    terminal_counts = [
        int(row["source_time_aware_semantics"]["coverage_summary"]["terminal_boundary_event_count"])
        for row in parity_rows
    ]
    timeline_counts = [
        len(list(row["source_time_aware_semantics"]["timeline_events"]))
        for row in parity_rows
    ]
    duration_ratio_values = [
        round(float(row["source_duration_sec"]) / max(1e-9, float(row["target_duration_sec"])), 6)
        for row in parity_rows
    ]
    source_duration_metadata_drift_values = [
        round(float(row.get("source_duration_metadata_drift_sec", 0.0)), 6)
        for row in parity_rows
    ]
    target_duration_metadata_drift_values = [
        round(float(row.get("target_duration_metadata_drift_sec", 0.0)), 6)
        for row in parity_rows
    ]
    source_ready_count = 0
    for row in parity_rows:
        for split_name in list(row.get("split_memberships", [])):
            split_counter[str(split_name)] += 1
        if bool(row["upgrade_status"].get("semantic_ready_for_source_side_bootstrap", False)):
            source_ready_count += 1
    return {
        "pair_spec_paths": [path.as_posix() for path in pair_spec_paths],
        "target_event_semantic_sidecar_path": target_event_semantic_sidecar_path.as_posix(),
        "target_event_timing_semantic_sidecar_path": target_event_timing_semantic_sidecar_path.as_posix(),
        "semantic_contract_version": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_SIDECAR_VERSION,
        "semantic_label_space_version": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_LABEL_SPACE_VERSION,
        "transfer_type": PAIRED_PARALLEL_SOURCE_SEMANTIC_PARITY_TRANSFER_TYPE,
        "record_count": len(parity_rows),
        "split_membership_counts": dict(sorted(split_counter.items())),
        "parity_status_counts": dict(sorted(parity_status_counter.items())),
        "utterance_structure_type_counts": dict(sorted(structure_type_counter.items())),
        "label_status_counts": dict(sorted(label_status_counter.items())),
        "semantic_ready_for_source_side_bootstrap_count": int(source_ready_count),
        "frame_projection": {
            "frame_length": int(frame_length),
            "hop_length": int(hop_length),
            "sample_rate": int(sample_rate),
        },
        "source_estimated_frame_count_stats": build_numeric_summary(source_frame_counts),
        "lexical_char_count_stats": build_numeric_summary(lexical_char_counts),
        "clause_region_count_stats": build_numeric_summary(clause_counts),
        "pause_boundary_event_count_stats": build_numeric_summary(pause_counts),
        "terminal_boundary_event_count_stats": build_numeric_summary(terminal_counts),
        "timeline_event_count_stats": build_numeric_summary(timeline_counts),
        "source_to_target_duration_ratio_stats": build_numeric_summary(duration_ratio_values),
        "source_duration_metadata_drift_sec_stats": build_numeric_summary(source_duration_metadata_drift_values),
        "target_duration_metadata_drift_sec_stats": build_numeric_summary(target_duration_metadata_drift_values),
        "notes": [
            "这份 sidecar 不是 native source text semantic，而是利用 paired parallel 同内容 target 语义做的 source-side parity bootstrap。",
            "source frame timing 由 target lexical ratios 投影到 source duration 上，不是 source forced alignment。",
            "source/target duration 现在优先读取真实 wav 元数据，不再盲信 pair spec 里的 duration_sec。",
            "它的意义是补 source-side / parity-aware semantic assets，不应误写成 source-native semantic 已完成。",
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


def build_boundary_timing_events(
    pause_boundaries: list[dict[str, object]],
    terminal_boundaries: list[dict[str, object]],
    frame_count: int,
    boundary_half_width_frames: int,
) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for raw_boundary in pause_boundaries:
        events.append(
            build_boundary_timing_event(
                raw_boundary=raw_boundary,
                event_type="pause_boundary_window",
                frame_count=frame_count,
                boundary_half_width_frames=boundary_half_width_frames,
            )
        )
    for raw_boundary in terminal_boundaries:
        events.append(
            build_boundary_timing_event(
                raw_boundary=raw_boundary,
                event_type="terminal_boundary_window",
                frame_count=frame_count,
                boundary_half_width_frames=boundary_half_width_frames,
            )
        )
    return events


def build_boundary_timing_event(
    raw_boundary: dict[str, object],
    event_type: str,
    frame_count: int,
    boundary_half_width_frames: int,
) -> dict[str, object]:
    center_frame_index = min(frame_count - 1, max(0, int(raw_boundary.get("frame_index", 0))))
    frame_start_index = max(0, center_frame_index - boundary_half_width_frames)
    frame_end_index = min(frame_count - 1, center_frame_index + boundary_half_width_frames)
    return {
        "event_type": event_type,
        "symbol": str(raw_boundary.get("symbol", "")),
        "symbol_type": str(raw_boundary.get("symbol_type", "unknown")),
        "char_index": int(raw_boundary.get("char_index", 0)),
        "lexical_index": int(raw_boundary.get("lexical_index", 0)),
        "lexical_ratio": float(raw_boundary.get("lexical_ratio", 0.0)),
        "center_frame_index": center_frame_index,
        "frame_start_index": frame_start_index,
        "frame_end_index": frame_end_index,
        "frame_count": max(0, frame_end_index - frame_start_index + 1),
    }


def build_clause_timing_regions(
    clause_spans: list[dict[str, object]],
    frame_count: int,
) -> list[dict[str, object]]:
    regions: list[dict[str, object]] = []
    sorted_clauses = sorted(
        clause_spans,
        key=lambda item: (
            int(item.get("frame_start_index", 0)),
            int(item.get("clause_index", 0)),
        ),
    )
    for clause_index, raw_clause in enumerate(sorted_clauses):
        frame_start_index = min(frame_count - 1, max(0, int(raw_clause.get("frame_start_index", 0))))
        raw_frame_end_index = min(frame_count - 1, max(frame_start_index, int(raw_clause.get("frame_end_index", frame_start_index))))
        next_frame_start_index = None
        if clause_index + 1 < len(sorted_clauses):
            next_frame_start_index = min(
                frame_count - 1,
                max(0, int(sorted_clauses[clause_index + 1].get("frame_start_index", 0))),
            )
        if next_frame_start_index is not None and next_frame_start_index > frame_start_index:
            frame_end_index = min(raw_frame_end_index, next_frame_start_index - 1)
        else:
            frame_end_index = raw_frame_end_index
        regions.append(
            {
                "event_type": "clause_region",
                "clause_index": int(raw_clause.get("clause_index", 0)),
                "clause_role": str(raw_clause.get("role", "unknown")),
                "closing_symbol": str(raw_clause.get("closing_symbol", "")) if raw_clause.get("closing_symbol") is not None else "",
                "closing_symbol_type": str(raw_clause.get("closing_symbol_type", "none")),
                "frame_start_index": frame_start_index,
                "frame_end_index": frame_end_index,
                "frame_count": max(0, frame_end_index - frame_start_index + 1),
                "lexical_start_index": int(raw_clause.get("lexical_start_index", 0)),
                "lexical_end_index": int(raw_clause.get("lexical_end_index", 0)),
                "lexical_char_count": int(raw_clause.get("lexical_char_count", 0)),
                "lexical_start_ratio": float(raw_clause.get("lexical_start_ratio", 0.0)),
                "lexical_end_ratio": float(raw_clause.get("lexical_end_ratio", 0.0)),
            }
        )
    return regions


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


def render_target_event_timing_semantic_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# target event timing semantic sidecar 摘要",
        "",
        "## 总览",
        f"- semantic_contract_version: `{summary['semantic_contract_version']}`",
        f"- semantic_label_space_version: `{summary['semantic_label_space_version']}`",
        f"- weak_event_hints_path: `{summary['weak_event_hints_path']}`",
        f"- target_event_semantic_sidecar_path: `{summary['target_event_semantic_sidecar_path']}`",
        f"- timing_alignment_type: `{summary['timing_alignment_type']}`",
        f"- boundary_half_width_frames: `{summary['boundary_half_width_frames']}`",
        f"- record_count: `{summary['record_count']}`",
        f"- split_counts: `{summary['split_counts']}`",
        f"- inventory_status_counts: `{summary['inventory_status_counts']}`",
        "",
        "## 时序覆盖统计",
        f"- weak_time_alignment_ready_for_target_side_bootstrap_count: `{summary['weak_time_alignment_ready_for_target_side_bootstrap_count']}`",
        f"- estimated_frame_count_stats: `{summary['estimated_frame_count_stats']}`",
        f"- clause_region_count_stats: `{summary['clause_region_count_stats']}`",
        f"- pause_boundary_event_count_stats: `{summary['pause_boundary_event_count_stats']}`",
        f"- terminal_boundary_event_count_stats: `{summary['terminal_boundary_event_count_stats']}`",
        f"- timeline_event_count_stats: `{summary['timeline_event_count_stats']}`",
        f"- clause_region_coverage_frames_stats: `{summary['clause_region_coverage_frames_stats']}`",
        f"- pause_boundary_window_coverage_frames_stats: `{summary['pause_boundary_window_coverage_frames_stats']}`",
        f"- terminal_boundary_window_coverage_frames_stats: `{summary['terminal_boundary_window_coverage_frames_stats']}`",
        "",
        "## 结构统计",
        f"- utterance_structure_type_counts: `{summary['utterance_structure_type_counts']}`",
        f"- future_label_status_counts: `{summary['future_label_status_counts']}`",
        f"- clause_role_counts: `{summary['clause_role_counts']}`",
        f"- boundary_symbol_type_counts: `{summary['boundary_symbol_type_counts']}`",
        "",
        "## 说明",
        "- 该 sidecar 是 target-side 弱时序桥接资产，保留 clause spans 与 boundary windows 的稀疏时间结构。",
        "- 当前 frame timing 仍来自标点和 lexical progress，不是 forced alignment，也不是 design-state `e_evt` 真值。",
        "- 这一步的目标是把“time-aware semantic asset”正式物化，供后续真正的 consumer 直接消费。 ",
    ]
    return "\n".join(lines) + "\n"


def render_paired_parallel_source_semantic_parity_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# paired parallel source semantic parity sidecar 摘要",
        "",
        "## 总览",
        f"- semantic_contract_version: `{summary['semantic_contract_version']}`",
        f"- semantic_label_space_version: `{summary['semantic_label_space_version']}`",
        f"- transfer_type: `{summary['transfer_type']}`",
        f"- pair_spec_paths: `{summary['pair_spec_paths']}`",
        f"- target_event_semantic_sidecar_path: `{summary['target_event_semantic_sidecar_path']}`",
        f"- target_event_timing_semantic_sidecar_path: `{summary['target_event_timing_semantic_sidecar_path']}`",
        f"- record_count: `{summary['record_count']}`",
        f"- split_membership_counts: `{summary['split_membership_counts']}`",
        f"- parity_status_counts: `{summary['parity_status_counts']}`",
        "",
        "## 统计",
        f"- semantic_ready_for_source_side_bootstrap_count: `{summary['semantic_ready_for_source_side_bootstrap_count']}`",
        f"- source_estimated_frame_count_stats: `{summary['source_estimated_frame_count_stats']}`",
        f"- lexical_char_count_stats: `{summary['lexical_char_count_stats']}`",
        f"- clause_region_count_stats: `{summary['clause_region_count_stats']}`",
        f"- pause_boundary_event_count_stats: `{summary['pause_boundary_event_count_stats']}`",
        f"- terminal_boundary_event_count_stats: `{summary['terminal_boundary_event_count_stats']}`",
        f"- timeline_event_count_stats: `{summary['timeline_event_count_stats']}`",
        f"- source_to_target_duration_ratio_stats: `{summary['source_to_target_duration_ratio_stats']}`",
        f"- source_duration_metadata_drift_sec_stats: `{summary['source_duration_metadata_drift_sec_stats']}`",
        f"- target_duration_metadata_drift_sec_stats: `{summary['target_duration_metadata_drift_sec_stats']}`",
        "",
        "## 结构分布",
        f"- utterance_structure_type_counts: `{summary['utterance_structure_type_counts']}`",
        f"- label_status_counts: `{summary['label_status_counts']}`",
        "",
        "## 说明",
        "- 该 sidecar 通过 paired parallel 同内容 target 语义向 source 侧做 parity bootstrap，不代表 source-native text/phone semantic 已完成。",
        "- timing 来自 target lexical ratios 向 source frame 轴的投影，不是 source forced alignment。",
        "- 这一步的目标是补 source-side / parity-aware semantic assets，为后续更上游的 supervision 路线提供基础。 ",
    ]
    return "\n".join(lines) + "\n"
