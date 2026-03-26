from __future__ import annotations

from datetime import datetime
import json
import math
from pathlib import Path

import torch
import torch.nn.functional as F

from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_training import (
    compute_rms_guard_loss,
    compute_stft_reconstruction_loss,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.stage5_speech_emergence_probe import (
    compute_pearson_correlation,
    frame_waveform_sequence,
    summarize_frame_sequence_metrics,
    summarize_scalar_values,
)


OBJECTIVE_COLLAPSE_VARIANTS = [
    {
        "label": "baseline_decode_route",
        "description": "Current Stage5 decode route from the selected checkpoint using predicted activity gate, smooth3, and post_ola_envelope.",
        "kind": "baseline",
    },
    {
        "label": "oracle_active_frame_target_rms",
        "description": "Replace all short-time structure with one fixed target frame while preserving the aligned target frame RMS trajectory.",
        "kind": "oracle_fixed_template",
        "template_mode": "active_target_frame",
    },
    {
        "label": "oracle_sine_target_rms",
        "description": "Replace all short-time structure with one fixed sine template while preserving the aligned target frame RMS trajectory.",
        "kind": "oracle_fixed_template",
        "template_mode": "sine",
    },
]

TRANSITION_DELTA_LAMBDA_GRID = [0.1, 0.25, 0.3, 0.5, 0.75, 1.0]
TRANSITION_COMBO_DELTA_LAMBDA_GRID = [0.3, 0.5, 0.75, 1.0, 1.5]
TRANSITION_COMBO_FLUX_LAMBDA_GRID = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]
DIRECTIONAL_FLUX_DIRECTION_LAMBDA_GRID = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
DIRECTIONAL_FLUX_ZERO_JITTER_LAMBDA_GRID = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
ACTIVE_TEMPLATE_EXCESS_LAMBDA_GRID = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
ACTIVE_TEMPLATE_ZERO_JITTER_LAMBDA_GRID = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
ACTIVE_TEMPLATE_DELTA_LAMBDA_GRID = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]


def analyze_stage5_nores_waveform_objective_collapse(
    *,
    output_dir: Path,
    checkpoint_path: Path | None,
    checkpoint_selection_path: Path | None,
    selection_target: str,
    dataset_index_path: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    device: str,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_index_path = dataset_index_path.resolve()
    resolved_apply_mode = normalize_predicted_activity_gate_apply_mode(predicted_activity_gate_apply_mode)
    resolved_checkpoint_path, selection_summary = resolve_checkpoint_path_from_inputs(
        checkpoint_path=checkpoint_path,
        checkpoint_selection_path=checkpoint_selection_path,
        selection_target=selection_target,
    )
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the waveform-objective collapse probe.")

    first_payload = load_training_package_payload(Path(package_entries[0]["training_package_path"]))
    first_batch = extract_training_batch(first_payload)
    first_runtime = extract_training_runtime(first_payload)
    model = build_model_from_checkpoint(
        checkpoint_payload=checkpoint_payload,
        first_batch=first_batch,
        first_runtime=first_runtime,
    )
    resolved_device = torch.device(device)
    model = model.to(resolved_device)
    model.eval()

    per_record_rows: list[dict[str, object]] = []
    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            aligned_waveform = batch["aligned_waveform"].to(torch.float32)
            frame_length = int(runtime["frame_length"])
            hop_length = int(runtime["hop_length"])
            sample_rate = int(runtime["sample_rate"])
            target_frames = frame_waveform_sequence(
                waveform=aligned_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            target_frame_rms = compute_centered_frame_rms(target_frames)

            baseline_outputs = model(
                periodic_branch_features=batch["periodic_branch_features"].to(device=resolved_device, dtype=torch.float32),
                noise_branch_features=batch["noise_branch_features"].to(device=resolved_device, dtype=torch.float32),
            )
            baseline_predicted_activity = torch.maximum(
                baseline_outputs["periodic_gate"],
                baseline_outputs["noise_gate"],
            )
            baseline_waveform = reconstruct_waveform_from_frames(
                waveform_frames=baseline_outputs["waveform_frames"],
                frame_length=frame_length,
                hop_length=hop_length,
                frame_gains=baseline_predicted_activity if bool(use_predicted_activity_gate) else None,
                frame_gain_floor=float(predicted_activity_gate_floor),
                frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                frame_gain_apply_mode=resolved_apply_mode,
            ).detach().cpu().to(torch.float32)
            baseline_metrics = summarize_objective_variant(
                decoded_waveform=baseline_waveform,
                aligned_waveform=aligned_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                sample_rate=sample_rate,
                waveform_weight=float(waveform_weight),
                stft_weight=float(stft_weight),
                rms_guard_weight=float(rms_guard_weight),
            )

            variant_rows = [
                {
                    "label": "baseline_decode_route",
                    "description": OBJECTIVE_COLLAPSE_VARIANTS[0]["description"],
                    "construction_notes": [
                        "Selected checkpoint decode with the current heard-route semantics.",
                        f"predicted_activity_gate={bool(use_predicted_activity_gate)}",
                        f"predicted_activity_gate_floor={float(predicted_activity_gate_floor)}",
                        f"predicted_activity_gate_smoothing_frames={int(predicted_activity_gate_smoothing_frames)}",
                        f"predicted_activity_gate_apply_mode={resolved_apply_mode}",
                    ],
                    "scalar_metrics": baseline_metrics,
                }
            ]

            for variant in OBJECTIVE_COLLAPSE_VARIANTS[1:]:
                fixed_template_frames, construction_notes = build_fixed_template_target_rms_frames(
                    target_frames=target_frames,
                    template_mode=str(variant["template_mode"]),
                    target_frame_rms=target_frame_rms,
                )
                synthetic_waveform = reconstruct_waveform_from_frames(
                    waveform_frames=fixed_template_frames,
                    frame_length=frame_length,
                    hop_length=hop_length,
                ).detach().cpu().to(torch.float32)
                scalar_metrics = summarize_objective_variant(
                    decoded_waveform=synthetic_waveform,
                    aligned_waveform=aligned_waveform,
                    frame_length=frame_length,
                    hop_length=hop_length,
                    sample_rate=sample_rate,
                    waveform_weight=float(waveform_weight),
                    stft_weight=float(stft_weight),
                    rms_guard_weight=float(rms_guard_weight),
                )
                variant_rows.append(
                    {
                        "label": str(variant["label"]),
                        "description": str(variant["description"]),
                        "construction_notes": construction_notes,
                        "scalar_metrics": scalar_metrics,
                    }
                )

            for variant_row in variant_rows:
                variant_row["delta_vs_baseline"] = summarize_objective_delta_vs_baseline(
                    candidate_metrics=dict(variant_row["scalar_metrics"]),
                    baseline_metrics=baseline_metrics,
                )

            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "variants": variant_rows,
                }
            )

    aggregate_rows = build_variant_aggregates(per_record_rows)
    transition_combo_grid_summary = build_transition_combo_grid_summary(
        per_record_rows=per_record_rows,
        delta_lambda_grid=TRANSITION_COMBO_DELTA_LAMBDA_GRID,
        flux_lambda_grid=TRANSITION_COMBO_FLUX_LAMBDA_GRID,
    )
    directional_flux_candidate_grid_summary = build_directional_flux_candidate_grid_summary(
        per_record_rows=per_record_rows,
        direction_lambda_grid=DIRECTIONAL_FLUX_DIRECTION_LAMBDA_GRID,
        zero_jitter_lambda_grid=DIRECTIONAL_FLUX_ZERO_JITTER_LAMBDA_GRID,
    )
    active_template_candidate_grid_summary = build_active_template_candidate_grid_summary(
        per_record_rows=per_record_rows,
        template_lambda_grid=ACTIVE_TEMPLATE_EXCESS_LAMBDA_GRID,
        zero_jitter_lambda_grid=ACTIVE_TEMPLATE_ZERO_JITTER_LAMBDA_GRID,
    )
    active_template_targeted_summary = build_active_template_targeted_summary(
        per_record_rows=per_record_rows,
        candidate_grid_summary=active_template_candidate_grid_summary,
    )
    active_template_delta_candidate_grid_summary = build_active_template_delta_candidate_grid_summary(
        per_record_rows=per_record_rows,
        template_lambda_grid=ACTIVE_TEMPLATE_EXCESS_LAMBDA_GRID,
        delta_lambda_grid=ACTIVE_TEMPLATE_DELTA_LAMBDA_GRID,
    )
    active_template_delta_targeted_summary = build_active_template_delta_targeted_summary(
        per_record_rows=per_record_rows,
        candidate_grid_summary=active_template_delta_candidate_grid_summary,
    )
    transition_targeted_hard_failure_summary = build_transition_targeted_hard_failure_summary(
        per_record_rows=per_record_rows,
        combo_grid_summary=transition_combo_grid_summary,
    )
    hard_record_ids = [
        str(item["record_id"])
        for item in list(transition_targeted_hard_failure_summary.get("repeated_hard_failures", []))
    ]
    transition_hard_case_breakdown = build_transition_hard_case_breakdown(
        hard_record_ids=hard_record_ids,
        package_entries=package_entries,
        model=model,
        device=resolved_device,
        use_predicted_activity_gate=bool(use_predicted_activity_gate),
        predicted_activity_gate_floor=float(predicted_activity_gate_floor),
        predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        predicted_activity_gate_apply_mode=resolved_apply_mode,
        waveform_weight=float(waveform_weight),
        stft_weight=float(stft_weight),
        rms_guard_weight=float(rms_guard_weight),
        best_combo=dict(transition_targeted_hard_failure_summary.get("best_combo", {})),
    )
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if checkpoint_selection_path is None else str(selection_target),
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "objective_weights": {
            "waveform": float(waveform_weight),
            "stft": float(stft_weight),
            "rms_guard": float(rms_guard_weight),
        },
        "decode_runtime": {
            "device": str(resolved_device),
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
            "fusion_mode": str(model.fusion_mode),
            "waveform_decoder_mode": str(model.waveform_decoder_mode),
        },
        "probe_variants": [
            {
                "label": str(item["label"]),
                "description": str(item["description"]),
                "kind": str(item["kind"]),
                "template_mode": item.get("template_mode"),
            }
            for item in OBJECTIVE_COLLAPSE_VARIANTS
        ],
        "variant_weighted_objective_ranking": build_weighted_objective_ranking(aggregate_rows),
        "structure_sidecar_rankings": build_structure_sidecar_rankings(aggregate_rows),
        "transition_delta_candidate_objective_rankings": build_transition_delta_candidate_objective_rankings(
            aggregate_rows=aggregate_rows,
            lambda_grid=TRANSITION_DELTA_LAMBDA_GRID,
        ),
        "transition_delta_flip_thresholds_vs_baseline": build_transition_delta_flip_thresholds_vs_baseline(
            aggregate_rows=aggregate_rows
        ),
        "transition_combo_grid_summary": transition_combo_grid_summary,
        "directional_flux_candidate_grid_summary": directional_flux_candidate_grid_summary,
        "active_template_candidate_grid_summary": active_template_candidate_grid_summary,
        "active_template_targeted_summary": active_template_targeted_summary,
        "active_template_delta_candidate_grid_summary": active_template_delta_candidate_grid_summary,
        "active_template_delta_targeted_summary": active_template_delta_targeted_summary,
        "transition_targeted_hard_failure_summary": transition_targeted_hard_failure_summary,
        "transition_hard_case_breakdown": transition_hard_case_breakdown,
        "variant_aggregates": aggregate_rows,
        "records": per_record_rows,
        "notes": [
            "This probe is objective-level support for the Stage5 no-res speech-emergence root-cause question.",
            "baseline_decode_route reuses the same decode semantics that produced the heard buzzing route.",
            "oracle_* variants are not trainable routes; they are constructive counterexamples showing what the current waveform objective does or does not strongly reject.",
            "If a fixed-template variant lands near or below baseline weighted_wave_objective while keeping template_cosine near 1.0, the current waveform objective is permissive to template-collapse fake solutions.",
            "loss_mrstft_short_256_512_1024 is a short-window MRSTFT sidecar diagnostic, not the current training loss.",
            "loss_frame_unit_rms_l1 removes each frame mean and RMS before comparison so it can diagnose short-time shape mismatch without letting envelope dominate the score.",
            "loss_frame_unit_rms_logspec_l1 compares per-frame log spectra after per-frame mean/RMS normalization.",
            "loss_frame_delta_unit_rms_l1 and loss_frame_spectral_flux_l1 compare adjacent-frame change patterns instead of static frame content.",
            "transition_delta_candidate_objective_rankings are aggregate what-if scores of weighted_wave_objective + lambda * loss_frame_delta_unit_rms_l1.",
            "transition_combo_grid_summary is a per-record robustness sweep over weighted_wave_objective + lambda_delta * frame_delta + lambda_flux * spectral_flux.",
            "directional_flux_candidate_grid_summary is a per-record robustness sweep over weighted_wave_objective + lambda_direction * active-target directional-flux cosine loss + lambda_zero * zero-target flux-jitter loss.",
            "active_template_candidate_grid_summary is a per-record robustness sweep over weighted_wave_objective + lambda_template * active-frame template-excess loss + lambda_zero * zero-target flux-jitter loss.",
            "active_template_targeted_summary materializes the simplest best active-template combo, its residual losses, and stationary-risk group summaries.",
            "active_template_delta_candidate_grid_summary is a per-record robustness sweep over weighted_wave_objective + lambda_template * active-frame template-excess loss + lambda_delta * frame-delta loss.",
            "active_template_delta_targeted_summary materializes the simplest best active-template-plus-delta combo, its residual losses, and stationary-risk group summaries.",
            "transition_targeted_hard_failure_summary uses the best current transition combo from the grid summary and materializes repeated hard-failure records for the next diagnostic step.",
            "transition_hard_case_breakdown localizes the transition-side failure windows for the repeated hard-failure records under the best current combo.",
            "failure_signature is a heuristic per-hard-case summary over positive-advantage transitions; q25/q75 are record-local target-transition-strength quartiles under the current delta/flux weighting.",
            "flux_alignment_summary compares signed spectral-flux direction and magnitude on positive flux-advantage transitions; band shares are normalized across low/mid/high rFFT thirds, and active_target ratios exclude near-zero target-flux transitions below 0.05.",
        ],
    }
    json_path = output_dir / "stage5_waveform_objective_collapse_probe.json"
    md_path = output_dir / "stage5_waveform_objective_collapse_probe.md"
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


