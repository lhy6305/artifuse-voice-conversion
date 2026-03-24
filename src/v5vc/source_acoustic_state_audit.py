from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.offline_mvp.data import load_waveform
from v5vc.source_acoustic_state_extraction import extract_source_acoustic_state
from v5vc.streaming_student.teacher_labels import resolve_teacher_source


DEFAULT_SOURCE_ACOUSTIC_STATE_AUDIT_INPUTS = (
    Path("data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav"),
    Path("data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_132.wav"),
    Path("data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav"),
)


def audit_source_acoustic_state_extraction(
    input_audio_paths: list[Path],
    output_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    max_audio_sec: float | None,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    resolved_source = resolve_teacher_source(
        route_handoff_path=route_handoff_path,
        experiment_metrics_path=None,
        checkpoint_path=checkpoint_path,
        split_dir=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
    )
    checkpoint_payload = load_checkpoint(Path(resolved_source["checkpoint_path"]))
    checkpoint_config = checkpoint_payload.get("config")
    if not isinstance(checkpoint_config, dict):
        raise ValueError("Teacher checkpoint does not contain a valid config payload.")
    model_config = checkpoint_config.get("model")
    if not isinstance(model_config, dict):
        raise ValueError("Teacher checkpoint config.model is missing.")

    frame_length = int(model_config["frame_length"])
    hop_length = int(model_config["hop_length"])
    case_summaries: list[dict[str, object]] = []
    for input_audio_path in resolve_input_audio_paths(input_audio_paths):
        waveform, sample_rate = load_waveform(input_audio_path.resolve(), max_duration_sec=max_audio_sec)
        frame_start_samples = build_frame_start_samples(
            waveform_samples=int(waveform.numel()),
            frame_length=frame_length,
            hop_length=hop_length,
        )
        payload = extract_source_acoustic_state(
            waveform=waveform,
            sample_rate=sample_rate,
            frame_start_samples=frame_start_samples,
            frame_length=frame_length,
        )
        case_summary = build_case_summary(
            input_audio_path=input_audio_path,
            sample_rate=sample_rate,
            waveform_samples=int(waveform.numel()),
            frame_length=frame_length,
            hop_length=hop_length,
            extraction_payload=payload,
        )
        case_output_dir = cases_dir / input_audio_path.stem
        case_output_dir.mkdir(parents=True, exist_ok=True)
        (case_output_dir / "source_acoustic_state_audit.json").write_text(
            json.dumps(case_summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        (case_output_dir / "source_acoustic_state_audit.md").write_text(
            build_case_markdown(case_summary),
            encoding="utf-8",
            newline="\n",
        )
        case_summaries.append(case_summary)

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "audit_version": "source_acoustic_state_audit_v1",
        "teacher": {
            "experiment_id": str(resolved_source["teacher_anchor"]["experiment_id"]),
            "checkpoint_path": Path(resolved_source["checkpoint_path"]).resolve().as_posix(),
            "route_handoff_path": (
                None
                if resolved_source.get("route_handoff_path") is None
                else Path(resolved_source["route_handoff_path"]).resolve().as_posix()
            ),
        },
        "runtime_alignment": {
            "frame_length": frame_length,
            "hop_length": hop_length,
        },
        "case_count": len(case_summaries),
        "cases": case_summaries,
        "aggregate": build_aggregate_summary(case_summaries),
        "notes": [
            "This audit checks the source acoustic state extraction chain on real short-form inputs before Stage5 no-res retraining.",
            "The audit uses the teacher checkpoint only to recover frame_length and hop_length so extracted controls stay aligned with the downstream contract grid.",
            "High-F0 or low-voiced-ratio cases here are calibration warnings for v2-core, not proof that the downstream contract itself is unusable.",
        ],
    }
    (output_dir / "source_acoustic_state_audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "source_acoustic_state_audit_summary.md").write_text(
        build_summary_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_input_audio_paths(input_audio_paths: list[Path]) -> list[Path]:
    if input_audio_paths:
        return [path.resolve() for path in input_audio_paths]
    return [path.resolve() for path in DEFAULT_SOURCE_ACOUSTIC_STATE_AUDIT_INPUTS]


def build_frame_start_samples(
    waveform_samples: int,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    if waveform_samples <= 0:
        return torch.zeros((0,), dtype=torch.long)
    effective_samples = max(int(frame_length), int(waveform_samples))
    frame_count = ((effective_samples - int(frame_length)) // int(hop_length)) + 1
    return torch.arange(frame_count, dtype=torch.long) * int(hop_length)


def build_case_summary(
    input_audio_path: Path,
    sample_rate: int,
    waveform_samples: int,
    frame_length: int,
    hop_length: int,
    extraction_payload: dict[str, object],
) -> dict[str, object]:
    f0_hz = extraction_payload["f0_hz"].view(-1).to(torch.float32)
    vuv = extraction_payload["vuv"].view(-1).to(torch.float32)
    aper = extraction_payload["aper"].view(-1).to(torch.float32)
    energy = extraction_payload["E"].view(-1).to(torch.float32)
    nonzero_f0_mask = f0_hz > 0.0
    high_f0_mask = f0_hz >= 400.0
    stats = dict(extraction_payload["stats"])
    return {
        "input_audio_path": input_audio_path.as_posix(),
        "audio": {
            "sample_rate": int(sample_rate),
            "waveform_samples": int(waveform_samples),
            "duration_sec": round(float(waveform_samples / max(1, sample_rate)), 6),
        },
        "runtime_alignment": {
            "frame_length": int(frame_length),
            "hop_length": int(hop_length),
            "analysis_frame_length": int(stats.get("analysis_frame_length", frame_length)),
        },
        "extraction": {
            "version": extraction_payload["version"],
            "aper_version": extraction_payload["aper_version"],
            "stats": stats,
        },
        "metrics": {
            "vuv_mean": round(float(vuv.mean().item()) if vuv.numel() > 0 else 0.0, 6),
            "vuv_q95": round(float(torch.quantile(vuv, 0.95).item()) if vuv.numel() > 0 else 0.0, 6),
            "vuv_max": round(float(vuv.max().item()) if vuv.numel() > 0 else 0.0, 6),
            "nonzero_f0_frame_count": int(nonzero_f0_mask.sum().item()),
            "nonzero_f0_ratio": round(float(nonzero_f0_mask.to(torch.float32).mean().item()) if f0_hz.numel() > 0 else 0.0, 6),
            "f0_mean_hz_nonzero": round(float(f0_hz[nonzero_f0_mask].mean().item()) if bool(nonzero_f0_mask.any().item()) else 0.0, 6),
            "f0_p50_hz_nonzero": round(float(torch.quantile(f0_hz[nonzero_f0_mask], 0.50).item()) if bool(nonzero_f0_mask.any().item()) else 0.0, 6),
            "f0_p90_hz_nonzero": round(float(torch.quantile(f0_hz[nonzero_f0_mask], 0.90).item()) if bool(nonzero_f0_mask.any().item()) else 0.0, 6),
            "f0_max_hz": round(float(f0_hz.max().item()) if f0_hz.numel() > 0 else 0.0, 6),
            "high_f0_ratio_ge_400hz": round(float(high_f0_mask.to(torch.float32).mean().item()) if f0_hz.numel() > 0 else 0.0, 6),
            "aper_mean": round(float(aper.mean().item()) if aper.numel() > 0 else 0.0, 6),
            "aper_q50": round(float(torch.quantile(aper, 0.50).item()) if aper.numel() > 0 else 0.0, 6),
            "aper_q95": round(float(torch.quantile(aper, 0.95).item()) if aper.numel() > 0 else 0.0, 6),
            "E_mean": round(float(energy.mean().item()) if energy.numel() > 0 else 0.0, 6),
            "E_q05": round(float(torch.quantile(energy, 0.05).item()) if energy.numel() > 0 else 0.0, 6),
            "E_q95": round(float(torch.quantile(energy, 0.95).item()) if energy.numel() > 0 else 0.0, 6),
        },
        "warnings": build_case_warnings(
            voiced_ratio=float(stats.get("voiced_ratio", 0.0)),
            f0_nonzero_ratio=float(nonzero_f0_mask.to(torch.float32).mean().item()) if f0_hz.numel() > 0 else 0.0,
            high_f0_ratio=float(high_f0_mask.to(torch.float32).mean().item()) if f0_hz.numel() > 0 else 0.0,
            f0_p90_hz=float(torch.quantile(f0_hz[nonzero_f0_mask], 0.90).item()) if bool(nonzero_f0_mask.any().item()) else 0.0,
        ),
    }


def build_case_warnings(
    voiced_ratio: float,
    f0_nonzero_ratio: float,
    high_f0_ratio: float,
    f0_p90_hz: float,
) -> list[str]:
    warnings: list[str] = []
    if voiced_ratio < 0.15:
        warnings.append("voiced_ratio_low")
    if f0_nonzero_ratio < 0.15:
        warnings.append("nonzero_f0_ratio_low")
    if high_f0_ratio > 0.20:
        warnings.append("high_f0_ratio_elevated")
    if f0_p90_hz > 420.0:
        warnings.append("f0_p90_too_high")
    return warnings


def build_aggregate_summary(case_summaries: list[dict[str, object]]) -> dict[str, object]:
    if not case_summaries:
        return {
            "warning_case_count": 0,
            "warning_cases": [],
        }
    voiced_ratios = [float(case["extraction"]["stats"]["voiced_ratio"]) for case in case_summaries]
    nonzero_f0_ratios = [float(case["metrics"]["nonzero_f0_ratio"]) for case in case_summaries]
    f0_p90_values = [float(case["metrics"]["f0_p90_hz_nonzero"]) for case in case_summaries]
    high_f0_ratios = [float(case["metrics"]["high_f0_ratio_ge_400hz"]) for case in case_summaries]
    warning_cases = [
        {
            "input_audio_path": case["input_audio_path"],
            "warnings": list(case["warnings"]),
        }
        for case in case_summaries
        if case["warnings"]
    ]
    return {
        "mean_voiced_ratio": round(sum(voiced_ratios) / len(voiced_ratios), 6),
        "mean_nonzero_f0_ratio": round(sum(nonzero_f0_ratios) / len(nonzero_f0_ratios), 6),
        "mean_f0_p90_hz_nonzero": round(sum(f0_p90_values) / len(f0_p90_values), 6),
        "mean_high_f0_ratio_ge_400hz": round(sum(high_f0_ratios) / len(high_f0_ratios), 6),
        "warning_case_count": len(warning_cases),
        "warning_cases": warning_cases,
    }


def build_case_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Source Acoustic State Audit Case",
        "",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- audio: {json.dumps(summary['audio'], ensure_ascii=False)}",
        f"- runtime_alignment: {json.dumps(summary['runtime_alignment'], ensure_ascii=False)}",
        f"- extraction: {json.dumps(summary['extraction'], ensure_ascii=False)}",
        f"- metrics: {json.dumps(summary['metrics'], ensure_ascii=False)}",
        f"- warnings: {json.dumps(summary['warnings'], ensure_ascii=False)}",
    ]
    return "\n".join(lines) + "\n"


def build_summary_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Source Acoustic State Audit Summary",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- audit_version: {summary['audit_version']}",
        f"- teacher: {json.dumps(summary['teacher'], ensure_ascii=False)}",
        f"- runtime_alignment: {json.dumps(summary['runtime_alignment'], ensure_ascii=False)}",
        f"- case_count: {summary['case_count']}",
        f"- aggregate: {json.dumps(summary['aggregate'], ensure_ascii=False)}",
        "",
        "## Cases",
    ]
    for case in list(summary.get("cases", [])):
        lines.append(
            f"- input_audio_path={case['input_audio_path']} "
            f"voiced_ratio={case['extraction']['stats']['voiced_ratio']} "
            f"nonzero_f0_ratio={case['metrics']['nonzero_f0_ratio']} "
            f"f0_p90_hz_nonzero={case['metrics']['f0_p90_hz_nonzero']} "
            f"warnings={json.dumps(case['warnings'], ensure_ascii=False)}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
