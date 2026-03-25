from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.event_semantics import (
    build_current_runtime_event_semantics_meta,
    build_teacher_e_evt_v1_targets,
)
from v5vc.offline_teacher_runtime import (
    OfflineMVPTeacherRuntime,
    compare_runtime_outputs,
    resolve_chunk_samples,
    resolve_runtime_device,
    run_full_pass,
    run_streaming_pass,
)
from v5vc.offline_mvp.data import load_waveform
from v5vc.source_acoustic_state_extraction import extract_source_acoustic_state
from v5vc.streaming_student.teacher_labels import resolve_teacher_source
from v5vc.train_entry import instantiate_offline_mvp_model


CONTRACT_VERSION_V1 = "offline_teacher_downstream_control_v1"
CONTRACT_VERSION_V2 = "offline_teacher_downstream_control_v2"
CONTRACT_VERSION_V3 = "offline_teacher_downstream_control_v3"


def export_offline_mvp_teacher_downstream_contract(
    input_audio_path: Path,
    output_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    max_audio_sec: float | None,
    verify_against_full_pass: bool,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_source = resolve_teacher_source(
        route_handoff_path=route_handoff_path,
        experiment_metrics_path=None,
        checkpoint_path=checkpoint_path,
        split_dir=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
    )
    checkpoint_payload = load_checkpoint(Path(resolved_source["checkpoint_path"]))
    checkpoint_config = checkpoint_payload.get("config")
    if not isinstance(checkpoint_config, dict):
        raise ValueError("Teacher checkpoint does not contain a valid config payload.")
    model_config = checkpoint_config.get("model")
    if not isinstance(model_config, dict):
        raise ValueError("Teacher checkpoint config.model is missing.")

    waveform, sample_rate = load_waveform(input_audio_path.resolve(), max_duration_sec=max_audio_sec)
    frame_length = int(model_config["frame_length"])
    hop_length = int(model_config["hop_length"])
    resolved_device = resolve_runtime_device(device)
    effective_chunk_samples = resolve_chunk_samples(
        chunk_samples=chunk_samples,
        chunk_ms=chunk_ms,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    model = instantiate_offline_mvp_model(dict(model_config))
    model.load_state_dict(checkpoint_payload["model_state_dict"])
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    runtime = OfflineMVPTeacherRuntime(
        model=model,
        device=resolved_device,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    streaming_outputs = run_streaming_pass(
        runtime=runtime,
        waveform=waveform,
        chunk_samples=effective_chunk_samples,
        sample_rate=sample_rate,
        hidden_dim=int(model_config["hidden_dim"]),
        z_art_dim=int(model_config["z_art_dim"]),
        event_dim=int(model_config["event_dim"]),
        acoustic_dim=int(model_config["acoustic_dim"]),
    )

    verification = None
    if verify_against_full_pass:
        full_pass_outputs = run_full_pass(
            model=model,
            device=resolved_device,
            waveform=waveform,
        )
        verification = compare_runtime_outputs(
            full_pass_outputs=full_pass_outputs,
            streaming_outputs=streaming_outputs,
        )

    conditioning = load_conditioning_asset(
        calibration_asset_path=calibration_asset_path,
    )
    contract_payload = build_contract_payload(
        input_audio_path=input_audio_path,
        resolved_source=resolved_source,
        waveform=waveform,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
        chunk_samples=effective_chunk_samples,
        device=resolved_device,
        streaming_outputs=streaming_outputs,
        conditioning=conditioning,
        verification=verification,
    )
    tensor_payload = build_tensor_payload(
        input_audio_path=input_audio_path,
        resolved_source=resolved_source,
        waveform=waveform,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
        chunk_samples=effective_chunk_samples,
        streaming_outputs=streaming_outputs,
        conditioning=conditioning,
    )

    tensor_path = output_dir / "teacher_downstream_control_contract.pt"
    json_path = output_dir / "teacher_downstream_control_contract.json"
    md_path = output_dir / "teacher_downstream_control_contract.md"
    torch.save(tensor_payload, tensor_path)
    json_path.write_text(
        json.dumps(contract_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_markdown(contract_payload),
        encoding="utf-8",
        newline="\n",
    )


def load_conditioning_asset(calibration_asset_path: Path | None) -> dict[str, object]:
    if calibration_asset_path is None:
        calibration_asset_path = Path(
            "data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"
        )
    calibration_asset_path = calibration_asset_path.resolve()
    payload = json.loads(calibration_asset_path.read_text(encoding="utf-8"))
    assets = dict(payload.get("conditioning_assets", {}))
    speaker_vector = [float(value) for value in list(assets.get("s_spk_target", {}).get("vector", []))]
    geom_vector = [float(value) for value in list(assets.get("s_geom_target", {}).get("vector", []))]
    alpha_value = float(assets.get("alpha", {}).get("value", 1.0))
    return {
        "asset_path": calibration_asset_path.as_posix(),
        "asset_status": str(payload.get("status", "unknown")),
        "s_spk_target": torch.tensor(speaker_vector, dtype=torch.float32),
        "s_geom_target": torch.tensor(geom_vector, dtype=torch.float32),
        "alpha": float(alpha_value),
        "speaker_dim": len(speaker_vector),
        "geom_dim": len(geom_vector),
    }


def build_contract_payload(
    input_audio_path: Path,
    resolved_source: dict[str, object],
    waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    chunk_samples: int,
    device: torch.device,
    streaming_outputs: dict[str, object],
    conditioning: dict[str, object],
    verification: dict[str, object] | None,
) -> dict[str, object]:
    frame_count = int(streaming_outputs["frame_count"])
    source_acoustic_state = extract_source_acoustic_state(
        waveform=waveform,
        sample_rate=sample_rate,
        frame_start_samples=streaming_outputs["frame_start_samples"].to(torch.long),
        frame_length=frame_length,
    )
    f0_hz = source_acoustic_state["f0_hz"]
    vuv = source_acoustic_state["vuv"]
    aper = source_acoustic_state["aper"]
    energy_control = source_acoustic_state["E"]
    energy_log = streaming_outputs["acoustic"][:, 0]
    zero_cross_rate = streaming_outputs["acoustic"][:, 2]
    event_probs = streaming_outputs["event_probs"]
    teacher_e_evt = build_teacher_e_evt_v1_targets(
        legacy_event_probs=event_probs,
        target_event_semantic_sidecar=None,
        target_event_timing_semantic_sidecar=None,
        valid_frame_count=frame_count,
    )
    e_evt_tensor = teacher_e_evt["tensor"]
    event_semantics_meta = build_current_runtime_event_semantics_meta()
    return {
        "contract_version": CONTRACT_VERSION_V3,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_audio_path": input_audio_path.resolve().as_posix(),
        "teacher": {
            "experiment_id": str(resolved_source["teacher_anchor"]["experiment_id"]),
            "checkpoint_path": Path(resolved_source["checkpoint_path"]).resolve().as_posix(),
            "route_handoff_path": (
                None
                if resolved_source.get("route_handoff_path") is None
                else Path(resolved_source["route_handoff_path"]).resolve().as_posix()
            ),
        },
        "runtime": {
            "device": str(device),
            "sample_rate": int(sample_rate),
            "frame_length": int(frame_length),
            "hop_length": int(hop_length),
            "frame_ms": round(float(frame_length / sample_rate * 1000.0), 6),
            "hop_ms": round(float(hop_length / sample_rate * 1000.0), 6),
            "chunk_samples": int(chunk_samples),
            "chunk_ms": round(float(chunk_samples / sample_rate * 1000.0), 6),
            "frame_count": frame_count,
        },
        "conditioning": {
            "asset_path": conditioning["asset_path"],
            "asset_status": conditioning["asset_status"],
            "speaker_dim": int(conditioning["speaker_dim"]),
            "geom_dim": int(conditioning["geom_dim"]),
            "alpha": round(float(conditioning["alpha"]), 6),
        },
        "source_acoustic_state": {
            "version": source_acoustic_state["version"],
            "aper_version": source_acoustic_state["aper_version"],
            "stats": dict(source_acoustic_state["stats"]),
        },
        "event_semantics": event_semantics_meta,
        "e_evt_semantics": {
            "meta": dict(teacher_e_evt["meta"]),
            "summary": dict(teacher_e_evt["summary"]),
        },
        "provided_keys": {
            "v2_core": [
                "frame_start_ms",
                "z_art",
                "event_probs",
                "f0_hz",
                "vuv",
                "aper",
                "E",
                "conditioning.s_spk_target",
                "conditioning.s_geom_target",
                "conditioning.alpha",
            ],
            "v3_semantic_core": [
                "e_evt",
                "e_evt_meta",
                "e_evt_summary",
            ],
            "v2_optional": [],
            "v2_diagnostic": [
                "event_logits",
                "hidden",
                "fused_hidden",
                "acoustic.energy_log",
                "acoustic.abs_mean",
                "acoustic.zero_cross_rate",
                "acoustic.delta_energy",
            ],
        },
        "derived_proxy_keys": [
            "energy_proxy",
            "voiced_proxy",
            "aperiodicity_proxy",
            "event_presence_proxy",
            "energy_change_proxy",
        ],
        "missing_design_keys": [
            "r_res",
            "final_vocoder_waveform",
        ],
        "summary_stats": {
            "f0_hz": summarize_tensor(f0_hz),
            "vuv": summarize_tensor(vuv),
            "aper": summarize_tensor(aper),
            "E": summarize_tensor(energy_control),
            "energy_log": summarize_tensor(energy_log),
            "zero_cross_rate": summarize_tensor(zero_cross_rate),
            "event_presence_proxy": summarize_tensor(e_evt_tensor.amax(dim=-1, keepdim=True)),
            "voiced_proxy": summarize_tensor(vuv),
            "energy_proxy": summarize_tensor(torch.sigmoid((energy_control + 4.0) * 2.0)),
        },
        "verification": verification,
        "notes": [
            "This contract upgrades the teacher-first downstream packet to the C-prime v2-core baseline plus the first explicit downstream e_evt bridge for the experimental Stage5 route.",
            "f0_hz / vuv / aper / E are produced by a deterministic source acoustic state extraction chain aligned to the teacher runtime frame grid.",
            "aper-v1 is a single scalar per frame in [0, 1], where 0 is more periodic and 1 is more aperiodic; it is intended for the noise branch only.",
            "Current legacy event_probs are still retained as diagnostic compatibility fields and still follow the offline_mvp_heuristic_event_target_v1 label space.",
            "e_evt is now exported explicitly as a downstream bootstrap bridge; because this runtime packet has no target timing sidecar, the boundary-related e_evt dimensions remain zero-filled diagnostics rather than claimed true boundary supervision.",
            "r_res and final_vocoder_waveform remain intentionally absent because Phase C3 stays on the no-res baseline route.",
        ],
    }


def build_tensor_payload(
    input_audio_path: Path,
    resolved_source: dict[str, object],
    waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    chunk_samples: int,
    streaming_outputs: dict[str, object],
    conditioning: dict[str, object],
) -> dict[str, object]:
    source_acoustic_state = extract_source_acoustic_state(
        waveform=waveform,
        sample_rate=sample_rate,
        frame_start_samples=streaming_outputs["frame_start_samples"].to(torch.long),
        frame_length=frame_length,
    )
    acoustic = streaming_outputs["acoustic"].to(torch.float32)
    energy_log = acoustic[:, 0:1]
    abs_mean = acoustic[:, 1:2]
    zero_cross_rate = acoustic[:, 2:3]
    delta_energy = acoustic[:, 3:4]
    event_probs = streaming_outputs["event_probs"].to(torch.float32)
    teacher_e_evt = build_teacher_e_evt_v1_targets(
        legacy_event_probs=event_probs,
        target_event_semantic_sidecar=None,
        target_event_timing_semantic_sidecar=None,
        valid_frame_count=int(event_probs.shape[0]),
    )
    e_evt_tensor = teacher_e_evt["tensor"].to(torch.float32)
    f0_hz = source_acoustic_state["f0_hz"].to(torch.float32)
    vuv = source_acoustic_state["vuv"].to(torch.float32)
    aper = source_acoustic_state["aper"].to(torch.float32)
    energy_control = source_acoustic_state["E"].to(torch.float32)
    event_semantics_meta = build_current_runtime_event_semantics_meta()
    return {
        "contract_version": CONTRACT_VERSION_V3,
        "input_audio_path": input_audio_path.resolve().as_posix(),
        "teacher": {
            "experiment_id": str(resolved_source["teacher_anchor"]["experiment_id"]),
            "checkpoint_path": Path(resolved_source["checkpoint_path"]).resolve().as_posix(),
        },
        "runtime": {
            "sample_rate": int(sample_rate),
            "frame_length": int(frame_length),
            "hop_length": int(hop_length),
            "chunk_samples": int(chunk_samples),
        },
        "frame_start_samples": streaming_outputs["frame_start_samples"].to(torch.long),
        "frame_start_ms": streaming_outputs["frame_start_ms"].to(torch.float32),
        "hidden": streaming_outputs["hidden"].to(torch.float32),
        "fused_hidden": streaming_outputs["fused_hidden"].to(torch.float32),
        "z_art": streaming_outputs["z_art"].to(torch.float32),
        "event_logits": streaming_outputs["event_logits"].to(torch.float32),
        "event_probs": event_probs,
        "event_semantics_meta": event_semantics_meta,
        "e_evt": e_evt_tensor,
        "e_evt_meta": dict(teacher_e_evt["meta"]),
        "e_evt_summary": dict(teacher_e_evt["summary"]),
        "f0_hz": f0_hz,
        "vuv": vuv,
        "aper": aper,
        "E": energy_control,
        "source_acoustic_state_meta": {
            "version": source_acoustic_state["version"],
            "aper_version": source_acoustic_state["aper_version"],
            "stats": dict(source_acoustic_state["stats"]),
        },
        "acoustic": {
            "energy_log": energy_log,
            "abs_mean": abs_mean,
            "zero_cross_rate": zero_cross_rate,
            "delta_energy": delta_energy,
        },
        "derived_proxies": {
            "energy_proxy": torch.sigmoid((energy_control + 4.0) * 2.0),
            "voiced_proxy": vuv,
            "aperiodicity_proxy": aper,
            "event_presence_proxy": e_evt_tensor.amax(dim=-1, keepdim=True),
            "energy_change_proxy": torch.maximum(e_evt_tensor[:, 1:2], e_evt_tensor[:, 2:3]),
        },
        "conditioning": {
            "s_spk_target": conditioning["s_spk_target"].to(torch.float32),
            "s_geom_target": conditioning["s_geom_target"].to(torch.float32),
            "alpha": torch.tensor([float(conditioning["alpha"])], dtype=torch.float32),
        },
    }


def summarize_tensor(tensor: torch.Tensor) -> dict[str, float]:
    if tensor.numel() == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(float(tensor.mean().item()), 6),
        "std": round(float(tensor.std(unbiased=False).item()), 6),
        "min": round(float(tensor.min().item()), 6),
        "max": round(float(tensor.max().item()), 6),
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP Teacher Downstream Control Contract",
        "",
        f"- contract_version: {summary['contract_version']}",
        f"- generated_at: {summary['generated_at']}",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- teacher: {json.dumps(summary['teacher'], ensure_ascii=False)}",
        f"- runtime: {json.dumps(summary['runtime'], ensure_ascii=False)}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- source_acoustic_state: {json.dumps(summary.get('source_acoustic_state', {}), ensure_ascii=False)}",
        f"- event_semantics: {json.dumps(summary.get('event_semantics', {}), ensure_ascii=False)}",
        f"- e_evt_semantics: {json.dumps(summary.get('e_evt_semantics', {}), ensure_ascii=False)}",
        "",
        "## Keys",
        f"- provided_keys: {json.dumps(summary['provided_keys'], ensure_ascii=False)}",
        f"- derived_proxy_keys: {json.dumps(summary['derived_proxy_keys'], ensure_ascii=False)}",
        f"- missing_design_keys: {json.dumps(summary['missing_design_keys'], ensure_ascii=False)}",
        "",
        "## Summary Stats",
    ]
    for key, payload in dict(summary["summary_stats"]).items():
        lines.append(f"- {key}: {json.dumps(payload, ensure_ascii=False)}")
    verification = summary.get("verification")
    if isinstance(verification, dict):
        lines.extend(
            [
                "",
                "## Verification",
                f"- frame_count_equal: {verification.get('frame_count_equal')}",
                f"- frame_alignment_equal: {verification.get('frame_alignment_equal')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Notes",
        ]
    )
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
