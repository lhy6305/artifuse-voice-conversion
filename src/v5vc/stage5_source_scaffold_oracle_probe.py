from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import resolve_checkpoint_path_from_inputs, resolve_package_entries
from v5vc.offline_vocoder_training import (
    DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
)
from v5vc.stage5_branch_feature_oracle_probe import build_package_input_layout
from v5vc.stage5_representation_oracle_probe import (
    DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    DEFAULT_WAVEFORM_MLP_LR,
    DEFAULT_WAVEFORM_MLP_STEPS,
    build_target_proxy_bundle,
    evaluate_oracle_probe_stage,
)


STAGE_SPECS = [
    ("selected_dynamic_controls", "Current Stage5-selected dynamic controls rebuilt from source_scaffold available_controls."),
    ("selected_joint_contract", "Current Stage5-selected joint contract including conditioning."),
    ("all_available_controls", "Full dynamic control contract from source_scaffold available_controls."),
    ("unselected_available_controls", "Dynamic controls present in source_scaffold but omitted from the current Stage5-selected contract."),
    ("all_controls_plus_conditioning", "Full source_scaffold control contract plus static conditioning."),
    ("event_gate_family", "Explicit e_evt family only."),
    ("event_probs_family", "Legacy event_probs family only."),
    ("event_full_family", "Combined event gate and event probability families."),
    ("f0_family", "Raw and normalized F0 controls."),
    ("voicing_aper_family", "Voicing and aperiodicity controls and proxies."),
    ("energy_family", "Energy, normalized energy, and energy-related auxiliary controls."),
    ("proxy_family", "Proxy-only family: energy, voiced, aperiodicity, event presence, and energy change."),
    ("aux_stat_family", "Auxiliary scalar controls such as abs_mean, zero_cross_rate, and delta_energy."),
    ("conditioning_family", "Static conditioning only."),
]
STATIC_STAGE_NAMES = {"conditioning_family"}
DYNAMIC_STAGE_NAMES = {stage_name for stage_name, _ in STAGE_SPECS if stage_name not in STATIC_STAGE_NAMES}


