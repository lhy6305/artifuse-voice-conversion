from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import (
    assess_stage5_decoded_buzz_reject,
    build_model_from_checkpoint,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_speech_emergence_probe import (
    summarize_frame_sequence_metrics,
    summarize_scalar_values,
)
from v5vc.target_format_recovery import write_waveform_int16


HANDOFF_DECODE_ROUTES = [
    {
        "label": "decoded_no_gate",
        "description": "Overlap-add on waveform_frames without predicted activity gating.",
        "use_predicted_activity_gate": False,
        "predicted_activity_gate_apply_mode": "pre_overlap_add",
    },
    {
        "label": "decoded_pre_ola_gate",
        "description": "Apply predicted activity to each frame before overlap-add.",
        "use_predicted_activity_gate": True,
        "predicted_activity_gate_apply_mode": "pre_overlap_add",
    },
    {
        "label": "decoded_post_ola_gate",
        "description": "Apply predicted activity as a post-overlap-add envelope.",
        "use_predicted_activity_gate": True,
        "predicted_activity_gate_apply_mode": "post_ola_envelope",
    },
]


def analyze_stage5_nores_waveform_handoff(
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
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    decoder_branch_mean_mix_alpha: float = 0.0,
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
        raise ValueError("No Stage5 training packages were selected for the waveform handoff probe.")

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

    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            periodic_branch_features = batch["periodic_branch_features"].to(device=resolved_device, dtype=torch.float32)
            noise_branch_features = batch["noise_branch_features"].to(device=resolved_device, dtype=torch.float32)
            aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32).view(-1)
            outputs = model(
                periodic_branch_features,
                noise_branch_features,
                decoder_branch_mean_mix_alpha=float(decoder_branch_mean_mix_alpha),
            )
            predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"]).detach().cpu().to(
                torch.float32
            )
            if predicted_activity.ndim == 2 and int(predicted_activity.shape[-1]) == 1:
                predicted_activity = predicted_activity.squeeze(-1)
            periodic_hidden = outputs["periodic_hidden"].detach().cpu().to(torch.float32)
            noise_hidden = outputs["noise_hidden"].detach().cpu().to(torch.float32)
            branch_mean_hidden = outputs["branch_mean_hidden"].detach().cpu().to(torch.float32)
            fused_hidden = outputs["fused_hidden"].detach().cpu().to(torch.float32)
            decoder_hidden = outputs["decoder_hidden"].detach().cpu().to(torch.float32)
            waveform_frame_logits = outputs["waveform_frame_logits"].detach().cpu().to(torch.float32)
            waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
            stage_metrics = summarize_handoff_stage_metrics(
                periodic_hidden=periodic_hidden,
                noise_hidden=noise_hidden,
                branch_mean_hidden=branch_mean_hidden,
                fused_hidden=fused_hidden,
                decoder_hidden=decoder_hidden,
                waveform_frame_logits=waveform_frame_logits,
                waveform_frames=waveform_frames,
            )

            record_slug = sanitize_record_id(str(entry["record_id"]))
            aligned_target_audio_path = output_dir / f"{record_slug}__aligned_target.wav"
            write_waveform_int16(aligned_target_audio_path, aligned_waveform, int(runtime["sample_rate"]))

            route_rows = []
            for route in HANDOFF_DECODE_ROUTES:
                route_waveform = reconstruct_waveform_from_frames(
                    waveform_frames=waveform_frames,
                    frame_length=int(runtime["frame_length"]),
                    hop_length=int(runtime["hop_length"]),
                    frame_gains=predicted_activity if bool(route["use_predicted_activity_gate"]) else None,
                    frame_gain_floor=float(predicted_activity_gate_floor),
                    frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                    frame_gain_apply_mode=str(route["predicted_activity_gate_apply_mode"]),
                ).detach().cpu().to(torch.float32)
                route_audio_path = output_dir / f"{record_slug}__{str(route['label'])}.wav"
                write_waveform_int16(route_audio_path, route_waveform, int(runtime["sample_rate"]))
                assessment = assess_stage5_decoded_buzz_reject(
                    decoded_waveform=route_waveform,
                    aligned_target=aligned_waveform,
                    predicted_activity=predicted_activity,
                    sample_rate=int(runtime["sample_rate"]),
                    frame_length=int(runtime["frame_length"]),
                    hop_length=int(runtime["hop_length"]),
                )
                route_rows.append(
                    {
                        "label": str(route["label"]),
                        "description": str(route["description"]),
                        "predicted_activity_gate_apply_mode": str(route["predicted_activity_gate_apply_mode"]),
                        "use_predicted_activity_gate": bool(route["use_predicted_activity_gate"]),
                        "audio_path": route_audio_path.as_posix(),
                        "buzz_reject_assessment": assessment,
                    }
                )

            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "aligned_target_audio_path": aligned_target_audio_path.as_posix(),
                    "stage_metrics": stage_metrics,
                    "routes": route_rows,
                }
            )

    handoff_stage_aggregates = build_handoff_stage_aggregates(per_record_rows)
    route_aggregates = build_handoff_route_aggregates(per_record_rows)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if checkpoint_selection_path is None else resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "decode_runtime": {
            "device": str(resolved_device),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "decoder_branch_mean_mix_alpha": float(decoder_branch_mean_mix_alpha),
            "fusion_mode": str(getattr(model, "fusion_mode", "plain")),
            "waveform_decoder_mode": str(getattr(model, "waveform_decoder_mode", "unknown")),
            "use_decoder_branch_condition_adapter": bool(
                getattr(model, "use_decoder_branch_condition_adapter", False)
            ),
            "use_residual_shape_branch_condition_adapter": bool(
                getattr(model, "use_residual_shape_branch_condition_adapter", False)
            ),
            "residual_shape_branch_condition_scale": float(
                getattr(model, "residual_shape_branch_condition_scale", 1.0)
            ),
            "residual_shape_branch_condition_mode": str(
                getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")
            ),
        },
        "handoff_stage_aggregates": handoff_stage_aggregates,
        "route_aggregates": route_aggregates,
        "diagnosis": diagnose_waveform_handoff(
            handoff_stage_aggregates=handoff_stage_aggregates,
            route_aggregates=route_aggregates,
        ),
        "records": per_record_rows,
        "notes": [
            "This probe keeps weights fixed and only decomposes the heard Stage5 path into decoder_hidden, waveform_frame_logits, waveform_frames, and three waveform reconstruction routes.",
            "decoded_no_gate tests whether buzz already exists before predicted activity gating.",
            "decoded_pre_ola_gate and decoded_post_ola_gate let us compare whether the current export-side gate semantics materially worsen the failure.",
        ],
    }
    json_path = output_dir / "stage5_waveform_handoff_probe.json"
    md_path = output_dir / "stage5_waveform_handoff_probe.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_waveform_handoff_probe_markdown(summary), encoding="utf-8")


