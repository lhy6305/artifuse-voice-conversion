from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path


VALID_SESSION_STATUSES = ("planned", "active", "blocked", "completed")
LIVE_SESSION_STATUSES = ("planned", "active", "blocked")


def register_ai_work_session(
    session_id: str,
    owner: str,
    lane: str,
    status: str,
    objective: str,
    output_dir: Path,
    write_roots: list[Path],
    read_roots: list[Path],
    handoff_docs: list[Path],
    depends_on: list[str],
    notes: list[str],
) -> None:
    normalized_status = str(status).strip().lower()
    if normalized_status not in VALID_SESSION_STATUSES:
        raise ValueError(
            f"Unsupported session status: {status}. "
            f"Expected one of {VALID_SESSION_STATUSES}."
        )
    normalized_session_id = sanitize_session_id(session_id)
    if not normalized_session_id:
        raise ValueError("session_id must not be empty.")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    session_json_path = output_dir / f"{normalized_session_id}.json"
    now = datetime.now().isoformat(timespec="seconds")
    existing_payload = {}
    if session_json_path.exists():
        existing_payload = json.loads(session_json_path.read_text(encoding="utf-8"))

    payload = {
        "session_id": normalized_session_id,
        "owner": str(owner).strip(),
        "lane": str(lane).strip(),
        "status": normalized_status,
        "objective": str(objective).strip(),
        "created_at": existing_payload.get("created_at", now),
        "updated_at": now,
        "write_roots": normalize_paths(write_roots),
        "read_roots": normalize_paths(read_roots),
        "handoff_docs": normalize_paths(handoff_docs),
        "depends_on": dedupe_text_items(depends_on),
        "notes": dedupe_text_items(notes),
        "write_root_conflicts": [],
        "warnings": [],
    }
    write_session_payload(output_dir=output_dir, payload=payload)
    materialize_ai_work_session_index(output_dir)


def materialize_ai_work_session_index(output_dir: Path) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    sessions = []
    for path in sorted(output_dir.glob("*.json")):
        if path.name == "ai_work_sessions_index.json":
            continue
        sessions.append(normalize_session_payload(json.loads(path.read_text(encoding="utf-8"))))
    sessions.sort(
        key=lambda item: (
            session_status_rank(str(item.get("status", ""))),
            str(item.get("lane", "")),
            str(item.get("session_id", "")),
        )
    )

    session_conflicts, conflict_records = analyze_write_root_conflicts(sessions)
    for session in sessions:
        session_id = str(session["session_id"])
        session["write_root_conflicts"] = session_conflicts.get(session_id, [])
        session["warnings"] = build_session_warnings(session)
        write_session_payload(output_dir=output_dir, payload=session)

    index_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "session_count": len(sessions),
        "active_session_count": sum(1 for item in sessions if item.get("status") == "active"),
        "conflict_count": len(conflict_records),
        "conflicted_session_count": sum(
            1 for item in sessions if list(item.get("write_root_conflicts", []))
        ),
        "write_root_conflicts": conflict_records,
        "sessions": sessions,
    }
    index_json_path = output_dir / "ai_work_sessions_index.json"
    index_md_path = output_dir / "ai_work_sessions_index.md"
    index_json_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    index_md_path.write_text(
        build_index_markdown(index_payload),
        encoding="utf-8",
        newline="\n",
    )
    if conflict_records:
        print("WARNING: write-root conflicts detected in AI work session registry.")
        for conflict in conflict_records:
            print(f"  - {conflict['summary']}")


def normalize_session_payload(payload: dict[str, object]) -> dict[str, object]:
    return {
        "session_id": sanitize_session_id(str(payload.get("session_id", ""))),
        "owner": str(payload.get("owner", "")).strip(),
        "lane": str(payload.get("lane", "")).strip(),
        "status": str(payload.get("status", "planned")).strip().lower(),
        "objective": str(payload.get("objective", "")).strip(),
        "created_at": str(payload.get("created_at", "")),
        "updated_at": str(payload.get("updated_at", "")),
        "write_roots": dedupe_text_items(list(payload.get("write_roots", []))),
        "read_roots": dedupe_text_items(list(payload.get("read_roots", []))),
        "handoff_docs": dedupe_text_items(list(payload.get("handoff_docs", []))),
        "depends_on": dedupe_text_items(list(payload.get("depends_on", []))),
        "notes": dedupe_text_items(list(payload.get("notes", []))),
        "write_root_conflicts": [],
        "warnings": [],
    }


