from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


def load_streaming_student_init_checkpoint(
    model: torch.nn.Module,
    checkpoint_path: Path,
    allow_partial: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved_checkpoint_path = checkpoint_path.resolve()
    payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    model_state_dict = payload.get("model_state_dict")
    if not isinstance(model_state_dict, dict):
        raise ValueError(f"Init checkpoint missing model_state_dict: {resolved_checkpoint_path}")
    missing_keys: list[str] = []
    unexpected_keys: list[str] = []
    skipped_shape_mismatch_keys: list[str] = []
    if allow_partial:
        current_state_dict = model.state_dict()
        filtered_model_state_dict: dict[str, Any] = {}
        for key, value in model_state_dict.items():
            if key not in current_state_dict:
                continue
            current_value = current_state_dict[key]
            if (
                isinstance(value, torch.Tensor)
                and isinstance(current_value, torch.Tensor)
                and tuple(value.shape) != tuple(current_value.shape)
            ):
                skipped_shape_mismatch_keys.append(key)
                continue
            filtered_model_state_dict[key] = value
        incompatible_keys = model.load_state_dict(filtered_model_state_dict, strict=False)
        missing_keys = list(incompatible_keys.missing_keys)
        unexpected_keys = list(incompatible_keys.unexpected_keys)
    else:
        model.load_state_dict(model_state_dict)
    summary = {
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "allow_partial": bool(allow_partial),
        "missing_key_count": len(missing_keys),
        "unexpected_key_count": len(unexpected_keys),
        "skipped_shape_mismatch_key_count": len(skipped_shape_mismatch_keys),
        "missing_keys": missing_keys,
        "unexpected_keys": unexpected_keys,
        "skipped_shape_mismatch_keys": skipped_shape_mismatch_keys,
        "matched_exactly": (
            len(missing_keys) == 0
            and len(unexpected_keys) == 0
            and len(skipped_shape_mismatch_keys) == 0
        ),
    }
    return payload, summary
