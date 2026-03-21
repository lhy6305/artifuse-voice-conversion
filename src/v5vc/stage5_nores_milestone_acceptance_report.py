from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from v5vc.data_scan import write_json


def materialize_stage5_nores_milestone_acceptance_report(
    audio_audit_review_path: Path,
    output_dir: Path,
    template_path: Path,
    title: str | None = None,
) -> None:
    audio_audit_review_path = audio_audit_review_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()

    review_summary = json.loads(audio_audit_review_path.read_text(encoding="utf-8"))
    review_mode = str(review_summary.get("review_mode", "")).strip().lower()
    if review_mode != "milestone_acceptance":
        raise ValueError(
            "Stage5 no-res milestone acceptance report requires audio_audit_review.json exported in milestone_acceptance mode."
        )

    manifest_paths = [Path(item).resolve() for item in list(review_summary.get("manifest_paths", []))]
    if not manifest_paths:
        raise ValueError("audio_audit_review.json does not contain manifest_paths.")
    if len(manifest_paths) != 1:
        raise ValueError(
            "Stage5 no-res milestone acceptance report expects exactly one bundle manifest because this is an absolute-acceptance audit."
        )

    bundle_manifest_path = manifest_paths[0]
    bundle_manifest = json.loads(bundle_manifest_path.read_text(encoding="utf-8"))
    template_text = template_path.read_text(encoding="utf-8")

    reset_managed_directory(output_dir)
    report = build_stage5_nores_milestone_acceptance_report(
        review_summary=review_summary,
        bundle_manifest=bundle_manifest,
        audio_audit_review_path=audio_audit_review_path,
        bundle_manifest_path=bundle_manifest_path,
        output_dir=output_dir,
        title=title,
    )
    write_json(output_dir / "stage5_nores_milestone_acceptance_report.json", report)
    (output_dir / "stage5_nores_milestone_acceptance_report.md").write_text(
        render_template(template_text, build_render_fields(report)),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_stage5_nores_milestone_acceptance_report(
    *,
    review_summary: dict[str, object],
    bundle_manifest: dict[str, object],
    audio_audit_review_path: Path,
    bundle_manifest_path: Path,
    output_dir: Path,
    title: str | None,
) -> dict[str, object]:
    validity_counts = normalize_validity_counts(review_summary)
    field_aggregates = dict(dict(review_summary.get("aggregate", {})).get("by_field", {}))
    verdict_counts = normalize_string_count_map(field_aggregates.get("milestone_verdict", {}))
    intelligibility_counts = normalize_string_count_map(field_aggregates.get("intelligibility", {}))
    stability_counts = normalize_string_count_map(field_aggregates.get("stability", {}))
    naturalness_counts = normalize_string_count_map(field_aggregates.get("basic_naturalness", {}))

    record_count = int(review_summary.get("record_count", 0))
    completed_count = int(review_summary.get("completed_count", 0))
    comparable_count = int(validity_counts["yes"]) + int(validity_counts["partial"])
    noncomparable_count = int(validity_counts["no"])
    explicit_verdict_count = sum(verdict_counts.values())
    milestone_readout = classify_milestone_readout(
        comparable_count=comparable_count,
        explicit_verdict_count=explicit_verdict_count,
        verdict_counts=verdict_counts,
    )

    review_markdown_path = audio_audit_review_path.with_suffix(".md")
    selected_checkpoint_summary = dict(bundle_manifest.get("selected_checkpoint_summary", {}))
    source_artifacts = {
        "audio_audit_review_path": audio_audit_review_path.as_posix(),
        "audio_audit_review_markdown_path": (
            review_markdown_path.as_posix() if review_markdown_path.exists() else "(missing)"
        ),
        "bundle_manifest_path": bundle_manifest_path.as_posix(),
        "checkpoint_path": str(bundle_manifest.get("checkpoint_path", "(missing)")),
        "checkpoint_selection_path": str(bundle_manifest.get("checkpoint_selection_path", "(missing)")),
    }
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "title": title or "stage5 no-res milestone acceptance report",
        "review_mode": str(review_summary.get("review_mode", "")),
        "executive_status": (
            f"Milestone acceptance audit completed {completed_count}/{record_count}; "
            f"comparable judgments={comparable_count}/{record_count}; "
            f"milestone_verdict aggregate is {format_count_summary(verdict_counts)}; "
            f"{milestone_readout['note']}"
        ),
        "review_coverage": {
            "record_count": record_count,
            "completed_count": completed_count,
            "comparable_count": comparable_count,
            "partial_comparable_count": int(validity_counts["partial"]),
            "noncomparable_count": noncomparable_count,
            "explicit_verdict_count": explicit_verdict_count,
        },
        "bundle_context": {
            "branch_label": str(bundle_manifest.get("branch_label", "(missing)")),
            "selection_target": str(bundle_manifest.get("selection_target", "(missing)")),
            "listening_audio_source": str(bundle_manifest.get("listening_audio_source", "(missing)")),
            "selected_checkpoint_step": selected_checkpoint_summary.get("step"),
            "sample_count": int(bundle_manifest.get("sample_count", 0)),
        },
        "milestone_readout": milestone_readout,
        "field_aggregates": {
            "intelligibility": intelligibility_counts,
            "stability": stability_counts,
            "basic_naturalness": naturalness_counts,
            "milestone_verdict": verdict_counts,
        },
        "record_notes": build_record_notes(review_summary),
        "session_notes": str(review_summary.get("session_notes", "")),
        "source_artifacts": source_artifacts,
        "notes": [
            "This fixed-format report is for the Stage5 no-res absolute milestone acceptance question, not for branch-vs-branch ranking.",
            "milestone_verdict is aggregated as structured evidence; keep the per-record notes visible before making any route-change decision.",
            "aligned_target remains a bootstrap objective reference here; it is not a user-line source-to-target acceptance target.",
        ],
        "output_dir": output_dir.as_posix(),
    }


