from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import torch

from v5vc.streaming_student.data import load_streaming_student_target_examples_from_records
from v5vc.streaming_student.fine_structure import (
    build_batched_unit_rms_waveform_frames,
    build_temporal_chunk_vectors,
    fit_waveform_pca_codebook,
)


def build_default_fine_structure_supervision_config() -> dict[str, object]:
    return {
        "mode": "waveform_frame_reconstruction_only_v1",
        "fit_split": "target_train",
        "fit_record_count": 64,
        "fit_frame_cap": 8192,
        "normalize_code": False,
        "chunk_radius": 0,
    }


def resolve_fine_structure_supervision_config(
    *,
    config: Mapping[str, object] | None,
    model_config: Mapping[str, object],
) -> dict[str, object]:
    effective = build_default_fine_structure_supervision_config()
    if config is not None:
        if not isinstance(config, Mapping):
            raise ValueError("fine_structure_supervision must be a mapping object when provided.")
        effective.update(dict(config))
    resolved_mode = str(effective.get("mode", "waveform_frame_reconstruction_only_v1")).strip().lower()
    if resolved_mode not in {
        "waveform_frame_reconstruction_only_v1",
        "waveform_pca_code_v1",
        "waveform_chunk_pca_code_v1",
    }:
        raise ValueError(
            "fine_structure_supervision.mode must be one of: "
            "waveform_frame_reconstruction_only_v1, waveform_pca_code_v1, "
            "waveform_chunk_pca_code_v1."
        )
    resolved_split = str(effective.get("fit_split", "target_train")).strip().lower()
    if resolved_split not in {"target_train", "target_validation", "target_special_eval"}:
        raise ValueError(
            "fine_structure_supervision.fit_split must be one of: "
            "target_train, target_validation, target_special_eval."
        )
    code_dim = int(model_config.get("fine_structure_code_dim", 0))
    if resolved_mode in {"waveform_pca_code_v1", "waveform_chunk_pca_code_v1"} and code_dim <= 0:
        raise ValueError(
            "fine_structure_supervision PCA-code modes require model.fine_structure_code_dim > 0."
        )
    resolved_chunk_radius = max(0, int(effective.get("chunk_radius", 0)))
    if resolved_mode == "waveform_chunk_pca_code_v1" and resolved_chunk_radius <= 0:
        raise ValueError(
            "fine_structure_supervision.mode=waveform_chunk_pca_code_v1 requires chunk_radius > 0."
        )
    return {
        "mode": resolved_mode,
        "fit_split": resolved_split,
        "fit_record_count": max(1, int(effective.get("fit_record_count", 64))),
        "fit_frame_cap": max(1, int(effective.get("fit_frame_cap", 8192))),
        "normalize_code": bool(effective.get("normalize_code", False)),
        "chunk_radius": resolved_chunk_radius,
        "code_dim": code_dim,
    }


def build_fine_structure_supervision_asset(
    *,
    fine_structure_supervision: Mapping[str, object],
    records_by_split: Mapping[str, list[dict[str, object]]],
    config_path: Path,
    frame_length: int,
    hop_length: int,
) -> dict[str, object] | None:
    resolved_mode = str(fine_structure_supervision.get("mode", "waveform_frame_reconstruction_only_v1")).strip().lower()
    if resolved_mode not in {"waveform_pca_code_v1", "waveform_chunk_pca_code_v1"}:
        return None
    fit_split = str(fine_structure_supervision["fit_split"])
    candidate_records = list(records_by_split.get(fit_split, []))
    if not candidate_records:
        raise ValueError(
            f"fine_structure_supervision requested fit_split={fit_split!r}, but no records were available."
        )
    selected_records = select_evenly_spaced_records(
        records=candidate_records,
        record_count=int(fine_structure_supervision["fit_record_count"]),
    )
    examples = load_streaming_student_target_examples_from_records(
        selected_records,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        include_target_acoustic_state=False,
        pitch_provider_request=None,
    )
    waveform_chunks: list[torch.Tensor] = []
    for example in examples:
        valid_frames = int(example.teacher_frame_mask.sum().item())
        if valid_frames <= 0:
            continue
        waveform_batch = example.waveform.unsqueeze(0).to(torch.float32)
        frame_lengths = torch.tensor([valid_frames], dtype=torch.long)
        frames = build_batched_unit_rms_waveform_frames(
            waveform_batch=waveform_batch,
            frame_lengths=frame_lengths,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
        )[0, :valid_frames]
        processed_frames = frames.detach().cpu()
        if resolved_mode == "waveform_chunk_pca_code_v1":
            processed_frames = build_temporal_chunk_vectors(
                processed_frames,
                radius=int(fine_structure_supervision.get("chunk_radius", 0)),
            )
        waveform_chunks.append(processed_frames)
    if not waveform_chunks:
        raise ValueError("fine_structure_supervision could not gather any valid waveform frames.")
    waveform_frames = torch.cat(waveform_chunks, dim=0)
    fit_frame_cap = int(fine_structure_supervision["fit_frame_cap"])
    if int(waveform_frames.shape[0]) > fit_frame_cap:
        selected_indices = torch.linspace(
            0,
            int(waveform_frames.shape[0]) - 1,
            steps=fit_frame_cap,
            dtype=torch.float32,
        ).round().to(torch.long)
        waveform_frames = waveform_frames[selected_indices]
    codebook = fit_waveform_pca_codebook(
        waveform_frames=waveform_frames,
        code_dim=int(fine_structure_supervision["code_dim"]),
    )
    resolved_chunk_radius = int(fine_structure_supervision.get("chunk_radius", 0))
    code_family = (
        "waveform_chunk_pca_code"
        if resolved_mode == "waveform_chunk_pca_code_v1"
        else "waveform_pca_code"
    )
    return {
        "mode": resolved_mode,
        "fit_split": fit_split,
        "fit_record_count": len(selected_records),
        "fit_frame_count": int(codebook["fit_frame_count"]),
        "fit_frame_cap": fit_frame_cap,
        "code_family": code_family,
        "code_dim": int(codebook["components"].shape[-1]),
        "normalize_code": bool(fine_structure_supervision.get("normalize_code", False)),
        "chunk_radius": resolved_chunk_radius,
        "frame_length": int(frame_length),
        "hop_length": int(hop_length),
        "config_path": str(config_path),
        "codebook": codebook,
        "codebook_summary": {
            "codebook_version": str(codebook["codebook_version"]),
            "fit_frame_count": int(codebook["fit_frame_count"]),
            "input_waveform_dim": int(codebook["input_waveform_dim"]),
            "code_dim": int(codebook["components"].shape[-1]),
            "normalize_code": bool(fine_structure_supervision.get("normalize_code", False)),
            "chunk_radius": resolved_chunk_radius,
            "code_std_mean": float(codebook["code_std"].mean().item()),
            "explained_variance_ratio": float(codebook["explained_variance_ratio"]),
        },
    }


def select_evenly_spaced_records(
    *,
    records: list[dict[str, object]],
    record_count: int,
) -> list[dict[str, object]]:
    if not records:
        return []
    effective_count = max(1, min(int(record_count), len(records)))
    if effective_count >= len(records):
        return list(records)
    indices = (
        torch.linspace(0, len(records) - 1, steps=effective_count, dtype=torch.float32)
        .round()
        .to(torch.long)
        .tolist()
    )
    return [records[int(index)] for index in indices]
