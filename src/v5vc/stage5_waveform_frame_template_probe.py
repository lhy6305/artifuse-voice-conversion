from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory
from v5vc.nores_vocoder_audio_export import (
    AUTO_REJECT_ADJACENT_COSINE_MEAN,
    AUTO_REJECT_TEMPLATE_COSINE_MEAN,
    AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED,
    build_model_from_checkpoint,
    summarize_frame_sequence_metrics,
)
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
)
from v5vc.stage5_source_filter_probe import sanitize_record_id
from v5vc.stage5_speech_emergence_probe import frame_waveform_sequence
from v5vc.stage5_vuv_path_probe import summarize_vuv_conditioned_frame_sequence
from v5vc.stage5_waveform_decoder_structure_probe import build_voicing_conditioning_bundle
from v5vc.target_format_recovery import load_waveform_float


def analyze_stage5_nores_waveform_frame_template_collapse_review(
    *,
    output_dir: Path,
    review_bundle_path: Path,
    audio_export_manifest_paths: list[Path],
    high_band_hz: float,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    review_bundle = json.loads(review_bundle_path.resolve().read_text(encoding="utf-8"))
    review_records = list(review_bundle.get("records", []))
    if not review_records:
        raise ValueError("Review bundle contains no records.")

    manifest_payloads = load_export_manifest_payloads(audio_export_manifest_paths)
    export_routes_by_record = build_export_routes_by_record(manifest_payloads)
    model_cache: dict[str, torch.nn.Module] = {}
    per_record_rows: list[dict[str, object]] = []

    for review_record in review_records:
        record_id = str(review_record.get("record_id", "")).strip()
        if not record_id:
            continue
        route_entries = export_routes_by_record.get(record_id)
        if not route_entries:
            raise KeyError(f"Unable to resolve export-manifest entries for review record: {record_id}")

        anchor_entry = route_entries[0]
        package_path = Path(str(anchor_entry["training_package_path"])).resolve()
        payload = load_training_package_payload(package_path)
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)
        checkpoint_path = Path(str(anchor_entry["checkpoint_path"])).resolve()
        model_key = checkpoint_path.as_posix()
        if model_key not in model_cache:
            checkpoint_payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            model = build_model_from_checkpoint(
                checkpoint_payload=checkpoint_payload,
                first_batch=batch,
                first_runtime=runtime,
            )
            model.eval()
            model_cache[model_key] = model
        model = model_cache[model_key]

        decoder_branch_mean_mix_alpha = float(anchor_entry["waveform_decode"].get("decoder_branch_mean_mix_alpha", 0.0))
        with torch.no_grad():
            outputs = model(
                periodic_branch_features=batch["periodic_branch_features"],
                noise_branch_features=batch["noise_branch_features"],
                decoder_branch_mean_mix_alpha=decoder_branch_mean_mix_alpha,
            )

        waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
        frame_count = int(waveform_frames.shape[0])
        if frame_count <= 0:
            raise ValueError(f"No waveform frames available for template-collapse review record: {record_id}")

        sample_rate = int(runtime["sample_rate"])
        frame_length = int(runtime["frame_length"])
        hop_length = int(runtime["hop_length"])
        aligned_waveform = batch["aligned_waveform"].detach().cpu().to(torch.float32)
        aligned_frames = frame_waveform_sequence(
            waveform=aligned_waveform,
            frame_length=frame_length,
            hop_length=hop_length,
            target_frame_count=frame_count,
        )
        conditioning = build_voicing_conditioning_bundle(
            frame_count=frame_count,
            vuv_target=batch.get("periodic_gate_target", batch.get("vuv_target")),
            voiced_proxy_target=batch.get("voiced_proxy_target"),
            aper_target=batch.get("aper_target"),
            aperiodicity_proxy_target=batch.get("aperiodicity_proxy_target"),
            energy_log_rms_norm_target=batch.get("energy_log_rms_norm_target"),
            energy_control_target=batch.get("energy_control_target"),
        )
        if conditioning is None:
            raise ValueError(f"Unable to derive vuv conditioning for template-collapse review record: {record_id}")

        aligned_frame_metrics = summarize_frame_sequence_metrics(aligned_frames)
        waveform_frame_metrics = summarize_frame_sequence_metrics(waveform_frames)
        aligned_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=aligned_frames,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )
        waveform_frames_vuv_summary = summarize_vuv_conditioned_frame_sequence(
            analysis_frames=waveform_frames,
            conditioning=conditioning,
            sample_rate=sample_rate,
            high_band_hz=high_band_hz,
        )

        route_rows: list[dict[str, object]] = []
        for route_entry in route_entries:
            decoded_path = Path(str(route_entry["decoded_audio_path"])).resolve()
            decoded_waveform, decoded_sample_rate = load_waveform_float(decoded_path)
            if int(decoded_sample_rate) != sample_rate:
                raise ValueError(
                    f"Decoded waveform sample rate mismatch for {decoded_path}: "
                    f"{decoded_sample_rate} vs expected {sample_rate}"
                )
            decoded_frames = frame_waveform_sequence(
                waveform=decoded_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                target_frame_count=frame_count,
            )
            decoded_frame_metrics = summarize_frame_sequence_metrics(decoded_frames)
            decoded_vuv_summary = summarize_vuv_conditioned_frame_sequence(
                analysis_frames=decoded_frames,
                conditioning=conditioning,
                sample_rate=sample_rate,
                high_band_hz=high_band_hz,
            )
            buzz_assessment = dict(route_entry.get("buzz_reject_assessment", {}))
            route_rows.append(
                {
                    "route_label": str(route_entry["route_label"]),
                    "audio_export_manifest_path": str(route_entry["audio_export_manifest_path"]),
                    "branch_label": str(route_entry.get("branch_label", "")),
                    "reconstruction_contract_mode": str(
                        dict(route_entry.get("waveform_decode", {})).get(
                            "reconstruction_contract_mode",
                            "hann_window_sum_norm",
                        )
                    ),
                    "use_predicted_activity_gate": bool(
                        dict(route_entry.get("waveform_decode", {})).get("use_predicted_activity_gate", True)
                    ),
                    "decoded_audio_path": decoded_path.as_posix(),
                    "decoded_frame_metrics": decoded_frame_metrics,
                    "decoded_vuv_summary": decoded_vuv_summary,
                    "template_cosine_gap_vs_waveform_frames": round(
                        float(decoded_frame_metrics["template_cosine_mean"])
                        - float(waveform_frame_metrics["template_cosine_mean"]),
                        6,
                    ),
                    "adjacent_cosine_gap_vs_waveform_frames": round(
                        float(decoded_frame_metrics["adjacent_cosine_mean"])
                        - float(waveform_frame_metrics["adjacent_cosine_mean"]),
                        6,
                    ),
                    "decoded_vuv_high_band_gap_vs_waveform_frames": round(
                        float(decoded_vuv_summary["unvoiced_minus_voiced_high_band_ratio"])
                        - float(waveform_frames_vuv_summary["unvoiced_minus_voiced_high_band_ratio"]),
                        6,
                    ),
                    "buzz_reject_assessment": buzz_assessment,
                }
            )

        per_record_rows.append(
            {
                "record_id": record_id,
                "review_status": str(review_record.get("status", "unknown")),
                "split_name": str(review_record.get("split_name", anchor_entry.get("split_name", ""))),
                "review_bundle_path": review_bundle_path.resolve().as_posix(),
                "checkpoint_path": checkpoint_path.as_posix(),
                "training_package_path": package_path.as_posix(),
                "aligned_frame_metrics": aligned_frame_metrics,
                "waveform_frames_metrics": waveform_frame_metrics,
                "aligned_vuv_summary": aligned_vuv_summary,
                "waveform_frames_vuv_summary": waveform_frames_vuv_summary,
                "routes": route_rows,
                "diagnosis": diagnose_record_template_collapse(
                    aligned_frame_metrics=aligned_frame_metrics,
                    waveform_frame_metrics=waveform_frame_metrics,
                    waveform_frames_vuv_summary=waveform_frames_vuv_summary,
                    route_rows=route_rows,
                ),
            }
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_type": "stage5_waveform_frame_template_collapse_review_v1",
        "review_bundle_path": review_bundle_path.resolve().as_posix(),
        "audio_export_manifest_paths": [path.resolve().as_posix() for path in audio_export_manifest_paths],
        "record_count": len(per_record_rows),
        "review_bundle_label": str(review_bundle.get("bundle_label", "")),
        "source_family": str(review_bundle.get("source_family", "")),
        "high_band_hz": float(high_band_hz),
        "stage_aggregates": build_stage_aggregates(per_record_rows),
        "route_aggregates": build_route_aggregates(per_record_rows, manifest_payloads),
        "diagnosis": diagnose_template_collapse_review(
            stage_aggregates=build_stage_aggregates(per_record_rows),
            route_aggregates=build_route_aggregates(per_record_rows, manifest_payloads),
        ),
        "records": per_record_rows,
        "notes": [
            "This review asks whether rectangular export-side success on vuv metrics simply exposes a pre-existing waveform_frames template-collapse that Hann had partially masked.",
            "waveform_frames metrics are measured directly on the model-produced frame sequence before any frame-to-waveform reconstruction contract is applied.",
            "decoded route metrics come from the real exported decoded.wav assets referenced by each manifest, so route comparisons stay on the actual heard path.",
        ],
    }
    json_path = output_dir / "stage5_waveform_frame_template_collapse_review.json"
    md_path = output_dir / "stage5_waveform_frame_template_collapse_review.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(render_template_collapse_review_markdown(summary), encoding="utf-8", newline="\n")


