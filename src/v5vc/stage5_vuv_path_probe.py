from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import build_model_from_checkpoint
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    frame_waveform_sequence,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import read_wav_mono, slice_or_pad_waveform
from v5vc.stage5_source_filter_probe import estimate_peak_spacing_summary, mean_or_zero, sanitize_record_id
from v5vc.stage5_waveform_decoder_structure_probe import (
    build_voicing_conditioning_bundle,
    save_linear_spectrogram_png,
    summarize_masked_frame_spectral_statistics,
    summarize_sequence_conditioned_cluster_metrics,
    summarize_sequence_control_coupling_metrics,
)


def analyze_stage5_nores_vuv_path_review(
    *,
    output_dir: Path,
    review_bundle_path: Path,
    audio_export_manifest_paths: list[Path],
    target_record_ids: list[str] | None,
    prefer_audio_export_status: bool,
    high_band_hz: float,
    peak_count: int,
    peak_min_separation_hz: float,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    review_bundle_path = review_bundle_path.resolve()
    audio_export_manifest_paths = [path.resolve() for path in audio_export_manifest_paths]

    review_bundle = json.loads(review_bundle_path.read_text(encoding="utf-8"))
    review_records = list(review_bundle.get("records", []))
    if not review_records:
        raise ValueError("Review bundle contains no records.")
    if target_record_ids:
        wanted_ids = {str(record_id).strip() for record_id in target_record_ids if str(record_id).strip()}
        review_records = [
            record for record in review_records if str(record.get("record_id", "")).strip() in wanted_ids
        ]
        if not review_records:
            raise ValueError("No review-bundle records matched target_record_ids.")

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

        if "waveform_decoder_base_logits" not in outputs:
            raise ValueError(
                "Stage5 vuv-path review currently expects a fused_single waveform path with waveform_decoder_base_logits."
            )

        sample_rate = int(runtime["sample_rate"])
        frame_length = int(runtime["frame_length"])
        hop_length = int(runtime["hop_length"])

        decoded_audio_path = Path(
            str(export_entry.get("decoded_audio_path", review_record.get("decoded_audio_path", "")))
        ).resolve()
        aligned_target_audio_path = Path(
            str(export_entry.get("aligned_target_audio_path", review_record.get("aligned_target_audio_path", "")))
        ).resolve()
        decoded_waveform, decoded_sample_rate = read_wav_mono(decoded_audio_path)
        aligned_waveform, aligned_sample_rate = read_wav_mono(aligned_target_audio_path)
        if int(decoded_sample_rate) != sample_rate or int(aligned_sample_rate) != sample_rate:
            raise ValueError(
                f"Sample-rate mismatch for {record_id}: decoded={decoded_sample_rate}, "
                f"aligned={aligned_sample_rate}, runtime={sample_rate}"
            )
        target_length = min(int(decoded_waveform.shape[0]), int(aligned_waveform.shape[0]))
        decoded_waveform = slice_or_pad_waveform(decoded_waveform, target_length)
        aligned_waveform = slice_or_pad_waveform(aligned_waveform, target_length)

        decoded_frames = frame_waveform_sequence(
            waveform=decoded_waveform,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        aligned_frames = frame_waveform_sequence(
            waveform=aligned_waveform,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
        base_logits = outputs["waveform_decoder_base_logits"].detach().cpu().to(torch.float32)
        residual_shape_delta = outputs.get(
            "waveform_residual_shape_delta",
            torch.zeros_like(outputs["waveform_decoder_base_logits"]),
        ).detach().cpu().to(torch.float32)
        decoder_hidden = outputs["decoder_hidden"].detach().cpu().to(torch.float32)
        periodic_gate = outputs["periodic_gate"].detach().cpu().to(torch.float32)
        noise_gate = outputs["noise_gate"].detach().cpu().to(torch.float32)

        common_frame_count = min(
            int(decoded_frames.shape[0]),
            int(aligned_frames.shape[0]),
            int(waveform_frames.shape[0]),
            int(base_logits.shape[0]),
            int(residual_shape_delta.shape[0]),
            int(decoder_hidden.shape[0]),
            int(periodic_gate.shape[0]),
            int(noise_gate.shape[0]),
        )
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for review record: {record_id}")

        decoded_frames = decoded_frames[:common_frame_count]
        aligned_frames = aligned_frames[:common_frame_count]
        waveform_frames = waveform_frames[:common_frame_count]
        base_logits = base_logits[:common_frame_count]
        residual_shape_delta = residual_shape_delta[:common_frame_count]
        decoder_hidden = decoder_hidden[:common_frame_count]
        periodic_gate = periodic_gate[:common_frame_count]
        noise_gate = noise_gate[:common_frame_count]

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
            raise ValueError(f"Unable to derive vuv conditioning for review record: {record_id}")
        resolved_voicing_source = (
            "periodic_gate_target"
            if batch.get("periodic_gate_target") is not None
            else str(conditioning.get("voicing_source", "missing"))
        )

        decoded_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=decoded_frames,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
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
        base_logits_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=base_logits,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )
        residual_shape_delta_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=residual_shape_delta,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )

        decoder_hidden_control_metrics, decoder_hidden_control_notes = summarize_sequence_control_coupling_metrics(
            sequence=decoder_hidden,
            conditioning=conditioning,
        )
        base_logits_control_metrics, base_logits_control_notes = summarize_sequence_control_coupling_metrics(
            sequence=base_logits,
            conditioning=conditioning,
        )
        residual_shape_delta_control_metrics, residual_shape_delta_control_notes = summarize_sequence_control_coupling_metrics(
            sequence=residual_shape_delta,
            conditioning=conditioning,
        )

        decoder_hidden_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(
            sequence=decoder_hidden,
            conditioning=conditioning,
        )
        base_logits_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(
            sequence=base_logits,
            conditioning=conditioning,
        )
        residual_shape_delta_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(
            sequence=residual_shape_delta,
            conditioning=conditioning,
        )

        gate_summary = summarize_gate_behavior(
            periodic_gate=periodic_gate,
            noise_gate=noise_gate,
            conditioning=conditioning,
        )

        peak_spacing_summary = {
            "base_logits": estimate_peak_spacing_summary(
                analysis_frames=base_logits,
                mask=conditioning["voiced_mask"],
                sample_rate=sample_rate,
                peak_count=peak_count,
                peak_min_separation_hz=peak_min_separation_hz,
            ),
            "waveform_frames": estimate_peak_spacing_summary(
                analysis_frames=waveform_frames,
                mask=conditioning["voiced_mask"],
                sample_rate=sample_rate,
                peak_count=peak_count,
                peak_min_separation_hz=peak_min_separation_hz,
            ),
            "decoded": estimate_peak_spacing_summary(
                analysis_frames=decoded_frames,
                mask=conditioning["voiced_mask"],
                sample_rate=sample_rate,
                peak_count=peak_count,
                peak_min_separation_hz=peak_min_separation_hz,
            ),
            "aligned": estimate_peak_spacing_summary(
                analysis_frames=aligned_frames,
                mask=conditioning["voiced_mask"],
                sample_rate=sample_rate,
                peak_count=peak_count,
                peak_min_separation_hz=peak_min_separation_hz,
            ),
        }

        record_slug = sanitize_record_id(record_id)
        record_dir = output_dir / record_slug
        record_dir.mkdir(parents=True, exist_ok=True)
        stage_spectrogram_paths = save_stage_spectrogram_assets(
            record_dir=record_dir,
            sample_rate=sample_rate,
            frame_length=frame_length,
            hop_length=hop_length,
            decoded_waveform=decoded_waveform,
            aligned_waveform=aligned_waveform,
            base_logits=base_logits,
            residual_shape_delta=residual_shape_delta,
            waveform_frames=waveform_frames,
        )

        diagnosis = diagnose_record_vuv_path(
            gate_summary=gate_summary,
            aligned_vuv_summary=aligned_vuv_summary,
            base_logits_vuv_summary=base_logits_vuv_summary,
            waveform_frames_vuv_summary=waveform_frames_vuv_summary,
            decoded_vuv_summary=decoded_vuv_summary,
            residual_shape_delta_vuv_summary=residual_shape_delta_vuv_summary,
        )

        per_record_rows.append(
            {
                "record_id": record_id,
                "split_name": str(review_record.get("split_name", export_entry.get("split_name", ""))),
                "status": resolve_review_status(
                    review_record=review_record,
                    export_entry=export_entry,
                    prefer_audio_export_status=prefer_audio_export_status,
                ),
                "review_bundle_path": review_bundle_path.as_posix(),
                "audio_export_manifest_path": str(export_entry["audio_export_manifest_path"]),
                "checkpoint_path": checkpoint_path.as_posix(),
                "branch_label": str(export_entry.get("branch_label", "")),
                "training_package_path": package_path.as_posix(),
                "decoded_audio_path": decoded_audio_path.as_posix(),
                "aligned_target_audio_path": aligned_target_audio_path.as_posix(),
                "conditioning_summary": {
                    "frame_count": int(conditioning["frame_count"]),
                    "active_frame_fraction": float(conditioning["active_frame_fraction"]),
                    "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
                    "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
                    "voicing_source": resolved_voicing_source,
                    "aper_source": str(conditioning["aper_source"]),
                    "energy_source": str(conditioning["energy_source"]),
                },
                "stage_spectrogram_paths": stage_spectrogram_paths,
                "gate_summary": gate_summary,
                "vuv_summaries": {
                    "aligned": aligned_vuv_summary,
                    "decoded": decoded_vuv_summary,
                    "waveform_frames": waveform_frames_vuv_summary,
                    "waveform_decoder_base_logits": base_logits_vuv_summary,
                    "waveform_residual_shape_delta": residual_shape_delta_vuv_summary,
                },
                "control_coupling": {
                    "decoder_hidden": {
                        "metrics": decoder_hidden_control_metrics,
                        "notes": decoder_hidden_control_notes,
                    },
                    "waveform_decoder_base_logits": {
                        "metrics": base_logits_control_metrics,
                        "notes": base_logits_control_notes,
                    },
                    "waveform_residual_shape_delta": {
                        "metrics": residual_shape_delta_control_metrics,
                        "notes": residual_shape_delta_control_notes,
                    },
                },
                "conditioned_clusters": {
                    "decoder_hidden": decoder_hidden_cluster_metrics,
                    "waveform_decoder_base_logits": base_logits_cluster_metrics,
                    "waveform_residual_shape_delta": residual_shape_delta_cluster_metrics,
                },
                "peak_spacing_summary": peak_spacing_summary,
                "diagnosis": diagnosis,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_vuv_path_review_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "target_record_ids": [str(record_id).strip() for record_id in (target_record_ids or []) if str(record_id).strip()],
        "prefer_audio_export_status": bool(prefer_audio_export_status),
        "high_band_hz": float(high_band_hz),
        "peak_count": int(peak_count),
        "peak_min_separation_hz": float(peak_min_separation_hz),
        "aggregates": build_vuv_path_aggregates(per_record_rows),
        "diagnosis": diagnose_vuv_path_review(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This review-slice probe localizes vuv separation loss inside the current Stage5 fused_single waveform path.",
            "It complements the decoded-waveform source-filter review by adding base-logits and residual-shape-delta summaries for the same human-review slice.",
            "Voicing conditioning falls back to periodic_gate_target when explicit vuv_target is absent in the reviewed Stage5 package.",
            "The current implementation expects waveform_decoder_base_logits to exist, which matches the active residual-shape fixed-input route.",
        ],
    }
    json_path = output_dir / "stage5_vuv_path_review.json"
    md_path = output_dir / "stage5_vuv_path_review.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_vuv_path_review_markdown(summary), encoding="utf-8", newline="\n")


def build_export_record_map(audio_export_manifest_paths: list[Path]) -> dict[str, dict[str, object]]:
    record_map: dict[str, dict[str, object]] = {}
    for manifest_path in audio_export_manifest_paths:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in payload.get("records", []):
            record_id = str(record.get("record_id", "")).strip()
            if not record_id:
                continue
            record_map[record_id] = {
                **dict(record),
                "audio_export_manifest_path": manifest_path.as_posix(),
                "checkpoint_path": str(payload["checkpoint_path"]),
                "dataset_index_path": str(payload.get("dataset_index_path", "")),
                "branch_label": str(payload.get("branch_label", "")),
                "waveform_decode": dict(payload.get("waveform_decode", {})),
            }
    return record_map


def resolve_review_status(
    *,
    review_record: dict[str, object],
    export_entry: dict[str, object],
    prefer_audio_export_status: bool,
) -> str:
    if prefer_audio_export_status:
        export_status = str(dict(export_entry.get("buzz_reject_assessment", {})).get("status", "")).strip()
        if export_status:
            return export_status
    return str(review_record.get("status", "unknown"))


def summarize_vuv_conditioned_frame_sequence(
    *,
    analysis_frames: torch.Tensor,
    conditioning: dict[str, object],
    sample_rate: int,
    high_band_hz: float,
) -> dict[str, float]:
    voiced_stats = summarize_masked_frame_spectral_statistics(
        analysis_frames=analysis_frames,
        mask=conditioning["voiced_mask"],
        sample_rate=sample_rate,
        high_band_hz=high_band_hz,
    )
    unvoiced_stats = summarize_masked_frame_spectral_statistics(
        analysis_frames=analysis_frames,
        mask=conditioning["unvoiced_mask"],
        sample_rate=sample_rate,
        high_band_hz=high_band_hz,
    )
    return {
        "voiced_centroid_hz": float(voiced_stats["spectral_centroid_hz_mean"]),
        "unvoiced_centroid_hz": float(unvoiced_stats["spectral_centroid_hz_mean"]),
        "unvoiced_minus_voiced_centroid_hz": round(
            float(unvoiced_stats["spectral_centroid_hz_mean"]) - float(voiced_stats["spectral_centroid_hz_mean"]),
            6,
        ),
        "voiced_high_band_ratio": float(voiced_stats["spectral_high_band_energy_ratio_mean"]),
        "unvoiced_high_band_ratio": float(unvoiced_stats["spectral_high_band_energy_ratio_mean"]),
        "unvoiced_minus_voiced_high_band_ratio": round(
            float(unvoiced_stats["spectral_high_band_energy_ratio_mean"])
            - float(voiced_stats["spectral_high_band_energy_ratio_mean"]),
            6,
        ),
        "voiced_frame_rms_mean": float(voiced_stats["frame_rms_mean"]),
        "unvoiced_frame_rms_mean": float(unvoiced_stats["frame_rms_mean"]),
        "unvoiced_minus_voiced_frame_rms_mean": round(
            float(unvoiced_stats["frame_rms_mean"]) - float(voiced_stats["frame_rms_mean"]),
            6,
        ),
    }


def summarize_gate_behavior(
    *,
    periodic_gate: torch.Tensor,
    noise_gate: torch.Tensor,
    conditioning: dict[str, object],
) -> dict[str, float]:
    periodic_gate_1d = periodic_gate.detach().cpu().to(torch.float32).view(-1)
    noise_gate_1d = noise_gate.detach().cpu().to(torch.float32).view(-1)
    voiced_mask = conditioning["voiced_mask"]
    unvoiced_mask = conditioning["unvoiced_mask"]
    active_mask = conditioning["active_mask"]
    return {
        "periodic_gate_active_mean": round(masked_mean(periodic_gate_1d, active_mask), 6),
        "noise_gate_active_mean": round(masked_mean(noise_gate_1d, active_mask), 6),
        "periodic_gate_voiced_mean": round(masked_mean(periodic_gate_1d, voiced_mask), 6),
        "periodic_gate_unvoiced_mean": round(masked_mean(periodic_gate_1d, unvoiced_mask), 6),
        "noise_gate_voiced_mean": round(masked_mean(noise_gate_1d, voiced_mask), 6),
        "noise_gate_unvoiced_mean": round(masked_mean(noise_gate_1d, unvoiced_mask), 6),
        "periodic_minus_noise_voiced_mean": round(
            masked_mean(periodic_gate_1d - noise_gate_1d, voiced_mask),
            6,
        ),
        "noise_minus_periodic_unvoiced_mean": round(
            masked_mean(noise_gate_1d - periodic_gate_1d, unvoiced_mask),
            6,
        ),
    }


def masked_mean(values: torch.Tensor, mask: torch.Tensor) -> float:
    mask_cpu = mask.detach().cpu().to(torch.bool).view(-1)
    values_cpu = values.detach().cpu().to(torch.float32).view(-1)
    if int(mask_cpu.shape[0]) != int(values_cpu.shape[0]) or not bool(mask_cpu.any().item()):
        return 0.0
    return float(values_cpu[mask_cpu].mean().item())


def save_stage_spectrogram_assets(
    *,
    record_dir: Path,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor,
    base_logits: torch.Tensor,
    residual_shape_delta: torch.Tensor,
    waveform_frames: torch.Tensor,
) -> dict[str, str]:
    stage_waveforms = {
        "decoded": decoded_waveform,
        "aligned": aligned_waveform,
        "waveform_decoder_base_logits": reconstruct_waveform_from_frames(
            waveform_frames=base_logits,
            frame_length=frame_length,
            hop_length=hop_length,
        ).detach().cpu(),
        "waveform_residual_shape_delta": reconstruct_waveform_from_frames(
            waveform_frames=residual_shape_delta,
            frame_length=frame_length,
            hop_length=hop_length,
        ).detach().cpu(),
        "waveform_frames": reconstruct_waveform_from_frames(
            waveform_frames=waveform_frames,
            frame_length=frame_length,
            hop_length=hop_length,
        ).detach().cpu(),
    }
    for label, waveform in stage_waveforms.items():
        save_linear_spectrogram_png(
            waveform=waveform,
            sample_rate=sample_rate,
            output_path=record_dir / f"{label}.linear_spectrogram.png",
            frame_length=frame_length,
            hop_length=hop_length,
        )
    return {
        label: (record_dir / f"{label}.linear_spectrogram.png").as_posix()
        for label in stage_waveforms.keys()
    }


def diagnose_record_vuv_path(
    *,
    gate_summary: dict[str, float],
    aligned_vuv_summary: dict[str, float],
    base_logits_vuv_summary: dict[str, float],
    waveform_frames_vuv_summary: dict[str, float],
    decoded_vuv_summary: dict[str, float],
    residual_shape_delta_vuv_summary: dict[str, float],
) -> dict[str, object]:
    aligned_gap = float(aligned_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    base_gap = float(base_logits_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    waveform_gap = float(waveform_frames_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    decoded_gap = float(decoded_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    residual_gap = float(residual_shape_delta_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))

    if aligned_gap > 0.0 and base_gap <= 0.0:
        primary = "base_logits_vuv_separation_missing"
    elif aligned_gap > 0.0 and waveform_gap <= 0.0 and base_gap > 0.0:
        primary = "waveform_frames_vuv_separation_lost_after_base_logits"
    elif aligned_gap > 0.0 and decoded_gap <= 0.0 and waveform_gap > 0.0:
        primary = "decoded_waveform_vuv_separation_lost_after_frame_projection"
    else:
        primary = "needs_manual_review"

    secondary: list[str] = []
    if residual_gap <= 0.0:
        secondary.append("residual_shape_delta_not_unvoiced_focused")
    if float(gate_summary.get("noise_minus_periodic_unvoiced_mean", 0.0)) <= 0.0:
        secondary.append("noise_gate_not_dominant_on_unvoiced_frames")
    return {
        "primary_localization": primary,
        "secondary_localizations": secondary,
    }


def build_vuv_path_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    base_high = []
    waveform_high = []
    decoded_high = []
    aligned_high = []
    residual_high = []
    noise_gate_unvoiced = []
    periodic_gate_voiced = []
    for record in records:
        vuv_summaries = dict(record.get("vuv_summaries", {}))
        gate_summary = dict(record.get("gate_summary", {}))
        base_high.append(
            float(
                dict(vuv_summaries.get("waveform_decoder_base_logits", {})).get(
                    "unvoiced_minus_voiced_high_band_ratio",
                    0.0,
                )
            )
        )
        waveform_high.append(
            float(dict(vuv_summaries.get("waveform_frames", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
        )
        decoded_high.append(
            float(dict(vuv_summaries.get("decoded", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
        )
        aligned_high.append(
            float(dict(vuv_summaries.get("aligned", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
        )
        residual_high.append(
            float(
                dict(vuv_summaries.get("waveform_residual_shape_delta", {})).get(
                    "unvoiced_minus_voiced_high_band_ratio",
                    0.0,
                )
            )
        )
        noise_gate_unvoiced.append(float(gate_summary.get("noise_gate_unvoiced_mean", 0.0)))
        periodic_gate_voiced.append(float(gate_summary.get("periodic_gate_voiced_mean", 0.0)))
    return {
        "base_logits_vuv_high_band_ratio_mean": round(mean_or_zero(base_high), 6),
        "waveform_frames_vuv_high_band_ratio_mean": round(mean_or_zero(waveform_high), 6),
        "decoded_vuv_high_band_ratio_mean": round(mean_or_zero(decoded_high), 6),
        "aligned_vuv_high_band_ratio_mean": round(mean_or_zero(aligned_high), 6),
        "residual_shape_delta_vuv_high_band_ratio_mean": round(mean_or_zero(residual_high), 6),
        "noise_gate_unvoiced_mean": round(mean_or_zero(noise_gate_unvoiced), 6),
        "periodic_gate_voiced_mean": round(mean_or_zero(periodic_gate_voiced), 6),
        "base_logits_vuv_nonpositive_count": sum(1 for value in base_high if value <= 0.0),
        "waveform_frames_vuv_nonpositive_count": sum(1 for value in waveform_high if value <= 0.0),
        "decoded_vuv_nonpositive_count": sum(1 for value in decoded_high if value <= 0.0),
        "residual_shape_delta_vuv_nonpositive_count": sum(1 for value in residual_high if value <= 0.0),
    }


def diagnose_vuv_path_review(records: list[dict[str, object]]) -> dict[str, object]:
    primary_counts: dict[str, int] = {}
    secondary_counts: dict[str, int] = {}
    for record in records:
        diagnosis = dict(record.get("diagnosis", {}))
        primary = str(diagnosis.get("primary_localization", "needs_manual_review"))
        primary_counts[primary] = primary_counts.get(primary, 0) + 1
        for label in list(diagnosis.get("secondary_localizations", [])):
            key = str(label)
            secondary_counts[key] = secondary_counts.get(key, 0) + 1
    if primary_counts:
        primary_localization = max(primary_counts.items(), key=lambda item: (item[1], item[0]))[0]
    else:
        primary_localization = "needs_manual_review"
    return {
        "primary_localization": primary_localization,
        "primary_counts": primary_counts,
        "secondary_counts": secondary_counts,
    }


def render_vuv_path_review_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Vuv Path Review Probe",
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
        "base_logits_vuv_high_band_ratio_mean",
        "waveform_frames_vuv_high_band_ratio_mean",
        "decoded_vuv_high_band_ratio_mean",
        "aligned_vuv_high_band_ratio_mean",
        "residual_shape_delta_vuv_high_band_ratio_mean",
        "noise_gate_unvoiced_mean",
        "periodic_gate_voiced_mean",
        "base_logits_vuv_nonpositive_count",
        "decoded_vuv_nonpositive_count",
    ):
        lines.append(f"- `{key}`: `{aggregates.get(key)}`")
    lines.extend(["", "## Records"])
    for record in list(summary.get("records", [])):
        diagnosis = dict(record.get("diagnosis", {}))
        vuv_summaries = dict(record.get("vuv_summaries", {}))
        stage_spectrogram_paths = dict(record.get("stage_spectrogram_paths", {}))
        base_logits_vuv = dict(vuv_summaries.get("waveform_decoder_base_logits", {}))
        decoded_vuv = dict(vuv_summaries.get("decoded", {}))
        lines.append(f"- `{record['record_id']}`")
        lines.append(f"  - primary localization: `{diagnosis.get('primary_localization')}`")
        lines.append(f"  - secondary localizations: `{json.dumps(diagnosis.get('secondary_localizations', []))}`")
        lines.append(
            "  - base_logits high-band vuv gap: "
            f"`{base_logits_vuv.get('unvoiced_minus_voiced_high_band_ratio')}`"
        )
        lines.append(
            "  - decoded high-band vuv gap: "
            f"`{decoded_vuv.get('unvoiced_minus_voiced_high_band_ratio')}`"
        )
        lines.append(
            "  - base-logits spectrogram: "
            f"`{stage_spectrogram_paths.get('waveform_decoder_base_logits', '')}`"
        )
        lines.append(
            "  - decoded spectrogram: "
            f"`{stage_spectrogram_paths.get('decoded', '')}`"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- This probe localizes the active review slice inside the current fused_single waveform path rather than only at the final decoded waveform.",
            "- Positive aligned vuv contrast with non-positive base-logits contrast means the loss is already present before overlap-add decode semantics.",
            "",
        ]
    )
    return "\n".join(lines)
