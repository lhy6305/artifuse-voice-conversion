from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_scaffold import resolve_residual_shape_branch_condition_delta
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.source_acoustic_state_extraction import DEFAULT_VUV_VOICED_FRAME_THRESHOLD
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.stage5_speech_emergence_probe import (
    compute_pearson_correlation,
    compute_zero_crossing_rate,
    frame_waveform_sequence,
    summarize_frame_sequence_metrics,
    summarize_probe_delta_vs_baseline,
    summarize_scalar_values,
)
from v5vc.target_format_recovery import write_waveform_int16


STRUCTURE_PROBE_VARIANTS = [
    {
        "label": "baseline",
        "description": "Original checkpoint path without any hidden-state intervention.",
        "transforms": [],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "waveform_decoder_base_logits_only",
        "description": "Suppress residual-shape injection and listen to raw waveform_decoder(decoder_hidden) output alone.",
        "transforms": [],
        "waveform_output_mode": "base_logits_only",
    },
    {
        "label": "waveform_residual_shape_only",
        "description": "Zero base logits and listen to residual-shape delta alone to test whether the injection branch carries speech-like structure by itself.",
        "transforms": [],
        "waveform_output_mode": "residual_shape_only",
    },
    {
        "label": "periodic_hidden_frame_mean",
        "description": "Collapse periodic encoder dynamics to its package-wise frame mean before fusion.",
        "transforms": [("periodic_hidden", "frame_mean")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "noise_hidden_frame_mean",
        "description": "Collapse noise encoder dynamics to its package-wise frame mean before fusion.",
        "transforms": [("noise_hidden", "frame_mean")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "fused_hidden_frame_mean",
        "description": "Collapse fusion output dynamics to its package-wise frame mean before the waveform decoder.",
        "transforms": [("fused_hidden", "frame_mean")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "fused_hidden_zero",
        "description": "Zero the waveform decoder input while leaving branch-side activity gates unchanged.",
        "transforms": [("fused_hidden", "zero")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "fused_hidden_from_periodic_hidden",
        "description": "Bypass fusion and feed periodic_hidden directly into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_periodic_hidden")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "fused_hidden_from_noise_hidden",
        "description": "Bypass fusion and feed noise_hidden directly into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_noise_hidden")],
        "waveform_output_mode": "full_output",
    },
    {
        "label": "fused_hidden_from_branch_mean",
        "description": "Bypass fusion and feed the equal-weight branch mean into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_branch_mean")],
        "waveform_output_mode": "full_output",
    },
]


def sanitize_record_id(record_id: str) -> str:
    return str(record_id).replace("::", "__").replace("/", "_").replace("\\", "_")


def flatten_control_tensor(control: torch.Tensor | None, frame_count: int) -> torch.Tensor | None:
    if control is None:
        return None
    control_cpu = control.detach().cpu().to(torch.float32)
    if control_cpu.ndim == 2 and int(control_cpu.shape[-1]) == 1:
        control_cpu = control_cpu.squeeze(-1)
    control_cpu = control_cpu.view(-1)
    if int(control_cpu.shape[0]) < int(frame_count):
        return None
    return control_cpu[:frame_count]


def resolve_energy_mask_control(
    *,
    energy_log_rms_norm_target: torch.Tensor | None,
    energy_control_target: torch.Tensor | None,
    frame_count: int,
) -> torch.Tensor | None:
    energy_control = flatten_control_tensor(energy_log_rms_norm_target, frame_count)
    if energy_control is not None:
        return energy_control.clamp(0.0, 1.0)
    energy_log = flatten_control_tensor(energy_control_target, frame_count)
    if energy_log is None:
        return None
    return torch.sigmoid((energy_log + 4.0) * 2.0).clamp(0.0, 1.0)


def resolve_voicing_mask_control(
    *,
    vuv_target: torch.Tensor | None,
    voiced_proxy_target: torch.Tensor | None,
    aper_target: torch.Tensor | None,
    aperiodicity_proxy_target: torch.Tensor | None,
    frame_count: int,
) -> tuple[torch.Tensor | None, str]:
    for control, label in (
        (vuv_target, "vuv_target"),
        (voiced_proxy_target, "voiced_proxy_target"),
    ):
        flattened = flatten_control_tensor(control, frame_count)
        if flattened is not None:
            return flattened.clamp(0.0, 1.0), label
    for control, label in (
        (aper_target, "aper_target_inverted"),
        (aperiodicity_proxy_target, "aperiodicity_proxy_target_inverted"),
    ):
        flattened = flatten_control_tensor(control, frame_count)
        if flattened is not None:
            return (1.0 - flattened).clamp(0.0, 1.0), label
    return None, "missing"


def resolve_aperiodicity_control(
    *,
    aper_target: torch.Tensor | None,
    aperiodicity_proxy_target: torch.Tensor | None,
    frame_count: int,
) -> tuple[torch.Tensor | None, str]:
    for control, label in (
        (aper_target, "aper_target"),
        (aperiodicity_proxy_target, "aperiodicity_proxy_target"),
    ):
        flattened = flatten_control_tensor(control, frame_count)
        if flattened is not None:
            return flattened.clamp(0.0, 1.0), label
    return None, "missing"


def build_voicing_conditioning_bundle(
    *,
    frame_count: int,
    vuv_target: torch.Tensor | None,
    voiced_proxy_target: torch.Tensor | None,
    aper_target: torch.Tensor | None,
    aperiodicity_proxy_target: torch.Tensor | None,
    energy_log_rms_norm_target: torch.Tensor | None,
    energy_control_target: torch.Tensor | None,
    energy_active_threshold: float = 0.1,
    voiced_threshold: float = DEFAULT_VUV_VOICED_FRAME_THRESHOLD,
) -> dict[str, object] | None:
    voicing_control, voicing_source = resolve_voicing_mask_control(
        vuv_target=vuv_target,
        voiced_proxy_target=voiced_proxy_target,
        aper_target=aper_target,
        aperiodicity_proxy_target=aperiodicity_proxy_target,
        frame_count=frame_count,
    )
    if voicing_control is None:
        return None
    aper_control, aper_source = resolve_aperiodicity_control(
        aper_target=aper_target,
        aperiodicity_proxy_target=aperiodicity_proxy_target,
        frame_count=frame_count,
    )
    energy_control = resolve_energy_mask_control(
        energy_log_rms_norm_target=energy_log_rms_norm_target,
        energy_control_target=energy_control_target,
        frame_count=frame_count,
    )
    if energy_control is None:
        active_mask = torch.ones_like(voicing_control, dtype=torch.bool)
        active_frame_fraction = 1.0
        energy_source = "missing"
    else:
        active_mask = energy_control >= float(energy_active_threshold)
        active_frame_fraction = float(active_mask.to(torch.float32).mean().item())
        energy_source = (
            "energy_log_rms_norm_target"
            if energy_log_rms_norm_target is not None
            else "energy_control_target_sigmoid"
        )
    voiced_mask = active_mask & (voicing_control >= float(voiced_threshold))
    unvoiced_mask = active_mask & (~voiced_mask)
    active_frame_count = int(active_mask.to(torch.int64).sum().item())
    return {
        "frame_count": int(frame_count),
        "voicing_control": voicing_control,
        "aper_control": aper_control,
        "energy_control": energy_control,
        "active_mask": active_mask,
        "voiced_mask": voiced_mask,
        "unvoiced_mask": unvoiced_mask,
        "active_frame_count": active_frame_count,
        "active_frame_fraction": round(float(active_frame_fraction), 6),
        "active_voiced_fraction": round(
            0.0
            if active_frame_count <= 0
            else float(voiced_mask.to(torch.float32).sum().item()) / float(active_frame_count),
            6,
        ),
        "active_unvoiced_fraction": round(
            0.0
            if active_frame_count <= 0
            else float(unvoiced_mask.to(torch.float32).sum().item()) / float(active_frame_count),
            6,
        ),
        "voicing_source": voicing_source,
        "aper_source": aper_source,
        "energy_source": energy_source,
    }


def summarize_masked_frame_spectral_statistics(
    *,
    analysis_frames: torch.Tensor,
    mask: torch.Tensor,
    sample_rate: int,
    high_band_hz: float = 4000.0,
) -> dict[str, float]:
    frame_count = int(analysis_frames.shape[0])
    mask_cpu = mask.detach().cpu().to(torch.bool).view(-1)
    if int(mask_cpu.shape[0]) != frame_count:
        raise ValueError(
            "Mask length does not match analysis frame count for spectral conditioning: "
            f"{int(mask_cpu.shape[0])} vs {frame_count}"
        )
    selected_count = int(mask_cpu.to(torch.int64).sum().item())
    if selected_count <= 0:
        return {
            "frame_count": 0.0,
            "spectral_centroid_hz_mean": 0.0,
            "spectral_bandwidth_hz_mean": 0.0,
            "spectral_rolloff95_hz_mean": 0.0,
            "spectral_high_band_energy_ratio_mean": 0.0,
            "frame_rms_mean": 0.0,
        }

    frames = analysis_frames.detach().cpu().to(torch.float32)[mask_cpu]
    frame_length = int(frames.shape[-1])
    window = torch.hann_window(frame_length, dtype=torch.float32)
    windowed = frames * window.unsqueeze(0)
    spectrum = torch.fft.rfft(windowed, dim=-1)
    power = spectrum.abs().pow(2.0)
    freqs = torch.fft.rfftfreq(frame_length, d=1.0 / float(sample_rate)).to(torch.float32)
    power_sum = power.sum(dim=-1).clamp_min(1.0e-8)
    centroid = (power * freqs.unsqueeze(0)).sum(dim=-1) / power_sum
    centered = freqs.unsqueeze(0) - centroid.unsqueeze(-1)
    bandwidth = ((power * centered.pow(2.0)).sum(dim=-1) / power_sum).clamp_min(0.0).sqrt()
    cumulative = power.cumsum(dim=-1)
    rolloff_threshold = 0.95 * power_sum
    rolloff_index = (cumulative >= rolloff_threshold.unsqueeze(-1)).to(torch.float32).argmax(dim=-1)
    rolloff = freqs[rolloff_index]
    high_band_mask = freqs >= float(high_band_hz)
    if bool(high_band_mask.any().item()):
        high_band_ratio = power[:, high_band_mask].sum(dim=-1) / power_sum
    else:
        high_band_ratio = torch.zeros_like(power_sum)
    frame_rms = frames.pow(2.0).mean(dim=-1).sqrt()
    return {
        "frame_count": float(selected_count),
        "spectral_centroid_hz_mean": round(float(centroid.mean().item()), 6),
        "spectral_bandwidth_hz_mean": round(float(bandwidth.mean().item()), 6),
        "spectral_rolloff95_hz_mean": round(float(rolloff.mean().item()), 6),
        "spectral_high_band_energy_ratio_mean": round(float(high_band_ratio.mean().item()), 6),
        "frame_rms_mean": round(float(frame_rms.mean().item()), 6),
    }


