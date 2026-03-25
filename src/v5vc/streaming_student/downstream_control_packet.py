from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import torch

from v5vc.event_semantics import build_design_state_e_evt_v1_meta
from v5vc.offline_teacher_vocoder_input_scaffold import (
    DEFAULT_STAGE5_F0_CEIL_HZ,
    DEFAULT_STAGE5_F0_FLOOR_HZ,
    normalize_energy_log_rms_for_stage5,
    normalize_f0_hz_for_stage5,
)
from v5vc.source_acoustic_state_extraction import (
    DEFAULT_VUV_VOICED_FRAME_THRESHOLD,
    extract_source_acoustic_state,
)
from v5vc.streaming_student.data import (
    load_streaming_student_conditioning_asset,
    load_streaming_student_target_examples_from_records,
    load_streaming_student_target_records_by_split,
)
from v5vc.streaming_student.losses import resolve_semantic_supervision_config
from v5vc.streaming_student.plan_entry import instantiate_streaming_student_scaffold


DOWNSTREAM_CONTROL_PACKET_VERSION = "streaming_student_downstream_control_v1"


def export_streaming_student_downstream_control_packet(
    checkpoint_path: Path,
    output_dir: Path,
    teacher_label_index_path: Path,
    calibration_asset_path: Path,
    split_dir: Path | None,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    branch_label: str | None,
    max_audio_sec: float | None,
) -> dict[str, object]:
    checkpoint_path = checkpoint_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = payload.get("config")
    if not isinstance(config, dict):
        raise ValueError(f"Checkpoint missing config payload: {checkpoint_path}")
    config_path = Path(str(payload.get("config_path", "configs/streaming_student_stage_template.json")))
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()

    records_by_split, split_summary = load_streaming_student_target_records_by_split(
        config_path=config_path,
        config=config,
        teacher_label_index_path=teacher_label_index_path,
        split_dir=split_dir,
    )
    normalized_split_name = str(split_name).strip()
    if normalized_split_name not in records_by_split:
        raise ValueError(f"Unsupported split_name: {split_name}")
    selected_records = select_target_records(
        records=records_by_split[normalized_split_name],
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not selected_records:
        raise ValueError("No target records selected for Stage3 downstream control packet export.")

    conditioning_asset = load_streaming_student_conditioning_asset(calibration_asset_path)
    model = instantiate_streaming_student_scaffold(model_config=dict(config["model"]))
    model.load_state_dict(payload["model_state_dict"])
    model.eval()

    semantic_supervision = resolve_semantic_supervision_config(config=config.get("semantic_supervision"))
    branch = branch_label or str(payload.get("experiment_id", checkpoint_path.stem))
    event_target_family = str(semantic_supervision.get("event_target_family", "unknown"))
    event_projection_mode = str(semantic_supervision.get("event_projection_mode", "unknown"))
    frame_length = int(config["model"]["frame_length"])
    hop_length = int(config["model"]["hop_length"])
    effective_max_audio_sec = None if max_audio_sec is None else float(max_audio_sec)

    exported_records: list[dict[str, object]] = []
    packet_ready_count = 0

    with torch.no_grad():
        for record in selected_records:
            example = load_streaming_student_target_examples_from_records([record])[0]
            waveform = example.waveform
            if effective_max_audio_sec is not None:
                max_samples = max(1, int(round(example.sample_rate * effective_max_audio_sec)))
                waveform = waveform[:max_samples].contiguous()
            lengths = torch.tensor([waveform.numel()], dtype=torch.long)
            waveform_batch = waveform.unsqueeze(0)
            speaker_embedding = conditioning_asset["speaker_embedding"].unsqueeze(0).to(torch.float32)
            geom_embedding = conditioning_asset["geom_embedding"].unsqueeze(0).to(torch.float32)
            outputs = model(
                waveform=waveform_batch,
                lengths=lengths,
                speaker_embedding=speaker_embedding,
                geom_embedding=geom_embedding,
            )
            frame_mask = outputs["frame_mask"][0].to(torch.bool).cpu()
            frame_count = int(frame_mask.sum().item())
            if frame_count <= 0:
                raise ValueError(f"Stage3 downstream control packet encountered zero valid frames for {example.record_id}")

            frame_start_samples = (
                torch.arange(frame_count, dtype=torch.long) * hop_length
            )
            frame_start_ms = (
                frame_start_samples.to(torch.float32) / float(example.sample_rate) * 1000.0
            )
            reference_state = extract_source_acoustic_state(
                waveform=waveform,
                sample_rate=int(example.sample_rate),
                frame_start_samples=frame_start_samples,
                frame_length=frame_length,
            )

            z_art = outputs["z_art"][0, :frame_count].to(torch.float32).cpu()
            event_probs = outputs["event_probs"][0, :frame_count].to(torch.float32).cpu()
            event_logits = outputs["event_logits"][0, :frame_count].to(torch.float32).cpu()
            event_prior_probs = torch.sigmoid(
                outputs["event_prior_logits"][0, :frame_count].to(torch.float32)
            ).cpu()
            coarse_log_f0 = outputs["coarse_log_f0"][0, :frame_count].to(torch.float32).cpu()
            log_f0_correction = outputs["log_f0_correction"][0, :frame_count].to(torch.float32).cpu()
            f0_log_proxy = coarse_log_f0 + log_f0_correction
            vuv_prob = torch.sigmoid(outputs["vuv_logits"][0, :frame_count].to(torch.float32)).cpu()
            aper_prob = torch.sigmoid(
                (
                    outputs["aperiodicity"][0, :frame_count].to(torch.float32)
                    + outputs["aper_correction"][0, :frame_count].to(torch.float32)
                )
            ).cpu()
            energy_log = outputs["energy"][0, :frame_count].to(torch.float32).cpu()
            energy_norm = torch.sigmoid((energy_log + 4.0) * 2.0)
            energy_stage5_norm = normalize_energy_log_rms_for_stage5(energy_log)
            reference_f0_hz = reference_state["f0_hz"][:frame_count].to(torch.float32).cpu()
            reference_vuv = reference_state["vuv"][:frame_count].to(torch.float32).cpu()
            reference_aper = reference_state["aper"][:frame_count].to(torch.float32).cpu()
            reference_energy_log = reference_state["E"][:frame_count].to(torch.float32).cpu()
            reference_energy_stage5_norm = normalize_energy_log_rms_for_stage5(reference_energy_log)
            f0_calibration = calibrate_f0_log_proxy_to_reference(
                f0_log_proxy=f0_log_proxy,
                predicted_vuv_prob=vuv_prob,
                reference_f0_hz=reference_f0_hz,
                reference_vuv=reference_vuv,
            )
            packet_ready = bool(event_target_family == "teacher_e_evt_v1" and int(event_probs.shape[-1]) >= 8)
            if packet_ready:
                packet_ready_count += 1
                e_evt = event_probs
                e_evt_meta = build_design_state_e_evt_v1_meta()
            else:
                e_evt = torch.zeros((frame_count, 0), dtype=torch.float32)
                e_evt_meta = {
                    "event_contract_version": "legacy_event_probs_only",
                    "event_label_space_version": "legacy_event_probs_only",
                    "semantic_status": "not_ready_for_named_e_evt_packet",
                    "event_dimensions": [],
                    "event_dimension_specs": [],
                }

            tensor_payload = {
                "packet_version": DOWNSTREAM_CONTROL_PACKET_VERSION,
                "record_id": example.record_id,
                "split_name": normalized_split_name,
                "audio_path": str(example.audio_path),
                "sample_rate": int(example.sample_rate),
                "frame_length": frame_length,
                "hop_length": hop_length,
                "frame_start_samples": frame_start_samples,
                "frame_start_ms": frame_start_ms,
                "controls": {
                    "z_art": z_art,
                    "legacy_event_probs": event_probs,
                    "e_evt": e_evt,
                    "f0_log_proxy": f0_log_proxy,
                    "f0_hz_calibrated": f0_calibration["f0_hz_calibrated"],
                    "f0_hz_stage5_norm": f0_calibration["f0_hz_stage5_norm"],
                    "vuv_prob": vuv_prob,
                    "aper_prob": aper_prob,
                    "energy_log": energy_log,
                    "energy_norm": energy_norm,
                    "energy_stage5_norm": energy_stage5_norm,
                },
                "reference_controls": {
                    "f0_hz": reference_f0_hz,
                    "vuv": reference_vuv,
                    "aper": reference_aper,
                    "energy_log": reference_energy_log,
                    "energy_stage5_norm": reference_energy_stage5_norm,
                },
                "diagnostics": {
                    "event_logits": event_logits,
                    "event_prior_probs": event_prior_probs,
                    "coarse_log_f0": coarse_log_f0,
                    "log_f0_correction": log_f0_correction,
                    "frame_mask": frame_mask[:frame_count],
                    "f0_calibration": dict(f0_calibration["summary"]),
                },
                "conditioning": {
                    "speaker_embedding": conditioning_asset["speaker_embedding"].to(torch.float32),
                    "geom_embedding": conditioning_asset["geom_embedding"].to(torch.float32),
                    "alpha": torch.tensor([float(conditioning_asset["alpha"])], dtype=torch.float32),
                },
                "control_contract": {
                    "event_target_family": event_target_family,
                    "event_projection_mode": event_projection_mode,
                    "packet_ready_for_named_e_evt_handoff": packet_ready,
                    "e_evt_meta": e_evt_meta,
                    "f0_status": "analysis_only_affine_calibrated_to_target_reference",
                    "aper_status": "bounded_proxy_with_target_reference_audit",
                    "energy_status": "log_proxy_with_stage5_norm_and_target_reference_audit",
                    "r_res_status": "absent_by_design",
                },
            }
            tensor_relative_path = Path("records") / f"{sanitize_filename(example.record_id)}.pt"
            tensor_path = output_dir / tensor_relative_path
            torch.save(tensor_payload, tensor_path)

            exported_records.append(
                {
                    "record_id": example.record_id,
                    "audio_path": str(example.audio_path),
                    "split_name": normalized_split_name,
                    "packet_path": tensor_path.as_posix(),
                    "packet_relative_path": tensor_relative_path.as_posix(),
                    "frame_count": frame_count,
                    "packet_ready_for_named_e_evt_handoff": packet_ready,
                    "event_target_family": event_target_family,
                    "event_projection_mode": event_projection_mode,
                    "z_art_abs_mean": round(float(z_art.abs().mean().item()), 6),
                    "e_evt_mean": (
                        round(float(e_evt.mean().item()), 6)
                        if int(e_evt.numel()) > 0
                        else None
                    ),
                    "vuv_prob_mean": round(float(vuv_prob.mean().item()), 6),
                    "aper_prob_mean": round(float(aper_prob.mean().item()), 6),
                    "energy_log_mean": round(float(energy_log.mean().item()), 6),
                    "energy_norm_mean": round(float(energy_norm.mean().item()), 6),
                    "energy_stage5_norm_mean": round(float(energy_stage5_norm.mean().item()), 6),
                    "f0_log_proxy_mean": round(float(f0_log_proxy.mean().item()), 6),
                    "f0_reference_voiced_frame_count": int(
                        f0_calibration["summary"]["reference_voiced_frame_count"]
                    ),
                    "f0_proxy_reference_corr": f0_calibration["summary"]["proxy_reference_corr"],
                    "f0_calibrated_log2_mae": f0_calibration["summary"]["calibrated_log2_mae"],
                    "vuv_reference_mae": round(
                        float((vuv_prob - reference_vuv).abs().mean().item()),
                        6,
                    ),
                    "aper_reference_mae": round(
                        float((aper_prob - reference_aper).abs().mean().item()),
                        6,
                    ),
                    "energy_stage5_norm_reference_mae": round(
                        float((energy_stage5_norm - reference_energy_stage5_norm).abs().mean().item()),
                        6,
                    ),
                }
            )

    summary = {
        "packet_version": DOWNSTREAM_CONTROL_PACKET_VERSION,
        "checkpoint_path": checkpoint_path.as_posix(),
        "config_path": config_path.as_posix(),
        "teacher_label_index_path": Path(teacher_label_index_path).resolve().as_posix(),
        "calibration_asset_path": Path(calibration_asset_path).resolve().as_posix(),
        "split_dir": split_summary["split_dir"],
        "split_name": normalized_split_name,
        "branch_label": branch,
        "sample_count": len(exported_records),
        "max_audio_sec": effective_max_audio_sec,
        "conditioning": conditioning_asset["summary"],
        "semantic_supervision": semantic_supervision,
        "contract": {
            "event_target_family": event_target_family,
            "event_projection_mode": event_projection_mode,
            "frame_length": frame_length,
            "hop_length": hop_length,
            "r_res_enabled": bool(config["model"].get("r_res_enabled", False)),
            "f0_status": "analysis_only_affine_calibrated_to_target_reference",
            "aper_status": "bounded_proxy_with_target_reference_audit",
            "energy_status": "log_proxy_with_stage5_norm_and_target_reference_audit",
        },
        "packet_ready_count": packet_ready_count,
        "records": exported_records,
        "notes": [
            "This export is the first student-side downstream packet candidate, not a Stage5 training result.",
            "Current e_evt is exported only when checkpoint semantic_supervision.event_target_family=teacher_e_evt_v1.",
            "F0 now also exports an analysis-only affine-calibrated Hz view against target-reference acoustic state; this is an audit aid, not yet a deployment-ready control contract.",
            "aper and energy now export target-reference audit views so packet usefulness can be judged before any new Stage5 adapter is opened.",
            "r_res remains intentionally absent on this route.",
        ],
    }
    (output_dir / "streaming_student_downstream_control_packet.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "streaming_student_downstream_control_packet.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def select_target_records(
    records: list[dict[str, object]],
    sample_count: int,
    target_record_ids: list[str] | None,
) -> list[dict[str, object]]:
    if target_record_ids:
        record_map = {str(record["record_id"]): record for record in records}
        selected: list[dict[str, object]] = []
        missing: list[str] = []
        for record_id in target_record_ids:
            record = record_map.get(record_id)
            if record is None:
                missing.append(record_id)
                continue
            selected.append(record)
        if missing:
            raise ValueError(f"Unknown target_record_ids: {missing}")
        return selected
    if sample_count <= 0:
        raise ValueError("sample_count must be positive.")
    if len(records) <= sample_count:
        return records
    if sample_count == 1:
        return [records[0]]
    indices: list[int] = []
    max_index = len(records) - 1
    for index in range(sample_count):
        candidate = round(index * max_index / (sample_count - 1))
        if candidate not in indices:
            indices.append(candidate)
    while len(indices) < sample_count:
        for candidate in range(len(records)):
            if candidate not in indices:
                indices.append(candidate)
            if len(indices) >= sample_count:
                break
    return [records[index] for index in indices[:sample_count]]


def sanitize_filename(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            safe.append(char)
        else:
            safe.append("_")
    return "".join(safe).strip("_") or "record"


def calibrate_f0_log_proxy_to_reference(
    *,
    f0_log_proxy: torch.Tensor,
    predicted_vuv_prob: torch.Tensor,
    reference_f0_hz: torch.Tensor,
    reference_vuv: torch.Tensor,
) -> dict[str, object]:
    proxy = f0_log_proxy.view(-1).to(torch.float32)
    pred_vuv = predicted_vuv_prob.view(-1).to(torch.float32)
    ref_f0 = reference_f0_hz.view(-1).to(torch.float32)
    ref_vuv = reference_vuv.view(-1).to(torch.float32)
    voiced_mask = (ref_f0 > 0.0) & (ref_vuv >= DEFAULT_VUV_VOICED_FRAME_THRESHOLD)
    voiced_count = int(voiced_mask.to(torch.long).sum().item())
    if voiced_count < 8:
        zero = torch.zeros_like(proxy).unsqueeze(-1)
        return {
            "f0_hz_calibrated": zero,
            "f0_hz_stage5_norm": zero,
            "summary": {
                "status": "insufficient_reference_voiced_frames",
                "reference_voiced_frame_count": voiced_count,
                "proxy_reference_corr": None,
                "affine_scale": None,
                "affine_bias": None,
                "calibrated_log2_mae": None,
            },
        }

    x = proxy[voiced_mask]
    y = torch.log2(ref_f0[voiced_mask].clamp_min(DEFAULT_STAGE5_F0_FLOOR_HZ))
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    denominator = float((x_centered.pow(2)).sum().item())
    if denominator <= 1.0e-8:
        scale = 0.0
        bias = float(y.mean().item())
        corr = 0.0
    else:
        scale = float((x_centered * y_centered).sum().item() / denominator)
        bias = float((y.mean() - x.mean() * scale).item())
        corr = compute_correlation(x, y)
    scale = max(min(scale, 8.0), -8.0)

    pred_log2 = proxy * scale + bias
    pred_f0_hz = torch.pow(2.0, pred_log2).clamp(
        min=DEFAULT_STAGE5_F0_FLOOR_HZ,
        max=DEFAULT_STAGE5_F0_CEIL_HZ,
    )
    voiced_gate = pred_vuv >= DEFAULT_VUV_VOICED_FRAME_THRESHOLD
    pred_f0_hz = torch.where(voiced_gate, pred_f0_hz, torch.zeros_like(pred_f0_hz))
    pred_f0_hz = pred_f0_hz.unsqueeze(-1)
    pred_f0_stage5_norm = normalize_f0_hz_for_stage5(pred_f0_hz)

    calibrated_log2 = torch.log2(pred_f0_hz.squeeze(-1)[voiced_mask].clamp_min(DEFAULT_STAGE5_F0_FLOOR_HZ))
    calibrated_log2_mae = float((calibrated_log2 - y).abs().mean().item())
    return {
        "f0_hz_calibrated": pred_f0_hz,
        "f0_hz_stage5_norm": pred_f0_stage5_norm,
        "summary": {
            "status": "ok",
            "reference_voiced_frame_count": voiced_count,
            "proxy_reference_corr": round(corr, 6),
            "affine_scale": round(scale, 6),
            "affine_bias": round(bias, 6),
            "calibrated_log2_mae": round(calibrated_log2_mae, 6),
        },
    }


def compute_correlation(x: torch.Tensor, y: torch.Tensor) -> float:
    if int(x.numel()) <= 1 or int(y.numel()) <= 1:
        return 0.0
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    denominator = float(
        x_centered.pow(2).sum().sqrt().item() * y_centered.pow(2).sum().sqrt().item()
    )
    if denominator <= 1.0e-8:
        return 0.0
    return float((x_centered * y_centered).sum().item() / denominator)


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage3 downstream control packet",
        "",
        f"- packet_version: {summary['packet_version']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- config_path: {summary['config_path']}",
        f"- teacher_label_index_path: {summary['teacher_label_index_path']}",
        f"- calibration_asset_path: {summary['calibration_asset_path']}",
        f"- split_dir: {summary['split_dir']}",
        f"- split_name: {summary['split_name']}",
        f"- branch_label: {summary['branch_label']}",
        f"- sample_count: {summary['sample_count']}",
        f"- packet_ready_count: {summary['packet_ready_count']}",
        f"- max_audio_sec: {summary['max_audio_sec']}",
        f"- conditioning: {json.dumps(summary['conditioning'], ensure_ascii=False)}",
        f"- contract: {json.dumps(summary['contract'], ensure_ascii=False)}",
        "",
        "## Records",
    ]
    for record in summary["records"]:
        lines.append(f"### {record['record_id']}")
        lines.append(f"- audio_path: {record['audio_path']}")
        lines.append(f"- packet_path: {record['packet_path']}")
        lines.append(f"- frame_count: {record['frame_count']}")
        lines.append(
            f"- packet_ready_for_named_e_evt_handoff: {record['packet_ready_for_named_e_evt_handoff']}"
        )
        lines.append(f"- event_target_family: {record['event_target_family']}")
        lines.append(f"- event_projection_mode: {record['event_projection_mode']}")
        lines.append(f"- z_art_abs_mean: {record['z_art_abs_mean']}")
        lines.append(f"- e_evt_mean: {record['e_evt_mean']}")
        lines.append(f"- vuv_prob_mean: {record['vuv_prob_mean']}")
        lines.append(f"- aper_prob_mean: {record['aper_prob_mean']}")
        lines.append(f"- energy_log_mean: {record['energy_log_mean']}")
        lines.append(f"- energy_norm_mean: {record['energy_norm_mean']}")
        lines.append(f"- energy_stage5_norm_mean: {record['energy_stage5_norm_mean']}")
        lines.append(f"- f0_log_proxy_mean: {record['f0_log_proxy_mean']}")
        lines.append(f"- f0_reference_voiced_frame_count: {record['f0_reference_voiced_frame_count']}")
        lines.append(f"- f0_proxy_reference_corr: {record['f0_proxy_reference_corr']}")
        lines.append(f"- f0_calibrated_log2_mae: {record['f0_calibrated_log2_mae']}")
        lines.append(f"- vuv_reference_mae: {record['vuv_reference_mae']}")
        lines.append(f"- aper_reference_mae: {record['aper_reference_mae']}")
        lines.append(
            f"- energy_stage5_norm_reference_mae: {record['energy_stage5_norm_reference_mae']}"
        )
        lines.append("")
    lines.extend(["## Notes"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
