from __future__ import annotations

from pathlib import Path

import hashlib
import json

import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F
import torchaudio.functional as audio_functional
from librosa.filters import mel as build_librosa_mel


RMVPE_SAMPLE_RATE = 16000
RMVPE_MEL_BINS = 128
RMVPE_WIN_LENGTH = 1024
RMVPE_HOP_LENGTH = 160
RMVPE_FMIN = 30.0
RMVPE_FMAX = 8000.0
RMVPE_MODEL_VERSION = "stage3_rmvpe_onnx_v1"
RMVPE_CONFIDENCE_PROVIDER_VERSION = "stage3_rmvpe_confidence_provider_v1"
RMVPE_SPLIT_CONFIDENCE_PROVIDER_VERSION = "stage3_rmvpe_split_confidence_provider_v1"


def build_rmvpe_stage3_pitch_provider_tensors(
    *,
    target_f0_hz: torch.Tensor,
    target_vuv: torch.Tensor,
    target_confidence: torch.Tensor | None = None,
) -> dict[str, torch.Tensor]:
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


class RmvpeMelSpectrogram(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        mel_basis = build_librosa_mel(
            sr=RMVPE_SAMPLE_RATE,
            n_fft=RMVPE_WIN_LENGTH,
            n_mels=RMVPE_MEL_BINS,
            fmin=RMVPE_FMIN,
            fmax=RMVPE_FMAX,
            htk=True,
        )
        self.register_buffer("mel_basis", torch.from_numpy(mel_basis).to(torch.float32))
        self.register_buffer(
            "hann_window",
            torch.hann_window(RMVPE_WIN_LENGTH, periodic=True).to(torch.float32),
        )

    def forward(self, waveform: torch.Tensor) -> torch.Tensor:
        if waveform.ndim != 2:
            raise ValueError(f"Expected waveform shape [B, T], got {tuple(waveform.shape)}")
        stft = torch.stft(
            waveform,
            n_fft=RMVPE_WIN_LENGTH,
            hop_length=RMVPE_HOP_LENGTH,
            win_length=RMVPE_WIN_LENGTH,
            window=self.hann_window.to(device=waveform.device),
            center=True,
            return_complex=True,
        )
        magnitude = torch.sqrt(stft.real.pow(2) + stft.imag.pow(2))
        mel_output = torch.matmul(self.mel_basis.to(device=waveform.device), magnitude)
        return torch.log(torch.clamp(mel_output, min=1.0e-5))


class RmvpeOnnxModel:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path.resolve()
        self.mel_extractor = RmvpeMelSpectrogram()
        self.session = ort.InferenceSession(
            self.model_path.as_posix(),
            providers=["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        cents_mapping = 20 * np.arange(360) + 1997.3794084376191
        self.cents_mapping = np.pad(cents_mapping, (4, 4))

    def infer_from_audio(self, waveform_16k: torch.Tensor, *, voicing_threshold: float) -> np.ndarray:
        f0_hz, _confidence = self.infer_f0_hz_and_confidence_from_audio(
            waveform_16k,
            voicing_threshold=voicing_threshold,
        )
        return f0_hz

    def infer_f0_hz_and_confidence_from_audio(
        self,
        waveform_16k: torch.Tensor,
        *,
        voicing_threshold: float | None,
    ) -> tuple[np.ndarray, np.ndarray]:
        if waveform_16k.ndim != 1:
            raise ValueError(f"Expected waveform_16k shape [T], got {tuple(waveform_16k.shape)}")
        mel = self.mel_extractor(waveform_16k.to(torch.float32).unsqueeze(0)).cpu().numpy()
        original_frame_count = int(mel.shape[-1])
        padded_frame_count = 32 * ((original_frame_count - 1) // 32 + 1)
        if padded_frame_count > original_frame_count:
            mel = np.pad(
                mel,
                ((0, 0), (0, 0), (0, padded_frame_count - original_frame_count)),
                mode="constant",
            )
        salience = self.session.run([self.output_name], {self.input_name: mel})[0][0]
        salience = salience[:original_frame_count]
        return self.decode_f0_hz_and_confidence(
            salience=salience,
            voicing_threshold=voicing_threshold,
        )

    def decode_f0_hz(self, *, salience: np.ndarray, voicing_threshold: float) -> np.ndarray:
        f0_hz, _confidence = self.decode_f0_hz_and_confidence(
            salience=salience,
            voicing_threshold=voicing_threshold,
        )
        return f0_hz

    def decode_f0_hz_and_confidence(
        self,
        *,
        salience: np.ndarray,
        voicing_threshold: float | None,
    ) -> tuple[np.ndarray, np.ndarray]:
        center = np.argmax(salience, axis=1)
        padded_salience = np.pad(salience, ((0, 0), (4, 4)))
        center = center + 4
        starts = center - 4
        ends = center + 5
        local_salience = np.stack(
            [padded_salience[index, starts[index] : ends[index]] for index in range(padded_salience.shape[0])],
            axis=0,
        )
        local_cents = np.stack(
            [self.cents_mapping[starts[index] : ends[index]] for index in range(padded_salience.shape[0])],
            axis=0,
        )
        weight_sum = np.sum(local_salience, axis=1)
        cents_pred = np.zeros((padded_salience.shape[0],), dtype=np.float32)
        valid = weight_sum > 0.0
        if bool(valid.any()):
            cents_pred[valid] = (
                np.sum(local_salience[valid] * local_cents[valid], axis=1) / weight_sum[valid]
            ).astype(np.float32)
        frame_max = np.max(padded_salience, axis=1)
        if voicing_threshold is not None:
            cents_pred[frame_max <= float(voicing_threshold)] = 0.0
        f0_hz = 10.0 * np.power(2.0, cents_pred / 1200.0)
        f0_hz[cents_pred <= 0.0] = 0.0
        return f0_hz.astype(np.float32), frame_max.astype(np.float32)


_RMVPE_MODEL_CACHE: dict[str, RmvpeOnnxModel] = {}


def get_rmvpe_onnx_model(model_path: Path) -> RmvpeOnnxModel:
    resolved_model_path = model_path.resolve()
    cache_key = resolved_model_path.as_posix()
    cached = _RMVPE_MODEL_CACHE.get(cache_key)
    if cached is None:
        cached = RmvpeOnnxModel(resolved_model_path)
        _RMVPE_MODEL_CACHE[cache_key] = cached
    return cached


def infer_rmvpe_f0_hz_sequence(
    *,
    waveform: torch.Tensor,
    sample_rate: int,
    model_path: Path,
    voicing_threshold: float,
) -> torch.Tensor:
    waveform_16k = waveform.to(torch.float32)
    if int(sample_rate) != RMVPE_SAMPLE_RATE:
        waveform_16k = audio_functional.resample(
            waveform_16k.unsqueeze(0),
            orig_freq=int(sample_rate),
            new_freq=RMVPE_SAMPLE_RATE,
        )[0]
    rmvpe_model = get_rmvpe_onnx_model(model_path.resolve())
    return torch.from_numpy(
        rmvpe_model.infer_from_audio(
            waveform_16k=waveform_16k,
            voicing_threshold=float(voicing_threshold),
        )
    ).to(torch.float32)


def infer_rmvpe_f0_hz_and_confidence_sequence(
    *,
    waveform: torch.Tensor,
    sample_rate: int,
    model_path: Path,
    voicing_threshold: float | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    waveform_16k = waveform.to(torch.float32)
    if int(sample_rate) != RMVPE_SAMPLE_RATE:
        waveform_16k = audio_functional.resample(
            waveform_16k.unsqueeze(0),
            orig_freq=int(sample_rate),
            new_freq=RMVPE_SAMPLE_RATE,
        )[0]
    rmvpe_model = get_rmvpe_onnx_model(model_path.resolve())
    f0_hz, confidence = rmvpe_model.infer_f0_hz_and_confidence_from_audio(
        waveform_16k=waveform_16k,
        voicing_threshold=None if voicing_threshold is None else float(voicing_threshold),
    )
    return (
        torch.from_numpy(f0_hz).to(torch.float32),
        torch.from_numpy(confidence).to(torch.float32),
    )


def sample_rmvpe_sequence_on_frame_grid(
    *,
    rmvpe_sequence: torch.Tensor,
    frame_start_samples: torch.Tensor,
    source_sample_rate: int,
    anchor_offset_samples: int = 0,
    lag_frames: int = 0,
) -> torch.Tensor:
    if rmvpe_sequence.ndim != 1:
        raise ValueError(f"Expected rmvpe_sequence shape [T], got {tuple(rmvpe_sequence.shape)}")
    sampled_frame_positions = (
        frame_start_samples.to(torch.float32)
        + float(anchor_offset_samples)
        + float(lag_frames * RMVPE_HOP_LENGTH) * (float(source_sample_rate) / float(RMVPE_SAMPLE_RATE))
    )
    provider_indices = torch.round(
        sampled_frame_positions
        * (float(RMVPE_SAMPLE_RATE) / float(source_sample_rate))
        / float(RMVPE_HOP_LENGTH)
    ).to(torch.long)
    provider_indices = provider_indices.clamp(0, max(0, int(rmvpe_sequence.numel()) - 1))
    return rmvpe_sequence[provider_indices].unsqueeze(-1)


def sample_rmvpe_f0_hz_on_frame_grid(
    *,
    rmvpe_f0_hz: torch.Tensor,
    frame_start_samples: torch.Tensor,
    source_sample_rate: int,
    anchor_offset_samples: int = 0,
    lag_frames: int = 0,
) -> torch.Tensor:
    return sample_rmvpe_sequence_on_frame_grid(
        rmvpe_sequence=rmvpe_f0_hz,
        frame_start_samples=frame_start_samples,
        source_sample_rate=source_sample_rate,
        anchor_offset_samples=anchor_offset_samples,
        lag_frames=lag_frames,
    )


def extract_rmvpe_pitch_provider_tensors(
    *,
    record_id: str,
    audio_path: Path,
    waveform: torch.Tensor,
    sample_rate: int,
    frame_start_samples: torch.Tensor,
    model_path: Path,
    cache_dir: Path,
    voicing_threshold: float,
) -> dict[str, torch.Tensor]:
    resolved_audio_path = audio_path.resolve()
    resolved_model_path = model_path.resolve()
    resolved_cache_dir = cache_dir.resolve()
    resolved_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key_payload = {
        "provider_version": RMVPE_MODEL_VERSION,
        "record_id": str(record_id),
        "audio_path": resolved_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "waveform_num_samples": int(waveform.numel()),
        "frame_count": int(frame_start_samples.numel()),
        "last_frame_start_sample": (
            -1 if frame_start_samples.numel() <= 0 else int(frame_start_samples[-1].item())
        ),
        "model_path": resolved_model_path.as_posix(),
        "voicing_threshold": float(voicing_threshold),
    }
    cache_key = hashlib.sha1(
        json.dumps(cache_key_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    cache_path = resolved_cache_dir / f"{cache_key}.pt"
    if cache_path.exists():
        cached_payload = torch.load(cache_path, map_location="cpu", weights_only=False)
        if isinstance(cached_payload, dict) and cached_payload.get("cache_key") == cache_key:
            cached_tensors = cached_payload.get("pitch_provider_tensors")
            if isinstance(cached_tensors, dict):
                return {
                    key: value.to(torch.float32)
                    for key, value in cached_tensors.items()
                    if isinstance(value, torch.Tensor)
                }

    rmvpe_f0_tensor = infer_rmvpe_f0_hz_sequence(
        waveform=waveform,
        sample_rate=int(sample_rate),
        model_path=resolved_model_path,
        voicing_threshold=float(voicing_threshold),
    )
    if rmvpe_f0_tensor.numel() <= 0:
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
            target_vuv=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
        )
    else:
        provider_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
            rmvpe_f0_hz=rmvpe_f0_tensor,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        )
        provider_vuv = (provider_f0_hz > 0.0).to(torch.float32)
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=provider_f0_hz,
            target_vuv=provider_vuv,
        )
    torch.save(
        {
            "cache_key": cache_key,
            "cache_key_payload": cache_key_payload,
            "pitch_provider_tensors": provider_tensors,
        },
        cache_path,
    )
    return provider_tensors


def extract_rmvpe_confidence_pitch_provider_tensors(
    *,
    record_id: str,
    audio_path: Path,
    waveform: torch.Tensor,
    sample_rate: int,
    frame_start_samples: torch.Tensor,
    model_path: Path,
    cache_dir: Path,
) -> dict[str, torch.Tensor]:
    resolved_audio_path = audio_path.resolve()
    resolved_model_path = model_path.resolve()
    resolved_cache_dir = cache_dir.resolve()
    resolved_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key_payload = {
        "provider_version": RMVPE_CONFIDENCE_PROVIDER_VERSION,
        "record_id": str(record_id),
        "audio_path": resolved_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "waveform_num_samples": int(waveform.numel()),
        "frame_count": int(frame_start_samples.numel()),
        "last_frame_start_sample": (
            -1 if frame_start_samples.numel() <= 0 else int(frame_start_samples[-1].item())
        ),
        "model_path": resolved_model_path.as_posix(),
    }
    cache_key = hashlib.sha1(
        json.dumps(cache_key_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    cache_path = resolved_cache_dir / f"{cache_key}.pt"
    if cache_path.exists():
        cached_payload = torch.load(cache_path, map_location="cpu", weights_only=False)
        if isinstance(cached_payload, dict) and cached_payload.get("cache_key") == cache_key:
            cached_tensors = cached_payload.get("pitch_provider_tensors")
            if isinstance(cached_tensors, dict):
                return {
                    key: value.to(torch.float32)
                    for key, value in cached_tensors.items()
                    if isinstance(value, torch.Tensor)
                }

    rmvpe_f0_tensor, rmvpe_confidence_tensor = infer_rmvpe_f0_hz_and_confidence_sequence(
        waveform=waveform,
        sample_rate=int(sample_rate),
        model_path=resolved_model_path,
        voicing_threshold=None,
    )
    if rmvpe_f0_tensor.numel() <= 0:
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
            target_vuv=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
        )
    else:
        provider_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
            rmvpe_f0_hz=rmvpe_f0_tensor,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        )
        provider_confidence = sample_rmvpe_sequence_on_frame_grid(
            rmvpe_sequence=rmvpe_confidence_tensor,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        ).clamp(0.0, 1.0)
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=provider_f0_hz,
            target_vuv=provider_confidence,
        )
    torch.save(
        {
            "cache_key": cache_key,
            "cache_key_payload": cache_key_payload,
            "pitch_provider_tensors": provider_tensors,
        },
        cache_path,
    )
    return provider_tensors


def extract_rmvpe_split_confidence_pitch_provider_tensors(
    *,
    record_id: str,
    audio_path: Path,
    waveform: torch.Tensor,
    sample_rate: int,
    frame_start_samples: torch.Tensor,
    model_path: Path,
    cache_dir: Path,
    voicing_threshold: float,
) -> dict[str, torch.Tensor]:
    resolved_audio_path = audio_path.resolve()
    resolved_model_path = model_path.resolve()
    resolved_cache_dir = cache_dir.resolve()
    resolved_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key_payload = {
        "provider_version": RMVPE_SPLIT_CONFIDENCE_PROVIDER_VERSION,
        "record_id": str(record_id),
        "audio_path": resolved_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "waveform_num_samples": int(waveform.numel()),
        "frame_count": int(frame_start_samples.numel()),
        "last_frame_start_sample": (
            -1 if frame_start_samples.numel() <= 0 else int(frame_start_samples[-1].item())
        ),
        "model_path": resolved_model_path.as_posix(),
        "voicing_threshold": float(voicing_threshold),
    }
    cache_key = hashlib.sha1(
        json.dumps(cache_key_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    cache_path = resolved_cache_dir / f"{cache_key}.pt"
    if cache_path.exists():
        cached_payload = torch.load(cache_path, map_location="cpu", weights_only=False)
        if isinstance(cached_payload, dict) and cached_payload.get("cache_key") == cache_key:
            cached_tensors = cached_payload.get("pitch_provider_tensors")
            if isinstance(cached_tensors, dict):
                return {
                    key: value.to(torch.float32)
                    for key, value in cached_tensors.items()
                    if isinstance(value, torch.Tensor)
                }

    rmvpe_f0_tensor, rmvpe_confidence_tensor = infer_rmvpe_f0_hz_and_confidence_sequence(
        waveform=waveform,
        sample_rate=int(sample_rate),
        model_path=resolved_model_path,
        voicing_threshold=None,
    )
    if rmvpe_f0_tensor.numel() <= 0:
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
            target_vuv=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
            target_confidence=torch.zeros((frame_start_samples.numel(), 1), dtype=torch.float32),
        )
    else:
        provider_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
            rmvpe_f0_hz=rmvpe_f0_tensor,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        )
        provider_confidence = sample_rmvpe_sequence_on_frame_grid(
            rmvpe_sequence=rmvpe_confidence_tensor,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        ).clamp(0.0, 1.0)
        provider_vuv = (provider_confidence >= float(voicing_threshold)).to(torch.float32)
        provider_tensors = build_rmvpe_stage3_pitch_provider_tensors(
            target_f0_hz=provider_f0_hz,
            target_vuv=provider_vuv,
            target_confidence=provider_confidence,
        )
    torch.save(
        {
            "cache_key": cache_key,
            "cache_key_payload": cache_key_payload,
            "pitch_provider_tensors": provider_tensors,
        },
        cache_path,
    )
    return provider_tensors
