from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from v5vc.manifest_builder import load_jsonl

PUNCTUATION_CATEGORY_BY_CODEPOINT = {
    0xFF0C: "pause_comma",
    0x3001: "pause_enumeration",
    0xFF1B: "pause_semicolon",
    0xFF1A: "pause_colon",
    0x3002: "terminal_period",
    0xFF1F: "terminal_question",
    0xFF01: "terminal_exclamation",
}


def build_b1_supervision_inventory(
    split_dir: Path,
    data_output_dir: Path,
    report_output_dir: Path,
) -> dict[str, object]:
    split_dir = split_dir.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    data_output_dir.mkdir(parents=True, exist_ok=True)
    report_output_dir.mkdir(parents=True, exist_ok=True)

    target_manifests = [
        ("target_train", split_dir / "target_train.jsonl"),
        ("target_validation", split_dir / "target_validation.jsonl"),
        ("target_special_eval", split_dir / "target_special_eval.jsonl"),
    ]
    source_manifests = [
        ("source_train", split_dir / "source_train.jsonl"),
        ("source_validation", split_dir / "source_validation.jsonl"),
    ]

    target_inventory_records: list[dict[str, object]] = []
    source_inventory_records: list[dict[str, object]] = []
    target_summary = initialize_target_summary()
    source_summary = initialize_source_summary()

    for split_name, manifest_path in target_manifests:
        for record in load_jsonl(manifest_path):
            inventory_record = build_target_inventory_record(record=record, split_name=split_name)
            target_inventory_records.append(inventory_record)
            update_target_summary(summary=target_summary, record=inventory_record)

    for split_name, manifest_path in source_manifests:
        for record in load_jsonl(manifest_path):
            inventory_record = build_source_inventory_record(record=record, split_name=split_name)
            source_inventory_records.append(inventory_record)
            update_source_summary(summary=source_summary, record=inventory_record)

    target_inventory_path = data_output_dir / "target_supervision_inventory.jsonl"
    source_inventory_path = data_output_dir / "source_supervision_inventory.jsonl"
    write_jsonl(target_inventory_path, target_inventory_records)
    write_jsonl(source_inventory_path, source_inventory_records)

    payload = {
        "split_dir": split_dir.as_posix(),
        "data_output_dir": data_output_dir.as_posix(),
        "target_inventory_path": target_inventory_path.as_posix(),
        "source_inventory_path": source_inventory_path.as_posix(),
        "target_summary": finalize_target_summary(target_summary),
        "source_summary": finalize_source_summary(source_summary),
        "notes": [
            "This inventory intentionally stays offline and uses only currently materialized manifests.",
            "Target-side text supervision is available now; source-side text supervision is not available in round1.",
            "target_special_eval remains a nonverbal challenge slice and should not be treated as normal lexical supervision.",
            "Phone/manner/place labels are not yet available in the workspace and remain future label slots.",
        ],
    }
    (report_output_dir / "b1_supervision_inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (report_output_dir / "b1_supervision_inventory.md").write_text(
        render_markdown_report(payload),
        encoding="utf-8",
        newline="\n",
    )
    return payload


