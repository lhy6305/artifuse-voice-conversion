from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from v5vc.data_scan import write_json


TIE_LABEL = "打平"
FIELD_LABELS = {
    "best_rhythm": "节奏最好",
    "best_boundary": "边界最好",
    "most_stable": "最稳定",
    "overall_pick": "综合首选",
}


def materialize_stage5_low_activity_audit_result_report(
    audio_audit_review_path: Path,
    governance_report_path: Path,
    output_dir: Path,
    template_path: Path,
    title: str | None = None,
) -> None:
    audio_audit_review_path = audio_audit_review_path.resolve()
    governance_report_path = governance_report_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()

    review_summary = json.loads(audio_audit_review_path.read_text(encoding="utf-8"))
    governance_report = json.loads(governance_report_path.read_text(encoding="utf-8"))
    template_text = template_path.read_text(encoding="utf-8")

    reset_managed_directory(output_dir)
    report = build_audit_result_report_payload(
        review_summary=review_summary,
        governance_report=governance_report,
        audio_audit_review_path=audio_audit_review_path,
        governance_report_path=governance_report_path,
        output_dir=output_dir,
        title=title,
    )
    write_json(output_dir / "stage5_low_activity_audit_result_report.json", report)
    (output_dir / "stage5_low_activity_audit_result_report.md").write_text(
        render_template(template_text, build_render_fields(report)),
        encoding="utf-8",
        newline="\n",
    )



def build_audit_result_report_payload(
    review_summary: dict[str, object],
    governance_report: dict[str, object],
    audio_audit_review_path: Path,
    governance_report_path: Path,
    output_dir: Path,
    title: str | None,
) -> dict[str, object]:
    governance_labels = collect_governance_labels(governance_report)
    canonical_field_aggregates = build_canonical_field_aggregates(review_summary, governance_labels)
    validity_counts = normalize_validity_counts(review_summary)
    completed_count = int(review_summary.get("completed_count", 0))
    record_count = int(review_summary.get("record_count", 0))
    comparable_count = int(validity_counts["yes"]) + int(validity_counts["partial"])
    noncomparable_count = int(validity_counts["no"])
    overall_pick_counts = canonical_field_aggregates.get("overall_pick", {})

    fragmentation_branches = set(governance_report["fragmentation_axis"]["best_fragmentation_branches"])
    leakage_strength_branches = set(governance_report["leakage_strength_axis"]["best_leakage_strength_branches"])
    axis_support = {
        "fragmentation_axis": sum(
            count for label, count in overall_pick_counts.items() if label in fragmentation_branches
        ),
        "leakage_strength_axis": sum(
            count for label, count in overall_pick_counts.items() if label in leakage_strength_branches
        ),
        "tie": int(overall_pick_counts.get(TIE_LABEL, 0)),
    }
    leading_branch_labels = determine_leading_branch_labels(overall_pick_counts)
    readout_label, readout_note = classify_cross_axis_readout(
        comparable_count=comparable_count,
        axis_support=axis_support,
        leading_branch_labels=leading_branch_labels,
        governance_mode=str(governance_report["governance_mode"]),
    )

    executive_status = (
        f"Human audit completed {completed_count}/{record_count}; "
        f"comparable records={comparable_count}/{record_count}; "
        f"overall-pick aggregate among comparable records is {format_count_summary(overall_pick_counts)}; "
        f"{readout_note}"
    )

    comparable_record_notes, noncomparable_record_notes = split_record_notes(
        review_summary=review_summary,
        governance_labels=governance_labels,
    )
    governance_source_artifacts = dict(governance_report["source_artifacts"])
    governance_snapshot = {
        "executive_status": str(governance_report["executive_status"]),
        "fragmentation_axis": dict(governance_report["fragmentation_axis"]),
        "leakage_strength_axis": dict(governance_report["leakage_strength_axis"]),
        "cross_axis_note": str(governance_report["cross_axis_note"]),
        "selected_candidate": dict(governance_report["soft_rerank"]["selected_candidate"]),
    }

    review_markdown_path = audio_audit_review_path.with_suffix(".md")
    governance_markdown_path = governance_report_path.with_suffix(".md")
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "title": title or "stage5 low-activity audit result report",
        "audio_source": str(governance_report["audio_source"]),
        "governance_mode": str(governance_report["governance_mode"]),
        "executive_status": executive_status,
        "review_coverage": {
            "record_count": record_count,
            "completed_count": completed_count,
            "comparable_count": comparable_count,
            "partial_comparable_count": int(validity_counts["partial"]),
            "noncomparable_count": noncomparable_count,
        },
        "overall_pick_aggregate": overall_pick_counts,
        "cross_axis_readout": {
            "label": readout_label,
            "note": readout_note,
            "leading_branch_labels": leading_branch_labels,
            "axis_support": axis_support,
        },
        "field_aggregates": canonical_field_aggregates,
        "comparable_record_notes": comparable_record_notes,
        "noncomparable_record_notes": noncomparable_record_notes,
        "session_notes": str(review_summary.get("session_notes", "")),
        "governance_snapshot": governance_snapshot,
        "source_artifacts": {
            "audio_audit_review_path": audio_audit_review_path.as_posix(),
            "audio_audit_review_markdown_path": (
                review_markdown_path.as_posix() if review_markdown_path.exists() else "(missing)"
            ),
            "governance_report_path": governance_report_path.as_posix(),
            "governance_report_markdown_path": (
                governance_markdown_path.as_posix() if governance_markdown_path.exists() else "(missing)"
            ),
            "checkpoint_selection_path": str(governance_source_artifacts["checkpoint_selection_path"]),
            "probe_path": str(governance_source_artifacts["probe_path"]),
        },
        "notes": [
            "This fixed-format report joins human audio-audit output with the fixed governance report instead of requiring a separate narrative-only interpretation memo.",
            "Cross-axis readout is derived from comparable-record overall_pick results; tie counts are preserved instead of being forced into one branch.",
            "Use the governance snapshot to keep fragmentation-axis and leakage-strength-axis wording aligned with the quantitative report.",
        ],
        "output_dir": output_dir.as_posix(),
    }


