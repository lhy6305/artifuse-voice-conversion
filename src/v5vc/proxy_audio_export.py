from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
import math
from pathlib import Path

import torch

from v5vc.ablation_eval import build_model_from_config, load_checkpoint, resolve_checkpoint_path, resolve_split_dir
from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import load_source_examples_from_records
from v5vc.target_format_recovery import write_waveform_int16


def export_offline_mvp_proxy_audio(
    config_path: Path,
    split_dir: Path | None,
    output_dir: Path,
    experiment_metrics_path: Path | None,
    checkpoint_path: Path | None,
    source_manifest_path: Path | None,
    source_record_ids: list[str] | None,
    sample_count: int,
    branch_label: str | None,
    max_audio_sec: float | None,
) -> dict[str, object]:
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    project_root = config_path.parent.parent
    resolved_split_dir = resolve_split_dir(project_root=project_root, config=config, split_dir=split_dir)
    resolved_checkpoint_path = resolve_checkpoint_path(
        checkpoint_path=checkpoint_path,
        experiment_metrics_path=experiment_metrics_path,
    )
    resolved_source_manifest = resolve_source_manifest(
        split_dir=resolved_split_dir,
        source_manifest_path=source_manifest_path,
    )
    source_records = load_jsonl(resolved_source_manifest)
    selected_records = select_source_records(
        records=source_records,
        sample_count=sample_count,
        source_record_ids=source_record_ids,
    )
    if not selected_records:
        raise ValueError("No source records selected for proxy audio export.")

    effective_max_audio_sec = (
        float(max_audio_sec)
        if max_audio_sec is not None
        else float(config["data"]["max_audio_sec"])
    )
    examples = load_source_examples_from_records(
        records=selected_records,
        max_duration_sec=effective_max_audio_sec,
    )

    model = build_model_from_config(config)
    checkpoint = load_checkpoint(resolved_checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    branch_name = branch_label or infer_branch_label(
        experiment_metrics_path=experiment_metrics_path,
        checkpoint_path=resolved_checkpoint_path,
    )
    exported_records: list[dict[str, object]] = []
    notes = [
        "Proxy audio is reconstructed from the model's predicted acoustic features only.",
        "This is a human-audit proxy, not a full vocoder or final runtime-quality waveform.",
        "Current synthesis uses a de-pitched low-frequency envelope proxy; audible carrier pitch is normalized across branches.",
        "Input and proxy audio are exported together to support relative listening checks.",
    ]

    with torch.no_grad():
        for example in examples:
            waveform = example.waveform.unsqueeze(0)
            lengths = torch.tensor([example.waveform.numel()], dtype=torch.long)
            outputs = model(
                waveform=waveform,
                lengths=lengths,
            )
            proxy_waveform = synthesize_proxy_waveform(
                acoustic=outputs["acoustic"][0],
                frame_mask=outputs["frame_mask"][0],
                sample_rate=int(example.sample_rate),
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
            )
            stem = sanitize_filename(f"{branch_name}__{example.record_id}")
            input_path = output_dir / f"{stem}__input.wav"
            proxy_path = output_dir / f"{stem}__proxy.wav"
            write_waveform_int16(input_path, example.waveform, sample_rate=int(example.sample_rate))
            write_waveform_int16(proxy_path, proxy_waveform, sample_rate=int(example.sample_rate))
            exported_records.append(
                {
                    "record_id": example.record_id,
                    "audio_path": str(example.audio_path),
                    "sample_rate": int(example.sample_rate),
                    "input_audio_path": input_path.as_posix(),
                    "proxy_audio_path": proxy_path.as_posix(),
                }
            )

    result = {
        "config_path": config_path.as_posix(),
        "split_dir": resolved_split_dir.as_posix(),
        "source_manifest_path": resolved_source_manifest.as_posix(),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "experiment_metrics_path": experiment_metrics_path.resolve().as_posix()
        if experiment_metrics_path is not None
        else None,
        "branch_label": branch_name,
        "sample_count": len(exported_records),
        "max_audio_sec": effective_max_audio_sec,
        "records": exported_records,
        "notes": notes,
    }
    (output_dir / "proxy_audio_export.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "proxy_audio_export.md").write_text(
        build_markdown(result),
        encoding="utf-8",
        newline="\n",
    )
    return result



def resolve_source_manifest(
    split_dir: Path,
    source_manifest_path: Path | None,
) -> Path:
    if source_manifest_path is not None:
        return source_manifest_path.resolve()
    validation_manifest = (split_dir / "source_validation.jsonl").resolve()
    if validation_manifest.exists():
        return validation_manifest
    return (split_dir / "source_train.jsonl").resolve()


def select_source_records(
    records: list[dict[str, object]],
    sample_count: int,
    source_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    if source_record_ids:
        record_map = {str(record["record_id"]): record for record in records}
        selected: list[dict[str, object]] = []
        missing: list[str] = []
        for record_id in source_record_ids:
            record = record_map.get(record_id)
            if record is None:
                missing.append(record_id)
                continue
            selected.append(record)
        if missing:
            raise ValueError(f"Unknown source_record_ids: {missing}")
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


def infer_branch_label(
    experiment_metrics_path: Path | None,
    checkpoint_path: Path,
) -> str:
    if experiment_metrics_path is not None:
        payload = json.loads(experiment_metrics_path.resolve().read_text(encoding="utf-8"))
        experiment_id = payload.get("experiment_id")
        if isinstance(experiment_id, str) and experiment_id:
            return experiment_id
    return checkpoint_path.stem


def synthesize_proxy_waveform(
    acoustic: torch.Tensor,
    frame_mask: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> torch.Tensor:
    masked = acoustic[frame_mask]
    if masked.numel() == 0:
        return torch.zeros(frame_length, dtype=torch.float32)

    frame_count = int(masked.shape[0])
    total_length = (frame_count - 1) * hop_length + frame_length
    output = torch.zeros(total_length, dtype=torch.float32)
    weights = torch.zeros(total_length, dtype=torch.float32)
    window = torch.hann_window(frame_length, periodic=False, dtype=torch.float32)
    phase = 0.0
    generator = torch.Generator()
    generator.manual_seed(20260315)
    carrier_frequency = 185.0

    for frame_index in range(frame_count):
        energy_log, abs_mean, zero_cross, delta_energy = [
            float(value) for value in masked[frame_index].tolist()
        ]
        raw_rms_target = math.sqrt(max(1.0e-8, 10.0 ** energy_log))
        raw_abs_target = max(abs_mean, 0.0)
        activity_gate = compute_proxy_activity_gate(
            rms_target=raw_rms_target,
            abs_target=raw_abs_target,
        )
        rms_target = min(max(raw_rms_target, 0.0), 0.6)
        abs_target = min(max(raw_abs_target, 0.0), 0.6)
        zero_cross = min(max(zero_cross, 0.0), 0.95)
        delta_energy = min(max(delta_energy, -0.5), 0.5)
        if activity_gate <= 1.0e-4:
            phase_increment = 2.0 * math.pi * carrier_frequency / sample_rate
            phase = float((phase + frame_length * phase_increment) % (2.0 * math.pi))
            continue
        brightness = 1.0 / (1.0 + math.exp(-((zero_cross - 0.12) / 0.04)))
        noise_mix = (0.04 + 0.12 * brightness) * activity_gate
        harmonic_mix = (0.12 + 0.12 * min(max(abs_target / 0.22, 0.0), 1.0)) * activity_gate

        phase_increment = 2.0 * math.pi * carrier_frequency / sample_rate
        phase_positions = phase + phase_increment * torch.arange(frame_length, dtype=torch.float32)
        tone = (
            0.9 * torch.sin(phase_positions)
            + harmonic_mix * torch.sin(phase_positions * 2.0 + 0.17)
            + 0.03 * brightness * torch.sin(phase_positions * 3.0 + 0.31)
        )
        noise = torch.randn(frame_length, generator=generator, dtype=torch.float32)
        noise = smooth_noise(noise=noise, passes=8)
        noise = noise / noise.std().clamp_min(1.0e-6)
        frame = (1.0 - noise_mix) * tone + noise_mix * noise

        frame = frame / frame.pow(2).mean().sqrt().clamp_min(1.0e-6)
        frame = frame * rms_target
        current_abs = frame.abs().mean().clamp_min(1.0e-6)
        abs_scale = abs_target / float(current_abs.item())
        frame = frame * float(max(0.0, min(abs_scale, 1.8)))
        ramp = torch.linspace(-0.5, 0.5, frame_length, dtype=torch.float32)
        frame = frame * (1.0 + delta_energy * 0.35 * ramp).clamp(min=0.65, max=1.35)
        frame = frame * activity_gate
        frame = frame.clamp(-1.0, 1.0)

        start = frame_index * hop_length
        end = start + frame_length
        output[start:end] += frame * window
        weights[start:end] += window
        phase = float((phase + frame_length * phase_increment) % (2.0 * math.pi))

    output = output / weights.clamp_min(1.0e-6)
    output = smooth_noise(noise=output, passes=5)
    peak = float(output.abs().max().item())
    if peak > 0.98:
        output = output * (0.98 / peak)
    return output.clamp(-1.0, 1.0)


def compute_proxy_activity_gate(
    rms_target: float,
    abs_target: float,
    *,
    silence_floor: float = 0.002,
    active_floor: float = 0.012,
) -> float:
    activity = max(float(rms_target), float(abs_target))
    if activity <= silence_floor:
        return 0.0
    if activity >= active_floor:
        return 1.0
    return (activity - silence_floor) / (active_floor - silence_floor)


def match_audit_waveform_loudness(
    waveforms: dict[str, torch.Tensor],
    *,
    peak_limit: float = 0.98,
    max_gain_db: float = 12.0,
) -> tuple[dict[str, torch.Tensor], dict[str, dict[str, float | bool]]]:
    valid_rms_values = [
        max(float(compute_waveform_rms(waveform)), 1.0e-8)
        for waveform in waveforms.values()
        if waveform.numel() > 0
    ]
    if not valid_rms_values:
        return dict(waveforms), {}

    target_rms = math.exp(sum(math.log(value) for value in valid_rms_values) / len(valid_rms_values))
    max_gain_scale = 10.0 ** (max_gain_db / 20.0)
    matched: dict[str, torch.Tensor] = {}
    metadata: dict[str, dict[str, float | bool]] = {}

    for name, waveform in waveforms.items():
        rms_before = float(compute_waveform_rms(waveform))
        peak_before = float(waveform.abs().max().item()) if waveform.numel() > 0 else 0.0
        requested_scale = target_rms / max(rms_before, 1.0e-8)
        scale = min(max(requested_scale, 1.0 / max_gain_scale), max_gain_scale)
        clipped_by_gain_cap = not math.isclose(scale, requested_scale, rel_tol=1.0e-6, abs_tol=1.0e-6)

        adjusted = waveform * float(scale)
        adjusted_peak = float(adjusted.abs().max().item()) if adjusted.numel() > 0 else 0.0
        if adjusted_peak > peak_limit:
            adjusted = adjusted * float(peak_limit / adjusted_peak)
            clipped_by_peak_limit = True
        else:
            clipped_by_peak_limit = False

        rms_after = float(compute_waveform_rms(adjusted))
        peak_after = float(adjusted.abs().max().item()) if adjusted.numel() > 0 else 0.0
        matched[name] = adjusted.clamp(-1.0, 1.0)
        metadata[name] = {
            "rms_dbfs_before": round(rms_to_dbfs(rms_before), 6),
            "rms_dbfs_after": round(rms_to_dbfs(rms_after), 6),
            "peak_before": round(peak_before, 6),
            "peak_after": round(peak_after, 6),
            "gain_db_requested": round(scale_to_db(requested_scale), 6),
            "gain_db_applied": round(scale_to_db(max(rms_after, 1.0e-8) / max(rms_before, 1.0e-8)), 6),
            "clipped_by_gain_cap": clipped_by_gain_cap,
            "clipped_by_peak_limit": clipped_by_peak_limit,
        }
    return matched, metadata


def compute_waveform_rms(waveform: torch.Tensor) -> float:
    if waveform.numel() == 0:
        return 0.0
    return float(waveform.to(torch.float32).pow(2).mean().sqrt().item())


def rms_to_dbfs(rms: float) -> float:
    return 20.0 * math.log10(max(float(rms), 1.0e-8))


def scale_to_db(scale: float) -> float:
    return 20.0 * math.log10(max(float(scale), 1.0e-8))


def smooth_noise(noise: torch.Tensor, passes: int) -> torch.Tensor:
    smoothed = noise
    for _ in range(max(0, passes)):
        previous = torch.cat([smoothed[:1], smoothed[:-1]])
        next_value = torch.cat([smoothed[1:], smoothed[-1:]])
        smoothed = 0.2 * previous + 0.6 * smoothed + 0.2 * next_value
    return smoothed


def sanitize_filename(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            safe.append(char)
        else:
            safe.append("_")
    return "".join(safe)


def build_markdown(result: dict[str, object]) -> str:
    lines = [
        "# offline MVP proxy audio export",
        "",
        f"- branch_label: {result['branch_label']}",
        f"- config_path: {result['config_path']}",
        f"- checkpoint_path: {result['checkpoint_path']}",
        f"- source_manifest_path: {result['source_manifest_path']}",
        f"- sample_count: {result['sample_count']}",
        f"- max_audio_sec: {result['max_audio_sec']}",
        "",
        "## records",
    ]
    for record in result["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- audio_path: {record['audio_path']}")
        lines.append(f"- input_audio_path: {record['input_audio_path']}")
        lines.append(f"- proxy_audio_path: {record['proxy_audio_path']}")
        lines.append("")
    lines.extend(["## notes"])
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
