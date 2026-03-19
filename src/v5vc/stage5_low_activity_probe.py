from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import wave

import torch

from v5vc.offline_vocoder_training import compute_frame_activity_target
from v5vc.target_format_recovery import write_waveform_int16


DEFAULT_FRAME_LENGTH = 400
DEFAULT_HOP_LENGTH = 160
DEFAULT_MIN_LOW_ACTIVITY_FRAMES = 8
DEFAULT_TARGET_ACTIVITY_THRESHOLD = 0.35
DEFAULT_CANDIDATE_ACTIVITY_THRESHOLD = 0.45
DEFAULT_WINDOW_PADDING_SEC = 0.2
DEFAULT_MIN_AUDIT_WINDOW_SEC = 2.4
DEFAULT_MAX_AUDIT_WINDOW_SEC = 3.0


@dataclass(frozen=True)
class BundleRecord:
    record_id: str
    branch_label: str
    aligned_target_audio_path: Path
    source_manifest_path: Path
    source_payload: dict[str, object]


def analyze_stage5_low_activity_fragments(
    bundle_paths: list[Path],
    output_dir: Path,
    analysis_audio_sources: list[str],
    target_activity_threshold: float,
    candidate_activity_threshold: float,
    min_low_activity_frames: int,
    top_k_windows: int,
    window_padding_sec: float,
    min_audit_window_sec: float,
    max_audit_window_sec: float,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    clip_root_dir = output_dir / "clips"
    clip_root_dir.mkdir(parents=True, exist_ok=True)

    bundles = [load_stage5_bundle(path) for path in bundle_paths]
    if len(bundles) < 2:
        raise ValueError("At least two Stage5 bundles are required for low-activity comparison.")
    shared_record_ids = sorted(
        set(bundles[0]["records"].keys()).intersection(*(set(bundle["records"].keys()) for bundle in bundles[1:]))
    )
    if not shared_record_ids:
        raise ValueError("The provided Stage5 bundles do not share any record ids.")

    normalized_sources = [normalize_audio_source_name(item) for item in analysis_audio_sources]
    results_by_source: dict[str, dict[str, object]] = {}
    for audio_source in normalized_sources:
        source_result = analyze_audio_source(
            bundles=bundles,
            shared_record_ids=shared_record_ids,
            audio_source=audio_source,
            target_activity_threshold=float(target_activity_threshold),
            candidate_activity_threshold=float(candidate_activity_threshold),
            min_low_activity_frames=max(1, int(min_low_activity_frames)),
            top_k_windows=max(1, int(top_k_windows)),
            window_padding_sec=max(0.0, float(window_padding_sec)),
            min_audit_window_sec=max(0.0, float(min_audit_window_sec)),
            max_audit_window_sec=max(0.0, float(max_audit_window_sec)),
            clip_root_dir=clip_root_dir,
        )
        results_by_source[audio_source] = source_result

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_low_activity_fragmentation_probe_v1",
        "bundle_manifests": [bundle["manifest_path"].as_posix() for bundle in bundles],
        "bundle_branch_labels": [bundle["branch_label"] for bundle in bundles],
        "record_count": len(shared_record_ids),
        "target_activity_threshold": float(target_activity_threshold),
        "candidate_activity_threshold": float(candidate_activity_threshold),
        "min_low_activity_frames": max(1, int(min_low_activity_frames)),
        "top_k_windows": max(1, int(top_k_windows)),
        "window_padding_sec": max(0.0, float(window_padding_sec)),
        "min_audit_window_sec": max(0.0, float(min_audit_window_sec)),
        "max_audit_window_sec": max(0.0, float(max_audit_window_sec)),
        "analysis_sources": results_by_source,
        "notes": [
            "Low-activity segments are derived from aligned_target.wav via the same compute_frame_activity_target(...) energy bridge used in Stage5 activity-gate supervision.",
            "Fragmentation score is defined as extra_bursts_inside_target_low_activity plus mean absolute frame-activity toggle inside the same segment.",
            "listening uses listening_audio_path from the Stage5 bundle, while decoded uses decoded_audio_path for raw diagnostic follow-up.",
            "Exported listening clips preserve at least window_padding_sec context on both sides and expand to min_audit_window_sec when the raw suspicious segment is too short for human judgment.",
        ],
    }
    (output_dir / "stage5_low_activity_fragmentation_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "stage5_low_activity_fragmentation_probe.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    build_audio_audit_bundle_manifests(summary=summary, output_dir=output_dir)


def load_stage5_bundle(path: Path) -> dict[str, object]:
    manifest_path = resolve_stage5_bundle_manifest(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    branch_label = infer_branch_label(payload=payload, manifest_path=manifest_path)
    records: dict[str, BundleRecord] = {}
    for record_payload in payload.get("records", []):
        record_id = str(record_payload.get("record_id", "")).strip()
        aligned_target_path = resolve_record_audio_path(record_payload, "aligned_target")
        if not record_id or aligned_target_path is None:
            continue
        records[record_id] = BundleRecord(
            record_id=record_id,
            branch_label=branch_label,
            aligned_target_audio_path=aligned_target_path,
            source_manifest_path=manifest_path,
            source_payload=dict(record_payload),
        )
    return {
        "manifest_path": manifest_path,
        "branch_label": branch_label,
        "records": records,
    }


def resolve_stage5_bundle_manifest(path: Path) -> Path:
    candidate = path.resolve()
    if candidate.is_dir():
        for filename in ("nores_vocoder_audio_export.json", "proxy_audio_export.json"):
            manifest_path = candidate / filename
            if manifest_path.exists():
                return manifest_path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Unable to resolve Stage5 bundle manifest from: {path}")


def infer_branch_label(payload: dict[str, object], manifest_path: Path) -> str:
    branch_label = payload.get("branch_label")
    if isinstance(branch_label, str) and branch_label.strip():
        return branch_label.strip()
    return manifest_path.parent.name


def normalize_audio_source_name(audio_source: str) -> str:
    normalized = str(audio_source).strip().lower()
    if normalized not in {"listening", "decoded", "decoded_pitch_matched", "audit_proxy"}:
        raise ValueError(f"Unsupported analysis_audio_source: {audio_source}")
    return normalized


def resolve_record_audio_path(record_payload: dict[str, object], audio_source: str) -> Path | None:
    source_to_keys = {
        "aligned_target": ("aligned_target_audio_path", "input_audio_path"),
        "listening": ("listening_audio_path", "proxy_audio_path"),
        "decoded": ("decoded_audio_path",),
        "decoded_pitch_matched": ("decoded_pitch_matched_audio_path",),
        "audit_proxy": ("audit_proxy_audio_path", "proxy_audio_path"),
    }
    for key in source_to_keys[audio_source]:
        raw_path = record_payload.get(key)
        if isinstance(raw_path, str) and raw_path.strip():
            resolved = Path(raw_path).resolve()
            if resolved.exists():
                return resolved
    return None


def analyze_audio_source(
    bundles: list[dict[str, object]],
    shared_record_ids: list[str],
    audio_source: str,
    target_activity_threshold: float,
    candidate_activity_threshold: float,
    min_low_activity_frames: int,
    top_k_windows: int,
    window_padding_sec: float,
    min_audit_window_sec: float,
    max_audit_window_sec: float,
    clip_root_dir: Path,
) -> dict[str, object]:
    branch_aggregates: dict[str, dict[str, float]] = {}
    record_results: list[dict[str, object]] = []
    suspicious_windows: list[dict[str, object]] = []

    for record_id in shared_record_ids:
        bundle_records = [bundle["records"][record_id] for bundle in bundles]
        target_waveform, sample_rate = read_wav_mono(bundle_records[0].aligned_target_audio_path)
        target_activity = compute_frame_activity_target(
            aligned_waveform=target_waveform,
            frame_length=DEFAULT_FRAME_LENGTH,
            hop_length=DEFAULT_HOP_LENGTH,
        ).squeeze(-1)
        low_activity_segments = identify_low_activity_segments(
            frame_activity=target_activity,
            threshold=float(target_activity_threshold),
            min_frames=max(1, int(min_low_activity_frames)),
            sample_rate=sample_rate,
            frame_length=DEFAULT_FRAME_LENGTH,
            hop_length=DEFAULT_HOP_LENGTH,
        )
        if not low_activity_segments:
            continue

        branch_results: list[dict[str, object]] = []
        for record in bundle_records:
            candidate_path = resolve_record_audio_path(record.source_payload, audio_source)
            if candidate_path is None:
                continue
            candidate_waveform, candidate_sr = read_wav_mono(candidate_path)
            if candidate_sr != sample_rate:
                raise ValueError(
                    f"Sample-rate mismatch for {record_id}: target={sample_rate}, {record.branch_label}={candidate_sr}"
                )
            candidate_waveform = slice_or_pad_waveform(candidate_waveform, target_waveform.shape[0])
            candidate_activity = compute_frame_activity_target(
                aligned_waveform=candidate_waveform,
                frame_length=DEFAULT_FRAME_LENGTH,
                hop_length=DEFAULT_HOP_LENGTH,
            ).squeeze(-1)
            segment_metrics = [
                compute_segment_metrics(
                    segment=segment,
                    candidate_activity=candidate_activity,
                    candidate_waveform=candidate_waveform,
                    candidate_activity_threshold=float(candidate_activity_threshold),
                    sample_rate=sample_rate,
                )
                for segment in low_activity_segments
            ]
            aggregate = summarize_branch_segment_metrics(segment_metrics)
            branch_result = {
                "branch_label": record.branch_label,
                "candidate_audio_path": candidate_path.as_posix(),
                "aggregate": aggregate,
                "segment_metrics": segment_metrics,
            }
            branch_results.append(branch_result)
            branch_aggregate = branch_aggregates.setdefault(
                record.branch_label,
                {
                    "record_count": 0.0,
                    "segment_count": 0.0,
                    "fragmentation_score_sum": 0.0,
                    "extra_bursts_sum": 0.0,
                    "activity_toggle_sum": 0.0,
                    "active_fraction_sum": 0.0,
                    "delta_peak_sum": 0.0,
                },
            )
            branch_aggregate["record_count"] += 1.0
            branch_aggregate["segment_count"] += float(aggregate["segment_count"])
            branch_aggregate["fragmentation_score_sum"] += float(aggregate["mean_fragmentation_score"])
            branch_aggregate["extra_bursts_sum"] += float(aggregate["mean_extra_bursts"])
            branch_aggregate["activity_toggle_sum"] += float(aggregate["mean_activity_toggle"])
            branch_aggregate["active_fraction_sum"] += float(aggregate["mean_active_fraction"])
            branch_aggregate["delta_peak_sum"] += float(aggregate["mean_sample_delta_peak"])

        if len(branch_results) < 2:
            continue
        record_result = build_record_result(
            record_id=record_id,
            sample_rate=sample_rate,
            low_activity_segments=low_activity_segments,
            branch_results=branch_results,
            audio_source=audio_source,
            target_waveform=target_waveform,
            target_audio_path=bundle_records[0].aligned_target_audio_path,
            clip_root_dir=clip_root_dir,
            top_k_windows=top_k_windows,
            window_padding_sec=window_padding_sec,
            min_audit_window_sec=min_audit_window_sec,
            max_audit_window_sec=max_audit_window_sec,
        )
        record_results.append(record_result)
        suspicious_windows.extend(record_result["top_windows"])

    branch_summaries = summarize_branch_aggregates(branch_aggregates)
    suspicious_windows.sort(
        key=lambda item: (
            float(item["delta_fragmentation_score"]),
            float(item["worst_branch"]["sample_delta_peak"]),
        ),
        reverse=True,
    )
    top_windows = suspicious_windows[: max(1, int(top_k_windows))]
    return {
        "record_count": len(record_results),
        "branch_aggregates": branch_summaries,
        "records": record_results,
        "top_windows": top_windows,
    }


def identify_low_activity_segments(
    frame_activity: torch.Tensor,
    threshold: float,
    min_frames: int,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> list[dict[str, object]]:
    mask = frame_activity <= float(threshold)
    segments: list[dict[str, object]] = []
    start_index: int | None = None
    for frame_index, is_low in enumerate(mask.tolist() + [False]):
        if is_low and start_index is None:
            start_index = frame_index
            continue
        if is_low:
            continue
        if start_index is None:
            continue
        if frame_index - start_index >= max(1, int(min_frames)):
            start_frame_index = int(start_index)
            end_frame_index = int(frame_index)
            start_sample = int(start_frame_index * hop_length)
            end_sample = int((end_frame_index - 1) * hop_length + frame_length)
            start_sec = start_sample / float(sample_rate)
            end_sec = end_sample / float(sample_rate)
            segments.append(
                {
                    "segment_index": len(segments),
                    "start_frame_index": start_frame_index,
                    "end_frame_index": end_frame_index,
                    "start_sample": start_sample,
                    "end_sample": end_sample,
                    "start_sec": round(start_sec, 6),
                    "end_sec": round(end_sec, 6),
                    "duration_sec": round(max(0.0, end_sec - start_sec), 6),
                    "target_activity_mean": round(
                        float(frame_activity[start_frame_index:end_frame_index].mean().item()),
                        6,
                    ),
                }
            )
        start_index = None
    return segments


def compute_segment_metrics(
    segment: dict[str, object],
    candidate_activity: torch.Tensor,
    candidate_waveform: torch.Tensor,
    candidate_activity_threshold: float,
    sample_rate: int,
) -> dict[str, object]:
    start_frame_index = int(segment["start_frame_index"])
    end_frame_index = int(segment["end_frame_index"])
    start_sample = int(segment["start_sample"])
    end_sample = int(segment["end_sample"])
    activity_slice = candidate_activity[start_frame_index:end_frame_index]
    waveform_slice = candidate_waveform[start_sample:end_sample]
    active_mask = activity_slice >= float(candidate_activity_threshold)
    burst_count = count_bursts(active_mask)
    extra_bursts = max(0, burst_count - 1)
    activity_toggle = 0.0
    if activity_slice.numel() > 1:
        activity_toggle = float(torch.abs(activity_slice[1:] - activity_slice[:-1]).mean().item())
    sample_delta_abs_mean = 0.0
    sample_delta_peak = 0.0
    if waveform_slice.numel() > 1:
        delta = torch.abs(waveform_slice[1:] - waveform_slice[:-1])
        sample_delta_abs_mean = float(delta.mean().item())
        sample_delta_peak = float(delta.max().item())
    fragmentation_score = float(extra_bursts) + float(activity_toggle)
    return {
        "segment_index": int(segment["segment_index"]),
        "start_frame_index": start_frame_index,
        "end_frame_index": end_frame_index,
        "start_sample": start_sample,
        "end_sample": end_sample,
        "start_sec": float(segment["start_sec"]),
        "end_sec": float(segment["end_sec"]),
        "duration_sec": float(segment["duration_sec"]),
        "target_activity_mean": float(segment["target_activity_mean"]),
        "burst_count": int(burst_count),
        "extra_bursts": int(extra_bursts),
        "activity_toggle_mean": round(activity_toggle, 6),
        "activity_mean": round(float(activity_slice.mean().item()) if activity_slice.numel() > 0 else 0.0, 6),
        "activity_peak": round(float(activity_slice.max().item()) if activity_slice.numel() > 0 else 0.0, 6),
        "active_fraction": round(float(active_mask.to(torch.float32).mean().item()) if active_mask.numel() > 0 else 0.0, 6),
        "sample_delta_abs_mean": round(sample_delta_abs_mean, 6),
        "sample_delta_peak": round(sample_delta_peak, 6),
        "fragmentation_score": round(fragmentation_score, 6),
        "duration_frames": int(end_frame_index - start_frame_index),
        "duration_samples": int(end_sample - start_sample),
        "sample_rate": int(sample_rate),
    }


def count_bursts(active_mask: torch.Tensor) -> int:
    burst_count = 0
    previous = False
    for is_active in active_mask.tolist():
        current = bool(is_active)
        if current and not previous:
            burst_count += 1
        previous = current
    return burst_count


def summarize_branch_segment_metrics(segment_metrics: list[dict[str, object]]) -> dict[str, object]:
    if not segment_metrics:
        return {
            "segment_count": 0,
            "mean_fragmentation_score": 0.0,
            "mean_extra_bursts": 0.0,
            "mean_activity_toggle": 0.0,
            "mean_active_fraction": 0.0,
            "mean_sample_delta_peak": 0.0,
        }
    segment_count = float(len(segment_metrics))
    return {
        "segment_count": int(segment_count),
        "mean_fragmentation_score": round(
            sum(float(item["fragmentation_score"]) for item in segment_metrics) / segment_count,
            6,
        ),
        "mean_extra_bursts": round(
            sum(float(item["extra_bursts"]) for item in segment_metrics) / segment_count,
            6,
        ),
        "mean_activity_toggle": round(
            sum(float(item["activity_toggle_mean"]) for item in segment_metrics) / segment_count,
            6,
        ),
        "mean_active_fraction": round(
            sum(float(item["active_fraction"]) for item in segment_metrics) / segment_count,
            6,
        ),
        "mean_sample_delta_peak": round(
            sum(float(item["sample_delta_peak"]) for item in segment_metrics) / segment_count,
            6,
        ),
    }


def summarize_branch_aggregates(branch_aggregates: dict[str, dict[str, float]]) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for branch_label, aggregate in sorted(branch_aggregates.items()):
        record_count = max(1.0, float(aggregate["record_count"]))
        summary[branch_label] = {
            "record_count": int(aggregate["record_count"]),
            "mean_segment_count": round(float(aggregate["segment_count"]) / record_count, 6),
            "mean_fragmentation_score": round(float(aggregate["fragmentation_score_sum"]) / record_count, 6),
            "mean_extra_bursts": round(float(aggregate["extra_bursts_sum"]) / record_count, 6),
            "mean_activity_toggle": round(float(aggregate["activity_toggle_sum"]) / record_count, 6),
            "mean_active_fraction": round(float(aggregate["active_fraction_sum"]) / record_count, 6),
            "mean_sample_delta_peak": round(float(aggregate["delta_peak_sum"]) / record_count, 6),
        }
    return summary


def build_record_result(
    record_id: str,
    sample_rate: int,
    low_activity_segments: list[dict[str, object]],
    branch_results: list[dict[str, object]],
    audio_source: str,
    target_waveform: torch.Tensor,
    target_audio_path: Path,
    clip_root_dir: Path,
    top_k_windows: int,
    window_padding_sec: float,
    min_audit_window_sec: float,
    max_audit_window_sec: float,
) -> dict[str, object]:
    top_windows: list[dict[str, object]] = []
    for segment_index, segment in enumerate(low_activity_segments):
        ranked = []
        for branch_result in branch_results:
            metric = branch_result["segment_metrics"][segment_index]
            ranked.append(
                {
                    "branch_label": branch_result["branch_label"],
                    "candidate_audio_path": branch_result["candidate_audio_path"],
                    **metric,
                }
            )
        ranked.sort(
            key=lambda item: (
                float(item["fragmentation_score"]),
                float(item["sample_delta_peak"]),
                float(item["active_fraction"]),
            ),
            reverse=True,
        )
        worst_branch = ranked[0]
        best_branch = ranked[-1]
        delta_fragmentation_score = round(
            float(worst_branch["fragmentation_score"]) - float(best_branch["fragmentation_score"]),
            6,
        )
        delta_extra_bursts = int(worst_branch["extra_bursts"]) - int(best_branch["extra_bursts"])
        if delta_fragmentation_score <= 0.0 and delta_extra_bursts <= 0:
            continue
        clip_dir, audit_window = export_segment_clips(
            clip_root_dir=clip_root_dir,
            audio_source=audio_source,
            record_id=record_id,
            segment=segment,
            target_waveform=target_waveform,
            target_audio_path=target_audio_path,
            branch_ranked_metrics=ranked,
            sample_rate=sample_rate,
            padding_sec=window_padding_sec,
            min_audit_window_sec=min_audit_window_sec,
            max_audit_window_sec=max_audit_window_sec,
        )
        top_windows.append(
            {
                "record_id": record_id,
                "segment_index": int(segment["segment_index"]),
                "start_sec": float(segment["start_sec"]),
                "end_sec": float(segment["end_sec"]),
                "duration_sec": float(segment["duration_sec"]),
                "target_activity_mean": float(segment["target_activity_mean"]),
                "delta_fragmentation_score": delta_fragmentation_score,
                "delta_extra_bursts": delta_extra_bursts,
                "worst_branch": worst_branch,
                "best_branch": best_branch,
                "clip_dir": clip_dir.as_posix(),
                "clip_start_sec": float(audit_window["clip_start_sec"]),
                "clip_end_sec": float(audit_window["clip_end_sec"]),
                "clip_duration_sec": float(audit_window["clip_duration_sec"]),
                "ranked_branches": ranked,
            }
        )
    top_windows.sort(
        key=lambda item: (
            float(item["delta_fragmentation_score"]),
            float(item["worst_branch"]["sample_delta_peak"]),
        ),
        reverse=True,
    )
    return {
        "record_id": record_id,
        "sample_rate": int(sample_rate),
        "low_activity_segment_count": len(low_activity_segments),
        "branch_results": branch_results,
        "top_windows": top_windows[: max(1, int(top_k_windows))],
    }


def export_segment_clips(
    clip_root_dir: Path,
    audio_source: str,
    record_id: str,
    segment: dict[str, object],
    target_waveform: torch.Tensor,
    target_audio_path: Path,
    branch_ranked_metrics: list[dict[str, object]],
    sample_rate: int,
    padding_sec: float,
    min_audit_window_sec: float,
    max_audit_window_sec: float,
) -> tuple[Path, dict[str, object]]:
    record_dir = clip_root_dir / sanitize_filename(audio_source) / sanitize_filename(record_id)
    record_dir.mkdir(parents=True, exist_ok=True)
    clip_dir = record_dir / (
        f"segment_{int(segment['segment_index']):02d}_"
        f"{int(round(float(segment['start_sec']) * 1000.0)):06d}_"
        f"{int(round(float(segment['end_sec']) * 1000.0)):06d}ms"
    )
    clip_dir.mkdir(parents=True, exist_ok=True)
    audit_window = compute_audit_window_bounds(
        segment=segment,
        total_samples=int(target_waveform.shape[0]),
        sample_rate=sample_rate,
        padding_sec=padding_sec,
        min_audit_window_sec=min_audit_window_sec,
        max_audit_window_sec=max_audit_window_sec,
    )
    clip_start = int(audit_window["clip_start_sample"])
    clip_end = int(audit_window["clip_end_sample"])
    write_waveform_int16(
        clip_dir / "aligned_target.wav",
        target_waveform[clip_start:clip_end],
        sample_rate=sample_rate,
    )
    metadata = {
        "record_id": record_id,
        "audio_source": audio_source,
        "segment_index": int(segment["segment_index"]),
        "start_sec": float(segment["start_sec"]),
        "end_sec": float(segment["end_sec"]),
        "clip_start_sec": float(audit_window["clip_start_sec"]),
        "clip_end_sec": float(audit_window["clip_end_sec"]),
        "clip_duration_sec": float(audit_window["clip_duration_sec"]),
        "padding_sec": float(padding_sec),
        "min_audit_window_sec": float(min_audit_window_sec),
        "max_audit_window_sec": float(max_audit_window_sec),
        "target_audio_path": target_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "branches": [],
    }
    for branch_metric in branch_ranked_metrics:
        candidate_waveform, _ = read_wav_mono(Path(branch_metric["candidate_audio_path"]))
        candidate_waveform = slice_or_pad_waveform(candidate_waveform, int(target_waveform.shape[0]))
        branch_output_path = clip_dir / f"{sanitize_filename(branch_metric['branch_label'])}.wav"
        write_waveform_int16(
            branch_output_path,
            candidate_waveform[clip_start:clip_end],
            sample_rate=sample_rate,
        )
        metadata["branches"].append(
            {
                "branch_label": branch_metric["branch_label"],
                "candidate_audio_path": branch_metric["candidate_audio_path"],
                "clip_path": branch_output_path.as_posix(),
                "fragmentation_score": branch_metric["fragmentation_score"],
                "extra_bursts": branch_metric["extra_bursts"],
                "sample_delta_peak": branch_metric["sample_delta_peak"],
            }
        )
    (clip_dir / "segment_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return clip_dir, audit_window


def compute_audit_window_bounds(
    segment: dict[str, object],
    total_samples: int,
    sample_rate: int,
    padding_sec: float,
    min_audit_window_sec: float,
    max_audit_window_sec: float,
) -> dict[str, object]:
    clip_start = max(0, int(segment["start_sample"]) - int(round(float(padding_sec) * float(sample_rate))))
    clip_end = min(total_samples, int(segment["end_sample"]) + int(round(float(padding_sec) * float(sample_rate))))
    required_samples = max(0, clip_end - clip_start)
    min_window_samples = max(0, int(round(float(min_audit_window_sec) * float(sample_rate))))
    max_window_samples = max(0, int(round(float(max_audit_window_sec) * float(sample_rate))))
    desired_samples = max(required_samples, min_window_samples)
    if max_window_samples > 0 and required_samples <= max_window_samples:
        desired_samples = min(desired_samples, max_window_samples)
    extra_samples = max(0, desired_samples - required_samples)
    extra_left = extra_samples // 2
    extra_right = extra_samples - extra_left
    clip_start = max(0, clip_start - extra_left)
    clip_end = min(total_samples, clip_end + extra_right)
    current_samples = max(0, clip_end - clip_start)
    if current_samples < desired_samples:
        shortfall = desired_samples - current_samples
        left_room = clip_start
        shift_left = min(left_room, shortfall)
        clip_start -= shift_left
        shortfall -= shift_left
        right_room = max(0, total_samples - clip_end)
        shift_right = min(right_room, shortfall)
        clip_end += shift_right
    clip_duration_sec = max(0.0, float(clip_end - clip_start) / float(sample_rate))
    return {
        "clip_start_sample": int(clip_start),
        "clip_end_sample": int(clip_end),
        "clip_start_sec": round(float(clip_start) / float(sample_rate), 6),
        "clip_end_sec": round(float(clip_end) / float(sample_rate), 6),
        "clip_duration_sec": round(clip_duration_sec, 6),
    }


def read_wav_mono(path: Path) -> tuple[torch.Tensor, int]:
    with wave.open(str(path), "rb") as reader:
        frame_count = int(reader.getnframes())
        sample_rate = int(reader.getframerate())
        sample_width = int(reader.getsampwidth())
        channel_count = int(reader.getnchannels())
        raw = bytes(reader.readframes(frame_count))
    if sample_width == 1:
        waveform = torch.tensor(list(raw), dtype=torch.float32)
        if channel_count > 1:
            waveform = waveform.view(-1, channel_count).mean(dim=1)
        waveform = (waveform - 128.0) / 128.0
        return waveform.contiguous(), sample_rate
    if sample_width == 2:
        waveform = torch.frombuffer(bytearray(raw), dtype=torch.int16).clone().to(torch.float32)
        if channel_count > 1:
            waveform = waveform.view(-1, channel_count).mean(dim=1)
        waveform = waveform / 32768.0
        return waveform.contiguous(), sample_rate
    if sample_width == 4:
        waveform = torch.frombuffer(bytearray(raw), dtype=torch.int32).clone().to(torch.float32)
        if channel_count > 1:
            waveform = waveform.view(-1, channel_count).mean(dim=1)
        waveform = waveform / 2147483648.0
        return waveform.contiguous(), sample_rate
    raise ValueError(f"Unsupported wav sample width: {sample_width}")


def slice_or_pad_waveform(waveform: torch.Tensor, target_length: int) -> torch.Tensor:
    if int(waveform.shape[0]) == int(target_length):
        return waveform
    if int(waveform.shape[0]) > int(target_length):
        return waveform[:target_length]
    padded = waveform.new_zeros((int(target_length),))
    padded[: int(waveform.shape[0])] = waveform
    return padded


def sanitize_filename(value: str) -> str:
    sanitized = [
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in str(value)
    ]
    return "".join(sanitized).strip("_") or "item"


def build_audio_audit_bundle_manifests(summary: dict[str, object], output_dir: Path) -> None:
    bundle_root_dir = output_dir / "audio_audit_bundles"
    bundle_root_dir.mkdir(parents=True, exist_ok=True)
    generated_at = str(summary.get("generated_at", ""))
    min_human_audit_window_sec = min(2.0, max(0.0, float(summary.get("min_audit_window_sec", 0.0))))

    for source_name, source_payload in dict(summary.get("analysis_sources", {})).items():
        top_windows = list(source_payload.get("top_windows", []))
        eligible_windows = [
            window
            for window in top_windows
            if float(window.get("clip_duration_sec", 0.0)) >= float(min_human_audit_window_sec)
        ]
        if eligible_windows:
            top_windows = eligible_windows
        if not top_windows:
            continue

        manifests_by_branch: dict[str, dict[str, object]] = {}
        for window in top_windows:
            clip_dir = Path(str(window["clip_dir"])).resolve()
            metadata_path = clip_dir / "segment_metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            aligned_target_clip_path = clip_dir / "aligned_target.wav"
            if not aligned_target_clip_path.exists():
                continue

            segment_record_id = (
                f"{metadata['record_id']}::"
                f"{source_name}::"
                f"segment{int(window['segment_index']):02d}::"
                f"clip{int(round(float(metadata.get('clip_start_sec', window['start_sec'])) * 1000.0)):06d}_"
                f"{int(round(float(metadata.get('clip_end_sec', window['end_sec'])) * 1000.0)):06d}ms"
            )
            for branch_payload in metadata.get("branches", []):
                branch_label = str(branch_payload.get("branch_label", "")).strip()
                clip_path = Path(str(branch_payload.get("clip_path", ""))).resolve()
                if not branch_label or not clip_path.exists():
                    continue
                manifest = manifests_by_branch.setdefault(
                    branch_label,
                    {
                        "generated_at": generated_at,
                        "bundle_type": "stage5_low_activity_fragmentation_audio_audit_bundle_v1",
                        "branch_label": f"{source_name}:{branch_label}",
                        "analysis_audio_source": source_name,
                        "minimum_human_audit_window_sec": float(min_human_audit_window_sec),
                        "source_probe_summary_path": (output_dir / "stage5_low_activity_fragmentation_probe.json").as_posix(),
                        "records": [],
                    },
                )
                manifest["records"].append(
                    {
                        "record_id": segment_record_id,
                        "input_audio_path": aligned_target_clip_path.as_posix(),
                        "aligned_target_audio_path": aligned_target_clip_path.as_posix(),
                        "listening_audio_source": source_name,
                        "listening_audio_path": clip_path.as_posix(),
                        "proxy_audio_path": clip_path.as_posix(),
                        "audio_path": str(metadata.get("target_audio_path", "")),
                        "sample_rate": int(metadata.get("sample_rate", 44100)),
                        "source_record_id": metadata.get("record_id"),
                        "segment_index": int(metadata.get("segment_index", window["segment_index"])),
                        "segment_start_sec": float(metadata.get("start_sec", window["start_sec"])),
                        "segment_end_sec": float(metadata.get("end_sec", window["end_sec"])),
                        "clip_start_sec": float(metadata.get("clip_start_sec", window.get("clip_start_sec", window["start_sec"]))),
                        "clip_end_sec": float(metadata.get("clip_end_sec", window.get("clip_end_sec", window["end_sec"]))),
                        "clip_duration_sec": float(
                            metadata.get(
                                "clip_duration_sec",
                                window.get("clip_duration_sec", float(window["end_sec"]) - float(window["start_sec"])),
                            )
                        ),
                        "fragmentation_probe": {
                            "delta_fragmentation_score": float(window["delta_fragmentation_score"]),
                            "delta_extra_bursts": int(window["delta_extra_bursts"]),
                            "worst_branch": window["worst_branch"]["branch_label"],
                            "best_branch": window["best_branch"]["branch_label"],
                            "clip_dir": clip_dir.as_posix(),
                        },
                    }
                )

        for branch_label, manifest_payload in manifests_by_branch.items():
            records = sorted(
                manifest_payload["records"],
                key=lambda item: (
                    -float(item["fragmentation_probe"]["delta_fragmentation_score"]),
                    item["record_id"],
                ),
            )
            manifest_payload["records"] = records
            branch_dir = bundle_root_dir / sanitize_filename(source_name) / sanitize_filename(branch_label)
            branch_dir.mkdir(parents=True, exist_ok=True)
            (branch_dir / "proxy_audio_export.json").write_text(
                json.dumps(manifest_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Low-Activity Fragmentation Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- record_count: {summary['record_count']}",
        f"- bundle_branch_labels: {summary['bundle_branch_labels']}",
        f"- target_activity_threshold: {summary['target_activity_threshold']}",
        f"- candidate_activity_threshold: {summary['candidate_activity_threshold']}",
        f"- min_low_activity_frames: {summary['min_low_activity_frames']}",
        f"- top_k_windows: {summary['top_k_windows']}",
        f"- window_padding_sec: {summary['window_padding_sec']}",
        f"- min_audit_window_sec: {summary['min_audit_window_sec']}",
        f"- max_audit_window_sec: {summary['max_audit_window_sec']}",
        "",
    ]
    for source_name, source_payload in summary["analysis_sources"].items():
        lines.append(f"## Source: {source_name}")
        lines.append("")
        lines.append("### Audio Audit Bundles")
        lines.append(
            f"- bundle_root={Path('audio_audit_bundles') / sanitize_filename(source_name)}"
        )
        lines.append("")
        lines.append("### Branch Aggregates")
        for branch_label, aggregate in source_payload["branch_aggregates"].items():
            lines.append(
                f"- {branch_label}: "
                f"mean_fragmentation_score={aggregate['mean_fragmentation_score']} "
                f"mean_extra_bursts={aggregate['mean_extra_bursts']} "
                f"mean_activity_toggle={aggregate['mean_activity_toggle']} "
                f"mean_active_fraction={aggregate['mean_active_fraction']} "
                f"mean_sample_delta_peak={aggregate['mean_sample_delta_peak']}"
            )
        lines.append("")
        lines.append("### Top Windows")
        for window in source_payload["top_windows"]:
            lines.append(
                f"- record_id={window['record_id']} "
                f"segment_index={window['segment_index']} "
                f"start_sec={window['start_sec']} "
                f"end_sec={window['end_sec']} "
                f"clip_start_sec={window.get('clip_start_sec', window['start_sec'])} "
                f"clip_end_sec={window.get('clip_end_sec', window['end_sec'])} "
                f"clip_duration_sec={window.get('clip_duration_sec', window['duration_sec'])} "
                f"delta_fragmentation_score={window['delta_fragmentation_score']} "
                f"worst_branch={window['worst_branch']['branch_label']} "
                f"best_branch={window['best_branch']['branch_label']} "
                f"clip_dir={window['clip_dir']}"
            )
        lines.append("")
    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
