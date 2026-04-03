from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
EXPECTED_PYTHON = ROOT_DIR / "python.exe"
MIN_SUPPORTED_PYTHON = (3, 10)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path.resolve())))


def _expected_python_paths() -> set[str]:
    paths = {_normalized_path(EXPECTED_PYTHON)}
    if not EXPECTED_PYTHON.exists():
        return paths

    try:
        probe = subprocess.run(
            [str(EXPECTED_PYTHON), "-c", "import sys; print(sys.executable)"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return paths

    runtime_path = probe.stdout.strip()
    if runtime_path:
        paths.add(_normalized_path(Path(runtime_path)))
    return paths


def build_python_runtime_warnings(
    current_executable: str | None = None,
    version_info: tuple[int, int, int] | None = None,
) -> list[str]:
    current_path = Path(current_executable or sys.executable)
    current_version = tuple(version_info or sys.version_info[:3])
    warnings: list[str] = []

    if _normalized_path(current_path) not in _expected_python_paths():
        warnings.append(
            "[warning] Unexpected Python interpreter: "
            f"current={current_path.resolve()} expected={EXPECTED_PYTHON.resolve()}. "
            "Use .\\python.exe manage.py ..."
        )

    if current_version < MIN_SUPPORTED_PYTHON:
        warnings.append(
            "[warning] Python version is below the project baseline: "
            f"current={current_version[0]}.{current_version[1]}.{current_version[2]} "
            f"minimum={MIN_SUPPORTED_PYTHON[0]}.{MIN_SUPPORTED_PYTHON[1]}. "
            "Use the repository .\\python.exe interpreter."
        )

    return warnings


def emit_python_runtime_warnings() -> None:
    for warning in build_python_runtime_warnings():
        print(warning, file=sys.stderr)


def run() -> int:
    emit_python_runtime_warnings()

    from v5vc.cli import main

    return main()


if __name__ == "__main__":
    raise SystemExit(run())
