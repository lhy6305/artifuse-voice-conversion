from __future__ import annotations

import json
import math
import re
import shutil
import unicodedata
import wave
from array import array
from collections import Counter
from pathlib import Path

from v5vc.data_scan import (
    SILENCE_THRESHOLDS_DBFS,
    amplitude_to_dbfs,
    analyze_wav_windows,
    compute_peak,
    compute_rms,
    decode_samples,
    read_wav_metadata,
    summarize_numeric,
    write_json,
    write_manifest,
)


def run_preprocessing(
    firefly_dir: Path,
    source_audio: Path,
    config_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
) -> None:
    firefly_dir = firefly_dir.resolve()
    source_audio = source_audio.resolve()
    config_path = config_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()

    config = json.loads(config_path.read_text(encoding="utf-8"))

    data_output_dir.mkdir(parents=True, exist_ok=True)
    report_output_dir.mkdir(parents=True, exist_ok=True)

    target_output_dir = data_output_dir / "firefly_mainstream"
    source_output_dir = data_output_dir / "source_segments"
    reset_managed_directory(target_output_dir)
    reset_managed_directory(source_output_dir)
    reset_managed_directory(report_output_dir)

    target_report = preprocess_firefly_dataset(
        dataset_dir=firefly_dir,
        output_dir=target_output_dir,
        config=config["target_dataset"],
    )
    source_report = preprocess_source_audio(
        audio_path=source_audio,
        output_dir=source_output_dir,
        config=config["source_audio"],
    )

    summary = build_preprocess_summary(target_report=target_report, source_report=source_report)
    write_json(report_output_dir / "target_dataset_report.json", target_report)
    write_json(report_output_dir / "source_audio_report.json", source_report)
    write_json(report_output_dir / "preprocess_summary.json", summary)
    write_markdown_summary(report_output_dir / "preprocess_summary.md", summary, target_report, source_report)


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def preprocess_firefly_dataset(dataset_dir: Path, output_dir: Path, config: dict[str, object]) -> dict[str, object]:
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    keep_sample_rate = int(config["mainstream_sample_rate"])
    keep_channels = int(config["mainstream_channels"])
    keep_punctuation = set(config["text_rules"]["keep_punctuation"])
    normalize_map = dict(config["text_rules"]["normalize_map"])
    remove_chars = set(config["text_rules"]["remove_characters"])
    compress_whitespace = bool(config["text_rules"]["compress_whitespace"])
    collapse_repeated_punctuation = bool(config["text_rules"].get("collapse_repeated_punctuation", True))

    all_records: list[dict[str, object]] = []
    train_records: list[dict[str, object]] = []
    excluded_records: list[dict[str, object]] = []
    kept_punctuation_counter: Counter[str] = Counter()
    removed_symbol_counter: Counter[str] = Counter()
    normalized_symbol_counter: Counter[str] = Counter()

    for wav_path in sorted(dataset_dir.rglob("*.wav")):
        lab_path = wav_path.with_suffix(".lab")
        relative_wav = wav_path.relative_to(dataset_dir).as_posix()
        relative_lab = lab_path.relative_to(dataset_dir).as_posix() if lab_path.exists() else None
        wav_meta = read_wav_metadata(wav_path)

        raw_text = lab_path.read_text(encoding="utf-8") if lab_path.exists() else ""
        normalized = normalize_firefly_text(
            text=raw_text,
            keep_punctuation=keep_punctuation,
            normalize_map=normalize_map,
            remove_characters=remove_chars,
            compress_whitespace=compress_whitespace,
            collapse_repeated_punctuation=collapse_repeated_punctuation,
        )

        include_reasons: list[str] = []
        if wav_meta.sample_rate != keep_sample_rate:
            include_reasons.append(f"sample_rate={wav_meta.sample_rate}")
        if wav_meta.channels != keep_channels:
            include_reasons.append(f"channels={wav_meta.channels}")
        if not lab_path.exists():
            include_reasons.append("missing_lab")
        if not normalized["cleaned_text"]:
            include_reasons.append("empty_cleaned_text")

        for symbol, count in normalized["kept_punctuation_counter"].items():
            kept_punctuation_counter[symbol] += count
        for symbol, count in normalized["removed_counter"].items():
            removed_symbol_counter[symbol] += count
        for symbol, count in normalized["normalized_counter"].items():
            normalized_symbol_counter[symbol] += count

        cleaned_lab_relative = Path("labels") / Path(relative_lab if relative_lab else relative_wav).with_suffix(".lab")
        record = {
            "id": wav_path.relative_to(dataset_dir).with_suffix("").as_posix(),
            "wav_path": relative_wav,
            "original_lab_path": relative_lab,
            "cleaned_lab_path": cleaned_lab_relative.as_posix(),
            "wav": wav_meta.to_dict(),
            "text": {
                "raw": raw_text,
                "cleaned": normalized["cleaned_text"],
                "kept_punctuation": sorted(normalized["kept_punctuation_counter"]),
                "removed_symbols": sorted(normalized["removed_counter"]),
                "normalized_symbols": normalized["normalized_events"],
            },
            "include_in_round1": not include_reasons,
            "exclusion_reasons": include_reasons,
        }
        all_records.append(record)

        if include_reasons:
            excluded_records.append(record)
            continue

        cleaned_lab_path = output_dir / cleaned_lab_relative
        cleaned_lab_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_lab_path.write_text(normalized["cleaned_text"] + "\n", encoding="utf-8", newline="\n")
        train_records.append(record)

    write_manifest(output_dir / "manifest_all.jsonl", all_records)
    write_manifest(output_dir / "manifest_round1_train.jsonl", train_records)
    write_manifest(output_dir / "manifest_round1_excluded.jsonl", excluded_records)

    return {
        "dataset_dir": dataset_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "mainstream_rule": {
            "sample_rate": keep_sample_rate,
            "channels": keep_channels,
        },
        "counts": {
            "all_records": len(all_records),
            "round1_train_records": len(train_records),
            "excluded_records": len(excluded_records),
        },
        "round1_total_duration_sec": round(
            sum(record["wav"]["duration_sec"] for record in train_records),
            6,
        ),
        "clean_text_length_stats": summarize_numeric(
            [len(record["text"]["cleaned"]) for record in all_records]
        ),
        "kept_punctuation_frequency": kept_punctuation_counter.most_common(20),
        "removed_symbol_frequency": removed_symbol_counter.most_common(20),
        "normalized_symbol_frequency": normalized_symbol_counter.most_common(20),
        "excluded_examples": excluded_records[:30],
    }


