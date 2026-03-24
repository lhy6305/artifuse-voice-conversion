from __future__ import annotations

import math

import torch
import torch.nn.functional as F


SOURCE_ACOUSTIC_STATE_EXTRACTION_VERSION = "source_acoustic_state_extraction_v1"
APERIODICITY_VERSION = "aper-v1"
DEFAULT_F0_FLOOR_HZ = 50.0
DEFAULT_F0_CEIL_HZ = 550.0
DEFAULT_VUV_VOICED_FRAME_THRESHOLD = 0.2
DEFAULT_ANALYSIS_PERIOD_COUNT = 3.0
DEFAULT_ANALYSIS_WINDOW_MULTIPLIER = 6


def extract_source_acoustic_state(
    waveform: torch.Tensor,
    sample_rate: int,
    frame_start_samples: torch.Tensor,
    frame_length: int,
    *,
    f0_floor_hz: float = DEFAULT_F0_FLOOR_HZ,
    f0_ceil_hz: float = DEFAULT_F0_CEIL_HZ,
) -> dict[str, object]:
    frames = slice_aligned_frames(
        waveform=waveform,
        frame_start_samples=frame_start_samples,
        frame_length=frame_length,
    )
    if frames.numel() == 0:
        empty = torch.zeros((0, 1), dtype=torch.float32)
        return {
            "version": SOURCE_ACOUSTIC_STATE_EXTRACTION_VERSION,
            "aper_version": APERIODICITY_VERSION,
            "f0_hz": empty,
            "vuv": empty,
            "aper": empty,
            "E": empty,
            "stats": {
                "frame_count": 0,
                "voiced_frame_count": 0,
                "voiced_ratio": 0.0,
                "f0_floor_hz": float(f0_floor_hz),
                "f0_ceil_hz": float(f0_ceil_hz),
                "analysis_frame_length": int(frame_length),
            },
        }

    analysis_frame_length = resolve_analysis_frame_length(
        sample_rate=int(sample_rate),
        frame_length=int(frame_length),
        f0_floor_hz=float(f0_floor_hz),
    )
    analysis_frames = slice_centered_analysis_frames(
        waveform=waveform,
        frame_start_samples=frame_start_samples,
        frame_length=frame_length,
        analysis_frame_length=analysis_frame_length,
    )
    analysis_window = torch.hann_window(analysis_frame_length, periodic=False, dtype=torch.float32)
    windowed_analysis_frames = analysis_frames * analysis_window.view(1, -1)
    centered_analysis_frames = windowed_analysis_frames - windowed_analysis_frames.mean(dim=-1, keepdim=True)
    rms = torch.sqrt(frames.pow(2).mean(dim=-1).clamp_min(1.0e-8))
    energy_control = torch.log10(rms.clamp_min(1.0e-8)).unsqueeze(-1)

    f0_hz, vuv = estimate_f0_and_vuv(
        frames=centered_analysis_frames,
        sample_rate=int(sample_rate),
        f0_floor_hz=float(f0_floor_hz),
        f0_ceil_hz=float(f0_ceil_hz),
        energy_control=energy_control.squeeze(-1),
    )
    aper = estimate_aperiodicity(
        frames=windowed_analysis_frames,
        sample_rate=int(sample_rate),
        f0_hz=f0_hz.squeeze(-1),
        vuv=vuv.squeeze(-1),
    )
    voiced_mask = vuv.squeeze(-1) >= DEFAULT_VUV_VOICED_FRAME_THRESHOLD
    f0_hz = torch.where(voiced_mask.unsqueeze(-1), f0_hz, torch.zeros_like(f0_hz))
    aper = torch.where(voiced_mask.unsqueeze(-1), aper, torch.ones_like(aper))

    voiced_frame_count = int(voiced_mask.sum().item())
    return {
        "version": SOURCE_ACOUSTIC_STATE_EXTRACTION_VERSION,
        "aper_version": APERIODICITY_VERSION,
        "f0_hz": f0_hz.to(torch.float32),
        "vuv": vuv.to(torch.float32),
        "aper": aper.to(torch.float32),
        "E": energy_control.to(torch.float32),
        "stats": {
            "frame_count": int(frames.shape[0]),
            "voiced_frame_count": voiced_frame_count,
            "voiced_ratio": round(voiced_frame_count / max(1, int(frames.shape[0])), 6),
            "f0_floor_hz": float(f0_floor_hz),
            "f0_ceil_hz": float(f0_ceil_hz),
            "analysis_frame_length": int(analysis_frame_length),
        },
    }