def summarize_sequence_control_coupling_metrics(
    *,
    sequence: torch.Tensor,
    conditioning: dict[str, object] | None,
) -> tuple[dict[str, float], dict[str, str]]:
    if conditioning is None:
        return {}, {}
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    if sequence_cpu.ndim != 2:
        raise ValueError(f"Expected sequence shape [frames, dims], got {tuple(sequence_cpu.shape)}")
    frame_count = int(sequence_cpu.shape[0])
    expected_frame_count = int(conditioning["frame_count"])
    if frame_count != expected_frame_count:
        raise ValueError(
            "Conditioning frame count does not match sequence frame count: "
            f"{expected_frame_count} vs {frame_count}"
        )
    frame_rms = sequence_cpu.pow(2.0).mean(dim=1).sqrt()
    active_mask = conditioning["active_mask"]
    voiced_mask = conditioning["voiced_mask"]
    unvoiced_mask = conditioning["unvoiced_mask"]
    voicing_control = conditioning["voicing_control"]
    aper_control = conditioning["aper_control"]
    energy_control = conditioning["energy_control"]
    aper_energy_product_control = None
    if aper_control is not None and energy_control is not None:
        aper_energy_product_control = aper_control * energy_control
    active_frame_count = int(conditioning["active_frame_count"])
    metrics = {
        "active_frame_fraction": float(conditioning["active_frame_fraction"]),
        "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
        "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
        "voiced_frame_rms_mean": round(
            0.0 if not bool(voiced_mask.any().item()) else float(frame_rms[voiced_mask].mean().item()),
            6,
        ),
        "unvoiced_frame_rms_mean": round(
            0.0 if not bool(unvoiced_mask.any().item()) else float(frame_rms[unvoiced_mask].mean().item()),
            6,
        ),
        "frame_rms_std": round(float(frame_rms.std(unbiased=False).item()), 6),
        "frame_rms_mean": round(float(frame_rms.mean().item()), 6),
    }
    metrics["unvoiced_minus_voiced_frame_rms_mean"] = round(
        float(metrics["unvoiced_frame_rms_mean"]) - float(metrics["voiced_frame_rms_mean"]),
        6,
    )
    if active_frame_count > 1:
        metrics["active_frame_rms_to_voicing_corr"] = float(
            compute_pearson_correlation(frame_rms[active_mask], voicing_control[active_mask])
        )
        if energy_control is not None:
            metrics["active_frame_rms_to_energy_corr"] = float(
                compute_pearson_correlation(frame_rms[active_mask], energy_control[active_mask])
            )
        if aper_control is not None:
            metrics["active_frame_rms_to_aper_corr"] = float(
                compute_pearson_correlation(frame_rms[active_mask], aper_control[active_mask])
            )
        if aper_energy_product_control is not None:
            metrics["active_frame_rms_to_aper_energy_product_corr"] = float(
                compute_pearson_correlation(frame_rms[active_mask], aper_energy_product_control[active_mask])
            )
    notes = {
        "voicing_source": str(conditioning.get("voicing_source", "missing")),
        "aper_source": str(conditioning.get("aper_source", "missing")),
        "energy_source": str(conditioning.get("energy_source", "missing")),
    }
    return metrics, notes


def summarize_sequence_geometry_metrics(sequence: torch.Tensor) -> dict[str, float]:
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    if sequence_cpu.ndim != 2:
        raise ValueError(f"Expected sequence shape [frames, dims], got {tuple(sequence_cpu.shape)}")
    frame_count = int(sequence_cpu.shape[0])
    dim = int(sequence_cpu.shape[1])
    if frame_count <= 1 or dim <= 0:
        return {
            "effective_rank": 0.0,
            "effective_rank_fraction": 0.0,
            "top1_variance_ratio": 0.0,
            "top4_variance_ratio": 0.0,
            "mean_centered_frame_norm": 0.0,
        }
    centered = sequence_cpu - sequence_cpu.mean(dim=0, keepdim=True)
    covariance = centered.transpose(0, 1).matmul(centered) / max(1, frame_count - 1)
    covariance = 0.5 * (covariance + covariance.transpose(0, 1))
    eigvals = stable_covariance_eigvalsh(covariance).clamp_min(0.0)
    total = float(eigvals.sum().item())
    if total <= 1.0e-12:
        return {
            "effective_rank": 0.0,
            "effective_rank_fraction": 0.0,
            "top1_variance_ratio": 0.0,
            "top4_variance_ratio": 0.0,
            "mean_centered_frame_norm": round(float(centered.norm(dim=1).mean().item()), 6),
        }
    probs = eigvals / total
    positive = probs[probs > 1.0e-12]
    entropy = float((-(positive * positive.log()).sum()).item())
    effective_rank = float(torch.exp(torch.tensor(entropy, dtype=torch.float32)).item())
    sorted_vals = torch.sort(eigvals, descending=True).values
    top1_ratio = float(sorted_vals[:1].sum().item() / total)
    top4_ratio = float(sorted_vals[: min(4, int(sorted_vals.shape[0]))].sum().item() / total)
    return {
        "effective_rank": round(effective_rank, 6),
        "effective_rank_fraction": round(effective_rank / float(min(frame_count, dim)), 6),
        "top1_variance_ratio": round(top1_ratio, 6),
        "top4_variance_ratio": round(top4_ratio, 6),
        "mean_centered_frame_norm": round(float(centered.norm(dim=1).mean().item()), 6),
    }


def stable_covariance_eigvalsh(covariance: torch.Tensor) -> torch.Tensor:
    diagonal = torch.eye(
        int(covariance.shape[0]),
        dtype=covariance.dtype,
        device=covariance.device,
    )
    jitter = 0.0
    for _ in range(5):
        try:
            target = covariance if jitter <= 0.0 else covariance + diagonal * jitter
            return torch.linalg.eigvalsh(target)
        except torch._C._LinAlgError:
            jitter = 1.0e-8 if jitter <= 0.0 else jitter * 10.0
    singular_values = torch.linalg.svdvals(covariance)
    return torch.sort(singular_values.square(), descending=False).values


def summarize_sequence_conditioned_cluster_metrics(
    sequence: torch.Tensor,
    conditioning: dict[str, object] | None,
) -> dict[str, float]:
    if conditioning is None:
        return {}
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    if sequence_cpu.ndim != 2:
        raise ValueError(f"Expected sequence shape [frames, dims], got {tuple(sequence_cpu.shape)}")
    frame_count = int(sequence_cpu.shape[0])
    if frame_count != int(conditioning["frame_count"]):
        raise ValueError(
            "Conditioning frame count does not match sequence frame count: "
            f"{int(conditioning['frame_count'])} vs {frame_count}"
        )
    active_mask = conditioning["active_mask"]
    voiced_mask = conditioning["voiced_mask"]
    unvoiced_mask = conditioning["unvoiced_mask"]
    voiced_count = int(voiced_mask.to(torch.int64).sum().item())
    unvoiced_count = int(unvoiced_mask.to(torch.int64).sum().item())
    if voiced_count <= 0 or unvoiced_count <= 0:
        return {
            "voiced_frame_count": float(voiced_count),
            "unvoiced_frame_count": float(unvoiced_count),
            "voiced_unvoiced_centroid_distance": 0.0,
            "voiced_unvoiced_centroid_cosine": 0.0,
            "within_voiced_spread": 0.0,
            "within_unvoiced_spread": 0.0,
            "voiced_unvoiced_separation_ratio": 0.0,
            "active_template_distance_mean": 0.0,
        }
    voiced_seq = sequence_cpu[voiced_mask]
    unvoiced_seq = sequence_cpu[unvoiced_mask]
    voiced_centroid = voiced_seq.mean(dim=0)
    unvoiced_centroid = unvoiced_seq.mean(dim=0)
    centroid_delta = unvoiced_centroid - voiced_centroid
    centroid_distance = float(centroid_delta.norm().item())
    voiced_norm = float(voiced_centroid.norm().item())
    unvoiced_norm = float(unvoiced_centroid.norm().item())
    denominator = max(1.0e-8, voiced_norm * unvoiced_norm)
    centroid_cosine = float((voiced_centroid * unvoiced_centroid).sum().item() / denominator)
    within_voiced = float((voiced_seq - voiced_centroid.unsqueeze(0)).norm(dim=1).mean().item())
    within_unvoiced = float((unvoiced_seq - unvoiced_centroid.unsqueeze(0)).norm(dim=1).mean().item())
    active_seq = sequence_cpu[active_mask]
    active_centroid = active_seq.mean(dim=0)
    active_template_distance_mean = float((active_seq - active_centroid.unsqueeze(0)).norm(dim=1).mean().item())
    return {
        "voiced_frame_count": float(voiced_count),
        "unvoiced_frame_count": float(unvoiced_count),
        "voiced_unvoiced_centroid_distance": round(centroid_distance, 6),
        "voiced_unvoiced_centroid_cosine": round(centroid_cosine, 6),
        "within_voiced_spread": round(within_voiced, 6),
        "within_unvoiced_spread": round(within_unvoiced, 6),
        "voiced_unvoiced_separation_ratio": round(
            0.0 if (within_voiced + within_unvoiced) <= 1.0e-8 else centroid_distance / (within_voiced + within_unvoiced),
            6,
        ),
        "active_template_distance_mean": round(active_template_distance_mean, 6),
    }


def summarize_voicing_conditioned_waveform_metrics(
    *,
    waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    target_frame_count: int,
    sample_rate: int,
    vuv_target: torch.Tensor | None = None,
    voiced_proxy_target: torch.Tensor | None = None,
    aper_target: torch.Tensor | None = None,
    aperiodicity_proxy_target: torch.Tensor | None = None,
    energy_log_rms_norm_target: torch.Tensor | None = None,
    energy_control_target: torch.Tensor | None = None,
    energy_active_threshold: float = 0.1,
    voiced_threshold: float = DEFAULT_VUV_VOICED_FRAME_THRESHOLD,
) -> tuple[dict[str, float], dict[str, float]]:
    analysis_frames = frame_waveform_sequence(
        waveform=waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(target_frame_count),
    )
    frame_count = int(analysis_frames.shape[0])
    conditioning = build_voicing_conditioning_bundle(
        frame_count=frame_count,
        vuv_target=vuv_target,
        voiced_proxy_target=voiced_proxy_target,
        aper_target=aper_target,
        aperiodicity_proxy_target=aperiodicity_proxy_target,
        energy_control_target=energy_control_target,
        energy_log_rms_norm_target=energy_log_rms_norm_target,
        energy_active_threshold=float(energy_active_threshold),
        voiced_threshold=float(voiced_threshold),
    )
    if conditioning is None:
        return {}, {"voicing_source": "missing"}

    voicing_control = conditioning["voicing_control"]
    energy_control = conditioning["energy_control"]
    active_mask = conditioning["active_mask"]
    voiced_mask = conditioning["voiced_mask"]
    unvoiced_mask = conditioning["unvoiced_mask"]
    active_frame_count = int(conditioning["active_frame_count"])
    voiced_stats = summarize_masked_frame_spectral_statistics(
        analysis_frames=analysis_frames,
        mask=voiced_mask,
        sample_rate=int(sample_rate),
    )
    unvoiced_stats = summarize_masked_frame_spectral_statistics(
        analysis_frames=analysis_frames,
        mask=unvoiced_mask,
        sample_rate=int(sample_rate),
    )
    voiced_frame_fraction = 0.0 if frame_count <= 0 else float(voiced_mask.to(torch.float32).mean().item())
    unvoiced_frame_fraction = 0.0 if frame_count <= 0 else float(unvoiced_mask.to(torch.float32).mean().item())
    metrics = {
        "active_frame_fraction": float(conditioning["active_frame_fraction"]),
        "voiced_frame_fraction": round(voiced_frame_fraction, 6),
        "unvoiced_frame_fraction": round(unvoiced_frame_fraction, 6),
        "active_voiced_fraction": float(conditioning["active_voiced_fraction"]),
        "active_unvoiced_fraction": float(conditioning["active_unvoiced_fraction"]),
        "voiced_spectral_centroid_hz_mean": float(voiced_stats["spectral_centroid_hz_mean"]),
        "unvoiced_spectral_centroid_hz_mean": float(unvoiced_stats["spectral_centroid_hz_mean"]),
        "unvoiced_minus_voiced_spectral_centroid_hz": round(
            float(unvoiced_stats["spectral_centroid_hz_mean"])
            - float(voiced_stats["spectral_centroid_hz_mean"]),
            6,
        ),
        "voiced_spectral_bandwidth_hz_mean": float(voiced_stats["spectral_bandwidth_hz_mean"]),
        "unvoiced_spectral_bandwidth_hz_mean": float(unvoiced_stats["spectral_bandwidth_hz_mean"]),
        "unvoiced_minus_voiced_spectral_bandwidth_hz": round(
            float(unvoiced_stats["spectral_bandwidth_hz_mean"])
            - float(voiced_stats["spectral_bandwidth_hz_mean"]),
            6,
        ),
        "voiced_spectral_rolloff95_hz_mean": float(voiced_stats["spectral_rolloff95_hz_mean"]),
        "unvoiced_spectral_rolloff95_hz_mean": float(unvoiced_stats["spectral_rolloff95_hz_mean"]),
        "unvoiced_minus_voiced_spectral_rolloff95_hz": round(
            float(unvoiced_stats["spectral_rolloff95_hz_mean"])
            - float(voiced_stats["spectral_rolloff95_hz_mean"]),
            6,
        ),
        "voiced_spectral_high_band_energy_ratio_mean": float(
            voiced_stats["spectral_high_band_energy_ratio_mean"]
        ),
        "unvoiced_spectral_high_band_energy_ratio_mean": float(
            unvoiced_stats["spectral_high_band_energy_ratio_mean"]
        ),
        "unvoiced_minus_voiced_spectral_high_band_energy_ratio": round(
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
        "voicing_control_mean": round(float(voicing_control.mean().item()), 6),
        "voicing_control_active_mean": round(
            0.0 if active_frame_count <= 0 else float(voicing_control[active_mask].mean().item()),
            6,
        ),
    }
    if energy_control is not None:
        metrics["energy_control_mean"] = round(float(energy_control.mean().item()), 6)
        metrics["energy_control_active_mean"] = round(
            0.0 if active_frame_count <= 0 else float(energy_control[active_mask].mean().item()),
            6,
        )
    if active_frame_count > 0 and energy_control is not None:
        metrics["active_voicing_energy_corr"] = float(
            compute_pearson_correlation(
                voicing_control[active_mask],
                energy_control[active_mask],
            )
        )
    return metrics, {
        "voicing_source": str(conditioning.get("voicing_source", "missing")),
        "aper_source": str(conditioning.get("aper_source", "missing")),
        "energy_source": str(conditioning.get("energy_source", "missing")),
    }


def analyze_stage5_nores_waveform_decoder_structure(
    *,
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    dataset_index_path: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    device: str,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_index_path = dataset_index_path.resolve()
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
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
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the waveform-decoder structure probe.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    )
    resolved_device = torch.device(device)
    model = model.to(resolved_device)
    model.eval()
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    per_record_rows: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)

            variant_rows: list[dict[str, object]] = []
            baseline_waveform = None
            baseline_scalar_metrics = None
            record_dir = records_dir / sanitize_record_id(str(entry["record_id"]))
            record_dir.mkdir(parents=True, exist_ok=True)
            for variant in STRUCTURE_PROBE_VARIANTS:
                scalar_metrics, stage_metrics, decoded_waveform, transform_notes = run_structure_probe_variant(
                    model=model,
                    batch=batch,
                    runtime=runtime,
                    device=resolved_device,
                    use_predicted_activity_gate=bool(use_predicted_activity_gate),
                    predicted_activity_gate_floor=float(predicted_activity_gate_floor),
                    predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                    predicted_activity_gate_apply_mode=resolved_apply_mode,
                    transforms=list(variant["transforms"]),
                    waveform_output_mode=str(variant.get("waveform_output_mode", "full_output")),
                )
                label = str(variant["label"])
                audio_path = record_dir / f"{sanitize_record_id(label)}.wav"
                spectrogram_path = record_dir / f"{sanitize_record_id(label)}.linear_spectrogram.png"
                write_probe_waveform_assets(
                    waveform=decoded_waveform,
                    sample_rate=int(runtime["sample_rate"]),
                    audio_path=audio_path,
                    spectrogram_path=spectrogram_path,
                    frame_length=int(runtime["frame_length"]),
                    hop_length=int(runtime["hop_length"]),
                )
                variant_row = {
                    "label": label,
                    "description": str(variant["description"]),
                    "waveform_output_mode": str(variant.get("waveform_output_mode", "full_output")),
                    "transform_notes": transform_notes,
                    "audio_path": audio_path.as_posix(),
                    "spectrogram_path": spectrogram_path.as_posix(),
                    "scalar_metrics": scalar_metrics,
                    "stage_metrics": stage_metrics,
                    "_decoded_waveform": decoded_waveform,
                }
                if label == "baseline":
                    baseline_waveform = decoded_waveform
                    baseline_scalar_metrics = scalar_metrics
                variant_rows.append(variant_row)

            if baseline_waveform is None or baseline_scalar_metrics is None:
                raise RuntimeError("Stage5 waveform-decoder structure probe failed to produce a baseline variant.")

            for variant_row in variant_rows:
                variant_row["delta_vs_baseline"] = summarize_probe_delta_vs_baseline(
                    candidate_metrics=dict(variant_row["scalar_metrics"]),
                    baseline_metrics=baseline_scalar_metrics,
                    candidate_waveform=variant_row.get("_decoded_waveform"),
                    baseline_waveform=baseline_waveform,
                )
                variant_row["stage_delta_vs_baseline"] = summarize_stage_delta_vs_baseline(
                    candidate_stage_metrics=dict(variant_row["stage_metrics"]),
                    baseline_stage_metrics=dict(variant_rows[0]["stage_metrics"]),
                )
                variant_row.pop("_decoded_waveform", None)

            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "variants": variant_rows,
                }
            )

    aggregate_rows = build_variant_aggregates(per_record_rows)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if checkpoint_selection_path is None else resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "decode_runtime": {
            "device": str(resolved_device),
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
            "fusion_mode": str(model.fusion_mode),
            "waveform_decoder_mode": str(model.waveform_decoder_mode),
            "use_decoder_branch_condition_adapter": bool(getattr(model, "use_decoder_branch_condition_adapter", False)),
            "use_residual_shape_branch_condition_adapter": bool(
                getattr(model, "use_residual_shape_branch_condition_adapter", False)
            ),
            "residual_shape_branch_condition_scale": float(
                getattr(model, "residual_shape_branch_condition_scale", 1.0)
            ),
            "residual_shape_branch_condition_mode": str(
                getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")
            ),
        },
        "probe_variants": [
            {
                "label": str(item["label"]),
                "description": str(item["description"]),
                "transforms": [f"{stage}={mode}" for stage, mode in list(item["transforms"])],
                "waveform_output_mode": str(item.get("waveform_output_mode", "full_output")),
            }
            for item in STRUCTURE_PROBE_VARIANTS
        ],
        "variant_impact_ranking": build_variant_impact_ranking(aggregate_rows),
        "baseline_decoder_collapse_summary": build_baseline_decoder_collapse_summary(aggregate_rows),
        "baseline_upstream_coupling_localization_summary": build_baseline_upstream_coupling_localization_summary(
            aggregate_rows
        ),
        "baseline_decoder_projection_geometry_summary": build_baseline_decoder_projection_geometry_summary(
            aggregate_rows
        ),
        "voicing_conditioned_shape_summary": build_voicing_conditioned_shape_summary(aggregate_rows),
        "variant_aggregates": aggregate_rows,
        "records": per_record_rows,
        "notes": [
            "This probe is a structure-level diagnosis for the Stage5 no-res waveform decoder route, not a checkpoint ranking pass.",
            "baseline uses the current heard-route decode semantics so the resulting decoded-frame diversity stays aligned with the audible buzz path.",
            "periodic_hidden_frame_mean and noise_hidden_frame_mean test whether branch-side temporal diversity still matters once it reaches fusion.",
            "fused_hidden_frame_mean and fused_hidden_zero test whether the waveform decoder preserves or discards temporal diversity already present in fused_hidden.",
            "fused_hidden_from_periodic_hidden, fused_hidden_from_noise_hidden, and fused_hidden_from_branch_mean bypass fusion and ask whether the existing waveform decoder can respond if it is fed branch-side hidden dynamics directly.",
            "If fused_hidden remains materially less template-like than waveform_frames on baseline, that is evidence the waveform decoder itself is a collapse site.",
            "If fused_hidden_frame_mean barely changes waveform_frames or decoded metrics, the waveform decoder is acting close to a fixed-template projector around the current operating region.",
            "decoded_voicing_conditioned and aligned_voicing_conditioned summarize frame-level spectral splits under the same target-side voiced-vs-unvoiced masks, so we can ask whether baseline/base_logits/residual_shape reproduce the target's two-shape contrast instead of only matching global buzz brightness.",
        ],
    }
    json_path = output_dir / "stage5_waveform_decoder_structure_probe.json"
    md_path = output_dir / "stage5_waveform_decoder_structure_probe.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def run_structure_probe_variant(
    *,
    model: torch.nn.Module,
    batch: dict[str, torch.Tensor],
    runtime: dict[str, int],
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    transforms: list[tuple[str, str]],
    waveform_output_mode: str,
) -> tuple[dict[str, float], dict[str, dict[str, float]], torch.Tensor, list[str]]:
    periodic_hidden = model.periodic_encoder(
        batch["periodic_branch_features"].to(device=device, dtype=torch.float32)
    )
    noise_hidden = model.noise_encoder(
        batch["noise_branch_features"].to(device=device, dtype=torch.float32)
    )
    transform_notes: list[str] = []
    periodic_hidden = apply_structure_transform(
        tensor=periodic_hidden,
        transforms=transforms,
        stage_name="periodic_hidden",
        transform_notes=transform_notes,
    )
    noise_hidden = apply_structure_transform(
        tensor=noise_hidden,
        transforms=transforms,
        stage_name="noise_hidden",
        transform_notes=transform_notes,
    )
    fused_hidden = compute_fused_hidden_for_probe(
        model=model,
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
    )
    fused_hidden = apply_structure_transform(
        tensor=fused_hidden,
        transforms=transforms,
        stage_name="fused_hidden",
        transform_notes=transform_notes,
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
    )
    outputs = compute_waveform_structure_outputs_for_probe(
        model=model,
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        fused_hidden=fused_hidden,
        waveform_output_mode=waveform_output_mode,
    )
    waveform_frames = outputs["waveform_frames"]
    periodic_gate = torch.sigmoid(model.periodic_gate(periodic_hidden))
    noise_gate = torch.sigmoid(model.noise_gate(noise_hidden))
    predicted_activity = torch.maximum(periodic_gate, noise_gate)
    decoded_waveform = reconstruct_waveform_from_frames(
        waveform_frames=waveform_frames,
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
        frame_gain_floor=float(predicted_activity_gate_floor),
        frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        frame_gain_apply_mode=predicted_activity_gate_apply_mode,
    ).detach().cpu().to(torch.float32)
    stage_metrics = summarize_stage_metrics(
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        fused_hidden=fused_hidden,
        waveform_decoder_base_logits=outputs["waveform_decoder_base_logits"],
        waveform_residual_shape_delta=outputs["waveform_residual_shape_delta"],
        decoder_hidden=outputs["decoder_hidden"],
        waveform_frame_logits=outputs["waveform_frame_logits"],
        waveform_frames=waveform_frames,
        decoded_waveform=decoded_waveform,
        aligned_waveform=batch.get("aligned_waveform"),
        vuv_target=batch.get("vuv_target"),
        voiced_proxy_target=batch.get("voiced_proxy_target"),
        aper_target=batch.get("aper_target"),
        aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
        energy_control_target=batch.get("energy_control_target"),
        energy_log_rms_norm_target=batch.get("energy_log_rms_norm_target"),
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        sample_rate=int(runtime["sample_rate"]),
        predicted_activity=predicted_activity,
        periodic_gate=periodic_gate,
        noise_gate=noise_gate,
    )
    scalar_metrics = flatten_stage_metrics(stage_metrics)
    return scalar_metrics, stage_metrics, decoded_waveform, transform_notes


