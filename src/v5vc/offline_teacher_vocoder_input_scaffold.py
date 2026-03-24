from __future__ import annotations

from datetime import datetime
import json
import math
from pathlib import Path

import torch


SUPPORTED_CONTRACT_VERSIONS = {
    "offline_teacher_downstream_control_v1",
    "offline_teacher_downstream_control_v2",
}
DEFAULT_STAGE5_F0_FLOOR_HZ = 50.0
DEFAULT_STAGE5_F0_CEIL_HZ = 550.0
DEFAULT_STAGE5_ENERGY_LOG10_FLOOR = -3.8
DEFAULT_STAGE5_ENERGY_LOG10_CEIL = -0.8


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
    contract_version = str(payload.get("contract_version"))
    if contract_version not in SUPPORTED_CONTRACT_VERSIONS:
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
    source_acoustic_state_meta = dict(payload.get("source_acoustic_state_meta", {}))
    source_acoustic_state_stats = dict(source_acoustic_state_meta.get("stats", {}))

    energy_proxy = derived["energy_proxy"].to(torch.float32)
    voiced_proxy = derived["voiced_proxy"].to(torch.float32)
    aperiodicity_proxy = derived["aperiodicity_proxy"].to(torch.float32)
    event_presence_proxy = derived["event_presence_proxy"].to(torch.float32)
    energy_change_proxy = derived["energy_change_proxy"].to(torch.float32)
    f0_hz = payload.get("f0_hz")
    vuv = payload.get("vuv")
    aper = payload.get("aper")
    energy_control = payload.get("E")
    has_v2_core = (
        contract_version == "offline_teacher_downstream_control_v2"
        and isinstance(f0_hz, torch.Tensor)
        and isinstance(vuv, torch.Tensor)
        and isinstance(aper, torch.Tensor)
        and isinstance(energy_control, torch.Tensor)
    )
    if has_v2_core:
        f0_hz = f0_hz.to(torch.float32)
        vuv = vuv.to(torch.float32)
        aper = aper.to(torch.float32)
        energy_control = energy_control.to(torch.float32)
        normalized_f0_hz = normalize_f0_hz_for_stage5(
            f0_hz,
            f0_floor_hz=resolve_positive_float(
                source_acoustic_state_stats.get("f0_floor_hz"),
                DEFAULT_STAGE5_F0_FLOOR_HZ,
            ),
            f0_ceil_hz=resolve_positive_float(
                source_acoustic_state_stats.get("f0_ceil_hz"),
                DEFAULT_STAGE5_F0_CEIL_HZ,
            ),
        )
        normalized_energy_control = normalize_energy_log_rms_for_stage5(energy_control)
    else:
        f0_hz = None
        vuv = None
        aper = None
        energy_control = None
        normalized_f0_hz = None
        normalized_energy_control = None

    speaker_embedding = conditioning["s_spk_target"].to(torch.float32)
    geom_embedding = conditioning["s_geom_target"].to(torch.float32)
    alpha = conditioning["alpha"].to(torch.float32)

    frame_count = int(frame_start_ms.shape[0])
    speaker_broadcast = speaker_embedding.unsqueeze(0).expand(frame_count, -1)
    geom_broadcast = geom_embedding.unsqueeze(0).expand(frame_count, -1)
    alpha_broadcast = alpha.view(1, 1).expand(frame_count, 1)
    missing_r_res = torch.zeros((frame_count, 0), dtype=torch.float32)
    if has_v2_core:
        periodic_branch_features = torch.cat(
            [
                z_art,
                normalized_f0_hz,
                vuv,
                normalized_energy_control,
                alpha_broadcast,
                speaker_broadcast,
                geom_broadcast,
            ],
            dim=-1,
        )
        noise_branch_features = torch.cat(
            [
                event_probs,
                aper,
                vuv,
                normalized_energy_control,
                alpha_broadcast,
                speaker_broadcast,
                geom_broadcast,
            ],
            dim=-1,
        )
        periodic_feature_semantics = [
            "z_art",
            "f0_hz_log_norm",
            "vuv",
            "E_log_rms_norm",
            "alpha",
            "s_spk_target",
            "s_geom_target",
        ]
        noise_feature_semantics = [
            "event_probs",
            "aper",
            "vuv",
            "E_log_rms_norm",
            "alpha",
            "s_spk_target",
            "s_geom_target",
        ]
        missing_periodic_design_keys: list[str] = []
        missing_noise_design_keys = ["r_res"]
        stage5_requested_but_missing = {
            "r_res": missing_r_res,
        }
    else:
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
        periodic_feature_semantics = [
            "z_art",
            "voiced_proxy",
            "energy_proxy",
            "alpha",
            "s_spk_target",
            "s_geom_target",
        ]
        noise_feature_semantics = [
            "event_probs",
            "aperiodicity_proxy",
            "event_presence_proxy",
            "energy_change_proxy",
            "energy_proxy",
            "alpha",
            "s_spk_target",
        ]
        missing_periodic_design_keys = ["f0_hz"]
        missing_noise_design_keys = ["r_res"]
        stage5_requested_but_missing = {
            "f0_hz": torch.zeros((frame_count, 1), dtype=torch.float32),
            "r_res": missing_r_res,
        }

    scaffold_payload = {
        "scaffold_version": (
            "offline_teacher_vocoder_input_scaffold_v2"
            if has_v2_core
            else "offline_teacher_vocoder_input_scaffold_v1"
        ),
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
            **(
                {}
                if not has_v2_core
                else {
                    "f0_hz": f0_hz,
                    "f0_hz_log_norm": normalized_f0_hz,
                    "vuv": vuv,
                    "aper": aper,
                    "E": energy_control,
                    "E_log_rms_norm": normalized_energy_control,
                }
            ),
        },
        "conditioning": {
            "s_spk_target": speaker_embedding,
            "s_geom_target": geom_embedding,
            "alpha": alpha,
        },
        "stage5_requested_but_missing": stage5_requested_but_missing,
        "branch_scaffold": {
            "periodic_branch_features": periodic_branch_features,
            "noise_branch_features": noise_branch_features,
            "periodic_feature_semantics": periodic_feature_semantics,
            "noise_feature_semantics": noise_feature_semantics,
            "missing_periodic_design_keys": missing_periodic_design_keys,
            "missing_noise_design_keys": missing_noise_design_keys,
        },
    }

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "contract_path": contract_path.as_posix(),
        "scaffold_version": str(scaffold_payload["scaffold_version"]),
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
            **(
                {}
                if not has_v2_core
                else {
                    "f0_hz_dim": int(f0_hz.shape[-1]),
                    "f0_hz_log_norm_dim": int(normalized_f0_hz.shape[-1]),
                    "vuv_dim": int(vuv.shape[-1]),
                    "aper_dim": int(aper.shape[-1]),
                    "E_dim": int(energy_control.shape[-1]),
                    "E_log_rms_norm_dim": int(normalized_energy_control.shape[-1]),
                }
            ),
        },
        "missing_design_keys": {
            "periodic_branch": list(missing_periodic_design_keys),
            "noise_branch": ["r_res"],
            "global": ["final_vocoder_waveform"],
        },
        "notes": (
            [
                "This scaffold is a consumer-side adapter for the C-prime v2-core contract rather than a final vocoder implementation.",
                "periodic_branch_features now consume explicit f0_hz / vuv / E semantics through bounded consumer-side normalizations rather than raw Hz/log-RMS magnitudes.",
                "noise_branch_features now consume aper / vuv / normalized E together with event_probs, while r_res remains intentionally absent on the no-res baseline route.",
            ]
            if has_v2_core
            else [
                "This scaffold is a consumer-side adapter for the current teacher-first contract, not a real vocoder implementation.",
                "periodic_branch_features uses voiced_proxy and energy_proxy instead of final f0_hz/vuv/E semantics.",
                "noise_branch_features uses aperiodicity_proxy and event_probs, but r_res remains unavailable in the current teacher path.",
            ]
        ),
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


