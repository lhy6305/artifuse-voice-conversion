from __future__ import annotations

from datetime import datetime
import json
import shutil
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.event_semantics import (
    TEACHER_E_EVT_BRIDGE_MODE_LEGACY_EVENT_PROBS_V1,
    TEACHER_E_EVT_TARGET_SHAPING_MODE_HARD_BOX_V1,
)
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
from v5vc.offline_vocoder_scaffold import (
    NoResidualSourceFilterVocoderScaffold,
    build_nores_vocoder_scaffold_from_state_dict,
    resolve_residual_shape_branch_condition_delta,
)
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.stage5_speech_emergence_probe import (
    compute_pearson_correlation,
    frame_waveform_sequence,
    summarize_probe_delta_vs_baseline,
    summarize_frame_sequence_metrics,
)
from v5vc.stage5_waveform_decoder_structure_probe import (
    STRUCTURE_PROBE_VARIANTS,
    apply_structure_transform,
    build_baseline_decoder_collapse_summary,
    build_variant_aggregates,
    build_variant_impact_ranking,
    compute_fused_hidden_for_probe,
)
from v5vc.stage5_waveform_handoff_probe import (
    HANDOFF_DECODE_ROUTES,
    build_handoff_stage_aggregates,
    summarize_handoff_stage_metrics,
)
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
    "reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json"
)
DEFAULT_SELF_CHECK_INPUT_AUDIO_PATH = Path(
    "data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav"
)
DEFAULT_EXPLICIT_CLEAN_TARGET_REFERENCE_AUDIO_PATH = Path(
    "data_convert/dataset_firefly_raw/chapter3_3_firefly_135.wav"
)
DEFAULT_AUDIBLE_SMOKE_TARGET_REFERENCE_MAX_AUDIO_SEC = 3.0
DEFAULT_AUDIBLE_COMPARE_BASELINE_SUMMARY_JSON_PATH = Path(
    "reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_baseline_smoke_round1_2/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json"
)
DEFAULT_AUDIBLE_COMPARE_CANDIDATE_SUMMARY_JSON_PATH = Path(
    "reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_active_template_delta_smoke_round1_2/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json"
)
DEFAULT_AUDIBLE_COMPARE_ACTIVE_CHECKPOINT_SELECTION_PATH = Path(
    "reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json"
)
DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION = "teacher_first_runtime_risk_v1"
DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION_V2 = "teacher_first_runtime_risk_v2_reference_relative"
DEFAULT_RUNTIME_REFERENCE_DECODER_BEHAVIOR_CACHE_DIR = Path(
    "reports/runtime/offline_mvp_teacher_first_vc_reference_decoder_behavior_cache"
)
HIGH_RISK_SPECTRAL_CENTROID_HZ = 3200.0
HIGH_RISK_SPECTRAL_ROLLOFF95_HZ = 22000.0
HIGH_RISK_HIGH_BAND_ENERGY_RATIO = 0.25
ELEVATED_RISK_SPECTRAL_CENTROID_HZ = 3100.0
ELEVATED_RISK_SPECTRAL_ROLLOFF95_HZ = 21500.0
ELEVATED_RISK_HIGH_BAND_ENERGY_RATIO = 0.15
HIGH_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN = 3.0
HIGH_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION = 0.75
ELEVATED_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN = 1.0
ELEVATED_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION = 0.25
DECODER_PROBE_CONTROL_FAMILY_ALIASES = {
    "z_art": "z_art",
    "zart": "z_art",
    "event_probs": "event_family",
    "event_probs_family": "event_family",
    "events": "event_family",
    "e_evt": "event_family",
    "teacher_e_evt": "event_family",
    "event_family": "event_family",
    "f0": "f0_hz_log_norm",
    "f0_hz": "f0_hz_log_norm",
    "f0_hz_log_norm": "f0_hz_log_norm",
    "vuv": "vuv",
    "aper": "aper",
    "energy_control": "E_log_rms_norm",
    "energy_log_rms_norm": "E_log_rms_norm",
    "e_log_rms_norm": "E_log_rms_norm",
    "e": "E_log_rms_norm",
    "periodic_e_log_rms_norm": "periodic_E_log_rms_norm",
    "periodic_energy_control": "periodic_E_log_rms_norm",
    "periodic_energy_log_rms_norm": "periodic_E_log_rms_norm",
    "noise_e_log_rms_norm": "noise_E_log_rms_norm",
    "noise_energy_control": "noise_E_log_rms_norm",
    "noise_energy_log_rms_norm": "noise_E_log_rms_norm",
    "conditioning_family": "conditioning_family",
    "acoustic_state_family": "acoustic_state_family",
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
    "reference_affine_match": "reference_affine_match",
    "reference_affine": "reference_affine_match",
    "affine": "reference_affine_match",
    "time_roll_half": "time_roll_half",
    "roll_half": "time_roll_half",
    "temporal_roll_half": "time_roll_half",
    "time_shuffle": "time_shuffle",
    "shuffle": "time_shuffle",
    "temporal_shuffle": "time_shuffle",
}
DECODER_PROBE_CONTROL_FAMILY_TARGETS = {
    "z_art": (("periodic", "z_art"),),
    "event_family": (("noise", "e_evt"), ("noise", "event_probs")),
    "f0_hz_log_norm": (("periodic", "f0_hz_log_norm"),),
    "vuv": (("periodic", "vuv"), ("noise", "vuv")),
    "aper": (("noise", "aper"),),
    "E_log_rms_norm": (("periodic", "E_log_rms_norm"), ("noise", "E_log_rms_norm")),
    "periodic_E_log_rms_norm": (("periodic", "E_log_rms_norm"),),
    "noise_E_log_rms_norm": (("noise", "E_log_rms_norm"),),
    "conditioning_family": (
        ("periodic", "alpha"),
        ("periodic", "s_spk_target"),
        ("periodic", "s_geom_target"),
        ("noise", "alpha"),
        ("noise", "s_spk_target"),
        ("noise", "s_geom_target"),
    ),
    "acoustic_state_family": (
        ("periodic", "f0_hz_log_norm"),
        ("periodic", "vuv"),
        ("periodic", "E_log_rms_norm"),
        ("noise", "aper"),
        ("noise", "vuv"),
        ("noise", "E_log_rms_norm"),
    ),
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
ACOUSTIC_TEMPORAL_ALIGNMENT_PAIR_DEFINITIONS = (
    {
        "pair_id": "aper_to_frame_rms",
        "label": "aper -> frame_rms",
        "series_key": "noise.aper",
        "description": "Lagged correlation between noise-branch aper and waveform frame RMS.",
    },
    {
        "pair_id": "energy_to_frame_rms",
        "label": "E_log_rms_norm -> frame_rms",
        "series_key": "noise.E_log_rms_norm",
        "description": "Lagged correlation between noise-branch normalized energy control and waveform frame RMS.",
    },
    {
        "pair_id": "aper_energy_product_to_frame_rms",
        "label": "aper * E_log_rms_norm -> frame_rms",
        "series_key": "noise.aper_times_E_log_rms_norm",
        "description": "Lagged correlation between the acoustic-state product aper*E and waveform frame RMS.",
    },
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
    reference_package_paths: list[Path] | None = None,
    reference_package_limit: int = 32,
    normalization_strategy: str = "none",
    control_family_overrides: list[str] | None = None,
) -> None:
    if float(predicted_activity_gate_floor) < 0.0 or float(predicted_activity_gate_floor) > 1.0:
        raise ValueError("predicted_activity_gate_floor must be within [0.0, 1.0].")
    if int(predicted_activity_gate_smoothing_frames) < 0:
        raise ValueError("predicted_activity_gate_smoothing_frames must be >= 0.")
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    resolved_normalization_strategy = normalize_decoder_probe_normalization_strategy(normalization_strategy)
    resolved_control_family_overrides = parse_decoder_probe_control_family_overrides(control_family_overrides)

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
    normalization_summary: dict[str, object] = {
        "strategy": resolved_normalization_strategy,
        "transformations": [],
        "control_family_overrides": serialize_decoder_probe_control_family_overrides(
            resolved_control_family_overrides
        ),
        "reference_package_count": 0,
    }
    resolved_vocoder_checkpoint_path: Path | None = None
    resolved_conditioning: dict[str, object] | None = None
    checkpoint_payload: dict[str, object] | None = None
    branch_label: str | None = None
    decoded_waveform: torch.Tensor | None = None
    sample_rate: int | None = None
    reference_decoder_behavior_summary: dict[str, object] | None = None
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
        if resolved_normalization_strategy != "none" or resolved_control_family_overrides:
            resolved_reference_packages = resolve_reference_package_paths(
                reference_package_paths=list(reference_package_paths or []),
                reference_package_limit=int(reference_package_limit),
            )
            reference_feature_summary = build_reference_distribution_summary(resolved_reference_packages)
            scaffold_payload, normalization_summary = normalize_scaffold_payload_for_decoder_probe(
                scaffold_payload=scaffold_payload,
                reference_feature_summary=reference_feature_summary,
                normalization_strategy=resolved_normalization_strategy,
                control_family_overrides=resolved_control_family_overrides,
            )
            normalization_summary = {
                **normalization_summary,
                "reference_package_count": len(resolved_reference_packages),
            }

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
            decoder_branch_mean_mix_alpha=0.0,
            use_decoder_branch_condition_adapter=bool(model.use_decoder_branch_condition_adapter),
            use_residual_shape_branch_condition_adapter=bool(model.use_residual_shape_branch_condition_adapter),
        )
        reference_decoder_behavior_summary = load_or_build_runtime_reference_decoder_behavior_summary(
            checkpoint_payload=checkpoint_payload,
            checkpoint_path=resolved_vocoder_checkpoint_path,
            selection_summary=selection_summary,
            selection_target=selection_target,
            use_predicted_activity_gate=bool(use_predicted_activity_gate),
            predicted_activity_gate_floor=float(predicted_activity_gate_floor),
            predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
            predicted_activity_gate_apply_mode=resolved_apply_mode,
            reference_package_paths=list(reference_package_paths or []),
            reference_package_limit=int(reference_package_limit),
            device=resolved_device,
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
            normalization_summary=normalization_summary,
            contract_tensor_path=contract_tensor_path if bool(save_intermediates) else None,
            scaffold_tensor_path=scaffold_tensor_path if bool(save_intermediates) else None,
            contract_runtime=contract_runtime,
            teacher_summary=teacher_summary,
            conditioning_summary=conditioning_summary,
            selection_summary=selection_summary,
            branch_label=branch_label,
            decoded_waveform=decoded_waveform,
            sample_rate=sample_rate,
            reference_decoder_behavior_summary=reference_decoder_behavior_summary,
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
            normalization_summary=normalization_summary,
            contract_tensor_path=contract_tensor_path if contract_tensor_path.exists() else None,
            scaffold_tensor_path=scaffold_tensor_path if scaffold_tensor_path.exists() else None,
            contract_runtime=contract_runtime,
            teacher_summary=teacher_summary,
            conditioning_summary=conditioning_summary,
            selection_summary=selection_summary,
            branch_label=branch_label,
            decoded_waveform=decoded_waveform,
            sample_rate=sample_rate,
            reference_decoder_behavior_summary=reference_decoder_behavior_summary,
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
    model = build_nores_vocoder_scaffold_from_state_dict(
        state_dict=state_dict,
        periodic_input_dim=int(periodic_input_dim),
        noise_input_dim=int(noise_input_dim),
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
    tensor_state_dict = {
        key: value
        for key, value in state_dict.items()
        if isinstance(value, torch.Tensor)
    }
    expected_model = build_nores_vocoder_scaffold_from_state_dict(
        state_dict=tensor_state_dict,
        periodic_input_dim=int(periodic_input_dim),
        noise_input_dim=int(noise_input_dim),
        frame_length=int(frame_length),
    )
    expected_state_dict = expected_model.state_dict()
    mismatches: list[str] = []
    missing_keys = [key for key in expected_state_dict if key not in tensor_state_dict]
    unexpected_keys = [key for key in tensor_state_dict if key not in expected_state_dict]
    for key, expected_value in expected_state_dict.items():
        actual_value = tensor_state_dict.get(key)
        if actual_value is None:
            continue
        actual_shape = tuple(int(dim) for dim in actual_value.shape)
        expected_shape = tuple(int(dim) for dim in expected_value.shape)
        if actual_shape != expected_shape:
            mismatches.append(f"{key}: expected {expected_shape} but found {actual_shape}")
    if missing_keys or unexpected_keys or mismatches:
        details: list[str] = []
        if missing_keys:
            details.append("missing_keys=" + ", ".join(sorted(missing_keys)))
        if unexpected_keys:
            details.append("unexpected_keys=" + ", ".join(sorted(unexpected_keys)))
        if mismatches:
            details.append("shape_mismatches=" + " | ".join(mismatches))
        raise ValueError(
            "Stage5 vocoder checkpoint is incompatible with the current scaffold: "
            + " | ".join(details)
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
    target_event_semantic_sidecar: dict[str, object] | None = None,
    target_event_timing_semantic_sidecar: dict[str, object] | None = None,
    source_semantic_parity_sidecar: dict[str, object] | None = None,
    teacher_e_evt_bridge_mode: str = TEACHER_E_EVT_BRIDGE_MODE_LEGACY_EVENT_PROBS_V1,
    teacher_e_evt_target_shaping_mode: str = TEACHER_E_EVT_TARGET_SHAPING_MODE_HARD_BOX_V1,
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
        waveform=waveform,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
        chunk_samples=effective_chunk_samples,
        device=resolved_device,
        streaming_outputs=streaming_outputs,
        conditioning=conditioning,
        verification=verification,
        target_event_semantic_sidecar=target_event_semantic_sidecar,
        target_event_timing_semantic_sidecar=target_event_timing_semantic_sidecar,
        source_semantic_parity_sidecar=source_semantic_parity_sidecar,
        teacher_e_evt_bridge_mode=teacher_e_evt_bridge_mode,
        teacher_e_evt_target_shaping_mode=teacher_e_evt_target_shaping_mode,
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
        target_event_semantic_sidecar=target_event_semantic_sidecar,
        target_event_timing_semantic_sidecar=target_event_timing_semantic_sidecar,
        source_semantic_parity_sidecar=source_semantic_parity_sidecar,
        teacher_e_evt_bridge_mode=teacher_e_evt_bridge_mode,
        teacher_e_evt_target_shaping_mode=teacher_e_evt_target_shaping_mode,
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
    normalization_summary: dict[str, object],
    contract_tensor_path: Path | None,
    scaffold_tensor_path: Path | None,
    contract_runtime: dict[str, object],
    teacher_summary: dict[str, object],
    conditioning_summary: dict[str, object],
    selection_summary: dict[str, object] | None,
    branch_label: str | None,
    decoded_waveform: torch.Tensor | None,
    sample_rate: int | None,
    reference_decoder_behavior_summary: dict[str, object] | None,
    completed_stages: list[str],
    skipped_stages: list[str],
    current_stage: str | None,
    failure: dict[str, object] | None,
) -> dict[str, object]:
    decoded_audio_samples = None if decoded_waveform is None else int(decoded_waveform.shape[0])
    decoded_audio_sec = None
    decoded_waveform_rms = None
    decoded_spectral_summary = None
    decoded_scalar_metrics = None
    if decoded_waveform is not None and sample_rate:
        decoded_audio_sec = round(float(decoded_waveform.shape[0] / sample_rate), 6)
        decoded_waveform_rms = round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6)
        decoded_spectral_summary = compute_waveform_spectral_summary(decoded_waveform, int(sample_rate))
        decoded_scalar_metrics = {
            "decoded_waveform_rms": float(decoded_waveform_rms),
            "decoded_abs_mean": round(float(decoded_waveform.abs().mean().item()), 6),
            "decoded_peak_abs": round(float(decoded_waveform.abs().max().item()), 6),
            "decoded_zero_crossing_rate": round(float(compute_zero_crossing_rate(decoded_waveform)), 6),
            "decoded_spectral_centroid_hz": float(decoded_spectral_summary["centroid_hz"]),
            "decoded_spectral_bandwidth_hz": float(decoded_spectral_summary["bandwidth_hz"]),
            "decoded_spectral_rolloff95_hz": float(decoded_spectral_summary["rolloff95_hz"]),
            "decoded_spectral_high_band_energy_ratio": float(decoded_spectral_summary["high_band_energy_ratio"]),
        }
    applicability_risk = assess_runtime_applicability_risk(
        decoded_spectral_summary=decoded_spectral_summary,
        decoded_scalar_metrics=decoded_scalar_metrics,
        reference_decoder_behavior_summary=reference_decoder_behavior_summary,
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
    if str(normalization_summary.get("strategy", "none")) != "none" or list(
        normalization_summary.get("control_family_overrides", [])
    ):
        notes.append(
            "normalization is an inference-only experimental adaptation applied after scaffold export; it does not modify the saved teacher contract or Stage5 checkpoint."
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
            "normalization": normalization_summary,
            "decoded_spectral_summary": decoded_spectral_summary,
            "decoded_scalar_metrics": decoded_scalar_metrics,
        },
        "applicability_risk": applicability_risk,
        "reference_decoder_behavior": reference_decoder_behavior_summary,
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


def load_or_build_runtime_reference_decoder_behavior_summary(
    *,
    checkpoint_payload: dict[str, object] | None,
    checkpoint_path: Path | None,
    selection_summary: dict[str, object] | None,
    selection_target: str,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    reference_package_paths: list[Path],
    reference_package_limit: int,
    device: torch.device,
) -> dict[str, object] | None:
    if checkpoint_payload is None or checkpoint_path is None:
        return None
    resolved_reference_packages = resolve_reference_package_paths(
        reference_package_paths=reference_package_paths,
        reference_package_limit=reference_package_limit,
    )
    if not resolved_reference_packages:
        return None
    branch_label = infer_branch_label(
        checkpoint_path=checkpoint_path,
        selection_summary=selection_summary,
        selection_target=selection_target,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=str(predicted_activity_gate_apply_mode),
        decoder_branch_mean_mix_alpha=0.0,
        use_decoder_branch_condition_adapter=False,
        use_residual_shape_branch_condition_adapter=False,
    )
    cache_dir = (
        DEFAULT_RUNTIME_REFERENCE_DECODER_BEHAVIOR_CACHE_DIR.resolve()
        / sanitize_cache_component(str(branch_label))
        / f"packages_{len(resolved_reference_packages):03d}"
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    summary_json_path = cache_dir / "reference_decoder_behavior_summary.json"
    if summary_json_path.exists():
        return json.loads(summary_json_path.read_text(encoding="utf-8"))
    summary = build_reference_decoder_behavior_summary(
        reference_package_paths=resolved_reference_packages,
        checkpoint_payload=checkpoint_payload,
        checkpoint_path=checkpoint_path,
        selection_summary=selection_summary,
        device=device,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=str(predicted_activity_gate_apply_mode),
    )
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def sanitize_cache_component(value: str) -> str:
    normalized = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in str(value)
    ).strip("._")
    return normalized or "unknown"


def assess_runtime_applicability_risk(
    *,
    decoded_spectral_summary: dict[str, object] | None,
    decoded_scalar_metrics: dict[str, float] | None,
    reference_decoder_behavior_summary: dict[str, object] | None,
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
    heuristic_version = DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION
    reference_shift = None
    reference_checkpoint_path = None
    reference_branch_label = None
    if isinstance(reference_decoder_behavior_summary, dict):
        metric_distribution = reference_decoder_behavior_summary.get("metric_distribution")
        if isinstance(metric_distribution, dict) and isinstance(decoded_scalar_metrics, dict):
            heuristic_version = DEFAULT_RUNTIME_APPLICABILITY_RISK_HEURISTIC_VERSION_V2
            reference_shift = analyze_decoder_metric_shift(
                candidate_metrics=dict(decoded_scalar_metrics),
                reference_metric_distribution=dict(metric_distribution),
            )
            reference_checkpoint_path = reference_decoder_behavior_summary.get("checkpoint_path")
            reference_branch_label = reference_decoder_behavior_summary.get("branch_label")
    centroid_hz = float(decoded_spectral_summary["centroid_hz"])
    rolloff95_hz = float(decoded_spectral_summary["rolloff95_hz"])
    high_band_energy_ratio = float(decoded_spectral_summary["high_band_energy_ratio"])
    high_risk_signals = []
    elevated_risk_signals = []
    if isinstance(reference_shift, dict):
        abs_z_median = float(reference_shift.get("abs_z_median", 0.0))
        outside_fraction = float(reference_shift.get("outside_q01_q99_fraction", 0.0))
        if abs_z_median >= HIGH_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN:
            high_risk_signals.append(
                "decoded scalar behavior is far from the cached in-distribution decoder reference: "
                f"abs_z_median={abs_z_median:.6f} >= {HIGH_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN:.2f}"
            )
        elif abs_z_median >= ELEVATED_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN:
            elevated_risk_signals.append(
                "decoded scalar behavior is moderately shifted from the cached in-distribution decoder reference: "
                f"abs_z_median={abs_z_median:.6f} >= {ELEVATED_RISK_REFERENCE_SHIFT_ABS_Z_MEDIAN:.2f}"
            )
        if outside_fraction >= HIGH_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION:
            high_risk_signals.append(
                "decoded scalar behavior falls outside the cached in-distribution q01-q99 envelope too often: "
                f"outside_fraction={outside_fraction:.6f} >= {HIGH_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION:.2f}"
            )
        elif outside_fraction >= ELEVATED_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION:
            elevated_risk_signals.append(
                "decoded scalar behavior falls outside the cached in-distribution q01-q99 envelope often enough to require review: "
                f"outside_fraction={outside_fraction:.6f} >= {ELEVATED_RISK_REFERENCE_SHIFT_OUTSIDE_FRACTION:.2f}"
            )
    if high_band_energy_ratio >= HIGH_RISK_HIGH_BAND_ENERGY_RATIO:
        if reference_shift is None:
            high_risk_signals.append(
                f"decoded high-band-energy ratio {high_band_energy_ratio:.6f} exceeds the current high-risk threshold {HIGH_RISK_HIGH_BAND_ENERGY_RATIO:.2f}"
            )
        else:
            elevated_risk_signals.append(
                f"decoded high-band-energy ratio {high_band_energy_ratio:.6f} remains above the legacy high-risk threshold {HIGH_RISK_HIGH_BAND_ENERGY_RATIO:.2f}; keep human review enabled."
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
        if reference_shift is None:
            high_risk_signals.append(
                f"decoded spectral centroid {centroid_hz:.3f} Hz exceeds the current high-risk threshold {HIGH_RISK_SPECTRAL_CENTROID_HZ:.1f} Hz"
            )
        else:
            elevated_risk_signals.append(
                f"decoded spectral centroid {centroid_hz:.3f} Hz remains above the legacy high-risk threshold {HIGH_RISK_SPECTRAL_CENTROID_HZ:.1f} Hz; keep human review enabled."
            )
    elif centroid_hz >= ELEVATED_RISK_SPECTRAL_CENTROID_HZ:
        elevated_risk_signals.append(
            f"decoded spectral centroid {centroid_hz:.3f} Hz exceeds the elevated-risk threshold {ELEVATED_RISK_SPECTRAL_CENTROID_HZ:.1f} Hz"
        )
    if high_risk_signals:
        status = "high_risk"
        summary = (
            "Decoded behavior is too far from the currently cached in-distribution decoder reference and should still be treated as obvious buzzing risk."
        )
    elif len(elevated_risk_signals) >= 2:
        status = "elevated_risk"
        summary = (
            "Decoded behavior is closer to the current decoder reference than the obvious-buzz regime, but it still needs review before being treated as healthy audio."
        )
    else:
        status = "low_risk"
        summary = "Decoded behavior stays within the current reference-relative guardrails and does not trigger the obvious-buzz heuristics."
    signals = high_risk_signals if high_risk_signals else elevated_risk_signals
    recommended_actions = []
    if status in {"high_risk", "elevated_risk"}:
        recommended_actions = [
            "Treat this output as diagnostic and inspect the decoded wav before using it as a user-facing sample.",
            "Run analyze-offline-mvp-teacher-first-vc-decoder-behavior with post_ola_envelope, pre_overlap_add, and disabled predicted gate to isolate whether the gate path is amplifying the artifact.",
            "If the risk persists across decode settings, treat the current Stage5 checkpoint as out-of-distribution for this user-line control payload.",
        ]
    return {
        "heuristic_version": heuristic_version,
        "status": status,
        "summary": summary,
        "use_predicted_activity_gate": bool(use_predicted_activity_gate),
        "predicted_activity_gate_apply_mode": str(predicted_activity_gate_apply_mode),
        "decoded_spectral_summary": decoded_spectral_summary,
        "reference_decoder_behavior_checkpoint_path": reference_checkpoint_path,
        "reference_decoder_behavior_branch_label": reference_branch_label,
        "reference_shift": reference_shift,
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
    reference_decoder_behavior = dict(summary.get("reference_decoder_behavior", {}))
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
        f"- heuristic_version: {applicability_risk.get('heuristic_version')}",
        f"- reference_shift: {json.dumps(applicability_risk.get('reference_shift'), ensure_ascii=False)}",
        f"- signals: {json.dumps(applicability_risk.get('signals'), ensure_ascii=False)}",
        f"- recommended_actions: {json.dumps(applicability_risk.get('recommended_actions'), ensure_ascii=False)}",
        "",
        "## Reference Decoder Behavior",
        f"- checkpoint_path: {reference_decoder_behavior.get('checkpoint_path')}",
        f"- branch_label: {reference_decoder_behavior.get('branch_label')}",
        f"- case_count: {reference_decoder_behavior.get('case_count')}",
        f"- metric_distribution: {json.dumps(reference_decoder_behavior.get('metric_distribution'), ensure_ascii=False)}",
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


def build_teacher_first_vc_audible_smoke_bundle(
    *,
    output_dir: Path,
    input_audio_paths: list[Path] | None,
    input_spec_jsonl_path: Path | None,
    device: str,
    max_audio_sec_default: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    chunk_ms: float | None,
    calibration_asset_path: Path | None,
    target_reference_audio_path: Path | None,
    target_reference_max_audio_sec: float | None,
) -> None:
    resolved_specs = resolve_review_bundle_input_specs(
        input_audio_paths=input_audio_paths,
        input_spec_jsonl_path=input_spec_jsonl_path,
        max_audio_sec_default=max_audio_sec_default,
    )
    if not resolved_specs:
        raise ValueError("Audible smoke bundle requires at least one input audio.")

    resolved_calibration_asset_path = (
        DEFAULT_CALIBRATION_ASSET_PATH if calibration_asset_path is None else calibration_asset_path.resolve()
    )
    resolved_target_reference_audio_path = resolve_audible_smoke_target_reference_audio_path(
        calibration_asset_path=resolved_calibration_asset_path,
        target_reference_audio_path=target_reference_audio_path,
    )
    resolved_target_reference_max_audio_sec = coerce_optional_float(target_reference_max_audio_sec)

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    runs_dir = output_dir / "runs"
    listening_dir = output_dir / "listening"
    runs_dir.mkdir(parents=True, exist_ok=True)
    listening_dir.mkdir(parents=True, exist_ok=True)

    persisted_specs_path = output_dir / "audible_smoke_input_specs.jsonl"
    persisted_specs_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in resolved_specs) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    target_reference_asset_path = listening_dir / "_shared_target_reference.wav"
    target_reference_asset = materialize_smoke_audio_asset(
        source_audio_path=resolved_target_reference_audio_path,
        output_audio_path=target_reference_asset_path,
        max_audio_sec=resolved_target_reference_max_audio_sec,
    )

    case_results: list[dict[str, object]] = []
    for index, spec in enumerate(resolved_specs, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=spec.get("case_id"),
            input_audio_path=Path(str(spec["input_audio_path"])),
            index=index,
        )
        case_output_dir = runs_dir / case_id
        listening_case_dir = listening_dir / case_id
        listening_case_dir.mkdir(parents=True, exist_ok=True)
        exception: Exception | None = None
        try:
            run_offline_mvp_teacher_first_vc_demo(
                input_audio_path=Path(str(spec["input_audio_path"])),
                output_dir=case_output_dir,
                teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                teacher_checkpoint_path=None,
                calibration_asset_path=resolved_calibration_asset_path,
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
        source_input_asset = materialize_smoke_audio_asset(
            source_audio_path=Path(str(spec["input_audio_path"])),
            output_audio_path=listening_case_dir / "source_input.wav",
            max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
        )
        passthrough_asset = materialize_smoke_audio_asset(
            source_audio_path=Path(str(spec["input_audio_path"])),
            output_audio_path=listening_case_dir / "smoke_baseline_passthrough.wav",
            max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
        )
        target_reference_case_path = listening_case_dir / "target_reference.wav"
        shutil.copy2(target_reference_asset_path, target_reference_case_path)

        decoded_asset_path = listening_case_dir / "decoded_experimental.wav"
        decoded_audio_exists = bool(summary.get("decoded_audio_exists")) and Path(
            str(summary.get("decoded_audio_path"))
        ).is_file()
        if decoded_audio_exists:
            shutil.copy2(case_output_dir / "decoded.wav", decoded_asset_path)

        applicability_risk = dict(summary.get("applicability_risk", {}))
        controls_ready = (
            source_input_asset["exists"]
            and passthrough_asset["exists"]
            and target_reference_case_path.is_file()
        )
        case_results.append(
            {
                "case_index": index,
                "case_id": case_id,
                "status": summary.get("status"),
                "input_audio_path": summary.get("input_audio_path"),
                "max_audio_sec": spec.get("max_audio_sec"),
                "summary_path": (case_output_dir / "teacher_first_vc_demo.json").as_posix(),
                "decoded_audio_path": summary.get("decoded_audio_path"),
                "decoded_listening_audio_path": decoded_asset_path.as_posix() if decoded_audio_exists else None,
                "source_input_audio_path": source_input_asset["output_audio_path"],
                "smoke_baseline_passthrough_audio_path": passthrough_asset["output_audio_path"],
                "target_reference_audio_path": target_reference_case_path.as_posix(),
                "decoded_audio_sec": summary.get("decoded_audio_sec"),
                "decoded_waveform_rms": summary.get("decoded_waveform_rms"),
                "branch_label": dict(summary.get("vocoder", {})).get("branch_label"),
                "applicability_risk": applicability_risk,
                "positive_controls_ready": controls_ready,
                "decoded_audio_exists": decoded_audio_exists,
                "decoded_high_risk": str(applicability_risk.get("status")) == "high_risk",
                "failure": summary.get("failure"),
                "exception": None
                if exception is None
                else {
                    "error_type": type(exception).__name__,
                    "error_message": str(exception),
                },
                "notes": list(spec.get("notes", [])) if isinstance(spec.get("notes"), list) else [],
            }
        )

    bundle_summary = build_audible_smoke_bundle_summary(
        output_dir=output_dir,
        device=device,
        chunk_ms=chunk_ms,
        save_intermediates=save_intermediates,
        verify_against_full_pass=verify_against_full_pass,
        case_results=case_results,
        input_spec_jsonl_path=input_spec_jsonl_path,
        persisted_specs_path=persisted_specs_path,
        calibration_asset_path=resolved_calibration_asset_path,
        target_reference_audio_path=resolved_target_reference_audio_path,
        target_reference_asset=target_reference_asset,
        target_reference_shared_audio_path=target_reference_asset_path,
    )
    write_audible_smoke_bundle_summary(
        summary_json_path=output_dir / "teacher_first_vc_audible_smoke_bundle.json",
        summary_md_path=output_dir / "teacher_first_vc_audible_smoke_bundle.md",
        summary=bundle_summary,
    )
    if not bool(bundle_summary["all_cases_pipeline_succeeded"]):
        raise ValueError(
            "teacher-first VC audible smoke bundle contains failed demo cases; inspect teacher_first_vc_audible_smoke_bundle.json for details."
        )
    if not bool(bundle_summary["all_cases_positive_controls_ready"]):
        raise ValueError(
            "teacher-first VC audible smoke bundle is missing positive-control audio; inspect teacher_first_vc_audible_smoke_bundle.json for details."
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
    sanitized = sanitize_bundle_component(base)
    if not sanitized:
        sanitized = f"case_{index:03d}"
    return f"{index:03d}_{sanitized}"


def sanitize_bundle_component(raw_value: object) -> str:
    return "".join(
        char if char.isalnum() or char in {"_", "-"} else "_"
        for char in str(raw_value)
    ).strip("_")


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


def resolve_audible_smoke_target_reference_audio_path(
    *,
    calibration_asset_path: Path,
    target_reference_audio_path: Path | None,
) -> Path:
    if target_reference_audio_path is not None:
        resolved = target_reference_audio_path.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Target reference audio does not exist: {resolved}")
        return resolved
    if DEFAULT_EXPLICIT_CLEAN_TARGET_REFERENCE_AUDIO_PATH.is_file():
        return DEFAULT_EXPLICIT_CLEAN_TARGET_REFERENCE_AUDIO_PATH.resolve()
    payload = json.loads(calibration_asset_path.resolve().read_text(encoding="utf-8"))
    selected_record_ids = list(dict(payload.get("selection_summary", {})).get("selected_record_ids", []))
    source_records_path = Path(str(dict(payload.get("estimation_metadata", {})).get("source_records_path", ""))).resolve()
    if not selected_record_ids:
        raise ValueError(
            "Calibration asset does not expose selection_summary.selected_record_ids for audible smoke target reference."
        )
    if not source_records_path.is_file():
        raise FileNotFoundError(
            f"Calibration asset source_records_path is missing for audible smoke target reference: {source_records_path}"
        )
    record_map: dict[str, Path] = {}
    for row in load_jsonl(source_records_path):
        record_id = row.get("record_id")
        audio_path = row.get("audio_path")
        if record_id in {None, ""} or audio_path in {None, ""}:
            continue
        record_map[str(record_id)] = Path(str(audio_path)).resolve()
    for record_id in selected_record_ids:
        resolved = record_map.get(str(record_id))
        if resolved is not None and resolved.is_file():
            return resolved
    raise FileNotFoundError(
        "Could not resolve any selected calibration target audio for audible smoke bundle target reference."
    )


def materialize_smoke_audio_asset(
    *,
    source_audio_path: Path,
    output_audio_path: Path,
    max_audio_sec: float | None,
) -> dict[str, object]:
    waveform, sample_rate = load_waveform(source_audio_path.resolve(), max_duration_sec=max_audio_sec)
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    write_waveform_int16(output_audio_path, waveform, sample_rate=int(sample_rate))
    return {
        "source_audio_path": source_audio_path.resolve().as_posix(),
        "output_audio_path": output_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "audio_sec": round(float(waveform.shape[0]) / float(sample_rate), 6) if int(sample_rate) > 0 else 0.0,
        "waveform_rms": round(float(waveform.to(torch.float32).pow(2).mean().sqrt().item()), 6)
        if waveform.numel() > 0
        else 0.0,
        "exists": output_audio_path.is_file(),
    }


def build_audible_smoke_bundle_summary(
    *,
    output_dir: Path,
    device: str,
    chunk_ms: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    case_results: list[dict[str, object]],
    input_spec_jsonl_path: Path | None,
    persisted_specs_path: Path,
    calibration_asset_path: Path,
    target_reference_audio_path: Path,
    target_reference_asset: dict[str, object],
    target_reference_shared_audio_path: Path,
) -> dict[str, object]:
    pipeline_succeeded_count = sum(1 for item in case_results if str(item.get("status")) == "succeeded")
    positive_controls_ready_count = sum(1 for item in case_results if bool(item.get("positive_controls_ready")))
    decoded_high_risk_count = sum(1 for item in case_results if bool(item.get("decoded_high_risk")))
    decoded_present_count = sum(1 for item in case_results if bool(item.get("decoded_audio_exists")))
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_audible_smoke_bundle_v1",
        "output_dir": output_dir.as_posix(),
        "input_spec_jsonl_path": safe_resolve_path(input_spec_jsonl_path),
        "materialized_input_specs_path": persisted_specs_path.as_posix(),
        "device": str(device),
        "chunk_ms": chunk_ms,
        "save_intermediates": bool(save_intermediates),
        "verify_against_full_pass": bool(verify_against_full_pass),
        "case_count": len(case_results),
        "pipeline_succeeded_count": pipeline_succeeded_count,
        "pipeline_failed_count": len(case_results) - pipeline_succeeded_count,
        "positive_controls_ready_count": positive_controls_ready_count,
        "decoded_present_count": decoded_present_count,
        "decoded_high_risk_count": decoded_high_risk_count,
        "all_cases_pipeline_succeeded": pipeline_succeeded_count == len(case_results),
        "all_cases_positive_controls_ready": positive_controls_ready_count == len(case_results),
        "shared_target_reference": {
            "calibration_asset_path": calibration_asset_path.as_posix(),
            "resolved_source_audio_path": target_reference_audio_path.as_posix(),
            "shared_audio_path": target_reference_shared_audio_path.as_posix(),
            "sample_rate": target_reference_asset["sample_rate"],
            "audio_sec": target_reference_asset["audio_sec"],
            "waveform_rms": target_reference_asset["waveform_rms"],
        },
        "listening_dir": (output_dir / "listening").as_posix(),
        "runs_dir": (output_dir / "runs").as_posix(),
        "cases": case_results,
        "notes": [
            "This bundle separates positive-control listening assets from the current experimental decoded output.",
            "Each case exports source_input.wav, target_reference.wav, smoke_baseline_passthrough.wav, and decoded_experimental.wav when the demo run succeeds.",
            "A case can be a valid audible smoke bundle even when decoded_experimental.wav remains high-risk buzzing; that condition is reported explicitly rather than hidden behind exit-code success.",
        ],
    }


def write_audible_smoke_bundle_summary(
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
        build_audible_smoke_bundle_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_audible_smoke_bundle_markdown(summary: dict[str, object]) -> str:
    shared_target_reference = dict(summary.get("shared_target_reference", {}))
    lines = [
        "# Teacher-First VC Audible Smoke Bundle",
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
        f"- pipeline_succeeded_count: {summary['pipeline_succeeded_count']}",
        f"- pipeline_failed_count: {summary['pipeline_failed_count']}",
        f"- positive_controls_ready_count: {summary['positive_controls_ready_count']}",
        f"- decoded_present_count: {summary['decoded_present_count']}",
        f"- decoded_high_risk_count: {summary['decoded_high_risk_count']}",
        f"- all_cases_pipeline_succeeded: {summary['all_cases_pipeline_succeeded']}",
        f"- all_cases_positive_controls_ready: {summary['all_cases_positive_controls_ready']}",
        f"- listening_dir: {summary['listening_dir']}",
        f"- runs_dir: {summary['runs_dir']}",
        "",
        "## Shared Target Reference",
        f"- calibration_asset_path: {shared_target_reference.get('calibration_asset_path')}",
        f"- resolved_source_audio_path: {shared_target_reference.get('resolved_source_audio_path')}",
        f"- shared_audio_path: {shared_target_reference.get('shared_audio_path')}",
        f"- sample_rate: {shared_target_reference.get('sample_rate')}",
        f"- audio_sec: {shared_target_reference.get('audio_sec')}",
        f"- waveform_rms: {shared_target_reference.get('waveform_rms')}",
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
                f"  positive_controls_ready: {case.get('positive_controls_ready')}",
                f"  decoded_audio_exists: {case.get('decoded_audio_exists')}",
                f"  decoded_high_risk: {case.get('decoded_high_risk')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  source_input_audio_path: {case.get('source_input_audio_path')}",
                f"  target_reference_audio_path: {case.get('target_reference_audio_path')}",
                f"  smoke_baseline_passthrough_audio_path: {case.get('smoke_baseline_passthrough_audio_path')}",
                f"  decoded_listening_audio_path: {case.get('decoded_listening_audio_path')}",
                f"  decoded_audio_sec: {case.get('decoded_audio_sec')}",
                f"  decoded_waveform_rms: {case.get('decoded_waveform_rms')}",
                f"  branch_label: {case.get('branch_label')}",
                f"  applicability_risk: {json.dumps(case.get('applicability_risk'), ensure_ascii=False)}",
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


def build_teacher_first_vc_audible_compare_bundle(
    *,
    output_dir: Path,
    input_audio_paths: list[Path] | None,
    input_spec_jsonl_path: Path | None,
    device: str,
    max_audio_sec_default: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    chunk_ms: float | None,
    calibration_asset_path: Path | None,
    target_reference_audio_path: Path | None,
    target_reference_max_audio_sec: float | None,
    vocoder_spec_jsonl_path: Path | None,
) -> None:
    resolved_specs = resolve_review_bundle_input_specs(
        input_audio_paths=input_audio_paths,
        input_spec_jsonl_path=input_spec_jsonl_path,
        max_audio_sec_default=max_audio_sec_default,
    )
    if not resolved_specs:
        raise ValueError("Audible compare bundle requires at least one input audio.")

    resolved_vocoder_specs = resolve_audible_compare_vocoder_specs(
        vocoder_spec_jsonl_path=vocoder_spec_jsonl_path,
    )
    if not resolved_vocoder_specs:
        raise ValueError("Audible compare bundle requires at least one vocoder variant.")

    resolved_calibration_asset_path = (
        DEFAULT_CALIBRATION_ASSET_PATH if calibration_asset_path is None else calibration_asset_path.resolve()
    )
    resolved_target_reference_audio_path = resolve_audible_smoke_target_reference_audio_path(
        calibration_asset_path=resolved_calibration_asset_path,
        target_reference_audio_path=target_reference_audio_path,
    )
    resolved_target_reference_max_audio_sec = coerce_optional_float(target_reference_max_audio_sec)

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    runs_dir = output_dir / "runs"
    listening_dir = output_dir / "listening"
    runs_dir.mkdir(parents=True, exist_ok=True)
    listening_dir.mkdir(parents=True, exist_ok=True)

    persisted_specs_path = output_dir / "audible_compare_input_specs.jsonl"
    persisted_specs_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in resolved_specs) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    persisted_vocoder_specs_path = output_dir / "audible_compare_vocoder_specs.jsonl"
    persisted_vocoder_specs_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in resolved_vocoder_specs) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    target_reference_asset_path = listening_dir / "_shared_target_reference.wav"
    target_reference_asset = materialize_smoke_audio_asset(
        source_audio_path=resolved_target_reference_audio_path,
        output_audio_path=target_reference_asset_path,
        max_audio_sec=resolved_target_reference_max_audio_sec,
    )

    case_results: list[dict[str, object]] = []
    for index, spec in enumerate(resolved_specs, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=spec.get("case_id"),
            input_audio_path=Path(str(spec["input_audio_path"])),
            index=index,
        )
        listening_case_dir = listening_dir / case_id
        listening_case_dir.mkdir(parents=True, exist_ok=True)
        source_input_asset = materialize_smoke_audio_asset(
            source_audio_path=Path(str(spec["input_audio_path"])),
            output_audio_path=listening_case_dir / "source_input.wav",
            max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
        )
        passthrough_asset = materialize_smoke_audio_asset(
            source_audio_path=Path(str(spec["input_audio_path"])),
            output_audio_path=listening_case_dir / "smoke_baseline_passthrough.wav",
            max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
        )
        target_reference_case_path = listening_case_dir / "target_reference.wav"
        shutil.copy2(target_reference_asset_path, target_reference_case_path)

        variant_results: list[dict[str, object]] = []
        for variant_index, vocoder_spec in enumerate(resolved_vocoder_specs, start=1):
            variant_id = str(vocoder_spec["variant_id"])
            case_output_dir = runs_dir / case_id / variant_id
            exception: Exception | None = None
            try:
                run_offline_mvp_teacher_first_vc_demo(
                    input_audio_path=Path(str(spec["input_audio_path"])),
                    output_dir=case_output_dir,
                    teacher_route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
                    teacher_checkpoint_path=None,
                    calibration_asset_path=resolved_calibration_asset_path,
                    vocoder_checkpoint_path=None
                    if vocoder_spec.get("checkpoint_selection_path")
                    else Path(str(vocoder_spec["checkpoint_path"])),
                    vocoder_checkpoint_selection_path=None
                    if not vocoder_spec.get("checkpoint_selection_path")
                    else Path(str(vocoder_spec["checkpoint_selection_path"])),
                    selection_target=str(vocoder_spec.get("selection_target") or "best_validation"),
                    chunk_samples=None,
                    chunk_ms=chunk_ms,
                    device=device,
                    max_audio_sec=coerce_optional_float(spec.get("max_audio_sec")),
                    verify_against_full_pass=bool(verify_against_full_pass),
                    save_intermediates=bool(save_intermediates),
                    use_predicted_activity_gate=bool(vocoder_spec.get("use_predicted_activity_gate", True)),
                    predicted_activity_gate_floor=0.0,
                    predicted_activity_gate_smoothing_frames=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
                    predicted_activity_gate_apply_mode=str(
                        vocoder_spec.get("predicted_activity_gate_apply_mode") or "post_ola_envelope"
                    ),
                    normalization_strategy=str(vocoder_spec.get("normalization_strategy") or "none"),
                    control_family_overrides=list(vocoder_spec.get("control_family_overrides", [])),
                )
            except Exception as exc:
                exception = exc

            summary = load_teacher_first_vc_demo_summary(case_output_dir / "teacher_first_vc_demo.json")
            decoded_asset_path = listening_case_dir / f"decoded_{variant_id}.wav"
            decoded_audio_exists = bool(summary.get("decoded_audio_exists")) and Path(
                str(summary.get("decoded_audio_path"))
            ).is_file()
            if decoded_audio_exists:
                shutil.copy2(case_output_dir / "decoded.wav", decoded_asset_path)
            applicability_risk = dict(summary.get("applicability_risk", {}))
            variant_results.append(
                {
                    "variant_index": variant_index,
                    "variant_id": variant_id,
                    "label": vocoder_spec["label"],
                    "checkpoint_path": vocoder_spec["checkpoint_path"],
                    "checkpoint_selection_path": vocoder_spec.get("checkpoint_selection_path"),
                    "checkpoint_source_summary_path": vocoder_spec.get("checkpoint_source_summary_path"),
                    "checkpoint_source_key": vocoder_spec.get("checkpoint_source_key"),
                    "selection_target": vocoder_spec.get("selection_target"),
                    "status": summary.get("status"),
                    "summary_path": (case_output_dir / "teacher_first_vc_demo.json").as_posix(),
                    "decoded_audio_path": summary.get("decoded_audio_path"),
                    "decoded_listening_audio_path": decoded_asset_path.as_posix() if decoded_audio_exists else None,
                    "decoded_audio_exists": decoded_audio_exists,
                    "decoded_audio_sec": summary.get("decoded_audio_sec"),
                    "decoded_waveform_rms": summary.get("decoded_waveform_rms"),
                    "branch_label": dict(summary.get("vocoder", {})).get("branch_label"),
                    "use_predicted_activity_gate": vocoder_spec.get("use_predicted_activity_gate"),
                    "predicted_activity_gate_apply_mode": vocoder_spec.get(
                        "predicted_activity_gate_apply_mode"
                    ),
                    "normalization_strategy": vocoder_spec.get("normalization_strategy"),
                    "control_family_overrides": list(vocoder_spec.get("control_family_overrides", [])),
                    "control_family_override_summary": list(
                        vocoder_spec.get("control_family_override_summary", [])
                    ),
                    "applicability_risk_status": applicability_risk.get("status"),
                    "applicability_risk_summary": applicability_risk.get("summary"),
                    "applicability_risk": applicability_risk,
                    "decoded_high_risk": str(applicability_risk.get("status")) == "high_risk",
                    "failure": summary.get("failure"),
                    "exception": None
                    if exception is None
                    else {
                        "error_type": type(exception).__name__,
                        "error_message": str(exception),
                    },
                    "notes": list(vocoder_spec.get("notes", []))
                    if isinstance(vocoder_spec.get("notes"), list)
                    else [],
                }
            )

        case_results.append(
            {
                "case_index": index,
                "case_id": case_id,
                "input_audio_path": safe_resolve_path(Path(str(spec["input_audio_path"]))),
                "max_audio_sec": spec.get("max_audio_sec"),
                "source_input_audio_path": source_input_asset["output_audio_path"],
                "smoke_baseline_passthrough_audio_path": passthrough_asset["output_audio_path"],
                "target_reference_audio_path": target_reference_case_path.as_posix(),
                "positive_controls_ready": (
                    source_input_asset["exists"]
                    and passthrough_asset["exists"]
                    and target_reference_case_path.is_file()
                ),
                "variants": variant_results,
                "notes": list(spec.get("notes", [])) if isinstance(spec.get("notes"), list) else [],
            }
        )

    bundle_summary = build_audible_compare_bundle_summary(
        output_dir=output_dir,
        device=device,
        chunk_ms=chunk_ms,
        save_intermediates=save_intermediates,
        verify_against_full_pass=verify_against_full_pass,
        case_results=case_results,
        input_spec_jsonl_path=input_spec_jsonl_path,
        persisted_specs_path=persisted_specs_path,
        persisted_vocoder_specs_path=persisted_vocoder_specs_path,
        calibration_asset_path=resolved_calibration_asset_path,
        target_reference_audio_path=resolved_target_reference_audio_path,
        target_reference_asset=target_reference_asset,
        target_reference_shared_audio_path=target_reference_asset_path,
    )
    write_audible_compare_bundle_summary(
        summary_json_path=output_dir / "teacher_first_vc_audible_compare_bundle.json",
        summary_md_path=output_dir / "teacher_first_vc_audible_compare_bundle.md",
        summary=bundle_summary,
    )
    if not bool(bundle_summary["all_cases_positive_controls_ready"]):
        raise ValueError(
            "teacher-first VC audible compare bundle is missing positive-control audio; inspect teacher_first_vc_audible_compare_bundle.json for details."
        )
    if not bool(bundle_summary["all_variant_runs_succeeded"]):
        raise ValueError(
            "teacher-first VC audible compare bundle contains failed variant runs; inspect teacher_first_vc_audible_compare_bundle.json for details."
        )


def default_audible_compare_vocoder_specs() -> list[dict[str, object]]:
    return [
        {
            "label": "normfix_default",
            "checkpoint_selection_path": DEFAULT_AUDIBLE_COMPARE_ACTIVE_CHECKPOINT_SELECTION_PATH.resolve().as_posix(),
            "selection_target": "best_validation",
            "notes": [
                "Current experiment-line default user-line chain on the contractv2_normfix Stage5 checkpoint.",
                "This keeps predicted activity gate enabled with post_ola_envelope and does not apply inference-only normalization.",
            ],
        },
        {
            "label": "affine_events_refmean_gateoff",
            "checkpoint_selection_path": DEFAULT_AUDIBLE_COMPARE_ACTIVE_CHECKPOINT_SELECTION_PATH.resolve().as_posix(),
            "selection_target": "best_validation",
            "normalization_strategy": "reference_affine_match",
            "control_family_overrides": ["event_probs=reference_mean"],
            "use_predicted_activity_gate": False,
            "notes": [
                "Current best inference-only candidate from the 2026-03-24 decoder-behavior probe.",
                "Uses reference_affine_match plus event_probs=reference_mean with the predicted activity gate disabled.",
            ],
        },
    ]


def resolve_audible_compare_vocoder_specs(
    *,
    vocoder_spec_jsonl_path: Path | None,
) -> list[dict[str, object]]:
    raw_specs: list[dict[str, object]] = []
    if vocoder_spec_jsonl_path is None:
        raw_specs = default_audible_compare_vocoder_specs()
    else:
        for row in load_jsonl(vocoder_spec_jsonl_path.resolve()):
            raw_specs.append(dict(row))
    resolved_specs: list[dict[str, object]] = []
    seen_variant_ids: dict[str, int] = {}
    for index, row in enumerate(raw_specs, start=1):
        raw_variant_id = row.get("variant_id")
        label = str(row.get("label") or raw_variant_id or f"variant_{index:02d}").strip()
        variant_id_base = build_compare_variant_id(
            label=str(raw_variant_id or label),
            index=index,
        )
        duplicate_count = int(seen_variant_ids.get(variant_id_base, 0))
        seen_variant_ids[variant_id_base] = duplicate_count + 1
        variant_id = (
            variant_id_base
            if duplicate_count == 0
            else f"{variant_id_base}_{duplicate_count + 1:02d}"
        )
        checkpoint_path_value = row.get("checkpoint_path")
        checkpoint_selection_path_value = row.get("checkpoint_selection_path")
        checkpoint_source_summary_path_value = row.get("checkpoint_source_summary_path")
        checkpoint_source_key = str(row.get("checkpoint_source_key") or "best_checkpoint").strip()
        selection_target = str(row.get("selection_target") or "best_validation").strip()
        if checkpoint_path_value not in {None, ""}:
            checkpoint_path = Path(str(checkpoint_path_value)).resolve()
            checkpoint_selection_path = (
                None
                if checkpoint_selection_path_value in {None, ""}
                else Path(str(checkpoint_selection_path_value)).resolve()
            )
            checkpoint_source_summary_path = (
                None
                if checkpoint_source_summary_path_value in {None, ""}
                else Path(str(checkpoint_source_summary_path_value)).resolve()
            )
        elif checkpoint_selection_path_value not in {None, ""}:
            checkpoint_selection_path = Path(str(checkpoint_selection_path_value)).resolve()
            checkpoint_path, _ = resolve_checkpoint_path_from_inputs(
                checkpoint_path=None,
                checkpoint_selection_path=checkpoint_selection_path,
                selection_target=selection_target,
            )
            checkpoint_source_summary_path = (
                None
                if checkpoint_source_summary_path_value in {None, ""}
                else Path(str(checkpoint_source_summary_path_value)).resolve()
            )
        else:
            if checkpoint_source_summary_path_value in {None, ""}:
                raise ValueError(
                    "Each audible compare vocoder spec row must include checkpoint_path, checkpoint_selection_path, or checkpoint_source_summary_path."
                )
            checkpoint_path = resolve_checkpoint_path_from_training_summary(
                summary_json_path=Path(str(checkpoint_source_summary_path_value)),
                checkpoint_source_key=checkpoint_source_key,
            )
            checkpoint_source_summary_path = Path(str(checkpoint_source_summary_path_value)).resolve()
            checkpoint_selection_path = None
        use_predicted_activity_gate = bool(row.get("use_predicted_activity_gate", True))
        predicted_activity_gate_apply_mode = normalize_predicted_activity_gate_apply_mode(
            str(row.get("predicted_activity_gate_apply_mode") or "post_ola_envelope")
        )
        normalization_strategy = normalize_decoder_probe_normalization_strategy(
            str(row.get("normalization_strategy") or "none")
        )
        raw_control_family_overrides = row.get("control_family_overrides")
        if raw_control_family_overrides is None or raw_control_family_overrides == "":
            control_family_overrides = []
        elif isinstance(raw_control_family_overrides, list):
            control_family_overrides = [str(item) for item in raw_control_family_overrides if str(item).strip()]
        else:
            control_family_overrides = [str(raw_control_family_overrides)]
        parsed_control_family_overrides = parse_decoder_probe_control_family_overrides(
            control_family_overrides
        )
        resolved_specs.append(
            {
                "variant_index": index,
                "variant_id": variant_id,
                "label": label,
                "checkpoint_path": checkpoint_path.as_posix(),
                "checkpoint_selection_path": None
                if checkpoint_selection_path is None
                else checkpoint_selection_path.as_posix(),
                "checkpoint_source_summary_path": None
                if checkpoint_source_summary_path is None
                else checkpoint_source_summary_path.as_posix(),
                "checkpoint_source_key": checkpoint_source_key,
                "selection_target": selection_target,
                "use_predicted_activity_gate": use_predicted_activity_gate,
                "predicted_activity_gate_apply_mode": predicted_activity_gate_apply_mode,
                "normalization_strategy": normalization_strategy,
                "control_family_overrides": control_family_overrides,
                "control_family_override_summary": serialize_decoder_probe_control_family_overrides(
                    parsed_control_family_overrides
                ),
                "notes": list(row.get("notes", [])) if isinstance(row.get("notes"), list) else [],
            }
        )
    return resolved_specs


def resolve_checkpoint_path_from_training_summary(
    *,
    summary_json_path: Path,
    checkpoint_source_key: str,
) -> Path:
    resolved_summary_path = summary_json_path.resolve()
    if not resolved_summary_path.is_file():
        raise FileNotFoundError(f"Training summary json does not exist: {resolved_summary_path}")
    payload = json.loads(resolved_summary_path.read_text(encoding="utf-8"))
    artifacts = dict(payload.get("artifacts", {}))
    key = str(checkpoint_source_key).strip().lower()
    if key == "best_checkpoint":
        checkpoint_value = dict(artifacts.get("best_checkpoint", {})).get("checkpoint_path")
    elif key == "latest_checkpoint":
        checkpoint_value = artifacts.get("latest_checkpoint_path")
    else:
        raise ValueError(f"Unsupported checkpoint_source_key: {checkpoint_source_key}")
    if checkpoint_value in {None, ""}:
        raise ValueError(
            f"Training summary {resolved_summary_path} does not expose checkpoint for {checkpoint_source_key}."
        )
    resolved_checkpoint_path = Path(str(checkpoint_value)).resolve()
    if not resolved_checkpoint_path.is_file():
        raise FileNotFoundError(
            f"Resolved compare-bundle checkpoint does not exist: {resolved_checkpoint_path}"
        )
    return resolved_checkpoint_path


def build_compare_variant_id(*, label: str, index: int) -> str:
    sanitized = sanitize_bundle_component(label)
    if not sanitized:
        sanitized = f"variant_{index:02d}"
    return sanitized


def build_audible_compare_bundle_summary(
    *,
    output_dir: Path,
    device: str,
    chunk_ms: float | None,
    save_intermediates: bool,
    verify_against_full_pass: bool,
    case_results: list[dict[str, object]],
    input_spec_jsonl_path: Path | None,
    persisted_specs_path: Path,
    persisted_vocoder_specs_path: Path,
    calibration_asset_path: Path,
    target_reference_audio_path: Path,
    target_reference_asset: dict[str, object],
    target_reference_shared_audio_path: Path,
) -> dict[str, object]:
    variant_run_count = 0
    variant_succeeded_count = 0
    variant_decoded_present_count = 0
    variant_decoded_high_risk_count = 0
    variant_rollups: dict[str, dict[str, object]] = {}
    positive_controls_ready_count = 0
    for case in case_results:
        if bool(case.get("positive_controls_ready")):
            positive_controls_ready_count += 1
        for variant in list(case.get("variants", [])):
            if not isinstance(variant, dict):
                continue
            variant_run_count += 1
            if str(variant.get("status")) == "succeeded":
                variant_succeeded_count += 1
            if bool(variant.get("decoded_audio_exists")):
                variant_decoded_present_count += 1
            if bool(variant.get("decoded_high_risk")):
                variant_decoded_high_risk_count += 1
            variant_id = str(variant.get("variant_id"))
            rollup = variant_rollups.setdefault(
                variant_id,
                {
                    "variant_id": variant_id,
                    "label": variant.get("label"),
                    "checkpoint_path": variant.get("checkpoint_path"),
                    "checkpoint_selection_path": variant.get("checkpoint_selection_path"),
                    "checkpoint_source_summary_path": variant.get("checkpoint_source_summary_path"),
                    "checkpoint_source_key": variant.get("checkpoint_source_key"),
                    "selection_target": variant.get("selection_target"),
                    "use_predicted_activity_gate": variant.get("use_predicted_activity_gate"),
                    "predicted_activity_gate_apply_mode": variant.get("predicted_activity_gate_apply_mode"),
                    "normalization_strategy": variant.get("normalization_strategy"),
                    "control_family_overrides": list(variant.get("control_family_overrides", [])),
                    "control_family_override_summary": list(
                        variant.get("control_family_override_summary", [])
                    ),
                    "case_count": 0,
                    "succeeded_count": 0,
                    "decoded_present_count": 0,
                    "decoded_high_risk_count": 0,
                    "high_risk_case_ids": [],
                    "notes": list(variant.get("notes", [])) if isinstance(variant.get("notes"), list) else [],
                },
            )
            rollup["case_count"] = int(rollup["case_count"]) + 1
            if str(variant.get("status")) == "succeeded":
                rollup["succeeded_count"] = int(rollup["succeeded_count"]) + 1
            if bool(variant.get("decoded_audio_exists")):
                rollup["decoded_present_count"] = int(rollup["decoded_present_count"]) + 1
            if bool(variant.get("decoded_high_risk")):
                rollup["decoded_high_risk_count"] = int(rollup["decoded_high_risk_count"]) + 1
                rollup["high_risk_case_ids"] = list(rollup.get("high_risk_case_ids", [])) + [
                    str(case.get("case_id"))
                ]
    vocoder_variants = list(variant_rollups.values())
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_audible_compare_bundle_v1",
        "output_dir": output_dir.as_posix(),
        "input_spec_jsonl_path": safe_resolve_path(input_spec_jsonl_path),
        "materialized_input_specs_path": persisted_specs_path.as_posix(),
        "materialized_vocoder_specs_path": persisted_vocoder_specs_path.as_posix(),
        "device": str(device),
        "chunk_ms": chunk_ms,
        "save_intermediates": bool(save_intermediates),
        "verify_against_full_pass": bool(verify_against_full_pass),
        "case_count": len(case_results),
        "variant_count": len(vocoder_variants),
        "variant_run_count": variant_run_count,
        "variant_succeeded_count": variant_succeeded_count,
        "variant_failed_count": variant_run_count - variant_succeeded_count,
        "variant_decoded_present_count": variant_decoded_present_count,
        "variant_decoded_high_risk_count": variant_decoded_high_risk_count,
        "positive_controls_ready_count": positive_controls_ready_count,
        "all_cases_positive_controls_ready": positive_controls_ready_count == len(case_results),
        "all_variant_runs_succeeded": variant_succeeded_count == variant_run_count,
        "shared_target_reference": {
            "calibration_asset_path": calibration_asset_path.as_posix(),
            "resolved_source_audio_path": target_reference_audio_path.as_posix(),
            "shared_audio_path": target_reference_shared_audio_path.as_posix(),
            "sample_rate": target_reference_asset["sample_rate"],
            "audio_sec": target_reference_asset["audio_sec"],
            "waveform_rms": target_reference_asset["waveform_rms"],
        },
        "listening_dir": (output_dir / "listening").as_posix(),
        "runs_dir": (output_dir / "runs").as_posix(),
        "vocoder_variants": vocoder_variants,
        "cases": case_results,
        "notes": [
            "smoke_baseline_passthrough.wav is an intentional positive control and should match the source input for each case.",
            "This compare bundle keeps one shared source/target/passthrough trio per case, then exports one decoded_<variant>.wav per configured checkpoint.",
            "A compare bundle can be structurally valid even when every decoded variant remains high-risk buzzing; that condition is surfaced explicitly in variant_decoded_high_risk_count.",
        ],
    }


def write_audible_compare_bundle_summary(
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
        build_audible_compare_bundle_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_audible_compare_bundle_markdown(summary: dict[str, object]) -> str:
    shared_target_reference = dict(summary.get("shared_target_reference", {}))
    lines = [
        "# Teacher-First VC Audible Compare Bundle",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- input_spec_jsonl_path: {summary['input_spec_jsonl_path']}",
        f"- materialized_input_specs_path: {summary['materialized_input_specs_path']}",
        f"- materialized_vocoder_specs_path: {summary['materialized_vocoder_specs_path']}",
        f"- device: {summary['device']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- save_intermediates: {summary['save_intermediates']}",
        f"- verify_against_full_pass: {summary['verify_against_full_pass']}",
        f"- case_count: {summary['case_count']}",
        f"- variant_count: {summary['variant_count']}",
        f"- variant_run_count: {summary['variant_run_count']}",
        f"- variant_succeeded_count: {summary['variant_succeeded_count']}",
        f"- variant_failed_count: {summary['variant_failed_count']}",
        f"- variant_decoded_present_count: {summary['variant_decoded_present_count']}",
        f"- variant_decoded_high_risk_count: {summary['variant_decoded_high_risk_count']}",
        f"- positive_controls_ready_count: {summary['positive_controls_ready_count']}",
        f"- all_cases_positive_controls_ready: {summary['all_cases_positive_controls_ready']}",
        f"- all_variant_runs_succeeded: {summary['all_variant_runs_succeeded']}",
        f"- listening_dir: {summary['listening_dir']}",
        f"- runs_dir: {summary['runs_dir']}",
        "",
        "## Shared Target Reference",
        f"- calibration_asset_path: {shared_target_reference.get('calibration_asset_path')}",
        f"- resolved_source_audio_path: {shared_target_reference.get('resolved_source_audio_path')}",
        f"- shared_audio_path: {shared_target_reference.get('shared_audio_path')}",
        f"- sample_rate: {shared_target_reference.get('sample_rate')}",
        f"- audio_sec: {shared_target_reference.get('audio_sec')}",
        f"- waveform_rms: {shared_target_reference.get('waveform_rms')}",
        "",
        "## Variants",
    ]
    for variant in list(summary.get("vocoder_variants", [])):
        if not isinstance(variant, dict):
            continue
        lines.extend(
            [
                f"- variant_id: {variant.get('variant_id')}",
                f"  label: {variant.get('label')}",
                f"  checkpoint_path: {variant.get('checkpoint_path')}",
                f"  checkpoint_selection_path: {variant.get('checkpoint_selection_path')}",
                f"  checkpoint_source_summary_path: {variant.get('checkpoint_source_summary_path')}",
                f"  checkpoint_source_key: {variant.get('checkpoint_source_key')}",
                f"  selection_target: {variant.get('selection_target')}",
                f"  use_predicted_activity_gate: {variant.get('use_predicted_activity_gate')}",
                f"  predicted_activity_gate_apply_mode: {variant.get('predicted_activity_gate_apply_mode')}",
                f"  normalization_strategy: {variant.get('normalization_strategy')}",
                f"  control_family_overrides: {json.dumps(variant.get('control_family_overrides'), ensure_ascii=False)}",
                f"  control_family_override_summary: {json.dumps(variant.get('control_family_override_summary'), ensure_ascii=False)}",
                f"  case_count: {variant.get('case_count')}",
                f"  succeeded_count: {variant.get('succeeded_count')}",
                f"  decoded_present_count: {variant.get('decoded_present_count')}",
                f"  decoded_high_risk_count: {variant.get('decoded_high_risk_count')}",
                f"  high_risk_case_ids: {json.dumps(variant.get('high_risk_case_ids'), ensure_ascii=False)}",
                f"  notes: {json.dumps(variant.get('notes'), ensure_ascii=False)}",
            ]
        )
    lines.extend(["", "## Cases"])
    for case in list(summary.get("cases", [])):
        if not isinstance(case, dict):
            continue
        lines.extend(
            [
                f"- case_index: {case.get('case_index')}",
                f"  case_id: {case.get('case_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  max_audio_sec: {case.get('max_audio_sec')}",
                f"  positive_controls_ready: {case.get('positive_controls_ready')}",
                f"  source_input_audio_path: {case.get('source_input_audio_path')}",
                f"  smoke_baseline_passthrough_audio_path: {case.get('smoke_baseline_passthrough_audio_path')}",
                f"  target_reference_audio_path: {case.get('target_reference_audio_path')}",
                f"  notes: {json.dumps(case.get('notes'), ensure_ascii=False)}",
            ]
        )
        for variant in list(case.get("variants", [])):
            if not isinstance(variant, dict):
                continue
            lines.extend(
                [
                    f"  variant_id: {variant.get('variant_id')}",
                    f"  variant_label: {variant.get('label')}",
                    f"  variant_status: {variant.get('status')}",
                    f"  variant_decoded_audio_exists: {variant.get('decoded_audio_exists')}",
                    f"  variant_decoded_high_risk: {variant.get('decoded_high_risk')}",
                    f"  variant_decoded_listening_audio_path: {variant.get('decoded_listening_audio_path')}",
                    f"  variant_decoded_audio_sec: {variant.get('decoded_audio_sec')}",
                    f"  variant_decoded_waveform_rms: {variant.get('decoded_waveform_rms')}",
                    f"  variant_branch_label: {variant.get('branch_label')}",
                    f"  variant_checkpoint_path: {variant.get('checkpoint_path')}",
                    f"  variant_checkpoint_selection_path: {variant.get('checkpoint_selection_path')}",
                    f"  variant_selection_target: {variant.get('selection_target')}",
                    f"  variant_use_predicted_activity_gate: {variant.get('use_predicted_activity_gate')}",
                    f"  variant_predicted_activity_gate_apply_mode: {variant.get('predicted_activity_gate_apply_mode')}",
                    f"  variant_normalization_strategy: {variant.get('normalization_strategy')}",
                    f"  variant_control_family_overrides: {json.dumps(variant.get('control_family_overrides'), ensure_ascii=False)}",
                    f"  variant_control_family_override_summary: {json.dumps(variant.get('control_family_override_summary'), ensure_ascii=False)}",
                    f"  variant_applicability_risk_status: {variant.get('applicability_risk_status')}",
                    f"  variant_applicability_risk_summary: {variant.get('applicability_risk_summary')}",
                    f"  variant_summary_path: {variant.get('summary_path')}",
                    f"  variant_applicability_risk: {json.dumps(variant.get('applicability_risk'), ensure_ascii=False)}",
                    f"  variant_failure: {json.dumps(variant.get('failure'), ensure_ascii=False)}",
                    f"  variant_exception: {json.dumps(variant.get('exception'), ensure_ascii=False)}",
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
        "reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/packages/train"
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


def materialize_stage5_input_variant_split(
    *,
    package_entries: list[dict[str, object]],
    split_name: str,
    packages_root: Path,
    control_family_overrides: list[dict[str, object]],
    package_limit: int | None,
) -> list[dict[str, object]]:
    selected_entries = list(package_entries)
    if package_limit is not None and int(package_limit) >= 0:
        selected_entries = selected_entries[: int(package_limit)]
    output_entries = []
    for entry in selected_entries:
        source_package_path = Path(str(entry["training_package_path"])).resolve()
        payload = load_training_package_payload(source_package_path)
        source_scaffold_path = Path(str(payload["source_scaffold_path"])).resolve()
        source_scaffold = torch.load(source_scaffold_path, map_location="cpu", weights_only=False)
        if not isinstance(source_scaffold, dict):
            raise TypeError(f"Unsupported source scaffold payload type: {type(source_scaffold)!r}")
        transformed_inputs, transform_summary = apply_input_variant_to_training_package_payload(
            payload=payload,
            source_scaffold=source_scaffold,
            control_family_overrides=control_family_overrides,
        )
        record_id = str(entry.get("record_id", source_package_path.parent.parent.name))
        record_dir = packages_root / split_name / sanitize_bundle_component(record_id) / "train_targets"
        record_dir.mkdir(parents=True, exist_ok=True)
        output_package_path = record_dir / "offline_mvp_nores_vocoder_train_targets.pt"
        transformed_payload = dict(payload)
        transformed_payload["inputs"] = transformed_inputs
        transformed_payload["input_variant"] = {
            "control_family_overrides": serialize_decoder_probe_control_family_overrides(control_family_overrides),
            "transform_summary": transform_summary,
            "source_package_path": source_package_path.as_posix(),
        }
        torch.save(transformed_payload, output_package_path)
        output_entries.append(
            {
                **entry,
                "split_name": split_name,
                "training_package_path": output_package_path.as_posix(),
                "input_variant": dict(transformed_payload["input_variant"]),
            }
        )
    return output_entries


def apply_input_variant_to_training_package_payload(
    *,
    payload: dict[str, object],
    source_scaffold: dict[str, object],
    control_family_overrides: list[dict[str, object]],
) -> tuple[dict[str, torch.Tensor], dict[str, object]]:
    inputs = dict(payload["inputs"])
    periodic_features = inputs["periodic_branch_features"].detach().clone().to(torch.float32)
    noise_features = inputs["noise_branch_features"].detach().clone().to(torch.float32)
    layout = build_branch_feature_layout(source_scaffold)
    transformations: list[str] = []
    applied_targets = []
    for override in control_family_overrides:
        family = str(override["family"])
        mode = str(override["mode"])
        serialized_targets = []
        for branch_name, semantic in list(override.get("targets", [])):
            slice_info = layout[branch_name].get(semantic)
            if slice_info is None:
                continue
            start, end = slice_info
            branch_features = periodic_features if branch_name == "periodic" else noise_features
            if mode == "zero":
                branch_features[:, start:end] = 0.0
            elif mode in {"time_roll_half", "time_shuffle"}:
                branch_features[:, start:end] = apply_temporal_probe_override(
                    candidate_features=branch_features[:, start:end],
                    mode=mode,
                    semantic_key=f"{branch_name}.{semantic}",
                )
            else:
                raise ValueError(f"Unsupported dataset input variant mode: {mode!r}")
            transformations.append(f"{branch_name}.{semantic} -> {mode}[{start}:{end}]")
            serialized_targets.append(f"{branch_name}.{semantic}")
        applied_targets.append(
            {
                "family": family,
                "mode": mode,
                "targets": serialized_targets,
            }
        )
    return (
        {
            **inputs,
            "periodic_branch_features": periodic_features,
            "noise_branch_features": noise_features,
        },
        {
            "transformations": transformations,
            "control_family_overrides": applied_targets,
        },
    )


def build_reference_acoustic_temporal_alignment_case_summary(
    *,
    package_path: Path,
    max_lag_frames: int,
) -> dict[str, object]:
    payload = load_training_package_payload(package_path)
    batch = extract_training_batch(payload)
    runtime = extract_training_runtime(payload)
    source_scaffold_path = Path(str(payload["source_scaffold_path"])).resolve()
    source_scaffold = torch.load(source_scaffold_path, map_location="cpu", weights_only=False)
    if not isinstance(source_scaffold, dict):
        raise TypeError(f"Unsupported source scaffold payload type: {type(source_scaffold)!r}")
    series_map = build_scaffold_feature_series_map(
        periodic_features=batch["periodic_branch_features"],
        noise_features=batch["noise_branch_features"],
        scaffold_payload=source_scaffold,
    )
    frame_rms = build_frame_rms_sequence(
        waveform=batch["aligned_waveform"],
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        target_frame_count=int(payload["frame_count"]),
    )
    return {
        "record_id": str(package_path.parent.parent.name),
        "training_package_path": package_path.as_posix(),
        "source_scaffold_path": source_scaffold_path.as_posix(),
        "frame_count": int(payload["frame_count"]),
        "pair_summaries": build_acoustic_temporal_alignment_pair_summaries(
            series_map=series_map,
            frame_rms=frame_rms,
            max_lag_frames=int(max_lag_frames),
        ),
    }


def build_reference_acoustic_temporal_alignment_summary(
    *,
    reference_cases: list[dict[str, object]],
) -> dict[str, object]:
    pair_aggregates: dict[str, dict[str, object]] = {}
    for pair_definition in ACOUSTIC_TEMPORAL_ALIGNMENT_PAIR_DEFINITIONS:
        pair_id = str(pair_definition["pair_id"])
        rows = [
            dict(case_pair)
            for case in reference_cases
            for case_pair in list(case.get("pair_summaries", []))
            if str(case_pair.get("pair_id")) == pair_id
        ]
        scalar_distributions = {}
        for metric_key in (
            "zero_lag_corr",
            "best_corr",
            "best_lag_frames",
            "best_nonzero_corr",
            "zero_minus_best_nonzero_corr",
        ):
            scalar_distributions[metric_key] = summarize_scalar_distribution(
                [float(row.get(metric_key, 0.0)) for row in rows]
            )
        pair_aggregates[pair_id] = {
            "label": str(pair_definition["label"]),
            "description": str(pair_definition["description"]),
            "record_count": len(rows),
            "scalar_distributions": scalar_distributions,
        }
    return {
        "reference_case_count": len(reference_cases),
        "pair_aggregates": pair_aggregates,
        "cases": reference_cases,
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


def build_user_acoustic_temporal_alignment_case_summary(
    *,
    case_id: str,
    input_audio_path: Path,
    scaffold_payload: dict[str, object],
    max_audio_sec: float | None,
    max_lag_frames: int,
    reference_summary: dict[str, object],
) -> dict[str, object]:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload.get("source_runtime", {}))
    waveform, sample_rate = load_waveform(input_audio_path, max_duration_sec=max_audio_sec)
    frame_rms = build_frame_rms_sequence(
        waveform=waveform,
        frame_length=int(source_runtime["frame_length"]),
        hop_length=int(source_runtime["hop_length"]),
        target_frame_count=int(scaffold_payload["frame_count"]),
    )
    pair_summaries = build_acoustic_temporal_alignment_pair_summaries(
        series_map=build_scaffold_feature_series_map(
            periodic_features=branch_scaffold["periodic_branch_features"].to(torch.float32),
            noise_features=branch_scaffold["noise_branch_features"].to(torch.float32),
            scaffold_payload=scaffold_payload,
        ),
        frame_rms=frame_rms,
        max_lag_frames=int(max_lag_frames),
    )
    return {
        "case_id": case_id,
        "input_audio_path": input_audio_path.as_posix(),
        "sample_rate": int(sample_rate),
        "frame_count": int(scaffold_payload["frame_count"]),
        "pair_summaries": [
            annotate_acoustic_temporal_alignment_pair_against_reference(
                pair_summary=pair_summary,
                reference_summary=reference_summary,
            )
            for pair_summary in pair_summaries
        ],
    }


def build_frame_rms_sequence(
    *,
    waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    target_frame_count: int,
) -> torch.Tensor:
    frames = frame_waveform_sequence(
        waveform=waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(target_frame_count),
    )
    return frames.pow(2).mean(dim=1).sqrt().to(torch.float32)


def build_scaffold_feature_series_map(
    *,
    periodic_features: torch.Tensor,
    noise_features: torch.Tensor,
    scaffold_payload: dict[str, object],
) -> dict[str, torch.Tensor]:
    layout = build_branch_feature_layout(scaffold_payload)
    series_map = {}
    for branch_name, branch_layout in layout.items():
        branch_features = periodic_features if branch_name == "periodic" else noise_features
        for semantic, (start, end) in branch_layout.items():
            if end - start <= 0:
                continue
            series_map[f"{branch_name}.{semantic}"] = branch_features[:, start:end].to(torch.float32)
    aper = series_map.get("noise.aper")
    energy = series_map.get("noise.E_log_rms_norm")
    if isinstance(aper, torch.Tensor) and isinstance(energy, torch.Tensor):
        series_map["noise.aper_times_E_log_rms_norm"] = aper * energy
    return series_map


def build_acoustic_temporal_alignment_pair_summaries(
    *,
    series_map: dict[str, torch.Tensor],
    frame_rms: torch.Tensor,
    max_lag_frames: int,
) -> list[dict[str, object]]:
    pair_summaries = []
    for pair_definition in ACOUSTIC_TEMPORAL_ALIGNMENT_PAIR_DEFINITIONS:
        series_key = str(pair_definition["series_key"])
        source_series = series_map.get(series_key)
        if not isinstance(source_series, torch.Tensor):
            continue
        collapsed_source = source_series.to(torch.float32)
        if collapsed_source.ndim == 2 and int(collapsed_source.shape[1]) > 1:
            collapsed_source = collapsed_source.mean(dim=1)
        else:
            collapsed_source = collapsed_source.view(-1)
        lag_curve = build_lagged_correlation_curve(
            source=collapsed_source,
            target=frame_rms,
            max_lag_frames=int(max_lag_frames),
        )
        best_row = max(lag_curve, key=lambda item: float(item["corr"]))
        nonzero_rows = [row for row in lag_curve if int(row["lag_frames"]) != 0]
        best_nonzero_row = max(nonzero_rows, key=lambda item: float(item["corr"])) if nonzero_rows else best_row
        zero_row = next(row for row in lag_curve if int(row["lag_frames"]) == 0)
        pair_summaries.append(
            {
                "pair_id": str(pair_definition["pair_id"]),
                "label": str(pair_definition["label"]),
                "description": str(pair_definition["description"]),
                "series_key": series_key,
                "zero_lag_corr": float(zero_row["corr"]),
                "best_corr": float(best_row["corr"]),
                "best_lag_frames": int(best_row["lag_frames"]),
                "best_nonzero_corr": float(best_nonzero_row["corr"]),
                "zero_minus_best_nonzero_corr": round(
                    float(zero_row["corr"]) - float(best_nonzero_row["corr"]),
                    6,
                ),
                "lag_curve": lag_curve,
            }
        )
    return pair_summaries


def build_lagged_correlation_curve(
    *,
    source: torch.Tensor,
    target: torch.Tensor,
    max_lag_frames: int,
) -> list[dict[str, object]]:
    source_cpu = source.detach().cpu().to(torch.float32).view(-1)
    target_cpu = target.detach().cpu().to(torch.float32).view(-1)
    rows = []
    for lag in range(-int(max_lag_frames), int(max_lag_frames) + 1):
        if lag < 0:
            aligned_source = source_cpu[-lag:]
            aligned_target = target_cpu[: int(target_cpu.shape[0]) + lag]
        elif lag > 0:
            aligned_source = source_cpu[:-lag]
            aligned_target = target_cpu[lag:]
        else:
            aligned_source = source_cpu
            aligned_target = target_cpu
        common_length = min(int(aligned_source.shape[0]), int(aligned_target.shape[0]))
        rows.append(
            {
                "lag_frames": int(lag),
                "corr": float(
                    compute_pearson_correlation(
                        aligned_source[:common_length],
                        aligned_target[:common_length],
                    )
                ),
            }
        )
    return rows


def summarize_scalar_distribution(values: list[float]) -> dict[str, object]:
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "q01": 0.0,
            "median": 0.0,
            "q99": 0.0,
            "max": 0.0,
        }
    tensor = torch.tensor(values, dtype=torch.float32)
    quantiles = torch.quantile(tensor, torch.tensor([0.01, 0.5, 0.99], dtype=torch.float32))
    return {
        "count": int(tensor.numel()),
        "mean": round(float(tensor.mean().item()), 6),
        "std": round(float(tensor.std(unbiased=False).item()), 6),
        "min": round(float(tensor.min().item()), 6),
        "q01": round(float(quantiles[0].item()), 6),
        "median": round(float(quantiles[1].item()), 6),
        "q99": round(float(quantiles[2].item()), 6),
        "max": round(float(tensor.max().item()), 6),
    }


def annotate_acoustic_temporal_alignment_pair_against_reference(
    *,
    pair_summary: dict[str, object],
    reference_summary: dict[str, object],
) -> dict[str, object]:
    pair_id = str(pair_summary["pair_id"])
    pair_reference = dict(dict(reference_summary["pair_aggregates"]).get(pair_id, {}))
    scalar_distributions = dict(pair_reference.get("scalar_distributions", {}))
    annotated = dict(pair_summary)
    annotated["reference_comparison"] = {
        metric_key: build_scalar_reference_comparison(
            value=float(pair_summary.get(metric_key, 0.0)),
            distribution=dict(scalar_distributions.get(metric_key, {})),
        )
        for metric_key in (
            "zero_lag_corr",
            "best_corr",
            "best_lag_frames",
            "best_nonzero_corr",
            "zero_minus_best_nonzero_corr",
        )
    }
    return annotated


def build_scalar_reference_comparison(
    *,
    value: float,
    distribution: dict[str, object],
) -> dict[str, object]:
    mean = float(distribution.get("mean", 0.0))
    std = float(distribution.get("std", 0.0))
    z_score = 0.0 if std <= 1.0e-8 else (float(value) - mean) / std
    return {
        "reference_mean": round(mean, 6),
        "reference_std": round(std, 6),
        "z_score": round(float(z_score), 6),
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


def build_teacher_first_acoustic_temporal_alignment_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Acoustic Temporal Alignment Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- max_lag_frames: {summary['max_lag_frames']}",
        f"- reference_package_count: {summary['reference_package_count']}",
        f"- case_count: {summary['case_count']}",
        "",
        "## Reference Pair Aggregates",
    ]
    reference_summary = dict(summary.get("reference_summary", {}))
    pair_aggregates = dict(reference_summary.get("pair_aggregates", {}))
    for pair_id, pair_summary in pair_aggregates.items():
        scalar_distributions = dict(pair_summary.get("scalar_distributions", {}))
        lines.append(
            f"- {pair_id}: "
            f"zero_lag_mean={dict(scalar_distributions.get('zero_lag_corr', {})).get('mean', 0.0)} "
            f"best_lag_mean={dict(scalar_distributions.get('best_lag_frames', {})).get('mean', 0.0)} "
            f"zero_minus_best_nonzero_mean={dict(scalar_distributions.get('zero_minus_best_nonzero_corr', {})).get('mean', 0.0)}"
        )
    lines.extend(["", "## Cases"])
    for case in list(summary.get("cases", [])):
        lines.extend(
            [
                f"- case_id: {case.get('case_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  frame_count: {case.get('frame_count')}",
            ]
        )
        for pair_summary in list(case.get("pair_summaries", [])):
            reference_comparison = dict(pair_summary.get("reference_comparison", {}))
            zero_ref = dict(reference_comparison.get("zero_lag_corr", {}))
            gap_ref = dict(reference_comparison.get("zero_minus_best_nonzero_corr", {}))
            lines.append(
                "  "
                f"{pair_summary.get('pair_id')}: zero_lag_corr={pair_summary.get('zero_lag_corr')} "
                f"best_corr={pair_summary.get('best_corr')} "
                f"best_lag_frames={pair_summary.get('best_lag_frames')} "
                f"zero_minus_best_nonzero_corr={pair_summary.get('zero_minus_best_nonzero_corr')} "
                f"zero_lag_z={zero_ref.get('z_score', 0.0)} "
                f"gap_z={gap_ref.get('z_score', 0.0)}"
            )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_stage5_input_variant_dataset_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Input Variant Dataset",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- source_dataset_index_path: {summary['source_dataset_index_path']}",
        f"- output_dir: {summary['output_dir']}",
        f"- train_package_count: {summary['train_package_count']}",
        f"- validation_package_count: {summary['validation_package_count']}",
        f"- control_family_overrides: {json.dumps(summary['control_family_overrides'], ensure_ascii=False)}",
        "",
        "## Train Packages",
    ]
    for entry in list(summary.get("train_packages", [])):
        lines.append(
            f"- {entry.get('record_id')}: {entry.get('training_package_path')} "
            f"variant={json.dumps(entry.get('input_variant', {}), ensure_ascii=False)}"
        )
    lines.extend(["", "## Validation Packages"])
    for entry in list(summary.get("validation_packages", [])):
        lines.append(
            f"- {entry.get('record_id')}: {entry.get('training_package_path')} "
            f"variant={json.dumps(entry.get('input_variant', {}), ensure_ascii=False)}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def materialize_teacher_first_stage5_input_variant_dataset(
    *,
    dataset_index_path: Path,
    output_dir: Path,
    control_family_overrides: list[str] | None,
    max_train_packages: int | None,
    max_validation_packages: int | None,
) -> None:
    resolved_control_family_overrides = parse_decoder_probe_control_family_overrides(control_family_overrides)
    unsupported_modes = [
        str(item["mode"])
        for item in resolved_control_family_overrides
        if str(item["mode"]) not in {"zero", "time_roll_half", "time_shuffle"}
    ]
    if unsupported_modes:
        raise ValueError(
            "Dataset input variant materializer supports only zero/time_roll_half/time_shuffle overrides; "
            f"got {unsupported_modes}."
        )
    dataset_index = json.loads(dataset_index_path.resolve().read_text(encoding="utf-8"))
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    packages_root = output_dir / "packages"
    packages_root.mkdir(parents=True, exist_ok=True)

    train_entries = materialize_stage5_input_variant_split(
        package_entries=list(dataset_index.get("train_packages", [])),
        split_name="train",
        packages_root=packages_root,
        control_family_overrides=resolved_control_family_overrides,
        package_limit=max_train_packages,
    )
    validation_entries = materialize_stage5_input_variant_split(
        package_entries=list(dataset_index.get("validation_packages", [])),
        split_name="validation",
        packages_root=packages_root,
        control_family_overrides=resolved_control_family_overrides,
        package_limit=max_validation_packages,
    )
    summary = {
        "dataset_index_version": "offline_mvp_nores_vocoder_dataset_index_v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_stage5_input_variant_dataset_v1",
        "source_dataset_index_path": dataset_index_path.resolve().as_posix(),
        "output_dir": output_dir.as_posix(),
        "control_family_overrides": serialize_decoder_probe_control_family_overrides(
            resolved_control_family_overrides
        ),
        "max_train_packages": max_train_packages,
        "max_validation_packages": max_validation_packages,
        "train_package_count": len(train_entries),
        "validation_package_count": len(validation_entries),
        "train_packages": train_entries,
        "validation_packages": validation_entries,
        "notes": [
            "This command rewrites Stage5 training packages by applying probe-style input-control transforms directly to package inputs.",
            "It is intended to bridge user-line diagnostics into a reusable training-dataset candidate without modifying the baseline training loop.",
            "Only zero/time_roll_half/time_shuffle are supported here because reference-backed replacements need external reference statistics and are probe-only.",
        ],
    }
    (output_dir / "offline_mvp_nores_vocoder_dataset_index.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "offline_mvp_nores_vocoder_dataset_index.md").write_text(
        build_stage5_input_variant_dataset_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def analyze_teacher_first_vc_acoustic_temporal_alignment(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    reference_package_paths: list[Path],
    reference_package_limit: int,
    device: str,
    max_audio_sec: float | None,
    chunk_ms: float | None,
    max_lag_frames: int,
) -> None:
    if not input_audio_paths:
        raise ValueError("Acoustic temporal-alignment probe requires at least one input audio.")
    if int(max_lag_frames) < 0:
        raise ValueError("max_lag_frames must be >= 0.")
    resolved_reference_packages = resolve_reference_package_paths(
        reference_package_paths=reference_package_paths,
        reference_package_limit=reference_package_limit,
    )
    if not resolved_reference_packages:
        raise ValueError("Acoustic temporal-alignment probe requires at least one reference Stage5 training package.")

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    reference_cases = [
        build_reference_acoustic_temporal_alignment_case_summary(
            package_path=package_path,
            max_lag_frames=int(max_lag_frames),
        )
        for package_path in resolved_reference_packages
    ]
    reference_summary = build_reference_acoustic_temporal_alignment_summary(
        reference_cases=reference_cases,
    )

    case_summaries = []
    for index, input_audio_path in enumerate(input_audio_paths, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=None,
            input_audio_path=input_audio_path.resolve(),
            index=index,
        )
        case_output_dir = cases_dir / case_id
        contract_dir = case_output_dir / "teacher_contract"
        scaffold_dir = case_output_dir / "teacher_vocoder_input_scaffold"
        contract_dir.mkdir(parents=True, exist_ok=True)
        scaffold_dir.mkdir(parents=True, exist_ok=True)
        stage_state: dict[str, object] = {
            "current_stage": "teacher_source_resolution",
            "completed_stages": [],
            "skipped_stages": [],
        }
        export_teacher_contract_with_stage_tracking(
            input_audio_path=input_audio_path,
            output_dir=contract_dir,
            route_handoff_path=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
            checkpoint_path=None,
            calibration_asset_path=DEFAULT_CALIBRATION_ASSET_PATH,
            device=str(device),
            max_audio_sec=max_audio_sec,
            chunk_samples=None,
            chunk_ms=chunk_ms,
            verify_against_full_pass=False,
            stage_state=stage_state,
            conditioning=None,
        )
        build_offline_mvp_teacher_vocoder_input_scaffold(
            contract_path=contract_dir / "teacher_downstream_control_contract.pt",
            output_dir=scaffold_dir,
        )
        scaffold_payload = torch.load(
            scaffold_dir / "teacher_vocoder_input_scaffold.pt",
            map_location="cpu",
            weights_only=False,
        )
        if not isinstance(scaffold_payload, dict):
            raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")
        case_summaries.append(
            build_user_acoustic_temporal_alignment_case_summary(
                case_id=case_id,
                input_audio_path=input_audio_path.resolve(),
                scaffold_payload=scaffold_payload,
                max_audio_sec=max_audio_sec,
                max_lag_frames=int(max_lag_frames),
                reference_summary=reference_summary,
            )
        )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_acoustic_temporal_alignment_probe_v1",
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "chunk_ms": chunk_ms,
        "max_lag_frames": int(max_lag_frames),
        "reference_package_count": len(resolved_reference_packages),
        "reference_packages": [path.as_posix() for path in resolved_reference_packages],
        "reference_summary": reference_summary,
        "case_count": len(case_summaries),
        "cases": case_summaries,
        "notes": [
            "This probe compares user-line source-derived acoustic-state controls against actual waveform frame RMS, then checks whether the lag-correlation shape looks in-distribution relative to Stage5 training packages.",
            "It does not decode waveform audio and therefore isolates scaffold/control timing behavior from checkpoint decode behavior.",
            "If user-line zero-lag alignment stays near the reference package range, the remaining failure is more likely checkpoint consumption or downstream amplification than teacher/scaffold over-alignment alone.",
        ],
    }
    (output_dir / "teacher_first_vc_acoustic_temporal_alignment_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_first_vc_acoustic_temporal_alignment_probe.md").write_text(
        build_teacher_first_acoustic_temporal_alignment_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def analyze_teacher_first_vc_decoder_behavior(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    vocoder_checkpoint_path: Path | None,
    vocoder_checkpoint_selection_path: Path | None,
    selection_target: str,
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
        checkpoint_path=vocoder_checkpoint_path,
        checkpoint_selection_path=vocoder_checkpoint_selection_path,
        selection_target=selection_target,
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
            selection_target=selection_target,
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


def analyze_teacher_first_vc_waveform_handoff(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    vocoder_checkpoint_path: Path | None,
    vocoder_checkpoint_selection_path: Path | None,
    selection_target: str,
    reference_package_paths: list[Path],
    reference_package_limit: int,
    device: str,
    max_audio_sec: float | None,
    chunk_ms: float | None,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    control_family_overrides: list[str] | None = None,
) -> None:
    if not input_audio_paths:
        raise ValueError("Waveform handoff probe requires at least one input audio.")

    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=vocoder_checkpoint_path,
        checkpoint_selection_path=vocoder_checkpoint_selection_path,
        selection_target=selection_target,
    )
    checkpoint_payload = load_vocoder_checkpoint_payload(resolved_checkpoint_path)
    resolved_device = resolve_runtime_device(device)
    resolved_control_family_overrides = parse_decoder_probe_control_family_overrides(control_family_overrides)
    requires_reference_summary = any(
        str(item.get("mode")).startswith("reference_") for item in resolved_control_family_overrides
    )
    resolved_reference_packages: list[Path] = []
    reference_feature_summary: dict[str, object] | None = None
    if requires_reference_summary:
        resolved_reference_packages = resolve_reference_package_paths(
            reference_package_paths=reference_package_paths,
            reference_package_limit=reference_package_limit,
        )
        if not resolved_reference_packages:
            raise ValueError(
                "Waveform handoff probe requires at least one reference Stage5 training package when "
                "using reference_mean control-family overrides."
            )
        reference_feature_summary = build_reference_distribution_summary(resolved_reference_packages)

    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

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
            selection_target=selection_target,
            chunk_samples=None,
            chunk_ms=chunk_ms,
            device=str(device),
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=False,
            save_intermediates=True,
            use_predicted_activity_gate=True,
            predicted_activity_gate_floor=float(predicted_activity_gate_floor),
            predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
            predicted_activity_gate_apply_mode="post_ola_envelope",
        )
        demo_summary = load_teacher_first_vc_demo_summary(case_output_dir / "teacher_first_vc_demo.json")
        scaffold_payload = torch.load(
            case_output_dir / "teacher_vocoder_input_scaffold" / "teacher_vocoder_input_scaffold.pt",
            map_location="cpu",
            weights_only=False,
        )
        if not isinstance(scaffold_payload, dict):
            raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")
        if reference_feature_summary is None:
            empty_reference_feature_summary = {
                "periodic": {"per_dim_mean": [], "per_dim_q01": [], "per_dim_q99": []},
                "noise": {"per_dim_mean": [], "per_dim_q01": [], "per_dim_q99": []},
            }
            normalized_scaffold_payload, normalization_summary = normalize_scaffold_payload_for_decoder_probe(
                scaffold_payload=scaffold_payload,
                reference_feature_summary=empty_reference_feature_summary,
                normalization_strategy="none",
                control_family_overrides=resolved_control_family_overrides,
            )
        else:
            normalized_scaffold_payload, normalization_summary = normalize_scaffold_payload_for_decoder_probe(
                scaffold_payload=scaffold_payload,
                reference_feature_summary=reference_feature_summary,
                normalization_strategy="none",
                control_family_overrides=resolved_control_family_overrides,
            )
        case_summaries.append(
            build_waveform_handoff_case_summary(
                case_id=case_id,
                demo_summary=demo_summary,
                scaffold_payload=normalized_scaffold_payload,
                checkpoint_payload=checkpoint_payload,
                device=resolved_device,
                predicted_activity_gate_floor=float(predicted_activity_gate_floor),
                predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                case_output_dir=case_output_dir,
                normalization_summary=normalization_summary,
            )
        )

    handoff_stage_aggregates = build_handoff_stage_aggregates(
        [{"stage_metrics": dict(case["stage_metrics"])} for case in case_summaries]
    )
    route_aggregates = build_teacher_first_waveform_handoff_route_aggregates(case_summaries)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_waveform_handoff_probe_v1",
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "chunk_ms": chunk_ms,
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "selected_checkpoint_summary": selection_summary,
        "waveform_decode": {
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "route_labels": [str(route["label"]) for route in HANDOFF_DECODE_ROUTES],
            "control_family_overrides": serialize_decoder_probe_control_family_overrides(
                resolved_control_family_overrides
            ),
        },
        "reference_package_count": len(resolved_reference_packages),
        "reference_packages": [path.as_posix() for path in resolved_reference_packages],
        "reference_feature_summary": reference_feature_summary,
        "case_count": len(case_summaries),
        "handoff_stage_aggregates": handoff_stage_aggregates,
        "route_aggregates": route_aggregates,
        "diagnosis": diagnose_teacher_first_waveform_handoff(
            handoff_stage_aggregates=handoff_stage_aggregates,
            route_aggregates=route_aggregates,
        ),
        "cases": case_summaries,
        "notes": [
            "This probe keeps the current teacher-first runtime path intact, then replays the same saved scaffold through one Stage5 forward pass and exports intermediate waveform handoff assets.",
            "decoder_hidden is summarized numerically and saved in tensors only because it is not waveform-valued audio.",
            "waveform_frame_logits_stitched.wav and waveform_frames_stitched.wav let us hear the pre-OLA stage before overlap-add and gate semantics.",
            "decoded_no_gate, decoded_pre_ola_gate, and decoded_post_ola_gate isolate whether the failure is already present before predicted activity gating or is materially amplified by the export-side gate route.",
            "control_family_overrides are inference-only probe interventions; they do not modify the saved teacher contract or default runtime path.",
            "reference_mean control-family overrides reuse Stage5 training-package feature means as a probe-time replacement source.",
        ],
    }
    (output_dir / "teacher_first_vc_waveform_handoff_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_first_vc_waveform_handoff_probe.md").write_text(
        build_teacher_first_waveform_handoff_probe_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def analyze_teacher_first_vc_waveform_decoder_structure(
    *,
    input_audio_paths: list[Path],
    output_dir: Path,
    vocoder_checkpoint_path: Path | None,
    vocoder_checkpoint_selection_path: Path | None,
    selection_target: str,
    device: str,
    max_audio_sec: float | None,
    chunk_ms: float,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> None:
    if not input_audio_paths:
        raise ValueError("At least one --input-audio path is required for the teacher-first waveform decoder structure probe.")
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    resolved_device = torch.device(device)
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=vocoder_checkpoint_path,
        checkpoint_selection_path=vocoder_checkpoint_selection_path,
        selection_target=selection_target,
    )
    checkpoint_payload = torch.load(
        resolved_checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    case_summaries: list[dict[str, object]] = []
    for case_index, input_audio_path in enumerate(input_audio_paths, start=1):
        case_id = build_review_bundle_case_id(
            raw_case_id=None,
            input_audio_path=input_audio_path.resolve(),
            index=case_index,
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
            selection_target=selection_target,
            chunk_samples=None,
            chunk_ms=chunk_ms,
            device=str(device),
            max_audio_sec=max_audio_sec,
            verify_against_full_pass=False,
            save_intermediates=True,
            use_predicted_activity_gate=bool(use_predicted_activity_gate),
            predicted_activity_gate_floor=float(predicted_activity_gate_floor),
            predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
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
        case_summaries.append(
            build_waveform_decoder_structure_case_summary(
                case_id=case_id,
                demo_summary=demo_summary,
                scaffold_payload=scaffold_payload,
                checkpoint_payload=checkpoint_payload,
                device=resolved_device,
                use_predicted_activity_gate=bool(use_predicted_activity_gate),
                predicted_activity_gate_floor=float(predicted_activity_gate_floor),
                predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                predicted_activity_gate_apply_mode=resolved_apply_mode,
                case_output_dir=case_output_dir,
            )
        )

    aggregate_rows = build_variant_aggregates(case_summaries)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_waveform_decoder_structure_probe_v1",
        "output_dir": output_dir.as_posix(),
        "device": str(device),
        "max_audio_sec": max_audio_sec,
        "chunk_ms": chunk_ms,
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "selected_checkpoint_summary": selection_summary,
        "decode_runtime": {
            "device": str(resolved_device),
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
        },
        "case_count": len(case_summaries),
        "probe_variants": [
            {
                "label": str(item["label"]),
                "description": str(item["description"]),
                "transforms": [f"{stage}={mode}" for stage, mode in list(item["transforms"])],
            }
            for item in STRUCTURE_PROBE_VARIANTS
        ],
        "variant_impact_ranking": build_variant_impact_ranking(aggregate_rows),
        "baseline_decoder_collapse_summary": build_baseline_decoder_collapse_summary(aggregate_rows),
        "variant_aggregates": aggregate_rows,
        "cases": case_summaries,
        "notes": [
            "This probe reuses the teacher-first user-line scaffold, then applies the same hidden-state bypass transforms used by the Stage5 waveform decoder structure probe.",
            "baseline is decoded from the teacher-first user-line scaffold with the current checkpoint and the requested predicted-activity gate setting.",
            "fused_hidden_from_periodic_hidden, fused_hidden_from_noise_hidden, and fused_hidden_from_branch_mean bypass fusion and test whether the current decoder route can still respond to branch-side hidden dynamics on user-line inputs.",
            "If branch-side bypasses reduce decoded template metrics sharply while baseline remains near-fixed-template, the first collapse is still upstream of the decoder, even on user-line.",
        ],
    }
    (output_dir / "teacher_first_vc_waveform_decoder_structure_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_first_vc_waveform_decoder_structure_probe.md").write_text(
        build_teacher_first_waveform_decoder_structure_probe_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_waveform_handoff_case_summary(
    *,
    case_id: str,
    demo_summary: dict[str, object],
    scaffold_payload: dict[str, object],
    checkpoint_payload: dict[str, object],
    device: torch.device,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    case_output_dir: Path,
    normalization_summary: dict[str, object] | None = None,
) -> dict[str, object]:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload["source_runtime"])
    model = build_vocoder_model_from_runtime_dims(
        checkpoint_payload=checkpoint_payload,
        periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
        frame_length=int(source_runtime["frame_length"]),
    ).to(device)
    model.eval()
    with torch.no_grad():
        outputs = model(
            periodic_branch_features=branch_scaffold["periodic_branch_features"].to(device=device, dtype=torch.float32),
            noise_branch_features=branch_scaffold["noise_branch_features"].to(device=device, dtype=torch.float32),
        )

    periodic_gate = outputs["periodic_gate"].detach().cpu().to(torch.float32)
    noise_gate = outputs["noise_gate"].detach().cpu().to(torch.float32)
    predicted_activity = torch.maximum(periodic_gate, noise_gate).detach().cpu().to(torch.float32)
    if predicted_activity.ndim == 2 and int(predicted_activity.shape[-1]) == 1:
        predicted_activity = predicted_activity.squeeze(-1)
    periodic_hidden = outputs["periodic_hidden"].detach().cpu().to(torch.float32)
    noise_hidden = outputs["noise_hidden"].detach().cpu().to(torch.float32)
    branch_mean_hidden = outputs["branch_mean_hidden"].detach().cpu().to(torch.float32)
    fused_hidden = outputs["fused_hidden"].detach().cpu().to(torch.float32)
    decoder_hidden = outputs["decoder_hidden"].detach().cpu().to(torch.float32)
    waveform_frame_logits = outputs["waveform_frame_logits"].detach().cpu().to(torch.float32)
    waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
    stage_metrics = summarize_handoff_stage_metrics(
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        branch_mean_hidden=branch_mean_hidden,
        fused_hidden=fused_hidden,
        decoder_hidden=decoder_hidden,
        waveform_frame_logits=waveform_frame_logits,
        waveform_frames=waveform_frames,
    )

    handoff_dir = case_output_dir / "waveform_handoff_probe"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    logits_audio_path = handoff_dir / "waveform_frame_logits_stitched.wav"
    frames_audio_path = handoff_dir / "waveform_frames_stitched.wav"
    write_waveform_int16(
        logits_audio_path,
        flatten_frame_sequence_for_audio(waveform_frame_logits),
        sample_rate=int(source_runtime["sample_rate"]),
    )
    write_waveform_int16(
        frames_audio_path,
        flatten_frame_sequence_for_audio(waveform_frames),
        sample_rate=int(source_runtime["sample_rate"]),
    )

    torch.save(
        {
            "periodic_hidden": periodic_hidden,
            "noise_hidden": noise_hidden,
            "branch_mean_hidden": branch_mean_hidden,
            "fused_hidden": fused_hidden,
            "decoder_hidden": decoder_hidden,
            "waveform_frame_logits": waveform_frame_logits,
            "waveform_frames": waveform_frames,
            "periodic_gate": periodic_gate,
            "noise_gate": noise_gate,
            "predicted_activity": predicted_activity,
        },
        handoff_dir / "teacher_first_vc_waveform_handoff_tensors.pt",
    )

    route_rows = []
    for route in HANDOFF_DECODE_ROUTES:
        route_waveform = reconstruct_waveform_from_frames(
            waveform_frames=waveform_frames,
            frame_length=int(source_runtime["frame_length"]),
            hop_length=int(source_runtime["hop_length"]),
            frame_gains=predicted_activity if bool(route["use_predicted_activity_gate"]) else None,
            frame_gain_floor=float(predicted_activity_gate_floor),
            frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
            frame_gain_apply_mode=str(route["predicted_activity_gate_apply_mode"]),
        ).detach().cpu().to(torch.float32)
        route_audio_path = handoff_dir / f"{sanitize_bundle_component(str(route['label']))}.wav"
        write_waveform_int16(
            route_audio_path,
            route_waveform,
            sample_rate=int(source_runtime["sample_rate"]),
        )
        route_rows.append(
            {
                "label": str(route["label"]),
                "description": str(route["description"]),
                "audio_path": route_audio_path.as_posix(),
                "metrics": summarize_teacher_first_handoff_route_metrics(
                    waveform=route_waveform,
                    sample_rate=int(source_runtime["sample_rate"]),
                    frame_length=int(source_runtime["frame_length"]),
                    hop_length=int(source_runtime["hop_length"]),
                    predicted_activity=predicted_activity,
                ),
            }
        )

    return {
        "case_id": case_id,
        "input_audio_path": demo_summary.get("input_audio_path"),
        "main_decoded_audio_path": demo_summary.get("decoded_audio_path"),
        "decoded_audio_sec": demo_summary.get("decoded_audio_sec"),
        "decoded_waveform_rms": demo_summary.get("decoded_waveform_rms"),
        "normalization": normalization_summary or {
            "strategy": "none",
            "transformations": [],
            "control_family_overrides": [],
        },
        "handoff_dir": handoff_dir.as_posix(),
        "handoff_tensor_path": (handoff_dir / "teacher_first_vc_waveform_handoff_tensors.pt").as_posix(),
        "stage_audio_exports": {
            "waveform_frame_logits_stitched_audio_path": logits_audio_path.as_posix(),
            "waveform_frames_stitched_audio_path": frames_audio_path.as_posix(),
        },
        "stage_metrics": stage_metrics,
        "routes": route_rows,
    }


def build_waveform_decoder_structure_case_summary(
    *,
    case_id: str,
    demo_summary: dict[str, object],
    scaffold_payload: dict[str, object],
    checkpoint_payload: dict[str, object],
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    case_output_dir: Path,
) -> dict[str, object]:
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])
    source_runtime = dict(scaffold_payload["source_runtime"])
    model = build_vocoder_model_from_runtime_dims(
        checkpoint_payload=checkpoint_payload,
        periodic_input_dim=int(branch_scaffold["periodic_branch_features"].shape[-1]),
        noise_input_dim=int(branch_scaffold["noise_branch_features"].shape[-1]),
        frame_length=int(source_runtime["frame_length"]),
    ).to(device)
    model.eval()

    periodic_branch_features = branch_scaffold["periodic_branch_features"].to(device=device, dtype=torch.float32)
    noise_branch_features = branch_scaffold["noise_branch_features"].to(device=device, dtype=torch.float32)
    structure_dir = case_output_dir / "waveform_decoder_structure_probe"
    structure_dir.mkdir(parents=True, exist_ok=True)

    variant_rows: list[dict[str, object]] = []
    baseline_waveform = None
    baseline_scalar_metrics = None
    tensors_to_save: dict[str, dict[str, torch.Tensor]] = {}
    with torch.no_grad():
        base_periodic_hidden = model.periodic_encoder(periodic_branch_features)
        base_noise_hidden = model.noise_encoder(noise_branch_features)
        for variant in STRUCTURE_PROBE_VARIANTS:
            transforms = list(variant["transforms"])
            transform_notes: list[str] = []
            periodic_hidden = apply_structure_transform(
                tensor=base_periodic_hidden,
                transforms=transforms,
                stage_name="periodic_hidden",
                transform_notes=transform_notes,
            )
            noise_hidden = apply_structure_transform(
                tensor=base_noise_hidden,
                transforms=transforms,
                stage_name="noise_hidden",
                transform_notes=transform_notes,
            )
            fused_hidden = compute_fused_hidden_for_probe(
                model=model,
                periodic_hidden=periodic_hidden,
                noise_hidden=noise_hidden,
            )
            fused_hidden = apply_structure_transform(
                tensor=fused_hidden,
                transforms=transforms,
                stage_name="fused_hidden",
                transform_notes=transform_notes,
                periodic_hidden=periodic_hidden,
                noise_hidden=noise_hidden,
            )
            outputs = compute_teacher_first_waveform_structure_outputs(
                model=model,
                periodic_hidden=periodic_hidden,
                noise_hidden=noise_hidden,
                fused_hidden=fused_hidden,
            )
            branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
            periodic_gate = torch.sigmoid(model.periodic_gate(periodic_hidden))
            noise_gate = torch.sigmoid(model.noise_gate(noise_hidden))
            predicted_activity = torch.maximum(periodic_gate, noise_gate)
            if predicted_activity.ndim == 2 and int(predicted_activity.shape[-1]) == 1:
                predicted_activity = predicted_activity.squeeze(-1)
            decoded_waveform = reconstruct_waveform_from_frames(
                waveform_frames=outputs["waveform_frames"].detach().cpu().to(torch.float32),
                frame_length=int(source_runtime["frame_length"]),
                hop_length=int(source_runtime["hop_length"]),
                frame_gains=predicted_activity.detach().cpu().to(torch.float32)
                if bool(use_predicted_activity_gate)
                else None,
                frame_gain_floor=float(predicted_activity_gate_floor),
                frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                frame_gain_apply_mode=str(predicted_activity_gate_apply_mode),
            ).detach().cpu().to(torch.float32)
            stage_metrics = summarize_handoff_stage_metrics(
                periodic_hidden=periodic_hidden.detach().cpu().to(torch.float32),
                noise_hidden=noise_hidden.detach().cpu().to(torch.float32),
                branch_mean_hidden=branch_mean_hidden.detach().cpu().to(torch.float32),
                fused_hidden=fused_hidden.detach().cpu().to(torch.float32),
                decoder_hidden=outputs["decoder_hidden"].detach().cpu().to(torch.float32),
                waveform_frame_logits=outputs["waveform_frame_logits"].detach().cpu().to(torch.float32),
                waveform_frames=outputs["waveform_frames"].detach().cpu().to(torch.float32),
            )
            scalar_metrics = summarize_teacher_first_structure_scalar_metrics(
                stage_metrics=stage_metrics,
                decoded_waveform=decoded_waveform,
                sample_rate=int(source_runtime["sample_rate"]),
                frame_length=int(source_runtime["frame_length"]),
                hop_length=int(source_runtime["hop_length"]),
                predicted_activity=predicted_activity.detach().cpu().to(torch.float32),
            )
            label = str(variant["label"])
            audio_path = structure_dir / f"{sanitize_bundle_component(label)}.wav"
            write_waveform_int16(
                audio_path,
                decoded_waveform,
                sample_rate=int(source_runtime["sample_rate"]),
            )
            variant_row = {
                "label": label,
                "description": str(variant["description"]),
                "transform_notes": transform_notes,
                "audio_path": audio_path.as_posix(),
                "scalar_metrics": scalar_metrics,
                "stage_metrics": stage_metrics,
                "_decoded_waveform": decoded_waveform,
            }
            tensors_to_save[label] = {
                "periodic_hidden": periodic_hidden.detach().cpu().to(torch.float32),
                "noise_hidden": noise_hidden.detach().cpu().to(torch.float32),
                "branch_mean_hidden": branch_mean_hidden.detach().cpu().to(torch.float32),
                "fused_hidden": fused_hidden.detach().cpu().to(torch.float32),
                "decoder_hidden": outputs["decoder_hidden"].detach().cpu().to(torch.float32),
                "waveform_frame_logits": outputs["waveform_frame_logits"].detach().cpu().to(torch.float32),
                "waveform_frames": outputs["waveform_frames"].detach().cpu().to(torch.float32),
                "predicted_activity": predicted_activity.detach().cpu().to(torch.float32),
            }
            if label == "baseline":
                baseline_waveform = decoded_waveform
                baseline_scalar_metrics = scalar_metrics
            variant_rows.append(variant_row)

    if baseline_waveform is None or baseline_scalar_metrics is None:
        raise RuntimeError("Teacher-first waveform decoder structure probe failed to produce a baseline variant.")

    for variant_row in variant_rows:
        variant_row["delta_vs_baseline"] = summarize_probe_delta_vs_baseline(
            candidate_metrics=dict(variant_row["scalar_metrics"]),
            baseline_metrics=baseline_scalar_metrics,
            candidate_waveform=variant_row.get("_decoded_waveform"),
            baseline_waveform=baseline_waveform,
        )
        variant_row["stage_delta_vs_baseline"] = {}
        variant_row.pop("_decoded_waveform", None)

    torch.save(
        tensors_to_save,
        structure_dir / "teacher_first_vc_waveform_decoder_structure_tensors.pt",
    )
    return {
        "record_id": case_id,
        "input_audio_path": demo_summary.get("input_audio_path"),
        "main_decoded_audio_path": demo_summary.get("decoded_audio_path"),
        "structure_dir": structure_dir.as_posix(),
        "training_package_path": None,
        "variants": variant_rows,
    }


def compute_teacher_first_waveform_structure_outputs(
    *,
    model: NoResidualSourceFilterVocoderScaffold,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
) -> dict[str, torch.Tensor]:
    waveform_decoder_mode = str(getattr(model, "waveform_decoder_mode", "fused_single"))
    if waveform_decoder_mode != "fused_single":
        raise ValueError(f"Unsupported waveform_decoder_mode in teacher-first structure probe: {waveform_decoder_mode!r}")
    waveform_decoder = getattr(model, "waveform_decoder", None)
    if waveform_decoder is None:
        raise RuntimeError("waveform_decoder is not initialized for fused_single teacher-first structure probe.")
    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    decoder_hidden = fused_hidden
    if bool(getattr(model, "use_decoder_branch_condition_adapter", False)):
        decoder_branch_condition_adapter = getattr(model, "decoder_branch_condition_adapter", None)
        decoder_branch_condition_gate = getattr(model, "decoder_branch_condition_gate", None)
        decoder_fused_condition_proj = getattr(model, "decoder_fused_condition_proj", None)
        if (
            decoder_branch_condition_adapter is None
            or decoder_branch_condition_gate is None
            or decoder_fused_condition_proj is None
        ):
            raise RuntimeError("Decoder branch-condition adapter modules are not initialized for teacher-first structure probe.")
        branch_condition_features = torch.cat(
            [
                fused_hidden,
                branch_mean_hidden,
                fused_hidden - branch_mean_hidden,
            ],
            dim=-1,
        )
        branch_condition_context = decoder_branch_condition_adapter(branch_condition_features)
        branch_condition_gate = torch.sigmoid(decoder_branch_condition_gate(branch_condition_context))
        fused_condition = torch.tanh(decoder_fused_condition_proj(branch_condition_context))
        decoder_hidden = decoder_hidden + branch_condition_gate * fused_condition
    waveform_frame_logits = waveform_decoder(decoder_hidden)
    if bool(getattr(model, "use_residual_shape_branch_condition_adapter", False)):
        residual_shape_branch_condition_adapter = getattr(model, "residual_shape_branch_condition_adapter", None)
        residual_shape_branch_condition_gate_head = getattr(model, "residual_shape_branch_condition_gate", None)
        residual_shape_branch_condition_proj = getattr(model, "residual_shape_branch_condition_proj", None)
        if (
            residual_shape_branch_condition_adapter is None
            or residual_shape_branch_condition_gate_head is None
            or residual_shape_branch_condition_proj is None
        ):
            raise RuntimeError(
                "Residual-shape branch-condition adapter modules are not initialized for teacher-first structure probe."
            )
        residual_shape_branch_condition_features = torch.cat(
            [
                fused_hidden,
                branch_mean_hidden,
                fused_hidden - branch_mean_hidden,
            ],
            dim=-1,
        )
        residual_shape_branch_condition_context = residual_shape_branch_condition_adapter(
            residual_shape_branch_condition_features
        )
        residual_shape_branch_condition_gate = torch.sigmoid(
            residual_shape_branch_condition_gate_head(residual_shape_branch_condition_context)
        )
        residual_shape_branch_condition_delta = resolve_residual_shape_branch_condition_delta(
            delta=torch.tanh(
                residual_shape_branch_condition_proj(residual_shape_branch_condition_context)
            ),
            mode=str(getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")),
        )
        waveform_frame_logits = (
            waveform_frame_logits
            + float(getattr(model, "residual_shape_branch_condition_scale", 1.0))
            * residual_shape_branch_condition_gate
            * residual_shape_branch_condition_delta
        )
    return {
        "decoder_hidden": decoder_hidden,
        "waveform_frame_logits": waveform_frame_logits,
        "waveform_frames": torch.tanh(waveform_frame_logits),
    }


def summarize_teacher_first_structure_scalar_metrics(
    *,
    stage_metrics: dict[str, float],
    decoded_waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    predicted_activity: torch.Tensor,
) -> dict[str, float]:
    route_metrics = summarize_teacher_first_handoff_route_metrics(
        waveform=decoded_waveform,
        sample_rate=int(sample_rate),
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        predicted_activity=predicted_activity,
    )
    scalar_metrics = dict(stage_metrics)
    scalar_metrics.update(
        {
            "decoded_waveform_rms": float(route_metrics["waveform_rms"]),
            "decoded_abs_mean": float(route_metrics["waveform_abs_mean"]),
            "decoded_peak_abs": float(route_metrics["waveform_peak_abs"]),
            "decoded_zero_crossing_rate": float(route_metrics["waveform_zero_crossing_rate"]),
            "decoded_frames_template_cosine_mean": float(route_metrics["decoded_frame_template_cosine_mean"]),
            "decoded_frames_adjacent_cosine_mean": float(route_metrics["decoded_frame_adjacent_cosine_mean"]),
            "decoded_frames_frame_rms_cv": float(route_metrics["decoded_frame_rms_cv"]),
            "predicted_activity_to_decoded_frame_rms_corr": float(
                route_metrics["predicted_activity_to_decoded_frame_rms_corr"]
            ),
            "decoded_spectral_centroid_hz": float(route_metrics["decoded_spectral_centroid_hz"]),
            "decoded_spectral_bandwidth_hz": float(route_metrics["decoded_spectral_bandwidth_hz"]),
            "decoded_spectral_rolloff95_hz": float(route_metrics["decoded_spectral_rolloff95_hz"]),
            "decoded_spectral_high_band_energy_ratio": float(
                route_metrics["decoded_spectral_high_band_energy_ratio"]
            ),
            "predicted_activity_mean": round(float(predicted_activity.mean().item()), 6),
            "predicted_activity_std": round(float(predicted_activity.std(unbiased=False).item()), 6),
        }
    )
    scalar_metrics["fused_to_waveform_template_cosine_gap"] = round(
        float(scalar_metrics["waveform_frames_template_cosine_mean"])
        - float(scalar_metrics["fused_hidden_template_cosine_mean"]),
        6,
    )
    scalar_metrics["fused_to_waveform_adjacent_cosine_gap"] = round(
        float(scalar_metrics["waveform_frames_adjacent_cosine_mean"])
        - float(scalar_metrics["fused_hidden_adjacent_cosine_mean"]),
        6,
    )
    scalar_metrics["waveform_to_decoded_template_cosine_gap"] = round(
        float(scalar_metrics["decoded_frames_template_cosine_mean"])
        - float(scalar_metrics["waveform_frames_template_cosine_mean"]),
        6,
    )
    scalar_metrics["waveform_to_decoded_adjacent_cosine_gap"] = round(
        float(scalar_metrics["decoded_frames_adjacent_cosine_mean"])
        - float(scalar_metrics["waveform_frames_adjacent_cosine_mean"]),
        6,
    )
    return scalar_metrics


def flatten_frame_sequence_for_audio(frames: torch.Tensor) -> torch.Tensor:
    frames_cpu = frames.detach().cpu().to(torch.float32)
    if frames_cpu.ndim != 2:
        raise ValueError(f"Expected frames shape [frames, samples], got {tuple(frames_cpu.shape)}")
    return frames_cpu.reshape(-1)


def summarize_teacher_first_handoff_route_metrics(
    *,
    waveform: torch.Tensor,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
    predicted_activity: torch.Tensor,
) -> dict[str, float]:
    waveform_cpu = waveform.detach().cpu().to(torch.float32).view(-1)
    spectral = compute_waveform_spectral_summary(waveform_cpu, int(sample_rate))
    frames = frame_waveform_sequence(
        waveform=waveform_cpu,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(predicted_activity.shape[0]),
    )
    frame_metrics = summarize_frame_sequence_metrics(frames)
    frame_rms = frames.pow(2).mean(dim=1).sqrt()
    return {
        "waveform_rms": round(float(waveform_cpu.pow(2).mean().sqrt().item()), 6),
        "waveform_abs_mean": round(float(waveform_cpu.abs().mean().item()), 6),
        "waveform_peak_abs": round(float(waveform_cpu.abs().max().item()), 6),
        "waveform_zero_crossing_rate": round(float(compute_zero_crossing_rate(waveform_cpu)), 6),
        "decoded_frame_template_cosine_mean": float(frame_metrics["template_cosine_mean"]),
        "decoded_frame_adjacent_cosine_mean": float(frame_metrics["adjacent_cosine_mean"]),
        "decoded_frame_rms_cv": float(frame_metrics["frame_rms_cv"]),
        "predicted_activity_to_decoded_frame_rms_corr": float(
            compute_pearson_correlation(predicted_activity.view(-1), frame_rms)
        ),
        "decoded_spectral_centroid_hz": round(float(spectral["centroid_hz"]), 6),
        "decoded_spectral_bandwidth_hz": round(float(spectral["bandwidth_hz"]), 6),
        "decoded_spectral_rolloff95_hz": round(float(spectral["rolloff95_hz"]), 6),
        "decoded_spectral_high_band_energy_ratio": round(float(spectral["high_band_energy_ratio"]), 6),
    }


def build_teacher_first_waveform_handoff_route_aggregates(
    case_summaries: list[dict[str, object]],
) -> list[dict[str, object]]:
    route_map: dict[str, dict[str, object]] = {}
    for case in case_summaries:
        for route in list(case.get("routes", [])):
            label = str(route["label"])
            bucket = route_map.setdefault(
                label,
                {
                    "label": label,
                    "description": str(route["description"]),
                    "record_count": 0,
                    "metrics": {},
                },
            )
            bucket["record_count"] = int(bucket["record_count"]) + 1
            for key, value in dict(route.get("metrics", {})).items():
                bucket["metrics"].setdefault(str(key), []).append(float(value))
    order = {str(route["label"]): index for index, route in enumerate(HANDOFF_DECODE_ROUTES)}
    aggregates = []
    for label, payload in route_map.items():
        aggregates.append(
            {
                "label": label,
                "description": str(payload["description"]),
                "record_count": int(payload["record_count"]),
                "metrics": {
                    key: summarize_scalar_values(values)
                    for key, values in sorted(dict(payload["metrics"]).items())
                },
            }
        )
    return sorted(aggregates, key=lambda item: order.get(str(item["label"]), 999))


def diagnose_teacher_first_waveform_handoff(
    *,
    handoff_stage_aggregates: dict[str, dict[str, float]],
    route_aggregates: list[dict[str, object]],
) -> dict[str, object]:
    route_map = {str(item["label"]): item for item in route_aggregates}
    no_gate_metrics = dict(dict(route_map.get("decoded_no_gate", {})).get("metrics", {}))
    pre_gate_metrics = dict(dict(route_map.get("decoded_pre_ola_gate", {})).get("metrics", {}))
    post_gate_metrics = dict(dict(route_map.get("decoded_post_ola_gate", {})).get("metrics", {}))

    def mean_metric(bucket: dict[str, object], key: str) -> float:
        return float(dict(bucket.get(key, {})).get("mean", 0.0))

    logits_template = float(
        dict(handoff_stage_aggregates.get("waveform_frame_logits_template_cosine_mean", {})).get("mean", 0.0)
    )
    frames_template = float(
        dict(handoff_stage_aggregates.get("waveform_frames_template_cosine_mean", {})).get("mean", 0.0)
    )
    logits_adjacent = float(
        dict(handoff_stage_aggregates.get("waveform_frame_logits_adjacent_cosine_mean", {})).get("mean", 0.0)
    )
    frames_adjacent = float(
        dict(handoff_stage_aggregates.get("waveform_frames_adjacent_cosine_mean", {})).get("mean", 0.0)
    )
    return {
        "logits_to_frames_template_cosine_gap": round(frames_template - logits_template, 6),
        "logits_to_frames_adjacent_cosine_gap": round(frames_adjacent - logits_adjacent, 6),
        "pre_ola_vs_no_gate_template_delta": round(
            mean_metric(pre_gate_metrics, "decoded_frame_template_cosine_mean")
            - mean_metric(no_gate_metrics, "decoded_frame_template_cosine_mean"),
            6,
        ),
        "post_ola_vs_no_gate_template_delta": round(
            mean_metric(post_gate_metrics, "decoded_frame_template_cosine_mean")
            - mean_metric(no_gate_metrics, "decoded_frame_template_cosine_mean"),
            6,
        ),
        "post_ola_vs_no_gate_high_band_delta": round(
            mean_metric(post_gate_metrics, "decoded_spectral_high_band_energy_ratio")
            - mean_metric(no_gate_metrics, "decoded_spectral_high_band_energy_ratio"),
            6,
        ),
        "post_ola_vs_no_gate_centroid_hz_delta": round(
            mean_metric(post_gate_metrics, "decoded_spectral_centroid_hz")
            - mean_metric(no_gate_metrics, "decoded_spectral_centroid_hz"),
            6,
        ),
        "likely_failure_already_present_by_frames_before_gate": bool(
            abs(frames_template - logits_template) < 0.01
            and abs(
                mean_metric(post_gate_metrics, "decoded_spectral_high_band_energy_ratio")
                - mean_metric(no_gate_metrics, "decoded_spectral_high_band_energy_ratio")
            )
            < 0.02
            and abs(
                mean_metric(post_gate_metrics, "decoded_frame_template_cosine_mean")
                - mean_metric(no_gate_metrics, "decoded_frame_template_cosine_mean")
            )
            < 0.01
        ),
    }


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
        decoder_branch_mean_mix_alpha=0.0,
        use_decoder_branch_condition_adapter=bool(model.use_decoder_branch_condition_adapter),
        use_residual_shape_branch_condition_adapter=bool(model.use_residual_shape_branch_condition_adapter),
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
                f"{raw_mode!r}. Expected one of: zero, reference_mean, reference_affine_match, "
                "time_roll_half, time_shuffle."
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
    periodic_reference = dict(reference_feature_summary.get("periodic", {}))
    noise_reference = dict(reference_feature_summary.get("noise", {}))
    requires_reference_mean = normalized_strategy in {
        "conditioning_reference_mean",
        "conditioning_reference_mean_plus_reference_q01_q99_clip",
        "reference_affine_match",
    } or any(str(item.get("mode")) in {"reference_mean", "reference_affine_match"} for item in resolved_control_family_overrides)
    requires_reference_std = normalized_strategy == "reference_affine_match" or any(
        str(item.get("mode")) == "reference_affine_match" for item in resolved_control_family_overrides
    )
    requires_reference_quantiles = normalized_strategy in {
        "reference_q01_q99_clip",
        "conditioning_reference_mean_plus_reference_q01_q99_clip",
    }
    periodic_mean = resolve_reference_stat_tensor(
        reference_distribution=periodic_reference,
        key="per_dim_mean",
        required=requires_reference_mean,
    )
    periodic_std = resolve_reference_stat_tensor(
        reference_distribution=periodic_reference,
        key="per_dim_std",
        required=requires_reference_std,
    )
    periodic_q01 = resolve_reference_stat_tensor(
        reference_distribution=periodic_reference,
        key="per_dim_q01",
        required=requires_reference_quantiles,
    )
    periodic_q99 = resolve_reference_stat_tensor(
        reference_distribution=periodic_reference,
        key="per_dim_q99",
        required=requires_reference_quantiles,
    )
    noise_mean = resolve_reference_stat_tensor(
        reference_distribution=noise_reference,
        key="per_dim_mean",
        required=requires_reference_mean,
    )
    noise_std = resolve_reference_stat_tensor(
        reference_distribution=noise_reference,
        key="per_dim_std",
        required=requires_reference_std,
    )
    noise_q01 = resolve_reference_stat_tensor(
        reference_distribution=noise_reference,
        key="per_dim_q01",
        required=requires_reference_quantiles,
    )
    noise_q99 = resolve_reference_stat_tensor(
        reference_distribution=noise_reference,
        key="per_dim_q99",
        required=requires_reference_quantiles,
    )

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
                reference_std = periodic_std
            else:
                branch_features = noise_features
                reference_mean = noise_mean
                reference_std = noise_std
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
            elif mode == "reference_affine_match":
                branch_features[:, start:end] = match_feature_distribution_to_reference(
                    candidate_features=branch_features[:, start:end],
                    reference_mean=reference_mean[start:end],
                    reference_std=reference_std[start:end],
                )
                transformations.append(
                    f"{branch_name}.{semantic} -> reference_affine_match[{start}:{end}]"
                )
            elif mode in {"time_roll_half", "time_shuffle"}:
                branch_features[:, start:end] = apply_temporal_probe_override(
                    candidate_features=branch_features[:, start:end],
                    mode=mode,
                    semantic_key=f"{branch_name}.{semantic}",
                )
                transformations.append(
                    f"{branch_name}.{semantic} -> {mode}[{start}:{end}]"
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


def resolve_reference_stat_tensor(
    *,
    reference_distribution: dict[str, object],
    key: str,
    required: bool,
) -> torch.Tensor:
    values = reference_distribution.get(key)
    if values is None:
        if required:
            raise ValueError(
                f"Reference feature summary is missing required statistic {key!r} for the requested probe."
            )
        return torch.empty(0, dtype=torch.float32)
    return torch.tensor(values, dtype=torch.float32)


def apply_temporal_probe_override(
    *,
    candidate_features: torch.Tensor,
    mode: str,
    semantic_key: str,
) -> torch.Tensor:
    candidate = candidate_features.to(torch.float32)
    frame_count = int(candidate.shape[0])
    if frame_count <= 1:
        return candidate
    if mode == "time_roll_half":
        shift = max(1, frame_count // 2)
        return torch.roll(candidate, shifts=shift, dims=0)
    if mode == "time_shuffle":
        seed = sum((index + 1) * byte for index, byte in enumerate(semantic_key.encode("utf-8")))
        generator = torch.Generator(device="cpu")
        generator.manual_seed(int(seed % 2_147_483_647))
        permutation = torch.randperm(frame_count, generator=generator, device="cpu")
        return candidate.index_select(0, permutation.to(device=candidate.device))
    raise ValueError(f"Unsupported temporal probe override mode: {mode!r}")


def build_branch_feature_layout(scaffold_payload: dict[str, object]) -> dict[str, dict[str, tuple[int, int]]]:
    available_controls = dict(scaffold_payload["available_controls"])
    conditioning = dict(scaffold_payload["conditioning"])
    branch_scaffold = dict(scaffold_payload["branch_scaffold"])

    periodic = build_branch_feature_semantic_layout(
        feature_semantics=list(branch_scaffold.get("periodic_feature_semantics", [])),
        available_controls=available_controls,
        conditioning=conditioning,
    )
    noise = build_branch_feature_semantic_layout(
        feature_semantics=list(branch_scaffold.get("noise_feature_semantics", [])),
        available_controls=available_controls,
        conditioning=conditioning,
    )
    return {
        "periodic": periodic,
        "noise": noise,
    }


def build_branch_feature_semantic_layout(
    *,
    feature_semantics: list[object],
    available_controls: dict[str, object],
    conditioning: dict[str, object],
) -> dict[str, tuple[int, int]]:
    layout: dict[str, tuple[int, int]] = {}
    start = 0
    for raw_semantic in feature_semantics:
        semantic = str(raw_semantic)
        dim = resolve_branch_semantic_dim(
            semantic=semantic,
            available_controls=available_controls,
            conditioning=conditioning,
        )
        layout[semantic] = (start, start + dim)
        start += dim
    return layout


def resolve_branch_semantic_dim(
    *,
    semantic: str,
    available_controls: dict[str, object],
    conditioning: dict[str, object],
) -> int:
    if semantic == "alpha":
        value = conditioning.get("alpha")
        if isinstance(value, torch.Tensor):
            return int(value.numel())
        return 1
    if semantic in {"s_spk_target", "s_geom_target"}:
        value = conditioning.get(semantic)
        if not isinstance(value, torch.Tensor):
            raise KeyError(f"Conditioning semantic is missing for decoder probe layout: {semantic}")
        return int(value.shape[-1])
    if semantic in available_controls:
        value = available_controls[semantic]
        if not isinstance(value, torch.Tensor):
            raise KeyError(f"Available control semantic is not tensor-valued for decoder probe layout: {semantic}")
        return int(value.shape[-1])
    raise KeyError(f"Unsupported branch semantic for decoder probe layout: {semantic}")


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


def build_teacher_first_waveform_handoff_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Waveform Handoff Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- waveform_decode: {json.dumps(summary.get('waveform_decode', {}), ensure_ascii=False)}",
        f"- diagnosis: {json.dumps(summary.get('diagnosis', {}), ensure_ascii=False)}",
        "",
        "## Route Aggregates",
    ]
    for route in list(summary.get("route_aggregates", [])):
        metrics = dict(route.get("metrics", {}))
        lines.append(
            "- "
            f"{route.get('label')}: "
            f"template={dict(metrics.get('decoded_frame_template_cosine_mean', {})).get('mean', 0.0)}, "
            f"activity_corr={dict(metrics.get('predicted_activity_to_decoded_frame_rms_corr', {})).get('mean', 0.0)}, "
            f"centroid={dict(metrics.get('decoded_spectral_centroid_hz', {})).get('mean', 0.0)}, "
            f"high_band={dict(metrics.get('decoded_spectral_high_band_energy_ratio', {})).get('mean', 0.0)}"
        )
    lines.extend(
        [
            "",
            "## Handoff Stage Aggregates",
            "- "
            f"logits_template={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frame_logits_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"frames_template={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"logits_abs_ge_1={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frame_logits_fraction_abs_ge_1', {}).get('mean', 0.0)}, "
            f"frames_abs_ge_095={dict(summary.get('handoff_stage_aggregates', {})).get('waveform_frames_fraction_abs_ge_095', {}).get('mean', 0.0)}",
            "",
            "## Cases",
        ]
    )
    for case in list(summary.get("cases", [])):
        lines.extend(
            [
                f"- case_id: {case.get('case_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  main_decoded_audio_path: {case.get('main_decoded_audio_path')}",
                f"  normalization: {json.dumps(case.get('normalization', {}), ensure_ascii=False)}",
                f"  handoff_dir: {case.get('handoff_dir')}",
                f"  stage_audio_exports: {json.dumps(case.get('stage_audio_exports', {}), ensure_ascii=False)}",
                f"  stage_metrics: {json.dumps(case.get('stage_metrics', {}), ensure_ascii=False)}",
            ]
        )
        for route in list(case.get("routes", [])):
            lines.append(
                "  "
                f"{route.get('label')}: audio_path={route.get('audio_path')} "
                f"metrics={json.dumps(route.get('metrics', {}), ensure_ascii=False)}"
            )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def build_teacher_first_waveform_decoder_structure_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Teacher-First VC Waveform Decoder Structure Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- output_dir: {summary['output_dir']}",
        f"- device: {summary['device']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- decode_runtime: {json.dumps(summary.get('decode_runtime', {}), ensure_ascii=False)}",
        f"- baseline_decoder_collapse_summary: {json.dumps(summary.get('baseline_decoder_collapse_summary', {}), ensure_ascii=False)}",
        "",
        "## Variant Impact Ranking",
    ]
    for item in list(summary.get("variant_impact_ranking", [])):
        lines.append(
            "- "
            f"{item['label']}: "
            f"waveform_mean_abs_delta_vs_baseline={item['mean_waveform_mean_abs_delta_vs_baseline']:.6f}, "
            f"fused_to_waveform_template_gap={item['mean_fused_to_waveform_template_cosine_gap']:.6f}, "
            f"fused_to_waveform_adjacent_gap={item['mean_fused_to_waveform_adjacent_cosine_gap']:.6f}, "
            f"waveform_template={item['mean_waveform_frames_template_cosine_mean']:.6f}, "
            f"decoded_template={item['mean_decoded_frame_template_cosine_mean']:.6f}"
        )
    lines.extend(["", "## Variant Aggregates"])
    for item in list(summary.get("variant_aggregates", [])):
        scalar_metrics = dict(item.get("scalar_metrics", {}))
        delta_vs_baseline = dict(item.get("delta_vs_baseline", {}))
        lines.append(
            "- "
            f"{item['label']}: "
            f"record_count={item['record_count']}, "
            f"waveform_delta={delta_vs_baseline.get('waveform_mean_abs_delta_vs_baseline', {}).get('mean', 0.0)}, "
            f"fused_template={scalar_metrics.get('fused_hidden_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"waveform_template={scalar_metrics.get('waveform_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"decoded_template={scalar_metrics.get('decoded_frames_template_cosine_mean', {}).get('mean', 0.0)}, "
            f"decoded_centroid={scalar_metrics.get('decoded_spectral_centroid_hz', {}).get('mean', 0.0)}, "
            f"decoded_high_band={scalar_metrics.get('decoded_spectral_high_band_energy_ratio', {}).get('mean', 0.0)}"
        )
    lines.extend(["", "## Cases"])
    for case in list(summary.get("cases", [])):
        lines.extend(
            [
                f"- record_id: {case.get('record_id')}",
                f"  input_audio_path: {case.get('input_audio_path')}",
                f"  main_decoded_audio_path: {case.get('main_decoded_audio_path')}",
                f"  structure_dir: {case.get('structure_dir')}",
            ]
        )
        for variant in list(case.get("variants", [])):
            lines.append(
                "  "
                f"{variant.get('label')}: audio_path={variant.get('audio_path')} "
                f"scalar_metrics={json.dumps(variant.get('scalar_metrics', {}), ensure_ascii=False)}"
            )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