def compute_fused_hidden_for_probe(
    *,
    model: torch.nn.Module,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
) -> torch.Tensor:
    fusion_mode = str(getattr(model, "fusion_mode", "plain"))
    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    branch_difference_hidden = periodic_hidden - noise_hidden
    if fusion_mode == "plain":
        if getattr(model, "fusion", None) is None:
            raise RuntimeError("model.fusion is not initialized for plain fusion mode.")
        return model.fusion(torch.cat([periodic_hidden, noise_hidden], dim=-1))
    if fusion_mode == "branch_mean_residual_v1":
        fusion_branch_mean_residual = getattr(model, "fusion_branch_mean_residual", None)
        if fusion_branch_mean_residual is None:
            raise RuntimeError("fusion_branch_mean_residual is not initialized for branch_mean_residual_v1.")
        fusion_residual_hidden = fusion_branch_mean_residual(
            torch.cat(
                [
                    periodic_hidden,
                    noise_hidden,
                    branch_difference_hidden,
                ],
                dim=-1,
            )
        )
        return branch_mean_hidden + fusion_residual_hidden
    if fusion_mode == "periodic_residual_v1":
        fusion_periodic_residual_adapter = getattr(model, "fusion_periodic_residual_adapter", None)
        fusion_periodic_residual_gate = getattr(model, "fusion_periodic_residual_gate", None)
        fusion_periodic_residual_proj = getattr(model, "fusion_periodic_residual_proj", None)
        if (
            fusion_periodic_residual_adapter is None
            or fusion_periodic_residual_gate is None
            or fusion_periodic_residual_proj is None
        ):
            raise RuntimeError("fusion_periodic_residual modules are not initialized for periodic_residual_v1.")
        fusion_residual_context = fusion_periodic_residual_adapter(
            torch.cat(
                [
                    periodic_hidden,
                    noise_hidden,
                    branch_difference_hidden,
                ],
                dim=-1,
            )
        )
        fusion_residual_gate = torch.sigmoid(fusion_periodic_residual_gate(fusion_residual_context))
        fusion_residual_hidden = fusion_residual_gate * torch.tanh(
            fusion_periodic_residual_proj(fusion_residual_context)
        )
        return periodic_hidden + fusion_residual_hidden
    if fusion_mode == "branch_mean_contrast_residual_v1":
        fusion_branch_mean_contrast_norm = getattr(model, "fusion_branch_mean_contrast_norm", None)
        fusion_branch_mean_contrast_gate = getattr(model, "fusion_branch_mean_contrast_gate", None)
        fusion_branch_mean_contrast_proj = getattr(model, "fusion_branch_mean_contrast_proj", None)
        if (
            fusion_branch_mean_contrast_norm is None
            or fusion_branch_mean_contrast_gate is None
            or fusion_branch_mean_contrast_proj is None
        ):
            raise RuntimeError(
                "fusion_branch_mean_contrast modules are not initialized for branch_mean_contrast_residual_v1."
            )
        contrast_hidden = fusion_branch_mean_contrast_norm(branch_difference_hidden)
        fusion_residual_gate = torch.sigmoid(fusion_branch_mean_contrast_gate(contrast_hidden))
        fusion_residual_hidden = fusion_residual_gate * torch.tanh(
            fusion_branch_mean_contrast_proj(contrast_hidden)
        )
        return branch_mean_hidden + fusion_residual_hidden
    raise ValueError(f"Unsupported fusion_mode in structure probe: {fusion_mode!r}")


