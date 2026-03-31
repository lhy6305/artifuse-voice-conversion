from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    normalize_predicted_activity_gate_apply_mode,
)
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


DECODE_PROJECTION_ROUTES = [
    {
        "label": "decoded_no_gate",
        "description": "Overlap-add on waveform_frames without predicted activity gating.",
        "use_predicted_activity_gate": False,
        "predicted_activity_gate_apply_mode": "pre_overlap_add",
    },
    {
        "label": "decoded_pre_ola_gate",
        "description": "Apply predicted activity to each frame before overlap-add.",
        "use_predicted_activity_gate": True,
        "predicted_activity_gate_apply_mode": "pre_overlap_add",
    },
    {
        "label": "decoded_post_ola_gate",
        "description": "Apply predicted activity as a post-overlap-add envelope.",
        "use_predicted_activity_gate": True,
        "predicted_activity_gate_apply_mode": "post_ola_envelope",
    },
]


def analyze_stage5_nores_vuv_decode_projection_review(
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
        predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"]).detach().cpu().to(torch.float32)
        if predicted_activity.ndim == 2 and int(predicted_activity.shape[-1]) == 1:
            predicted_activity = predicted_activity.squeeze(-1)

        sample_rate = int(runtime["sample_rate"])
        frame_length = int(runtime["frame_length"])
        hop_length = int(runtime["hop_length"])
        common_frame_count = min(int(waveform_frames.shape[0]), int(predicted_activity.shape[0]))
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for decode-projection review record: {record_id}")
        waveform_frames = waveform_frames[:common_frame_count]
        predicted_activity = predicted_activity[:common_frame_count]

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
            raise ValueError(f"Unable to derive vuv conditioning for decode-projection review record: {record_id}")

        aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32)
        aligned_frames = frame_waveform_sequence(
            waveform=aligned_waveform,
            frame_length=frame_length,
            hop_length=hop_length,
            target_frame_count=common_frame_count,
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

        export_decode = dict(export_entry.get("waveform_decode", {}))
        frame_gain_floor = float(export_decode.get("predicted_activity_gate_floor", 0.0))
        frame_gain_smoothing_frames = int(export_decode.get("predicted_activity_gate_smoothing_frames", 0))

        record_dir = output_dir / sanitize_record_id(record_id)
        record_dir.mkdir(parents=True, exist_ok=True)
        aligned_audio_path = record_dir / "aligned_target.wav"
        write_waveform_int16(aligned_audio_path, aligned_waveform, sample_rate=sample_rate)

        route_rows: list[dict[str, object]] = []
        for route in DECODE_PROJECTION_ROUTES:
            resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(
                str(route["predicted_activity_gate_apply_mode"])
            )
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=waveform_frames,
                frame_length=frame_length,
                hop_length=hop_length,
                frame_gains=predicted_activity if bool(route["use_predicted_activity_gate"]) else None,
                frame_gain_floor=frame_gain_floor,
                frame_gain_smoothing_frames=frame_gain_smoothing_frames,
                frame_gain_apply_mode=resolved_apply_mode,
            ).detach().cpu().to(torch.float32)
            decoded_frames = frame_waveform_sequence(
                waveform=decoded_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                target_frame_count=common_frame_count,
            )
            decoded_vuv_summary = summarize_vuv_conditioned_frame_sequence(
                analysis_frames=decoded_frames,
                conditioning=conditioning,
                sample_rate=sample_rate,
                high_band_hz=high_band_hz,
            )
            audio_path = record_dir / f"{str(route['label'])}.wav"
            spectrogram_path = record_dir / f"{str(route['label'])}.linear_spectrogram.png"
            write_waveform_int16(audio_path, decoded_waveform, sample_rate=sample_rate)
            save_linear_spectrogram_png(
                waveform=decoded_waveform,
                sample_rate=sample_rate,
                output_path=spectrogram_path,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            route_rows.append(
                {
                    "label": str(route["label"]),
                    "description": str(route["description"]),
                    "use_predicted_activity_gate": bool(route["use_predicted_activity_gate"]),
                    "predicted_activity_gate_apply_mode": resolved_apply_mode,
                    "audio_path": audio_path.as_posix(),
                    "spectrogram_path": spectrogram_path.as_posix(),
                    "vuv_summary": decoded_vuv_summary,
                }
            )

        aligned_spectrogram_path = record_dir / "aligned_target.linear_spectrogram.png"
        waveform_frames_spectrogram_path = record_dir / "waveform_frames.linear_spectrogram.png"
        save_linear_spectrogram_png(
            waveform=aligned_waveform,
            sample_rate=sample_rate,
            output_path=aligned_spectrogram_path,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        waveform_frames_waveform = reconstruct_waveform_from_frames(
            waveform_frames=waveform_frames,
            frame_length=frame_length,
            hop_length=hop_length,
            frame_gains=None,
            frame_gain_floor=0.0,
            frame_gain_smoothing_frames=0,
            frame_gain_apply_mode="pre_overlap_add",
        ).detach().cpu().to(torch.float32)
        save_linear_spectrogram_png(
            waveform=waveform_frames_waveform,
            sample_rate=sample_rate,
            output_path=waveform_frames_spectrogram_path,
            frame_length=frame_length,
            hop_length=hop_length,
        )

        diagnosis = diagnose_record_decode_projection(
            aligned_vuv_summary=aligned_vuv_summary,
            waveform_frames_vuv_summary=waveform_frames_vuv_summary,
            route_rows=route_rows,
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
                "predicted_activity_summary": {
                    "mean": round(float(predicted_activity.mean().item()), 6),
                    "std": round(float(predicted_activity.std(unbiased=False).item()), 6),
                    "min": round(float(predicted_activity.min().item()), 6),
                    "max": round(float(predicted_activity.max().item()), 6),
                    "frame_gain_floor": float(frame_gain_floor),
                    "frame_gain_smoothing_frames": int(frame_gain_smoothing_frames),
                },
                "stage_spectrogram_paths": {
                    "aligned_target": aligned_spectrogram_path.as_posix(),
                    "waveform_frames": waveform_frames_spectrogram_path.as_posix(),
                },
                "vuv_summaries": {
                    "aligned": aligned_vuv_summary,
                    "waveform_frames": waveform_frames_vuv_summary,
                    "decoded_no_gate": dict(route_rows[0]["vuv_summary"]),
                    "decoded_pre_ola_gate": dict(route_rows[1]["vuv_summary"]),
                    "decoded_post_ola_gate": dict(route_rows[2]["vuv_summary"]),
                },
                "routes": route_rows,
                "diagnosis": diagnosis,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_vuv_decode_projection_review_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "aggregates": build_decode_projection_aggregates(per_record_rows),
        "diagnosis": diagnose_decode_projection_review(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This review-slice probe keeps the same waveform_frames and decomposes only the downstream decode route.",
            "decoded_no_gate isolates Hann overlap-add without predicted activity gating.",
            "decoded_pre_ola_gate and decoded_post_ola_gate test whether gate application mode adds extra vuv separation loss after overlap-add.",
        ],
    }
    json_path = output_dir / "stage5_vuv_decode_projection_review.json"
    md_path = output_dir / "stage5_vuv_decode_projection_review.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_decode_projection_review_markdown(summary), encoding="utf-8", newline="\n")


def diagnose_record_decode_projection(
    *,
    aligned_vuv_summary: dict[str, float],
    waveform_frames_vuv_summary: dict[str, float],
    route_rows: list[dict[str, object]],
) -> dict[str, object]:
    aligned_gap = float(aligned_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    waveform_gap = float(waveform_frames_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    route_map = {str(row["label"]): dict(row) for row in route_rows}
    no_gate_gap = float(dict(route_map.get("decoded_no_gate", {})).get("vuv_summary", {}).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    pre_gap = float(dict(route_map.get("decoded_pre_ola_gate", {})).get("vuv_summary", {}).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
    post_gap = float(dict(route_map.get("decoded_post_ola_gate", {})).get("vuv_summary", {}).get("unvoiced_minus_voiced_high_band_ratio", 0.0))

    if aligned_gap > 0.0 and waveform_gap <= 0.0:
        primary = "waveform_frames_vuv_not_ready_for_decode_probe"
    elif aligned_gap > 0.0 and no_gate_gap <= 0.0 and waveform_gap > 0.0:
        primary = "ola_decode_vuv_separation_lost_before_predicted_gate"
    elif no_gate_gap > 0.0 and pre_gap <= 0.0 and post_gap <= 0.0:
        primary = "predicted_activity_gate_vuv_separation_lost_after_no_gate_decode"
    elif no_gate_gap > 0.0 and pre_gap > 0.0 and post_gap <= 0.0:
        primary = "post_ola_envelope_vuv_separation_lost_after_pre_gate_decode"
    else:
        primary = "needs_manual_review"

    secondary: list[str] = []
    if pre_gap < no_gate_gap:
        secondary.append("pre_overlap_add_reduces_vuv_gap")
    if post_gap < no_gate_gap:
        secondary.append("post_ola_envelope_reduces_vuv_gap")
    if post_gap < pre_gap:
        secondary.append("post_ola_envelope_worse_than_pre_overlap_add")
    return {
        "primary_localization": primary,
        "secondary_localizations": secondary,
    }


def build_decode_projection_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    aligned = []
    waveform = []
    no_gate = []
    pre_gate = []
    post_gate = []
    for record in records:
        vuv_summaries = dict(record.get("vuv_summaries", {}))
        aligned.append(float(dict(vuv_summaries.get("aligned", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        waveform.append(float(dict(vuv_summaries.get("waveform_frames", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        no_gate.append(float(dict(vuv_summaries.get("decoded_no_gate", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        pre_gate.append(float(dict(vuv_summaries.get("decoded_pre_ola_gate", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
        post_gate.append(float(dict(vuv_summaries.get("decoded_post_ola_gate", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0)))
    return {
        "aligned_vuv_high_band_ratio_mean": round(mean_or_zero(aligned), 6),
        "waveform_frames_vuv_high_band_ratio_mean": round(mean_or_zero(waveform), 6),
        "decoded_no_gate_vuv_high_band_ratio_mean": round(mean_or_zero(no_gate), 6),
        "decoded_pre_ola_gate_vuv_high_band_ratio_mean": round(mean_or_zero(pre_gate), 6),
        "decoded_post_ola_gate_vuv_high_band_ratio_mean": round(mean_or_zero(post_gate), 6),
        "waveform_frames_vuv_nonpositive_count": sum(1 for value in waveform if value <= 0.0),
        "decoded_no_gate_vuv_nonpositive_count": sum(1 for value in no_gate if value <= 0.0),
        "decoded_pre_ola_gate_vuv_nonpositive_count": sum(1 for value in pre_gate if value <= 0.0),
        "decoded_post_ola_gate_vuv_nonpositive_count": sum(1 for value in post_gate if value <= 0.0),
    }


def diagnose_decode_projection_review(records: list[dict[str, object]]) -> dict[str, object]:
    primary_counts: dict[str, int] = {}
    for record in records:
        primary = str(dict(record.get("diagnosis", {})).get("primary_localization", "missing"))
        primary_counts[primary] = primary_counts.get(primary, 0) + 1

    aggregates = build_decode_projection_aggregates(records)
    waveform_mean = float(aggregates["waveform_frames_vuv_high_band_ratio_mean"])
    no_gate_mean = float(aggregates["decoded_no_gate_vuv_high_band_ratio_mean"])
    pre_mean = float(aggregates["decoded_pre_ola_gate_vuv_high_band_ratio_mean"])
    post_mean = float(aggregates["decoded_post_ola_gate_vuv_high_band_ratio_mean"])
    if waveform_mean > 0.0 and no_gate_mean <= 0.0:
        primary = "ola_decode_vuv_separation_lost_before_predicted_gate"
    elif no_gate_mean > 0.0 and pre_mean <= 0.0 and post_mean <= 0.0:
        primary = "predicted_activity_gate_vuv_separation_lost_after_no_gate_decode"
    elif no_gate_mean > 0.0 and pre_mean > 0.0 and post_mean <= 0.0:
        primary = "post_ola_envelope_vuv_separation_lost_after_pre_gate_decode"
    elif waveform_mean <= 0.0:
        primary = "waveform_frames_vuv_not_ready_for_decode_probe"
    else:
        primary = "needs_manual_review"
    return {
        "primary_diagnosis": primary,
        "primary_localization_counts": primary_counts,
    }


def render_decode_projection_review_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Vuv Decode-Projection Review Probe",
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
        "decoded_no_gate_vuv_high_band_ratio_mean",
        "decoded_pre_ola_gate_vuv_high_band_ratio_mean",
        "decoded_post_ola_gate_vuv_high_band_ratio_mean",
        "waveform_frames_vuv_nonpositive_count",
        "decoded_no_gate_vuv_nonpositive_count",
        "decoded_pre_ola_gate_vuv_nonpositive_count",
        "decoded_post_ola_gate_vuv_nonpositive_count",
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
        lines.append(
            "  - decoded_no_gate high-band vuv gap: "
            f"`{dict(vuv_summaries.get('decoded_no_gate', {})).get('unvoiced_minus_voiced_high_band_ratio', 0.0)}`"
        )
        lines.append(
            "  - decoded_pre_ola_gate high-band vuv gap: "
            f"`{dict(vuv_summaries.get('decoded_pre_ola_gate', {})).get('unvoiced_minus_voiced_high_band_ratio', 0.0)}`"
        )
        lines.append(
            "  - decoded_post_ola_gate high-band vuv gap: "
            f"`{dict(vuv_summaries.get('decoded_post_ola_gate', {})).get('unvoiced_minus_voiced_high_band_ratio', 0.0)}`"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- This probe isolates decode-side vuv loss after waveform_frames rather than re-testing the upstream carrier path.",
            "- decoded_no_gate shows whether Hann overlap-add alone erases the recovered vuv separation.",
            "- decoded_pre_ola_gate and decoded_post_ola_gate show whether the predicted-activity gate worsens or explains the remaining loss.",
        ]
    )
    return "\n".join(lines) + "\n"
