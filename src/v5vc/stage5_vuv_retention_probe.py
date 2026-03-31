from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import (
    assess_stage5_decoded_buzz_reject,
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


@dataclass(frozen=True)
class RetentionVariant:
    label: str
    description: str
    voiced_centered_scale: float = 1.0
    unvoiced_centered_scale: float = 1.0
    residual_voiced_scale: float = 1.0
    residual_unvoiced_scale: float = 1.0


RETENTION_VARIANTS = [
    RetentionVariant(
        label="baseline",
        description="Checkpoint baseline without any waveform-logit intervention.",
    ),
    RetentionVariant(
        label="unvoiced_centered_gain150",
        description="Increase centered waveform-frame-logit contrast on target-side unvoiced frames by 1.5x.",
        unvoiced_centered_scale=1.5,
    ),
    RetentionVariant(
        label="unvoiced_centered_gain200",
        description="Increase centered waveform-frame-logit contrast on target-side unvoiced frames by 2.0x.",
        unvoiced_centered_scale=2.0,
    ),
    RetentionVariant(
        label="voiced_shrink090__unvoiced_centered_gain150",
        description="Shrink voiced centered logit contrast to 0.9x while boosting unvoiced centered contrast to 1.5x.",
        voiced_centered_scale=0.9,
        unvoiced_centered_scale=1.5,
    ),
    RetentionVariant(
        label="residual_unvoiced_gain300",
        description="Scale residual-shape delta by 3.0x on target-side unvoiced frames only.",
        residual_unvoiced_scale=3.0,
    ),
    RetentionVariant(
        label="residual_unvoiced_gain300__unvoiced_centered_gain150",
        description="Combine 3.0x residual-shape unvoiced scaling with 1.5x unvoiced centered logit contrast.",
        unvoiced_centered_scale=1.5,
        residual_unvoiced_scale=3.0,
    ),
]


def analyze_stage5_nores_vuv_retention_probe(
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

        sample_rate = int(runtime["sample_rate"])
        frame_length = int(runtime["frame_length"])
        hop_length = int(runtime["hop_length"])
        predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"]).detach().cpu().to(torch.float32)
        base_logits = outputs["waveform_decoder_base_logits"].detach().cpu().to(torch.float32)
        residual_shape_delta = outputs.get(
            "waveform_residual_shape_delta",
            torch.zeros_like(outputs["waveform_decoder_base_logits"]),
        ).detach().cpu().to(torch.float32)
        aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32)

        common_frame_count = min(
            int(base_logits.shape[0]),
            int(residual_shape_delta.shape[0]),
            int(predicted_activity.shape[0]),
        )
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for retention probe record: {record_id}")
        base_logits = base_logits[:common_frame_count]
        residual_shape_delta = residual_shape_delta[:common_frame_count]
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
            raise ValueError(f"Unable to derive vuv conditioning for retention probe record: {record_id}")

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

        resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(
            str(export_entry.get("waveform_decode", {}).get("predicted_activity_gate_apply_mode", "post_ola_envelope"))
        )
        frame_gain_floor = float(export_entry.get("waveform_decode", {}).get("predicted_activity_gate_floor", 0.0))
        frame_gain_smoothing_frames = int(
            export_entry.get("waveform_decode", {}).get("predicted_activity_gate_smoothing_frames", 0)
        )
        use_predicted_activity_gate = bool(export_entry.get("waveform_decode", {}).get("use_predicted_activity_gate", True))

        record_dir = output_dir / sanitize_record_id(record_id)
        record_dir.mkdir(parents=True, exist_ok=True)
        variant_rows = []
        for variant in RETENTION_VARIANTS:
            variant_logits = build_variant_waveform_frame_logits(
                base_logits=base_logits,
                residual_shape_delta=residual_shape_delta,
                conditioning=conditioning,
                variant=variant,
            )
            variant_frames = torch.tanh(variant_logits)
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=variant_frames,
                frame_length=frame_length,
                hop_length=hop_length,
                frame_gains=predicted_activity if use_predicted_activity_gate else None,
                frame_gain_floor=frame_gain_floor,
                frame_gain_smoothing_frames=frame_gain_smoothing_frames,
                frame_gain_apply_mode=resolved_apply_mode,
            ).detach().cpu().to(torch.float32)
            target_length = min(int(decoded_waveform.shape[0]), int(aligned_waveform.shape[0]))
            decoded_waveform = decoded_waveform[:target_length]
            aligned_waveform_variant = aligned_waveform[:target_length]
            decoded_frames = frame_waveform_sequence(
                waveform=decoded_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                target_frame_count=common_frame_count,
            )
            waveform_frames_vuv_summary = summarize_vuv_conditioned_frame_sequence(
                analysis_frames=variant_frames,
                conditioning=conditioning,
                sample_rate=sample_rate,
                high_band_hz=high_band_hz,
            )
            decoded_vuv_summary = summarize_vuv_conditioned_frame_sequence(
                analysis_frames=decoded_frames,
                conditioning=conditioning,
                sample_rate=sample_rate,
                high_band_hz=high_band_hz,
            )
            buzz_assessment = assess_stage5_decoded_buzz_reject(
                decoded_waveform=decoded_waveform,
                aligned_target=aligned_waveform_variant,
                predicted_activity=predicted_activity,
                sample_rate=sample_rate,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            variant_asset_paths = save_variant_assets(
                record_dir=record_dir,
                variant_label=variant.label,
                decoded_waveform=decoded_waveform,
                sample_rate=sample_rate,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            variant_rows.append(
                {
                    "variant_label": variant.label,
                    "description": variant.description,
                    "waveform_frames_vuv_summary": waveform_frames_vuv_summary,
                    "decoded_vuv_summary": decoded_vuv_summary,
                    "buzz_reject_assessment": buzz_assessment,
                    "decoded_asset_paths": variant_asset_paths,
                }
            )

        per_record_rows.append(
            {
                "record_id": record_id,
                "split_name": str(review_record.get("split_name", export_entry.get("split_name", ""))),
                "status": str(review_record.get("status", "unknown")),
                "checkpoint_path": checkpoint_path.as_posix(),
                "training_package_path": package_path.as_posix(),
                "conditioning_summary": {
                    "frame_count": int(conditioning["frame_count"]),
                    "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
                    "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
                    "voicing_source": str(
                        "periodic_gate_target"
                        if batch.get("periodic_gate_target") is not None
                        else conditioning.get("voicing_source", "missing")
                    ),
                },
                "aligned_vuv_summary": aligned_vuv_summary,
                "variants": variant_rows,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_vuv_retention_probe_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "variants": [variant.__dict__ for variant in RETENTION_VARIANTS],
        "aggregates": build_retention_aggregates(per_record_rows),
        "diagnosis": diagnose_retention_probe(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This is a review-slice counterfactual probe only; it does not modify the checkpoint and only perturbs waveform_frame_logits after the current base-logits and residual-shape path is produced.",
            "The target-side vuv mask is used only for localization on the same reviewed records, not as a deployable runtime signal.",
            "If even aggressive unvoiced emphasis variants stay flat, the practical lesson is that the current path is missing a usable unvoiced direction rather than only under-scaling it.",
        ],
    }
    json_path = output_dir / "stage5_vuv_retention_probe.json"
    md_path = output_dir / "stage5_vuv_retention_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_retention_probe_markdown(summary), encoding="utf-8", newline="\n")


def build_variant_waveform_frame_logits(
    *,
    base_logits: torch.Tensor,
    residual_shape_delta: torch.Tensor,
    conditioning: dict[str, object],
    variant: RetentionVariant,
) -> torch.Tensor:
    voiced_mask = conditioning["voiced_mask"].detach().cpu().to(torch.bool).view(-1, 1)
    unvoiced_mask = conditioning["unvoiced_mask"].detach().cpu().to(torch.bool).view(-1, 1)

    adjusted_residual = residual_shape_delta.clone()
    adjusted_residual = torch.where(
        voiced_mask,
        adjusted_residual * float(variant.residual_voiced_scale),
        adjusted_residual,
    )
    adjusted_residual = torch.where(
        unvoiced_mask,
        adjusted_residual * float(variant.residual_unvoiced_scale),
        adjusted_residual,
    )
    logits = base_logits + adjusted_residual
    frame_mean = logits.mean(dim=-1, keepdim=True)
    centered = logits - frame_mean
    adjusted_logits = logits.clone()
    if abs(float(variant.voiced_centered_scale) - 1.0) > 1.0e-9:
        voiced_adjusted = frame_mean + float(variant.voiced_centered_scale) * centered
        adjusted_logits = torch.where(voiced_mask, voiced_adjusted, adjusted_logits)
    if abs(float(variant.unvoiced_centered_scale) - 1.0) > 1.0e-9:
        unvoiced_adjusted = frame_mean + float(variant.unvoiced_centered_scale) * centered
        adjusted_logits = torch.where(unvoiced_mask, unvoiced_adjusted, adjusted_logits)
    return adjusted_logits


def save_variant_assets(
    *,
    record_dir: Path,
    variant_label: str,
    decoded_waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> dict[str, str]:
    audio_path = record_dir / f"{variant_label}.decoded.wav"
    spectrogram_path = record_dir / f"{variant_label}.decoded.linear_spectrogram.png"
    write_waveform_int16(audio_path, decoded_waveform, sample_rate=sample_rate)
    save_linear_spectrogram_png(
        waveform=decoded_waveform,
        sample_rate=sample_rate,
        output_path=spectrogram_path,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    return {
        "decoded_audio_path": audio_path.as_posix(),
        "decoded_spectrogram_path": spectrogram_path.as_posix(),
    }


def build_retention_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    variants_summary: dict[str, dict[str, object]] = {}
    for variant in RETENTION_VARIANTS:
        waveform_gap_values = []
        decoded_gap_values = []
        auto_reject_count = 0
        review_required_count = 0
        for record in records:
            matched = next(
                (item for item in list(record.get("variants", [])) if item.get("variant_label") == variant.label),
                None,
            )
            if matched is None:
                continue
            waveform_gap_values.append(
                float(
                    dict(matched.get("waveform_frames_vuv_summary", {})).get(
                        "unvoiced_minus_voiced_high_band_ratio",
                        0.0,
                    )
                )
            )
            decoded_gap_values.append(
                float(dict(matched.get("decoded_vuv_summary", {})).get("unvoiced_minus_voiced_high_band_ratio", 0.0))
            )
            assessment = dict(matched.get("buzz_reject_assessment", {}))
            if bool(assessment.get("auto_reject", False)):
                auto_reject_count += 1
            if str(assessment.get("status", "")) == "review_required":
                review_required_count += 1
        variants_summary[variant.label] = {
            "waveform_frames_vuv_high_band_ratio_mean": round(mean_or_zero(waveform_gap_values), 6),
            "decoded_vuv_high_band_ratio_mean": round(mean_or_zero(decoded_gap_values), 6),
            "auto_reject_count": int(auto_reject_count),
            "review_required_count": int(review_required_count),
        }
    return {"variants": variants_summary}


def diagnose_retention_probe(records: list[dict[str, object]]) -> dict[str, object]:
    baseline_waveform_mean = 0.0
    best_variant = "baseline"
    best_waveform_mean = -1.0e9
    variants = build_retention_aggregates(records).get("variants", {})
    if isinstance(variants, dict):
        for label, payload in variants.items():
            waveform_mean = float(dict(payload).get("waveform_frames_vuv_high_band_ratio_mean", 0.0))
            if label == "baseline":
                baseline_waveform_mean = waveform_mean
            if waveform_mean > best_waveform_mean:
                best_waveform_mean = waveform_mean
                best_variant = str(label)
    improvement = float(best_waveform_mean - baseline_waveform_mean)
    if best_variant == "baseline" or improvement <= 0.002:
        primary = "simple_unvoiced_emphasis_not_enough"
    else:
        primary = "simple_unvoiced_emphasis_has_partial_leverage"
    return {
        "primary_diagnosis": primary,
        "best_variant_by_waveform_frames_vuv_gap": best_variant,
        "best_waveform_frames_vuv_gap_gain_vs_baseline": round(improvement, 6),
    }


def render_retention_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Vuv Retention Probe",
        "",
        "## Summary",
        f"- review bundle: `{summary['review_bundle_path']}`",
        f"- source family: `{summary.get('source_family', '')}`",
        f"- record count: `{summary.get('record_count', 0)}`",
        f"- primary diagnosis: `{dict(summary.get('diagnosis', {})).get('primary_diagnosis', 'unknown')}`",
        f"- best variant by waveform-frames vuv gap: `{dict(summary.get('diagnosis', {})).get('best_variant_by_waveform_frames_vuv_gap', 'unknown')}`",
        "",
        "## Aggregate Variants",
    ]
    variants = dict(dict(summary.get("aggregates", {})).get("variants", {}))
    for variant in RETENTION_VARIANTS:
        payload = dict(variants.get(variant.label, {}))
        lines.append(f"- `{variant.label}`")
        lines.append(
            f"  - waveform_frames vuv high-band mean: `{payload.get('waveform_frames_vuv_high_band_ratio_mean')}`"
        )
        lines.append(f"  - decoded vuv high-band mean: `{payload.get('decoded_vuv_high_band_ratio_mean')}`")
        lines.append(f"  - auto_reject_count: `{payload.get('auto_reject_count')}`")
        lines.append(f"  - review_required_count: `{payload.get('review_required_count')}`")
    lines.extend(["", "## Records"])
    for record in list(summary.get("records", [])):
        lines.append(f"- `{record['record_id']}`")
        lines.append(
            "  - aligned high-band vuv gap: "
            f"`{dict(record.get('aligned_vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio')}`"
        )
        for variant in list(record.get("variants", [])):
            lines.append(
                "  - "
                f"`{variant['variant_label']}` waveform/decoded vuv gap: "
                f"`{dict(variant.get('waveform_frames_vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio')}` / "
                f"`{dict(variant.get('decoded_vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio')}`"
            )
    lines.extend(
        [
            "",
            "## Notes",
            "- This probe is only a bounded counterfactual on the reviewed slice and does not claim a training-free fix.",
            "- If a variant improves waveform-frames vuv gap but decoded buzz status stays flat, the route may still need a real structural change rather than a simple gain rule.",
            "",
        ]
    )
    return "\n".join(lines)
