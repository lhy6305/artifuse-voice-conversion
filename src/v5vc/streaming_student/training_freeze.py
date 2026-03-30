from __future__ import annotations

from typing import Any

import torch


def apply_streaming_student_training_freeze(
    model: torch.nn.Module,
    training_config: dict[str, Any] | None,
) -> tuple[list[torch.nn.Parameter], dict[str, Any]]:
    freeze_config = {}
    if isinstance(training_config, dict):
        freeze_config = training_config.get("freeze") or {}
    if not isinstance(freeze_config, dict):
        freeze_config = {}
    trainable_prefixes = _normalize_prefixes(freeze_config.get("trainable_parameter_prefixes"))
    if not trainable_prefixes:
        trainable_parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
        return trainable_parameters, {
            "enabled": False,
            "mode": "all_trainable",
            "trainable_parameter_prefixes": [],
            "trainable_parameter_count": len(trainable_parameters),
            "frozen_parameter_count": 0,
            "trainable_parameter_names": [name for name, _ in model.named_parameters()],
            "frozen_parameter_names": [],
        }

    trainable_parameters: list[torch.nn.Parameter] = []
    trainable_parameter_names: list[str] = []
    frozen_parameter_names: list[str] = []
    for name, parameter in model.named_parameters():
        is_trainable = _matches_any_prefix(name=name, prefixes=trainable_prefixes)
        parameter.requires_grad_(is_trainable)
        if is_trainable:
            trainable_parameters.append(parameter)
            trainable_parameter_names.append(name)
        else:
            frozen_parameter_names.append(name)
    if not trainable_parameters:
        raise ValueError(
            "training.freeze.trainable_parameter_prefixes matched no parameters."
        )
    return trainable_parameters, {
        "enabled": True,
        "mode": "prefix_allowlist_v1",
        "trainable_parameter_prefixes": trainable_prefixes,
        "trainable_parameter_count": len(trainable_parameter_names),
        "frozen_parameter_count": len(frozen_parameter_names),
        "trainable_parameter_names": trainable_parameter_names,
        "frozen_parameter_names": frozen_parameter_names,
    }


def _normalize_prefixes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        prefix = item.strip()
        if prefix:
            normalized.append(prefix)
    return normalized


def _matches_any_prefix(name: str, prefixes: list[str]) -> bool:
    return any(_name_matches_prefix(name=name, prefix=prefix) for prefix in prefixes)


def _name_matches_prefix(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(f"{prefix}.")
