from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from v5vc.data_scan import write_json


def materialize_offline_mvp_stage_report(
    handoff_document_path: Path,
    output_dir: Path,
    template_path: Path,
    title: str | None = None,
) -> None:
    handoff_document_path = handoff_document_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()

    handoff_document = json.loads(handoff_document_path.read_text(encoding="utf-8"))
    template_text = template_path.read_text(encoding="utf-8")

    reset_managed_directory(output_dir)
    report = build_stage_report_payload(
        handoff_document=handoff_document,
        handoff_document_path=handoff_document_path,
        output_dir=output_dir,
        title=title,
    )
    write_json(output_dir / "stage_report.json", report)
    (output_dir / "stage_report.md").write_text(
        render_template(template_text, build_render_fields(report)),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_stage_report_payload(
    handoff_document: dict[str, object],
    handoff_document_path: Path,
    output_dir: Path,
    title: str | None,
) -> dict[str, object]:
    source_artifacts = dict(handoff_document["source_artifacts"])
    copy_ready_handoff = list(handoff_document["copy_ready_handoff"])
    route_anchor = dict(handoff_document["route_anchor"])
    alternatives = dict(handoff_document["alternatives"])
    route_governance = dict(handoff_document["route_governance"])
    stage_label = str(handoff_document["stage_label"])
    route_policy = str(handoff_document["route_policy"])

    executive_status = (
        f"Current route is {route_policy}; "
        f"active anchor remains {route_anchor['experiment_id']}; "
        f"{route_governance['guardrail_line']}"
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "title": title or f"offline MVP stage report - {stage_label}",
        "stage_label": stage_label,
        "route_policy": route_policy,
        "anchor_reference": str(handoff_document["anchor_reference"]),
        "route_budget_or_floor": dict(handoff_document["route_budget_or_floor"]),
        "executive_status": executive_status,
        "current_anchor": route_anchor,
        "route_governance": route_governance,
        "primary_tradeoff": {
            "validation_alternative": alternatives["best_validation_alternative"],
            "special_alternative": alternatives["best_special_alternative"],
        },
        "carry_forward_handoff": copy_ready_handoff,
        "next_step_guidance": str(handoff_document["next_step_guidance"]),
        "notes": [
            "This stage report is derived from the fixed-format handoff document rather than raw selector/comparison outputs.",
            "Route governance is rendered explicitly so synthetic checkpoint options do not get mistaken for formal default anchors.",
            "Use executive_status for status updates; use carry_forward_handoff when the full route-aware wording is needed.",
        ],
        "source_artifacts": {
            "handoff_document_path": handoff_document_path.as_posix(),
            "route_handoff_path": str(source_artifacts["route_handoff_path"]),
            "route_selection_path": str(source_artifacts["route_selection_path"]),
            "experiment_metrics_paths": list(source_artifacts["experiment_metrics_paths"]),
        },
        "output_dir": output_dir.as_posix(),
    }


def build_render_fields(report: dict[str, object]) -> dict[str, str]:
    current_anchor = report["current_anchor"]
    primary_tradeoff = report["primary_tradeoff"]
    route_governance = report["route_governance"]
    source_artifacts = report["source_artifacts"]
    return {
        "title": str(report["title"]),
        "generated_at": str(report["generated_at"]),
        "stage_label": str(report["stage_label"]),
        "route_policy": str(report["route_policy"]),
        "anchor_reference": str(report["anchor_reference"]),
        "route_budget_or_floor": json.dumps(report["route_budget_or_floor"], ensure_ascii=False, sort_keys=True),
        "executive_status": str(report["executive_status"]),
        "current_anchor_line": format_anchor_line(current_anchor),
        "current_anchor_governance_line": format_governance_line(current_anchor),
        "route_governance_summary": str(route_governance["summary_line"]),
        "route_governance_guardrail": str(route_governance["guardrail_line"]),
        "validation_alternative_line": format_alternative_line(primary_tradeoff["validation_alternative"]),
        "validation_alternative_governance_line": format_governance_line(primary_tradeoff["validation_alternative"]),
        "special_alternative_line": format_alternative_line(primary_tradeoff["special_alternative"]),
        "special_alternative_governance_line": format_governance_line(primary_tradeoff["special_alternative"]),
        "carry_forward_handoff_block": build_bullet_block(report["carry_forward_handoff"]),
        "next_step_guidance": str(report["next_step_guidance"]),
        "handoff_document_path": str(source_artifacts["handoff_document_path"]),
        "route_handoff_path": str(source_artifacts["route_handoff_path"]),
        "route_selection_path": str(source_artifacts["route_selection_path"]),
        "experiment_metrics_paths_block": build_prefixed_block(
            prefix="- experiment_metrics_path: ",
            items=source_artifacts["experiment_metrics_paths"],
        ),
        "notes_block": build_bullet_block(report["notes"]),
    }


def build_bullet_block(items: list[object]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


def build_prefixed_block(prefix: str, items: list[object]) -> str:
    if not items:
        return f"{prefix}(none)"
    return "\n".join(f"{prefix}{item}" for item in items)


def format_anchor_line(payload: dict[str, object]) -> str:
    return (
        f"{payload['experiment_id']} "
        f"(val={payload['target_validation_loss_total']}, "
        f"special_delta={payload['delta_loss_total']}, "
        f"zero_e_evt={payload['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={payload['zero_z_art_delta_target_loss_total']})"
    )


def format_alternative_line(payload: dict[str, object]) -> str:
    delta = payload["delta_vs_route_anchor"]
    return (
        f"{payload['experiment_id']} "
        f"(delta_vs_route: val={delta['target_validation_loss_total']}, "
        f"special={delta['delta_loss_total']}, "
        f"zero_e_evt={delta['zero_e_evt_delta_target_loss_total']}, "
        f"zero_z_art={delta['zero_z_art_delta_target_loss_total']})"
    )


def format_governance_line(payload: dict[str, object]) -> str:
    governance = dict(payload["governance"])
    return f"{governance['anchor_class']}: {governance['note']}"


def render_template(template_text: str, render_fields: dict[str, str]) -> str:
    rendered = template_text
    for key, value in render_fields.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered
