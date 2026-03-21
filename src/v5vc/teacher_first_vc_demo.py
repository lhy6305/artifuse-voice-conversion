from __future__ import annotations

from datetime import datetime
import json
import shutil
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import (
    DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
    infer_branch_label,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
)
from v5vc.offline_teacher_downstream_contract import export_offline_mvp_teacher_downstream_contract
from v5vc.offline_teacher_runtime import resolve_runtime_device
from v5vc.offline_teacher_vocoder_input_scaffold import build_offline_mvp_teacher_vocoder_input_scaffold
from v5vc.offline_vocoder_scaffold import NoResidualSourceFilterVocoderScaffold
from v5vc.offline_vocoder_training import reconstruct_waveform_from_frames
from v5vc.target_format_recovery import write_waveform_int16


DEFAULT_TEACHER_ROUTE_HANDOFF_PATH = Path(
    "reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"
)
DEFAULT_CALIBRATION_ASSET_PATH = Path(
    "data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"
)
DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH = Path(
    "reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json"
)


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

    contract_dir = output_dir / (
        "teacher_contract" if bool(save_intermediates) else "_tmp_teacher_contract"
    )
    scaffold_dir = output_dir / (
        "teacher_vocoder_input_scaffold" if bool(save_intermediates) else "_tmp_teacher_vocoder_input_scaffold"
    )

    export_offline_mvp_teacher_downstream_contract(
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
    )
    contract_tensor_path = contract_dir / "teacher_downstream_control_contract.pt"
    contract_json_path = contract_dir / "teacher_downstream_control_contract.json"
    build_offline_mvp_teacher_vocoder_input_scaffold(
        contract_path=contract_tensor_path,
        output_dir=scaffold_dir,
    )
    scaffold_tensor_path = scaffold_dir / "teacher_vocoder_input_scaffold.pt"

    contract_payload = json.loads(contract_json_path.read_text(encoding="utf-8"))
    scaffold_payload = torch.load(scaffold_tensor_path, map_location="cpu", weights_only=False)
    if not isinstance(scaffold_payload, dict):
        raise TypeError(f"Unsupported scaffold payload type: {type(scaffold_payload)!r}")

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

    checkpoint_payload = torch.load(resolved_vocoder_checkpoint_path, map_location="cpu", weights_only=False)
    model = build_vocoder_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        scaffold_payload=scaffold_payload,
    )
    resolved_device = resolve_runtime_device(device)
    model = model.to(resolved_device)
    model.eval()

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

    decoded_path = output_dir / "decoded.wav"
    write_waveform_int16(decoded_path, decoded_waveform, sample_rate=sample_rate)

    branch_label = infer_branch_label(
        checkpoint_path=resolved_vocoder_checkpoint_path,
        selection_summary=selection_summary,
        selection_target=selection_target,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=resolved_apply_mode,
    )
    contract_runtime = dict(contract_payload.get("runtime", {}))
    teacher_summary = dict(contract_payload.get("teacher", {}))
    conditioning_summary = dict(contract_payload.get("conditioning", {}))
    selection_summary_path = (
        None
        if vocoder_checkpoint_selection_path is None
        else vocoder_checkpoint_selection_path.resolve().as_posix()
    )

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "teacher_first_single_target_vc_demo_v1",
        "input_audio_path": input_audio_path.resolve().as_posix(),
        "decoded_audio_path": decoded_path.as_posix(),
        "decoded_audio_samples": int(decoded_waveform.shape[0]),
        "decoded_audio_sec": round(float(decoded_waveform.shape[0] / sample_rate), 6),
        "decoded_waveform_rms": round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6),
        "teacher": {
            "experiment_id": teacher_summary.get("experiment_id"),
            "checkpoint_path": teacher_summary.get("checkpoint_path"),
            "route_handoff_path": teacher_summary.get("route_handoff_path"),
            "verify_against_full_pass": bool(verify_against_full_pass),
            "chunk_samples": contract_runtime.get("chunk_samples"),
            "chunk_ms": contract_runtime.get("chunk_ms"),
        },
        "conditioning": conditioning_summary,
        "vocoder": {
            "checkpoint_path": resolved_vocoder_checkpoint_path.as_posix(),
            "checkpoint_selection_path": selection_summary_path,
            "selection_target": None if selection_summary is None else str(selection_target),
            "selection_summary": selection_summary,
            "branch_label": branch_label,
        },
        "waveform_decode": {
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
        },
        "artifacts": {
            "save_intermediates": bool(save_intermediates),
            "teacher_contract_path": (
                contract_tensor_path.as_posix() if bool(save_intermediates) else None
            ),
            "teacher_vocoder_input_scaffold_path": (
                scaffold_tensor_path.as_posix() if bool(save_intermediates) else None
            ),
        },
        "notes": [
            "This command is a teacher-first single-target demo path, not the final product-grade many-to-many runtime.",
            "decoded.wav is generated without aligned_target-dependent pitch matching, audit proxy, or validation-side loss readouts.",
            "The current target conditioning still comes from the existing calibration asset and therefore represents a fixed single-target preset.",
            "When stable_late_stop is absent from a checkpoint-selection payload, prefer best_validation or pass an explicit vocoder checkpoint.",
        ],
    }
    summary_json_path = output_dir / "teacher_first_vc_demo.json"
    summary_md_path = output_dir / "teacher_first_vc_demo.md"
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

    if not bool(save_intermediates):
        shutil.rmtree(contract_dir, ignore_errors=True)
        shutil.rmtree(scaffold_dir, ignore_errors=True)


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


def build_markdown(summary: dict[str, object]) -> str:
    teacher = dict(summary["teacher"])
    conditioning = dict(summary["conditioning"])
    vocoder = dict(summary["vocoder"])
    waveform_decode = dict(summary["waveform_decode"])
    artifacts = dict(summary["artifacts"])
    lines = [
        "# Teacher-First Single-Target VC Demo",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- mode: {summary['mode']}",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- decoded_audio_path: {summary['decoded_audio_path']}",
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
        "## Artifacts",
        f"- {json.dumps(artifacts, ensure_ascii=False)}",
        "",
        "## Notes",
    ]
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"