def load_export_manifest_payloads(audio_export_manifest_paths: list[Path]) -> list[dict[str, object]]:
    payloads = []
    route_labels_seen: set[str] = set()
    for manifest_path in audio_export_manifest_paths:
        resolved_manifest_path = manifest_path.resolve()
        payload = json.loads(resolved_manifest_path.read_text(encoding="utf-8"))
        route_label = infer_manifest_route_label(resolved_manifest_path, payload)
        deduped_route_label = route_label
        suffix = 2
        while deduped_route_label in route_labels_seen:
            deduped_route_label = f"{route_label}__{suffix}"
            suffix += 1
        route_labels_seen.add(deduped_route_label)
        payloads.append(
            {
                "manifest_path": resolved_manifest_path,
                "route_label": deduped_route_label,
                "payload": payload,
            }
        )
    return payloads


def infer_manifest_route_label(manifest_path: Path, payload: dict[str, object]) -> str:
    waveform_decode = dict(payload.get("waveform_decode", {}))
    contract_mode = str(waveform_decode.get("reconstruction_contract_mode", "hann_window_sum_norm"))
    gate_label = "gateon" if bool(waveform_decode.get("use_predicted_activity_gate", True)) else "gateoff"
    return f"{contract_mode}__{gate_label}"


def build_export_routes_by_record(manifest_payloads: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    record_map: dict[str, list[dict[str, object]]] = {}
    for manifest_info in manifest_payloads:
        manifest_path = Path(str(manifest_info["manifest_path"]))
        route_label = str(manifest_info["route_label"])
        payload = dict(manifest_info["payload"])
        for record in list(payload.get("records", [])):
            record_id = str(record.get("record_id", "")).strip()
            if not record_id:
                continue
            record_map.setdefault(record_id, []).append(
                {
                    **dict(record),
                    "route_label": route_label,
                    "audio_export_manifest_path": manifest_path.as_posix(),
                    "checkpoint_path": str(payload.get("checkpoint_path", "")),
                    "dataset_index_path": str(payload.get("dataset_index_path", "")),
                    "branch_label": str(payload.get("branch_label", "")),
                    "waveform_decode": dict(payload.get("waveform_decode", {})),
                }
            )
    return record_map


def build_stage_aggregates(per_record_rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    metrics: dict[str, list[float]] = {}
    for row in per_record_rows:
        aligned_frame_metrics = dict(row["aligned_frame_metrics"])
        waveform_frames_metrics = dict(row["waveform_frames_metrics"])
        aligned_vuv_summary = dict(row["aligned_vuv_summary"])
        waveform_frames_vuv_summary = dict(row["waveform_frames_vuv_summary"])
        append_metric(metrics, "aligned_frame_template_cosine_mean", aligned_frame_metrics["template_cosine_mean"])
        append_metric(metrics, "aligned_frame_adjacent_cosine_mean", aligned_frame_metrics["adjacent_cosine_mean"])
        append_metric(metrics, "waveform_frames_template_cosine_mean", waveform_frames_metrics["template_cosine_mean"])
        append_metric(metrics, "waveform_frames_adjacent_cosine_mean", waveform_frames_metrics["adjacent_cosine_mean"])
        append_metric(metrics, "waveform_frames_template_cosine_gap_vs_aligned", round(
            float(waveform_frames_metrics["template_cosine_mean"]) - float(aligned_frame_metrics["template_cosine_mean"]),
            6,
        ))
        append_metric(metrics, "waveform_frames_adjacent_cosine_gap_vs_aligned", round(
            float(waveform_frames_metrics["adjacent_cosine_mean"]) - float(aligned_frame_metrics["adjacent_cosine_mean"]),
            6,
        ))
        append_metric(
            metrics,
            "aligned_vuv_high_band_ratio_gap",
            aligned_vuv_summary["unvoiced_minus_voiced_high_band_ratio"],
        )
        append_metric(
            metrics,
            "waveform_frames_vuv_high_band_ratio_gap",
            waveform_frames_vuv_summary["unvoiced_minus_voiced_high_band_ratio"],
        )
    return {key: summarize_scalar_values(values) for key, values in sorted(metrics.items())}


def build_route_aggregates(
    per_record_rows: list[dict[str, object]],
    manifest_payloads: list[dict[str, object]],
) -> list[dict[str, object]]:
    route_map: dict[str, dict[str, object]] = {}
    order = {str(item["route_label"]): index for index, item in enumerate(manifest_payloads)}
    for row in per_record_rows:
        for route_row in list(row["routes"]):
            route_label = str(route_row["route_label"])
            bucket = route_map.setdefault(
                route_label,
                {
                    "route_label": route_label,
                    "branch_label": str(route_row.get("branch_label", "")),
                    "reconstruction_contract_mode": str(route_row.get("reconstruction_contract_mode", "")),
                    "use_predicted_activity_gate": bool(route_row.get("use_predicted_activity_gate", True)),
                    "record_count": 0,
                    "auto_reject_count": 0,
                    "decoded_vuv_high_band_ratio_nonpositive_count": 0,
                    "metrics": {},
                },
            )
            metrics_bucket = dict(bucket["metrics"])
            bucket["record_count"] = int(bucket["record_count"]) + 1
            assessment = dict(route_row.get("buzz_reject_assessment", {}))
            if bool(assessment.get("auto_reject", False)):
                bucket["auto_reject_count"] = int(bucket["auto_reject_count"]) + 1
            decoded_vuv_summary = dict(route_row.get("decoded_vuv_summary", {}))
            if float(decoded_vuv_summary.get("unvoiced_minus_voiced_high_band_ratio", 0.0)) <= 0.0:
                bucket["decoded_vuv_high_band_ratio_nonpositive_count"] = (
                    int(bucket["decoded_vuv_high_band_ratio_nonpositive_count"]) + 1
                )
            append_metric(
                metrics_bucket,
                "decoded_frame_template_cosine_mean",
                dict(route_row["decoded_frame_metrics"])["template_cosine_mean"],
            )
            append_metric(
                metrics_bucket,
                "decoded_frame_adjacent_cosine_mean",
                dict(route_row["decoded_frame_metrics"])["adjacent_cosine_mean"],
            )
            append_metric(
                metrics_bucket,
                "template_cosine_gap_vs_waveform_frames",
                route_row["template_cosine_gap_vs_waveform_frames"],
            )
            append_metric(
                metrics_bucket,
                "adjacent_cosine_gap_vs_waveform_frames",
                route_row["adjacent_cosine_gap_vs_waveform_frames"],
            )
            append_metric(
                metrics_bucket,
                "decoded_vuv_high_band_ratio_gap",
                decoded_vuv_summary["unvoiced_minus_voiced_high_band_ratio"],
            )
            append_metric(
                metrics_bucket,
                "decoded_vuv_high_band_gap_vs_waveform_frames",
                route_row["decoded_vuv_high_band_gap_vs_waveform_frames"],
            )
            bucket["metrics"] = metrics_bucket
    aggregates = []
    for route_label, payload in route_map.items():
        metrics = dict(payload["metrics"])
        aggregates.append(
            {
                "route_label": route_label,
                "branch_label": payload["branch_label"],
                "reconstruction_contract_mode": payload["reconstruction_contract_mode"],
                "use_predicted_activity_gate": payload["use_predicted_activity_gate"],
                "record_count": int(payload["record_count"]),
                "auto_reject_count": int(payload["auto_reject_count"]),
                "review_required_count": max(
                    0,
                    int(payload["record_count"]) - int(payload["auto_reject_count"]),
                ),
                "all_records_auto_reject": bool(payload["record_count"])
                and int(payload["auto_reject_count"]) == int(payload["record_count"]),
                "decoded_vuv_high_band_ratio_nonpositive_count": int(
                    payload["decoded_vuv_high_band_ratio_nonpositive_count"]
                ),
                "metrics": {key: summarize_scalar_values(values) for key, values in sorted(metrics.items())},
            }
        )
    return sorted(aggregates, key=lambda item: order.get(str(item["route_label"]), 999))


def append_metric(metric_map: dict[str, list[float]], key: str, value: float) -> None:
    metric_map.setdefault(str(key), []).append(float(value))


def summarize_scalar_values(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}
    return {
        "count": float(len(values)),
        "mean": round(sum(values) / len(values), 6),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
    }


def diagnose_record_template_collapse(
    *,
    aligned_frame_metrics: dict[str, float],
    waveform_frame_metrics: dict[str, float],
    waveform_frames_vuv_summary: dict[str, float],
    route_rows: list[dict[str, object]],
) -> dict[str, object]:
    waveform_template = float(waveform_frame_metrics["template_cosine_mean"])
    waveform_adjacent = float(waveform_frame_metrics["adjacent_cosine_mean"])
    aligned_template = float(aligned_frame_metrics["template_cosine_mean"])
    diagnosis = {
        "waveform_frames_meet_template_collapse_threshold": bool(
            waveform_template >= AUTO_REJECT_TEMPLATE_COSINE_MEAN
            and waveform_adjacent >= AUTO_REJECT_ADJACENT_COSINE_MEAN
            and (waveform_template - aligned_template) >= AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED
        ),
        "waveform_frames_vuv_high_band_gap": round(
            float(waveform_frames_vuv_summary["unvoiced_minus_voiced_high_band_ratio"]),
            6,
        ),
    }
    rectangular_route = next(
        (
            route_row
            for route_row in route_rows
            if str(route_row.get("reconstruction_contract_mode", "")) == "rectangular_overlap_count_norm"
        ),
        None,
    )
    if rectangular_route is not None:
        diagnosis["rectangular_template_gap_vs_waveform_frames"] = float(
            rectangular_route["template_cosine_gap_vs_waveform_frames"]
        )
        diagnosis["rectangular_vuv_gap_vs_waveform_frames"] = float(
            rectangular_route["decoded_vuv_high_band_gap_vs_waveform_frames"]
        )
    diagnosis["primary_localization"] = (
        "waveform_frames_already_template_collapsed_before_reconstruction"
        if diagnosis["waveform_frames_meet_template_collapse_threshold"]
        else "needs_more_localization"
    )
    return diagnosis


def diagnose_template_collapse_review(
    *,
    stage_aggregates: dict[str, dict[str, float]],
    route_aggregates: list[dict[str, object]],
) -> dict[str, object]:
    waveform_template = float(stage_aggregates.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0))
    waveform_adjacent = float(stage_aggregates.get("waveform_frames_adjacent_cosine_mean", {}).get("mean", 0.0))
    waveform_template_gap = float(
        stage_aggregates.get("waveform_frames_template_cosine_gap_vs_aligned", {}).get("mean", 0.0)
    )
    waveform_vuv_gap = float(stage_aggregates.get("waveform_frames_vuv_high_band_ratio_gap", {}).get("mean", 0.0))
    route_map = {str(route["route_label"]): route for route in route_aggregates}
    rectangular_route = next(
        (
            route
            for route in route_aggregates
            if str(route.get("reconstruction_contract_mode", "")) == "rectangular_overlap_count_norm"
        ),
        {},
    )
    hann_route = next(
        (
            route
            for route in route_aggregates
            if str(route.get("reconstruction_contract_mode", "")) == "hann_window_sum_norm"
        ),
        {},
    )
    diagnosis = {
        "waveform_frames_meet_template_collapse_threshold": bool(
            waveform_template >= AUTO_REJECT_TEMPLATE_COSINE_MEAN
            and waveform_adjacent >= AUTO_REJECT_ADJACENT_COSINE_MEAN
            and waveform_template_gap >= AUTO_REJECT_TEMPLATE_GAP_VS_ALIGNED
        ),
        "waveform_frames_template_cosine_mean": round(waveform_template, 6),
        "waveform_frames_adjacent_cosine_mean": round(waveform_adjacent, 6),
        "waveform_frames_template_cosine_gap_vs_aligned": round(waveform_template_gap, 6),
        "waveform_frames_vuv_high_band_ratio_gap": round(waveform_vuv_gap, 6),
        "route_labels": sorted(route_map.keys()),
    }
    if rectangular_route:
        metrics = dict(rectangular_route.get("metrics", {}))
        diagnosis["rectangular_decoded_template_cosine_mean"] = round(
            float(metrics.get("decoded_frame_template_cosine_mean", {}).get("mean", 0.0)),
            6,
        )
        diagnosis["rectangular_template_gap_vs_waveform_frames"] = round(
            float(metrics.get("template_cosine_gap_vs_waveform_frames", {}).get("mean", 0.0)),
            6,
        )
        diagnosis["rectangular_decoded_vuv_high_band_ratio_gap"] = round(
            float(metrics.get("decoded_vuv_high_band_ratio_gap", {}).get("mean", 0.0)),
            6,
        )
    if hann_route:
        metrics = dict(hann_route.get("metrics", {}))
        diagnosis["hann_decoded_template_cosine_mean"] = round(
            float(metrics.get("decoded_frame_template_cosine_mean", {}).get("mean", 0.0)),
            6,
        )
        diagnosis["hann_template_gap_vs_waveform_frames"] = round(
            float(metrics.get("template_cosine_gap_vs_waveform_frames", {}).get("mean", 0.0)),
            6,
        )
        diagnosis["hann_decoded_vuv_high_band_ratio_gap"] = round(
            float(metrics.get("decoded_vuv_high_band_ratio_gap", {}).get("mean", 0.0)),
            6,
        )
    if diagnosis["waveform_frames_meet_template_collapse_threshold"]:
        diagnosis["primary_localization"] = "waveform_frames_already_template_collapsed_before_reconstruction"
    else:
        diagnosis["primary_localization"] = "needs_more_localization"
    return diagnosis


def render_template_collapse_review_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 waveform-frame template-collapse review",
        "",
        f"- review_bundle: {summary.get('review_bundle_path')}",
        f"- audio_export_manifests: {json.dumps(summary.get('audio_export_manifest_paths', []), ensure_ascii=False)}",
        f"- record_count: {summary.get('record_count')}",
        f"- high_band_hz: {summary.get('high_band_hz')}",
        f"- diagnosis: {json.dumps(summary.get('diagnosis', {}), ensure_ascii=False)}",
        "",
        "## Stage aggregates",
    ]
    stage_aggregates = dict(summary.get("stage_aggregates", {}))
    lines.append(
        "- "
        f"aligned_template={stage_aggregates.get('aligned_frame_template_cosine_mean', {}).get('mean', 0.0)}, "
        f"waveform_template={stage_aggregates.get('waveform_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
        f"waveform_adjacent={stage_aggregates.get('waveform_frames_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
        f"waveform_template_gap_vs_aligned={stage_aggregates.get('waveform_frames_template_cosine_gap_vs_aligned', {}).get('mean', 0.0)}, "
        f"waveform_vuv_high_band_gap={stage_aggregates.get('waveform_frames_vuv_high_band_ratio_gap', {}).get('mean', 0.0)}"
    )
    lines.extend(["", "## Route aggregates"])
    for route_row in list(summary.get("route_aggregates", [])):
        metrics = dict(route_row.get("metrics", {}))
        lines.append(
            "- "
            f"{route_row.get('route_label')}: auto_reject_count={route_row.get('auto_reject_count')}/"
            f"{route_row.get('record_count')}, "
            f"decoded_template={metrics.get('decoded_frame_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"template_gap_vs_waveform={metrics.get('template_cosine_gap_vs_waveform_frames', {}).get('mean', 0.0)}, "
            f"decoded_vuv_high_band_gap={metrics.get('decoded_vuv_high_band_ratio_gap', {}).get('mean', 0.0)}, "
            f"decoded_vuv_nonpositive_count={route_row.get('decoded_vuv_high_band_ratio_nonpositive_count')}"
        )
    lines.extend(["", "## Per-record"])
    for row in list(summary.get("records", [])):
        record_id = str(row.get("record_id", ""))
        lines.append(f"- {record_id}")
        lines.append(
            "  "
            f"waveform_template={dict(row.get('waveform_frames_metrics', {})).get('template_cosine_mean')}, "
            f"waveform_adjacent={dict(row.get('waveform_frames_metrics', {})).get('adjacent_cosine_mean')}, "
            f"waveform_vuv_high_band_gap={dict(row.get('waveform_frames_vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio')}"
        )
        for route_row in list(row.get("routes", [])):
            lines.append(
                "  "
                f"{route_row.get('route_label')}: template={dict(route_row.get('decoded_frame_metrics', {})).get('template_cosine_mean')} "
                f"template_gap_vs_waveform={route_row.get('template_cosine_gap_vs_waveform_frames')} "
                f"decoded_vuv_high_band_gap={dict(route_row.get('decoded_vuv_summary', {})).get('unvoiced_minus_voiced_high_band_ratio')} "
                f"buzz_status={dict(route_row.get('buzz_reject_assessment', {})).get('status')}"
            )
    lines.append("")
    return "\n".join(lines)
