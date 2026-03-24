from __future__ import annotations

from datetime import datetime
import json
import math
import os
from pathlib import Path
import random
from time import perf_counter

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import load_waveform
from v5vc.offline_teacher_runtime import resolve_runtime_device
from v5vc.offline_teacher_downstream_contract import export_offline_mvp_teacher_downstream_contract
from v5vc.offline_teacher_vocoder_input_scaffold import (
    build_offline_mvp_teacher_vocoder_input_scaffold,
    normalize_energy_log_rms_for_stage5,
)
from v5vc.offline_vocoder_scaffold import NoResidualSourceFilterVocoderScaffold

DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE = "pre_overlap_add"
DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD = 0.02
SUPPORTED_TEACHER_VOCODER_SCAFFOLD_VERSIONS = {
    "offline_teacher_vocoder_input_scaffold_v1",
    "offline_teacher_vocoder_input_scaffold_v2",
}
SUPPORTED_TRAINING_PACKAGE_VERSIONS = {
    "offline_mvp_nores_vocoder_train_targets_v1",
    "offline_mvp_nores_vocoder_train_targets_v2",
}


def normalize_training_reconstruction_frame_gain_apply_mode(frame_gain_apply_mode: str) -> str:
    normalized = str(frame_gain_apply_mode).strip().lower()
    if normalized not in {"pre_overlap_add", "post_ola_envelope"}:
        raise ValueError(f"Unsupported training reconstruction frame_gain_apply_mode: {frame_gain_apply_mode}")
    return normalized


def build_offline_mvp_nores_vocoder_training_package(
    scaffold_path: Path,
    target_audio_path: Path,
    output_dir: Path,
    harmonic_bins: int,
    noise_bins: int,
    sample_rate: int | None,
    frame_length: int | None,
    hop_length: int | None,
) -> None:
    scaffold_path = scaffold_path.resolve()
    target_audio_path = target_audio_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = torch.load(scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported scaffold payload type: {type(payload)!r}")
    scaffold_version = str(payload.get("scaffold_version"))
    if scaffold_version not in SUPPORTED_TEACHER_VOCODER_SCAFFOLD_VERSIONS:
        raise ValueError(
            "Unsupported scaffold_version for no-residual vocoder training package: "
            f"{payload.get('scaffold_version')!r}"
        )

    source_runtime = dict(payload.get("source_runtime", {}))
    resolved_sample_rate = resolve_required_int(
        runtime_value=source_runtime.get("sample_rate"),
        override_value=sample_rate,
        field_name="sample_rate",
    )
    resolved_frame_length = resolve_required_int(
        runtime_value=source_runtime.get("frame_length"),
        override_value=frame_length,
        field_name="frame_length",
    )
    resolved_hop_length = resolve_required_int(
        runtime_value=source_runtime.get("hop_length"),
        override_value=hop_length,
        field_name="hop_length",
    )

    branch_scaffold = dict(payload["branch_scaffold"])
    periodic_branch_features = branch_scaffold["periodic_branch_features"].to(torch.float32)
    noise_branch_features = branch_scaffold["noise_branch_features"].to(torch.float32)
    available_controls = dict(payload["available_controls"])
    frame_count = int(payload["frame_count"])
    has_v2_core = scaffold_version == "offline_teacher_vocoder_input_scaffold_v2"

    waveform, actual_sample_rate = load_waveform(target_audio_path)
    if int(actual_sample_rate) != int(resolved_sample_rate):
        raise ValueError(
            "Target audio sample rate does not match scaffold runtime metadata: "
            f"audio={actual_sample_rate} scaffold={resolved_sample_rate}"
        )

    aligned_waveform = align_waveform_to_teacher_frames(
        waveform=waveform,
        frame_count=frame_count,
        frame_length=resolved_frame_length,
        hop_length=resolved_hop_length,
    )
    harmonic_target, noise_target, spectrogram_stats = build_branch_spectral_targets(
        waveform=aligned_waveform,
        frame_length=resolved_frame_length,
        hop_length=resolved_hop_length,
        harmonic_bins=int(harmonic_bins),
        noise_bins=int(noise_bins),
    )

    voiced_proxy = available_controls["voiced_proxy"].to(torch.float32)
    aperiodicity_proxy = available_controls["aperiodicity_proxy"].to(torch.float32)
    event_presence_proxy = available_controls["event_presence_proxy"].to(torch.float32)
    if has_v2_core:
        vuv = available_controls["vuv"].to(torch.float32)
        aper = available_controls["aper"].to(torch.float32)
        energy_control = available_controls["E"].to(torch.float32)
        normalized_energy_control = available_controls.get("E_log_rms_norm")
        if isinstance(normalized_energy_control, torch.Tensor):
            normalized_energy_control = normalized_energy_control.to(torch.float32)
        else:
            normalized_energy_control = normalize_energy_log_rms_for_stage5(energy_control)
        periodic_gate_target = vuv.clamp(0.0, 1.0)
        noise_gate_target = torch.maximum(aper * normalized_energy_control, event_presence_proxy).clamp(0.0, 1.0)
        energy_proxy = normalized_energy_control.clamp(0.0, 1.0)
        training_package_version = "offline_mvp_nores_vocoder_train_targets_v2"
        notes = [
            "This package provides a minimal Stage5 spectral reconstruction target set for the no-residual baseline route.",
            "Targets are frame-aligned to the teacher runtime semantics and remain a proxy objective, not the final waveform/GAN training contract from the design doc.",
            "periodic_gate_target now uses explicit vuv, while noise_gate_target uses max(aper * E_log_rms_norm, event_presence_proxy) so unvoiced low-energy frames do not force the noise branch fully open.",
            "aligned_waveform is retained so later decoder/waveform-STFT bootstrap runs can reuse the same package contract.",
        ]
    else:
        periodic_gate_target = voiced_proxy.clamp(0.0, 1.0)
        noise_gate_target = torch.maximum(aperiodicity_proxy, event_presence_proxy).clamp(0.0, 1.0)
        energy_proxy = available_controls["energy_proxy"].to(torch.float32)
        training_package_version = "offline_mvp_nores_vocoder_train_targets_v1"
        notes = [
            "This package provides a minimal Stage5 spectral reconstruction target set for the no-residual baseline route.",
            "Targets are frame-aligned to the teacher runtime semantics and remain a proxy objective, not the final waveform/GAN training contract from the design doc.",
            "periodic_gate_target uses voiced_proxy, and noise_gate_target uses max(aperiodicity_proxy, event_presence_proxy).",
            "aligned_waveform is retained so later decoder/waveform-STFT bootstrap runs can reuse the same package contract.",
        ]

    training_payload = {
        "training_package_version": training_package_version,
        "source_scaffold_path": scaffold_path.as_posix(),
        "source_scaffold_version": scaffold_version,
        "target_audio_path": target_audio_path.as_posix(),
        "source_audio_path": payload.get("source_audio_path"),
        "frame_count": frame_count,
        "runtime": {
            "sample_rate": int(resolved_sample_rate),
            "frame_length": int(resolved_frame_length),
            "hop_length": int(resolved_hop_length),
        },
        "inputs": {
            "periodic_branch_features": periodic_branch_features,
            "noise_branch_features": noise_branch_features,
        },
        "targets": {
            "harmonic_envelope_target": harmonic_target,
            "noise_envelope_target": noise_target,
            "periodic_gate_target": periodic_gate_target,
            "noise_gate_target": noise_gate_target,
            "energy_proxy_target": energy_proxy.clamp(0.0, 1.0),
        },
        "aligned_waveform": aligned_waveform.to(torch.float32),
        "notes": notes,
    }

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "training_package_version": training_package_version,
        "source_scaffold_path": scaffold_path.as_posix(),
        "source_scaffold_version": scaffold_version,
        "target_audio_path": target_audio_path.as_posix(),
        "source_audio_path": payload.get("source_audio_path"),
        "runtime": training_payload["runtime"],
        "frame_count": frame_count,
        "aligned_waveform_samples": int(aligned_waveform.shape[0]),
        "periodic_input_dim": int(periodic_branch_features.shape[-1]),
        "noise_input_dim": int(noise_branch_features.shape[-1]),
        "harmonic_target_dim": int(harmonic_target.shape[-1]),
        "noise_target_dim": int(noise_target.shape[-1]),
        "spectrogram_stats": spectrogram_stats,
        "notes": list(training_payload["notes"]),
    }

    pt_path = output_dir / "offline_mvp_nores_vocoder_train_targets.pt"
    json_path = output_dir / "offline_mvp_nores_vocoder_train_targets.json"
    md_path = output_dir / "offline_mvp_nores_vocoder_train_targets.md"
    torch.save(training_payload, pt_path)
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_training_package_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def run_offline_mvp_nores_vocoder_training_step(
    training_package_path: Path,
    output_dir: Path,
    device: str,
    seed: int,
    deterministic: bool,
    hidden_dim: int,
    learning_rate: float,
    max_grad_norm: float,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
) -> None:
    training_package_path = training_package_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_device = resolve_runtime_device(device)
    reproducibility = set_training_seed(
        int(seed),
        resolved_device,
        deterministic=bool(deterministic),
    )
    resolved_reconstruction_frame_gain_apply_mode = normalize_training_reconstruction_frame_gain_apply_mode(
        reconstruction_frame_gain_apply_mode
    )

    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage5] nores_vocoder_train_step_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} "
        f"training_package={training_package_path.as_posix()}"
    )

    payload = load_training_package_payload(training_package_path)
    runtime = extract_training_runtime(payload)
    training_batch = move_batch_to_device(
        extract_training_batch(payload),
        resolved_device,
    )
    periodic_branch_features = training_batch["periodic_branch_features"]
    noise_branch_features = training_batch["noise_branch_features"]
    harmonic_target = training_batch["harmonic_target"]
    noise_target = training_batch["noise_target"]
    periodic_gate_target = training_batch["periodic_gate_target"]
    noise_gate_target = training_batch["noise_gate_target"]

    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(periodic_branch_features.shape[-1]),
        noise_input_dim=int(noise_branch_features.shape[-1]),
        hidden_dim=int(hidden_dim),
        harmonic_bins=int(harmonic_target.shape[-1]),
        noise_bins=int(noise_target.shape[-1]),
        frame_length=int(runtime["frame_length"]),
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))
    model.train()

    outputs = model(
        periodic_branch_features=periodic_branch_features,
        noise_branch_features=noise_branch_features,
    )
    total_loss, loss_metrics = compute_nores_vocoder_losses(
        outputs=outputs,
        harmonic_target=harmonic_target,
        noise_target=noise_target,
        periodic_gate_target=periodic_gate_target,
        noise_gate_target=noise_gate_target,
        aligned_waveform=training_batch["aligned_waveform"],
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        harmonic_weight=harmonic_weight,
        noise_weight=noise_weight,
        periodic_gate_weight=periodic_gate_weight,
        noise_gate_weight=noise_gate_weight,
        activity_gate_weight=activity_gate_weight,
        waveform_weight=waveform_weight,
        stft_weight=stft_weight,
        rms_guard_weight=rms_guard_weight,
        active_template_weight=active_template_weight,
        frame_delta_weight=frame_delta_weight,
        use_predicted_activity_gate=use_predicted_activity_gate,
        reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
    )
    optimizer.zero_grad(set_to_none=True)
    total_loss.backward()
    grad_norm = float(clip_grad_norm_(model.parameters(), float(max_grad_norm)).item())
    optimizer.step()

    run_ended_at = datetime.now()
    run_duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "training_package_path": training_package_path.as_posix(),
        "model": {
            "name": "no_residual_source_filter_vocoder_scaffold",
            "hidden_dim": int(hidden_dim),
            "harmonic_bins": int(harmonic_target.shape[-1]),
            "noise_bins": int(noise_target.shape[-1]),
            "decoder_frame_length": int(runtime["frame_length"]),
        },
        "optimizer": {
            "name": "Adam",
            "learning_rate": float(learning_rate),
            "max_grad_norm": float(max_grad_norm),
        },
        "runtime": {
            "device": str(resolved_device),
        },
        "reproducibility": reproducibility,
        "loss_weights": {
            "harmonic": float(harmonic_weight),
            "noise": float(noise_weight),
            "periodic_gate": float(periodic_gate_weight),
            "noise_gate": float(noise_gate_weight),
            "activity_gate": float(activity_gate_weight),
            "waveform": float(waveform_weight),
            "stft": float(stft_weight),
            "rms_guard": float(rms_guard_weight),
            "active_template": float(active_template_weight),
            "frame_delta": float(frame_delta_weight),
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "reconstruction_frame_gain_apply_mode": resolved_reconstruction_frame_gain_apply_mode,
        },
        "train_step": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(run_duration_sec, 6),
            "frame_count": int(payload["frame_count"]),
            "grad_norm": round(grad_norm, 6),
            "loss_metrics": loss_metrics,
        },
        "notes": [
            "This is a single-step Stage5 plumbing validation for the no-residual baseline route.",
            "The objective may combine proxy spectral/gate targets with optional aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder recipe from the design doc.",
            "Use this step to verify loss, backward, optimizer, and checkpoint plumbing before adding adversarial or larger-scale decoder training.",
        ],
    }

    checkpoint_path = output_dir / "offline_mvp_nores_vocoder_train_step.pt"
    json_path = output_dir / "offline_mvp_nores_vocoder_train_step.json"
    md_path = output_dir / "offline_mvp_nores_vocoder_train_step.md"
    torch.save(
        {
            "training_step_version": "offline_mvp_nores_vocoder_train_step_v1",
            "training_package_path": training_package_path.as_posix(),
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "summary": summary,
        },
        checkpoint_path,
    )
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_training_step_markdown(summary, checkpoint_path),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage5] nores_vocoder_train_step_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} "
        f"duration_sec={round(run_duration_sec, 6)} "
        f"loss_total={loss_metrics['loss_total']} "
        f"checkpoint={checkpoint_path.as_posix()}"
    )