def sanitize_record_id(record_id: str) -> str:
    return str(record_id).replace("::", "__").replace("/", "_").replace("\\", "_")


def summarize_handoff_stage_metrics(
    *,
    periodic_hidden: torch.Tensor | None = None,
    noise_hidden: torch.Tensor | None = None,
    branch_mean_hidden: torch.Tensor | None = None,
    fused_hidden: torch.Tensor | None = None,
    waveform_decoder_base_logits: torch.Tensor | None = None,
    waveform_residual_shape_delta: torch.Tensor | None = None,
    decoder_hidden: torch.Tensor,
    waveform_frame_logits: torch.Tensor,
    waveform_frames: torch.Tensor,
) -> dict[str, float]:
    metrics = {}
    if periodic_hidden is not None:
        metrics.update(prefix_metrics("periodic_hidden", summarize_sequence_metrics(periodic_hidden)))
    if noise_hidden is not None:
        metrics.update(prefix_metrics("noise_hidden", summarize_sequence_metrics(noise_hidden)))
    if branch_mean_hidden is not None:
        metrics.update(prefix_metrics("branch_mean_hidden", summarize_sequence_metrics(branch_mean_hidden)))
    if fused_hidden is not None:
        metrics.update(prefix_metrics("fused_hidden", summarize_sequence_metrics(fused_hidden)))
    if waveform_decoder_base_logits is not None:
        metrics.update(
            prefix_metrics(
                "waveform_decoder_base_logits",
                summarize_sequence_metrics(waveform_decoder_base_logits),
            )
        )
    if waveform_residual_shape_delta is not None:
        metrics.update(
            prefix_metrics(
                "waveform_residual_shape_delta",
                summarize_sequence_metrics(waveform_residual_shape_delta),
            )
        )
    metrics.update(prefix_metrics("decoder_hidden", summarize_sequence_metrics(decoder_hidden)))
    metrics.update(prefix_metrics("waveform_frame_logits", summarize_sequence_metrics(waveform_frame_logits)))
    metrics.update(prefix_metrics("waveform_frames", summarize_sequence_metrics(waveform_frames)))
    logits_abs = waveform_frame_logits.abs()
    frames_abs = waveform_frames.abs()
    metrics["waveform_frame_logits_fraction_abs_ge_1"] = round(float((logits_abs >= 1.0).float().mean().item()), 6)
    metrics["waveform_frame_logits_fraction_abs_ge_2"] = round(float((logits_abs >= 2.0).float().mean().item()), 6)
    metrics["waveform_frame_logits_fraction_abs_ge_3"] = round(float((logits_abs >= 3.0).float().mean().item()), 6)
    metrics["waveform_frames_fraction_abs_ge_095"] = round(float((frames_abs >= 0.95).float().mean().item()), 6)
    metrics["waveform_frames_fraction_abs_ge_099"] = round(float((frames_abs >= 0.99).float().mean().item()), 6)
    metrics["logits_to_frames_template_cosine_gap"] = round(
        float(metrics["waveform_frames_template_cosine_mean"])
        - float(metrics["waveform_frame_logits_template_cosine_mean"]),
        6,
    )
    metrics["logits_to_frames_adjacent_cosine_gap"] = round(
        float(metrics["waveform_frames_adjacent_cosine_mean"])
        - float(metrics["waveform_frame_logits_adjacent_cosine_mean"]),
        6,
    )
    if branch_mean_hidden is not None and fused_hidden is not None:
        metrics["branch_mean_to_fused_template_cosine_gap"] = round(
            float(metrics["fused_hidden_template_cosine_mean"])
            - float(metrics["branch_mean_hidden_template_cosine_mean"]),
            6,
        )
        metrics["branch_mean_to_fused_adjacent_cosine_gap"] = round(
            float(metrics["fused_hidden_adjacent_cosine_mean"])
            - float(metrics["branch_mean_hidden_adjacent_cosine_mean"]),
            6,
        )
    if fused_hidden is not None:
        metrics["fused_to_decoder_template_cosine_gap"] = round(
            float(metrics["decoder_hidden_template_cosine_mean"])
            - float(metrics["fused_hidden_template_cosine_mean"]),
            6,
        )
        metrics["fused_to_decoder_adjacent_cosine_gap"] = round(
            float(metrics["decoder_hidden_adjacent_cosine_mean"])
            - float(metrics["fused_hidden_adjacent_cosine_mean"]),
            6,
        )
    metrics["decoder_to_logits_template_cosine_gap"] = round(
        float(metrics["waveform_frame_logits_template_cosine_mean"])
        - float(metrics["decoder_hidden_template_cosine_mean"]),
        6,
    )
    metrics["decoder_to_logits_adjacent_cosine_gap"] = round(
        float(metrics["waveform_frame_logits_adjacent_cosine_mean"])
        - float(metrics["decoder_hidden_adjacent_cosine_mean"]),
        6,
    )
    return metrics


