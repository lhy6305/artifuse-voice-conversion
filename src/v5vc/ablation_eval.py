from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
from pathlib import Path

import torch

from v5vc.data_scan import write_json
from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    TEXT_FEATURE_VERSION_LEGACY_V0,
    attach_target_weak_event_hints,
    build_char_vocab,
    collate_source_batch,
    collate_target_batch,
    load_target_weak_event_hint_map,
    load_source_examples_from_records,
    load_target_examples_from_records,
)
from v5vc.offline_mvp.losses import build_frame_targets, compute_offline_mvp_loss
from v5vc.offline_mvp.model import OfflineMVPNoResidualModel


ABLATION_MODES = ("none", "zero_z_art", "zero_e_evt")


def evaluate_offline_mvp_ablations(
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
    result = build_ablation_result(
        config_path=config_path,
        config=config,
        split_dir=resolved_split_dir,
        checkpoint_path=resolved_checkpoint_path,
    )

    write_json(output_dir / "ablation_eval.json", result)
    (output_dir / "ablation_eval.md").write_text(
        build_markdown(result),
        encoding="utf-8",
        newline="\n",
    )

    if experiment_metrics_path is not None:
        update_experiment_metrics(experiment_metrics_path.resolve(), result)


def build_ablation_result(
    config_path: Path,
    config: dict[str, object],
    split_dir: Path,
    checkpoint_path: Path,
) -> dict[str, object]:
    target_train_records = load_jsonl(split_dir / "target_train.jsonl")
    target_validation_records = load_jsonl(split_dir / "target_validation.jsonl")
    source_validation_records = load_jsonl(split_dir / "source_validation.jsonl")
    hint_map = resolve_target_weak_event_hint_map(config_path=config_path, config=config)
    if hint_map is not None:
        target_train_records = attach_target_weak_event_hints(target_train_records, hint_map)
        target_validation_records = attach_target_weak_event_hints(target_validation_records, hint_map)
    vocab = build_char_vocab(target_train_records)

    model = build_model_from_config(config)
    checkpoint = load_checkpoint(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    result = {
        "config_path": config_path.as_posix(),
        "split_dir": split_dir.as_posix(),
        "checkpoint_path": checkpoint_path.as_posix(),
        "ablation_modes": {},
        "comparisons": {},
        "notes": [
            "Ablation results are computed on the formal hybrid validation split only.",
            "zero_z_art zeroes the articulatory control before control fusion.",
            "zero_e_evt zeroes the event control path before control fusion.",
        ],
    }

    for mode in ABLATION_MODES:
        result["ablation_modes"][mode] = evaluate_mode(
            model=model,
            target_records=target_validation_records,
            source_records=source_validation_records,
            vocab=vocab,
            config=config,
            ablation_mode=mode,
        )

    baseline = result["ablation_modes"]["none"]
    for mode in ("zero_z_art", "zero_e_evt"):
        result["comparisons"][mode] = compare_modes(
            baseline=baseline,
            ablated=result["ablation_modes"][mode],
        )
    return result



def resolve_split_dir(project_root: Path, config: dict[str, object], split_dir: Path | None) -> Path:
    if split_dir is not None:
        return split_dir.resolve()
    split_dir_config = config["data"].get("split_dir")
    if split_dir_config in {None, ""}:
        raise ValueError("Ablation evaluation requires data.split_dir or --split-dir.")
    return (project_root / split_dir_config).resolve()


def resolve_target_weak_event_hint_map(
    config_path: Path,
    config: dict[str, object],
) -> dict[str, dict[str, object]] | None:
    hint_path_config = config["data"].get("target_weak_event_hints_path")
    if hint_path_config in {None, ""}:
        return None
    return load_target_weak_event_hint_map((config_path.parent.parent / hint_path_config).resolve())


def resolve_checkpoint_path(
    checkpoint_path: Path | None,
    experiment_metrics_path: Path | None,
) -> Path:
    if checkpoint_path is not None:
        return checkpoint_path.resolve()
    if experiment_metrics_path is None:
        raise ValueError("Ablation evaluation requires --checkpoint or --experiment-metrics.")
    payload = json.loads(experiment_metrics_path.resolve().read_text(encoding="utf-8"))
    checkpoint_ref = (
        payload.get("metrics", {})
        .get("training_run", {})
        .get("artifacts", {})
        .get("checkpoint_path")
    )
    if not checkpoint_ref:
        raise ValueError("Could not resolve checkpoint_path from experiment metrics.")
    return Path(checkpoint_ref).resolve()


def load_experiment_metrics_payload(path: Path) -> dict[str, object]:
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def load_checkpoint(path: Path) -> dict[str, object]:
    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        checkpoint = torch.load(path, map_location="cpu")
    if not isinstance(checkpoint, dict):
        raise TypeError(f"Unsupported checkpoint payload type: {type(checkpoint)!r}")
    return checkpoint


def build_model_from_config(config: dict[str, object]) -> OfflineMVPNoResidualModel:
    return OfflineMVPNoResidualModel(
        hidden_dim=int(config["model"]["hidden_dim"]),
        z_art_dim=int(config["model"]["z_art_dim"]),
        event_dim=int(config["model"]["event_dim"]),
        acoustic_dim=int(config["model"]["acoustic_dim"]),
        frame_length=int(config["model"]["frame_length"]),
        hop_length=int(config["model"]["hop_length"]),
        text_aux_dim=int(config["model"].get("text_aux_dim", 3)),
        text_aux_head_config=config["model"].get("text_aux_head_config"),
    )


def evaluate_mode(
    model: OfflineMVPNoResidualModel,
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
    vocab: dict[str, int],
    config: dict[str, object],
    ablation_mode: str,
) -> dict[str, object]:
    max_audio_sec = float(config["data"]["max_audio_sec"])
    target_batch_size = int(config["data"]["target_batch_size"])
    source_batch_size = int(config["data"]["source_batch_size"])
    frame_length = int(config["model"]["frame_length"])
    hop_length = int(config["model"]["hop_length"])
    loss_weights = config["losses"]
    text_feature_version = str(config["data"].get("target_text_feature_version", TEXT_FEATURE_VERSION_LEGACY_V0))

    target_batches = chunk_records(target_records, batch_size=target_batch_size)
    source_batches = chunk_records(source_records, batch_size=source_batch_size)
    batch_count = min(len(target_batches), len(source_batches))
    if batch_count == 0:
        raise ValueError("No validation batches available for ablation evaluation.")

    aggregate = {
        "target": init_metric_accumulator(),
        "source": init_metric_accumulator(),
        "shift": init_shift_accumulator(),
    }

    with torch.no_grad():
        for batch_index in range(batch_count):
            target_examples = load_target_examples_from_records(
                target_batches[batch_index],
                vocab=vocab,
                max_duration_sec=max_audio_sec,
                text_feature_version=text_feature_version,
            )
            source_examples = load_source_examples_from_records(
                source_batches[batch_index],
                max_duration_sec=max_audio_sec,
            )
            target_batch = collate_target_batch(target_examples)
            source_batch = collate_source_batch(source_examples)

            target_base_outputs = model(
                waveform=target_batch["waveform"],
                lengths=target_batch["audio_lengths"],
                ablation_mode="none",
            )
            source_base_outputs = model(
                waveform=source_batch["waveform"],
                lengths=source_batch["lengths"],
                ablation_mode="none",
            )
            target_outputs = target_base_outputs if ablation_mode == "none" else model(
                waveform=target_batch["waveform"],
                lengths=target_batch["audio_lengths"],
                ablation_mode=ablation_mode,
            )
            source_outputs = source_base_outputs if ablation_mode == "none" else model(
                waveform=source_batch["waveform"],
                lengths=source_batch["lengths"],
                ablation_mode=ablation_mode,
            )

            target_targets = build_frame_targets(
                waveform=target_batch["waveform"],
                lengths=target_batch["audio_lengths"],
                frame_length=frame_length,
                hop_length=hop_length,
                weak_event_hints=target_batch.get("weak_event_hints"),
            )
            source_targets = build_frame_targets(
                waveform=source_batch["waveform"],
                lengths=source_batch["lengths"],
                frame_length=frame_length,
                hop_length=hop_length,
            )
            _, target_metrics = compute_offline_mvp_loss(
                outputs=target_outputs,
                acoustic_target=target_targets["acoustic_target"],
                event_target=target_targets["event_target"],
                frame_mask=target_targets["frame_mask"],
                text_aux_target=target_batch["text_features"],
                texts=target_batch["texts"],
                weights=loss_weights,
                target_special_supervision=target_batch.get("target_special_supervision"),
                weak_event_target=target_targets.get("weak_event_target"),
                weak_event_weight=target_targets.get("weak_event_weight"),
                pause_boundary_strength=target_targets.get("pause_boundary_strength"),
                terminal_boundary_strength=target_targets.get("terminal_boundary_strength"),
                boundary_type_strengths=target_targets.get("boundary_type_strengths"),
                clause_role_strengths=target_targets.get("clause_role_strengths"),
                clause_transition_strengths=target_targets.get("clause_transition_strengths"),
                utterance_structure_strengths=target_targets.get("utterance_structure_strengths"),
            )
            _, source_metrics = compute_offline_mvp_loss(
                outputs=source_outputs,
                acoustic_target=source_targets["acoustic_target"],
                event_target=source_targets["event_target"],
                frame_mask=source_targets["frame_mask"],
                text_aux_target=None,
                texts=None,
                weights=loss_weights,
            )
            accumulate_metrics(aggregate["target"], target_metrics)
            accumulate_metrics(aggregate["source"], source_metrics)
            accumulate_shift_metrics(
                aggregate["shift"],
                target_base_outputs=target_base_outputs,
                target_outputs=target_outputs,
                target_frame_mask=target_targets["frame_mask"],
                source_base_outputs=source_base_outputs,
                source_outputs=source_outputs,
                source_frame_mask=source_targets["frame_mask"],
            )

    return {
        "ablation_mode": ablation_mode,
        "batch_count": batch_count,
        "target": finalize_metric_accumulator(aggregate["target"], batch_count),
        "source": finalize_metric_accumulator(aggregate["source"], batch_count),
        "shift": finalize_shift_accumulator(aggregate["shift"], batch_count),
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


def init_shift_accumulator() -> dict[str, float]:
    return {
        "target_acoustic_mae": 0.0,
        "target_text_aux_mae": 0.0,
        "source_acoustic_mae": 0.0,
        "source_text_aux_mae": 0.0,
    }


def accumulate_metrics(accumulator: dict[str, float], metrics: dict[str, float]) -> None:
    for key in accumulator:
        accumulator[key] += float(metrics[key])


def finalize_metric_accumulator(accumulator: dict[str, float], batch_count: int) -> dict[str, float]:
    return {
        key: round(value / max(1, batch_count), 6)
        for key, value in accumulator.items()
    }


def accumulate_shift_metrics(
    accumulator: dict[str, float],
    target_base_outputs: dict[str, torch.Tensor],
    target_outputs: dict[str, torch.Tensor],
    target_frame_mask: torch.Tensor,
    source_base_outputs: dict[str, torch.Tensor],
    source_outputs: dict[str, torch.Tensor],
    source_frame_mask: torch.Tensor,
) -> None:
    accumulator["target_acoustic_mae"] += masked_mae(
        baseline=target_base_outputs["acoustic"],
        ablated=target_outputs["acoustic"],
        frame_mask=target_frame_mask,
    )
    accumulator["target_text_aux_mae"] += float(
        (target_base_outputs["text_aux"] - target_outputs["text_aux"]).abs().mean().item()
    )
    accumulator["source_acoustic_mae"] += masked_mae(
        baseline=source_base_outputs["acoustic"],
        ablated=source_outputs["acoustic"],
        frame_mask=source_frame_mask,
    )
    accumulator["source_text_aux_mae"] += float(
        (source_base_outputs["text_aux"] - source_outputs["text_aux"]).abs().mean().item()
    )


def finalize_shift_accumulator(accumulator: dict[str, float], batch_count: int) -> dict[str, float]:
    return {
        key: round(value / max(1, batch_count), 6)
        for key, value in accumulator.items()
    }


def masked_mae(
    baseline: torch.Tensor,
    ablated: torch.Tensor,
    frame_mask: torch.Tensor,
) -> float:
    weights = frame_mask.to(baseline.dtype).unsqueeze(-1)
    diff = (baseline - ablated).abs() * weights
    denom = weights.sum().clamp_min(1.0)
    return float((diff.sum() / denom).item())


def chunk_records(records: list[dict[str, object]], batch_size: int) -> list[list[dict[str, object]]]:
    return [
        records[index : index + batch_size]
        for index in range(0, len(records), batch_size)
        if records[index : index + batch_size]
    ]


def compare_modes(
    baseline: dict[str, object],
    ablated: dict[str, object],
) -> dict[str, object]:
    return {
        "delta_target_loss_total": round(
            ablated["target"]["loss_total"] - baseline["target"]["loss_total"],
            6,
        ),
        "delta_source_loss_total": round(
            ablated["source"]["loss_total"] - baseline["source"]["loss_total"],
            6,
        ),
        "delta_target_loss_clause_transition_aux": round(
            ablated["target"]["loss_clause_transition_aux"] - baseline["target"]["loss_clause_transition_aux"],
            6,
        ),
        "delta_source_loss_clause_transition_aux": round(
            ablated["source"]["loss_clause_transition_aux"] - baseline["source"]["loss_clause_transition_aux"],
            6,
        ),
        "delta_target_loss_structural_clause_transition_aux": round(
            ablated["target"]["loss_structural_clause_transition_aux"]
            - baseline["target"]["loss_structural_clause_transition_aux"],
            6,
        ),
        "delta_source_loss_structural_clause_transition_aux": round(
            ablated["source"]["loss_structural_clause_transition_aux"]
            - baseline["source"]["loss_structural_clause_transition_aux"],
            6,
        ),
        "delta_target_loss_boundary_contrast_aux": round(
            ablated["target"]["loss_boundary_contrast_aux"] - baseline["target"]["loss_boundary_contrast_aux"],
            6,
        ),
        "delta_source_loss_boundary_contrast_aux": round(
            ablated["source"]["loss_boundary_contrast_aux"] - baseline["source"]["loss_boundary_contrast_aux"],
            6,
        ),
        "delta_target_loss_punctuation_profile_aux": round(
            ablated["target"]["loss_punctuation_profile_aux"] - baseline["target"]["loss_punctuation_profile_aux"],
            6,
        ),
        "delta_source_loss_punctuation_profile_aux": round(
            ablated["source"]["loss_punctuation_profile_aux"] - baseline["source"]["loss_punctuation_profile_aux"],
            6,
        ),
        "delta_target_loss_structural_clause_profile_aux": round(
            ablated["target"]["loss_structural_clause_profile_aux"]
            - baseline["target"]["loss_structural_clause_profile_aux"],
            6,
        ),
        "delta_source_loss_structural_clause_profile_aux": round(
            ablated["source"]["loss_structural_clause_profile_aux"]
            - baseline["source"]["loss_structural_clause_profile_aux"],
            6,
        ),
        "delta_target_loss_challenge_proxy_profile_aux": round(
            ablated["target"]["loss_challenge_proxy_profile_aux"]
            - baseline["target"]["loss_challenge_proxy_profile_aux"],
            6,
        ),
        "delta_source_loss_challenge_proxy_profile_aux": round(
            ablated["source"]["loss_challenge_proxy_profile_aux"]
            - baseline["source"]["loss_challenge_proxy_profile_aux"],
            6,
        ),
        "delta_target_loss_z_art_influence_aux": round(
            ablated["target"]["loss_z_art_influence_aux"] - baseline["target"]["loss_z_art_influence_aux"],
            6,
        ),
        "delta_source_loss_z_art_influence_aux": round(
            ablated["source"]["loss_z_art_influence_aux"] - baseline["source"]["loss_z_art_influence_aux"],
            6,
        ),
        "delta_target_loss_formal_special_clause_shape_aux": round(
            ablated["target"]["loss_formal_special_clause_shape_aux"]
            - baseline["target"]["loss_formal_special_clause_shape_aux"],
            6,
        ),
        "delta_source_loss_formal_special_clause_shape_aux": round(
            ablated["source"]["loss_formal_special_clause_shape_aux"]
            - baseline["source"]["loss_formal_special_clause_shape_aux"],
            6,
        ),
        "delta_target_loss_text_aux_effective": round(
            ablated["target"]["loss_text_aux_effective"] - baseline["target"]["loss_text_aux_effective"],
            6,
        ),
        "delta_source_loss_text_aux_effective": round(
            ablated["source"]["loss_text_aux_effective"] - baseline["source"]["loss_text_aux_effective"],
            6,
        ),
        "delta_target_loss_text_aux_structural": round(
            ablated["target"]["loss_text_aux_structural"] - baseline["target"]["loss_text_aux_structural"],
            6,
        ),
        "delta_target_loss_text_aux_lexical": round(
            ablated["target"]["loss_text_aux_lexical"] - baseline["target"]["loss_text_aux_lexical"],
            6,
        ),
        "delta_target_acoustic_mae": round(ablated["shift"]["target_acoustic_mae"], 6),
        "delta_source_acoustic_mae": round(ablated["shift"]["source_acoustic_mae"], 6),
        "delta_target_text_aux_mae": round(ablated["shift"]["target_text_aux_mae"], 6),
        "delta_source_text_aux_mae": round(ablated["shift"]["source_text_aux_mae"], 6),
    }


def build_markdown(result: dict[str, object]) -> str:
    lines = [
        "# offline MVP 控制消融评估",
        "",
        f"- config_path: {result['config_path']}",
        f"- split_dir: {result['split_dir']}",
        f"- checkpoint_path: {result['checkpoint_path']}",
        "",
    ]
    for mode, payload in result["ablation_modes"].items():
        lines.extend(
            [
                f"## {mode}",
                f"- batch_count: {payload['batch_count']}",
                f"- target.loss_total: {payload['target']['loss_total']}",
                f"- source.loss_total: {payload['source']['loss_total']}",
                f"- target.loss_text_aux_effective: {payload['target']['loss_text_aux_effective']}",
                f"- source.loss_text_aux_effective: {payload['source']['loss_text_aux_effective']}",
                f"- target.loss_text_aux_structural: {payload['target']['loss_text_aux_structural']}",
                f"- target.loss_text_aux_lexical: {payload['target']['loss_text_aux_lexical']}",
                f"- target.loss_clause_transition_aux: {payload['target']['loss_clause_transition_aux']}",
                f"- target.loss_structural_clause_transition_aux: {payload['target']['loss_structural_clause_transition_aux']}",
                f"- target.loss_boundary_contrast_aux: {payload['target']['loss_boundary_contrast_aux']}",
                f"- target.loss_punctuation_profile_aux: {payload['target']['loss_punctuation_profile_aux']}",
                f"- target.loss_structural_clause_profile_aux: {payload['target']['loss_structural_clause_profile_aux']}",
                f"- target.loss_challenge_proxy_profile_aux: {payload['target']['loss_challenge_proxy_profile_aux']}",
                f"- target.loss_z_art_influence_aux: {payload['target']['loss_z_art_influence_aux']}",
                f"- target.loss_formal_special_clause_shape_aux: {payload['target']['loss_formal_special_clause_shape_aux']}",
                f"- source.loss_clause_transition_aux: {payload['source']['loss_clause_transition_aux']}",
                f"- source.loss_structural_clause_transition_aux: {payload['source']['loss_structural_clause_transition_aux']}",
                f"- source.loss_boundary_contrast_aux: {payload['source']['loss_boundary_contrast_aux']}",
                f"- source.loss_punctuation_profile_aux: {payload['source']['loss_punctuation_profile_aux']}",
                f"- source.loss_structural_clause_profile_aux: {payload['source']['loss_structural_clause_profile_aux']}",
                f"- source.loss_challenge_proxy_profile_aux: {payload['source']['loss_challenge_proxy_profile_aux']}",
                f"- source.loss_z_art_influence_aux: {payload['source']['loss_z_art_influence_aux']}",
                f"- source.loss_formal_special_clause_shape_aux: {payload['source']['loss_formal_special_clause_shape_aux']}",
                f"- target_acoustic_mae: {payload['shift']['target_acoustic_mae']}",
                f"- source_acoustic_mae: {payload['shift']['source_acoustic_mae']}",
                f"- target_text_aux_mae: {payload['shift']['target_text_aux_mae']}",
                f"- source_text_aux_mae: {payload['shift']['source_text_aux_mae']}",
                "",
            ]
        )
    lines.append("## 对比")
    for mode, payload in result["comparisons"].items():
        lines.append(f"- {mode}: {json.dumps(payload, ensure_ascii=False)}")
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
    payload["metrics"]["ablation_eval"] = result
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