def run_offline_mvp_nores_vocoder_training_loop(
    training_package_path: Path,
    output_dir: Path,
    validation_package_path: Path | None,
    device: str,
    seed: int,
    deterministic: bool,
    num_steps: int,
    validation_interval: int,
    checkpoint_interval: int,
    hidden_dim: int,
    learning_rate: float,
    max_grad_norm: float,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
) -> None:
    training_package_path = training_package_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_device = resolve_runtime_device(device)
    reproducibility = set_training_seed(
        int(seed),
        resolved_device,
        deterministic=bool(deterministic),
    )
    resolved_reconstruction_frame_gain_apply_mode = normalize_training_reconstruction_frame_gain_apply_mode(
        reconstruction_frame_gain_apply_mode
    )
    checkpoints_dir = output_dir / "checkpoints"
    logs_dir = output_dir / "logs"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage5] nores_vocoder_training_loop_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} "
        f"training_package={training_package_path.as_posix()}"
    )

    training_payload = load_training_package_payload(training_package_path)
    training_runtime = extract_training_runtime(training_payload)
    training_batch = move_batch_to_device(
        extract_training_batch(training_payload),
        resolved_device,
    )

    resolved_validation_package_path = None
    if validation_package_path is not None:
        resolved_validation_package_path = validation_package_path.resolve()
        validation_payload = load_training_package_payload(resolved_validation_package_path)
    else:
        validation_payload = training_payload
    validation_runtime = extract_training_runtime(validation_payload)
    validation_batch = move_batch_to_device(
        extract_training_batch(validation_payload),
        resolved_device,
    )

    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(training_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(training_batch["noise_branch_features"].shape[-1]),
        hidden_dim=int(hidden_dim),
        harmonic_bins=int(training_batch["harmonic_target"].shape[-1]),
        noise_bins=int(training_batch["noise_target"].shape[-1]),
        frame_length=int(training_runtime["frame_length"]),
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))

    effective_num_steps = max(1, int(num_steps))
    effective_validation_interval = max(1, int(validation_interval))
    effective_checkpoint_interval = max(1, int(checkpoint_interval))
    step_history: list[dict[str, object]] = []
    validation_history: list[dict[str, object]] = []
    checkpoint_paths: list[str] = []

    for step_index in range(effective_num_steps):
        current_step = step_index + 1
        step_started_at = datetime.now()
        step_started_perf = perf_counter()
        model.train()
        outputs = model(
            periodic_branch_features=training_batch["periodic_branch_features"],
            noise_branch_features=training_batch["noise_branch_features"],
        )
        total_loss, loss_metrics = compute_nores_vocoder_losses(
            outputs=outputs,
            harmonic_target=training_batch["harmonic_target"],
            noise_target=training_batch["noise_target"],
            periodic_gate_target=training_batch["periodic_gate_target"],
            noise_gate_target=training_batch["noise_gate_target"],
            aligned_waveform=training_batch["aligned_waveform"],
            frame_length=int(training_runtime["frame_length"]),
            hop_length=int(training_runtime["hop_length"]),
            harmonic_weight=harmonic_weight,
            noise_weight=noise_weight,
            periodic_gate_weight=periodic_gate_weight,
            noise_gate_weight=noise_gate_weight,
            activity_gate_weight=activity_gate_weight,
            waveform_weight=waveform_weight,
            stft_weight=stft_weight,
            rms_guard_weight=rms_guard_weight,
            active_template_weight=active_template_weight,
            frame_delta_weight=frame_delta_weight,
            use_predicted_activity_gate=use_predicted_activity_gate,
            reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
        )
        optimizer.zero_grad(set_to_none=True)
        total_loss.backward()
        grad_norm = float(clip_grad_norm_(model.parameters(), float(max_grad_norm)).item())
        optimizer.step()

        step_ended_at = datetime.now()
        step_duration_sec = perf_counter() - step_started_perf
        step_payload = {
            "step": current_step,
            "started_at": step_started_at.isoformat(timespec="seconds"),
            "ended_at": step_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(step_duration_sec, 6),
            "frame_count": int(training_payload["frame_count"]),
            "grad_norm": round(grad_norm, 6),
            "loss_metrics": loss_metrics,
            "status": "step_completed",
        }
        step_history.append(step_payload)
        (logs_dir / f"nores_vocoder_loop.step{current_step}.json").write_text(
            json.dumps(step_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        print(
            "[stage5] nores_vocoder_training_loop_step_completed "
            f"step={current_step} ended_at={step_ended_at.isoformat(timespec='seconds')} "
            f"duration_sec={round(step_duration_sec, 6)} loss_total={loss_metrics['loss_total']}"
        )

        if current_step % effective_validation_interval == 0 or current_step == effective_num_steps:
            validation_payload_summary = run_nores_vocoder_validation_pass(
                model=model,
                validation_batch=validation_batch,
                step=current_step,
                harmonic_weight=harmonic_weight,
                noise_weight=noise_weight,
                periodic_gate_weight=periodic_gate_weight,
                noise_gate_weight=noise_gate_weight,
                activity_gate_weight=activity_gate_weight,
                waveform_weight=waveform_weight,
                stft_weight=stft_weight,
                rms_guard_weight=rms_guard_weight,
                active_template_weight=active_template_weight,
                frame_delta_weight=frame_delta_weight,
                use_predicted_activity_gate=use_predicted_activity_gate,
                reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
                frame_length=int(validation_runtime["frame_length"]),
                hop_length=int(validation_runtime["hop_length"]),
                validation_source=(
                    "separate_validation_package"
                    if resolved_validation_package_path is not None
                    else "train_targets_reused"
                ),
            )
            validation_history.append(validation_payload_summary)

        if current_step % effective_checkpoint_interval == 0 or current_step == effective_num_steps:
            checkpoint_path = checkpoints_dir / f"offline_mvp_nores_vocoder_loop.step{current_step}.pt"
            torch.save(
                {
                    "training_loop_version": "offline_mvp_nores_vocoder_training_loop_v1",
                    "step": current_step,
                    "training_package_path": training_package_path.as_posix(),
                    "validation_package_path": (
                        None
                        if resolved_validation_package_path is None
                        else resolved_validation_package_path.as_posix()
                    ),
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "step_metrics": step_payload,
                    "validation_metrics": None if not validation_history else validation_history[-1],
                },
                checkpoint_path,
            )
            checkpoint_paths.append(checkpoint_path.as_posix())

    run_ended_at = datetime.now()
    run_duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "training_package_path": training_package_path.as_posix(),
        "validation_package_path": (
            None if resolved_validation_package_path is None else resolved_validation_package_path.as_posix()
        ),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(run_duration_sec, 6),
        },
        "model": {
            "name": "no_residual_source_filter_vocoder_scaffold",
            "hidden_dim": int(hidden_dim),
            "harmonic_bins": int(training_batch["harmonic_target"].shape[-1]),
            "noise_bins": int(training_batch["noise_target"].shape[-1]),
            "decoder_frame_length": int(training_runtime["frame_length"]),
        },
        "runtime": {
            "device": str(resolved_device),
        },
        "reproducibility": reproducibility,
        "training": {
            "seed": int(seed),
            "deterministic": bool(reproducibility["deterministic_algorithms"]),
            "num_steps": effective_num_steps,
            "validation_interval": effective_validation_interval,
            "checkpoint_interval": effective_checkpoint_interval,
            "learning_rate": float(learning_rate),
            "max_grad_norm": float(max_grad_norm),
            "loss_weights": {
                "harmonic": float(harmonic_weight),
                "noise": float(noise_weight),
                "periodic_gate": float(periodic_gate_weight),
                "noise_gate": float(noise_gate_weight),
                "activity_gate": float(activity_gate_weight),
                "waveform": float(waveform_weight),
                "stft": float(stft_weight),
                "rms_guard": float(rms_guard_weight),
                "active_template": float(active_template_weight),
                "frame_delta": float(frame_delta_weight),
                "use_predicted_activity_gate": bool(use_predicted_activity_gate),
                "reconstruction_frame_gain_apply_mode": resolved_reconstruction_frame_gain_apply_mode,
            },
        },
        "train_frame_count": int(training_payload["frame_count"]),
        "validation_frame_count": int(validation_payload["frame_count"]),
        "step_history": step_history,
        "validation_history": validation_history,
        "artifacts": {
            "checkpoint_paths": checkpoint_paths,
            "latest_checkpoint_path": None if not checkpoint_paths else checkpoint_paths[-1],
            "best_checkpoint": select_best_nores_vocoder_checkpoint(
                checkpoint_paths=checkpoint_paths,
                validation_history=validation_history,
            ),
        },
        "notes": [
            "This is a minimal Stage5 multi-step loop for the no-residual baseline route.",
            "The loop currently optimizes one aligned train-target package repeatedly to verify optimizer/checkpoint/validation plumbing before dataset-level batching.",
            "Validation can optionally reuse the train package or read a separate package, and may include aligned waveform/STFT bootstrap losses, but it is still not the final multi-resolution or adversarial vocoder objective.",
        ],
        "next_steps": [
            "Replace the single-package loop with dataset-level package sampling once multiple aligned target packages exist.",
            "Decide whether the next Stage5 objective should keep using the bootstrap waveform/STFT path or move to a stronger multi-resolution decoder recipe.",
            "Keep final-vocoder language disabled until decoder, validation, and audio export are truly added.",
        ],
    }

    summary_json_path = logs_dir / "offline_mvp_nores_vocoder_loop.summary.json"
    summary_md_path = output_dir / "offline_mvp_nores_vocoder_loop.summary.md"
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_training_loop_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage5] nores_vocoder_training_loop_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} "
        f"duration_sec={round(run_duration_sec, 6)} "
        f"latest_checkpoint={summary['artifacts']['latest_checkpoint_path']}"
    )


