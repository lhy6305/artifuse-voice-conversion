from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

import torch

from v5vc.artifact_reuse import (
    build_file_fingerprint,
    load_json_dict_if_exists,
)
from v5vc.offline_vocoder_training import (
    DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
    DEFAULT_STAGE5_SEMANTIC_CONSUMER_MODE,
    build_offline_mvp_nores_vocoder_training_package,
    compute_path_size_bytes,
    load_training_package_payload,
    safe_record_id,
    summarize_dataset_package_index,
)


STREAMING_STUDENT_VOCODER_INPUT_SCAFFOLD_VERSION = "streaming_student_vocoder_input_scaffold_v1"
STREAMING_STUDENT_STAGE5_DATASET_INDEX_VERSION = "streaming_student_stage5_dataset_index_v1"
STREAMING_STUDENT_STAGE5_PACKAGE_REUSE_SIGNATURE_VERSION = (
    "streaming_student_stage5_package_reuse_signature_v1"
)
SUPPORTED_STAGE5_NOISE_EVENT_FAMILIES = {
    "e_evt",
    "legacy_event_probs",
}


def build_streaming_student_stage5_dataset_packages(
    packet_export_path: Path,
    output_dir: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    semantic_consumer_mode: str = DEFAULT_STAGE5_SEMANTIC_CONSUMER_MODE,
    target_contract_mode: str = DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
    noise_event_family: str = "e_evt",
    skip_existing: bool = False,
) -> None:
    packet_export_path = packet_export_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_noise_event_family = normalize_stage5_noise_event_family(noise_event_family)
    export_summary = json.loads(packet_export_path.read_text(encoding="utf-8"))
    selected_records = select_packet_export_records(
        records=list(export_summary.get("records", [])),
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not selected_records:
        raise ValueError("No records selected from streaming student downstream control packet export.")

    started = perf_counter()
    packages_dir = output_dir / "packages"
    package_entries: list[dict[str, object]] = []

    for record in selected_records:
        record_started = perf_counter()
        record_id = str(record["record_id"])
        packet_path = Path(str(record["packet_path"])).resolve()
        packet_payload = torch.load(packet_path, map_location="cpu", weights_only=False)
        if not isinstance(packet_payload, dict):
            raise TypeError(f"Unsupported streaming student packet payload type: {type(packet_payload)!r}")
        target_audio_path = Path(str(record["audio_path"])).resolve()
        record_dir = packages_dir / str(split_name) / safe_record_id(record_id)
        scaffold_dir = record_dir / "scaffold"
        targets_dir = record_dir / "train_targets"
        package_path = targets_dir / "offline_mvp_nores_vocoder_train_targets.pt"
        signature_path = targets_dir / "offline_mvp_nores_vocoder_train_targets.reuse_signature.json"
        expected_signature = build_streaming_student_stage5_package_reuse_signature(
            record_id=record_id,
            packet_path=packet_path,
            target_audio_path=target_audio_path,
            semantic_consumer_mode=str(semantic_consumer_mode),
            target_contract_mode=str(target_contract_mode),
            noise_event_family=resolved_noise_event_family,
        )
        package_reused = should_reuse_existing_streaming_student_stage5_package(
            package_path=package_path,
            signature_path=signature_path,
            skip_existing=skip_existing,
            expected_signature=expected_signature,
            target_audio_path=target_audio_path,
            semantic_consumer_mode=str(semantic_consumer_mode),
            target_contract_mode=str(target_contract_mode),
        )
        if not package_reused:
            build_streaming_student_vocoder_input_scaffold(
                packet_path=packet_path,
                output_dir=scaffold_dir,
                noise_event_family=resolved_noise_event_family,
            )
            build_offline_mvp_nores_vocoder_training_package(
                scaffold_path=scaffold_dir / "streaming_student_vocoder_input_scaffold.pt",
                target_audio_path=target_audio_path,
                output_dir=targets_dir,
                harmonic_bins=32,
                noise_bins=32,
                sample_rate=None,
                frame_length=None,
                hop_length=None,
                target_event_semantic_sidecar=None,
                target_event_timing_semantic_sidecar=None,
                source_semantic_parity_sidecar=None,
                semantic_consumer_mode=semantic_consumer_mode,
                target_contract_mode=target_contract_mode,
            )
            signature_path.write_text(
                json.dumps(expected_signature, ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )
        package_payload = load_training_package_payload(package_path)
        package_entries.append(
            {
                "record_id": record_id,
                "audio_path": target_audio_path.as_posix(),
                "source_audio_path": target_audio_path.as_posix(),
                "target_audio_path": target_audio_path.as_posix(),
                "source_record_id": record_id,
                "target_record_id": record_id,
                "record_mode": "stage3_student_target_self_decode",
                "duration_sec": resolve_duration_sec(packet_payload),
                "split_name": str(split_name),
                "packet_path": packet_path.as_posix(),
                "training_package_path": package_path.as_posix(),
                "training_package_version": str(package_payload.get("training_package_version", "unknown")),
                "source_scaffold_version": str(package_payload.get("source_scaffold_version", "unknown")),
                "target_event_semantic_sidecar_present": False,
                "target_semantic_overview": dict(package_payload.get("target_semantic_overview", {})),
                "target_event_timing_semantic_sidecar_present": False,
                "target_timing_semantic_overview": dict(package_payload.get("target_timing_semantic_overview", {})),
                "source_semantic_parity_sidecar_present": False,
                "source_semantic_parity_overview": dict(package_payload.get("source_semantic_parity_overview", {})),
                "semantic_consumer": dict(package_payload.get("semantic_consumer", {})),
                "target_contract": dict(package_payload.get("target_contract", {})),
                "frame_count": int(package_payload["frame_count"]),
                "periodic_input_dim": int(package_payload["inputs"]["periodic_branch_features"].shape[-1]),
                "noise_input_dim": int(package_payload["inputs"]["noise_branch_features"].shape[-1]),
                "harmonic_target_dim": int(package_payload["targets"]["harmonic_envelope_target"].shape[-1]),
                "noise_target_dim": int(package_payload["targets"]["noise_envelope_target"].shape[-1]),
                "package_size_bytes": int(compute_path_size_bytes(record_dir)),
                "package_build_sec": round(perf_counter() - record_started, 6),
                "package_status": "reused_existing" if package_reused else "built_now",
            }
        )

    normalized_split_name = str(split_name).strip().lower()
    if normalized_split_name not in {"train", "validation"}:
        raise ValueError("split_name must be train or validation for Stage5 export compatibility.")
    train_packages = package_entries if normalized_split_name == "train" else []
    validation_packages = package_entries if normalized_split_name == "validation" else []
    package_summary = summarize_dataset_package_index(
        train_packages=train_packages,
        validation_packages=validation_packages,
        run_duration_sec=perf_counter() - started,
    )
    summary = {
        "dataset_index_version": STREAMING_STUDENT_STAGE5_DATASET_INDEX_VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "packet_export_path": packet_export_path.as_posix(),
        "selection_mode": "packet_export_order",
        "split_name": normalized_split_name,
        "semantic_consumer_mode": str(semantic_consumer_mode),
        "target_contract_mode": str(target_contract_mode),
        "noise_event_family": resolved_noise_event_family,
        "train_packages": train_packages,
        "validation_packages": validation_packages,
        "summary": package_summary,
        "notes": [
            "This dataset index is a minimal Stage5 decode bridge built from Stage3 student_control_packet exports.",
            "Each package is target-self reconstruction only: the student packet and aligned target audio come from the same target-side record.",
            f"noise_event_family={resolved_noise_event_family} controls whether the synthetic Stage5 noise-branch first 8 dims use student e_evt or legacy_event_probs.",
            "This route is for fail-fast decoded.wav export against existing Stage5 no-res checkpoints, not a new Stage5 training baseline.",
        ],
    }
    json_path = output_dir / "streaming_student_stage5_dataset_index.json"
    md_path = output_dir / "streaming_student_stage5_dataset_index.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(build_dataset_markdown(summary), encoding="utf-8", newline="\n")


def build_streaming_student_vocoder_input_scaffold(
    packet_path: Path,
    output_dir: Path,
    noise_event_family: str = "e_evt",
) -> None:
    packet_path = packet_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_noise_event_family = normalize_stage5_noise_event_family(noise_event_family)
    payload = torch.load(packet_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported streaming student packet payload type: {type(payload)!r}")
    if str(payload.get("packet_version")) != "streaming_student_downstream_control_v1":
        raise ValueError(f"Unsupported packet_version: {payload.get('packet_version')!r}")

    controls = dict(payload["controls"])
    conditioning = dict(payload["conditioning"])
    fine_structure_reference = dict(payload.get("fine_structure_reference", {}))
    fine_structure_code = dict(payload.get("fine_structure_code", {}))
    control_contract = dict(payload.get("control_contract", {}))
    e_evt_meta = dict(control_contract.get("e_evt_meta", {}))
    frame_start_ms = payload["frame_start_ms"].to(torch.float32)
    frame_count = int(frame_start_ms.shape[0])
    z_art = controls["z_art"].to(torch.float32)
    event_probs = controls["legacy_event_probs"].to(torch.float32)
    e_evt = controls["e_evt"].to(torch.float32)
    noise_event_tensor = e_evt if resolved_noise_event_family == "e_evt" else event_probs
    f0_hz = controls["f0_hz_calibrated"].to(torch.float32)
    f0_hz_log_norm = controls["f0_hz_stage5_norm"].to(torch.float32)
    vuv = controls["vuv_prob"].to(torch.float32).clamp(0.0, 1.0)
    aper = controls["aper_prob_calibrated"].to(torch.float32).clamp(0.0, 1.0)
    energy_log = controls["energy_log"].to(torch.float32)
    energy_norm = controls["energy_stage5_norm_calibrated"].to(torch.float32).clamp(0.0, 1.0)
    speaker_embedding = conditioning["speaker_embedding"].to(torch.float32)
    geom_embedding = conditioning["geom_embedding"].to(torch.float32)
    alpha = conditioning["alpha"].to(torch.float32).view(1)
    speaker_broadcast = speaker_embedding.unsqueeze(0).expand(frame_count, -1)
    geom_broadcast = geom_embedding.unsqueeze(0).expand(frame_count, -1)
    alpha_broadcast = alpha.view(1, 1).expand(frame_count, 1)

    event_presence_proxy = build_event_presence_proxy_from_e_evt(noise_event_tensor).to(torch.float32)
    delta_energy = torch.zeros_like(energy_log)
    if frame_count > 1:
        delta_energy[1:] = energy_log[1:] - energy_log[:-1]
    zero_like_energy = torch.zeros_like(energy_log)

    periodic_branch_features = torch.cat(
        [z_art, f0_hz_log_norm, vuv, energy_norm, alpha_broadcast, speaker_broadcast, geom_broadcast],
        dim=-1,
    )
    noise_branch_features = torch.cat(
        [noise_event_tensor, aper, vuv, energy_norm, alpha_broadcast, speaker_broadcast, geom_broadcast],
        dim=-1,
    )
    available_controls = {
        "z_art": z_art,
            "event_probs": event_probs,
            "e_evt": e_evt,
        "energy_log": energy_log,
        "abs_mean": zero_like_energy.clone(),
        "zero_cross_rate": zero_like_energy.clone(),
        "delta_energy": delta_energy,
        "energy_proxy": energy_norm,
        "voiced_proxy": vuv,
        "aperiodicity_proxy": aper,
        "event_presence_proxy": event_presence_proxy,
        "energy_change_proxy": delta_energy.abs().clamp(0.0, 1.0),
        "f0_hz": f0_hz,
        "f0_hz_log_norm": f0_hz_log_norm,
        "vuv": vuv,
        "aper": aper,
        "E": energy_log,
        "E_log_rms_norm": energy_norm,
        **(
            {}
            if not isinstance(fine_structure_reference.get("unit_rms_waveform_frame"), torch.Tensor)
            else {
                "packet_unit_rms_waveform_frame": fine_structure_reference["unit_rms_waveform_frame"].to(
                    torch.float32
                ),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_reference.get("unit_rms_logspec"), torch.Tensor)
            else {
                "packet_unit_rms_logspec": fine_structure_reference["unit_rms_logspec"].to(torch.float32),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_reference.get("unit_rms_logspec_delta"), torch.Tensor)
            else {
                "packet_unit_rms_logspec_delta": fine_structure_reference["unit_rms_logspec_delta"].to(
                    torch.float32
                ),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_code.get("waveform_geometry_code"), torch.Tensor)
            else {
                "packet_learned_waveform_geometry_code": fine_structure_code["waveform_geometry_code"].to(
                    torch.float32
                ),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_code.get("waveform_geometry_short_temporal_code"), torch.Tensor)
            else {
                "packet_learned_waveform_geometry_short_temporal_code": fine_structure_code[
                    "waveform_geometry_short_temporal_code"
                ].to(torch.float32),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_code.get("waveform_geometry_center_code"), torch.Tensor)
            else {
                "packet_learned_waveform_geometry_center_code": fine_structure_code[
                    "waveform_geometry_center_code"
                ].to(torch.float32),
            }
        ),
        **(
            {}
            if not isinstance(fine_structure_code.get("waveform_geometry_neighbor_delta_code"), torch.Tensor)
            else {
                "packet_learned_waveform_geometry_neighbor_delta_code": fine_structure_code[
                    "waveform_geometry_neighbor_delta_code"
                ].to(torch.float32),
            }
        ),
    }
    scaffold_payload = {
        "scaffold_version": STREAMING_STUDENT_VOCODER_INPUT_SCAFFOLD_VERSION,
        "source_contract_path": packet_path.as_posix(),
        "source_contract_version": str(payload["packet_version"]),
        "source_audio_path": str(payload.get("audio_path")),
        "source_teacher": {
            "checkpoint_path": None,
            "experiment_id": str(Path(str(payload.get("audio_path", "unknown"))).stem),
            "route_handoff_path": None,
        },
        "source_runtime": {
            "sample_rate": int(payload["sample_rate"]),
            "frame_length": int(payload["frame_length"]),
            "hop_length": int(payload["hop_length"]),
            "frame_count": frame_count,
        },
        "frame_start_ms": frame_start_ms,
        "frame_count": frame_count,
        "available_controls": available_controls,
        "conditioning": {
            "s_spk_target": speaker_embedding,
            "s_geom_target": geom_embedding,
            "alpha": alpha,
        },
        "event_semantics_meta": {
            "event_probs_version": "streaming_student_predicted_event_probs_v1",
            "event_prob_dimensions": list(e_evt_meta.get("event_dimensions", [])),
            "semantic_status": "streaming_student_packet_bridge",
        },
        "e_evt_meta": e_evt_meta,
        "e_evt_summary": {
            "boundary_source": "streaming_student_predicted_packet",
            "timing_sidecar_used": False,
            "source_semantic_parity_used": False,
        },
        "stage5_requested_but_missing": {
            "r_res": torch.zeros((frame_count, 0), dtype=torch.float32),
        },
        "branch_scaffold": {
            "periodic_branch_features": periodic_branch_features,
            "noise_branch_features": noise_branch_features,
            "periodic_feature_semantics": [
                "z_art",
                "f0_hz_log_norm",
                "vuv",
                "E_log_rms_norm",
                "alpha",
                "s_spk_target",
                "s_geom_target",
            ],
            "noise_feature_semantics": [
                "e_evt" if resolved_noise_event_family == "e_evt" else "event_probs",
                "aper",
                "vuv",
                "E_log_rms_norm",
                "alpha",
                "s_spk_target",
                "s_geom_target",
            ],
            "noise_event_feature_family": resolved_noise_event_family,
            "missing_periodic_design_keys": [],
            "missing_noise_design_keys": ["r_res"],
        },
    }
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "packet_path": packet_path.as_posix(),
        "scaffold_version": STREAMING_STUDENT_VOCODER_INPUT_SCAFFOLD_VERSION,
        "record_id": str(payload.get("record_id", "unknown")),
        "noise_event_family": resolved_noise_event_family,
        "frame_count": frame_count,
        "periodic_branch_feature_dim": int(periodic_branch_features.shape[-1]),
        "noise_branch_feature_dim": int(noise_branch_features.shape[-1]),
        "available_controls": {
            "z_art_dim": int(z_art.shape[-1]),
            "event_dim": int(event_probs.shape[-1]),
            "e_evt_dim": int(e_evt.shape[-1]),
            "f0_hz_dim": int(f0_hz.shape[-1]),
            "f0_hz_log_norm_dim": int(f0_hz_log_norm.shape[-1]),
            "vuv_dim": int(vuv.shape[-1]),
            "aper_dim": int(aper.shape[-1]),
            "E_dim": int(energy_log.shape[-1]),
            "E_log_rms_norm_dim": int(energy_norm.shape[-1]),
            **(
                {}
                if not isinstance(fine_structure_reference.get("unit_rms_waveform_frame"), torch.Tensor)
                else {
                    "packet_unit_rms_waveform_frame_dim": int(
                        fine_structure_reference["unit_rms_waveform_frame"].shape[-1]
                    ),
                }
            ),
            **(
                {}
                if not isinstance(fine_structure_reference.get("unit_rms_logspec"), torch.Tensor)
                else {
                    "packet_unit_rms_logspec_dim": int(
                        fine_structure_reference["unit_rms_logspec"].shape[-1]
                    ),
                }
            ),
            **(
                {}
                if not isinstance(fine_structure_reference.get("unit_rms_logspec_delta"), torch.Tensor)
                else {
                    "packet_unit_rms_logspec_delta_dim": int(
                        fine_structure_reference["unit_rms_logspec_delta"].shape[-1]
                    ),
                }
            ),
            **(
                {}
                if not isinstance(fine_structure_code.get("waveform_geometry_code"), torch.Tensor)
                else {
                    "packet_learned_waveform_geometry_code_dim": int(
                        fine_structure_code["waveform_geometry_code"].shape[-1]
                    ),
                    "packet_learned_waveform_geometry_code_family": str(
                        fine_structure_code.get("code_family", "unknown")
                    ),
                    "packet_learned_waveform_geometry_code_source_mode": str(
                        fine_structure_code.get("source_mode", "unknown")
                    ),
                }
            ),
            **(
                {}
                if not isinstance(fine_structure_code.get("waveform_geometry_center_code"), torch.Tensor)
                else {
                    "packet_learned_waveform_geometry_center_code_dim": int(
                        fine_structure_code["waveform_geometry_center_code"].shape[-1]
                    ),
                    "packet_learned_waveform_geometry_neighbor_delta_code_dim": (
                        0
                        if not isinstance(fine_structure_code.get("waveform_geometry_neighbor_delta_code"), torch.Tensor)
                        else int(fine_structure_code["waveform_geometry_neighbor_delta_code"].shape[-1])
                    ),
                }
            ),
            "speaker_dim": int(speaker_embedding.shape[-1]),
            "geom_dim": int(geom_embedding.shape[-1]),
        },
        "notes": [
            "This scaffold adapts Stage3 student_control_packet outputs into the Stage5 no-res explicit-control feature family.",
            "It preserves the existing Stage5 36/36 explicit-control layout so current no-res checkpoints can be fail-fast decoded without retraining.",
            f"The noise-branch first 8 dims currently use {resolved_noise_event_family}. Use legacy_event_probs when evaluating old v2/event_probs Stage5 checkpoints.",
            "f0 / aper / energy remain packet-calibrated analysis controls; this route is for end-to-end decode screening, not a claim that named-control readiness is complete.",
            "packet_unit_rms_logspec and packet_unit_rms_logspec_delta are analysis-only dense fine-structure references exported for oracle gating; current Stage5 branch layouts do not consume them yet.",
            "packet_learned_waveform_geometry_code is the deployable student-predicted upstream fine-structure contract candidate when present.",
            "packet_learned_waveform_geometry_center_code and packet_learned_waveform_geometry_neighbor_delta_code expose the same predicted contract in a center-vs-local-delta split for Stage5 interface experiments.",
        ],
    }
    pt_path = output_dir / "streaming_student_vocoder_input_scaffold.pt"
    json_path = output_dir / "streaming_student_vocoder_input_scaffold.json"
    md_path = output_dir / "streaming_student_vocoder_input_scaffold.md"
    torch.save(scaffold_payload, pt_path)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    md_path.write_text(build_scaffold_markdown(summary), encoding="utf-8", newline="\n")


def build_event_presence_proxy_from_e_evt(e_evt_tensor: torch.Tensor) -> torch.Tensor:
    if e_evt_tensor.ndim != 2 or int(e_evt_tensor.shape[0]) <= 0:
        return torch.zeros((0, 1), dtype=e_evt_tensor.dtype, device=e_evt_tensor.device)
    if int(e_evt_tensor.shape[-1]) >= 4:
        acoustic_event_slice = e_evt_tensor[:, 0:4]
    else:
        acoustic_event_slice = e_evt_tensor
    return acoustic_event_slice.amax(dim=-1, keepdim=True)


def normalize_stage5_noise_event_family(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in SUPPORTED_STAGE5_NOISE_EVENT_FAMILIES:
        raise ValueError(
            f"Unsupported noise_event_family: {value!r}. "
            f"Expected one of {sorted(SUPPORTED_STAGE5_NOISE_EVENT_FAMILIES)}."
        )
    return normalized


def select_packet_export_records(
    records: list[dict[str, object]],
    sample_count: int,
    target_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    if target_record_ids:
        record_map = {str(record["record_id"]): record for record in records}
        selected: list[dict[str, object]] = []
        missing: list[str] = []
        for record_id in target_record_ids:
            match = record_map.get(str(record_id))
            if match is None:
                missing.append(str(record_id))
                continue
            selected.append(match)
        if missing:
            raise ValueError(f"Unknown target_record_ids in packet export: {missing}")
        return selected
    if int(sample_count) <= 0:
        raise ValueError("sample_count must be positive.")
    return list(records[: int(sample_count)])


def build_streaming_student_stage5_package_reuse_signature(
    *,
    record_id: str,
    packet_path: Path,
    target_audio_path: Path,
    semantic_consumer_mode: str,
    target_contract_mode: str,
    noise_event_family: str,
) -> dict[str, object]:
    return {
        "signature_version": STREAMING_STUDENT_STAGE5_PACKAGE_REUSE_SIGNATURE_VERSION,
        "record_id": str(record_id),
        "packet_file": build_file_fingerprint(packet_path),
        "target_audio_file": build_file_fingerprint(target_audio_path),
        "semantic_consumer_mode": str(semantic_consumer_mode),
        "target_contract_mode": str(target_contract_mode),
        "noise_event_family": str(noise_event_family),
    }


def should_reuse_existing_streaming_student_stage5_package(
    *,
    package_path: Path,
    signature_path: Path,
    skip_existing: bool,
    expected_signature: dict[str, object],
    target_audio_path: Path,
    semantic_consumer_mode: str,
    target_contract_mode: str,
) -> bool:
    if not bool(skip_existing and package_path.exists()):
        return False
    existing_signature = load_json_dict_if_exists(signature_path)
    if existing_signature != expected_signature:
        return False
    try:
        existing_payload = load_training_package_payload(package_path)
    except Exception:
        return False
    if str(existing_payload.get("source_audio_path", "")) != target_audio_path.as_posix():
        return False
    if str(existing_payload.get("target_audio_path", "")) != target_audio_path.as_posix():
        return False
    existing_semantic_consumer = dict(existing_payload.get("semantic_consumer", {}))
    if str(existing_semantic_consumer.get("semantic_consumer_mode", "none")) != str(semantic_consumer_mode):
        return False
    existing_target_contract = dict(existing_payload.get("target_contract", {}))
    if (
        str(existing_target_contract.get("target_contract_mode", DEFAULT_STAGE5_TARGET_CONTRACT_MODE))
        != str(target_contract_mode)
    ):
        return False
    return True


def resolve_duration_sec(packet_payload: dict[str, object]) -> float:
    frame_count = int(packet_payload.get("frame_count", 0))
    hop_length = int(packet_payload.get("hop_length", 0))
    sample_rate = int(packet_payload.get("sample_rate", 0))
    if frame_count < 0:
        raise ValueError(f"frame_count must be non-negative, got {frame_count}.")
    if frame_count == 0:
        return 0.0
    if hop_length <= 0 or sample_rate <= 0:
        raise ValueError(
            "streaming_student packet payload is missing valid hop_length/sample_rate for duration computation."
        )
    return round(frame_count * hop_length / sample_rate, 6)


def build_scaffold_markdown(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Streaming Student Stage5 Scaffold",
            "",
            f"- scaffold_version: {summary['scaffold_version']}",
            f"- packet_path: {summary['packet_path']}",
            f"- record_id: {summary['record_id']}",
            f"- frame_count: {summary['frame_count']}",
            f"- periodic_branch_feature_dim: {summary['periodic_branch_feature_dim']}",
            f"- noise_branch_feature_dim: {summary['noise_branch_feature_dim']}",
            f"- available_controls: {json.dumps(summary['available_controls'], ensure_ascii=False)}",
            "",
            "## Notes",
            *[f"- {line}" for line in summary["notes"]],
            "",
        ]
    )


def build_dataset_markdown(summary: dict[str, object]) -> str:
    package_summary = dict(summary["summary"])
    normalized_split_name = str(summary.get("split_name", "")).strip().lower()
    active_split_key = "validation" if normalized_split_name == "validation" else "train"
    active_split_summary = dict(package_summary.get(active_split_key, {}))
    return "\n".join(
        [
            "# Streaming Student Stage5 Dataset Index",
            "",
            f"- dataset_index_version: {summary['dataset_index_version']}",
            f"- packet_export_path: {summary['packet_export_path']}",
            f"- split_name: {summary['split_name']}",
            f"- semantic_consumer_mode: {summary['semantic_consumer_mode']}",
            f"- target_contract_mode: {summary['target_contract_mode']}",
            f"- noise_event_family: {summary['noise_event_family']}",
            f"- active_split_key: {active_split_key}",
            f"- validation_package_count: {len(summary['validation_packages'])}",
            f"- periodic_input_dims: {json.dumps(active_split_summary.get('periodic_input_dims', []), ensure_ascii=False)}",
            f"- noise_input_dims: {json.dumps(active_split_summary.get('noise_input_dims', []), ensure_ascii=False)}",
            "",
            "## Notes",
            *[f"- {line}" for line in summary["notes"]],
            "",
        ]
    )
