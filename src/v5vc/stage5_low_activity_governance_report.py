from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from v5vc.data_scan import write_json


def materialize_stage5_low_activity_governance_report(
    checkpoint_selection_path: Path,
    output_dir: Path,
    template_path: Path,
    title: str | None = None,
) -> None:
    checkpoint_selection_path = checkpoint_selection_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()

    summary = json.loads(checkpoint_selection_path.read_text(encoding="utf-8"))
    template_text = template_path.read_text(encoding="utf-8")

    reset_managed_directory(output_dir)
    report = build_governance_report_payload(
        summary=summary,
        checkpoint_selection_path=checkpoint_selection_path,
        output_dir=output_dir,
        title=title,
    )
    write_json(output_dir / "stage5_low_activity_governance_report.json", report)
    (output_dir / "stage5_low_activity_governance_report.md").write_text(
        render_template(template_text, build_render_fields(report)),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_governance_report_payload(
    summary: dict[str, object],
    checkpoint_selection_path: Path,
    output_dir: Path,
    title: str | None,
) -> dict[str, object]:
    low_activity_probe_analysis = dict(summary["low_activity_probe_analysis"])
    governance_template = dict(low_activity_probe_analysis["governance_template"])
    fragmentation_axis = dict(governance_template["fragmentation_axis"])
    leakage_strength_axis = dict(governance_template["leakage_strength_axis"])
    spectral_sidecar = dict(low_activity_probe_analysis.get("spectral_sidecar", {}))
    low_activity_soft_rerank = dict(summary["low_activity_soft_rerank"])
    selected_candidate = dict(low_activity_soft_rerank["selected_candidate"])
    executive_status = (
        f"Current low-activity governance mode is {governance_template['mode']}; "
        f"fragmentation axis favors {format_branch_label_group(fragmentation_axis['best_fragmentation_branches'])}; "
        f"leakage-strength axis favors {format_branch_label_group(leakage_strength_axis['best_leakage_strength_branches'])}; "
        f"soft rerank currently selects step {selected_candidate['step']}."
    )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "title": title or "stage5 low-activity governance report",
        "audio_source": str(low_activity_probe_analysis["audio_source"]),
        "governance_mode": str(governance_template["mode"]),
        "executive_status": executive_status,
        "fragmentation_axis": fragmentation_axis,
        "leakage_strength_axis": leakage_strength_axis,
        "spectral_sidecar": spectral_sidecar,
        "cross_axis_note": str(governance_template["cross_axis_note"]),
        "soft_rerank": {
            "enabled": bool(low_activity_soft_rerank["enabled"]),
            "soft_validation_ratio": float(low_activity_soft_rerank["soft_validation_ratio"]),
            "eligible_candidate_count": int(low_activity_soft_rerank["eligible_candidate_count"]),
            "selected_candidate": {
                "step": int(selected_candidate["step"]),
                "score": float(selected_candidate["low_activity_governance_score"]),
                "loss_total": float(selected_candidate["loss_total"]),
                "rms_ratio_deviation": float(selected_candidate["rms_ratio_deviation"]),
            },
        },
        "top_windows": list(low_activity_probe_analysis.get("top_windows", [])),
        "source_artifacts": {
            "checkpoint_selection_path": checkpoint_selection_path.as_posix(),
            "probe_path": str(low_activity_probe_analysis["probe_path"]),
            "summary_path": str(summary["summary_path"]),
        },
        "notes": [
            "This fixed-format report is derived from nores_vocoder_checkpoint_selection.json and reuses the embedded dual-axis governance template.",
            "Fragmentation axis and leakage-strength axis are intentionally rendered separately so tradeoff cases do not get compressed into a single winner.",
            "Use top_windows for decoded listening follow-up; use the dual-axis template for governance wording.",
        ],
        "output_dir": output_dir.as_posix(),
    }


