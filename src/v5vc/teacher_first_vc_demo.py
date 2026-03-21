from __future__ import annotations

from datetime import datetime
import json
import shutil
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.manifest_builder import load_jsonl
from v5vc.nores_vocoder_audio_export import (
    DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
    infer_branch_label,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
)
from v5vc.offline_mvp.data import load_waveform
from v5vc.offline_teacher_downstream_contract import (
    build_contract_payload,
    build_markdown as build_contract_markdown,
    build_tensor_payload,
    load_conditioning_asset,
)
from v5vc.offline_teacher_runtime import (
    OfflineMVPTeacherRuntime,
    compare_runtime_outputs,
    resolve_chunk_samples,
    resolve_runtime_device,
    run_full_pass,
    run_streaming_pass,
)
from v5vc.offline_teacher_vocoder_input_scaffold import build_offline_mvp_teacher_vocoder_input_scaffold
from v5vc.offline_vocoder_scaffold import NoResidualSourceFilterVocoderScaffold
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.streaming_student.teacher_labels import resolve_teacher_source
from v5vc.target_format_recovery import write_waveform_int16
from v5vc.train_entry import instantiate_offline_mvp_model


DEFAULT_TEACHER_ROUTE_HANDOFF_PATH = Path(
    "reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"
)
DEFAULT_CALIBRATION_ASSET_PATH = Path(
    "data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"
)
DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH = Path(
    "reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json"
)
DEFAULT_SELF_CHECK_INPUT_AUDIO_PATH = Path(
    "data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav"
)
DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION = "teacher_first_runtime_risk_v1"
HIGH_RISK_SPECTRAL_CENTROID_HZ = 3200.0
HIGH_RISK_SPECTRAL_ROLLOFF95_HZ = 22000.0
HIGH_RISK_HIGH_BAND_ENERGY_RATIO = 0.25
ELEVATED_RISK_SPECTRAL_CENTROID_HZ = 3100.0
ELEVATED_RISK_SPECTRAL_ROLLOFF95_HZ = 21500.0
ELEVATED_RISK_HIGH_BAND_ENERGY_RATIO = 0.15
DECODER_PROBE_CONTROL_FAMILY_ALIASES = {
    "z_art": "z_art",
    "zart": "z_art",
    "event_probs": "event_probs",
    "event_probs_family": "event_probs",
    "events": "event_probs",
    "proxy_family": "proxy_family",
    "proxies": "proxy_family",
    "all_proxies": "proxy_family",
    "voiced_proxy": "voiced_proxy",
    "energy_proxy": "energy_proxy",
    "periodic_energy_proxy": "periodic_energy_proxy",
    "noise_energy_proxy": "noise_energy_proxy",
    "aperiodicity_proxy": "aperiodicity_proxy",
    "event_presence_proxy": "event_presence_proxy",
    "energy_change_proxy": "energy_change_proxy",
}
DECODER_PROBE_CONTROL_OVERRIDE_MODE_ALIASES = {
    "zero": "zero",
    "zeros": "zero",
    "reference_mean": "reference_mean",
    "refmean": "reference_mean",
    "mean": "reference_mean",
}
DECODER_PROBE_CONTROL_FAMILY_TARGETS = {
    "z_art": (("periodic", "z_art"),),
    "event_probs": (("noise", "event_probs"),),
    "voiced_proxy": (("periodic", "voiced_proxy"),),
    "energy_proxy": (("periodic", "energy_proxy"), ("noise", "energy_proxy")),
    "periodic_energy_proxy": (("periodic", "energy_proxy"),),
    "noise_energy_proxy": (("noise", "energy_proxy"),),
    "aperiodicity_proxy": (("noise", "aperiodicity_proxy"),),
    "event_presence_proxy": (("noise", "event_presence_proxy"),),
    "energy_change_proxy": (("noise", "energy_change_proxy"),),
    "proxy_family": (
        ("periodic", "voiced_proxy"),
        ("periodic", "energy_proxy"),
        ("noise", "aperiodicity_proxy"),
        ("noise", "event_presence_proxy"),
        ("noise", "energy_change_proxy"),
        ("noise", "energy_proxy"),
    ),
}


PIPELINE_LAYER_DEFINITIONS = (
    {
        "layer_id": "teacher_runtime",
        "label": "Teacher runtime",
        "stage_ids": (
            "teacher_source_resolution",
            "teacher_model_load",
            "input_audio_load",
            "teacher_runtime_streaming",
            "teacher_runtime_verification",
        ),
    },
    {
        "layer_id": "teacher_contract",
        "label": "Teacher downstream contract",
        "stage_ids": (
            "conditioning_asset_load",
            "teacher_contract_write",
        ),
    },
    {
        "layer_id": "teacher_vocoder_input_scaffold",
        "label": "Teacher vocoder input scaffold",
        "stage_ids": ("teacher_vocoder_input_scaffold",),
    },
    {
        "layer_id": "vocoder_checkpoint",
        "label": "Stage5 vocoder checkpoint",
        "stage_ids": (
            "vocoder_checkpoint_resolution",
            "vocoder_checkpoint_payload_load",
            "vocoder_checkpoint_load",
        ),
    },
    {
        "layer_id": "waveform_reconstruction",
        "label": "Waveform reconstruction",
        "stage_ids": (
            "waveform_decode",
            "decoded_audio_write",
        ),
    },
)


STAGE_METADATA = {
    "teacher_source_resolution": {
        "layer_id": "teacher_runtime",
        "label": "Resolve teacher route handoff / checkpoint",
        "diagnostic_summary": "Unable to resolve the teacher runtime source from the route handoff or explicit checkpoint.",
        "likely_causes": [
            "The teacher route handoff path is missing, stale, or points to a removed checkpoint.",
            "The explicit teacher checkpoint path is incorrect.",
        ],
        "recommended_actions": [
            "Check --teacher-route-handoff or pass --teacher-checkpoint explicitly.",
            "Confirm the referenced teacher checkpoint still exists in the workspace.",
        ],
    },
    "teacher_model_load": {
        "layer_id": "teacher_runtime",
        "label": "Load teacher checkpoint and instantiate runtime model",
        "diagnostic_summary": "The teacher checkpoint could not be loaded into the offline teacher runtime model.",
        "likely_causes": [
            "The teacher checkpoint file is missing or corrupted.",
            "The checkpoint config/model payload is incomplete or no longer matches current code.",
        ],
        "recommended_actions": [
            "Re-check the teacher checkpoint path or regenerate the handoff payload.",
            "If code changed, use a compatible checkpoint or rebuild the runtime route handoff.",
        ],
    },
    "input_audio_load": {
        "layer_id": "teacher_runtime",
        "label": "Load input audio",
        "diagnostic_summary": "The input audio could not be read into the teacher runtime.",
        "likely_causes": [
            "The input wav path is wrong or the file no longer exists.",
            "The audio format is unsupported or the file is corrupted.",
        ],
        "recommended_actions": [
            "Verify --input-audio points to an existing wav file.",
            "If needed, re-export the source clip to a standard mono wav before retrying.",
        ],
    },
    "teacher_runtime_streaming": {
        "layer_id": "teacher_runtime",
        "label": "Run teacher streaming runtime",
        "diagnostic_summary": "The teacher runtime failed while generating downstream control tensors.",
        "likely_causes": [
            "The requested device is unavailable.",
            "The teacher checkpoint/runtime code is incompatible with the current input or model config.",
        ],
        "recommended_actions": [
            "Retry with --device cpu to rule out device-specific issues.",
            "If the failure is reproducible, inspect the teacher checkpoint and model config pair.",
        ],
    },
    "teacher_runtime_verification": {
        "layer_id": "teacher_runtime",
        "label": "Verify streaming runtime against full pass",
        "diagnostic_summary": "The optional full-pass verification failed for the teacher runtime.",
        "likely_causes": [
            "Streaming and full-pass teacher outputs diverged beyond the current consistency check.",
            "The additional verification forward pass failed on the requested device.",
        ],
        "recommended_actions": [
            "Retry with --skip-full-pass-verify if you only need the minimal runtime path.",
            "If verification is required, inspect runtime/full-pass alignment on the same input.",
        ],
    },
    "conditioning_asset_load": {
        "layer_id": "teacher_contract",
        "label": "Load single-target conditioning preset",
        "diagnostic_summary": "The fixed single-target conditioning preset could not be loaded.",
        "likely_causes": [
            "The calibration asset path is missing or invalid JSON.",
            "The calibration asset does not expose the expected conditioning vectors.",
        ],
        "recommended_actions": [
            "Check --calibration-asset and confirm it points to the estimated single-target asset.",
            "Rebuild the calibration asset if its payload is incomplete.",
        ],
    },
    "teacher_contract_write": {
        "layer_id": "teacher_contract",
        "label": "Materialize teacher downstream contract",
        "diagnostic_summary": "Teacher runtime outputs were produced, but the downstream contract could not be materialized or written.",
        "likely_causes": [
            "The contract payload or tensor serialization failed.",
            "The managed output directory could not be written as expected.",
        ],
        "recommended_actions": [
            "Inspect the output directory permissions and partial teacher_contract artifacts.",
            "If this persists, verify the contract payload fields are still compatible with downstream consumers.",
        ],
    },
    "teacher_vocoder_input_scaffold": {
        "layer_id": "teacher_vocoder_input_scaffold",
        "label": "Build teacher vocoder input scaffold",
        "diagnostic_summary": "The teacher downstream contract exists, but the consumer-side vocoder scaffold could not be built.",
        "likely_causes": [
            "The teacher contract tensor is missing required keys or shapes.",
            "The scaffold materializer is incompatible with the current contract payload.",
        ],
        "recommended_actions": [
            "Inspect the saved teacher contract artifacts and confirm they are complete.",
            "If code changed, update the scaffold builder or regenerate the contract with the matching version.",
        ],
    },
    "vocoder_checkpoint_resolution": {
        "layer_id": "vocoder_checkpoint",
        "label": "Resolve Stage5 vocoder checkpoint",
        "diagnostic_summary": "The Stage5 vocoder checkpoint could not be resolved from the selection payload or explicit input.",
        "likely_causes": [
            "The checkpoint-selection payload is missing the requested role.",
            "The explicit vocoder checkpoint path was not provided or is incorrect.",
        ],
        "recommended_actions": [
            "Use --selection-target best_validation or pass --vocoder-checkpoint explicitly.",
            "Check the checkpoint-selection json and confirm the requested role exists.",
        ],
    },
    "vocoder_checkpoint_load": {
        "layer_id": "vocoder_checkpoint",
        "label": "Load Stage5 vocoder checkpoint",
        "diagnostic_summary": "A Stage5 vocoder checkpoint path was resolved, but the checkpoint could not be loaded into the current scaffold.",
        "likely_causes": [
            "The Stage5 checkpoint file is missing or corrupted.",
            "The checkpoint state dict no longer matches the current vocoder scaffold definition.",
        ],
        "recommended_actions": [
            "Confirm the resolved vocoder checkpoint exists and is readable.",
            "If the code changed, use a compatible Stage5 checkpoint or refresh the selection payload.",
        ],
    },
    "vocoder_checkpoint_payload_load": {
        "layer_id": "vocoder_checkpoint",
        "label": "Load Stage5 vocoder checkpoint payload",
        "diagnostic_summary": "A vocoder checkpoint file was found, but its payload does not look like a Stage5 no-res vocoder checkpoint.",
        "likely_causes": [
            "The provided file is from a different model family, such as a teacher checkpoint.",
            "The checkpoint file is truncated or does not contain the expected model_state_dict payload.",
        ],
        "recommended_actions": [
            "Use the current Stage5 checkpoint-selection payload or pass a known no-res vocoder checkpoint explicitly.",
            "If you intended to use another checkpoint family, convert or export a compatible Stage5 vocoder checkpoint first.",
        ],
    },
    "waveform_decode": {
        "layer_id": "waveform_reconstruction",
        "label": "Run Stage5 waveform decode",
        "diagnostic_summary": "The Stage5 vocoder model loaded, but waveform frames could not be decoded or reconstructed.",
        "likely_causes": [
            "The scaffold features are incompatible with the selected Stage5 checkpoint.",
            "The decode-side predicted activity gate or OLA reconstruction hit an unexpected shape/runtime issue.",
        ],
        "recommended_actions": [
            "Inspect the scaffold tensor shapes and the resolved Stage5 checkpoint together.",
            "If needed, retry with the current default gate settings before changing decode-side parameters.",
        ],
    },
    "decoded_audio_write": {
        "layer_id": "waveform_reconstruction",
        "label": "Write decoded wav",
        "diagnostic_summary": "Waveform reconstruction succeeded, but the decoded wav could not be written to disk.",
        "likely_causes": [
            "The managed output directory is not writable.",
            "The decoded waveform payload is malformed at final write time.",
        ],
        "recommended_actions": [
            "Check write permissions for the requested output directory.",
            "Inspect any partial decoded artifacts left in the run directory before retrying.",
        ],
    },
}


