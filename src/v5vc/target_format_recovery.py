from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
import shutil
import wave
from pathlib import Path

import torch
import torch.nn.functional as F

from v5vc.data_scan import read_wav_metadata, summarize_numeric, write_json, write_manifest

PUNCTUATION_SET = set("，。？！；：、")


def recover_round1_target_formats(
    input_dir: Path,
    output_dir: Path,
    report_output_dir: Path,
    target_sample_rate: int,
    target_channels: int,
    keep_no_text_voice_isolated: bool,
) -> None:
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()
    report_output_dir = report_output_dir.resolve()

    train_manifest = load_jsonl(input_dir / "manifest_round1_train.jsonl")
    excluded_manifest = load_jsonl(input_dir / "manifest_round1_excluded.jsonl")
    raw_firefly_dir = infer_raw_firefly_dir(input_dir)

    reset_managed_directory(output_dir)
    reset_managed_directory(report_output_dir)
    copy_existing_labels(input_dir / "labels", output_dir / "labels")

    recovered_records: list[dict[str, object]] = []
    remaining_excluded: list[dict[str, object]] = []
    failed_records: list[dict[str, object]] = []

    for record in excluded_manifest:
        if not should_recover_record(record, keep_no_text_voice_isolated=keep_no_text_voice_isolated):
            remaining_excluded.append(record)
            continue
        try:
            recovered_records.append(
                recover_record(
                    record=record,
                    raw_firefly_dir=raw_firefly_dir,
                    output_dir=output_dir,
                    target_sample_rate=target_sample_rate,
                    target_channels=target_channels,
                )
            )
        except Exception as exc:  # pragma: no cover
            failed = dict(record)
            failed["round1_1_recovery_error"] = str(exc)
            failed_records.append(failed)

    combined_train_records = train_manifest + recovered_records
    final_excluded_records = remaining_excluded + failed_records

    write_manifest(output_dir / "manifest_round1_train.jsonl", combined_train_records)
    write_manifest(output_dir / "manifest_round1_excluded.jsonl", final_excluded_records)
    write_manifest(output_dir / "manifest_round1_recovered.jsonl", recovered_records)

    summary = build_summary(
        base_train_records=train_manifest,
        recovered_records=recovered_records,
        remaining_excluded=remaining_excluded,
        failed_records=failed_records,
        target_sample_rate=target_sample_rate,
        target_channels=target_channels,
    )
    write_json(report_output_dir / "target_format_recovery_summary.json", summary)
    (report_output_dir / "target_format_recovery_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records



def copy_existing_labels(source_dir: Path, target_dir: Path) -> None:
    if not source_dir.exists():
        return
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)


def infer_raw_firefly_dir(input_dir: Path) -> Path:
    project_root = input_dir.parent.parent.parent
    candidate = project_root / "data_convert" / "dataset_firefly_raw"
    if not candidate.exists():
        raise FileNotFoundError(f"Unable to locate raw firefly dataset at {candidate}")
    return candidate


def should_recover_record(
    record: dict[str, object],
    keep_no_text_voice_isolated: bool,
) -> bool:
    reasons = set(str(reason) for reason in record.get("exclusion_reasons", []))
    if not reasons:
        return False
    allowed_prefixes = ("sample_rate=", "channels=")
    if any(not any(reason.startswith(prefix) for prefix in allowed_prefixes) for reason in reasons):
        return False
    if keep_no_text_voice_isolated and str(record["id"]).startswith("no_text_voice/"):
        return False
    return has_lexical_content(str(record["text"]["cleaned"]))


def has_lexical_content(text: str) -> bool:
    return any(char not in PUNCTUATION_SET for char in text)