def build_render_fields(report: dict[str, object]) -> dict[str, str]:
    fragmentation_axis = report["fragmentation_axis"]
    leakage_strength_axis = report["leakage_strength_axis"]
    spectral_sidecar = report.get("spectral_sidecar", {})
    soft_rerank = report["soft_rerank"]
    selected_candidate = soft_rerank["selected_candidate"]
    source_artifacts = report["source_artifacts"]
    return {
        "title": str(report["title"]),
        "generated_at": str(report["generated_at"]),
        "audio_source": str(report["audio_source"]),
        "governance_mode": str(report["governance_mode"]),
        "executive_status": str(report["executive_status"]),
        "fragmentation_axis_line": (
            f"best_fragmentation={format_branch_label_group(fragmentation_axis['best_fragmentation_branches'])} "
            f"best_alignment={format_branch_label_group(fragmentation_axis['best_alignment_branches'])} "
            f"best_quietness={format_branch_label_group(fragmentation_axis['best_quietness_branches'])}"
        ),
        "fragmentation_note": str(fragmentation_axis["note"]),
        "leakage_strength_axis_line": (
            f"best_leakage_strength={format_branch_label_group(leakage_strength_axis['best_leakage_strength_branches'])} "
            f"worst_floor_leakage={format_branch_label_group(leakage_strength_axis['worst_floor_leakage_branches'])}"
        ),
        "leakage_strength_tie_break_block": build_metric_ranking_block(
            leakage_strength_axis["worst_floor_leakage_strength_ranking"]
        ),
        "leakage_smoothness_tie_break_block": build_metric_ranking_block(
            leakage_strength_axis["worst_floor_leakage_smoothness_ranking"]
        ),
        "leakage_note": str(leakage_strength_axis["note"]),
        "spectral_sidecar_line": (
            "best_centroid_gap="
            f"{format_branch_label_group(spectral_sidecar.get('best_spectral_centroid_gap_branches', []))} "
            "best_bandwidth_gap="
            f"{format_branch_label_group(spectral_sidecar.get('best_spectral_bandwidth_gap_branches', []))} "
            "best_rolloff_gap="
            f"{format_branch_label_group(spectral_sidecar.get('best_spectral_rolloff95_gap_branches', []))} "
            "best_hf_ratio_gap="
            f"{format_branch_label_group(spectral_sidecar.get('best_spectral_hf_ratio_gap_branches', []))}"
        ),
        "spectral_sidecar_note": str(
            spectral_sidecar.get(
                "note",
                "Target-relative spectral-shape sidecar is unavailable.",
            )
        ),
        "cross_axis_note": str(report["cross_axis_note"]),
        "soft_rerank_summary": (
            f"enabled={soft_rerank['enabled']} "
            f"soft_validation_ratio={soft_rerank['soft_validation_ratio']} "
            f"eligible_candidate_count={soft_rerank['eligible_candidate_count']} "
            f"selected_step={selected_candidate['step']} "
            f"selected_score={selected_candidate['score']} "
            f"loss_total={selected_candidate['loss_total']} "
            f"rms_ratio_deviation={selected_candidate['rms_ratio_deviation']}"
        ),
        "top_windows_block": build_top_windows_block(report["top_windows"]),
        "checkpoint_selection_path": str(source_artifacts["checkpoint_selection_path"]),
        "probe_path": str(source_artifacts["probe_path"]),
        "summary_path": str(source_artifacts["summary_path"]),
        "notes_block": build_bullet_block(report["notes"]),
    }


def format_branch_label_group(branch_labels: list[str]) -> str:
    if not branch_labels:
        return "[]"
    if len(branch_labels) == 1:
        return branch_labels[0]
    return "[" + ", ".join(branch_labels) + "]"


def build_metric_ranking_block(items: list[dict[str, object]]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(
        f"- {item['branch_label']} ({item['metric_name']}={item['metric_value']})"
        for item in items
    )


def build_top_windows_block(items: list[dict[str, object]]) -> str:
    if not items:
        return "- (none)"
    rows: list[str] = []
    for item in items:
        rows.append(
            f"- record_id={item['record_id']} segment_index={item['segment_index']} "
            f"delta_fragmentation_score={item['delta_fragmentation_score']} "
            f"worst_branch={item['worst_branch']} best_branch={item['best_branch']}"
        )
    return "\n".join(rows)


def build_bullet_block(items: list[object]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


def render_template(template_text: str, render_fields: dict[str, str]) -> str:
    rendered = template_text
    for key, value in render_fields.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered
