from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.data_scan import summarize_numeric
from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import build_char_vocab, collate_target_batch, load_target_examples_from_records
from v5vc.special_eval import chunk_records, compute_punctuation_ratio, infer_target_group
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold
from v5vc.streaming_student.pitch_provider import DEFAULT_STAGE3_PITCH_PROVIDER_MODE


def build_streaming_student_eval_bridge(
    config_path: Path,
    output_dir: Path,
    split_dir: Path | None,
    calibration_asset_path: Path | None,
    batch_size: int,
    max_records_per_slice: int | None,
) -> None:
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    split_dir = resolve_split_dir(config_path=config_path, config=config, split_dir=split_dir)
    calibration_asset_path = None if calibration_asset_path is None else calibration_asset_path.resolve()

    target_train_records = load_jsonl(split_dir / "target_train.jsonl")
    target_validation_records = load_jsonl(split_dir / "target_validation.jsonl")
    target_special_eval_records = load_jsonl(split_dir / "target_special_eval.jsonl")
    if max_records_per_slice is not None and max_records_per_slice > 0:
        target_validation_records = target_validation_records[:max_records_per_slice]
        target_special_eval_records = target_special_eval_records[:max_records_per_slice]
    vocab = build_char_vocab(target_train_records)

    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.eval()
    if model.frontend.pitch_provider_mode != DEFAULT_STAGE3_PITCH_PROVIDER_MODE:
        raise ValueError(
            "build_streaming_student_eval_bridge does not support explicit pitch_provider_mode yet."
        )
    conditioning = load_conditioning_asset(
        config=config,
        calibration_asset_path=calibration_asset_path,
    )

    with torch.no_grad():
        validation_summary = evaluate_target_slice(
            model=model,
            records=target_validation_records,
            vocab=vocab,
            batch_size=int(batch_size),
            speaker_embedding=conditioning["speaker_embedding"],
            geom_embedding=conditioning["geom_embedding"],
        )
        special_summary = evaluate_target_slice(
            model=model,
            records=target_special_eval_records,
            vocab=vocab,
            batch_size=int(batch_size),
            speaker_embedding=conditioning["speaker_embedding"],
            geom_embedding=conditioning["geom_embedding"],
        )

    bridge_summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "split_dir": split_dir.as_posix(),
        "calibration_asset_path": None if calibration_asset_path is None else calibration_asset_path.as_posix(),
        "conditioning_source": conditioning["summary"],
        "frame_contract": {
            "frame_length": int(config["model"]["frame_length"]),
            "hop_length": int(config["model"]["hop_length"]),
        },
        "stable_keys": [
            "frame_mask",
            "z_art",
            "event_logits",
            "coarse_log_f0",
            "vuv_logits",
            "aperiodicity",
            "energy",
        ],
        "target_validation": validation_summary,
        "target_special_eval": special_summary,
        "comparisons": compare_target_slices(
            validation_summary=validation_summary,
            special_summary=special_summary,
        ),
        "notes": [
            "This bridge validates Stage3 output contracts and summary wiring, not model quality.",
            "When no real calibration asset is available, the bridge uses deterministic placeholder conditioning.",
            "Do not interpret bridge deltas as a replacement for offline_mvp route metrics.",
        ],
    }

    json_path = output_dir / "streaming_student_eval_bridge.json"
    md_path = output_dir / "streaming_student_eval_bridge.md"
    json_path.write_text(
        json.dumps(bridge_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(bridge_summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_split_dir(
    config_path: Path,
    config: dict[str, object],
    split_dir: Path | None,
) -> Path:
    if split_dir is not None:
        return split_dir.resolve()
    raw_value = config.get("data", {}).get("split_dir")
    if raw_value in {None, ""}:
        raise ValueError("split_dir is required for the Stage3 eval bridge.")
    return (config_path.parent.parent / str(raw_value)).resolve()


def load_conditioning_asset(
    config: dict[str, object],
    calibration_asset_path: Path | None,
) -> dict[str, object]:
    speaker_dim = int(config["model"]["speaker_embed_dim"])
    geom_dim = int(config["model"]["geom_embed_dim"])
    if calibration_asset_path is not None and calibration_asset_path.exists():
        payload = json.loads(calibration_asset_path.read_text(encoding="utf-8"))
        assets = dict(payload.get("conditioning_assets", {}))
        speaker_vector = normalize_vector(assets.get("s_spk_target", {}).get("vector"), speaker_dim)
        geom_vector = normalize_vector(assets.get("s_geom_target", {}).get("vector"), geom_dim)
        alpha_value = float(assets.get("alpha", {}).get("value", 1.0))
        return {
            "speaker_embedding": torch.tensor(speaker_vector, dtype=torch.float32),
            "geom_embedding": torch.tensor(geom_vector, dtype=torch.float32),
            "summary": {
                "asset_status": str(payload.get("status", "unknown")),
                "alpha_value": alpha_value,
                "speaker_dim": speaker_dim,
                "geom_dim": geom_dim,
                "source": calibration_asset_path.as_posix(),
            },
        }
    return {
        "speaker_embedding": torch.zeros((speaker_dim,), dtype=torch.float32),
        "geom_embedding": torch.zeros((geom_dim,), dtype=torch.float32),
        "summary": {
            "asset_status": "placeholder_zero_vectors",
            "alpha_value": 1.0,
            "speaker_dim": speaker_dim,
            "geom_dim": geom_dim,
            "source": None,
        },
    }


def normalize_vector(raw_vector: object, expected_dim: int) -> list[float]:
    if not isinstance(raw_vector, list) or len(raw_vector) != expected_dim:
        return [0.0] * expected_dim
    return [float(value) for value in raw_vector]


def evaluate_target_slice(
    model: torch.nn.Module,
    records: list[dict[str, object]],
    vocab: dict[str, int],
    batch_size: int,
    speaker_embedding: torch.Tensor,
    geom_embedding: torch.Tensor,
) -> dict[str, object]:
    if not records:
        raise ValueError("No target records available for the Stage3 eval bridge.")
    batches = chunk_records(records, batch_size=max(1, batch_size))
    accumulator = init_output_stat_accumulator()

    for batch_records in batches:
        examples = load_target_examples_from_records(
            batch_records,
            vocab=vocab,
            max_duration_sec=None,
        )
        batch = collate_target_batch(examples)
        batch_speaker_embedding = speaker_embedding.unsqueeze(0).expand(len(batch_records), -1)
        batch_geom_embedding = geom_embedding.unsqueeze(0).expand(len(batch_records), -1)
        outputs = model(
            waveform=batch["waveform"],
            lengths=batch["audio_lengths"],
            speaker_embedding=batch_speaker_embedding,
            geom_embedding=batch_geom_embedding,
        )
        accumulate_output_stats(
            accumulator=accumulator,
            outputs=outputs,
            frame_mask=outputs["frame_mask"],
        )

    durations = [float(record["audio"]["duration_sec"]) for record in records]
    punctuation_ratios = [compute_punctuation_ratio(str(record["text"]["clean"] or "")) for record in records]
    group_counts = Counter(infer_target_group(record) for record in records)
    return {
        "record_count": len(records),
        "batch_count": len(batches),
        "duration_stats_sec": summarize_numeric(durations),
        "punctuation_ratio": summarize_numeric(punctuation_ratios),
        "group_counts": dict(sorted(group_counts.items())),
        "output_stats": finalize_output_stat_accumulator(accumulator=accumulator, batch_count=len(batches)),
        "record_ids": [str(record["record_id"]) for record in records],
    }


def init_output_stat_accumulator() -> dict[str, float]:
    return {
        "shared_hidden_abs_mean": 0.0,
        "z_art_abs_mean": 0.0,
        "z_art_delta_abs_mean": 0.0,
        "event_prob_mean": 0.0,
        "event_presence_prob_mean": 0.0,
        "coarse_log_f0_mean": 0.0,
        "coarse_log_f0_delta_abs_mean": 0.0,
        "vuv_prob_mean": 0.0,
        "aperiodicity_mean": 0.0,
        "energy_mean": 0.0,
        "log_f0_correction_abs_mean": 0.0,
        "aper_correction_abs_mean": 0.0,
    }


def accumulate_output_stats(
    accumulator: dict[str, float],
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
) -> None:
    event_probs = outputs.get("event_probs")
    if event_probs is None:
        event_probs = torch.sigmoid(outputs["event_logits"])
    vuv_probs = torch.sigmoid(outputs["vuv_logits"])
    accumulator["shared_hidden_abs_mean"] += masked_abs_mean(outputs["shared_hidden"], frame_mask)
    accumulator["z_art_abs_mean"] += masked_abs_mean(outputs["z_art"], frame_mask)
    accumulator["z_art_delta_abs_mean"] += masked_temporal_abs_mean(outputs["z_art"], frame_mask)
    accumulator["event_prob_mean"] += masked_mean(event_probs, frame_mask)
    accumulator["event_presence_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 0)
    accumulator["coarse_log_f0_mean"] += masked_mean(outputs["coarse_log_f0"], frame_mask)
    accumulator["coarse_log_f0_delta_abs_mean"] += masked_temporal_abs_mean(outputs["coarse_log_f0"], frame_mask)
    accumulator["vuv_prob_mean"] += masked_mean(vuv_probs, frame_mask)
    accumulator["aperiodicity_mean"] += masked_mean(outputs["aperiodicity"], frame_mask)
    accumulator["energy_mean"] += masked_mean(outputs["energy"], frame_mask)
    accumulator["log_f0_correction_abs_mean"] += masked_abs_mean(outputs["log_f0_correction"], frame_mask)
    accumulator["aper_correction_abs_mean"] += masked_abs_mean(outputs["aper_correction"], frame_mask)


def finalize_output_stat_accumulator(
    accumulator: dict[str, float],
    batch_count: int,
) -> dict[str, float]:
    return {
        key: round(value / max(1, batch_count), 6)
        for key, value in accumulator.items()
    }


def masked_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    weights = frame_mask.to(tensor.dtype).unsqueeze(-1).expand_as(tensor)
    numerator = (tensor * weights).sum()
    denominator = weights.sum().clamp_min(1.0)
    return float((numerator / denominator).item())


def masked_abs_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    return masked_mean(tensor.abs(), frame_mask)


def masked_channel_mean(tensor: torch.Tensor, frame_mask: torch.Tensor, channel_index: int) -> float:
    return masked_mean(tensor[..., channel_index : channel_index + 1], frame_mask)


def masked_temporal_abs_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    if tensor.shape[1] <= 1:
        return 0.0
    delta = (tensor[:, 1:] - tensor[:, :-1]).abs()
    temporal_mask = (frame_mask[:, 1:] & frame_mask[:, :-1]).to(delta.dtype).unsqueeze(-1).expand_as(delta)
    numerator = (delta * temporal_mask).sum()
    denominator = temporal_mask.sum().clamp_min(1.0)
    return float((numerator / denominator).item())


def compare_target_slices(
    validation_summary: dict[str, object],
    special_summary: dict[str, object],
) -> dict[str, float]:
    return {
        f"delta_{key}": round(
            float(special_summary["output_stats"][key]) - float(validation_summary["output_stats"][key]),
            6,
        )
        for key in validation_summary["output_stats"].keys()
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Eval Bridge",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- split_dir: {summary['split_dir']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- conditioning_source: {json.dumps(summary['conditioning_source'], ensure_ascii=False)}",
        f"- frame_contract: {json.dumps(summary['frame_contract'], ensure_ascii=False)}",
        "",
    ]
    for key in ("target_validation", "target_special_eval"):
        payload = summary[key]
        lines.extend(
            [
                f"## {key}",
                f"- record_count: {payload['record_count']}",
                f"- batch_count: {payload['batch_count']}",
                f"- duration_stats_sec: {json.dumps(payload['duration_stats_sec'], ensure_ascii=False)}",
                f"- punctuation_ratio: {json.dumps(payload['punctuation_ratio'], ensure_ascii=False)}",
                f"- group_counts: {json.dumps(payload['group_counts'], ensure_ascii=False)}",
            ]
        )
        for stat_key, stat_value in payload["output_stats"].items():
            lines.append(f"- {stat_key}: {stat_value}")
        lines.append("")
    lines.extend(["## Comparisons"])
    for key, value in summary["comparisons"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