def recover_record(
    record: dict[str, object],
    raw_firefly_dir: Path,
    output_dir: Path,
    target_sample_rate: int,
    target_channels: int,
) -> dict[str, object]:
    if target_channels != 1:
        raise ValueError("Current recovery implementation only supports mono output.")

    raw_wav_path = raw_firefly_dir / str(record["wav_path"])
    waveform, source_sample_rate = load_waveform_float(raw_wav_path)
    recovered_waveform = resample_waveform(
        waveform=waveform,
        source_sample_rate=source_sample_rate,
        target_sample_rate=target_sample_rate,
    )

    prepared_relative = Path("audio") / Path(str(record["wav_path"]))
    prepared_path = output_dir / prepared_relative
    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    write_waveform_int16(prepared_path, recovered_waveform, sample_rate=target_sample_rate)

    cleaned_lab_relative = Path(str(record["cleaned_lab_path"]))
    cleaned_lab_path = output_dir / cleaned_lab_relative
    cleaned_lab_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_lab_path.write_text(str(record["text"]["cleaned"]) + "\n", encoding="utf-8", newline="\n")

    recovered_metadata = read_wav_metadata(prepared_path)
    updated = dict(record)
    updated["prepared_wav_path"] = prepared_relative.as_posix()
    updated["include_in_round1"] = True
    updated["exclusion_reasons"] = []
    updated["wav"] = recovered_metadata.to_dict()
    updated["round1_1_recovery"] = {
        "source_wav_path": raw_wav_path.as_posix(),
        "source_sample_rate": source_sample_rate,
        "source_channels": int(record["wav"]["channels"]),
        "target_sample_rate": target_sample_rate,
        "target_channels": target_channels,
        "recovery_mode": "lexical_format_normalization",
    }
    return updated


def load_waveform_float(path: Path) -> tuple[torch.Tensor, int]:
    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_count = wav_file.getnframes()
        raw = wav_file.readframes(frame_count)

    if sample_width != 2:
        raise ValueError(f"Unsupported sample width in {path}: {sample_width}")

    waveform = torch.frombuffer(bytearray(raw), dtype=torch.int16).to(torch.float32)
    if channels > 1:
        waveform = waveform.view(-1, channels).mean(dim=1)
    waveform = waveform / 32768.0
    return waveform.clone(), sample_rate


def resample_waveform(
    waveform: torch.Tensor,
    source_sample_rate: int,
    target_sample_rate: int,
) -> torch.Tensor:
    if source_sample_rate == target_sample_rate:
        return waveform
    target_length = max(1, int(round(waveform.numel() * target_sample_rate / source_sample_rate)))
    resampled = F.interpolate(
        waveform.view(1, 1, -1),
        size=target_length,
        mode="linear",
        align_corners=False,
    )
    return resampled.view(-1).clamp_(-1.0, 1.0)


def write_waveform_int16(path: Path, waveform: torch.Tensor, sample_rate: int) -> None:
    pcm = (waveform.clamp(-1.0, 1.0) * 32767.0).round().to(torch.int16).cpu().numpy()
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def build_summary(
    base_train_records: list[dict[str, object]],
    recovered_records: list[dict[str, object]],
    remaining_excluded: list[dict[str, object]],
    failed_records: list[dict[str, object]],
    target_sample_rate: int,
    target_channels: int,
) -> dict[str, object]:
    return {
        "base_round1_train_count": len(base_train_records),
        "recovered_count": len(recovered_records),
        "remaining_excluded_count": len(remaining_excluded),
        "failed_recovery_count": len(failed_records),
        "target_sample_rate": target_sample_rate,
        "target_channels": target_channels,
        "base_duration_sec": round(sum(float(row["wav"]["duration_sec"]) for row in base_train_records), 6),
        "recovered_duration_sec": round(sum(float(row["wav"]["duration_sec"]) for row in recovered_records), 6),
        "remaining_excluded_duration_sec": round(
            sum(float(row["wav"]["duration_sec"]) for row in remaining_excluded),
            6,
        ),
        "recovered_duration_stats_sec": summarize_numeric(
            [float(row["wav"]["duration_sec"]) for row in recovered_records]
        ) if recovered_records else None,
        "remaining_excluded_ids": [str(row["id"]) for row in remaining_excluded],
        "failed_recovery_ids": [str(row["id"]) for row in failed_records],
        "notes": [
            "round1.1 target recovery keeps current no_text_voice exclusions isolated by default.",
            "recovered records are normalized to 44100 Hz mono and written under output_dir/audio.",
            "combined manifest_round1_train.jsonl now contains original round1 target records plus recovered lexical records.",
        ],
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# round1.1 target format recovery 摘要",
        "",
        f"- base_round1_train_count: {summary['base_round1_train_count']}",
        f"- recovered_count: {summary['recovered_count']}",
        f"- remaining_excluded_count: {summary['remaining_excluded_count']}",
        f"- failed_recovery_count: {summary['failed_recovery_count']}",
        f"- target_sample_rate: {summary['target_sample_rate']}",
        f"- target_channels: {summary['target_channels']}",
        f"- base_duration_sec: {summary['base_duration_sec']}",
        f"- recovered_duration_sec: {summary['recovered_duration_sec']}",
        f"- remaining_excluded_duration_sec: {summary['remaining_excluded_duration_sec']}",
        "",
        "## notes",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
