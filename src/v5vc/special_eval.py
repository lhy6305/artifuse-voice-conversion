from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

import torch

from v5vc.ablation_eval import build_model_from_config, load_checkpoint, resolve_checkpoint_path, resolve_split_dir
from v5vc.data_scan import summarize_numeric, write_json
from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    TEXT_FEATURE_VERSION_LEGACY_V0,
    attach_target_weak_event_hints,
    build_char_vocab,
    collate_target_batch,
    load_target_weak_event_hint_map,
    load_target_examples_from_records,
)
from v5vc.offline_mvp.losses import build_frame_targets, compute_offline_mvp_loss

PUNCTUATION_SET = set("，。？！；：、")


def evaluate_round1_special_eval(
    split_dir: Path,
    output_dir: Path,
    experiment_metrics_path: Path | None,
) -> None:
    split_dir = split_dir.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    target_validation_records = load_jsonl(split_dir / "target_validation.jsonl")
    target_special_eval_records = load_jsonl(split_dir / "target_special_eval.jsonl")
    split_summary = json.loads((split_dir / "split_summary.json").read_text(encoding="utf-8"))

    result = build_special_eval_result(
        split_dir=split_dir,
        split_summary=split_summary,
        target_validation_records=target_validation_records,
        target_special_eval_records=target_special_eval_records,
    )

    write_json(output_dir / "special_eval.json", result)
    write_markdown(output_dir / "special_eval.md", result)

    if experiment_metrics_path is not None:
        update_experiment_metrics(experiment_metrics_path.resolve(), result)


def evaluate_offline_mvp_special_eval(
    config_path: Path,
    split_dir: Path | None,
    output_dir: Path,
    experiment_metrics_path: Path | None,
    checkpoint_path: Path | None,
) -> None:
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
    result = build_model_special_eval_result(
        config_path=config_path,
        config=config,
        split_dir=resolved_split_dir,
        checkpoint_path=resolved_checkpoint_path,
    )

    write_json(output_dir / "special_eval_model.json", result)
    (output_dir / "special_eval_model.md").write_text(
        build_model_markdown(result),
        encoding="utf-8",
        newline="\n",
    )

    if experiment_metrics_path is not None:
        update_experiment_metrics_model(experiment_metrics_path.resolve(), result)


def build_model_special_eval_result(
    config_path: Path,
    config: dict[str, object],
    split_dir: Path,
    checkpoint_path: Path,
) -> dict[str, object]:
    resolved_split_dir = split_dir.resolve()
    resolved_checkpoint_path = checkpoint_path.resolve()

    target_train_records = load_jsonl(resolved_split_dir / "target_train.jsonl")
    target_validation_records = load_jsonl(resolved_split_dir / "target_validation.jsonl")
    target_special_eval_records = load_jsonl(resolved_split_dir / "target_special_eval.jsonl")
    hint_map = resolve_target_weak_event_hint_map(config_path=config_path, config=config)
    if hint_map is not None:
        target_train_records = attach_target_weak_event_hints(target_train_records, hint_map)
        target_validation_records = attach_target_weak_event_hints(target_validation_records, hint_map)
        target_special_eval_records = attach_target_weak_event_hints(target_special_eval_records, hint_map)
    split_summary = json.loads((resolved_split_dir / "split_summary.json").read_text(encoding="utf-8"))
    vocab = build_char_vocab(target_train_records)

    model = build_model_from_config(config)
    checkpoint = load_checkpoint(resolved_checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    validation_eval = evaluate_target_slice(
        model=model,
        records=target_validation_records,
        vocab=vocab,
        config=config,
    )
    special_eval = evaluate_target_slice(
        model=model,
        records=target_special_eval_records,
        vocab=vocab,
        config=config,
    )

    return {
        "config_path": config_path.as_posix(),
        "split_dir": resolved_split_dir.as_posix(),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "split_option_name": split_summary["option_name"],
        "target_validation": validation_eval,
        "target_special_eval": special_eval,
        "comparisons": compare_target_slices(
            validation_eval=validation_eval,
            special_eval=special_eval,
        ),
        "notes": [
            "Model-level special_eval is reported separately from regular validation.",
            "Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.",
            "Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.",
        ],
    }


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def resolve_target_weak_event_hint_map(
    config_path: Path,
    config: dict[str, object],
) -> dict[str, dict[str, object]] | None:
    hint_path_config = config["data"].get("target_weak_event_hints_path")
    if hint_path_config in {None, ""}:
        return None
    return load_target_weak_event_hint_map((config_path.parent.parent / hint_path_config).resolve())


def evaluate_target_slice(
    model: torch.nn.Module,
    records: list[dict[str, object]],
    vocab: dict[str, int],
    config: dict[str, object],
) -> dict[str, object]:
    batch_size = int(config["data"]["target_batch_size"])
    max_audio_sec = float(config["data"]["max_audio_sec"])
    text_feature_version = str(config["data"].get("target_text_feature_version", TEXT_FEATURE_VERSION_LEGACY_V0))
    frame_length = int(config["model"]["frame_length"])
    hop_length = int(config["model"]["hop_length"])
    loss_weights = config["losses"]
    batches = chunk_records(records, batch_size=batch_size)
    if not batches:
        raise ValueError("No target records available for model-level special_eval.")

    metric_accumulator = init_metric_accumulator()
    stat_accumulator = init_output_stat_accumulator()

    with torch.no_grad():
        for batch_records in batches:
            examples = load_target_examples_from_records(
                batch_records,
                vocab=vocab,
                max_duration_sec=max_audio_sec,
                text_feature_version=text_feature_version,
            )
            batch = collate_target_batch(examples)
            outputs = model(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
            )
            targets = build_frame_targets(
                waveform=batch["waveform"],
                lengths=batch["audio_lengths"],
                frame_length=frame_length,
                hop_length=hop_length,
                weak_event_hints=batch.get("weak_event_hints"),
            )
            _, metrics = compute_offline_mvp_loss(
                outputs=outputs,
                acoustic_target=targets["acoustic_target"],
                event_target=targets["event_target"],
                frame_mask=targets["frame_mask"],
                text_aux_target=batch["text_features"],
                texts=batch["texts"],
                weights=loss_weights,
                target_special_supervision=batch.get("target_special_supervision"),
                weak_event_target=targets.get("weak_event_target"),
                weak_event_weight=targets.get("weak_event_weight"),
                pause_boundary_strength=targets.get("pause_boundary_strength"),
                terminal_boundary_strength=targets.get("terminal_boundary_strength"),
                boundary_type_strengths=targets.get("boundary_type_strengths"),
                clause_role_strengths=targets.get("clause_role_strengths"),
                clause_transition_strengths=targets.get("clause_transition_strengths"),
                utterance_structure_strengths=targets.get("utterance_structure_strengths"),
            )
            accumulate_metrics(metric_accumulator, metrics)
            accumulate_output_stats(
                accumulator=stat_accumulator,
                outputs=outputs,
                frame_mask=targets["frame_mask"],
            )

    return {
        "record_count": len(records),
        "batch_count": len(batches),
        "duration_stats_sec": summarize_numeric(
            [float(record["audio"]["duration_sec"]) for record in records]
        ),
        "clean_char_count": summarize_numeric(
            [len(str(record["text"]["clean"] or "")) for record in records]
        ),
        "metrics": finalize_metric_accumulator(metric_accumulator, len(batches)),
        "output_stats": finalize_output_stat_accumulator(stat_accumulator, len(batches)),
        "record_ids": [str(record["record_id"]) for record in records],
    }


def build_special_eval_result(
    split_dir: Path,
    split_summary: dict[str, object],
    target_validation_records: list[dict[str, object]],
    target_special_eval_records: list[dict[str, object]],
) -> dict[str, object]:
    validation_ids = {record["record_id"] for record in target_validation_records}
    special_eval_ids = [record["record_id"] for record in target_special_eval_records]
    special_eval_group_counts = Counter(infer_target_group(record) for record in target_special_eval_records)
    clean_texts = [str(record["text"]["clean"] or "") for record in target_special_eval_records]
    punctuation_only_count = sum(is_punctuation_only(text) for text in clean_texts)

    checks = {
        "special_eval_manifest_nonempty": len(target_special_eval_records) > 0,
        "special_eval_record_ids_unique": len(set(special_eval_ids)) == len(special_eval_ids),
        "special_eval_disjoint_from_main_validation": all(record_id not in validation_ids for record_id in special_eval_ids),
        "special_eval_all_from_no_text_voice": set(special_eval_group_counts) == {"no_text_voice"},
        "special_eval_all_target_role": all(record["role"] == "target" for record in target_special_eval_records),
    }

    summary = {
        "split_dir": split_dir.as_posix(),
        "split_option_name": split_summary["option_name"],
        "target_validation_record_count": len(target_validation_records),
        "target_special_eval_record_count": len(target_special_eval_records),
        "target_special_eval_duration_stats_sec": summarize_numeric(
            [float(record["audio"]["duration_sec"]) for record in target_special_eval_records]
        ),
        "target_special_eval_clean_char_count": summarize_numeric(
            [len(str(record["text"]["clean"] or "")) for record in target_special_eval_records]
        ),
        "target_special_eval_punctuation_ratio": summarize_numeric(
            [compute_punctuation_ratio(str(record["text"]["clean"] or "")) for record in target_special_eval_records]
        ),
        "target_special_eval_group_counts": dict(sorted(special_eval_group_counts.items())),
        "target_special_eval_punctuation_only_count": punctuation_only_count,
        "target_validation_duration_stats_sec": summarize_numeric(
            [float(record["audio"]["duration_sec"]) for record in target_validation_records]
        ),
    }

    return {
        "overall_ok": all(checks.values()),
        "checks": checks,
        "summary": summary,
        "special_eval_record_ids": special_eval_ids,
        "notes": [
            "target_special_eval is a challenge-only set and should not be merged back into regular validation.",
            "current round1 special_eval records are expected to come from no_text_voice only.",
            "current special_eval clean text is punctuation-only, so this set should be interpreted as a stress slice rather than normal content validation.",
        ],
    }


def init_metric_accumulator() -> dict[str, float]:
    return {
        "loss_total": 0.0,
        "loss_acoustic": 0.0,
        "loss_event": 0.0,
        "loss_z_smooth": 0.0,
        "loss_text_aux": 0.0,
        "loss_text_aux_effective": 0.0,
        "loss_text_aux_structural": 0.0,
        "loss_text_aux_lexical": 0.0,
        "loss_weak_event": 0.0,
        "loss_clause_transition_aux": 0.0,
        "loss_structural_clause_transition_aux": 0.0,
        "loss_boundary_contrast_aux": 0.0,
        "loss_punctuation_profile_aux": 0.0,
        "loss_structural_clause_profile_aux": 0.0,
        "loss_challenge_proxy_profile_aux": 0.0,
        "loss_z_art_influence_aux": 0.0,
        "loss_formal_special_clause_shape_aux": 0.0,
    }


def accumulate_metrics(accumulator: dict[str, float], metrics: dict[str, float]) -> None:
    for key in accumulator:
        accumulator[key] += float(metrics[key])


def finalize_metric_accumulator(accumulator: dict[str, float], batch_count: int) -> dict[str, float]:
    return {
        key: round(value / max(1, batch_count), 6)
        for key, value in accumulator.items()
    }


def init_output_stat_accumulator() -> dict[str, float]:
    return {
        "z_art_abs_mean": 0.0,
        "z_art_delta_abs_mean": 0.0,
        "event_prob_mean": 0.0,
        "event_presence_prob_mean": 0.0,
        "event_delta_prob_mean": 0.0,
        "event_rise_prob_mean": 0.0,
        "event_fall_prob_mean": 0.0,
        "event_energy_prob_mean": 0.0,
        "event_presence_peak_ratio": 0.0,
        "acoustic_abs_mean": 0.0,
        "acoustic_energy_mean": 0.0,
        "acoustic_delta_abs_mean": 0.0,
        "text_aux_abs_mean": 0.0,
    }


def accumulate_output_stats(
    accumulator: dict[str, float],
    outputs: dict[str, torch.Tensor],
    frame_mask: torch.Tensor,
) -> None:
    event_probs = outputs.get("event_probs")
    if event_probs is None:
        event_probs = torch.sigmoid(outputs["event_logits"])
    accumulator["z_art_abs_mean"] += masked_abs_mean(outputs["z_art"], frame_mask)
    accumulator["z_art_delta_abs_mean"] += masked_temporal_abs_mean(outputs["z_art"], frame_mask)
    accumulator["event_prob_mean"] += masked_mean(event_probs, frame_mask)
    accumulator["event_presence_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 0)
    accumulator["event_delta_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 1)
    accumulator["event_rise_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 5)
    accumulator["event_fall_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 6)
    accumulator["event_energy_prob_mean"] += masked_channel_mean(event_probs, frame_mask, 7)
    accumulator["event_presence_peak_ratio"] += masked_threshold_ratio(event_probs[..., 0], frame_mask, threshold=0.5)
    accumulator["acoustic_abs_mean"] += masked_abs_mean(outputs["acoustic"], frame_mask)
    accumulator["acoustic_energy_mean"] += masked_channel_mean(outputs["acoustic"], frame_mask, 0)
    accumulator["acoustic_delta_abs_mean"] += masked_channel_abs_mean(outputs["acoustic"], frame_mask, 3)
    accumulator["text_aux_abs_mean"] += float(outputs["text_aux"].abs().mean().item())


def finalize_output_stat_accumulator(accumulator: dict[str, float], batch_count: int) -> dict[str, float]:
    return {
        key: round(value / max(1, batch_count), 6)
        for key, value in accumulator.items()
    }


def masked_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    weights = frame_mask.to(tensor.dtype).unsqueeze(-1)
    expanded_weights = weights.expand_as(tensor)
    numerator = (tensor * expanded_weights).sum()
    denominator = expanded_weights.sum().clamp_min(1.0)
    return float((numerator / denominator).item())


def masked_abs_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    return masked_mean(tensor.abs(), frame_mask)


def masked_channel_mean(tensor: torch.Tensor, frame_mask: torch.Tensor, channel_index: int) -> float:
    return masked_mean(tensor[..., channel_index : channel_index + 1], frame_mask)


def masked_channel_abs_mean(tensor: torch.Tensor, frame_mask: torch.Tensor, channel_index: int) -> float:
    return masked_abs_mean(tensor[..., channel_index : channel_index + 1], frame_mask)


def masked_temporal_abs_mean(tensor: torch.Tensor, frame_mask: torch.Tensor) -> float:
    if tensor.shape[1] <= 1:
        return 0.0
    delta = (tensor[:, 1:] - tensor[:, :-1]).abs()
    temporal_mask = (frame_mask[:, 1:] & frame_mask[:, :-1]).to(delta.dtype).unsqueeze(-1)
    numerator = (delta * temporal_mask).sum()
    denominator = temporal_mask.expand_as(delta).sum().clamp_min(1.0)
    return float((numerator / denominator).item())


def masked_threshold_ratio(tensor: torch.Tensor, frame_mask: torch.Tensor, threshold: float) -> float:
    weights = frame_mask.to(tensor.dtype)
    positives = ((tensor >= threshold).to(tensor.dtype) * weights).sum()
    denominator = weights.sum().clamp_min(1.0)
    return float((positives / denominator).item())


def chunk_records(records: list[dict[str, object]], batch_size: int) -> list[list[dict[str, object]]]:
    return [
        records[index : index + batch_size]
        for index in range(0, len(records), batch_size)
        if records[index : index + batch_size]
    ]


def compare_target_slices(
    validation_eval: dict[str, object],
    special_eval: dict[str, object],
) -> dict[str, float]:
    return {
        "delta_loss_total": round(
            special_eval["metrics"]["loss_total"] - validation_eval["metrics"]["loss_total"],
            6,
        ),
        "delta_loss_acoustic": round(
            special_eval["metrics"]["loss_acoustic"] - validation_eval["metrics"]["loss_acoustic"],
            6,
        ),
        "delta_loss_event": round(
            special_eval["metrics"]["loss_event"] - validation_eval["metrics"]["loss_event"],
            6,
        ),
        "delta_loss_text_aux": round(
            special_eval["metrics"]["loss_text_aux"] - validation_eval["metrics"]["loss_text_aux"],
            6,
        ),
        "delta_loss_text_aux_effective": round(
            special_eval["metrics"]["loss_text_aux_effective"]
            - validation_eval["metrics"]["loss_text_aux_effective"],
            6,
        ),
        "delta_loss_text_aux_structural": round(
            special_eval["metrics"]["loss_text_aux_structural"]
            - validation_eval["metrics"]["loss_text_aux_structural"],
            6,
        ),
        "delta_loss_text_aux_lexical": round(
            special_eval["metrics"]["loss_text_aux_lexical"]
            - validation_eval["metrics"]["loss_text_aux_lexical"],
            6,
        ),
        "delta_loss_clause_transition_aux": round(
            special_eval["metrics"]["loss_clause_transition_aux"]
            - validation_eval["metrics"]["loss_clause_transition_aux"],
            6,
        ),
        "delta_loss_structural_clause_transition_aux": round(
            special_eval["metrics"]["loss_structural_clause_transition_aux"]
            - validation_eval["metrics"]["loss_structural_clause_transition_aux"],
            6,
        ),
        "delta_loss_boundary_contrast_aux": round(
            special_eval["metrics"]["loss_boundary_contrast_aux"]
            - validation_eval["metrics"]["loss_boundary_contrast_aux"],
            6,
        ),
        "delta_loss_punctuation_profile_aux": round(
            special_eval["metrics"]["loss_punctuation_profile_aux"]
            - validation_eval["metrics"]["loss_punctuation_profile_aux"],
            6,
        ),
        "delta_loss_structural_clause_profile_aux": round(
            special_eval["metrics"]["loss_structural_clause_profile_aux"]
            - validation_eval["metrics"]["loss_structural_clause_profile_aux"],
            6,
        ),
        "delta_loss_challenge_proxy_profile_aux": round(
            special_eval["metrics"]["loss_challenge_proxy_profile_aux"]
            - validation_eval["metrics"]["loss_challenge_proxy_profile_aux"],
            6,
        ),
        "delta_loss_z_art_influence_aux": round(
            special_eval["metrics"]["loss_z_art_influence_aux"]
            - validation_eval["metrics"]["loss_z_art_influence_aux"],
            6,
        ),
        "delta_loss_formal_special_clause_shape_aux": round(
            special_eval["metrics"]["loss_formal_special_clause_shape_aux"]
            - validation_eval["metrics"]["loss_formal_special_clause_shape_aux"],
            6,
        ),
        "delta_z_art_abs_mean": round(
            special_eval["output_stats"]["z_art_abs_mean"] - validation_eval["output_stats"]["z_art_abs_mean"],
            6,
        ),
        "delta_z_art_delta_abs_mean": round(
            special_eval["output_stats"]["z_art_delta_abs_mean"]
            - validation_eval["output_stats"]["z_art_delta_abs_mean"],
            6,
        ),
        "delta_event_prob_mean": round(
            special_eval["output_stats"]["event_prob_mean"] - validation_eval["output_stats"]["event_prob_mean"],
            6,
        ),
        "delta_event_presence_prob_mean": round(
            special_eval["output_stats"]["event_presence_prob_mean"]
            - validation_eval["output_stats"]["event_presence_prob_mean"],
            6,
        ),
        "delta_event_delta_prob_mean": round(
            special_eval["output_stats"]["event_delta_prob_mean"]
            - validation_eval["output_stats"]["event_delta_prob_mean"],
            6,
        ),
        "delta_event_rise_prob_mean": round(
            special_eval["output_stats"]["event_rise_prob_mean"]
            - validation_eval["output_stats"]["event_rise_prob_mean"],
            6,
        ),
        "delta_event_fall_prob_mean": round(
            special_eval["output_stats"]["event_fall_prob_mean"]
            - validation_eval["output_stats"]["event_fall_prob_mean"],
            6,
        ),
        "delta_event_energy_prob_mean": round(
            special_eval["output_stats"]["event_energy_prob_mean"]
            - validation_eval["output_stats"]["event_energy_prob_mean"],
            6,
        ),
        "delta_event_presence_peak_ratio": round(
            special_eval["output_stats"]["event_presence_peak_ratio"]
            - validation_eval["output_stats"]["event_presence_peak_ratio"],
            6,
        ),
        "delta_acoustic_abs_mean": round(
            special_eval["output_stats"]["acoustic_abs_mean"] - validation_eval["output_stats"]["acoustic_abs_mean"],
            6,
        ),
        "delta_acoustic_energy_mean": round(
            special_eval["output_stats"]["acoustic_energy_mean"]
            - validation_eval["output_stats"]["acoustic_energy_mean"],
            6,
        ),
        "delta_acoustic_delta_abs_mean": round(
            special_eval["output_stats"]["acoustic_delta_abs_mean"]
            - validation_eval["output_stats"]["acoustic_delta_abs_mean"],
            6,
        ),
        "delta_text_aux_abs_mean": round(
            special_eval["output_stats"]["text_aux_abs_mean"] - validation_eval["output_stats"]["text_aux_abs_mean"],
            6,
        ),
    }


def infer_target_group(record: dict[str, object]) -> str:
    original_lab_path = str(record["source_metadata"]["original_lab_path"]).replace("\\", "/")
    parts = [part for part in original_lab_path.split("/") if part]
    return parts[0] if len(parts) > 1 else "<root>"


def compute_punctuation_ratio(text: str) -> float:
    if not text:
        return 0.0
    punctuation_count = sum(1 for char in text if char in PUNCTUATION_SET)
    return punctuation_count / len(text)


def is_punctuation_only(text: str) -> bool:
    return bool(text) and all(char in PUNCTUATION_SET for char in text)


def write_markdown(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# round1 target special eval 评估",
        "",
        f"- overall_ok: {result['overall_ok']}",
        "",
        "## 检查项",
    ]
    for key, value in result["checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## 摘要",
            f"- split_dir: {result['summary']['split_dir']}",
            f"- split_option_name: {result['summary']['split_option_name']}",
            f"- target_validation_record_count: {result['summary']['target_validation_record_count']}",
            f"- target_special_eval_record_count: {result['summary']['target_special_eval_record_count']}",
            f"- target_special_eval_group_counts: {json.dumps(result['summary']['target_special_eval_group_counts'], ensure_ascii=False)}",
            f"- target_special_eval_punctuation_only_count: {result['summary']['target_special_eval_punctuation_only_count']}",
            "",
            "## 备注",
        ]
    )
    for note in result["notes"]:
        lines.append(f"- {note}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_model_markdown(result: dict[str, object]) -> str:
    lines = [
        "# offline MVP target_special_eval 模型级评估",
        "",
        f"- config_path: {result['config_path']}",
        f"- split_dir: {result['split_dir']}",
        f"- checkpoint_path: {result['checkpoint_path']}",
        f"- split_option_name: {result['split_option_name']}",
        "",
    ]
    for key in ("target_validation", "target_special_eval"):
        payload = result[key]
        lines.extend(
            [
                f"## {key}",
                f"- record_count: {payload['record_count']}",
                f"- batch_count: {payload['batch_count']}",
                f"- loss_total: {payload['metrics']['loss_total']}",
                f"- loss_acoustic: {payload['metrics']['loss_acoustic']}",
                f"- loss_event: {payload['metrics']['loss_event']}",
                f"- loss_text_aux: {payload['metrics']['loss_text_aux']}",
                f"- loss_text_aux_effective: {payload['metrics']['loss_text_aux_effective']}",
                f"- loss_text_aux_structural: {payload['metrics']['loss_text_aux_structural']}",
                f"- loss_text_aux_lexical: {payload['metrics']['loss_text_aux_lexical']}",
                f"- loss_clause_transition_aux: {payload['metrics']['loss_clause_transition_aux']}",
                f"- loss_structural_clause_transition_aux: {payload['metrics']['loss_structural_clause_transition_aux']}",
                f"- loss_boundary_contrast_aux: {payload['metrics']['loss_boundary_contrast_aux']}",
                f"- loss_punctuation_profile_aux: {payload['metrics']['loss_punctuation_profile_aux']}",
                f"- loss_structural_clause_profile_aux: {payload['metrics']['loss_structural_clause_profile_aux']}",
                f"- loss_challenge_proxy_profile_aux: {payload['metrics']['loss_challenge_proxy_profile_aux']}",
                f"- loss_z_art_influence_aux: {payload['metrics']['loss_z_art_influence_aux']}",
                f"- loss_formal_special_clause_shape_aux: {payload['metrics']['loss_formal_special_clause_shape_aux']}",
                f"- z_art_abs_mean: {payload['output_stats']['z_art_abs_mean']}",
                f"- z_art_delta_abs_mean: {payload['output_stats']['z_art_delta_abs_mean']}",
                f"- event_prob_mean: {payload['output_stats']['event_prob_mean']}",
                f"- event_presence_prob_mean: {payload['output_stats']['event_presence_prob_mean']}",
                f"- event_delta_prob_mean: {payload['output_stats']['event_delta_prob_mean']}",
                f"- event_rise_prob_mean: {payload['output_stats']['event_rise_prob_mean']}",
                f"- event_fall_prob_mean: {payload['output_stats']['event_fall_prob_mean']}",
                f"- event_energy_prob_mean: {payload['output_stats']['event_energy_prob_mean']}",
                f"- event_presence_peak_ratio: {payload['output_stats']['event_presence_peak_ratio']}",
                f"- acoustic_abs_mean: {payload['output_stats']['acoustic_abs_mean']}",
                f"- acoustic_energy_mean: {payload['output_stats']['acoustic_energy_mean']}",
                f"- acoustic_delta_abs_mean: {payload['output_stats']['acoustic_delta_abs_mean']}",
                f"- text_aux_abs_mean: {payload['output_stats']['text_aux_abs_mean']}",
                "",
            ]
        )
    lines.append("## 对比")
    for key, value in result["comparisons"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## 备注"])
    for note in result["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def update_experiment_metrics(path: Path, result: dict[str, object]) -> None:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {
            "experiment_id": path.stem.replace(".metrics", ""),
            "status": "initialized",
            "created_at": None,
            "metrics": {},
            "notes": [],
        }

    payload.setdefault("metrics", {})
    payload["metrics"]["target_special_eval"] = result
    if payload.get("status") in {None, "initialized"}:
        payload["status"] = "special_eval_evaluated"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def update_experiment_metrics_model(path: Path, result: dict[str, object]) -> None:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {
            "experiment_id": path.stem.replace(".metrics", ""),
            "status": "initialized",
            "created_at": None,
            "metrics": {},
            "notes": [],
        }

    payload.setdefault("metrics", {})
    payload["metrics"]["target_special_eval_model"] = result
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
