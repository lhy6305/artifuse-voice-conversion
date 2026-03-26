from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import (
    build_model_from_checkpoint,
    normalize_predicted_activity_gate_apply_mode,
    resolve_checkpoint_path_from_inputs,
    resolve_package_entries,
)
from v5vc.offline_vocoder_scaffold import resolve_residual_shape_branch_condition_delta
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary
from v5vc.stage5_speech_emergence_probe import (
    compute_pearson_correlation,
    compute_zero_crossing_rate,
    frame_waveform_sequence,
    summarize_frame_sequence_metrics,
    summarize_probe_delta_vs_baseline,
    summarize_scalar_values,
)


STRUCTURE_PROBE_VARIANTS = [
    {
        "label": "baseline",
        "description": "Original checkpoint path without any hidden-state intervention.",
        "transforms": [],
    },
    {
        "label": "periodic_hidden_frame_mean",
        "description": "Collapse periodic encoder dynamics to its package-wise frame mean before fusion.",
        "transforms": [("periodic_hidden", "frame_mean")],
    },
    {
        "label": "noise_hidden_frame_mean",
        "description": "Collapse noise encoder dynamics to its package-wise frame mean before fusion.",
        "transforms": [("noise_hidden", "frame_mean")],
    },
    {
        "label": "fused_hidden_frame_mean",
        "description": "Collapse fusion output dynamics to its package-wise frame mean before the waveform decoder.",
        "transforms": [("fused_hidden", "frame_mean")],
    },
    {
        "label": "fused_hidden_zero",
        "description": "Zero the waveform decoder input while leaving branch-side activity gates unchanged.",
        "transforms": [("fused_hidden", "zero")],
    },
    {
        "label": "fused_hidden_from_periodic_hidden",
        "description": "Bypass fusion and feed periodic_hidden directly into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_periodic_hidden")],
    },
    {
        "label": "fused_hidden_from_noise_hidden",
        "description": "Bypass fusion and feed noise_hidden directly into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_noise_hidden")],
    },
    {
        "label": "fused_hidden_from_branch_mean",
        "description": "Bypass fusion and feed the equal-weight branch mean into the waveform decoder.",
        "transforms": [("fused_hidden", "replace_with_branch_mean")],
    },
]


