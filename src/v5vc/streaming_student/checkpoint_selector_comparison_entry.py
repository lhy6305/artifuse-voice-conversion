from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

from v5vc.managed_paths import resolve_managed_output_dir, reset_managed_directory
from v5vc.streaming_student.checkpoint_selection_entry import (
    select_streaming_student_best_checkpoint,
)
from v5vc.streaming_student.packet_checkpoint_selection_entry import (
    select_streaming_student_packet_aware_checkpoint,
)


CHECKPOINT_SELECTOR_COMPARISON_VERSION = "stage3_checkpoint_selector_comparison_v1"


def compare_streaming_student_checkpoint_selectors(
    checkpoint_paths: list[Path],
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    packet_reference_checkpoint_path: Path | None,
    split_dir: Path | None,
    batch_size: int,
    include_special_eval: bool,
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
        default_stem="ss_ckpt_sel_cmp",
    )
    reset_managed_directory(output_dir)
    resolved_checkpoint_paths = [path.resolve() for path in checkpoint_paths]
    if not resolved_checkpoint_paths:
        raise ValueError("At least one checkpoint path is required.")
    resolved_packet_reference_checkpoint_path = (
        None if packet_reference_checkpoint_path is None else packet_reference_checkpoint_path.resolve()
    )
    if (
        resolved_packet_reference_checkpoint_path is not None
        and resolved_packet_reference_checkpoint_path not in resolved_checkpoint_paths
    ):
        raise ValueError("packet_reference_checkpoint_path must be one of the compared checkpoint paths.")

    posthoc_output_dir = output_dir / "posthoc"
    packet_output_dir = output_dir / "pkt"
    select_streaming_student_best_checkpoint(
        checkpoint_paths=resolved_checkpoint_paths,
        output_dir=posthoc_output_dir,
        teacher_label_index_path=teacher_label_index_path,
        calibration_asset_path=calibration_asset_path,
        split_dir=split_dir,
        batch_size=batch_size,
        include_special_eval=include_special_eval,
    )
    select_streaming_student_packet_aware_checkpoint(
        checkpoint_paths=resolved_checkpoint_paths,
        output_dir=packet_output_dir,
        teacher_label_index_path=teacher_label_index_path,
        calibration_asset_path=calibration_asset_path,
        split_dir=split_dir,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
        max_audio_sec=max_audio_sec,
    )

    posthoc_summary = json.loads(
        (posthoc_output_dir / "streaming_student_checkpoint_selection.json").read_text(encoding="utf-8")
    )
    packet_summary = json.loads(
        (packet_output_dir / "streaming_student_packet_checkpoint_selection.json").read_text(encoding="utf-8")
    )
    comparison = build_selector_comparison(
        checkpoint_paths=resolved_checkpoint_paths,
        posthoc_summary=posthoc_summary,
        packet_summary=packet_summary,
        packet_reference_checkpoint_path=resolved_packet_reference_checkpoint_path,
    )
    decision_summary = build_decision_summary(comparison)
    run_ended_at = datetime.now()
    duration_sec = perf_counter() - run_started_perf
    summary = {
        "generated_at": run_ended_at.isoformat(timespec="seconds"),
        "comparison_version": CHECKPOINT_SELECTOR_COMPARISON_VERSION,
        "requested_output_dir": requested_output_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "checkpoint_paths": [path.as_posix() for path in resolved_checkpoint_paths],
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "packet_reference_checkpoint_path": (
            None
            if resolved_packet_reference_checkpoint_path is None
            else resolved_packet_reference_checkpoint_path.as_posix()
        ),
        "split_dir": None if split_dir is None else Path(split_dir).resolve().as_posix(),
        "posthoc_teacher_loss": {
            "output_dir": posthoc_output_dir.as_posix(),
            "summary_path": (posthoc_output_dir / "streaming_student_checkpoint_selection.json").as_posix(),
            "selector_version": posthoc_summary.get("selector_version"),
            "selection_objective": posthoc_summary.get("selection_objective"),
            "selection_rule": posthoc_summary.get("selection_rule"),
            "include_special_eval": bool(posthoc_summary.get("include_special_eval", False)),
            "best_checkpoint": posthoc_summary.get("best_checkpoint_by_posthoc_teacher_loss", posthoc_summary.get("best_checkpoint")),
        },
        "packet_aware": {
            "output_dir": packet_output_dir.as_posix(),
            "summary_path": (packet_output_dir / "streaming_student_packet_checkpoint_selection.json").as_posix(),
            "selector_version": packet_summary.get("selector_version"),
            "selection_objective": packet_summary.get("selection_objective"),
            "selection_rule": packet_summary.get("selection_rule"),
            "split_name": packet_summary.get("split_name"),
            "sample_count": packet_summary.get("sample_count"),
            "target_record_ids": packet_summary.get("target_record_ids"),
            "max_audio_sec": packet_summary.get("max_audio_sec"),
            "best_checkpoint": packet_summary.get("best_checkpoint_by_packet_screen", packet_summary.get("best_checkpoint")),
        },
        "comparison": comparison,
        "decision_summary": decision_summary,
        "timing": {
            "started_at": run_started_at.isoformat(timespec="seconds"),
            "ended_at": run_ended_at.isoformat(timespec="seconds"),
            "duration_sec": round(duration_sec, 6),
        },
        "notes": [
            "This report runs both Stage3 selectors on the same checkpoint set and makes any disagreement explicit.",
            "The post-hoc teacher-loss selector and the packet-aware selector answer different questions and should not be collapsed into one universal best checkpoint.",
            "A selector disagreement is not automatically a bug; it can reflect different decision objectives.",
            "decision_summary separates teacher-loss reference choice from handoff-facing packet-screen choice and does not treat selector disagreement as a bug by default.",
        ],
    }

    (output_dir / "streaming_student_checkpoint_selector_comparison.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "streaming_student_checkpoint_selector_comparison.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_selector_comparison(
    *,
    checkpoint_paths: list[Path],
    posthoc_summary: dict[str, object],
    packet_summary: dict[str, object],
    packet_reference_checkpoint_path: Path | None,
) -> dict[str, object]:
    posthoc_ranking = list(posthoc_summary.get("ranking", []))
    packet_ranking = list(packet_summary.get("ranking", []))
    posthoc_positions = build_ranking_positions(posthoc_ranking)
    packet_positions = build_ranking_positions(packet_ranking)
    rows: list[dict[str, object]] = []
    for checkpoint_path in checkpoint_paths:
        checkpoint_key = checkpoint_path.as_posix()
        posthoc_row = next(
            (row for row in posthoc_ranking if str(row.get("checkpoint_path")) == checkpoint_key),
            None,
        )
        packet_row = next(
            (row for row in packet_ranking if str(row.get("checkpoint_path")) == checkpoint_key),
            None,
        )
        rows.append(
            {
                "checkpoint_path": checkpoint_key,
                "step": None
                if posthoc_row is None and packet_row is None
                else int(
                    (posthoc_row or packet_row or {}).get("step", 0)
                ),
                "posthoc_teacher_loss_rank": posthoc_positions.get(checkpoint_key),
                "packet_aware_rank": packet_positions.get(checkpoint_key),
                "rank_delta": compute_rank_delta(
                    posthoc_positions.get(checkpoint_key),
                    packet_positions.get(checkpoint_key),
                ),
                "posthoc_teacher_loss_total": None if posthoc_row is None else posthoc_row.get("target_validation_loss_total"),
                "posthoc_special_eval_loss_total": None if posthoc_row is None else posthoc_row.get("target_special_eval_loss_total"),
                "packet_auto_reject_count": None if packet_row is None else packet_row.get("auto_reject_count"),
                "packet_vuv_ready_count": None if packet_row is None else packet_row.get("vuv_ready_count"),
                "packet_f0_ready_count": None if packet_row is None else packet_row.get("f0_ready_count"),
                "packet_aper_ready_count": None if packet_row is None else packet_row.get("aper_ready_count"),
                "packet_energy_ready_count": None if packet_row is None else packet_row.get("energy_ready_count"),
                "packet_avg_vuv_reference_mae": None if packet_row is None else packet_row.get("avg_vuv_reference_mae"),
                "packet_avg_f0_proxy_reference_corr": None if packet_row is None else packet_row.get("avg_f0_proxy_reference_corr"),
            }
        )
    top_posthoc = posthoc_summary.get("best_checkpoint_by_posthoc_teacher_loss", posthoc_summary.get("best_checkpoint"))
    top_packet = packet_summary.get("best_checkpoint_by_packet_screen", packet_summary.get("best_checkpoint"))
    top_posthoc_path = None if not isinstance(top_posthoc, dict) else str(top_posthoc.get("checkpoint_path"))
    top_packet_path = None if not isinstance(top_packet, dict) else str(top_packet.get("checkpoint_path"))
    packet_reference_context = build_packet_reference_context(
        checkpoint_paths=checkpoint_paths,
        packet_ranking=packet_ranking,
        packet_reference_checkpoint_path=packet_reference_checkpoint_path,
    )
    return {
        "top1_agree": bool(top_posthoc_path and top_posthoc_path == top_packet_path),
        "top1_posthoc_teacher_loss": top_posthoc,
        "top1_packet_aware": top_packet,
        "top1_path_match": None if top_posthoc_path is None or top_packet_path is None else top_posthoc_path == top_packet_path,
        "largest_rank_gap": build_largest_rank_gap(rows),
        "packet_reference_context": packet_reference_context,
        "per_checkpoint": rows,
    }


def build_decision_summary(comparison: dict[str, object]) -> dict[str, object]:
    top_posthoc = comparison.get("top1_posthoc_teacher_loss")
    top_packet = comparison.get("top1_packet_aware")
    top1_agree = bool(comparison.get("top1_agree", False))
    packet_reference_context = dict(comparison.get("packet_reference_context") or {})
    nonreference_packet_candidate = packet_reference_context.get("best_nonreference_packet_candidate_checkpoint")
    handoff_facing_packet_candidate = (
        nonreference_packet_candidate
        if nonreference_packet_candidate is not None
        else top_packet
    )
    packet_auto_reject_count = (
        None
        if not isinstance(top_packet, dict)
        else top_packet.get("auto_reject_count")
    )
    packet_all_core_controls_ready_count = (
        None
        if not isinstance(top_packet, dict)
        else top_packet.get("all_core_controls_ready_count")
    )
    route_open_recommended = bool(
        top1_agree
        and isinstance(top_packet, dict)
        and int(packet_auto_reject_count or 0) <= 0
        and int(packet_all_core_controls_ready_count or 0) > 0
    )
    if route_open_recommended:
        rationale = (
            "Both selectors agree on the same top checkpoint and the packet-aware top row shows no sampled auto-reject with at least one sampled all-core-ready record."
        )
    elif isinstance(top_packet, dict) and int(packet_auto_reject_count or 0) > 0:
        rationale = (
            "Do not open a new Stage5 route from this comparison because the packet-aware top checkpoint still shows sampled auto-reject behavior."
        )
    elif isinstance(top_packet, dict) and int(packet_all_core_controls_ready_count or 0) <= 0:
        rationale = (
            "Do not open a new Stage5 route from this comparison because the packet-aware top checkpoint still shows zero sampled all-core-ready records."
        )
    elif not top1_agree:
        rationale = (
            "Do not collapse the checkpoint family to one universal best checkpoint here because the two selectors disagree on the top candidate."
        )
    else:
        rationale = (
            "This comparison is selector guidance only and should not by itself promote a new Stage5 route."
        )
    return {
        "teacher_loss_leader_checkpoint": top_posthoc,
        "packet_screen_leader_checkpoint": top_packet,
        "teacher_loss_reference_checkpoint": top_posthoc,
        "handoff_facing_packet_candidate_checkpoint": handoff_facing_packet_candidate,
        "packet_reference_checkpoint": packet_reference_context.get("packet_reference_checkpoint"),
        "packet_reference_holds": packet_reference_context.get("packet_reference_holds"),
        "packet_aware_next_best_nonreference_candidate_checkpoint": packet_reference_context.get(
            "best_nonreference_packet_candidate_checkpoint"
        ),
        "unified_best_checkpoint": top_posthoc if top1_agree else None,
        "top1_agree": top1_agree,
        "open_new_stage5_route_recommended": route_open_recommended,
        "rationale": rationale,
    }


def build_ranking_positions(ranking: list[dict[str, object]]) -> dict[str, int]:
    return {
        str(row["checkpoint_path"]): index + 1
        for index, row in enumerate(ranking)
    }


def compute_rank_delta(posthoc_rank: int | None, packet_rank: int | None) -> int | None:
    if posthoc_rank is None or packet_rank is None:
        return None
    return int(packet_rank) - int(posthoc_rank)


def build_largest_rank_gap(rows: list[dict[str, object]]) -> dict[str, object] | None:
    candidates = [row for row in rows if row.get("rank_delta") is not None]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda row: abs(int(row["rank_delta"])),
    )


