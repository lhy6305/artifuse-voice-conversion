from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn

from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_training import (
    DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    compute_centered_frame_rms,
    compute_frame_logspec,
    extract_training_batch,
    extract_training_runtime,
    frame_waveform_sequence,
    load_training_package_payload,
    normalize_frames_unit_rms,
    resolve_voicing_supervision_control,
)
from v5vc.stage5_speech_emergence_probe import compute_pearson_correlation


PROBE_STAGES = [
    "periodic_hidden",
    "noise_hidden",
    "fused_hidden",
    "decoder_hidden",
    "waveform_decoder_base_logits",
]

DEFAULT_WAVEFORM_MLP_HIDDEN_DIM = 128
DEFAULT_WAVEFORM_MLP_STEPS = 200
DEFAULT_WAVEFORM_MLP_LR = 1.0e-3


def analyze_stage5_nores_representation_oracle_probe(
    *,
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    dataset_index_path: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    device: str,
    decoder_branch_mean_mix_alpha: float,
    active_frame_rms_threshold: float = DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    logspec_bins: int = 48,
    ridge_lambda: float = 1.0,
    test_stride: int = 3,
    waveform_mlp_hidden_dim: int = DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    waveform_mlp_steps: int = DEFAULT_WAVEFORM_MLP_STEPS,
    waveform_mlp_lr: float = DEFAULT_WAVEFORM_MLP_LR,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_index_path = dataset_index_path.resolve()
    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
        selection_target=selection_target,
    )
    resolved_selection_target = (
        str(selection_summary.get("_resolved_selection_target", selection_target))
        if isinstance(selection_summary, dict)
        else str(selection_target)
    )
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the representation oracle probe.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    )
    resolved_device = torch.device(device)
    model = model.to(resolved_device)
    model.eval()

    per_record_rows: list[dict[str, object]] = []
    record_feature_cache: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            payload = load_training_package_payload(Path(str(entry["training_package_path"])).resolve())
            batch = extract_training_batch(payload)
            runtime = extract_training_runtime(payload)
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"].to(
                    device=resolved_device,
                    dtype=torch.float32,
                ),
                noise_branch_features=batch["noise_branch_features"].to(
                    device=resolved_device,
                    dtype=torch.float32,
                ),
                decoder_branch_mean_mix_alpha=float(decoder_branch_mean_mix_alpha),
            )
            target_bundle = build_target_proxy_bundle(
                batch=batch,
                aligned_waveform=batch["aligned_waveform"],
                frame_length=int(runtime["frame_length"]),
                hop_length=int(runtime["hop_length"]),
                periodic_gate_target=batch["periodic_gate_target"],
                active_frame_rms_threshold=float(active_frame_rms_threshold),
                logspec_bins=int(logspec_bins),
            )
            stage_rows: list[dict[str, object]] = []
            stage_feature_cache: dict[str, dict[str, torch.Tensor]] = {}
            for stage_name in PROBE_STAGES:
                stage_sequence = outputs.get(stage_name)
                if stage_sequence is None:
                    continue
                metrics, feature_cache = evaluate_oracle_probe_stage(
                    stage_name=stage_name,
                    stage_sequence=stage_sequence.detach().cpu().to(torch.float32),
                    target_rms=target_bundle["target_rms"],
                    target_voicing=target_bundle["target_voicing"],
                    target_logspec=target_bundle["target_logspec"],
                    target_waveform_frames=target_bundle["target_waveform_frames"],
                    active_mask=target_bundle["active_mask"],
                    ridge_lambda=float(ridge_lambda),
                    test_stride=int(test_stride),
                    waveform_mlp_hidden_dim=int(waveform_mlp_hidden_dim),
                    waveform_mlp_steps=int(waveform_mlp_steps),
                    waveform_mlp_lr=float(waveform_mlp_lr),
                )
                stage_rows.append(metrics)
                stage_feature_cache[str(stage_name)] = feature_cache
            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": str(entry["training_package_path"]),
                    "frame_count": int(target_bundle["frame_count"]),
                    "active_frame_count": int(target_bundle["active_frame_count"]),
                    "voicing_source": str(target_bundle["voicing_source"]),
                    "stages": stage_rows,
                }
            )
            record_feature_cache.append(
                {
                    "record_id": str(entry["record_id"]),
                    "stage_feature_cache": stage_feature_cache,
                }
            )

    stage_aggregates = build_stage_aggregates(per_record_rows)
    cross_record_stage_aggregates = build_leave_one_record_out_stage_aggregates(
        record_feature_cache=record_feature_cache,
        ridge_lambda=float(ridge_lambda),
        waveform_mlp_hidden_dim=int(waveform_mlp_hidden_dim),
        waveform_mlp_steps=int(waveform_mlp_steps),
        waveform_mlp_lr=float(waveform_mlp_lr),
    )
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": (
            None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix()
        ),
        "selection_target": None if checkpoint_selection_path is None else resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "probe_config": {
            "device": str(resolved_device),
            "decoder_branch_mean_mix_alpha": float(decoder_branch_mean_mix_alpha),
            "active_frame_rms_threshold": float(active_frame_rms_threshold),
            "logspec_bins": int(logspec_bins),
            "ridge_lambda": float(ridge_lambda),
            "test_stride": int(test_stride),
            "waveform_mlp_hidden_dim": int(waveform_mlp_hidden_dim),
            "waveform_mlp_steps": int(waveform_mlp_steps),
            "waveform_mlp_lr": float(waveform_mlp_lr),
            "stage_names": list(PROBE_STAGES),
        },
        "stage_aggregates": stage_aggregates,
        "cross_record_stage_aggregates": cross_record_stage_aggregates,
        "oracle_sufficiency_summary": build_oracle_sufficiency_summary(
            stage_aggregates,
            cross_record_stage_aggregates,
        ),
        "records": per_record_rows,
        "notes": [
            "This is an oracle-style representation sufficiency probe: it freezes the Stage5 checkpoint and fits only cheap ridge readouts on top of intermediate sequences.",
            "The purpose is to test whether target-side frame RMS, voicing, and compressed log-spectrum proxies remain recoverable from each stage, not to rank checkpoints by audible quality.",
            "Record-level evaluation uses an in-record temporal holdout split so a stage must generalize beyond the exact frames used to fit the readout.",
            "Cross-record leave-one-record-out aggregates test whether a single shared linear decoder family can generalize to held-out records from each stage, which is closer to the production output-head question.",
        ],
    }
    json_path = output_dir / "stage5_representation_oracle_probe.json"
    md_path = output_dir / "stage5_representation_oracle_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(build_markdown(summary), encoding="utf-8", newline="\n")


