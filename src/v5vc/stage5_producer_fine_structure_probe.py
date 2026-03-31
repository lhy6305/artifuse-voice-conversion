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


PRODUCER_FINE_STAGE_SPECS = [
    ("periodic_hidden", "Periodic encoder output."),
    ("noise_hidden", "Noise encoder output."),
    ("branch_mean_hidden", "Equal-weight branch mean before contrast residual injection."),
    ("branch_difference_hidden", "Raw branch difference that feeds the branch-contrast residual path."),
    ("fusion_residual_hidden", "Actual gated residual injected by the branch-contrast fusion path."),
    ("fused_hidden", "Fusion output before decoder-side conditioning."),
    ("decoder_hidden", "Decoder hidden after branch-mean mixing and branch-condition injection."),
    ("waveform_decoder_input_hidden", "Waveform-decoder input after the pre-head adapter path."),
    ("waveform_decoder_base_logits", "Current production base-logits head output."),
]


def analyze_stage5_nores_producer_fine_structure_probe(
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
        raise ValueError("No Stage5 training packages were selected for the producer fine-structure probe.")

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

    stage_names = resolve_present_stage_names(model=model, package_entries=package_entries, device=resolved_device)
    stage_descriptions = {name: description for name, description in PRODUCER_FINE_STAGE_SPECS if name in stage_names}

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
            candidate_sequences = build_candidate_stage_sequences(outputs)
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
                {
                    "record_id": str(entry["record_id"]),
                    "stage_feature_cache": stage_feature_cache,
                }
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
            "device": str(resolved_device),
            "decoder_branch_mean_mix_alpha": float(decoder_branch_mean_mix_alpha),
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
        "producer_fine_structure_summary": build_producer_summary(cross_record_stage_aggregates),
        "records": per_record_rows,
        "notes": [
            "This probe narrows the oracle question to the Stage5 producer/fusion chain rather than the full downstream path.",
            "The main question is whether record-generalizable fine waveform geometry is strongest before fusion, inside the branch-contrast residual path, or only after decoder-side conditioning.",
            "As in the representation oracle probe, all readouts freeze the checkpoint and fit only cheap oracle decoders on top of intermediate sequences.",
        ],
    }
    json_path = output_dir / "stage5_producer_fine_structure_probe.json"
    md_path = output_dir / "stage5_producer_fine_structure_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(build_markdown(summary), encoding="utf-8", newline="\n")


def build_candidate_stage_sequences(outputs: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    candidate_sequences: dict[str, torch.Tensor] = {}
    periodic_hidden = outputs.get("periodic_hidden")
    noise_hidden = outputs.get("noise_hidden")
    branch_mean_hidden = outputs.get("branch_mean_hidden")
    if periodic_hidden is not None:
        candidate_sequences["periodic_hidden"] = periodic_hidden
    if noise_hidden is not None:
        candidate_sequences["noise_hidden"] = noise_hidden
    if branch_mean_hidden is not None:
        candidate_sequences["branch_mean_hidden"] = branch_mean_hidden
    if periodic_hidden is not None and noise_hidden is not None:
        candidate_sequences["branch_difference_hidden"] = periodic_hidden - noise_hidden
    for stage_name in (
        "fusion_residual_hidden",
        "fused_hidden",
        "decoder_hidden",
        "waveform_decoder_input_hidden",
        "waveform_decoder_base_logits",
    ):
        stage_sequence = outputs.get(stage_name)
        if stage_sequence is not None:
            candidate_sequences[stage_name] = stage_sequence
    return candidate_sequences


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
            decoder_branch_mean_mix_alpha=0.0,
        )
    candidate_sequences = build_candidate_stage_sequences(outputs)
    return [stage_name for stage_name, _ in PRODUCER_FINE_STAGE_SPECS if stage_name in candidate_sequences]


