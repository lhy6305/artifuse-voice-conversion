from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

from datetime import datetime
import json
import math
from pathlib import Path

import torch

from v5vc.nores_vocoder_checkpoint_selection import select_offline_mvp_nores_vocoder_checkpoint
from v5vc.offline_vocoder_scaffold import (
    NoResidualSourceFilterVocoderScaffold,
    build_nores_vocoder_scaffold_from_state_dict,
)
from v5vc.offline_vocoder_training import (
    DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
    compute_nores_vocoder_losses,
    extract_training_batch,
    extract_training_runtime,
    frame_waveform_sequence,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.proxy_audio_export import compute_proxy_activity_gate, smooth_noise
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.target_format_recovery import write_waveform_int16

DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES = 3
DEFAULT_STAGE5_BUZZ_REJECT_HEURISTIC_VERSION = "stage5_buzz_reject_v2"
AUTO_REJECT_TEMPLATE_COSINE_MEAN = 0.985
AUTO_REJECT_ADJACENT_COSINE_MEAN = 0.97
AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED = 0.75
AUTO_REJECT_ACTIVITY_CORR = 0.75
AUTO_REJECT_HIGH_BAND_ENERGY_RATIO = 0.45
AUTO_REJECT_HIGH_BAND_GAP = 0.2
AUTO_REJECT_CENTROID_GAP_HZ = 2500.0
AUTO_REJECT_TEMPLATE_COSINE_MEAN_ENVELOPE_BUZZ = 0.97
AUTO_REJECT_ADJACENT_COSINE_MEAN_ENVELOPE_BUZZ = 0.99
AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED_ENVELOPE_BUZZ = 0.9
AUTO_REJECT_ACTIVITY_CORR_ENVELOPE_BUZZ = 0.88
AUTO_REJECT_HIGH_BAND_GAP_ENVELOPE_BUZZ = 0.3
AUTO_REJECT_CENTROID_GAP_HZ_ENVELOPE_BUZZ = 3500.0


def export_offline_mvp_nores_vocoder_audio(
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    dataset_index_path: Path | None,
    selection_target: str,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    audit_carrier_frequency: float,
    listening_audio_source: str,
    pitch_match_reference: str,
    pitch_match_fmin_hz: float,
    pitch_match_fmax_hz: float,
    pitch_match_max_semitones: float,
    activity_gate_weight: float | None,
    active_template_weight: float | None,
    frame_delta_weight: float | None,
    use_predicted_activity_gate: bool | None,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    decoder_branch_mean_mix_alpha: float = 0.0,
) -> None:
    if float(predicted_activity_gate_floor) < 0.0 or float(predicted_activity_gate_floor) > 1.0:
        raise ValueError("predicted_activity_gate_floor must be within [0.0, 1.0].")
    if int(predicted_activity_gate_smoothing_frames) < 0:
        raise ValueError("predicted_activity_gate_smoothing_frames must be >= 0.")
    if float(decoder_branch_mean_mix_alpha) < 0.0 or float(decoder_branch_mean_mix_alpha) > 1.0:
        raise ValueError("decoder_branch_mean_mix_alpha must be within [0.0, 1.0].")
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    resolved_listening_audio_source = normalize_listening_audio_source(listening_audio_source)
    resolved_pitch_match_reference = normalize_pitch_match_reference(pitch_match_reference)
    resolved_predicted_activity_gate_apply_mode = normalize_predicted_activity_gate_apply_mode(
        predicted_activity_gate_apply_mode
    )
    resolved_export_use_predicted_activity_gate = (
        True if use_predicted_activity_gate is None else bool(use_predicted_activity_gate)
    )

    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
        selection_target=selection_target,
    )
    resolved_selection_target = (
        str(selection_summary.get("_resolved_selection_target", selection_target))
        if isinstance(selection_summary, dict)
        else str(selection_target)
    )
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    training_summary = resolve_nores_vocoder_training_summary(
        checkpoint_path=resolved_checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
    )
    training_loss_weights = resolve_nores_vocoder_export_metric_defaults(
        training_summary=training_summary,
        activity_gate_weight=activity_gate_weight,
        active_template_weight=active_template_weight,
        frame_delta_weight=frame_delta_weight,
    )
    if dataset_index_path is None:
        dataset_index_path = Path(str(checkpoint_payload["dataset_index_path"])).resolve()
    else:
        dataset_index_path = dataset_index_path.resolve()
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No package entries selected for no-residual vocoder audio export.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    )
    model.eval()
    branch_label = infer_branch_label(
        checkpoint_path=resolved_checkpoint_path,
        selection_summary=selection_summary,
        selection_target=resolved_selection_target,
        use_predicted_activity_gate=bool(resolved_export_use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=resolved_predicted_activity_gate_apply_mode,
        decoder_branch_mean_mix_alpha=float(decoder_branch_mean_mix_alpha),
        use_decoder_branch_condition_adapter=bool(model.use_decoder_branch_condition_adapter),
        use_residual_shape_branch_condition_adapter=bool(model.use_residual_shape_branch_condition_adapter),
        residual_shape_branch_condition_scale=float(getattr(model, "residual_shape_branch_condition_scale", 1.0)),
        residual_shape_branch_condition_mode=str(
            getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")
        ),
    )
    loss_metrics_exactly_match_decoded_audio = bool(
        (not bool(resolved_export_use_predicted_activity_gate) and not bool(training_loss_weights["use_predicted_activity_gate"]))
        or (
            bool(resolved_export_use_predicted_activity_gate)
            == bool(training_loss_weights["use_predicted_activity_gate"])
            and str(training_loss_weights["reconstruction_frame_gain_apply_mode"])
            == resolved_predicted_activity_gate_apply_mode
            and float(predicted_activity_gate_floor) == 0.0
            and int(predicted_activity_gate_smoothing_frames) == 0
        )
    )

    exported_records: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
                decoder_branch_mean_mix_alpha=decoder_branch_mean_mix_alpha,
            )
            _, loss_metrics = compute_nores_vocoder_losses(
                outputs=outputs,
                harmonic_target=batch["harmonic_target"],
                noise_target=batch["noise_target"],
                periodic_gate_target=batch["periodic_gate_target"],
                noise_gate_target=batch["noise_gate_target"],
                aligned_waveform=batch["aligned_waveform"],
                energy_proxy_target=batch.get("energy_proxy_target"),
                energy_log_rms_norm_target=batch.get("energy_log_rms_norm_target"),
                aper_target=batch.get("aper_target"),
                vuv_target=batch.get("vuv_target"),
                voiced_proxy_target=batch.get("voiced_proxy_target"),
                aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
                sample_rate=int(runtime["sample_rate"]),
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                harmonic_weight=1.0,
                noise_weight=1.0,
                periodic_gate_weight=0.2,
                noise_gate_weight=0.2,
                activity_gate_weight=float(training_loss_weights["activity_gate"]),
                waveform_weight=0.5,
                stft_weight=0.5,
                rms_guard_weight=0.2,
                active_template_weight=float(training_loss_weights["active_template"]),
                frame_delta_weight=float(training_loss_weights["frame_delta"]),
                use_predicted_activity_gate=bool(training_loss_weights["use_predicted_activity_gate"]),
                reconstruction_frame_gain_apply_mode=str(
                    training_loss_weights["reconstruction_frame_gain_apply_mode"]
                ),
            )
            predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"])
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=outputs["waveform_frames"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                frame_gains=predicted_activity if bool(resolved_export_use_predicted_activity_gate) else None,
                frame_gain_floor=float(predicted_activity_gate_floor),
                frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                frame_gain_apply_mode=resolved_predicted_activity_gate_apply_mode,
            ).cpu()
            aligned_target = batch["aligned_waveform"][: decoded_waveform.shape[0]].cpu()
            audit_proxy = synthesize_nores_vocoder_audit_proxy(
                decoded_waveform=decoded_waveform,
                aligned_target=aligned_target,
                sample_rate=int(runtime["sample_rate"]),
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                carrier_frequency=float(audit_carrier_frequency),
            )
            stem = sanitize_filename(str(entry["record_id"]))
            aligned_target_path = output_dir / f"{stem}__aligned_target.wav"
            decoded_path = output_dir / f"{stem}__decoded.wav"
            decoded_pitch_matched_path = output_dir / f"{stem}__decoded_pitch_matched.wav"
            audit_proxy_path = output_dir / f"{stem}__audit_proxy.wav"
            write_waveform_int16(aligned_target_path, aligned_target, sample_rate=int(runtime["sample_rate"]))
            write_waveform_int16(decoded_path, decoded_waveform, sample_rate=int(runtime["sample_rate"]))
            pitch_match_metrics = None
            decoded_pitch_matched = None
            if resolved_pitch_match_reference == "aligned_target":
                decoded_pitch_matched, pitch_match_metrics = pitch_match_decoded_waveform_to_reference(
                    decoded_waveform=decoded_waveform,
                    reference_waveform=aligned_target,
                    sample_rate=int(runtime["sample_rate"]),
                    fmin_hz=float(pitch_match_fmin_hz),
                    fmax_hz=float(pitch_match_fmax_hz),
                    max_semitones=float(pitch_match_max_semitones),
                )
                write_waveform_int16(
                    decoded_pitch_matched_path,
                    decoded_pitch_matched,
                    sample_rate=int(runtime["sample_rate"]),
                )
            write_waveform_int16(audit_proxy_path, audit_proxy, sample_rate=int(runtime["sample_rate"]))
            listening_audio_path = resolve_listening_audio_path(
                listening_audio_source=resolved_listening_audio_source,
                decoded_path=decoded_path,
                decoded_pitch_matched_path=decoded_pitch_matched_path if pitch_match_metrics is not None else None,
                audit_proxy_path=audit_proxy_path,
            )
            buzz_reject_assessment = assess_stage5_decoded_buzz_reject(
                decoded_waveform=decoded_waveform,
                aligned_target=aligned_target,
                predicted_activity=predicted_activity.cpu(),
                sample_rate=int(runtime["sample_rate"]),
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
            )
            exported_records.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "target_audio_path": str(payload.get("target_audio_path")),
                    "sample_rate": int(runtime["sample_rate"]),
                    "aligned_target_audio_path": aligned_target_path.as_posix(),
                    "decoded_audio_path": decoded_path.as_posix(),
                    "decoded_pitch_matched_audio_path": None
                    if pitch_match_metrics is None
                    else decoded_pitch_matched_path.as_posix(),
                    "audit_proxy_audio_path": audit_proxy_path.as_posix(),
                    "listening_audio_source": resolved_listening_audio_source,
                    "listening_audio_path": listening_audio_path.as_posix(),
                    "audio_path": str(payload.get("target_audio_path")),
                    "input_audio_path": aligned_target_path.as_posix(),
                    "proxy_audio_path": listening_audio_path.as_posix(),
                    "pitch_match_metrics": pitch_match_metrics,
                    "loss_metrics": loss_metrics,
                    "loss_metrics_semantics": {
                        "source": "checkpoint_forward_objective_metrics",
                        "use_predicted_activity_gate": bool(training_loss_weights["use_predicted_activity_gate"]),
                        "reconstruction_frame_gain_apply_mode": str(
                            training_loss_weights["reconstruction_frame_gain_apply_mode"]
                        ),
                        "predicted_activity_gate_floor": None,
                        "predicted_activity_gate_smoothing_frames": None,
                        "activity_gate_weight": float(training_loss_weights["activity_gate"]),
                        "active_template_weight": float(training_loss_weights["active_template"]),
                        "frame_delta_weight": float(training_loss_weights["frame_delta"]),
                        "exactly_matches_decoded_audio": loss_metrics_exactly_match_decoded_audio,
                    },
                    "buzz_reject_assessment": buzz_reject_assessment,
                }
            )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "branch_label": branch_label,
        "audit_render": {
            "mode": "low_frequency_proxy_from_decoded_waveform",
            "carrier_frequency_hz": float(audit_carrier_frequency),
            "silence_gate_reference": "aligned_target",
        },
        "listening_audio_source": resolved_listening_audio_source,
        "pitch_match": {
            "reference": resolved_pitch_match_reference,
            "fmin_hz": float(pitch_match_fmin_hz),
            "fmax_hz": float(pitch_match_fmax_hz),
            "max_semitones": float(pitch_match_max_semitones),
        },
        "waveform_decode": {
            "use_predicted_activity_gate": bool(resolved_export_use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_predicted_activity_gate_apply_mode,
            "decoder_branch_mean_mix_alpha": float(decoder_branch_mean_mix_alpha),
            "fusion_mode": str(model.fusion_mode),
            "use_decoder_branch_condition_adapter": bool(model.use_decoder_branch_condition_adapter),
            "use_residual_shape_branch_condition_adapter": bool(model.use_residual_shape_branch_condition_adapter),
            "residual_shape_branch_condition_scale": float(
                getattr(model, "residual_shape_branch_condition_scale", 1.0)
            ),
            "residual_shape_branch_condition_mode": str(
                getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")
            ),
            "use_noise_hidden_residual_adapter": bool(getattr(model, "use_noise_hidden_residual_adapter", False)),
            "noise_hidden_residual_mode": str(getattr(model, "noise_hidden_residual_mode", "gate_plus_delta_v1")),
            "noise_hidden_residual_scale": float(getattr(model, "noise_hidden_residual_scale", 1.0)),
        },
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "dataset_index_path": dataset_index_path.as_posix(),
        "checkpoint_selection_path": None if selection_summary is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if selection_summary is None else resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "loss_metrics_semantics": {
            "source": "checkpoint_forward_objective_metrics",
            "training_summary_path": (
                None
                if not isinstance(training_summary, dict)
                else training_summary.get("_resolved_summary_path")
            ),
            "use_predicted_activity_gate": bool(training_loss_weights["use_predicted_activity_gate"]),
            "reconstruction_frame_gain_apply_mode": str(
                training_loss_weights["reconstruction_frame_gain_apply_mode"]
            ),
            "predicted_activity_gate_floor": None,
            "predicted_activity_gate_smoothing_frames": None,
            "activity_gate_weight": float(training_loss_weights["activity_gate"]),
            "active_template_weight": float(training_loss_weights["active_template"]),
            "frame_delta_weight": float(training_loss_weights["frame_delta"]),
            "exactly_matches_decoded_audio": loss_metrics_exactly_match_decoded_audio,
        },
        "split_name": str(split_name),
        "sample_count": len(exported_records),
        "buzz_reject_summary": summarize_stage5_buzz_reject_assessments(exported_records),
        "records": exported_records,
        "notes": [
            "aligned_target.wav is the frame-aligned target waveform used by the current Stage5 bootstrap objective.",
            "decoded.wav is reconstructed from the checkpoint's waveform_frames head via overlap-add with the current export-side gate settings.",
            "When use_predicted_activity_gate is enabled, predicted_activity_gate_floor, predicted_activity_gate_smoothing_frames, and predicted_activity_gate_apply_mode define export-side gate softening only; they do not rewrite checkpoint weights.",
            "Unless explicitly overridden, checkpoint_forward_objective_metrics inherit activity/template/delta/gating defaults from the resolved Stage5 training summary, while decoded.wav follows the export-side decode settings.",
            "decoded_pitch_matched.wav is an optional listening-only variant that globally pitch-shifts decoded.wav toward the aligned target's median voiced F0 while preserving duration.",
            "audit_proxy.wav is a low-frequency audit render derived from decoded.wav and gated by aligned_target activity so current GUI listening is less fatiguing and target silence remains silent.",
            f"proxy_audio_path in the GUI-compatible manifest points to {resolved_listening_audio_source}.wav for primary listening; the non-primary audio is retained for technical inspection.",
            "This export is for human listening and checkpoint comparison; it is still not the final multi-resolution or adversarial vocoder route from the design doc.",
            "buzz_reject_assessment is a conservative negative gate only: auto_reject_obvious_buzz can suppress clearly failed outputs, but review_required does not mean the sample is good.",
        ],
    }
    (output_dir / "nores_vocoder_audio_export.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "nores_vocoder_audio_export.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    proxy_summary = build_proxy_audio_export_summary(summary)
    (output_dir / "proxy_audio_export.json").write_text(
        json.dumps(proxy_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "proxy_audio_export.md").write_text(
        build_proxy_audio_export_markdown(proxy_summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_checkpoint_path_from_inputs(
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
) -> tuple[Path, dict[str, object] | None]:
    if checkpoint_path is not None:
        return checkpoint_path.resolve(), None
    if checkpoint_selection_path is None:
        raise ValueError("Either checkpoint_path or checkpoint_selection_path is required.")
    payload = json.loads(checkpoint_selection_path.resolve().read_text(encoding="utf-8"))
    target_key = normalize_selection_target(selection_target)
    resolved_selection_target = str(selection_target).strip().lower()
    selected = payload.get(target_key)
    if (not isinstance(selected, dict) or "step" not in selected) and target_key == "selected_stable_late_stop":
        fallback_key = "best_validation_checkpoint"
        fallback_selected = payload.get(fallback_key)
        if isinstance(fallback_selected, dict) and "step" in fallback_selected:
            target_key = fallback_key
            resolved_selection_target = "best_validation"
            selected = fallback_selected
    if not isinstance(selected, dict) or "step" not in selected:
        raise ValueError(f"checkpoint selection payload does not contain {target_key!r}.")
    summary_path = Path(str(payload["summary_path"])).resolve()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    checkpoint_paths = summary.get("artifacts", {}).get("checkpoint_paths", [])
    selected_step = int(selected["step"])
    matched_path = None
    for item in checkpoint_paths:
        item_path = Path(str(item))
        stem = item_path.stem
        if stem.endswith(f".step{selected_step}"):
            matched_path = item_path.resolve()
            break
    if matched_path is None:
        raise ValueError(f"Unable to resolve checkpoint path for selected step {selected_step}.")
    selection_summary = dict(selected)
    selection_summary["_resolved_selection_target_key"] = target_key
    selection_summary["_resolved_selection_target"] = resolved_selection_target
    return matched_path, selection_summary


def resolve_nores_vocoder_training_summary(
    checkpoint_path: Path,
    checkpoint_selection_path: Path | None,
) -> dict[str, object] | None:
    candidate_paths: list[Path] = []
    if checkpoint_selection_path is not None:
        selection_payload = json.loads(checkpoint_selection_path.resolve().read_text(encoding="utf-8"))
        summary_path_raw = selection_payload.get("summary_path")
        if summary_path_raw:
            candidate_paths.append(Path(str(summary_path_raw)).resolve())
    checkpoint_path = checkpoint_path.resolve()
    candidate_paths.extend(
        [
            checkpoint_path.parent.parent / "logs" / "offline_mvp_nores_vocoder_dataset_loop.summary.json",
            checkpoint_path.parent.parent / "offline_mvp_nores_vocoder_dataset_loop.summary.json",
            checkpoint_path.parent.parent / "offline_mvp_nores_vocoder_loop.summary.json",
        ]
    )
    for candidate_path in candidate_paths:
        if not candidate_path.exists():
            continue
        summary = json.loads(candidate_path.read_text(encoding="utf-8"))
        if not isinstance(summary, dict):
            continue
        summary["_resolved_summary_path"] = candidate_path.as_posix()
        return summary
    return None


def resolve_nores_vocoder_export_metric_defaults(
    *,
    training_summary: dict[str, object] | None,
    activity_gate_weight: float | None,
    active_template_weight: float | None,
    frame_delta_weight: float | None,
) -> dict[str, object]:
    training_payload = (
        dict(training_summary.get("training", {}))
        if isinstance(training_summary, dict) and isinstance(training_summary.get("training"), dict)
        else {}
    )
    loss_weights = (
        dict(training_payload.get("loss_weights", {}))
        if isinstance(training_payload.get("loss_weights"), dict)
        else {}
    )
    return {
        "activity_gate": (
            float(activity_gate_weight)
            if activity_gate_weight is not None
            else float(loss_weights.get("activity_gate", 0.0))
        ),
        "active_template": (
            float(active_template_weight)
            if active_template_weight is not None
            else float(loss_weights.get("active_template", 0.0))
        ),
        "frame_delta": (
            float(frame_delta_weight)
            if frame_delta_weight is not None
            else float(loss_weights.get("frame_delta", 0.0))
        ),
        "use_predicted_activity_gate": bool(loss_weights.get("use_predicted_activity_gate", False)),
        "reconstruction_frame_gain_apply_mode": str(
            loss_weights.get(
                "reconstruction_frame_gain_apply_mode",
                DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
            )
        ),
    }


def normalize_selection_target(selection_target: str) -> str:
    normalized = str(selection_target).strip().lower()
    mapping = {
        "stable_late_stop": "selected_stable_late_stop",
        "best_validation": "best_validation_checkpoint",
        "best_rms": "best_rms_checkpoint",
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported selection_target: {selection_target}")
    return mapping[normalized]


def normalize_listening_audio_source(listening_audio_source: str) -> str:
    normalized = str(listening_audio_source).strip().lower()
    if normalized not in {"decoded", "decoded_pitch_matched", "audit_proxy"}:
        raise ValueError(f"Unsupported listening_audio_source: {listening_audio_source}")
    return normalized


def normalize_pitch_match_reference(pitch_match_reference: str) -> str:
    normalized = str(pitch_match_reference).strip().lower()
    if normalized not in {"none", "aligned_target"}:
        raise ValueError(f"Unsupported pitch_match_reference: {pitch_match_reference}")
    return normalized


def normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode: str) -> str:
    normalized = str(predicted_activity_gate_apply_mode).strip().lower()
    if normalized not in {"pre_overlap_add", "post_ola_envelope"}:
        raise ValueError(
            "Unsupported predicted_activity_gate_apply_mode: "
            f"{predicted_activity_gate_apply_mode}"
        )
    return normalized


def resolve_listening_audio_path(
    listening_audio_source: str,
    decoded_path: Path,
    decoded_pitch_matched_path: Path | None,
    audit_proxy_path: Path,
) -> Path:
    if listening_audio_source == "decoded":
        return decoded_path
    if listening_audio_source == "decoded_pitch_matched":
        if decoded_pitch_matched_path is None:
            raise ValueError("decoded_pitch_matched listening source requires pitch-matched export output.")
        return decoded_pitch_matched_path
    return audit_proxy_path


def resolve_package_entries(
    dataset_index: dict[str, object],
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    normalized_split = str(split_name).strip().lower()
    if normalized_split == "validation":
        entries = list(dataset_index.get("validation_packages", []))
    elif normalized_split == "train":
        entries = list(dataset_index.get("train_packages", []))
    else:
        raise ValueError(f"Unsupported split_name: {split_name}")
    if target_record_ids:
        entry_map = {str(entry["record_id"]): entry for entry in entries}
        selected = []
        missing = []
        for record_id in target_record_ids:
            match = entry_map.get(str(record_id))
            if match is None:
                missing.append(str(record_id))
                continue
            selected.append(match)
        if missing:
            raise ValueError(f"Unknown target_record_ids: {missing}")
        return selected
    if sample_count <= 0:
        raise ValueError("sample_count must be positive.")
    if len(entries) <= sample_count:
        return entries
    if sample_count == 1:
        return [entries[0]]
    indices: list[int] = []
    max_index = len(entries) - 1
    for index in range(sample_count):
        candidate = round(index * max_index / (sample_count - 1))
        if candidate not in indices:
            indices.append(candidate)
    while len(indices) < sample_count:
        for candidate in range(len(entries)):
            if candidate not in indices:
                indices.append(candidate)
            if len(indices) >= sample_count:
                break
    return [entries[index] for index in indices[:sample_count]]


def assess_stage5_decoded_buzz_reject(
    *,
    decoded_waveform: torch.Tensor,
    aligned_target: torch.Tensor,
    predicted_activity: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    decoded_waveform_cpu = decoded_waveform.detach().cpu().to(torch.float32).view(-1)
    aligned_target_cpu = aligned_target.detach().cpu().to(torch.float32).view(-1)[: decoded_waveform_cpu.shape[0]]
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform_cpu, int(sample_rate))
    aligned_spectral = compute_waveform_spectral_summary(aligned_target_cpu, int(sample_rate))
    decoded_frames = frame_waveform_sequence(
        waveform=decoded_waveform_cpu,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    aligned_frames = frame_waveform_sequence(
        waveform=aligned_target_cpu,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    common_frame_count = min(int(decoded_frames.shape[0]), int(aligned_frames.shape[0]))
    if common_frame_count <= 0:
        return {
            "heuristic_version": DEFAULT_STAGE5_BUZZ_REJECT_HEURISTIC_VERSION,
            "status": "unknown",
            "auto_reject": False,
            "summary": "Unable to estimate buzz-reject status because decoded or aligned frames are unavailable.",
            "signals": [],
            "metrics": {},
        }
    decoded_frames = decoded_frames[:common_frame_count]
    aligned_frames = aligned_frames[:common_frame_count]
    predicted_activity_cpu = predicted_activity.detach().cpu().to(torch.float32).view(-1)[:common_frame_count]
    decoded_frame_metrics = summarize_frame_sequence_metrics(decoded_frames)
    aligned_frame_metrics = summarize_frame_sequence_metrics(aligned_frames)
    decoded_frame_rms = decoded_frames.pow(2).mean(dim=1).sqrt()
    aligned_frame_rms = aligned_frames.pow(2).mean(dim=1).sqrt()
    decoded_activity_corr = compute_pearson_correlation(decoded_frame_rms, aligned_frame_rms)
    predicted_activity_corr = compute_pearson_correlation(predicted_activity_cpu, aligned_frame_rms)
    metrics = {
        "decoded_zero_crossing_rate": round(float(compute_zero_cross_ratio(decoded_waveform_cpu)), 6),
        "decoded_spectral_summary": decoded_spectral,
        "aligned_spectral_summary": aligned_spectral,
        "decoded_frame_template_cosine_mean": float(decoded_frame_metrics["template_cosine_mean"]),
        "decoded_frame_adjacent_cosine_mean": float(decoded_frame_metrics["adjacent_cosine_mean"]),
        "decoded_frame_rms_cv": float(decoded_frame_metrics["frame_rms_cv"]),
        "aligned_frame_template_cosine_mean": float(aligned_frame_metrics["template_cosine_mean"]),
        "aligned_frame_adjacent_cosine_mean": float(aligned_frame_metrics["adjacent_cosine_mean"]),
        "aligned_frame_rms_cv": float(aligned_frame_metrics["frame_rms_cv"]),
        "decoded_frame_template_cosine_gap_vs_aligned": round(
            float(decoded_frame_metrics["template_cosine_mean"]) - float(aligned_frame_metrics["template_cosine_mean"]),
            6,
        ),
        "decoded_frame_adjacent_cosine_gap_vs_aligned": round(
            float(decoded_frame_metrics["adjacent_cosine_mean"]) - float(aligned_frame_metrics["adjacent_cosine_mean"]),
            6,
        ),
        "decoded_frame_rms_to_aligned_frame_rms_corr": float(decoded_activity_corr),
        "predicted_activity_to_aligned_frame_rms_corr": float(predicted_activity_corr),
        "spectral_centroid_gap_hz": round(
            abs(float(decoded_spectral["centroid_hz"]) - float(aligned_spectral["centroid_hz"])),
            6,
        ),
        "spectral_high_band_energy_ratio_gap": round(
            abs(
                float(decoded_spectral["high_band_energy_ratio"])
                - float(aligned_spectral["high_band_energy_ratio"])
            ),
            6,
        ),
    }
    signals: list[str] = []
    template_collapse = (
        float(metrics["decoded_frame_template_cosine_mean"]) >= AUTO_REJECT_TEMPLATE_COSINE_MEAN
        and float(metrics["decoded_frame_adjacent_cosine_mean"]) >= AUTO_REJECT_ADJACENT_COSINE_MEAN
        and float(metrics["decoded_frame_template_cosine_gap_vs_aligned"]) >= AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED
    )
    envelope_following = (
        float(metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]) >= AUTO_REJECT_ACTIVITY_CORR
        or float(metrics["predicted_activity_to_aligned_frame_rms_corr"]) >= AUTO_REJECT_ACTIVITY_CORR
    )
    extreme_high_band = (
        float(decoded_spectral["high_band_energy_ratio"]) >= AUTO_REJECT_HIGH_BAND_ENERGY_RATIO
        and float(metrics["spectral_high_band_energy_ratio_gap"]) >= AUTO_REJECT_HIGH_BAND_GAP
        and float(metrics["spectral_centroid_gap_hz"]) >= AUTO_REJECT_CENTROID_GAP_HZ
    )
    envelope_template_buzz = (
        float(metrics["decoded_frame_template_cosine_mean"]) >= AUTO_REJECT_TEMPLATE_COSINE_MEAN_ENVELOPE_BUZZ
        and float(metrics["decoded_frame_adjacent_cosine_mean"]) >= AUTO_REJECT_ADJACENT_COSINE_MEAN_ENVELOPE_BUZZ
        and float(metrics["decoded_frame_template_cosine_gap_vs_aligned"])
        >= AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED_ENVELOPE_BUZZ
        and max(
            float(metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]),
            float(metrics["predicted_activity_to_aligned_frame_rms_corr"]),
        )
        >= AUTO_REJECT_ACTIVITY_CORR_ENVELOPE_BUZZ
        and float(metrics["spectral_high_band_energy_ratio_gap"]) >= AUTO_REJECT_HIGH_BAND_GAP_ENVELOPE_BUZZ
        and float(metrics["spectral_centroid_gap_hz"]) >= AUTO_REJECT_CENTROID_GAP_HZ_ENVELOPE_BUZZ
    )
    if template_collapse:
        signals.append(
            "decoded short-time frames remain highly template-collapsed relative to aligned target diversity"
        )
    if envelope_following:
        signals.append(
            "decoded frame RMS mainly follows aligned target envelope while short-time structure stays collapsed"
        )
    if extreme_high_band:
        signals.append(
            "decoded spectral brightness remains far above aligned target and matches the historical harsh-buzz pattern"
        )
    if envelope_template_buzz:
        signals.append(
            "decoded route matches the human-confirmed envelope-following buzz family even without the older extreme high-band signature"
        )
    auto_reject = bool((template_collapse and envelope_following) or extreme_high_band or envelope_template_buzz)
    if auto_reject:
        status = "auto_reject_obvious_buzz"
        summary = (
            "Decoded waveform matches the Stage5 negative pattern for obvious buzz/template-collapse failure."
        )
    else:
        status = "review_required"
        summary = (
            "Decoded waveform does not cross the conservative auto-reject gate; human review is still required before any positive claim."
        )
    return {
        "heuristic_version": DEFAULT_STAGE5_BUZZ_REJECT_HEURISTIC_VERSION,
        "status": status,
        "auto_reject": auto_reject,
        "summary": summary,
        "signals": signals,
        "metrics": metrics,
    }


def summarize_stage5_buzz_reject_assessments(records: list[dict[str, object]]) -> dict[str, object]:
    assessments = [
        dict(record.get("buzz_reject_assessment", {}))
        for record in records
        if isinstance(record.get("buzz_reject_assessment"), dict)
    ]
    auto_reject_count = sum(1 for item in assessments if bool(item.get("auto_reject", False)))
    return {
        "heuristic_version": DEFAULT_STAGE5_BUZZ_REJECT_HEURISTIC_VERSION,
        "record_count": len(assessments),
        "auto_reject_count": int(auto_reject_count),
        "review_required_count": max(0, len(assessments) - auto_reject_count),
        "all_records_auto_reject": bool(assessments) and auto_reject_count == len(assessments),
        "auto_reject_record_ids": [
            str(record["record_id"])
            for record in records
            if bool(dict(record.get("buzz_reject_assessment", {})).get("auto_reject", False))
        ],
    }


def build_model_from_checkpoint(
    checkpoint_payload: dict[str, object],
    first_batch: dict[str, torch.Tensor],
    first_runtime: dict[str, int],
) -> NoResidualSourceFilterVocoderScaffold:
    state_dict = dict(checkpoint_payload["model_state_dict"])
    model_config = checkpoint_payload.get("model_config")
    residual_shape_branch_condition_scale = 1.0
    residual_shape_branch_condition_mode = "raw_additive_v1"
    use_noise_hidden_residual_adapter = False
    noise_hidden_residual_mode = "gate_plus_delta_v1"
    noise_hidden_residual_scale = 1.0
    if isinstance(model_config, dict):
        residual_shape_branch_condition_scale = float(
            model_config.get("residual_shape_branch_condition_scale", 1.0)
        )
        residual_shape_branch_condition_mode = str(
            model_config.get("residual_shape_branch_condition_mode", "raw_additive_v1")
        )
        use_noise_hidden_residual_adapter = bool(model_config.get("use_noise_hidden_residual_adapter", False))
        noise_hidden_residual_mode = str(model_config.get("noise_hidden_residual_mode", "gate_plus_delta_v1"))
        noise_hidden_residual_scale = float(model_config.get("noise_hidden_residual_scale", 1.0))
    model = build_nores_vocoder_scaffold_from_state_dict(
        state_dict=state_dict,
        periodic_input_dim=int(first_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(first_batch["noise_branch_features"].shape[-1]),
        frame_length=int(first_runtime["frame_length"]),
        residual_shape_branch_condition_scale=residual_shape_branch_condition_scale,
        residual_shape_branch_condition_mode=residual_shape_branch_condition_mode,
        use_noise_hidden_residual_adapter=use_noise_hidden_residual_adapter,
        noise_hidden_residual_mode=noise_hidden_residual_mode,
        noise_hidden_residual_scale=noise_hidden_residual_scale,
    )
    model.load_state_dict(state_dict)
    return model



def sanitize_filename(value: str) -> str:
    sanitized = [
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in value
    ]
    return "".join(sanitized).strip("_") or "sample"


def synthesize_nores_vocoder_audit_proxy(
    decoded_waveform: torch.Tensor,
    aligned_target: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    carrier_frequency: float,
) -> torch.Tensor:
    if decoded_waveform.numel() == 0:
        return torch.zeros_like(aligned_target)
    total_length = int(min(decoded_waveform.shape[0], aligned_target.shape[0]))
    if total_length <= 0:
        return torch.zeros_like(aligned_target)
    decoded = decoded_waveform[:total_length].to(torch.float32)
    target = aligned_target[:total_length].to(torch.float32)
    frame_count = max(1, math.ceil(max(1, total_length - frame_length) / hop_length) + 1)
    output = torch.zeros(total_length, dtype=torch.float32)
    weights = torch.zeros(total_length, dtype=torch.float32)
    window = torch.hann_window(frame_length, periodic=False, dtype=torch.float32)
    generator = torch.Generator()
    generator.manual_seed(20260318)
    phase = 0.0
    previous_rms = 0.0
    phase_increment = 2.0 * math.pi * float(carrier_frequency) / int(sample_rate)

    for frame_index in range(frame_count):
        start = int(frame_index * hop_length)
        end = start + int(frame_length)
        decoded_frame = slice_or_pad_waveform(decoded, start=start, end=end)
        target_frame = slice_or_pad_waveform(target, start=start, end=end)
        target_rms = float(target_frame.pow(2).mean().sqrt().item())
        target_abs = float(target_frame.abs().mean().item())
        activity_gate = compute_proxy_activity_gate(
            rms_target=target_rms,
            abs_target=target_abs,
        )
        phase_positions = phase + phase_increment * torch.arange(frame_length, dtype=torch.float32)
        phase = float((phase + frame_length * phase_increment) % (2.0 * math.pi))
        if activity_gate <= 1.0e-4:
            continue
        decoded_rms = float(decoded_frame.pow(2).mean().sqrt().item())
        decoded_abs = float(decoded_frame.abs().mean().item())
        zero_cross = compute_zero_cross_ratio(decoded_frame)
        delta_energy = max(-0.5, min(0.5, (decoded_rms - previous_rms) * 8.0))
        previous_rms = decoded_rms
        brightness = 1.0 / (1.0 + math.exp(-((zero_cross - 0.12) / 0.04)))
        noise_mix = (0.02 + 0.08 * brightness) * activity_gate
        harmonic_mix = (0.08 + 0.10 * min(max(decoded_abs / 0.18, 0.0), 1.0)) * activity_gate
        tone = (
            0.92 * torch.sin(phase_positions)
            + harmonic_mix * torch.sin(phase_positions * 2.0 + 0.17)
            + 0.02 * brightness * torch.sin(phase_positions * 3.0 + 0.31)
        )
        noise = torch.randn(frame_length, generator=generator, dtype=torch.float32)
        noise = smooth_noise(noise=noise, passes=8)
        noise = noise / noise.std().clamp_min(1.0e-6)
        frame = (1.0 - noise_mix) * tone + noise_mix * noise
        frame = frame / frame.pow(2).mean().sqrt().clamp_min(1.0e-6)
        frame = frame * max(0.0, min(decoded_rms, 0.35))
        ramp = torch.linspace(-0.5, 0.5, frame_length, dtype=torch.float32)
        frame = frame * (1.0 + delta_energy * 0.20 * ramp).clamp(min=0.8, max=1.2)
        frame = frame * activity_gate
        frame = frame.clamp(-1.0, 1.0)
        output_start = start
        output_end = min(end, total_length)
        valid_length = output_end - output_start
        if valid_length <= 0:
            continue
        output[output_start:output_end] += frame[:valid_length] * window[:valid_length]
        weights[output_start:output_end] += window[:valid_length]

    output = output / weights.clamp_min(1.0e-6)
    output = smooth_noise(noise=output, passes=4)
    peak = float(output.abs().max().item()) if output.numel() > 0 else 0.0
    if peak > 0.98:
        output = output * float(0.98 / peak)
    return output.clamp(-1.0, 1.0)


def slice_or_pad_waveform(
    waveform: torch.Tensor,
    start: int,
    end: int,
) -> torch.Tensor:
    frame_length = int(end - start)
    if frame_length <= 0:
        return waveform.new_zeros((0,))
    if start >= int(waveform.shape[0]):
        return waveform.new_zeros((frame_length,))
    sliced = waveform[start:min(end, int(waveform.shape[0]))]
    if int(sliced.shape[0]) >= frame_length:
        return sliced[:frame_length]
    padded = waveform.new_zeros((frame_length,))
    padded[: int(sliced.shape[0])] = sliced
    return padded


def compute_zero_cross_ratio(waveform: torch.Tensor) -> float:
    if waveform.numel() <= 1:
        return 0.0
    previous = waveform[:-1]
    current = waveform[1:]
    return float(((previous * current) < 0.0).to(torch.float32).mean().item())


def summarize_frame_sequence_metrics(frames: torch.Tensor) -> dict[str, float]:
    if frames.ndim != 2:
        raise ValueError(f"Expected frames shape [frames, samples], got {tuple(frames.shape)}")
    frames_cpu = frames.detach().cpu().to(torch.float32)
    frame_rms = frames_cpu.pow(2).mean(dim=1).sqrt()
    centered = frames_cpu - frames_cpu.mean(dim=1, keepdim=True)
    normalized = centered / centered.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    adjacent_cosine = frames_cpu.new_zeros((0,), dtype=torch.float32)
    if int(normalized.shape[0]) > 1:
        adjacent_cosine = (normalized[:-1] * normalized[1:]).sum(dim=1)
    template = centered.mean(dim=0)
    template_direction = template / template.norm().clamp_min(1.0e-6)
    template_cosine = (normalized * template_direction.unsqueeze(0)).sum(dim=1)
    frame_rms_mean = float(frame_rms.mean().item())
    frame_rms_std = float(frame_rms.std(unbiased=False).item())
    return {
        "frame_rms_mean": round(frame_rms_mean, 6),
        "frame_rms_std": round(frame_rms_std, 6),
        "frame_rms_cv": round(0.0 if abs(frame_rms_mean) <= 1.0e-8 else frame_rms_std / frame_rms_mean, 6),
        "adjacent_cosine_mean": round(
            0.0 if int(adjacent_cosine.numel()) <= 0 else float(adjacent_cosine.mean().item()),
            6,
        ),
        "adjacent_cosine_abs_mean": round(
            0.0 if int(adjacent_cosine.numel()) <= 0 else float(adjacent_cosine.abs().mean().item()),
            6,
        ),
        "template_cosine_mean": round(float(template_cosine.mean().item()), 6),
    }


def compute_pearson_correlation(left: torch.Tensor, right: torch.Tensor) -> float:
    left_cpu = left.detach().cpu().to(torch.float32).view(-1)
    right_cpu = right.detach().cpu().to(torch.float32).view(-1)
    common_length = min(int(left_cpu.shape[0]), int(right_cpu.shape[0]))
    if common_length <= 1:
        return 0.0
    left_slice = left_cpu[:common_length]
    right_slice = right_cpu[:common_length]
    left_centered = left_slice - left_slice.mean()
    right_centered = right_slice - right_slice.mean()
    denominator = left_centered.norm() * right_centered.norm()
    if float(denominator.item()) <= 1.0e-8:
        return 0.0
    return round(float((left_centered * right_centered).sum().item() / denominator.item()), 6)


def pitch_match_decoded_waveform_to_reference(
    decoded_waveform: torch.Tensor,
    reference_waveform: torch.Tensor,
    sample_rate: int,
    fmin_hz: float,
    fmax_hz: float,
    max_semitones: float,
) -> tuple[torch.Tensor, dict[str, object] | None]:
    decoded_median_f0_hz = estimate_median_voiced_f0_hz(
        waveform=decoded_waveform,
        sample_rate=sample_rate,
        fmin_hz=fmin_hz,
        fmax_hz=fmax_hz,
    )
    reference_median_f0_hz = estimate_median_voiced_f0_hz(
        waveform=reference_waveform,
        sample_rate=sample_rate,
        fmin_hz=fmin_hz,
        fmax_hz=fmax_hz,
    )
    metrics = {
        "reference": "aligned_target",
        "decoded_median_f0_hz": None if decoded_median_f0_hz is None else round(float(decoded_median_f0_hz), 6),
        "reference_median_f0_hz": None if reference_median_f0_hz is None else round(float(reference_median_f0_hz), 6),
        "applied_semitones": 0.0,
        "applied_ratio": 1.0,
        "status": "skipped_missing_f0",
    }
    if decoded_median_f0_hz is None or reference_median_f0_hz is None:
        return decoded_waveform.clone(), metrics
    raw_semitones = 12.0 * math.log2(float(reference_median_f0_hz) / float(decoded_median_f0_hz))
    applied_semitones = max(-float(max_semitones), min(float(max_semitones), raw_semitones))
    if abs(applied_semitones) < 0.05:
        metrics["status"] = "skipped_small_shift"
        return decoded_waveform.clone(), metrics
    shifted = apply_global_pitch_shift(
        waveform=decoded_waveform,
        sample_rate=sample_rate,
        semitones=applied_semitones,
    )
    metrics["applied_semitones"] = round(float(applied_semitones), 6)
    metrics["applied_ratio"] = round(float(2.0 ** (applied_semitones / 12.0)), 6)
    metrics["status"] = "applied"
    return shifted, metrics


def estimate_median_voiced_f0_hz(
    waveform: torch.Tensor,
    sample_rate: int,
    fmin_hz: float,
    fmax_hz: float,
) -> float | None:
    if waveform.numel() <= 0:
        return None
    try:
        import librosa
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("librosa is required for pitch-matched audio export.") from exc
    samples = waveform.detach().to(torch.float32).cpu().numpy()
    f0_hz, _voiced_flag, _voiced_prob = librosa.pyin(
        samples,
        fmin=float(fmin_hz),
        fmax=float(fmax_hz),
        sr=int(sample_rate),
        frame_length=2048,
        hop_length=256,
    )
    voiced_f0_hz = f0_hz[np.isfinite(f0_hz)]
    if voiced_f0_hz.size <= 0:
        return None
    return float(np.median(voiced_f0_hz))


def apply_global_pitch_shift(
    waveform: torch.Tensor,
    sample_rate: int,
    semitones: float,
) -> torch.Tensor:
    if waveform.numel() <= 0:
        return waveform.clone()
    try:
        import librosa
    except ImportError as exc:
        raise RuntimeError("librosa is required for pitch-matched audio export.") from exc
    samples = waveform.detach().to(torch.float32).cpu().numpy()
    shifted = librosa.effects.pitch_shift(
        samples,
        sr=int(sample_rate),
        n_steps=float(semitones),
    )
    shifted_tensor = torch.from_numpy(shifted).to(torch.float32)
    if int(shifted_tensor.shape[0]) != int(waveform.shape[0]):
        shifted_tensor = slice_or_pad_waveform(
            shifted_tensor,
            start=0,
            end=int(waveform.shape[0]),
        )
    peak = float(shifted_tensor.abs().max().item()) if shifted_tensor.numel() > 0 else 0.0
    if peak > 0.999:
        shifted_tensor = shifted_tensor * float(0.999 / peak)
    return shifted_tensor.clamp(-1.0, 1.0)


def infer_branch_label(
    checkpoint_path: Path,
    selection_summary: dict[str, object] | None,
    selection_target: str,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    decoder_branch_mean_mix_alpha: float = 0.0,
    use_decoder_branch_condition_adapter: bool = False,
    use_residual_shape_branch_condition_adapter: bool = False,
    residual_shape_branch_condition_scale: float = 1.0,
    residual_shape_branch_condition_mode: str = "raw_additive_v1",
) -> str:
    suffix = describe_waveform_decode_variant(
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=str(predicted_activity_gate_apply_mode),
        decoder_branch_mean_mix_alpha=float(decoder_branch_mean_mix_alpha),
        use_decoder_branch_condition_adapter=bool(use_decoder_branch_condition_adapter),
        use_residual_shape_branch_condition_adapter=bool(use_residual_shape_branch_condition_adapter),
        residual_shape_branch_condition_scale=float(residual_shape_branch_condition_scale),
        residual_shape_branch_condition_mode=str(residual_shape_branch_condition_mode),
    )
    if selection_summary is not None:
        selected_step = selection_summary.get("step")
        if selected_step is not None:
            return f"stage5_{selection_target}_step{int(selected_step)}{suffix}"
    return f"{checkpoint_path.stem}{suffix}"


def describe_waveform_decode_variant(
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    decoder_branch_mean_mix_alpha: float = 0.0,
    use_decoder_branch_condition_adapter: bool = False,
    use_residual_shape_branch_condition_adapter: bool = False,
    residual_shape_branch_condition_scale: float = 1.0,
    residual_shape_branch_condition_mode: str = "raw_additive_v1",
) -> str:
    parts: list[str] = []
    if bool(use_decoder_branch_condition_adapter):
        parts.append("branchcond")
    if bool(use_residual_shape_branch_condition_adapter):
        parts.append("residualshapecond")
        if abs(float(residual_shape_branch_condition_scale) - 1.0) > 1.0e-9:
            scale_tag = int(round(float(residual_shape_branch_condition_scale) * 1000.0))
            parts.append(f"rsscale{scale_tag:03d}")
        if str(residual_shape_branch_condition_mode).strip().lower() != "raw_additive_v1":
            parts.append("rsunitrms")
    if float(decoder_branch_mean_mix_alpha) > 1.0e-9:
        mix_tag = int(round(float(decoder_branch_mean_mix_alpha) * 1000.0))
        parts.append(f"mix{mix_tag:03d}")
    if not bool(use_predicted_activity_gate):
        parts.append("gateoff")
        return "__decode_" + "_".join(parts)
    if int(predicted_activity_gate_smoothing_frames) > 0:
        parts.append(f"smooth{int(predicted_activity_gate_smoothing_frames)}")
    if float(predicted_activity_gate_floor) > 1.0e-9:
        floor_tag = int(round(float(predicted_activity_gate_floor) * 1000.0))
        parts.append(f"floor{floor_tag:03d}")
    normalized_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    if normalized_apply_mode == "post_ola_envelope":
        parts.append("postenv")
    if not parts:
        return ""
    return "__decode_" + "_".join(parts)


def build_proxy_audio_export_summary(summary: dict[str, object]) -> dict[str, object]:
    records = []
    for record in summary["records"]:
        records.append(
            {
                "record_id": record["record_id"],
                "audio_path": record["audio_path"],
                "sample_rate": record["sample_rate"],
                "input_audio_path": record["input_audio_path"],
                "decoded_audio_path": record.get("decoded_audio_path"),
                "decoded_pitch_matched_audio_path": record.get("decoded_pitch_matched_audio_path"),
                "audit_proxy_audio_path": record.get("audit_proxy_audio_path"),
                "listening_audio_source": record.get("listening_audio_source"),
                "listening_audio_path": record.get("listening_audio_path"),
                "proxy_audio_path": record["proxy_audio_path"],
                "pitch_match_metrics": record.get("pitch_match_metrics"),
                "loss_metrics": record["loss_metrics"],
                "loss_metrics_semantics": record.get("loss_metrics_semantics"),
                "buzz_reject_assessment": record.get("buzz_reject_assessment"),
            }
        )
    return {
        "generated_at": summary["generated_at"],
        "export_type": "stage5_nores_vocoder_audio_export",
        "branch_label": summary["branch_label"],
        "checkpoint_path": summary["checkpoint_path"],
        "checkpoint_selection_path": summary["checkpoint_selection_path"],
        "selection_target": summary["selection_target"],
        "selected_checkpoint_summary": summary["selected_checkpoint_summary"],
        "audit_render": summary.get("audit_render"),
        "listening_audio_source": summary.get("listening_audio_source"),
        "pitch_match": summary.get("pitch_match"),
        "waveform_decode": summary.get("waveform_decode"),
        "loss_metrics_semantics": summary.get("loss_metrics_semantics"),
        "dataset_index_path": summary["dataset_index_path"],
        "split_name": summary["split_name"],
        "sample_count": summary["sample_count"],
        "buzz_reject_summary": summary.get("buzz_reject_summary"),
        "records": records,
        "notes": summary["notes"],
    }


def build_proxy_audio_export_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Audio Audit Bundle",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- branch_label: {summary['branch_label']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- audit_render: {json.dumps(summary.get('audit_render'), ensure_ascii=False)}",
        f"- listening_audio_source: {summary.get('listening_audio_source')}",
        f"- pitch_match: {json.dumps(summary.get('pitch_match'), ensure_ascii=False)}",
        f"- waveform_decode: {json.dumps(summary.get('waveform_decode'), ensure_ascii=False)}",
        f"- loss_metrics_semantics: {json.dumps(summary.get('loss_metrics_semantics'), ensure_ascii=False)}",
        f"- sample_count: {summary['sample_count']}",
        f"- buzz_reject_summary: {json.dumps(summary.get('buzz_reject_summary'), ensure_ascii=False)}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"input_audio_path={record['input_audio_path']} "
            f"listening_audio_path={record.get('listening_audio_path')} "
            f"decoded_pitch_matched_audio_path={record.get('decoded_pitch_matched_audio_path')} "
            f"proxy_audio_path={record['proxy_audio_path']} "
            f"loss_metrics_semantics={json.dumps(record.get('loss_metrics_semantics'), ensure_ascii=False)} "
            f"buzz_reject_status={dict(record.get('buzz_reject_assessment', {})).get('status')}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Audio Export",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
        f"- audit_render: {json.dumps(summary.get('audit_render'), ensure_ascii=False)}",
        f"- listening_audio_source: {summary.get('listening_audio_source')}",
        f"- pitch_match: {json.dumps(summary.get('pitch_match'), ensure_ascii=False)}",
        f"- waveform_decode: {json.dumps(summary.get('waveform_decode'), ensure_ascii=False)}",
        f"- loss_metrics_semantics: {json.dumps(summary.get('loss_metrics_semantics'), ensure_ascii=False)}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- buzz_reject_summary: {json.dumps(summary.get('buzz_reject_summary'), ensure_ascii=False)}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"loss_total={record['loss_metrics']['loss_total']} "
            f"buzz_reject_status={dict(record.get('buzz_reject_assessment', {})).get('status')} "
            f"aligned_target_audio_path={record['aligned_target_audio_path']} "
            f"decoded_audio_path={record['decoded_audio_path']} "
            f"decoded_pitch_matched_audio_path={record.get('decoded_pitch_matched_audio_path')} "
            f"audit_proxy_audio_path={record.get('audit_proxy_audio_path')}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
