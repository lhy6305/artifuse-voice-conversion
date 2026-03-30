from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import torch

from v5vc.streaming_student.rmvpe_inference import (
    extract_rmvpe_confidence_pitch_provider_tensors,
    extract_rmvpe_pitch_provider_tensors,
    extract_rmvpe_split_confidence_pitch_provider_tensors,
)


DEFAULT_STAGE3_PITCH_PROVIDER_MODE = "none"
DEFAULT_STAGE3_PITCH_PROVIDER_CACHE_DIR = Path("tmp/streaming_student_pitch_provider_cache")
DEFAULT_STAGE3_PITCH_PROVIDER_VOICING_THRESHOLD = 0.03


def normalize_stage3_pitch_provider_mode(value: object) -> str:
    normalized = str(
        DEFAULT_STAGE3_PITCH_PROVIDER_MODE if value in {None, ""} else value
    ).strip().lower()
    if normalized not in {
        "none",
        "deterministic_extractor_v1",
        "rmvpe_v1",
        "rmvpe_confidence_v1",
        "rmvpe_split_confidence_v1",
    }:
        raise ValueError(
            "Stage3 pitch_provider_mode must be one of: "
            "none, deterministic_extractor_v1, rmvpe_v1, rmvpe_confidence_v1, "
            "rmvpe_split_confidence_v1."
        )
    return normalized


def stage3_pitch_provider_requires_explicit_inputs(value: object) -> bool:
    return normalize_stage3_pitch_provider_mode(value) != DEFAULT_STAGE3_PITCH_PROVIDER_MODE


def resolve_stage3_pitch_provider_request(
    model_config: Mapping[str, object],
    *,
    config_path: Path | None = None,
) -> dict[str, object]:
    mode = normalize_stage3_pitch_provider_mode(model_config.get("pitch_provider_mode"))
    request: dict[str, object] = {"mode": mode}
    if mode == DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
        return request
    if mode == "deterministic_extractor_v1":
        return request
    root_dir = Path.cwd() if config_path is None else config_path.parent.parent.resolve()
    raw_model_path = model_config.get("pitch_provider_model_path")
    if raw_model_path in {None, ""}:
        raise ValueError(f"{mode} requires model.pitch_provider_model_path.")
    model_path = Path(str(raw_model_path))
    if not model_path.is_absolute():
        model_path = (root_dir / model_path).resolve()
    raw_cache_dir = model_config.get("pitch_provider_cache_dir")
    cache_dir = (
        DEFAULT_STAGE3_PITCH_PROVIDER_CACHE_DIR / mode
        if raw_cache_dir in {None, ""}
        else Path(str(raw_cache_dir))
    )
    if not cache_dir.is_absolute():
        cache_dir = (root_dir / cache_dir).resolve()
    request["model_path"] = model_path
    request["cache_dir"] = cache_dir
    request["voicing_threshold"] = float(
        model_config.get(
            "pitch_provider_voicing_threshold",
            DEFAULT_STAGE3_PITCH_PROVIDER_VOICING_THRESHOLD,
        )
    )
    return request


def build_stage3_pitch_provider_tensors(
    *,
    target_f0_hz: torch.Tensor,
    target_vuv: torch.Tensor,
    target_confidence: torch.Tensor | None = None,
) -> dict[str, torch.Tensor]:
    if not isinstance(target_f0_hz, torch.Tensor):
        raise ValueError("target_f0_hz must be a torch.Tensor.")
    if not isinstance(target_vuv, torch.Tensor):
        raise ValueError("target_vuv must be a torch.Tensor.")
    resolved_f0_hz = target_f0_hz.to(torch.float32).clamp_min(0.0)
    resolved_vuv = target_vuv.to(torch.float32).clamp(0.0, 1.0)
    log2_f0 = torch.zeros_like(resolved_f0_hz, dtype=torch.float32)
    voiced_mask = resolved_f0_hz > 0.0
    if bool(voiced_mask.any().item()):
        log2_f0 = torch.where(
            voiced_mask,
            torch.log2(resolved_f0_hz.clamp_min(1.0)),
            log2_f0,
        )
    provider_tensors = {
        "pitch_provider_f0_hz": resolved_f0_hz,
        "pitch_provider_log2_f0": log2_f0,
        "pitch_provider_vuv": resolved_vuv,
    }
    if isinstance(target_confidence, torch.Tensor):
        provider_tensors["pitch_provider_confidence"] = (
            target_confidence.to(torch.float32).clamp(0.0, 1.0)
        )
    return provider_tensors