def build_packet_reference_context(
    *,
    checkpoint_paths: list[Path],
    packet_ranking: list[dict[str, object]],
    packet_reference_checkpoint_path: Path | None,
) -> dict[str, object] | None:
    if packet_reference_checkpoint_path is None:
        return None
    reference_key = packet_reference_checkpoint_path.as_posix()
    reference_rank = None
    reference_row = None
    for index, row in enumerate(packet_ranking):
        if str(row.get("checkpoint_path")) == reference_key:
            reference_rank = index + 1
            reference_row = row
            break
    nonreference_rows = [
        row
        for row in packet_ranking
        if str(row.get("checkpoint_path")) != reference_key
    ]
    best_nonreference = None if not nonreference_rows else nonreference_rows[0]
    best_nonreference_rank = None
    if best_nonreference is not None:
        for index, row in enumerate(packet_ranking):
            if str(row.get("checkpoint_path")) == str(best_nonreference.get("checkpoint_path")):
                best_nonreference_rank = index + 1
                break
    return {
        "packet_reference_checkpoint": reference_row,
        "packet_reference_rank": reference_rank,
        "packet_reference_holds": bool(reference_rank == 1),
        "best_nonreference_packet_candidate_checkpoint": best_nonreference,
        "best_nonreference_packet_candidate_rank": best_nonreference_rank,
    }