def normalize_firefly_text(
    text: str,
    keep_punctuation: set[str],
    normalize_map: dict[str, str],
    remove_characters: set[str],
    compress_whitespace: bool,
    collapse_repeated_punctuation: bool,
) -> dict[str, object]:
    cleaned_chars: list[str] = []
    removed_counter: Counter[str] = Counter()
    normalized_counter: Counter[str] = Counter()
    kept_punctuation_counter: Counter[str] = Counter()
    normalized_events: list[dict[str, str]] = []

    for char in text:
        replacement = char
        if char in normalize_map:
            replacement = normalize_map[char]
            normalized_counter[char] += 1
            normalized_events.append({"from": char, "to": replacement})
        if replacement in remove_characters:
            removed_counter[replacement] += 1
            continue

        if replacement.isspace():
            cleaned_chars.append(" ")
            continue

        if replacement in keep_punctuation:
            kept_punctuation_counter[replacement] += 1
            cleaned_chars.append(replacement)
            continue

        if is_punctuation_like(replacement):
            removed_counter[replacement] += 1
            continue

        cleaned_chars.append(replacement)

    cleaned_text = "".join(cleaned_chars)
    if compress_whitespace:
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    if collapse_repeated_punctuation:
        punctuation_class = "".join(re.escape(char) for char in sorted(keep_punctuation))
        if punctuation_class:
            cleaned_text = re.sub(rf"([{punctuation_class}])\1+", r"\1", cleaned_text)

    return {
        "cleaned_text": cleaned_text,
        "removed_counter": removed_counter,
        "normalized_counter": normalized_counter,
        "kept_punctuation_counter": kept_punctuation_counter,
        "normalized_events": normalized_events[:50],
    }