def write_session_payload(output_dir: Path, payload: dict[str, object]) -> None:
    session_id = str(payload["session_id"])
    session_json_path = output_dir / f"{session_id}.json"
    session_md_path = output_dir / f"{session_id}.md"
    session_json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    session_md_path.write_text(
        build_session_markdown(payload),
        encoding="utf-8",
        newline="\n",
    )


def analyze_write_root_conflicts(
    sessions: list[dict[str, object]],
) -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    session_conflicts = {
        str(session.get("session_id", "")): []
        for session in sessions
    }
    conflict_records: list[dict[str, object]] = []
    live_sessions = [
        session
        for session in sessions
        if str(session.get("status", "")).strip().lower() in LIVE_SESSION_STATUSES
    ]
    for index, session_a in enumerate(live_sessions):
        for session_b in live_sessions[index + 1 :]:
            for root_a in list(session_a.get("write_roots", [])):
                for root_b in list(session_b.get("write_roots", [])):
                    overlap = classify_write_root_overlap(str(root_a), str(root_b))
                    if overlap is None:
                        continue
                    shared_scope = overlap["shared_scope"]
                    summary = (
                        f"{session_a['session_id']} ({session_a['status']}) and "
                        f"{session_b['session_id']} ({session_b['status']}) overlap on "
                        f"{shared_scope} [{overlap['pair_overlap_type']}]"
                    )
                    conflict_records.append(
                        {
                            "session_a": session_a["session_id"],
                            "session_b": session_b["session_id"],
                            "owner_a": session_a["owner"],
                            "owner_b": session_b["owner"],
                            "lane_a": session_a["lane"],
                            "lane_b": session_b["lane"],
                            "status_a": session_a["status"],
                            "status_b": session_b["status"],
                            "write_root_a": root_a,
                            "write_root_b": root_b,
                            "shared_scope": shared_scope,
                            "overlap_type": overlap["pair_overlap_type"],
                            "summary": summary,
                        }
                    )
                    session_conflicts[str(session_a["session_id"])].append(
                        build_session_conflict_entry(
                            session=session_a,
                            other_session=session_b,
                            write_root=str(root_a),
                            other_write_root=str(root_b),
                            overlap_type=overlap["for_a"],
                            shared_scope=shared_scope,
                        )
                    )
                    session_conflicts[str(session_b["session_id"])].append(
                        build_session_conflict_entry(
                            session=session_b,
                            other_session=session_a,
                            write_root=str(root_b),
                            other_write_root=str(root_a),
                            overlap_type=overlap["for_b"],
                            shared_scope=shared_scope,
                        )
                    )
    return session_conflicts, conflict_records


def build_session_conflict_entry(
    *,
    session: dict[str, object],
    other_session: dict[str, object],
    write_root: str,
    other_write_root: str,
    overlap_type: str,
    shared_scope: str,
) -> dict[str, object]:
    warning = (
        f"write_root {write_root} overlaps with {other_session['session_id']} "
        f"({other_session['status']}) at {shared_scope} [{overlap_type}]"
    )
    return {
        "other_session_id": other_session["session_id"],
        "other_owner": other_session["owner"],
        "other_lane": other_session["lane"],
        "other_status": other_session["status"],
        "write_root": write_root,
        "other_write_root": other_write_root,
        "shared_scope": shared_scope,
        "overlap_type": overlap_type,
        "warning": warning,
    }


def classify_write_root_overlap(path_a: str, path_b: str) -> dict[str, str] | None:
    parts_a = normalize_path_parts(path_a)
    parts_b = normalize_path_parts(path_b)
    if parts_a == parts_b:
        shared_scope = Path(path_a).resolve(strict=False).as_posix()
        return {
            "pair_overlap_type": "same_path",
            "for_a": "same_path",
            "for_b": "same_path",
            "shared_scope": shared_scope,
        }
    if is_prefix_path(parts_a, parts_b):
        return {
            "pair_overlap_type": "session_a_contains_session_b",
            "for_a": "self_root_contains_other",
            "for_b": "other_root_contains_self",
            "shared_scope": Path(path_a).resolve(strict=False).as_posix(),
        }
    if is_prefix_path(parts_b, parts_a):
        return {
            "pair_overlap_type": "session_b_contains_session_a",
            "for_a": "other_root_contains_self",
            "for_b": "self_root_contains_other",
            "shared_scope": Path(path_b).resolve(strict=False).as_posix(),
        }
    return None


