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
from v5vc.stage5_speech_emergence_probe import frame_waveform_sequence
from v5vc.stage5_source_filter_probe import mean_or_zero, sanitize_record_id
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
class NoiseHiddenResidualVariant:
    label: str
    description: str
    mode: str
    strength: float


NOISE_HIDDEN_RESIDUAL_VARIANTS = [
    NoiseHiddenResidualVariant(
        label="baseline",
        description="Checkpoint baseline without any residual-path intervention.",
        mode="baseline",
        strength=0.0,
    ),
    NoiseHiddenResidualVariant(
        label="target_unvoiced_residual_gain300",
        description="Positive control: 3.0x residual-shape delta on target-side unvoiced frames only.",
        mode="target_unvoiced_mask",
        strength=3.0,
    ),
    NoiseHiddenResidualVariant(
        label="noise_hidden_rms_soft_residual_gain300",
        description="Runtime-only residual scaling using 1 + 2 * normalized noise_hidden frame RMS.",
        mode="noise_hidden_rms_soft",
        strength=2.0,
    ),
    NoiseHiddenResidualVariant(
        label="noise_hidden_rms_soft_residual_gain500",
        description="Runtime-only stronger residual scaling using 1 + 4 * normalized noise_hidden frame RMS.",
        mode="noise_hidden_rms_soft",
        strength=4.0,
    ),
    NoiseHiddenResidualVariant(
        label="noise_hidden_delta_soft_residual_gain500",
        description="Runtime-only residual scaling using 1 + 4 * normalized noise_hidden frame-delta magnitude.",
        mode="noise_hidden_delta_soft",
        strength=4.0,
    ),
    NoiseHiddenResidualVariant(
        label="noise_hidden_rmsdelta_soft_residual_gain500",
        description="Runtime-only residual scaling using 1 + 4 * averaged normalized noise_hidden RMS and delta signals.",
        mode="noise_hidden_rmsdelta_soft",
        strength=4.0,
    ),
]