def build_markdown(summary: dict[str, object]) -> str:
    comparison = dict(summary["comparison"])
    decision_summary = dict(summary["decision_summary"])
    lines = [
        "# Stage3 Streaming Student Checkpoint Selector Comparison",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- comparison_version: {summary['comparison_version']}",
        f"- checkpoint_paths: {summary['checkpoint_paths']}",
        f"- packet_reference_checkpoint_path: {summary['packet_reference_checkpoint_path']}",
        f"- posthoc_teacher_loss_best: {json.dumps(summary['posthoc_teacher_loss']['best_checkpoint'], ensure_ascii=False)}",
        f"- packet_aware_best: {json.dumps(summary['packet_aware']['best_checkpoint'], ensure_ascii=False)}",
        f"- top1_agree: {comparison['top1_agree']}",
        f"- largest_rank_gap: {json.dumps(comparison['largest_rank_gap'], ensure_ascii=False)}",
        "",
        "## Decision Summary",
        f"- teacher_loss_leader_checkpoint: {json.dumps(decision_summary['teacher_loss_leader_checkpoint'], ensure_ascii=False)}",
        f"- packet_screen_leader_checkpoint: {json.dumps(decision_summary['packet_screen_leader_checkpoint'], ensure_ascii=False)}",
        f"- teacher_loss_reference_checkpoint: {json.dumps(decision_summary['teacher_loss_reference_checkpoint'], ensure_ascii=False)}",
        f"- handoff_facing_packet_candidate_checkpoint: {json.dumps(decision_summary['handoff_facing_packet_candidate_checkpoint'], ensure_ascii=False)}",
        f"- packet_reference_checkpoint: {json.dumps(decision_summary['packet_reference_checkpoint'], ensure_ascii=False)}",
        f"- packet_reference_holds: {json.dumps(decision_summary['packet_reference_holds'], ensure_ascii=False)}",
        f"- packet_aware_next_best_nonreference_candidate_checkpoint: {json.dumps(decision_summary['packet_aware_next_best_nonreference_candidate_checkpoint'], ensure_ascii=False)}",
        f"- unified_best_checkpoint: {json.dumps(decision_summary['unified_best_checkpoint'], ensure_ascii=False)}",
        f"- open_new_stage5_route_recommended: {decision_summary['open_new_stage5_route_recommended']}",
        f"- rationale: {decision_summary['rationale']}",
        "",
        "## Per Checkpoint",
    ]
    for row in comparison["per_checkpoint"]:
        lines.append(
            f"- step={row['step']} posthoc_teacher_loss_rank={row['posthoc_teacher_loss_rank']} "
            f"packet_aware_rank={row['packet_aware_rank']} rank_delta={row['rank_delta']} "
            f"posthoc_teacher_loss_total={row['posthoc_teacher_loss_total']} "
            f"posthoc_special_eval_loss_total={row['posthoc_special_eval_loss_total']} "
            f"packet_auto_reject_count={row['packet_auto_reject_count']} "
            f"packet_vuv_ready_count={row['packet_vuv_ready_count']} "
            f"packet_f0_ready_count={row['packet_f0_ready_count']} "
            f"packet_aper_ready_count={row['packet_aper_ready_count']} "
            f"packet_energy_ready_count={row['packet_energy_ready_count']} "
            f"packet_avg_vuv_reference_mae={row['packet_avg_vuv_reference_mae']} "
            f"packet_avg_f0_proxy_reference_corr={row['packet_avg_f0_proxy_reference_corr']} "
            f"checkpoint_path={row['checkpoint_path']}"
        )
    lines.extend(["", "## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