def analyze_stage5_nores_waveform_decoder_structure(
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
    resolved_selection_target = (
        str(selection_summary.get("_resolved_selection_target", selection_target))
        if isinstance(selection_summary, dict)
        else str(selection_target)
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
        raise ValueError("No Stage5 training packages were selected for the waveform-decoder structure probe.")

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

            variant_rows: list[dict[str, object]] = []
            baseline_waveform = None
            baseline_scalar_metrics = None
            for variant in STRUCTURE_PROBE_VARIANTS:
                scalar_metrics, stage_metrics, decoded_waveform, transform_notes = run_structure_probe_variant(
                    model=model,
                    batch=batch,
                    runtime=runtime,
                    device=resolved_device,
                    use_predicted_activity_gate=bool(use_predicted_activity_gate),
                    predicted_activity_gate_floor=float(predicted_activity_gate_floor),
                    predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                    predicted_activity_gate_apply_mode=resolved_apply_mode,
                    transforms=list(variant["transforms"]),
                )
                variant_row = {
                    "label": str(variant["label"]),
                    "description": str(variant["description"]),
                    "transform_notes": transform_notes,
                    "scalar_metrics": scalar_metrics,
                    "stage_metrics": stage_metrics,
                    "_decoded_waveform": decoded_waveform,
                }
                if str(variant["label"]) == "baseline":
                    baseline_waveform = decoded_waveform
                    baseline_scalar_metrics = scalar_metrics
                variant_rows.append(variant_row)

            if baseline_waveform is None or baseline_scalar_metrics is None:
                raise RuntimeError("Stage5 waveform-decoder structure probe failed to produce a baseline variant.")

            for variant_row in variant_rows:
                variant_row["delta_vs_baseline"] = summarize_probe_delta_vs_baseline(
                    candidate_metrics=dict(variant_row["scalar_metrics"]),
                    baseline_metrics=baseline_scalar_metrics,
                    candidate_waveform=variant_row.get("_decoded_waveform"),
                    baseline_waveform=baseline_waveform,
                )
                variant_row["stage_delta_vs_baseline"] = summarize_stage_delta_vs_baseline(
                    candidate_stage_metrics=dict(variant_row["stage_metrics"]),
                    baseline_stage_metrics=dict(variant_rows[0]["stage_metrics"]),
                )
                variant_row.pop("_decoded_waveform", None)

            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "variants": variant_rows,
                }
            )

    aggregate_rows = build_variant_aggregates(per_record_rows)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if checkpoint_selection_path is None else resolved_selection_target,
        "selected_checkpoint_summary": selection_summary,
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(per_record_rows),
        "decode_runtime": {
            "device": str(resolved_device),
            "use_predicted_activity_gate": bool(use_predicted_activity_gate),
            "predicted_activity_gate_floor": float(predicted_activity_gate_floor),
            "predicted_activity_gate_smoothing_frames": int(predicted_activity_gate_smoothing_frames),
            "predicted_activity_gate_apply_mode": resolved_apply_mode,
            "fusion_mode": str(model.fusion_mode),
            "waveform_decoder_mode": str(model.waveform_decoder_mode),
            "use_decoder_branch_condition_adapter": bool(getattr(model, "use_decoder_branch_condition_adapter", False)),
            "use_residual_shape_branch_condition_adapter": bool(
                getattr(model, "use_residual_shape_branch_condition_adapter", False)
            ),
            "residual_shape_branch_condition_scale": float(
                getattr(model, "residual_shape_branch_condition_scale", 1.0)
            ),
            "residual_shape_branch_condition_mode": str(
                getattr(model, "residual_shape_branch_condition_mode", "raw_additive_v1")
            ),
        },
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
        "records": per_record_rows,
        "notes": [
            "This probe is a structure-level diagnosis for the Stage5 no-res waveform decoder route, not a checkpoint ranking pass.",
            "baseline uses the current heard-route decode semantics so the resulting decoded-frame diversity stays aligned with the audible buzz path.",
            "periodic_hidden_frame_mean and noise_hidden_frame_mean test whether branch-side temporal diversity still matters once it reaches fusion.",
            "fused_hidden_frame_mean and fused_hidden_zero test whether the waveform decoder preserves or discards temporal diversity already present in fused_hidden.",
            "fused_hidden_from_periodic_hidden, fused_hidden_from_noise_hidden, and fused_hidden_from_branch_mean bypass fusion and ask whether the existing waveform decoder can respond if it is fed branch-side hidden dynamics directly.",
            "If fused_hidden remains materially less template-like than waveform_frames on baseline, that is evidence the waveform decoder itself is a collapse site.",
            "If fused_hidden_frame_mean barely changes waveform_frames or decoded metrics, the waveform decoder is acting close to a fixed-template projector around the current operating region.",
        ],
    }
    json_path = output_dir / "stage5_waveform_decoder_structure_probe.json"
    md_path = output_dir / "stage5_waveform_decoder_structure_probe.md"
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


def run_structure_probe_variant(
    *,
    model: torch.nn.Module,
    batch: dict[str, torch.Tensor],
    runtime: dict[str, int],
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
    transforms: list[tuple[str, str]],
) -> tuple[dict[str, float], dict[str, dict[str, float]], torch.Tensor, list[str]]:
    periodic_hidden = model.periodic_encoder(
        batch["periodic_branch_features"].to(device=device, dtype=torch.float32)
    )
    noise_hidden = model.noise_encoder(
        batch["noise_branch_features"].to(device=device, dtype=torch.float32)
    )
    transform_notes: list[str] = []
    periodic_hidden = apply_structure_transform(
        tensor=periodic_hidden,
        transforms=transforms,
        stage_name="periodic_hidden",
        transform_notes=transform_notes,
    )
    noise_hidden = apply_structure_transform(
        tensor=noise_hidden,
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
    waveform_frames = compute_waveform_frames_for_probe(
        model=model,
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        fused_hidden=fused_hidden,
    )
    periodic_gate = torch.sigmoid(model.periodic_gate(periodic_hidden))
    noise_gate = torch.sigmoid(model.noise_gate(noise_hidden))
    predicted_activity = torch.maximum(periodic_gate, noise_gate)
    decoded_waveform = reconstruct_waveform_from_frames(
        waveform_frames=waveform_frames,
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        frame_gains=predicted_activity if bool(use_predicted_activity_gate) else None,
        frame_gain_floor=float(predicted_activity_gate_floor),
        frame_gain_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
        frame_gain_apply_mode=predicted_activity_gate_apply_mode,
    ).detach().cpu().to(torch.float32)
    stage_metrics = summarize_stage_metrics(
        periodic_hidden=periodic_hidden,
        noise_hidden=noise_hidden,
        fused_hidden=fused_hidden,
        waveform_frames=waveform_frames,
        decoded_waveform=decoded_waveform,
        aligned_waveform=batch.get("aligned_waveform"),
        frame_length=int(runtime["frame_length"]),
        hop_length=int(runtime["hop_length"]),
        sample_rate=int(runtime["sample_rate"]),
        predicted_activity=predicted_activity,
        periodic_gate=periodic_gate,
        noise_gate=noise_gate,
    )
    scalar_metrics = flatten_stage_metrics(stage_metrics)
    return scalar_metrics, stage_metrics, decoded_waveform, transform_notes


def compute_fused_hidden_for_probe(
    *,
    model: torch.nn.Module,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
) -> torch.Tensor:
    fusion_mode = str(getattr(model, "fusion_mode", "plain"))
    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    branch_difference_hidden = periodic_hidden - noise_hidden
    if fusion_mode == "plain":
        if getattr(model, "fusion", None) is None:
            raise RuntimeError("model.fusion is not initialized for plain fusion mode.")
        return model.fusion(torch.cat([periodic_hidden, noise_hidden], dim=-1))
    if fusion_mode == "branch_mean_residual_v1":
        fusion_branch_mean_residual = getattr(model, "fusion_branch_mean_residual", None)
        if fusion_branch_mean_residual is None:
            raise RuntimeError("fusion_branch_mean_residual is not initialized for branch_mean_residual_v1.")
        fusion_residual_hidden = fusion_branch_mean_residual(
            torch.cat(
                [
                    periodic_hidden,
                    noise_hidden,
                    branch_difference_hidden,
                ],
                dim=-1,
            )
        )
        return branch_mean_hidden + fusion_residual_hidden
    if fusion_mode == "periodic_residual_v1":
        fusion_periodic_residual_adapter = getattr(model, "fusion_periodic_residual_adapter", None)
        fusion_periodic_residual_gate = getattr(model, "fusion_periodic_residual_gate", None)
        fusion_periodic_residual_proj = getattr(model, "fusion_periodic_residual_proj", None)
        if (
            fusion_periodic_residual_adapter is None
            or fusion_periodic_residual_gate is None
            or fusion_periodic_residual_proj is None
        ):
            raise RuntimeError("fusion_periodic_residual modules are not initialized for periodic_residual_v1.")
        fusion_residual_context = fusion_periodic_residual_adapter(
            torch.cat(
                [
                    periodic_hidden,
                    noise_hidden,
                    branch_difference_hidden,
                ],
                dim=-1,
            )
        )
        fusion_residual_gate = torch.sigmoid(fusion_periodic_residual_gate(fusion_residual_context))
        fusion_residual_hidden = fusion_residual_gate * torch.tanh(
            fusion_periodic_residual_proj(fusion_residual_context)
        )
        return periodic_hidden + fusion_residual_hidden
    if fusion_mode == "branch_mean_contrast_residual_v1":
        fusion_branch_mean_contrast_norm = getattr(model, "fusion_branch_mean_contrast_norm", None)
        fusion_branch_mean_contrast_gate = getattr(model, "fusion_branch_mean_contrast_gate", None)
        fusion_branch_mean_contrast_proj = getattr(model, "fusion_branch_mean_contrast_proj", None)
        if (
            fusion_branch_mean_contrast_norm is None
            or fusion_branch_mean_contrast_gate is None
            or fusion_branch_mean_contrast_proj is None
        ):
            raise RuntimeError(
                "fusion_branch_mean_contrast modules are not initialized for branch_mean_contrast_residual_v1."
            )
        contrast_hidden = fusion_branch_mean_contrast_norm(branch_difference_hidden)
        fusion_residual_gate = torch.sigmoid(fusion_branch_mean_contrast_gate(contrast_hidden))
        fusion_residual_hidden = fusion_residual_gate * torch.tanh(
            fusion_branch_mean_contrast_proj(contrast_hidden)
        )
        return branch_mean_hidden + fusion_residual_hidden
    raise ValueError(f"Unsupported fusion_mode in structure probe: {fusion_mode!r}")


def compute_waveform_frames_for_probe(
    *,
    model: torch.nn.Module,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
) -> torch.Tensor:
    waveform_decoder_mode = str(getattr(model, "waveform_decoder_mode", "fused_single"))
    if waveform_decoder_mode != "fused_single":
        raise ValueError(f"Unsupported waveform_decoder_mode in structure probe: {waveform_decoder_mode!r}")
    waveform_decoder = getattr(model, "waveform_decoder", None)
    if waveform_decoder is None:
        raise RuntimeError("waveform_decoder is not initialized for fused_single structure probe.")
    branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)
    decoder_hidden = fused_hidden
    branch_condition_gate = None
    if bool(getattr(model, "use_decoder_branch_condition_adapter", False)):
        decoder_branch_condition_adapter = getattr(model, "decoder_branch_condition_adapter", None)
        decoder_branch_condition_gate = getattr(model, "decoder_branch_condition_gate", None)
        decoder_fused_condition_proj = getattr(model, "decoder_fused_condition_proj", None)
        if (
            decoder_branch_condition_adapter is None
            or decoder_branch_condition_gate is None
            or decoder_fused_condition_proj is None
        ):
            raise RuntimeError("Decoder branch-condition adapter modules are not initialized for structure probe.")
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
            raise RuntimeError("Residual-shape branch-condition adapter modules are not initialized for structure probe.")
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
    return torch.tanh(waveform_frame_logits)


