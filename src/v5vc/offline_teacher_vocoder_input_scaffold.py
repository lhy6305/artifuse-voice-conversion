from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch


def build_offline_mvp_teacher_vocoder_input_scaffold(
    contract_path: Path,
    output_dir: Path,
) -> None:
    contract_path = contract_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = torch.load(contract_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported contract payload type: {type(payload)!r}")
    if str(payload.get("contract_version")) != "offline_teacher_downstream_control_v1":
        raise ValueError(
            "Unsupported contract_version for teacher vocoder input scaffold: "
            f"{payload.get('contract_version')!r}"
        )

    frame_start_ms = payload["frame_start_ms"].to(torch.float32)
    z_art = payload["z_art"].to(torch.float32)
    event_probs = payload["event_probs"].to(torch.float32)
    acoustic = dict(payload["acoustic"])
    derived = dict(payload["derived_proxies"])
    conditioning = dict(payload["conditioning"])

    energy_proxy = derived["energy_proxy"].to(torch.float32)
    voiced_proxy = derived["voiced_proxy"].to(torch.float32)
    aperiodicity_proxy = derived["aperiodicity_proxy"].to(torch.float32)
    event_presence_proxy = derived["event_presence_proxy"].to(torch.float32)
    energy_change_proxy = derived["energy_change_proxy"].to(torch.float32)

    speaker_embedding = conditioning["s_spk_target"].to(torch.float32)
    geom_embedding = conditioning["s_geom_target"].to(torch.float32)
    alpha = conditioning["alpha"].to(torch.float32)

    frame_count = int(frame_start_ms.shape[0])
    speaker_broadcast = speaker_embedding.unsqueeze(0).expand(frame_count, -1)
    geom_broadcast = geom_embedding.unsqueeze(0).expand(frame_count, -1)
    alpha_broadcast = alpha.view(1, 1).expand(frame_count, 1)
    missing_f0_hz = torch.zeros((frame_count, 1), dtype=torch.float32)
    missing_r_res = torch.zeros((frame_count, 0), dtype=torch.float32)

    periodic_branch_features = torch.cat(
        [
            z_art,
            voiced_proxy,
            energy_proxy,
            alpha_broadcast,
            speaker_broadcast,
            geom_broadcast,
        ],
        dim=-1,
    )
    noise_branch_features = torch.cat(
        [
            event_probs,
            aperiodicity_proxy,
            event_presence_proxy,
            energy_change_proxy,
            energy_proxy,
            alpha_broadcast,
            speaker_broadcast,
        ],
        dim=-1,
    )

    scaffold_payload = {
        "scaffold_version": "offline_teacher_vocoder_input_scaffold_v1",
        "source_contract_path": contract_path.as_posix(),
        "source_contract_version": str(payload["contract_version"]),
        "source_audio_path": payload.get("input_audio_path"),
        "source_teacher": dict(payload.get("teacher", {})),
        "source_runtime": dict(payload.get("runtime", {})),
        "frame_start_ms": frame_start_ms,
        "frame_count": frame_count,
        "available_controls": {
            "z_art": z_art,
            "event_probs": event_probs,
            "energy_log": acoustic["energy_log"].to(torch.float32),
            "abs_mean": acoustic["abs_mean"].to(torch.float32),
            "zero_cross_rate": acoustic["zero_cross_rate"].to(torch.float32),
            "delta_energy": acoustic["delta_energy"].to(torch.float32),
            "energy_proxy": energy_proxy,
            "voiced_proxy": voiced_proxy,
            "aperiodicity_proxy": aperiodicity_proxy,
            "event_presence_proxy": event_presence_proxy,
            "energy_change_proxy": energy_change_proxy,
        },
        "conditioning": {
            "s_spk_target": speaker_embedding,
            "s_geom_target": geom_embedding,
            "alpha": alpha,
        },
        "stage5_requested_but_missing": {
            "f0_hz": missing_f0_hz,
            "r_res": missing_r_res,
        },
        "branch_scaffold": {
            "periodic_branch_features": periodic_branch_features,
            "noise_branch_features": noise_branch_features,
            "periodic_feature_semantics": [
                "z_art",
                "voiced_proxy",
                "energy_proxy",
                "alpha",
                "s_spk_target",
                "s_geom_target",
            ],
            "noise_feature_semantics": [
                "event_probs",
                "aperiodicity_proxy",
                "event_presence_proxy",
                "energy_change_proxy",
                "energy_proxy",
                "alpha",
                "s_spk_target",
            ],
            "missing_periodic_design_keys": ["f0_hz"],
            "missing_noise_design_keys": ["r_res"],
        },
    }

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "contract_path": contract_path.as_posix(),
        "scaffold_version": "offline_teacher_vocoder_input_scaffold_v1",
        "source_audio_path": payload.get("input_audio_path"),
        "source_runtime": dict(payload.get("runtime", {})),
        "frame_count": frame_count,
        "periodic_branch_feature_dim": int(periodic_branch_features.shape[-1]),
        "noise_branch_feature_dim": int(noise_branch_features.shape[-1]),
        "available_controls": {
            "z_art_dim": int(z_art.shape[-1]),
            "event_dim": int(event_probs.shape[-1]),
            "speaker_dim": int(speaker_embedding.shape[-1]),
            "geom_dim": int(geom_embedding.shape[-1]),
        },
        "missing_design_keys": {
            "periodic_branch": ["f0_hz"],
            "noise_branch": ["r_res"],
            "global": ["final_vocoder_waveform"],
        },
        "notes": [
            "This scaffold is a consumer-side adapter for the current teacher-first contract, not a real vocoder implementation.",
            "periodic_branch_features uses voiced_proxy and energy_proxy instead of final f0_hz/vuv/E semantics.",
            "noise_branch_features uses aperiodicity_proxy and event_probs, but r_res remains unavailable in the current teacher path.",
        ],
    }

    pt_path = output_dir / "teacher_vocoder_input_scaffold.pt"
    json_path = output_dir / "teacher_vocoder_input_scaffold.json"
    md_path = output_dir / "teacher_vocoder_input_scaffold.md"
    torch.save(scaffold_payload, pt_path)
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP Teacher Vocoder Input Scaffold",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- contract_path: {summary['contract_path']}",
        f"- scaffold_version: {summary['scaffold_version']}",
        f"- source_audio_path: {summary['source_audio_path']}",
        f"- source_runtime: {json.dumps(summary['source_runtime'], ensure_ascii=False)}",
        f"- frame_count: {summary['frame_count']}",
        f"- periodic_branch_feature_dim: {summary['periodic_branch_feature_dim']}",
        f"- noise_branch_feature_dim: {summary['noise_branch_feature_dim']}",
        f"- available_controls: {json.dumps(summary['available_controls'], ensure_ascii=False)}",
        f"- missing_design_keys: {json.dumps(summary['missing_design_keys'], ensure_ascii=False)}",
        "",
        "## Notes",
    ]
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
