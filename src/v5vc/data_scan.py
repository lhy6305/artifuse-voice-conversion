from __future__ import annotations

import json
import math
import statistics
import unicodedata
import wave
from array import array
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SILENCE_THRESHOLDS_DBFS = (-50, -45, -40, -35, -30)
TOP_WINDOWS_TO_KEEP = 10


@dataclass
class WavMetadata:
    channels: int
    sample_width_bytes: int
    sample_rate: int
    frame_count: int
    duration_sec: float
    compression_type: str
    compression_name: str

    def to_dict(self) -> dict[str, object]:
        return {
            "channels": self.channels,
            "sample_width_bytes": self.sample_width_bytes,
            "sample_rate": self.sample_rate,
            "frame_count": self.frame_count,
            "duration_sec": round(self.duration_sec, 6),
            "compression_type": self.compression_type,
            "compression_name": self.compression_name,
        }


def scan_project_data(
    firefly_dir: Path,
    source_audio: Path,
    output_dir: Path,
    window_ms: int,
) -> None:
    firefly_dir = firefly_dir.resolve()
    source_audio = source_audio.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    firefly_report = scan_firefly_dataset(firefly_dir)
    source_report = scan_source_audio(source_audio, window_ms=window_ms)
    summary = build_summary(firefly_report=firefly_report, source_report=source_report)

    write_json(output_dir / "firefly_report.json", firefly_report)
    write_json(output_dir / "source_audio_report.json", source_report)
    write_json(output_dir / "scan_summary.json", summary)
    write_markdown_report(output_dir / "scan_report.md", summary, firefly_report, source_report)
    write_manifest(output_dir / "firefly_manifest.jsonl", firefly_report["manifest"])


def scan_firefly_dataset(dataset_dir: Path) -> dict[str, object]:
    wav_files = sorted(dataset_dir.rglob("*.wav"))
    lab_files = sorted(dataset_dir.rglob("*.lab"))

    wav_map = {path.relative_to(dataset_dir).with_suffix("").as_posix(): path for path in wav_files}
    lab_map = {path.relative_to(dataset_dir).with_suffix("").as_posix(): path for path in lab_files}

    paired_keys = sorted(set(wav_map) & set(lab_map))
    wav_only = sorted(set(wav_map) - set(lab_map))
    lab_only = sorted(set(lab_map) - set(wav_map))

    manifest: list[dict[str, object]] = []
    encoding_errors: list[dict[str, str]] = []
    punctuation_counter: Counter[str] = Counter()
    sample_rate_counter: Counter[int] = Counter()
    channel_counter: Counter[int] = Counter()
    duration_values: list[float] = []
    text_length_values: list[int] = []
    path_prefix_counter: Counter[str] = Counter()

    for key in paired_keys:
        wav_path = wav_map[key]
        lab_path = lab_map[key]
        wav_meta = read_wav_metadata(wav_path)
        sample_rate_counter[wav_meta.sample_rate] += 1
        channel_counter[wav_meta.channels] += 1
        duration_values.append(wav_meta.duration_sec)

        try:
            text = lab_path.read_text(encoding="utf-8")
            text_encoding_ok = True
        except UnicodeDecodeError as exc:
            text = ""
            text_encoding_ok = False
            encoding_errors.append(
                {
                    "path": lab_path.relative_to(dataset_dir).as_posix(),
                    "error": str(exc),
                }
            )

        text_stats = analyze_text(text)
        for symbol, count in text_stats["punctuation_counter"].items():
            punctuation_counter[symbol] += count
        text_length_values.append(text_stats["character_count"])

        relative_parent = wav_path.relative_to(dataset_dir).parent.as_posix()
        path_prefix_counter[relative_parent or "."] += 1

        manifest.append(
            {
                "id": key,
                "wav_path": wav_path.relative_to(dataset_dir).as_posix(),
                "lab_path": lab_path.relative_to(dataset_dir).as_posix(),
                "wav": wav_meta.to_dict(),
                "text": text,
                "text_encoding_ok": text_encoding_ok,
                "text_stats": {
                    "character_count": text_stats["character_count"],
                    "non_whitespace_count": text_stats["non_whitespace_count"],
                    "punctuation_count": text_stats["punctuation_count"],
                    "unique_punctuation": text_stats["unique_punctuation"],
                },
            }
        )

    return {
        "dataset_dir": dataset_dir.as_posix(),
        "file_counts": {
            "wav": len(wav_files),
            "lab": len(lab_files),
            "paired": len(paired_keys),
            "wav_without_lab": len(wav_only),
            "lab_without_wav": len(lab_only),
        },
        "sample_rate_distribution": dict(sorted(sample_rate_counter.items())),
        "channel_distribution": dict(sorted(channel_counter.items())),
        "duration_stats_sec": summarize_numeric(duration_values),
        "text_length_stats": summarize_numeric(text_length_values),
        "top_parent_directories": path_prefix_counter.most_common(20),
        "wav_without_lab": [f"{key}.wav" for key in wav_only],
        "lab_without_wav": [f"{key}.lab" for key in lab_only],
        "encoding_errors": encoding_errors,
        "punctuation_frequency": punctuation_counter.most_common(30),
        "manifest": manifest,
    }