def apply_structure_transform(
    *,
    tensor: torch.Tensor,
    transforms: list[tuple[str, str]],
    stage_name: str,
    transform_notes: list[str],
    periodic_hidden: torch.Tensor | None = None,
    noise_hidden: torch.Tensor | None = None,
) -> torch.Tensor:
    transformed = tensor
    for target_stage, mode in transforms:
        if str(target_stage) != str(stage_name):
            continue
        if mode == "frame_mean":
            mean_values = transformed.mean(dim=0, keepdim=True)
            transformed = mean_values.expand_as(transformed)
        elif mode == "zero":
            transformed = torch.zeros_like(transformed)
        elif mode == "replace_with_periodic_hidden":
            if periodic_hidden is None:
                raise ValueError("periodic_hidden is required for replace_with_periodic_hidden.")
            if tuple(periodic_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "periodic_hidden shape does not match fused_hidden for bypass substitution: "
                    f"{tuple(periodic_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = periodic_hidden
        elif mode == "replace_with_noise_hidden":
            if noise_hidden is None:
                raise ValueError("noise_hidden is required for replace_with_noise_hidden.")
            if tuple(noise_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "noise_hidden shape does not match fused_hidden for bypass substitution: "
                    f"{tuple(noise_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = noise_hidden
        elif mode == "replace_with_branch_mean":
            if periodic_hidden is None or noise_hidden is None:
                raise ValueError("periodic_hidden and noise_hidden are required for replace_with_branch_mean.")
            if tuple(periodic_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "periodic_hidden shape does not match fused_hidden for branch-mean substitution: "
                    f"{tuple(periodic_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            if tuple(noise_hidden.shape) != tuple(transformed.shape):
                raise ValueError(
                    "noise_hidden shape does not match fused_hidden for branch-mean substitution: "
                    f"{tuple(noise_hidden.shape)} vs {tuple(transformed.shape)}"
                )
            transformed = 0.5 * (periodic_hidden + noise_hidden)
        else:
            raise ValueError(f"Unsupported structure-probe transform mode: {mode!r}")
        transform_notes.append(f"{stage_name} -> {mode}")
    return transformed


def summarize_stage_metrics(
    *,
    periodic_hidden: torch.Tensor,
    noise_hidden: torch.Tensor,
    fused_hidden: torch.Tensor,
    waveform_frames: torch.Tensor,
    decoded_waveform: torch.Tensor,
    aligned_waveform: torch.Tensor | None,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
    predicted_activity: torch.Tensor,
    periodic_gate: torch.Tensor,
    noise_gate: torch.Tensor,
) -> dict[str, dict[str, float]]:
    periodic_hidden_cpu = periodic_hidden.detach().cpu().to(torch.float32)
    noise_hidden_cpu = noise_hidden.detach().cpu().to(torch.float32)
    fused_hidden_cpu = fused_hidden.detach().cpu().to(torch.float32)
    waveform_frames_cpu = waveform_frames.detach().cpu().to(torch.float32)
    decoded_analysis_frames = frame_waveform_sequence(
        waveform=decoded_waveform,
        frame_length=int(frame_length),
        hop_length=int(hop_length),
        target_frame_count=int(waveform_frames_cpu.shape[0]),
    )
    aligned_waveform_cpu = None
    aligned_frame_metrics = None
    aligned_frame_rms = None
    if aligned_waveform is not None:
        aligned_waveform_cpu = aligned_waveform.detach().cpu().to(torch.float32)[: decoded_waveform.shape[0]]
        aligned_analysis_frames = frame_waveform_sequence(
            waveform=aligned_waveform_cpu,
            frame_length=int(frame_length),
            hop_length=int(hop_length),
            target_frame_count=int(waveform_frames_cpu.shape[0]),
        )
        aligned_frame_metrics = summarize_representation_metrics(aligned_analysis_frames)
        aligned_frame_rms = aligned_analysis_frames.pow(2).mean(dim=1).sqrt()
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform, int(sample_rate))
    decoded_frame_metrics = summarize_representation_metrics(decoded_analysis_frames)
    periodic_metrics = summarize_representation_metrics(periodic_hidden_cpu)
    noise_metrics = summarize_representation_metrics(noise_hidden_cpu)
    fused_metrics = summarize_representation_metrics(fused_hidden_cpu)
    waveform_frame_metrics = summarize_representation_metrics(waveform_frames_cpu)
    decode_metrics = {
        "decoded_waveform_rms": round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6),
        "decoded_abs_mean": round(float(decoded_waveform.abs().mean().item()), 6),
        "decoded_peak_abs": round(float(decoded_waveform.abs().max().item()), 6),
        "decoded_zero_crossing_rate": round(float(compute_zero_crossing_rate(decoded_waveform)), 6),
        "decoded_spectral_centroid_hz": float(decoded_spectral["centroid_hz"]),
        "decoded_spectral_bandwidth_hz": float(decoded_spectral["bandwidth_hz"]),
        "decoded_spectral_rolloff95_hz": float(decoded_spectral["rolloff95_hz"]),
        "decoded_spectral_high_band_energy_ratio": float(decoded_spectral["high_band_energy_ratio"]),
        "predicted_activity_mean": round(float(predicted_activity.detach().cpu().mean().item()), 6),
        "predicted_activity_std": round(float(predicted_activity.detach().cpu().std(unbiased=False).item()), 6),
        "periodic_gate_mean": round(float(periodic_gate.detach().cpu().mean().item()), 6),
        "noise_gate_mean": round(float(noise_gate.detach().cpu().mean().item()), 6),
    }
    if aligned_waveform_cpu is not None and aligned_frame_metrics is not None and aligned_frame_rms is not None:
        decoded_frame_rms = decoded_analysis_frames.pow(2).mean(dim=1).sqrt()
        decode_metrics.update(
            {
                "aligned_waveform_rms": round(float(aligned_waveform_cpu.pow(2).mean().sqrt().item()), 6),
                "decoded_to_aligned_rms_ratio": round(
                    0.0
                    if float(aligned_waveform_cpu.pow(2).mean().sqrt().item()) <= 1.0e-8
                    else float(decoded_waveform.pow(2).mean().sqrt().item())
                    / float(aligned_waveform_cpu.pow(2).mean().sqrt().item()),
                    6,
                ),
                "decoded_frame_rms_to_aligned_frame_rms_corr": float(
                    compute_pearson_correlation(decoded_frame_rms, aligned_frame_rms)
                ),
                "decoded_frame_template_cosine_gap_vs_aligned": round(
                    float(decoded_frame_metrics["template_cosine_mean"])
                    - float(aligned_frame_metrics["template_cosine_mean"]),
                    6,
                ),
                "decoded_frame_adjacent_cosine_gap_vs_aligned": round(
                    float(decoded_frame_metrics["adjacent_cosine_mean"])
                    - float(aligned_frame_metrics["adjacent_cosine_mean"]),
                    6,
                ),
            }
        )
    return {
        "periodic_hidden": periodic_metrics,
        "noise_hidden": noise_metrics,
        "fused_hidden": fused_metrics,
        "waveform_frames": waveform_frame_metrics,
        "decoded_frames": decoded_frame_metrics,
        "decode": decode_metrics,
    }


def summarize_representation_metrics(sequence: torch.Tensor) -> dict[str, float]:
    metrics = summarize_frame_sequence_metrics(sequence)
    sequence_cpu = sequence.detach().cpu().to(torch.float32)
    temporal_delta = sequence_cpu.new_zeros((0,), dtype=torch.float32)
    if int(sequence_cpu.shape[0]) > 1:
        temporal_delta = (sequence_cpu[1:] - sequence_cpu[:-1]).abs()
    metrics.update(
        {
            "sequence_std": round(float(sequence_cpu.std(unbiased=False).item()), 6),
            "sequence_abs_mean": round(float(sequence_cpu.abs().mean().item()), 6),
            "frame_delta_abs_mean": round(
                0.0 if int(temporal_delta.numel()) <= 0 else float(temporal_delta.mean().item()),
                6,
            ),
        }
    )
    return metrics


def flatten_stage_metrics(stage_metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    flattened: dict[str, float] = {}
    for stage_name, metrics in stage_metrics.items():
        for key, value in metrics.items():
            flattened[f"{stage_name}_{key}"] = float(value)
            if stage_name == "decode":
                flattened[key] = float(value)
    fused_metrics = dict(stage_metrics["fused_hidden"])
    waveform_metrics = dict(stage_metrics["waveform_frames"])
    decoded_metrics = dict(stage_metrics["decoded_frames"])
    flattened["fused_to_waveform_template_cosine_gap"] = round(
        float(waveform_metrics["template_cosine_mean"]) - float(fused_metrics["template_cosine_mean"]),
        6,
    )
    flattened["fused_to_waveform_adjacent_cosine_gap"] = round(
        float(waveform_metrics["adjacent_cosine_mean"]) - float(fused_metrics["adjacent_cosine_mean"]),
        6,
    )
    flattened["fused_to_waveform_delta_abs_mean_ratio"] = round(
        0.0
        if abs(float(fused_metrics["frame_delta_abs_mean"])) <= 1.0e-8
        else float(waveform_metrics["frame_delta_abs_mean"]) / float(fused_metrics["frame_delta_abs_mean"]),
        6,
    )
    flattened["waveform_to_decoded_template_cosine_gap"] = round(
        float(decoded_metrics["template_cosine_mean"]) - float(waveform_metrics["template_cosine_mean"]),
        6,
    )
    flattened["waveform_to_decoded_adjacent_cosine_gap"] = round(
        float(decoded_metrics["adjacent_cosine_mean"]) - float(waveform_metrics["adjacent_cosine_mean"]),
        6,
    )
    return flattened


def summarize_stage_delta_vs_baseline(
    *,
    candidate_stage_metrics: dict[str, dict[str, float]],
    baseline_stage_metrics: dict[str, dict[str, float]],
) -> dict[str, float]:
    deltas: dict[str, float] = {}
    for stage_name, metrics in candidate_stage_metrics.items():
        baseline_metrics = dict(baseline_stage_metrics.get(stage_name, {}))
        for key, value in metrics.items():
            deltas[f"{stage_name}_{key}_delta_vs_baseline"] = round(
                float(value) - float(baseline_metrics.get(key, 0.0)),
                6,
            )
    return deltas


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
                    "stage_delta_vs_baseline": {},
                },
            )
            bucket["record_count"] = int(bucket["record_count"]) + 1
            for key, value in dict(variant_row["scalar_metrics"]).items():
                bucket["scalar_metrics"].setdefault(key, []).append(float(value))
            for key, value in dict(variant_row["delta_vs_baseline"]).items():
                bucket["delta_vs_baseline"].setdefault(key, []).append(float(value))
            for key, value in dict(variant_row["stage_delta_vs_baseline"]).items():
                bucket["stage_delta_vs_baseline"].setdefault(key, []).append(float(value))
    aggregates = []
    for label, payload in variant_map.items():
        aggregates.append(
            {
                "label": label,
                "description": payload["description"],
                "record_count": int(payload["record_count"]),
                "scalar_metrics": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["scalar_metrics"]).items()
                },
                "delta_vs_baseline": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["delta_vs_baseline"]).items()
                },
                "stage_delta_vs_baseline": {
                    key: summarize_scalar_values(values)
                    for key, values in dict(payload["stage_delta_vs_baseline"]).items()
                },
            }
        )
    return sorted(
        aggregates,
        key=lambda item: (
            0 if item["label"] == "baseline" else 1,
            -abs(
                float(
                    item["delta_vs_baseline"]
                    .get("waveform_mean_abs_delta_vs_baseline", {})
                    .get("mean", 0.0)
                )
            ),
        ),
    )


def build_variant_impact_ranking(aggregate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ranking = []
    for row in aggregate_rows:
        if row["label"] == "baseline":
            continue
        scalar_metrics = dict(row["scalar_metrics"])
        delta_vs_baseline = dict(row["delta_vs_baseline"])
        ranking.append(
            {
                "label": row["label"],
                "description": row["description"],
                "mean_waveform_mean_abs_delta_vs_baseline": float(
                    delta_vs_baseline.get("waveform_mean_abs_delta_vs_baseline", {}).get("mean", 0.0)
                ),
                "mean_fused_to_waveform_template_cosine_gap": float(
                    scalar_metrics.get("fused_to_waveform_template_cosine_gap", {}).get("mean", 0.0)
                ),
                "mean_fused_to_waveform_adjacent_cosine_gap": float(
                    scalar_metrics.get("fused_to_waveform_adjacent_cosine_gap", {}).get("mean", 0.0)
                ),
                "mean_waveform_frames_template_cosine_mean": float(
                    scalar_metrics.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0)
                ),
                "mean_decoded_frame_template_cosine_mean": float(
                    scalar_metrics.get("decoded_frames_template_cosine_mean", {}).get("mean", 0.0)
                ),
            }
        )
    return sorted(
        ranking,
        key=lambda item: abs(float(item["mean_waveform_mean_abs_delta_vs_baseline"])),
        reverse=True,
    )


