from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
from datetime import datetime
from pathlib import Path

from v5vc.data_scan import write_json


def materialize_offline_mvp_route_handoff_doc(
    route_handoff_path: Path,
    output_dir: Path,
    template_path: Path,
    title: str | None = None,
) -> None:
    route_handoff_path = route_handoff_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()

    summary = json.loads(route_handoff_path.read_text(encoding="utf-8"))
    template_text = template_path.read_text(encoding="utf-8")

    reset_managed_directory(output_dir)
    document = build_document_payload(
        summary=summary,
        route_handoff_path=route_handoff_path,
        output_dir=output_dir,
        title=title,
    )
    write_json(output_dir / "handoff_document.json", document)
    (output_dir / "handoff_document.md").write_text(
        render_template(template_text, build_render_fields(document)),
        encoding="utf-8",
        newline="\n",
    )



def build_document_payload(
    summary: dict[str, object],
    route_handoff_path: Path,
    output_dir: Path,
    title: str | None,
) -> dict[str, object]:
    route_context = dict(summary["route_context"])
    route_anchor = dict(summary["route_anchor"])
    alternatives = dict(summary["alternatives"])
    route_governance = dict(summary["route_governance"])
    artifact_bundle = dict(summary["artifact_bundle"])
    stage_label = str(summary["stage_label"])
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "title": title or f"offline MVP handoff document - {stage_label}",
        "stage_label": stage_label,
        "route_policy": str(route_context["selected_policy"]),
        "route_budget_or_floor": dict(route_context["inputs"]),
        "anchor_reference": str(route_anchor["experiment_id"]),
        "next_step_guidance": str(summary["next_step_guidance"]),
        "copy_ready_handoff": list(summary["copy_ready_handoff"]),
        "notes": list(summary["notes"]),
        "route_anchor": route_anchor,
        "alternatives": alternatives,
        "route_governance": route_governance,
        "source_artifacts": {
            "route_handoff_path": route_handoff_path.as_posix(),
            "route_selection_path": str(artifact_bundle["route_selection_path"]),
            "experiment_metrics_paths": list(artifact_bundle["experiment_metrics_paths"]),
        },
        "output_dir": output_dir.as_posix(),
    }


def build_render_fields(document: dict[str, object]) -> dict[str, str]:
    route_anchor = document["route_anchor"]
    alternatives = document["alternatives"]
    route_governance = document["route_governance"]
    source_artifacts = document["source_artifacts"]
    return {
        "title": str(document["title"]),
        "generated_at": str(document["generated_at"]),
        "stage_label": str(document["stage_label"]),
        "route_policy": str(document["route_policy"]),
        "route_budget_or_floor": json.dumps(document["route_budget_or_floor"], ensure_ascii=False, sort_keys=True),
        "anchor_reference": str(document["anchor_reference"]),
        "route_governance_summary": str(route_governance["summary_line"]),
        "route_governance_guardrail": str(route_governance["guardrail_line"]),
        "route_handoff_path": str(source_artifacts["route_handoff_path"]),
        "route_selection_path": str(source_artifacts["route_selection_path"]),
        "copy_ready_handoff_block": build_bullet_block(document["copy_ready_handoff"]),
        "route_anchor_line": format_anchor_line(route_anchor),
        "route_anchor_governance_line": format_governance_line(route_anchor),
        "best_validation_alternative_line": format_alternative_line(
            alternatives["best_validation_alternative"]
        ),
        "best_validation_alternative_governance_line": format_governance_line(
            alternatives["best_validation_alternative"]
        ),
        "best_special_alternative_line": format_alternative_line(
            alternatives["best_special_alternative"]
        ),
        "best_special_alternative_governance_line": format_governance_line(
            alternatives["best_special_alternative"]
        ),
        "best_e_evt_alternative_line": format_alternative_line(alternatives["best_e_evt_alternative"]),
        "best_e_evt_alternative_governance_line": format_governance_line(
            alternatives["best_e_evt_alternative"]
        ),
        "best_z_art_alternative_line": format_alternative_line(alternatives["best_z_art_alternative"]),
        "best_z_art_alternative_governance_line": format_governance_line(
            alternatives["best_z_art_alternative"]
        ),
        "experiment_metrics_paths_block": build_prefixed_block(
            prefix="- experiment_metrics_path: ",
            items=source_artifacts["experiment_metrics_paths"],
        ),
        "next_step_guidance": str(document["next_step_guidance"]),
        "notes_block": build_bullet_block(document["notes"]),
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