def normalize_validity_counts(review_summary: dict[str, object]) -> dict[str, int]:
    raw_counts = dict(dict(review_summary.get("aggregate", {})).get("valid_for_comparison", {}))
    return {
        "yes": int(raw_counts.get("yes", 0)),
        "partial": int(raw_counts.get("partial", 0)),
        "no": int(raw_counts.get("no", 0)),
    }


def normalize_string_count_map(raw_counts: object) -> dict[str, int]:
    if not isinstance(raw_counts, dict):
        return {}
    return {str(key): int(value) for key, value in raw_counts.items()}


def classify_milestone_readout(
    *,
    comparable_count: int,
    explicit_verdict_count: int,
    verdict_counts: dict[str, int],
) -> dict[str, object]:
    pass_count = int(verdict_counts.get("通过", 0))
    borderline_count = int(verdict_counts.get("边缘", 0))
    fail_count = int(verdict_counts.get("未通过", 0))
    if comparable_count <= 0:
        return {
            "label": "pending",
            "note": "No comparable milestone judgments exist yet.",
        }
    if explicit_verdict_count < comparable_count:
        return {
            "label": "incomplete_judgment",
            "note": (
                f"Only {explicit_verdict_count}/{comparable_count} comparable records have an explicit milestone_verdict; "
                "finish the remaining judgments before treating this audit as closed."
            ),
        }
    if fail_count > 0:
        return {
            "label": "not_cleared",
            "note": f"{fail_count} comparable record(s) were marked 未通过, so the current route is not yet cleared as a passed milestone.",
        }
    if borderline_count > 0:
        return {
            "label": "borderline",
            "note": f"No comparable record was marked 未通过, but {borderline_count} record(s) remain 边缘; keep the route as borderline instead of passed.",
        }
    if pass_count == comparable_count:
        return {
            "label": "cleared",
            "note": f"All {comparable_count} comparable records were marked 通过.",
        }
    return {
        "label": "mixed",
        "note": "Milestone verdicts remain mixed or under-specified.",
    }


def build_record_notes(review_summary: dict[str, object]) -> list[dict[str, str]]:
    validity_options = {
        str(code): str(label)
        for code, label in dict(review_summary.get("validity_options", {})).items()
    }
    items: list[dict[str, str]] = []
    for record in list(review_summary.get("records", [])):
        if not isinstance(record, dict):
            continue
        review = dict(record.get("review", {}))
        interpreted_review = dict(record.get("interpreted_review", {}))
        validity_code = str(review.get("valid_for_comparison", "yes"))
        items.append(
            {
                "record_id": str(record.get("record_id", "")),
                "validity": validity_options.get(validity_code, validity_code),
                "intelligibility": str(interpreted_review.get("intelligibility", review.get("intelligibility", ""))),
                "stability": str(interpreted_review.get("stability", review.get("stability", ""))),
                "basic_naturalness": str(
                    interpreted_review.get("basic_naturalness", review.get("basic_naturalness", ""))
                ),
                "milestone_verdict": str(
                    interpreted_review.get("milestone_verdict", review.get("milestone_verdict", ""))
                ),
                "notes": str(review.get("notes", "")).strip() or "(empty)",
            }
        )
    return items