def build_baseline_decoder_collapse_summary(aggregate_rows: list[dict[str, object]]) -> dict[str, float | str]:
    baseline_row = next((row for row in aggregate_rows if row["label"] == "baseline"), None)
    if baseline_row is None:
        return {}
    scalar_metrics = dict(baseline_row["scalar_metrics"])
    fused_template = float(scalar_metrics.get("fused_hidden_template_cosine_mean", {}).get("mean", 0.0))
    waveform_template = float(scalar_metrics.get("waveform_frames_template_cosine_mean", {}).get("mean", 0.0))
    decoded_template = float(scalar_metrics.get("decoded_frames_template_cosine_mean", {}).get("mean", 0.0))
    fused_adjacent = float(scalar_metrics.get("fused_hidden_adjacent_cosine_mean", {}).get("mean", 0.0))
    waveform_adjacent = float(scalar_metrics.get("waveform_frames_adjacent_cosine_mean", {}).get("mean", 0.0))
    decoder_gap_template = round(waveform_template - fused_template, 6)
    decoder_gap_adjacent = round(waveform_adjacent - fused_adjacent, 6)
    if decoder_gap_template >= 0.15 and decoder_gap_adjacent >= 0.15:
        diagnosis = "waveform_decoder_collapse_likely"
    elif decoder_gap_template >= 0.08 or decoder_gap_adjacent >= 0.08:
        diagnosis = "waveform_decoder_collapse_possible"
    else:
        diagnosis = "collapse_not_localized_to_waveform_decoder"
    return {
        "fused_hidden_template_cosine_mean": round(fused_template, 6),
        "waveform_frames_template_cosine_mean": round(waveform_template, 6),
        "decoded_frames_template_cosine_mean": round(decoded_template, 6),
        "fused_hidden_adjacent_cosine_mean": round(fused_adjacent, 6),
        "waveform_frames_adjacent_cosine_mean": round(waveform_adjacent, 6),
        "fused_to_waveform_template_cosine_gap": decoder_gap_template,
        "fused_to_waveform_adjacent_cosine_gap": decoder_gap_adjacent,
        "diagnosis": diagnosis,
    }


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Waveform Decoder Structure Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- checkpoint_path: {summary['checkpoint_path']}",
        f"- checkpoint_selection_path: {summary['checkpoint_selection_path']}",
        f"- selection_target: {summary['selection_target']}",
        f"- selected_checkpoint_summary: {json.dumps(summary['selected_checkpoint_summary'], ensure_ascii=False)}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- decode_runtime: {json.dumps(summary['decode_runtime'], ensure_ascii=False)}",
        f"- baseline_decoder_collapse_summary: {json.dumps(summary['baseline_decoder_collapse_summary'], ensure_ascii=False)}",
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
            f"fused_adjacent={scalar_metrics.get('fused_hidden_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"waveform_adjacent={scalar_metrics.get('waveform_frames_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"decoded_adjacent={scalar_metrics.get('decoded_frames_adjacent_cosine_mean', {}).get('mean', 0.0)}, "
            f"fused_to_waveform_template_gap={scalar_metrics.get('fused_to_waveform_template_cosine_gap', {}).get('mean', 0.0)}, "
            f"fused_to_waveform_adjacent_gap={scalar_metrics.get('fused_to_waveform_adjacent_cosine_gap', {}).get('mean', 0.0)}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
