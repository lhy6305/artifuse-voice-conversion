from __future__ import annotations

import torch
import torch.nn.functional as F

from v5vc.source_acoustic_state_extraction import slice_aligned_frames


FINE_STRUCTURE_REFERENCE_LOGSPEC_BINS = 48
FINE_STRUCTURE_WAVEFORM_PCA_CODEBOOK_VERSION = "streaming_student_waveform_pca_codebook_v1"


def build_fine_structure_reference(
    *,
    waveform: torch.Tensor,
    frame_start_samples: torch.Tensor,
    frame_length: int,
    logspec_bins: int = FINE_STRUCTURE_REFERENCE_LOGSPEC_BINS,
) -> dict[str, torch.Tensor]:
    aligned_frames = slice_aligned_frames(
        waveform=waveform,
        frame_start_samples=frame_start_samples,
        frame_length=int(frame_length),
    )
    normalized_frames = normalize_frames_unit_rms(aligned_frames)
    unit_rms_logspec = compress_logspec_bins(
        compute_frame_logspec(normalized_frames),
        output_bins=int(logspec_bins),
    )
    return {
        "unit_rms_waveform_frame": normalized_frames,
        "unit_rms_logspec": unit_rms_logspec,
        "unit_rms_logspec_delta": compute_adjacent_deltas(unit_rms_logspec),
    }


def build_batched_unit_rms_waveform_frames(
    *,
    waveform_batch: torch.Tensor,
    frame_lengths: torch.Tensor,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    batch_waveform = waveform_batch.detach().to(torch.float32)
    batch_frame_lengths = frame_lengths.detach().to(torch.long)
    batch_size = int(batch_waveform.shape[0])
    max_frames = int(batch_frame_lengths.max().item()) if batch_size > 0 else 0
    target = batch_waveform.new_zeros((batch_size, max_frames, int(frame_length)))
    for index in range(batch_size):
        valid_frames = int(batch_frame_lengths[index].item())
        if valid_frames <= 0:
            continue
        frame_start_samples = (
            torch.arange(valid_frames, dtype=torch.long, device=batch_waveform.device) * int(hop_length)
        )
        frames = slice_aligned_frames(
            waveform=batch_waveform[index],
            frame_start_samples=frame_start_samples,
            frame_length=int(frame_length),
        )
        target[index, :valid_frames] = normalize_frames_unit_rms(frames)
    return target


def normalize_frames_unit_rms(frames: torch.Tensor) -> torch.Tensor:
    frames_fp32 = frames.detach().to(torch.float32)
    if int(frames_fp32.shape[0]) <= 0:
        return frames_fp32
    centered = frames_fp32 - frames_fp32.mean(dim=1, keepdim=True)
    frame_rms = centered.pow(2).mean(dim=1, keepdim=True).sqrt().clamp_min(1.0e-6)
    return centered / frame_rms


def compute_frame_logspec(frames: torch.Tensor) -> torch.Tensor:
    frames_fp32 = frames.detach().to(torch.float32)
    spectrum = torch.fft.rfft(frames_fp32, dim=1)
    return torch.log1p(spectrum.abs())


def compress_logspec_bins(logspec: torch.Tensor, *, output_bins: int) -> torch.Tensor:
    logspec_fp32 = logspec.detach().to(torch.float32)
    if int(logspec_fp32.shape[-1]) == int(output_bins):
        return logspec_fp32.contiguous()
    return F.adaptive_avg_pool1d(logspec_fp32.unsqueeze(1), int(output_bins)).squeeze(1).contiguous()


def compute_adjacent_deltas(sequence: torch.Tensor) -> torch.Tensor:
    sequence_fp32 = sequence.detach().to(torch.float32)
    if int(sequence_fp32.shape[0]) <= 0:
        return sequence_fp32
    deltas = torch.zeros_like(sequence_fp32)
    if int(sequence_fp32.shape[0]) > 1:
        deltas[1:] = sequence_fp32[1:] - sequence_fp32[:-1]
    return deltas.contiguous()


def build_temporal_chunk_vectors(sequence: torch.Tensor, *, radius: int) -> torch.Tensor:
    sequence_fp32 = sequence.detach().to(torch.float32)
    resolved_radius = max(0, int(radius))
    if resolved_radius <= 0:
        return sequence_fp32.contiguous()
    squeeze_batch = False
    if sequence_fp32.ndim == 2:
        sequence_fp32 = sequence_fp32.unsqueeze(0)
        squeeze_batch = True
    if sequence_fp32.ndim != 3:
        raise ValueError("build_temporal_chunk_vectors expects a 2D or 3D tensor.")
    batch_size, frame_count, feature_dim = sequence_fp32.shape
    if frame_count <= 0:
        return sequence_fp32.squeeze(0) if squeeze_batch else sequence_fp32
    padded = F.pad(
        sequence_fp32.transpose(1, 2),
        (resolved_radius, resolved_radius),
        mode="replicate",
    ).transpose(1, 2)
    chunks = [
        padded[:, offset : offset + frame_count, :]
        for offset in range(2 * resolved_radius + 1)
    ]
    chunked = torch.cat(chunks, dim=-1).contiguous()
    if squeeze_batch:
        return chunked.squeeze(0)
    return chunked


def fit_waveform_pca_codebook(*, waveform_frames: torch.Tensor, code_dim: int) -> dict[str, object]:
    frames = waveform_frames.detach().cpu().to(torch.float32)
    mean = frames.mean(dim=0, keepdim=True)
    centered = frames - mean
    max_rank = min(int(centered.shape[0]), int(centered.shape[1]), max(1, int(code_dim)))
    _, singular_values, vh = torch.linalg.svd(centered, full_matrices=False)
    components = vh[:max_rank].transpose(0, 1).contiguous()
    total_variance = float(singular_values.pow(2).sum().item())
    retained_variance = float(singular_values[:max_rank].pow(2).sum().item())
    explained_variance_ratio = 0.0 if total_variance <= 1.0e-8 else retained_variance / total_variance
    projected = centered @ components
    code_std = projected.std(dim=0, unbiased=False).clamp_min(1.0e-4)
    return {
        "codebook_version": FINE_STRUCTURE_WAVEFORM_PCA_CODEBOOK_VERSION,
        "fit_frame_count": int(frames.shape[0]),
        "input_waveform_dim": int(frames.shape[1]),
        "mean": mean,
        "components": components,
        "code_std": code_std,
        "explained_variance_ratio": round(float(explained_variance_ratio), 6),
    }


def project_waveform_pca_code(
    *,
    waveform_reference: torch.Tensor,
    codebook: dict[str, object],
    normalize_code: bool = False,
) -> torch.Tensor:
    waveform = waveform_reference.detach().to(torch.float32)
    mean = codebook["mean"].to(device=waveform.device, dtype=waveform.dtype)
    components = codebook["components"].to(device=waveform.device, dtype=waveform.dtype)
    projected = (waveform - mean) @ components
    if not normalize_code:
        return projected
    code_std = codebook["code_std"].to(device=projected.device, dtype=projected.dtype)
    return projected / code_std


def decode_waveform_pca_code(
    *,
    waveform_code: torch.Tensor,
    codebook: dict[str, object],
    normalized_code: bool = False,
) -> torch.Tensor:
    code = waveform_code.detach().to(torch.float32)
    mean = codebook["mean"].to(device=code.device, dtype=code.dtype)
    components = codebook["components"].to(device=code.device, dtype=code.dtype)
    if normalized_code:
        code_std = codebook["code_std"].to(device=code.device, dtype=code.dtype)
        code = code * code_std
    return code @ components.transpose(0, 1) + mean
