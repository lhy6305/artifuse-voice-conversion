from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


def init_experiment_record(
    slug: str,
    owner: str,
    config_path: Path,
    output_dir: Path,
    template_path: Path,
    route_selection_path: Path | None = None,
) -> None:
    config_path = config_path.resolve()
    output_dir = output_dir.resolve()
    template_path = template_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    experiment_id = build_experiment_id(output_dir=output_dir, slug=slug)
    record_path = output_dir / f"{experiment_id}.md"
    metrics_path = output_dir / f"{experiment_id}.metrics.json"

    template_text = template_path.read_text(encoding="utf-8")
    route_context = load_route_context(route_selection_path)
    filled_text = fill_template(
        template_text=template_text,
        experiment_id=experiment_id,
        owner=owner,
        config_path=config_path,
        metrics_path=metrics_path,
        route_context=route_context,
    )
    record_path.write_text(filled_text, encoding="utf-8", newline="\n")

    metrics_payload = {
        "experiment_id": experiment_id,
        "status": "initialized",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "metrics": {},
        "notes": [],
    }
    metrics_path.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )


def build_experiment_id(output_dir: Path, slug: str) -> str:
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    safe_slug = slug.strip().lower().replace(" ", "-")
    existing = sorted(output_dir.glob(f"EXP-{date_prefix}-*.md"))
    max_index = 0
    index_pattern = re.compile(rf"^EXP-{date_prefix}-(\d{{3}})-")
    for path in existing:
        match = index_pattern.match(path.stem)
        if match is None:
            continue
        max_index = max(max_index, int(match.group(1)))
    next_index = max_index + 1
    return f"EXP-{date_prefix}-{next_index:03d}-{safe_slug}"


def load_route_context(route_selection_path: Path | None) -> dict[str, str]:
    if route_selection_path is None:
        return {}
    resolved_path = route_selection_path.resolve()
    payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    selected_policy = payload.get("selected_policy", {})
    selected_anchor = payload.get("selected_anchor", {})
    inputs = payload.get("inputs", {})
    return {
        "route_policy": str(selected_policy.get("policy_name", "")),
        "route_budget_or_floor": json.dumps(inputs, ensure_ascii=False, sort_keys=True),
        "anchor_reference": str(selected_anchor.get("experiment_id", "")),
    }


def fill_template(
    template_text: str,
    experiment_id: str,
    owner: str,
    config_path: Path,
    metrics_path: Path,
    route_context: dict[str, str],
) -> str:
    lines = template_text.splitlines()
    output_lines: list[str] = []
    for line in lines:
        if line == "- experiment_id:":
            output_lines.append(f"- experiment_id: {experiment_id}")
        elif line == "- date:":
            output_lines.append(f"- date: {datetime.now().isoformat(timespec='seconds')}")
        elif line == "- owner:":
            output_lines.append(f"- owner: {owner}")
        elif line == "- config_path:":
            output_lines.append(f"- config_path: {config_path.as_posix()}")
        elif line == "- route_policy:":
            output_lines.append(f"- route_policy: {route_context.get('route_policy', '')}")
        elif line == "- route_budget_or_floor:":
            output_lines.append(f"- route_budget_or_floor: {route_context.get('route_budget_or_floor', '')}")
        elif line == "- anchor_reference:":
            output_lines.append(f"- anchor_reference: {route_context.get('anchor_reference', '')}")
        elif line == "- summary:":
            output_lines.append("- summary: initialized")
        elif line == "- follow_up:":
            output_lines.append(f"- follow_up: metrics file -> {metrics_path.as_posix()}")
        else:
            output_lines.append(line)
    return "\n".join(output_lines) + "\n"