def build_target_inventory_record(
    record: dict[str, object],
    split_name: str,
) -> dict[str, object]:
    clean_text = str(record["text"]["clean"] or "")
    punctuation_sequence = extract_punctuation_sequence(clean_text)
    lexical_char_count = count_lexical_chars(clean_text)
    punctuation_counter = Counter(item["category"] for item in punctuation_sequence)
    duration_sec = float(record["audio"]["duration_sec"])
    lexical_chars_per_sec = 0.0 if duration_sec <= 0 else round(lexical_char_count / duration_sec, 6)
    punctuation_density_per_sec = 0.0 if duration_sec <= 0 else round(len(punctuation_sequence) / duration_sec, 6)
    nonverbal_only = lexical_char_count == 0
    return {
        "record_id": str(record["record_id"]),
        "role": "target",
        "split_name": split_name,
        "audio_path": str(record["audio_path"]),
        "audio_duration_sec": duration_sec,
        "text": {
            "clean": clean_text,
            "total_char_count": len(clean_text),
            "lexical_char_count": lexical_char_count,
            "punctuation_count": len(punctuation_sequence),
            "punctuation_counts": dict(sorted(punctuation_counter.items())),
            "lexical_chars_per_sec": lexical_chars_per_sec,
            "punctuation_density_per_sec": punctuation_density_per_sec,
            "nonverbal_only": nonverbal_only,
        },
        "punctuation_sequence": punctuation_sequence,
        "supervision_sources": {
            "clean_text_available": True,
            "punctuation_boundary_hints_available": len(punctuation_sequence) > 0,
            "utterance_level_text_aux_available": not nonverbal_only,
            "phone_sequence_available": False,
            "manner_sequence_available": False,
            "place_sequence_available": False,
            "forced_alignment_available": False,
            "audio_heuristic_event_target_available": True,
        },
        "future_label_slots": {
            "phone_sequence": None,
            "manner_sequence": None,
            "place_sequence": None,
            "boundary_alignment": None,
            "label_status": "pending_upgrade",
        },
    }


def build_source_inventory_record(
    record: dict[str, object],
    split_name: str,
) -> dict[str, object]:
    return {
        "record_id": str(record["record_id"]),
        "role": "source",
        "split_name": split_name,
        "audio_path": str(record["audio_path"]),
        "audio_duration_sec": float(record["audio"]["duration_sec"]),
        "text": {
            "clean": None,
            "total_char_count": 0,
            "lexical_char_count": 0,
            "punctuation_count": 0,
            "punctuation_counts": {},
            "lexical_chars_per_sec": 0.0,
            "punctuation_density_per_sec": 0.0,
            "nonverbal_only": False,
        },
        "punctuation_sequence": [],
        "supervision_sources": {
            "clean_text_available": False,
            "punctuation_boundary_hints_available": False,
            "utterance_level_text_aux_available": False,
            "phone_sequence_available": False,
            "manner_sequence_available": False,
            "place_sequence_available": False,
            "forced_alignment_available": False,
            "audio_heuristic_event_target_available": True,
        },
        "future_label_slots": {
            "phone_sequence": None,
            "manner_sequence": None,
            "place_sequence": None,
            "boundary_alignment": None,
            "label_status": "missing_transcript",
        },
    }


def extract_punctuation_sequence(text: str) -> list[dict[str, object]]:
    sequence: list[dict[str, object]] = []
    for index, character in enumerate(text):
        category = PUNCTUATION_CATEGORY_BY_CODEPOINT.get(ord(character))
        if category is None:
            continue
        sequence.append(
            {
                "char_index": index,
                "char": character,
                "category": category,
            }
        )
    return sequence


def count_lexical_chars(text: str) -> int:
    return sum(1 for character in text if ord(character) not in PUNCTUATION_CATEGORY_BY_CODEPOINT)


def initialize_target_summary() -> dict[str, object]:
    return {
        "record_count": 0,
        "split_counts": Counter(),
        "nonverbal_only_count": 0,
        "punctuation_category_counts": Counter(),
        "records_with_pause_hints": 0,
        "total_lexical_char_count": 0,
        "total_audio_duration_sec": 0.0,
    }


def initialize_source_summary() -> dict[str, object]:
    return {
        "record_count": 0,
        "split_counts": Counter(),
        "records_with_text": 0,
        "total_audio_duration_sec": 0.0,
    }


def update_target_summary(summary: dict[str, object], record: dict[str, object]) -> None:
    summary["record_count"] += 1
    summary["split_counts"][record["split_name"]] += 1
    summary["total_audio_duration_sec"] += float(record["audio_duration_sec"])
    summary["total_lexical_char_count"] += int(record["text"]["lexical_char_count"])
    if bool(record["text"]["nonverbal_only"]):
        summary["nonverbal_only_count"] += 1
    if bool(record["supervision_sources"]["punctuation_boundary_hints_available"]):
        summary["records_with_pause_hints"] += 1
    for item in record["punctuation_sequence"]:
        summary["punctuation_category_counts"][item["category"]] += 1