def run_offline_mvp_teacher_first_vc_demo(
    input_audio_path: Path,
    output_dir: Path,
    teacher_route_handoff_path: Path | None,
    teacher_checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    vocoder_checkpoint_path: Path | None,
    vocoder_checkpoint_selection_path: Path | None,
    selection_target: str,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    max_audio_sec: float | None,
    verify_against_full_pass: bool,
    save_intermediates: bool,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> None:
    if float(predicted_activity_gate_floor) < 0.0 or float(predicted_activity_gate_floor) > 1.0:
        raise ValueError("predicted_activity_gate_floor must be within [0.0, 1.0].")
    if int(predicted_activity_gate_smoothing_frames) < 0:
        raise ValueError("predicted_activity_gate_smoothing_frames must be >= 0.")
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    decoded_path = output_dir / "decoded.wav"
    summary_json_path = output_dir / "teacher_first_vc_demo.json"
    summary_md_path = output_dir / "teacher_first_vc_demo.md"
    contract_dir = output_dir / (
        "teacher_contract" if bool(save_intermediates) else "_tmp_teacher_contract"
    )
    scaffold_dir = output_dir / (
        "teacher_vocoder_input_scaffold" if bool(save_intermediates) else "_tmp_teacher_vocoder_input_scaffold"
    )
    contract_tensor_path = contract_dir / "teacher_downstream_control_contract.pt"
    scaffold_tensor_path = scaffold_dir / "teacher_vocoder_input_scaffold.pt"
    contract_runtime: dict[str, object] = {}
    teacher_summary: dict[str, object] = {}
    conditioning_summary: dict[str, object] = {}
    selection_summary: dict[str, object] | None = None
    resolved_vocoder_checkpoint_path: Path | None = None
    resolved_conditioning: dict[str, object] | None = None
    checkpoint_payload: dict[str, object] | None = None
    branch_label: str | None = None
    decoded_waveform: torch.Tensor | None = None
    sample_rate: int | None = None
    stage_state: dict[str, object] = {
        "current_stage": "teacher_source_resolution",
        "completed_stages": [],
        "skipped_stages": [],
    }

    try:
        set_stage(stage_state, "conditioning_asset_load")
        resolved_conditioning = load_conditioning_asset(
            calibration_asset_path=calibration_asset_path,
        )
        mark_stage_completed(stage_state, "conditioning_asset_load")

        set_stage(stage_state, "vocoder_checkpoint_resolution")
        try:
            resolved_vocoder_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
                checkpoint_path=vocoder_checkpoint_path,
                checkpoint_selection_path=vocoder_checkpoint_selection_path,
                selection_target=selection_target,
            )
        except ValueError as exc:
            if (
                vocoder_checkpoint_path is None
                and str(selection_target).strip().lower() == "stable_late_stop"
            ):
                raise ValueError(
                    "The requested vocoder checkpoint selection payload does not expose stable_late_stop. "
                    "Use --selection-target best_validation or pass --vocoder-checkpoint explicitly."
                ) from exc
            raise
        if not resolved_vocoder_checkpoint_path.is_file():
            raise FileNotFoundError(
                f"Resolved Stage5 vocoder checkpoint does not exist: {resolved_vocoder_checkpoint_path}"
            )
        mark_stage_completed(stage_state, "vocoder_checkpoint_resolution")

        set_stage(stage_state, "vocoder_checkpoint_payload_load")
        checkpoint_payload = load_vocoder_checkpoint_payload(
            resolved_vocoder_checkpoint_path
        )
        mark_stage_completed(stage_state, "vocoder_checkpoint_payload_load")

        contract_payload = export_teacher_contract_with_stage_tracking(
            input_audio_path=input_audio_path,
            output_dir=contract_dir,
            route_handoff_path=teacher_route_handoff_path,
            checkpoint_path=teacher_checkpoint_path,
            calibration_asset_path=calibration_asset_path,
            conditioning=resolved_conditioning,
            chunk_samples=chunk_samples,
            chunk_ms=chunk_ms,
            device=device,
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=bool(verify_against_full_pass),
            stage_state=stage_state,
        )
        contract_runtime = dict(contract_payload.get("runtime", {}))
        teacher_summary = dict(contract_payload.get("teacher", {}))
        conditioning_summary = dict(contract_payload.get("conditioning", {}))

        set_stage(stage_state, "teacher_vocoder_input_scaffold")
        build_offline_mvp_teacher_vocoder_input_scaffold(
            contract_path=contract_tensor_path,
            output_dir=scaffold_dir,
        )
        mark_stage_completed(stage_state, "teacher_vocoder_input_scaffold")
        scaffold_payload = torch.load(scaffold_tensor_path, map_location="cpu", weights_only=False)
        if not isinstance(scaffold_payload, dict):
            raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")

        set_stage(stage_state, "vocoder_checkpoint_load")
        model = build_vocoder_model_from_checkpoint(
            checkpoint_payload=checkpoint_payload,
            scaffold_payload=scaffold_payload,
        )
        resolved_device = resolve_runtime_device(device)
        model = model.to(resolved_device)
        model.eval()
        mark_stage_completed(stage_state, "vocoder_checkpoint_load")

        branch_scaffold = dict(scaffold_payload["branch_scaffold"])
        periodic_branch_features = branch_scaffold["periodic_branch_features"].to(
            device=resolved_device,
            dtype=torch.float32,
        )
        noise_branch_features = branch_scaffold["noise_branch_features"].to(
            device=resolved_device,
            dtype=torch.float32,
        )
        source_runtime = dict(scaffold_payload.get("source_runtime", {}))
        sample_rate = int(source_runtime["sample_rate"])
        frame_length = int(source_runtime["frame_length"])
        hop_length = int(source_runtime["hop_length"])

        set_stage(stage_state, "waveform_decode")
        with torch.no_grad():
            outputs = model(
                periodic_branch_features=periodic_branch_features,
                noise_branch_features=noise_branch_features,
            )
            predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"])
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=outputs["waveform_frames"],
                frame_length=frame_length,
                hop_length=hop_length,
                frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
                frame_gain_floor=float(predicted_activity_gate_floor),
                frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                frame_gain_apply_mode=resolved_apply_mode,
            ).detach().cpu()
        mark_stage_completed(stage_state, "waveform_decode")

        set_stage(stage_state, "decoded_audio_write")
        write_waveform_int16(decoded_path, decoded_waveform, sample_rate=sample_rate)
        mark_stage_completed(stage_state, "decoded_audio_write")
        branch_label = infer_branch_label(
            checkpoint_path=resolved_vocoder_checkpoint_path,
            selection_summary=selection_summary,
            selection_target=selection_target,
            use_predicted_activity_gate=bool(use_predicted_activity_gate),
            predicted_activity_gate_floor=float(predicted_activity_gate_floor),
            predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
            predicted_activity_gate_apply_mode=resolved_apply_mode,
        )
        summary = build_summary_payload(
            status="succeeded",
            input_audio_path=input_audio_path,
            output_dir=output_dir,
            decoded_path=decoded_path,
            teacher_route_handoff_path=teacher_route_handoff_path,
            teacher_checkpoint_path=teacher_checkpoint_path,
            calibration_asset_path=calibration_asset_path,
            vocoder_checkpoint_path=resolved_vocoder_checkpoint_path,
            vocoder_checkpoint_selection_path=vocoder_checkpoint_selection_path,
            selection_target=selection_target,
            verify_against_full_pass=verify_against_full_pass,
            save_intermediates=save_intermediates,
            use_predicted_activity_gate=use_predicted_activity_gate,
            predicted_activity_gate_floor=predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=resolved_apply_mode,
            contract_tensor_path=contract_tensor_path if bool(save_intermediates) else None,
            scaffold_tensor_path=scaffold_tensor_path if bool(save_intermediates) else None,
            contract_runtime=contract_runtime,
            teacher_summary=teacher_summary,
            conditioning_summary=conditioning_summary,
            selection_summary=selection_summary,
            branch_label=branch_label,
            decoded_waveform=decoded_waveform,
            sample_rate=sample_rate,
            completed_stages=list(stage_state.get("completed_stages", [])),
            skipped_stages=list(stage_state.get("skipped_stages", [])),
            current_stage=None,
            failure=None,
        )
        write_summary(
            summary_json_path=summary_json_path,
            summary_md_path=summary_md_path,
            summary=summary,
        )
        if not bool(save_intermediates):
            shutil.rmtree(contract_dir, ignore_errors=True)
            shutil.rmtree(scaffold_dir, ignore_errors=True)
    except Exception as exc:
        current_stage = stage_state_value(stage_state, "current_stage", "unknown")
        failure_summary = build_summary_payload(
            status="failed",
            input_audio_path=input_audio_path,
            output_dir=output_dir,
            decoded_path=decoded_path,
            teacher_route_handoff_path=teacher_route_handoff_path,
            teacher_checkpoint_path=teacher_checkpoint_path,
            calibration_asset_path=calibration_asset_path,
            vocoder_checkpoint_path=resolved_vocoder_checkpoint_path or vocoder_checkpoint_path,
            vocoder_checkpoint_selection_path=vocoder_checkpoint_selection_path,
            selection_target=selection_target,
            verify_against_full_pass=verify_against_full_pass,
            save_intermediates=save_intermediates,
            use_predicted_activity_gate=use_predicted_activity_gate,
            predicted_activity_gate_floor=predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=resolved_apply_mode,
            contract_tensor_path=contract_tensor_path if contract_tensor_path.exists() else None,
            scaffold_tensor_path=scaffold_tensor_path if scaffold_tensor_path.exists() else None,
            contract_runtime=contract_runtime,
            teacher_summary=teacher_summary,
            conditioning_summary=conditioning_summary,
            selection_summary=selection_summary,
            branch_label=branch_label,
            decoded_waveform=decoded_waveform,
            sample_rate=sample_rate,
            completed_stages=list(stage_state.get("completed_stages", [])),
            skipped_stages=list(stage_state.get("skipped_stages", [])),
            current_stage=current_stage,
            failure=build_failure_payload(stage_id=current_stage, error=exc),
        )
        try:
            write_summary(
                summary_json_path=summary_json_path,
                summary_md_path=summary_md_path,
                summary=failure_summary,
            )
        except Exception:
            pass
        raise


def build_vocoder_model_from_checkpoint(
    checkpoint_payload: dict[str, object],
    scaffold_payload: dict[str, object],
) -> NoResidualSourceFilterVocoderScaffold:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload.get("source_runtime", {}))
    return build_vocoder_model_from_runtime_dims(
        checkpoint_payload=checkpoint_payload,
        periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
        frame_length=int(source_runtime["frame_length"]),
    )


def build_vocoder_model_from_runtime_dims(
    *,
    checkpoint_payload: dict[str, object],
    periodic_input_dim: int,
    noise_input_dim: int,
    frame_length: int,
) -> NoResidualSourceFilterVocoderScaffold:
    state_dict = dict(checkpoint_payload["model_state_dict"])
    validate_vocoder_checkpoint_against_runtime_dims(
        state_dict=state_dict,
        periodic_input_dim=periodic_input_dim,
        noise_input_dim=noise_input_dim,
        frame_length=frame_length,
    )
    hidden_dim = int(state_dict["periodic_encoder.0.weight"].shape[0])
    harmonic_bins = int(state_dict["harmonic_envelope.weight"].shape[0])
    noise_bins = int(state_dict["noise_envelope.weight"].shape[0])
    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(periodic_input_dim),
        noise_input_dim=int(noise_input_dim),
        hidden_dim=hidden_dim,
        harmonic_bins=harmonic_bins,
        noise_bins=noise_bins,
        frame_length=int(frame_length),
    )
    model.load_state_dict(state_dict)
    return model


def validate_vocoder_checkpoint_against_scaffold(
    *,
    state_dict: dict[str, object],
    branch_scaffold: dict[str, object],
    source_runtime: dict[str, object],
) -> None:
    validate_vocoder_checkpoint_against_runtime_dims(
        state_dict=state_dict,
        periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
        frame_length=int(source_runtime["frame_length"]),
    )


def validate_vocoder_checkpoint_against_runtime_dims(
    *,
    state_dict: dict[str, object],
    periodic_input_dim: int,
    noise_input_dim: int,
    frame_length: int,
) -> None:
    expected_shapes = {
        "periodic_encoder.0.weight": (None, int(periodic_input_dim)),
        "noise_encoder.0.weight": (None, int(noise_input_dim)),
        "waveform_decoder.3.weight": (int(frame_length), None),
        "waveform_decoder.3.bias": (int(frame_length),),
    }
    mismatches = []
    for key, expected_shape in expected_shapes.items():
        value = state_dict.get(key)
        if not isinstance(value, torch.Tensor):
            continue
        actual_shape = tuple(int(dim) for dim in value.shape)
        if len(actual_shape) != len(expected_shape):
            mismatches.append(
                f"{key}: expected rank {len(expected_shape)} but found shape {actual_shape}"
            )
            continue
        mismatch_parts = []
        for index, expected_dim in enumerate(expected_shape):
            if expected_dim is None:
                continue
            if actual_shape[index] != expected_dim:
                mismatch_parts.append(
                    f"dim{index} expected {expected_dim} but found {actual_shape[index]}"
                )
        if mismatch_parts:
            mismatches.append(f"{key}: " + "; ".join(mismatch_parts))
    if mismatches:
        raise ValueError(
            "Stage5 vocoder checkpoint is incompatible with the current scaffold: "
            + " | ".join(mismatches)
        )


