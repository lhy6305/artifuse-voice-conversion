from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.managed_paths import compact_path_component, resolve_managed_output_dir
from v5vc.streaming_student.downstream_control_packet import (
    export_streaming_student_downstream_control_packet,
)


PACKET_AWARE_SELECTOR_VERSION = "stage3_packet_aware_checkpoint_selector_v1"


def select_streaming_student_packet_aware_checkpoint(
    checkpoint_paths: list[Path],
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    max_audio_sec: float | None,
) -> None:
    run_started_at = datetime.now()
    run_started_perf = perf_counter()
    requested_output_dir = output_dir.resolve()
    output_dir = resolve_managed_output_dir(
        requested_output_dir,
        default_stem="ss_ckpt_sel_pkt",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_checkpoint_paths = [path.resolve() for path in checkpoint_paths]
    if not resolved_checkpoint_paths:
        raise ValueError("At least one checkpoint path is required.")

    packet_exports_dir = output_dir / "pkt_exp"
    packet_exports_dir.mkdir(parents=True, exist_ok=True)

    evaluations: list[dict[str, object]] = []
    for checkpoint_path in resolved_checkpoint_paths:
        payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        step = int(payload.get("step", 0))
        experiment_id = str(payload.get("experiment_id", checkpoint_path.stem))
        compact_experiment_id = compact_path_component(experiment_id, max_length=32)
        export_dir = packet_exports_dir / f"s{step:04d}_{compact_experiment_id}"
        packet_summary = export_streaming_student_downstream_control_packet(
            checkpoint_path=checkpoint_path,
            output_dir=export_dir,
            teacher_label_index_path=teacher_label_index_path,
            calibration_asset_path=calibration_asset_path,
            split_dir=split_dir,
            split_name=split_name,
            sample_count=sample_count,
            target_record_ids=target_record_ids,
            branch_label=experiment_id,
            max_audio_sec=max_audio_sec,
        )
        evaluations.append(
            build_packet_evaluation(
                checkpoint_path=checkpoint_path,
                step=step,
                experiment_id=experiment_id,
                packet_export_dir=export_dir,
                packet_summary=packet_summary,
            )
        )

    ranked = rank_packet_evaluations(evaluations)
    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "selector_version": PACKET_AWARE_SELECTOR_VERSION,
        "selection_objective": "packet_aware_downstream_screen",
        "requested_output_dir": requested_output_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "checkpoint_paths": [path.as_posix() for path in resolved_checkpoint_paths],
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "split_dir": None if split_dir is None else Path(split_dir).resolve().as_posix(),
        "split_name": str(split_name),
        "sample_count": int(sample_count),
        "target_record_ids": None if not target_record_ids else list(target_record_ids),
        "max_audio_sec": None if max_audio_sec is None else float(max_audio_sec),
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "selection_rule": (
            "packet_facing_lexicographic("
            "min_auto_reject_count,"
            " max_all_core_controls_ready_count,"
            " max_vuv_ready_count,"
            " max_f0_ready_count,"
            " max_aper_ready_count,"
            " max_energy_ready_count,"
            " min_avg_vuv_reference_mae,"
            " min_avg_aper_calibrated_reference_mae,"
            " min_avg_energy_stage5_norm_calibrated_reference_mae,"
            " max_avg_f0_proxy_reference_corr,"
            " min_avg_f0_calibrated_log2_mae,"
            " min_step"
            ")"
        ),
        "evaluations": evaluations,
        "ranking": ranked,
        "best_checkpoint_by_packet_screen": None if not ranked else ranked[0],
        "best_checkpoint": None if not ranked else ranked[0],
        "notes": [
            "This report ranks Stage3 checkpoints using downstream packet cheap-screen behavior rather than teacher-supervised validation only.",
            "The rule is packet-facing and negative-gate oriented: it can help choose the least-bad handoff candidate, but it does not prove Stage5 readiness.",
            "Use this selection together with validation summaries, not as a replacement for them.",
            "best_checkpoint is kept as a legacy alias for best_checkpoint_by_packet_screen.",
        ],
    }

    json_path = output_dir / "streaming_student_packet_checkpoint_selection.json"
    md_path = output_dir / "streaming_student_packet_checkpoint_selection.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_packet_evaluation(
    *,
    checkpoint_path: Path,
    step: int,
    experiment_id: str,
    packet_export_dir: Path,
    packet_summary: dict[str, object],
) -> dict[str, object]:
    readiness_summary = dict(packet_summary.get("named_control_readiness_summary", {}))
    records = list(packet_summary.get("records", []))
    return {
        "checkpoint_path": checkpoint_path.as_posix(),
        "step": int(step),
        "experiment_id": str(experiment_id),
        "packet_export_dir": packet_export_dir.as_posix(),
        "packet_summary_path": (packet_export_dir / "streaming_student_downstream_control_packet.json").as_posix(),
        "packet_ready_count": int(packet_summary.get("packet_ready_count", 0)),
        "named_control_readiness_summary": readiness_summary,
        "averages": build_packet_metric_averages(records),
        "record_metrics": [
            {
                "record_id": str(record.get("record_id")),
                "f0_proxy_reference_corr": record.get("f0_proxy_reference_corr"),
                "f0_calibrated_log2_mae": record.get("f0_calibrated_log2_mae"),
                "vuv_reference_mae": record.get("vuv_reference_mae"),
                "aper_calibrated_reference_mae": record.get("aper_calibrated_reference_mae"),
                "energy_stage5_norm_calibrated_reference_mae": record.get(
                    "energy_stage5_norm_calibrated_reference_mae"
                ),
                "named_control_readiness": record.get("named_control_readiness"),
            }
            for record in records
        ],
    }


