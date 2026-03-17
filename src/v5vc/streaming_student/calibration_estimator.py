from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import load_waveform


def estimate_streaming_student_calibration(
    config_path: Path,
    calibration_records_path: Path,
    calibration_template_path: Path,
    output_path: Path,
    report_output_dir: Path,
    frame_length: int = 1024,
    hop_length: int = 256,
) -> None:
    config_path = config_path.resolve()
    calibration_records_path = calibration_records_path.resolve()
    calibration_template_path = calibration_template_path.resolve()
    output_path = output_path.resolve()
    report_output_dir = report_output_dir.resolve()
    report_output_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    template = json.loads(calibration_template_path.read_text(encoding="utf-8"))
    records = load_jsonl(calibration_records_path)
    if not records:
        raise ValueError(f"No calibration records found: {calibration_records_path}")

    analysis = analyze_calibration_records(
        records=records,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    estimated_asset = build_estimated_asset(
        template=template,
        config=config,
        analysis=analysis,
        source_records_path=calibration_records_path,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    output_path.write_text(
        json.dumps(estimated_asset, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    report_json_path = report_output_dir / "streaming_student_calibration_estimate_summary.json"
    report_md_path = report_output_dir / "streaming_student_calibration_estimate_summary.md"
    report_json_path.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    report_md_path.write_text(
        build_markdown(
            analysis=analysis,
            estimated_asset=estimated_asset,
            output_path=output_path,
        ),
        encoding="utf-8",
        newline="\n",
    )


def analyze_calibration_records(
    records: list[dict[str, object]],
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    per_record: list[dict[str, object]] = []
    global_frames: list[torch.Tensor] = []
    total_duration_sec = 0.0

    for record in records:
        waveform, sample_rate = load_waveform(Path(record["audio_path"]), max_duration_sec=None)
        stats = analyze_waveform(
            waveform=waveform,
            sample_rate=sample_rate,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        stats["record_id"] = str(record["record_id"])
        stats["audio_path"] = str(record["audio_path"])
        stats["duration_sec"] = float(record["audio"]["duration_sec"])
        per_record.append(stats)
        total_duration_sec += float(record["audio"]["duration_sec"])
        global_frames.append(stats.pop("_selected_frames"))

    selected_frames = torch.cat(global_frames, dim=0)
    aggregate = summarize_selected_frames(selected_frames=selected_frames)
    analysis = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "record_count": len(records),
        "total_duration_sec": round(total_duration_sec, 6),
        "frame_length": frame_length,
        "hop_length": hop_length,
        "aggregate_features": aggregate,
        "records": per_record,
        "notes": [
            "This is a heuristic bootstrap estimator derived directly from calibration waveforms.",
            "The current estimate is intended to replace placeholder zero vectors, not to serve as a final calibration algorithm.",
            "alpha is a bounded scalar inferred from low-band spectral centroid and low/high energy balance.",
        ],
    }
    return analysis


def analyze_waveform(
    waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    if waveform.numel() < frame_length:
        waveform = torch.nn.functional.pad(waveform, (0, frame_length - waveform.numel()))
    frames = waveform.unfold(0, frame_length, hop_length)
    if frames.shape[0] == 0:
        frames = waveform[:frame_length].unsqueeze(0)
    window = torch.hann_window(frame_length, dtype=waveform.dtype, device=waveform.device)
    windowed = frames * window

    rms = windowed.pow(2).mean(dim=-1).sqrt()
    abs_mean = windowed.abs().mean(dim=-1)
    zero_cross = (((windowed[:, 1:] >= 0) != (windowed[:, :-1] >= 0)).to(torch.float32)).mean(dim=-1)
    frame_energy = windowed.pow(2).sum(dim=-1)
    energy_threshold = torch.quantile(frame_energy, 0.35)
    selected_mask = frame_energy >= energy_threshold
    selected_frames = windowed[selected_mask]
    if selected_frames.shape[0] == 0:
        selected_frames = windowed

    spectrum = torch.fft.rfft(selected_frames, dim=-1).abs().pow(2)
    freqs = torch.fft.rfftfreq(frame_length, d=1.0 / sample_rate).to(spectrum.device)
    total_power = spectrum.sum(dim=-1).clamp_min(1e-8)
    centroid_hz = (spectrum * freqs).sum(dim=-1) / total_power

    low_mask = freqs <= 800.0
    lowmid_mask = (freqs > 800.0) & (freqs <= 2000.0)
    mid_mask = (freqs > 2000.0) & (freqs <= 4000.0)
    high_mask = freqs > 4000.0
    low_power = spectrum[:, low_mask].sum(dim=-1)
    lowmid_power = spectrum[:, lowmid_mask].sum(dim=-1)
    mid_power = spectrum[:, mid_mask].sum(dim=-1)
    high_power = spectrum[:, high_mask].sum(dim=-1)
    voiced_like_ratio = (zero_cross < 0.12).to(torch.float32).mean()

    return {
        "sample_rate": sample_rate,
        "frame_count": int(frames.shape[0]),
        "selected_frame_count": int(selected_frames.shape[0]),
        "rms_mean": round(float(rms.mean().item()), 6),
        "abs_mean": round(float(abs_mean.mean().item()), 6),
        "zero_cross_mean": round(float(zero_cross.mean().item()), 6),
        "centroid_hz_mean": round(float(centroid_hz.mean().item()), 6),
        "low_power_ratio_mean": round(float((low_power / total_power).mean().item()), 6),
        "lowmid_power_ratio_mean": round(float((lowmid_power / total_power).mean().item()), 6),
        "mid_power_ratio_mean": round(float((mid_power / total_power).mean().item()), 6),
        "high_power_ratio_mean": round(float((high_power / total_power).mean().item()), 6),
        "voiced_like_ratio": round(float(voiced_like_ratio.item()), 6),
        "_selected_frames": selected_frames.detach().cpu(),
    }


def summarize_selected_frames(selected_frames: torch.Tensor) -> dict[str, float]:
    spectrum = torch.fft.rfft(selected_frames, dim=-1).abs().pow(2)
    frame_length = int(selected_frames.shape[-1])
    freqs = torch.fft.rfftfreq(frame_length, d=1.0 / 44100.0).to(spectrum.device)
    total_power = spectrum.sum(dim=-1).clamp_min(1e-8)
    centroid_hz = (spectrum * freqs).sum(dim=-1) / total_power

    low_mask = freqs <= 800.0
    lowmid_mask = (freqs > 800.0) & (freqs <= 2000.0)
    mid_mask = (freqs > 2000.0) & (freqs <= 4000.0)
    high_mask = freqs > 4000.0

    rms = selected_frames.pow(2).mean(dim=-1).sqrt()
    abs_mean = selected_frames.abs().mean(dim=-1)
    zero_cross = (((selected_frames[:, 1:] >= 0) != (selected_frames[:, :-1] >= 0)).to(torch.float32)).mean(dim=-1)
    low_ratio = spectrum[:, low_mask].sum(dim=-1) / total_power
    lowmid_ratio = spectrum[:, lowmid_mask].sum(dim=-1) / total_power
    mid_ratio = spectrum[:, mid_mask].sum(dim=-1) / total_power
    high_ratio = spectrum[:, high_mask].sum(dim=-1) / total_power
    low_high_ratio = spectrum[:, low_mask].sum(dim=-1) / spectrum[:, high_mask].sum(dim=-1).clamp_min(1e-8)

    return {
        "rms_mean": round(float(rms.mean().item()), 6),
        "rms_std": round(float(rms.std(unbiased=False).item()), 6),
        "abs_mean": round(float(abs_mean.mean().item()), 6),
        "zero_cross_mean": round(float(zero_cross.mean().item()), 6),
        "zero_cross_std": round(float(zero_cross.std(unbiased=False).item()), 6),
        "centroid_hz_mean": round(float(centroid_hz.mean().item()), 6),
        "centroid_hz_std": round(float(centroid_hz.std(unbiased=False).item()), 6),
        "low_ratio_mean": round(float(low_ratio.mean().item()), 6),
        "lowmid_ratio_mean": round(float(lowmid_ratio.mean().item()), 6),
        "mid_ratio_mean": round(float(mid_ratio.mean().item()), 6),
        "high_ratio_mean": round(float(high_ratio.mean().item()), 6),
        "low_high_ratio_mean": round(float(low_high_ratio.mean().item()), 6),
    }


def build_estimated_asset(
    template: dict[str, object],
    config: dict[str, object],
    analysis: dict[str, object],
    source_records_path: Path,
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    aggregate = dict(analysis["aggregate_features"])
    speaker_dim = int(config["model"]["speaker_embed_dim"])
    geom_dim = int(config["model"]["geom_embed_dim"])

    speaker_features = [
        aggregate["rms_mean"],
        aggregate["rms_std"],
        aggregate["abs_mean"],
        aggregate["zero_cross_mean"],
        aggregate["zero_cross_std"],
        aggregate["centroid_hz_mean"] / 4000.0,
        aggregate["centroid_hz_std"] / 2000.0,
        aggregate["low_ratio_mean"],
        aggregate["lowmid_ratio_mean"],
        aggregate["mid_ratio_mean"],
        aggregate["high_ratio_mean"],
        min(1.0, aggregate["low_high_ratio_mean"] / 10.0),
    ]
    speaker_vector = expand_feature_vector(speaker_features, speaker_dim)

    geom_features = [
        aggregate["low_ratio_mean"],
        aggregate["lowmid_ratio_mean"],
        aggregate["mid_ratio_mean"],
        aggregate["high_ratio_mean"],
        aggregate["centroid_hz_mean"] / 2500.0,
        aggregate["centroid_hz_std"] / 1200.0,
        aggregate["zero_cross_mean"],
        min(1.0, aggregate["low_high_ratio_mean"] / 8.0),
    ]
    geom_vector = expand_feature_vector(geom_features, geom_dim)

    alpha_value = estimate_alpha(aggregate)
    estimated_asset = dict(template)
    estimated_asset["status"] = "heuristic_bootstrap_estimated"
    estimated_asset["generated_at"] = analysis["generated_at"]
    estimated_asset["estimation_metadata"] = {
        "estimator": "waveform_feature_bootstrap_v1",
        "source_records_path": source_records_path.as_posix(),
        "frame_length": frame_length,
        "hop_length": hop_length,
        "record_count": int(analysis["record_count"]),
        "total_duration_sec": float(analysis["total_duration_sec"]),
    }
    estimated_asset["conditioning_assets"] = {
        "s_spk_target": {
            "dim": speaker_dim,
            "status": "heuristic_estimated",
            "vector": speaker_vector,
        },
        "s_geom_target": {
            "dim": geom_dim,
            "status": "heuristic_estimated",
            "vector": geom_vector,
        },
        "alpha": {
            "parameterization": "global_scalar",
            "status": "heuristic_estimated",
            "value": alpha_value,
            "suggested_bounds": [0.85, 1.15],
        },
    }
    estimated_asset["notes"] = list(template.get("notes", [])) + [
        "This asset replaces placeholder zeros with heuristic waveform-derived estimates.",
        "Treat these values as bootstrap conditioning priors until a dedicated calibration estimator exists.",
    ]
    return estimated_asset


def expand_feature_vector(features: list[float], dim: int) -> list[float]:
    values = torch.tensor(features, dtype=torch.float32)
    centered = values - values.mean()
    scale = centered.abs().max().clamp_min(1e-6)
    normalized = centered / scale
    expanded = []
    for index in range(dim):
        source = float(normalized[index % len(normalized)].item())
        phase = ((index % 4) - 1.5) / 3.0
        expanded.append(round(max(-1.0, min(1.0, source + phase * 0.1)), 6))
    return expanded


def estimate_alpha(aggregate: dict[str, float]) -> float:
    centroid_term = (float(aggregate["centroid_hz_mean"]) - 950.0) / 1400.0
    balance_term = (float(aggregate["low_ratio_mean"]) - float(aggregate["high_ratio_mean"])) * 0.35
    raw = 1.0 + centroid_term * 0.08 + balance_term
    return round(max(0.85, min(1.15, raw)), 6)


def build_markdown(
    analysis: dict[str, object],
    estimated_asset: dict[str, object],
    output_path: Path,
) -> str:
    aggregate = analysis["aggregate_features"]
    assets = estimated_asset["conditioning_assets"]
    lines = [
        "# Stage3 Streaming Student Calibration Estimate Summary",
        "",
        f"- generated_at: {analysis['generated_at']}",
        f"- record_count: {analysis['record_count']}",
        f"- total_duration_sec: {analysis['total_duration_sec']}",
        f"- output_path: {output_path.as_posix()}",
        f"- estimator: {estimated_asset['estimation_metadata']['estimator']}",
        "",
        "## Aggregate Features",
    ]
    for key, value in aggregate.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Estimated Assets",
            f"- s_spk_target_dim: {assets['s_spk_target']['dim']}",
            f"- s_spk_target_status: {assets['s_spk_target']['status']}",
            f"- s_spk_target_preview: {assets['s_spk_target']['vector'][:6]}",
            f"- s_geom_target_dim: {assets['s_geom_target']['dim']}",
            f"- s_geom_target_status: {assets['s_geom_target']['status']}",
            f"- s_geom_target_preview: {assets['s_geom_target']['vector'][:6]}",
            f"- alpha_status: {assets['alpha']['status']}",
            f"- alpha_value: {assets['alpha']['value']}",
            "",
            "## Notes",
        ]
    )
    for note in analysis["notes"]:
        lines.append(f"- {note}")
    for note in estimated_asset["notes"][-2:]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