def load_vocoder_checkpoint_payload(checkpoint_path: Path) -> dict[str, object]:
    checkpoint_payload = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )
    if not isinstance(checkpoint_payload, dict):
        raise TypeError(f"Unsupported vocoder checkpoint payload type: {type(checkpoint_payload)!r}")
    state_dict = checkpoint_payload.get("model_state_dict")
    if not isinstance(state_dict, dict):
        raise ValueError("Vocoder checkpoint payload is missing model_state_dict.")
    required_keys = (
        "periodic_encoder.0.weight",
        "noise_encoder.0.weight",
        "harmonic_envelope.weight",
        "noise_envelope.weight",
    )
    missing_keys = [key for key in required_keys if key not in state_dict]
    if missing_keys:
        raise ValueError(
            "Vocoder checkpoint payload is missing required Stage5 keys: "
            + ", ".join(missing_keys)
        )
    return checkpoint_payload


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def export_teacher_contract_with_stage_tracking(
    *,
    input_audio_path: Path,
    output_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    conditioning: dict[str, object] | None,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    max_audio_sec: float | None,
    verify_against_full_pass: bool,
    stage_state: dict[str, object],
) -> dict[str, object]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    set_stage(stage_state, "teacher_source_resolution")
    resolved_source = resolve_teacher_source(
        route_handoff_path=route_handoff_path,
        experiment_metrics_path=None,
        checkpoint_path=checkpoint_path,
        split_dir=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
    )
    mark_stage_completed(stage_state, "teacher_source_resolution")

    set_stage(stage_state, "teacher_model_load")
    checkpoint_payload = load_checkpoint(Path(resolved_source["checkpoint_path"]))
    checkpoint_config = checkpoint_payload.get("config")
    if not isinstance(checkpoint_config, dict):
        raise ValueError("Teacher checkpoint does not contain a valid config payload.")
    model_config = checkpoint_config.get("model")
    if not isinstance(model_config, dict):
        raise ValueError("Teacher checkpoint config.model is missing.")
    resolved_device = resolve_runtime_device(device)
    model = instantiate_offline_mvp_model(dict(model_config))
    model.load_state_dict(checkpoint_payload["model_state_dict"])
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    mark_stage_completed(stage_state, "teacher_model_load")

    set_stage(stage_state, "input_audio_load")
    waveform, sample_rate = load_waveform(input_audio_path.resolve(), max_duration_sec=max_audio_sec)
    frame_length = int(model_config["frame_length"])
    hop_length = int(model_config["hop_length"])
    effective_chunk_samples = resolve_chunk_samples(
        chunk_samples=chunk_samples,
        chunk_ms=chunk_ms,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    mark_stage_completed(stage_state, "input_audio_load")

    set_stage(stage_state, "teacher_runtime_streaming")
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
    mark_stage_completed(stage_state, "teacher_runtime_streaming")

    verification = None
    if verify_against_full_pass:
        set_stage(stage_state, "teacher_runtime_verification")
        full_pass_outputs = run_full_pass(
            model=model,
            device=resolved_device,
            waveform=waveform,
        )
        verification = compare_runtime_outputs(
            full_pass_outputs=full_pass_outputs,
            streaming_outputs=streaming_outputs,
        )
        mark_stage_completed(stage_state, "teacher_runtime_verification")
    else:
        mark_stage_skipped(stage_state, "teacher_runtime_verification")

    if conditioning is None:
        set_stage(stage_state, "conditioning_asset_load")
        conditioning = load_conditioning_asset(
            calibration_asset_path=calibration_asset_path,
        )
        mark_stage_completed(stage_state, "conditioning_asset_load")

    contract_payload = build_contract_payload(
        input_audio_path=input_audio_path,
        resolved_source=resolved_source,
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
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
        chunk_samples=effective_chunk_samples,
        streaming_outputs=streaming_outputs,
        conditioning=conditioning,
    )

    set_stage(stage_state, "teacher_contract_write")
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
        build_contract_markdown(contract_payload),
        encoding="utf-8",
        newline="\n",
    )
    mark_stage_completed(stage_state, "teacher_contract_write")
    return contract_payload


def set_stage(stage_state: dict[str, object], stage_id: str) -> None:
    stage_state["current_stage"] = stage_id


def mark_stage_completed(stage_state: dict[str, object], stage_id: str) -> None:
    completed_stages = list(stage_state.setdefault("completed_stages", []))
    if stage_id not in completed_stages:
        completed_stages.append(stage_id)
    stage_state["completed_stages"] = completed_stages


def mark_stage_skipped(stage_state: dict[str, object], stage_id: str) -> None:
    skipped_stages = list(stage_state.setdefault("skipped_stages", []))
    if stage_id not in skipped_stages:
        skipped_stages.append(stage_id)
    stage_state["skipped_stages"] = skipped_stages


def stage_state_value(stage_state: dict[str, object], key: str, fallback: str) -> str:
    value = stage_state.get(key, fallback)
    return str(value) if value is not None else fallback


def build_summary_payload(
    *,
    status: str,
    input_audio_path: Path,
    output_dir: Path,
    decoded_path: Path,
    teacher_route_handoff_path: Path | None,
    teacher_checkpoint_path: Path | None,
    calibration_asset_path: Path | None,
    vocoder_checkpoint_path: Path | None,
    vocoder_checkpoint_selection_path: Path | None,
    selection_target: str,
    verify_against_full_pass: bool,
    save_intermediates: bool,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    contract_tensor_path: Path | None,
    scaffold_tensor_path: Path | None,
    contract_runtime: dict[str, object],
    teacher_summary: dict[str, object],
    conditioning_summary: dict[str, object],
    selection_summary: dict[str, object] | None,
    branch_label: str | None,
    decoded_waveform: torch.Tensor | None,
    sample_rate: int | None,
    completed_stages: list[str],
    skipped_stages: list[str],
    current_stage: str | None,
    failure: dict[str, object] | None,
) -> dict[str, object]:
    decoded_audio_samples = None if decoded_waveform is None else int(decoded_waveform.shape[0])
    decoded_audio_sec = None
    decoded_waveform_rms = None
    decoded_spectral_summary = None
    if decoded_waveform is not None and sample_rate:
        decoded_audio_sec = round(float(decoded_waveform.shape[0] / sample_rate), 6)
        decoded_waveform_rms = round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6)
        decoded_spectral_summary = compute_waveform_spectral_summary(decoded_waveform, int(sample_rate))
    applicability_risk = assess_runtime_applicability_risk(
        decoded_spectral_summary=decoded_spectral_summary,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_apply_mode=str(predicted_activity_gate_apply_mode),
    )
    notes = [
        "This command is a teacher-first single-target demo path, not the final product-grade many-to-many runtime.",
        "decoded.wav is generated without aligned_target-dependent pitch matching, audit proxy, or validation-side loss readouts.",
        "The current target conditioning still comes from the existing calibration asset and therefore represents a fixed single-target preset.",
        "When stable_late_stop is absent from a checkpoint-selection payload, prefer best_validation or pass an explicit vocoder checkpoint.",
        "pipeline.layers exposes a user-facing failure ladder so the summary shows whether the run stopped at teacher runtime, contract, scaffold, vocoder checkpoint, or waveform reconstruction.",
    ]
    risk_status = str(applicability_risk.get("status"))
    if risk_status in {"high_risk", "elevated_risk"}:
        notes.append(
            "applicability_risk flags that decoded spectral behavior may sit outside the currently known healthy Stage5 user-line range; treat the output as diagnostic rather than product-grade audio."
        )
    if failure is not None:
        notes.append(
            "Failure summaries are written to teacher_first_vc_demo.json/.md so the terminal-user path remains diagnosable."
        )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_demo_v1",
        "status": status,
        "input_audio_path": safe_resolve_path(input_audio_path),
        "output_dir": output_dir.as_posix(),
        "decoded_audio_path": decoded_path.as_posix(),
        "decoded_audio_exists": decoded_path.exists(),
        "decoded_audio_samples": decoded_audio_samples,
        "decoded_audio_sec": decoded_audio_sec,
        "decoded_waveform_rms": decoded_waveform_rms,
        "teacher": {
            "experiment_id": teacher_summary.get("experiment_id"),
            "checkpoint_path": teacher_summary.get("checkpoint_path")
            or safe_resolve_path(teacher_checkpoint_path),
            "route_handoff_path": teacher_summary.get("route_handoff_path")
            or safe_resolve_path(teacher_route_handoff_path),
            "verify_against_full_pass": bool(verify_against_full_pass),
            "chunk_samples": contract_runtime.get("chunk_samples"),
            "chunk_ms": contract_runtime.get("chunk_ms"),
        },
        "conditioning": (
            conditioning_summary
            if conditioning_summary
            else {
                "asset_path": safe_resolve_path(calibration_asset_path),
            }
        ),
        "vocoder": {
            "checkpoint_path": safe_resolve_path(vocoder_checkpoint_path),
            "checkpoint_selection_path": safe_resolve_path(vocoder_checkpoint_selection_path),
            "selection_target": str(selection_target),
            "selection_summary": selection_summary,
            "branch_label": branch_label,
        },
        "waveform_decode": {
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": predicted_activity_gate_apply_mode,
            "decoded_spectral_summary": decoded_spectral_summary,
        },
        "applicability_risk": applicability_risk,
        "pipeline": {
            "current_stage": current_stage,
            "completed_stages": list(completed_stages),
            "skipped_stages": list(skipped_stages),
            "layers": build_pipeline_layers(
                completed_stages=completed_stages,
                skipped_stages=skipped_stages,
                current_stage=current_stage,
            ),
        },
        "artifacts": {
            "save_intermediates": bool(save_intermediates),
            "teacher_contract_path": None if contract_tensor_path is None else contract_tensor_path.as_posix(),
            "teacher_vocoder_input_scaffold_path": (
                None if scaffold_tensor_path is None else scaffold_tensor_path.as_posix()
            ),
        },
        "failure": failure,
        "notes": notes,
    }


def build_pipeline_layers(
    *,
    completed_stages: list[str],
    skipped_stages: list[str],
    current_stage: str | None,
) -> list[dict[str, object]]:
    done_stages = set(completed_stages) | set(skipped_stages)
    layers = []
    for layer in PIPELINE_LAYER_DEFINITIONS:
        stage_ids = tuple(layer["stage_ids"])
        if current_stage in stage_ids:
            status = "failed"
        elif all(stage_id in done_stages for stage_id in stage_ids):
            status = "succeeded"
        elif any(stage_id in done_stages for stage_id in stage_ids):
            status = "partial"
        else:
            status = "pending"
        layers.append(
            {
                "layer_id": layer["layer_id"],
                "label": layer["label"],
                "status": status,
                "stage_ids": list(stage_ids),
            }
        )
    return layers


def assess_runtime_applicability_risk(
    *,
    decoded_spectral_summary: dict[str, object] | None,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_apply_mode: str,
) -> dict[str, object]:
    if not isinstance(decoded_spectral_summary, dict):
        return {
            "heuristic_version": DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION,
            "status": "unknown",
            "summary": "Applicability risk could not be estimated because decoded spectral statistics are unavailable.",
            "signals": [],
            "recommended_actions": [],
        }
    centroid_hz = float(decoded_spectral_summary["centroid_hz"])
    rolloff95_hz = float(decoded_spectral_summary["rolloff95_hz"])
    high_band_energy_ratio = float(decoded_spectral_summary["high_band_energy_ratio"])
    high_risk_signals = []
    elevated_risk_signals = []
    if high_band_energy_ratio >= HIGH_RISK_HIGH_BAND_ENERGY_RATIO:
        high_risk_signals.append(
            f"decoded high-band-energy ratio {high_band_energy_ratio:.6f} exceeds the current high-risk threshold {HIGH_RISK_HIGH_BAND_ENERGY_RATIO:.2f}"
        )
    elif high_band_energy_ratio >= ELEVATED_RISK_HIGH_BAND_ENERGY_RATIO:
        elevated_risk_signals.append(
            f"decoded high-band-energy ratio {high_band_energy_ratio:.6f} exceeds the elevated-risk threshold {ELEVATED_RISK_HIGH_BAND_ENERGY_RATIO:.2f}"
        )
    if rolloff95_hz >= HIGH_RISK_SPECTRAL_ROLLOFF95_HZ:
        high_risk_signals.append(
            f"decoded rolloff95 {rolloff95_hz:.3f} Hz exceeds the current high-risk threshold {HIGH_RISK_SPECTRAL_ROLLOFF95_HZ:.1f} Hz"
        )
    elif rolloff95_hz >= ELEVATED_RISK_SPECTRAL_ROLLOFF95_HZ:
        elevated_risk_signals.append(
            f"decoded rolloff95 {rolloff95_hz:.3f} Hz exceeds the elevated-risk threshold {ELEVATED_RISK_SPECTRAL_ROLLOFF95_HZ:.1f} Hz"
        )
    if centroid_hz >= HIGH_RISK_SPECTRAL_CENTROID_HZ:
        high_risk_signals.append(
            f"decoded spectral centroid {centroid_hz:.3f} Hz exceeds the current high-risk threshold {HIGH_RISK_SPECTRAL_CENTROID_HZ:.1f} Hz"
        )
    elif centroid_hz >= ELEVATED_RISK_SPECTRAL_CENTROID_HZ:
        elevated_risk_signals.append(
            f"decoded spectral centroid {centroid_hz:.3f} Hz exceeds the elevated-risk threshold {ELEVATED_RISK_SPECTRAL_CENTROID_HZ:.1f} Hz"
        )
    if high_risk_signals:
        status = "high_risk"
        summary = (
            "Decoded spectral behavior crosses the current high-risk buzzing heuristics derived from the 2026-03-21 user-line decoder probe."
        )
    elif len(elevated_risk_signals) >= 2:
        status = "elevated_risk"
        summary = (
            "Decoded spectral behavior crosses multiple elevated-risk heuristics and may sit near the known buzzing boundary."
        )
    else:
        status = "low_risk"
        summary = "Decoded spectral behavior does not cross the current buzzing heuristics."
    signals = high_risk_signals if high_risk_signals else elevated_risk_signals
    recommended_actions = []
    if status in {"high_risk", "elevated_risk"}:
        recommended_actions = [
            "Treat this output as diagnostic and inspect the decoded wav before using it as a user-facing sample.",
            "Run analyze-offline-mvp-teacher-first-vc-decoder-behavior with post_ola_envelope, pre_overlap_add, and disabled predicted gate to isolate whether the gate path is amplifying the artifact.",
            "If the risk persists across decode settings, treat the current Stage5 checkpoint as out-of-distribution for this user-line control payload.",
        ]
    return {
        "heuristic_version": DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION,
        "status": status,
        "summary": summary,
        "use_predicted_activity_gate": bool(use_predicted_activity_gate),
        "predicted_activity_gate_apply_mode": str(predicted_activity_gate_apply_mode),
        "decoded_spectral_summary": decoded_spectral_summary,
        "signals": signals,
        "recommended_actions": recommended_actions,
    }