def compute_centered_frame_rms(frames: torch.Tensor) -> torch.Tensor:
    centered = frames.detach().cpu().to(torch.float32) - frames.detach().cpu().to(torch.float32).mean(dim=1, keepdim=True)
    return centered.pow(2).mean(dim=1).sqrt()


def build_fixed_template_target_rms_frames(
    *,
    target_frames: torch.Tensor,
    template_mode: str,
    target_frame_rms: torch.Tensor,
) -> tuple[torch.Tensor, list[str]]:
    resolved_mode = str(template_mode).strip().lower()
    target_frames_cpu = target_frames.detach().cpu().to(torch.float32)
    centered_frames = target_frames_cpu - target_frames_cpu.mean(dim=1, keepdim=True)
    if resolved_mode == "active_target_frame":
        frame_rms = centered_frames.pow(2).mean(dim=1).sqrt()
        template_index = int(frame_rms.argmax().item())
        template = centered_frames[template_index]
        notes = [
            "template_mode=active_target_frame",
            "template_source=highest_centered_rms_target_frame",
            f"template_index={template_index}",
            "frame_envelope=aligned_target_centered_rms",
        ]
    elif resolved_mode == "sine":
        template = build_fixed_sine_template(frame_length=int(target_frames_cpu.shape[-1]), cycles_per_frame=8.0)
        notes = [
            "template_mode=sine",
            "template_source=synthetic_sine_8_cycles_per_frame",
            "frame_envelope=aligned_target_centered_rms",
        ]
    else:
        raise ValueError(f"Unsupported template_mode: {template_mode!r}")
    template = normalize_template_unit_rms(template)
    fixed_frames = target_frame_rms.view(-1, 1) * template.view(1, -1)
    return fixed_frames.to(torch.float32), notes


def build_fixed_sine_template(*, frame_length: int, cycles_per_frame: float) -> torch.Tensor:
    time_axis = torch.arange(int(frame_length), dtype=torch.float32)
    radians = 2.0 * math.pi * float(cycles_per_frame) * time_axis / float(frame_length)
    return torch.sin(radians)


def normalize_template_unit_rms(template: torch.Tensor) -> torch.Tensor:
    template_cpu = template.detach().cpu().to(torch.float32).view(-1)
    centered_template = template_cpu - template_cpu.mean()
    return centered_template / centered_template.pow(2).mean().sqrt().clamp_min(1.0e-6)


def summarize_objective_variant(
    *,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
) -> dict[str, float]:
    decoded_waveform_cpu = decoded_waveform.detach().cpu().to(torch.float32).view(-1)
    target_waveform = aligned_waveform.detach().cpu().to(torch.float32).view(-1)[: decoded_waveform_cpu.shape[0]]
    waveform_loss = float(F.l1_loss(decoded_waveform_cpu, target_waveform).item())
    stft_loss = float(
        compute_stft_reconstruction_loss(
            predicted_waveform=decoded_waveform_cpu,
            target_waveform=target_waveform,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
        ).item()
    )
    rms_guard_loss, decoded_rms_tensor, target_rms_tensor = compute_rms_guard_loss(
        predicted_waveform=decoded_waveform_cpu,
        target_waveform=target_waveform,
    )
    decoded_analysis_frames = frame_waveform_sequence(
        waveform=decoded_waveform_cpu,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
    )
    aligned_analysis_frames = frame_waveform_sequence(
        waveform=target_waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(decoded_analysis_frames.shape[0]),
    )
    decoded_frame_metrics = summarize_frame_sequence_metrics(decoded_analysis_frames)
    aligned_frame_metrics = summarize_frame_sequence_metrics(aligned_analysis_frames)
    decoded_frame_rms = decoded_analysis_frames.pow(2).mean(dim=1).sqrt()
    aligned_frame_rms = aligned_analysis_frames.pow(2).mean(dim=1).sqrt()
    decoded_normalized_frames = normalize_frames_unit_rms(decoded_analysis_frames)
    aligned_normalized_frames = normalize_frames_unit_rms(aligned_analysis_frames)
    frame_unit_rms_l1_loss = float(F.l1_loss(decoded_normalized_frames, aligned_normalized_frames).item())
    decoded_frame_logspec = compute_frame_logspec(decoded_normalized_frames)
    aligned_frame_logspec = compute_frame_logspec(aligned_normalized_frames)
    frame_unit_rms_logspec_l1_loss = float(F.l1_loss(decoded_frame_logspec, aligned_frame_logspec).item())
    decoded_frame_deltas = compute_adjacent_deltas(decoded_normalized_frames)
    aligned_frame_deltas = compute_adjacent_deltas(aligned_normalized_frames)
    frame_delta_unit_rms_l1_loss = float(F.l1_loss(decoded_frame_deltas, aligned_frame_deltas).item())
    decoded_spectral_flux = compute_adjacent_deltas(decoded_frame_logspec)
    aligned_spectral_flux = compute_adjacent_deltas(aligned_frame_logspec)
    frame_spectral_flux_l1_loss = float(F.l1_loss(decoded_spectral_flux, aligned_spectral_flux).item())
    directional_flux_metrics = compute_directional_flux_sidecar_metrics(
        decoded_spectral_flux=decoded_spectral_flux,
        aligned_spectral_flux=aligned_spectral_flux,
    )
    active_template_metrics = compute_active_template_structure_sidecar_metrics(
        decoded_normalized_frames=decoded_normalized_frames,
        aligned_normalized_frames=aligned_normalized_frames,
        aligned_frame_rms=aligned_frame_rms,
    )
    multires_stft_short_loss = float(
        compute_multires_stft_reconstruction_loss(
            predicted_waveform=decoded_waveform_cpu,
            target_waveform=target_waveform,
            frame_lengths=[256, 512, int(frame_length)],
        ).item()
    )
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform_cpu, int(sample_rate))
    aligned_spectral = compute_waveform_spectral_summary(target_waveform, int(sample_rate))
    decoded_rms = float(decoded_rms_tensor.item())
    target_rms = float(target_rms_tensor.item())
    weighted_wave_objective = (
        float(waveform_weight) * waveform_loss
        + float(stft_weight) * stft_loss
        + float(rms_guard_weight) * float(rms_guard_loss.item())
    )
    return {
        "loss_waveform": round(waveform_loss, 6),
        "loss_stft": round(stft_loss, 6),
        "loss_rms_guard": round(float(rms_guard_loss.item()), 6),
        "weighted_wave_objective": round(weighted_wave_objective, 6),
        "loss_mrstft_short_256_512_1024": round(multires_stft_short_loss, 6),
        "loss_frame_unit_rms_l1": round(frame_unit_rms_l1_loss, 6),
        "loss_frame_unit_rms_logspec_l1": round(frame_unit_rms_logspec_l1_loss, 6),
        "loss_frame_delta_unit_rms_l1": round(frame_delta_unit_rms_l1_loss, 6),
        "loss_frame_spectral_flux_l1": round(frame_spectral_flux_l1_loss, 6),
        "loss_frame_spectral_flux_direction_cosine_all": round(
            float(directional_flux_metrics["loss_frame_spectral_flux_direction_cosine_all"]),
            6,
        ),
        "loss_frame_spectral_flux_direction_cosine_active_0p05": round(
            float(directional_flux_metrics["loss_frame_spectral_flux_direction_cosine_active_0p05"]),
            6,
        ),
        "loss_frame_spectral_flux_zero_target_jitter_0p05": round(
            float(directional_flux_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"]),
            6,
        ),
        "loss_active_frame_template_excess_relu_0p02": round(
            float(active_template_metrics["loss_active_frame_template_excess_relu_0p02"]),
            6,
        ),
        "decoded_waveform_rms": round(decoded_rms, 6),
        "target_waveform_rms": round(target_rms, 6),
        "decoded_to_target_rms_ratio": round(0.0 if target_rms <= 1.0e-8 else decoded_rms / target_rms, 6),
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
        "decoded_frame_template_cosine_mean": float(decoded_frame_metrics["template_cosine_mean"]),
        "decoded_frame_adjacent_cosine_mean": float(decoded_frame_metrics["adjacent_cosine_mean"]),
        "decoded_frame_rms_cv": float(decoded_frame_metrics["frame_rms_cv"]),
        "aligned_frame_template_cosine_mean": float(aligned_frame_metrics["template_cosine_mean"]),
        "aligned_frame_adjacent_cosine_mean": float(aligned_frame_metrics["adjacent_cosine_mean"]),
        "aligned_frame_rms_cv": float(aligned_frame_metrics["frame_rms_cv"]),
        "decoded_frame_template_cosine_gap_vs_aligned": round(
            float(decoded_frame_metrics["template_cosine_mean"]) - float(aligned_frame_metrics["template_cosine_mean"]),
            6,
        ),
        "decoded_frame_adjacent_cosine_gap_vs_aligned": round(
            float(decoded_frame_metrics["adjacent_cosine_mean"]) - float(aligned_frame_metrics["adjacent_cosine_mean"]),
            6,
        ),
        "decoded_frame_rms_to_aligned_frame_rms_corr": float(
            compute_pearson_correlation(decoded_frame_rms, aligned_frame_rms)
        ),
    }


def normalize_frames_unit_rms(frames: torch.Tensor) -> torch.Tensor:
    frames_cpu = frames.detach().cpu().to(torch.float32)
    centered = frames_cpu - frames_cpu.mean(dim=1, keepdim=True)
    frame_rms = centered.pow(2).mean(dim=1, keepdim=True).sqrt().clamp_min(1.0e-6)
    return centered / frame_rms


def compute_frame_logspec(frames: torch.Tensor) -> torch.Tensor:
    frames_cpu = frames.detach().cpu().to(torch.float32)
    spectrum = torch.fft.rfft(frames_cpu, dim=1)
    return torch.log1p(spectrum.abs())


def compute_adjacent_deltas(sequence: torch.Tensor) -> torch.Tensor:
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    if int(sequence_cpu.shape[0]) <= 1:
        return sequence_cpu.new_zeros((1, *sequence_cpu.shape[1:]))
    return sequence_cpu[1:] - sequence_cpu[:-1]


def compute_directional_flux_sidecar_metrics(
    *,
    decoded_spectral_flux: torch.Tensor,
    aligned_spectral_flux: torch.Tensor,
    active_target_threshold: float = 0.05,
) -> dict[str, float]:
    decoded_flux_cpu = decoded_spectral_flux.detach().cpu().to(torch.float32)
    aligned_flux_cpu = aligned_spectral_flux.detach().cpu().to(torch.float32)
    flux_cosine = compute_rowwise_cosine_similarity(decoded_flux_cpu, aligned_flux_cpu)
    target_flux_magnitude = aligned_flux_cpu.abs().mean(dim=1)
    active_target_mask = target_flux_magnitude >= float(active_target_threshold)
    zero_target_mask = ~active_target_mask
    return {
        "loss_frame_spectral_flux_direction_cosine_all": float((1.0 - flux_cosine).mean().item()),
        "loss_frame_spectral_flux_direction_cosine_active_0p05": float(
            (1.0 - flux_cosine[active_target_mask]).mean().item()
        )
        if bool(active_target_mask.any())
        else 0.0,
        "loss_frame_spectral_flux_zero_target_jitter_0p05": float(decoded_flux_cpu[zero_target_mask].abs().mean().item())
        if bool(zero_target_mask.any())
        else 0.0,
    }


def compute_active_template_structure_sidecar_metrics(
    *,
    decoded_normalized_frames: torch.Tensor,
    aligned_normalized_frames: torch.Tensor,
    aligned_frame_rms: torch.Tensor,
    active_frame_rms_threshold: float = 0.02,
) -> dict[str, float]:
    decoded_frames_cpu = decoded_normalized_frames.detach().cpu().to(torch.float32)
    aligned_frames_cpu = aligned_normalized_frames.detach().cpu().to(torch.float32)
    aligned_frame_rms_cpu = aligned_frame_rms.detach().cpu().to(torch.float32).view(-1)
    active_mask = aligned_frame_rms_cpu >= float(active_frame_rms_threshold)
    if not bool(active_mask.any()):
        return {
            "loss_active_frame_template_excess_relu_0p02": 0.0,
        }
    decoded_template_cosine = compute_frame_cosine_to_reference(
        frames=decoded_frames_cpu,
        reference_index=0,
    )
    aligned_template_cosine = compute_frame_cosine_to_reference(
        frames=aligned_frames_cpu,
        reference_index=0,
    )
    active_template_excess = (decoded_template_cosine[active_mask] - aligned_template_cosine[active_mask]).clamp_min(0.0)
    return {
        "loss_active_frame_template_excess_relu_0p02": float(active_template_excess.mean().item()),
    }


def compute_frame_cosine_to_reference(*, frames: torch.Tensor, reference_index: int) -> torch.Tensor:
    frames_cpu = frames.detach().cpu().to(torch.float32)
    if int(frames_cpu.shape[0]) == 0:
        return frames_cpu.new_zeros((0,))
    resolved_reference_index = min(max(int(reference_index), 0), int(frames_cpu.shape[0]) - 1)
    reference = frames_cpu[resolved_reference_index : resolved_reference_index + 1]
    normalized_reference = reference / reference.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    normalized_frames = frames_cpu / frames_cpu.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    return (normalized_frames * normalized_reference).sum(dim=1)


def compute_multires_stft_reconstruction_loss(
    *,
    predicted_waveform: torch.Tensor,
    target_waveform: torch.Tensor,
    frame_lengths: list[int],
) -> torch.Tensor:
    losses = []
    for frame_length in frame_lengths:
        resolved_frame_length = int(frame_length)
        resolved_hop_length = max(1, resolved_frame_length // 4)
        losses.append(
            compute_stft_reconstruction_loss(
                predicted_waveform=predicted_waveform,
                target_waveform=target_waveform,
                frame_length=resolved_frame_length,
                hop_length=resolved_hop_length,
            )
        )
    return torch.stack(losses).mean()


def summarize_objective_delta_vs_baseline(
    *,
    candidate_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
) -> dict[str, float]:
    return {
        "weighted_wave_objective_delta_vs_baseline": round(
            float(candidate_metrics["weighted_wave_objective"]) - float(baseline_metrics["weighted_wave_objective"]),
            6,
        ),
        "loss_waveform_delta_vs_baseline": round(
            float(candidate_metrics["loss_waveform"]) - float(baseline_metrics["loss_waveform"]),
            6,
        ),
        "loss_stft_delta_vs_baseline": round(
            float(candidate_metrics["loss_stft"]) - float(baseline_metrics["loss_stft"]),
            6,
        ),
        "loss_rms_guard_delta_vs_baseline": round(
            float(candidate_metrics["loss_rms_guard"]) - float(baseline_metrics["loss_rms_guard"]),
            6,
        ),
        "decoded_frame_template_cosine_delta_vs_baseline": round(
            float(candidate_metrics["decoded_frame_template_cosine_mean"])
            - float(baseline_metrics["decoded_frame_template_cosine_mean"]),
            6,
        ),
        "decoded_frame_adjacent_cosine_delta_vs_baseline": round(
            float(candidate_metrics["decoded_frame_adjacent_cosine_mean"])
            - float(baseline_metrics["decoded_frame_adjacent_cosine_mean"]),
            6,
        ),
        "decoded_frame_rms_corr_delta_vs_baseline": round(
            float(candidate_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"])
            - float(baseline_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]),
            6,
        ),
    }


def build_variant_aggregates(per_record_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    variant_map: dict[str, dict[str, object]] = {}
    for record_row in per_record_rows:
        for variant_row in list(record_row["variants"]):
            label = str(variant_row["label"])
            bucket = variant_map.setdefault(
                label,
                {
                    "label": label,
                    "description": str(variant_row["description"]),
                    "record_count": 0,
                    "scalar_metrics": {},
                    "delta_vs_baseline": {},
                },
            )
            bucket["record_count"] = int(bucket["record_count"]) + 1
            for key, value in dict(variant_row["scalar_metrics"]).items():
                bucket["scalar_metrics"].setdefault(key, []).append(float(value))
            for key, value in dict(variant_row["delta_vs_baseline"]).items():
                bucket["delta_vs_baseline"].setdefault(key, []).append(float(value))
    aggregates = []
    for payload in variant_map.values():
        aggregates.append(
            {
                "label": str(payload["label"]),
                "description": str(payload["description"]),
                "record_count": int(payload["record_count"]),
                "scalar_metrics": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["scalar_metrics"]).items()
                },
                "delta_vs_baseline": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["delta_vs_baseline"]).items()
                },
            }
        )
    return sorted(
        aggregates,
        key=lambda item: (
            float(item["scalar_metrics"]["weighted_wave_objective"]["mean"]),
            str(item["label"]),
        ),
    )