def analyze_stage5_nores_vuv_noise_hidden_residual_probe(
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
        noise_hidden = outputs["noise_hidden"].detach().cpu().to(torch.float32)
        aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32)

        common_frame_count = min(
            int(base_logits.shape[0]),
            int(residual_shape_delta.shape[0]),
            int(predicted_activity.shape[0]),
            int(noise_hidden.shape[0]),
        )
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for noise-hidden residual probe record: {record_id}")
        base_logits = base_logits[:common_frame_count]
        residual_shape_delta = residual_shape_delta[:common_frame_count]
        predicted_activity = predicted_activity[:common_frame_count]
        noise_hidden = noise_hidden[:common_frame_count]

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
            raise ValueError(f"Unable to derive vuv conditioning for noise-hidden residual probe record: {record_id}")

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

        noise_hidden_signal_summary = summarize_noise_hidden_signals(noise_hidden)

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
        for variant in NOISE_HIDDEN_RESIDUAL_VARIANTS:
            variant_logits = build_noise_hidden_variant_logits(
                base_logits=base_logits,
                residual_shape_delta=residual_shape_delta,
                noise_hidden=noise_hidden,
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
            variant_asset_paths = save_noise_hidden_variant_assets(
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
                "noise_hidden_signal_summary": noise_hidden_signal_summary,
                "aligned_vuv_summary": aligned_vuv_summary,
                "variants": variant_rows,
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_vuv_noise_hidden_residual_probe_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "variants": [variant.__dict__ for variant in NOISE_HIDDEN_RESIDUAL_VARIANTS],
        "aggregates": build_noise_hidden_aggregates(per_record_rows),
        "diagnosis": diagnose_noise_hidden_probe(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This probe asks whether noise_hidden already carries a deployable unvoiced emphasis signal even though the current noise_gate-based residual rules failed.",
            "If noise_hidden-derived residual scaling approaches the target-mask positive control, the next structural probe should favor an explicit noise-hidden-to-residual path rather than more gate tweaks.",
        ],
    }
    json_path = output_dir / "stage5_vuv_noise_hidden_residual_probe.json"
    md_path = output_dir / "stage5_vuv_noise_hidden_residual_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_noise_hidden_probe_markdown(summary), encoding="utf-8", newline="\n")


def summarize_noise_hidden_signals(noise_hidden: torch.Tensor) -> dict[str, float]:
    noise_hidden_cpu = noise_hidden.detach().cpu().to(torch.float32)
    frame_rms = noise_hidden_cpu.pow(2).mean(dim=-1).sqrt()
    frame_delta = frame_rms.new_zeros(frame_rms.shape)
    if int(frame_rms.shape[0]) > 1:
        frame_delta[1:] = (frame_rms[1:] - frame_rms[:-1]).abs()
    return {
        "noise_hidden_frame_rms_mean": round(float(frame_rms.mean().item()), 6),
        "noise_hidden_frame_rms_std": round(float(frame_rms.std(unbiased=False).item()), 6),
        "noise_hidden_frame_delta_mean": round(float(frame_delta.mean().item()), 6),
        "noise_hidden_frame_delta_std": round(float(frame_delta.std(unbiased=False).item()), 6),
    }


def build_noise_hidden_variant_logits(
    *,
    base_logits: torch.Tensor,
    residual_shape_delta: torch.Tensor,
    noise_hidden: torch.Tensor,
    conditioning: dict[str, object],
    variant: NoiseHiddenResidualVariant,
) -> torch.Tensor:
    if variant.mode == "baseline":
        return base_logits + residual_shape_delta
    if variant.mode == "target_unvoiced_mask":
        unvoiced_mask = conditioning["unvoiced_mask"].detach().cpu().to(torch.bool).view(-1, 1)
        adjusted_residual = torch.where(
            unvoiced_mask,
            residual_shape_delta * float(variant.strength),
            residual_shape_delta,
        )
        return base_logits + adjusted_residual

    signal = build_noise_hidden_signal(noise_hidden=noise_hidden, mode=variant.mode)
    scale = 1.0 + float(variant.strength) * signal.view(-1, 1)
    adjusted_residual = residual_shape_delta * scale
    return base_logits + adjusted_residual


def build_noise_hidden_signal(
    *,
    noise_hidden: torch.Tensor,
    mode: str,
) -> torch.Tensor:
    noise_hidden_cpu = noise_hidden.detach().cpu().to(torch.float32)
    frame_rms = noise_hidden_cpu.pow(2).mean(dim=-1).sqrt()
    norm_rms = normalize_1d_signal(frame_rms)
    frame_delta = frame_rms.new_zeros(frame_rms.shape)
    if int(frame_rms.shape[0]) > 1:
        frame_delta[1:] = (frame_rms[1:] - frame_rms[:-1]).abs()
    norm_delta = normalize_1d_signal(frame_delta)
    if mode == "noise_hidden_rms_soft":
        return norm_rms
    if mode == "noise_hidden_delta_soft":
        return norm_delta
    if mode == "noise_hidden_rmsdelta_soft":
        return 0.5 * (norm_rms + norm_delta)
    raise ValueError(f"Unsupported noise-hidden residual variant mode: {mode}")


def normalize_1d_signal(values: torch.Tensor) -> torch.Tensor:
    values_cpu = values.detach().cpu().to(torch.float32).view(-1)
    min_value = float(values_cpu.min().item()) if int(values_cpu.numel()) > 0 else 0.0
    max_value = float(values_cpu.max().item()) if int(values_cpu.numel()) > 0 else 0.0
    span = max_value - min_value
    if span <= 1.0e-8:
        return torch.zeros_like(values_cpu)
    return (values_cpu - min_value) / span


def save_noise_hidden_variant_assets(
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


def build_noise_hidden_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    variants_summary: dict[str, dict[str, object]] = {}
    for variant in NOISE_HIDDEN_RESIDUAL_VARIANTS:
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


def diagnose_noise_hidden_probe(records: list[dict[str, object]]) -> dict[str, object]:
    variants = dict(build_noise_hidden_aggregates(records).get("variants", {}))
    oracle = dict(variants.get("target_unvoiced_residual_gain300", {}))
    best_runtime_label = "baseline"
    best_runtime_value = float(dict(variants.get("baseline", {})).get("waveform_frames_vuv_high_band_ratio_mean", 0.0))
    for label, payload in variants.items():
        if label in {"baseline", "target_unvoiced_residual_gain300"}:
            continue
        waveform_value = float(dict(payload).get("waveform_frames_vuv_high_band_ratio_mean", 0.0))
        if waveform_value > best_runtime_value:
            best_runtime_value = waveform_value
            best_runtime_label = str(label)
    oracle_value = float(oracle.get("waveform_frames_vuv_high_band_ratio_mean", 0.0))
    gap_to_oracle = float(oracle_value - best_runtime_value)
    if best_runtime_value <= 0.0 and oracle_value > 0.0:
        primary = "noise_hidden_signal_not_yet_exposed_as_usable_unvoiced_residual_control"
    elif gap_to_oracle > 0.002:
        primary = "noise_hidden_has_partial_but_suboracle_unvoiced_residual_leverage"
    else:
        primary = "noise_hidden_is_close_to_oracle_for_unvoiced_residual_control"
    return {
        "primary_diagnosis": primary,
        "best_noise_hidden_variant_by_waveform_frames_vuv_gap": best_runtime_label,
        "best_noise_hidden_waveform_frames_vuv_gap": round(best_runtime_value, 6),
        "oracle_target_unvoiced_waveform_frames_vuv_gap": round(oracle_value, 6),
        "noise_hidden_gap_to_oracle": round(gap_to_oracle, 6),
    }


def render_noise_hidden_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Vuv Noise-Hidden Residual Probe",
        "",
        "## Summary",
        f"- review bundle: `{summary['review_bundle_path']}`",
        f"- source family: `{summary.get('source_family', '')}`",
        f"- record count: `{summary.get('record_count', 0)}`",
        f"- primary diagnosis: `{dict(summary.get('diagnosis', {})).get('primary_diagnosis', 'unknown')}`",
        f"- best noise-hidden variant: `{dict(summary.get('diagnosis', {})).get('best_noise_hidden_variant_by_waveform_frames_vuv_gap', 'unknown')}`",
        "",
        "## Aggregate Variants",
    ]
    variants = dict(dict(summary.get("aggregates", {})).get("variants", {}))
    for variant in NOISE_HIDDEN_RESIDUAL_VARIANTS:
        payload = dict(variants.get(variant.label, {}))
        lines.append(f"- `{variant.label}`")
        lines.append(
            f"  - waveform_frames vuv high-band mean: `{payload.get('waveform_frames_vuv_high_band_ratio_mean')}`"
        )
        lines.append(f"  - decoded vuv high-band mean: `{payload.get('decoded_vuv_high_band_ratio_mean')}`")
        lines.append(f"  - auto_reject_count: `{payload.get('auto_reject_count')}`")
    lines.extend(["", "## Records"])
    for record in list(summary.get("records", [])):
        lines.append(f"- `{record['record_id']}`")
        lines.append(
            "  - noise_hidden_frame_rms_std: "
            f"`{dict(record.get('noise_hidden_signal_summary', {})).get('noise_hidden_frame_rms_std')}`"
        )
        lines.append(
            "  - noise_hidden_frame_delta_std: "
            f"`{dict(record.get('noise_hidden_signal_summary', {})).get('noise_hidden_frame_delta_std')}`"
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
            "- This probe tests deployable runtime signals from `noise_hidden`, not target-side oracle masks and not the already-failed gate heads.",
            "",
        ]
    )
    return "\n".join(lines)