def build_offline_mvp_nores_vocoder_dataset_packages(
    train_split_path: Path,
    validation_split_path: Path | None,
    output_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    max_audio_sec: float | None,
    verify_against_full_pass: bool,
    max_train_records: int | None,
    max_validation_records: int | None,
    selection_mode: str,
    skip_existing: bool,
) -> None:
    train_split_path = train_split_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage5] nores_vocoder_dataset_packages_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} "
        f"output_dir={output_dir.as_posix()}"
    )

    train_records = select_dataset_records(
        records=load_jsonl(train_split_path),
        max_records=max_train_records,
        selection_mode=selection_mode,
    )
    if validation_split_path is not None:
        validation_split_path = validation_split_path.resolve()
        validation_records = select_dataset_records(
            records=load_jsonl(validation_split_path),
            max_records=max_validation_records,
            selection_mode=selection_mode,
        )
    else:
        validation_records = []

    packages_dir = output_dir / "packages"
    train_entries = build_dataset_packages_for_split(
        records=train_records,
        split_name="train",
        packages_dir=packages_dir,
        route_handoff_path=route_handoff_path,
        checkpoint_path=checkpoint_path,
        calibration_asset_path=calibration_asset_path,
        chunk_samples=chunk_samples,
        chunk_ms=chunk_ms,
        device=device,
        max_audio_sec=max_audio_sec,
        verify_against_full_pass=verify_against_full_pass,
        skip_existing=skip_existing,
    )
    validation_entries = build_dataset_packages_for_split(
        records=validation_records,
        split_name="validation",
        packages_dir=packages_dir,
        route_handoff_path=route_handoff_path,
        checkpoint_path=checkpoint_path,
        calibration_asset_path=calibration_asset_path,
        chunk_samples=chunk_samples,
        chunk_ms=chunk_ms,
        device=device,
        max_audio_sec=max_audio_sec,
        verify_against_full_pass=verify_against_full_pass,
        skip_existing=skip_existing,
    )
    run_ended_at = datetime.now()
    run_duration_sec = perf_counter() - run_started_perf

    index_payload = {
        "dataset_index_version": "offline_mvp_nores_vocoder_dataset_index_v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(run_duration_sec, 6),
        },
        "selection_mode": str(selection_mode),
        "train_split_path": train_split_path.as_posix(),
        "validation_split_path": None if validation_split_path is None else validation_split_path.as_posix(),
        "train_packages": train_entries,
        "validation_packages": validation_entries,
        "notes": [
            "This dataset index is a Stage5 package-level bridge built on top of the teacher-first contract path.",
            "Each package still contains proxy spectral/gate targets rather than a final waveform decoder objective.",
            "Current package generation may reload the teacher checkpoint per record, so this builder is a functional baseline rather than a throughput-optimized exporter.",
        ],
    }
    index_payload["summary"] = summarize_dataset_package_index(
        train_packages=train_entries,
        validation_packages=validation_entries,
        run_duration_sec=run_duration_sec,
    )

    index_json_path = output_dir / "offline_mvp_nores_vocoder_dataset_index.json"
    index_md_path = output_dir / "offline_mvp_nores_vocoder_dataset_index.md"
    index_json_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    index_md_path.write_text(
        build_dataset_index_markdown(index_payload),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage5] nores_vocoder_dataset_packages_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} "
        f"duration_sec={round(run_duration_sec, 6)} "
        f"train_packages={len(train_entries)} validation_packages={len(validation_entries)}"
    )


