from __future__ import annotations

from datetime import datetime
import json
import shutil
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
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
from v5vc.offline_vocoder_training import reconstruct_waveform_from_frames
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
    branch_label: str | None = None
    decoded_waveform: torch.Tensor | None = None
    sample_rate: int | None = None
    stage_state: dict[str, object] = {
        "current_stage": "teacher_source_resolution",
        "completed_stages": [],
        "skipped_stages": [],
    }

    try:
        contract_payload = export_teacher_contract_with_stage_tracking(
            input_audio_path=input_audio_path,
            output_dir=contract_dir,
            route_handoff_path=teacher_route_handoff_path,
            checkpoint_path=teacher_checkpoint_path,
            calibration_asset_path=calibration_asset_path,
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
        mark_stage_completed(stage_state, "vocoder_checkpoint_resolution")

        set_stage(stage_state, "vocoder_checkpoint_load")
        checkpoint_payload = torch.load(
            resolved_vocoder_checkpoint_path,
            map_location="cpu",
            weights_only=False,
        )
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
            contract_tensor_path=contract_tensor_path,
            scaffold_tensor_path=scaffold_tensor_path,
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
    state_dict = dict(checkpoint_payload["model_state_dict"])
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload.get("source_runtime", {}))
    hidden_dim = int(state_dict["periodic_encoder.0.weight"].shape[0])
    harmonic_bins = int(state_dict["harmonic_envelope.weight"].shape[0])
    noise_bins = int(state_dict["noise_envelope.weight"].shape[0])
    frame_length = int(source_runtime["frame_length"])
    model = NoResidualSourceFilterVocoderScaffold(
        periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
        hidden_dim=hidden_dim,
        harmonic_bins=harmonic_bins,
        noise_bins=noise_bins,
        frame_length=frame_length,
    )
    model.load_state_dict(state_dict)
    return model


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
    if decoded_waveform is not None and sample_rate:
        decoded_audio_sec = round(float(decoded_waveform.shape[0] / sample_rate), 6)
        decoded_waveform_rms = round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6)
    notes = [
        "This command is a teacher-first single-target demo path, not the final product-grade many-to-many runtime.",
        "decoded.wav is generated without aligned_target-dependent pitch matching, audit proxy, or validation-side loss readouts.",
        "The current target conditioning still comes from the existing calibration asset and therefore represents a fixed single-target preset.",
        "When stable_late_stop is absent from a checkpoint-selection payload, prefer best_validation or pass an explicit vocoder checkpoint.",
        "pipeline.layers exposes a user-facing failure ladder so the summary shows whether the run stopped at teacher runtime, contract, scaffold, vocoder checkpoint, or waveform reconstruction.",
    ]
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
        },
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