def compute_waveform_structure_outputs_for_probe(
    *,
    model: torch.nn.Module,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
    waveform_output_mode: str = "full_output",
) -> dict[str, torch.Tensor]:
    waveform_decoder_mode = str(getattr(model, "waveform_decoder_mode", "fused_single"))
    if waveform_decoder_mode != "fused_single":
        raise ValueError(f"Unsupported waveform_decoder_mode in structure probe: {waveform_decoder_mode!r}")
    waveform_decoder = getattr(model, "waveform_decoder", None)
    if waveform_decoder is None:
        raise RuntimeError("waveform_decoder is not initialized for fused_single structure probe.")
    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    decoder_hidden = fused_hidden
    waveform_decoder_input_hidden = decoder_hidden
    branch_condition_gate = None
    if bool(getattr(model, "use_decoder_branch_condition_adapter", False)):
        decoder_branch_condition_adapter = getattr(model, "decoder_branch_condition_adapter", None)
        decoder_branch_condition_gate = getattr(model, "decoder_branch_condition_gate", None)
        decoder_fused_condition_proj = getattr(model, "decoder_fused_condition_proj", None)
        if (
            decoder_branch_condition_adapter is None
            or decoder_branch_condition_gate is None
            or decoder_fused_condition_proj is None
        ):
            raise RuntimeError("Decoder branch-condition adapter modules are not initialized for structure probe.")
        branch_condition_features = torch.cat(
            [
                fused_hidden,
                branch_mean_hidden,
                fused_hidden - branch_mean_hidden,
            ],
            dim=-1,
        )
        branch_condition_context = decoder_branch_condition_adapter(branch_condition_features)
        branch_condition_gate = torch.sigmoid(decoder_branch_condition_gate(branch_condition_context))
        fused_condition = torch.tanh(decoder_fused_condition_proj(branch_condition_context))
        decoder_hidden = decoder_hidden + branch_condition_gate * fused_condition
    if bool(getattr(model, "use_waveform_decoder_input_adapter", False)):
        waveform_decoder_input_adapter = getattr(model, "waveform_decoder_input_adapter", None)
        waveform_decoder_input_gate_head = getattr(model, "waveform_decoder_input_gate", None)
        waveform_decoder_input_proj = getattr(model, "waveform_decoder_input_proj", None)
        if (
            waveform_decoder_input_adapter is None
            or waveform_decoder_input_gate_head is None
            or waveform_decoder_input_proj is None
        ):
            raise RuntimeError("Waveform decoder input adapter modules are not initialized for structure probe.")
        waveform_decoder_input_context = waveform_decoder_input_adapter(decoder_hidden)
        waveform_decoder_input_gate = torch.sigmoid(
            waveform_decoder_input_gate_head(waveform_decoder_input_context)
        )
        waveform_decoder_input_delta = torch.tanh(
            waveform_decoder_input_proj(waveform_decoder_input_context)
        )
        waveform_decoder_input_hidden = (
            decoder_hidden
            + float(getattr(model, "waveform_decoder_input_adapter_scale", 1.0))
            * waveform_decoder_input_gate
            * waveform_decoder_input_delta
        )
    waveform_decoder_base_logits, _ = model.compute_waveform_decoder_base_logits(
        waveform_decoder_input_hidden
    )
    waveform_frame_logits = waveform_decoder_base_logits
    residual_shape_delta = torch.zeros_like(waveform_decoder_base_logits)
    if bool(getattr(model, "use_residual_shape_branch_condition_adapter", False)):
        residual_shape_branch_condition_adapter = getattr(model, "residual_shape_branch_condition_adapter", None)
        residual_shape_branch_condition_gate_head = getattr(model, "residual_shape_branch_condition_gate", None)
        residual_shape_branch_condition_proj = getattr(model, "residual_shape_branch_condition_proj", None)
        if (
            residual_shape_branch_condition_adapter is None
            or residual_shape_branch_condition_gate_head is None
            or residual_shape_branch_condition_proj is None
        ):
            raise RuntimeError("Residual-shape branch-condition adapter modules are not initialized for structure probe.")
        residual_shape_branch_condition_features = torch.cat(
            [
                fused_hidden,
                branch_mean_hidden,
                fused_hidden - branch_mean_hidden,
            ],
            dim=-1,
        )
        residual_shape_branch_condition_context = residual_shape_branch_condition_adapter(
            residual_shape_branch_condition_features
        )
        residual_shape_branch_condition_gate = torch.sigmoid(
            residual_shape_branch_condition_gate_head(residual_shape_branch_condition_context)
        )
        residual_shape_branch_condition_delta = resolve_residual_shape_branch_condition_delta(
            delta=torch.tanh(
                residual_shape_branch_condition_proj(residual_shape_branch_condition_context)
            ),
            mode=str(getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")),
        )
        residual_shape_delta = (
            float(getattr(model, "residual_shape_branch_condition_scale", 1.0))
            * residual_shape_branch_condition_gate
            * residual_shape_branch_condition_delta
        )
    resolved_output_mode = str(waveform_output_mode).strip().lower()
    if resolved_output_mode == "full_output":
        waveform_frame_logits = waveform_decoder_base_logits + residual_shape_delta
    elif resolved_output_mode == "base_logits_only":
        waveform_frame_logits = waveform_decoder_base_logits
    elif resolved_output_mode == "residual_shape_only":
        waveform_frame_logits = residual_shape_delta
    else:
        raise ValueError(f"Unsupported waveform_output_mode in structure probe: {waveform_output_mode!r}")
    return {
        "decoder_hidden": decoder_hidden,
        "waveform_decoder_base_logits": waveform_decoder_base_logits,
        "waveform_residual_shape_delta": residual_shape_delta,
        "waveform_frame_logits": waveform_frame_logits,
        "waveform_frames": torch.tanh(waveform_frame_logits),
    }


def write_probe_waveform_assets(
    *,
    waveform: torch.Tensor,
    sample_rate: int,
    audio_path: Path,
    spectrogram_path: Path,
    frame_length: int,
    hop_length: int,
) -> None:
    write_waveform_int16(audio_path, waveform, sample_rate=sample_rate)
    save_linear_spectrogram_png(
        waveform=waveform,
        sample_rate=int(sample_rate),
        output_path=spectrogram_path,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )


def save_linear_spectrogram_png(
    *,
    waveform: torch.Tensor,
    sample_rate: int,
    output_path: Path,
    frame_length: int,
    hop_length: int,
) -> None:
    import matplotlib.pyplot as plt

    waveform_cpu = waveform.detach().cpu().to(torch.float32).view(-1)
    n_fft = 1024
    win_length = min(int(n_fft), max(256, int(frame_length)))
    hop = max(1, int(hop_length))
    window = torch.hann_window(win_length, dtype=torch.float32)
    spectrogram = torch.stft(
        waveform_cpu,
        n_fft=n_fft,
        hop_length=hop,
        win_length=win_length,
        window=window,
        center=True,
        return_complex=True,
    ).abs()
    if int(spectrogram.numel()) <= 0:
        image = torch.zeros((1, 1), dtype=torch.float32)
    else:
        upper = float(torch.quantile(spectrogram.reshape(-1), 0.995).item())
        if upper <= 1.0e-8:
            upper = float(spectrogram.max().item())
        if upper <= 1.0e-8:
            image = torch.zeros_like(spectrogram)
        else:
            image = (spectrogram / upper).clamp(0.0, 1.0)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.imsave(output_path, image.flip(0).numpy(), cmap="gray", vmin=0.0, vmax=1.0)


def apply_structure_transform(
    *,
    tensor: torch.Tensor,
    transforms: list[tuple[str, str]],
    stage_name: str,
    transform_notes: list[str],
    periodic_hidden: torch.Tensor | None = None,
    noise_hidden: torch.Tensor | None = None,
) -> torch.Tensor:
    transformed = tensor
    for target_stage, mode in transforms:
        if str(target_stage) != str(stage_name):
            continue
        if mode == "frame_mean":
            mean_values = transformed.mean(dim=0, keepdim=True)
            transformed = mean_values.expand_as(transformed)
        elif mode == "zero":
            transformed = torch.zeros_like(transformed)
        elif mode == "replace_with_periodic_hidden":
            if periodic_hidden is None:
                raise ValueError("periodic_hidden is required for replace_with_periodic_hidden.")
            if tuple(periodic_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "periodic_hidden shape does not match fused_hidden for bypass substitution: "
                    f"{tuple(periodic_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = periodic_hidden
        elif mode == "replace_with_noise_hidden":
            if noise_hidden is None:
                raise ValueError("noise_hidden is required for replace_with_noise_hidden.")
            if tuple(noise_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "noise_hidden shape does not match fused_hidden for bypass substitution: "
                    f"{tuple(noise_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = noise_hidden
        elif mode == "replace_with_branch_mean":
            if periodic_hidden is None or noise_hidden is None:
                raise ValueError("periodic_hidden and noise_hidden are required for replace_with_branch_mean.")
            if tuple(periodic_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "periodic_hidden shape does not match fused_hidden for branch-mean substitution: "
                    f"{tuple(periodic_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            if tuple(noise_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "noise_hidden shape does not match fused_hidden for branch-mean substitution: "
                    f"{tuple(noise_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = 0.5 * (periodic_hidden + noise_hidden)
        else:
            raise ValueError(f"Unsupported structure-probe transform mode: {mode!r}")
        transform_notes.append(f"{stage_name} -> {mode}")
    return transformed


def summarize_stage_metrics(
    *,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
    waveform_decoder_base_logits: torch.Tensor,
    waveform_residual_shape_delta: torch.Tensor,
    decoder_hidden: torch.Tensor,
    waveform_frame_logits: torch.Tensor,
    waveform_frames: torch.Tensor,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor | None,
    vuv_target: torch.Tensor | None,
    voiced_proxy_target: torch.Tensor | None,
    aper_target: torch.Tensor | None,
    aperiodicity_proxy_target: torch.Tensor | None,
    energy_control_target: torch.Tensor | None,
    energy_log_rms_norm_target: torch.Tensor | None,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
    predicted_activity: torch.Tensor,
    periodic_gate: torch.Tensor,
    noise_gate: torch.Tensor,
) -> dict[str, dict[str, float]]:
    periodic_hidden_cpu = periodic_hidden.detach().cpu().to(torch.float32)
    noise_hidden_cpu = noise_hidden.detach().cpu().to(torch.float32)
    fused_hidden_cpu = fused_hidden.detach().cpu().to(torch.float32)
    waveform_frames_cpu = waveform_frames.detach().cpu().to(torch.float32)
    decoded_analysis_frames = frame_waveform_sequence(
        waveform=decoded_waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(waveform_frames_cpu.shape[0]),
    )
    aligned_waveform_cpu = None
    aligned_frame_metrics = None
    aligned_frame_rms = None
    if aligned_waveform is not None:
        aligned_waveform_cpu = aligned_waveform.detach().cpu().to(torch.float32)[: decoded_waveform.shape[0]]
        aligned_analysis_frames = frame_waveform_sequence(
            waveform=aligned_waveform_cpu,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            target_frame_count=int(waveform_frames_cpu.shape[0]),
        )
        aligned_frame_metrics = summarize_representation_metrics(aligned_analysis_frames)
        aligned_frame_rms = aligned_analysis_frames.pow(2).mean(dim=1).sqrt()
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform, int(sample_rate))
    decoded_frame_metrics = summarize_representation_metrics(decoded_analysis_frames)
    conditioning = build_voicing_conditioning_bundle(
        frame_count=int(waveform_frames_cpu.shape[0]),
        vuv_target=vuv_target,
        voiced_proxy_target=voiced_proxy_target,
        aper_target=aper_target,
        aperiodicity_proxy_target=aperiodicity_proxy_target,
        energy_control_target=energy_control_target,
        energy_log_rms_norm_target=energy_log_rms_norm_target,
    )
    decoded_voicing_metrics, decoded_voicing_notes = summarize_voicing_conditioned_waveform_metrics(
        waveform=decoded_waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(waveform_frames_cpu.shape[0]),
        sample_rate=int(sample_rate),
        vuv_target=vuv_target,
        voiced_proxy_target=voiced_proxy_target,
        aper_target=aper_target,
        aperiodicity_proxy_target=aperiodicity_proxy_target,
        energy_log_rms_norm_target=energy_log_rms_norm_target,
        energy_control_target=energy_control_target,
    )
    periodic_metrics = summarize_representation_metrics(periodic_hidden_cpu)
    noise_metrics = summarize_representation_metrics(noise_hidden_cpu)
    fused_metrics = summarize_representation_metrics(fused_hidden_cpu)
    base_logits_metrics = summarize_representation_metrics(
        waveform_decoder_base_logits.detach().cpu().to(torch.float32)
    )
    residual_shape_metrics = summarize_representation_metrics(
        waveform_residual_shape_delta.detach().cpu().to(torch.float32)
    )
    decoder_metrics = summarize_representation_metrics(decoder_hidden.detach().cpu().to(torch.float32))
    waveform_frame_logits_metrics = summarize_representation_metrics(
        waveform_frame_logits.detach().cpu().to(torch.float32)
    )
    waveform_frame_metrics = summarize_representation_metrics(waveform_frames_cpu)
    fused_control_metrics, fused_control_notes = summarize_sequence_control_coupling_metrics(
        sequence=fused_hidden_cpu,
        conditioning=conditioning,
    )
    fused_geometry_metrics = summarize_sequence_geometry_metrics(fused_hidden_cpu)
    fused_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(fused_hidden_cpu, conditioning)
    decoder_control_metrics, decoder_control_notes = summarize_sequence_control_coupling_metrics(
        sequence=decoder_hidden.detach().cpu().to(torch.float32),
        conditioning=conditioning,
    )
    decoder_geometry_metrics = summarize_sequence_geometry_metrics(
        decoder_hidden.detach().cpu().to(torch.float32)
    )
    decoder_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(
        decoder_hidden.detach().cpu().to(torch.float32),
        conditioning,
    )
    base_logits_control_metrics, base_logits_control_notes = summarize_sequence_control_coupling_metrics(
        sequence=waveform_decoder_base_logits.detach().cpu().to(torch.float32),
        conditioning=conditioning,
    )
    base_logits_geometry_metrics = summarize_sequence_geometry_metrics(
        waveform_decoder_base_logits.detach().cpu().to(torch.float32)
    )
    base_logits_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(
        waveform_decoder_base_logits.detach().cpu().to(torch.float32),
        conditioning,
    )
    waveform_frame_control_metrics, waveform_frame_control_notes = summarize_sequence_control_coupling_metrics(
        sequence=waveform_frames_cpu,
        conditioning=conditioning,
    )
    waveform_frame_geometry_metrics = summarize_sequence_geometry_metrics(waveform_frames_cpu)
    waveform_frame_cluster_metrics = summarize_sequence_conditioned_cluster_metrics(waveform_frames_cpu, conditioning)
    decode_metrics = {
        "decoded_waveform_rms": round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6),
        "decoded_abs_mean": round(float(decoded_waveform.abs().mean().item()), 6),
        "decoded_peak_abs": round(float(decoded_waveform.abs().max().item()), 6),
        "decoded_zero_crossing_rate": round(float(compute_zero_crossing_rate(decoded_waveform)), 6),
        "decoded_spectral_centroid_hz": float(decoded_spectral["centroid_hz"]),
        "decoded_spectral_bandwidth_hz": float(decoded_spectral["bandwidth_hz"]),
        "decoded_spectral_rolloff95_hz": float(decoded_spectral["rolloff95_hz"]),
        "decoded_spectral_high_band_energy_ratio": float(decoded_spectral["high_band_energy_ratio"]),
        "predicted_activity_mean": round(float(predicted_activity.detach().cpu().mean().item()), 6),
        "predicted_activity_std": round(float(predicted_activity.detach().cpu().std(unbiased=False).item()), 6),
        "periodic_gate_mean": round(float(periodic_gate.detach().cpu().mean().item()), 6),
        "noise_gate_mean": round(float(noise_gate.detach().cpu().mean().item()), 6),
    }
    if aligned_waveform_cpu is not None and aligned_frame_metrics is not None and aligned_frame_rms is not None:
        decoded_frame_rms = decoded_analysis_frames.pow(2).mean(dim=1).sqrt()
        decode_metrics.update(
            {
                "aligned_waveform_rms": round(float(aligned_waveform_cpu.pow(2).mean().sqrt().item()), 6),
                "decoded_to_aligned_rms_ratio": round(
                    0.0
                    if float(aligned_waveform_cpu.pow(2).mean().sqrt().item()) <= 1.0e-8
                    else float(decoded_waveform.pow(2).mean().sqrt().item())
                    / float(aligned_waveform_cpu.pow(2).mean().sqrt().item()),
                    6,
                ),
                "decoded_frame_rms_to_aligned_frame_rms_corr": float(
                    compute_pearson_correlation(decoded_frame_rms, aligned_frame_rms)
                ),
                "decoded_frame_template_cosine_gap_vs_aligned": round(
                    float(decoded_frame_metrics["template_cosine_mean"])
                    - float(aligned_frame_metrics["template_cosine_mean"]),
                    6,
                ),
                "decoded_frame_adjacent_cosine_gap_vs_aligned": round(
                    float(decoded_frame_metrics["adjacent_cosine_mean"])
                    - float(aligned_frame_metrics["adjacent_cosine_mean"]),
                    6,
                ),
            }
        )
    aligned_voicing_metrics = {}
    if aligned_waveform_cpu is not None:
        aligned_voicing_metrics, _ = summarize_voicing_conditioned_waveform_metrics(
            waveform=aligned_waveform_cpu,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            target_frame_count=int(waveform_frames_cpu.shape[0]),
            sample_rate=int(sample_rate),
            vuv_target=vuv_target,
            voiced_proxy_target=voiced_proxy_target,
            aper_target=aper_target,
            aperiodicity_proxy_target=aperiodicity_proxy_target,
            energy_log_rms_norm_target=energy_log_rms_norm_target,
            energy_control_target=energy_control_target,
        )
    control_metrics = {
        "voicing_control_ready": 0.0 if not decoded_voicing_metrics else 1.0,
        "voicing_source_is_vuv_target": 1.0 if decoded_voicing_notes.get("voicing_source") == "vuv_target" else 0.0,
        "voicing_source_is_voiced_proxy_target": (
            1.0 if decoded_voicing_notes.get("voicing_source") == "voiced_proxy_target" else 0.0
        ),
        "voicing_source_is_aper_inversion": (
            1.0 if str(decoded_voicing_notes.get("voicing_source", "")).endswith("_inverted") else 0.0
        ),
        "aper_source_is_aper_target": 1.0 if decoded_voicing_notes.get("aper_source") == "aper_target" else 0.0,
        "aper_source_is_proxy_target": (
            1.0 if decoded_voicing_notes.get("aper_source") == "aperiodicity_proxy_target" else 0.0
        ),
        "energy_source_is_norm_target": (
            1.0 if decoded_voicing_notes.get("energy_source") == "energy_log_rms_norm_target" else 0.0
        ),
        "energy_source_is_logsig_target": (
            1.0 if decoded_voicing_notes.get("energy_source") == "energy_control_target_sigmoid" else 0.0
        ),
    }
    if decoded_voicing_metrics and aligned_voicing_metrics:
        control_metrics.update(
            {
                "decoded_vs_aligned_unvoiced_minus_voiced_spectral_centroid_hz_gap": round(
                    float(decoded_voicing_metrics["unvoiced_minus_voiced_spectral_centroid_hz"])
                    - float(aligned_voicing_metrics["unvoiced_minus_voiced_spectral_centroid_hz"]),
                    6,
                ),
                "decoded_vs_aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio_gap": round(
                    float(decoded_voicing_metrics["unvoiced_minus_voiced_spectral_high_band_energy_ratio"])
                    - float(aligned_voicing_metrics["unvoiced_minus_voiced_spectral_high_band_energy_ratio"]),
                    6,
                ),
            }
        )
    return {
        "periodic_hidden": periodic_metrics,
        "noise_hidden": noise_metrics,
        "fused_hidden": fused_metrics,
        "waveform_decoder_base_logits": base_logits_metrics,
        "waveform_residual_shape_delta": residual_shape_metrics,
        "decoder_hidden": decoder_metrics,
        "waveform_frame_logits": waveform_frame_logits_metrics,
        "waveform_frames": waveform_frame_metrics,
        "decoded_frames": decoded_frame_metrics,
        "decode": decode_metrics,
        "decoded_voicing_conditioned": decoded_voicing_metrics,
        "aligned_voicing_conditioned": aligned_voicing_metrics,
        "voicing_controls": control_metrics,
        "fused_hidden_control_coupling": fused_control_metrics,
        "fused_hidden_geometry": fused_geometry_metrics,
        "fused_hidden_conditioned_clusters": fused_cluster_metrics,
        "decoder_hidden_control_coupling": decoder_control_metrics,
        "decoder_hidden_geometry": decoder_geometry_metrics,
        "decoder_hidden_conditioned_clusters": decoder_cluster_metrics,
        "waveform_decoder_base_logits_control_coupling": base_logits_control_metrics,
        "waveform_decoder_base_logits_geometry": base_logits_geometry_metrics,
        "waveform_decoder_base_logits_conditioned_clusters": base_logits_cluster_metrics,
        "waveform_frames_control_coupling": waveform_frame_control_metrics,
        "waveform_frames_geometry": waveform_frame_geometry_metrics,
        "waveform_frames_conditioned_clusters": waveform_frame_cluster_metrics,
    }


def summarize_representation_metrics(sequence: torch.Tensor) -> dict[str, float]:
    metrics = summarize_frame_sequence_metrics(sequence)
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    temporal_delta = sequence_cpu.new_zeros((0,), dtype=torch.float32)
    if int(sequence_cpu.shape[0]) > 1:
        temporal_delta = (sequence_cpu[1:] - sequence_cpu[:-1]).abs()
    metrics.update(
        {
            "sequence_std": round(float(sequence_cpu.std(unbiased=False).item()), 6),
            "sequence_abs_mean": round(float(sequence_cpu.abs().mean().item()), 6),
            "frame_delta_abs_mean": round(
                0.0 if int(temporal_delta.numel()) <= 0 else float(temporal_delta.mean().item()),
                6,
            ),
        }
    )
    return metrics


def flatten_stage_metrics(stage_metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    flattened: dict[str, float] = {}
    for stage_name, metrics in stage_metrics.items():
        for key, value in metrics.items():
            flattened[f"{stage_name}_{key}"] = float(value)
            if stage_name == "decode":
                flattened[key] = float(value)
    fused_metrics = dict(stage_metrics["fused_hidden"])
    waveform_metrics = dict(stage_metrics["waveform_frames"])
    decoded_metrics = dict(stage_metrics["decoded_frames"])
    flattened["fused_to_waveform_template_cosine_gap"] = round(
        float(waveform_metrics["template_cosine_mean"]) - float(fused_metrics["template_cosine_mean"]),
        6,
    )
    flattened["fused_to_waveform_adjacent_cosine_gap"] = round(
        float(waveform_metrics["adjacent_cosine_mean"]) - float(fused_metrics["adjacent_cosine_mean"]),
        6,
    )
    flattened["fused_to_waveform_delta_abs_mean_ratio"] = round(
        0.0
        if abs(float(fused_metrics["frame_delta_abs_mean"])) <= 1.0e-8
        else float(waveform_metrics["frame_delta_abs_mean"]) / float(fused_metrics["frame_delta_abs_mean"]),
        6,
    )
    flattened["waveform_to_decoded_template_cosine_gap"] = round(
        float(decoded_metrics["template_cosine_mean"]) - float(waveform_metrics["template_cosine_mean"]),
        6,
    )
    flattened["waveform_to_decoded_adjacent_cosine_gap"] = round(
        float(decoded_metrics["adjacent_cosine_mean"]) - float(waveform_metrics["adjacent_cosine_mean"]),
        6,
    )
    return flattened


def summarize_stage_delta_vs_baseline(
    *,
    candidate_stage_metrics: dict[str, dict[str, float]],
    baseline_stage_metrics: dict[str, dict[str, float]],
) -> dict[str, float]:
    deltas: dict[str, float] = {}
    for stage_name, metrics in candidate_stage_metrics.items():
        baseline_metrics = dict(baseline_stage_metrics.get(stage_name, {}))
        for key, value in metrics.items():
            deltas[f"{stage_name}_{key}_delta_vs_baseline"] = round(
                float(value) - float(baseline_metrics.get(key, 0.0)),
                6,
            )
    return deltas


def build_variant_aggregates(per_record_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    variant_map: dict[str, dict[str, object]] = {}
    for record_row in per_record_rows:
        for variant_row in list(record_row["variants"]):
            label = str(variant_row["label"])
            bucket = variant_map.setdefault(
                label,
                {
                    "label": label,
                    "description": str(variant_row["description"]),
                    "record_count": 0,
                    "scalar_metrics": {},
                    "delta_vs_baseline": {},
                    "stage_delta_vs_baseline": {},
                },
            )
            bucket["record_count"] = int(bucket["record_count"]) + 1
            for key, value in dict(variant_row["scalar_metrics"]).items():
                bucket["scalar_metrics"].setdefault(key, []).append(float(value))
            for key, value in dict(variant_row["delta_vs_baseline"]).items():
                bucket["delta_vs_baseline"].setdefault(key, []).append(float(value))
            for key, value in dict(variant_row["stage_delta_vs_baseline"]).items():
                bucket["stage_delta_vs_baseline"].setdefault(key, []).append(float(value))
    aggregates = []
    for label, payload in variant_map.items():
        aggregates.append(
            {
                "label": label,
                "description": payload["description"],
                "record_count": int(payload["record_count"]),
                "scalar_metrics": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["scalar_metrics"]).items()
                },
                "delta_vs_baseline": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["delta_vs_baseline"]).items()
                },
                "stage_delta_vs_baseline": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["stage_delta_vs_baseline"]).items()
                },
            }
        )
    return sorted(
        aggregates,
        key=lambda item: (
            0 if item["label"] == "baseline" else 1,
            -abs(
                float(
                    item["delta_vs_baseline"]
                    .get("waveform_mean_abs_delta_vs_baseline", {})
                    .get("mean", 0.0)
                )
            ),
        ),
    )


