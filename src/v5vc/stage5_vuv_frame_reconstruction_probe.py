from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import build_model_from_checkpoint
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_source_filter_probe import mean_or_zero, sanitize_record_id
from v5vc.stage5_speech_emergence_probe import frame_waveform_sequence
from v5vc.stage5_vuv_path_probe import (
    build_export_record_map,
    summarize_vuv_conditioned_frame_sequence,
)
from v5vc.stage5_waveform_decoder_structure_probe import (
    build_voicing_conditioning_bundle,
    save_linear_spectrogram_png,
)
from v5vc.target_format_recovery import write_waveform_int16


@dataclass(frozen=True)
class FrameReconstructionVariant:
    label: str
    description: str
    mode: str


FRAME_RECONSTRUCTION_VARIANTS = [
    FrameReconstructionVariant(
        label="hann_ola_baseline",
        description="Current decode path without predicted activity gating: Hann-window overlap-add with window-weight normalization.",
        mode="hann_ola_baseline",
    ),
    FrameReconstructionVariant(
        label="rectangular_ola",
        description="Overlap-add with a rectangular window and simple overlap averaging.",
        mode="rectangular_ola",
    ),
    FrameReconstructionVariant(
        label="hop_stitch",
        description="Stitch only the first hop-length slice from each frame and keep the last frame tail.",
        mode="hop_stitch",
    ),
    FrameReconstructionVariant(
        label="flatten_frames",
        description="Flatten frames end to end without any overlap-add.",
        mode="flatten_frames",
    ),
]