def build_packet_metric_averages(records: list[dict[str, object]]) -> dict[str, float | None]:
    return {
        "avg_f0_proxy_reference_corr": average_numeric_metric(records, "f0_proxy_reference_corr"),
        "avg_f0_calibrated_log2_mae": average_numeric_metric(records, "f0_calibrated_log2_mae"),
        "avg_vuv_reference_mae": average_numeric_metric(records, "vuv_reference_mae"),
        "avg_aper_calibrated_reference_mae": average_numeric_metric(
            records, "aper_calibrated_reference_mae"
        ),
        "avg_energy_stage5_norm_calibrated_reference_mae": average_numeric_metric(
            records, "energy_stage5_norm_calibrated_reference_mae"
        ),
    }


def average_numeric_metric(records: list[dict[str, object]], key: str) -> float | None:
    values: list[float] = []
    for record in records:
        value = record.get(key)
        if value is None:
            continue
        values.append(float(value))
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def rank_packet_evaluations(evaluations: list[dict[str, object]]) -> list[dict[str, object]]:
    ranked_rows: list[dict[str, object]] = []
    for payload in evaluations:
        readiness_summary = dict(payload.get("named_control_readiness_summary", {}))
        averages = dict(payload.get("averages", {}))
        ranked_rows.append(
            {
                "checkpoint_path": str(payload["checkpoint_path"]),
                "step": int(payload["step"]),
                "experiment_id": str(payload["experiment_id"]),
                "packet_export_dir": str(payload["packet_export_dir"]),
                "auto_reject_count": int(readiness_summary.get("auto_reject_count", 0)),
                "all_core_controls_ready_count": int(
                    readiness_summary.get("all_core_controls_ready_count", 0)
                ),
                "vuv_ready_count": int(readiness_summary.get("vuv_ready_count", 0)),
                "f0_ready_count": int(readiness_summary.get("f0_ready_count", 0)),
                "aper_ready_count": int(readiness_summary.get("aper_ready_count", 0)),
                "energy_ready_count": int(readiness_summary.get("energy_ready_count", 0)),
                "avg_vuv_reference_mae": averages.get("avg_vuv_reference_mae"),
                "avg_aper_calibrated_reference_mae": averages.get(
                    "avg_aper_calibrated_reference_mae"
                ),
                "avg_energy_stage5_norm_calibrated_reference_mae": averages.get(
                    "avg_energy_stage5_norm_calibrated_reference_mae"
                ),
                "avg_f0_proxy_reference_corr": averages.get("avg_f0_proxy_reference_corr"),
                "avg_f0_calibrated_log2_mae": averages.get("avg_f0_calibrated_log2_mae"),
            }
        )
    ranked_rows.sort(
        key=lambda item: (
            int(item["auto_reject_count"]),
            -int(item["all_core_controls_ready_count"]),
            -int(item["vuv_ready_count"]),
            -int(item["f0_ready_count"]),
            -int(item["aper_ready_count"]),
            -int(item["energy_ready_count"]),
            float("inf")
            if item["avg_vuv_reference_mae"] is None
            else float(item["avg_vuv_reference_mae"]),
            float("inf")
            if item["avg_aper_calibrated_reference_mae"] is None
            else float(item["avg_aper_calibrated_reference_mae"]),
            float("inf")
            if item["avg_energy_stage5_norm_calibrated_reference_mae"] is None
            else float(item["avg_energy_stage5_norm_calibrated_reference_mae"]),
            float("inf")
            if item["avg_f0_proxy_reference_corr"] is None
            else -float(item["avg_f0_proxy_reference_corr"]),
            float("inf")
            if item["avg_f0_calibrated_log2_mae"] is None
            else float(item["avg_f0_calibrated_log2_mae"]),
            int(item["step"]),
        )
    )
    return ranked_rows


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 Streaming Student Packet-Aware Checkpoint Selection",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- selector_version: {summary['selector_version']}",
        f"- selection_objective: {summary['selection_objective']}",
        f"- checkpoint_paths: {summary['checkpoint_paths']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- target_record_ids: {summary['target_record_ids']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- selection_rule: {summary['selection_rule']}",
        f"- best_checkpoint_by_packet_screen: {json.dumps(summary['best_checkpoint_by_packet_screen'], ensure_ascii=False)}",
        "",
        "## Ranking",
    ]
    for row in summary["ranking"]:
        lines.append(
            f"- step={row['step']} auto_reject_count={row['auto_reject_count']} "
            f"vuv_ready_count={row['vuv_ready_count']} f0_ready_count={row['f0_ready_count']} "
            f"aper_ready_count={row['aper_ready_count']} energy_ready_count={row['energy_ready_count']} "
            f"avg_vuv_reference_mae={row['avg_vuv_reference_mae']} "
            f"avg_aper_calibrated_reference_mae={row['avg_aper_calibrated_reference_mae']} "
            f"avg_energy_stage5_norm_calibrated_reference_mae={row['avg_energy_stage5_norm_calibrated_reference_mae']} "
            f"avg_f0_proxy_reference_corr={row['avg_f0_proxy_reference_corr']} "
            f"avg_f0_calibrated_log2_mae={row['avg_f0_calibrated_log2_mae']} "
            f"checkpoint_path={row['checkpoint_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