def build_weighted_objective_ranking(aggregate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ranking = []
    for row in aggregate_rows:
        scalar_metrics = dict(row["scalar_metrics"])
        delta_metrics = dict(row["delta_vs_baseline"])
        ranking.append(
            {
                "label": str(row["label"]),
                "description": str(row["description"]),
                "mean_weighted_wave_objective": float(scalar_metrics["weighted_wave_objective"]["mean"]),
                "mean_loss_waveform": float(scalar_metrics["loss_waveform"]["mean"]),
                "mean_loss_stft": float(scalar_metrics["loss_stft"]["mean"]),
                "mean_loss_rms_guard": float(scalar_metrics["loss_rms_guard"]["mean"]),
                "mean_loss_mrstft_short_256_512_1024": float(
                    scalar_metrics["loss_mrstft_short_256_512_1024"]["mean"]
                ),
                "mean_loss_frame_unit_rms_l1": float(scalar_metrics["loss_frame_unit_rms_l1"]["mean"]),
                "mean_loss_frame_unit_rms_logspec_l1": float(scalar_metrics["loss_frame_unit_rms_logspec_l1"]["mean"]),
                "mean_loss_frame_delta_unit_rms_l1": float(scalar_metrics["loss_frame_delta_unit_rms_l1"]["mean"]),
                "mean_loss_frame_spectral_flux_l1": float(scalar_metrics["loss_frame_spectral_flux_l1"]["mean"]),
                "mean_decoded_frame_template_cosine": float(scalar_metrics["decoded_frame_template_cosine_mean"]["mean"]),
                "mean_decoded_frame_rms_to_aligned_frame_rms_corr": float(
                    scalar_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]["mean"]
                ),
                "mean_weighted_wave_objective_delta_vs_baseline": float(
                    delta_metrics["weighted_wave_objective_delta_vs_baseline"]["mean"]
                ),
            }
        )
    return sorted(ranking, key=lambda item: (float(item["mean_weighted_wave_objective"]), str(item["label"])))


def build_structure_sidecar_rankings(aggregate_rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    metric_names = [
        "loss_mrstft_short_256_512_1024",
        "loss_frame_unit_rms_l1",
        "loss_frame_unit_rms_logspec_l1",
        "loss_frame_delta_unit_rms_l1",
        "loss_frame_spectral_flux_l1",
        "loss_frame_spectral_flux_direction_cosine_all",
        "loss_frame_spectral_flux_direction_cosine_active_0p05",
        "loss_frame_spectral_flux_zero_target_jitter_0p05",
        "loss_active_frame_template_excess_relu_0p02",
    ]
    rankings: dict[str, list[dict[str, object]]] = {}
    for metric_name in metric_names:
        rows = []
        for row in aggregate_rows:
            scalar_metrics = dict(row["scalar_metrics"])
            rows.append(
                {
                    "label": str(row["label"]),
                    "description": str(row["description"]),
                    "mean": float(scalar_metrics[metric_name]["mean"]),
                    "decoded_frame_template_cosine_mean": float(scalar_metrics["decoded_frame_template_cosine_mean"]["mean"]),
                    "decoded_frame_rms_to_aligned_frame_rms_corr": float(
                        scalar_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]["mean"]
                    ),
                }
            )
        rankings[metric_name] = sorted(rows, key=lambda item: (float(item["mean"]), str(item["label"])))
    return rankings


def build_transition_delta_candidate_objective_rankings(
    *,
    aggregate_rows: list[dict[str, object]],
    lambda_grid: list[float],
) -> list[dict[str, object]]:
    rankings: list[dict[str, object]] = []
    for lambda_value in lambda_grid:
        variant_rows = []
        for row in aggregate_rows:
            scalar_metrics = dict(row["scalar_metrics"])
            weighted_wave_objective = float(scalar_metrics["weighted_wave_objective"]["mean"])
            frame_delta_loss = float(scalar_metrics["loss_frame_delta_unit_rms_l1"]["mean"])
            candidate_score = weighted_wave_objective + float(lambda_value) * frame_delta_loss
            variant_rows.append(
                {
                    "label": str(row["label"]),
                    "description": str(row["description"]),
                    "candidate_score": round(candidate_score, 6),
                    "weighted_wave_objective": round(weighted_wave_objective, 6),
                    "loss_frame_delta_unit_rms_l1": round(frame_delta_loss, 6),
                    "decoded_frame_template_cosine_mean": float(scalar_metrics["decoded_frame_template_cosine_mean"]["mean"]),
                    "decoded_frame_rms_to_aligned_frame_rms_corr": float(
                        scalar_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]["mean"]
                    ),
                }
            )
        variant_rows = sorted(variant_rows, key=lambda item: (float(item["candidate_score"]), str(item["label"])))
        rankings.append(
            {
                "lambda": round(float(lambda_value), 6),
                "ranking": variant_rows,
            }
        )
    return rankings


def build_transition_delta_flip_thresholds_vs_baseline(
    aggregate_rows: list[dict[str, object]]
) -> list[dict[str, object]]:
    row_map = {str(row["label"]): row for row in aggregate_rows}
    baseline_row = row_map.get("baseline_decode_route")
    if baseline_row is None:
        return []
    baseline_scalar_metrics = dict(baseline_row["scalar_metrics"])
    baseline_weighted = float(baseline_scalar_metrics["weighted_wave_objective"]["mean"])
    baseline_frame_delta = float(baseline_scalar_metrics["loss_frame_delta_unit_rms_l1"]["mean"])
    thresholds = []
    for label, row in row_map.items():
        if label == "baseline_decode_route":
            continue
        scalar_metrics = dict(row["scalar_metrics"])
        candidate_weighted = float(scalar_metrics["weighted_wave_objective"]["mean"])
        candidate_frame_delta = float(scalar_metrics["loss_frame_delta_unit_rms_l1"]["mean"])
        weighted_gap = baseline_weighted - candidate_weighted
        delta_advantage = candidate_frame_delta - baseline_frame_delta
        flip_lambda = None
        if delta_advantage > 0.0:
            flip_lambda = weighted_gap / delta_advantage
        thresholds.append(
            {
                "label": label,
                "description": str(row["description"]),
                "baseline_weighted_gap": round(weighted_gap, 6),
                "baseline_frame_delta_advantage": round(delta_advantage, 6),
                "flip_lambda_min": None if flip_lambda is None else round(float(flip_lambda), 6),
            }
        )
    return sorted(
        thresholds,
        key=lambda item: float("inf") if item["flip_lambda_min"] is None else float(item["flip_lambda_min"]),
    )