def build_variant_impact_ranking(aggregate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ranking = []
    for row in aggregate_rows:
        if row["label"] == "baseline":
            continue
        scalar_metrics = dict(row["scalar_metrics"])
        delta_vs_baseline = dict(row["delta_vs_baseline"])
        ranking.append(
            {
                "label": row["label"],
                "description": row["description"],
                "mean_waveform_mean_abs_delta_vs_baseline": float(
                    delta_vs_baseline.get("waveform_mean_abs_delta_vs_baseline", {}).get("mean", 0.0)
                ),
                "mean_fused_to_waveform_template_cosine_gap": float(
                    scalar_metrics.get("fused_to_waveform_template_cosine_gap", {}).get("mean", 0.0)
                ),
                "mean_fused_to_waveform_adjacent_cosine_gap": float(
                    scalar_metrics.get("fused_to_waveform_adjacent_cosine_gap", {}).get("mean", 0.0)
                ),
                "mean_waveform_frames_template_cosine_mean": float(
                    scalar_metrics.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0)
                ),
                "mean_decoded_frame_template_cosine_mean": float(
                    scalar_metrics.get("decoded_frames_template_cosine_mean", {}).get("mean", 0.0)
                ),
            }
        )
    return sorted(
        ranking,
        key=lambda item: abs(float(item["mean_waveform_mean_abs_delta_vs_baseline"])),
        reverse=True,
    )