def slice_aligned_frames(
    waveform: torch.Tensor,
    frame_start_samples: torch.Tensor,
    frame_length: int,
) -> torch.Tensor:
    waveform_1d = waveform.detach().to(torch.float32).cpu().view(-1)
    starts = frame_start_samples.detach().to(torch.long).cpu().view(-1)
    if starts.numel() == 0:
        return torch.zeros((0, frame_length), dtype=torch.float32)
    frames: list[torch.Tensor] = []
    for start in starts.tolist():
        resolved_start = max(0, int(start))
        end = resolved_start + int(frame_length)
        frame = waveform_1d[resolved_start:end]
        if frame.numel() < int(frame_length):
            frame = F.pad(frame, (0, int(frame_length) - int(frame.numel())))
        frames.append(frame)
    return torch.stack(frames, dim=0)


def slice_centered_analysis_frames(
    waveform: torch.Tensor,
    frame_start_samples: torch.Tensor,
    frame_length: int,
    analysis_frame_length: int,
) -> torch.Tensor:
    waveform_1d = waveform.detach().to(torch.float32).cpu().view(-1)
    starts = frame_start_samples.detach().to(torch.long).cpu().view(-1)
    if starts.numel() == 0:
        return torch.zeros((0, analysis_frame_length), dtype=torch.float32)
    half_width = int(analysis_frame_length // 2)
    center_offset = int(frame_length // 2)
    frames: list[torch.Tensor] = []
    for start in starts.tolist():
        center = int(start) + center_offset
        analysis_start = center - half_width
        analysis_end = analysis_start + int(analysis_frame_length)
        padded_start = max(0, analysis_start)
        padded_end = min(int(waveform_1d.numel()), analysis_end)
        frame = waveform_1d[padded_start:padded_end]
        pad_left = max(0, -analysis_start)
        pad_right = max(0, analysis_end - int(waveform_1d.numel()))
        if pad_left > 0 or pad_right > 0:
            frame = F.pad(frame, (pad_left, pad_right))
        if frame.numel() != int(analysis_frame_length):
            frame = F.pad(frame, (0, int(analysis_frame_length) - int(frame.numel())))
        frames.append(frame)
    return torch.stack(frames, dim=0)


def resolve_analysis_frame_length(
    sample_rate: int,
    frame_length: int,
    f0_floor_hz: float,
) -> int:
    min_period_samples = int(math.ceil(float(sample_rate) / max(float(f0_floor_hz), 1.0)))
    analysis_frame_length = max(
        int(frame_length) * DEFAULT_ANALYSIS_WINDOW_MULTIPLIER,
        int(math.ceil(min_period_samples * DEFAULT_ANALYSIS_PERIOD_COUNT)),
    )
    if analysis_frame_length % 2 != 0:
        analysis_frame_length += 1
    return max(int(frame_length), analysis_frame_length)


def estimate_f0_and_vuv(
    frames: torch.Tensor,
    sample_rate: int,
    f0_floor_hz: float,
    f0_ceil_hz: float,
    energy_control: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    frame_length = int(frames.shape[-1])
    lag_min = max(1, int(math.floor(sample_rate / max(f0_ceil_hz, 1.0))))
    lag_max = min(frame_length - 1, int(math.ceil(sample_rate / max(f0_floor_hz, 1.0))))
    if lag_max <= lag_min:
        zero = torch.zeros((frames.shape[0], 1), dtype=torch.float32)
        return zero, zero

    fft_size = 1
    while fft_size < frame_length * 2:
        fft_size *= 2
    spectrum = torch.fft.rfft(frames, n=fft_size)
    autocorr = torch.fft.irfft(spectrum * spectrum.conj(), n=fft_size)[..., : lag_max + 1]
    autocorr0 = autocorr[:, :1].clamp_min(1.0e-6)
    normalized = autocorr / autocorr0
    search = normalized[:, lag_min : lag_max + 1]
    lag_values = torch.arange(lag_min, lag_max + 1, dtype=torch.float32).view(1, -1)
    peak_values, peak_indices = search.max(dim=-1)
    near_peak_mask = search >= (peak_values.unsqueeze(-1) * 0.93)
    longest_near_peak_lags = torch.where(
        near_peak_mask,
        lag_values.expand(search.shape[0], -1),
        torch.zeros_like(search),
    ).max(dim=-1).values.to(torch.long)
    best_lags = torch.where(
        longest_near_peak_lags > 0,
        longest_near_peak_lags,
        peak_indices + lag_min,
    )
    f0_hz = (float(sample_rate) / best_lags.to(torch.float32).clamp_min(1.0)).unsqueeze(-1)

    periodicity = ((peak_values - 0.25) / 0.55).clamp(0.0, 1.0)
    energy_norm = ((energy_control.to(torch.float32) + 4.5) / 4.5).clamp(0.0, 1.0)
    vuv = (0.7 * periodicity + 0.3 * energy_norm).clamp(0.0, 1.0).unsqueeze(-1)
    return f0_hz, vuv


def estimate_aperiodicity(
    frames: torch.Tensor,
    sample_rate: int,
    f0_hz: torch.Tensor,
    vuv: torch.Tensor,
) -> torch.Tensor:
    if frames.numel() == 0:
        return torch.zeros((0, 1), dtype=torch.float32)
    spectrum = torch.fft.rfft(frames, dim=-1)
    power = spectrum.abs().pow(2)
    total_energy = power.sum(dim=-1).clamp_min(1.0e-8)
    freq_resolution = float(sample_rate) / float(frames.shape[-1])
    nyquist_hz = float(sample_rate) * 0.5
    aper_values = torch.ones((frames.shape[0],), dtype=torch.float32)

    for frame_index in range(frames.shape[0]):
        if float(vuv[frame_index].item()) < DEFAULT_VUV_VOICED_FRAME_THRESHOLD:
            continue
        resolved_f0 = float(f0_hz[frame_index].item())
        if resolved_f0 <= 0.0:
            continue
        harmonic_mask = torch.zeros((power.shape[-1],), dtype=torch.bool)
        max_harmonic = max(1, int(nyquist_hz // resolved_f0))
        half_width_hz = max(30.0, min(90.0, resolved_f0 * 0.2))
        half_width_bins = max(1, int(round(half_width_hz / max(freq_resolution, 1.0e-6))))
        for harmonic_index in range(1, max_harmonic + 1):
            harmonic_hz = harmonic_index * resolved_f0
            center_bin = int(round(harmonic_hz / max(freq_resolution, 1.0e-6)))
            if center_bin >= power.shape[-1]:
                break
            start = max(0, center_bin - half_width_bins)
            end = min(power.shape[-1], center_bin + half_width_bins + 1)
            harmonic_mask[start:end] = True
        harmonic_energy = power[frame_index, harmonic_mask].sum()
        aper_values[frame_index] = (
            1.0 - (harmonic_energy / total_energy[frame_index]).clamp(0.0, 1.0)
        ).to(torch.float32)

    smoothed = F.avg_pool1d(
        aper_values.view(1, 1, -1),
        kernel_size=3,
        stride=1,
        padding=1,
    ).view(-1)
    voiced_mask = vuv.to(torch.float32) >= DEFAULT_VUV_VOICED_FRAME_THRESHOLD
    aper_values = torch.where(voiced_mask, smoothed.clamp(0.0, 1.0), torch.ones_like(smoothed))
    return aper_values.unsqueeze(-1)