def collect_governance_labels(governance_report: dict[str, object]) -> set[str]:
    labels: set[str] = set()
    fragmentation_axis = dict(governance_report["fragmentation_axis"])
    leakage_strength_axis = dict(governance_report["leakage_strength_axis"])
    for key in ("best_fragmentation_branches", "best_alignment_branches", "best_quietness_branches"):
        labels.update(str(item) for item in fragmentation_axis.get(key, []))
    for key in ("best_leakage_strength_branches", "worst_floor_leakage_branches"):
        labels.update(str(item) for item in leakage_strength_axis.get(key, []))
    for key in (
        "worst_floor_leakage_strength_ranking",
        "worst_floor_leakage_smoothness_ranking",
    ):
        for item in leakage_strength_axis.get(key, []):
            labels.add(str(item["branch_label"]))
    for item in governance_report.get("top_windows", []):
        labels.add(str(item["worst_branch"]))
        labels.add(str(item["best_branch"]))
    return labels


def normalize_validity_counts(review_summary: dict[str, object]) -> dict[str, int]:
    counter = {"yes": 0, "partial": 0, "no": 0}
    for raw_label, raw_value in dict(review_summary["aggregate"]["valid_for_comparison"]).items():
        counter[normalize_validity_value(str(raw_label))] += int(raw_value)
    return counter


def build_canonical_field_aggregates(
    review_summary: dict[str, object],
    governance_labels: set[str],
) -> dict[str, dict[str, int]]:
    aggregates: dict[str, dict[str, int]] = {}
    for field_id, raw_counts in dict(review_summary["aggregate"]["by_field"]).items():
        counter: Counter[str] = Counter()
        for raw_label, raw_value in dict(raw_counts).items():
            counter[canonicalize_candidate_label(str(raw_label), governance_labels)] += int(raw_value)
        aggregates[str(field_id)] = dict(sorted(counter.items()))
    return aggregates


def determine_leading_branch_labels(overall_pick_counts: dict[str, int]) -> list[str]:
    branch_counts = {
        label: count
        for label, count in overall_pick_counts.items()
        if label != TIE_LABEL and count > 0
    }
    if not branch_counts:
        return []
    max_count = max(branch_counts.values())
    return sorted(label for label, count in branch_counts.items() if count == max_count)