def analyze_stage5_nores_vuv_frame_reconstruction_review(
    *,
    output_dir: Path,
    review_bundle_path: Path,
    audio_export_manifest_paths: list[Path],
    high_band_hz: float,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    review_bundle_path = review_bundle_path.resolve()
    audio_export_manifest_paths = [path.resolve() for path in audio_export_manifest_paths]

    review_bundle = json.loads(review_bundle_path.read_text(encoding="utf-8"))
    review_records = list(review_bundle.get("records", []))
    if not review_records:
        raise ValueError("Review bundle contains no records.")

    export_record_map = build_export_record_map(audio_export_manifest_paths)
    model_cache: dict[str, torch.nn.Module] = {}
    per_record_rows: list[dict[str, object]] = []

    for review_record in review_records:
        record_id = str(review_record.get("record_id", "")).strip()
        if not record_id:
            continue
        export_entry = export_record_map.get(record_id)
        if export_entry is None:
            raise KeyError(f"Unable to resolve export-manifest entry for review record: {record_id}")

        package_path = Path(str(export_entry["training_package_path"])).resolve()
        payload = load_training_package_payload(package_path)
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)
        checkpoint_path = Path(str(export_entry["checkpoint_path"])).resolve()
        model_key = checkpoint_path.as_posix()
        if model_key not in model_cache:
            checkpoint_payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            model = build_model_from_checkpoint(
                checkpoint_payload=checkpoint_payload,
                first_batch=batch,
                first_runtime=runtime,
            )
            model.eval()
            model_cache[model_key] = model
        model = model_cache[model_key]

        decoder_branch_mean_mix_alpha = float(export_entry["waveform_decode"].get("decoder_branch_mean_mix_alpha", 0.0))
        with torch.no_grad():
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
                decoder_branch_mean_mix_alpha=decoder_branch_mean_mix_alpha,
            )

        waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
        sample_rate = int(runtime["sample_rate"])
        frame_length = int(runtime["frame_length"])
        hop_length = int(runtime["hop_length"])
        frame_count = int(waveform_frames.shape[0])
        if frame_count <= 0:
            raise ValueError(f"No waveform frames available for reconstruction review record: {record_id}")

        conditioning = build_voicing_conditioning_bundle(
            frame_count=frame_count,
            vuv_target=batch.get("periodic_gate_target", batch.get("vuv_target")),
            voiced_proxy_target=batch.get("voiced_proxy_target"),
            aper_target=batch.get("aper_target"),
            aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
            energy_log_rms_norm_target=batch.get("energy_log_rms_norm_target"),
            energy_control_target=batch.get("energy_control_target"),
        )
        if conditioning is None:
            raise ValueError(f"Unable to derive vuv conditioning for reconstruction review record: {record_id}")

        aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32)
        aligned_frames = frame_waveform_sequence(
            waveform=aligned_waveform,
            frame_length=frame_length,
            hop_length=hop_length,
            target_frame_count=frame_count,
        )
        aligned_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=aligned_frames,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )
        waveform_frames_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=waveform_frames,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )

        record_dir = output_dir / sanitize_record_id(record_id)
        record_dir.mkdir(parents=True, exist_ok=True)
        aligned_audio_path = record_dir / "aligned_target.wav"
        aligned_spectrogram_path = record_dir / "aligned_target.linear_spectrogram.png"
        write_waveform_int16(aligned_audio_path, aligned_waveform, sample_rate=sample_rate)
        save_linear_spectrogram_png(
            waveform=aligned_waveform,
            sample_rate=sample_rate,
            output_path=aligned_spectrogram_path,
            frame_length=frame_length,
            hop_length=hop_length,
        )

        variant_rows: list[dict[str, object]] = []
        for variant in FRAME_RECONSTRUCTION_VARIANTS:
            reconstructed_waveform = reconstruct_waveform_frames_variant(
                waveform_frames=waveform_frames,
                frame_length=frame_length,
                hop_length=hop_length,
                variant=variant,
            )
            reconstructed_frames = frame_waveform_sequence(
                waveform=reconstructed_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                target_frame_count=frame_count,
            )
            decoded_vuv_summary = summarize_vuv_conditioned_frame_sequence(
                analysis_frames=reconstructed_frames,
                conditioning=conditioning,
                sample_rate=sample_rate,
                high_band_hz=high_band_hz,
            )
            audio_path = record_dir / f"{variant.label}.wav"
            spectrogram_path = record_dir / f"{variant.label}.linear_spectrogram.png"
            write_waveform_int16(audio_path, reconstructed_waveform, sample_rate=sample_rate)
            save_linear_spectrogram_png(
                waveform=reconstructed_waveform,
                sample_rate=sample_rate,
                output_path=spectrogram_path,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            variant_rows.append(
                {
                    "label": variant.label,
                    "description": variant.description,
                    "mode": variant.mode,
                    "audio_path": audio_path.as_posix(),
                    "spectrogram_path": spectrogram_path.as_posix(),
                    "waveform_length": int(reconstructed_waveform.shape[0]),
                    "vuv_summary": decoded_vuv_summary,
                }
            )

        diagnosis = diagnose_record_frame_reconstruction(
            aligned_vuv_summary=aligned_vuv_summary,
            waveform_frames_vuv_summary=waveform_frames_vuv_summary,
            variant_rows=variant_rows,
        )
        per_record_rows.append(
            {
                "record_id": record_id,
                "split_name": str(review_record.get("split_name", export_entry.get("split_name", ""))),
                "status": str(review_record.get("status", "unknown")),
                "review_bundle_path": review_bundle_path.as_posix(),
                "audio_export_manifest_path": str(export_entry["audio_export_manifest_path"]),
                "checkpoint_path": checkpoint_path.as_posix(),
                "training_package_path": package_path.as_posix(),
                "conditioning_summary": {
                    "frame_count": int(conditioning["frame_count"]),
                    "active_frame_fraction": float(conditioning["active_frame_fraction"]),
                    "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
                    "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
                    "voicing_source": str(conditioning.get("voicing_source", "missing")),
                },
                "stage_spectrogram_paths": {
                    "aligned_target": aligned_spectrogram_path.as_posix(),
                },
                "vuv_summaries": {
                    "aligned": aligned_vuv_summary,
                    "waveform_frames": waveform_frames_vuv_summary,
                },
                "variants": variant_rows,
                "diagnosis": diagnosis,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_vuv_frame_reconstruction_review_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "aggregates": build_frame_reconstruction_aggregates(per_record_rows),
        "diagnosis": diagnose_frame_reconstruction_review(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This probe keeps waveform_frames fixed and changes only the frame-to-waveform reconstruction geometry.",
            "hann_ola_baseline reproduces the current no-gate decode route.",
            "rectangular_ola, hop_stitch, and flatten_frames test whether overlap-add geometry itself is the main vuv-loss site.",
        ],
    }
    json_path = output_dir / "stage5_vuv_frame_reconstruction_review.json"
    md_path = output_dir / "stage5_vuv_frame_reconstruction_review.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_frame_reconstruction_review_markdown(summary), encoding="utf-8", newline="\n")


def reconstruct_waveform_frames_variant(
    *,
    waveform_frames: torch.Tensor,
    frame_length: int,
    hop_length: int,
    variant: FrameReconstructionVariant,
) -> torch.Tensor:
    frames = waveform_frames.detach().cpu().to(torch.float32)
    if frames.ndim != 2:
        raise ValueError(f"Expected waveform_frames shape [frames, samples], got {tuple(frames.shape)}")
    if int(frames.shape[-1]) != int(frame_length):
        raise ValueError(
            "waveform_frames sample dimension does not match frame_length: "
            f"frames={tuple(frames.shape)} frame_length={frame_length}"
        )
    if variant.mode == "hann_ola_baseline":
        return reconstruct_waveform_from_frames(
            waveform_frames=frames,
            frame_length=frame_length,
            hop_length=hop_length,
            frame_gains=None,
            frame_gain_floor=0.0,
            frame_gain_smoothing_frames=0,
            frame_gain_apply_mode="pre_overlap_add",
        ).detach().cpu().to(torch.float32)
    if variant.mode == "rectangular_ola":
        return reconstruct_waveform_from_frames_rectangular_average(
            waveform_frames=frames,
            frame_length=frame_length,
            hop_length=hop_length,
        )
    if variant.mode == "hop_stitch":
        return reconstruct_waveform_from_frames_hop_stitch(
            waveform_frames=frames,
            frame_length=frame_length,
            hop_length=hop_length,
        )
    if variant.mode == "flatten_frames":
        return frames.reshape(-1).contiguous()
    raise ValueError(f"Unsupported frame reconstruction variant mode: {variant.mode}")


def reconstruct_waveform_from_frames_rectangular_average(
    *,
    waveform_frames: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    frame_count = int(waveform_frames.shape[0])
    total_length = int(frame_length + max(0, frame_count - 1) * hop_length)
    output = waveform_frames.new_zeros((total_length,))
    weights = waveform_frames.new_zeros((total_length,))
    window = waveform_frames.new_ones((int(frame_length),))
    for frame_index in range(frame_count):
        start = int(frame_index * hop_length)
        end = start + int(frame_length)
        output[start:end] += waveform_frames[frame_index] * window
        weights[start:end] += window
    return output / weights.clamp_min(1.0e-6)


def reconstruct_waveform_from_frames_hop_stitch(
    *,
    waveform_frames: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    if int(hop_length) <= 0:
        raise ValueError("hop_length must be positive for hop_stitch reconstruction.")
    frame_count = int(waveform_frames.shape[0])
    if frame_count <= 0:
        return waveform_frames.new_zeros((0,))
    segments = []
    for frame_index in range(max(0, frame_count - 1)):
        segments.append(waveform_frames[frame_index, : int(hop_length)])
    tail_length = max(1, int(frame_length) - int(hop_length))
    segments.append(waveform_frames[-1, -tail_length:])
    return torch.cat(segments, dim=0).contiguous()


def diagnose_record_frame_reconstruction(
    *,
    aligned_vuv_summary: dict[str, float],
    waveform_frames_vuv_summary: dict[str, float],
    variant_rows: list[dict[str, object]],
) -> dict[str, object]:
    aligned_gap = float(aligned_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    waveform_gap = float(waveform_frames_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    variant_map = {
        str(row["label"]): float(dict(row.get("vuv_summary", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
        for row in variant_rows
    }
    hann_gap = float(variant_map.get("hann_ola_baseline", 0.0))
    rect_gap = float(variant_map.get("rectangular_ola", 0.0))
    stitch_gap = float(variant_map.get("hop_stitch", 0.0))
    flatten_gap = float(variant_map.get("flatten_frames", 0.0))
    if aligned_gap > 0.0 and waveform_gap <= 0.0:
        primary = "waveform_frames_vuv_not_ready_for_reconstruction_probe"
    elif waveform_gap > 0.0 and hann_gap <= 0.0 and rect_gap <= 0.0 and stitch_gap > 0.0:
        primary = "overlap_add_geometry_vuv_separation_loss"
    elif waveform_gap > 0.0 and hann_gap <= 0.0 and rect_gap > hann_gap:
        primary = "hann_windowing_worse_than_rectangular_overlap_average"
    elif waveform_gap > 0.0 and hann_gap <= 0.0 and flatten_gap > 0.0:
        primary = "frame_flattening_preserves_vuv_but_ola_loses_it"
    else:
        primary = "needs_manual_review"
    secondary: list[str] = []
    if rect_gap > hann_gap:
        secondary.append("rectangular_ola_better_than_hann_ola")
    if stitch_gap > hann_gap:
        secondary.append("hop_stitch_better_than_hann_ola")
    if flatten_gap > hann_gap:
        secondary.append("flatten_frames_better_than_hann_ola")
    return {
        "primary_localization": primary,
        "secondary_localizations": secondary,
    }


def build_frame_reconstruction_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    aligned = []
    waveform = []
    variant_values: dict[str, list[float]] = {variant.label: [] for variant in FRAME_RECONSTRUCTION_VARIANTS}
    for record in records:
        aligned.append(float(dict(record.get("vuv_summaries", {})).get("aligned", {}).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        waveform.append(float(dict(record.get("vuv_summaries", {})).get("waveform_frames", {}).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        for variant_row in list(record.get("variants", [])):
            label = str(variant_row.get("label", ""))
            if label in variant_values:
                variant_values[label].append(
                    float(dict(variant_row.get("vuv_summary", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
                )
    aggregates: dict[str, object] = {
        "aligned_vuv_high_band_ratio_mean": round(mean_or_zero(aligned), 6),
        "waveform_frames_vuv_high_band_ratio_mean": round(mean_or_zero(waveform), 6),
        "waveform_frames_vuv_nonpositive_count": sum(1 for value in waveform if value <= 0.0),
    }
    for label, values in variant_values.items():
        aggregates[f"{label}_vuv_high_band_ratio_mean"] = round(mean_or_zero(values), 6)
        aggregates[f"{label}_vuv_nonpositive_count"] = sum(1 for value in values if value <= 0.0)
    return aggregates


def diagnose_frame_reconstruction_review(records: list[dict[str, object]]) -> dict[str, object]:
    primary_counts: dict[str, int] = {}
    for record in records:
        primary = str(dict(record.get("diagnosis", {})).get("primary_localization", "missing"))
        primary_counts[primary] = primary_counts.get(primary, 0) + 1
    aggregates = build_frame_reconstruction_aggregates(records)
    waveform_mean = float(aggregates["waveform_frames_vuv_high_band_ratio_mean"])
    hann_mean = float(aggregates["hann_ola_baseline_vuv_high_band_ratio_mean"])
    rect_mean = float(aggregates["rectangular_ola_vuv_high_band_ratio_mean"])
    stitch_mean = float(aggregates["hop_stitch_vuv_high_band_ratio_mean"])
    flatten_mean = float(aggregates["flatten_frames_vuv_high_band_ratio_mean"])
    if waveform_mean <= 0.0:
        primary = "waveform_frames_vuv_not_ready_for_reconstruction_probe"
    elif hann_mean <= 0.0 and rect_mean <= 0.0 and stitch_mean > 0.0:
        primary = "overlap_add_geometry_vuv_separation_loss"
    elif hann_mean <= 0.0 and rect_mean > hann_mean:
        primary = "hann_windowing_worse_than_rectangular_overlap_average"
    elif hann_mean <= 0.0 and flatten_mean > 0.0:
        primary = "frame_flattening_preserves_vuv_but_ola_loses_it"
    else:
        primary = "needs_manual_review"
    return {
        "primary_diagnosis": primary,
        "primary_localization_counts": primary_counts,
    }


def render_frame_reconstruction_review_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Vuv Frame-Reconstruction Review Probe",
        "",
        "## Summary",
        f"- review bundle: `{summary.get('review_bundle_path', '')}`",
        f"- source family: `{summary.get('source_family', '')}`",
        f"- record count: `{summary.get('record_count', 0)}`",
        f"- primary diagnosis: `{dict(summary.get('diagnosis', {})).get('primary_diagnosis', 'missing')}`",
        "",
        "## Aggregate Signals",
    ]
    aggregates = dict(summary.get("aggregates", {}))
    for key in [
        "aligned_vuv_high_band_ratio_mean",
        "waveform_frames_vuv_high_band_ratio_mean",
        "hann_ola_baseline_vuv_high_band_ratio_mean",
        "rectangular_ola_vuv_high_band_ratio_mean",
        "hop_stitch_vuv_high_band_ratio_mean",
        "flatten_frames_vuv_high_band_ratio_mean",
        "waveform_frames_vuv_nonpositive_count",
        "hann_ola_baseline_vuv_nonpositive_count",
        "rectangular_ola_vuv_nonpositive_count",
        "hop_stitch_vuv_nonpositive_count",
        "flatten_frames_vuv_nonpositive_count",
    ]:
        lines.append(f"- `{key}`: `{aggregates.get(key, 0)}`")
    lines.extend(["", "## Records"])
    for record in list(summary.get("records", [])):
        diagnosis = dict(record.get("diagnosis", {}))
        vuv_summaries = dict(record.get("vuv_summaries", {}))
        lines.append(f"- `{record.get('record_id', '')}`")
        lines.append(f"  - primary localization: `{diagnosis.get('primary_localization', 'missing')}`")
        lines.append(f"  - secondary localizations: `{diagnosis.get('secondary_localizations', [])}`")
        lines.append(
            "  - waveform_frames high-band vuv gap: "
            f"`{dict(vuv_summaries.get('waveform_frames', {})).get('unvoiced_minus_voiced_high_band_ratio', 0.0)}`"
        )
        for variant_row in list(record.get("variants", [])):
            lines.append(
                f"  - {variant_row.get('label', '')} high-band vuv gap: "
                f"`{dict(variant_row.get('vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio', 0.0)}`"
            )
    lines.extend(
        [
            "",
            "## Notes",
            "- This probe holds waveform_frames fixed and only changes frame-to-waveform reconstruction geometry.",
            "- `hann_ola_baseline` reproduces the current no-gate decode route.",
            "- `rectangular_ola`, `hop_stitch`, and `flatten_frames` test whether overlap-add itself is the main sink for the rescued vuv separation.",
        ]
    )
    return "\n".join(lines) + "\n"