def build_failure_payload(
    *,
    stage_id: str,
    error: Exception,
) -> dict[str, object]:
    metadata = STAGE_METADATA.get(
        stage_id,
        {
            "layer_id": "unknown",
            "label": stage_id,
            "diagnostic_summary": "The teacher-first demo failed at an unclassified stage.",
            "likely_causes": [],
            "recommended_actions": [],
        },
    )
    layer_label = next(
        (
            layer["label"]
            for layer in PIPELINE_LAYER_DEFINITIONS
            if layer["layer_id"] == metadata["layer_id"]
        ),
        metadata["layer_id"],
    )
    return {
        "layer": metadata["layer_id"],
        "layer_label": layer_label,
        "stage": stage_id,
        "stage_label": metadata["label"],
        "error_type": type(error).__name__,
        "error_message": str(error),
        "diagnostic_summary": metadata["diagnostic_summary"],
        "likely_causes": list(metadata["likely_causes"]),
        "recommended_actions": list(metadata["recommended_actions"]),
    }


def safe_resolve_path(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.resolve(strict=False).as_posix()


def write_summary(
    summary_json_path: Path,
    summary_md_path: Path,
    summary: dict[str, object],
) -> None:
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_markdown(summary: dict[str, object]) -> str:
    teacher = dict(summary["teacher"])
    conditioning = dict(summary["conditioning"])
    vocoder = dict(summary["vocoder"])
    waveform_decode = dict(summary["waveform_decode"])
    applicability_risk = dict(summary.get("applicability_risk", {}))
    pipeline = dict(summary.get("pipeline", {}))
    artifacts = dict(summary["artifacts"])
    failure = summary.get("failure")
    lines = [
        "# Teacher-First Single-Target VC Demo",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- status: {summary.get('status')}",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- output_dir: {summary.get('output_dir')}",
        f"- decoded_audio_path: {summary['decoded_audio_path']}",
        f"- decoded_audio_exists: {summary.get('decoded_audio_exists')}",
        f"- decoded_audio_samples: {summary['decoded_audio_samples']}",
        f"- decoded_audio_sec: {summary['decoded_audio_sec']}",
        f"- decoded_waveform_rms: {summary['decoded_waveform_rms']}",
        "",
        "## Teacher",
        f"- experiment_id: {teacher.get('experiment_id')}",
        f"- checkpoint_path: {teacher.get('checkpoint_path')}",
        f"- route_handoff_path: {teacher.get('route_handoff_path')}",
        f"- verify_against_full_pass: {teacher.get('verify_against_full_pass')}",
        f"- chunk_samples: {teacher.get('chunk_samples')}",
        f"- chunk_ms: {teacher.get('chunk_ms')}",
        "",
        "## Conditioning",
        f"- asset_path: {conditioning.get('asset_path')}",
        f"- asset_status: {conditioning.get('asset_status')}",
        f"- speaker_dim: {conditioning.get('speaker_dim')}",
        f"- geom_dim: {conditioning.get('geom_dim')}",
        f"- alpha: {conditioning.get('alpha')}",
        "",
        "## Vocoder",
        f"- checkpoint_path: {vocoder.get('checkpoint_path')}",
        f"- checkpoint_selection_path: {vocoder.get('checkpoint_selection_path')}",
        f"- selection_target: {vocoder.get('selection_target')}",
        f"- branch_label: {vocoder.get('branch_label')}",
        f"- selection_summary: {json.dumps(vocoder.get('selection_summary'), ensure_ascii=False)}",
        "",
        "## Waveform Decode",
        f"- {json.dumps(waveform_decode, ensure_ascii=False)}",
        "",
        "## Applicability Risk",
        f"- status: {applicability_risk.get('status')}",
        f"- summary: {applicability_risk.get('summary')}",
        f"- signals: {json.dumps(applicability_risk.get('signals'), ensure_ascii=False)}",
        f"- recommended_actions: {json.dumps(applicability_risk.get('recommended_actions'), ensure_ascii=False)}",
        "",
        "## Pipeline",
        f"- current_stage: {pipeline.get('current_stage')}",
        f"- completed_stages: {json.dumps(pipeline.get('completed_stages'), ensure_ascii=False)}",
        f"- skipped_stages: {json.dumps(pipeline.get('skipped_stages'), ensure_ascii=False)}",
    ]
    for layer in list(pipeline.get("layers", [])):
        if not isinstance(layer, dict):
            continue
        lines.append(
            f"- {layer.get('layer_id')}: status={layer.get('status')} stage_ids={json.dumps(layer.get('stage_ids'), ensure_ascii=False)}"
        )
    lines.extend(
        [
            "",
        "## Artifacts",
        f"- {json.dumps(artifacts, ensure_ascii=False)}",
        "",
        "## Failure",
        ]
    )
    if isinstance(failure, dict):
        lines.extend(
            [
                f"- layer: {failure.get('layer')}",
                f"- layer_label: {failure.get('layer_label')}",
                f"- stage: {failure.get('stage')}",
                f"- stage_label: {failure.get('stage_label')}",
                f"- error_type: {failure.get('error_type')}",
                f"- error_message: {failure.get('error_message')}",
                f"- diagnostic_summary: {failure.get('diagnostic_summary')}",
                f"- likely_causes: {json.dumps(failure.get('likely_causes'), ensure_ascii=False)}",
                f"- recommended_actions: {json.dumps(failure.get('recommended_actions'), ensure_ascii=False)}",
            ]
        )
    else:
        lines.append(f"- {json.dumps(failure, ensure_ascii=False)}")
    lines.extend(
        [
        "",
        "## Notes",
        ]
    )
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def run_teacher_first_vc_demo_self_check(
    *,
    input_audio_path: Path,
    output_dir: Path,
    device: str,
    max_audio_sec: float | None,
) -> None:
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    baseline_case_dir = cases_dir / "success_baseline"
    baseline_case_result = execute_self_check_case(
        case_id="success_baseline",
        case_dir=baseline_case_dir,
        expect_status="succeeded",
        expect_failure_layer=None,
        expect_failure_stage=None,
        runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
            input_audio_path=input_audio_path,
            output_dir=case_output_dir,
            teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
            teacher_checkpoint_path=None,
            calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
            vocoder_checkpoint_path=None,
            vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
            selection_target="best_validation",
            chunk_samples=None,
            chunk_ms=None,
            device=device,
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=False,
            save_intermediates=False,
            use_predicted_activity_gate=True,
            predicted_activity_gate_floor=0.0,
            predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
            predicted_activity_gate_apply_mode="post_ola_envelope",
        ),
    )
    baseline_summary = load_teacher_first_vc_demo_summary(
        baseline_case_dir / "teacher_first_vc_demo.json"
    )
    baseline_teacher_checkpoint = Path(str(baseline_summary["teacher"]["checkpoint_path"]))
    baseline_vocoder_checkpoint = Path(str(baseline_summary["vocoder"]["checkpoint_path"]))
    tampered_checkpoint_path = materialize_tampered_vocoder_checkpoint(
        source_checkpoint_path=baseline_vocoder_checkpoint,
        output_path=output_dir / "tmp_inputs" / "tampered_stage5_vocoder_bad_periodic_dim.pt",
    )

    results = [baseline_case_result]
    results.append(
        execute_self_check_case(
            case_id="failure_bad_calibration",
            case_dir=cases_dir / "failure_bad_calibration",
            expect_status="failed",
            expect_failure_layer="teacher_contract",
            expect_failure_stage="conditioning_asset_load",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=output_dir / "tmp_inputs" / "missing_calibration.json",
                vocoder_checkpoint_path=None,
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )
    results.append(
        execute_self_check_case(
            case_id="failure_bad_vocoder_checkpoint_path",
            case_dir=cases_dir / "failure_bad_vocoder_checkpoint_path",
            expect_status="failed",
            expect_failure_layer="vocoder_checkpoint",
            expect_failure_stage="vocoder_checkpoint_resolution",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=output_dir / "tmp_inputs" / "missing_vocoder_checkpoint.pt",
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )
    results.append(
        execute_self_check_case(
            case_id="failure_wrong_checkpoint_family",
            case_dir=cases_dir / "failure_wrong_checkpoint_family",
            expect_status="failed",
            expect_failure_layer="vocoder_checkpoint",
            expect_failure_stage="vocoder_checkpoint_payload_load",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=baseline_teacher_checkpoint,
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )
    results.append(
        execute_self_check_case(
            case_id="failure_missing_selection_payload",
            case_dir=cases_dir / "failure_missing_selection_payload",
            expect_status="failed",
            expect_failure_layer="vocoder_checkpoint",
            expect_failure_stage="vocoder_checkpoint_resolution",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=None,
                vocoder_checkpoint_selection_path=output_dir / "tmp_inputs" / "missing_selection_payload.json",
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )
    results.append(
        execute_self_check_case(
            case_id="failure_stable_late_stop_missing",
            case_dir=cases_dir / "failure_stable_late_stop_missing",
            expect_status="failed",
            expect_failure_layer="vocoder_checkpoint",
            expect_failure_stage="vocoder_checkpoint_resolution",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=None,
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="stable_late_stop",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )
    results.append(
        execute_self_check_case(
            case_id="failure_checkpoint_scaffold_mismatch",
            case_dir=cases_dir / "failure_checkpoint_scaffold_mismatch",
            expect_status="failed",
            expect_failure_layer="vocoder_checkpoint",
            expect_failure_stage="vocoder_checkpoint_load",
            runner=lambda case_output_dir: run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=input_audio_path,
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=tampered_checkpoint_path,
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=None,
                device=device,
                max_audio_sec=max_audio_sec,
                verify_against_full_pass=False,
                save_intermediates=True,
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            ),
        )
    )

    aggregate = build_self_check_summary(
        input_audio_path=input_audio_path,
        output_dir=output_dir,
        device=device,
        max_audio_sec=max_audio_sec,
        case_results=results,
    )
    write_self_check_summary(
        summary_json_path=output_dir / "teacher_first_vc_demo_self_check.json",
        summary_md_path=output_dir / "teacher_first_vc_demo_self_check.md",
        summary=aggregate,
    )
    if not bool(aggregate["all_passed"]):
        raise ValueError(
            "teacher-first VC demo self-check found mismatches; inspect teacher_first_vc_demo_self_check.json for details."
        )


def execute_self_check_case(
    *,
    case_id: str,
    case_dir: Path,
    expect_status: str,
    expect_failure_layer: str | None,
    expect_failure_stage: str | None,
    runner,
) -> dict[str, object]:
    exception: Exception | None = None
    try:
        runner(case_dir)
    except Exception as exc:
        exception = exc
    summary_path = case_dir / "teacher_first_vc_demo.json"
    summary = load_teacher_first_vc_demo_summary(summary_path)
    status = str(summary.get("status"))
    failure = summary.get("failure")
    actual_failure_layer = None if not isinstance(failure, dict) else failure.get("layer")
    actual_failure_stage = None if not isinstance(failure, dict) else failure.get("stage")
    checks = {
        "status_matches": status == expect_status,
        "failure_layer_matches": actual_failure_layer == expect_failure_layer,
        "failure_stage_matches": actual_failure_stage == expect_failure_stage,
    }
    passed = all(bool(value) for value in checks.values())
    return {
        "case_id": case_id,
        "passed": passed,
        "expected": {
            "status": expect_status,
            "failure_layer": expect_failure_layer,
            "failure_stage": expect_failure_stage,
        },
        "actual": {
            "status": status,
            "failure_layer": actual_failure_layer,
            "failure_stage": actual_failure_stage,
            "summary_path": summary_path.as_posix(),
        },
        "checks": checks,
        "exception": None
        if exception is None
        else {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
        },
        "branch_label": dict(summary.get("vocoder", {})).get("branch_label"),
    }


def load_teacher_first_vc_demo_summary(summary_path: Path) -> dict[str, object]:
    if not summary_path.is_file():
        raise FileNotFoundError(f"Expected self-check case summary is missing: {summary_path}")
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Unsupported self-check case summary payload type: {type(payload)!r}")
    return payload


def materialize_tampered_vocoder_checkpoint(
    *,
    source_checkpoint_path: Path,
    output_path: Path,
) -> Path:
    checkpoint_payload = load_vocoder_checkpoint_payload(source_checkpoint_path)
    state_dict = dict(checkpoint_payload["model_state_dict"])
    periodic_weight = state_dict["periodic_encoder.0.weight"]
    if int(periodic_weight.shape[1]) <= 1:
        raise ValueError("Cannot materialize tampered vocoder checkpoint from a degenerate periodic input dimension.")
    state_dict["periodic_encoder.0.weight"] = periodic_weight[:, :-1].contiguous()
    tampered_payload = dict(checkpoint_payload)
    tampered_payload["model_state_dict"] = state_dict
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(tampered_payload, output_path)
    return output_path


def build_self_check_summary(
    *,
    input_audio_path: Path,
    output_dir: Path,
    device: str,
    max_audio_sec: float | None,
    case_results: list[dict[str, object]],
) -> dict[str, object]:
    passed_count = sum(1 for item in case_results if bool(item.get("passed")))
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_demo_self_check_v1",
        "input_audio_path": safe_resolve_path(input_audio_path),
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "case_count": len(case_results),
        "passed_count": passed_count,
        "failed_count": len(case_results) - passed_count,
        "all_passed": passed_count == len(case_results),
        "cases": case_results,
        "notes": [
            "This self-check is a regression guard for the terminal-user teacher-first demo path.",
            "It exercises one short success path plus representative configuration and checkpoint misuse failures.",
            "Each case still writes its own teacher_first_vc_demo.json/.md so individual failures remain diagnosable.",
        ],
    }


def write_self_check_summary(
    *,
    summary_json_path: Path,
    summary_md_path: Path,
    summary: dict[str, object],
) -> None:
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_self_check_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_self_check_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Demo Self-Check",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- case_count: {summary['case_count']}",
        f"- passed_count: {summary['passed_count']}",
        f"- failed_count: {summary['failed_count']}",
        f"- all_passed: {summary['all_passed']}",
        "",
        "## Cases",
    ]
    for case in list(summary.get("cases", [])):
        if not isinstance(case, dict):
            continue
        lines.extend(
            [
                f"- case_id: {case.get('case_id')}",
                f"  passed: {case.get('passed')}",
                f"  expected: {json.dumps(case.get('expected'), ensure_ascii=False)}",
                f"  actual: {json.dumps(case.get('actual'), ensure_ascii=False)}",
                f"  checks: {json.dumps(case.get('checks'), ensure_ascii=False)}",
                f"  exception: {json.dumps(case.get('exception'), ensure_ascii=False)}",
                f"  branch_label: {case.get('branch_label')}",
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


def build_teacher_first_vc_review_bundle(
    *,
    output_dir: Path,
    input_audio_paths: list[Path] | None,
    input_spec_jsonl_path: Path | None,
    device: str,
    max_audio_sec_default: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    chunk_ms: float | None,
) -> None:
    resolved_specs = resolve_review_bundle_input_specs(
        input_audio_paths=input_audio_paths,
        input_spec_jsonl_path=input_spec_jsonl_path,
        max_audio_sec_default=max_audio_sec_default,
    )
    if not resolved_specs:
        raise ValueError("Review bundle requires at least one input audio.")

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    runs_dir = output_dir / "runs"
    listening_dir = output_dir / "listening"
    runs_dir.mkdir(parents=True, exist_ok=True)
    listening_dir.mkdir(parents=True, exist_ok=True)

    persisted_specs_path = output_dir / "review_bundle_input_specs.jsonl"
    persisted_specs_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in resolved_specs) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    case_results: list[dict[str, object]] = []
    for index, spec in enumerate(resolved_specs, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=spec.get("case_id"),
            input_audio_path=Path(str(spec["input_audio_path"])),
            index=index,
        )
        case_output_dir = runs_dir / case_id
        exception: Exception | None = None
        try:
            run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=Path(str(spec["input_audio_path"])),
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
                vocoder_checkpoint_path=None,
                vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
                selection_target="best_validation",
                chunk_samples=None,
                chunk_ms=chunk_ms,
                device=device,
                max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
                verify_against_full_pass=bool(verify_against_full_pass),
                save_intermediates=bool(save_intermediates),
                use_predicted_activity_gate=True,
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode="post_ola_envelope",
            )
        except Exception as exc:
            exception = exc
        summary = load_teacher_first_vc_demo_summary(case_output_dir / "teacher_first_vc_demo.json")
        listening_audio_path = None
        if bool(summary.get("decoded_audio_exists")):
            copied_name = f"{case_id}.wav"
            listening_audio_path = listening_dir / copied_name
            shutil.copy2(case_output_dir / "decoded.wav", listening_audio_path)
        vocoder = dict(summary.get("vocoder", {}))
        failure = summary.get("failure")
        case_results.append(
            {
                "case_index": index,
                "case_id": case_id,
                "status": summary.get("status"),
                "input_audio_path": summary.get("input_audio_path"),
                "max_audio_sec": spec.get("max_audio_sec"),
                "summary_path": (case_output_dir / "teacher_first_vc_demo.json").as_posix(),
                "decoded_audio_path": summary.get("decoded_audio_path"),
                "listening_audio_path": None if listening_audio_path is None else listening_audio_path.as_posix(),
                "decoded_audio_sec": summary.get("decoded_audio_sec"),
                "decoded_waveform_rms": summary.get("decoded_waveform_rms"),
                "branch_label": vocoder.get("branch_label"),
                "failure": failure,
                "exception": None
                if exception is None
                else {
                    "error_type": type(exception).__name__,
                    "error_message": str(exception),
                },
                "notes": list(spec.get("notes", [])) if isinstance(spec.get("notes"), list) else [],
            }
        )

    bundle_summary = build_review_bundle_summary(
        output_dir=output_dir,
        device=device,
        chunk_ms=chunk_ms,
        save_intermediates=save_intermediates,
        verify_against_full_pass=verify_against_full_pass,
        case_results=case_results,
        input_spec_jsonl_path=input_spec_jsonl_path,
        persisted_specs_path=persisted_specs_path,
    )
    write_review_bundle_summary(
        summary_json_path=output_dir / "teacher_first_vc_review_bundle.json",
        summary_md_path=output_dir / "teacher_first_vc_review_bundle.md",
        summary=bundle_summary,
    )
    if not bool(bundle_summary["all_succeeded"]):
        raise ValueError(
            "teacher-first VC review bundle contains failed cases; inspect teacher_first_vc_review_bundle.json for details."
        )


def resolve_review_bundle_input_specs(
    *,
    input_audio_paths: list[Path] | None,
    input_spec_jsonl_path: Path | None,
    max_audio_sec_default: float | None,
) -> list[dict[str, object]]:
    resolved_specs: list[dict[str, object]] = []
    if input_spec_jsonl_path is not None:
        for row in load_jsonl(input_spec_jsonl_path.resolve()):
            input_audio_value = row.get("input_audio_path")
            if input_audio_value in {None, ""}:
                raise ValueError("Each review bundle spec row must include input_audio_path.")
            resolved_specs.append(
                {
                    "case_id": row.get("case_id"),
                    "input_audio_path": safe_resolve_path(Path(str(input_audio_value))),
                    "max_audio_sec": coerce_optional_float(row.get("max_audio_sec")),
                    "notes": list(row.get("notes", [])) if isinstance(row.get("notes"), list) else [],
                }
            )
    for path in list(input_audio_paths or []):
        resolved_specs.append(
            {
                "case_id": None,
                "input_audio_path": safe_resolve_path(path),
                "max_audio_sec": max_audio_sec_default,
                "notes": [],
            }
        )
    return resolved_specs


def build_review_bundle_case_id(
    *,
    raw_case_id: object,
    input_audio_path: Path,
    index: int,
) -> str:
    if raw_case_id not in {None, ""}:
        base = str(raw_case_id)
    else:
        base = input_audio_path.stem
    sanitized = "".join(
        char if char.isalnum() or char in {"_", "-"} else "_"
        for char in base
    ).strip("_")
    if not sanitized:
        sanitized = f"case_{index:03d}"
    return f"{index:03d}_{sanitized}"


def coerce_optional_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    return float(value)


def build_review_bundle_summary(
    *,
    output_dir: Path,
    device: str,
    chunk_ms: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    case_results: list[dict[str, object]],
    input_spec_jsonl_path: Path | None,
    persisted_specs_path: Path,
) -> dict[str, object]:
    succeeded_count = sum(1 for item in case_results if str(item.get("status")) == "succeeded")
    failed_count = len(case_results) - succeeded_count
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_review_bundle_v1",
        "output_dir": output_dir.as_posix(),
        "input_spec_jsonl_path": safe_resolve_path(input_spec_jsonl_path),
        "materialized_input_specs_path": persisted_specs_path.as_posix(),
        "device": str(device),
        "chunk_ms": chunk_ms,
        "save_intermediates": bool(save_intermediates),
        "verify_against_full_pass": bool(verify_against_full_pass),
        "case_count": len(case_results),
        "succeeded_count": succeeded_count,
        "failed_count": failed_count,
        "all_succeeded": failed_count == 0,
        "listening_dir": (output_dir / "listening").as_posix(),
        "runs_dir": (output_dir / "runs").as_posix(),
        "cases": case_results,
        "notes": [
            "This bundle is for terminal-user listening review, not paired validation against aligned_target.",
            "Each case is exported with the current teacher-first single-target runtime defaults, including post_ola_envelope decode.",
            "listening/ contains flattened decoded wav files for quick review; runs/ retains full per-case summaries and optional intermediates.",
        ],
    }


def write_review_bundle_summary(
    *,
    summary_json_path: Path,
    summary_md_path: Path,
    summary: dict[str, object],
) -> None:
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_review_bundle_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_review_bundle_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Review Bundle",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- input_spec_jsonl_path: {summary['input_spec_jsonl_path']}",
        f"- materialized_input_specs_path: {summary['materialized_input_specs_path']}",
        f"- device: {summary['device']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- save_intermediates: {summary['save_intermediates']}",
        f"- verify_against_full_pass: {summary['verify_against_full_pass']}",
        f"- case_count: {summary['case_count']}",
        f"- succeeded_count: {summary['succeeded_count']}",
        f"- failed_count: {summary['failed_count']}",
        f"- all_succeeded: {summary['all_succeeded']}",
        f"- listening_dir: {summary['listening_dir']}",
        f"- runs_dir: {summary['runs_dir']}",
        "",
        "## Cases",
    ]
    for case in list(summary.get("cases", [])):
        if not isinstance(case, dict):
            continue
        lines.extend(
            [
                f"- case_index: {case.get('case_index')}",
                f"  case_id: {case.get('case_id')}",
                f"  status: {case.get('status')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  max_audio_sec: {case.get('max_audio_sec')}",
                f"  listening_audio_path: {case.get('listening_audio_path')}",
                f"  decoded_audio_sec: {case.get('decoded_audio_sec')}",
                f"  decoded_waveform_rms: {case.get('decoded_waveform_rms')}",
                f"  branch_label: {case.get('branch_label')}",
                f"  summary_path: {case.get('summary_path')}",
                f"  failure: {json.dumps(case.get('failure'), ensure_ascii=False)}",
                f"  exception: {json.dumps(case.get('exception'), ensure_ascii=False)}",
                f"  notes: {json.dumps(case.get('notes'), ensure_ascii=False)}",
            ]
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def analyze_teacher_first_vc_applicability(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    reference_package_paths: list[Path],
    reference_package_limit: int,
    device: str,
    max_audio_sec: float | None,
    chunk_ms: float | None,
) -> None:
    resolved_reference_packages = resolve_reference_package_paths(
        reference_package_paths=reference_package_paths,
        reference_package_limit=reference_package_limit,
    )
    if not resolved_reference_packages:
        raise ValueError("Applicability probe requires at least one reference Stage5 training package.")
    if not input_audio_paths:
        raise ValueError("Applicability probe requires at least one input audio.")

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    reference_summary = build_reference_distribution_summary(resolved_reference_packages)
    case_summaries = []
    for index, input_audio_path in enumerate(input_audio_paths, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=None,
            input_audio_path=input_audio_path.resolve(),
            index=index,
        )
        case_output_dir = cases_dir / case_id
        run_offline_mvp_teacher_first_vc_demo(
            input_audio_path=input_audio_path,
            output_dir=case_output_dir,
            teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
            teacher_checkpoint_path=None,
            calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
            vocoder_checkpoint_path=None,
            vocoder_checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
            selection_target="best_validation",
            chunk_samples=None,
            chunk_ms=chunk_ms,
            device=device,
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=False,
            save_intermediates=True,
            use_predicted_activity_gate=True,
            predicted_activity_gate_floor=0.0,
            predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
            predicted_activity_gate_apply_mode="post_ola_envelope",
        )
        demo_summary = load_teacher_first_vc_demo_summary(case_output_dir / "teacher_first_vc_demo.json")
        scaffold_payload = torch.load(
            case_output_dir / "teacher_vocoder_input_scaffold" / "teacher_vocoder_input_scaffold.pt",
            map_location="cpu",
            weights_only=False,
        )
        case_summaries.append(
            build_applicability_case_summary(
                case_id=case_id,
                demo_summary=demo_summary,
                scaffold_payload=scaffold_payload,
                reference_summary=reference_summary,
            )
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_applicability_probe_v1",
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "chunk_ms": chunk_ms,
        "reference_package_count": len(resolved_reference_packages),
        "reference_packages": [path.as_posix() for path in resolved_reference_packages],
        "reference_summary": reference_summary,
        "case_count": len(case_summaries),
        "cases": case_summaries,
        "notes": [
            "This probe compares teacher-first user-line scaffold features against Stage5 training-package input distributions.",
            "Large deviations here indicate that a runnable source-to-target path does not automatically imply the current user-line controls are in-distribution for the no-res vocoder.",
            "The goal is applicability diagnosis, not listening review or checkpoint ranking.",
        ],
    }
    (output_dir / "teacher_first_vc_applicability_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_first_vc_applicability_probe.md").write_text(
        build_applicability_probe_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_reference_package_paths(
    *,
    reference_package_paths: list[Path],
    reference_package_limit: int,
) -> list[Path]:
    if reference_package_paths:
        return [path.resolve() for path in reference_package_paths]
    default_root = Path(
        "reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/train"
    )
    candidates = sorted(default_root.rglob("offline_mvp_nores_vocoder_train_targets.pt"))
    if reference_package_limit > 0:
        candidates = candidates[:reference_package_limit]
    return [path.resolve() for path in candidates]


def build_reference_distribution_summary(reference_package_paths: list[Path]) -> dict[str, object]:
    periodic_batches = []
    noise_batches = []
    for package_path in reference_package_paths:
        payload = load_training_package_payload(package_path)
        batch = extract_training_batch(payload)
        periodic_batches.append(batch["periodic_branch_features"].to(torch.float32))
        noise_batches.append(batch["noise_branch_features"].to(torch.float32))
    periodic_all = torch.cat(periodic_batches, dim=0)
    noise_all = torch.cat(noise_batches, dim=0)
    return {
        "periodic": summarize_feature_distribution(periodic_all),
        "noise": summarize_feature_distribution(noise_all),
    }


def summarize_feature_distribution(features: torch.Tensor) -> dict[str, object]:
    tensor = features.to(torch.float32)
    per_dim_mean = tensor.mean(dim=0)
    per_dim_std = tensor.std(dim=0, unbiased=False)
    per_dim_min = tensor.amin(dim=0)
    per_dim_max = tensor.amax(dim=0)
    quantiles = torch.quantile(tensor, torch.tensor([0.01, 0.5, 0.99], dtype=torch.float32), dim=0)
    return {
        "frame_count": int(tensor.shape[0]),
        "feature_dim": int(tensor.shape[1]),
        "global_mean": round(float(tensor.mean().item()), 6),
        "global_std": round(float(tensor.std(unbiased=False).item()), 6),
        "per_dim_mean": [round(float(value), 6) for value in per_dim_mean.tolist()],
        "per_dim_std": [round(float(value), 6) for value in per_dim_std.tolist()],
        "per_dim_min": [round(float(value), 6) for value in per_dim_min.tolist()],
        "per_dim_max": [round(float(value), 6) for value in per_dim_max.tolist()],
        "per_dim_q01": [round(float(value), 6) for value in quantiles[0].tolist()],
        "per_dim_median": [round(float(value), 6) for value in quantiles[1].tolist()],
        "per_dim_q99": [round(float(value), 6) for value in quantiles[2].tolist()],
    }


def build_applicability_case_summary(
    *,
    case_id: str,
    demo_summary: dict[str, object],
    scaffold_payload: dict[str, object],
    reference_summary: dict[str, object],
) -> dict[str, object]:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    periodic_semantics = list(branch_scaffold.get("periodic_feature_semantics", []))
    noise_semantics = list(branch_scaffold.get("noise_feature_semantics", []))
    periodic_features = branch_scaffold["periodic_branch_features"].to(torch.float32)
    noise_features = branch_scaffold["noise_branch_features"].to(torch.float32)
    periodic_analysis = analyze_feature_shift(
        candidate_features=periodic_features,
        reference_distribution=dict(reference_summary["periodic"]),
        feature_semantics=periodic_semantics,
    )
    noise_analysis = analyze_feature_shift(
        candidate_features=noise_features,
        reference_distribution=dict(reference_summary["noise"]),
        feature_semantics=noise_semantics,
    )
    return {
        "case_id": case_id,
        "input_audio_path": demo_summary.get("input_audio_path"),
        "decoded_audio_path": demo_summary.get("decoded_audio_path"),
        "decoded_audio_sec": demo_summary.get("decoded_audio_sec"),
        "decoded_waveform_rms": demo_summary.get("decoded_waveform_rms"),
        "branch_label": dict(demo_summary.get("vocoder", {})).get("branch_label"),
        "periodic": periodic_analysis,
        "noise": noise_analysis,
    }


def analyze_feature_shift(
    *,
    candidate_features: torch.Tensor,
    reference_distribution: dict[str, object],
    feature_semantics: list[object],
) -> dict[str, object]:
    candidate = candidate_features.to(torch.float32)
    candidate_mean = candidate.mean(dim=0)
    candidate_std = candidate.std(dim=0, unbiased=False)
    reference_mean = torch.tensor(reference_distribution["per_dim_mean"], dtype=torch.float32)
    reference_std = torch.tensor(reference_distribution["per_dim_std"], dtype=torch.float32)
    reference_q01 = torch.tensor(reference_distribution["per_dim_q01"], dtype=torch.float32)
    reference_q99 = torch.tensor(reference_distribution["per_dim_q99"], dtype=torch.float32)
    mean_z = (candidate_mean - reference_mean).abs() / torch.clamp(reference_std, min=1.0e-6)
    out_of_band_fraction = (
        ((candidate < reference_q01.unsqueeze(0)) | (candidate > reference_q99.unsqueeze(0)))
        .to(torch.float32)
        .mean(dim=0)
    )
    top_shift_indices = torch.argsort(mean_z, descending=True)[: min(8, int(candidate.shape[1]))]
    top_shift_channels = []
    for index in top_shift_indices.tolist():
        top_shift_channels.append(
            {
                "index": int(index),
                "semantic": normalize_feature_semantic(feature_semantics, index),
                "candidate_mean": round(float(candidate_mean[index].item()), 6),
                "candidate_std": round(float(candidate_std[index].item()), 6),
                "reference_mean": round(float(reference_mean[index].item()), 6),
                "reference_std": round(float(reference_std[index].item()), 6),
                "mean_abs_z": round(float(mean_z[index].item()), 6),
                "out_of_q01_q99_fraction": round(float(out_of_band_fraction[index].item()), 6),
            }
        )
    return {
        "frame_count": int(candidate.shape[0]),
        "feature_dim": int(candidate.shape[1]),
        "global_mean": round(float(candidate.mean().item()), 6),
        "global_std": round(float(candidate.std(unbiased=False).item()), 6),
        "mean_abs_z_median": round(float(torch.median(mean_z).item()), 6),
        "mean_abs_z_max": round(float(torch.max(mean_z).item()), 6),
        "out_of_q01_q99_fraction_mean": round(float(out_of_band_fraction.mean().item()), 6),
        "top_shift_channels": top_shift_channels,
    }


def normalize_feature_semantic(feature_semantics: list[object], index: int) -> str:
    if index >= len(feature_semantics):
        return f"feature_{index}"
    value = feature_semantics[index]
    return str(value)


def build_applicability_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Applicability Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- reference_package_count: {summary['reference_package_count']}",
        f"- case_count: {summary['case_count']}",
        "",
        "## Cases",
    ]
    for case in list(summary.get("cases", [])):
        if not isinstance(case, dict):
            continue
        lines.extend(
            [
                f"- case_id: {case.get('case_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  decoded_audio_sec: {case.get('decoded_audio_sec')}",
                f"  decoded_waveform_rms: {case.get('decoded_waveform_rms')}",
                f"  branch_label: {case.get('branch_label')}",
                f"  periodic: {json.dumps(case.get('periodic'), ensure_ascii=False)}",
                f"  noise: {json.dumps(case.get('noise'), ensure_ascii=False)}",
            ]
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def analyze_teacher_first_vc_decoder_behavior(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    reference_package_paths: list[Path],
    reference_package_limit: int,
    device: str,
    max_audio_sec: float | None,
    chunk_ms: float | None,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_apply_mode: str,
    normalization_strategy: str,
    control_family_overrides: list[str] | None,
) -> None:
    resolved_reference_packages = resolve_reference_package_paths(
        reference_package_paths=reference_package_paths,
        reference_package_limit=reference_package_limit,
    )
    if not resolved_reference_packages:
        raise ValueError("Decoder-behavior probe requires at least one reference Stage5 training package.")
    if not input_audio_paths:
        raise ValueError("Decoder-behavior probe requires at least one input audio.")

    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=None,
        checkpoint_selection_path=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
        selection_target="best_validation",
    )
    checkpoint_payload = load_vocoder_checkpoint_payload(resolved_checkpoint_path)
    resolved_device = resolve_runtime_device(device)
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    resolved_normalization_strategy = normalize_decoder_probe_normalization_strategy(normalization_strategy)
    resolved_control_family_overrides = parse_decoder_probe_control_family_overrides(control_family_overrides)

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    reference_feature_summary = build_reference_distribution_summary(resolved_reference_packages)
    reference_summary = build_reference_decoder_behavior_summary(
        reference_package_paths=resolved_reference_packages,
        checkpoint_payload=checkpoint_payload,
        checkpoint_path=resolved_checkpoint_path,
        selection_summary=selection_summary,
        device=resolved_device,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=0.0,
        predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        predicted_activity_gate_apply_mode=resolved_apply_mode,
    )
    case_summaries = []
    for index, input_audio_path in enumerate(input_audio_paths, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=None,
            input_audio_path=input_audio_path.resolve(),
            index=index,
        )
        case_output_dir = cases_dir / case_id
        run_offline_mvp_teacher_first_vc_demo(
            input_audio_path=input_audio_path,
            output_dir=case_output_dir,
            teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
            teacher_checkpoint_path=None,
            calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
            vocoder_checkpoint_path=resolved_checkpoint_path,
            vocoder_checkpoint_selection_path=None,
            selection_target="best_validation",
            chunk_samples=None,
            chunk_ms=chunk_ms,
            device=str(device),
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=False,
            save_intermediates=True,
            use_predicted_activity_gate=bool(use_predicted_activity_gate),
            predicted_activity_gate_floor=0.0,
            predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
            predicted_activity_gate_apply_mode=resolved_apply_mode,
        )
        demo_summary = load_teacher_first_vc_demo_summary(case_output_dir / "teacher_first_vc_demo.json")
        scaffold_payload = torch.load(
            case_output_dir / "teacher_vocoder_input_scaffold" / "teacher_vocoder_input_scaffold.pt",
            map_location="cpu",
            weights_only=False,
        )
        if not isinstance(scaffold_payload, dict):
            raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")
        normalized_scaffold_payload, normalization_summary = normalize_scaffold_payload_for_decoder_probe(
            scaffold_payload=scaffold_payload,
            reference_feature_summary=reference_feature_summary,
            normalization_strategy=resolved_normalization_strategy,
            control_family_overrides=resolved_control_family_overrides,
        )
        case_summaries.append(
            build_decoder_behavior_case_summary(
                case_id=case_id,
                demo_summary=demo_summary,
                scaffold_payload=normalized_scaffold_payload,
                checkpoint_payload=checkpoint_payload,
                device=resolved_device,
                reference_metric_distribution=dict(reference_summary["metric_distribution"]),
                use_predicted_activity_gate=bool(use_predicted_activity_gate),
                predicted_activity_gate_floor=0.0,
                predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                predicted_activity_gate_apply_mode=resolved_apply_mode,
                normalization_summary=normalization_summary,
                probe_decoded_audio_path=case_output_dir / "decoder_probe_decoded.wav",
            )
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_decoder_behavior_probe_v1",
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "chunk_ms": chunk_ms,
        "waveform_decode": {
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": 0.0,
            "predicted_activity_gate_smoothing_frames": DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
            "normalization_strategy": resolved_normalization_strategy,
            "control_family_overrides": serialize_decoder_probe_control_family_overrides(
                resolved_control_family_overrides
            ),
        },
        "reference_package_count": len(resolved_reference_packages),
        "reference_packages": [path.as_posix() for path in resolved_reference_packages],
        "reference_feature_summary": reference_feature_summary,
        "reference_decoder_behavior": reference_summary,
        "case_count": len(case_summaries),
        "cases": case_summaries,
        "notes": [
            "This probe compares decoder-side behavior for teacher-first user-line cases against the same checkpoint on in-distribution Stage5 training packages.",
            "If user-line inputs look only mildly shifted at the scaffold level but decoder metrics are extreme here, the failure is more likely a checkpoint-conditioning applicability issue than a simple file or routing bug.",
            "High decoded spectral centroid, high high-band-energy ratio, or heavy waveform-frame clipping relative to reference cases are strong signs of the observed high-frequency buzzing failure mode.",
            "normalization_strategy is inference-only probe logic; it does not modify the saved teacher contract or the main user-line runtime defaults.",
            "control_family_overrides are inference-only probe interventions for family-level root-cause isolation; they do not change the saved teacher contract or default runtime path.",
        ],
    }
    (output_dir / "teacher_first_vc_decoder_behavior_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_first_vc_decoder_behavior_probe.md").write_text(
        build_decoder_behavior_probe_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_reference_decoder_behavior_summary(
    *,
    reference_package_paths: list[Path],
    checkpoint_payload: dict[str, object],
    checkpoint_path: Path,
    selection_summary: dict[str, object] | None,
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> dict[str, object]:
    first_payload = load_training_package_payload(reference_package_paths[0])
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_vocoder_model_from_runtime_dims(
        checkpoint_payload=checkpoint_payload,
        periodic_input_dim=int(first_batch["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(first_batch["noise_branch_features"].shape[-1]),
        frame_length=int(first_runtime["frame_length"]),
    ).to(device)
    model.eval()

    branch_label = infer_branch_label(
        checkpoint_path=checkpoint_path,
        selection_summary=selection_summary,
        selection_target="best_validation",
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=predicted_activity_gate_floor,
        predicted_activity_gate_smoothing_frames=predicted_activity_gate_smoothing_frames,
        predicted_activity_gate_apply_mode=predicted_activity_gate_apply_mode,
    )
    reference_cases = []
    for package_path in reference_package_paths:
        payload = load_training_package_payload(package_path)
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)
        validate_vocoder_checkpoint_against_runtime_dims(
            state_dict=dict(checkpoint_payload["model_state_dict"]),
            periodic_input_dim=int(batch["periodic_branch_features"].shape[-1]),
            noise_input_dim=int(batch["noise_branch_features"].shape[-1]),
            frame_length=int(runtime["frame_length"]),
        )
        metrics, _ = collect_decoder_behavior_metrics(
            model=model,
            periodic_branch_features=batch["periodic_branch_features"],
            noise_branch_features=batch["noise_branch_features"],
            sample_rate=int(runtime["sample_rate"]),
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
            device=device,
            use_predicted_activity_gate=bool(use_predicted_activity_gate),
            predicted_activity_gate_floor=predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=predicted_activity_gate_apply_mode,
            aligned_waveform=batch["aligned_waveform"],
        )
        reference_cases.append(
            {
                "training_package_path": package_path.as_posix(),
                "target_audio_path": str(payload.get("target_audio_path")),
                "source_audio_path": str(payload.get("source_audio_path")),
                "frame_count": int(payload["frame_count"]),
                "decoder_metrics": metrics,
            }
        )

    metric_distribution = summarize_decoder_metric_distribution(
        [dict(case["decoder_metrics"]["scalar_metrics"]) for case in reference_cases]
    )
    return {
        "checkpoint_path": checkpoint_path.as_posix(),
        "branch_label": branch_label,
        "case_count": len(reference_cases),
        "metric_distribution": metric_distribution,
        "cases": reference_cases,
    }


def normalize_decoder_probe_normalization_strategy(normalization_strategy: str) -> str:
    normalized = str(normalization_strategy).strip().lower().replace("-", "_")
    aliases = {
        "none": "none",
        "conditioning_mean": "conditioning_reference_mean",
        "conditioning_reference_mean": "conditioning_reference_mean",
        "clip": "reference_q01_q99_clip",
        "reference_q01_q99_clip": "reference_q01_q99_clip",
        "affine": "reference_affine_match",
        "reference_affine_match": "reference_affine_match",
        "conditioning_mean_plus_clip": "conditioning_reference_mean_plus_reference_q01_q99_clip",
        "conditioning_reference_mean_plus_reference_q01_q99_clip": "conditioning_reference_mean_plus_reference_q01_q99_clip",
    }
    if normalized not in aliases:
        raise ValueError(
            "Unsupported normalization strategy for decoder probe: "
            f"{normalization_strategy!r}. Expected one of: none, conditioning_reference_mean, "
            "reference_q01_q99_clip, reference_affine_match, "
            "conditioning_reference_mean_plus_reference_q01_q99_clip."
        )
    return aliases[normalized]


def parse_decoder_probe_control_family_overrides(
    control_family_overrides: list[str] | None,
) -> list[dict[str, object]]:
    if not control_family_overrides:
        return []
    normalized_rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for raw_value in control_family_overrides:
        raw_text = str(raw_value).strip()
        if not raw_text:
            continue
        separator = "=" if "=" in raw_text else ":"
        if separator not in raw_text:
            raise ValueError(
                "Unsupported control-family override format: "
                f"{raw_value!r}. Expected family=mode, for example z_art=reference_mean."
            )
        raw_family, raw_mode = [part.strip().lower().replace("-", "_") for part in raw_text.split(separator, 1)]
        family = DECODER_PROBE_CONTROL_FAMILY_ALIASES.get(raw_family)
        if family is None:
            raise ValueError(
                "Unsupported control-family override family: "
                f"{raw_family!r}. Expected one of: "
                + ", ".join(sorted(DECODER_PROBE_CONTROL_FAMILY_TARGETS.keys()))
                + "."
            )
        mode = DECODER_PROBE_CONTROL_OVERRIDE_MODE_ALIASES.get(raw_mode)
        if mode is None:
            raise ValueError(
                "Unsupported control-family override mode: "
                f"{raw_mode!r}. Expected one of: zero, reference_mean."
            )
        dedupe_key = (family, mode)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized_rows.append(
            {
                "family": family,
                "mode": mode,
                "targets": list(DECODER_PROBE_CONTROL_FAMILY_TARGETS[family]),
            }
        )
    return normalized_rows


def serialize_decoder_probe_control_family_overrides(
    control_family_overrides: list[dict[str, object]],
) -> list[dict[str, object]]:
    serialized_rows = []
    for item in control_family_overrides:
        targets = list(item.get("targets", []))
        serialized_rows.append(
            {
                "family": str(item.get("family")),
                "mode": str(item.get("mode")),
                "targets": [f"{branch}.{semantic}" for branch, semantic in targets],
            }
        )
    return serialized_rows


def normalize_scaffold_payload_for_decoder_probe(
    *,
    scaffold_payload: dict[str, object],
    reference_feature_summary: dict[str, object],
    normalization_strategy: str,
    control_family_overrides: list[dict[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    normalized_strategy = normalize_decoder_probe_normalization_strategy(normalization_strategy)
    resolved_control_family_overrides = list(control_family_overrides or [])
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    periodic_features = branch_scaffold["periodic_branch_features"].detach().clone().to(torch.float32)
    noise_features = branch_scaffold["noise_branch_features"].detach().clone().to(torch.float32)
    transformations: list[str] = []
    if normalized_strategy == "none" and not resolved_control_family_overrides:
        return (
            {
                **scaffold_payload,
                "branch_scaffold": {
                    **branch_scaffold,
                    "periodic_branch_features": periodic_features,
                    "noise_branch_features": noise_features,
                },
            },
            {
                "strategy": normalized_strategy,
                "transformations": transformations,
                "control_family_overrides": [],
            },
        )

    layout = build_branch_feature_layout(scaffold_payload)
    periodic_reference = dict(reference_feature_summary["periodic"])
    noise_reference = dict(reference_feature_summary["noise"])
    periodic_mean = torch.tensor(periodic_reference["per_dim_mean"], dtype=torch.float32)
    periodic_q01 = torch.tensor(periodic_reference["per_dim_q01"], dtype=torch.float32)
    periodic_q99 = torch.tensor(periodic_reference["per_dim_q99"], dtype=torch.float32)
    noise_mean = torch.tensor(noise_reference["per_dim_mean"], dtype=torch.float32)
    noise_q01 = torch.tensor(noise_reference["per_dim_q01"], dtype=torch.float32)
    noise_q99 = torch.tensor(noise_reference["per_dim_q99"], dtype=torch.float32)

    if normalized_strategy in {
        "conditioning_reference_mean",
        "conditioning_reference_mean_plus_reference_q01_q99_clip",
    }:
        for semantic in ("alpha", "s_spk_target", "s_geom_target"):
            slice_info = layout["periodic"].get(semantic)
            if slice_info is None:
                continue
            start, end = slice_info
            periodic_features[:, start:end] = periodic_mean[start:end].view(1, end - start).expand(
                periodic_features.shape[0],
                end - start,
            )
            transformations.append(
                f"periodic.{semantic} -> reference_mean[{start}:{end}]"
            )
        for semantic in ("alpha", "s_spk_target"):
            slice_info = layout["noise"].get(semantic)
            if slice_info is None:
                continue
            start, end = slice_info
            noise_features[:, start:end] = noise_mean[start:end].view(1, end - start).expand(
                noise_features.shape[0],
                end - start,
            )
            transformations.append(
                f"noise.{semantic} -> reference_mean[{start}:{end}]"
            )
    if normalized_strategy in {
        "reference_q01_q99_clip",
        "conditioning_reference_mean_plus_reference_q01_q99_clip",
    }:
        periodic_features = torch.maximum(
            torch.minimum(periodic_features, periodic_q99.view(1, -1)),
            periodic_q01.view(1, -1),
        )
        noise_features = torch.maximum(
            torch.minimum(noise_features, noise_q99.view(1, -1)),
            noise_q01.view(1, -1),
        )
        transformations.append("periodic.* -> clamp(reference_q01, reference_q99)")
        transformations.append("noise.* -> clamp(reference_q01, reference_q99)")
    if normalized_strategy == "reference_affine_match":
        periodic_features = match_feature_distribution_to_reference(
            candidate_features=periodic_features,
            reference_mean=periodic_mean,
            reference_std=torch.tensor(periodic_reference["per_dim_std"], dtype=torch.float32),
        )
        noise_features = match_feature_distribution_to_reference(
            candidate_features=noise_features,
            reference_mean=noise_mean,
            reference_std=torch.tensor(noise_reference["per_dim_std"], dtype=torch.float32),
        )
        transformations.append("periodic.* -> affine_match(reference_mean, reference_std)")
        transformations.append("noise.* -> affine_match(reference_mean, reference_std)")
    control_override_summary = []
    for override in resolved_control_family_overrides:
        family = str(override["family"])
        mode = str(override["mode"])
        targets = list(override.get("targets", []))
        serialized_targets = []
        for branch_name, semantic in targets:
            slice_info = layout[branch_name].get(semantic)
            if slice_info is None:
                continue
            start, end = slice_info
            if branch_name == "periodic":
                branch_features = periodic_features
                reference_mean = periodic_mean
            else:
                branch_features = noise_features
                reference_mean = noise_mean
            if mode == "zero":
                branch_features[:, start:end] = 0.0
                transformations.append(f"{branch_name}.{semantic} -> zero[{start}:{end}]")
            elif mode == "reference_mean":
                branch_features[:, start:end] = reference_mean[start:end].view(1, end - start).expand(
                    branch_features.shape[0],
                    end - start,
                )
                transformations.append(
                    f"{branch_name}.{semantic} -> reference_mean[{start}:{end}]"
                )
            else:
                raise ValueError(f"Unsupported control-family override mode after normalization: {mode!r}")
            serialized_targets.append(f"{branch_name}.{semantic}")
        control_override_summary.append(
            {
                "family": family,
                "mode": mode,
                "targets": serialized_targets,
            }
        )
    return (
        {
            **scaffold_payload,
            "branch_scaffold": {
                **branch_scaffold,
                "periodic_branch_features": periodic_features,
                "noise_branch_features": noise_features,
            },
        },
        {
            "strategy": normalized_strategy,
            "transformations": transformations,
            "control_family_overrides": control_override_summary,
        },
    )


def match_feature_distribution_to_reference(
    *,
    candidate_features: torch.Tensor,
    reference_mean: torch.Tensor,
    reference_std: torch.Tensor,
) -> torch.Tensor:
    candidate = candidate_features.to(torch.float32)
    candidate_mean = candidate.mean(dim=0)
    candidate_std = candidate.std(dim=0, unbiased=False)
    safe_candidate_std = torch.clamp(candidate_std, min=1.0e-6)
    safe_reference_std = torch.clamp(reference_std.to(torch.float32), min=0.0)
    normalized = (candidate - candidate_mean.view(1, -1)) / safe_candidate_std.view(1, -1)
    matched = normalized * safe_reference_std.view(1, -1) + reference_mean.view(1, -1)
    zero_reference_mask = safe_reference_std <= 1.0e-8
    if bool(zero_reference_mask.any().item()):
        matched[:, zero_reference_mask] = reference_mean[zero_reference_mask].view(1, -1).expand(
            candidate.shape[0],
            int(zero_reference_mask.sum().item()),
        )
    return matched


def build_branch_feature_layout(scaffold_payload: dict[str, object]) -> dict[str, dict[str, tuple[int, int]]]:
    available_controls = dict(scaffold_payload["available_controls"])
    conditioning = dict(scaffold_payload["conditioning"])

    z_art_dim = int(available_controls["z_art"].shape[-1])
    event_dim = int(available_controls["event_probs"].shape[-1])
    energy_proxy_dim = int(available_controls["energy_proxy"].shape[-1])
    voiced_proxy_dim = int(available_controls["voiced_proxy"].shape[-1])
    aperiodicity_proxy_dim = int(available_controls["aperiodicity_proxy"].shape[-1])
    event_presence_proxy_dim = int(available_controls["event_presence_proxy"].shape[-1])
    energy_change_proxy_dim = int(available_controls["energy_change_proxy"].shape[-1])
    speaker_dim = int(conditioning["s_spk_target"].shape[-1])
    geom_dim = int(conditioning["s_geom_target"].shape[-1])
    alpha_dim = int(conditioning["alpha"].numel())

    periodic_start = 0
    periodic = {}
    for semantic, dim in (
        ("z_art", z_art_dim),
        ("voiced_proxy", voiced_proxy_dim),
        ("energy_proxy", energy_proxy_dim),
        ("alpha", alpha_dim),
        ("s_spk_target", speaker_dim),
        ("s_geom_target", geom_dim),
    ):
        periodic[semantic] = (periodic_start, periodic_start + dim)
        periodic_start += dim

    noise_start = 0
    noise = {}
    for semantic, dim in (
        ("event_probs", event_dim),
        ("aperiodicity_proxy", aperiodicity_proxy_dim),
        ("event_presence_proxy", event_presence_proxy_dim),
        ("energy_change_proxy", energy_change_proxy_dim),
        ("energy_proxy", energy_proxy_dim),
        ("alpha", alpha_dim),
        ("s_spk_target", speaker_dim),
    ):
        noise[semantic] = (noise_start, noise_start + dim)
        noise_start += dim
    return {
        "periodic": periodic,
        "noise": noise,
    }


def build_decoder_behavior_case_summary(
    *,
    case_id: str,
    demo_summary: dict[str, object],
    scaffold_payload: dict[str, object],
    checkpoint_payload: dict[str, object],
    device: torch.device,
    reference_metric_distribution: dict[str, object],
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    normalization_summary: dict[str, object],
    probe_decoded_audio_path: Path | None,
) -> dict[str, object]:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload["source_runtime"])
    metrics, decoded_waveform = collect_decoder_behavior_metrics(
        model=build_vocoder_model_from_runtime_dims(
            checkpoint_payload=checkpoint_payload,
            periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
            noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
            frame_length=int(source_runtime["frame_length"]),
        ).to(device).eval(),
        periodic_branch_features=branch_scaffold["periodic_branch_features"].to(torch.float32),
        noise_branch_features=branch_scaffold["noise_branch_features"].to(torch.float32),
        sample_rate=int(source_runtime["sample_rate"]),
        frame_length=int(source_runtime["frame_length"]),
        hop_length=int(source_runtime["hop_length"]),
        device=device,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=predicted_activity_gate_floor,
        predicted_activity_gate_smoothing_frames=predicted_activity_gate_smoothing_frames,
        predicted_activity_gate_apply_mode=predicted_activity_gate_apply_mode,
        aligned_waveform=None,
    )
    if probe_decoded_audio_path is not None:
        write_waveform_int16(
            probe_decoded_audio_path,
            decoded_waveform,
            sample_rate=int(source_runtime["sample_rate"]),
        )
    return {
        "case_id": case_id,
        "input_audio_path": demo_summary.get("input_audio_path"),
        "decoded_audio_path": None if probe_decoded_audio_path is None else probe_decoded_audio_path.as_posix(),
        "decoded_audio_sec": demo_summary.get("decoded_audio_sec"),
        "decoded_waveform_rms": demo_summary.get("decoded_waveform_rms"),
        "branch_label": dict(demo_summary.get("vocoder", {})).get("branch_label"),
        "normalization": normalization_summary,
        "decoder_metrics": metrics,
        "reference_shift": analyze_decoder_metric_shift(
            candidate_metrics=dict(metrics["scalar_metrics"]),
            reference_metric_distribution=reference_metric_distribution,
        ),
    }


def collect_decoder_behavior_metrics(
    *,
    model: NoResidualSourceFilterVocoderScaffold,
    periodic_branch_features: torch.Tensor,
    noise_branch_features: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    aligned_waveform: torch.Tensor | None,
) -> tuple[dict[str, object], torch.Tensor]:
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    with torch.no_grad():
        outputs = model(
            periodic_branch_features=periodic_branch_features.to(device=device, dtype=torch.float32),
            noise_branch_features=noise_branch_features.to(device=device, dtype=torch.float32),
        )
        predicted_activity = torch.maximum(outputs["periodic_gate"], outputs["noise_gate"])
        decoded_waveform = reconstruct_waveform_from_frames(
            waveform_frames=outputs["waveform_frames"],
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
            frame_gain_floor=float(predicted_activity_gate_floor),
            frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
            frame_gain_apply_mode=resolved_apply_mode,
        )
    periodic_gate = outputs["periodic_gate"].detach().cpu().to(torch.float32).view(-1)
    noise_gate = outputs["noise_gate"].detach().cpu().to(torch.float32).view(-1)
    predicted_activity_cpu = predicted_activity.detach().cpu().to(torch.float32).view(-1)
    waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
    decoded_waveform_cpu = decoded_waveform.detach().cpu().to(torch.float32)
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform_cpu, int(sample_rate))
    scalar_metrics = {
        "periodic_gate_mean": round(float(periodic_gate.mean().item()), 6),
        "periodic_gate_std": round(float(periodic_gate.std(unbiased=False).item()), 6),
        "periodic_gate_active_fraction": round(float((periodic_gate >= 0.5).to(torch.float32).mean().item()), 6),
        "noise_gate_mean": round(float(noise_gate.mean().item()), 6),
        "noise_gate_std": round(float(noise_gate.std(unbiased=False).item()), 6),
        "noise_gate_active_fraction": round(float((noise_gate >= 0.5).to(torch.float32).mean().item()), 6),
        "predicted_activity_mean": round(float(predicted_activity_cpu.mean().item()), 6),
        "predicted_activity_std": round(float(predicted_activity_cpu.std(unbiased=False).item()), 6),
        "predicted_activity_active_fraction": round(
            float((predicted_activity_cpu >= 0.5).to(torch.float32).mean().item()),
            6,
        ),
        "waveform_frames_mean": round(float(waveform_frames.mean().item()), 6),
        "waveform_frames_std": round(float(waveform_frames.std(unbiased=False).item()), 6),
        "waveform_frames_abs_mean": round(float(waveform_frames.abs().mean().item()), 6),
        "waveform_frames_clip_fraction": round(
            float((waveform_frames.abs() >= 0.95).to(torch.float32).mean().item()),
            6,
        ),
        "decoded_waveform_rms": round(float(decoded_waveform_cpu.pow(2).mean().sqrt().item()), 6),
        "decoded_abs_mean": round(float(decoded_waveform_cpu.abs().mean().item()), 6),
        "decoded_peak_abs": round(float(decoded_waveform_cpu.abs().max().item()), 6),
        "decoded_zero_crossing_rate": round(float(compute_zero_crossing_rate(decoded_waveform_cpu)), 6),
        "decoded_spectral_centroid_hz": float(decoded_spectral["centroid_hz"]),
        "decoded_spectral_bandwidth_hz": float(decoded_spectral["bandwidth_hz"]),
        "decoded_spectral_rolloff95_hz": float(decoded_spectral["rolloff95_hz"]),
        "decoded_spectral_high_band_energy_ratio": float(decoded_spectral["high_band_energy_ratio"]),
    }
    aligned_reference = None
    if aligned_waveform is not None:
        aligned_waveform_cpu = aligned_waveform.detach().cpu().to(torch.float32)[: decoded_waveform_cpu.shape[0]]
        aligned_spectral = compute_waveform_spectral_summary(aligned_waveform_cpu, int(sample_rate))
        aligned_rms = float(aligned_waveform_cpu.pow(2).mean().sqrt().item())
        scalar_metrics.update(
            {
                "aligned_waveform_rms": round(aligned_rms, 6),
                "decoded_to_aligned_rms_ratio": round(
                    0.0 if aligned_rms <= 1.0e-8 else float(decoded_waveform_cpu.pow(2).mean().sqrt().item()) / aligned_rms,
                    6,
                ),
                "spectral_centroid_gap_hz": round(
                    abs(float(decoded_spectral["centroid_hz"]) - float(aligned_spectral["centroid_hz"])),
                    6,
                ),
                "spectral_bandwidth_gap_hz": round(
                    abs(float(decoded_spectral["bandwidth_hz"]) - float(aligned_spectral["bandwidth_hz"])),
                    6,
                ),
                "spectral_rolloff95_gap_hz": round(
                    abs(float(decoded_spectral["rolloff95_hz"]) - float(aligned_spectral["rolloff95_hz"])),
                    6,
                ),
                "spectral_high_band_energy_ratio_gap": round(
                    abs(
                        float(decoded_spectral["high_band_energy_ratio"])
                        - float(aligned_spectral["high_band_energy_ratio"])
                    ),
                    6,
                ),
            }
        )
        aligned_reference = {
            "waveform_rms": round(aligned_rms, 6),
            "spectral_summary": aligned_spectral,
        }
    return {
        "frame_count": int(periodic_gate.shape[0]),
        "use_predicted_activity_gate": bool(use_predicted_activity_gate),
        "predicted_activity_gate_apply_mode": resolved_apply_mode,
        "gates": {
            "periodic_mean": scalar_metrics["periodic_gate_mean"],
            "periodic_std": scalar_metrics["periodic_gate_std"],
            "periodic_active_fraction": scalar_metrics["periodic_gate_active_fraction"],
            "noise_mean": scalar_metrics["noise_gate_mean"],
            "noise_std": scalar_metrics["noise_gate_std"],
            "noise_active_fraction": scalar_metrics["noise_gate_active_fraction"],
            "predicted_activity_mean": scalar_metrics["predicted_activity_mean"],
            "predicted_activity_std": scalar_metrics["predicted_activity_std"],
            "predicted_activity_active_fraction": scalar_metrics["predicted_activity_active_fraction"],
        },
        "waveform_frames": {
            "mean": scalar_metrics["waveform_frames_mean"],
            "std": scalar_metrics["waveform_frames_std"],
            "abs_mean": scalar_metrics["waveform_frames_abs_mean"],
            "clip_fraction_abs_ge_095": scalar_metrics["waveform_frames_clip_fraction"],
        },
        "decoded_waveform": {
            "rms": scalar_metrics["decoded_waveform_rms"],
            "abs_mean": scalar_metrics["decoded_abs_mean"],
            "peak_abs": scalar_metrics["decoded_peak_abs"],
            "zero_crossing_rate": scalar_metrics["decoded_zero_crossing_rate"],
            "spectral_summary": decoded_spectral,
        },
        "aligned_reference": aligned_reference,
        "scalar_metrics": scalar_metrics,
    }, decoded_waveform_cpu


def compute_zero_crossing_rate(waveform: torch.Tensor) -> float:
    if int(waveform.numel()) < 2:
        return 0.0
    left = waveform[:-1]
    right = waveform[1:]
    return float(((left * right) < 0).to(torch.float32).mean().item())


def summarize_decoder_metric_distribution(metric_rows: list[dict[str, float]]) -> dict[str, object]:
    if not metric_rows:
        return {}
    metric_names = sorted({key for row in metric_rows for key in row.keys()})
    distribution = {}
    for metric_name in metric_names:
        values = [float(row[metric_name]) for row in metric_rows if metric_name in row]
        distribution[metric_name] = summarize_scalar_values(values)
    return distribution


def summarize_scalar_values(values: list[float]) -> dict[str, float]:
    tensor = torch.tensor(values, dtype=torch.float32)
    quantiles = torch.quantile(tensor, torch.tensor([0.01, 0.5, 0.99], dtype=torch.float32))
    return {
        "count": int(tensor.shape[0]),
        "mean": round(float(tensor.mean().item()), 6),
        "std": round(float(tensor.std(unbiased=False).item()), 6),
        "min": round(float(tensor.amin().item()), 6),
        "q01": round(float(quantiles[0].item()), 6),
        "median": round(float(quantiles[1].item()), 6),
        "q99": round(float(quantiles[2].item()), 6),
        "max": round(float(tensor.amax().item()), 6),
    }


def analyze_decoder_metric_shift(
    *,
    candidate_metrics: dict[str, float],
    reference_metric_distribution: dict[str, object],
) -> dict[str, object]:
    comparable_metric_names = [
        metric_name
        for metric_name in sorted(candidate_metrics.keys())
        if metric_name in reference_metric_distribution
    ]
    if not comparable_metric_names:
        return {
            "metric_count": 0,
            "abs_z_median": 0.0,
            "abs_z_max": 0.0,
            "outside_q01_q99_fraction": 0.0,
            "top_shift_metrics": [],
        }
    z_rows = []
    outside_flags = []
    for metric_name in comparable_metric_names:
        reference = dict(reference_metric_distribution[metric_name])
        reference_mean = float(reference["mean"])
        reference_std = max(1.0e-6, float(reference["std"]))
        candidate_value = float(candidate_metrics[metric_name])
        abs_z = abs(candidate_value - reference_mean) / reference_std
        outside = candidate_value < float(reference["q01"]) or candidate_value > float(reference["q99"])
        z_rows.append(
            {
                "metric": metric_name,
                "candidate_value": round(candidate_value, 6),
                "reference_mean": round(reference_mean, 6),
                "reference_std": round(float(reference["std"]), 6),
                "reference_q01": round(float(reference["q01"]), 6),
                "reference_q99": round(float(reference["q99"]), 6),
                "abs_z": round(abs_z, 6),
                "outside_q01_q99": bool(outside),
            }
        )
        outside_flags.append(1.0 if outside else 0.0)
    z_rows.sort(key=lambda item: float(item["abs_z"]), reverse=True)
    z_tensor = torch.tensor([float(item["abs_z"]) for item in z_rows], dtype=torch.float32)
    outside_tensor = torch.tensor(outside_flags, dtype=torch.float32)
    return {
        "metric_count": len(z_rows),
        "abs_z_median": round(float(torch.median(z_tensor).item()), 6),
        "abs_z_max": round(float(torch.max(z_tensor).item()), 6),
        "outside_q01_q99_fraction": round(float(outside_tensor.mean().item()), 6),
        "top_shift_metrics": z_rows[: min(10, len(z_rows))],
    }


def build_decoder_behavior_probe_markdown(summary: dict[str, object]) -> str:
    reference_summary = dict(summary.get("reference_decoder_behavior", {}))
    waveform_decode = dict(summary.get("waveform_decode", {}))
    lines = [
        "# Teacher-First VC Decoder Behavior Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- waveform_decode: {json.dumps(waveform_decode, ensure_ascii=False)}",
        f"- reference_package_count: {summary['reference_package_count']}",
        f"- case_count: {summary['case_count']}",
        f"- reference_checkpoint_path: {reference_summary.get('checkpoint_path')}",
        f"- reference_branch_label: {reference_summary.get('branch_label')}",
        "",
        "## Cases",
    ]
    for case in list(summary.get("cases", [])):
        if not isinstance(case, dict):
            continue
        lines.extend(
            [
                f"- case_id: {case.get('case_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  decoded_audio_path: {case.get('decoded_audio_path')}",
                f"  decoded_audio_sec: {case.get('decoded_audio_sec')}",
                f"  decoded_waveform_rms: {case.get('decoded_waveform_rms')}",
                f"  branch_label: {case.get('branch_label')}",
                f"  normalization: {json.dumps(case.get('normalization'), ensure_ascii=False)}",
                f"  decoder_metrics: {json.dumps(case.get('decoder_metrics'), ensure_ascii=False)}",
                f"  reference_shift: {json.dumps(case.get('reference_shift'), ensure_ascii=False)}",
            ]
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