def build_stage_aggregates(
    records: list[dict[str, object]],
    *,
    stage_names: list[str],
) -> list[dict[str, object]]:
    stage_rows: dict[str, list[dict[str, object]]] = {}
    for record in records:
        for stage in record.get("stages", []):
            stage_rows.setdefault(str(stage["stage_name"]), []).append(stage)
    aggregates: list[dict[str, object]] = []
    for stage_name in stage_names:
        rows = stage_rows.get(stage_name, [])
        if not rows:
            continue
        def mean_of(key: str) -> float:
            return round(sum(float(row.get(key, 0.0)) for row in rows) / float(len(rows)), 6)
        aggregates.append(
            {
                "stage_name": stage_name,
                "record_count": len(rows),
                "oracle_logspec_frame_cosine_mean": mean_of("oracle_logspec_frame_cosine_mean"),
                "oracle_waveform_frame_cosine_mean": mean_of("oracle_waveform_frame_cosine_mean"),
                "oracle_waveform_mlp_frame_cosine_mean": mean_of("oracle_waveform_mlp_frame_cosine_mean"),
                "oracle_rms_corr_mean": mean_of("oracle_rms_corr"),
                "oracle_vuv_accuracy_mean": mean_of("oracle_vuv_accuracy"),
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

    stage_rows: list[dict[str, object]] = []
    if len(record_feature_cache) <= 1:
        return stage_rows
    for stage_name in stage_names:
        heldout_rows: list[dict[str, object]] = []
        for heldout_index, heldout_record in enumerate(record_feature_cache):
            heldout_stage_cache = heldout_record["stage_feature_cache"].get(stage_name)
            if heldout_stage_cache is None:
                continue
            train_feature_chunks: list[torch.Tensor] = []
            train_rms_chunks: list[torch.Tensor] = []
            train_voicing_chunks: list[torch.Tensor] = []
            train_logspec_chunks: list[torch.Tensor] = []
            train_waveform_chunks: list[torch.Tensor] = []
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
                train_waveform_chunks.append(train_stage_cache["target_waveform_frames"])
            if not train_feature_chunks:
                continue
            train_x = torch.cat(train_feature_chunks, dim=0)
            train_rms = torch.cat(train_rms_chunks, dim=0)
            train_voicing = torch.cat(train_voicing_chunks, dim=0)
            train_logspec = torch.cat(train_logspec_chunks, dim=0)
            train_waveform = torch.cat(train_waveform_chunks, dim=0)
            test_x = heldout_stage_cache["features"]
            test_rms = heldout_stage_cache["target_rms"]
            test_voicing = heldout_stage_cache["target_voicing"]
            test_logspec = heldout_stage_cache["target_logspec"]
            test_waveform = heldout_stage_cache["target_waveform_frames"]
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
                        waveform_mlp_pred,
                        test_waveform,
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
                "oracle_logspec_frame_cosine_mean": mean_of("oracle_logspec_frame_cosine_mean"),
                "oracle_waveform_frame_cosine_mean": mean_of("oracle_waveform_frame_cosine_mean"),
                "oracle_waveform_mlp_frame_cosine_mean": mean_of("oracle_waveform_mlp_frame_cosine_mean"),
                "oracle_rms_corr_mean": mean_of("oracle_rms_corr"),
                "oracle_vuv_accuracy_mean": mean_of("oracle_vuv_accuracy"),
                "heldout_records": heldout_rows,
            }
        )
    return stage_rows


def build_producer_summary(cross_record_stage_aggregates: list[dict[str, object]]) -> dict[str, object]:
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
    branch_difference = by_stage.get("branch_difference_hidden")
    fusion_residual = by_stage.get("fusion_residual_hidden")
    branch_mean = by_stage.get("branch_mean_hidden")
    fused_hidden = by_stage.get("fused_hidden")
    decoder_hidden = by_stage.get("decoder_hidden")
    waveform_input_hidden = by_stage.get("waveform_decoder_input_hidden")
    base_logits = by_stage.get("waveform_decoder_base_logits")
    summary: dict[str, object] = {
        "best_cross_record_waveform_stage": str(best_linear["stage_name"]),
        "best_cross_record_waveform_value": float(best_linear["oracle_waveform_frame_cosine_mean"]),
        "best_cross_record_waveform_mlp_stage": str(best_mlp["stage_name"]),
        "best_cross_record_waveform_mlp_value": float(best_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
    }
    if branch_difference is not None and fusion_residual is not None:
        summary["branch_difference_to_fusion_residual_waveform_mlp_drop"] = round(
            float(branch_difference["oracle_waveform_mlp_frame_cosine_mean"])
            - float(fusion_residual["oracle_waveform_mlp_frame_cosine_mean"]),
            6,
        )
    if branch_mean is not None and fused_hidden is not None:
        summary["branch_mean_to_fused_hidden_waveform_mlp_drop"] = round(
            float(branch_mean["oracle_waveform_mlp_frame_cosine_mean"])
            - float(fused_hidden["oracle_waveform_mlp_frame_cosine_mean"]),
            6,
        )
    if decoder_hidden is not None and waveform_input_hidden is not None:
        summary["decoder_hidden_to_waveform_input_hidden_waveform_mlp_drop"] = round(
            float(decoder_hidden["oracle_waveform_mlp_frame_cosine_mean"])
            - float(waveform_input_hidden["oracle_waveform_mlp_frame_cosine_mean"]),
            6,
        )
    if waveform_input_hidden is not None and base_logits is not None:
        summary["waveform_input_hidden_to_base_logits_waveform_mlp_drop"] = round(
            float(waveform_input_hidden["oracle_waveform_mlp_frame_cosine_mean"])
            - float(base_logits["oracle_waveform_mlp_frame_cosine_mean"]),
            6,
        )
    summary["diagnosis"] = "needs_manual_reading"
    return summary


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Producer Fine-Structure Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- producer_fine_structure_summary: {json.dumps(summary['producer_fine_structure_summary'], ensure_ascii=False)}",
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
                + f"waveform_frame_cosine={stage['oracle_waveform_frame_cosine_mean']}, "
                + f"waveform_mlp_frame_cosine={stage['oracle_waveform_mlp_frame_cosine_mean']}, "
                + f"logspec_cosine={stage['oracle_logspec_frame_cosine_mean']}"
            )
    lines.append("")
    lines.append("## Notes")
    for note in summary.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