def build_transition_combo_grid_summary(
    *,
    per_record_rows: list[dict[str, object]],
    delta_lambda_grid: list[float],
    flux_lambda_grid: list[float],
) -> list[dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    for delta_lambda in delta_lambda_grid:
        for flux_lambda in flux_lambda_grid:
            matchup_rows = []
            total_wins = 0
            for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
                win_count = 0
                margins: list[float] = []
                for record_row in per_record_rows:
                    variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
                    baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
                    other_metrics = dict(variant_map[other_label]["scalar_metrics"])
                    baseline_score = (
                        float(baseline_metrics["weighted_wave_objective"])
                        + float(delta_lambda) * float(baseline_metrics["loss_frame_delta_unit_rms_l1"])
                        + float(flux_lambda) * float(baseline_metrics["loss_frame_spectral_flux_l1"])
                    )
                    other_score = (
                        float(other_metrics["weighted_wave_objective"])
                        + float(delta_lambda) * float(other_metrics["loss_frame_delta_unit_rms_l1"])
                        + float(flux_lambda) * float(other_metrics["loss_frame_spectral_flux_l1"])
                    )
                    margin = baseline_score - other_score
                    margins.append(margin)
                    if margin < 0.0:
                        win_count += 1
                total_wins += win_count
                sorted_margins = sorted(margins)
                matchup_rows.append(
                    {
                        "other_label": other_label,
                        "win_count": int(win_count),
                        "record_count": int(len(margins)),
                        "mean_margin": round(sum(margins) / max(1, len(margins)), 6),
                        "median_margin": round(sorted_margins[len(sorted_margins) // 2], 6),
                        "min_margin": round(sorted_margins[0], 6),
                        "max_margin": round(sorted_margins[-1], 6),
                    }
                )
            summary_rows.append(
                {
                    "delta_lambda": round(float(delta_lambda), 6),
                    "flux_lambda": round(float(flux_lambda), 6),
                    "total_wins": int(total_wins),
                    "max_total_wins": 2 * len(per_record_rows),
                    "matchups": matchup_rows,
                }
            )
    return sorted(
        summary_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["delta_lambda"]),
            float(item["flux_lambda"]),
        ),
    )


def build_directional_flux_candidate_grid_summary(
    *,
    per_record_rows: list[dict[str, object]],
    direction_lambda_grid: list[float],
    zero_jitter_lambda_grid: list[float],
) -> list[dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    for direction_lambda in direction_lambda_grid:
        for zero_jitter_lambda in zero_jitter_lambda_grid:
            matchup_rows = []
            total_wins = 0
            for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
                win_count = 0
                margins: list[float] = []
                for record_row in per_record_rows:
                    variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
                    baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
                    other_metrics = dict(variant_map[other_label]["scalar_metrics"])
                    baseline_score = (
                        float(baseline_metrics["weighted_wave_objective"])
                        + float(direction_lambda)
                        * float(baseline_metrics["loss_frame_spectral_flux_direction_cosine_active_0p05"])
                        + float(zero_jitter_lambda)
                        * float(baseline_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
                    )
                    other_score = (
                        float(other_metrics["weighted_wave_objective"])
                        + float(direction_lambda)
                        * float(other_metrics["loss_frame_spectral_flux_direction_cosine_active_0p05"])
                        + float(zero_jitter_lambda)
                        * float(other_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
                    )
                    margin = baseline_score - other_score
                    margins.append(margin)
                    if margin < 0.0:
                        win_count += 1
                total_wins += win_count
                sorted_margins = sorted(margins)
                matchup_rows.append(
                    {
                        "other_label": other_label,
                        "win_count": int(win_count),
                        "record_count": int(len(margins)),
                        "mean_margin": round(sum(margins) / max(1, len(margins)), 6),
                        "median_margin": round(sorted_margins[len(sorted_margins) // 2], 6),
                        "min_margin": round(sorted_margins[0], 6),
                        "max_margin": round(sorted_margins[-1], 6),
                    }
                )
            summary_rows.append(
                {
                    "direction_lambda": round(float(direction_lambda), 6),
                    "zero_jitter_lambda": round(float(zero_jitter_lambda), 6),
                    "total_wins": int(total_wins),
                    "max_total_wins": 2 * len(per_record_rows),
                    "matchups": matchup_rows,
                }
            )
    return sorted(
        summary_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["direction_lambda"]),
            float(item["zero_jitter_lambda"]),
        ),
    )


def build_active_template_candidate_grid_summary(
    *,
    per_record_rows: list[dict[str, object]],
    template_lambda_grid: list[float],
    zero_jitter_lambda_grid: list[float],
) -> list[dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    for template_lambda in template_lambda_grid:
        for zero_jitter_lambda in zero_jitter_lambda_grid:
            matchup_rows = []
            total_wins = 0
            for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
                win_count = 0
                margins: list[float] = []
                for record_row in per_record_rows:
                    variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
                    baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
                    other_metrics = dict(variant_map[other_label]["scalar_metrics"])
                    baseline_score = (
                        float(baseline_metrics["weighted_wave_objective"])
                        + float(template_lambda)
                        * float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"])
                        + float(zero_jitter_lambda)
                        * float(baseline_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
                    )
                    other_score = (
                        float(other_metrics["weighted_wave_objective"])
                        + float(template_lambda)
                        * float(other_metrics["loss_active_frame_template_excess_relu_0p02"])
                        + float(zero_jitter_lambda)
                        * float(other_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
                    )
                    margin = baseline_score - other_score
                    margins.append(margin)
                    if margin < 0.0:
                        win_count += 1
                total_wins += win_count
                sorted_margins = sorted(margins)
                matchup_rows.append(
                    {
                        "other_label": other_label,
                        "win_count": int(win_count),
                        "record_count": int(len(margins)),
                        "mean_margin": round(sum(margins) / max(1, len(margins)), 6),
                        "median_margin": round(sorted_margins[len(sorted_margins) // 2], 6),
                        "min_margin": round(sorted_margins[0], 6),
                        "max_margin": round(sorted_margins[-1], 6),
                    }
                )
            summary_rows.append(
                {
                    "template_lambda": round(float(template_lambda), 6),
                    "zero_jitter_lambda": round(float(zero_jitter_lambda), 6),
                    "total_wins": int(total_wins),
                    "max_total_wins": 2 * len(per_record_rows),
                    "matchups": matchup_rows,
                }
            )
    return sorted(
        summary_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["template_lambda"]),
            float(item["zero_jitter_lambda"]),
        ),
    )


def build_active_template_targeted_summary(
    *,
    per_record_rows: list[dict[str, object]],
    candidate_grid_summary: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    grid_rows = list(candidate_grid_summary or [])
    if not grid_rows:
        grid_rows = build_active_template_candidate_grid_summary(
            per_record_rows=per_record_rows,
            template_lambda_grid=ACTIVE_TEMPLATE_EXCESS_LAMBDA_GRID,
            zero_jitter_lambda_grid=ACTIVE_TEMPLATE_ZERO_JITTER_LAMBDA_GRID,
        )
    if not grid_rows:
        return {}
    best_combo = sorted(
        grid_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["zero_jitter_lambda"]),
            float(item["template_lambda"]),
        ),
    )[0]
    template_lambda = float(best_combo["template_lambda"])
    zero_jitter_lambda = float(best_combo["zero_jitter_lambda"])
    residual_rows = []
    win_rows = []
    for record_row in per_record_rows:
        variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
        baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
        baseline_score = (
            float(baseline_metrics["weighted_wave_objective"])
            + template_lambda * float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"])
            + zero_jitter_lambda * float(baseline_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
        )
        matchup_rows = []
        for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
            other_metrics = dict(variant_map[other_label]["scalar_metrics"])
            other_score = (
                float(other_metrics["weighted_wave_objective"])
                + template_lambda * float(other_metrics["loss_active_frame_template_excess_relu_0p02"])
                + zero_jitter_lambda * float(other_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"])
            )
            matchup_rows.append(
                {
                    "other_label": other_label,
                    "margin": round(baseline_score - other_score, 6),
                    "baseline_score": round(baseline_score, 6),
                    "other_score": round(other_score, 6),
                    "baseline_active_template_excess": round(
                        float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"]),
                        6,
                    ),
                    "other_active_template_excess": round(
                        float(other_metrics["loss_active_frame_template_excess_relu_0p02"]),
                        6,
                    ),
                }
            )
        row = {
            "record_id": str(record_row["record_id"]),
            "mean_margin": round(sum(float(item["margin"]) for item in matchup_rows) / len(matchup_rows), 6),
            "matchups": matchup_rows,
            "target_stationarity": {
                "aligned_frame_template_cosine_mean": round(float(baseline_metrics["aligned_frame_template_cosine_mean"]), 6),
                "aligned_frame_adjacent_cosine_mean": round(float(baseline_metrics["aligned_frame_adjacent_cosine_mean"]), 6),
                "aligned_frame_rms_cv": round(float(baseline_metrics["aligned_frame_rms_cv"]), 6),
            },
            "baseline_scalar_metrics": {
                "weighted_wave_objective": round(float(baseline_metrics["weighted_wave_objective"]), 6),
                "loss_active_frame_template_excess_relu_0p02": round(
                    float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"]),
                    6,
                ),
                "loss_frame_spectral_flux_zero_target_jitter_0p05": round(
                    float(baseline_metrics["loss_frame_spectral_flux_zero_target_jitter_0p05"]),
                    6,
                ),
            },
        }
        if any(float(item["margin"]) > 0.0 for item in matchup_rows):
            residual_rows.append(row)
        else:
            win_rows.append(row)

    def mean_of(rows: list[dict[str, object]], selector: str) -> float:
        if not rows:
            return 0.0
        parts = selector.split(".")
        values = []
        for row in rows:
            payload = row
            for key in parts:
                payload = payload[key]  # type: ignore[index]
            values.append(float(payload))
        return round(sum(values) / len(values), 6)

    return {
        "best_combo": {
            "template_lambda": round(template_lambda, 6),
            "zero_jitter_lambda": round(zero_jitter_lambda, 6),
            "total_wins": int(best_combo["total_wins"]),
            "max_total_wins": int(best_combo["max_total_wins"]),
        },
        "residual_losses": sorted(
            residual_rows,
            key=lambda item: (-float(item["mean_margin"]), str(item["record_id"])),
        ),
        "stationary_risk_summary": {
            "residual_record_count": int(len(residual_rows)),
            "win_record_count": int(len(win_rows)),
            "residual_mean_aligned_frame_template_cosine": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_template_cosine_mean",
            ),
            "win_mean_aligned_frame_template_cosine": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_template_cosine_mean",
            ),
            "residual_mean_aligned_frame_adjacent_cosine": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_adjacent_cosine_mean",
            ),
            "win_mean_aligned_frame_adjacent_cosine": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_adjacent_cosine_mean",
            ),
            "residual_mean_aligned_frame_rms_cv": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_rms_cv",
            ),
            "win_mean_aligned_frame_rms_cv": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_rms_cv",
            ),
            "residual_mean_baseline_active_template_excess": mean_of(
                residual_rows,
                "baseline_scalar_metrics.loss_active_frame_template_excess_relu_0p02",
            ),
            "win_mean_baseline_active_template_excess": mean_of(
                win_rows,
                "baseline_scalar_metrics.loss_active_frame_template_excess_relu_0p02",
            ),
            "residual_mean_baseline_zero_jitter": mean_of(
                residual_rows,
                "baseline_scalar_metrics.loss_frame_spectral_flux_zero_target_jitter_0p05",
            ),
            "win_mean_baseline_zero_jitter": mean_of(
                win_rows,
                "baseline_scalar_metrics.loss_frame_spectral_flux_zero_target_jitter_0p05",
            ),
        },
    }


def build_active_template_delta_candidate_grid_summary(
    *,
    per_record_rows: list[dict[str, object]],
    template_lambda_grid: list[float],
    delta_lambda_grid: list[float],
) -> list[dict[str, object]]:
    summary_rows: list[dict[str, object]] = []
    for template_lambda in template_lambda_grid:
        for delta_lambda in delta_lambda_grid:
            matchup_rows = []
            total_wins = 0
            for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
                win_count = 0
                margins: list[float] = []
                for record_row in per_record_rows:
                    variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
                    baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
                    other_metrics = dict(variant_map[other_label]["scalar_metrics"])
                    baseline_score = (
                        float(baseline_metrics["weighted_wave_objective"])
                        + float(template_lambda)
                        * float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"])
                        + float(delta_lambda) * float(baseline_metrics["loss_frame_delta_unit_rms_l1"])
                    )
                    other_score = (
                        float(other_metrics["weighted_wave_objective"])
                        + float(template_lambda)
                        * float(other_metrics["loss_active_frame_template_excess_relu_0p02"])
                        + float(delta_lambda) * float(other_metrics["loss_frame_delta_unit_rms_l1"])
                    )
                    margin = baseline_score - other_score
                    margins.append(margin)
                    if margin < 0.0:
                        win_count += 1
                total_wins += win_count
                sorted_margins = sorted(margins)
                matchup_rows.append(
                    {
                        "other_label": other_label,
                        "win_count": int(win_count),
                        "record_count": int(len(margins)),
                        "mean_margin": round(sum(margins) / max(1, len(margins)), 6),
                        "median_margin": round(sorted_margins[len(sorted_margins) // 2], 6),
                        "min_margin": round(sorted_margins[0], 6),
                        "max_margin": round(sorted_margins[-1], 6),
                    }
                )
            summary_rows.append(
                {
                    "template_lambda": round(float(template_lambda), 6),
                    "delta_lambda": round(float(delta_lambda), 6),
                    "total_wins": int(total_wins),
                    "max_total_wins": 2 * len(per_record_rows),
                    "matchups": matchup_rows,
                }
            )
    return sorted(
        summary_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["delta_lambda"]),
            float(item["template_lambda"]),
        ),
    )


def build_active_template_delta_targeted_summary(
    *,
    per_record_rows: list[dict[str, object]],
    candidate_grid_summary: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    grid_rows = list(candidate_grid_summary or [])
    if not grid_rows:
        grid_rows = build_active_template_delta_candidate_grid_summary(
            per_record_rows=per_record_rows,
            template_lambda_grid=ACTIVE_TEMPLATE_EXCESS_LAMBDA_GRID,
            delta_lambda_grid=ACTIVE_TEMPLATE_DELTA_LAMBDA_GRID,
        )
    if not grid_rows:
        return {}
    best_combo = sorted(
        grid_rows,
        key=lambda item: (
            -int(item["total_wins"]),
            float(item["delta_lambda"]),
            float(item["template_lambda"]),
        ),
    )[0]
    template_lambda = float(best_combo["template_lambda"])
    delta_lambda = float(best_combo["delta_lambda"])
    residual_rows = []
    win_rows = []
    for record_row in per_record_rows:
        variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
        baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
        baseline_score = (
            float(baseline_metrics["weighted_wave_objective"])
            + template_lambda * float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"])
            + delta_lambda * float(baseline_metrics["loss_frame_delta_unit_rms_l1"])
        )
        matchup_rows = []
        for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
            other_metrics = dict(variant_map[other_label]["scalar_metrics"])
            other_score = (
                float(other_metrics["weighted_wave_objective"])
                + template_lambda * float(other_metrics["loss_active_frame_template_excess_relu_0p02"])
                + delta_lambda * float(other_metrics["loss_frame_delta_unit_rms_l1"])
            )
            matchup_rows.append(
                {
                    "other_label": other_label,
                    "margin": round(baseline_score - other_score, 6),
                    "baseline_score": round(baseline_score, 6),
                    "other_score": round(other_score, 6),
                    "baseline_active_template_excess": round(
                        float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"]),
                        6,
                    ),
                    "other_active_template_excess": round(
                        float(other_metrics["loss_active_frame_template_excess_relu_0p02"]),
                        6,
                    ),
                    "baseline_frame_delta": round(float(baseline_metrics["loss_frame_delta_unit_rms_l1"]), 6),
                    "other_frame_delta": round(float(other_metrics["loss_frame_delta_unit_rms_l1"]), 6),
                }
            )
        row = {
            "record_id": str(record_row["record_id"]),
            "mean_margin": round(sum(float(item["margin"]) for item in matchup_rows) / len(matchup_rows), 6),
            "matchups": matchup_rows,
            "target_stationarity": {
                "aligned_frame_template_cosine_mean": round(float(baseline_metrics["aligned_frame_template_cosine_mean"]), 6),
                "aligned_frame_adjacent_cosine_mean": round(float(baseline_metrics["aligned_frame_adjacent_cosine_mean"]), 6),
                "aligned_frame_rms_cv": round(float(baseline_metrics["aligned_frame_rms_cv"]), 6),
            },
            "baseline_scalar_metrics": {
                "weighted_wave_objective": round(float(baseline_metrics["weighted_wave_objective"]), 6),
                "loss_active_frame_template_excess_relu_0p02": round(
                    float(baseline_metrics["loss_active_frame_template_excess_relu_0p02"]),
                    6,
                ),
                "loss_frame_delta_unit_rms_l1": round(float(baseline_metrics["loss_frame_delta_unit_rms_l1"]), 6),
            },
        }
        if any(float(item["margin"]) > 0.0 for item in matchup_rows):
            residual_rows.append(row)
        else:
            win_rows.append(row)

    def mean_of(rows: list[dict[str, object]], selector: str) -> float:
        if not rows:
            return 0.0
        parts = selector.split(".")
        values = []
        for row in rows:
            payload = row
            for key in parts:
                payload = payload[key]  # type: ignore[index]
            values.append(float(payload))
        return round(sum(values) / len(values), 6)

    return {
        "best_combo": {
            "template_lambda": round(template_lambda, 6),
            "delta_lambda": round(delta_lambda, 6),
            "total_wins": int(best_combo["total_wins"]),
            "max_total_wins": int(best_combo["max_total_wins"]),
        },
        "residual_losses": sorted(
            residual_rows,
            key=lambda item: (-float(item["mean_margin"]), str(item["record_id"])),
        ),
        "stationary_risk_summary": {
            "residual_record_count": int(len(residual_rows)),
            "win_record_count": int(len(win_rows)),
            "residual_mean_aligned_frame_template_cosine": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_template_cosine_mean",
            ),
            "win_mean_aligned_frame_template_cosine": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_template_cosine_mean",
            ),
            "residual_mean_aligned_frame_adjacent_cosine": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_adjacent_cosine_mean",
            ),
            "win_mean_aligned_frame_adjacent_cosine": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_adjacent_cosine_mean",
            ),
            "residual_mean_aligned_frame_rms_cv": mean_of(
                residual_rows,
                "target_stationarity.aligned_frame_rms_cv",
            ),
            "win_mean_aligned_frame_rms_cv": mean_of(
                win_rows,
                "target_stationarity.aligned_frame_rms_cv",
            ),
            "residual_mean_baseline_active_template_excess": mean_of(
                residual_rows,
                "baseline_scalar_metrics.loss_active_frame_template_excess_relu_0p02",
            ),
            "win_mean_baseline_active_template_excess": mean_of(
                win_rows,
                "baseline_scalar_metrics.loss_active_frame_template_excess_relu_0p02",
            ),
            "residual_mean_baseline_frame_delta": mean_of(
                residual_rows,
                "baseline_scalar_metrics.loss_frame_delta_unit_rms_l1",
            ),
            "win_mean_baseline_frame_delta": mean_of(
                win_rows,
                "baseline_scalar_metrics.loss_frame_delta_unit_rms_l1",
            ),
        },
    }