def scan_source_audio(audio_path: Path, window_ms: int) -> dict[str, object]:
    metadata = read_wav_metadata(audio_path)
    window_stats = analyze_wav_windows(audio_path, window_ms=window_ms)

    return {
        "audio_path": audio_path.as_posix(),
        "wav": metadata.to_dict(),
        "window_ms": window_ms,
        "window_count": len(window_stats["windows"]),
        "dbfs_stats": summarize_numeric(window_stats["dbfs_values"]),
        "peak_dbfs_stats": summarize_numeric(window_stats["peak_dbfs_values"]),
        "silence_ratio_by_threshold": {
            str(threshold): round(window_stats["silence_counts"][threshold] / max(1, len(window_stats["windows"])), 6)
            for threshold in SILENCE_THRESHOLDS_DBFS
        },
        "clipped_window_ratio": round(window_stats["clipped_windows"] / max(1, len(window_stats["windows"])), 6),
        "top_loud_windows": window_stats["top_loud_windows"],
        "top_peak_windows": window_stats["top_peak_windows"],
    }


def build_summary(firefly_report: dict[str, object], source_report: dict[str, object]) -> dict[str, object]:
    firefly_counts = firefly_report["file_counts"]
    summary = {
        "high_level_findings": {
            "firefly_paired_ratio": round(
                firefly_counts["paired"] / max(1, firefly_counts["wav"]),
                6,
            ),
            "firefly_has_orphans": bool(
                firefly_counts["wav_without_lab"] or firefly_counts["lab_without_wav"]
            ),
            "source_duration_sec": source_report["wav"]["duration_sec"],
            "source_silence_ratio_dbfs_minus_40": source_report["silence_ratio_by_threshold"]["-40"],
        },
        "next_decisions_to_report": [
            "是否保留或归一化 firefly 文本中的标点符号",
            "源说话人音频的静音裁剪阈值和切分策略",
            "目标数据是否需要按子目录或场景做分桶",
        ],
    }
    return summary


def read_wav_metadata(path: Path) -> WavMetadata:
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        compression_type = wav_file.getcomptype()
        compression_name = wav_file.getcompname()

    duration_sec = frame_count / sample_rate if sample_rate else 0.0
    return WavMetadata(
        channels=channels,
        sample_width_bytes=sample_width,
        sample_rate=sample_rate,
        frame_count=frame_count,
        duration_sec=duration_sec,
        compression_type=compression_type,
        compression_name=compression_name,
    )


def analyze_text(text: str) -> dict[str, object]:
    punctuation_counter: Counter[str] = Counter()
    non_whitespace_count = 0
    for char in text:
        if not char.isspace():
            non_whitespace_count += 1
        if unicodedata.category(char).startswith("P"):
            punctuation_counter[char] += 1

    return {
        "character_count": len(text),
        "non_whitespace_count": non_whitespace_count,
        "punctuation_count": sum(punctuation_counter.values()),
        "unique_punctuation": sorted(punctuation_counter),
        "punctuation_counter": punctuation_counter,
    }


