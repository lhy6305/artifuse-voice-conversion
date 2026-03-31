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
from v5vc.offline_vocoder_scaffold import resolve_residual_shape_branch_condition_delta
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_speech_emergence_probe import frame_waveform_sequence
from v5vc.stage5_source_filter_probe import mean_or_zero, sanitize_record_id
from v5vc.stage5_vuv_noise_hidden_residual_probe import (
    build_noise_hidden_signal,
    summarize_noise_hidden_signals,
)
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
class NoiseHiddenResidualStructureVariant:
    label: str
    description: str
    mode: str
    strength: float = 0.0


NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS = [
    NoiseHiddenResidualStructureVariant(
        label="baseline",
        description="Checkpoint baseline without any residual-path intervention.",
        mode="baseline",
    ),
    NoiseHiddenResidualStructureVariant(
        label="target_unvoiced_residual_gain300",
        description="Positive control: 3.0x residual-shape delta on target-side unvoiced frames only.",
        mode="target_unvoiced_mask",
        strength=3.0,
    ),
    NoiseHiddenResidualStructureVariant(
        label="noise_hidden_rms_soft_residual_gain500",
        description="Best prior runtime-only comparator: 1 + 4 * normalized noise_hidden frame RMS.",
        mode="noise_hidden_rms_soft",
        strength=4.0,
    ),
    NoiseHiddenResidualStructureVariant(
        label="residual_branch_fused_from_noise_hidden",
        description="Recompute residual-shape adapter features with noise_hidden in the fused slot.",
        mode="residual_branch_fused_from_noise_hidden",
    ),
    NoiseHiddenResidualStructureVariant(
        label="residual_branch_branchmean_from_noise_hidden",
        description="Recompute residual-shape adapter features with noise_hidden in the branch-mean slot.",
        mode="residual_branch_branchmean_from_noise_hidden",
    ),
    NoiseHiddenResidualStructureVariant(
        label="residual_branch_noise_hidden_vs_periodic",
        description="Recompute residual-shape adapter features as explicit noise_hidden vs periodic_hidden contrast.",
        mode="residual_branch_noise_hidden_vs_periodic",
    ),
    NoiseHiddenResidualStructureVariant(
        label="residual_branch_noise_hidden_only",
        description="Collapse both residual-shape adapter feature slots to noise_hidden alone.",
        mode="residual_branch_noise_hidden_only",
    ),
]


