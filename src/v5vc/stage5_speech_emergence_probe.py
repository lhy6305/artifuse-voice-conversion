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
from v5vc.offline_vocoder_training import (
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
    reconstruct_waveform_from_frames,
)
from v5vc.stage5_low_activity_probe import compute_waveform_spectral_summary


STANDARD_ROOT_CAUSE_VARIANTS = [
    {
        "label": "baseline",
        "description": "Original checkpoint inputs without any probe override.",
        "transforms": [],
    },
    {
        "label": "z_art_zero",
        "description": "Zero the periodic z_art family to test whether articulated latent content is used at all.",
        "transforms": [("periodic", "z_art", "zero")],
    },
    {
        "label": "z_art_frame_mean",
        "description": "Collapse z_art dynamics to the package-wise frame mean while preserving its coarse level.",
        "transforms": [("periodic", "z_art", "frame_mean")],
    },
    {
        "label": "event_probs_zero",
        "description": "Zero the noise-branch event probabilities to test whether event conditioning materially changes the decoded output.",
        "transforms": [("noise", "event_probs", "zero")],
    },
    {
        "label": "event_probs_frame_mean",
        "description": "Collapse event probability dynamics to the package-wise frame mean.",
        "transforms": [("noise", "event_probs", "frame_mean")],
    },
    {
        "label": "periodic_proxies_zero",
        "description": "Zero periodic voiced/energy proxies to test whether the route mostly follows low-order envelope hints.",
        "transforms": [
            ("periodic", "voiced_proxy", "zero"),
            ("periodic", "energy_proxy", "zero"),
        ],
    },
    {
        "label": "periodic_proxies_frame_mean",
        "description": "Collapse periodic voiced/energy dynamics to the package-wise frame mean.",
        "transforms": [
            ("periodic", "voiced_proxy", "frame_mean"),
            ("periodic", "energy_proxy", "frame_mean"),
        ],
    },
    {
        "label": "noise_proxies_zero",
        "description": "Zero aperiodicity/event-presence/energy-change proxies on the noise branch.",
        "transforms": [
            ("noise", "aperiodicity_proxy", "zero"),
            ("noise", "event_presence_proxy", "zero"),
            ("noise", "energy_change_proxy", "zero"),
            ("noise", "energy_proxy", "zero"),
        ],
    },
    {
        "label": "noise_proxies_frame_mean",
        "description": "Collapse noise-branch proxy dynamics to the package-wise frame mean.",
        "transforms": [
            ("noise", "aperiodicity_proxy", "frame_mean"),
            ("noise", "event_presence_proxy", "frame_mean"),
            ("noise", "energy_change_proxy", "frame_mean"),
            ("noise", "energy_proxy", "frame_mean"),
        ],
    },
    {
        "label": "conditioning_zero",
        "description": "Zero alpha/speaker/geom conditioning to test whether constant target conditioning dominates the decoded behavior.",
        "transforms": [
            ("periodic", "alpha", "zero"),
            ("periodic", "s_spk_target", "zero"),
            ("periodic", "s_geom_target", "zero"),
            ("noise", "alpha", "zero"),
            ("noise", "s_spk_target", "zero"),
        ],
    },
]


def analyze_stage5_nores_speech_emergence(
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
    checkpoint_payload = torch.load(resolved_checkpoint_path, map_location="cpu", weights_only=False)
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the speech-emergence probe.")

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
    aggregate_rows: list[dict[str, object]] = []
    reference_variant_label = "baseline"

    with torch.no_grad():
        for entry in package_entries:
            package_path = Path(str(entry["training_package_path"])).resolve()
            payload = load_training_package_payload(package_path)
            runtime = extract_training_runtime(payload)
            batch = extract_training_batch(payload)
            scaffold_payload = torch.load(Path(str(payload["source_scaffold_path"])).resolve(), map_location="cpu", weights_only=False)
            feature_layout = build_stage5_scaffold_feature_layout(scaffold_payload)

            variant_runs = []
            baseline_waveform = None
            baseline_metrics = None
            for variant in STANDARD_ROOT_CAUSE_VARIANTS:
                periodic_features, noise_features, transform_notes = apply_variant_to_batch_features(
                    batch=batch,
                    feature_layout=feature_layout,
                    transforms=list(variant["transforms"]),
                )
                scalar_metrics, decoded_waveform = run_probe_variant(
                    model=model,
                    periodic_branch_features=periodic_features,
                    noise_branch_features=noise_features,
                    aligned_waveform=batch["aligned_waveform"],
                    frame_length=int(runtime["frame_length"]),
                    hop_length=int(runtime["hop_length"]),
                    sample_rate=int(runtime["sample_rate"]),
                    device=resolved_device,
                    use_predicted_activity_gate=bool(use_predicted_activity_gate),
                    predicted_activity_gate_floor=float(predicted_activity_gate_floor),
                    predicted_activity_gate_smoothing_frames=int(predicted_activity_gate_smoothing_frames),
                    predicted_activity_gate_apply_mode=resolved_apply_mode,
                )
                variant_row = {
                    "label": variant["label"],
                    "description": variant["description"],
                    "transform_notes": transform_notes,
                    "scalar_metrics": scalar_metrics,
                }
                if variant["label"] == reference_variant_label:
                    baseline_waveform = decoded_waveform
                    baseline_metrics = scalar_metrics
                variant_runs.append(variant_row)

            if baseline_waveform is None or baseline_metrics is None:
                raise RuntimeError("Stage5 speech-emergence probe failed to produce a baseline variant.")

            for variant_row in variant_runs:
                variant_row["delta_vs_baseline"] = summarize_probe_delta_vs_baseline(
                    candidate_metrics=variant_row["scalar_metrics"],
                    baseline_metrics=baseline_metrics,
                    candidate_waveform=baseline_waveform if variant_row["label"] == reference_variant_label else None,
                    baseline_waveform=baseline_waveform,
                )

            per_record_rows.append(
                {
                    "record_id": str(entry["record_id"]),
                    "training_package_path": package_path.as_posix(),
                    "source_scaffold_path": str(payload["source_scaffold_path"]),
                    "variants": variant_runs,
                }
            )

    aggregate_rows = build_variant_aggregates(per_record_rows)
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint_path": resolved_checkpoint_path.as_posix(),
        "checkpoint_selection_path": None if checkpoint_selection_path is None else checkpoint_selection_path.resolve().as_posix(),
        "selection_target": None if checkpoint_selection_path is None else str(selection_target),
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
        },
        "probe_variants": [
            {
                "label": item["label"],
                "description": item["description"],
                "transforms": [f"{branch}.{semantic}={mode}" for branch, semantic, mode in item["transforms"]],
            }
            for item in STANDARD_ROOT_CAUSE_VARIANTS
        ],
        "variant_impact_ranking": build_variant_impact_ranking(aggregate_rows),
        "variant_aggregates": aggregate_rows,
        "records": per_record_rows,
        "notes": [
            "This probe is route-level root-cause support for the Stage5 no-res speech-emergence failure, not a checkpoint ranking pass.",
            "The baseline variant uses the current export-style decode semantics so the numbers stay aligned with the heard Stage5 route: predicted gate on, smooth3, and post_ola_envelope.",
            "zero means an entire control family slice is forced to 0.0 at inference time; frame_mean means the family loses all frame-to-frame dynamics but keeps its package-wise average level.",
            "If a family override barely changes decoded waveform and spectral metrics, that is evidence the current checkpoint is not strongly using that family.",
            "If proxy-family overrides dominate while z_art/event overrides stay weak, the route is likely leaning on low-order envelope proxies rather than speech-structural control.",
        ],
    }
    json_path = output_dir / "stage5_speech_emergence_probe.json"
    md_path = output_dir / "stage5_speech_emergence_probe.md"
    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(
        build_probe_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def build_stage5_scaffold_feature_layout(scaffold_payload: dict[str, object]) -> dict[str, dict[str, tuple[int, int]]]:
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
    return {"periodic": periodic, "noise": noise}


def apply_variant_to_batch_features(
    *,
    batch: dict[str, torch.Tensor],
    feature_layout: dict[str, dict[str, tuple[int, int]]],
    transforms: list[tuple[str, str, str]],
) -> tuple[torch.Tensor, torch.Tensor, list[str]]:
    periodic_features = batch["periodic_branch_features"].detach().clone().to(torch.float32)
    noise_features = batch["noise_branch_features"].detach().clone().to(torch.float32)
    transform_notes: list[str] = []
    for branch_name, semantic, mode in transforms:
        slice_info = feature_layout[branch_name].get(semantic)
        if slice_info is None:
            continue
        start, end = slice_info
        branch_features = periodic_features if branch_name == "periodic" else noise_features
        if mode == "zero":
            branch_features[:, start:end] = 0.0
        elif mode == "frame_mean":
            mean_values = branch_features[:, start:end].mean(dim=0, keepdim=True)
            branch_features[:, start:end] = mean_values.expand(branch_features.shape[0], end - start)
        else:
            raise ValueError(f"Unsupported Stage5 speech-emergence probe mode: {mode!r}")
        transform_notes.append(f"{branch_name}.{semantic} -> {mode}[{start}:{end}]")
    return periodic_features, noise_features, transform_notes


def run_probe_variant(
    *,
    model: torch.nn.Module,
    periodic_branch_features: torch.Tensor,
    noise_branch_features: torch.Tensor,
    aligned_waveform: torch.Tensor | None,
    frame_length: int,
    hop_length: int,
    sample_rate: int,
    device: torch.device,
    use_predicted_activity_gate: bool,
    predicted_activity_gate_floor: float,
    predicted_activity_gate_smoothing_frames: int,
    predicted_activity_gate_apply_mode: str,
) -> tuple[dict[str, float], torch.Tensor]:
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
        frame_gain_apply_mode=predicted_activity_gate_apply_mode,
    ).detach().cpu().to(torch.float32)
    periodic_gate = outputs["periodic_gate"].detach().cpu().to(torch.float32).view(-1)
    noise_gate = outputs["noise_gate"].detach().cpu().to(torch.float32).view(-1)
    predicted_activity_cpu = predicted_activity.detach().cpu().to(torch.float32).view(-1)
    waveform_frames = outputs["waveform_frames"].detach().cpu().to(torch.float32)
    decoded_spectral = compute_waveform_spectral_summary(decoded_waveform, int(sample_rate))
    metrics = {
        "periodic_gate_mean": round(float(periodic_gate.mean().item()), 6),
        "noise_gate_mean": round(float(noise_gate.mean().item()), 6),
        "predicted_activity_mean": round(float(predicted_activity_cpu.mean().item()), 6),
        "predicted_activity_std": round(float(predicted_activity_cpu.std(unbiased=False).item()), 6),
        "waveform_frames_std": round(float(waveform_frames.std(unbiased=False).item()), 6),
        "waveform_frames_abs_mean": round(float(waveform_frames.abs().mean().item()), 6),
        "waveform_frames_clip_fraction_abs_ge_095": round(
            float((waveform_frames.abs() >= 0.95).to(torch.float32).mean().item()),
            6,
        ),
        "decoded_waveform_rms": round(float(decoded_waveform.pow(2).mean().sqrt().item()), 6),
        "decoded_abs_mean": round(float(decoded_waveform.abs().mean().item()), 6),
        "decoded_peak_abs": round(float(decoded_waveform.abs().max().item()), 6),
        "decoded_zero_crossing_rate": round(float(compute_zero_crossing_rate(decoded_waveform)), 6),
        "decoded_spectral_centroid_hz": float(decoded_spectral["centroid_hz"]),
        "decoded_spectral_bandwidth_hz": float(decoded_spectral["bandwidth_hz"]),
        "decoded_spectral_rolloff95_hz": float(decoded_spectral["rolloff95_hz"]),
        "decoded_spectral_high_band_energy_ratio": float(decoded_spectral["high_band_energy_ratio"]),
    }
    if aligned_waveform is not None:
        aligned_waveform_cpu = aligned_waveform.detach().cpu().to(torch.float32)[: decoded_waveform.shape[0]]
        aligned_spectral = compute_waveform_spectral_summary(aligned_waveform_cpu, int(sample_rate))
        aligned_rms = float(aligned_waveform_cpu.pow(2).mean().sqrt().item())
        metrics.update(
            {
                "aligned_waveform_rms": round(aligned_rms, 6),
                "decoded_to_aligned_rms_ratio": round(
                    0.0 if aligned_rms <= 1.0e-8 else float(decoded_waveform.pow(2).mean().sqrt().item()) / aligned_rms,
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
    return metrics, decoded_waveform


def summarize_probe_delta_vs_baseline(
    *,
    candidate_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
    candidate_waveform: torch.Tensor | None,
    baseline_waveform: torch.Tensor,
) -> dict[str, float]:
    if candidate_waveform is None:
        candidate_waveform = baseline_waveform
    common_length = int(min(candidate_waveform.shape[0], baseline_waveform.shape[0]))
    if common_length > 0:
        candidate_slice = candidate_waveform[:common_length]
        baseline_slice = baseline_waveform[:common_length]
        waveform_mean_abs_delta = float((candidate_slice - baseline_slice).abs().mean().item())
        baseline_rms = float(baseline_slice.pow(2).mean().sqrt().item())
        candidate_rms = float(candidate_slice.pow(2).mean().sqrt().item())
    else:
        waveform_mean_abs_delta = 0.0
        baseline_rms = 0.0
        candidate_rms = 0.0
    return {
        "waveform_mean_abs_delta_vs_baseline": round(waveform_mean_abs_delta, 6),
        "decoded_waveform_rms_delta_vs_baseline": round(
            float(candidate_metrics["decoded_waveform_rms"]) - float(baseline_metrics["decoded_waveform_rms"]),
            6,
        ),
        "decoded_zero_crossing_rate_delta_vs_baseline": round(
            float(candidate_metrics["decoded_zero_crossing_rate"]) - float(baseline_metrics["decoded_zero_crossing_rate"]),
            6,
        ),
        "decoded_spectral_centroid_delta_hz_vs_baseline": round(
            float(candidate_metrics["decoded_spectral_centroid_hz"]) - float(baseline_metrics["decoded_spectral_centroid_hz"]),
            6,
        ),
        "decoded_spectral_high_band_ratio_delta_vs_baseline": round(
            float(candidate_metrics["decoded_spectral_high_band_energy_ratio"])
            - float(baseline_metrics["decoded_spectral_high_band_energy_ratio"]),
            6,
        ),
        "predicted_activity_mean_delta_vs_baseline": round(
            float(candidate_metrics["predicted_activity_mean"]) - float(baseline_metrics["predicted_activity_mean"]),
            6,
        ),
        "baseline_waveform_rms": round(float(baseline_rms), 6),
        "candidate_waveform_rms": round(float(candidate_rms), 6),
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
            }
        )
    return sorted(
        aggregates,
        key=lambda item: (
            0 if item["label"] == "baseline" else 1,
            -float(
                item["delta_vs_baseline"]
                .get("waveform_mean_abs_delta_vs_baseline", {})
                .get("mean", 0.0)
            ),
        ),
    )


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


def build_variant_impact_ranking(aggregate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ranked = []
    for row in aggregate_rows:
        if row["label"] == "baseline":
            continue
        deltas = dict(row["delta_vs_baseline"])
        ranked.append(
            {
                "label": row["label"],
                "description": row["description"],
                "mean_waveform_mean_abs_delta_vs_baseline": float(
                    deltas.get("waveform_mean_abs_delta_vs_baseline", {}).get("mean", 0.0)
                ),
                "mean_decoded_spectral_centroid_delta_hz_vs_baseline": float(
                    deltas.get("decoded_spectral_centroid_delta_hz_vs_baseline", {}).get("mean", 0.0)
                ),
                "mean_decoded_spectral_high_band_ratio_delta_vs_baseline": float(
                    deltas.get("decoded_spectral_high_band_ratio_delta_vs_baseline", {}).get("mean", 0.0)
                ),
                "mean_predicted_activity_mean_delta_vs_baseline": float(
                    deltas.get("predicted_activity_mean_delta_vs_baseline", {}).get("mean", 0.0)
                ),
            }
        )
    return sorted(
        ranked,
        key=lambda item: abs(float(item["mean_waveform_mean_abs_delta_vs_baseline"])),
        reverse=True,
    )


def compute_zero_crossing_rate(waveform: torch.Tensor) -> float:
    if int(waveform.numel()) < 2:
        return 0.0
    left = waveform[:-1]
    right = waveform[1:]
    return float(((left * right) < 0).to(torch.float32).mean().item())


def build_probe_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 No-Res Speech-Emergence Probe",
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
        "",
        "## Variant Impact Ranking",
    ]
    for item in list(summary.get("variant_impact_ranking", [])):
        lines.append(
            f"- label={item['label']} "
            f"waveform_mean_abs_delta_vs_baseline={item['mean_waveform_mean_abs_delta_vs_baseline']} "
            f"decoded_spectral_centroid_delta_hz_vs_baseline={item['mean_decoded_spectral_centroid_delta_hz_vs_baseline']} "
            f"decoded_spectral_high_band_ratio_delta_vs_baseline={item['mean_decoded_spectral_high_band_ratio_delta_vs_baseline']} "
            f"predicted_activity_mean_delta_vs_baseline={item['mean_predicted_activity_mean_delta_vs_baseline']}"
        )
    lines.extend(["", "## Variant Aggregates"])
    for item in list(summary.get("variant_aggregates", [])):
        lines.append(
            f"- label={item['label']} "
            f"record_count={item['record_count']} "
            f"delta_vs_baseline={json.dumps(item['delta_vs_baseline'], ensure_ascii=False)} "
            f"scalar_metrics={json.dumps(item['scalar_metrics'], ensure_ascii=False)}"
        )
    lines.extend(["", "## Notes"])
    for note in list(summary.get("notes", [])):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