def run_offline_mvp_nores_vocoder_dataset_training_loop(
    dataset_index_path: Path,
    output_dir: Path,
    device: str,
    num_steps: int,
    packages_per_step: int,
    validation_interval: int,
    checkpoint_interval: int,
    sampler_mode: str,
    seed: int,
    deterministic: bool,
    hidden_dim: int,
    learning_rate: float,
    max_grad_norm: float,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
) -> None:
    dataset_index_path = dataset_index_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_device = resolve_runtime_device(device)
    reproducibility = set_training_seed(
        int(seed),
        resolved_device,
        deterministic=bool(deterministic),
    )
    resolved_reconstruction_frame_gain_apply_mode = normalize_training_reconstruction_frame_gain_apply_mode(
        reconstruction_frame_gain_apply_mode
    )
    checkpoints_dir = output_dir / "checkpoints"
    logs_dir = output_dir / "logs"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    print(
        "[stage5] nores_vocoder_dataset_training_loop_started "
        f"started_at={run_started_at.isoformat(timespec='seconds')} "
        f"dataset_index={dataset_index_path.as_posix()}"
    )

    index_payload = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    if str(index_payload.get("dataset_index_version")) != "offline_mvp_nores_vocoder_dataset_index_v1":
        raise ValueError(
            "Unsupported dataset_index_version for no-residual vocoder dataset loop: "
            f"{index_payload.get('dataset_index_version')!r}"
        )
    train_packages = list(index_payload.get("train_packages", []))
    validation_packages = list(index_payload.get("validation_packages", []))
    if not train_packages:
        raise ValueError("Dataset index does not contain any train_packages.")

    initial_payload = load_training_package_payload(Path(train_packages[0]["training_package_path"]))
    initial_runtime = extract_training_runtime(initial_payload)
    initial_batch = move_batch_to_device(
        extract_training_batch(initial_payload),
        resolved_device,
    )
    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(initial_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(initial_batch["noise_branch_features"].shape[-1]),
        hidden_dim=int(hidden_dim),
        harmonic_bins=int(initial_batch["harmonic_target"].shape[-1]),
        noise_bins=int(initial_batch["noise_target"].shape[-1]),
        frame_length=int(initial_runtime["frame_length"]),
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))

    effective_num_steps = max(1, int(num_steps))
    effective_packages_per_step = max(1, int(packages_per_step))
    effective_validation_interval = max(1, int(validation_interval))
    effective_checkpoint_interval = max(1, int(checkpoint_interval))
    normalized_sampler_mode = str(sampler_mode).strip().lower()
    if normalized_sampler_mode not in {"sequential", "shuffle"}:
        raise ValueError(f"Unsupported sampler_mode: {sampler_mode}")
    rng = random.Random(int(seed))

    train_cursor = 0
    train_order = list(range(len(train_packages)))
    if normalized_sampler_mode == "shuffle":
        rng.shuffle(train_order)

    step_history: list[dict[str, object]] = []
    validation_history: list[dict[str, object]] = []
    checkpoint_paths: list[str] = []

    for step_index in range(effective_num_steps):
        current_step = step_index + 1
        step_started_at = datetime.now()
        step_started_perf = perf_counter()
        selected_entries, train_cursor, train_order = select_package_entries_for_step(
            packages=train_packages,
            packages_per_step=effective_packages_per_step,
            sampler_mode=normalized_sampler_mode,
            rng=rng,
            current_order=train_order,
            current_cursor=train_cursor,
        )
        model.train()
        accumulated_loss = None
        package_metrics: list[dict[str, object]] = []
        for entry in selected_entries:
            payload = load_training_package_payload(Path(entry["training_package_path"]))
            runtime = extract_training_runtime(payload)
            batch = move_batch_to_device(
                extract_training_batch(payload),
                resolved_device,
            )
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
            )
            total_loss, loss_metrics = compute_nores_vocoder_losses(
                outputs=outputs,
                harmonic_target=batch["harmonic_target"],
                noise_target=batch["noise_target"],
                periodic_gate_target=batch["periodic_gate_target"],
                noise_gate_target=batch["noise_gate_target"],
                aligned_waveform=batch["aligned_waveform"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                harmonic_weight=harmonic_weight,
                noise_weight=noise_weight,
                periodic_gate_weight=periodic_gate_weight,
                noise_gate_weight=noise_gate_weight,
                activity_gate_weight=activity_gate_weight,
                waveform_weight=waveform_weight,
                stft_weight=stft_weight,
                rms_guard_weight=rms_guard_weight,
                active_template_weight=active_template_weight,
                frame_delta_weight=frame_delta_weight,
                use_predicted_activity_gate=use_predicted_activity_gate,
                reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
            )
            accumulated_loss = total_loss if accumulated_loss is None else accumulated_loss + total_loss
            package_metrics.append(
                {
                    "record_id": entry["record_id"],
                    "training_package_path": entry["training_package_path"],
                    "frame_count": int(payload["frame_count"]),
                    "loss_metrics": loss_metrics,
                }
            )
        if accumulated_loss is None:
            raise RuntimeError("No packages were selected for the current training step.")
        total_loss = accumulated_loss / float(len(selected_entries))
        optimizer.zero_grad(set_to_none=True)
        total_loss.backward()
        grad_norm = float(clip_grad_norm_(model.parameters(), float(max_grad_norm)).item())
        optimizer.step()

        step_ended_at = datetime.now()
        step_duration_sec = perf_counter() - step_started_perf
        step_payload = {
            "step": current_step,
            "started_at": step_started_at.isoformat(timespec="seconds"),
            "ended_at": step_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(step_duration_sec, 6),
            "packages_per_step": len(selected_entries),
            "record_ids": [entry["record_id"] for entry in selected_entries],
            "loss_metrics": average_loss_metrics([item["loss_metrics"] for item in package_metrics]),
            "package_metrics": package_metrics,
            "grad_norm": round(grad_norm, 6),
            "status": "step_completed",
        }
        step_history.append(step_payload)
        (logs_dir / f"nores_vocoder_dataset_loop.step{current_step}.json").write_text(
            json.dumps(step_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        print(
            "[stage5] nores_vocoder_dataset_training_loop_step_completed "
            f"step={current_step} ended_at={step_ended_at.isoformat(timespec='seconds')} "
            f"duration_sec={round(step_duration_sec, 6)} loss_total={step_payload['loss_metrics']['loss_total']}"
        )

        if current_step % effective_validation_interval == 0 or current_step == effective_num_steps:
            if validation_packages:
                validation_payload_summary = run_nores_vocoder_dataset_validation_pass(
                    model=model,
                    package_entries=validation_packages,
                    device=resolved_device,
                    step=current_step,
                    harmonic_weight=harmonic_weight,
                    noise_weight=noise_weight,
                    periodic_gate_weight=periodic_gate_weight,
                    noise_gate_weight=noise_gate_weight,
                    activity_gate_weight=activity_gate_weight,
                    waveform_weight=waveform_weight,
                    stft_weight=stft_weight,
                    rms_guard_weight=rms_guard_weight,
                    active_template_weight=active_template_weight,
                    frame_delta_weight=frame_delta_weight,
                    use_predicted_activity_gate=use_predicted_activity_gate,
                    reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
                    validation_source="validation_packages",
                )
            else:
                validation_payload_summary = run_nores_vocoder_dataset_validation_pass(
                    model=model,
                    package_entries=train_packages,
                    device=resolved_device,
                    step=current_step,
                    harmonic_weight=harmonic_weight,
                    noise_weight=noise_weight,
                    periodic_gate_weight=periodic_gate_weight,
                    noise_gate_weight=noise_gate_weight,
                    activity_gate_weight=activity_gate_weight,
                    waveform_weight=waveform_weight,
                    stft_weight=stft_weight,
                    rms_guard_weight=rms_guard_weight,
                    active_template_weight=active_template_weight,
                    frame_delta_weight=frame_delta_weight,
                    use_predicted_activity_gate=use_predicted_activity_gate,
                    reconstruction_frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
                    validation_source="train_packages_reused",
                )
            validation_history.append(validation_payload_summary)

        if current_step % effective_checkpoint_interval == 0 or current_step == effective_num_steps:
            checkpoint_path = checkpoints_dir / f"offline_mvp_nores_vocoder_dataset_loop.step{current_step}.pt"
            torch.save(
                {
                    "training_loop_version": "offline_mvp_nores_vocoder_dataset_training_loop_v1",
                    "step": current_step,
                    "dataset_index_path": dataset_index_path.as_posix(),
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "step_metrics": step_payload,
                    "validation_metrics": None if not validation_history else validation_history[-1],
                },
                checkpoint_path,
            )
            checkpoint_paths.append(checkpoint_path.as_posix())

    run_ended_at = datetime.now()
    run_duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "dataset_index_path": dataset_index_path.as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(run_duration_sec, 6),
        },
        "dataset": {
            "train_package_count": len(train_packages),
            "validation_package_count": len(validation_packages),
        },
        "model": {
            "name": "no_residual_source_filter_vocoder_scaffold",
            "hidden_dim": int(hidden_dim),
            "harmonic_bins": int(initial_batch["harmonic_target"].shape[-1]),
            "noise_bins": int(initial_batch["noise_target"].shape[-1]),
            "decoder_frame_length": int(initial_runtime["frame_length"]),
        },
        "runtime": {
            "device": str(resolved_device),
        },
        "training": {
            "num_steps": effective_num_steps,
            "packages_per_step": effective_packages_per_step,
            "validation_interval": effective_validation_interval,
            "checkpoint_interval": effective_checkpoint_interval,
            "sampler_mode": normalized_sampler_mode,
            "seed": int(seed),
            "deterministic": bool(reproducibility["deterministic_algorithms"]),
            "learning_rate": float(learning_rate),
            "max_grad_norm": float(max_grad_norm),
            "loss_weights": {
                "harmonic": float(harmonic_weight),
                "noise": float(noise_weight),
                "periodic_gate": float(periodic_gate_weight),
                "noise_gate": float(noise_gate_weight),
                "activity_gate": float(activity_gate_weight),
                "waveform": float(waveform_weight),
                "stft": float(stft_weight),
                "rms_guard": float(rms_guard_weight),
                "active_template": float(active_template_weight),
                "frame_delta": float(frame_delta_weight),
                "use_predicted_activity_gate": bool(use_predicted_activity_gate),
                "reconstruction_frame_gain_apply_mode": resolved_reconstruction_frame_gain_apply_mode,
            },
        },
        "step_history": step_history,
        "validation_history": validation_history,
        "artifacts": {
            "checkpoint_paths": checkpoint_paths,
            "latest_checkpoint_path": None if not checkpoint_paths else checkpoint_paths[-1],
            "best_checkpoint": select_best_nores_vocoder_checkpoint(
                checkpoint_paths=checkpoint_paths,
                validation_history=validation_history,
            ),
        },
        "notes": [
            "This loop is the first dataset-level Stage5 path: each step now samples from multiple aligned target packages instead of reusing one package forever.",
            "Current package batches are still Python-level lists of variable-length packages rather than a packed tensor dataloader.",
            "Validation reflects the current objective mix, including optional aligned waveform/STFT bootstrap losses when enabled, and should not be confused with final vocoder generalization.",
        ],
        "next_steps": [
            "Scale the dataset index from tiny smoke subsets to a larger split-backed package pool once runtime cost is acceptable.",
            "Decide whether to keep package-level sequential loading or move to a cached/packed dataset for throughput.",
            "Decide whether the current bootstrap decoder objective should be scaled further or replaced by a stronger multi-resolution/adversarial waveform recipe.",
        ],
    }

    summary_json_path = logs_dir / "offline_mvp_nores_vocoder_dataset_loop.summary.json"
    summary_md_path = output_dir / "offline_mvp_nores_vocoder_dataset_loop.summary.md"
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_dataset_training_loop_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    print(
        "[stage5] nores_vocoder_dataset_training_loop_completed "
        f"ended_at={run_ended_at.isoformat(timespec='seconds')} "
        f"duration_sec={round(run_duration_sec, 6)} "
        f"latest_checkpoint={summary['artifacts']['latest_checkpoint_path']}"
    )


def resolve_required_int(
    runtime_value: object,
    override_value: int | None,
    field_name: str,
) -> int:
    if override_value is not None:
        return int(override_value)
    if runtime_value in {None, ""}:
        raise ValueError(
            f"Missing {field_name} in scaffold runtime metadata. "
            f"Provide --{field_name.replace('_', '-')} explicitly."
        )
    return int(runtime_value)


def load_training_package_payload(training_package_path: Path) -> dict[str, object]:
    payload = torch.load(training_package_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported training package payload type: {type(payload)!r}")
    if str(payload.get("training_package_version")) not in SUPPORTED_TRAINING_PACKAGE_VERSIONS:
        raise ValueError(
            "Unsupported training_package_version for no-residual vocoder training: "
            f"{payload.get('training_package_version')!r}"
        )
    return payload


def extract_training_batch(payload: dict[str, object]) -> dict[str, torch.Tensor]:
    inputs = dict(payload["inputs"])
    targets = dict(payload["targets"])
    return {
        "periodic_branch_features": inputs["periodic_branch_features"].to(torch.float32),
        "noise_branch_features": inputs["noise_branch_features"].to(torch.float32),
        "harmonic_target": targets["harmonic_envelope_target"].to(torch.float32),
        "noise_target": targets["noise_envelope_target"].to(torch.float32),
        "periodic_gate_target": targets["periodic_gate_target"].to(torch.float32),
        "noise_gate_target": targets["noise_gate_target"].to(torch.float32),
        "aligned_waveform": payload["aligned_waveform"].to(torch.float32),
    }


def extract_training_runtime(payload: dict[str, object]) -> dict[str, int]:
    runtime = dict(payload.get("runtime", {}))
    return {
        "sample_rate": int(runtime["sample_rate"]),
        "frame_length": int(runtime["frame_length"]),
        "hop_length": int(runtime["hop_length"]),
    }


def move_batch_to_device(
    batch: dict[str, torch.Tensor],
    device: torch.device,
) -> dict[str, torch.Tensor]:
    return {
        key: value.to(device)
        for key, value in batch.items()
    }


def set_training_seed(
    seed: int,
    device: torch.device,
    deterministic: bool = False,
) -> dict[str, object]:
    deterministic_enabled = bool(deterministic)
    if deterministic_enabled and device.type == "cuda":
        # CuBLAS needs an explicit workspace mode before the first matmul call
        # or PyTorch will only warn about non-deterministic GPU kernels.
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    torch.manual_seed(int(seed))
    if device.type == "cuda":
        torch.cuda.manual_seed_all(int(seed))
    torch.use_deterministic_algorithms(deterministic_enabled, warn_only=deterministic_enabled)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.benchmark = not deterministic_enabled
        torch.backends.cudnn.deterministic = deterministic_enabled
    return {
        "seed": int(seed),
        "deterministic_algorithms": deterministic_enabled,
        "cudnn_deterministic": bool(deterministic_enabled and device.type == "cuda"),
        "cudnn_benchmark": bool((not deterministic_enabled) and device.type == "cuda"),
    }


def select_dataset_records(
    records: list[dict[str, object]],
    max_records: int | None,
    selection_mode: str,
) -> list[dict[str, object]]:
    normalized_mode = str(selection_mode).strip().lower()
    selected = list(records)
    if normalized_mode == "shortest_duration":
        selected.sort(key=lambda item: float(dict(item.get("audio", {})).get("duration_sec", 0.0)))
    elif normalized_mode != "file_order":
        raise ValueError(f"Unsupported selection_mode: {selection_mode}")
    if max_records is not None:
        selected = selected[: max(0, int(max_records))]
    return selected


def build_dataset_packages_for_split(
    records: list[dict[str, object]],
    split_name: str,
    packages_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    max_audio_sec: float | None,
    verify_against_full_pass: bool,
    skip_existing: bool,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for record in records:
        record_started_perf = perf_counter()
        record_id = str(record["record_id"])
        audio_path = Path(str(record["audio_path"])).resolve()
        record_dir = packages_dir / split_name / safe_record_id(record_id)
        contract_dir = record_dir / "contract"
        scaffold_dir = record_dir / "scaffold"
        targets_dir = record_dir / "train_targets"
        package_path = targets_dir / "offline_mvp_nores_vocoder_train_targets.pt"
        package_reused = bool(skip_existing and package_path.exists())
        if not package_reused:
            export_offline_mvp_teacher_downstream_contract(
                input_audio_path=audio_path,
                output_dir=contract_dir,
                route_handoff_path=route_handoff_path,
                checkpoint_path=checkpoint_path,
                calibration_asset_path=calibration_asset_path,
                chunk_samples=chunk_samples,
                chunk_ms=chunk_ms,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=verify_against_full_pass,
            )
            build_offline_mvp_teacher_vocoder_input_scaffold(
                contract_path=contract_dir / "teacher_downstream_control_contract.pt",
                output_dir=scaffold_dir,
            )
            build_offline_mvp_nores_vocoder_training_package(
                scaffold_path=scaffold_dir / "teacher_vocoder_input_scaffold.pt",
                target_audio_path=audio_path,
                output_dir=targets_dir,
                harmonic_bins=32,
                noise_bins=32,
                sample_rate=None,
                frame_length=None,
                hop_length=None,
            )
        package_payload = load_training_package_payload(package_path)
        package_build_sec = perf_counter() - record_started_perf
        package_size_bytes = compute_path_size_bytes(record_dir)
        entries.append(
            {
                "record_id": record_id,
                "audio_path": audio_path.as_posix(),
                "duration_sec": float(dict(record.get("audio", {})).get("duration_sec", 0.0)),
                "split_name": split_name,
                "training_package_path": package_path.as_posix(),
                "training_package_version": str(package_payload.get("training_package_version", "unknown")),
                "source_scaffold_version": str(package_payload.get("source_scaffold_version", "unknown")),
                "frame_count": int(package_payload["frame_count"]),
                "periodic_input_dim": int(package_payload["inputs"]["periodic_branch_features"].shape[-1]),
                "noise_input_dim": int(package_payload["inputs"]["noise_branch_features"].shape[-1]),
                "harmonic_target_dim": int(package_payload["targets"]["harmonic_envelope_target"].shape[-1]),
                "noise_target_dim": int(package_payload["targets"]["noise_envelope_target"].shape[-1]),
                "package_size_bytes": int(package_size_bytes),
                "package_build_sec": round(package_build_sec, 6),
                "package_status": "reused_existing" if package_reused else "built_now",
            }
        )
    return entries


def compute_path_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return int(path.stat().st_size)
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += int(child.stat().st_size)
    return total


def summarize_dataset_package_index(
    train_packages: list[dict[str, object]],
    validation_packages: list[dict[str, object]],
    run_duration_sec: float,
) -> dict[str, object]:
    def summarize_split(entries: list[dict[str, object]]) -> dict[str, object]:
        total_audio_duration_sec = sum(float(entry.get("duration_sec", 0.0)) for entry in entries)
        total_frame_count = sum(int(entry.get("frame_count", 0)) for entry in entries)
        total_package_size_bytes = sum(int(entry.get("package_size_bytes", 0)) for entry in entries)
        total_package_build_sec = sum(float(entry.get("package_build_sec", 0.0)) for entry in entries)
        built_now_count = sum(1 for entry in entries if str(entry.get("package_status")) == "built_now")
        reused_existing_count = sum(1 for entry in entries if str(entry.get("package_status")) == "reused_existing")
        training_package_versions = sorted({str(entry.get("training_package_version", "unknown")) for entry in entries})
        source_scaffold_versions = sorted({str(entry.get("source_scaffold_version", "unknown")) for entry in entries})
        periodic_input_dims = sorted({int(entry.get("periodic_input_dim", 0)) for entry in entries}) if entries else []
        noise_input_dims = sorted({int(entry.get("noise_input_dim", 0)) for entry in entries}) if entries else []
        harmonic_target_dims = sorted({int(entry.get("harmonic_target_dim", 0)) for entry in entries}) if entries else []
        noise_target_dims = sorted({int(entry.get("noise_target_dim", 0)) for entry in entries}) if entries else []
        return {
            "package_count": len(entries),
            "total_audio_duration_sec": round(total_audio_duration_sec, 6),
            "total_frame_count": int(total_frame_count),
            "total_package_size_bytes": int(total_package_size_bytes),
            "total_package_build_sec": round(total_package_build_sec, 6),
            "avg_package_build_sec": round(
                (total_package_build_sec / len(entries)) if entries else 0.0,
                6,
            ),
            "avg_package_size_bytes": round(
                (total_package_size_bytes / len(entries)) if entries else 0.0,
                2,
            ),
            "built_now_count": int(built_now_count),
            "reused_existing_count": int(reused_existing_count),
            "training_package_versions": training_package_versions,
            "source_scaffold_versions": source_scaffold_versions,
            "periodic_input_dims": periodic_input_dims,
            "noise_input_dims": noise_input_dims,
            "harmonic_target_dims": harmonic_target_dims,
            "noise_target_dims": noise_target_dims,
            "versions_consistent": len(training_package_versions) <= 1 and len(source_scaffold_versions) <= 1,
            "dims_consistent": (
                len(periodic_input_dims) <= 1
                and len(noise_input_dims) <= 1
                and len(harmonic_target_dims) <= 1
                and len(noise_target_dims) <= 1
            ),
        }

    train_summary = summarize_split(train_packages)
    validation_summary = summarize_split(validation_packages)
    return {
        "train_package_count": len(train_packages),
        "validation_package_count": len(validation_packages),
        "train": train_summary,
        "validation": validation_summary,
        "total_package_count": len(train_packages) + len(validation_packages),
        "total_package_size_bytes": int(
            train_summary["total_package_size_bytes"] + validation_summary["total_package_size_bytes"]
        ),
        "total_package_build_sec": round(
            float(train_summary["total_package_build_sec"]) + float(validation_summary["total_package_build_sec"]),
            6,
        ),
        "index_build_duration_sec": round(float(run_duration_sec), 6),
    }


def safe_record_id(record_id: str) -> str:
    return (
        str(record_id)
        .replace("::", "__")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )


def align_waveform_to_teacher_frames(
    waveform: torch.Tensor,
    frame_count: int,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    required_samples = int(frame_length + max(0, frame_count - 1) * hop_length)
    if waveform.shape[0] < required_samples:
        waveform = F.pad(waveform, (0, required_samples - int(waveform.shape[0])))
    return waveform[:required_samples].contiguous()


def build_branch_spectral_targets(
    waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    harmonic_bins: int,
    noise_bins: int,
) -> tuple[torch.Tensor, torch.Tensor, dict[str, float]]:
    window = torch.hann_window(frame_length, dtype=waveform.dtype)
    spectrogram = torch.stft(
        waveform,
        n_fft=frame_length,
        hop_length=hop_length,
        win_length=frame_length,
        window=window,
        center=False,
        return_complex=True,
    )
    log_magnitude = torch.log1p(spectrogram.abs()).transpose(0, 1).contiguous()
    freq_bins = int(log_magnitude.shape[-1])
    split_bin = max(2, min(freq_bins - 1, freq_bins // 2))
    harmonic_source = log_magnitude[:, :split_bin]
    noise_source = log_magnitude[:, split_bin:]
    if noise_source.shape[-1] == 0:
        noise_source = log_magnitude[:, -1:]

    harmonic_target = F.adaptive_avg_pool1d(harmonic_source.unsqueeze(1), harmonic_bins).squeeze(1)
    noise_target = F.adaptive_avg_pool1d(noise_source.unsqueeze(1), noise_bins).squeeze(1)
    stats = {
        "stft_freq_bins": freq_bins,
        "harmonic_source_bins": int(harmonic_source.shape[-1]),
        "noise_source_bins": int(noise_source.shape[-1]),
        "harmonic_target_mean": round(float(harmonic_target.mean().item()), 6),
        "noise_target_mean": round(float(noise_target.mean().item()), 6),
    }
    return harmonic_target, noise_target, stats


def reconstruct_waveform_from_frames(
    waveform_frames: torch.Tensor,
    frame_length: int,
    hop_length: int,
    frame_gains: torch.Tensor | None = None,
    frame_gain_floor: float = 0.0,
    frame_gain_smoothing_frames: int = 0,
    frame_gain_apply_mode: str = DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
) -> torch.Tensor:
    if waveform_frames.ndim != 2:
        raise ValueError(f"Expected waveform_frames shape [frames, samples], got {tuple(waveform_frames.shape)}")
    if int(waveform_frames.shape[-1]) != int(frame_length):
        raise ValueError(
            "waveform_frames sample dimension does not match frame_length: "
            f"frames={tuple(waveform_frames.shape)} frame_length={frame_length}"
        )
    frame_count = int(waveform_frames.shape[0])
    total_length = int(frame_length + max(0, frame_count - 1) * hop_length)
    output = waveform_frames.new_zeros((total_length,))
    weights = waveform_frames.new_zeros((total_length,))
    normalized_apply_mode = str(frame_gain_apply_mode).strip().lower()
    if normalized_apply_mode not in {"pre_overlap_add", "post_ola_envelope"}:
        raise ValueError(f"Unsupported frame_gain_apply_mode: {frame_gain_apply_mode}")
    window = torch.hann_window(
        int(frame_length),
        periodic=False,
        dtype=waveform_frames.dtype,
        device=waveform_frames.device,
    )
    resolved_frame_gains = None
    if frame_gains is not None:
        resolved_frame_gains = frame_gains.to(dtype=waveform_frames.dtype, device=waveform_frames.device)
        if resolved_frame_gains.ndim == 2 and int(resolved_frame_gains.shape[-1]) == 1:
            resolved_frame_gains = resolved_frame_gains.squeeze(-1)
        if resolved_frame_gains.ndim != 1 or int(resolved_frame_gains.shape[0]) != frame_count:
            raise ValueError(
                "frame_gains must match waveform frame count: "
                f"frame_gains={tuple(resolved_frame_gains.shape)} frame_count={frame_count}"
            )
        resolved_frame_gains = prepare_reconstruction_frame_gains(
            frame_gains=resolved_frame_gains,
            frame_gain_floor=float(frame_gain_floor),
            frame_gain_smoothing_frames=int(frame_gain_smoothing_frames),
        )
    gain_output = None
    gain_weights = None
    if resolved_frame_gains is not None and normalized_apply_mode == "post_ola_envelope":
        gain_output = waveform_frames.new_zeros((total_length,))
        gain_weights = waveform_frames.new_zeros((total_length,))
    for frame_index in range(frame_count):
        start = int(frame_index * hop_length)
        end = start + int(frame_length)
        frame = waveform_frames[frame_index]
        if resolved_frame_gains is not None and normalized_apply_mode == "pre_overlap_add":
            frame = frame * resolved_frame_gains[frame_index].clamp(0.0, 1.0)
        output[start:end] += frame * window
        weights[start:end] += window
        if gain_output is not None and gain_weights is not None:
            gain = resolved_frame_gains[frame_index].clamp(0.0, 1.0)
            gain_output[start:end] += gain * window
            gain_weights[start:end] += window
    reconstructed = output / weights.clamp_min(1.0e-6)
    if gain_output is not None and gain_weights is not None:
        gain_envelope = gain_output / gain_weights.clamp_min(1.0e-6)
        reconstructed = reconstructed * gain_envelope.clamp(0.0, 1.0)
    return reconstructed


def prepare_reconstruction_frame_gains(
    frame_gains: torch.Tensor,
    frame_gain_floor: float,
    frame_gain_smoothing_frames: int,
) -> torch.Tensor:
    resolved = frame_gains.to(torch.float32)
    if resolved.ndim != 1:
        raise ValueError(f"frame_gains must be 1D, got {tuple(resolved.shape)}")
    if int(frame_gain_smoothing_frames) > 0 and int(resolved.shape[0]) > 1:
        radius = int(frame_gain_smoothing_frames)
        padded = F.pad(
            resolved.view(1, 1, -1),
            (radius, radius),
            mode="replicate",
        )
        kernel = resolved.new_ones((1, 1, radius * 2 + 1))
        kernel = kernel / float(kernel.numel())
        resolved = F.conv1d(padded, kernel).view(-1)
    floor = max(0.0, min(1.0, float(frame_gain_floor)))
    if floor > 0.0:
        resolved = resolved.clamp(0.0, 1.0)
        resolved = floor + resolved * (1.0 - floor)
    return resolved.to(dtype=frame_gains.dtype, device=frame_gains.device).clamp(0.0, 1.0)


def compute_frame_activity_target(
    aligned_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    silence_floor: float = 0.002,
    active_floor: float = 0.012,
) -> torch.Tensor:
    total_length = int(aligned_waveform.shape[0])
    frame_count = max(1, math.ceil(max(1, total_length - int(frame_length)) / int(hop_length)) + 1)
    activities: list[torch.Tensor] = []
    for frame_index in range(frame_count):
        start = int(frame_index * hop_length)
        end = start + int(frame_length)
        frame = aligned_waveform[start:end]
        if int(frame.shape[0]) < int(frame_length):
            frame = F.pad(frame, (0, int(frame_length) - int(frame.shape[0])))
        frame_rms = frame.pow(2).mean().sqrt()
        frame_abs = frame.abs().mean()
        frame_level = torch.maximum(frame_rms, frame_abs)
        frame_activity = ((frame_level - float(silence_floor)) / float(active_floor - silence_floor)).clamp(0.0, 1.0)
        activities.append(frame_activity)
    return torch.stack(activities, dim=0).unsqueeze(-1)


def compute_stft_reconstruction_loss(
    predicted_waveform: torch.Tensor,
    target_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    window = torch.hann_window(
        int(frame_length),
        dtype=predicted_waveform.dtype,
        device=predicted_waveform.device,
    )
    predicted_spec = torch.stft(
        predicted_waveform,
        n_fft=int(frame_length),
        hop_length=int(hop_length),
        win_length=int(frame_length),
        window=window,
        center=False,
        return_complex=True,
    )
    target_spec = torch.stft(
        target_waveform,
        n_fft=int(frame_length),
        hop_length=int(hop_length),
        win_length=int(frame_length),
        window=window,
        center=False,
        return_complex=True,
    )
    return F.l1_loss(torch.log1p(predicted_spec.abs()), torch.log1p(target_spec.abs()))


def frame_waveform_sequence(
    waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    waveform_tensor = waveform.to(torch.float32).view(-1)
    resolved_frame_length = max(1, int(frame_length))
    resolved_hop_length = max(1, int(hop_length))
    if int(waveform_tensor.numel()) <= 0:
        return waveform_tensor.new_zeros((0, resolved_frame_length))
    if int(waveform_tensor.numel()) < resolved_frame_length:
        pad_amount = resolved_frame_length - int(waveform_tensor.numel())
        waveform_tensor = F.pad(waveform_tensor, (0, pad_amount))
    frame_starts = list(
        range(0, max(1, int(waveform_tensor.numel()) - resolved_frame_length + 1), resolved_hop_length)
    )
    tail_start = max(0, int(waveform_tensor.numel()) - resolved_frame_length)
    if not frame_starts or frame_starts[-1] != tail_start:
        frame_starts.append(tail_start)
    frames = [waveform_tensor[start : start + resolved_frame_length] for start in frame_starts]
    return torch.stack(frames, dim=0)


def compute_centered_frame_rms(frames: torch.Tensor) -> torch.Tensor:
    frames_tensor = frames.to(torch.float32)
    centered = frames_tensor - frames_tensor.mean(dim=1, keepdim=True)
    return centered.pow(2).mean(dim=1).sqrt()


def normalize_frames_unit_rms(frames: torch.Tensor) -> torch.Tensor:
    frames_tensor = frames.to(torch.float32)
    centered = frames_tensor - frames_tensor.mean(dim=1, keepdim=True)
    frame_rms = centered.pow(2).mean(dim=1, keepdim=True).sqrt().clamp_min(1.0e-6)
    return centered / frame_rms


def compute_adjacent_deltas(sequence: torch.Tensor) -> torch.Tensor:
    sequence_tensor = sequence.to(torch.float32)
    if int(sequence_tensor.shape[0]) <= 1:
        return sequence_tensor.new_zeros((1, *sequence_tensor.shape[1:]))
    return sequence_tensor[1:] - sequence_tensor[:-1]


def compute_frame_cosine_to_reference(*, frames: torch.Tensor, reference_index: int) -> torch.Tensor:
    frames_tensor = frames.to(torch.float32)
    if int(frames_tensor.shape[0]) == 0:
        return frames_tensor.new_zeros((0,))
    resolved_reference_index = min(max(int(reference_index), 0), int(frames_tensor.shape[0]) - 1)
    reference = frames_tensor[resolved_reference_index : resolved_reference_index + 1]
    normalized_reference = reference / reference.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    normalized_frames = frames_tensor / frames_tensor.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    return (normalized_frames * normalized_reference).sum(dim=1)


def compute_active_template_and_frame_delta_losses(
    *,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    active_frame_rms_threshold: float = DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
) -> tuple[torch.Tensor, torch.Tensor]:
    decoded_analysis_frames = frame_waveform_sequence(
        waveform=decoded_waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    aligned_analysis_frames = frame_waveform_sequence(
        waveform=aligned_waveform[: decoded_waveform.shape[0]],
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    decoded_normalized_frames = normalize_frames_unit_rms(decoded_analysis_frames)
    aligned_normalized_frames = normalize_frames_unit_rms(aligned_analysis_frames)
    aligned_frame_rms = compute_centered_frame_rms(aligned_analysis_frames)
    decoded_frame_deltas = compute_adjacent_deltas(decoded_normalized_frames)
    aligned_frame_deltas = compute_adjacent_deltas(aligned_normalized_frames)
    frame_delta_loss = F.l1_loss(decoded_frame_deltas, aligned_frame_deltas)

    active_mask = aligned_frame_rms >= float(active_frame_rms_threshold)
    if bool(active_mask.any()):
        decoded_template_cosine = compute_frame_cosine_to_reference(
            frames=decoded_normalized_frames,
            reference_index=0,
        )
        aligned_template_cosine = compute_frame_cosine_to_reference(
            frames=aligned_normalized_frames,
            reference_index=0,
        )
        active_template_excess = (
            decoded_template_cosine[active_mask] - aligned_template_cosine[active_mask]
        ).clamp_min(0.0)
        active_template_loss = active_template_excess.mean()
    else:
        active_template_loss = decoded_waveform.new_zeros(())
    return active_template_loss, frame_delta_loss


def compute_rms_guard_loss(
    predicted_waveform: torch.Tensor,
    target_waveform: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    predicted_rms = predicted_waveform.pow(2).mean().sqrt().clamp_min(1.0e-6)
    target_rms = target_waveform.pow(2).mean().sqrt().clamp_min(1.0e-6)
    # Log-RMS keeps the guard scale-aware so low-amplitude collapse is penalized more clearly.
    rms_guard_loss = torch.abs(torch.log(predicted_rms) - torch.log(target_rms))
    return rms_guard_loss, predicted_rms, target_rms


def compute_nores_vocoder_losses(
    outputs: dict[str, torch.Tensor],
    harmonic_target: torch.Tensor,
    noise_target: torch.Tensor,
    periodic_gate_target: torch.Tensor,
    noise_gate_target: torch.Tensor,
    aligned_waveform: torch.Tensor | None,
    frame_length: int | None,
    hop_length: int | None,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
) -> tuple[torch.Tensor, dict[str, float]]:
    resolved_reconstruction_frame_gain_apply_mode = normalize_training_reconstruction_frame_gain_apply_mode(
        reconstruction_frame_gain_apply_mode
    )
    frame_activity_target = harmonic_target.new_ones(periodic_gate_target.shape)
    if aligned_waveform is not None and frame_length is not None and hop_length is not None:
        frame_activity_target = compute_frame_activity_target(
            aligned_waveform=aligned_waveform.to(periodic_gate_target.device),
            frame_length=int(frame_length),
            hop_length=int(hop_length),
        ).to(dtype=periodic_gate_target.dtype, device=periodic_gate_target.device)
    periodic_gate_supervision = periodic_gate_target * frame_activity_target
    noise_gate_supervision = noise_gate_target * frame_activity_target
    harmonic_loss = F.l1_loss(outputs["harmonic_envelope"], harmonic_target)
    noise_loss = F.l1_loss(outputs["noise_envelope"], noise_target)
    periodic_gate_loss = F.binary_cross_entropy(
        outputs["periodic_gate"].clamp(1e-6, 1.0 - 1e-6),
        periodic_gate_supervision,
    )
    noise_gate_loss = F.binary_cross_entropy(
        outputs["noise_gate"].clamp(1e-6, 1.0 - 1e-6),
        noise_gate_supervision,
    )
    predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"])
    activity_gate_loss = F.binary_cross_entropy(
        predicted_activity.clamp(1e-6, 1.0 - 1e-6),
        frame_activity_target,
    )
    waveform_loss = harmonic_loss.new_zeros(())
    stft_loss = harmonic_loss.new_zeros(())
    rms_guard_loss = harmonic_loss.new_zeros(())
    active_template_loss = harmonic_loss.new_zeros(())
    frame_delta_loss = harmonic_loss.new_zeros(())
    decoded_waveform_rms = 0.0
    target_waveform_rms = 0.0
    if (
        float(waveform_weight) > 0.0
        or float(stft_weight) > 0.0
        or float(rms_guard_weight) > 0.0
        or float(active_template_weight) > 0.0
        or float(frame_delta_weight) > 0.0
    ):
        if aligned_waveform is None:
            raise ValueError("aligned_waveform is required when waveform/structure losses are enabled.")
        if frame_length is None or hop_length is None:
            raise ValueError("frame_length and hop_length are required when waveform/structure losses are enabled.")
        waveform_frames = outputs.get("waveform_frames")
        if waveform_frames is None:
            raise ValueError("Model did not emit waveform_frames while waveform/structure losses are enabled.")
        decoded_waveform = reconstruct_waveform_from_frames(
            waveform_frames=waveform_frames,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
            frame_gain_apply_mode=resolved_reconstruction_frame_gain_apply_mode,
        )
        target_waveform = aligned_waveform[: decoded_waveform.shape[0]]
        waveform_loss = F.l1_loss(decoded_waveform, target_waveform)
        stft_loss = compute_stft_reconstruction_loss(
            predicted_waveform=decoded_waveform,
            target_waveform=target_waveform,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
        )
        rms_guard_loss, decoded_rms_tensor, target_rms_tensor = compute_rms_guard_loss(
            predicted_waveform=decoded_waveform,
            target_waveform=target_waveform,
        )
        active_template_loss, frame_delta_loss = compute_active_template_and_frame_delta_losses(
            decoded_waveform=decoded_waveform,
            aligned_waveform=target_waveform,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
        )
        decoded_waveform_rms = float(decoded_rms_tensor.detach().cpu().item())
        target_waveform_rms = float(target_rms_tensor.detach().cpu().item())
    total_loss = (
        harmonic_loss * float(harmonic_weight)
        + noise_loss * float(noise_weight)
        + periodic_gate_loss * float(periodic_gate_weight)
        + noise_gate_loss * float(noise_gate_weight)
        + activity_gate_loss * float(activity_gate_weight)
        + waveform_loss * float(waveform_weight)
        + stft_loss * float(stft_weight)
        + rms_guard_loss * float(rms_guard_weight)
        + active_template_loss * float(active_template_weight)
        + frame_delta_loss * float(frame_delta_weight)
    )
    metrics = {
        "loss_total": round(float(total_loss.detach().cpu().item()), 6),
        "loss_harmonic_envelope": round(float(harmonic_loss.detach().cpu().item()), 6),
        "loss_noise_envelope": round(float(noise_loss.detach().cpu().item()), 6),
        "loss_periodic_gate": round(float(periodic_gate_loss.detach().cpu().item()), 6),
        "loss_noise_gate": round(float(noise_gate_loss.detach().cpu().item()), 6),
        "loss_activity_gate": round(float(activity_gate_loss.detach().cpu().item()), 6),
        "loss_waveform": round(float(waveform_loss.detach().cpu().item()), 6),
        "loss_stft": round(float(stft_loss.detach().cpu().item()), 6),
        "loss_rms_guard": round(float(rms_guard_loss.detach().cpu().item()), 6),
        "loss_active_frame_template_excess_relu_0p02": round(float(active_template_loss.detach().cpu().item()), 6),
        "loss_frame_delta_unit_rms_l1": round(float(frame_delta_loss.detach().cpu().item()), 6),
        "periodic_gate_pred_mean": round(float(outputs["periodic_gate"].detach().mean().cpu().item()), 6),
        "noise_gate_pred_mean": round(float(outputs["noise_gate"].detach().mean().cpu().item()), 6),
        "activity_gate_pred_mean": round(float(predicted_activity.detach().mean().cpu().item()), 6),
        "periodic_gate_target_mean": round(float(periodic_gate_supervision.detach().mean().cpu().item()), 6),
        "noise_gate_target_mean": round(float(noise_gate_supervision.detach().mean().cpu().item()), 6),
        "activity_gate_target_mean": round(float(frame_activity_target.detach().mean().cpu().item()), 6),
        "reconstruction_frame_gain_apply_mode": resolved_reconstruction_frame_gain_apply_mode,
        "decoded_waveform_rms": round(decoded_waveform_rms, 6),
        "target_waveform_rms": round(target_waveform_rms, 6),
        "decoded_to_target_rms_ratio": round(
            0.0 if target_waveform_rms <= 1.0e-8 else decoded_waveform_rms / target_waveform_rms,
            6,
        ),
    }
    return total_loss, metrics


def run_nores_vocoder_validation_pass(
    model: NoResidualSourceFilterVocoderScaffold,
    validation_batch: dict[str, torch.Tensor],
    step: int,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
    frame_length: int,
    hop_length: int,
    validation_source: str,
) -> dict[str, object]:
    model.eval()
    with torch.no_grad():
        outputs = model(
            periodic_branch_features=validation_batch["periodic_branch_features"],
            noise_branch_features=validation_batch["noise_branch_features"],
        )
        _loss, loss_metrics = compute_nores_vocoder_losses(
            outputs=outputs,
            harmonic_target=validation_batch["harmonic_target"],
            noise_target=validation_batch["noise_target"],
            periodic_gate_target=validation_batch["periodic_gate_target"],
            noise_gate_target=validation_batch["noise_gate_target"],
            aligned_waveform=validation_batch["aligned_waveform"],
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            harmonic_weight=harmonic_weight,
            noise_weight=noise_weight,
            periodic_gate_weight=periodic_gate_weight,
            noise_gate_weight=noise_gate_weight,
            activity_gate_weight=activity_gate_weight,
            waveform_weight=waveform_weight,
            stft_weight=stft_weight,
            rms_guard_weight=rms_guard_weight,
            active_template_weight=active_template_weight,
            frame_delta_weight=frame_delta_weight,
            use_predicted_activity_gate=use_predicted_activity_gate,
            reconstruction_frame_gain_apply_mode=reconstruction_frame_gain_apply_mode,
        )
    return {
        "step": int(step),
        "validation_source": str(validation_source),
        "frame_count": int(validation_batch["harmonic_target"].shape[0]),
        "loss_metrics": loss_metrics,
    }


def select_package_entries_for_step(
    packages: list[dict[str, object]],
    packages_per_step: int,
    sampler_mode: str,
    rng: random.Random,
    current_order: list[int],
    current_cursor: int,
) -> tuple[list[dict[str, object]], int, list[int]]:
    if not packages:
        return [], current_cursor, current_order
    selected: list[dict[str, object]] = []
    order = list(current_order)
    cursor = int(current_cursor)
    while len(selected) < packages_per_step:
        if cursor >= len(order):
            order = list(range(len(packages)))
            if sampler_mode == "shuffle":
                rng.shuffle(order)
            cursor = 0
        selected.append(packages[order[cursor]])
        cursor += 1
    return selected, cursor, order


def run_nores_vocoder_dataset_validation_pass(
    model: NoResidualSourceFilterVocoderScaffold,
    package_entries: list[dict[str, object]],
    device: torch.device,
    step: int,
    harmonic_weight: float,
    noise_weight: float,
    periodic_gate_weight: float,
    noise_gate_weight: float,
    activity_gate_weight: float,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    active_template_weight: float,
    frame_delta_weight: float,
    use_predicted_activity_gate: bool,
    reconstruction_frame_gain_apply_mode: str,
    validation_source: str,
) -> dict[str, object]:
    package_metrics: list[dict[str, object]] = []
    model.eval()
    with torch.no_grad():
        for entry in package_entries:
            payload = load_training_package_payload(Path(entry["training_package_path"]))
            runtime = extract_training_runtime(payload)
            batch = move_batch_to_device(
                extract_training_batch(payload),
                device,
            )
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
            )
            _loss, loss_metrics = compute_nores_vocoder_losses(
                outputs=outputs,
                harmonic_target=batch["harmonic_target"],
                noise_target=batch["noise_target"],
                periodic_gate_target=batch["periodic_gate_target"],
                noise_gate_target=batch["noise_gate_target"],
                aligned_waveform=batch["aligned_waveform"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                harmonic_weight=harmonic_weight,
                noise_weight=noise_weight,
                periodic_gate_weight=periodic_gate_weight,
                noise_gate_weight=noise_gate_weight,
                activity_gate_weight=activity_gate_weight,
                waveform_weight=waveform_weight,
                stft_weight=stft_weight,
                rms_guard_weight=rms_guard_weight,
                active_template_weight=active_template_weight,
                frame_delta_weight=frame_delta_weight,
                use_predicted_activity_gate=use_predicted_activity_gate,
                reconstruction_frame_gain_apply_mode=reconstruction_frame_gain_apply_mode,
            )
            package_metrics.append(
                {
                    "record_id": entry["record_id"],
                    "training_package_path": entry["training_package_path"],
                    "frame_count": int(payload["frame_count"]),
                    "loss_metrics": loss_metrics,
                }
            )
    return {
        "step": int(step),
        "validation_source": str(validation_source),
        "package_count": len(package_entries),
        "record_ids": [str(entry["record_id"]) for entry in package_entries],
        "loss_metrics": average_loss_metrics([item["loss_metrics"] for item in package_metrics]),
        "package_metrics": package_metrics,
    }


def average_loss_metrics(metrics_list: list[dict[str, object]]) -> dict[str, object]:
    if not metrics_list:
        return {}
    keys = list(metrics_list[0].keys())
    averaged: dict[str, object] = {}
    for key in keys:
        values = [metrics[key] for metrics in metrics_list]
        first_value = values[0]
        try:
            averaged[key] = round(
                sum(float(value) for value in values) / len(values),
                6,
            )
        except (TypeError, ValueError):
            if any(value != first_value for value in values[1:]):
                raise ValueError(
                    f"Cannot average non-numeric loss metric {key!r} with inconsistent values: {values!r}"
                )
            averaged[key] = first_value
    return averaged


def select_best_nores_vocoder_checkpoint(
    checkpoint_paths: list[str],
    validation_history: list[dict[str, object]],
) -> dict[str, object] | None:
    if not checkpoint_paths or not validation_history:
        return None
    checkpoint_by_step: dict[int, str] = {}
    for checkpoint_path in checkpoint_paths:
        name = Path(checkpoint_path).stem
        if ".step" not in name:
            continue
        try:
            step = int(name.rsplit(".step", 1)[1])
        except ValueError:
            continue
        checkpoint_by_step[step] = checkpoint_path
    best_payload: dict[str, object] | None = None
    for validation_payload in validation_history:
        step = int(validation_payload["step"])
        checkpoint_path = checkpoint_by_step.get(step)
        if checkpoint_path is None:
            continue
        loss_total = float(validation_payload.get("loss_metrics", {}).get("loss_total", float("inf")))
        candidate = {
            "selection_rule": "min_validation_loss_total_over_recorded_checkpoints",
            "step": step,
            "loss_total": round(loss_total, 6),
            "checkpoint_path": checkpoint_path,
        }
        if best_payload is None or float(candidate["loss_total"]) < float(best_payload["loss_total"]):
            best_payload = candidate
    return best_payload


def build_training_package_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Train Targets",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- training_package_version: {summary['training_package_version']}",
        f"- source_scaffold_path: {summary['source_scaffold_path']}",
        f"- target_audio_path: {summary['target_audio_path']}",
        f"- source_audio_path: {summary['source_audio_path']}",
        f"- runtime: {json.dumps(summary['runtime'], ensure_ascii=False)}",
        f"- frame_count: {summary['frame_count']}",
        f"- aligned_waveform_samples: {summary['aligned_waveform_samples']}",
        f"- periodic_input_dim: {summary['periodic_input_dim']}",
        f"- noise_input_dim: {summary['noise_input_dim']}",
        f"- harmonic_target_dim: {summary['harmonic_target_dim']}",
        f"- noise_target_dim: {summary['noise_target_dim']}",
        f"- spectrogram_stats: {json.dumps(summary['spectrogram_stats'], ensure_ascii=False)}",
        "",
        "## Notes",
    ]
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_training_step_markdown(summary: dict[str, object], checkpoint_path: Path) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Train Step",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- training_package_path: {summary['training_package_path']}",
        f"- model: {json.dumps(summary['model'], ensure_ascii=False)}",
        f"- optimizer: {json.dumps(summary['optimizer'], ensure_ascii=False)}",
        f"- loss_weights: {json.dumps(summary['loss_weights'], ensure_ascii=False)}",
        f"- train_step: {json.dumps(summary['train_step'], ensure_ascii=False)}",
        f"- checkpoint_path: {checkpoint_path.as_posix()}",
        "",
        "## Notes",
    ]
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_training_loop_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Training Loop",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- training_package_path: {summary['training_package_path']}",
        f"- validation_package_path: {summary['validation_package_path']}",
        f"- timing: {json.dumps(summary['timing'], ensure_ascii=False)}",
        f"- model: {json.dumps(summary['model'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        f"- train_frame_count: {summary['train_frame_count']}",
        f"- validation_frame_count: {summary['validation_frame_count']}",
        "",
        "## Step History",
    ]
    for step_payload in list(summary.get("step_history", [])):
        lines.append(
            f"- step={step_payload['step']} loss_total={step_payload['loss_metrics']['loss_total']} "
            f"grad_norm={step_payload['grad_norm']} duration_sec={step_payload['duration_sec']}"
        )
    lines.extend(["", "## Validation History"])
    for validation_payload in list(summary.get("validation_history", [])):
        lines.append(
            f"- step={validation_payload['step']} validation_source={validation_payload['validation_source']} "
            f"loss_total={validation_payload['loss_metrics']['loss_total']}"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            f"- checkpoint_paths: {json.dumps(summary['artifacts']['checkpoint_paths'], ensure_ascii=False)}",
            f"- latest_checkpoint_path: {summary['artifacts']['latest_checkpoint_path']}",
            f"- best_checkpoint: {json.dumps(summary['artifacts']['best_checkpoint'], ensure_ascii=False)}",
            "",
            "## Notes",
        ]
    )
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    lines.extend(["", "## Next Steps"])
    for item in list(summary.get("next_steps", [])):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def build_dataset_index_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Dataset Index",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- timing: {json.dumps(summary.get('timing', {}), ensure_ascii=False)}",
        f"- selection_mode: {summary['selection_mode']}",
        f"- train_split_path: {summary['train_split_path']}",
        f"- validation_split_path: {summary['validation_split_path']}",
        f"- summary: {json.dumps(summary['summary'], ensure_ascii=False)}",
        "",
        "## Train Packages",
    ]
    for entry in list(summary.get("train_packages", [])):
        lines.append(
            f"- record_id={entry['record_id']} frame_count={entry['frame_count']} "
            f"duration_sec={round(float(entry['duration_sec']), 6)} "
            f"training_package_version={entry.get('training_package_version', 'unknown')} "
            f"source_scaffold_version={entry.get('source_scaffold_version', 'unknown')} "
            f"periodic_input_dim={entry.get('periodic_input_dim', 'unknown')} "
            f"noise_input_dim={entry.get('noise_input_dim', 'unknown')} "
            f"package_size_bytes={entry.get('package_size_bytes', 0)} "
            f"package_build_sec={entry.get('package_build_sec', 0)} "
            f"package_status={entry.get('package_status', 'unknown')} "
            f"training_package_path={entry['training_package_path']}"
        )
    lines.extend(["", "## Validation Packages"])
    for entry in list(summary.get("validation_packages", [])):
        lines.append(
            f"- record_id={entry['record_id']} frame_count={entry['frame_count']} "
            f"duration_sec={round(float(entry['duration_sec']), 6)} "
            f"training_package_version={entry.get('training_package_version', 'unknown')} "
            f"source_scaffold_version={entry.get('source_scaffold_version', 'unknown')} "
            f"periodic_input_dim={entry.get('periodic_input_dim', 'unknown')} "
            f"noise_input_dim={entry.get('noise_input_dim', 'unknown')} "
            f"package_size_bytes={entry.get('package_size_bytes', 0)} "
            f"package_build_sec={entry.get('package_build_sec', 0)} "
            f"package_status={entry.get('package_status', 'unknown')} "
            f"training_package_path={entry['training_package_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_dataset_training_loop_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP No-Residual Vocoder Dataset Training Loop",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- timing: {json.dumps(summary['timing'], ensure_ascii=False)}",
        f"- dataset: {json.dumps(summary['dataset'], ensure_ascii=False)}",
        f"- model: {json.dumps(summary['model'], ensure_ascii=False)}",
        f"- training: {json.dumps(summary['training'], ensure_ascii=False)}",
        "",
        "## Step History",
    ]
    for step_payload in list(summary.get("step_history", [])):
        lines.append(
            f"- step={step_payload['step']} loss_total={step_payload['loss_metrics']['loss_total']} "
            f"packages_per_step={step_payload['packages_per_step']} "
            f"record_ids={step_payload['record_ids']}"
        )
    lines.extend(["", "## Validation History"])
    for validation_payload in list(summary.get("validation_history", [])):
        lines.append(
            f"- step={validation_payload['step']} validation_source={validation_payload['validation_source']} "
            f"package_count={validation_payload['package_count']} "
            f"loss_total={validation_payload['loss_metrics']['loss_total']}"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            f"- checkpoint_paths: {json.dumps(summary['artifacts']['checkpoint_paths'], ensure_ascii=False)}",
            f"- latest_checkpoint_path: {summary['artifacts']['latest_checkpoint_path']}",
            f"- best_checkpoint: {json.dumps(summary['artifacts']['best_checkpoint'], ensure_ascii=False)}",
            "",
            "## Notes",
        ]
    )
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    lines.extend(["", "## Next Steps"])
    for item in list(summary.get("next_steps", [])):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
