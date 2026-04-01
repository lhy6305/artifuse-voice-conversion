from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_training import (
    DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
)
from v5vc.stage5_representation_oracle_probe import (
    DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    DEFAULT_WAVEFORM_MLP_LR,
    DEFAULT_WAVEFORM_MLP_STEPS,
    build_target_proxy_bundle,
    evaluate_oracle_probe_stage,
)


STAGE_SPECS = [
    ("periodic_branch_features", "Full periodic input."),
    ("noise_branch_features", "Full noise input."),
    ("joint_branch_features", "Concatenated branch input."),
    ("z_art_family", "Periodic z_art slice."),
    ("f0_hz_log_norm_family", "Periodic F0 slice."),
    ("event_family", "Noise event slice."),
    ("acoustic_state_family", "Cross-branch acoustic-state slice."),
    ("conditioning_family", "Cross-branch conditioning slice."),
    ("periodic_hidden", "Periodic encoder output."),
    ("noise_hidden", "Noise encoder output."),
]
RAW_STAGE_NAMES = {
    "periodic_branch_features",
    "noise_branch_features",
    "joint_branch_features",
    "z_art_family",
    "f0_hz_log_norm_family",
    "event_family",
    "acoustic_state_family",
    "conditioning_family",
}
STATIC_RAW_STAGE_NAMES = {"conditioning_family"}
DYNAMIC_RAW_STAGE_NAMES = RAW_STAGE_NAMES - STATIC_RAW_STAGE_NAMES
ENC_STAGE_NAMES = {"periodic_hidden", "noise_hidden"}


def analyze_stage5_nores_branch_feature_oracle_probe(
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
    active_frame_rms_threshold: float = DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    logspec_bins: int = 201,
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
        raise ValueError("No Stage5 training packages were selected for the branch-feature oracle probe.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    ).to(torch.device(device))
    model.eval()

    stage_names = resolve_present_stage_names(model=model, package_entries=package_entries, device=torch.device(device))
    stage_descriptions = {name: description for name, description in STAGE_SPECS if name in stage_names}
    per_record_rows: list[dict[str, object]] = []
    record_feature_cache: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            payload = load_training_package_payload(Path(str(entry["training_package_path"])).resolve())
            batch = extract_training_batch(payload)
            runtime = extract_training_runtime(payload)
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"].to(device=device, dtype=torch.float32),
                noise_branch_features=batch["noise_branch_features"].to(device=device, dtype=torch.float32),
            )
            candidate_sequences = build_candidate_stage_sequences(
                package_payload=payload,
                batch=batch,
                outputs=outputs,
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
            stage_rows = []
            stage_feature_cache: dict[str, dict[str, torch.Tensor]] = {}
            for stage_name in stage_names:
                stage_sequence = candidate_sequences.get(stage_name)
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
                {"record_id": str(entry["record_id"]), "stage_feature_cache": stage_feature_cache}
            )

    stage_aggregates = build_stage_aggregates(per_record_rows, stage_names=stage_names)
    cross_record_stage_aggregates = build_cross_record_stage_aggregates(
        record_feature_cache=record_feature_cache,
        stage_names=stage_names,
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
            "device": str(device),
            "active_frame_rms_threshold": float(active_frame_rms_threshold),
            "logspec_bins": int(logspec_bins),
            "ridge_lambda": float(ridge_lambda),
            "test_stride": int(test_stride),
            "waveform_mlp_hidden_dim": int(waveform_mlp_hidden_dim),
            "waveform_mlp_steps": int(waveform_mlp_steps),
            "waveform_mlp_lr": float(waveform_mlp_lr),
            "stage_names": stage_names,
        },
        "stage_descriptions": stage_descriptions,
        "stage_aggregates": stage_aggregates,
        "cross_record_stage_aggregates": cross_record_stage_aggregates,
        "branch_feature_summary": build_branch_feature_summary(cross_record_stage_aggregates),
        "records": per_record_rows,
        "notes": [
            "This probe extends the upstream localization step to the raw Stage5 branch-input contract.",
            "The main question is whether fine waveform geometry is already weak in branch inputs before the input encoders run.",
            "conditioning_family is a frame-constant conditioning slice, so any tiny cross-record waveform oracle score there should not be overread as temporal fine-structure evidence.",
        ],
    }
    (output_dir / "stage5_branch_feature_oracle_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "stage5_branch_feature_oracle_probe.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_candidate_stage_sequences(
    *,
    package_payload: dict[str, object],
    batch: dict[str, torch.Tensor],
    outputs: dict[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    periodic = batch["periodic_branch_features"].detach().cpu().to(torch.float32)
    noise = batch["noise_branch_features"].detach().cpu().to(torch.float32)
    stage_sequences = {
        "periodic_branch_features": periodic,
        "noise_branch_features": noise,
        "joint_branch_features": torch.cat([periodic, noise], dim=-1),
    }
    layout = build_package_input_layout(package_payload)
    add_family_stage_if_present(
        stage_sequences=stage_sequences,
        stage_name="z_art_family",
        batch=batch,
        layout=layout,
        targets=(("periodic", "z_art"),),
    )
    add_family_stage_if_present(
        stage_sequences=stage_sequences,
        stage_name="f0_hz_log_norm_family",
        batch=batch,
        layout=layout,
        targets=(("periodic", "f0_hz_log_norm"),),
    )
    add_family_stage_if_present(
        stage_sequences=stage_sequences,
        stage_name="event_family",
        batch=batch,
        layout=layout,
        targets=(("noise", "e_evt"), ("noise", "event_probs")),
    )
    add_family_stage_if_present(
        stage_sequences=stage_sequences,
        stage_name="acoustic_state_family",
        batch=batch,
        layout=layout,
        targets=(
            ("periodic", "f0_hz_log_norm"),
            ("periodic", "vuv"),
            ("periodic", "E_log_rms_norm"),
            ("noise", "aper"),
            ("noise", "vuv"),
            ("noise", "E_log_rms_norm"),
        ),
    )
    add_family_stage_if_present(
        stage_sequences=stage_sequences,
        stage_name="conditioning_family",
        batch=batch,
        layout=layout,
        targets=(
            ("periodic", "alpha"),
            ("periodic", "s_spk_target"),
            ("periodic", "s_geom_target"),
            ("noise", "alpha"),
            ("noise", "s_spk_target"),
            ("noise", "s_geom_target"),
        ),
    )
    for stage_name in ENC_STAGE_NAMES:
        if stage_name in outputs:
            stage_sequences[stage_name] = outputs[stage_name].detach().cpu().to(torch.float32)
    return stage_sequences


def add_family_stage_if_present(
    *,
    stage_sequences: dict[str, torch.Tensor],
    stage_name: str,
    batch: dict[str, torch.Tensor],
    layout: dict[str, dict[str, tuple[int, int]]],
    targets: tuple[tuple[str, str], ...],
) -> None:
    slices: list[torch.Tensor] = []
    for branch_name, semantic in targets:
        slice_info = layout.get(branch_name, {}).get(semantic)
        if slice_info is None:
            continue
        start, end = slice_info
        if end <= start:
            continue
        branch_tensor = batch["periodic_branch_features"] if branch_name == "periodic" else batch["noise_branch_features"]
        slices.append(branch_tensor[:, start:end].detach().cpu().to(torch.float32))
    if slices:
        stage_sequences[stage_name] = torch.cat(slices, dim=-1)


def build_package_input_layout(package_payload: dict[str, object]) -> dict[str, dict[str, tuple[int, int]]]:
    scaffold_path = Path(str(package_payload["source_scaffold_path"])).resolve()
    scaffold_payload = torch.load(scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(scaffold_payload, dict):
        raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")
    available_controls = dict(scaffold_payload["available_controls"])
    conditioning = dict(scaffold_payload["conditioning"])
    input_semantics = dict(package_payload.get("input_semantics", {}))
    semantic_consumer = dict(package_payload.get("semantic_consumer", {}))
    return {
        "periodic": build_semantic_layout(
            feature_semantics=list(input_semantics.get("periodic_feature_semantics", [])),
            available_controls=available_controls,
            conditioning=conditioning,
            semantic_consumer=semantic_consumer,
        ),
        "noise": build_semantic_layout(
            feature_semantics=list(input_semantics.get("noise_feature_semantics", [])),
            available_controls=available_controls,
            conditioning=conditioning,
            semantic_consumer=semantic_consumer,
        ),
    }


def build_semantic_layout(
    *,
    feature_semantics: list[object],
    available_controls: dict[str, object],
    conditioning: dict[str, object],
    semantic_consumer: dict[str, object],
) -> dict[str, tuple[int, int]]:
    layout: dict[str, tuple[int, int]] = {}
    start = 0
    for raw_semantic in feature_semantics:
        semantic = str(raw_semantic)
        dim = resolve_semantic_dim(
            semantic=semantic,
            available_controls=available_controls,
            conditioning=conditioning,
            semantic_consumer=semantic_consumer,
        )
        layout[semantic] = (start, start + dim)
        start += dim
    return layout


def resolve_semantic_dim(
    *,
    semantic: str,
    available_controls: dict[str, object],
    conditioning: dict[str, object],
    semantic_consumer: dict[str, object],
) -> int:
    if semantic == "alpha":
        value = conditioning.get("alpha")
        return int(value.numel()) if isinstance(value, torch.Tensor) else 1
    if semantic in {"s_spk_target", "s_geom_target"}:
        value = conditioning.get(semantic)
        if not isinstance(value, torch.Tensor):
            raise KeyError(f"Conditioning semantic is missing for branch-feature layout: {semantic}")
        return int(value.shape[-1])
    if semantic in available_controls:
        value = available_controls[semantic]
        if not isinstance(value, torch.Tensor):
            raise KeyError(f"Control semantic is not tensor-valued for branch-feature layout: {semantic}")
        return int(value.shape[-1])
    if semantic == str(semantic_consumer.get("semantic_tag")):
        return int(semantic_consumer.get("feature_dim", 0))
    raise KeyError(f"Unsupported branch semantic for branch-feature layout: {semantic}")


def resolve_present_stage_names(
    *,
    model: torch.nn.Module,
    package_entries: list[dict[str, object]],
    device: torch.device,
) -> list[str]:
    payload = load_training_package_payload(Path(str(package_entries[0]["training_package_path"])).resolve())
    batch = extract_training_batch(payload)
    with torch.no_grad():
        outputs = model(
            periodic_branch_features=batch["periodic_branch_features"].to(device=device, dtype=torch.float32),
            noise_branch_features=batch["noise_branch_features"].to(device=device, dtype=torch.float32),
        )
    candidate_sequences = build_candidate_stage_sequences(package_payload=payload, batch=batch, outputs=outputs)
    return [stage_name for stage_name, _ in STAGE_SPECS if stage_name in candidate_sequences]


def build_stage_aggregates(records: list[dict[str, object]], *, stage_names: list[str]) -> list[dict[str, object]]:
    rows_by_stage: dict[str, list[dict[str, object]]] = {}
    for record in records:
        for stage in record.get("stages", []):
            rows_by_stage.setdefault(str(stage["stage_name"]), []).append(stage)
    aggregates = []
    for stage_name in stage_names:
        rows = rows_by_stage.get(stage_name, [])
        if not rows:
            continue
        aggregates.append(
            {
                "stage_name": stage_name,
                "record_count": len(rows),
                "oracle_logspec_frame_cosine_mean": mean_rows(rows, "oracle_logspec_frame_cosine_mean"),
                "oracle_waveform_frame_cosine_mean": mean_rows(rows, "oracle_waveform_frame_cosine_mean"),
                "oracle_waveform_mlp_frame_cosine_mean": mean_rows(rows, "oracle_waveform_mlp_frame_cosine_mean"),
                "oracle_rms_corr_mean": mean_rows(rows, "oracle_rms_corr"),
                "oracle_vuv_accuracy_mean": mean_rows(rows, "oracle_vuv_accuracy"),
            }
        )
    return aggregates


def build_cross_record_stage_aggregates(
    *,
    record_feature_cache: list[dict[str, object]],
    stage_names: list[str],
    ridge_lambda: float,
    waveform_mlp_hidden_dim: int,
    waveform_mlp_steps: int,
    waveform_mlp_lr: float,
) -> list[dict[str, object]]:
    from v5vc.stage5_representation_oracle_probe import (
        compute_mean_frame_cosine,
        compute_pearson_correlation,
        fit_ridge_readout,
        predict_mlp_readout,
        predict_ridge_readout,
    )

    stage_rows = []
    if len(record_feature_cache) <= 1:
        return stage_rows
    for stage_name in stage_names:
        heldout_rows = []
        for heldout_index, heldout_record in enumerate(record_feature_cache):
            heldout = heldout_record["stage_feature_cache"].get(stage_name)
            if heldout is None:
                continue
            train_feature_chunks = []
            train_rms_chunks = []
            train_voicing_chunks = []
            train_logspec_chunks = []
            train_waveform_chunks = []
            for train_index, train_record in enumerate(record_feature_cache):
                if train_index == heldout_index:
                    continue
                train_stage = train_record["stage_feature_cache"].get(stage_name)
                if train_stage is None:
                    continue
                train_feature_chunks.append(train_stage["features"])
                train_rms_chunks.append(train_stage["target_rms"])
                train_voicing_chunks.append(train_stage["target_voicing"])
                train_logspec_chunks.append(train_stage["target_logspec"])
                train_waveform_chunks.append(train_stage["target_waveform_frames"])
            if not train_feature_chunks:
                continue
            train_x = torch.cat(train_feature_chunks, dim=0)
            train_rms = torch.cat(train_rms_chunks, dim=0)
            train_voicing = torch.cat(train_voicing_chunks, dim=0)
            train_logspec = torch.cat(train_logspec_chunks, dim=0)
            train_waveform = torch.cat(train_waveform_chunks, dim=0)
            test_x = heldout["features"]
            test_rms = heldout["target_rms"]
            test_voicing = heldout["target_voicing"]
            test_logspec = heldout["target_logspec"]
            test_waveform = heldout["target_waveform_frames"]
            rms_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_rms, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            voicing_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_voicing, ridge_lambda=float(ridge_lambda)),
                test_x,
            ).clamp(0.0, 1.0)
            logspec_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_logspec, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            waveform_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_waveform, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            waveform_mlp_pred = predict_mlp_readout(
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
                    "oracle_vuv_accuracy": float(voicing_accuracy.item()),
                    "oracle_logspec_frame_cosine_mean": compute_mean_frame_cosine(logspec_pred, test_logspec),
                    "oracle_waveform_frame_cosine_mean": compute_mean_frame_cosine(waveform_pred, test_waveform),
                    "oracle_waveform_mlp_frame_cosine_mean": compute_mean_frame_cosine(
                        waveform_mlp_pred, test_waveform
                    ),
                }
            )
        if heldout_rows:
            stage_rows.append(
                {
                    "stage_name": stage_name,
                    "record_count": len(heldout_rows),
                    "oracle_logspec_frame_cosine_mean": mean_rows(heldout_rows, "oracle_logspec_frame_cosine_mean"),
                    "oracle_waveform_frame_cosine_mean": mean_rows(heldout_rows, "oracle_waveform_frame_cosine_mean"),
                    "oracle_waveform_mlp_frame_cosine_mean": mean_rows(
                        heldout_rows, "oracle_waveform_mlp_frame_cosine_mean"
                    ),
                    "oracle_rms_corr_mean": mean_rows(heldout_rows, "oracle_rms_corr"),
                    "oracle_vuv_accuracy_mean": mean_rows(heldout_rows, "oracle_vuv_accuracy"),
                    "heldout_records": heldout_rows,
                }
            )
    return stage_rows


def build_branch_feature_summary(cross_record_stage_aggregates: list[dict[str, object]]) -> dict[str, object]:
    by_stage = {str(item["stage_name"]): item for item in cross_record_stage_aggregates}
    if not by_stage:
        return {"diagnosis": "missing_cross_record_stage_aggregates"}
    best_linear = max(
        cross_record_stage_aggregates,
        key=lambda item: float(item.get("oracle_waveform_frame_cosine_mean", 0.0)),
    )
    best_mlp = max(
        cross_record_stage_aggregates,
        key=lambda item: float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)),
    )
    raw_rows = [item for item in cross_record_stage_aggregates if str(item["stage_name"]) in RAW_STAGE_NAMES]
    enc_rows = [item for item in cross_record_stage_aggregates if str(item["stage_name"]) in ENC_STAGE_NAMES]
    best_raw_linear = None if not raw_rows else max(raw_rows, key=lambda item: float(item["oracle_waveform_frame_cosine_mean"]))
    best_raw_mlp = None if not raw_rows else max(raw_rows, key=lambda item: float(item["oracle_waveform_mlp_frame_cosine_mean"]))
    dynamic_raw_rows = [
        item for item in cross_record_stage_aggregates if str(item["stage_name"]) in DYNAMIC_RAW_STAGE_NAMES
    ]
    best_dynamic_raw_linear = (
        None
        if not dynamic_raw_rows
        else max(dynamic_raw_rows, key=lambda item: float(item["oracle_waveform_frame_cosine_mean"]))
    )
    best_dynamic_raw_mlp = (
        None
        if not dynamic_raw_rows
        else max(dynamic_raw_rows, key=lambda item: float(item["oracle_waveform_mlp_frame_cosine_mean"]))
    )
    best_enc_linear = None if not enc_rows else max(enc_rows, key=lambda item: float(item["oracle_waveform_frame_cosine_mean"]))
    best_enc_mlp = None if not enc_rows else max(enc_rows, key=lambda item: float(item["oracle_waveform_mlp_frame_cosine_mean"]))
    summary: dict[str, object] = {
        "best_cross_record_waveform_stage": str(best_linear["stage_name"]),
        "best_cross_record_waveform_value": float(best_linear["oracle_waveform_frame_cosine_mean"]),
        "best_cross_record_waveform_mlp_stage": str(best_mlp["stage_name"]),
        "best_cross_record_waveform_mlp_value": float(best_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
        "best_raw_input_waveform_stage": None if best_raw_linear is None else str(best_raw_linear["stage_name"]),
        "best_raw_input_waveform_value": None if best_raw_linear is None else float(best_raw_linear["oracle_waveform_frame_cosine_mean"]),
        "best_raw_input_waveform_mlp_stage": None if best_raw_mlp is None else str(best_raw_mlp["stage_name"]),
        "best_raw_input_waveform_mlp_value": None if best_raw_mlp is None else float(best_raw_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
        "best_dynamic_raw_input_waveform_stage": (
            None if best_dynamic_raw_linear is None else str(best_dynamic_raw_linear["stage_name"])
        ),
        "best_dynamic_raw_input_waveform_value": (
            None
            if best_dynamic_raw_linear is None
            else float(best_dynamic_raw_linear["oracle_waveform_frame_cosine_mean"])
        ),
        "best_dynamic_raw_input_waveform_mlp_stage": (
            None if best_dynamic_raw_mlp is None else str(best_dynamic_raw_mlp["stage_name"])
        ),
        "best_dynamic_raw_input_waveform_mlp_value": (
            None
            if best_dynamic_raw_mlp is None
            else float(best_dynamic_raw_mlp["oracle_waveform_mlp_frame_cosine_mean"])
        ),
        "best_encoded_waveform_stage": None if best_enc_linear is None else str(best_enc_linear["stage_name"]),
        "best_encoded_waveform_value": None if best_enc_linear is None else float(best_enc_linear["oracle_waveform_frame_cosine_mean"]),
        "best_encoded_waveform_mlp_stage": None if best_enc_mlp is None else str(best_enc_mlp["stage_name"]),
        "best_encoded_waveform_mlp_value": None if best_enc_mlp is None else float(best_enc_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
    }
    if best_raw_linear is not None and str(best_raw_linear["stage_name"]) in STATIC_RAW_STAGE_NAMES:
        summary["best_raw_input_waveform_stage_is_static"] = True
    if best_raw_mlp is not None and str(best_raw_mlp["stage_name"]) in STATIC_RAW_STAGE_NAMES:
        summary["best_raw_input_waveform_mlp_stage_is_static"] = True
    add_transition_drop(summary, by_stage, "periodic_branch_features", "periodic_hidden", "periodic_input_to_hidden")
    add_transition_drop(summary, by_stage, "noise_branch_features", "noise_hidden", "noise_input_to_hidden")
    best_raw_signal = max(
        float(summary.get("best_dynamic_raw_input_waveform_value") or 0.0),
        float(summary.get("best_dynamic_raw_input_waveform_mlp_value") or 0.0),
    )
    best_enc_signal = max(float(summary.get("best_encoded_waveform_value") or 0.0), float(summary.get("best_encoded_waveform_mlp_value") or 0.0))
    max_drop = max(
        float(summary.get("periodic_input_to_hidden_waveform_drop") or 0.0),
        float(summary.get("periodic_input_to_hidden_waveform_mlp_drop") or 0.0),
        float(summary.get("noise_input_to_hidden_waveform_drop") or 0.0),
        float(summary.get("noise_input_to_hidden_waveform_mlp_drop") or 0.0),
    )
    if best_raw_signal < 0.05:
        summary["diagnosis"] = "fine_waveform_geometry_is_already_weak_in_stage5_branch_inputs"
    elif max_drop >= 0.02 and best_enc_signal + 0.01 < best_raw_signal:
        summary["diagnosis"] = "periodic_or_noise_encoder_discards_available_fine_waveform_geometry"
    else:
        summary["diagnosis"] = "raw_branch_inputs_and_early_encoders_preserve_similarly_limited_fine_waveform_geometry"
    return summary


def add_transition_drop(summary: dict[str, object], by_stage: dict[str, dict[str, object]], src: str, dst: str, prefix: str) -> None:
    src_row = by_stage.get(src)
    dst_row = by_stage.get(dst)
    if src_row is None or dst_row is None:
        return
    summary[f"{prefix}_waveform_drop"] = round(
        float(src_row["oracle_waveform_frame_cosine_mean"]) - float(dst_row["oracle_waveform_frame_cosine_mean"]),
        6,
    )
    summary[f"{prefix}_waveform_mlp_drop"] = round(
        float(src_row["oracle_waveform_mlp_frame_cosine_mean"]) - float(dst_row["oracle_waveform_mlp_frame_cosine_mean"]),
        6,
    )


def mean_rows(rows: list[dict[str, object]], key: str) -> float:
    return round(sum(float(row.get(key, 0.0)) for row in rows) / float(len(rows)), 6)


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Branch-Feature Oracle Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- branch_feature_summary: {json.dumps(summary['branch_feature_summary'], ensure_ascii=False)}",
        "",
        "## Cross-Record Stage Aggregates",
    ]
    for row in summary.get("cross_record_stage_aggregates", []):
        lines.append(
            "- "
            + f"{row['stage_name']}: "
            + f"logspec_cosine={row['oracle_logspec_frame_cosine_mean']}, "
            + f"waveform_frame_cosine={row['oracle_waveform_frame_cosine_mean']}, "
            + f"waveform_mlp_frame_cosine={row['oracle_waveform_mlp_frame_cosine_mean']}, "
            + f"rms_corr={row['oracle_rms_corr_mean']}, "
            + f"vuv_accuracy={row['oracle_vuv_accuracy_mean']}"
        )
    lines.append("")
    lines.append("## Notes")
    for note in summary.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