def normalize_paths(paths: list[Path]) -> list[str]:
    normalized = []
    seen = set()
    for raw_path in paths:
        resolved = Path(raw_path).resolve(strict=False).as_posix()
        key = resolved.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(resolved)
    return normalized


def normalize_path_parts(path: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in Path(path).resolve(strict=False).parts)


def is_prefix_path(prefix_parts: tuple[str, ...], candidate_parts: tuple[str, ...]) -> bool:
    return len(prefix_parts) <= len(candidate_parts) and prefix_parts == candidate_parts[: len(prefix_parts)]


def build_session_warnings(session: dict[str, object]) -> list[str]:
    warnings = []
    for conflict in list(session.get("write_root_conflicts", [])):
        if not isinstance(conflict, dict):
            continue
        warning = str(conflict.get("warning", "")).strip()
        if warning:
            warnings.append(warning)
    return dedupe_text_items(warnings)


def dedupe_text_items(items: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text)
    return normalized


def sanitize_session_id(raw_session_id: str) -> str:
    return "".join(
        character if character.isalnum() or character in {"-", "_"} else "_"
        for character in str(raw_session_id).strip()
    ).strip("_")


def session_status_rank(status: str) -> int:
    try:
        return VALID_SESSION_STATUSES.index(str(status).strip().lower())
    except ValueError:
        return len(VALID_SESSION_STATUSES)


def build_session_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# AI Work Session",
        "",
        f"- session_id: {payload['session_id']}",
        f"- owner: {payload['owner']}",
        f"- lane: {payload['lane']}",
        f"- status: {payload['status']}",
        f"- objective: {payload['objective']}",
        f"- created_at: {payload['created_at']}",
        f"- updated_at: {payload['updated_at']}",
        "",
        "## Write Roots",
    ]
    for path in payload.get("write_roots", []):
        lines.append(f"- {path}")
    lines.append("")
    lines.append("## Write Root Conflicts")
    conflicts = list(payload.get("write_root_conflicts", []))
    if not conflicts:
        lines.append("- none")
    else:
        for conflict in conflicts:
            lines.append(f"- {conflict['warning']}")
    lines.append("")
    lines.append("## Warnings")
    warnings = list(payload.get("warnings", []))
    if not warnings:
        lines.append("- none")
    else:
        for warning in warnings:
            lines.append(f"- {warning}")
    lines.append("")
    lines.append("## Read Roots")
    for path in payload.get("read_roots", []):
        lines.append(f"- {path}")
    lines.append("")
    lines.append("## Handoff Docs")
    for path in payload.get("handoff_docs", []):
        lines.append(f"- {path}")
    lines.append("")
    lines.append("## Depends On")
    for item in payload.get("depends_on", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Notes")
    for note in payload.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def build_index_markdown(index_payload: dict[str, object]) -> str:
    lines = [
        "# AI Work Sessions Index",
        "",
        f"- generated_at: {index_payload['generated_at']}",
        f"- session_count: {index_payload['session_count']}",
        f"- active_session_count: {index_payload['active_session_count']}",
        f"- conflict_count: {index_payload['conflict_count']}",
        f"- conflicted_session_count: {index_payload['conflicted_session_count']}",
        "",
        "## Write Root Conflicts",
    ]
    conflicts = list(index_payload.get("write_root_conflicts", []))
    if not conflicts:
        lines.append("- none")
    else:
        for conflict in conflicts:
            lines.append(f"- {conflict['summary']}")
    lines.append("")
    grouped: dict[str, list[dict[str, object]]] = {status: [] for status in VALID_SESSION_STATUSES}
    for session in index_payload.get("sessions", []):
        grouped.setdefault(str(session.get("status", "planned")), []).append(session)
    for status in VALID_SESSION_STATUSES:
        lines.append(f"## {status}")
        sessions = grouped.get(status, [])
        if not sessions:
            lines.append("- none")
            lines.append("")
            continue
        for session in sessions:
            summary = (
                f"- {session['session_id']}: owner={session['owner']} lane={session['lane']} "
                f"objective={session['objective']}"
            )
            if list(session.get("write_root_conflicts", [])):
                summary += " [CONFLICT]"
            lines.append(summary)
            write_roots = list(session.get("write_roots", []))
            if write_roots:
                lines.append(f"  write_roots={write_roots}")
            depends_on = list(session.get("depends_on", []))
            if depends_on:
                lines.append(f"  depends_on={depends_on}")
        lines.append("")
    return "\n".join(lines)