def analyze_stage5_nores_source_scaffold_oracle_probe(
    *,
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    dataset_index_path: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
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
    resolved_checkpoint_path: Path | None = None
    selection_summary: dict[str, object] | None = None
    resolved_selection_target: str | None = None
    if checkpoint_path is not None or checkpoint_selection_path is not None:
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
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the source-scaffold oracle probe.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    stage_names = resolve_present_stage_names(package_payload=first_payload)
    stage_descriptions = {name: description for name, description in STAGE_SPECS if name in stage_names}

    per_record_rows: list[dict[str, object]] = []
    record_feature_cache: list[dict[str, object]] = []
    for entry in package_entries:
        payload = load_training_package_payload(Path(str(entry["training_package_path"])).resolve())
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)
        candidate_sequences = build_candidate_stage_sequences(package_payload=payload)
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
        "checkpoint_path": None if resolved_checkpoint_path is None else resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": (
            None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix()
        ),
        "selection_target": resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "probe_config": {
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
        "source_scaffold_summary": build_source_scaffold_summary(cross_record_stage_aggregates),
        "records": per_record_rows,
        "notes": [
            "This probe moves earlier than Stage5 branch features and reads the source_scaffold control contract directly.",
            "The main question is whether source_scaffold available_controls contains materially stronger fine waveform geometry than the current Stage5-selected contract.",
            "conditioning_family is frame-constant, so any tiny waveform oracle score there should be read only as record-level leakage, not temporal fine-structure evidence.",
            "Primary interpretation should compare selected_dynamic_controls, all_available_controls, and unselected_available_controls before any conditioning-augmented variants.",
        ],
    }
    (output_dir / "stage5_source_scaffold_oracle_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "stage5_source_scaffold_oracle_probe.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_candidate_stage_sequences(*, package_payload: dict[str, object]) -> dict[str, torch.Tensor]:
    scaffold_path = Path(str(package_payload["source_scaffold_path"])).resolve()
    scaffold_payload = torch.load(scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(scaffold_payload, dict):
        raise TypeError(f"Unsupported source scaffold payload type: {type(scaffold_payload)!r}")
    available_controls = dict(scaffold_payload["available_controls"])
    conditioning = dict(scaffold_payload["conditioning"])
    layout = build_package_input_layout(package_payload)
    frame_count = resolve_frame_count(available_controls)

    stage_sequences: dict[str, torch.Tensor] = {}
    selected_dynamic_slices = collect_layout_slices(
        available_controls=available_controls,
        conditioning=conditioning,
        layout=layout,
        frame_count=frame_count,
        include_conditioning=False,
    )
    selected_joint_slices = collect_layout_slices(
        available_controls=available_controls,
        conditioning=conditioning,
        layout=layout,
        frame_count=frame_count,
        include_conditioning=True,
    )
    if selected_dynamic_slices:
        stage_sequences["selected_dynamic_controls"] = torch.cat(selected_dynamic_slices, dim=-1)
    if selected_joint_slices:
        stage_sequences["selected_joint_contract"] = torch.cat(selected_joint_slices, dim=-1)

    all_control_keys = [key for key, value in available_controls.items() if isinstance(value, torch.Tensor)]
    if all_control_keys:
        stage_sequences["all_available_controls"] = concat_control_keys(available_controls, all_control_keys)

    selected_control_semantics = gather_selected_control_semantics(layout)
    unselected_control_keys = [key for key in all_control_keys if key not in selected_control_semantics]
    if unselected_control_keys:
        stage_sequences["unselected_available_controls"] = concat_control_keys(available_controls, unselected_control_keys)

    all_plus_conditioning = []
    if all_control_keys:
        all_plus_conditioning.append(concat_control_keys(available_controls, all_control_keys))
    conditioning_tensor = build_conditioning_tensor(conditioning, frame_count=frame_count)
    if conditioning_tensor is not None:
        all_plus_conditioning.append(conditioning_tensor)
        stage_sequences["conditioning_family"] = conditioning_tensor
    if all_plus_conditioning:
        stage_sequences["all_controls_plus_conditioning"] = torch.cat(all_plus_conditioning, dim=-1)

    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="event_gate_family",
        available_controls=available_controls,
        control_keys=("e_evt",),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="event_probs_family",
        available_controls=available_controls,
        control_keys=("event_probs",),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="event_full_family",
        available_controls=available_controls,
        control_keys=("e_evt", "event_probs"),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="f0_family",
        available_controls=available_controls,
        control_keys=("f0_hz", "f0_hz_log_norm"),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="voicing_aper_family",
        available_controls=available_controls,
        control_keys=("vuv", "voiced_proxy", "aper", "aperiodicity_proxy"),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="energy_family",
        available_controls=available_controls,
        control_keys=("E", "E_log_rms_norm", "energy_log", "energy_proxy", "delta_energy", "energy_change_proxy"),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="proxy_family",
        available_controls=available_controls,
        control_keys=("energy_proxy", "voiced_proxy", "aperiodicity_proxy", "event_presence_proxy", "energy_change_proxy"),
    )
    add_control_family_if_present(
        stage_sequences=stage_sequences,
        stage_name="aux_stat_family",
        available_controls=available_controls,
        control_keys=("abs_mean", "zero_cross_rate", "delta_energy"),
    )
    return stage_sequences


def collect_layout_slices(
    *,
    available_controls: dict[str, torch.Tensor],
    conditioning: dict[str, torch.Tensor],
    layout: dict[str, dict[str, tuple[int, int]]],
    frame_count: int,
    include_conditioning: bool,
) -> list[torch.Tensor]:
    slices: list[torch.Tensor] = []
    seen_dynamic: set[str] = set()
    seen_conditioning: set[str] = set()
    for branch_name in ("periodic", "noise"):
        for semantic in layout.get(branch_name, {}):
            if semantic in available_controls and semantic not in seen_dynamic:
                slices.append(available_controls[semantic].detach().cpu().to(torch.float32))
                seen_dynamic.add(semantic)
            elif include_conditioning and semantic in conditioning and semantic not in seen_conditioning:
                slices.append(
                    broadcast_conditioning_tensor(conditioning[semantic], frame_count=int(frame_count))
                )
                seen_conditioning.add(semantic)
    return slices


def gather_selected_control_semantics(layout: dict[str, dict[str, tuple[int, int]]]) -> set[str]:
    selected = set()
    for branch_layout in layout.values():
        for semantic in branch_layout:
            selected.add(str(semantic))
    return selected


def resolve_frame_count(available_controls: dict[str, torch.Tensor]) -> int:
    for value in available_controls.values():
        if isinstance(value, torch.Tensor) and value.ndim >= 2:
            return int(value.shape[0])
    raise ValueError("Unable to resolve frame_count from source_scaffold available_controls.")


def broadcast_conditioning_tensor(value: torch.Tensor, *, frame_count: int) -> torch.Tensor:
    tensor = value.detach().cpu().to(torch.float32).view(1, -1)
    return tensor.expand(int(frame_count), -1).clone()


def build_conditioning_tensor(
    conditioning: dict[str, torch.Tensor],
    *,
    frame_count: int,
) -> torch.Tensor | None:
    slices: list[torch.Tensor] = []
    for semantic in ("alpha", "s_spk_target", "s_geom_target"):
        value = conditioning.get(semantic)
        if not isinstance(value, torch.Tensor):
            continue
        slices.append(broadcast_conditioning_tensor(value, frame_count=int(frame_count)))
    if not slices:
        return None
    return torch.cat(slices, dim=-1)


def concat_control_keys(available_controls: dict[str, torch.Tensor], control_keys: list[str] | tuple[str, ...]) -> torch.Tensor:
    tensors = [
        available_controls[key].detach().cpu().to(torch.float32)
        for key in control_keys
        if key in available_controls and isinstance(available_controls[key], torch.Tensor)
    ]
    if not tensors:
        raise ValueError("No tensor-valued controls were found for the requested source_scaffold family.")
    return torch.cat(tensors, dim=-1)


def add_control_family_if_present(
    *,
    stage_sequences: dict[str, torch.Tensor],
    stage_name: str,
    available_controls: dict[str, torch.Tensor],
    control_keys: tuple[str, ...],
) -> None:
    present_keys = [key for key in control_keys if key in available_controls and isinstance(available_controls[key], torch.Tensor)]
    if not present_keys:
        return
    stage_sequences[stage_name] = concat_control_keys(available_controls, present_keys)


def resolve_present_stage_names(*, package_payload: dict[str, object]) -> list[str]:
    candidate_sequences = build_candidate_stage_sequences(package_payload=package_payload)
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


def build_source_scaffold_summary(cross_record_stage_aggregates: list[dict[str, object]]) -> dict[str, object]:
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
    dynamic_rows = [
        item for item in cross_record_stage_aggregates if str(item["stage_name"]) in DYNAMIC_STAGE_NAMES
    ]
    best_dynamic_linear = (
        None
        if not dynamic_rows
        else max(dynamic_rows, key=lambda item: float(item.get("oracle_waveform_frame_cosine_mean", 0.0)))
    )
    best_dynamic_mlp = (
        None
        if not dynamic_rows
        else max(dynamic_rows, key=lambda item: float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)))
    )
    selected_dynamic = by_stage.get("selected_dynamic_controls")
    selected_joint = by_stage.get("selected_joint_contract")
    all_controls = by_stage.get("all_available_controls")
    unselected_controls = by_stage.get("unselected_available_controls")
    all_plus_conditioning = by_stage.get("all_controls_plus_conditioning")
    summary: dict[str, object] = {
        "best_cross_record_waveform_stage": str(best_linear["stage_name"]),
        "best_cross_record_waveform_value": float(best_linear["oracle_waveform_frame_cosine_mean"]),
        "best_cross_record_waveform_mlp_stage": str(best_mlp["stage_name"]),
        "best_cross_record_waveform_mlp_value": float(best_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
        "best_dynamic_waveform_stage": None if best_dynamic_linear is None else str(best_dynamic_linear["stage_name"]),
        "best_dynamic_waveform_value": (
            None if best_dynamic_linear is None else float(best_dynamic_linear["oracle_waveform_frame_cosine_mean"])
        ),
        "best_dynamic_waveform_mlp_stage": (
            None if best_dynamic_mlp is None else str(best_dynamic_mlp["stage_name"])
        ),
        "best_dynamic_waveform_mlp_value": (
            None if best_dynamic_mlp is None else float(best_dynamic_mlp["oracle_waveform_mlp_frame_cosine_mean"])
        ),
    }
    add_stage_signal_snapshot(summary, selected_dynamic, "selected_dynamic")
    add_stage_signal_snapshot(summary, all_controls, "all_available_controls")
    add_stage_signal_snapshot(summary, unselected_controls, "unselected_available_controls")
    add_waveform_gain(summary, selected_dynamic, all_controls, "selected_dynamic_to_all_controls")
    add_waveform_gain(summary, selected_joint, all_plus_conditioning, "selected_joint_to_all_controls_plus_conditioning")
    add_waveform_gain(summary, selected_dynamic, unselected_controls, "selected_dynamic_to_unselected_controls")

    selected_dynamic_signal = max_stage_signal(selected_dynamic)
    all_controls_signal = max_stage_signal(all_controls)
    unselected_signal = max_stage_signal(unselected_controls)
    best_dynamic_contract_signal = max(selected_dynamic_signal, all_controls_signal, unselected_signal)
    if best_dynamic_contract_signal < 0.05:
        summary["diagnosis"] = "fine_waveform_geometry_is_already_weak_in_source_scaffold_control_contract"
    elif all_controls_signal >= selected_dynamic_signal + 0.02 and unselected_signal >= selected_dynamic_signal + 0.01:
        summary["diagnosis"] = "source_scaffold_contains_additional_fine_geometry_outside_current_stage5_selection"
    elif all_controls_signal >= selected_dynamic_signal + 0.02:
        summary["diagnosis"] = "full_source_scaffold_control_contract_is_stronger_than_current_stage5_selection"
    else:
        summary["diagnosis"] = "current_stage5_selection_is_not_the_main_reason_for_missing_fine_geometry"
    return summary


def add_stage_signal_snapshot(
    summary: dict[str, object],
    stage_row: dict[str, object] | None,
    prefix: str,
) -> None:
    if stage_row is None:
        return
    summary[f"{prefix}_waveform_value"] = float(stage_row["oracle_waveform_frame_cosine_mean"])
    summary[f"{prefix}_waveform_mlp_value"] = float(stage_row["oracle_waveform_mlp_frame_cosine_mean"])
    summary[f"{prefix}_logspec_value"] = float(stage_row["oracle_logspec_frame_cosine_mean"])
    summary[f"{prefix}_rms_corr"] = float(stage_row["oracle_rms_corr_mean"])
    summary[f"{prefix}_vuv_accuracy"] = float(stage_row["oracle_vuv_accuracy_mean"])


def add_waveform_gain(
    summary: dict[str, object],
    src_row: dict[str, object] | None,
    dst_row: dict[str, object] | None,
    prefix: str,
) -> None:
    if src_row is None or dst_row is None:
        return
    summary[f"{prefix}_waveform_gain"] = round(
        float(dst_row["oracle_waveform_frame_cosine_mean"]) - float(src_row["oracle_waveform_frame_cosine_mean"]),
        6,
    )
    summary[f"{prefix}_waveform_mlp_gain"] = round(
        float(dst_row["oracle_waveform_mlp_frame_cosine_mean"])
        - float(src_row["oracle_waveform_mlp_frame_cosine_mean"]),
        6,
    )


def max_stage_signal(stage_row: dict[str, object] | None) -> float:
    if stage_row is None:
        return 0.0
    return max(
        float(stage_row.get("oracle_waveform_frame_cosine_mean", 0.0)),
        float(stage_row.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)),
    )


def mean_rows(rows: list[dict[str, object]], key: str) -> float:
    return round(sum(float(row.get(key, 0.0)) for row in rows) / float(len(rows)), 6)


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Source-Scaffold Oracle Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- source_scaffold_summary: {json.dumps(summary['source_scaffold_summary'], ensure_ascii=False)}",
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