def classify_cross_axis_readout(
    comparable_count: int,
    axis_support: dict[str, int],
    leading_branch_labels: list[str],
    governance_mode: str,
) -> tuple[str, str]:
    if comparable_count <= 0:
        return (
            "no_comparable_readout",
            f"Human audit produced no comparable readout; keep governance mode at {governance_mode}.",
        )
    fragmentation_support = int(axis_support["fragmentation_axis"])
    leakage_support = int(axis_support["leakage_strength_axis"])
    if not leading_branch_labels and int(axis_support["tie"]) > 0:
        return (
            "tie_only",
            f"Comparable records only produced ties; keep governance mode at {governance_mode} instead of forcing a winner.",
        )
    if fragmentation_support > leakage_support:
        return (
            "leans_fragmentation_axis",
            (
                f"Human overall-pick currently leans fragmentation axis "
                f"({fragmentation_support} vs {leakage_support}); treat this as localized structural evidence, "
                f"not as a replacement for the leakage-strength axis."
            ),
        )
    if leakage_support > fragmentation_support:
        return (
            "leans_leakage_strength_axis",
            (
                f"Human overall-pick currently leans leakage-strength axis "
                f"({leakage_support} vs {fragmentation_support}); keep the fragmentation axis visible because local burst risk remains a separate question."
            ),
        )
    if fragmentation_support == leakage_support and fragmentation_support > 0:
        return (
            "split_across_axes",
            (
                "Human overall-pick remains split across the two governance axes; "
                f"keep governance mode at {governance_mode} rather than collapsing to a single winner."
            ),
        )
    return (
        "off_axis_or_inconclusive",
        f"Human overall-pick is inconclusive relative to the governance axes; keep governance mode at {governance_mode}.",
    )


