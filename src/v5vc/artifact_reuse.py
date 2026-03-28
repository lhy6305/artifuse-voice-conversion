from __future__ import annotations

import hashlib
import json
from pathlib import Path


def build_file_fingerprint(path: Path) -> dict[str, object]:
    resolved_path = path.resolve()
    if not resolved_path.exists():
        return {
            "path": resolved_path.as_posix(),
            "exists": False,
        }
    stat = resolved_path.stat()
    return {
        "path": resolved_path.as_posix(),
        "exists": True,
        "size_bytes": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
    }


def build_optional_file_fingerprint(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    return build_file_fingerprint(path)


def build_mapping_fingerprint(mapping: dict[str, object] | None) -> dict[str, object]:
    if not isinstance(mapping, dict):
        return {
            "present": False,
        }
    canonical_json = json.dumps(
        mapping,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "present": True,
        "sha256": hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
        "json_chars": len(canonical_json),
    }


def load_json_dict_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload
