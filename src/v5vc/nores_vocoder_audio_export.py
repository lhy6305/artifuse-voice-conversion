from __future__ import annotations

from datetime import datetime
import json
import math
import shutil
from pathlib import Path

import torch

from v5vc.nores_vocoder_checkpoint_selection import select_offline_mvp_nores_vocoder_checkpoint
from v5vc.offline_vocoder_scaffold import NoResidualSourceFilterVocoderScaffold
from v5vc.offline_vocoder_training import (
    compute_nores_vocoder_losses,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.proxy_audio_export import compute_proxy_activity_gate, smooth_noise
from v5vc.target_format_recovery import write_waveform_int16


def export_offline_mvp_nores_vocoder_audio(
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    audit_carrier_frequency: float,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
        selection_target=selection_target,
    )
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    dataset_index_path = Path(str(checkpoint_payload["dataset_index_path"])).resolve()
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No package entries selected for no-residual vocoder audio export.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    )
    model.eval()
    branch_label = infer_branch_label(
        checkpoint_path=resolved_checkpoint_path,
        selection_summary=selection_summary,
        selection_target=selection_target,
    )

    exported_records: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
            )
            _, loss_metrics = compute_nores_vocoder_losses(
                outputs=outputs,
                harmonic_target=batch["harmonic_target"],
                noise_target=batch["noise_target"],
                periodic_gate_target=batch["periodic_gate_target"],
                noise_gate_target=batch["noise_gate_target"],
                aligned_waveform=batch["aligned_waveform"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                harmonic_weight=1.0,
                noise_weight=1.0,
                periodic_gate_weight=0.2,
                noise_gate_weight=0.2,
                waveform_weight=0.5,
                stft_weight=0.5,
                rms_guard_weight=0.2,
            )
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=outputs["waveform_frames"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
            ).cpu()
            aligned_target = batch["aligned_waveform"][: decoded_waveform.shape[0]].cpu()
            audit_proxy = synthesize_nores_vocoder_audit_proxy(
                decoded_waveform=decoded_waveform,
                aligned_target=aligned_target,
                sample_rate=int(runtime["sample_rate"]),
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                carrier_frequency=float(audit_carrier_frequency),
            )
            stem = sanitize_filename(str(entry["record_id"]))
            aligned_target_path = output_dir / f"{stem}__aligned_target.wav"
            decoded_path = output_dir / f"{stem}__decoded.wav"
            audit_proxy_path = output_dir / f"{stem}__audit_proxy.wav"
            write_waveform_int16(aligned_target_path, aligned_target, sample_rate=int(runtime["sample_rate"]))
            write_waveform_int16(decoded_path, decoded_waveform, sample_rate=int(runtime["sample_rate"]))
            write_waveform_int16(audit_proxy_path, audit_proxy, sample_rate=int(runtime["sample_rate"]))
            exported_records.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "target_audio_path": str(payload.get("target_audio_path")),
                    "sample_rate": int(runtime["sample_rate"]),
                    "aligned_target_audio_path": aligned_target_path.as_posix(),
                    "decoded_audio_path": decoded_path.as_posix(),
                    "audit_proxy_audio_path": audit_proxy_path.as_posix(),
                    "audio_path": str(payload.get("target_audio_path")),
                    "input_audio_path": aligned_target_path.as_posix(),
                    "proxy_audio_path": audit_proxy_path.as_posix(),
                    "loss_metrics": loss_metrics,
                }
            )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "branch_label": branch_label,
        "audit_render": {
            "mode": "low_frequency_proxy_from_decoded_waveform",
            "carrier_frequency_hz": float(audit_carrier_frequency),
            "silence_gate_reference": "aligned_target",
        },
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if selection_summary is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if selection_summary is None else str(selection_target),
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(exported_records),
        "records": exported_records,
        "notes": [
            "aligned_target.wav is the frame-aligned target waveform used by the current Stage5 bootstrap objective.",
            "decoded.wav is reconstructed from the checkpoint's waveform_frames head via overlap-add with the training-time frame and hop settings.",
            "audit_proxy.wav is a low-frequency audit render derived from decoded.wav and gated by aligned_target activity so current GUI listening is less fatiguing and target silence remains silent.",
            "proxy_audio_path in the GUI-compatible manifest points to audit_proxy.wav by default; decoded.wav is retained for raw technical inspection.",
            "This export is for human listening and checkpoint comparison; it is still not the final multi-resolution or adversarial vocoder route from the design doc.",
        ],
    }
    (output_dir / "nores_vocoder_audio_export.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "nores_vocoder_audio_export.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    proxy_summary = build_proxy_audio_export_summary(summary)
    (output_dir / "proxy_audio_export.json").write_text(
        json.dumps(proxy_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "proxy_audio_export.md").write_text(
        build_proxy_audio_export_markdown(proxy_summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_checkpoint_path_from_inputs(
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
) -> tuple[Path, dict[str, object] | None]:
    if checkpoint_path is not None:
        return checkpoint_path.resolve(), None
    if checkpoint_selection_path is None:
        raise ValueError("Either checkpoint_path or checkpoint_selection_path is required.")
    payload = json.loads(checkpoint_selection_path.resolve().read_text(encoding="utf-8"))
    target_key = normalize_selection_target(selection_target)
    selected = payload.get(target_key)
    if not isinstance(selected, dict) or "step" not in selected:
        raise ValueError(f"checkpoint selection payload does not contain {target_key!r}.")
    summary_path = Path(str(payload["summary_path"])).resolve()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    checkpoint_paths = summary.get("artifacts", {}).get("checkpoint_paths", [])
    selected_step = int(selected["step"])
    matched_path = None
    for item in checkpoint_paths:
        item_path = Path(str(item))
        stem = item_path.stem
        if stem.endswith(f".step{selected_step}"):
            matched_path = item_path.resolve()
            break
    if matched_path is None:
        raise ValueError(f"Unable to resolve checkpoint path for selected step {selected_step}.")
    return matched_path, dict(selected)


def normalize_selection_target(selection_target: str) -> str:
    normalized = str(selection_target).strip().lower()
    mapping = {
        "stable_late_stop": "selected_stable_late_stop",
        "best_validation": "best_validation_checkpoint",
        "best_rms": "best_rms_checkpoint",
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported selection_target: {selection_target}")
    return mapping[normalized]


def resolve_package_entries(
    dataset_index: dict[str, object],
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    normalized_split = str(split_name).strip().lower()
    if normalized_split == "validation":
        entries = list(dataset_index.get("validation_packages", []))
    elif normalized_split == "train":
        entries = list(dataset_index.get("train_packages", []))
    else:
        raise ValueError(f"Unsupported split_name: {split_name}")
    if target_record_ids:
        entry_map = {str(entry["record_id"]): entry for entry in entries}
        selected = []
        missing = []
        for record_id in target_record_ids:
            match = entry_map.get(str(record_id))
            if match is None:
                missing.append(str(record_id))
                continue
            selected.append(match)
        if missing:
            raise ValueError(f"Unknown target_record_ids: {missing}")
        return selected
    if sample_count <= 0:
        raise ValueError("sample_count must be positive.")
    if len(entries) <= sample_count:
        return entries
    if sample_count == 1:
        return [entries[0]]
    indices: list[int] = []
    max_index = len(entries) - 1
    for index in range(sample_count):
        candidate = round(index * max_index / (sample_count - 1))
        if candidate not in indices:
            indices.append(candidate)
    while len(indices) < sample_count:
        for candidate in range(len(entries)):
            if candidate not in indices:
                indices.append(candidate)
            if len(indices) >= sample_count:
                break
    return [entries[index] for index in indices[:sample_count]]


def build_model_from_checkpoint(
    checkpoint_payload: dict[str, object],
    first_batch: dict[str, torch.Tensor],
    first_runtime: dict[str, int],
) -> NoResidualSourceFilterVocoderScaffold:
    state_dict = dict(checkpoint_payload["model_state_dict"])
    hidden_dim = int(state_dict["periodic_encoder.0.weight"].shape[0])
    harmonic_bins = int(state_dict["harmonic_envelope.weight"].shape[0])
    noise_bins = int(state_dict["noise_envelope.weight"].shape[0])
    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(first_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(first_batch["noise_branch_features"].shape[-1]),
        hidden_dim=hidden_dim,
        harmonic_bins=harmonic_bins,
        noise_bins=noise_bins,
        frame_length=int(first_runtime["frame_length"]),
    )
    model.load_state_dict(state_dict)
    return model


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(value: str) -> str:
    sanitized = [
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in value
    ]
    return "".join(sanitized).strip("_") or "sample"


def synthesize_nores_vocoder_audit_proxy(
    decoded_waveform: torch.Tensor,
    aligned_target: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    carrier_frequency: float,
) -> torch.Tensor:
    if decoded_waveform.numel() == 0:
        return torch.zeros_like(aligned_target)
    total_length = int(min(decoded_waveform.shape[0], aligned_target.shape[0]))
    if total_length <= 0:
        return torch.zeros_like(aligned_target)
    decoded = decoded_waveform[:total_length].to(torch.float32)
    target = aligned_target[:total_length].to(torch.float32)
    frame_count = max(1, math.ceil(max(1, total_length - frame_length) / hop_length) + 1)
    output = torch.zeros(total_length, dtype=torch.float32)
    weights = torch.zeros(total_length, dtype=torch.float32)
    window = torch.hann_window(frame_length, periodic=False, dtype=torch.float32)
    generator = torch.Generator()
    generator.manual_seed(20260318)
    phase = 0.0
    previous_rms = 0.0
    phase_increment = 2.0 * math.pi * float(carrier_frequency) / int(sample_rate)

    for frame_index in range(frame_count):
        start = int(frame_index * hop_length)
        end = start + int(frame_length)
        decoded_frame = slice_or_pad_waveform(decoded, start=start, end=end)
        target_frame = slice_or_pad_waveform(target, start=start, end=end)
        target_rms = float(target_frame.pow(2).mean().sqrt().item())
        target_abs = float(target_frame.abs().mean().item())
        activity_gate = compute_proxy_activity_gate(
            rms_target=target_rms,
            abs_target=target_abs,
        )
        phase_positions = phase + phase_increment * torch.arange(frame_length, dtype=torch.float32)
        phase = float((phase + frame_length * phase_increment) % (2.0 * math.pi))
        if activity_gate <= 1.0e-4:
            continue
        decoded_rms = float(decoded_frame.pow(2).mean().sqrt().item())
        decoded_abs = float(decoded_frame.abs().mean().item())
        zero_cross = compute_zero_cross_ratio(decoded_frame)
        delta_energy = max(-0.5, min(0.5, (decoded_rms - previous_rms) * 8.0))
        previous_rms = decoded_rms
        brightness = 1.0 / (1.0 + math.exp(-((zero_cross - 0.12) / 0.04)))
        noise_mix = (0.02 + 0.08 * brightness) * activity_gate
        harmonic_mix = (0.08 + 0.10 * min(max(decoded_abs / 0.18, 0.0), 1.0)) * activity_gate
        tone = (
            0.92 * torch.sin(phase_positions)
            + harmonic_mix * torch.sin(phase_positions * 2.0 + 0.17)
            + 0.02 * brightness * torch.sin(phase_positions * 3.0 + 0.31)
        )
        noise = torch.randn(frame_length, generator=generator, dtype=torch.float32)
        noise = smooth_noise(noise=noise, passes=8)
        noise = noise / noise.std().clamp_min(1.0e-6)
        frame = (1.0 - noise_mix) * tone + noise_mix * noise
        frame = frame / frame.pow(2).mean().sqrt().clamp_min(1.0e-6)
        frame = frame * max(0.0, min(decoded_rms, 0.35))
        ramp = torch.linspace(-0.5, 0.5, frame_length, dtype=torch.float32)
        frame = frame * (1.0 + delta_energy * 0.20 * ramp).clamp(min=0.8, max=1.2)
        frame = frame * activity_gate
        frame = frame.clamp(-1.0, 1.0)
        output_start = start
        output_end = min(end, total_length)
        valid_length = output_end - output_start
        if valid_length <= 0:
            continue
        output[output_start:output_end] += frame[:valid_length] * window[:valid_length]
        weights[output_start:output_end] += window[:valid_length]

    output = output / weights.clamp_min(1.0e-6)
    output = smooth_noise(noise=output, passes=4)
    peak = float(output.abs().max().item()) if output.numel() > 0 else 0.0
    if peak > 0.98:
        output = output * float(0.98 / peak)
    return output.clamp(-1.0, 1.0)


def slice_or_pad_waveform(
    waveform: torch.Tensor,
    start: int,
    end: int,
) -> torch.Tensor:
    frame_length = int(end - start)
    if frame_length <= 0:
        return waveform.new_zeros((0,))
    if start >= int(waveform.shape[0]):
        return waveform.new_zeros((frame_length,))
    sliced = waveform[start:min(end, int(waveform.shape[0]))]
    if int(sliced.shape[0]) >= frame_length:
        return sliced[:frame_length]
    padded = waveform.new_zeros((frame_length,))
    padded[: int(sliced.shape[0])] = sliced
    return padded


def compute_zero_cross_ratio(waveform: torch.Tensor) -> float:
    if waveform.numel() <= 1:
        return 0.0
    previous = waveform[:-1]
    current = waveform[1:]
    return float(((previous * current) < 0.0).to(torch.float32).mean().item())


def infer_branch_label(
    checkpoint_path: Path,
    selection_summary: dict[str, object] | None,
    selection_target: str,
) -> str:
    if selection_summary is not None:
        selected_step = selection_summary.get("step")
        if selected_step is not None:
            return f"stage5_{selection_target}_step{int(selected_step)}"
    return checkpoint_path.stem


def build_proxy_audio_export_summary(summary: dict[str, object]) -> dict[str, object]:
    records = []
    for record in summary["records"]:
        records.append(
            {
                "record_id": record["record_id"],
                "audio_path": record["audio_path"],
                "sample_rate": record["sample_rate"],
                "input_audio_path": record["input_audio_path"],
                "proxy_audio_path": record["proxy_audio_path"],
                "loss_metrics": record["loss_metrics"],
            }
        )
    return {
        "generated_at": summary["generated_at"],
        "export_type": "stage5_nores_vocoder_audio_export",
        "branch_label": summary["branch_label"],
        "checkpoint_path": summary["checkpoint_path"],
        "checkpoint_selection_path": summary["checkpoint_selection_path"],
        "selection_target": summary["selection_target"],
        "selected_checkpoint_summary": summary["selected_checkpoint_summary"],
        "audit_render": summary.get("audit_render"),
        "dataset_index_path": summary["dataset_index_path"],
        "split_name": summary["split_name"],
        "sample_count": summary["sample_count"],
        "records": records,
        "notes": summary["notes"],
    }


def build_proxy_audio_export_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Audio Audit Bundle",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- branch_label: {summary['branch_label']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- audit_render: {json.dumps(summary.get('audit_render'), ensure_ascii=False)}",
        f"- sample_count: {summary['sample_count']}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"input_audio_path={record['input_audio_path']} "
            f"proxy_audio_path={record['proxy_audio_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Audio Export",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
        f"- audit_render: {json.dumps(summary.get('audit_render'), ensure_ascii=False)}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(
            f"- record_id={record['record_id']} "
            f"loss_total={record['loss_metrics']['loss_total']} "
            f"aligned_target_audio_path={record['aligned_target_audio_path']} "
            f"decoded_audio_path={record['decoded_audio_path']} "
            f"audit_proxy_audio_path={record.get('audit_proxy_audio_path')}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