def build_baseline_decoder_collapse_summary(aggregate_rows: list[dict[str, object]]) -> dict[str, float | str]:
    baseline_row = next((row for row in aggregate_rows if row["label"] == "baseline"), None)
    if baseline_row is None:
        return {}
    scalar_metrics = dict(baseline_row["scalar_metrics"])
    fused_template = float(scalar_metrics.get("fused_hidden_template_cosine_mean", {}).get("mean", 0.0))
    waveform_template = float(scalar_metrics.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0))
    decoded_template = float(scalar_metrics.get("decoded_frames_template_cosine_mean", {}).get("mean", 0.0))
    fused_adjacent = float(scalar_metrics.get("fused_hidden_adjacent_cosine_mean", {}).get("mean", 0.0))
    waveform_adjacent = float(scalar_metrics.get("waveform_frames_adjacent_cosine_mean", {}).get("mean", 0.0))
    decoder_gap_template = round(waveform_template - fused_template, 6)
    decoder_gap_adjacent = round(waveform_adjacent - fused_adjacent, 6)
    if decoder_gap_template >= 0.15 and decoder_gap_adjacent >= 0.15:
        diagnosis = "waveform_decoder_collapse_likely"
    elif decoder_gap_template >= 0.08 or decoder_gap_adjacent >= 0.08:
        diagnosis = "waveform_decoder_collapse_possible"
    else:
        diagnosis = "collapse_not_localized_to_waveform_decoder"
    return {
        "fused_hidden_template_cosine_mean": round(fused_template, 6),
        "waveform_frames_template_cosine_mean": round(waveform_template, 6),
        "decoded_frames_template_cosine_mean": round(decoded_template, 6),
        "fused_hidden_adjacent_cosine_mean": round(fused_adjacent, 6),
        "waveform_frames_adjacent_cosine_mean": round(waveform_adjacent, 6),
        "fused_to_waveform_template_cosine_gap": decoder_gap_template,
        "fused_to_waveform_adjacent_cosine_gap": decoder_gap_adjacent,
        "diagnosis": diagnosis,
    }


