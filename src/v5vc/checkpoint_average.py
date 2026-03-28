from __future__ import annotations

import json
import re
from pathlib import Path

import torch


STEP_PATTERN = re.compile(r"\.step(\d+)\.pt$", re.IGNORECASE)


def average_offline_mvp_checkpoints(
    checkpoint_paths: list[Path],
    output_dir: Path,
    output_name: str,
) -> None:
    if len(checkpoint_paths) < 2:
        raise ValueError("Checkpoint averaging requires at least two --checkpoints values.")
    resolved_paths = [path.resolve() for path in checkpoint_paths]
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded_checkpoints = [load_checkpoint(path) for path in resolved_paths]
    state_dicts = [extract_model_state_dict(checkpoint, path) for checkpoint, path in zip(loaded_checkpoints, resolved_paths)]
    averaged_state_dict = average_state_dicts(state_dicts=state_dicts, checkpoint_paths=resolved_paths)
    step_values = [infer_checkpoint_step(path) for path in resolved_paths]

    output_checkpoint_path = (output_dir / f"{output_name}.pt").resolve()
    output_payload = {
        "experiment_id": f"averaged__{output_name}",
        "model_state_dict": averaged_state_dict,
        "config": loaded_checkpoints[0].get("config"),
        "step": None if any(step is None for step in step_values) else int(sum(step_values) / len(step_values)),
        "source_checkpoint_paths": [path.as_posix() for path in resolved_paths],
        "source_steps": step_values,
        "averaging": {
            "mode": "uniform_mean",
            "checkpoint_count": len(resolved_paths),
        },
    }
    torch.save(output_payload, output_checkpoint_path)

    summary = {
        "output_checkpoint_path": output_checkpoint_path.as_posix(),
        "checkpoint_count": len(resolved_paths),
        "source_checkpoint_paths": [path.as_posix() for path in resolved_paths],
        "source_steps": step_values,
        "mode": "uniform_mean",
        "notes": [
            "Floating-point tensors are averaged elementwise across checkpoints.",
            "Non-floating tensors and non-tensor metadata are copied from the first checkpoint after equality validation.",
        ],
    }
    (output_dir / f"{output_name}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / f"{output_name}.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def load_checkpoint(path: Path) -> dict[str, object]:
    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        checkpoint = torch.load(path, map_location="cpu")
    if not isinstance(checkpoint, dict):
        raise TypeError(f"Unsupported checkpoint payload type: {type(checkpoint)!r}")
    return checkpoint


def extract_model_state_dict(checkpoint: dict[str, object], checkpoint_path: Path) -> dict[str, torch.Tensor]:
    state_dict = checkpoint.get("model_state_dict")
    if not isinstance(state_dict, dict):
        raise ValueError(f"Checkpoint missing model_state_dict: {checkpoint_path}")
    return state_dict


def average_state_dicts(
    state_dicts: list[dict[str, torch.Tensor]],
    checkpoint_paths: list[Path],
) -> dict[str, torch.Tensor]:
    reference_keys = list(state_dicts[0].keys())
    for state_dict, checkpoint_path in zip(state_dicts[1:], checkpoint_paths[1:]):
        if list(state_dict.keys()) != reference_keys:
            raise ValueError(f"State dict keys do not match reference checkpoint: {checkpoint_path}")

    averaged: dict[str, torch.Tensor] = {}
    for key in reference_keys:
        values = [state_dict[key] for state_dict in state_dicts]
        first_value = values[0]
        if not isinstance(first_value, torch.Tensor):
            raise TypeError(f"Unsupported non-tensor state value for key {key!r}")
        if first_value.dtype.is_floating_point:
            stacked = torch.stack([value.detach().cpu().to(torch.float32) for value in values], dim=0)
            averaged_value = stacked.mean(dim=0).to(dtype=first_value.dtype)
            averaged[key] = averaged_value
            continue
        for value in values[1:]:
            if not torch.equal(first_value, value):
                raise ValueError(f"Non-floating tensor mismatch for key {key!r}")
        averaged[key] = first_value.detach().cpu().clone()
    return averaged


def infer_checkpoint_step(path: Path) -> int | None:
    match = STEP_PATTERN.search(path.name)
    if match is None:
        return None
    return int(match.group(1))


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# offline MVP checkpoint averaging",
        "",
        f"- output_checkpoint_path: {summary['output_checkpoint_path']}",
        f"- checkpoint_count: {summary['checkpoint_count']}",
        f"- source_steps: {summary['source_steps']}",
        f"- mode: {summary['mode']}",
        "",
        "## source checkpoints",
    ]
    for checkpoint_path in summary["source_checkpoint_paths"]:
        lines.append(f"- {checkpoint_path}")
    lines.extend(
        [
            "",
            "## notes",
        ]
    )
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