def build_transition_targeted_hard_failure_summary(
    *,
    per_record_rows: list[dict[str, object]],
    combo_grid_summary: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    best_grid_rows = list(combo_grid_summary or [])
    if not best_grid_rows:
        best_grid_rows = build_transition_combo_grid_summary(
            per_record_rows=per_record_rows,
            delta_lambda_grid=TRANSITION_COMBO_DELTA_LAMBDA_GRID,
            flux_lambda_grid=TRANSITION_COMBO_FLUX_LAMBDA_GRID,
        )
    if not best_grid_rows:
        return {}
    best_combo = dict(best_grid_rows[0])
    delta_lambda = float(best_combo["delta_lambda"])
    flux_lambda = float(best_combo["flux_lambda"])
    matchups = []
    repeated_loss_counter: dict[str, int] = {}
    repeated_win_counter: dict[str, int] = {}
    for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
        margin_rows = []
        for record_row in per_record_rows:
            variant_map = {str(item["label"]): item for item in list(record_row["variants"])}
            baseline_metrics = dict(variant_map["baseline_decode_route"]["scalar_metrics"])
            other_metrics = dict(variant_map[other_label]["scalar_metrics"])
            baseline_score = (
                float(baseline_metrics["weighted_wave_objective"])
                + delta_lambda * float(baseline_metrics["loss_frame_delta_unit_rms_l1"])
                + flux_lambda * float(baseline_metrics["loss_frame_spectral_flux_l1"])
            )
            other_score = (
                float(other_metrics["weighted_wave_objective"])
                + delta_lambda * float(other_metrics["loss_frame_delta_unit_rms_l1"])
                + flux_lambda * float(other_metrics["loss_frame_spectral_flux_l1"])
            )
            margin = baseline_score - other_score
            row = {
                "record_id": str(record_row["record_id"]),
                "margin": round(float(margin), 6),
                "baseline_candidate_score": round(float(baseline_score), 6),
                "other_candidate_score": round(float(other_score), 6),
                "baseline_weighted_wave_objective": round(float(baseline_metrics["weighted_wave_objective"]), 6),
                "baseline_loss_frame_delta_unit_rms_l1": round(float(baseline_metrics["loss_frame_delta_unit_rms_l1"]), 6),
                "baseline_loss_frame_spectral_flux_l1": round(float(baseline_metrics["loss_frame_spectral_flux_l1"]), 6),
                "baseline_loss_frame_unit_rms_logspec_l1": round(float(baseline_metrics["loss_frame_unit_rms_logspec_l1"]), 6),
                "baseline_decoded_frame_template_cosine_mean": round(
                    float(baseline_metrics["decoded_frame_template_cosine_mean"]),
                    6,
                ),
                "baseline_decoded_frame_rms_to_aligned_frame_rms_corr": round(
                    float(baseline_metrics["decoded_frame_rms_to_aligned_frame_rms_corr"]),
                    6,
                ),
                "baseline_aligned_frame_adjacent_cosine_mean": round(
                    float(baseline_metrics["aligned_frame_adjacent_cosine_mean"]),
                    6,
                ),
                "baseline_aligned_frame_rms_cv": round(float(baseline_metrics["aligned_frame_rms_cv"]), 6),
            }
            margin_rows.append(row)
            if float(margin) > 0.0:
                repeated_loss_counter[row["record_id"]] = repeated_loss_counter.get(row["record_id"], 0) + 1
            else:
                repeated_win_counter[row["record_id"]] = repeated_win_counter.get(row["record_id"], 0) + 1
        margin_rows = sorted(margin_rows, key=lambda item: float(item["margin"]))
        matchups.append(
            {
                "other_label": other_label,
                "best_wins": margin_rows[:6],
                "worst_losses": list(reversed(margin_rows[-6:])),
            }
        )
    repeated_hard_failures = sorted(
        (
            {
                "record_id": record_id,
                "loss_count": int(count),
            }
            for record_id, count in repeated_loss_counter.items()
            if int(count) >= 2
        ),
        key=lambda item: (-int(item["loss_count"]), str(item["record_id"])),
    )
    repeated_easy_wins = sorted(
        (
            {
                "record_id": record_id,
                "win_count": int(count),
            }
            for record_id, count in repeated_win_counter.items()
            if int(count) >= 2
        ),
        key=lambda item: (-int(item["win_count"]), str(item["record_id"])),
    )
    return {
        "best_combo": {
            "delta_lambda": round(delta_lambda, 6),
            "flux_lambda": round(flux_lambda, 6),
            "total_wins": int(best_combo["total_wins"]),
            "max_total_wins": int(best_combo["max_total_wins"]),
        },
        "repeated_hard_failures": repeated_hard_failures,
        "repeated_easy_wins": repeated_easy_wins,
        "matchups": matchups,
    }


def build_transition_hard_case_breakdown(
    *,
    hard_record_ids: list[str],
    package_entries: list[dict[str, object]],
    model: torch.nn.Module,
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    waveform_weight: float,
    stft_weight: float,
    rms_guard_weight: float,
    best_combo: dict[str, object],
) -> list[dict[str, object]]:
    hard_record_id_set = {str(item) for item in hard_record_ids}
    if not hard_record_id_set:
        return []
    delta_lambda = float(best_combo.get("delta_lambda", 0.0))
    flux_lambda = float(best_combo.get("flux_lambda", 0.0))
    package_map = {str(item["record_id"]): item for item in package_entries}
    rows = []
    with torch.no_grad():
        for record_id in sorted(hard_record_id_set):
            entry = package_map.get(record_id)
            if entry is None:
                continue
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            aligned_waveform = batch["aligned_waveform"].to(torch.float32)
            frame_length = int(runtime["frame_length"])
            hop_length = int(runtime["hop_length"])
            sample_rate = int(runtime["sample_rate"])
            target_frames = frame_waveform_sequence(
                waveform=aligned_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
            )
            target_frame_rms = compute_centered_frame_rms(target_frames)

            baseline_outputs = model(
                periodic_branch_features=batch["periodic_branch_features"].to(device=device, dtype=torch.float32),
                noise_branch_features=batch["noise_branch_features"].to(device=device, dtype=torch.float32),
            )
            baseline_predicted_activity = torch.maximum(
                baseline_outputs["periodic_gate"],
                baseline_outputs["noise_gate"],
            )
            baseline_waveform = reconstruct_waveform_from_frames(
                waveform_frames=baseline_outputs["waveform_frames"],
                frame_length=frame_length,
                hop_length=hop_length,
                frame_gains=baseline_predicted_activity if bool(use_predicted_activity_gate) else None,
                frame_gain_floor=float(predicted_activity_gate_floor),
                frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                frame_gain_apply_mode=predicted_activity_gate_apply_mode,
            ).detach().cpu().to(torch.float32)
            variant_payloads = {
                "baseline_decode_route": {
                    "decoded_waveform": baseline_waveform,
                    "scalar_metrics": summarize_objective_variant(
                        decoded_waveform=baseline_waveform,
                        aligned_waveform=aligned_waveform,
                        frame_length=frame_length,
                        hop_length=hop_length,
                        sample_rate=sample_rate,
                        waveform_weight=float(waveform_weight),
                        stft_weight=float(stft_weight),
                        rms_guard_weight=float(rms_guard_weight),
                    ),
                }
            }
            for variant in OBJECTIVE_COLLAPSE_VARIANTS[1:]:
                fixed_template_frames, _ = build_fixed_template_target_rms_frames(
                    target_frames=target_frames,
                    template_mode=str(variant["template_mode"]),
                    target_frame_rms=target_frame_rms,
                )
                synthetic_waveform = reconstruct_waveform_from_frames(
                    waveform_frames=fixed_template_frames,
                    frame_length=frame_length,
                    hop_length=hop_length,
                ).detach().cpu().to(torch.float32)
                variant_payloads[str(variant["label"])] = {
                    "decoded_waveform": synthetic_waveform,
                    "scalar_metrics": summarize_objective_variant(
                        decoded_waveform=synthetic_waveform,
                        aligned_waveform=aligned_waveform,
                        frame_length=frame_length,
                        hop_length=hop_length,
                        sample_rate=sample_rate,
                        waveform_weight=float(waveform_weight),
                        stft_weight=float(stft_weight),
                        rms_guard_weight=float(rms_guard_weight),
                    ),
                }
            oracle_candidate_rows = []
            for other_label in ["oracle_sine_target_rms", "oracle_active_frame_target_rms"]:
                metrics = dict(variant_payloads[other_label]["scalar_metrics"])
                candidate_score = (
                    float(metrics["weighted_wave_objective"])
                    + delta_lambda * float(metrics["loss_frame_delta_unit_rms_l1"])
                    + flux_lambda * float(metrics["loss_frame_spectral_flux_l1"])
                )
                oracle_candidate_rows.append(
                    {
                        "label": other_label,
                        "candidate_score": round(candidate_score, 6),
                        "margin_vs_baseline": round(
                            (
                                float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["weighted_wave_objective"])
                                + delta_lambda * float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["loss_frame_delta_unit_rms_l1"])
                                + flux_lambda * float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["loss_frame_spectral_flux_l1"])
                            )
                            - candidate_score,
                            6,
                        ),
                    }
                )
            reference_oracle = sorted(
                oracle_candidate_rows,
                key=lambda item: (float(item["candidate_score"]), str(item["label"])),
            )[0]
            baseline_breakdown = compute_transition_local_breakdown(
                decoded_waveform=variant_payloads["baseline_decode_route"]["decoded_waveform"],
                aligned_waveform=aligned_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                sample_rate=sample_rate,
                delta_lambda=delta_lambda,
                flux_lambda=flux_lambda,
            )
            oracle_breakdown = compute_transition_local_breakdown(
                decoded_waveform=variant_payloads[str(reference_oracle["label"])]["decoded_waveform"],
                aligned_waveform=aligned_waveform,
                frame_length=frame_length,
                hop_length=hop_length,
                sample_rate=sample_rate,
                delta_lambda=delta_lambda,
                flux_lambda=flux_lambda,
            )
            local_windows = summarize_transition_failure_windows(
                baseline_local_score=baseline_breakdown["local_transition_combo_score"],
                oracle_local_score=oracle_breakdown["local_transition_combo_score"],
                baseline_delta_error=baseline_breakdown["delta_error"],
                oracle_delta_error=oracle_breakdown["delta_error"],
                baseline_flux_error=baseline_breakdown["flux_error"],
                oracle_flux_error=oracle_breakdown["flux_error"],
                hop_length=hop_length,
                sample_rate=sample_rate,
            )
            duration_sec = float(aligned_waveform.shape[0]) / float(sample_rate)
            pattern_summary = summarize_transition_pattern(
                failure_windows=local_windows,
                duration_sec=duration_sec,
            )
            failure_signature = summarize_transition_failure_signature(
                baseline_breakdown=baseline_breakdown,
                oracle_breakdown=oracle_breakdown,
                duration_sec=duration_sec,
                hop_length=hop_length,
                sample_rate=sample_rate,
                delta_lambda=delta_lambda,
                flux_lambda=flux_lambda,
                pattern_summary=pattern_summary,
            )
            flux_alignment_summary = summarize_flux_alignment_signature(
                baseline_breakdown=baseline_breakdown,
                oracle_breakdown=oracle_breakdown,
                failure_signature=failure_signature,
            )
            rows.append(
                {
                    "record_id": record_id,
                    "training_package_path": package_path.as_posix(),
                    "best_combo": {
                        "delta_lambda": round(delta_lambda, 6),
                        "flux_lambda": round(flux_lambda, 6),
                    },
                    "reference_oracle": reference_oracle,
                    "baseline_candidate_score": round(
                        float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["weighted_wave_objective"])
                        + delta_lambda
                        * float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["loss_frame_delta_unit_rms_l1"])
                        + flux_lambda
                        * float(variant_payloads["baseline_decode_route"]["scalar_metrics"]["loss_frame_spectral_flux_l1"]),
                        6,
                    ),
                    "baseline_scalar_metrics": variant_payloads["baseline_decode_route"]["scalar_metrics"],
                    "reference_oracle_scalar_metrics": variant_payloads[str(reference_oracle["label"])]["scalar_metrics"],
                    "transition_local_summary": {
                        "duration_sec": round(duration_sec, 6),
                        "baseline_local_score_mean": round(
                            float(baseline_breakdown["local_transition_combo_score"].mean().item()),
                            6,
                        ),
                        "reference_oracle_local_score_mean": round(
                            float(oracle_breakdown["local_transition_combo_score"].mean().item()),
                            6,
                        ),
                        "positive_advantage_fraction": round(
                            float(
                                (baseline_breakdown["local_transition_combo_score"] - oracle_breakdown["local_transition_combo_score"] > 0.0)
                                .to(torch.float32)
                                .mean()
                                .item()
                            ),
                            6,
                        ),
                    },
                    "pattern_summary": pattern_summary,
                    "failure_signature": failure_signature,
                    "flux_alignment_summary": flux_alignment_summary,
                    "top_failure_windows": local_windows[:5],
                }
            )
    return rows