def summarize_sequence_metrics(sequence: torch.Tensor) -> dict[str, float]:
    base = summarize_frame_sequence_metrics(sequence.detach().cpu().to(torch.float32))
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    temporal_delta = sequence_cpu.new_zeros((0,), dtype=torch.float32)
    if int(sequence_cpu.shape[0]) > 1:
        temporal_delta = (sequence_cpu[1:] - sequence_cpu[:-1]).abs()
    base.update(
        {
            "sequence_std": round(float(sequence_cpu.std(unbiased=False).item()), 6),
            "sequence_abs_mean": round(float(sequence_cpu.abs().mean().item()), 6),
            "frame_delta_abs_mean": round(
                0.0 if int(temporal_delta.numel()) <= 0 else float(temporal_delta.mean().item()),
                6,
            ),
        }
    )
    return base


def prefix_metrics(prefix: str, metrics: dict[str, float]) -> dict[str, float]:
    return {f"{prefix}_{key}": float(value) for key, value in metrics.items()}


def build_handoff_stage_aggregates(per_record_rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    metric_map: dict[str, list[float]] = {}
    for record_row in per_record_rows:
        for key, value in dict(record_row["stage_metrics"]).items():
            metric_map.setdefault(str(key), []).append(float(value))
    return {key: summarize_scalar_values(values) for key, values in sorted(metric_map.items())}


def build_handoff_route_aggregates(per_record_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    route_map: dict[str, dict[str, object]] = {}
    for record_row in per_record_rows:
        for route_row in list(record_row["routes"]):
            label = str(route_row["label"])
            assessment = dict(route_row["buzz_reject_assessment"])
            metrics = flatten_assessment_metrics(assessment)
            bucket = route_map.setdefault(
                label,
                {
                    "label": label,
                    "description": str(route_row["description"]),
                    "record_count": 0,
                    "auto_reject_count": 0,
                    "metrics": {},
                },
            )
            bucket["record_count"] = int(bucket["record_count"]) + 1
            if bool(assessment.get("auto_reject", False)):
                bucket["auto_reject_count"] = int(bucket["auto_reject_count"]) + 1
            for key, value in metrics.items():
                bucket["metrics"].setdefault(key, []).append(float(value))
    aggregates = []
    order = {item["label"]: index for index, item in enumerate(HANDOFF_DECODE_ROUTES)}
    for label, payload in route_map.items():
        aggregates.append(
            {
                "label": label,
                "description": payload["description"],
                "record_count": int(payload["record_count"]),
                "auto_reject_count": int(payload["auto_reject_count"]),
                "all_records_auto_reject": bool(payload["record_count"]) and int(payload["auto_reject_count"])
                == int(payload["record_count"]),
                "metrics": {
                    key: summarize_scalar_values(values)
                    for key, values in sorted(dict(payload["metrics"]).items())
                },
            }
        )
    return sorted(aggregates, key=lambda item: order.get(item["label"], 999))


def flatten_assessment_metrics(assessment: dict[str, object]) -> dict[str, float]:
    metrics = dict(assessment.get("metrics", {}))
    return {
        "decoded_zero_crossing_rate": float(metrics.get("decoded_zero_crossing_rate", 0.0)),
        "decoded_frame_template_cosine_mean": float(metrics.get("decoded_frame_template_cosine_mean", 0.0)),
        "decoded_frame_adjacent_cosine_mean": float(metrics.get("decoded_frame_adjacent_cosine_mean", 0.0)),
        "decoded_frame_rms_to_aligned_frame_rms_corr": float(
            metrics.get("decoded_frame_rms_to_aligned_frame_rms_corr", 0.0)
        ),
        "predicted_activity_to_aligned_frame_rms_corr": float(
            metrics.get("predicted_activity_to_aligned_frame_rms_corr", 0.0)
        ),
        "spectral_centroid_gap_hz": float(metrics.get("spectral_centroid_gap_hz", 0.0)),
        "spectral_high_band_energy_ratio_gap": float(metrics.get("spectral_high_band_energy_ratio_gap", 0.0)),
    }


def diagnose_waveform_handoff(
    *,
    handoff_stage_aggregates: dict[str, dict[str, float]],
    route_aggregates: list[dict[str, object]],
) -> dict[str, object]:
    route_map = {str(item["label"]): item for item in route_aggregates}
    no_gate = dict(route_map.get("decoded_no_gate", {}))
    pre_gate = dict(route_map.get("decoded_pre_ola_gate", {}))
    post_gate = dict(route_map.get("decoded_post_ola_gate", {}))
    logits_template = float(
        handoff_stage_aggregates.get("waveform_frame_logits_template_cosine_mean", {}).get("mean", 0.0)
    )
    frames_template = float(
        handoff_stage_aggregates.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0)
    )
    logits_saturation = float(
        handoff_stage_aggregates.get("waveform_frame_logits_fraction_abs_ge_1", {}).get("mean", 0.0)
    )
    diagnosis = {
        "buzz_before_predicted_activity_gate": bool(no_gate.get("all_records_auto_reject", False)),
        "predicted_activity_gate_changes_auto_reject_status": bool(
            no_gate.get("all_records_auto_reject", False) != post_gate.get("all_records_auto_reject", False)
            or no_gate.get("all_records_auto_reject", False) != pre_gate.get("all_records_auto_reject", False)
        ),
        "tanh_is_main_new_collapse_site": abs(frames_template - logits_template) >= 0.01,
        "logits_show_heavy_saturation_pressure": logits_saturation >= 0.25,
    }
    if diagnosis["buzz_before_predicted_activity_gate"]:
        diagnosis["primary_localization"] = "buzz_present_by_waveform_frames_before_gate"
    elif bool(post_gate.get("all_records_auto_reject", False)):
        diagnosis["primary_localization"] = "buzz_mainfold_added_by_export_gate_route"
    else:
        diagnosis["primary_localization"] = "needs_more_localization"
    return diagnosis


def render_waveform_handoff_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 waveform handoff probe",
        "",
        f"- checkpoint: {summary.get('checkpoint_path')}",
        f"- dataset_index: {summary.get('dataset_index_path')}",
        f"- split: {summary.get('split_name')}",
        f"- sample_count: {summary.get('sample_count')}",
        f"- decode_runtime: {json.dumps(summary.get('decode_runtime'), ensure_ascii=False)}",
        f"- diagnosis: {json.dumps(summary.get('diagnosis'), ensure_ascii=False)}",
        "",
        "## Route aggregates",
    ]
    for route_row in list(summary.get("route_aggregates", [])):
        metrics = dict(route_row.get("metrics", {}))
        lines.append(
            "- "
            f"{route_row.get('label')}: auto_reject_count={route_row.get('auto_reject_count')}/"
            f"{route_row.get('record_count')}, "
            f"template={metrics.get('decoded_frame_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"rms_corr={metrics.get('decoded_frame_rms_to_aligned_frame_rms_corr', {}).get('mean', 0.0)}, "
            f"centroid_gap={metrics.get('spectral_centroid_gap_hz', {}).get('mean', 0.0)}, "
            f"high_band_gap={metrics.get('spectral_high_band_energy_ratio_gap', {}).get('mean', 0.0)}"
        )
    lines.extend(
        [
            "",
            "## Handoff stage aggregates",
            "- "
            f"logits_template={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frame_logits_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"frames_template={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"logits_abs_ge_1={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frame_logits_fraction_abs_ge_1', {}).get('mean', 0.0)}, "
            f"frames_abs_ge_095={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frames_fraction_abs_ge_095', {}).get('mean', 0.0)}",
            "",
            "## Per-record routes",
        ]
    )
    for record_row in list(summary.get("records", [])):
        lines.append(f"- {record_row.get('record_id')}")
        for route_row in list(record_row.get("routes", [])):
            assessment = dict(route_row.get("buzz_reject_assessment", {}))
            metrics = dict(assessment.get("metrics", {}))
            lines.append(
                "  "
                f"{route_row.get('label')}: status={assessment.get('status')} "
                f"template={metrics.get('decoded_frame_template_cosine_mean')} "
                f"rms_corr={metrics.get('decoded_frame_rms_to_aligned_frame_rms_corr')} "
                f"centroid_gap={metrics.get('spectral_centroid_gap_hz')} "
                f"high_band_gap={metrics.get('spectral_high_band_energy_ratio_gap')}"
            )
    lines.append("")
    return "\n".join(lines)
