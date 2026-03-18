from __future__ import annotations

from datetime import datetime
import json
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
from v5vc.target_format_recovery import write_waveform_int16


def export_offline_mvp_nores_vocoder_audio(
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
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
            stem = sanitize_filename(str(entry["record_id"]))
            aligned_target_path = output_dir / f"{stem}__aligned_target.wav"
            decoded_path = output_dir / f"{stem}__decoded.wav"
            write_waveform_int16(aligned_target_path, aligned_target, sample_rate=int(runtime["sample_rate"]))
            write_waveform_int16(decoded_path, decoded_waveform, sample_rate=int(runtime["sample_rate"]))
            exported_records.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "target_audio_path": str(payload.get("target_audio_path")),
                    "sample_rate": int(runtime["sample_rate"]),
                    "aligned_target_audio_path": aligned_target_path.as_posix(),
                    "decoded_audio_path": decoded_path.as_posix(),
                    "loss_metrics": loss_metrics,
                }
            )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
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


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Residual Vocoder Audio Export",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
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
            f"decoded_audio_path={record['decoded_audio_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