def build_voicing_conditioned_shape_summary(aggregate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    interesting_labels = {
        "baseline",
        "waveform_decoder_base_logits_only",
        "waveform_residual_shape_only",
    }
    rows = []
    for row in aggregate_rows:
        label = str(row["label"])
        if label not in interesting_labels:
            continue
        scalar_metrics = dict(row.get("scalar_metrics", {}))
        rows.append(
            {
                "label": label,
                "record_count": int(row.get("record_count", 0)),
                "decoded_unvoiced_minus_voiced_spectral_centroid_hz": float(
                    scalar_metrics.get(
                        "decoded_voicing_conditioned_unvoiced_minus_voiced_spectral_centroid_hz",
                        {},
                    ).get("mean", 0.0)
                ),
                "decoded_unvoiced_minus_voiced_spectral_high_band_energy_ratio": float(
                    scalar_metrics.get(
                        "decoded_voicing_conditioned_unvoiced_minus_voiced_spectral_high_band_energy_ratio",
                        {},
                    ).get("mean", 0.0)
                ),
                "aligned_unvoiced_minus_voiced_spectral_centroid_hz": float(
                    scalar_metrics.get(
                        "aligned_voicing_conditioned_unvoiced_minus_voiced_spectral_centroid_hz",
                        {},
                    ).get("mean", 0.0)
                ),
                "aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio": float(
                    scalar_metrics.get(
                        "aligned_voicing_conditioned_unvoiced_minus_voiced_spectral_high_band_energy_ratio",
                        {},
                    ).get("mean", 0.0)
                ),
                "decoded_vs_aligned_unvoiced_minus_voiced_spectral_centroid_hz_gap": float(
                    scalar_metrics.get(
                        "voicing_controls_decoded_vs_aligned_unvoiced_minus_voiced_spectral_centroid_hz_gap",
                        {},
                    ).get("mean", 0.0)
                ),
                "decoded_vs_aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio_gap": float(
                    scalar_metrics.get(
                        "voicing_controls_decoded_vs_aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio_gap",
                        {},
                    ).get("mean", 0.0)
                ),
                "decoded_active_voiced_fraction": float(
                    scalar_metrics.get("decoded_voicing_conditioned_active_voiced_fraction", {}).get("mean", 0.0)
                ),
                "decoded_active_unvoiced_fraction": float(
                    scalar_metrics.get("decoded_voicing_conditioned_active_unvoiced_fraction", {}).get("mean", 0.0)
                ),
            }
        )
    order = {"baseline": 0, "waveform_decoder_base_logits_only": 1, "waveform_residual_shape_only": 2}
    return sorted(rows, key=lambda item: order.get(str(item["label"]), 999))


def build_baseline_upstream_coupling_localization_summary(
    aggregate_rows: list[dict[str, object]],
) -> dict[str, float | str]:
    baseline_row = next((row for row in aggregate_rows if str(row.get("label")) == "baseline"), None)
    if baseline_row is None:
        return {}
    scalar_metrics = dict(baseline_row.get("scalar_metrics", {}))

    def mean_metric(key: str) -> float:
        return float(scalar_metrics.get(key, {}).get("mean", 0.0))

    stages = (
        "fused_hidden_control_coupling",
        "decoder_hidden_control_coupling",
        "waveform_decoder_base_logits_control_coupling",
        "waveform_frames_control_coupling",
    )
    summary: dict[str, float | str] = {}
    for stage_name in stages:
        short = stage_name.replace("_control_coupling", "")
        summary[f"{short}_rms_to_voicing_corr"] = round(
            mean_metric(f"{stage_name}_active_frame_rms_to_voicing_corr"),
            6,
        )
        summary[f"{short}_rms_to_aper_corr"] = round(
            mean_metric(f"{stage_name}_active_frame_rms_to_aper_corr"),
            6,
        )
        summary[f"{short}_rms_to_energy_corr"] = round(
            mean_metric(f"{stage_name}_active_frame_rms_to_energy_corr"),
            6,
        )
        summary[f"{short}_rms_to_aper_energy_product_corr"] = round(
            mean_metric(f"{stage_name}_active_frame_rms_to_aper_energy_product_corr"),
            6,
        )
        summary[f"{short}_unvoiced_minus_voiced_frame_rms_mean"] = round(
            mean_metric(f"{stage_name}_unvoiced_minus_voiced_frame_rms_mean"),
            6,
        )

    fused_to_decoder_voicing_jump = round(
        float(summary["decoder_hidden_rms_to_voicing_corr"]) - float(summary["fused_hidden_rms_to_voicing_corr"]),
        6,
    )
    decoder_to_logits_voicing_jump = round(
        float(summary["waveform_decoder_base_logits_rms_to_voicing_corr"])
        - float(summary["decoder_hidden_rms_to_voicing_corr"]),
        6,
    )
    logits_to_frames_voicing_jump = round(
        float(summary["waveform_frames_rms_to_voicing_corr"])
        - float(summary["waveform_decoder_base_logits_rms_to_voicing_corr"]),
        6,
    )
    fused_to_decoder_aper_jump = round(
        abs(float(summary["decoder_hidden_rms_to_aper_corr"]))
        - abs(float(summary["fused_hidden_rms_to_aper_corr"])),
        6,
    )
    decoder_to_logits_aper_jump = round(
        abs(float(summary["waveform_decoder_base_logits_rms_to_aper_corr"]))
        - abs(float(summary["decoder_hidden_rms_to_aper_corr"])),
        6,
    )
    logits_to_frames_aper_jump = round(
        abs(float(summary["waveform_frames_rms_to_aper_corr"]))
        - abs(float(summary["waveform_decoder_base_logits_rms_to_aper_corr"])),
        6,
    )
    fused_to_decoder_aper_energy_product_jump = round(
        abs(float(summary["decoder_hidden_rms_to_aper_energy_product_corr"]))
        - abs(float(summary["fused_hidden_rms_to_aper_energy_product_corr"])),
        6,
    )
    decoder_to_logits_aper_energy_product_jump = round(
        abs(float(summary["waveform_decoder_base_logits_rms_to_aper_energy_product_corr"]))
        - abs(float(summary["decoder_hidden_rms_to_aper_energy_product_corr"])),
        6,
    )
    logits_to_frames_aper_energy_product_jump = round(
        abs(float(summary["waveform_frames_rms_to_aper_energy_product_corr"]))
        - abs(float(summary["waveform_decoder_base_logits_rms_to_aper_energy_product_corr"])),
        6,
    )
    fused_to_decoder_uv_v_rms_jump = round(
        float(summary["decoder_hidden_unvoiced_minus_voiced_frame_rms_mean"])
        - float(summary["fused_hidden_unvoiced_minus_voiced_frame_rms_mean"]),
        6,
    )
    decoder_to_logits_uv_v_rms_jump = round(
        float(summary["waveform_decoder_base_logits_unvoiced_minus_voiced_frame_rms_mean"])
        - float(summary["decoder_hidden_unvoiced_minus_voiced_frame_rms_mean"]),
        6,
    )
    logits_to_frames_uv_v_rms_jump = round(
        float(summary["waveform_frames_unvoiced_minus_voiced_frame_rms_mean"])
        - float(summary["waveform_decoder_base_logits_unvoiced_minus_voiced_frame_rms_mean"]),
        6,
    )
    summary.update(
        {
            "fused_to_decoder_voicing_corr_jump": fused_to_decoder_voicing_jump,
            "decoder_to_base_logits_voicing_corr_jump": decoder_to_logits_voicing_jump,
            "base_logits_to_frames_voicing_corr_jump": logits_to_frames_voicing_jump,
            "fused_to_decoder_abs_aper_corr_jump": fused_to_decoder_aper_jump,
            "decoder_to_base_logits_abs_aper_corr_jump": decoder_to_logits_aper_jump,
            "base_logits_to_frames_abs_aper_corr_jump": logits_to_frames_aper_jump,
            "fused_to_decoder_abs_aper_energy_product_corr_jump": fused_to_decoder_aper_energy_product_jump,
            "decoder_to_base_logits_abs_aper_energy_product_corr_jump": decoder_to_logits_aper_energy_product_jump,
            "base_logits_to_frames_abs_aper_energy_product_corr_jump": logits_to_frames_aper_energy_product_jump,
            "fused_to_decoder_uv_v_rms_jump": fused_to_decoder_uv_v_rms_jump,
            "decoder_to_base_logits_uv_v_rms_jump": decoder_to_logits_uv_v_rms_jump,
            "base_logits_to_frames_uv_v_rms_jump": logits_to_frames_uv_v_rms_jump,
        }
    )

    jump_candidates = {
        "fused_to_decoder": max(
            abs(fused_to_decoder_voicing_jump),
            abs(fused_to_decoder_aper_jump),
            abs(fused_to_decoder_aper_energy_product_jump),
            abs(fused_to_decoder_uv_v_rms_jump),
        ),
        "decoder_to_base_logits": max(
            abs(decoder_to_logits_voicing_jump),
            abs(decoder_to_logits_aper_jump),
            abs(decoder_to_logits_aper_energy_product_jump),
            abs(decoder_to_logits_uv_v_rms_jump),
        ),
        "base_logits_to_frames": max(
            abs(logits_to_frames_voicing_jump),
            abs(logits_to_frames_aper_jump),
            abs(logits_to_frames_aper_energy_product_jump),
            abs(logits_to_frames_uv_v_rms_jump),
        ),
    }
    strongest_transition = max(jump_candidates.items(), key=lambda item: item[1])
    summary["strongest_transition"] = str(strongest_transition[0])
    summary["strongest_transition_score"] = round(float(strongest_transition[1]), 6)
    if float(strongest_transition[1]) < 0.03:
        diagnosis = "no_clear_new_stagewise_coupling_jump"
    elif str(strongest_transition[0]) == "decoder_to_base_logits":
        diagnosis = "decoder_hidden_to_base_logits_is_main_coupling_amplifier"
    elif str(strongest_transition[0]) == "base_logits_to_frames":
        diagnosis = "base_logits_to_waveform_frames_is_main_coupling_amplifier"
    else:
        diagnosis = "fused_hidden_to_decoder_hidden_is_main_coupling_amplifier"
    summary["diagnosis"] = diagnosis
    return summary


def build_baseline_decoder_projection_geometry_summary(
    aggregate_rows: list[dict[str, object]],
) -> dict[str, float | str]:
    baseline_row = next((row for row in aggregate_rows if str(row.get("label")) == "baseline"), None)
    if baseline_row is None:
        return {}
    scalar_metrics = dict(baseline_row.get("scalar_metrics", {}))

    def mean_metric(key: str) -> float:
        return float(scalar_metrics.get(key, {}).get("mean", 0.0))

    stages = (
        "fused_hidden",
        "decoder_hidden",
        "waveform_decoder_base_logits",
        "waveform_frames",
    )
    summary: dict[str, float | str] = {}
    for stage in stages:
        summary[f"{stage}_effective_rank_fraction"] = round(
            mean_metric(f"{stage}_geometry_effective_rank_fraction"),
            6,
        )
        summary[f"{stage}_top1_variance_ratio"] = round(
            mean_metric(f"{stage}_geometry_top1_variance_ratio"),
            6,
        )
        summary[f"{stage}_top4_variance_ratio"] = round(
            mean_metric(f"{stage}_geometry_top4_variance_ratio"),
            6,
        )
        summary[f"{stage}_voiced_unvoiced_separation_ratio"] = round(
            mean_metric(f"{stage}_conditioned_clusters_voiced_unvoiced_separation_ratio"),
            6,
        )
        summary[f"{stage}_active_template_distance_mean"] = round(
            mean_metric(f"{stage}_conditioned_clusters_active_template_distance_mean"),
            6,
        )

    decoder_to_logits_rank_drop = round(
        float(summary["decoder_hidden_effective_rank_fraction"])
        - float(summary["waveform_decoder_base_logits_effective_rank_fraction"]),
        6,
    )
    decoder_to_logits_top1_jump = round(
        float(summary["waveform_decoder_base_logits_top1_variance_ratio"])
        - float(summary["decoder_hidden_top1_variance_ratio"]),
        6,
    )
    decoder_to_logits_sep_jump = round(
        float(summary["waveform_decoder_base_logits_voiced_unvoiced_separation_ratio"])
        - float(summary["decoder_hidden_voiced_unvoiced_separation_ratio"]),
        6,
    )
    decoder_to_logits_template_drop = round(
        float(summary["decoder_hidden_active_template_distance_mean"])
        - float(summary["waveform_decoder_base_logits_active_template_distance_mean"]),
        6,
    )
    logits_to_frames_rank_drop = round(
        float(summary["waveform_decoder_base_logits_effective_rank_fraction"])
        - float(summary["waveform_frames_effective_rank_fraction"]),
        6,
    )
    logits_to_frames_top1_jump = round(
        float(summary["waveform_frames_top1_variance_ratio"])
        - float(summary["waveform_decoder_base_logits_top1_variance_ratio"]),
        6,
    )
    logits_to_frames_sep_jump = round(
        float(summary["waveform_frames_voiced_unvoiced_separation_ratio"])
        - float(summary["waveform_decoder_base_logits_voiced_unvoiced_separation_ratio"]),
        6,
    )
    logits_to_frames_template_drop = round(
        float(summary["waveform_decoder_base_logits_active_template_distance_mean"])
        - float(summary["waveform_frames_active_template_distance_mean"]),
        6,
    )
    summary.update(
        {
            "decoder_to_base_logits_effective_rank_drop": decoder_to_logits_rank_drop,
            "decoder_to_base_logits_top1_variance_jump": decoder_to_logits_top1_jump,
            "decoder_to_base_logits_cluster_separation_jump": decoder_to_logits_sep_jump,
            "decoder_to_base_logits_template_distance_drop": decoder_to_logits_template_drop,
            "base_logits_to_frames_effective_rank_drop": logits_to_frames_rank_drop,
            "base_logits_to_frames_top1_variance_jump": logits_to_frames_top1_jump,
            "base_logits_to_frames_cluster_separation_jump": logits_to_frames_sep_jump,
            "base_logits_to_frames_template_distance_drop": logits_to_frames_template_drop,
        }
    )
    jump_candidates = {
        "decoder_to_base_logits": max(
            abs(decoder_to_logits_rank_drop),
            abs(decoder_to_logits_top1_jump),
            abs(decoder_to_logits_sep_jump),
            abs(decoder_to_logits_template_drop),
        ),
        "base_logits_to_frames": max(
            abs(logits_to_frames_rank_drop),
            abs(logits_to_frames_top1_jump),
            abs(logits_to_frames_sep_jump),
            abs(logits_to_frames_template_drop),
        ),
    }
    strongest_transition = max(jump_candidates.items(), key=lambda item: item[1])
    summary["strongest_transition"] = str(strongest_transition[0])
    summary["strongest_transition_score"] = round(float(strongest_transition[1]), 6)
    if float(strongest_transition[1]) < 0.03:
        diagnosis = "no_clear_projection_geometry_jump"
    elif str(strongest_transition[0]) == "decoder_to_base_logits":
        diagnosis = "decoder_hidden_to_base_logits_is_main_geometry_collapse"
    else:
        diagnosis = "base_logits_to_frames_is_main_geometry_collapse"
    summary["diagnosis"] = diagnosis
    return summary


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Waveform Decoder Structure Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- decode_runtime: {json.dumps(summary['decode_runtime'], ensure_ascii=False)}",
        f"- baseline_decoder_collapse_summary: {json.dumps(summary['baseline_decoder_collapse_summary'], ensure_ascii=False)}",
        f"- baseline_upstream_coupling_localization_summary: {json.dumps(summary.get('baseline_upstream_coupling_localization_summary', {}), ensure_ascii=False)}",
        f"- baseline_decoder_projection_geometry_summary: {json.dumps(summary.get('baseline_decoder_projection_geometry_summary', {}), ensure_ascii=False)}",
        "",
        "## Voicing-Conditioned Shape Summary",
    ]
    for item in list(summary.get("voicing_conditioned_shape_summary", [])):
        lines.append(
            "- "
            f"{item['label']}: "
            f"decoded_uv_minus_v_centroid={item['decoded_unvoiced_minus_voiced_spectral_centroid_hz']:.6f}, "
            f"decoded_uv_minus_v_high_band={item['decoded_unvoiced_minus_voiced_spectral_high_band_energy_ratio']:.6f}, "
            f"aligned_uv_minus_v_centroid={item['aligned_unvoiced_minus_voiced_spectral_centroid_hz']:.6f}, "
            f"aligned_uv_minus_v_high_band={item['aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio']:.6f}, "
            f"decoded_vs_aligned_centroid_gap={item['decoded_vs_aligned_unvoiced_minus_voiced_spectral_centroid_hz_gap']:.6f}, "
            f"decoded_vs_aligned_high_band_gap={item['decoded_vs_aligned_unvoiced_minus_voiced_spectral_high_band_energy_ratio_gap']:.6f}"
        )
    lines.extend(
        [
            "",
        "## Variant Impact Ranking",
        ]
    )
    for item in list(summary.get("variant_impact_ranking", [])):
        lines.append(
            "- "
            f"{item['label']}: "
            f"waveform_mean_abs_delta_vs_baseline={item['mean_waveform_mean_abs_delta_vs_baseline']:.6f}, "
            f"fused_to_waveform_template_gap={item['mean_fused_to_waveform_template_cosine_gap']:.6f}, "
            f"fused_to_waveform_adjacent_gap={item['mean_fused_to_waveform_adjacent_cosine_gap']:.6f}, "
            f"waveform_template={item['mean_waveform_frames_template_cosine_mean']:.6f}, "
            f"decoded_template={item['mean_decoded_frame_template_cosine_mean']:.6f}"
        )
    lines.extend(["", "## Variant Aggregates"])
    for item in list(summary.get("variant_aggregates", [])):
        scalar_metrics = dict(item.get("scalar_metrics", {}))
        delta_vs_baseline = dict(item.get("delta_vs_baseline", {}))
        lines.append(
            "- "
            f"{item['label']}: "
            f"record_count={item['record_count']}, "
            f"waveform_delta={delta_vs_baseline.get('waveform_mean_abs_delta_vs_baseline', {}).get('mean', 0.0)}, "
            f"fused_template={scalar_metrics.get('fused_hidden_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"waveform_template={scalar_metrics.get('waveform_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"decoded_template={scalar_metrics.get('decoded_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"fused_adjacent={scalar_metrics.get('fused_hidden_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"waveform_adjacent={scalar_metrics.get('waveform_frames_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"decoded_adjacent={scalar_metrics.get('decoded_frames_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"fused_to_waveform_template_gap={scalar_metrics.get('fused_to_waveform_template_cosine_gap', {}).get('mean', 0.0)}, "
            f"fused_to_waveform_adjacent_gap={scalar_metrics.get('fused_to_waveform_adjacent_cosine_gap', {}).get('mean', 0.0)}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