def analyze_wav_windows(path: Path, window_ms: int) -> dict[str, object]:
    dbfs_values: list[float] = []
    peak_dbfs_values: list[float] = []
    silence_counts = {threshold: 0 for threshold in SILENCE_THRESHOLDS_DBFS}
    clipped_windows = 0
    windows: list[dict[str, float]] = []

    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
        channels = wav_file.getnchannels()
        frames_per_window = max(1, int(sample_rate * window_ms / 1000))
        max_amplitude = max_possible_amplitude(sample_width)
        frame_offset = 0

        while True:
            raw = wav_file.readframes(frames_per_window)
            if not raw:
                break

            samples = decode_samples(raw, sample_width)
            if channels > 1:
                sample_count = len(samples) // channels
            else:
                sample_count = len(samples)

            if sample_count == 0:
                break

            rms = compute_rms(samples, sample_width)
            peak = compute_peak(samples, sample_width)
            rms_norm = min(1.0, rms / max_amplitude) if max_amplitude else 0.0
            peak_norm = min(1.0, peak / max_amplitude) if max_amplitude else 0.0
            dbfs = amplitude_to_dbfs(rms_norm)
            peak_dbfs = amplitude_to_dbfs(peak_norm)
            start_sec = frame_offset / sample_rate
            end_sec = (frame_offset + sample_count) / sample_rate

            window_info = {
                "start_sec": round(start_sec, 3),
                "end_sec": round(end_sec, 3),
                "dbfs": round(dbfs, 3),
                "peak_dbfs": round(peak_dbfs, 3),
            }
            windows.append(window_info)
            dbfs_values.append(dbfs)
            peak_dbfs_values.append(peak_dbfs)
            for threshold in SILENCE_THRESHOLDS_DBFS:
                if dbfs <= threshold:
                    silence_counts[threshold] += 1
            if peak_norm >= 0.999:
                clipped_windows += 1

            frame_offset += sample_count

    top_loud_windows = sorted(windows, key=lambda item: item["dbfs"], reverse=True)[:TOP_WINDOWS_TO_KEEP]
    top_peak_windows = sorted(windows, key=lambda item: item["peak_dbfs"], reverse=True)[:TOP_WINDOWS_TO_KEEP]

    return {
        "dbfs_values": dbfs_values,
        "peak_dbfs_values": peak_dbfs_values,
        "silence_counts": silence_counts,
        "clipped_windows": clipped_windows,
        "windows": windows,
        "top_loud_windows": top_loud_windows,
        "top_peak_windows": top_peak_windows,
    }


def max_possible_amplitude(sample_width: int) -> float:
    if sample_width == 1:
        return 127.0
    bits = sample_width * 8
    return float((1 << (bits - 1)) - 1)


def decode_samples(raw: bytes, sample_width: int) -> array:
    if sample_width == 1:
        values = array("B")
        values.frombytes(raw)
        return array("b", [value - 128 for value in values])
    if sample_width == 2:
        values = array("h")
        values.frombytes(raw)
        return values
    if sample_width == 4:
        values = array("i")
        values.frombytes(raw)
        return values
    raise ValueError(f"Unsupported sample width: {sample_width} bytes")


def compute_rms(samples: Sequence[int], sample_width: int) -> float:
    if not samples:
        return 0.0
    mean_square = sum(float(value) * float(value) for value in samples) / len(samples)
    return math.sqrt(mean_square)


def compute_peak(samples: Sequence[int], sample_width: int) -> float:
    if not samples:
        return 0.0
    return max(abs(value) for value in samples)


def amplitude_to_dbfs(amplitude: float) -> float:
    if amplitude <= 0:
        return -120.0
    return 20.0 * math.log10(amplitude)


def summarize_numeric(values: list[float] | list[int]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "stdev": None,
        }

    return {
        "count": len(values),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(statistics.fmean(values), 6),
        "median": round(statistics.median(values), 6),
        "stdev": round(statistics.pstdev(values), 6),
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_manifest(path: Path, manifest: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in manifest:
            handle.write(json.dumps(item, ensure_ascii=False))
            handle.write("\n")


def write_markdown_report(
    path: Path,
    summary: dict[str, object],
    firefly_report: dict[str, object],
    source_report: dict[str, object],
) -> None:
    firefly_counts = firefly_report["file_counts"]
    source_wav = source_report["wav"]
    top_punctuation = ", ".join(
        f"{symbol}:{count}" for symbol, count in firefly_report["punctuation_frequency"][:10]
    ) or "无"

    lines = [
        "# 数据扫描报告",
        "",
        "## 目标说话人数据集",
        f"- 数据目录: `{firefly_report['dataset_dir']}`",
        f"- wav 数量: {firefly_counts['wav']}",
        f"- lab 数量: {firefly_counts['lab']}",
        f"- 成功配对数: {firefly_counts['paired']}",
        f"- 缺失 lab 的 wav 数: {firefly_counts['wav_without_lab']}",
        f"- 缺失 wav 的 lab 数: {firefly_counts['lab_without_wav']}",
        f"- 常见标点: {top_punctuation}",
        "",
        "## 源说话人音频",
        f"- 音频路径: `{source_report['audio_path']}`",
        f"- 采样率: {source_wav['sample_rate']}",
        f"- 声道数: {source_wav['channels']}",
        f"- 时长秒数: {source_wav['duration_sec']}",
        f"- -40 dBFS 静音窗占比: {source_report['silence_ratio_by_threshold']['-40']}",
        f"- 剪切窗占比: {source_report['clipped_window_ratio']}",
        "",
        "## 后续需用户决策的点",
    ]

    for item in summary["next_decisions_to_report"]:
        lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