def build_render_fields(report: dict[str, object]) -> dict[str, str]:
    coverage = dict(report["review_coverage"])
    bundle_context = dict(report["bundle_context"])
    milestone_readout = dict(report["milestone_readout"])
    field_aggregates = dict(report["field_aggregates"])
    source_artifacts = dict(report["source_artifacts"])
    return {
        "title": str(report["title"]),
        "generated_at": str(report["generated_at"]),
        "review_mode": str(report["review_mode"]),
        "executive_status": str(report["executive_status"]),
        "coverage_line": (
            f"record_count={coverage['record_count']} "
            f"completed_count={coverage['completed_count']} "
            f"comparable_count={coverage['comparable_count']} "
            f"partial_comparable_count={coverage['partial_comparable_count']} "
            f"noncomparable_count={coverage['noncomparable_count']} "
            f"explicit_verdict_count={coverage['explicit_verdict_count']}"
        ),
        "bundle_line": (
            f"branch_label={bundle_context['branch_label']} "
            f"selection_target={bundle_context['selection_target']} "
            f"selected_checkpoint_step={bundle_context['selected_checkpoint_step']} "
            f"sample_count={bundle_context['sample_count']}"
        ),
        "listening_source": str(bundle_context["listening_audio_source"]),
        "milestone_readout_label": str(milestone_readout["label"]),
        "milestone_readout_note": str(milestone_readout["note"]),
        "verdict_summary": format_count_summary(dict(field_aggregates.get("milestone_verdict", {}))),
        "intelligibility_summary": format_count_summary(dict(field_aggregates.get("intelligibility", {}))),
        "stability_summary": format_count_summary(dict(field_aggregates.get("stability", {}))),
        "naturalness_summary": format_count_summary(dict(field_aggregates.get("basic_naturalness", {}))),
        "record_notes_block": build_record_notes_block(list(report.get("record_notes", []))),
        "session_notes": str(report["session_notes"] or "(empty)"),
        "audio_audit_review_path": str(source_artifacts["audio_audit_review_path"]),
        "audio_audit_review_markdown_path": str(source_artifacts["audio_audit_review_markdown_path"]),
        "bundle_manifest_path": str(source_artifacts["bundle_manifest_path"]),
        "checkpoint_path": str(source_artifacts["checkpoint_path"]),
        "checkpoint_selection_path": str(source_artifacts["checkpoint_selection_path"]),
        "notes_block": build_bullet_block(list(report.get("notes", []))),
    }


def build_record_notes_block(items: list[dict[str, str]]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(
        (
            f"- record_id={item['record_id']} "
            f"validity={item['validity']} "
            f"intelligibility={item['intelligibility'] or '(empty)'} "
            f"stability={item['stability'] or '(empty)'} "
            f"basic_naturalness={item['basic_naturalness'] or '(empty)'} "
            f"milestone_verdict={item['milestone_verdict'] or '(empty)'} "
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


def render_template(template_text: str, render_fields: dict[str, str]) -> str:
    rendered = template_text
    for key, value in render_fields.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize a fixed-format Stage5 no-res milestone acceptance report from GUI review output."
    )
    parser.add_argument(
        "--audio-audit-review",
        type=Path,
        required=True,
        help="Path to audio_audit_review.json exported by the milestone_acceptance GUI session.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for the fixed-format milestone acceptance report outputs.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("reports/templates/stage5_nores_milestone_acceptance_report_template.md"),
        help="Markdown template used to render the milestone acceptance report.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional override title written into the milestone acceptance report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    materialize_stage5_nores_milestone_acceptance_report(
        audio_audit_review_path=args.audio_audit_review,
        output_dir=args.output_dir,
        template_path=args.template,
        title=args.title,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