def preprocess_source_audio(audio_path: Path, output_dir: Path, config: dict[str, object]) -> dict[str, object]:
    segments_dir = output_dir / "segments"
    peaks_dir = output_dir / "peaks"
    segments_dir.mkdir(parents=True, exist_ok=True)
    peaks_dir.mkdir(parents=True, exist_ok=True)

    window_ms = int(config["analysis_window_ms"])
    windows_report = analyze_wav_windows(audio_path, window_ms=window_ms)
    metadata = read_wav_metadata(audio_path)

    noise_floor_dbfs = estimate_noise_floor_dbfs(
        dbfs_values=windows_report["dbfs_values"],
        min_candidate_dbfs=float(config["noise_floor_estimation"]["min_candidate_dbfs"]),
        max_candidate_dbfs=float(config["noise_floor_estimation"]["max_candidate_dbfs"]),
        percentile=float(config["noise_floor_estimation"]["percentile"]),
        min_window_count=int(config["noise_floor_estimation"]["min_window_count"]),
    )
    stable_noise = (
        noise_floor_dbfs is not None
        and noise_floor_dbfs >= float(config["noise_floor_estimation"]["noise_present_dbfs"])
    )

    content_threshold_dbfs = float(config["segment_detection"]["absolute_content_threshold_dbfs"])
    if noise_floor_dbfs is not None:
        content_threshold_dbfs = max(
            content_threshold_dbfs,
            noise_floor_dbfs + float(config["segment_detection"]["relative_content_margin_db"]),
        )
    boundary_threshold_dbfs = float(
        config["boundary_rules"].get("boundary_threshold_dbfs", content_threshold_dbfs)
    )
    boundary_min_quiet_ms = int(config["boundary_rules"]["min_quiet_ms"])

    detected_segments = detect_content_segments(
        windows=windows_report["windows"],
        content_threshold_dbfs=content_threshold_dbfs,
        peak_threshold_dbfs=float(config["segment_detection"]["peak_assist_threshold_dbfs"]),
        min_segment_ms=int(config["segment_detection"]["min_segment_ms"]),
        max_gap_ms=int(config["segment_detection"]["max_gap_ms"]),
        pad_before_ms=int(config["segment_detection"]["pad_before_ms"]),
        pad_after_ms=int(config["segment_detection"]["pad_after_ms"]),
        total_duration_sec=metadata.duration_sec,
        window_ms=window_ms,
    )
    manual_peak_decisions = list(config["manual_review"]["peak_decisions"])
    manual_exclusion_intervals = build_manual_exclusion_intervals(manual_peak_decisions)
    filtered_segments = apply_exclusion_intervals_to_segments(
        segments=detected_segments,
        exclusion_intervals=manual_exclusion_intervals,
        min_segment_ms=int(config["segment_detection"]["min_segment_ms"]),
    )
    boundary_valid_segments, boundary_rejected_segments = enforce_segment_boundary_rules(
        segments=filtered_segments,
        windows=windows_report["windows"],
        boundary_threshold_dbfs=boundary_threshold_dbfs,
        min_quiet_ms=boundary_min_quiet_ms,
    )

    noise_gate_threshold_dbfs = None
    if stable_noise:
        noise_gate_threshold_dbfs = noise_floor_dbfs + float(config["noise_gate"]["gate_margin_db"])

    segment_records = export_source_segments(
        audio_path=audio_path,
        segments=boundary_valid_segments,
        output_dir=segments_dir,
        gate_window_ms=int(config["noise_gate"]["window_ms"]),
        noise_gate_threshold_dbfs=noise_gate_threshold_dbfs,
        apply_gate=bool(config["noise_gate"]["enabled"]) and stable_noise,
        peak_keep_threshold_dbfs=float(config["noise_gate"]["peak_keep_threshold_dbfs"]),
    )

    peak_candidates = detect_peak_candidates(
        windows=windows_report["windows"],
        top_k=int(config["peak_export"]["top_peak_count"]),
        abrupt_delta_db=float(config["peak_export"]["abrupt_delta_db"]),
        min_peak_dbfs=float(config["peak_export"]["min_peak_dbfs"]),
        top_abrupt_count=int(config["peak_export"]["top_abrupt_count"]),
        max_total_clips=int(config["peak_export"]["max_total_clips"]),
        min_separation_ms=int(config["peak_export"]["min_separation_ms"]),
        clip_pre_ms=int(config["peak_export"]["clip_pre_ms"]),
        clip_post_ms=int(config["peak_export"]["clip_post_ms"]),
        total_duration_sec=metadata.duration_sec,
        window_ms=window_ms,
    )
    peak_candidates = apply_manual_peak_review_to_candidates(
        peak_candidates=peak_candidates,
        manual_peak_decisions=manual_peak_decisions,
    )
    peak_records = export_peak_clips(
        audio_path=audio_path,
        peak_candidates=peak_candidates,
        output_dir=peaks_dir,
    )

    write_manifest(output_dir / "segment_manifest.jsonl", segment_records)
    write_manifest(output_dir / "peak_manifest.jsonl", peak_records)

    return {
        "audio_path": audio_path.as_posix(),
        "output_dir": output_dir.as_posix(),
        "wav": metadata.to_dict(),
        "analysis_window_ms": window_ms,
        "noise_floor_dbfs": None if noise_floor_dbfs is None else round(noise_floor_dbfs, 6),
        "stable_noise_detected": stable_noise,
        "content_threshold_dbfs": round(content_threshold_dbfs, 6),
        "boundary_threshold_dbfs": round(boundary_threshold_dbfs, 6),
        "boundary_min_quiet_ms": boundary_min_quiet_ms,
        "noise_gate_threshold_dbfs": None if noise_gate_threshold_dbfs is None else round(noise_gate_threshold_dbfs, 6),
        "silence_ratio_by_threshold": {
            str(threshold): round(windows_report["silence_counts"][threshold] / max(1, len(windows_report["windows"])), 6)
            for threshold in SILENCE_THRESHOLDS_DBFS
        },
        "detected_segment_count_before_manual_filters": len(detected_segments),
        "segment_count_after_manual_exclusions": len(filtered_segments),
        "boundary_rejected_segment_count": len(boundary_rejected_segments),
        "manual_exclusion_intervals": manual_exclusion_intervals,
        "segment_count": len(segment_records),
        "segment_total_duration_sec": round(
            sum(record["duration_sec"] for record in segment_records),
            6,
        ),
        "segment_duration_stats_sec": summarize_numeric(
            [record["duration_sec"] for record in segment_records]
        ),
        "peak_clip_count": len(peak_records),
        "peak_candidates": peak_records,
        "manual_peak_decisions": manual_peak_decisions,
        "boundary_rejected_examples": boundary_rejected_segments[:30],
    }


def estimate_noise_floor_dbfs(
    dbfs_values: list[float],
    min_candidate_dbfs: float,
    max_candidate_dbfs: float,
    percentile: float,
    min_window_count: int,
) -> float | None:
    candidates = [
        value for value in dbfs_values
        if min_candidate_dbfs <= value <= max_candidate_dbfs
    ]
    if len(candidates) < min_window_count:
        return None
    return percentile_value(candidates, percentile)


def detect_content_segments(
    windows: list[dict[str, float]],
    content_threshold_dbfs: float,
    peak_threshold_dbfs: float,
    min_segment_ms: int,
    max_gap_ms: int,
    pad_before_ms: int,
    pad_after_ms: int,
    total_duration_sec: float,
    window_ms: int,
) -> list[dict[str, float]]:
    raw_segments: list[dict[str, float]] = []
    current_start_sec: float | None = None
    last_active_end_sec: float | None = None
    gap_sec = max_gap_ms / 1000.0
    min_segment_sec = min_segment_ms / 1000.0

    for window in windows:
        is_active = (
            window["dbfs"] >= content_threshold_dbfs
            or window["peak_dbfs"] >= peak_threshold_dbfs
        )
        if is_active:
            if current_start_sec is None:
                current_start_sec = window["start_sec"]
            last_active_end_sec = window["end_sec"]
            continue

        if current_start_sec is not None and last_active_end_sec is not None:
            if window["start_sec"] - last_active_end_sec > gap_sec:
                raw_segments.append(
                    {
                        "start_sec": current_start_sec,
                        "end_sec": last_active_end_sec,
                    }
                )
                current_start_sec = None
                last_active_end_sec = None

    if current_start_sec is not None and last_active_end_sec is not None:
        raw_segments.append({"start_sec": current_start_sec, "end_sec": last_active_end_sec})

    merged_segments: list[dict[str, float]] = []
    for segment in raw_segments:
        if merged_segments and segment["start_sec"] - merged_segments[-1]["end_sec"] <= gap_sec:
            merged_segments[-1]["end_sec"] = segment["end_sec"]
        else:
            merged_segments.append(segment.copy())

    padded_segments: list[dict[str, float]] = []
    for segment in merged_segments:
        padded_start = max(0.0, segment["start_sec"] - pad_before_ms / 1000.0)
        padded_end = min(total_duration_sec, segment["end_sec"] + pad_after_ms / 1000.0)
        if padded_end - padded_start < min_segment_sec:
            continue
        padded_segments.append(
            {
                "start_sec": round(padded_start, 6),
                "end_sec": round(padded_end, 6),
            }
        )
    return padded_segments


def build_manual_exclusion_intervals(
    manual_peak_decisions: list[dict[str, object]],
) -> list[dict[str, object]]:
    intervals: list[dict[str, object]] = []
    for item in manual_peak_decisions:
        if item.get("segment_action") != "exclude_interval":
            continue
        intervals.append(
            {
                "name": item["clip_id"],
                "start_sec": float(item["start_sec"]),
                "end_sec": float(item["end_sec"]),
                "reason": item["reason"],
            }
        )
    return sorted(intervals, key=lambda item: item["start_sec"])


def apply_exclusion_intervals_to_segments(
    segments: list[dict[str, float]],
    exclusion_intervals: list[dict[str, object]],
    min_segment_ms: int,
) -> list[dict[str, float]]:
    min_segment_sec = min_segment_ms / 1000.0
    current_segments = [segment.copy() for segment in segments]

    for interval in exclusion_intervals:
        next_segments: list[dict[str, float]] = []
        interval_start = float(interval["start_sec"])
        interval_end = float(interval["end_sec"])
        for segment in current_segments:
            if segment["end_sec"] <= interval_start or segment["start_sec"] >= interval_end:
                next_segments.append(segment)
                continue

            left_end = min(segment["end_sec"], interval_start)
            right_start = max(segment["start_sec"], interval_end)
            if left_end - segment["start_sec"] >= min_segment_sec:
                next_segments.append(
                    {
                        "start_sec": round(segment["start_sec"], 6),
                        "end_sec": round(left_end, 6),
                    }
                )
            if segment["end_sec"] - right_start >= min_segment_sec:
                next_segments.append(
                    {
                        "start_sec": round(right_start, 6),
                        "end_sec": round(segment["end_sec"], 6),
                    }
                )
        current_segments = sorted(next_segments, key=lambda item: item["start_sec"])

    return current_segments


def enforce_segment_boundary_rules(
    segments: list[dict[str, float]],
    windows: list[dict[str, float]],
    boundary_threshold_dbfs: float,
    min_quiet_ms: int,
) -> tuple[list[dict[str, float]], list[dict[str, object]]]:
    required_quiet_sec = min_quiet_ms / 1000.0
    kept_segments: list[dict[str, float]] = []
    rejected_segments: list[dict[str, object]] = []

    for segment in segments:
        start_quiet_sec = quiet_duration_touching_boundary(
            windows=windows,
            boundary_sec=segment["start_sec"],
            direction="before",
            boundary_threshold_dbfs=boundary_threshold_dbfs,
        )
        end_quiet_sec = quiet_duration_touching_boundary(
            windows=windows,
            boundary_sec=segment["end_sec"],
            direction="after",
            boundary_threshold_dbfs=boundary_threshold_dbfs,
        )
        if start_quiet_sec >= required_quiet_sec and end_quiet_sec >= required_quiet_sec:
            kept_segments.append(segment)
            continue
        rejected_segments.append(
            {
                "start_sec": segment["start_sec"],
                "end_sec": segment["end_sec"],
                "duration_sec": round(segment["end_sec"] - segment["start_sec"], 6),
                "start_quiet_sec": round(start_quiet_sec, 6),
                "end_quiet_sec": round(end_quiet_sec, 6),
            }
        )

    return kept_segments, rejected_segments


def quiet_duration_touching_boundary(
    windows: list[dict[str, float]],
    boundary_sec: float,
    direction: str,
    boundary_threshold_dbfs: float,
) -> float:
    epsilon = 1e-6
    if direction == "before":
        index = find_window_index_at_or_before_boundary(windows, boundary_sec)
        if index is None:
            return 0.0
        window = windows[index]
        if window["dbfs"] > boundary_threshold_dbfs:
            return 0.0
        quiet_sec = max(0.0, min(boundary_sec, window["end_sec"]) - window["start_sec"])
        cursor = index - 1
        while cursor >= 0:
            previous = windows[cursor]
            current = windows[cursor + 1]
            if previous["dbfs"] > boundary_threshold_dbfs:
                break
            if abs(previous["end_sec"] - current["start_sec"]) > epsilon:
                break
            quiet_sec += previous["end_sec"] - previous["start_sec"]
            cursor -= 1
        return quiet_sec

    index = find_window_index_at_or_after_boundary(windows, boundary_sec)
    if index is None:
        return 0.0
    window = windows[index]
    if window["dbfs"] > boundary_threshold_dbfs:
        return 0.0
    quiet_sec = max(0.0, window["end_sec"] - max(boundary_sec, window["start_sec"]))
    cursor = index + 1
    while cursor < len(windows):
        previous = windows[cursor - 1]
        current = windows[cursor]
        if current["dbfs"] > boundary_threshold_dbfs:
            break
        if abs(previous["end_sec"] - current["start_sec"]) > epsilon:
            break
        quiet_sec += current["end_sec"] - current["start_sec"]
        cursor += 1
    return quiet_sec


def find_window_index_at_or_before_boundary(
    windows: list[dict[str, float]],
    boundary_sec: float,
) -> int | None:
    epsilon = 1e-6
    candidate: int | None = None
    for index, window in enumerate(windows):
        if window["start_sec"] - epsilon <= boundary_sec <= window["end_sec"] + epsilon:
            return index
        if window["end_sec"] <= boundary_sec + epsilon:
            candidate = index
        elif window["start_sec"] > boundary_sec + epsilon:
            break
    return candidate


def find_window_index_at_or_after_boundary(
    windows: list[dict[str, float]],
    boundary_sec: float,
) -> int | None:
    epsilon = 1e-6
    for index, window in enumerate(windows):
        if window["start_sec"] - epsilon <= boundary_sec <= window["end_sec"] + epsilon:
            return index
        if window["start_sec"] >= boundary_sec - epsilon:
            return index
    return None


def export_source_segments(
    audio_path: Path,
    segments: list[dict[str, float]],
    output_dir: Path,
    gate_window_ms: int,
    noise_gate_threshold_dbfs: float | None,
    apply_gate: bool,
    peak_keep_threshold_dbfs: float,
) -> list[dict[str, object]]:
    metadata = read_wav_metadata(audio_path)
    records: list[dict[str, object]] = []

    for index, segment in enumerate(segments, start=1):
        samples = read_wav_segment_samples(
            audio_path=audio_path,
            start_sec=segment["start_sec"],
            end_sec=segment["end_sec"],
        )
        if apply_gate and noise_gate_threshold_dbfs is not None:
            samples, gated_ratio = apply_noise_gate_to_samples(
                samples=samples,
                sample_rate=metadata.sample_rate,
                sample_width_bytes=metadata.sample_width_bytes,
                channels=metadata.channels,
                gate_window_ms=gate_window_ms,
                gate_threshold_dbfs=noise_gate_threshold_dbfs,
                peak_keep_threshold_dbfs=peak_keep_threshold_dbfs,
            )
        else:
            gated_ratio = 0.0

        output_name = (
            f"segment_{index:04d}_{int(segment['start_sec'] * 1000):010d}_{int(segment['end_sec'] * 1000):010d}.wav"
        )
        output_path = output_dir / output_name
        write_wav_samples(output_path, samples, metadata)

        records.append(
            {
                "segment_id": output_name[:-4],
                "path": output_path.as_posix(),
                "start_sec": segment["start_sec"],
                "end_sec": segment["end_sec"],
                "duration_sec": round(segment["end_sec"] - segment["start_sec"], 6),
                "noise_gated_ratio": round(gated_ratio, 6),
            }
        )
    return records


