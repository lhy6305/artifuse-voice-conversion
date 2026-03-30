from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.streaming_student.data import (
    StreamingStudentTargetExample,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.downstream_control_packet import (
    MAX_VUV_REFERENCE_MAE,
    MAX_F0_CALIBRATED_LOG2_MAE,
    MIN_F0_PROXY_REFERENCE_CORR,
)
from v5vc.streaming_student.pitch_provider import (
    DEFAULT_STAGE3_PITCH_PROVIDER_MODE,
    normalize_stage3_pitch_provider_mode,
    resolve_stage3_pitch_provider_request,
)
from v5vc.streaming_student.rmvpe_inference import (
    infer_rmvpe_f0_hz_and_confidence_sequence,
    infer_rmvpe_f0_hz_sequence,
    sample_rmvpe_f0_hz_on_frame_grid,
    sample_rmvpe_sequence_on_frame_grid,
)

JOINT_OCTAVE_SHIFT_CANDIDATES = (-2, -1, 0, 1, 2)
SUPPORTED_RMVPE_VUV_POSTPROCESS_PRESETS = (
    "raw",
    "fill1",
    "fill2",
    "fill3",
    "min2_fill1",
    "min2_fill2",
    "min2_fill3",
)


def audit_streaming_student_pitch_provider(
    config_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    split_dir: Path | None,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    lag_radius_frames: int,
    rmvpe_voicing_thresholds: list[float] | None = None,
    rmvpe_vuv_postprocess_presets: list[str] | None = None,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    normalized_split_name = str(split_name).strip()
    if normalized_split_name not in records_by_split:
        raise ValueError(f"Unsupported split_name: {split_name}")
    selected_records = select_target_records(
        records=records_by_split[normalized_split_name],
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    pitch_provider_request = resolve_stage3_pitch_provider_request(
        dict(config["model"]),
        config_path=config_path,
    )
    provider_mode = normalize_stage3_pitch_provider_mode(pitch_provider_request.get("mode"))
    if provider_mode == DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
        raise ValueError("pitch provider audit requires config.model.pitch_provider_mode != none.")
    normalized_rmvpe_voicing_thresholds = normalize_rmvpe_voicing_thresholds(
        rmvpe_voicing_thresholds,
        base_threshold=float(pitch_provider_request.get("voicing_threshold", 0.03)),
    )
    normalized_rmvpe_vuv_postprocess_presets = normalize_rmvpe_vuv_postprocess_presets(
        rmvpe_vuv_postprocess_presets,
    )

    examples = load_streaming_student_target_examples_from_records(
        selected_records,
        frame_length=int(config["model"]["frame_length"]),
        hop_length=int(config["model"]["hop_length"]),
        include_target_acoustic_state=True,
        pitch_provider_request=pitch_provider_request,
    )
    record_summaries = [
        build_provider_record_summary(
            example=example,
            frame_length=int(config["model"]["frame_length"]),
            hop_length=int(config["model"]["hop_length"]),
            pitch_provider_request=pitch_provider_request,
            lag_radius_frames=lag_radius_frames,
        )
        for example in examples
    ]

    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "split": split_summary,
        "split_name": normalized_split_name,
        "sample_count": len(record_summaries),
        "pitch_provider_request": serialize_pitch_provider_request(pitch_provider_request),
        "sweep": {
            "lag_radius_frames": int(lag_radius_frames),
            "anchor_modes": (
                ["precomputed_only"]
                if provider_mode != "rmvpe_v1"
                else ["start", "center", "end"]
            ),
        },
        "current_contract_summary": summarize_alignment_group(record_summaries, "current_contract"),
        "best_corr_summary": summarize_alignment_group(record_summaries, "best_corr_candidate"),
        "best_mae_summary": summarize_alignment_group(record_summaries, "best_mae_candidate"),
        "records": record_summaries,
        "notes": [
            "This audit evaluates raw pitch-provider behavior directly against teacher target F0 and VUV.",
            "No Stage3 student correction, proxy acoustic reconstruction, or downstream packet calibration is used in the main provider metrics here.",
            "current_contract uses the provider mapping currently consumed by the Stage3 frontend.",
        ],
    }
    if provider_mode == "rmvpe_v1":
        if normalized_rmvpe_voicing_thresholds or normalized_rmvpe_vuv_postprocess_presets:
            variant_summaries = build_rmvpe_current_contract_variant_summaries(
                examples=examples,
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
                model_path=Path(str(pitch_provider_request["model_path"])),
                voicing_thresholds=normalized_rmvpe_voicing_thresholds,
                vuv_postprocess_presets=normalized_rmvpe_vuv_postprocess_presets,
            )
            summary["rmvpe_current_contract_variant_summaries"] = variant_summaries
            summary["rmvpe_current_contract_best_variant"] = (
                None if not variant_summaries else dict(variant_summaries[0])
            )
            confidence_variant_summaries = build_rmvpe_confidence_aware_variant_summaries(
                examples=examples,
                hop_length=int(config["model"]["hop_length"]),
                model_path=Path(str(pitch_provider_request["model_path"])),
                confidence_thresholds=normalized_rmvpe_voicing_thresholds,
            )
            summary["rmvpe_confidence_aware_variant_summaries"] = confidence_variant_summaries
            summary["rmvpe_confidence_aware_best_variant"] = (
                None if not confidence_variant_summaries else dict(confidence_variant_summaries[0])
            )
        summary["hybrid_reference_vuv_current_summary"] = summarize_alignment_group(
            record_summaries,
            "hybrid_reference_vuv_current",
        )
        summary["notes"].append(
            "hybrid_reference_vuv_current keeps RMVPE F0 but replaces provider VUV with deterministic teacher-reference VUV."
        )
        summary["notes"].append(
            "joint_* metrics evaluate only frames where both provider and reference are voiced, to separate F0 quality from voiced-mask disagreement."
        )
        summary["notes"].append(
            "confidence-aware variants keep unthresholded RMVPE F0 and only change how provider VUV is derived from sampled confidence."
        )
    (output_dir / "streaming_student_pitch_provider_audit.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "streaming_student_pitch_provider_audit.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_provider_record_summary(
    *,
    example: StreamingStudentTargetExample,
    frame_length: int,
    hop_length: int,
    pitch_provider_request: dict[str, object],
    lag_radius_frames: int,
) -> dict[str, object]:
    provider_mode = normalize_stage3_pitch_provider_mode(pitch_provider_request.get("mode"))
    reference_metrics = compute_provider_alignment_metrics(
        provider_f0_hz=example.pitch_provider_f0_hz,
        provider_vuv=example.pitch_provider_vuv,
        target_f0_hz=example.target_f0_hz,
        target_vuv=example.target_vuv,
        anchor_mode="precomputed" if provider_mode != "rmvpe_v1" else "start",
        lag_frames=0,
    )
    summary = {
        "record_id": example.record_id,
        "audio_path": example.audio_path.resolve().as_posix(),
        "sample_rate": int(example.sample_rate),
        "frame_count": int(example.teacher_frame_mask.sum().item()),
        "current_contract": reference_metrics,
    }
    if provider_mode != "rmvpe_v1":
        summary["best_corr_candidate"] = dict(reference_metrics)
        summary["best_mae_candidate"] = dict(reference_metrics)
        summary["hybrid_reference_vuv_current"] = dict(reference_metrics)
        return summary

    frame_count = int(example.teacher_frame_mask.sum().item())
    frame_start_samples = torch.arange(frame_count, dtype=torch.long) * int(hop_length)
    rmvpe_f0_hz = infer_rmvpe_f0_hz_sequence(
        waveform=example.waveform,
        sample_rate=int(example.sample_rate),
        model_path=Path(str(pitch_provider_request["model_path"])),
        voicing_threshold=float(pitch_provider_request["voicing_threshold"]),
    )
    alignment_candidates: list[dict[str, object]] = []
    hybrid_reference_vuv_metrics = compute_provider_alignment_metrics(
        provider_f0_hz=example.pitch_provider_f0_hz,
        provider_vuv=example.target_vuv,
        target_f0_hz=example.target_f0_hz,
        target_vuv=example.target_vuv,
        anchor_mode="start",
        lag_frames=0,
    )
    anchor_offsets = {
        "start": 0,
        "center": int(frame_length) // 2,
        "end": max(0, int(frame_length) - 1),
    }
    for anchor_mode, anchor_offset in anchor_offsets.items():
        for lag_frames in range(-int(lag_radius_frames), int(lag_radius_frames) + 1):
            provider_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
                rmvpe_f0_hz=rmvpe_f0_hz,
                frame_start_samples=frame_start_samples,
                source_sample_rate=int(example.sample_rate),
                anchor_offset_samples=anchor_offset,
                lag_frames=lag_frames,
            )
            provider_vuv = (provider_f0_hz > 0.0).to(torch.float32)
            alignment_candidates.append(
                compute_provider_alignment_metrics(
                    provider_f0_hz=provider_f0_hz,
                    provider_vuv=provider_vuv,
                    target_f0_hz=example.target_f0_hz,
                    target_vuv=example.target_vuv,
                    anchor_mode=anchor_mode,
                    lag_frames=lag_frames,
                )
            )
    summary["best_corr_candidate"] = max(
        alignment_candidates,
        key=best_corr_key,
    )
    summary["best_mae_candidate"] = min(
        alignment_candidates,
        key=best_mae_key,
    )
    summary["hybrid_reference_vuv_current"] = hybrid_reference_vuv_metrics
    return summary


def build_rmvpe_current_contract_variant_summaries(
    *,
    examples: list[StreamingStudentTargetExample],
    frame_length: int,
    hop_length: int,
    model_path: Path,
    voicing_thresholds: list[float],
    vuv_postprocess_presets: list[str],
) -> list[dict[str, object]]:
    variant_summaries: list[dict[str, object]] = []
    for voicing_threshold in voicing_thresholds:
        sampled_sequences: list[tuple[StreamingStudentTargetExample, torch.Tensor, torch.Tensor]] = []
        for example in examples:
            frame_count = int(example.teacher_frame_mask.sum().item())
            frame_start_samples = torch.arange(frame_count, dtype=torch.long) * int(hop_length)
            rmvpe_f0_hz = infer_rmvpe_f0_hz_sequence(
                waveform=example.waveform,
                sample_rate=int(example.sample_rate),
                model_path=model_path,
                voicing_threshold=float(voicing_threshold),
            )
            provider_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
                rmvpe_f0_hz=rmvpe_f0_hz,
                frame_start_samples=frame_start_samples,
                source_sample_rate=int(example.sample_rate),
                anchor_offset_samples=0,
                lag_frames=0,
            )
            provider_vuv = (provider_f0_hz > 0.0).to(torch.float32)
            sampled_sequences.append((example, provider_f0_hz, provider_vuv))
        for preset in vuv_postprocess_presets:
            rows: list[dict[str, object]] = []
            record_briefs: list[dict[str, object]] = []
            for example, provider_f0_hz, provider_vuv in sampled_sequences:
                processed_f0_hz, processed_vuv = apply_rmvpe_vuv_postprocess(
                    provider_f0_hz=provider_f0_hz,
                    provider_vuv=provider_vuv,
                    preset=preset,
                )
                metrics = compute_provider_alignment_metrics(
                    provider_f0_hz=processed_f0_hz,
                    provider_vuv=processed_vuv,
                    target_f0_hz=example.target_f0_hz,
                    target_vuv=example.target_vuv,
                    anchor_mode="start",
                    lag_frames=0,
                )
                rows.append(metrics)
                record_briefs.append(
                    {
                        "record_id": example.record_id,
                        "voiced_log2_mae": metrics.get("voiced_log2_mae"),
                        "voiced_corr": metrics.get("voiced_corr"),
                        "joint_voiced_log2_mae": metrics.get("joint_voiced_log2_mae"),
                        "joint_voiced_corr": metrics.get("joint_voiced_corr"),
                        "vuv_f1": metrics.get("vuv_f1"),
                        "ready_like": metrics.get("ready_like"),
                    }
                )
            variant_summaries.append(
                {
                    "label": f"thr{float(voicing_threshold):.3f}_{preset}",
                    "voicing_threshold": round(float(voicing_threshold), 6),
                    "vuv_postprocess_preset": preset,
                    "aggregate": summarize_metric_rows(rows),
                    "records": record_briefs,
                }
            )
    variant_summaries.sort(key=rmvpe_variant_sort_key, reverse=True)
    return variant_summaries


def build_rmvpe_confidence_aware_variant_summaries(
    *,
    examples: list[StreamingStudentTargetExample],
    hop_length: int,
    model_path: Path,
    confidence_thresholds: list[float],
) -> list[dict[str, object]]:
    sampled_sequences: list[tuple[StreamingStudentTargetExample, torch.Tensor, torch.Tensor]] = []
    for example in examples:
        frame_count = int(example.teacher_frame_mask.sum().item())
        frame_start_samples = torch.arange(frame_count, dtype=torch.long) * int(hop_length)
        rmvpe_f0_hz, rmvpe_confidence = infer_rmvpe_f0_hz_and_confidence_sequence(
            waveform=example.waveform,
            sample_rate=int(example.sample_rate),
            model_path=model_path,
            voicing_threshold=None,
        )
        sampled_f0_hz = sample_rmvpe_f0_hz_on_frame_grid(
            rmvpe_f0_hz=rmvpe_f0_hz,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(example.sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        )
        sampled_confidence = sample_rmvpe_sequence_on_frame_grid(
            rmvpe_sequence=rmvpe_confidence,
            frame_start_samples=frame_start_samples,
            source_sample_rate=int(example.sample_rate),
            anchor_offset_samples=0,
            lag_frames=0,
        ).clamp(0.0, 1.0)
        sampled_sequences.append((example, sampled_f0_hz, sampled_confidence))

    variant_summaries: list[dict[str, object]] = []
    for threshold in confidence_thresholds:
        rows: list[dict[str, object]] = []
        record_briefs: list[dict[str, object]] = []
        for example, sampled_f0_hz, sampled_confidence in sampled_sequences:
            hard_vuv = (sampled_confidence >= float(threshold)).to(torch.float32)
            metrics = compute_provider_alignment_metrics(
                provider_f0_hz=sampled_f0_hz,
                provider_vuv=hard_vuv,
                target_f0_hz=example.target_f0_hz,
                target_vuv=example.target_vuv,
                anchor_mode="start",
                lag_frames=0,
            )
            rows.append(metrics)
            record_briefs.append(
                {
                    "record_id": example.record_id,
                    "voiced_log2_mae": metrics.get("voiced_log2_mae"),
                    "voiced_corr": metrics.get("voiced_corr"),
                    "joint_voiced_log2_mae": metrics.get("joint_voiced_log2_mae"),
                    "joint_voiced_corr": metrics.get("joint_voiced_corr"),
                    "vuv_f1": metrics.get("vuv_f1"),
                    "ready_like": metrics.get("ready_like"),
                }
            )
        variant_summaries.append(
            {
                "label": f"confthr{float(threshold):.3f}_hardvuv_unthresholdedf0",
                "confidence_threshold": round(float(threshold), 6),
                "vuv_mode": "hard_thresholded_confidence",
                "f0_mode": "unthresholded_sampled_f0",
                "aggregate": summarize_metric_rows(rows),
                "records": record_briefs,
            }
        )

    soft_rows: list[dict[str, object]] = []
    soft_record_briefs: list[dict[str, object]] = []
    for example, sampled_f0_hz, sampled_confidence in sampled_sequences:
        metrics = compute_provider_alignment_metrics(
            provider_f0_hz=sampled_f0_hz,
            provider_vuv=sampled_confidence,
            target_f0_hz=example.target_f0_hz,
            target_vuv=example.target_vuv,
            anchor_mode="start",
            lag_frames=0,
        )
        soft_rows.append(metrics)
        soft_record_briefs.append(
            {
                "record_id": example.record_id,
                "voiced_log2_mae": metrics.get("voiced_log2_mae"),
                "voiced_corr": metrics.get("voiced_corr"),
                "joint_voiced_log2_mae": metrics.get("joint_voiced_log2_mae"),
                "joint_voiced_corr": metrics.get("joint_voiced_corr"),
                "vuv_f1": metrics.get("vuv_f1"),
                "ready_like": metrics.get("ready_like"),
            }
        )
    variant_summaries.append(
        {
            "label": "softvuv_rawconfidence_unthresholdedf0",
            "confidence_threshold": None,
            "vuv_mode": "soft_sampled_confidence",
            "f0_mode": "unthresholded_sampled_f0",
            "aggregate": summarize_metric_rows(soft_rows),
            "records": soft_record_briefs,
        }
    )
    variant_summaries.sort(key=rmvpe_variant_sort_key, reverse=True)
    return variant_summaries


def compute_provider_alignment_metrics(
    *,
    provider_f0_hz: torch.Tensor | None,
    provider_vuv: torch.Tensor | None,
    target_f0_hz: torch.Tensor | None,
    target_vuv: torch.Tensor | None,
    anchor_mode: str,
    lag_frames: int,
) -> dict[str, object]:
    if not isinstance(provider_f0_hz, torch.Tensor) or not isinstance(provider_vuv, torch.Tensor):
        raise ValueError("Provider alignment metrics require provider_f0_hz and provider_vuv tensors.")
    if not isinstance(target_f0_hz, torch.Tensor) or not isinstance(target_vuv, torch.Tensor):
        raise ValueError("Provider alignment metrics require target_f0_hz and target_vuv tensors.")
    provider_f0_hz = provider_f0_hz.to(torch.float32).view(-1)
    provider_vuv = provider_vuv.to(torch.float32).view(-1)
    target_f0_hz = target_f0_hz.to(torch.float32).view(-1)
    target_vuv = target_vuv.to(torch.float32).view(-1)
    frame_count = min(
        int(provider_f0_hz.numel()),
        int(provider_vuv.numel()),
        int(target_f0_hz.numel()),
        int(target_vuv.numel()),
    )
    provider_f0_hz = provider_f0_hz[:frame_count]
    provider_vuv = provider_vuv[:frame_count]
    target_f0_hz = target_f0_hz[:frame_count]
    target_vuv = target_vuv[:frame_count]
    reference_voiced_mask = ((target_vuv >= 0.5) & (target_f0_hz > 0.0))
    predicted_vuv = provider_vuv.clamp(0.0, 1.0)
    predicted_voiced_mask = predicted_vuv >= 0.5
    provider_log2_f0 = torch.zeros_like(provider_f0_hz)
    provider_voiced_mask = provider_f0_hz > 0.0
    if bool(provider_voiced_mask.any().item()):
        provider_log2_f0 = torch.where(
            provider_voiced_mask,
            torch.log2(provider_f0_hz.clamp_min(1.0)),
            provider_log2_f0,
        )
    target_log2_f0 = torch.log2(target_f0_hz.clamp_min(1.0))
    voiced_log2_mae = None
    voiced_corr = None
    voiced_bias_mean = None
    affine_mae = None
    affine_slope = None
    affine_intercept = None
    if bool(reference_voiced_mask.any().item()):
        provider_voiced_log2 = provider_log2_f0[reference_voiced_mask]
        target_voiced_log2 = target_log2_f0[reference_voiced_mask]
        voiced_log2_mae = float((provider_voiced_log2 - target_voiced_log2).abs().mean().item())
        voiced_bias_mean = float((provider_voiced_log2 - target_voiced_log2).mean().item())
        voiced_corr = compute_correlation(provider_voiced_log2, target_voiced_log2)
        affine_fit = fit_affine(provider_voiced_log2, target_voiced_log2)
        if affine_fit is not None:
            affine_slope, affine_intercept, affine_mae = affine_fit
    joint_voiced_mask = reference_voiced_mask & predicted_voiced_mask & provider_voiced_mask
    joint_voiced_log2_mae = None
    joint_voiced_corr = None
    joint_voiced_bias_mean = None
    joint_affine_mae = None
    joint_affine_slope = None
    joint_affine_intercept = None
    joint_best_octave_shift = None
    joint_best_octave_shift_mae = None
    if bool(joint_voiced_mask.any().item()):
        provider_joint_log2 = provider_log2_f0[joint_voiced_mask]
        target_joint_log2 = target_log2_f0[joint_voiced_mask]
        joint_voiced_log2_mae = float((provider_joint_log2 - target_joint_log2).abs().mean().item())
        joint_voiced_bias_mean = float((provider_joint_log2 - target_joint_log2).mean().item())
        joint_voiced_corr = compute_correlation(provider_joint_log2, target_joint_log2)
        joint_affine_fit = fit_affine(provider_joint_log2, target_joint_log2)
        if joint_affine_fit is not None:
            joint_affine_slope, joint_affine_intercept, joint_affine_mae = joint_affine_fit
        octave_probe = probe_best_octave_shift(
            provider_log2_f0=provider_joint_log2,
            target_log2_f0=target_joint_log2,
        )
        if octave_probe is not None:
            joint_best_octave_shift, joint_best_octave_shift_mae = octave_probe
    vuv_mae = float((predicted_vuv - target_vuv.clamp(0.0, 1.0)).abs().mean().item())
    precision, recall, f1 = compute_binary_prf(
        predicted=predicted_voiced_mask,
        reference=reference_voiced_mask,
    )
    ready_like = (
        voiced_corr is not None
        and voiced_corr >= float(MIN_F0_PROXY_REFERENCE_CORR)
        and voiced_log2_mae is not None
        and voiced_log2_mae <= float(MAX_F0_CALIBRATED_LOG2_MAE)
        and vuv_mae <= float(MAX_VUV_REFERENCE_MAE)
    )
    return {
        "anchor_mode": anchor_mode,
        "lag_frames": int(lag_frames),
        "frame_count": int(frame_count),
        "reference_voiced_frame_count": int(reference_voiced_mask.to(torch.long).sum().item()),
        "provider_voiced_frame_count": int(predicted_voiced_mask.to(torch.long).sum().item()),
        "joint_voiced_frame_count": int(joint_voiced_mask.to(torch.long).sum().item()),
        "voiced_log2_mae": none_or_round(voiced_log2_mae),
        "voiced_corr": none_or_round(voiced_corr),
        "voiced_bias_mean": none_or_round(voiced_bias_mean),
        "affine_voiced_log2_mae": none_or_round(affine_mae),
        "affine_slope": none_or_round(affine_slope),
        "affine_intercept": none_or_round(affine_intercept),
        "joint_voiced_log2_mae": none_or_round(joint_voiced_log2_mae),
        "joint_voiced_corr": none_or_round(joint_voiced_corr),
        "joint_voiced_bias_mean": none_or_round(joint_voiced_bias_mean),
        "joint_affine_voiced_log2_mae": none_or_round(joint_affine_mae),
        "joint_affine_slope": none_or_round(joint_affine_slope),
        "joint_affine_intercept": none_or_round(joint_affine_intercept),
        "joint_octave_shift_best": none_or_round(joint_best_octave_shift),
        "joint_octave_shift_best_mae": none_or_round(joint_best_octave_shift_mae),
        "vuv_mae": round(vuv_mae, 6),
        "vuv_precision": round(precision, 6),
        "vuv_recall": round(recall, 6),
        "vuv_f1": round(f1, 6),
        "ready_like": bool(ready_like),
    }


def compute_binary_prf(*, predicted: torch.Tensor, reference: torch.Tensor) -> tuple[float, float, float]:
    predicted = predicted.to(torch.bool)
    reference = reference.to(torch.bool)
    tp = int((predicted & reference).to(torch.long).sum().item())
    fp = int((predicted & (~reference)).to(torch.long).sum().item())
    fn = int(((~predicted) & reference).to(torch.long).sum().item())
    precision = 0.0 if tp + fp <= 0 else tp / float(tp + fp)
    recall = 0.0 if tp + fn <= 0 else tp / float(tp + fn)
    f1 = 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)
    return precision, recall, f1


def compute_correlation(left: torch.Tensor, right: torch.Tensor) -> float | None:
    if left.numel() <= 1 or right.numel() <= 1:
        return None
    left_centered = left - left.mean()
    right_centered = right - right.mean()
    left_norm = float(left_centered.pow(2).sum().sqrt().item())
    right_norm = float(right_centered.pow(2).sum().sqrt().item())
    if left_norm <= 1.0e-8 or right_norm <= 1.0e-8:
        return None
    return float((left_centered * right_centered).sum().item() / (left_norm * right_norm))


def fit_affine(left: torch.Tensor, right: torch.Tensor) -> tuple[float, float, float] | None:
    if left.numel() <= 1 or right.numel() <= 1:
        return None
    design = torch.stack([left, torch.ones_like(left)], dim=-1)
    solution = torch.linalg.lstsq(design, right.unsqueeze(-1)).solution.squeeze(-1)
    if solution.numel() != 2:
        return None
    slope = float(solution[0].item())
    intercept = float(solution[1].item())
    prediction = left * slope + intercept
    mae = float((prediction - right).abs().mean().item())
    return slope, intercept, mae


def probe_best_octave_shift(
    *,
    provider_log2_f0: torch.Tensor,
    target_log2_f0: torch.Tensor,
) -> tuple[float, float] | None:
    if provider_log2_f0.numel() <= 0 or target_log2_f0.numel() <= 0:
        return None
    best_shift = None
    best_mae = None
    for shift in JOINT_OCTAVE_SHIFT_CANDIDATES:
        shifted = provider_log2_f0 + float(shift)
        mae = float((shifted - target_log2_f0).abs().mean().item())
        if best_mae is None or mae < best_mae:
            best_shift = float(shift)
            best_mae = mae
    if best_shift is None or best_mae is None:
        return None
    return best_shift, best_mae


def normalize_rmvpe_voicing_thresholds(
    values: list[float] | None,
    *,
    base_threshold: float,
) -> list[float]:
    normalized_values = [float(base_threshold)] if not values else [float(item) for item in values]
    unique_values: list[float] = []
    for value in normalized_values:
        if value < 0.0:
            raise ValueError(f"rmvpe voicing threshold must be non-negative, got {value}")
        rounded = round(float(value), 6)
        if rounded not in unique_values:
            unique_values.append(rounded)
    return unique_values


def normalize_rmvpe_vuv_postprocess_presets(values: list[str] | None) -> list[str]:
    normalized_values = ["raw"] if not values else [str(item).strip().lower() for item in values]
    unique_values: list[str] = []
    for value in normalized_values:
        if value not in SUPPORTED_RMVPE_VUV_POSTPROCESS_PRESETS:
            raise ValueError(
                "Unsupported rmvpe VUV postprocess preset: "
                f"{value}. Expected one of {SUPPORTED_RMVPE_VUV_POSTPROCESS_PRESETS}."
            )
        if value not in unique_values:
            unique_values.append(value)
    return unique_values


def apply_rmvpe_vuv_postprocess(
    *,
    provider_f0_hz: torch.Tensor,
    provider_vuv: torch.Tensor,
    preset: str,
) -> tuple[torch.Tensor, torch.Tensor]:
    min_voiced_run_frames, max_unvoiced_gap_fill_frames = resolve_rmvpe_vuv_postprocess_preset(preset)
    f0_hz = provider_f0_hz.to(torch.float32).view(-1).clone()
    vuv_mask = (provider_vuv.to(torch.float32).view(-1) >= 0.5) & (f0_hz > 0.0)
    if min_voiced_run_frames > 1:
        vuv_mask = suppress_short_voiced_runs(
            mask=vuv_mask,
            min_run_length=min_voiced_run_frames,
        )
    f0_hz = torch.where(vuv_mask, f0_hz, torch.zeros_like(f0_hz))
    if max_unvoiced_gap_fill_frames > 0:
        vuv_mask, f0_hz = fill_short_unvoiced_gaps(
            mask=vuv_mask,
            f0_hz=f0_hz,
            max_gap_length=max_unvoiced_gap_fill_frames,
        )
    return f0_hz.unsqueeze(-1), vuv_mask.to(torch.float32).unsqueeze(-1)


def resolve_rmvpe_vuv_postprocess_preset(preset: str) -> tuple[int, int]:
    normalized = str(preset).strip().lower()
    if normalized == "raw":
        return 1, 0
    if normalized.startswith("fill"):
        return 1, int(normalized.removeprefix("fill"))
    prefix, _, suffix = normalized.partition("_")
    if not prefix.startswith("min") or not suffix.startswith("fill"):
        raise ValueError(f"Unsupported RMVPE VUV postprocess preset: {preset}")
    return int(prefix.removeprefix("min")), int(suffix.removeprefix("fill"))


def suppress_short_voiced_runs(mask: torch.Tensor, *, min_run_length: int) -> torch.Tensor:
    if min_run_length <= 1:
        return mask.clone()
    updated = mask.to(torch.bool).clone()
    start = None
    for index in range(int(updated.numel()) + 1):
        active = index < int(updated.numel()) and bool(updated[index].item())
        if active and start is None:
            start = index
            continue
        if active:
            continue
        if start is not None:
            if index - start < int(min_run_length):
                updated[start:index] = False
            start = None
    return updated


def fill_short_unvoiced_gaps(
    *,
    mask: torch.Tensor,
    f0_hz: torch.Tensor,
    max_gap_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if max_gap_length <= 0:
        return mask.clone(), f0_hz.clone()
    updated_mask = mask.to(torch.bool).clone()
    updated_f0_hz = f0_hz.to(torch.float32).clone()
    index = 0
    num_frames = int(updated_mask.numel())
    while index < num_frames:
        if bool(updated_mask[index].item()):
            index += 1
            continue
        gap_start = index
        while index < num_frames and not bool(updated_mask[index].item()):
            index += 1
        gap_end = index
        gap_length = gap_end - gap_start
        if gap_length <= 0 or gap_length > int(max_gap_length):
            continue
        left_index = gap_start - 1
        right_index = gap_end
        if left_index < 0 or right_index >= num_frames:
            continue
        if not bool(updated_mask[left_index].item()) or not bool(updated_mask[right_index].item()):
            continue
        left_f0_hz = float(updated_f0_hz[left_index].item())
        right_f0_hz = float(updated_f0_hz[right_index].item())
        if left_f0_hz <= 0.0 or right_f0_hz <= 0.0:
            continue
        left_log2 = float(torch.log2(updated_f0_hz[left_index].clamp_min(1.0)).item())
        right_log2 = float(torch.log2(updated_f0_hz[right_index].clamp_min(1.0)).item())
        for local_offset in range(gap_length):
            alpha = float(local_offset + 1) / float(gap_length + 1)
            interpolated_log2 = (1.0 - alpha) * left_log2 + alpha * right_log2
            updated_mask[gap_start + local_offset] = True
            updated_f0_hz[gap_start + local_offset] = float(2.0 ** interpolated_log2)
    return updated_mask, updated_f0_hz


def best_corr_key(candidate: dict[str, object]) -> tuple[float, float, float]:
    corr = candidate.get("voiced_corr")
    mae = candidate.get("voiced_log2_mae")
    f1 = candidate.get("vuv_f1")
    return (
        -999.0 if corr is None else float(corr),
        -999.0 if f1 is None else float(f1),
        -999.0 if mae is None else -float(mae),
    )


def best_mae_key(candidate: dict[str, object]) -> tuple[float, float, float]:
    mae = candidate.get("voiced_log2_mae")
    corr = candidate.get("voiced_corr")
    f1 = candidate.get("vuv_f1")
    return (
        999.0 if mae is None else float(mae),
        999.0 if corr is None else -float(corr),
        999.0 if f1 is None else -float(f1),
    )


def summarize_alignment_group(
    records: list[dict[str, object]],
    key: str,
) -> dict[str, object]:
    rows = [dict(record[key]) for record in records]
    return summarize_metric_rows(rows)


def summarize_metric_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    anchor_counts: dict[str, int] = {}
    lag_counts: dict[str, int] = {}
    ready_like_count = 0
    for row in rows:
        anchor = str(row.get("anchor_mode", "unknown"))
        anchor_counts[anchor] = anchor_counts.get(anchor, 0) + 1
        lag_key = str(row.get("lag_frames", "unknown"))
        lag_counts[lag_key] = lag_counts.get(lag_key, 0) + 1
        if bool(row.get("ready_like", False)):
            ready_like_count += 1
    return {
        "record_count": len(rows),
        "ready_like_count": int(ready_like_count),
        "avg_voiced_log2_mae": average_metric(rows, "voiced_log2_mae"),
        "avg_voiced_corr": average_metric(rows, "voiced_corr"),
        "avg_affine_voiced_log2_mae": average_metric(rows, "affine_voiced_log2_mae"),
        "avg_joint_voiced_log2_mae": average_metric(rows, "joint_voiced_log2_mae"),
        "avg_joint_voiced_corr": average_metric(rows, "joint_voiced_corr"),
        "avg_joint_affine_voiced_log2_mae": average_metric(rows, "joint_affine_voiced_log2_mae"),
        "avg_joint_octave_shift_best_mae": average_metric(rows, "joint_octave_shift_best_mae"),
        "avg_vuv_mae": average_metric(rows, "vuv_mae"),
        "avg_vuv_f1": average_metric(rows, "vuv_f1"),
        "positive_voiced_corr_count": count_metric_rows(
            rows,
            "voiced_corr",
            lambda value: value > 0.0,
        ),
        "voiced_corr_ge_0_3_count": count_metric_rows(
            rows,
            "voiced_corr",
            lambda value: value >= 0.3,
        ),
        "voiced_log2_mae_le_0_2_count": count_metric_rows(
            rows,
            "voiced_log2_mae",
            lambda value: value <= 0.2,
        ),
        "anchor_counts": dict(sorted(anchor_counts.items())),
        "lag_counts": dict(sorted(lag_counts.items(), key=lambda item: int(item[0]))),
    }


def rmvpe_variant_sort_key(variant: dict[str, object]) -> tuple[float, float, float, float, float, float]:
    aggregate = dict(variant.get("aggregate", {}))
    ready_like_count = float(aggregate.get("ready_like_count", 0))
    positive_voiced_corr_count = float(aggregate.get("positive_voiced_corr_count", 0))
    avg_voiced_corr = -999.0 if aggregate.get("avg_voiced_corr") is None else float(aggregate["avg_voiced_corr"])
    avg_vuv_f1 = -999.0 if aggregate.get("avg_vuv_f1") is None else float(aggregate["avg_vuv_f1"])
    avg_voiced_log2_mae = 999.0 if aggregate.get("avg_voiced_log2_mae") is None else float(
        aggregate["avg_voiced_log2_mae"]
    )
    avg_joint_voiced_corr = (
        -999.0 if aggregate.get("avg_joint_voiced_corr") is None else float(aggregate["avg_joint_voiced_corr"])
    )
    return (
        ready_like_count,
        positive_voiced_corr_count,
        avg_voiced_corr,
        avg_vuv_f1,
        -avg_voiced_log2_mae,
        avg_joint_voiced_corr,
    )


def average_metric(rows: list[dict[str, object]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def none_or_round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def count_metric_rows(
    rows: list[dict[str, object]],
    key: str,
    predicate,
) -> int:
    count = 0
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        if bool(predicate(float(value))):
            count += 1
    return count


def serialize_pitch_provider_request(request: dict[str, object]) -> dict[str, object]:
    serialized: dict[str, object] = {}
    for key, value in request.items():
        if isinstance(value, Path):
            serialized[key] = value.as_posix()
        else:
            serialized[key] = value
    return serialized


def select_target_records(
    records: list[dict[str, object]],
    sample_count: int,
    target_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    if target_record_ids:
        record_map = {str(record["record_id"]): record for record in records}
        selected: list[dict[str, object]] = []
        missing: list[str] = []
        for record_id in target_record_ids:
            record = record_map.get(record_id)
            if record is None:
                missing.append(record_id)
                continue
            selected.append(record)
        if missing:
            raise ValueError(f"Unknown target_record_ids: {missing}")
        return selected
    if sample_count <= 0:
        raise ValueError("sample_count must be positive.")
    if len(records) <= sample_count:
        return records
    if sample_count == 1:
        return [records[0]]
    indices: list[int] = []
    max_index = len(records) - 1
    for index in range(sample_count):
        candidate = round(index * max_index / (sample_count - 1))
        if candidate not in indices:
            indices.append(candidate)
    while len(indices) < sample_count:
        for candidate in range(len(records)):
            if candidate not in indices:
                indices.append(candidate)
            if len(indices) >= sample_count:
                break
    return [records[index] for index in indices[:sample_count]]


def build_markdown(summary: dict[str, object]) -> str:
    current = dict(summary["current_contract_summary"])
    best_corr = dict(summary["best_corr_summary"])
    best_mae = dict(summary["best_mae_summary"])
    lines = [
        "# Stage3 pitch provider audit",
        "",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- pitch_provider_request: {json.dumps(summary['pitch_provider_request'], ensure_ascii=False)}",
        "",
        "## Aggregate",
        f"- current_contract: {json.dumps(current, ensure_ascii=False)}",
        f"- best_corr_summary: {json.dumps(best_corr, ensure_ascii=False)}",
        f"- best_mae_summary: {json.dumps(best_mae, ensure_ascii=False)}",
        "",
        "## Records",
    ]
    hybrid_summary = summary.get("hybrid_reference_vuv_current_summary")
    if isinstance(hybrid_summary, dict):
        lines.insert(-2, f"- hybrid_reference_vuv_current_summary: {json.dumps(hybrid_summary, ensure_ascii=False)}")
        lines.insert(-2, "")
    for record in summary["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- audio_path: {record['audio_path']}")
        lines.append(f"- current_contract: {json.dumps(record['current_contract'], ensure_ascii=False)}")
        lines.append(f"- best_corr_candidate: {json.dumps(record['best_corr_candidate'], ensure_ascii=False)}")
        lines.append(f"- best_mae_candidate: {json.dumps(record['best_mae_candidate'], ensure_ascii=False)}")
        if "hybrid_reference_vuv_current" in record:
            lines.append(
                f"- hybrid_reference_vuv_current: {json.dumps(record['hybrid_reference_vuv_current'], ensure_ascii=False)}"
            )
        lines.append("")
    variant_summaries = summary.get("rmvpe_current_contract_variant_summaries")
    if isinstance(variant_summaries, list) and variant_summaries:
        lines.append("## RMVPE Current-Contract Variants")
        for variant in variant_summaries[: min(10, len(variant_summaries))]:
            lines.append(
                f"- {variant['label']}: {json.dumps(variant['aggregate'], ensure_ascii=False)}"
            )
        lines.append("")
    confidence_variant_summaries = summary.get("rmvpe_confidence_aware_variant_summaries")
    if isinstance(confidence_variant_summaries, list) and confidence_variant_summaries:
        lines.append("## RMVPE Confidence-Aware Variants")
        for variant in confidence_variant_summaries[: min(10, len(confidence_variant_summaries))]:
            lines.append(
                f"- {variant['label']}: {json.dumps(variant['aggregate'], ensure_ascii=False)}"
            )
        lines.append("")
    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