def compute_transition_local_breakdown(
    *,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
    delta_lambda: float,
    flux_lambda: float,
) -> dict[str, torch.Tensor]:
    decoded_analysis_frames = frame_waveform_sequence(
        waveform=decoded_waveform,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    aligned_analysis_frames = frame_waveform_sequence(
        waveform=aligned_waveform,
        frame_length=frame_length,
        hop_length=hop_length,
        target_frame_count=int(decoded_analysis_frames.shape[0]),
    )
    decoded_normalized_frames = normalize_frames_unit_rms(decoded_analysis_frames)
    aligned_normalized_frames = normalize_frames_unit_rms(aligned_analysis_frames)
    decoded_frame_logspec = compute_frame_logspec(decoded_normalized_frames)
    aligned_frame_logspec = compute_frame_logspec(aligned_normalized_frames)
    decoded_frame_deltas = compute_adjacent_deltas(decoded_normalized_frames)
    aligned_frame_deltas = compute_adjacent_deltas(aligned_normalized_frames)
    decoded_spectral_flux = compute_adjacent_deltas(decoded_frame_logspec)
    aligned_spectral_flux = compute_adjacent_deltas(aligned_frame_logspec)
    delta_error = (decoded_frame_deltas - aligned_frame_deltas).abs().mean(dim=1)
    flux_error = (decoded_spectral_flux - aligned_spectral_flux).abs().mean(dim=1)
    local_transition_combo_score = delta_lambda * delta_error + flux_lambda * flux_error
    return {
        "delta_error": delta_error,
        "flux_error": flux_error,
        "decoded_delta_magnitude": decoded_frame_deltas.abs().mean(dim=1),
        "aligned_delta_magnitude": aligned_frame_deltas.abs().mean(dim=1),
        "decoded_flux_magnitude": decoded_spectral_flux.abs().mean(dim=1),
        "aligned_flux_magnitude": aligned_spectral_flux.abs().mean(dim=1),
        "decoded_spectral_flux": decoded_spectral_flux,
        "aligned_spectral_flux": aligned_spectral_flux,
        "local_transition_combo_score": local_transition_combo_score,
    }


def summarize_transition_failure_windows(
    *,
    baseline_local_score: torch.Tensor,
    oracle_local_score: torch.Tensor,
    baseline_delta_error: torch.Tensor,
    oracle_delta_error: torch.Tensor,
    baseline_flux_error: torch.Tensor,
    oracle_flux_error: torch.Tensor,
    hop_length: int,
    sample_rate: int,
) -> list[dict[str, object]]:
    local_advantage = baseline_local_score - oracle_local_score
    positive_indices = [int(index) for index, value in enumerate(local_advantage.tolist()) if float(value) > 0.0]
    if not positive_indices:
        return []
    windows: list[tuple[int, int]] = []
    start_index = positive_indices[0]
    previous_index = start_index
    for current_index in positive_indices[1:]:
        if current_index == previous_index + 1:
            previous_index = current_index
            continue
        windows.append((start_index, previous_index))
        start_index = current_index
        previous_index = current_index
    windows.append((start_index, previous_index))
    rows = []
    for start_index, end_index in windows:
        local_slice = slice(start_index, end_index + 1)
        advantage_slice = local_advantage[local_slice]
        baseline_delta_slice = baseline_delta_error[local_slice]
        oracle_delta_slice = oracle_delta_error[local_slice]
        baseline_flux_slice = baseline_flux_error[local_slice]
        oracle_flux_slice = oracle_flux_error[local_slice]
        rows.append(
            {
                "start_transition_index": int(start_index),
                "end_transition_index": int(end_index),
                "start_sec": round(float(start_index * hop_length / sample_rate), 6),
                "end_sec": round(float((end_index + 1) * hop_length / sample_rate), 6),
                "frame_count": int(end_index - start_index + 1),
                "mean_advantage": round(float(advantage_slice.mean().item()), 6),
                "total_advantage": round(float(advantage_slice.sum().item()), 6),
                "max_advantage": round(float(advantage_slice.max().item()), 6),
                "baseline_delta_error_mean": round(float(baseline_delta_slice.mean().item()), 6),
                "reference_oracle_delta_error_mean": round(float(oracle_delta_slice.mean().item()), 6),
                "baseline_flux_error_mean": round(float(baseline_flux_slice.mean().item()), 6),
                "reference_oracle_flux_error_mean": round(float(oracle_flux_slice.mean().item()), 6),
            }
        )
    return sorted(
        rows,
        key=lambda item: (-float(item["total_advantage"]), -float(item["mean_advantage"]), int(item["start_transition_index"])),
    )


def summarize_transition_pattern(
    *,
    failure_windows: list[dict[str, object]],
    duration_sec: float,
    boundary_sec: float = 0.05,
) -> dict[str, object]:
    if not failure_windows:
        return {
            "failure_window_count": 0,
            "total_positive_advantage": 0.0,
            "onset_advantage_share": 0.0,
            "offset_advantage_share": 0.0,
            "boundary_advantage_share": 0.0,
            "interior_advantage_share": 0.0,
            "max_window_share": 0.0,
            "dominant_region": "none",
            "dominant_window_sec_range": None,
            "pattern_label": "no_failure_windows",
        }
    onset_advantage = 0.0
    offset_advantage = 0.0
    interior_advantage = 0.0
    dominant_window = max(failure_windows, key=lambda item: float(item["total_advantage"]))
    total_positive_advantage = sum(float(item["total_advantage"]) for item in failure_windows)
    for item in failure_windows:
        start_sec = float(item["start_sec"])
        end_sec = float(item["end_sec"])
        total_advantage = float(item["total_advantage"])
        region = classify_transition_window_region(
            start_sec=start_sec,
            end_sec=end_sec,
            duration_sec=float(duration_sec),
            boundary_sec=float(boundary_sec),
        )
        if region == "onset":
            onset_advantage += total_advantage
        elif region == "offset":
            offset_advantage += total_advantage
        elif region == "boundary_both":
            onset_advantage += total_advantage / 2.0
            offset_advantage += total_advantage / 2.0
        else:
            interior_advantage += total_advantage
    boundary_advantage = onset_advantage + offset_advantage
    max_window_share = 0.0 if total_positive_advantage <= 1.0e-8 else float(dominant_window["total_advantage"]) / total_positive_advantage
    onset_share = 0.0 if total_positive_advantage <= 1.0e-8 else onset_advantage / total_positive_advantage
    offset_share = 0.0 if total_positive_advantage <= 1.0e-8 else offset_advantage / total_positive_advantage
    boundary_share = 0.0 if total_positive_advantage <= 1.0e-8 else boundary_advantage / total_positive_advantage
    interior_share = 0.0 if total_positive_advantage <= 1.0e-8 else interior_advantage / total_positive_advantage
    dominant_region = classify_transition_window_region(
        start_sec=float(dominant_window["start_sec"]),
        end_sec=float(dominant_window["end_sec"]),
        duration_sec=float(duration_sec),
        boundary_sec=float(boundary_sec),
    )
    pattern_label = "mixed_failure"
    if boundary_share >= 0.6 and dominant_region in {"onset", "offset", "boundary_both"}:
        pattern_label = "boundary_dominated"
    elif interior_share >= 0.5 and max_window_share >= 0.4:
        pattern_label = "isolated_interior_window"
    return {
        "failure_window_count": int(len(failure_windows)),
        "total_positive_advantage": round(total_positive_advantage, 6),
        "onset_advantage_share": round(onset_share, 6),
        "offset_advantage_share": round(offset_share, 6),
        "boundary_advantage_share": round(boundary_share, 6),
        "interior_advantage_share": round(interior_share, 6),
        "max_window_share": round(max_window_share, 6),
        "dominant_region": dominant_region,
        "dominant_window_sec_range": [
            round(float(dominant_window["start_sec"]), 6),
            round(float(dominant_window["end_sec"]), 6),
        ],
        "pattern_label": pattern_label,
    }


def summarize_transition_failure_signature(
    *,
    baseline_breakdown: dict[str, torch.Tensor],
    oracle_breakdown: dict[str, torch.Tensor],
    duration_sec: float,
    hop_length: int,
    sample_rate: int,
    delta_lambda: float,
    flux_lambda: float,
    pattern_summary: dict[str, object],
    boundary_sec: float = 0.05,
    near_zero_target_strength: float = 0.1,
    near_zero_oracle_score: float = 0.1,
) -> dict[str, object]:
    baseline_delta_error = baseline_breakdown["delta_error"]
    oracle_delta_error = oracle_breakdown["delta_error"]
    baseline_flux_error = baseline_breakdown["flux_error"]
    oracle_flux_error = oracle_breakdown["flux_error"]
    delta_advantage = float(delta_lambda) * (baseline_delta_error - oracle_delta_error)
    flux_advantage = float(flux_lambda) * (baseline_flux_error - oracle_flux_error)
    local_advantage = delta_advantage + flux_advantage
    positive_mask = local_advantage > 0.0
    positive_advantage_total = float(local_advantage[positive_mask].sum().item()) if bool(positive_mask.any()) else 0.0
    target_transition_strength = (
        float(delta_lambda) * baseline_breakdown["aligned_delta_magnitude"]
        + float(flux_lambda) * baseline_breakdown["aligned_flux_magnitude"]
    )
    reference_oracle_local_score = (
        float(delta_lambda) * oracle_delta_error
        + float(flux_lambda) * oracle_flux_error
    )
    if target_transition_strength.numel() == 0:
        return {
            "component_label": "no_transitions",
            "signature_label": "no_transitions",
        }
    q25 = float(torch.quantile(target_transition_strength, 0.25).item())
    q75 = float(torch.quantile(target_transition_strength, 0.75).item())
    transition_sec = (
        torch.arange(target_transition_strength.shape[0], dtype=torch.float32) * float(hop_length) / float(sample_rate)
    )
    boundary_mask = (transition_sec <= float(boundary_sec)) | (
        transition_sec >= max(0.0, float(duration_sec) - float(boundary_sec))
    )
    interior_mask = ~boundary_mask
    low_motion_mask = target_transition_strength <= q25
    high_motion_mask = target_transition_strength >= q75
    near_zero_target_mask = target_transition_strength <= float(near_zero_target_strength)
    near_zero_oracle_mask = reference_oracle_local_score <= float(near_zero_oracle_score)

    def weighted_positive_share(mask: torch.Tensor) -> float:
        if positive_advantage_total <= 1.0e-8:
            return 0.0
        overlap = positive_mask & mask
        if not bool(overlap.any()):
            return 0.0
        return float(local_advantage[overlap].sum().item()) / positive_advantage_total

    flux_dominant_share = weighted_positive_share(flux_advantage > delta_advantage)
    delta_dominant_share = weighted_positive_share(delta_advantage >= flux_advantage)
    component_label = "mixed_components"
    if flux_dominant_share >= 0.6:
        component_label = "flux_dominated"
    elif delta_dominant_share >= 0.6:
        component_label = "delta_dominated"

    boundary_share = float(pattern_summary.get("boundary_advantage_share", 0.0))
    interior_high_motion_share = weighted_positive_share(interior_mask & high_motion_mask)
    boundary_high_motion_share = weighted_positive_share(boundary_mask & high_motion_mask)
    near_zero_target_share = weighted_positive_share(near_zero_target_mask)
    near_zero_oracle_share = weighted_positive_share(near_zero_oracle_mask)
    signature_label = "mixed_transition_gap"
    if near_zero_target_share >= 0.15 and near_zero_oracle_share >= 0.15:
        signature_label = "steady_zero_target_jitter"
    elif boundary_share >= 0.6 and boundary_high_motion_share >= 0.2:
        signature_label = (
            "boundary_high_motion_flux_gap" if component_label == "flux_dominated" else "boundary_high_motion_transition_gap"
        )
    elif interior_high_motion_share >= 0.25:
        signature_label = (
            "interior_high_motion_flux_gap" if component_label == "flux_dominated" else "interior_high_motion_transition_gap"
        )
    elif weighted_positive_share(low_motion_mask) >= 0.25:
        signature_label = "low_motion_transition_gap"

    return {
        "component_label": component_label,
        "signature_label": signature_label,
        "target_transition_strength_q25": round(q25, 6),
        "target_transition_strength_q75": round(q75, 6),
        "low_motion_advantage_share_q25": round(weighted_positive_share(low_motion_mask), 6),
        "high_motion_advantage_share_q75": round(weighted_positive_share(high_motion_mask), 6),
        "boundary_low_motion_advantage_share_q25": round(weighted_positive_share(boundary_mask & low_motion_mask), 6),
        "boundary_high_motion_advantage_share_q75": round(boundary_high_motion_share, 6),
        "interior_low_motion_advantage_share_q25": round(weighted_positive_share(interior_mask & low_motion_mask), 6),
        "interior_high_motion_advantage_share_q75": round(interior_high_motion_share, 6),
        "near_zero_target_advantage_share_0p1": round(near_zero_target_share, 6),
        "near_zero_reference_oracle_error_advantage_share_0p1": round(near_zero_oracle_share, 6),
        "flux_dominant_advantage_share": round(flux_dominant_share, 6),
        "delta_dominant_advantage_share": round(delta_dominant_share, 6),
    }


def summarize_flux_alignment_signature(
    *,
    baseline_breakdown: dict[str, torch.Tensor],
    oracle_breakdown: dict[str, torch.Tensor],
    failure_signature: dict[str, object],
    active_target_flux_threshold: float = 0.05,
) -> dict[str, object]:
    baseline_flux = baseline_breakdown["decoded_spectral_flux"]
    oracle_flux = oracle_breakdown["decoded_spectral_flux"]
    aligned_flux = baseline_breakdown["aligned_spectral_flux"]
    baseline_flux_error = baseline_breakdown["flux_error"]
    oracle_flux_error = oracle_breakdown["flux_error"]
    positive_mask = baseline_flux_error > oracle_flux_error
    if not bool(positive_mask.any()):
        return {
            "alignment_label": "no_positive_flux_advantage",
        }

    baseline_cosine = compute_rowwise_cosine_similarity(baseline_flux, aligned_flux)
    oracle_cosine = compute_rowwise_cosine_similarity(oracle_flux, aligned_flux)
    baseline_flux_magnitude = baseline_flux.abs().mean(dim=1)
    oracle_flux_magnitude = oracle_flux.abs().mean(dim=1)
    target_flux_magnitude = aligned_flux.abs().mean(dim=1).clamp_min(1.0e-6)
    positive_advantage = (baseline_flux_error - oracle_flux_error).clamp_min(0.0)
    positive_advantage_total = float(positive_advantage[positive_mask].sum().item())
    bin_count = int(aligned_flux.shape[1])
    band_edges = [0, max(1, bin_count // 3), max(2, (2 * bin_count) // 3), bin_count]
    if band_edges[-2] >= bin_count:
        band_edges[-2] = max(1, bin_count - 1)
    band_rows = []
    band_totals = {}
    for label, start_index, end_index in [
        ("low", band_edges[0], band_edges[1]),
        ("mid", band_edges[1], band_edges[2]),
        ("high", band_edges[2], band_edges[3]),
    ]:
        if end_index <= start_index:
            band_totals[label] = 0.0
            continue
        baseline_band_error = (baseline_flux[:, start_index:end_index] - aligned_flux[:, start_index:end_index]).abs().mean(dim=1)
        oracle_band_error = (oracle_flux[:, start_index:end_index] - aligned_flux[:, start_index:end_index]).abs().mean(dim=1)
        band_positive_advantage = (baseline_band_error - oracle_band_error).clamp_min(0.0)
        band_total = float(band_positive_advantage[positive_mask].sum().item())
        band_totals[label] = band_total
        band_rows.append((label, band_total))
    band_total_sum = sum(float(value) for value in band_totals.values())
    band_shares = {
        label: (0.0 if band_total_sum <= 1.0e-8 else float(value) / band_total_sum)
        for label, value in band_totals.items()
    }
    dominant_band_label = sorted(
        band_rows,
        key=lambda item: (-float(item[1]), str(item[0])),
    )[0][0]

    baseline_ratio = baseline_flux_magnitude / target_flux_magnitude
    oracle_ratio = oracle_flux_magnitude / target_flux_magnitude
    cosine_gap = oracle_cosine - baseline_cosine
    active_target_mask = positive_mask & (target_flux_magnitude >= float(active_target_flux_threshold))
    if not bool(active_target_mask.any()):
        active_target_mask = positive_mask
    alignment_label = "mixed_flux_alignment_gap"
    if float(failure_signature.get("near_zero_target_advantage_share_0p1", 0.0)) >= 0.15:
        alignment_label = "zero_target_flux_jitter"
    elif (
        float(cosine_gap[positive_mask].mean().item()) >= 0.2
        and float(baseline_ratio[positive_mask].mean().item()) <= 0.35
        and float(oracle_ratio[positive_mask].mean().item()) <= 0.35
    ):
        alignment_label = "low_magnitude_direction_gap"

    return {
        "alignment_label": alignment_label,
        "dominant_band_label": dominant_band_label,
        "baseline_flux_alignment_cosine_mean_positive": round(float(baseline_cosine[positive_mask].mean().item()), 6),
        "reference_oracle_flux_alignment_cosine_mean_positive": round(float(oracle_cosine[positive_mask].mean().item()), 6),
        "flux_alignment_cosine_gap_positive": round(float(cosine_gap[positive_mask].mean().item()), 6),
        "baseline_flux_magnitude_mean_positive": round(float(baseline_flux_magnitude[positive_mask].mean().item()), 6),
        "reference_oracle_flux_magnitude_mean_positive": round(float(oracle_flux_magnitude[positive_mask].mean().item()), 6),
        "target_flux_magnitude_mean_positive": round(float(target_flux_magnitude[positive_mask].mean().item()), 6),
        "baseline_to_target_flux_magnitude_ratio_positive_active_target": round(
            float(baseline_ratio[active_target_mask].mean().item()),
            6,
        ),
        "reference_oracle_to_target_flux_magnitude_ratio_positive_active_target": round(
            float(oracle_ratio[active_target_mask].mean().item()),
            6,
        ),
        "low_band_positive_advantage_share": round(float(band_shares.get("low", 0.0)), 6),
        "mid_band_positive_advantage_share": round(float(band_shares.get("mid", 0.0)), 6),
        "high_band_positive_advantage_share": round(float(band_shares.get("high", 0.0)), 6),
    }


def compute_rowwise_cosine_similarity(left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
    left_cpu = left.detach().cpu().to(torch.float32)
    right_cpu = right.detach().cpu().to(torch.float32)
    left_norm = left_cpu.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    right_norm = right_cpu.norm(dim=1, keepdim=True).clamp_min(1.0e-6)
    return (left_cpu / left_norm * (right_cpu / right_norm)).sum(dim=1)


def classify_transition_window_region(
    *,
    start_sec: float,
    end_sec: float,
    duration_sec: float,
    boundary_sec: float,
) -> str:
    near_onset = float(start_sec) <= float(boundary_sec)
    near_offset = float(end_sec) >= max(0.0, float(duration_sec) - float(boundary_sec))
    if near_onset and near_offset:
        return "boundary_both"
    if near_onset:
        return "onset"
    if near_offset:
        return "offset"
    return "interior"


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Waveform Objective Collapse Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- objective_weights: {json.dumps(summary['objective_weights'], ensure_ascii=False)}",
        f"- decode_runtime: {json.dumps(summary['decode_runtime'], ensure_ascii=False)}",
        "",
        "## Weighted Objective Ranking",
    ]
    for row in list(summary["variant_weighted_objective_ranking"]):
        lines.append(
            "- "
            f"{row['label']}: weighted={row['mean_weighted_wave_objective']:.6f}, "
            f"delta_vs_baseline={row['mean_weighted_wave_objective_delta_vs_baseline']:.6f}, "
            f"waveform={row['mean_loss_waveform']:.6f}, "
            f"stft={row['mean_loss_stft']:.6f}, "
            f"rms_guard={row['mean_loss_rms_guard']:.6f}, "
            f"mrstft_short={row.get('mean_loss_mrstft_short_256_512_1024', 0.0):.6f}, "
            f"frame_unit_rms_l1={row.get('mean_loss_frame_unit_rms_l1', 0.0):.6f}, "
            f"frame_unit_rms_logspec_l1={row.get('mean_loss_frame_unit_rms_logspec_l1', 0.0):.6f}, "
            f"frame_delta_unit_rms_l1={row.get('mean_loss_frame_delta_unit_rms_l1', 0.0):.6f}, "
            f"frame_spectral_flux_l1={row.get('mean_loss_frame_spectral_flux_l1', 0.0):.6f}, "
            f"template_cosine={row['mean_decoded_frame_template_cosine']:.6f}, "
            f"frame_rms_corr={row['mean_decoded_frame_rms_to_aligned_frame_rms_corr']:.6f}"
        )
    lines.extend(
        [
            "",
            "## Structure Sidecar Rankings",
        ]
    )
    for metric_name, rows in dict(summary.get("structure_sidecar_rankings", {})).items():
        lines.append(f"- {metric_name}")
        for row in list(rows):
            lines.append(
                "  "
                f"{row['label']}: mean={row['mean']:.6f}, "
                f"template_cosine={row['decoded_frame_template_cosine_mean']:.6f}, "
                f"frame_rms_corr={row['decoded_frame_rms_to_aligned_frame_rms_corr']:.6f}"
            )
    lines.extend(
        [
            "",
            "## Transition Delta Candidate Objectives",
        ]
    )
    for item in list(summary.get("transition_delta_candidate_objective_rankings", [])):
        lines.append(f"- lambda={item['lambda']}")
        for row in list(item.get("ranking", [])):
            lines.append(
                "  "
                f"{row['label']}: candidate_score={row['candidate_score']:.6f}, "
                f"weighted={row['weighted_wave_objective']:.6f}, "
                f"frame_delta={row['loss_frame_delta_unit_rms_l1']:.6f}, "
                f"template_cosine={row['decoded_frame_template_cosine_mean']:.6f}, "
                f"frame_rms_corr={row['decoded_frame_rms_to_aligned_frame_rms_corr']:.6f}"
            )
    lines.extend(
        [
            "",
            "## Transition Delta Flip Thresholds",
        ]
    )
    for item in list(summary.get("transition_delta_flip_thresholds_vs_baseline", [])):
        lines.append(
            "- "
            f"{item['label']}: baseline_weighted_gap={item['baseline_weighted_gap']:.6f}, "
            f"baseline_frame_delta_advantage={item['baseline_frame_delta_advantage']:.6f}, "
            f"flip_lambda_min={item['flip_lambda_min']}"
        )
    lines.extend(
        [
            "",
            "## Transition Combo Grid Summary",
        ]
    )
    for item in list(summary.get("transition_combo_grid_summary", []))[:12]:
        matchup_text = "; ".join(
            (
                f"{matchup['other_label']}: wins={matchup['win_count']}/{matchup['record_count']}, "
                f"mean_margin={matchup['mean_margin']:.6f}, median_margin={matchup['median_margin']:.6f}, "
                f"min_margin={matchup['min_margin']:.6f}, max_margin={matchup['max_margin']:.6f}"
            )
            for matchup in list(item.get("matchups", []))
        )
        lines.append(
            "- "
            f"delta_lambda={item['delta_lambda']}, flux_lambda={item['flux_lambda']}, "
            f"total_wins={item['total_wins']}/{item['max_total_wins']}: {matchup_text}"
        )
    lines.extend(
        [
            "",
            "## Directional Flux Candidate Grid Summary",
        ]
    )
    for item in list(summary.get("directional_flux_candidate_grid_summary", []))[:12]:
        matchup_text = "; ".join(
            (
                f"{matchup['other_label']}: wins={matchup['win_count']}/{matchup['record_count']}, "
                f"mean_margin={matchup['mean_margin']:.6f}, median_margin={matchup['median_margin']:.6f}, "
                f"min_margin={matchup['min_margin']:.6f}, max_margin={matchup['max_margin']:.6f}"
            )
            for matchup in list(item.get("matchups", []))
        )
        lines.append(
            "- "
            f"direction_lambda={item['direction_lambda']}, zero_jitter_lambda={item['zero_jitter_lambda']}, "
            f"total_wins={item['total_wins']}/{item['max_total_wins']}: {matchup_text}"
        )
    lines.extend(
        [
            "",
            "## Active Template Candidate Grid Summary",
        ]
    )
    for item in list(summary.get("active_template_candidate_grid_summary", []))[:12]:
        matchup_text = "; ".join(
            (
                f"{matchup['other_label']}: wins={matchup['win_count']}/{matchup['record_count']}, "
                f"mean_margin={matchup['mean_margin']:.6f}, median_margin={matchup['median_margin']:.6f}, "
                f"min_margin={matchup['min_margin']:.6f}, max_margin={matchup['max_margin']:.6f}"
            )
            for matchup in list(item.get("matchups", []))
        )
        lines.append(
            "- "
            f"template_lambda={item['template_lambda']}, zero_jitter_lambda={item['zero_jitter_lambda']}, "
            f"total_wins={item['total_wins']}/{item['max_total_wins']}: {matchup_text}"
        )
    active_template_targeted_summary = dict(summary.get("active_template_targeted_summary", {}))
    if active_template_targeted_summary:
        best_combo = dict(active_template_targeted_summary.get("best_combo", {}))
        lines.extend(
            [
                "",
                "## Active Template Targeted Summary",
                (
                    "- best_combo: "
                    f"template_lambda={best_combo.get('template_lambda')}, "
                    f"zero_jitter_lambda={best_combo.get('zero_jitter_lambda')}, "
                    f"total_wins={best_combo.get('total_wins')}/{best_combo.get('max_total_wins')}"
                ),
            ]
        )
        stationary_risk_summary = dict(active_template_targeted_summary.get("stationary_risk_summary", {}))
        if stationary_risk_summary:
            lines.append(
                "- stationary_risk: "
                f"residual_count={stationary_risk_summary.get('residual_record_count')}, "
                f"win_count={stationary_risk_summary.get('win_record_count')}, "
                f"residual_adjacent_cos={stationary_risk_summary.get('residual_mean_aligned_frame_adjacent_cosine')}, "
                f"win_adjacent_cos={stationary_risk_summary.get('win_mean_aligned_frame_adjacent_cosine')}, "
                f"residual_rms_cv={stationary_risk_summary.get('residual_mean_aligned_frame_rms_cv')}, "
                f"win_rms_cv={stationary_risk_summary.get('win_mean_aligned_frame_rms_cv')}"
            )
        for item in list(active_template_targeted_summary.get("residual_losses", [])):
            target_stationarity = dict(item.get("target_stationarity", {}))
            matchup_text = ", ".join(
                f"{matchup['other_label']}({matchup['margin']:.6f})"
                for matchup in list(item.get("matchups", []))
            )
            lines.append(
                "- "
                f"{item['record_id']}: mean_margin={item.get('mean_margin')}, "
                f"matchups={matchup_text}, "
                f"aligned_template_cos={target_stationarity.get('aligned_frame_template_cosine_mean')}, "
                f"aligned_adjacent_cos={target_stationarity.get('aligned_frame_adjacent_cosine_mean')}, "
                f"aligned_rms_cv={target_stationarity.get('aligned_frame_rms_cv')}"
            )
    lines.extend(
        [
            "",
            "## Active Template + Delta Candidate Grid Summary",
        ]
    )
    for item in list(summary.get("active_template_delta_candidate_grid_summary", []))[:12]:
        matchup_text = "; ".join(
            (
                f"{matchup['other_label']}: wins={matchup['win_count']}/{matchup['record_count']}, "
                f"mean_margin={matchup['mean_margin']:.6f}, median_margin={matchup['median_margin']:.6f}, "
                f"min_margin={matchup['min_margin']:.6f}, max_margin={matchup['max_margin']:.6f}"
            )
            for matchup in list(item.get("matchups", []))
        )
        lines.append(
            "- "
            f"template_lambda={item['template_lambda']}, delta_lambda={item['delta_lambda']}, "
            f"total_wins={item['total_wins']}/{item['max_total_wins']}: {matchup_text}"
        )
    active_template_delta_targeted_summary = dict(summary.get("active_template_delta_targeted_summary", {}))
    if active_template_delta_targeted_summary:
        best_combo = dict(active_template_delta_targeted_summary.get("best_combo", {}))
        lines.extend(
            [
                "",
                "## Active Template + Delta Targeted Summary",
                (
                    "- best_combo: "
                    f"template_lambda={best_combo.get('template_lambda')}, "
                    f"delta_lambda={best_combo.get('delta_lambda')}, "
                    f"total_wins={best_combo.get('total_wins')}/{best_combo.get('max_total_wins')}"
                ),
            ]
        )
        stationary_risk_summary = dict(active_template_delta_targeted_summary.get("stationary_risk_summary", {}))
        if stationary_risk_summary:
            lines.append(
                "- stationary_risk: "
                f"residual_count={stationary_risk_summary.get('residual_record_count')}, "
                f"win_count={stationary_risk_summary.get('win_record_count')}, "
                f"residual_adjacent_cos={stationary_risk_summary.get('residual_mean_aligned_frame_adjacent_cosine')}, "
                f"win_adjacent_cos={stationary_risk_summary.get('win_mean_aligned_frame_adjacent_cosine')}, "
                f"residual_rms_cv={stationary_risk_summary.get('residual_mean_aligned_frame_rms_cv')}, "
                f"win_rms_cv={stationary_risk_summary.get('win_mean_aligned_frame_rms_cv')}, "
                f"residual_frame_delta={stationary_risk_summary.get('residual_mean_baseline_frame_delta')}, "
                f"win_frame_delta={stationary_risk_summary.get('win_mean_baseline_frame_delta')}"
            )
        for item in list(active_template_delta_targeted_summary.get("residual_losses", [])):
            target_stationarity = dict(item.get("target_stationarity", {}))
            matchup_text = ", ".join(
                f"{matchup['other_label']}({matchup['margin']:.6f})"
                for matchup in list(item.get("matchups", []))
            )
            lines.append(
                "- "
                f"{item['record_id']}: mean_margin={item.get('mean_margin')}, "
                f"matchups={matchup_text}, "
                f"aligned_template_cos={target_stationarity.get('aligned_frame_template_cosine_mean')}, "
                f"aligned_adjacent_cos={target_stationarity.get('aligned_frame_adjacent_cosine_mean')}, "
                f"aligned_rms_cv={target_stationarity.get('aligned_frame_rms_cv')}"
            )
    targeted_summary = dict(summary.get("transition_targeted_hard_failure_summary", {}))
    if targeted_summary:
        best_combo = dict(targeted_summary.get("best_combo", {}))
        lines.extend(
            [
                "",
                "## Transition Targeted Hard Failures",
                (
                    "- best_combo: "
                    f"delta_lambda={best_combo.get('delta_lambda')}, "
                    f"flux_lambda={best_combo.get('flux_lambda')}, "
                    f"total_wins={best_combo.get('total_wins')}/{best_combo.get('max_total_wins')}"
                ),
            ]
        )
        repeated_hard_failures = list(targeted_summary.get("repeated_hard_failures", []))
        if repeated_hard_failures:
            lines.append(
                "- repeated_hard_failures: "
                + ", ".join(f"{item['record_id']}({item['loss_count']})" for item in repeated_hard_failures)
            )
        repeated_easy_wins = list(targeted_summary.get("repeated_easy_wins", []))
        if repeated_easy_wins:
            lines.append(
                "- repeated_easy_wins: "
                + ", ".join(f"{item['record_id']}({item['win_count']})" for item in repeated_easy_wins)
            )
        for matchup in list(targeted_summary.get("matchups", [])):
            lines.append(f"- matchup={matchup['other_label']}")
            lines.append(
                "  best_wins: "
                + ", ".join(f"{item['record_id']}({item['margin']:.6f})" for item in list(matchup.get("best_wins", [])))
            )
            lines.append(
                "  worst_losses: "
                + ", ".join(f"{item['record_id']}({item['margin']:.6f})" for item in list(matchup.get("worst_losses", [])))
            )
    hard_case_breakdown = list(summary.get("transition_hard_case_breakdown", []))
    if hard_case_breakdown:
        lines.extend(
            [
                "",
                "## Transition Hard-Case Breakdown",
            ]
        )
        for item in hard_case_breakdown:
            reference_oracle = dict(item.get("reference_oracle", {}))
            local_summary = dict(item.get("transition_local_summary", {}))
            pattern_summary = dict(item.get("pattern_summary", {}))
            lines.append(
                "- "
                f"{item['record_id']}: reference_oracle={reference_oracle.get('label')}, "
                f"margin_vs_baseline={reference_oracle.get('margin_vs_baseline')}, "
                f"baseline_candidate_score={item.get('baseline_candidate_score')}, "
                f"baseline_local_score_mean={local_summary.get('baseline_local_score_mean')}, "
                f"reference_oracle_local_score_mean={local_summary.get('reference_oracle_local_score_mean')}, "
                f"positive_advantage_fraction={local_summary.get('positive_advantage_fraction')}"
            )
            lines.append(
                "  "
                f"pattern={pattern_summary.get('pattern_label')} "
                f"boundary_share={pattern_summary.get('boundary_advantage_share')} "
                f"interior_share={pattern_summary.get('interior_advantage_share')} "
                f"max_window_share={pattern_summary.get('max_window_share')} "
                f"dominant_region={pattern_summary.get('dominant_region')} "
                f"dominant_window={pattern_summary.get('dominant_window_sec_range')}"
            )
            failure_signature = dict(item.get("failure_signature", {}))
            if failure_signature:
                lines.append(
                    "  "
                    f"signature={failure_signature.get('signature_label')} "
                    f"components={failure_signature.get('component_label')} "
                    f"flux_share={failure_signature.get('flux_dominant_advantage_share')} "
                    f"delta_share={failure_signature.get('delta_dominant_advantage_share')} "
                    f"q25={failure_signature.get('target_transition_strength_q25')} "
                    f"q75={failure_signature.get('target_transition_strength_q75')}"
                )
                lines.append(
                    "  "
                    f"regimes: low_q25={failure_signature.get('low_motion_advantage_share_q25')} "
                    f"high_q75={failure_signature.get('high_motion_advantage_share_q75')} "
                    f"boundary_high_q75={failure_signature.get('boundary_high_motion_advantage_share_q75')} "
                    f"interior_high_q75={failure_signature.get('interior_high_motion_advantage_share_q75')} "
                    f"near_zero_target_0p1={failure_signature.get('near_zero_target_advantage_share_0p1')} "
                    f"near_zero_oracle_score_0p1={failure_signature.get('near_zero_reference_oracle_error_advantage_share_0p1')}"
                )
            flux_alignment_summary = dict(item.get("flux_alignment_summary", {}))
            if flux_alignment_summary:
                lines.append(
                    "  "
                    f"flux_alignment={flux_alignment_summary.get('alignment_label')} "
                    f"dominant_band={flux_alignment_summary.get('dominant_band_label')} "
                    f"baseline_cos={flux_alignment_summary.get('baseline_flux_alignment_cosine_mean_positive')} "
                    f"oracle_cos={flux_alignment_summary.get('reference_oracle_flux_alignment_cosine_mean_positive')} "
                    f"cos_gap={flux_alignment_summary.get('flux_alignment_cosine_gap_positive')}"
                )
                lines.append(
                    "  "
                    f"flux_mag_ratio_active_target: baseline={flux_alignment_summary.get('baseline_to_target_flux_magnitude_ratio_positive_active_target')} "
                    f"oracle={flux_alignment_summary.get('reference_oracle_to_target_flux_magnitude_ratio_positive_active_target')} "
                    f"bands(low/mid/high)="
                    f"{flux_alignment_summary.get('low_band_positive_advantage_share')}/"
                    f"{flux_alignment_summary.get('mid_band_positive_advantage_share')}/"
                    f"{flux_alignment_summary.get('high_band_positive_advantage_share')}"
                )
            for window in list(item.get("top_failure_windows", []))[:5]:
                lines.append(
                    "  "
                    f"window={window['start_sec']:.6f}-{window['end_sec']:.6f}s "
                    f"transitions={window['start_transition_index']}-{window['end_transition_index']} "
                    f"total_advantage={window['total_advantage']:.6f} "
                    f"mean_advantage={window['mean_advantage']:.6f} "
                    f"baseline_delta={window['baseline_delta_error_mean']:.6f} "
                    f"oracle_delta={window['reference_oracle_delta_error_mean']:.6f} "
                    f"baseline_flux={window['baseline_flux_error_mean']:.6f} "
                    f"oracle_flux={window['reference_oracle_flux_error_mean']:.6f}"
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
