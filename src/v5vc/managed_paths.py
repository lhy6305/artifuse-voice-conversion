from __future__ import annotations

import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


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