def compute_stage3_pitch_provider_tensors_for_example(
    *,
    pitch_provider_request: Mapping[str, object] | None,
    record_id: str,
    audio_path: Path,
    waveform: torch.Tensor,
    sample_rate: int,
    frame_start_samples: torch.Tensor,
    target_f0_hz: torch.Tensor | None,
    target_vuv: torch.Tensor | None,
) -> dict[str, torch.Tensor] | None:
    if pitch_provider_request is None:
        return None
    mode = normalize_stage3_pitch_provider_mode(pitch_provider_request.get("mode"))
    if mode == DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
        return None
    if mode == "deterministic_extractor_v1":
        if not isinstance(target_f0_hz, torch.Tensor) or not isinstance(target_vuv, torch.Tensor):
            raise ValueError(
                "deterministic_extractor_v1 requires target_f0_hz and target_vuv tensors."
            )
        return build_stage3_pitch_provider_tensors(
            target_f0_hz=target_f0_hz,
            target_vuv=target_vuv,
        )
    if mode == "rmvpe_v1":
        model_path = pitch_provider_request.get("model_path")
        cache_dir = pitch_provider_request.get("cache_dir")
        if not isinstance(model_path, Path):
            raise ValueError("rmvpe_v1 requires a resolved Path model_path in pitch_provider_request.")
        if not isinstance(cache_dir, Path):
            raise ValueError("rmvpe_v1 requires a resolved Path cache_dir in pitch_provider_request.")
        return extract_rmvpe_pitch_provider_tensors(
            record_id=record_id,
            audio_path=audio_path,
            waveform=waveform,
            sample_rate=sample_rate,
            frame_start_samples=frame_start_samples,
            model_path=model_path,
            cache_dir=cache_dir,
            voicing_threshold=float(pitch_provider_request.get("voicing_threshold", 0.03)),
        )
    if mode == "rmvpe_confidence_v1":
        model_path = pitch_provider_request.get("model_path")
        cache_dir = pitch_provider_request.get("cache_dir")
        if not isinstance(model_path, Path):
            raise ValueError("rmvpe_confidence_v1 requires a resolved Path model_path in pitch_provider_request.")
        if not isinstance(cache_dir, Path):
            raise ValueError("rmvpe_confidence_v1 requires a resolved Path cache_dir in pitch_provider_request.")
        return extract_rmvpe_confidence_pitch_provider_tensors(
            record_id=record_id,
            audio_path=audio_path,
            waveform=waveform,
            sample_rate=sample_rate,
            frame_start_samples=frame_start_samples,
            model_path=model_path,
            cache_dir=cache_dir,
        )
    if mode == "rmvpe_split_confidence_v1":
        model_path = pitch_provider_request.get("model_path")
        cache_dir = pitch_provider_request.get("cache_dir")
        if not isinstance(model_path, Path):
            raise ValueError(
                "rmvpe_split_confidence_v1 requires a resolved Path model_path in pitch_provider_request."
            )
        if not isinstance(cache_dir, Path):
            raise ValueError(
                "rmvpe_split_confidence_v1 requires a resolved Path cache_dir in pitch_provider_request."
            )
        return extract_rmvpe_split_confidence_pitch_provider_tensors(
            record_id=record_id,
            audio_path=audio_path,
            waveform=waveform,
            sample_rate=sample_rate,
            frame_start_samples=frame_start_samples,
            model_path=model_path,
            cache_dir=cache_dir,
            voicing_threshold=float(pitch_provider_request.get("voicing_threshold", 0.03)),
        )
    raise ValueError(f"Unsupported Stage3 pitch_provider_request mode: {mode}")


def build_stage3_pitch_provider_tensors_from_batch(
    batch: Mapping[str, object],
    *,
    pitch_provider_mode: object,
) -> dict[str, torch.Tensor] | None:
    if not stage3_pitch_provider_requires_explicit_inputs(pitch_provider_mode):
        return None
    pitch_provider_f0_hz = batch.get("pitch_provider_f0_hz")
    pitch_provider_log2_f0 = batch.get("pitch_provider_log2_f0")
    pitch_provider_vuv = batch.get("pitch_provider_vuv")
    pitch_provider_confidence = batch.get("pitch_provider_confidence")
    pitch_provider_available = batch.get("pitch_provider_available")
    mode = normalize_stage3_pitch_provider_mode(pitch_provider_mode)
    if not isinstance(pitch_provider_f0_hz, torch.Tensor):
        raise ValueError("Stage3 pitch provider requires batch tensor pitch_provider_f0_hz.")
    if not isinstance(pitch_provider_log2_f0, torch.Tensor):
        raise ValueError("Stage3 pitch provider requires batch tensor pitch_provider_log2_f0.")
    if not isinstance(pitch_provider_vuv, torch.Tensor):
        raise ValueError("Stage3 pitch provider requires batch tensor pitch_provider_vuv.")
    if not isinstance(pitch_provider_available, torch.Tensor):
        raise ValueError("Stage3 pitch provider requires batch tensor pitch_provider_available.")
    if not bool(pitch_provider_available.to(torch.bool).all().item()):
        raise ValueError("Stage3 pitch provider batch contains unpopulated explicit provider tensors.")
    resolved = {
        "pitch_provider_f0_hz": pitch_provider_f0_hz.to(torch.float32),
        "pitch_provider_log2_f0": pitch_provider_log2_f0.to(torch.float32),
        "pitch_provider_vuv": pitch_provider_vuv.to(torch.float32),
    }
    if mode == "rmvpe_split_confidence_v1":
        if not isinstance(pitch_provider_confidence, torch.Tensor):
            raise ValueError(
                "rmvpe_split_confidence_v1 requires batch tensor pitch_provider_confidence."
            )
        resolved["pitch_provider_confidence"] = pitch_provider_confidence.to(torch.float32)
    elif isinstance(pitch_provider_confidence, torch.Tensor):
        resolved["pitch_provider_confidence"] = pitch_provider_confidence.to(torch.float32)
    return resolved


def compute_stage3_frame_lengths(
    audio_lengths: torch.Tensor,
    *,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    if not isinstance(audio_lengths, torch.Tensor):
        raise ValueError("audio_lengths must be a torch.Tensor.")
    if audio_lengths.ndim != 1:
        raise ValueError(f"Expected audio_lengths shape [B], got {tuple(audio_lengths.shape)}")
    return ((audio_lengths.to(torch.long) - int(frame_length)).clamp_min(0) // int(hop_length)) + 1


def align_stage3_pitch_provider_tensors_to_audio_lengths(
    pitch_provider_tensors: dict[str, torch.Tensor] | None,
    *,
    audio_lengths: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> dict[str, torch.Tensor] | None:
    if pitch_provider_tensors is None:
        return None
    frame_lengths = compute_stage3_frame_lengths(
        audio_lengths,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    max_frames = int(frame_lengths.max().item())
    frame_mask = (
        torch.arange(max_frames, device=frame_lengths.device)[None, :]
        < frame_lengths[:, None]
    )
    aligned: dict[str, torch.Tensor] = {}
    for key, value in pitch_provider_tensors.items():
        if not isinstance(value, torch.Tensor):
            raise ValueError(f"pitch_provider_tensors[{key!r}] must be a torch.Tensor.")
        if value.shape[0] != frame_lengths.shape[0]:
            raise ValueError(
                f"pitch_provider_tensors[{key!r}] batch mismatch: "
                f"{value.shape[0]} vs {frame_lengths.shape[0]}"
            )
        if value.shape[1] < max_frames:
            raise ValueError(
                f"pitch_provider_tensors[{key!r}] frame_count too small: "
                f"{value.shape[1]} < required {max_frames}"
            )
        cropped = value[:, :max_frames].clone()
        if cropped.ndim == 3:
            cropped = cropped * frame_mask.unsqueeze(-1).to(device=cropped.device, dtype=cropped.dtype)
        elif cropped.ndim == 2:
            cropped = cropped * frame_mask.to(device=cropped.device, dtype=cropped.dtype)
        aligned[key] = cropped
    return aligned


def build_stage3_pitch_provider_model_inputs_from_batch(
    batch: Mapping[str, object],
    *,
    pitch_provider_mode: object,
    audio_lengths: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> dict[str, torch.Tensor | None]:
    pitch_provider_tensors = build_stage3_pitch_provider_tensors_from_batch(
        batch,
        pitch_provider_mode=pitch_provider_mode,
    )
    aligned_tensors = align_stage3_pitch_provider_tensors_to_audio_lengths(
        pitch_provider_tensors,
        audio_lengths=audio_lengths,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    if aligned_tensors is None:
        return {
            "pitch_provider_log2_f0": None,
            "pitch_provider_vuv": None,
            "pitch_provider_confidence": None,
        }
    return {
        "pitch_provider_log2_f0": aligned_tensors["pitch_provider_log2_f0"],
        "pitch_provider_vuv": aligned_tensors["pitch_provider_vuv"],
        "pitch_provider_confidence": aligned_tensors.get("pitch_provider_confidence"),
    }


def probability_to_logits(probability: torch.Tensor) -> torch.Tensor:
    clipped = probability.to(torch.float32).clamp(1.0e-4, 1.0 - 1.0e-4)
    return torch.log(clipped) - torch.log1p(-clipped)