def split_record_notes(
    review_summary: dict[str, object],
    governance_labels: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    comparable_records: list[dict[str, str]] = []
    noncomparable_records: list[dict[str, str]] = []
    for record in list(review_summary.get("records", [])):
        review = dict(record.get("review", {}))
        interpreted_review = dict(record.get("interpreted_review", {}))
        validity = normalize_validity_value(str(review.get("valid_for_comparison", "yes")))
        overall_pick = interpreted_review.get("overall_pick", review.get("overall_pick", ""))
        note_payload = {
            "record_id": str(record["record_id"]),
            "valid_for_comparison": validity,
            "overall_pick": canonicalize_candidate_label(str(overall_pick), governance_labels),
            "notes": str(review.get("notes", "")).strip() or "(empty)",
        }
        if validity == "no":
            noncomparable_records.append(note_payload)
        else:
            comparable_records.append(note_payload)
    return comparable_records, noncomparable_records


def normalize_validity_value(value: str) -> str:
    normalized = value.strip()
    if normalized in {"yes", "partial", "no"}:
        return normalized
    if normalized == "可比较":
        return "yes"
    if normalized == "部分可比较":
        return "partial"
    if normalized == "不建议比较":
        return "no"
    return "yes"


def canonicalize_candidate_label(label: str, governance_labels: set[str]) -> str:
    normalized = label.strip()
    if not normalized:
        return ""
    if normalized == TIE_LABEL:
        return TIE_LABEL
    for governance_label in governance_labels:
        if normalized == governance_label or normalized.endswith(f":{governance_label}"):
            return governance_label
    if ":" in normalized:
        return normalized.split(":")[-1]
    return normalized


def build_render_fields(report: dict[str, object]) -> dict[str, str]:
    coverage = dict(report["review_coverage"])
    governance_snapshot = dict(report["governance_snapshot"])
    fragmentation_axis = dict(governance_snapshot["fragmentation_axis"])
    leakage_strength_axis = dict(governance_snapshot["leakage_strength_axis"])
    selected_candidate = dict(governance_snapshot["selected_candidate"])
    cross_axis_readout = dict(report["cross_axis_readout"])
    source_artifacts = dict(report["source_artifacts"])
    return {
        "title": str(report["title"]),
        "generated_at": str(report["generated_at"]),
        "audio_source": str(report["audio_source"]),
        "governance_mode": str(report["governance_mode"]),
        "coverage_line": (
            f"record_count={coverage['record_count']} "
            f"completed_count={coverage['completed_count']} "
            f"comparable_count={coverage['comparable_count']} "
            f"partial_comparable_count={coverage['partial_comparable_count']} "
            f"noncomparable_count={coverage['noncomparable_count']}"
        ),
        "executive_status": str(report["executive_status"]),
        "governance_executive_status": str(governance_snapshot["executive_status"]),
        "fragmentation_axis_line": (
            f"best_fragmentation={format_branch_label_group(fragmentation_axis['best_fragmentation_branches'])} "
            f"best_alignment={format_branch_label_group(fragmentation_axis['best_alignment_branches'])} "
            f"best_quietness={format_branch_label_group(fragmentation_axis['best_quietness_branches'])}"
        ),
        "leakage_strength_axis_line": (
            f"best_leakage_strength={format_branch_label_group(leakage_strength_axis['best_leakage_strength_branches'])} "
            f"worst_floor_leakage={format_branch_label_group(leakage_strength_axis['worst_floor_leakage_branches'])}"
        ),
        "governance_cross_axis_note": str(governance_snapshot["cross_axis_note"]),
        "governance_selected_candidate": (
            f"step={selected_candidate['step']} "
            f"score={selected_candidate['score']} "
            f"loss_total={selected_candidate['loss_total']} "
            f"rms_ratio_deviation={selected_candidate['rms_ratio_deviation']}"
        ),
        "overall_pick_summary": format_count_summary(report["overall_pick_aggregate"]),
        "cross_axis_readout_label": str(cross_axis_readout["label"]),
        "cross_axis_readout_note": str(cross_axis_readout["note"]),
        "cross_axis_support_line": (
            f"fragmentation_axis={cross_axis_readout['axis_support']['fragmentation_axis']} "
            f"leakage_strength_axis={cross_axis_readout['axis_support']['leakage_strength_axis']} "
            f"tie={cross_axis_readout['axis_support']['tie']} "
            f"leading_branches={format_branch_label_group(cross_axis_readout['leading_branch_labels'])}"
        ),
        "field_aggregates_block": build_field_aggregates_block(report["field_aggregates"]),
        "comparable_record_notes_block": build_record_notes_block(report["comparable_record_notes"]),
        "noncomparable_record_notes_block": build_record_notes_block(report["noncomparable_record_notes"]),
        "session_notes": str(report["session_notes"] or "(empty)"),
        "audio_audit_review_path": str(source_artifacts["audio_audit_review_path"]),
        "audio_audit_review_markdown_path": str(source_artifacts["audio_audit_review_markdown_path"]),
        "governance_report_path": str(source_artifacts["governance_report_path"]),
        "governance_report_markdown_path": str(source_artifacts["governance_report_markdown_path"]),
        "checkpoint_selection_path": str(source_artifacts["checkpoint_selection_path"]),
        "probe_path": str(source_artifacts["probe_path"]),
        "notes_block": build_bullet_block(report["notes"]),
    }


def build_field_aggregates_block(field_aggregates: dict[str, dict[str, int]]) -> str:
    lines: list[str] = []
    for field_id in ("best_rhythm", "best_boundary", "most_stable", "overall_pick"):
        lines.append(f"### {FIELD_LABELS[field_id]}")
        counts = dict(field_aggregates.get(field_id, {}))
        if counts:
            for label, value in counts.items():
                lines.append(f"- {label}: {value}")
        else:
            lines.append("- (none)")
        lines.append("")
    return "\n".join(lines).strip()


def build_record_notes_block(items: list[dict[str, str]]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(
        (
            f"- record_id={item['record_id']} "
            f"valid_for_comparison={item['valid_for_comparison']} "
            f"overall_pick={item['overall_pick'] or '(none)'} "
            f"notes={item['notes']}"
        )
        for item in items
    )


def build_bullet_block(items: list[object]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


def format_count_summary(counts: dict[str, int]) -> str:
    if not counts:
        return "(none)"
    return ", ".join(f"{label}={value}" for label, value in counts.items())


def format_branch_label_group(branch_labels: list[str]) -> str:
    if not branch_labels:
        return "[]"
    if len(branch_labels) == 1:
        return branch_labels[0]
    return "[" + ", ".join(branch_labels) + "]"


def render_template(template_text: str, render_fields: dict[str, str]) -> str:
    rendered = template_text
    for key, value in render_fields.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered
