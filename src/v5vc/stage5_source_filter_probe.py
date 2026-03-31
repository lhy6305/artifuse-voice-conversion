from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import assess_stage5_decoded_buzz_reject
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    frame_waveform_sequence,
    load_training_package_payload,
)
from v5vc.stage5_low_activity_probe import read_wav_mono, slice_or_pad_waveform
from v5vc.stage5_waveform_decoder_structure_probe import (
    build_voicing_conditioning_bundle,
    save_linear_spectrogram_png,
    summarize_masked_frame_spectral_statistics,
)
from v5vc.stage5_speech_emergence_probe import summarize_frame_sequence_metrics


def analyze_stage5_nores_source_filter_review(
    *,
    output_dir: Path,
    review_bundle_path: Path,
    dataset_index_paths: list[Path],
    peak_count: int,
    peak_min_separation_hz: float,
    high_band_hz: float,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    review_bundle_path = review_bundle_path.resolve()
    dataset_index_paths = [path.resolve() for path in dataset_index_paths]

    review_bundle = json.loads(review_bundle_path.read_text(encoding="utf-8"))
    records = list(review_bundle.get("records", []))
    if not records:
        raise ValueError("Review bundle contains no records.")
    package_map = build_training_package_map(dataset_index_paths)

    per_record_rows: list[dict[str, object]] = []
    for review_record in records:
        record_id = str(review_record.get("record_id", "")).strip()
        if not record_id:
            continue
        package_entry = package_map.get(record_id)
        if package_entry is None:
            raise KeyError(f"Unable to resolve training package for review record: {record_id}")
        package_path = Path(str(package_entry["training_package_path"])).resolve()
        payload = load_training_package_payload(package_path)
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)

        decoded_waveform, decoded_sample_rate = read_wav_mono(Path(str(review_record["decoded_audio_path"])).resolve())
        aligned_waveform, aligned_sample_rate = read_wav_mono(
            Path(str(review_record["aligned_target_audio_path"])).resolve()
        )
        if int(decoded_sample_rate) != int(aligned_sample_rate):
            raise ValueError(
                f"Sample-rate mismatch for {record_id}: decoded={decoded_sample_rate} aligned={aligned_sample_rate}"
            )
        sample_rate = int(decoded_sample_rate)
        target_length = min(int(decoded_waveform.shape[0]), int(aligned_waveform.shape[0]))
        decoded_waveform = slice_or_pad_waveform(decoded_waveform, target_length)
        aligned_waveform = slice_or_pad_waveform(aligned_waveform, target_length)

        decoded_frames = frame_waveform_sequence(
            waveform=decoded_waveform,
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
        )
        aligned_frames = frame_waveform_sequence(
            waveform=aligned_waveform,
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
        )
        common_frame_count = min(int(decoded_frames.shape[0]), int(aligned_frames.shape[0]))
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for review record: {record_id}")
        decoded_frames = decoded_frames[:common_frame_count]
        aligned_frames = aligned_frames[:common_frame_count]

        conditioning = build_voicing_conditioning_bundle(
            frame_count=common_frame_count,
            vuv_target=batch.get("periodic_gate_target", batch.get("vuv_target")),
            voiced_proxy_target=batch.get("voiced_proxy_target"),
            aper_target=batch.get("aper_target"),
            aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
            energy_log_rms_norm_target=batch.get("energy_log_rms_norm_target"),
            energy_control_target=batch.get("energy_control_target"),
        )
        if conditioning is None:
            raise ValueError(f"Unable to derive voiced/unvoiced conditioning for review record: {record_id}")
        resolved_voicing_source = (
            "periodic_gate_target"
            if batch.get("periodic_gate_target") is not None
            else str(conditioning.get("voicing_source", "missing"))
        )

        voiced_mask = conditioning["voiced_mask"]
        unvoiced_mask = conditioning["unvoiced_mask"]
        decoded_voiced_stats = summarize_masked_frame_spectral_statistics(
            analysis_frames=decoded_frames,
            mask=voiced_mask,
            sample_rate=sample_rate,
            high_band_hz=float(high_band_hz),
        )
        decoded_unvoiced_stats = summarize_masked_frame_spectral_statistics(
            analysis_frames=decoded_frames,
            mask=unvoiced_mask,
            sample_rate=sample_rate,
            high_band_hz=float(high_band_hz),
        )
        aligned_voiced_stats = summarize_masked_frame_spectral_statistics(
            analysis_frames=aligned_frames,
            mask=voiced_mask,
            sample_rate=sample_rate,
            high_band_hz=float(high_band_hz),
        )
        aligned_unvoiced_stats = summarize_masked_frame_spectral_statistics(
            analysis_frames=aligned_frames,
            mask=unvoiced_mask,
            sample_rate=sample_rate,
            high_band_hz=float(high_band_hz),
        )

        vuv_contrast_summary = build_vuv_contrast_summary(
            conditioning=conditioning,
            decoded_voiced_stats=decoded_voiced_stats,
            decoded_unvoiced_stats=decoded_unvoiced_stats,
            aligned_voiced_stats=aligned_voiced_stats,
            aligned_unvoiced_stats=aligned_unvoiced_stats,
        )
        peak_spacing_summary = {
            "decoded": estimate_peak_spacing_summary(
                analysis_frames=decoded_frames,
                mask=voiced_mask,
                sample_rate=sample_rate,
                peak_count=int(peak_count),
                peak_min_separation_hz=float(peak_min_separation_hz),
            ),
            "aligned": estimate_peak_spacing_summary(
                analysis_frames=aligned_frames,
                mask=voiced_mask,
                sample_rate=sample_rate,
                peak_count=int(peak_count),
                peak_min_separation_hz=float(peak_min_separation_hz),
            ),
        }
        decoded_frame_metrics = summarize_frame_sequence_metrics(decoded_frames)
        aligned_frame_metrics = summarize_frame_sequence_metrics(aligned_frames)
        buzz_assessment = assess_stage5_decoded_buzz_reject(
            decoded_waveform=decoded_waveform,
            aligned_target=aligned_waveform,
            predicted_activity=batch["periodic_gate_target"][:common_frame_count],
            sample_rate=sample_rate,
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
        )

        record_slug = sanitize_record_id(record_id)
        record_dir = output_dir / record_slug
        decoded_spectrogram_path = record_dir / "decoded.linear_spectrogram.png"
        aligned_spectrogram_path = record_dir / "aligned.linear_spectrogram.png"
        save_linear_spectrogram_png(
            waveform=decoded_waveform,
            sample_rate=sample_rate,
            output_path=decoded_spectrogram_path,
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
        )
        save_linear_spectrogram_png(
            waveform=aligned_waveform,
            sample_rate=sample_rate,
            output_path=aligned_spectrogram_path,
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
        )

        per_record_rows.append(
            {
                "record_id": record_id,
                "split_name": str(review_record.get("split_name", package_entry.get("split_name", ""))),
                "status": str(review_record.get("status", "unknown")),
                "training_package_path": package_path.as_posix(),
                "decoded_audio_path": str(Path(str(review_record["decoded_audio_path"])).resolve().as_posix()),
                "aligned_target_audio_path": str(
                    Path(str(review_record["aligned_target_audio_path"])).resolve().as_posix()
                ),
                "decoded_spectrogram_path": decoded_spectrogram_path.as_posix(),
                "aligned_spectrogram_path": aligned_spectrogram_path.as_posix(),
                "conditioning_summary": {
                    "frame_count": int(conditioning["frame_count"]),
                    "active_frame_fraction": float(conditioning["active_frame_fraction"]),
                    "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
                    "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
                    "voicing_source": resolved_voicing_source,
                    "energy_source": str(conditioning["energy_source"]),
                },
                "vuv_contrast_summary": vuv_contrast_summary,
                "peak_spacing_summary": peak_spacing_summary,
                "machine_review_metrics": {
                    "decoded_frame_template_cosine_mean": float(decoded_frame_metrics["template_cosine_mean"]),
                    "aligned_frame_template_cosine_mean": float(aligned_frame_metrics["template_cosine_mean"]),
                    "decoded_frame_rms_to_aligned_frame_rms_corr": float(
                        buzz_assessment.get("metrics", {}).get("decoded_frame_rms_to_aligned_frame_rms_corr", 0.0)
                    ),
                    "spectral_centroid_gap_hz": float(
                        buzz_assessment.get("metrics", {}).get("spectral_centroid_gap_hz", 0.0)
                    ),
                    "spectral_high_band_energy_ratio_gap": float(
                        buzz_assessment.get("metrics", {}).get("spectral_high_band_energy_ratio_gap", 0.0)
                    ),
                    "decoded_zero_crossing_rate": float(
                        buzz_assessment.get("metrics", {}).get("decoded_zero_crossing_rate", 0.0)
                    ),
                },
                "buzz_reject_assessment": buzz_assessment,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_source_filter_review_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "dataset_index_paths": [path.as_posix() for path in dataset_index_paths],
        "peak_count": int(peak_count),
        "peak_min_separation_hz": float(peak_min_separation_hz),
        "high_band_hz": float(high_band_hz),
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "aggregates": build_source_filter_aggregates(per_record_rows),
        "diagnosis": diagnose_source_filter_review(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This probe is a post-export review tool: it does not rerun Stage5 decoding and instead audits decoded.wav plus aligned_target.wav against the original Stage5 training-package conditioning.",
            "Voiced/unvoiced statistics are conditioned by the Stage5 training package targets, with periodic_gate_target used as the fallback voiced proxy when explicit vuv_target is missing.",
            "Peak-spacing output is a sidecar for resonance regularity and should not replace direct spectrogram reading.",
        ],
    }
    json_path = output_dir / "stage5_source_filter_review.json"
    md_path = output_dir / "stage5_source_filter_review.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_source_filter_review_markdown(summary), encoding="utf-8", newline="\n")


def build_training_package_map(dataset_index_paths: list[Path]) -> dict[str, dict[str, object]]:
    package_map: dict[str, dict[str, object]] = {}
    for dataset_index_path in dataset_index_paths:
        payload = json.loads(dataset_index_path.read_text(encoding="utf-8"))
        for split_key in ("train_packages", "validation_packages"):
            for entry in payload.get(split_key, []):
                record_id = str(entry.get("record_id", "")).strip()
                if not record_id:
                    continue
                package_map[record_id] = dict(entry)
                package_map[record_id]["_dataset_index_path"] = dataset_index_path.as_posix()
    return package_map


def build_vuv_contrast_summary(
    *,
    conditioning: dict[str, object],
    decoded_voiced_stats: dict[str, float],
    decoded_unvoiced_stats: dict[str, float],
    aligned_voiced_stats: dict[str, float],
    aligned_unvoiced_stats: dict[str, float],
) -> dict[str, float]:
    voiced_fraction = float(conditioning.get("active_voiced_fraction", 0.0))
    return {
        "voiced_frame_ratio": round(voiced_fraction, 6),
        "decoded_voiced_centroid_hz": float(decoded_voiced_stats["spectral_centroid_hz_mean"]),
        "decoded_unvoiced_centroid_hz": float(decoded_unvoiced_stats["spectral_centroid_hz_mean"]),
        "decoded_voiced_high_band_ratio": float(decoded_voiced_stats["spectral_high_band_energy_ratio_mean"]),
        "decoded_unvoiced_high_band_ratio": float(decoded_unvoiced_stats["spectral_high_band_energy_ratio_mean"]),
        "aligned_voiced_centroid_hz": float(aligned_voiced_stats["spectral_centroid_hz_mean"]),
        "aligned_unvoiced_centroid_hz": float(aligned_unvoiced_stats["spectral_centroid_hz_mean"]),
        "aligned_voiced_high_band_ratio": float(aligned_voiced_stats["spectral_high_band_energy_ratio_mean"]),
        "aligned_unvoiced_high_band_ratio": float(aligned_unvoiced_stats["spectral_high_band_energy_ratio_mean"]),
        "decoded_unvoiced_minus_voiced_high_band_ratio": round(
            float(decoded_unvoiced_stats["spectral_high_band_energy_ratio_mean"])
            - float(decoded_voiced_stats["spectral_high_band_energy_ratio_mean"]),
            6,
        ),
        "aligned_unvoiced_minus_voiced_high_band_ratio": round(
            float(aligned_unvoiced_stats["spectral_high_band_energy_ratio_mean"])
            - float(aligned_voiced_stats["spectral_high_band_energy_ratio_mean"]),
            6,
        ),
        "decoded_unvoiced_minus_voiced_centroid_hz": round(
            float(decoded_unvoiced_stats["spectral_centroid_hz_mean"])
            - float(decoded_voiced_stats["spectral_centroid_hz_mean"]),
            6,
        ),
        "aligned_unvoiced_minus_voiced_centroid_hz": round(
            float(aligned_unvoiced_stats["spectral_centroid_hz_mean"])
            - float(aligned_voiced_stats["spectral_centroid_hz_mean"]),
            6,
        ),
    }


def estimate_peak_spacing_summary(
    *,
    analysis_frames: torch.Tensor,
    mask: torch.Tensor,
    sample_rate: int,
    peak_count: int,
    peak_min_separation_hz: float,
) -> dict[str, object]:
    mask_cpu = mask.detach().cpu().to(torch.bool).view(-1)
    frames = analysis_frames.detach().cpu().to(torch.float32)
    if int(mask_cpu.shape[0]) == int(frames.shape[0]) and bool(mask_cpu.any().item()):
        frames = frames[mask_cpu]
    if int(frames.shape[0]) <= 0:
        return {
            "peak_count": 0,
            "peak_freqs_hz": [],
            "mean_spacing_hz": 0.0,
            "spacing_std_hz": 0.0,
            "spacing_cv": 0.0,
        }
    frame_length = int(frames.shape[-1])
    window = torch.hann_window(frame_length, dtype=torch.float32)
    spectrum = torch.fft.rfft(frames * window.unsqueeze(0), dim=-1).abs().pow(2.0).mean(dim=0)
    freqs = torch.fft.rfftfreq(frame_length, d=1.0 / float(sample_rate)).to(torch.float32)
    if int(spectrum.numel()) < 3:
        return {
            "peak_count": 0,
            "peak_freqs_hz": [],
            "mean_spacing_hz": 0.0,
            "spacing_std_hz": 0.0,
            "spacing_cv": 0.0,
        }
    local_max = (spectrum[1:-1] >= spectrum[:-2]) & (spectrum[1:-1] >= spectrum[2:])
    candidate_indices = torch.nonzero(local_max, as_tuple=False).view(-1) + 1
    candidate_indices = candidate_indices[freqs[candidate_indices] >= 80.0]
    if int(candidate_indices.numel()) <= 0:
        return {
            "peak_count": 0,
            "peak_freqs_hz": [],
            "mean_spacing_hz": 0.0,
            "spacing_std_hz": 0.0,
            "spacing_cv": 0.0,
        }
    candidate_scores = spectrum[candidate_indices]
    sorted_order = torch.argsort(candidate_scores, descending=True)
    selected: list[int] = []
    for order_index in sorted_order.tolist():
        candidate_index = int(candidate_indices[int(order_index)].item())
        candidate_freq = float(freqs[candidate_index].item())
        if any(abs(candidate_freq - float(freqs[item].item())) < float(peak_min_separation_hz) for item in selected):
            continue
        selected.append(candidate_index)
        if len(selected) >= int(peak_count):
            break
    selected_freqs = sorted(float(freqs[index].item()) for index in selected)
    spacings = [selected_freqs[index + 1] - selected_freqs[index] for index in range(len(selected_freqs) - 1)]
    if spacings:
        spacing_tensor = torch.tensor(spacings, dtype=torch.float32)
        mean_spacing = float(spacing_tensor.mean().item())
        spacing_std = float(spacing_tensor.std(unbiased=False).item())
        spacing_cv = 0.0 if abs(mean_spacing) <= 1.0e-8 else spacing_std / mean_spacing
    else:
        mean_spacing = 0.0
        spacing_std = 0.0
        spacing_cv = 0.0
    return {
        "peak_count": len(selected_freqs),
        "peak_freqs_hz": [round(freq, 3) for freq in selected_freqs],
        "mean_spacing_hz": round(mean_spacing, 6),
        "spacing_std_hz": round(spacing_std, 6),
        "spacing_cv": round(spacing_cv, 6),
    }


def build_source_filter_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    decoded_vuv_high = []
    aligned_vuv_high = []
    decoded_vuv_centroid = []
    aligned_vuv_centroid = []
    template_cosines = []
    for record in records:
        vuv = dict(record.get("vuv_contrast_summary", {}))
        machine = dict(record.get("machine_review_metrics", {}))
        decoded_vuv_high.append(float(vuv.get("decoded_unvoiced_minus_voiced_high_band_ratio", 0.0)))
        aligned_vuv_high.append(float(vuv.get("aligned_unvoiced_minus_voiced_high_band_ratio", 0.0)))
        decoded_vuv_centroid.append(float(vuv.get("decoded_unvoiced_minus_voiced_centroid_hz", 0.0)))
        aligned_vuv_centroid.append(float(vuv.get("aligned_unvoiced_minus_voiced_centroid_hz", 0.0)))
        template_cosines.append(float(machine.get("decoded_frame_template_cosine_mean", 0.0)))
    return {
        "decoded_vuv_high_band_ratio_mean": round(mean_or_zero(decoded_vuv_high), 6),
        "aligned_vuv_high_band_ratio_mean": round(mean_or_zero(aligned_vuv_high), 6),
        "decoded_vuv_centroid_gap_hz_mean": round(mean_or_zero(decoded_vuv_centroid), 6),
        "aligned_vuv_centroid_gap_hz_mean": round(mean_or_zero(aligned_vuv_centroid), 6),
        "decoded_template_cosine_mean": round(mean_or_zero(template_cosines), 6),
        "decoded_vuv_high_band_ratio_nonpositive_count": sum(1 for value in decoded_vuv_high if value <= 0.0),
        "aligned_vuv_high_band_ratio_positive_count": sum(1 for value in aligned_vuv_high if value > 0.0),
    }


def diagnose_source_filter_review(records: list[dict[str, object]]) -> dict[str, object]:
    record_count = len(records)
    decoded_nonpositive = 0
    centroid_suppressed = 0
    for record in records:
        vuv = dict(record.get("vuv_contrast_summary", {}))
        decoded_high = float(vuv.get("decoded_unvoiced_minus_voiced_high_band_ratio", 0.0))
        aligned_high = float(vuv.get("aligned_unvoiced_minus_voiced_high_band_ratio", 0.0))
        decoded_centroid = float(vuv.get("decoded_unvoiced_minus_voiced_centroid_hz", 0.0))
        aligned_centroid = float(vuv.get("aligned_unvoiced_minus_voiced_centroid_hz", 0.0))
        if decoded_high <= 0.0 and aligned_high > 0.0:
            decoded_nonpositive += 1
        if abs(decoded_centroid) < 0.5 * max(abs(aligned_centroid), 1.0):
            centroid_suppressed += 1
    return {
        "primary_localization": (
            "vuv_separation_collapsed"
            if decoded_nonpositive >= max(1, record_count - 1)
            else "needs_more_localization"
        ),
        "decoded_vuv_high_band_ratio_nonpositive_count": int(decoded_nonpositive),
        "decoded_vuv_centroid_gap_suppressed_count": int(centroid_suppressed),
        "comb_spacing_sidecar_status": "suggestive_only",
    }


def render_source_filter_review_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Source-Filter Review Probe",
        "",
        "## Summary",
        f"- review bundle: `{summary['review_bundle_path']}`",
        f"- source family: `{summary.get('source_family', '')}`",
        f"- record count: `{summary.get('record_count', 0)}`",
        f"- primary localization: `{dict(summary.get('diagnosis', {})).get('primary_localization', 'unknown')}`",
        "",
        "## Aggregate Signals",
    ]
    aggregates = dict(summary.get("aggregates", {}))
    for key in (
        "decoded_vuv_high_band_ratio_mean",
        "aligned_vuv_high_band_ratio_mean",
        "decoded_vuv_centroid_gap_hz_mean",
        "aligned_vuv_centroid_gap_hz_mean",
        "decoded_template_cosine_mean",
        "decoded_vuv_high_band_ratio_nonpositive_count",
        "aligned_vuv_high_band_ratio_positive_count",
    ):
        lines.append(f"- `{key}`: `{aggregates.get(key)}`")
    lines.extend(["", "## Records"])
    for record in list(summary.get("records", [])):
        vuv = dict(record.get("vuv_contrast_summary", {}))
        lines.append(f"- `{record['record_id']}`")
        lines.append(f"  - decoded high-band vuv gap: `{vuv.get('decoded_unvoiced_minus_voiced_high_band_ratio')}`")
        lines.append(f"  - aligned high-band vuv gap: `{vuv.get('aligned_unvoiced_minus_voiced_high_band_ratio')}`")
        lines.append(f"  - decoded centroid vuv gap: `{vuv.get('decoded_unvoiced_minus_voiced_centroid_hz')}`")
        lines.append(f"  - aligned centroid vuv gap: `{vuv.get('aligned_unvoiced_minus_voiced_centroid_hz')}`")
        lines.append(f"  - decoded spectrogram: `{record['decoded_spectrogram_path']}`")
        lines.append(f"  - aligned spectrogram: `{record['aligned_spectrogram_path']}`")
    lines.extend(
        [
            "",
            "## Notes",
            "- Peak-spacing remains a sidecar only and should not replace direct spectrogram reading.",
            "- This probe formalizes the machine-side support for the human buzz conclusion; it does not claim speech quality by itself.",
            "",
        ]
    )
    return "\n".join(lines)


def mean_or_zero(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / float(len(values)))


def sanitize_record_id(record_id: str) -> str:
    return str(record_id).replace("::", "__").replace("/", "_").replace("\\", "_")
