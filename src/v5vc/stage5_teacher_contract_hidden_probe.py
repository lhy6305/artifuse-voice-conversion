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
from v5vc.stage5_representation_oracle_probe import (
    DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    DEFAULT_WAVEFORM_MLP_LR,
    DEFAULT_WAVEFORM_MLP_STEPS,
    build_target_proxy_bundle,
    evaluate_oracle_probe_stage,
)
from v5vc.stage5_source_scaffold_oracle_probe import (
    build_candidate_stage_sequences as build_source_scaffold_stage_sequences,
    build_cross_record_stage_aggregates,
    build_stage_aggregates,
)


STAGE_SPECS = [
    ("selected_dynamic_controls", "Current Stage5-selected dynamic controls rebuilt from source_scaffold available_controls."),
    ("all_available_controls", "Full dynamic control contract from source_scaffold available_controls."),
    ("unselected_available_controls", "Dynamic controls present in source_scaffold but omitted from the current Stage5-selected contract."),
    ("source_contract_core_controls", "Upstream source-contract core controls before source_scaffold branch rebuilding."),
    ("source_contract_full_dynamic", "Full upstream source-contract dynamic package before source_scaffold branch rebuilding."),
    ("source_contract_diagnostics_family", "Upstream source-contract diagnostics that are not forwarded into source_scaffold available_controls."),
    ("source_contract_controls_plus_diagnostics", "Full upstream source-contract dynamic package plus extra diagnostics."),
    ("source_contract_hidden", "Upstream source-contract hidden state when the source contract exports one."),
    ("source_contract_fused_hidden", "Upstream source-contract fused hidden state when the source contract exports one."),
]
CONTROL_STAGE_NAMES = {
    "selected_dynamic_controls",
    "all_available_controls",
    "unselected_available_controls",
    "source_contract_core_controls",
    "source_contract_full_dynamic",
    "source_contract_diagnostics_family",
    "source_contract_controls_plus_diagnostics",
}
HIDDEN_STAGE_NAMES = {"source_contract_hidden", "source_contract_fused_hidden"}


def analyze_stage5_nores_teacher_contract_hidden_probe(
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
        raise ValueError("No Stage5 training packages were selected for the teacher-contract hidden probe.")

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
        "stage_aggregates": build_stage_aggregates(per_record_rows, stage_names=stage_names),
        "cross_record_stage_aggregates": cross_record_stage_aggregates,
        "source_contract_summary": build_teacher_contract_hidden_summary(cross_record_stage_aggregates),
        "records": per_record_rows,
        "notes": [
            "This probe moves one step earlier than the read-only source_scaffold control contract and reopens the upstream source contract pointed to by source_scaffold.",
            "When the source contract is a streaming_student packet, the main comparison becomes exported packet controls versus packet-only diagnostics that are not forwarded into source_scaffold.",
            "The source_scaffold control subsets are kept inside the same probe as direct baselines so any upstream gain must appear inside the same run.",
        ],
    }
    (output_dir / "stage5_teacher_contract_hidden_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "stage5_teacher_contract_hidden_probe.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_candidate_stage_sequences(*, package_payload: dict[str, object]) -> dict[str, torch.Tensor]:
    stage_sequences: dict[str, torch.Tensor] = {}
    scaffold_stage_sequences = build_source_scaffold_stage_sequences(package_payload=package_payload)
    for stage_name in ("selected_dynamic_controls", "all_available_controls", "unselected_available_controls"):
        if stage_name in scaffold_stage_sequences:
            stage_sequences[stage_name] = scaffold_stage_sequences[stage_name]

    contract_payload = load_teacher_contract_payload(package_payload)
    packet_version = str(contract_payload.get("packet_version", ""))
    if packet_version == "streaming_student_downstream_control_v1":
        add_student_packet_stages(stage_sequences=stage_sequences, contract_payload=contract_payload)
    else:
        add_teacher_contract_stages(stage_sequences=stage_sequences, contract_payload=contract_payload)
    return stage_sequences


def add_teacher_contract_stages(
    *,
    stage_sequences: dict[str, torch.Tensor],
    contract_payload: dict[str, object],
) -> None:
    core_slices: list[torch.Tensor] = []
    full_dynamic_slices: list[torch.Tensor] = []
    z_art = extract_contract_tensor(contract_payload, "z_art")
    if z_art is not None:
        core_slices.append(z_art)
        full_dynamic_slices.append(z_art)
    for event_key in ("e_evt", "event_probs"):
        event_tensor = extract_contract_tensor(contract_payload, event_key)
        if event_tensor is not None:
            core_slices.append(event_tensor)
            full_dynamic_slices.append(event_tensor)
    v2_core = concat_contract_tensors(contract_payload, ("f0_hz", "vuv", "aper", "E"))
    if v2_core is not None:
        core_slices.append(v2_core)
        full_dynamic_slices.append(v2_core)
    acoustic_family = concat_nested_contract_tensors(
        contract_payload,
        "acoustic",
        ("energy_log", "abs_mean", "zero_cross_rate", "delta_energy"),
    )
    if acoustic_family is not None:
        full_dynamic_slices.append(acoustic_family)
    proxy_family = concat_nested_contract_tensors(
        contract_payload,
        "derived_proxies",
        ("energy_proxy", "voiced_proxy", "aperiodicity_proxy", "event_presence_proxy", "energy_change_proxy"),
    )
    if proxy_family is not None:
        full_dynamic_slices.append(proxy_family)
    if core_slices:
        stage_sequences["source_contract_core_controls"] = torch.cat(core_slices, dim=-1)
    if full_dynamic_slices:
        stage_sequences["source_contract_full_dynamic"] = torch.cat(full_dynamic_slices, dim=-1)
    for stage_name, contract_key in (
        ("source_contract_hidden", "hidden"),
        ("source_contract_fused_hidden", "fused_hidden"),
    ):
        stage_tensor = extract_contract_tensor(contract_payload, contract_key)
        if stage_tensor is not None:
            stage_sequences[stage_name] = stage_tensor


def add_student_packet_stages(
    *,
    stage_sequences: dict[str, torch.Tensor],
    contract_payload: dict[str, object],
) -> None:
    packet_core = concat_nested_contract_tensors(
        contract_payload,
        "controls",
        (
            "z_art",
            "e_evt",
            "legacy_event_probs",
            "f0_hz_calibrated",
            "vuv_prob",
            "aper_prob_calibrated",
            "energy_stage5_norm_calibrated",
        ),
    )
    packet_full = concat_nested_contract_tensors(
        contract_payload,
        "controls",
        (
            "z_art",
            "legacy_event_probs",
            "e_evt",
            "f0_log_proxy",
            "f0_hz_calibrated",
            "f0_hz_stage5_norm",
            "vuv_prob",
            "aper_prob",
            "aper_prob_calibrated",
            "energy_log",
            "energy_norm",
            "energy_stage5_norm",
            "energy_stage5_norm_calibrated",
        ),
    )
    packet_diagnostics = concat_nested_contract_tensors(
        contract_payload,
        "diagnostics",
        ("event_logits", "event_prior_probs", "coarse_log_f0", "log_f0_correction"),
    )
    if packet_core is not None:
        stage_sequences["source_contract_core_controls"] = packet_core
    if packet_full is not None:
        stage_sequences["source_contract_full_dynamic"] = packet_full
    if packet_diagnostics is not None:
        stage_sequences["source_contract_diagnostics_family"] = packet_diagnostics
    if packet_full is not None and packet_diagnostics is not None:
        stage_sequences["source_contract_controls_plus_diagnostics"] = torch.cat(
            [packet_full, packet_diagnostics],
            dim=-1,
        )


def load_teacher_contract_payload(package_payload: dict[str, object]) -> dict[str, object]:
    scaffold_path = Path(str(package_payload["source_scaffold_path"])).resolve()
    scaffold_payload = torch.load(scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(scaffold_payload, dict):
        raise TypeError(f"Unsupported source scaffold payload type: {type(scaffold_payload)!r}")
    contract_path = scaffold_payload.get("source_contract_path")
    if not isinstance(contract_path, str) or not contract_path:
        raise KeyError("source_scaffold payload is missing source_contract_path for teacher-contract hidden probe.")
    contract_payload = torch.load(Path(contract_path).resolve(), map_location="cpu", weights_only=False)
    if not isinstance(contract_payload, dict):
        raise TypeError(f"Unsupported teacher contract payload type: {type(contract_payload)!r}")
    return contract_payload


def extract_contract_tensor(contract_payload: dict[str, object], key: str) -> torch.Tensor | None:
    value = contract_payload.get(key)
    if not isinstance(value, torch.Tensor):
        return None
    return value.detach().cpu().to(torch.float32)


def concat_contract_tensors(contract_payload: dict[str, object], keys: tuple[str, ...]) -> torch.Tensor | None:
    slices = [tensor for key in keys if (tensor := extract_contract_tensor(contract_payload, key)) is not None]
    if not slices:
        return None
    return torch.cat(slices, dim=-1)


def concat_nested_contract_tensors(
    contract_payload: dict[str, object],
    parent_key: str,
    child_keys: tuple[str, ...],
) -> torch.Tensor | None:
    parent = contract_payload.get(parent_key)
    if not isinstance(parent, dict):
        return None
    slices = []
    for child_key in child_keys:
        value = parent.get(child_key)
        if isinstance(value, torch.Tensor):
            slices.append(value.detach().cpu().to(torch.float32))
    if not slices:
        return None
    return torch.cat(slices, dim=-1)


def resolve_present_stage_names(*, package_payload: dict[str, object]) -> list[str]:
    candidate_sequences = build_candidate_stage_sequences(package_payload=package_payload)
    return [stage_name for stage_name, _ in STAGE_SPECS if stage_name in candidate_sequences]


def build_teacher_contract_hidden_summary(cross_record_stage_aggregates: list[dict[str, object]]) -> dict[str, object]:
    by_stage = {str(item["stage_name"]): item for item in cross_record_stage_aggregates}
    if not by_stage:
        return {"diagnosis": "missing_cross_record_stage_aggregates"}
    best_linear = max(cross_record_stage_aggregates, key=lambda item: float(item.get("oracle_waveform_frame_cosine_mean", 0.0)))
    best_mlp = max(cross_record_stage_aggregates, key=lambda item: float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)))
    best_control = best_stage(cross_record_stage_aggregates, CONTROL_STAGE_NAMES)
    best_hidden = best_stage(cross_record_stage_aggregates, HIDDEN_STAGE_NAMES)
    summary: dict[str, object] = {
        "best_cross_record_waveform_stage": str(best_linear["stage_name"]),
        "best_cross_record_waveform_value": float(best_linear["oracle_waveform_frame_cosine_mean"]),
        "best_cross_record_waveform_mlp_stage": str(best_mlp["stage_name"]),
        "best_cross_record_waveform_mlp_value": float(best_mlp["oracle_waveform_mlp_frame_cosine_mean"]),
        "best_control_stage": None if best_control is None else str(best_control["stage_name"]),
        "best_control_signal": max_stage_signal(best_control),
        "best_hidden_stage": None if best_hidden is None else str(best_hidden["stage_name"]),
        "best_hidden_signal": max_stage_signal(best_hidden),
    }
    for prefix, src_name, dst_name in (
        ("selected_dynamic_to_source_contract_hidden", "selected_dynamic_controls", "source_contract_hidden"),
        ("all_controls_to_source_contract_hidden", "all_available_controls", "source_contract_hidden"),
        (
            "selected_dynamic_to_source_contract_fused_hidden",
            "selected_dynamic_controls",
            "source_contract_fused_hidden",
        ),
        (
            "all_controls_to_source_contract_fused_hidden",
            "all_available_controls",
            "source_contract_fused_hidden",
        ),
        (
            "selected_dynamic_to_source_contract_diagnostics",
            "selected_dynamic_controls",
            "source_contract_diagnostics_family",
        ),
        (
            "all_controls_to_source_contract_diagnostics",
            "all_available_controls",
            "source_contract_diagnostics_family",
        ),
    ):
        add_waveform_gain(summary, by_stage.get(src_name), by_stage.get(dst_name), prefix)
    best_hidden_signal = max_stage_signal(best_hidden)
    best_control_signal = max_stage_signal(best_control)
    diagnostics_signal = max_stage_signal(by_stage.get("source_contract_diagnostics_family"))
    if best_hidden_signal < 0.05:
        if diagnostics_signal < 0.05:
            summary["diagnosis"] = "fine_waveform_geometry_is_already_weak_in_the_available_upstream_source_contract"
        elif diagnostics_signal >= best_control_signal + 0.02:
            summary["diagnosis"] = "source_contract_diagnostics_are_stronger_than_forwarded_control_contract_but_still_subthreshold"
        else:
            summary["diagnosis"] = "fine_waveform_geometry_is_already_weak_even_without_hidden_state_export"
    elif best_hidden_signal >= best_control_signal + 0.02:
        summary["diagnosis"] = "source_contract_hidden_states_contain_additional_fine_geometry_outside_explicit_control_contract"
    elif best_hidden_signal > best_control_signal:
        summary["diagnosis"] = "source_contract_hidden_states_are_only_marginally_stronger_than_explicit_control_contract"
    else:
        summary["diagnosis"] = "explicit_control_contract_is_not_weaker_than_available_upstream_source_contract"
    return summary


def best_stage(rows: list[dict[str, object]], allowed_stage_names: set[str]) -> dict[str, object] | None:
    filtered = [row for row in rows if str(row["stage_name"]) in allowed_stage_names]
    if not filtered:
        return None
    return max(
        filtered,
        key=lambda item: max(
            float(item.get("oracle_waveform_frame_cosine_mean", 0.0)),
            float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)),
        ),
    )


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


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Source-Contract Upstream Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- source_contract_summary: {json.dumps(summary['source_contract_summary'], ensure_ascii=False)}",
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