def build_target_proxy_bundle(
    *,
    batch: dict[str, torch.Tensor],
    aligned_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    periodic_gate_target: torch.Tensor,
    active_frame_rms_threshold: float,
    logspec_bins: int,
) -> dict[str, object]:
    aligned_frames = frame_waveform_sequence(
        waveform=aligned_waveform.detach().cpu().to(torch.float32),
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    frame_count = int(aligned_frames.shape[0])
    aligned_rms = compute_centered_frame_rms(aligned_frames).clamp_min(1.0e-6)
    active_mask = aligned_rms >= float(active_frame_rms_threshold)
    if not bool(active_mask.any()):
        active_mask = torch.ones_like(aligned_rms, dtype=torch.bool)
    target_voicing, voicing_source = resolve_voicing_supervision_control(
        frame_count=int(frame_count),
        periodic_gate_target=periodic_gate_target.detach().cpu().to(torch.float32),
        vuv_target=batch.get("vuv_target"),
        voiced_proxy_target=batch.get("voiced_proxy_target"),
        aper_target=batch.get("aper_target"),
        aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
    )
    target_logspec = compress_logspec_bins(
        compute_frame_logspec(normalize_frames_unit_rms(aligned_frames)),
        output_bins=int(logspec_bins),
    )
    return {
        "frame_count": int(frame_count),
        "active_frame_count": int(active_mask.to(torch.int64).sum().item()),
        "active_mask": active_mask,
        "target_rms": aligned_rms,
        "target_voicing": target_voicing.detach().cpu().to(torch.float32),
        "target_logspec": target_logspec.detach().cpu().to(torch.float32),
        "target_waveform_frames": normalize_frames_unit_rms(aligned_frames).detach().cpu().to(torch.float32),
        "voicing_source": str(voicing_source),
    }


def compress_logspec_bins(logspec: torch.Tensor, *, output_bins: int) -> torch.Tensor:
    resolved_bins = max(1, int(output_bins))
    logspec_tensor = logspec.detach().cpu().to(torch.float32)
    if int(logspec_tensor.shape[0]) <= 0:
        return logspec_tensor.new_zeros((0, resolved_bins))
    pooled = F.adaptive_avg_pool1d(logspec_tensor.unsqueeze(1), resolved_bins).squeeze(1)
    return pooled


def build_temporal_holdout_masks(frame_count: int, *, test_stride: int) -> tuple[torch.Tensor, torch.Tensor]:
    resolved_count = max(0, int(frame_count))
    if resolved_count <= 1:
        train_mask = torch.ones((resolved_count,), dtype=torch.bool)
        test_mask = torch.ones((resolved_count,), dtype=torch.bool)
        return train_mask, test_mask
    indices = torch.arange(resolved_count, dtype=torch.int64)
    resolved_stride = max(2, int(test_stride))
    test_mask = indices.remainder(resolved_stride).eq(0)
    train_mask = ~test_mask
    if not bool(train_mask.any()) or not bool(test_mask.any()):
        split_index = max(1, resolved_count // 3)
        test_mask = torch.zeros((resolved_count,), dtype=torch.bool)
        test_mask[-split_index:] = True
        train_mask = ~test_mask
    return train_mask, test_mask


def fit_ridge_readout(
    *,
    train_x: torch.Tensor,
    train_y: torch.Tensor,
    ridge_lambda: float,
) -> dict[str, torch.Tensor]:
    x = train_x.to(torch.float32)
    y = train_y.to(torch.float32)
    x_mean = x.mean(dim=0, keepdim=True)
    x_std = x.std(dim=0, unbiased=False, keepdim=True).clamp_min(1.0e-4)
    y_mean = y.mean(dim=0, keepdim=True)
    centered_x = (x - x_mean) / x_std
    centered_y = y - y_mean
    feature_dim = int(centered_x.shape[-1])
    gram = centered_x.transpose(0, 1) @ centered_x
    regularizer = float(ridge_lambda) * torch.eye(feature_dim, dtype=centered_x.dtype)
    weights = torch.linalg.solve(
        gram + regularizer,
        centered_x.transpose(0, 1) @ centered_y,
    )
    return {
        "x_mean": x_mean,
        "x_std": x_std,
        "y_mean": y_mean,
        "weights": weights,
    }


def predict_ridge_readout(readout: dict[str, torch.Tensor], x: torch.Tensor) -> torch.Tensor:
    normalized_x = (x.to(torch.float32) - readout["x_mean"]) / readout["x_std"]
    return normalized_x @ readout["weights"] + readout["y_mean"]


def compute_mean_frame_cosine(prediction: torch.Tensor, target: torch.Tensor) -> float:
    pred = prediction.to(torch.float32)
    tgt = target.to(torch.float32)
    pred = pred / pred.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    tgt = tgt / tgt.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    return float((pred * tgt).sum(dim=1).mean().item())


def predict_mlp_readout(
    *,
    train_x: torch.Tensor,
    train_y: torch.Tensor,
    test_x: torch.Tensor,
    hidden_dim: int,
    train_steps: int,
    learning_rate: float,
) -> torch.Tensor:
    if int(test_x.shape[0]) <= 0:
        return train_y.new_zeros((0, int(train_y.shape[-1])))
    if int(train_x.shape[0]) <= 1 or int(hidden_dim) <= 0 or int(train_steps) <= 0:
        target_mean = train_y.mean(dim=0, keepdim=True)
        return target_mean.expand(int(test_x.shape[0]), -1).clone()
    x_train = train_x.detach().cpu().to(torch.float32)
    y_train = train_y.detach().cpu().to(torch.float32)
    x_test = test_x.detach().cpu().to(torch.float32)
    x_mean = x_train.mean(dim=0, keepdim=True)
    x_std = x_train.std(dim=0, unbiased=False, keepdim=True).clamp_min(1.0e-4)
    y_mean = y_train.mean(dim=0, keepdim=True)
    y_std = y_train.std(dim=0, unbiased=False, keepdim=True).clamp_min(1.0e-3)
    normalized_train_x = (x_train - x_mean) / x_std
    normalized_test_x = (x_test - x_mean) / x_std
    normalized_train_y = (y_train - y_mean) / y_std
    with torch.random.fork_rng():
        torch.manual_seed(0)
        model = nn.Sequential(
            nn.Linear(int(normalized_train_x.shape[-1]), int(hidden_dim)),
            nn.SiLU(),
            nn.Linear(int(hidden_dim), int(normalized_train_y.shape[-1])),
        )
    optimizer = torch.optim.Adam(model.parameters(), lr=float(learning_rate))
    with torch.enable_grad():
        for _ in range(max(1, int(train_steps))):
            optimizer.zero_grad(set_to_none=True)
            prediction = model(normalized_train_x)
            loss = F.mse_loss(prediction, normalized_train_y)
            loss.backward()
            optimizer.step()
        normalized_test_y = model(normalized_test_x).detach()
    return normalized_test_y * y_std + y_mean


def evaluate_oracle_probe_stage(
    *,
    stage_name: str,
    stage_sequence: torch.Tensor,
    target_rms: torch.Tensor,
    target_voicing: torch.Tensor,
    target_logspec: torch.Tensor,
    target_waveform_frames: torch.Tensor,
    active_mask: torch.Tensor,
    ridge_lambda: float,
    test_stride: int,
    waveform_mlp_hidden_dim: int,
    waveform_mlp_steps: int,
    waveform_mlp_lr: float,
) -> tuple[dict[str, object], dict[str, torch.Tensor]]:
    common_frame_count = min(
        int(stage_sequence.shape[0]),
        int(target_rms.shape[0]),
        int(target_voicing.shape[0]),
        int(target_logspec.shape[0]),
        int(target_waveform_frames.shape[0]),
        int(active_mask.shape[0]),
    )
    features = stage_sequence[:common_frame_count].detach().cpu().to(torch.float32)
    rms_target = target_rms[:common_frame_count].detach().cpu().to(torch.float32).unsqueeze(-1)
    voicing_target = target_voicing[:common_frame_count].detach().cpu().to(torch.float32).unsqueeze(-1)
    logspec_target = target_logspec[:common_frame_count].detach().cpu().to(torch.float32)
    waveform_target = target_waveform_frames[:common_frame_count].detach().cpu().to(torch.float32)
    effective_mask = active_mask[:common_frame_count].detach().cpu().to(torch.bool)
    if not bool(effective_mask.any()):
        effective_mask = torch.ones((common_frame_count,), dtype=torch.bool)
    features = features[effective_mask]
    rms_target = rms_target[effective_mask]
    voicing_target = voicing_target[effective_mask]
    logspec_target = logspec_target[effective_mask]
    waveform_target = waveform_target[effective_mask]
    effective_count = int(features.shape[0])
    train_mask, test_mask = build_temporal_holdout_masks(effective_count, test_stride=int(test_stride))

    def fit_and_predict(target: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if int(target.shape[0]) <= 1:
            return target.clone(), target.clone()
        readout = fit_ridge_readout(
            train_x=features[train_mask],
            train_y=target[train_mask],
            ridge_lambda=float(ridge_lambda),
        )
        return predict_ridge_readout(readout, features[train_mask]), predict_ridge_readout(readout, features[test_mask])

    _, rms_test_pred = fit_and_predict(rms_target)
    _, voicing_test_pred = fit_and_predict(voicing_target)
    _, logspec_test_pred = fit_and_predict(logspec_target)
    _, waveform_test_pred = fit_and_predict(waveform_target)
    waveform_test_pred_mlp = predict_mlp_readout(
        train_x=features[train_mask],
        train_y=waveform_target[train_mask],
        test_x=features[test_mask],
        hidden_dim=int(waveform_mlp_hidden_dim),
        train_steps=int(waveform_mlp_steps),
        learning_rate=float(waveform_mlp_lr),
    )

    rms_test_target = rms_target[test_mask]
    voicing_test_target = voicing_target[test_mask]
    logspec_test_target = logspec_target[test_mask]
    waveform_test_target = waveform_target[test_mask]

    voicing_prob = voicing_test_pred.clamp(0.0, 1.0)
    voicing_accuracy = (
        voicing_prob.ge(0.5).eq(voicing_test_target.ge(0.5)).to(torch.float32).mean()
        if int(voicing_prob.shape[0]) > 0
        else voicing_prob.new_tensor(0.0)
    )
    metrics = {
        "stage_name": str(stage_name),
        "active_frame_count": int(effective_count),
        "train_frame_count": int(train_mask.to(torch.int64).sum().item()),
        "test_frame_count": int(test_mask.to(torch.int64).sum().item()),
        "oracle_rms_corr": round(
            float(compute_pearson_correlation(rms_test_pred.view(-1), rms_test_target.view(-1))),
            6,
        ),
        "oracle_rms_mae": round(
            float((rms_test_pred - rms_test_target).abs().mean().item()),
            6,
        ),
        "oracle_vuv_corr": round(
            float(compute_pearson_correlation(voicing_prob.view(-1), voicing_test_target.view(-1))),
            6,
        ),
        "oracle_vuv_accuracy": round(float(voicing_accuracy.item()), 6),
        "oracle_logspec_frame_cosine_mean": round(
            compute_mean_frame_cosine(logspec_test_pred, logspec_test_target),
            6,
        ),
        "oracle_logspec_mae": round(
            float((logspec_test_pred - logspec_test_target).abs().mean().item()),
            6,
        ),
        "oracle_waveform_frame_cosine_mean": round(
            compute_mean_frame_cosine(waveform_test_pred, waveform_test_target),
            6,
        ),
        "oracle_waveform_frame_mae": round(
            float((waveform_test_pred - waveform_test_target).abs().mean().item()),
            6,
        ),
        "oracle_waveform_mlp_frame_cosine_mean": round(
            compute_mean_frame_cosine(waveform_test_pred_mlp, waveform_test_target),
            6,
        ),
        "oracle_waveform_mlp_frame_mae": round(
            float((waveform_test_pred_mlp - waveform_test_target).abs().mean().item()),
            6,
        ),
    }
    feature_cache = {
        "features": features,
        "target_rms": rms_target,
        "target_voicing": voicing_target,
        "target_logspec": logspec_target,
        "target_waveform_frames": waveform_target,
    }
    return metrics, feature_cache


def build_stage_aggregates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    stage_rows: dict[str, list[dict[str, object]]] = {}
    for record in records:
        for stage in record.get("stages", []):
            stage_rows.setdefault(str(stage["stage_name"]), []).append(stage)
    aggregates: list[dict[str, object]] = []
    for stage_name in PROBE_STAGES:
        rows = stage_rows.get(stage_name, [])
        if not rows:
            continue
        def mean_of(key: str) -> float:
            return round(
                sum(float(row.get(key, 0.0)) for row in rows) / float(len(rows)),
                6,
            )
        aggregates.append(
            {
                "stage_name": stage_name,
                "record_count": len(rows),
                "oracle_rms_corr_mean": mean_of("oracle_rms_corr"),
                "oracle_rms_mae_mean": mean_of("oracle_rms_mae"),
                "oracle_vuv_corr_mean": mean_of("oracle_vuv_corr"),
                "oracle_vuv_accuracy_mean": mean_of("oracle_vuv_accuracy"),
                "oracle_logspec_frame_cosine_mean": mean_of("oracle_logspec_frame_cosine_mean"),
                "oracle_logspec_mae_mean": mean_of("oracle_logspec_mae"),
                "oracle_waveform_frame_cosine_mean": mean_of("oracle_waveform_frame_cosine_mean"),
                "oracle_waveform_frame_mae_mean": mean_of("oracle_waveform_frame_mae"),
                "oracle_waveform_mlp_frame_cosine_mean": mean_of("oracle_waveform_mlp_frame_cosine_mean"),
                "oracle_waveform_mlp_frame_mae_mean": mean_of("oracle_waveform_mlp_frame_mae"),
            }
        )
    return aggregates


def build_leave_one_record_out_stage_aggregates(
    *,
    record_feature_cache: list[dict[str, object]],
    ridge_lambda: float,
    waveform_mlp_hidden_dim: int,
    waveform_mlp_steps: int,
    waveform_mlp_lr: float,
) -> list[dict[str, object]]:
    stage_rows: list[dict[str, object]] = []
    if len(record_feature_cache) <= 1:
        return stage_rows
    for stage_name in PROBE_STAGES:
        heldout_rows: list[dict[str, object]] = []
        for heldout_index, heldout_record in enumerate(record_feature_cache):
            heldout_stage_cache = heldout_record["stage_feature_cache"].get(stage_name)
            if heldout_stage_cache is None:
                continue
            train_feature_chunks: list[torch.Tensor] = []
            train_rms_chunks: list[torch.Tensor] = []
            train_voicing_chunks: list[torch.Tensor] = []
            train_logspec_chunks: list[torch.Tensor] = []
            for train_index, train_record in enumerate(record_feature_cache):
                if train_index == heldout_index:
                    continue
                train_stage_cache = train_record["stage_feature_cache"].get(stage_name)
                if train_stage_cache is None:
                    continue
                train_feature_chunks.append(train_stage_cache["features"])
                train_rms_chunks.append(train_stage_cache["target_rms"])
                train_voicing_chunks.append(train_stage_cache["target_voicing"])
                train_logspec_chunks.append(train_stage_cache["target_logspec"])
            if not train_feature_chunks:
                continue
            train_x = torch.cat(train_feature_chunks, dim=0)
            train_rms = torch.cat(train_rms_chunks, dim=0)
            train_voicing = torch.cat(train_voicing_chunks, dim=0)
            train_logspec = torch.cat(train_logspec_chunks, dim=0)
            train_waveform = torch.cat(
                [item["stage_feature_cache"][stage_name]["target_waveform_frames"] for idx, item in enumerate(record_feature_cache) if idx != heldout_index and stage_name in item["stage_feature_cache"]],
                dim=0,
            )
            test_x = heldout_stage_cache["features"]
            test_rms = heldout_stage_cache["target_rms"]
            test_voicing = heldout_stage_cache["target_voicing"]
            test_logspec = heldout_stage_cache["target_logspec"]
            test_waveform = heldout_stage_cache["target_waveform_frames"]
            rms_readout = fit_ridge_readout(train_x=train_x, train_y=train_rms, ridge_lambda=float(ridge_lambda))
            voicing_readout = fit_ridge_readout(
                train_x=train_x,
                train_y=train_voicing,
                ridge_lambda=float(ridge_lambda),
            )
            logspec_readout = fit_ridge_readout(
                train_x=train_x,
                train_y=train_logspec,
                ridge_lambda=float(ridge_lambda),
            )
            waveform_readout = fit_ridge_readout(
                train_x=train_x,
                train_y=train_waveform,
                ridge_lambda=float(ridge_lambda),
            )
            rms_pred = predict_ridge_readout(rms_readout, test_x)
            voicing_pred = predict_ridge_readout(voicing_readout, test_x).clamp(0.0, 1.0)
            logspec_pred = predict_ridge_readout(logspec_readout, test_x)
            waveform_pred = predict_ridge_readout(waveform_readout, test_x)
            waveform_pred_mlp = predict_mlp_readout(
                train_x=train_x,
                train_y=train_waveform,
                test_x=test_x,
                hidden_dim=int(waveform_mlp_hidden_dim),
                train_steps=int(waveform_mlp_steps),
                learning_rate=float(waveform_mlp_lr),
            )
            voicing_accuracy = (
                voicing_pred.ge(0.5).eq(test_voicing.ge(0.5)).to(torch.float32).mean()
                if int(test_voicing.shape[0]) > 0
                else test_voicing.new_tensor(0.0)
            )
            heldout_rows.append(
                {
                    "record_id": str(heldout_record["record_id"]),
                    "oracle_rms_corr": float(compute_pearson_correlation(rms_pred.view(-1), test_rms.view(-1))),
                    "oracle_rms_mae": float((rms_pred - test_rms).abs().mean().item()),
                    "oracle_vuv_corr": float(
                        compute_pearson_correlation(voicing_pred.view(-1), test_voicing.view(-1))
                    ),
                    "oracle_vuv_accuracy": float(voicing_accuracy.item()),
                    "oracle_logspec_frame_cosine_mean": compute_mean_frame_cosine(logspec_pred, test_logspec),
                    "oracle_logspec_mae": float((logspec_pred - test_logspec).abs().mean().item()),
                    "oracle_waveform_frame_cosine_mean": compute_mean_frame_cosine(waveform_pred, test_waveform),
                    "oracle_waveform_frame_mae": float((waveform_pred - test_waveform).abs().mean().item()),
                    "oracle_waveform_mlp_frame_cosine_mean": compute_mean_frame_cosine(
                        waveform_pred_mlp,
                        test_waveform,
                    ),
                    "oracle_waveform_mlp_frame_mae": float(
                        (waveform_pred_mlp - test_waveform).abs().mean().item()
                    ),
                }
            )
        if not heldout_rows:
            continue
        def mean_of(key: str) -> float:
            return round(sum(float(row[key]) for row in heldout_rows) / float(len(heldout_rows)), 6)
        stage_rows.append(
            {
                "stage_name": stage_name,
                "record_count": len(heldout_rows),
                "oracle_rms_corr_mean": mean_of("oracle_rms_corr"),
                "oracle_rms_mae_mean": mean_of("oracle_rms_mae"),
                "oracle_vuv_corr_mean": mean_of("oracle_vuv_corr"),
                "oracle_vuv_accuracy_mean": mean_of("oracle_vuv_accuracy"),
                "oracle_logspec_frame_cosine_mean": mean_of("oracle_logspec_frame_cosine_mean"),
                "oracle_logspec_mae_mean": mean_of("oracle_logspec_mae"),
                "oracle_waveform_frame_cosine_mean": mean_of("oracle_waveform_frame_cosine_mean"),
                "oracle_waveform_frame_mae_mean": mean_of("oracle_waveform_frame_mae"),
                "oracle_waveform_mlp_frame_cosine_mean": mean_of("oracle_waveform_mlp_frame_cosine_mean"),
                "oracle_waveform_mlp_frame_mae_mean": mean_of("oracle_waveform_mlp_frame_mae"),
                "heldout_records": heldout_rows,
            }
        )
    return stage_rows


def build_oracle_sufficiency_summary(
    stage_aggregates: list[dict[str, object]],
    cross_record_stage_aggregates: list[dict[str, object]],
) -> dict[str, object]:
    by_stage = {str(item["stage_name"]): item for item in stage_aggregates}
    cross_record_by_stage = {str(item["stage_name"]): item for item in cross_record_stage_aggregates}
    if not by_stage:
        return {"diagnosis": "missing_stage_aggregates"}
    best_logspec_stage = max(
        stage_aggregates,
        key=lambda item: float(item.get("oracle_logspec_frame_cosine_mean", 0.0)),
    )
    decoder_hidden = by_stage.get("decoder_hidden")
    base_logits = by_stage.get("waveform_decoder_base_logits")
    if decoder_hidden is None or base_logits is None:
        return {
            "best_logspec_stage": str(best_logspec_stage["stage_name"]),
            "diagnosis": "missing_decoder_hidden_or_base_logits_aggregate",
        }
    decoder_advantage = round(
        float(decoder_hidden["oracle_logspec_frame_cosine_mean"])
        - float(base_logits["oracle_logspec_frame_cosine_mean"]),
        6,
    )
    vuv_advantage = round(
        float(decoder_hidden["oracle_vuv_accuracy_mean"])
        - float(base_logits["oracle_vuv_accuracy_mean"]),
        6,
    )
    rms_advantage = round(
        float(decoder_hidden["oracle_rms_corr_mean"])
        - float(base_logits["oracle_rms_corr_mean"]),
        6,
    )
    cross_record_best_logspec_stage = None
    cross_record_best_waveform_stage = None
    cross_record_best_waveform_mlp_stage = None
    cross_record_diagnosis = "missing_cross_record_stage_aggregates"
    cross_record_decoder_advantage = None
    cross_record_decoder_waveform_advantage = None
    cross_record_decoder_waveform_mlp_advantage = None
    if cross_record_stage_aggregates:
        cross_record_best_logspec_stage = max(
            cross_record_stage_aggregates,
            key=lambda item: float(item.get("oracle_logspec_frame_cosine_mean", 0.0)),
        )
        cross_record_best_waveform_stage = max(
            cross_record_stage_aggregates,
            key=lambda item: float(item.get("oracle_waveform_frame_cosine_mean", 0.0)),
        )
        cross_record_best_waveform_mlp_stage = max(
            cross_record_stage_aggregates,
            key=lambda item: float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)),
        )
        cross_record_decoder_hidden = cross_record_by_stage.get("decoder_hidden")
        cross_record_base_logits = cross_record_by_stage.get("waveform_decoder_base_logits")
        if cross_record_decoder_hidden is not None and cross_record_base_logits is not None:
            cross_record_decoder_advantage = round(
                float(cross_record_decoder_hidden["oracle_logspec_frame_cosine_mean"])
                - float(cross_record_base_logits["oracle_logspec_frame_cosine_mean"]),
                6,
            )
            cross_record_decoder_waveform_advantage = round(
                float(cross_record_decoder_hidden["oracle_waveform_frame_cosine_mean"])
                - float(cross_record_base_logits["oracle_waveform_frame_cosine_mean"]),
                6,
            )
            cross_record_decoder_waveform_mlp_advantage = round(
                float(cross_record_decoder_hidden["oracle_waveform_mlp_frame_cosine_mean"])
                - float(cross_record_base_logits["oracle_waveform_mlp_frame_cosine_mean"]),
                6,
            )
            if cross_record_decoder_advantage >= 0.05 or (
                cross_record_decoder_waveform_advantage is not None
                and cross_record_decoder_waveform_advantage >= 0.05
            ) or (
                cross_record_decoder_waveform_mlp_advantage is not None
                and cross_record_decoder_waveform_mlp_advantage >= 0.05
            ):
                cross_record_diagnosis = "decoder_hidden_supports_a_better_shared_linear_readout_than_base_logits"
            elif float(cross_record_best_logspec_stage.get("oracle_logspec_frame_cosine_mean", 0.0)) < 0.5:
                cross_record_diagnosis = "shared_linear_oracle_fails_across_records_upstream_representation_may_be_insufficient"
            else:
                cross_record_diagnosis = "shared_linear_oracle_recovers_coarse_structure_from_multiple_stages"
    diagnosis = "needs_more_localization"
    if decoder_advantage >= 0.05 and (vuv_advantage >= 0.05 or rms_advantage >= 0.05):
        diagnosis = "decoder_hidden_contains_recoverable_structure_beyond_current_head"
    elif float(best_logspec_stage.get("oracle_logspec_frame_cosine_mean", 0.0)) < 0.5:
        diagnosis = "oracle_readout_fails_across_all_stages_upstream_representation_may_be_insufficient"
    elif cross_record_diagnosis == "decoder_hidden_supports_a_better_shared_linear_readout_than_base_logits":
        diagnosis = cross_record_diagnosis
    elif cross_record_diagnosis == "shared_linear_oracle_fails_across_records_upstream_representation_may_be_insufficient":
        diagnosis = cross_record_diagnosis
    return {
        "best_logspec_stage": str(best_logspec_stage["stage_name"]),
        "best_logspec_value": float(best_logspec_stage["oracle_logspec_frame_cosine_mean"]),
        "decoder_hidden_vs_base_logits_logspec_advantage": decoder_advantage,
        "decoder_hidden_vs_base_logits_vuv_accuracy_advantage": vuv_advantage,
        "decoder_hidden_vs_base_logits_rms_corr_advantage": rms_advantage,
        "cross_record_best_logspec_stage": (
            None if cross_record_best_logspec_stage is None else str(cross_record_best_logspec_stage["stage_name"])
        ),
        "cross_record_best_logspec_value": (
            None
            if cross_record_best_logspec_stage is None
            else float(cross_record_best_logspec_stage["oracle_logspec_frame_cosine_mean"])
        ),
        "cross_record_best_waveform_stage": (
            None if cross_record_best_waveform_stage is None else str(cross_record_best_waveform_stage["stage_name"])
        ),
        "cross_record_best_waveform_value": (
            None
            if cross_record_best_waveform_stage is None
            else float(cross_record_best_waveform_stage["oracle_waveform_frame_cosine_mean"])
        ),
        "cross_record_best_waveform_mlp_stage": (
            None
            if cross_record_best_waveform_mlp_stage is None
            else str(cross_record_best_waveform_mlp_stage["stage_name"])
        ),
        "cross_record_best_waveform_mlp_value": (
            None
            if cross_record_best_waveform_mlp_stage is None
            else float(cross_record_best_waveform_mlp_stage["oracle_waveform_mlp_frame_cosine_mean"])
        ),
        "cross_record_decoder_hidden_vs_base_logits_logspec_advantage": cross_record_decoder_advantage,
        "cross_record_decoder_hidden_vs_base_logits_waveform_advantage": cross_record_decoder_waveform_advantage,
        "cross_record_decoder_hidden_vs_base_logits_waveform_mlp_advantage": (
            cross_record_decoder_waveform_mlp_advantage
        ),
        "cross_record_diagnosis": cross_record_diagnosis,
        "diagnosis": diagnosis,
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Representation Oracle Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- oracle_sufficiency_summary: {json.dumps(summary['oracle_sufficiency_summary'], ensure_ascii=False)}",
        "",
        "## Stage Aggregates",
    ]
    for row in summary.get("stage_aggregates", []):
        lines.append(
            "- "
            + f"{row['stage_name']}: "
            + f"logspec_cosine={row['oracle_logspec_frame_cosine_mean']}, "
            + f"logspec_mae={row['oracle_logspec_mae_mean']}, "
            + f"waveform_frame_cosine={row['oracle_waveform_frame_cosine_mean']}, "
            + f"waveform_mlp_frame_cosine={row['oracle_waveform_mlp_frame_cosine_mean']}, "
            + f"rms_corr={row['oracle_rms_corr_mean']}, "
            + f"vuv_accuracy={row['oracle_vuv_accuracy_mean']}, "
            + f"vuv_corr={row['oracle_vuv_corr_mean']}"
        )
    lines.append("")
    lines.append("## Cross-Record Stage Aggregates")
    for row in summary.get("cross_record_stage_aggregates", []):
        lines.append(
            "- "
            + f"{row['stage_name']}: "
            + f"logspec_cosine={row['oracle_logspec_frame_cosine_mean']}, "
            + f"logspec_mae={row['oracle_logspec_mae_mean']}, "
            + f"waveform_frame_cosine={row['oracle_waveform_frame_cosine_mean']}, "
            + f"waveform_mlp_frame_cosine={row['oracle_waveform_mlp_frame_cosine_mean']}, "
            + f"rms_corr={row['oracle_rms_corr_mean']}, "
            + f"vuv_accuracy={row['oracle_vuv_accuracy_mean']}, "
            + f"vuv_corr={row['oracle_vuv_corr_mean']}"
        )
    lines.append("")
    lines.append("## Records")
    for record in summary.get("records", []):
        lines.append(
            "- "
            + f"{record['record_id']}: "
            + f"frame_count={record['frame_count']}, "
            + f"active_frame_count={record['active_frame_count']}, "
            + f"voicing_source={record['voicing_source']}"
        )
        for stage in record.get("stages", []):
            lines.append(
                "  "
                + f"{stage['stage_name']}: "
                + f"logspec_cosine={stage['oracle_logspec_frame_cosine_mean']}, "
                + f"waveform_frame_cosine={stage['oracle_waveform_frame_cosine_mean']}, "
                + f"waveform_mlp_frame_cosine={stage['oracle_waveform_mlp_frame_cosine_mean']}, "
                + f"rms_corr={stage['oracle_rms_corr']}, "
                + f"vuv_accuracy={stage['oracle_vuv_accuracy']}"
            )
    lines.append("")
    lines.append("## Notes")
    for note in summary.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
