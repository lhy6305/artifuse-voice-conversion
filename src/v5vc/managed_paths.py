from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_WINDOWS_PATH_SOFT_LIMIT = 220


def sanitize_path_component(raw_value: object) -> str:
    sanitized = "".join(
        char if str(char).isalnum() or char in {"_", "-"} else "_"
        for char in str(raw_value)
    ).strip("_-")
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    while "--" in sanitized:
        sanitized = sanitized.replace("--", "-")
    return sanitized or "artifact"


def compact_path_component(
    raw_value: object,
    *,
    max_length: int,
) -> str:
    sanitized = sanitize_path_component(raw_value)
    if len(sanitized) <= int(max_length):
        return sanitized
    digest = hashlib.sha1(sanitized.encode("utf-8")).hexdigest()[:6]
    body_budget = max(int(max_length) - len(digest) - 2, 8)
    head_budget = max(body_budget - 6, body_budget // 2)
    tail_budget = max(body_budget - head_budget, 4)
    head = sanitized[:head_budget].rstrip("_-")
    tail = sanitized[-tail_budget:].lstrip("_-")
    compact = "_".join(part for part in (head, tail, digest) if part)
    if len(compact) <= int(max_length):
        return compact
    head_budget = max(int(max_length) - len(digest) - 1, 1)
    head = sanitized[:head_budget].rstrip("_-")
    compact = "_".join(part for part in (head, digest) if part)
    return compact[: int(max_length)].strip("_-")


def resolve_managed_output_dir(
    path: Path,
    *,
    default_stem: str,
    max_full_path_length: int = LEGACY_WINDOWS_PATH_SOFT_LIMIT,
    max_leaf_length: int = 48,
) -> Path:
    resolved_path = path.resolve()
    original_path_text = str(resolved_path)
    if (
        len(original_path_text) <= int(max_full_path_length)
        and len(resolved_path.name) <= int(max_leaf_length)
    ):
        return resolved_path
    parent = resolved_path.parent
    parent_text = str(parent)
    available_leaf_length = max(
        12,
        min(
            int(max_leaf_length),
            int(max_full_path_length) - len(parent_text) - 1,
        ),
    )
    compact_leaf = compact_path_component(
        resolved_path.name or default_stem,
        max_length=available_leaf_length,
    )
    candidate = (parent / compact_leaf).resolve()
    if len(str(candidate)) <= int(max_full_path_length):
        return candidate
    fallback_leaf = compact_path_component(default_stem, max_length=available_leaf_length)
    return (parent / fallback_leaf).resolve()


def reset_managed_directory(path: Path) -> None:
    resolved_path = path.resolve()
    try:
        relative_path = resolved_path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"Managed directory must stay inside repo root {REPO_ROOT.as_posix()}: {resolved_path.as_posix()}"
        ) from exc
    if len(relative_path.parts) < 2:
        raise ValueError(
            "Managed directory path is too broad to clear safely: "
            f"{resolved_path.as_posix()}"
        )
    if resolved_path.exists() and not resolved_path.is_dir():
        raise NotADirectoryError(
            f"Managed directory path points to a file, refusing to clear it: {resolved_path.as_posix()}"
        )
    if resolved_path.exists():
        shutil.rmtree(resolved_path)
    resolved_path.mkdir(parents=True, exist_ok=True)
