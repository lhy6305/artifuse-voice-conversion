from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
import shutil
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.data_scan import summarize_numeric
from v5vc.event_semantics import (
    TEACHER_E_EVT_TARGET_SHAPING_MODE_CHOICES,
    TEACHER_E_EVT_TARGET_SHAPING_MODE_HARD_BOX_V1,
    build_design_state_e_evt_v1_meta,
    build_teacher_e_evt_v1_targets,
    normalize_teacher_e_evt_target_shaping_mode,
)
from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    TEXT_FEATURE_VERSION_LEGACY_V0,
    attach_target_event_semantic_sidecar,
    attach_target_event_timing_semantic_sidecar,
    attach_target_special_supervision,
    attach_target_weak_event_hints,
    build_record_semantic_overview,
    build_record_timing_semantic_overview,
    build_char_vocab,
    collate_target_batch,
    infer_target_event_semantic_sidecar_path,
    infer_target_event_timing_semantic_sidecar_path,
    load_target_examples_from_records,
    load_target_event_semantic_sidecar_map,
    load_target_event_timing_semantic_sidecar_map,
    load_target_special_supervision_map,
    load_target_weak_event_hint_map,
)
from v5vc.offline_mvp.losses import build_frame_targets
from v5vc.proxy_audio_export import sanitize_filename
from v5vc.train_entry import instantiate_offline_mvp_model


DEFAULT_ROUTE_HANDOFF_PATH = Path(
    "reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"
)
LOW_CONFIDENCE_THRESHOLD = 0.35


def build_streaming_student_teacher_labels(
    data_output_dir: Path,
    report_output_dir: Path,
    route_handoff_path: Path | None,
    experiment_metrics_path: Path | None,
    checkpoint_path: Path | None,
    split_dir: Path | None,
    batch_size: int,
    max_records_per_slice: int | None,
    teacher_e_evt_target_shaping_mode: str = TEACHER_E_EVT_TARGET_SHAPING_MODE_HARD_BOX_V1,
) -> None:
    shaping_mode = normalize_teacher_e_evt_target_shaping_mode(teacher_e_evt_target_shaping_mode)
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    source = resolve_teacher_source(
        route_handoff_path=route_handoff_path,
        experiment_metrics_path=experiment_metrics_path,
        checkpoint_path=checkpoint_path,
        split_dir=split_dir,
    )
    checkpoint_payload = load_checkpoint(source["checkpoint_path"])
    checkpoint_config = checkpoint_payload.get("config")
    if not isinstance(checkpoint_config, dict):
        raise ValueError("Teacher checkpoint does not contain a valid config payload.")
    if not isinstance(checkpoint_config.get("model"), dict):
        raise ValueError("Teacher checkpoint config.model is missing.")
    if not isinstance(checkpoint_config.get("data"), dict):
        raise ValueError("Teacher checkpoint config.data is missing.")

    model = instantiate_offline_mvp_model(dict(checkpoint_config["model"]))
    model.load_state_dict(checkpoint_payload["model_state_dict"])
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    records_by_split = load_target_records_by_split(
        split_dir=source["split_dir"],
        checkpoint_config=checkpoint_config,
        workspace_root=source["workspace_root"],
        max_records_per_slice=max_records_per_slice,
    )
    target_train_records = list(records_by_split["target_train"])
    vocab = build_char_vocab(target_train_records)
    text_feature_version = str(
        checkpoint_config["data"].get("target_text_feature_version", TEXT_FEATURE_VERSION_LEGACY_V0)
    )
    records_dir = data_output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    summary_slices: dict[str, object] = {}
    index_rows: list[dict[str, object]] = []
    aggregate_record_count = 0
    aggregate_frame_count = 0

    with torch.no_grad():
        for split_name in ("target_train", "target_validation", "target_special_eval"):
            export_result = export_split_teacher_labels(
                model=model,
                records=records_by_split[split_name],
                split_name=split_name,
                vocab=vocab,
                text_feature_version=text_feature_version,
                frame_length=int(checkpoint_config["model"]["frame_length"]),
                hop_length=int(checkpoint_config["model"]["hop_length"]),
                batch_size=max(1, int(batch_size)),
                records_dir=records_dir,
                teacher_anchor=source["teacher_anchor"],
                teacher_e_evt_target_shaping_mode=shaping_mode,
            )
            summary_slices[split_name] = export_result["summary"]
            index_rows.extend(export_result["index_rows"])
            aggregate_record_count += int(export_result["summary"]["record_count"])
            aggregate_frame_count += int(export_result["summary"]["frame_count_stats"]["sum"])

    index_path = data_output_dir / "teacher_label_index.jsonl"
    index_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in index_rows) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "route_handoff_path": None if source["route_handoff_path"] is None else source["route_handoff_path"].as_posix(),
        "experiment_metrics_path": (
            None if source["experiment_metrics_path"] is None else source["experiment_metrics_path"].as_posix()
        ),
        "checkpoint_path": source["checkpoint_path"].as_posix(),
        "split_dir": source["split_dir"].as_posix(),
        "data_output_dir": data_output_dir.as_posix(),
        "report_output_dir": report_output_dir.as_posix(),
        "teacher_anchor": source["teacher_anchor"],
        "index_path": index_path.as_posix(),
        "record_count": aggregate_record_count,
        "frame_count": aggregate_frame_count,
        "batch_size": max(1, int(batch_size)),
        "max_records_per_slice": None if max_records_per_slice is None else int(max_records_per_slice),
        "teacher_e_evt_target_shaping_mode": shaping_mode,
        "teacher_e_evt_target_shaping_mode_choices": sorted(TEACHER_E_EVT_TARGET_SHAPING_MODE_CHOICES),
        "feature_dims": {
            "hidden": int(checkpoint_config["model"]["hidden_dim"]),
            "fused_hidden": int(checkpoint_config["model"]["hidden_dim"]),
            "z_art": int(checkpoint_config["model"]["z_art_dim"]),
            "event_logits": int(checkpoint_config["model"]["event_dim"]),
            "e_evt": int(checkpoint_config["model"]["event_dim"]),
            "acoustic": int(checkpoint_config["model"]["acoustic_dim"]),
            "confidence": 1,
        },
        "slices": summary_slices,
        "notes": [
            "Teacher labels are pseudo labels exported from the formal offline_mvp route anchor, not physical ground truth.",
            "frame_confidence uses heuristic bootstrap_v1 and is meant for later weighting/filtering, not as a final confidence design.",
            "This export now materializes a bootstrap teacher_e_evt target so Stage3 can stop treating legacy heuristic event_probs as the final event contract.",
            "Stage3 may reuse these labels as assets, but should still keep its own training entry and loss contract separate from offline_mvp.",
            f"teacher_e_evt target shaping mode for this export = {shaping_mode}.",
        ],
    }

    summary_json_path = report_output_dir / "streaming_student_teacher_label_summary.json"
    summary_md_path = report_output_dir / "streaming_student_teacher_label_summary.md"
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_markdown(summary=summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def resolve_teacher_source(
    route_handoff_path: Path | None,
    experiment_metrics_path: Path | None,
    checkpoint_path: Path | None,
    split_dir: Path | None,
) -> dict[str, object]:
    workspace_root = Path.cwd().resolve()
    route_handoff_resolved = None
    route_anchor: dict[str, object] = {}
    if route_handoff_path is None:
        default_route_handoff_path = (workspace_root / DEFAULT_ROUTE_HANDOFF_PATH).resolve()
        if default_route_handoff_path.exists():
            route_handoff_path = default_route_handoff_path
    if route_handoff_path is not None:
        route_handoff_resolved = route_handoff_path.resolve()
        route_payload = json.loads(route_handoff_resolved.read_text(encoding="utf-8"))
        route_anchor = dict(route_payload.get("route_anchor", {}))
        if experiment_metrics_path is None:
            raw_metrics_path = route_anchor.get("experiment_metrics_path")
            if raw_metrics_path not in {None, ""}:
                experiment_metrics_path = resolve_path_ref(raw_metrics_path, workspace_root=workspace_root)
        if checkpoint_path is None:
            raw_checkpoint_path = route_anchor.get("checkpoint_path")
            if raw_checkpoint_path not in {None, ""}:
                checkpoint_path = resolve_path_ref(raw_checkpoint_path, workspace_root=workspace_root)

    metrics_payload = None
    metrics_path_resolved = None
    if experiment_metrics_path is not None:
        metrics_path_resolved = experiment_metrics_path.resolve()
        metrics_payload = json.loads(metrics_path_resolved.read_text(encoding="utf-8"))
    if checkpoint_path is None and metrics_payload is not None:
        checkpoint_ref = (
            metrics_payload.get("metrics", {})
            .get("training_run", {})
            .get("artifacts", {})
            .get("checkpoint_path")
        )
        if checkpoint_ref in {None, ""}:
            raise ValueError("Could not resolve checkpoint_path from experiment metrics.")
        checkpoint_path = resolve_path_ref(checkpoint_ref, workspace_root=workspace_root)
    if checkpoint_path is None:
        raise ValueError("Teacher-label export requires a route handoff, experiment metrics, or explicit checkpoint path.")

    if split_dir is None and metrics_payload is not None:
        split_ref = (
            metrics_payload.get("metrics", {})
            .get("training_run", {})
            .get("split", {})
            .get("split_dir")
        )
        if split_ref not in {None, ""}:
            split_dir = resolve_path_ref(split_ref, workspace_root=workspace_root)
    if split_dir is None:
        raise ValueError("Teacher-label export requires split_dir, either explicitly or via experiment metrics.")

    teacher_anchor = {
        "experiment_id": (
            str(route_anchor.get("experiment_id"))
            if route_anchor.get("experiment_id")
            else (None if metrics_payload is None else str(metrics_payload.get("experiment_id")))
        ),
        "checkpoint_path": checkpoint_path.resolve().as_posix(),
        "experiment_metrics_path": None if metrics_path_resolved is None else metrics_path_resolved.as_posix(),
        "route_policy": None,
        "route_selected_anchor_id": None,
        "source": "explicit_checkpoint",
    }
    if route_handoff_resolved is not None:
        route_payload = json.loads(route_handoff_resolved.read_text(encoding="utf-8"))
        route_context = dict(route_payload.get("route_context", {}))
        teacher_anchor["route_policy"] = route_context.get("selected_policy")
        teacher_anchor["route_selected_anchor_id"] = route_context.get("selected_anchor_id")
        teacher_anchor["source"] = "route_handoff_anchor"
    elif metrics_path_resolved is not None:
        teacher_anchor["source"] = "experiment_metrics"

    return {
        "workspace_root": workspace_root,
        "route_handoff_path": route_handoff_resolved,
        "experiment_metrics_path": metrics_path_resolved,
        "checkpoint_path": checkpoint_path.resolve(),
        "split_dir": split_dir.resolve(),
        "teacher_anchor": teacher_anchor,
    }


def resolve_path_ref(raw_path: object, workspace_root: Path) -> Path:
    candidate = Path(str(raw_path))
    if candidate.is_absolute():
        return candidate.resolve()
    return (workspace_root / candidate).resolve()


def load_target_records_by_split(
    split_dir: Path,
    checkpoint_config: dict[str, object],
    workspace_root: Path,
    max_records_per_slice: int | None,
) -> dict[str, list[dict[str, object]]]:
    records_by_split = {
        "target_train": load_jsonl(split_dir / "target_train.jsonl"),
        "target_validation": load_jsonl(split_dir / "target_validation.jsonl"),
        "target_special_eval": load_jsonl(split_dir / "target_special_eval.jsonl"),
    }
    weak_event_hints_path = checkpoint_config["data"].get("target_weak_event_hints_path")
    if weak_event_hints_path not in {None, ""}:
        resolved_hint_path = resolve_path_ref(weak_event_hints_path, workspace_root=workspace_root)
        if resolved_hint_path.exists():
            hint_map = load_target_weak_event_hint_map(resolved_hint_path)
            for split_name, records in records_by_split.items():
                records_by_split[split_name] = attach_target_weak_event_hints(records, hint_map)
    target_special_supervision_path = checkpoint_config["data"].get("target_special_supervision_path")
    if target_special_supervision_path not in {None, ""}:
        resolved_supervision_path = resolve_path_ref(target_special_supervision_path, workspace_root=workspace_root)
        if resolved_supervision_path.exists():
            supervision_map = load_target_special_supervision_map(resolved_supervision_path)
            for split_name, records in records_by_split.items():
                records_by_split[split_name] = attach_target_special_supervision(records, supervision_map)
    target_event_semantic_sidecar_path = resolve_target_event_semantic_sidecar_path(
        split_dir=split_dir,
        checkpoint_config=checkpoint_config,
        workspace_root=workspace_root,
    )
    if target_event_semantic_sidecar_path is not None and target_event_semantic_sidecar_path.exists():
        semantic_map = load_target_event_semantic_sidecar_map(target_event_semantic_sidecar_path)
        for split_name, records in records_by_split.items():
            records_by_split[split_name] = attach_target_event_semantic_sidecar(records, semantic_map)
    target_event_timing_semantic_sidecar_path = resolve_target_event_timing_semantic_sidecar_path(
        split_dir=split_dir,
        checkpoint_config=checkpoint_config,
        workspace_root=workspace_root,
    )
    if (
        target_event_timing_semantic_sidecar_path is not None
        and target_event_timing_semantic_sidecar_path.exists()
    ):
        timing_map = load_target_event_timing_semantic_sidecar_map(target_event_timing_semantic_sidecar_path)
        for split_name, records in records_by_split.items():
            records_by_split[split_name] = attach_target_event_timing_semantic_sidecar(records, timing_map)
    if max_records_per_slice is not None and max_records_per_slice > 0:
        for split_name in records_by_split:
            records_by_split[split_name] = records_by_split[split_name][: max_records_per_slice]
    return records_by_split


def resolve_target_event_semantic_sidecar_path(
    split_dir: Path,
    checkpoint_config: dict[str, object],
    workspace_root: Path,
) -> Path | None:
    raw_value = checkpoint_config["data"].get("target_event_semantic_sidecar_path")
    if raw_value not in {None, ""}:
        return resolve_path_ref(raw_value, workspace_root=workspace_root)
    return infer_target_event_semantic_sidecar_path(split_dir)


def resolve_target_event_timing_semantic_sidecar_path(
    split_dir: Path,
    checkpoint_config: dict[str, object],
    workspace_root: Path,
) -> Path | None:
    raw_value = checkpoint_config["data"].get("target_event_timing_semantic_sidecar_path")
    if raw_value not in {None, ""}:
        return resolve_path_ref(raw_value, workspace_root=workspace_root)
    return infer_target_event_timing_semantic_sidecar_path(split_dir)


def export_split_teacher_labels(
    model: torch.nn.Module,
    records: list[dict[str, object]],
    split_name: str,
    vocab: dict[str, int],
    text_feature_version: str,
    frame_length: int,
    hop_length: int,
    batch_size: int,
    records_dir: Path,
    teacher_anchor: dict[str, object],
    teacher_e_evt_target_shaping_mode: str,
) -> dict[str, object]:
    index_rows: list[dict[str, object]] = []
    duration_values: list[float] = []
    frame_counts: list[int] = []
    confidence_means: list[float] = []
    low_confidence_ratios: list[float] = []
    structure_counts: Counter[str] = Counter()
    terminal_counts: Counter[str] = Counter()
    semantic_contract_counts: Counter[str] = Counter()
    semantic_inventory_counts: Counter[str] = Counter()
    semantic_label_status_counts: Counter[str] = Counter()
    semantic_structure_counts: Counter[str] = Counter()
    semantic_terminal_counts: Counter[str] = Counter()
    timing_contract_counts: Counter[str] = Counter()
    timing_inventory_counts: Counter[str] = Counter()
    timing_label_status_counts: Counter[str] = Counter()
    timing_alignment_counts: Counter[str] = Counter()
    teacher_event_target_shaping_counts: Counter[str] = Counter()

    if not records:
        return {
            "index_rows": [],
            "summary": {
                "record_count": 0,
                "duration_stats_sec": summarize_numeric([]),
                "frame_count_stats": build_int_summary([]),
                "confidence_mean_stats": summarize_numeric([]),
                "low_confidence_frame_ratio_stats": summarize_numeric([]),
                "utterance_structure_type_counts": {},
                "final_terminal_type_counts": {},
                "semantic_contract_version_counts": {},
                "semantic_inventory_status_counts": {},
                "semantic_label_status_counts": {},
                "semantic_utterance_structure_type_counts": {},
                "semantic_final_terminal_type_counts": {},
                "timing_contract_version_counts": {},
                "timing_inventory_status_counts": {},
                "timing_label_status_counts": {},
                "timing_alignment_type_counts": {},
                "teacher_event_target_shaping_mode_counts": {},
                "sample_record_ids": [],
            },
        }

    for batch_start in range(0, len(records), batch_size):
        batch_records = records[batch_start : batch_start + batch_size]
        examples = load_target_examples_from_records(
            batch_records,
            vocab=vocab,
            max_duration_sec=None,
            text_feature_version=text_feature_version,
        )
        batch = collate_target_batch(examples)
        outputs = model(
            waveform=batch["waveform"],
            lengths=batch["audio_lengths"],
        )
        frame_targets = build_frame_targets(
            waveform=batch["waveform"],
            lengths=batch["audio_lengths"],
            frame_length=frame_length,
            hop_length=hop_length,
            weak_event_hints=batch.get("weak_event_hints"),
        )
        frame_confidence = estimate_frame_confidence(
            outputs=outputs,
            frame_targets=frame_targets,
            threshold=LOW_CONFIDENCE_THRESHOLD,
        )

        for sample_index, record in enumerate(batch_records):
            export_row = export_single_record(
                record=record,
                split_name=split_name,
                sample_index=sample_index,
                outputs=outputs,
                frame_confidence=frame_confidence,
                records_dir=records_dir,
                teacher_anchor=teacher_anchor,
                threshold=LOW_CONFIDENCE_THRESHOLD,
                teacher_e_evt_target_shaping_mode=teacher_e_evt_target_shaping_mode,
            )
            index_rows.append(export_row)
            duration_values.append(float(record["audio"]["duration_sec"]))
            frame_counts.append(int(export_row["frame_count"]))
            confidence_means.append(float(export_row["confidence_mean"]))
            low_confidence_ratios.append(float(export_row["low_confidence_frame_ratio"]))
            semantic_overview = build_record_semantic_overview(record)
            structure_counts[str(semantic_overview["semantic_utterance_structure_type"])] += 1
            terminal_counts[str(semantic_overview["semantic_final_terminal_type"])] += 1
            semantic_contract_counts[str(semantic_overview["semantic_contract_version"] or "missing")] += 1
            semantic_inventory_counts[str(semantic_overview["semantic_inventory_status"])] += 1
            semantic_label_status_counts[str(semantic_overview["semantic_label_status"])] += 1
            semantic_structure_counts[str(semantic_overview["semantic_utterance_structure_type"])] += 1
            semantic_terminal_counts[str(semantic_overview["semantic_final_terminal_type"])] += 1
            timing_overview = build_record_timing_semantic_overview(record)
            timing_contract_counts[str(timing_overview["timing_contract_version"] or "missing")] += 1
            timing_inventory_counts[str(timing_overview["timing_inventory_status"])] += 1
            timing_label_status_counts[str(timing_overview["timing_label_status"])] += 1
            timing_alignment_counts[str(timing_overview["timing_alignment_type"] or "missing")] += 1
            teacher_event_target_shaping_counts[str(export_row["teacher_event_target_shaping_mode"])] += 1

    return {
        "index_rows": index_rows,
        "summary": {
            "record_count": len(index_rows),
            "duration_stats_sec": summarize_numeric(duration_values),
            "frame_count_stats": build_int_summary(frame_counts),
            "confidence_mean_stats": summarize_numeric(confidence_means),
            "low_confidence_frame_ratio_stats": summarize_numeric(low_confidence_ratios),
            "utterance_structure_type_counts": dict(sorted(structure_counts.items())),
            "final_terminal_type_counts": dict(sorted(terminal_counts.items())),
            "semantic_contract_version_counts": dict(sorted(semantic_contract_counts.items())),
            "semantic_inventory_status_counts": dict(sorted(semantic_inventory_counts.items())),
            "semantic_label_status_counts": dict(sorted(semantic_label_status_counts.items())),
            "semantic_utterance_structure_type_counts": dict(sorted(semantic_structure_counts.items())),
            "semantic_final_terminal_type_counts": dict(sorted(semantic_terminal_counts.items())),
            "timing_contract_version_counts": dict(sorted(timing_contract_counts.items())),
            "timing_inventory_status_counts": dict(sorted(timing_inventory_counts.items())),
            "timing_label_status_counts": dict(sorted(timing_label_status_counts.items())),
            "timing_alignment_type_counts": dict(sorted(timing_alignment_counts.items())),
            "teacher_event_target_shaping_mode_counts": dict(sorted(teacher_event_target_shaping_counts.items())),
            "sample_record_ids": [str(row["record_id"]) for row in index_rows[:8]],
        },
    }


def export_single_record(
    record: dict[str, object],
    split_name: str,
    sample_index: int,
    outputs: dict[str, torch.Tensor],
    frame_confidence: torch.Tensor,
    records_dir: Path,
    teacher_anchor: dict[str, object],
    threshold: float,
    teacher_e_evt_target_shaping_mode: str,
) -> dict[str, object]:
    record_id = str(record["record_id"])
    frame_mask = outputs["frame_mask"][sample_index].detach().cpu()
    valid_frame_count = int(frame_mask.sum().item())
    if valid_frame_count <= 0:
        raise ValueError(f"Teacher export encountered zero valid frames for {record_id}.")
    semantic_overview = build_record_semantic_overview(record)
    timing_overview = build_record_timing_semantic_overview(record)
    teacher_e_evt = build_teacher_e_evt_v1_targets(
        legacy_event_probs=outputs["event_probs"][sample_index],
        target_event_semantic_sidecar=record.get("target_event_semantic_sidecar"),
        target_event_timing_semantic_sidecar=record.get("target_event_timing_semantic_sidecar"),
        valid_frame_count=valid_frame_count,
        teacher_e_evt_target_shaping_mode=teacher_e_evt_target_shaping_mode,
    )
    tensor_payload = {
        "record_id": record_id,
        "split_name": split_name,
        "teacher_anchor": dict(teacher_anchor),
        "export_format": "offline_mvp_teacher_labels_v2",
        "confidence_estimator": "bootstrap_v1",
        "frame_count": valid_frame_count,
        "frame_mask": trim_tensor(outputs["frame_mask"][sample_index], valid_frame_count),
        "hidden": trim_tensor(outputs["hidden"][sample_index], valid_frame_count),
        "fused_hidden": trim_tensor(outputs["fused_hidden"][sample_index], valid_frame_count),
        "z_art": trim_tensor(outputs["z_art"][sample_index], valid_frame_count),
        "event_logits": trim_tensor(outputs["event_logits"][sample_index], valid_frame_count),
        "event_probs": trim_tensor(outputs["event_probs"][sample_index], valid_frame_count),
        "e_evt": trim_tensor(teacher_e_evt["tensor"], valid_frame_count),
        "e_evt_meta": dict(teacher_e_evt["meta"]),
        "e_evt_summary": dict(teacher_e_evt["summary"]),
        "acoustic": trim_tensor(outputs["acoustic"][sample_index], valid_frame_count),
        "frame_confidence": trim_tensor(frame_confidence[sample_index], valid_frame_count),
    }
    relative_tensor_path = Path("records") / f"{sanitize_filename(record_id)}.pt"
    tensor_path = records_dir.parent / relative_tensor_path
    torch.save(tensor_payload, tensor_path)

    record_confidence = tensor_payload["frame_confidence"].to(torch.float32).squeeze(-1)
    low_confidence_ratio = float((record_confidence < threshold).to(torch.float32).mean().item())
    weak_event_hints = record.get("weak_event_hints")
    target_special_supervision = record.get("target_special_supervision")
    return {
        "record_id": record_id,
        "split_name": split_name,
        "audio_path": str(record["audio_path"]),
        "duration_sec": round(float(record["audio"]["duration_sec"]), 6),
        "frame_count": valid_frame_count,
        "teacher_label_path": tensor_path.as_posix(),
        "teacher_label_relative_path": relative_tensor_path.as_posix(),
        "confidence_mean": round(float(record_confidence.mean().item()), 6),
        "confidence_min": round(float(record_confidence.min().item()), 6),
        "confidence_max": round(float(record_confidence.max().item()), 6),
        "low_confidence_frame_ratio": round(low_confidence_ratio, 6),
        "utterance_structure_type": (
            None if not isinstance(weak_event_hints, dict) else str(weak_event_hints.get("utterance_structure_type"))
        ),
        "final_terminal_type": (
            None if not isinstance(weak_event_hints, dict) else str(weak_event_hints.get("final_terminal_type"))
        ),
        "semantic_source": str(semantic_overview["semantic_source"]),
        "semantic_contract_version": semantic_overview["semantic_contract_version"],
        "semantic_label_space_version": semantic_overview["semantic_label_space_version"],
        "semantic_inventory_status": str(semantic_overview["semantic_inventory_status"]),
        "semantic_label_status": str(semantic_overview["semantic_label_status"]),
        "semantic_utterance_structure_type": str(semantic_overview["semantic_utterance_structure_type"]),
        "semantic_final_terminal_type": str(semantic_overview["semantic_final_terminal_type"]),
        "teacher_event_contract_version": str(teacher_e_evt["meta"]["event_contract_version"]),
        "teacher_event_label_space_version": str(teacher_e_evt["meta"]["event_label_space_version"]),
        "teacher_event_target_shaping_mode": str(teacher_e_evt["meta"]["teacher_e_evt_target_shaping_mode"]),
        "timing_source": str(timing_overview["timing_source"]),
        "timing_contract_version": timing_overview["timing_contract_version"],
        "timing_label_space_version": timing_overview["timing_label_space_version"],
        "timing_inventory_status": str(timing_overview["timing_inventory_status"]),
        "timing_alignment_type": timing_overview["timing_alignment_type"],
        "timing_label_status": str(timing_overview["timing_label_status"]),
        "timing_clause_region_count": int(timing_overview["clause_region_count"]),
        "timing_pause_boundary_event_count": int(timing_overview["pause_boundary_event_count"]),
        "timing_terminal_boundary_event_count": int(timing_overview["terminal_boundary_event_count"]),
        "special_proximity_score": (
            None
            if not isinstance(target_special_supervision, dict)
            else round(float(target_special_supervision.get("special_proximity_score", 0.0)), 6)
        ),
        "pool_memberships": (
            {}
            if not isinstance(target_special_supervision, dict)
            else {
                str(key): bool(value)
                for key, value in dict(target_special_supervision.get("pool_memberships", {})).items()
                if str(key)
            }
        ),
    }


def trim_tensor(tensor: torch.Tensor, frame_count: int) -> torch.Tensor:
    trimmed = tensor[:frame_count].detach().cpu()
    if trimmed.dtype == torch.float32:
        return trimmed.to(torch.float16)
    return trimmed


def estimate_frame_confidence(
    outputs: dict[str, torch.Tensor],
    frame_targets: dict[str, torch.Tensor],
    threshold: float,
) -> torch.Tensor:
    event_probs = outputs["event_probs"].clamp(min=1.0e-5, max=1.0 - 1.0e-5)
    entropy = -(
        event_probs * torch.log(event_probs)
        + (1.0 - event_probs) * torch.log(1.0 - event_probs)
    )
    normalized_entropy = entropy / 0.6931471805599453
    event_certainty = 1.0 - normalized_entropy.mean(dim=-1, keepdim=True)

    acoustic_error = ((outputs["acoustic"] - frame_targets["acoustic_target"]) ** 2).mean(dim=-1, keepdim=True)
    acoustic_confidence = torch.exp(-8.0 * acoustic_error)

    z_art = outputs["z_art"]
    z_delta = torch.zeros((*z_art.shape[:2], 1), device=z_art.device, dtype=z_art.dtype)
    if z_art.shape[1] > 1:
        z_delta[:, 1:, 0] = (z_art[:, 1:] - z_art[:, :-1]).abs().mean(dim=-1)
    z_stability = torch.exp(-3.0 * z_delta)

    energy_norm = torch.sigmoid((frame_targets["acoustic_target"][..., 0:1] + 4.0) * 2.0)
    confidence = (
        event_certainty * 0.45
        + acoustic_confidence * 0.35
        + z_stability * 0.20
    )
    confidence = confidence * (0.55 + 0.45 * energy_norm)
    confidence = confidence.clamp(min=0.0, max=1.0)
    frame_mask = outputs["frame_mask"].to(confidence.dtype).unsqueeze(-1)
    confidence = confidence * frame_mask

    if float((confidence < threshold).to(torch.float32).mean().item()) >= 1.0:
        raise ValueError("Frame confidence collapsed to the low-confidence floor for an entire batch.")
    return confidence


def build_int_summary(values: list[int]) -> dict[str, int | float | None]:
    numeric = summarize_numeric(values)
    numeric["sum"] = int(sum(values))
    return numeric


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 streaming_student teacher-label export summary",
        "",
        "## Anchor",
        f"- teacher_anchor.experiment_id: {summary['teacher_anchor']['experiment_id']}",
        f"- teacher_anchor.source: {summary['teacher_anchor']['source']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- experiment_metrics_path: {summary['experiment_metrics_path']}",
        f"- route_handoff_path: {summary['route_handoff_path']}",
        f"- split_dir: {summary['split_dir']}",
        "",
        "## Export",
        f"- record_count: {summary['record_count']}",
        f"- frame_count: {summary['frame_count']}",
        f"- batch_size: {summary['batch_size']}",
        f"- max_records_per_slice: {summary['max_records_per_slice']}",
        f"- teacher_e_evt_target_shaping_mode: {summary['teacher_e_evt_target_shaping_mode']}",
        f"- index_path: {summary['index_path']}",
        "",
        "## Feature Dims",
    ]
    for key, value in dict(summary["feature_dims"]).items():
        lines.append(f"- {key}: {value}")
    for split_name in ("target_train", "target_validation", "target_special_eval"):
        slice_summary = dict(summary["slices"][split_name])
        lines.extend(
            [
                "",
                f"## {split_name}",
                f"- record_count: {slice_summary['record_count']}",
                f"- duration_mean_sec: {slice_summary['duration_stats_sec']['mean']}",
                f"- frame_count_mean: {slice_summary['frame_count_stats']['mean']}",
                f"- confidence_mean: {slice_summary['confidence_mean_stats']['mean']}",
                f"- low_confidence_frame_ratio_mean: {slice_summary['low_confidence_frame_ratio_stats']['mean']}",
                f"- utterance_structure_type_counts: {slice_summary['utterance_structure_type_counts']}",
                f"- final_terminal_type_counts: {slice_summary['final_terminal_type_counts']}",
                f"- semantic_contract_version_counts: {slice_summary['semantic_contract_version_counts']}",
                f"- semantic_inventory_status_counts: {slice_summary['semantic_inventory_status_counts']}",
                f"- semantic_label_status_counts: {slice_summary['semantic_label_status_counts']}",
                f"- semantic_utterance_structure_type_counts: {slice_summary['semantic_utterance_structure_type_counts']}",
                f"- semantic_final_terminal_type_counts: {slice_summary['semantic_final_terminal_type_counts']}",
                f"- timing_contract_version_counts: {slice_summary['timing_contract_version_counts']}",
                f"- timing_inventory_status_counts: {slice_summary['timing_inventory_status_counts']}",
                f"- timing_label_status_counts: {slice_summary['timing_label_status_counts']}",
                f"- timing_alignment_type_counts: {slice_summary['timing_alignment_type_counts']}",
                f"- teacher_event_target_shaping_mode_counts: {slice_summary['teacher_event_target_shaping_mode_counts']}",
                f"- sample_record_ids: {slice_summary['sample_record_ids']}",
            ]
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