def analyze_stage5_nores_vuv_noise_hidden_residual_structure_probe(
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

        if not bool(getattr(model, "use_residual_shape_branch_condition_adapter", False)):
            raise ValueError(
                "Noise-hidden residual-structure probe requires checkpoints with use_residual_shape_branch_condition_adapter."
            )

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
        periodic_hidden = outputs["periodic_hidden"].detach().cpu().to(torch.float32)
        noise_hidden = outputs["noise_hidden"].detach().cpu().to(torch.float32)
        fused_hidden = outputs["fused_hidden"].detach().cpu().to(torch.float32)
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
            int(periodic_hidden.shape[0]),
            int(noise_hidden.shape[0]),
            int(fused_hidden.shape[0]),
        )
        if common_frame_count <= 0:
            raise ValueError(f"No common frames available for noise-hidden residual-structure probe record: {record_id}")
        periodic_hidden = periodic_hidden[:common_frame_count]
        noise_hidden = noise_hidden[:common_frame_count]
        fused_hidden = fused_hidden[:common_frame_count]
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
            raise ValueError(
                f"Unable to derive vuv conditioning for noise-hidden residual-structure probe record: {record_id}"
            )

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
        for variant in NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS:
            variant_logits, residual_debug = build_noise_hidden_residual_structure_variant_logits(
                model=model,
                base_logits=base_logits,
                residual_shape_delta=residual_shape_delta,
                periodic_hidden=periodic_hidden,
                noise_hidden=noise_hidden,
                fused_hidden=fused_hidden,
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
                    "residual_debug": residual_debug,
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
        "analysis_type": "stage5_vuv_noise_hidden_residual_structure_probe_v1",
        "review_bundle_path": review_bundle_path.as_posix(),
        "audio_export_manifest_paths": [path.as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "variants": [variant.__dict__ for variant in NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS],
        "aggregates": build_structure_probe_aggregates(per_record_rows),
        "diagnosis": diagnose_structure_probe(per_record_rows),
        "records": per_record_rows,
        "notes": [
            "This probe keeps the active checkpoint frozen and recomputes only the residual-shape branch conditioning path with explicit noise_hidden feature routing.",
            "The main question is whether the current residual-shape adapter weights can already respond to a deployable noise-hidden carrier, or whether a new projection path would still be required.",
        ],
    }
    json_path = output_dir / "stage5_vuv_noise_hidden_residual_structure_probe.json"
    md_path = output_dir / "stage5_vuv_noise_hidden_residual_structure_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_structure_probe_markdown(summary), encoding="utf-8", newline="\n")


def build_noise_hidden_residual_structure_variant_logits(
    *,
    model: torch.nn.Module,
    base_logits: torch.Tensor,
    residual_shape_delta: torch.Tensor,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
    conditioning: dict[str, object],
    variant: NoiseHiddenResidualStructureVariant,
) -> tuple[torch.Tensor, dict[str, object]]:
    if variant.mode == "baseline":
        return base_logits + residual_shape_delta, summarize_residual_debug(
            mode=variant.mode,
            residual_shape_delta=residual_shape_delta,
        )
    if variant.mode == "target_unvoiced_mask":
        unvoiced_mask = conditioning["unvoiced_mask"].detach().cpu().to(torch.bool).view(-1, 1)
        adjusted_residual = torch.where(
            unvoiced_mask,
            residual_shape_delta * float(variant.strength),
            residual_shape_delta,
        )
        return base_logits + adjusted_residual, summarize_residual_debug(
            mode=variant.mode,
            residual_shape_delta=adjusted_residual,
        )
    if variant.mode == "noise_hidden_rms_soft":
        signal = build_noise_hidden_signal(noise_hidden=noise_hidden, mode="noise_hidden_rms_soft")
        adjusted_residual = residual_shape_delta * (1.0 + float(variant.strength) * signal.view(-1, 1))
        return base_logits + adjusted_residual, summarize_residual_debug(
            mode=variant.mode,
            residual_shape_delta=adjusted_residual,
            extra_summary={
                "noise_hidden_signal_mean": round(float(signal.mean().item()), 6),
                "noise_hidden_signal_std": round(float(signal.std(unbiased=False).item()), 6),
            },
        )

    rerouted_residual = recompute_residual_shape_delta_from_noise_hidden_structure(
        model=model,
        base_logits=base_logits,
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        fused_hidden=fused_hidden,
        mode=variant.mode,
    )
    return base_logits + rerouted_residual["waveform_residual_shape_delta"], summarize_residual_debug(
        mode=variant.mode,
        residual_shape_delta=rerouted_residual["waveform_residual_shape_delta"],
        extra_summary=rerouted_residual["debug_summary"],
    )


def recompute_residual_shape_delta_from_noise_hidden_structure(
    *,
    model: torch.nn.Module,
    base_logits: torch.Tensor,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
    mode: str,
) -> dict[str, object]:
    adapter = getattr(model, "residual_shape_branch_condition_adapter", None)
    gate_head = getattr(model, "residual_shape_branch_condition_gate", None)
    proj = getattr(model, "residual_shape_branch_condition_proj", None)
    if adapter is None or gate_head is None or proj is None:
        raise RuntimeError("Residual-shape branch-condition adapter modules are not initialized.")

    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    if mode == "residual_branch_fused_from_noise_hidden":
        feature_fused_hidden = noise_hidden
        feature_branch_mean_hidden = branch_mean_hidden
    elif mode == "residual_branch_branchmean_from_noise_hidden":
        feature_fused_hidden = fused_hidden
        feature_branch_mean_hidden = noise_hidden
    elif mode == "residual_branch_noise_hidden_vs_periodic":
        feature_fused_hidden = noise_hidden
        feature_branch_mean_hidden = periodic_hidden
    elif mode == "residual_branch_noise_hidden_only":
        feature_fused_hidden = noise_hidden
        feature_branch_mean_hidden = noise_hidden
    else:
        raise ValueError(f"Unsupported residual-structure variant mode: {mode}")

    residual_shape_features = torch.cat(
        [
            feature_fused_hidden,
            feature_branch_mean_hidden,
            feature_fused_hidden - feature_branch_mean_hidden,
        ],
        dim=-1,
    )
    residual_context = adapter(residual_shape_features)
    residual_gate = torch.sigmoid(gate_head(residual_context))
    residual_shape_delta = resolve_residual_shape_branch_condition_delta(
        delta=torch.tanh(proj(residual_context)),
        reference_frames=base_logits,
        mode=str(getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")),
    )
    if residual_shape_delta is None:
        raise RuntimeError("Residual-shape branch-condition delta unexpectedly resolved to None.")
    waveform_residual_shape_delta = (
        float(getattr(model, "residual_shape_branch_condition_scale", 1.0))
        * residual_gate
        * residual_shape_delta
    )
    return {
        "waveform_residual_shape_delta": waveform_residual_shape_delta.detach().cpu().to(torch.float32),
        "debug_summary": {
            "residual_gate_mean": round(float(residual_gate.mean().item()), 6),
            "residual_gate_std": round(float(residual_gate.std(unbiased=False).item()), 6),
            "feature_fused_rms_mean": round(float(feature_fused_hidden.pow(2).mean(dim=-1).sqrt().mean().item()), 6),
            "feature_branch_mean_rms_mean": round(
                float(feature_branch_mean_hidden.pow(2).mean(dim=-1).sqrt().mean().item()),
                6,
            ),
        },
    }


def summarize_residual_debug(
    *,
    mode: str,
    residual_shape_delta: torch.Tensor,
    extra_summary: dict[str, object] | None = None,
) -> dict[str, object]:
    summary = {
        "mode": mode,
        "residual_delta_abs_mean": round(float(residual_shape_delta.abs().mean().item()), 6),
        "residual_delta_rms_mean": round(float(residual_shape_delta.pow(2).mean(dim=-1).sqrt().mean().item()), 6),
    }
    if extra_summary:
        summary.update(extra_summary)
    return summary


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


def build_structure_probe_aggregates(records: list[dict[str, object]]) -> dict[str, object]:
    variants_summary: dict[str, dict[str, object]] = {}
    for variant in NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS:
        waveform_gap_values = []
        decoded_gap_values = []
        review_required_count = 0
        auto_reject_count = 0
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
            if str(assessment.get("status", "")) == "review_required":
                review_required_count += 1
            if bool(assessment.get("auto_reject", False)):
                auto_reject_count += 1
        variants_summary[variant.label] = {
            "waveform_frames_vuv_high_band_ratio_mean": round(mean_or_zero(waveform_gap_values), 6),
            "decoded_vuv_high_band_ratio_mean": round(mean_or_zero(decoded_gap_values), 6),
            "review_required_count": int(review_required_count),
            "auto_reject_count": int(auto_reject_count),
        }
    return {"variants": variants_summary}


def diagnose_structure_probe(records: list[dict[str, object]]) -> dict[str, object]:
    variants = dict(build_structure_probe_aggregates(records).get("variants", {}))
    baseline_value = float(dict(variants.get("baseline", {})).get("waveform_frames_vuv_high_band_ratio_mean", 0.0))
    oracle_value = float(
        dict(variants.get("target_unvoiced_residual_gain300", {})).get("waveform_frames_vuv_high_band_ratio_mean", 0.0)
    )
    best_scaling_value = float(
        dict(variants.get("noise_hidden_rms_soft_residual_gain500", {})).get("waveform_frames_vuv_high_band_ratio_mean", 0.0)
    )
    best_structural_label = "baseline"
    best_structural_value = baseline_value
    for variant in NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS:
        if not variant.label.startswith("residual_branch_"):
            continue
        waveform_value = float(
            dict(variants.get(variant.label, {})).get("waveform_frames_vuv_high_band_ratio_mean", 0.0)
        )
        if waveform_value > best_structural_value:
            best_structural_value = waveform_value
            best_structural_label = variant.label
    structural_gain_vs_baseline = best_structural_value - baseline_value
    structural_gap_to_scaling = best_scaling_value - best_structural_value
    structural_gap_to_oracle = oracle_value - best_structural_value
    if best_structural_value <= baseline_value + 1.0e-6 and best_scaling_value > baseline_value + 0.001:
        primary = "noise_hidden_signal_exists_but_current_residual_adapter_does_not_unlock_it_via_simple_feature_reroute"
    elif structural_gap_to_scaling <= 0.002:
        primary = "explicit_noise_hidden_to_residual_feature_reroute_is_close_to_best_scaling_counterfactual"
    else:
        primary = "explicit_noise_hidden_to_residual_feature_reroute_has_partial_leverage_but_needs_new_projection"
    return {
        "primary_diagnosis": primary,
        "best_structural_variant_by_waveform_frames_vuv_gap": best_structural_label,
        "best_structural_waveform_frames_vuv_gap": round(best_structural_value, 6),
        "baseline_waveform_frames_vuv_gap": round(baseline_value, 6),
        "best_scaling_counterfactual_waveform_frames_vuv_gap": round(best_scaling_value, 6),
        "oracle_target_unvoiced_waveform_frames_vuv_gap": round(oracle_value, 6),
        "structural_gain_vs_baseline": round(structural_gain_vs_baseline, 6),
        "structural_gap_to_best_scaling": round(structural_gap_to_scaling, 6),
        "structural_gap_to_oracle": round(structural_gap_to_oracle, 6),
    }


def render_structure_probe_markdown(summary: dict[str, object]) -> str:
    diagnosis = dict(summary.get("diagnosis", {}))
    variants = dict(dict(summary.get("aggregates", {})).get("variants", {}))
    lines = [
        "# Stage5 Vuv Noise-Hidden Residual Structure Probe",
        "",
        "## Summary",
        f"- review bundle: `{summary['review_bundle_path']}`",
        f"- record count: `{summary.get('record_count', 0)}`",
        f"- primary diagnosis: `{diagnosis.get('primary_diagnosis', 'unknown')}`",
        f"- best structural variant: `{diagnosis.get('best_structural_variant_by_waveform_frames_vuv_gap', 'unknown')}`",
        "",
        "## Aggregate Variants",
    ]
    for variant in NOISE_HIDDEN_RESIDUAL_STRUCTURE_VARIANTS:
        payload = dict(variants.get(variant.label, {}))
        lines.append(f"- `{variant.label}`")
        lines.append(
            f"  - waveform_frames vuv high-band mean: `{payload.get('waveform_frames_vuv_high_band_ratio_mean')}`"
        )
        lines.append(f"  - decoded vuv high-band mean: `{payload.get('decoded_vuv_high_band_ratio_mean')}`")
        lines.append(f"  - review_required_count: `{payload.get('review_required_count')}`")
    lines.extend(["", "## Notes"])
    lines.append(
        "- Structural variants recompute the existing residual-shape adapter with alternate noise_hidden-driven feature wiring; they do not add new trainable weights."
    )
    lines.append(
        "- The scaling comparator is included only to measure how much of the prior noise_hidden leverage can be recovered by a more deployable adapter-input reroute."
    )
    lines.append("")
    return "\n".join(lines)
