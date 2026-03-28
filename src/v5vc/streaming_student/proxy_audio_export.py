from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
import math
from pathlib import Path

import torch

from v5vc.proxy_audio_export import (
    match_audit_waveform_loudness,
    sanitize_filename,
    synthesize_proxy_waveform,
)
from v5vc.streaming_student.proxy_acoustic import build_streaming_student_proxy_acoustic_for_export
from v5vc.streaming_student.data import (
    load_streaming_student_conditioning_asset,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold
from v5vc.target_format_recovery import write_waveform_int16


def export_streaming_student_proxy_audio(
    checkpoint_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    branch_label: str | None,
    max_audio_sec: float | None,
) -> dict[str, object]:
    checkpoint_path = checkpoint_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = payload.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"Checkpoint missing config payload: {checkpoint_path}")
    config_path = Path(str(payload.get("config_path", "configs/streaming_student_stage_template.json")))
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()

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
    if not selected_records:
        raise ValueError("No target records selected for Stage3 proxy audio export.")

    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.load_state_dict(payload["model_state_dict"])
    model.eval()

    effective_max_audio_sec = None if max_audio_sec is None else float(max_audio_sec)
    checkpoint_experiment_id = str(payload.get("experiment_id", checkpoint_path.stem))
    effective_branch_label = branch_label or checkpoint_experiment_id

    exported_records: list[dict[str, object]] = []
    notes = [
        "Student proxy audio is reconstructed from Stage3 predicted control heads using a conservative structural mapping.",
        "Teacher proxy audio is reconstructed from exported teacher acoustic labels for the same record and time span.",
        "These files are structural audit proxies only, not full vocoder outputs or final runtime-quality inference audio.",
        "Current Stage3 proxy synthesis stays de-pitched and low-frequency on purpose so listening focuses on pause, energy, and stability.",
        "Teacher and student proxy wav files are loudness-matched per record before export so human review is less biased by global volume differences.",
    ]

    with torch.no_grad():
        for record in selected_records:
            example = load_streaming_student_target_examples_from_records([record])[0]
            waveform = example.waveform
            if effective_max_audio_sec is not None:
                max_samples = max(1, int(round(example.sample_rate * effective_max_audio_sec)))
                waveform = waveform[:max_samples].contiguous()
            lengths = torch.tensor([waveform.numel()], dtype=torch.long)
            waveform_batch = waveform.unsqueeze(0)
            speaker_embedding = conditioning_asset["speaker_embedding"].unsqueeze(0).to(torch.float32)
            geom_embedding = conditioning_asset["geom_embedding"].unsqueeze(0).to(torch.float32)
            outputs = model(
                waveform=waveform_batch,
                lengths=lengths,
                speaker_embedding=speaker_embedding,
                geom_embedding=geom_embedding,
            )
            student_proxy_acoustic = build_streaming_student_proxy_acoustic_for_export(outputs=outputs)[0]
            student_frame_mask = outputs["frame_mask"][0].to(torch.bool).cpu()
            student_frame_count = int(student_frame_mask.sum().item())
            teacher_frame_count = min(student_frame_count, int(example.teacher_frame_mask.sum().item()))
            if teacher_frame_count <= 0:
                raise ValueError(f"Teacher proxy export encountered zero valid frames for {example.record_id}")
            student_proxy_waveform = synthesize_proxy_waveform(
                acoustic=student_proxy_acoustic[:teacher_frame_count].cpu(),
                frame_mask=student_frame_mask[:teacher_frame_count],
                sample_rate=int(example.sample_rate),
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
            )
            teacher_proxy_waveform = synthesize_proxy_waveform(
                acoustic=example.teacher_acoustic[:teacher_frame_count].cpu(),
                frame_mask=torch.ones(teacher_frame_count, dtype=torch.bool),
                sample_rate=int(example.sample_rate),
                frame_length=int(config["model"]["frame_length"]),
                hop_length=int(config["model"]["hop_length"]),
            )
            matched_waveforms, loudness_metadata = match_audit_waveform_loudness(
                {
                    "teacher_proxy": teacher_proxy_waveform,
                    "student_proxy": student_proxy_waveform,
                }
            )
            teacher_proxy_waveform = matched_waveforms["teacher_proxy"]
            student_proxy_waveform = matched_waveforms["student_proxy"]
            stem = sanitize_filename(f"{effective_branch_label}__{example.record_id}")
            input_path = output_dir / f"{stem}__input.wav"
            teacher_proxy_path = output_dir / f"{stem}__teacher_proxy.wav"
            student_proxy_path = output_dir / f"{stem}__student_proxy.wav"
            write_waveform_int16(input_path, waveform.cpu(), sample_rate=int(example.sample_rate))
            write_waveform_int16(teacher_proxy_path, teacher_proxy_waveform, sample_rate=int(example.sample_rate))
            write_waveform_int16(student_proxy_path, student_proxy_waveform, sample_rate=int(example.sample_rate))
            exported_records.append(
                {
                    "record_id": example.record_id,
                    "split_name": normalized_split_name,
                    "audio_path": str(example.audio_path),
                    "sample_rate": int(example.sample_rate),
                    "input_audio_path": input_path.as_posix(),
                    "teacher_proxy_audio_path": teacher_proxy_path.as_posix(),
                    "student_proxy_audio_path": student_proxy_path.as_posix(),
                    "teacher_frame_count": teacher_frame_count,
                    "student_frame_count": student_frame_count,
                    "proxy_loudness_matching": loudness_metadata,
                }
            )

    result = {
        "checkpoint_path": checkpoint_path.as_posix(),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "split_dir": split_summary["split_dir"],
        "split_name": normalized_split_name,
        "branch_label": effective_branch_label,
        "sample_count": len(exported_records),
        "max_audio_sec": effective_max_audio_sec,
        "records": exported_records,
        "notes": notes,
    }
    (output_dir / "proxy_audio_export.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "proxy_audio_export.md").write_text(
        build_markdown(result),
        encoding="utf-8",
        newline="\n",
    )
    return result



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
def build_markdown(result: dict[str, object]) -> str:
    lines = [
        "# Stage3 streaming_student proxy audio export",
        "",
        f"- branch_label: {result['branch_label']}",
        f"- checkpoint_path: {result['checkpoint_path']}",
        f"- config_path: {result['config_path']}",
        f"- teacher_label_index_path: {result['teacher_label_index_path']}",
        f"- calibration_asset_path: {result['calibration_asset_path']}",
        f"- split_dir: {result['split_dir']}",
        f"- split_name: {result['split_name']}",
        f"- sample_count: {result['sample_count']}",
        f"- max_audio_sec: {result['max_audio_sec']}",
        "",
        "## records",
    ]
    for record in result["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- audio_path: {record['audio_path']}")
        lines.append(f"- input_audio_path: {record['input_audio_path']}")
        lines.append(f"- teacher_proxy_audio_path: {record['teacher_proxy_audio_path']}")
        lines.append(f"- student_proxy_audio_path: {record['student_proxy_audio_path']}")
        lines.append(f"- teacher_frame_count: {record['teacher_frame_count']}")
        lines.append(f"- student_frame_count: {record['student_frame_count']}")
        loudness = record.get("proxy_loudness_matching")
        if isinstance(loudness, dict):
            teacher_loudness = loudness.get("teacher_proxy")
            student_loudness = loudness.get("student_proxy")
            if isinstance(teacher_loudness, dict):
                lines.append(
                    "- teacher_proxy_loudness:"
                    f" before={teacher_loudness.get('rms_dbfs_before')} dBFS"
                    f", after={teacher_loudness.get('rms_dbfs_after')} dBFS"
                    f", gain={teacher_loudness.get('gain_db_applied')} dB"
                )
            if isinstance(student_loudness, dict):
                lines.append(
                    "- student_proxy_loudness:"
                    f" before={student_loudness.get('rms_dbfs_before')} dBFS"
                    f", after={student_loudness.get('rms_dbfs_after')} dBFS"
                    f", gain={student_loudness.get('gain_db_applied')} dB"
                )
        lines.append("")
    lines.extend(["## notes"])
    for note in result["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
