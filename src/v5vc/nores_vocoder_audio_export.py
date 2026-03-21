from __future__ import annotations

from datetime import datetime
import json
import math
import shutil
from pathlib import Path

import torch

from v5vc.nores_vocoder_checkpoint_selection import select_offline_mvp_nores_vocoder_checkpoint
from v5vc.offline_vocoder_scaffold import NoResidualSourceFilterVocoderScaffold
from v5vc.offline_vocoder_training import (
    compute_nores_vocoder_losses,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.proxy_audio_export import compute_proxy_activity_gate, smooth_noise
from v5vc.target_format_recovery import write_waveform_int16

DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES = 3


def export_offline_mvp_nores_vocoder_audio(
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
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
    activity_gate_weight: float,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> None:
    if float(predicted_activity_gate_floor) < 0.0 or float(predicted_activity_gate_floor) > 1.0:
        raise ValueError("predicted_activity_gate_floor must be within [0.0, 1.0].")
    if int(predicted_activity_gate_smoothing_frames) < 0:
        raise ValueError("predicted_activity_gate_smoothing_frames must be >= 0.")
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    resolved_listening_audio_source = normalize_listening_audio_source(listening_audio_source)
    resolved_pitch_match_reference = normalize_pitch_match_reference(pitch_match_reference)
    resolved_predicted_activity_gate_apply_mode = normalize_predicted_activity_gate_apply_mode(
        predicted_activity_gate_apply_mode
    )

    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
        selection_target=selection_target,
    )
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    dataset_index_path = Path(str(checkpoint_payload["dataset_index_path"])).resolve()
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
        selection_target=selection_target,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=resolved_predicted_activity_gate_apply_mode,
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
            )
            _, loss_metrics = compute_nores_vocoder_losses(
                outputs=outputs,
                harmonic_target=batch["harmonic_target"],
                noise_target=batch["noise_target"],
                periodic_gate_target=batch["periodic_gate_target"],
                noise_gate_target=batch["noise_gate_target"],
                aligned_waveform=batch["aligned_waveform"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                harmonic_weight=1.0,
                noise_weight=1.0,
                periodic_gate_weight=0.2,
                noise_gate_weight=0.2,
                activity_gate_weight=float(activity_gate_weight),
                waveform_weight=0.5,
                stft_weight=0.5,
                rms_guard_weight=0.2,
                use_predicted_activity_gate=bool(use_predicted_activity_gate),
            )
            predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"])
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=outputs["waveform_frames"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
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
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "activity_gate_weight_for_metrics": float(activity_gate_weight),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_predicted_activity_gate_apply_mode,
        },
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if selection_summary is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if selection_summary is None else str(selection_target),
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(exported_records),
        "records": exported_records,
        "notes": [
            "aligned_target.wav is the frame-aligned target waveform used by the current Stage5 bootstrap objective.",
            "decoded.wav is reconstructed from the checkpoint's waveform_frames head via overlap-add with the current export-side gate settings.",
            "When use_predicted_activity_gate is enabled, predicted_activity_gate_floor, predicted_activity_gate_smoothing_frames, and predicted_activity_gate_apply_mode define export-side gate softening only; they do not rewrite the saved checkpoint.",
            "decoded_pitch_matched.wav is an optional listening-only variant that globally pitch-shifts decoded.wav toward the aligned target's median voiced F0 while preserving duration.",
            "audit_proxy.wav is a low-frequency audit render derived from decoded.wav and gated by aligned_target activity so current GUI listening is less fatiguing and target silence remains silent.",
            f"proxy_audio_path in the GUI-compatible manifest points to {resolved_listening_audio_source}.wav for primary listening; the non-primary audio is retained for technical inspection.",
            "This export is for human listening and checkpoint comparison; it is still not the final multi-resolution or adversarial vocoder route from the design doc.",
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
    selected = payload.get(target_key)
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
    return matched_path, dict(selected)


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


def build_model_from_checkpoint(
    checkpoint_payload: dict[str, object],
    first_batch: dict[str, torch.Tensor],
    first_runtime: dict[str, int],
) -> NoResidualSourceFilterVocoderScaffold:
    state_dict = dict(checkpoint_payload["model_state_dict"])
    hidden_dim = int(state_dict["periodic_encoder.0.weight"].shape[0])
    harmonic_bins = int(state_dict["harmonic_envelope.weight"].shape[0])
    noise_bins = int(state_dict["noise_envelope.weight"].shape[0])
    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(first_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(first_batch["noise_branch_features"].shape[-1]),
        hidden_dim=hidden_dim,
        harmonic_bins=harmonic_bins,
        noise_bins=noise_bins,
        frame_length=int(first_runtime["frame_length"]),
    )
    model.load_state_dict(state_dict)
    return model


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


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
) -> str:
    suffix = describe_waveform_decode_variant(
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=str(predicted_activity_gate_apply_mode),
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
) -> str:
    if not bool(use_predicted_activity_gate):
        return "__decode_gate_off"
    parts: list[str] = []
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
    return "__decode_gate_" + "_".join(parts)


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
        "dataset_index_path": summary["dataset_index_path"],
        "split_name": summary["split_name"],
        "sample_count": summary["sample_count"],
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
        f"- sample_count: {summary['sample_count']}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"input_audio_path={record['input_audio_path']} "
            f"listening_audio_path={record.get('listening_audio_path')} "
            f"decoded_pitch_matched_audio_path={record.get('decoded_pitch_matched_audio_path')} "
            f"proxy_audio_path={record['proxy_audio_path']}"
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
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"loss_total={record['loss_metrics']['loss_total']} "
            f"aligned_target_audio_path={record['aligned_target_audio_path']} "
            f"decoded_audio_path={record['decoded_audio_path']} "
            f"decoded_pitch_matched_audio_path={record.get('decoded_pitch_matched_audio_path')} "
            f"audit_proxy_audio_path={record.get('audit_proxy_audio_path')}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
