from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.data_scan import summarize_numeric, write_json
from v5vc.manifest_builder import load_jsonl


def check_round1_data(
    round1_dir: Path,
    manifest_dir: Path,
    report_output_dir: Path,
) -> None:
    round1_dir = round1_dir.resolve()
    manifest_dir = manifest_dir.resolve()
    report_output_dir = report_output_dir.resolve()

    reset_managed_directory(report_output_dir)

    target_manifest = manifest_dir / "target_train.jsonl"
    source_manifest = manifest_dir / "source_train.jsonl"
    combined_manifest = manifest_dir / "combined_round1.jsonl"

    target_records = load_jsonl(target_manifest)
    source_records = load_jsonl(source_manifest)
    combined_records = load_jsonl(combined_manifest)

    target_report = validate_target_records(target_records)
    source_report = validate_source_records(source_records)
    combined_report = validate_combined_records(combined_records, target_records, source_records)

    summary = {
        "target": target_report,
        "source": source_report,
        "combined": combined_report,
        "overall_ok": all(
            (
                target_report["missing_audio_count"] == 0,
                target_report["missing_clean_lab_count"] == 0,
                target_report["empty_clean_text_count"] == 0,
                source_report["missing_audio_count"] == 0,
                combined_report["duplicate_record_id_count"] == 0,
                combined_report["count_matches_components"],
            )
        ),
    }

    write_json(report_output_dir / "integrity_summary.json", summary)
    write_markdown_summary(report_output_dir / "integrity_summary.md", summary)


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def validate_target_records(records: list[dict[str, object]]) -> dict[str, object]:
    missing_audio: list[str] = []
    missing_clean_lab: list[str] = []
    empty_clean_text: list[str] = []
    durations: list[float] = []

    for record in records:
        audio_path = Path(record["audio_path"])
        clean_lab_path = Path(record["text"]["cleaned_lab_path"])
        clean_text = record["text"]["clean"]
        duration_sec = float(record["audio"]["duration_sec"])

        if not audio_path.exists():
            missing_audio.append(record["record_id"])
        if not clean_lab_path.exists():
            missing_clean_lab.append(record["record_id"])
        if not clean_text:
            empty_clean_text.append(record["record_id"])
        durations.append(duration_sec)

    return {
        "record_count": len(records),
        "duration_stats_sec": summarize_numeric(durations),
        "missing_audio_count": len(missing_audio),
        "missing_audio_examples": missing_audio[:20],
        "missing_clean_lab_count": len(missing_clean_lab),
        "missing_clean_lab_examples": missing_clean_lab[:20],
        "empty_clean_text_count": len(empty_clean_text),
        "empty_clean_text_examples": empty_clean_text[:20],
    }


def validate_source_records(records: list[dict[str, object]]) -> dict[str, object]:
    missing_audio: list[str] = []
    durations: list[float] = []

    for record in records:
        audio_path = Path(record["audio_path"])
        duration_sec = float(record["audio"]["duration_sec"])
        if not audio_path.exists():
            missing_audio.append(record["record_id"])
        durations.append(duration_sec)

    return {
        "record_count": len(records),
        "duration_stats_sec": summarize_numeric(durations),
        "missing_audio_count": len(missing_audio),
        "missing_audio_examples": missing_audio[:20],
    }


def validate_combined_records(
    combined_records: list[dict[str, object]],
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
) -> dict[str, object]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for record in combined_records:
        record_id = str(record["record_id"])
        if record_id in seen:
            duplicates.append(record_id)
            continue
        seen.add(record_id)

    expected_count = len(target_records) + len(source_records)
    return {
        "record_count": len(combined_records),
        "expected_component_count": expected_count,
        "count_matches_components": len(combined_records) == expected_count,
        "duplicate_record_id_count": len(duplicates),
        "duplicate_record_id_examples": duplicates[:20],
    }


def write_markdown_summary(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# round1 数据完整性检查",
        "",
        f"- overall_ok: {summary['overall_ok']}",
        "",
        "## 目标说话人 manifest",
        f"- 记录数: {summary['target']['record_count']}",
        f"- 缺失音频数: {summary['target']['missing_audio_count']}",
        f"- 缺失清洗标签数: {summary['target']['missing_clean_lab_count']}",
        f"- 空清洗文本数: {summary['target']['empty_clean_text_count']}",
        "",
        "## 源说话人 manifest",
        f"- 记录数: {summary['source']['record_count']}",
        f"- 缺失音频数: {summary['source']['missing_audio_count']}",
        "",
        "## 合并 manifest",
        f"- 记录数: {summary['combined']['record_count']}",
        f"- 组件数量一致: {summary['combined']['count_matches_components']}",
        f"- 重复 record_id 数: {summary['combined']['duplicate_record_id_count']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