def detect_peak_candidates(
    windows: list[dict[str, float]],
    top_k: int,
    abrupt_delta_db: float,
    min_peak_dbfs: float,
    top_abrupt_count: int,
    max_total_clips: int,
    min_separation_ms: int,
    clip_pre_ms: int,
    clip_post_ms: int,
    total_duration_sec: float,
    window_ms: int,
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    sorted_peaks = sorted(windows, key=lambda item: item["peak_dbfs"], reverse=True)[:top_k]
    for item in sorted_peaks:
        candidates.append(
            build_peak_candidate(
                center_sec=(item["start_sec"] + item["end_sec"]) / 2.0,
                reason="top_peak",
                score=item["peak_dbfs"],
                clip_pre_ms=clip_pre_ms,
                clip_post_ms=clip_post_ms,
                total_duration_sec=total_duration_sec,
            )
        )

    abrupt_candidates: list[dict[str, object]] = []
    for previous, current in zip(windows, windows[1:]):
        delta = current["peak_dbfs"] - previous["peak_dbfs"]
        if delta >= abrupt_delta_db and current["peak_dbfs"] >= min_peak_dbfs:
            abrupt_candidates.append(
                build_peak_candidate(
                    center_sec=(current["start_sec"] + current["end_sec"]) / 2.0,
                    reason="abrupt_rise",
                    score=round(delta, 6),
                    clip_pre_ms=clip_pre_ms,
                    clip_post_ms=clip_post_ms,
                    total_duration_sec=total_duration_sec,
                )
            )
    candidates.extend(
        sorted(abrupt_candidates, key=lambda item: item["score"], reverse=True)[:top_abrupt_count]
    )

    deduped: list[dict[str, object]] = []
    min_separation_sec = min_separation_ms / 1000.0
    for item in sorted(candidates, key=lambda candidate: candidate["score"], reverse=True):
        if any(abs(item["center_sec"] - existing["center_sec"]) < min_separation_sec for existing in deduped):
            continue
        deduped.append(item)
        if len(deduped) >= max_total_clips:
            break
    return sorted(deduped, key=lambda item: item["center_sec"])


def apply_manual_peak_review_to_candidates(
    peak_candidates: list[dict[str, object]],
    manual_peak_decisions: list[dict[str, object]],
) -> list[dict[str, object]]:
    decision_map = {
        str(item["clip_id"]): item for item in manual_peak_decisions
    }
    filtered: list[dict[str, object]] = []
    for index, candidate in enumerate(peak_candidates, start=1):
        preview_clip_id = f"peak_{index:03d}_{int(float(candidate['center_sec']) * 1000):010d}_{candidate['reason']}"
        decision = decision_map.get(preview_clip_id)
        candidate_copy = candidate.copy()
        candidate_copy["clip_id"] = preview_clip_id
        candidate_copy["review_action"] = decision["review_action"] if decision else "keep"
        candidate_copy["review_reason"] = decision["reason"] if decision else "normal_voice_or_unreviewed"
        if candidate_copy["review_action"] == "exclude":
            continue
        filtered.append(candidate_copy)
    return filtered


def build_peak_candidate(
    center_sec: float,
    reason: str,
    score: float,
    clip_pre_ms: int,
    clip_post_ms: int,
    total_duration_sec: float,
) -> dict[str, object]:
    start_sec = max(0.0, center_sec - clip_pre_ms / 1000.0)
    end_sec = min(total_duration_sec, center_sec + clip_post_ms / 1000.0)
    return {
        "center_sec": round(center_sec, 6),
        "start_sec": round(start_sec, 6),
        "end_sec": round(end_sec, 6),
        "reason": reason,
        "score": round(score, 6),
    }


def export_peak_clips(
    audio_path: Path,
    peak_candidates: list[dict[str, object]],
    output_dir: Path,
) -> list[dict[str, object]]:
    metadata = read_wav_metadata(audio_path)
    records: list[dict[str, object]] = []

    for index, candidate in enumerate(peak_candidates, start=1):
        samples = read_wav_segment_samples(
            audio_path=audio_path,
            start_sec=float(candidate["start_sec"]),
            end_sec=float(candidate["end_sec"]),
        )
        output_name = (
            f"{candidate['clip_id']}.wav"
        )
        output_path = output_dir / output_name
        write_wav_samples(output_path, samples, metadata)
        records.append(
            {
                "clip_id": candidate["clip_id"],
                "path": output_path.as_posix(),
                **candidate,
            }
        )
    return records


def read_wav_segment_samples(audio_path: Path, start_sec: float, end_sec: float) -> array:
    metadata = read_wav_metadata(audio_path)
    start_frame = max(0, int(start_sec * metadata.sample_rate))
    end_frame = max(start_frame, int(end_sec * metadata.sample_rate))
    frame_count = end_frame - start_frame

    with wave.open(str(audio_path), "rb") as wav_file:
        wav_file.setpos(start_frame)
        raw = wav_file.readframes(frame_count)
    return decode_samples(raw, metadata.sample_width_bytes)


def write_wav_samples(output_path: Path, samples: array, metadata) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(metadata.channels)
        wav_file.setsampwidth(metadata.sample_width_bytes)
        wav_file.setframerate(metadata.sample_rate)
        wav_file.writeframes(samples.tobytes())


def apply_noise_gate_to_samples(
    samples: array,
    sample_rate: int,
    sample_width_bytes: int,
    channels: int,
    gate_window_ms: int,
    gate_threshold_dbfs: float,
    peak_keep_threshold_dbfs: float,
) -> tuple[array, float]:
    frames_per_window = max(1, int(sample_rate * gate_window_ms / 1000))
    samples_per_window = frames_per_window * channels
    if samples_per_window <= 0 or not samples:
        return samples, 0.0

    gated = array(samples.typecode, samples)
    gated_windows = 0
    total_windows = 0

    for start in range(0, len(gated), samples_per_window):
        end = min(len(gated), start + samples_per_window)
        chunk = gated[start:end]
        if not chunk:
            continue
        total_windows += 1
        rms = compute_rms(chunk, sample_width_bytes)
        peak = compute_peak(chunk, sample_width_bytes)
        rms_dbfs = amplitude_to_dbfs(rms / max_possible_amplitude(sample_width_bytes))
        peak_dbfs = amplitude_to_dbfs(peak / max_possible_amplitude(sample_width_bytes))
        if rms_dbfs <= gate_threshold_dbfs and peak_dbfs <= peak_keep_threshold_dbfs:
            for idx in range(start, end):
                gated[idx] = 0
            gated_windows += 1

    ratio = gated_windows / total_windows if total_windows else 0.0
    return gated, ratio


def max_possible_amplitude(sample_width_bytes: int) -> float:
    if sample_width_bytes == 1:
        return 127.0
    bits = sample_width_bytes * 8
    return float((1 << (bits - 1)) - 1)


def percentile_value(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot compute percentile on empty values.")
    rank = (len(ordered) - 1) * percentile / 100.0
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def is_punctuation_like(char: str) -> bool:
    return unicodedata.category(char).startswith("P") or unicodedata.category(char).startswith("S")


def build_preprocess_summary(
    target_report: dict[str, object],
    source_report: dict[str, object],
) -> dict[str, object]:
    return {
        "target_round1_train_records": target_report["counts"]["round1_train_records"],
        "target_excluded_records": target_report["counts"]["excluded_records"],
        "source_segment_count": source_report["segment_count"],
        "source_peak_clip_count": source_report["peak_clip_count"],
        "source_noise_floor_dbfs": source_report["noise_floor_dbfs"],
        "source_content_threshold_dbfs": source_report["content_threshold_dbfs"],
    }


def write_markdown_summary(
    path: Path,
    summary: dict[str, object],
    target_report: dict[str, object],
    source_report: dict[str, object],
) -> None:
    lines = [
        "# 预处理摘要",
        "",
        "## 目标说话人数据",
        f"- round1 训练样本数: {target_report['counts']['round1_train_records']}",
        f"- round1 排除样本数: {target_report['counts']['excluded_records']}",
        f"- round1 总时长秒数: {target_report['round1_total_duration_sec']}",
        "",
        "## 源说话人数据",
        f"- 内容段数量: {source_report['segment_count']}",
        f"- 内容段总时长秒数: {source_report['segment_total_duration_sec']}",
        f"- 峰值试听片段数量: {source_report['peak_clip_count']}",
        f"- 估计底噪 dBFS: {source_report['noise_floor_dbfs']}",
        f"- 内容判定阈值 dBFS: {source_report['content_threshold_dbfs']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
