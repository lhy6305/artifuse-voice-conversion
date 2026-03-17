from __future__ import annotations

import json
from pathlib import Path

import torch

from v5vc.offline_mvp.data import load_jsonl, load_waveform
from v5vc.offline_mvp.losses import build_frame_targets

EVENT_DIMENSIONS = [
    "energy_gate",
    "abs_delta_gate",
    "high_zero_cross",
    "low_zero_cross_voiced_like",
    "high_zero_cross_voiced_like",
    "delta_energy_rise",
    "delta_energy_fall",
    "energy_norm",
]

ACOUSTIC_DIMENSIONS = [
    "energy",
    "abs_mean",
    "zero_cross",
    "delta_energy",
]


def analyze_offline_mvp_event_targets(
    split_dir: Path,
    output_dir: Path,
    max_duration_sec: float = 2.0,
    frame_length: int = 400,
    hop_length: int = 160,
) -> dict[str, object]:
    split_dir = split_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = {
        "split_dir": split_dir.as_posix(),
        "frame_length": frame_length,
        "hop_length": hop_length,
        "max_duration_sec": max_duration_sec,
        "event_dimensions": EVENT_DIMENSIONS,
        "acoustic_dimensions": ACOUSTIC_DIMENSIONS,
        "groups": {},
        "notes": [
            "Event targets are derived from the current heuristic build_frame_targets implementation.",
            "Correlations are computed across masked frame-level targets only.",
            "This analysis is intended to detect imbalance, redundancy, and target/source mismatch.",
        ],
    }

    manifest_paths = {
        "target_train": split_dir / "target_train.jsonl",
        "source_train": split_dir / "source_train.jsonl",
    }
    for group_name, manifest_path in manifest_paths.items():
        analysis["groups"][group_name] = analyze_manifest(
            manifest_path=manifest_path,
            max_duration_sec=max_duration_sec,
            frame_length=frame_length,
            hop_length=hop_length,
        )

    analysis["comparison"] = build_group_comparison(
        target_group=analysis["groups"]["target_train"],
        source_group=analysis["groups"]["source_train"],
    )

    json_path = output_dir / "event_target_analysis.json"
    md_path = output_dir / "event_target_analysis.md"
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(analysis), encoding="utf-8")
    return analysis


def analyze_manifest(
    manifest_path: Path,
    max_duration_sec: float,
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    records = load_jsonl(manifest_path)
    event_sum: torch.Tensor | None = None
    acoustic_sum: torch.Tensor | None = None
    corr_samples: list[torch.Tensor] = []
    frame_count = 0

    for record in records:
        waveform, _ = load_waveform(Path(record["audio_path"]), max_duration_sec=max_duration_sec)
        batch = waveform.unsqueeze(0)
        lengths = torch.tensor([waveform.numel()], dtype=torch.long)
        targets = build_frame_targets(
            waveform=batch,
            lengths=lengths,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        mask = targets["frame_mask"][0]
        event = targets["event_target"][0][mask]
        acoustic = targets["acoustic_target"][0][mask]
        if event_sum is None:
            event_sum = event.sum(dim=0)
            acoustic_sum = acoustic.sum(dim=0)
        else:
            event_sum += event.sum(dim=0)
            acoustic_sum += acoustic.sum(dim=0)
        frame_count += int(mask.sum().item())
        corr_samples.append(torch.cat([event, acoustic], dim=-1))

    if event_sum is None or acoustic_sum is None:
        raise ValueError(f"No valid frames found in manifest: {manifest_path}")

    all_samples = torch.cat(corr_samples, dim=0).to(torch.float64)
    centered = all_samples - all_samples.mean(dim=0, keepdim=True)
    covariance = centered.T @ centered / max(1, all_samples.shape[0] - 1)
    std = torch.sqrt(torch.diag(covariance).clamp_min(1e-12))
    corr = covariance / std[:, None] / std[None, :]
    event_vs_acoustic = corr[: len(EVENT_DIMENSIONS), len(EVENT_DIMENSIONS) :].tolist()

    return {
        "manifest_path": manifest_path.resolve().as_posix(),
        "record_count": len(records),
        "frame_count": frame_count,
        "event_mean": [round(value, 6) for value in (event_sum / frame_count).tolist()],
        "acoustic_mean": [round(value, 6) for value in (acoustic_sum / frame_count).tolist()],
        "event_vs_acoustic_corr": [
            [round(value, 6) for value in row]
            for row in event_vs_acoustic
        ],
    }


def build_group_comparison(
    target_group: dict[str, object],
    source_group: dict[str, object],
) -> dict[str, object]:
    target_means = target_group["event_mean"]
    source_means = source_group["event_mean"]
    mean_gaps = []
    for index, event_name in enumerate(EVENT_DIMENSIONS):
        gap = round(float(target_means[index]) - float(source_means[index]), 6)
        mean_gaps.append(
            {
                "event_dimension": event_name,
                "target_mean": float(target_means[index]),
                "source_mean": float(source_means[index]),
                "gap": gap,
            }
        )
    ranked_gaps = sorted(mean_gaps, key=lambda item: abs(item["gap"]), reverse=True)
    return {
        "event_mean_gap_ranked": ranked_gaps,
    }


def render_markdown_report(analysis: dict[str, object]) -> str:
    lines = [
        "# Offline MVP Event Target Analysis",
        "",
        "## Summary",
        "- This report analyzes the current heuristic frame-level event targets used by the offline MVP scaffold.",
        "- The goal is to detect imbalance, redundancy, and target/source mismatch before making the next e_evt plan decision.",
        "",
        "## Event Dimensions",
    ]
    for index, name in enumerate(EVENT_DIMENSIONS):
        lines.append(f"- `{index}`: `{name}`")

    lines.extend(["", "## Group Stats"])
    for group_name, payload in analysis["groups"].items():
        lines.append(f"### `{group_name}`")
        lines.append(f"- record_count: `{payload['record_count']}`")
        lines.append(f"- frame_count: `{payload['frame_count']}`")
        lines.append("- event_mean:")
        for index, value in enumerate(payload["event_mean"]):
            lines.append(f"  - `{EVENT_DIMENSIONS[index]}`: `{value}`")
        lines.append("- acoustic_mean:")
        for index, value in enumerate(payload["acoustic_mean"]):
            lines.append(f"  - `{ACOUSTIC_DIMENSIONS[index]}`: `{value}`")
        lines.append("- event_vs_acoustic_corr:")
        for index, row in enumerate(payload["event_vs_acoustic_corr"]):
            formatted_row = ", ".join(
                f"{ACOUSTIC_DIMENSIONS[column]}={value}"
                for column, value in enumerate(row)
            )
            lines.append(f"  - `{EVENT_DIMENSIONS[index]}`: {formatted_row}")
        lines.append("")

    lines.extend(["## Target/Source Gaps"])
    for item in analysis["comparison"]["event_mean_gap_ranked"]:
        lines.append(
            f"- `{item['event_dimension']}`: target `{item['target_mean']}` vs source `{item['source_mean']}` "
            f"(gap `{item['gap']}`)"
        )

    lines.extend(["", "## Notes"])
    for note in analysis["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
