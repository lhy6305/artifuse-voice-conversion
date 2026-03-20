from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.data_scan import summarize_numeric, write_json, write_manifest


def build_round1_manifests(
    round1_dir: Path | None,
    output_dir: Path,
    report_output_dir: Path,
    target_dir: Path | None = None,
    source_dir: Path | None = None,
) -> None:
    output_dir = output_dir.resolve()
    report_output_dir = report_output_dir.resolve()

    reset_managed_directory(output_dir)
    reset_managed_directory(report_output_dir)

    if round1_dir is not None:
        round1_dir = round1_dir.resolve()
    firefly_dir = target_dir.resolve() if target_dir is not None else (round1_dir / "firefly_mainstream")
    source_segments_dir = source_dir.resolve() if source_dir is not None else (round1_dir / "source_segments")

    target_records = build_target_records(firefly_dir)
    source_records = build_source_records(source_segments_dir)
    combined_records = target_records + source_records
    summary = build_manifest_summary(target_records=target_records, source_records=source_records)

    write_manifest(output_dir / "target_train.jsonl", target_records)
    write_manifest(output_dir / "source_train.jsonl", source_records)
    write_manifest(output_dir / "combined_round1.jsonl", combined_records)
    write_json(report_output_dir / "manifest_summary.json", summary)
    write_markdown_summary(report_output_dir / "manifest_summary.md", summary)


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_target_records(firefly_dir: Path) -> list[dict[str, object]]:
    manifest_path = firefly_dir / "manifest_round1_train.jsonl"
    records = load_jsonl(manifest_path)
    standardized: list[dict[str, object]] = []
    raw_firefly_dir = infer_raw_firefly_dir(firefly_dir)

    for item in records:
        wav = item["wav"]
        prepared_wav_path = item.get("prepared_wav_path")
        if prepared_wav_path not in {None, ""}:
            audio_path = (firefly_dir / str(prepared_wav_path)).resolve().as_posix()
        else:
            audio_path = (raw_firefly_dir / item["wav_path"]).resolve().as_posix()
        standardized.append(
            {
                "record_id": f"target::{item['id']}",
                "dataset": "firefly_round1_mainstream",
                "role": "target",
                "split": "train",
                "audio_path": audio_path,
                "audio": {
                    "sample_rate": wav["sample_rate"],
                    "channels": wav["channels"],
                    "sample_width_bytes": wav["sample_width_bytes"],
                    "duration_sec": wav["duration_sec"],
                },
                "text": {
                    "raw": item["text"]["raw"],
                    "clean": item["text"]["cleaned"],
                    "cleaned_lab_path": (firefly_dir / item["cleaned_lab_path"]).resolve().as_posix(),
                },
                "labels": {
                    "has_text": True,
                    "text_is_runtime_required": False,
                },
                "source_metadata": {
                    "prepared_wav_path": prepared_wav_path,
                    "original_lab_path": item["original_lab_path"],
                    "cleaning_kept_punctuation": item["text"]["kept_punctuation"],
                    "cleaning_removed_symbols": item["text"]["removed_symbols"],
                },
            }
        )
    return standardized


def infer_raw_firefly_dir(firefly_dir: Path) -> Path:
    project_root = firefly_dir.parent.parent.parent
    candidate = project_root / "data_convert" / "dataset_firefly_raw"
    if not candidate.exists():
        raise FileNotFoundError(f"Unable to locate raw firefly dataset at {candidate}")
    return candidate


def build_source_records(source_dir: Path) -> list[dict[str, object]]:
    manifest_path = source_dir / "segment_manifest.jsonl"
    records = load_jsonl(manifest_path)
    standardized: list[dict[str, object]] = []

    for item in records:
        standardized.append(
            {
                "record_id": f"source::{item['segment_id']}",
                "dataset": "ly65_round1_segments",
                "role": "source",
                "split": "train_candidate",
                "audio_path": item["path"],
                "audio": {
                    "sample_rate": 48000,
                    "channels": 1,
                    "sample_width_bytes": 2,
                    "duration_sec": item["duration_sec"],
                },
                "text": {
                    "raw": None,
                    "clean": None,
                    "cleaned_lab_path": None,
                },
                "labels": {
                    "has_text": False,
                    "text_is_runtime_required": False,
                },
                "source_metadata": {
                    "start_sec": item["start_sec"],
                    "end_sec": item["end_sec"],
                    "noise_gated_ratio": item["noise_gated_ratio"],
                    "parent_recording": "dataset_ly65_raw.wav",
                },
            }
        )
    return standardized


def build_manifest_summary(
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "target_record_count": len(target_records),
        "target_duration_stats_sec": summarize_numeric(
            [record["audio"]["duration_sec"] for record in target_records]
        ),
        "source_record_count": len(source_records),
        "source_duration_stats_sec": summarize_numeric(
            [record["audio"]["duration_sec"] for record in source_records]
        ),
        "notes": [
            "target records contain cleaned text for training-side alignment and supervision",
            "source records currently do not contain text and are prepared as train candidates",
            "runtime inference still does not require text input",
        ],
    }


def write_markdown_summary(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# round1 训练 manifest 摘要",
        "",
        "## 目标说话人",
        f"- 记录数: {summary['target_record_count']}",
        f"- 时长统计: {json.dumps(summary['target_duration_stats_sec'], ensure_ascii=False)}",
        "",
        "## 源说话人",
        f"- 记录数: {summary['source_record_count']}",
        f"- 时长统计: {json.dumps(summary['source_duration_stats_sec'], ensure_ascii=False)}",
        "",
        "## 备注",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records