def update_source_summary(summary: dict[str, object], record: dict[str, object]) -> None:
    summary["record_count"] += 1
    summary["split_counts"][record["split_name"]] += 1
    summary["total_audio_duration_sec"] += float(record["audio_duration_sec"])
    if bool(record["supervision_sources"]["clean_text_available"]):
        summary["records_with_text"] += 1


def finalize_target_summary(summary: dict[str, object]) -> dict[str, object]:
    record_count = max(1, int(summary["record_count"]))
    total_audio_duration_sec = float(summary["total_audio_duration_sec"])
    return {
        "record_count": int(summary["record_count"]),
        "split_counts": dict(sorted(summary["split_counts"].items())),
        "nonverbal_only_count": int(summary["nonverbal_only_count"]),
        "records_with_pause_hints": int(summary["records_with_pause_hints"]),
        "punctuation_category_counts": dict(sorted(summary["punctuation_category_counts"].items())),
        "avg_lexical_chars_per_record": round(float(summary["total_lexical_char_count"]) / record_count, 6),
        "avg_audio_duration_sec": round(total_audio_duration_sec / record_count, 6),
        "avg_lexical_chars_per_sec": (
            0.0
            if total_audio_duration_sec <= 0
            else round(float(summary["total_lexical_char_count"]) / total_audio_duration_sec, 6)
        ),
    }


def finalize_source_summary(summary: dict[str, object]) -> dict[str, object]:
    record_count = max(1, int(summary["record_count"]))
    total_audio_duration_sec = float(summary["total_audio_duration_sec"])
    return {
        "record_count": int(summary["record_count"]),
        "split_counts": dict(sorted(summary["split_counts"].items())),
        "records_with_text": int(summary["records_with_text"]),
        "avg_audio_duration_sec": round(total_audio_duration_sec / record_count, 6),
    }


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def render_markdown_report(payload: dict[str, object]) -> str:
    target_summary = payload["target_summary"]
    source_summary = payload["source_summary"]
    lines = [
        "# B1 Supervision Inventory",
        "",
        "## Summary",
        "- This inventory records which supervision sources are already available offline in round1.",
        "- It is designed to support route B without assuming any network downloads or new third-party packages.",
        "",
        "先说人话：",
        "- 目标侧现在已经有可直接用的文本和标点停顿线索。",
        "- 源侧现在没有文本，所以暂时不能走同等级的文本监督。",
        "- `target_special_eval` 仍然只是非完整发声 challenge slice，不能拿来当正常 lexical supervision。",
        "",
        "## Target Summary",
        f"- record_count: `{target_summary['record_count']}`",
        f"- split_counts: `{target_summary['split_counts']}`",
        f"- nonverbal_only_count: `{target_summary['nonverbal_only_count']}`",
        f"- records_with_pause_hints: `{target_summary['records_with_pause_hints']}`",
        f"- avg_lexical_chars_per_record: `{target_summary['avg_lexical_chars_per_record']}`",
        f"- avg_audio_duration_sec: `{target_summary['avg_audio_duration_sec']}`",
        f"- avg_lexical_chars_per_sec: `{target_summary['avg_lexical_chars_per_sec']}`",
        f"- punctuation_category_counts: `{target_summary['punctuation_category_counts']}`",
        "",
        "## Source Summary",
        f"- record_count: `{source_summary['record_count']}`",
        f"- split_counts: `{source_summary['split_counts']}`",
        f"- records_with_text: `{source_summary['records_with_text']}`",
        f"- avg_audio_duration_sec: `{source_summary['avg_audio_duration_sec']}`",
        "",
        "## Immediate Implications",
        "- Route B can start from target-side punctuation and text-aware supervision immediately.",
        "- Route B cannot yet assume source-side phone or manner supervision in round1.",
        "- The safest first upgrade is to separate future lexical/event labels from the current heuristic frame targets instead of replacing training code in one jump.",
        "",
        "## Artifacts",
        f"- target_inventory_path: `{payload['target_inventory_path']}`",
        f"- source_inventory_path: `{payload['source_inventory_path']}`",
        "",
        "## Notes",
    ]
    for note in payload["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