def resolve_positive_float(value: object, default: float) -> float:
    try:
        resolved = float(value)
    except (TypeError, ValueError):
        return float(default)
    if not math.isfinite(resolved) or resolved <= 0.0:
        return float(default)
    return resolved


def normalize_f0_hz_for_stage5(
    f0_hz: torch.Tensor,
    *,
    f0_floor_hz: float = DEFAULT_STAGE5_F0_FLOOR_HZ,
    f0_ceil_hz: float = DEFAULT_STAGE5_F0_CEIL_HZ,
) -> torch.Tensor:
    f0_tensor = f0_hz.to(torch.float32)
    positive_mask = f0_tensor > 0.0
    safe_floor_hz = max(float(f0_floor_hz), 1.0)
    safe_ceil_hz = max(float(f0_ceil_hz), safe_floor_hz * 1.01)
    safe_f0 = torch.where(positive_mask, f0_tensor.clamp_min(safe_floor_hz), torch.full_like(f0_tensor, safe_floor_hz))
    denominator = math.log2(safe_ceil_hz / safe_floor_hz)
    normalized = torch.log2(safe_f0 / safe_floor_hz) / max(denominator, 1.0e-6)
    return torch.where(positive_mask, normalized, torch.zeros_like(normalized)).clamp(0.0, 1.0)


def normalize_energy_log_rms_for_stage5(
    energy_control: torch.Tensor,
    *,
    silence_floor_log10: float = DEFAULT_STAGE5_ENERGY_LOG10_FLOOR,
    active_ceiling_log10: float = DEFAULT_STAGE5_ENERGY_LOG10_CEIL,
) -> torch.Tensor:
    energy_tensor = energy_control.to(torch.float32)
    denominator = max(float(active_ceiling_log10) - float(silence_floor_log10), 1.0e-6)
    return ((energy_tensor - float(silence_floor_log10)) / denominator).clamp(0.0, 1.0)


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
