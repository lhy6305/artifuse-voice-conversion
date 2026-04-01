from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.nores_vocoder_audio_export import resolve_package_entries
from v5vc.offline_vocoder_training import (
    DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    extract_training_batch,
    extract_training_runtime,
    load_training_package_payload,
)
from v5vc.stage5_representation_oracle_probe import (
    DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    DEFAULT_WAVEFORM_MLP_LR,
    DEFAULT_WAVEFORM_MLP_STEPS,
    build_target_proxy_bundle,
    compute_mean_frame_cosine,
    compute_pearson_correlation,
    fit_ridge_readout,
    predict_mlp_readout,
    predict_ridge_readout,
)
from v5vc.stage5_source_scaffold_oracle_probe import build_candidate_stage_sequences


DEFAULT_WAVEFORM_CODE_DIMS = (8, 16, 32, 64, 96, 128)


def analyze_stage5_nores_fine_structure_code_oracle_probe(
    *,
    output_dir: Path,
    dataset_index_path: Path,
    split_name: str,
    sample_count: int,
    target_record_ids: list[str] | None,
    active_frame_rms_threshold: float = DEFAULT_ACTIVE_TEMPLATE_FRAME_RMS_THRESHOLD,
    logspec_bins: int = 48,
    ridge_lambda: float = 1.0,
    waveform_mlp_hidden_dim: int = DEFAULT_WAVEFORM_MLP_HIDDEN_DIM,
    waveform_mlp_steps: int = DEFAULT_WAVEFORM_MLP_STEPS,
    waveform_mlp_lr: float = DEFAULT_WAVEFORM_MLP_LR,
    code_dims: tuple[int, ...] = DEFAULT_WAVEFORM_CODE_DIMS,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_index_path = dataset_index_path.resolve()
    dataset_index = json.loads(dataset_index_path.read_text(encoding="utf-8"))
    package_entries = resolve_package_entries(
        dataset_index=dataset_index,
        split_name=split_name,
        sample_count=sample_count,
        target_record_ids=target_record_ids,
    )
    if not package_entries:
        raise ValueError("No Stage5 training packages were selected for the fine-structure code oracle probe.")

    normalized_code_dims = tuple(sorted({max(1, int(dim)) for dim in code_dims}))
    record_rows: list[dict[str, object]] = []
    cross_record_inputs: list[dict[str, object]] = []

    for entry in package_entries:
        payload = load_training_package_payload(Path(str(entry["training_package_path"])).resolve())
        batch = extract_training_batch(payload)
        runtime = extract_training_runtime(payload)
        candidate_sequences = build_candidate_stage_sequences(package_payload=payload)
        target_bundle = build_target_proxy_bundle(
            batch=batch,
            aligned_waveform=batch["aligned_waveform"],
            frame_length=int(runtime["frame_length"]),
            hop_length=int(runtime["hop_length"]),
            periodic_gate_target=batch["periodic_gate_target"],
            active_frame_rms_threshold=float(active_frame_rms_threshold),
            logspec_bins=int(logspec_bins),
        )
        selected_dynamic = expect_stage_sequence(candidate_sequences, "selected_dynamic_controls")
        compact_reference = expect_stage_sequence(candidate_sequences, "fine_structure_reference_family")
        waveform_reference = expect_stage_sequence(candidate_sequences, "fine_structure_waveform_reference_family")
        active_mask = target_bundle["active_mask"].detach().cpu().to(torch.bool)
        frame_count = min(
            int(active_mask.shape[0]),
            int(selected_dynamic.shape[0]),
            int(compact_reference.shape[0]),
            int(waveform_reference.shape[0]),
            int(target_bundle["target_rms"].shape[0]),
            int(target_bundle["target_voicing"].shape[0]),
            int(target_bundle["target_logspec"].shape[0]),
            int(target_bundle["target_waveform_frames"].shape[0]),
        )
        active_mask = active_mask[:frame_count]
        if not bool(active_mask.any()):
            active_mask = torch.ones((frame_count,), dtype=torch.bool)
        row = {
            "record_id": str(entry["record_id"]),
            "training_package_path": str(entry["training_package_path"]),
            "frame_count": int(frame_count),
            "active_frame_count": int(active_mask.to(torch.int64).sum().item()),
        }
        cross_record_inputs.append(
            {
                "record_id": str(entry["record_id"]),
                "selected_dynamic": selected_dynamic[:frame_count][active_mask].detach().cpu().to(torch.float32),
                "compact_reference": compact_reference[:frame_count][active_mask].detach().cpu().to(torch.float32),
                "waveform_reference": waveform_reference[:frame_count][active_mask].detach().cpu().to(torch.float32),
                "target_rms": target_bundle["target_rms"][:frame_count].detach().cpu().to(torch.float32).unsqueeze(-1)[
                    active_mask
                ],
                "target_voicing": target_bundle["target_voicing"][:frame_count]
                .detach()
                .cpu()
                .to(torch.float32)
                .unsqueeze(-1)[active_mask],
                "target_logspec": target_bundle["target_logspec"][:frame_count].detach().cpu().to(torch.float32)[
                    active_mask
                ],
                "target_waveform_frames": target_bundle["target_waveform_frames"][:frame_count]
                .detach()
                .cpu()
                .to(torch.float32)[active_mask],
            }
        )
        record_rows.append(row)

    cross_record_stage_aggregates = build_cross_record_code_aggregates(
        record_rows=cross_record_inputs,
        code_dims=normalized_code_dims,
        ridge_lambda=float(ridge_lambda),
        waveform_mlp_hidden_dim=int(waveform_mlp_hidden_dim),
        waveform_mlp_steps=int(waveform_mlp_steps),
        waveform_mlp_lr=float(waveform_mlp_lr),
    )
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_index_path": dataset_index_path.as_posix(),
        "split_name": str(split_name),
        "sample_count": len(record_rows),
        "probe_config": {
            "active_frame_rms_threshold": float(active_frame_rms_threshold),
            "logspec_bins": int(logspec_bins),
            "ridge_lambda": float(ridge_lambda),
            "waveform_mlp_hidden_dim": int(waveform_mlp_hidden_dim),
            "waveform_mlp_steps": int(waveform_mlp_steps),
            "waveform_mlp_lr": float(waveform_mlp_lr),
            "code_dims": list(normalized_code_dims),
        },
        "cross_record_stage_aggregates": cross_record_stage_aggregates,
        "fine_structure_code_summary": build_code_summary(cross_record_stage_aggregates),
        "records": record_rows,
        "notes": [
            "This probe keeps the new analysis-only unit_rms_waveform_frame family as an upper bound, then fits compact waveform-geometry PCA codes on train records only inside each leave-one-record-out fold.",
            "compact_reference means the hand-designed unit_rms_logspec plus delta family added in 567.",
            "selected_dynamic_controls remains the current deployable Stage5 dynamic-control baseline.",
            "waveform_pca_code_dim_* families are train-fold-learned compact codes derived from unit_rms_waveform_frame rather than magnitude-only compact spectra.",
        ],
    }
    (output_dir / "stage5_fine_structure_code_oracle_probe.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "stage5_fine_structure_code_oracle_probe.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def expect_stage_sequence(candidate_sequences: dict[str, torch.Tensor], stage_name: str) -> torch.Tensor:
    stage_sequence = candidate_sequences.get(stage_name)
    if not isinstance(stage_sequence, torch.Tensor):
        raise ValueError(f"Required fine-structure oracle stage is missing from source scaffold: {stage_name}")
    return stage_sequence.detach().cpu().to(torch.float32)


def build_cross_record_code_aggregates(
    *,
    record_rows: list[dict[str, object]],
    code_dims: tuple[int, ...],
    ridge_lambda: float,
    waveform_mlp_hidden_dim: int,
    waveform_mlp_steps: int,
    waveform_mlp_lr: float,
) -> list[dict[str, object]]:
    if len(record_rows) <= 1:
        return []
    stage_names = [
        "selected_dynamic_controls",
        "compact_reference",
        "waveform_reference_upper_bound",
        *[f"waveform_pca_code_dim_{code_dim}" for code_dim in code_dims],
        *[f"selected_dynamic_plus_waveform_pca_code_dim_{code_dim}" for code_dim in code_dims],
    ]
    stage_rows: list[dict[str, object]] = []
    for stage_name in stage_names:
        heldout_rows = []
        for heldout_index, heldout_record in enumerate(record_rows):
            train_rows = [row for index, row in enumerate(record_rows) if index != heldout_index]
            if not train_rows:
                continue
            train_waveform = torch.cat([row["waveform_reference"] for row in train_rows], dim=0)
            code_dim = parse_waveform_code_dim(stage_name)
            pca_projection = None if code_dim is None else fit_pca_projection(train_waveform, code_dim=code_dim)
            train_x = build_stage_feature_matrix(stage_name=stage_name, row=train_rows[0], pca_projection=pca_projection)
            train_x = torch.cat(
                [build_stage_feature_matrix(stage_name=stage_name, row=row, pca_projection=pca_projection) for row in train_rows],
                dim=0,
            )
            test_x = build_stage_feature_matrix(
                stage_name=stage_name,
                row=heldout_record,
                pca_projection=pca_projection,
            )
            train_rms = torch.cat([row["target_rms"] for row in train_rows], dim=0)
            train_voicing = torch.cat([row["target_voicing"] for row in train_rows], dim=0)
            train_logspec = torch.cat([row["target_logspec"] for row in train_rows], dim=0)
            train_waveform_target = torch.cat([row["target_waveform_frames"] for row in train_rows], dim=0)
            test_rms = heldout_record["target_rms"]
            test_voicing = heldout_record["target_voicing"]
            test_logspec = heldout_record["target_logspec"]
            test_waveform_target = heldout_record["target_waveform_frames"]
            rms_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_rms, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            voicing_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_voicing, ridge_lambda=float(ridge_lambda)),
                test_x,
            ).clamp(0.0, 1.0)
            logspec_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_logspec, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            waveform_pred = predict_ridge_readout(
                fit_ridge_readout(train_x=train_x, train_y=train_waveform_target, ridge_lambda=float(ridge_lambda)),
                test_x,
            )
            waveform_mlp_pred = predict_mlp_readout(
                train_x=train_x,
                train_y=train_waveform_target,
                test_x=test_x,
                hidden_dim=int(waveform_mlp_hidden_dim),
                train_steps=int(waveform_mlp_steps),
                learning_rate=float(waveform_mlp_lr),
            )
            voicing_accuracy = (
                voicing_pred.ge(0.5).eq(test_voicing.ge(0.5)).to(torch.float32).mean()
                if int(test_voicing.shape[0]) > 0
                else test_voicing.new_tensor(0.0)
            )
            heldout_rows.append(
                {
                    "record_id": str(heldout_record["record_id"]),
                    "oracle_rms_corr": float(compute_pearson_correlation(rms_pred.view(-1), test_rms.view(-1))),
                    "oracle_vuv_accuracy": float(voicing_accuracy.item()),
                    "oracle_logspec_frame_cosine_mean": compute_mean_frame_cosine(logspec_pred, test_logspec),
                    "oracle_waveform_frame_cosine_mean": compute_mean_frame_cosine(waveform_pred, test_waveform_target),
                    "oracle_waveform_mlp_frame_cosine_mean": compute_mean_frame_cosine(
                        waveform_mlp_pred, test_waveform_target
                    ),
                    "feature_dim": int(test_x.shape[-1]),
                }
            )
        if heldout_rows:
            stage_rows.append(
                {
                    "stage_name": stage_name,
                    "record_count": len(heldout_rows),
                    "feature_dim": int(heldout_rows[0]["feature_dim"]),
                    "oracle_logspec_frame_cosine_mean": mean_rows(heldout_rows, "oracle_logspec_frame_cosine_mean"),
                    "oracle_waveform_frame_cosine_mean": mean_rows(heldout_rows, "oracle_waveform_frame_cosine_mean"),
                    "oracle_waveform_mlp_frame_cosine_mean": mean_rows(
                        heldout_rows, "oracle_waveform_mlp_frame_cosine_mean"
                    ),
                    "oracle_rms_corr_mean": mean_rows(heldout_rows, "oracle_rms_corr"),
                    "oracle_vuv_accuracy_mean": mean_rows(heldout_rows, "oracle_vuv_accuracy"),
                    "heldout_records": heldout_rows,
                }
            )
    return stage_rows


def parse_waveform_code_dim(stage_name: str) -> int | None:
    prefix = "waveform_pca_code_dim_"
    joined_prefix = "selected_dynamic_plus_waveform_pca_code_dim_"
    if stage_name.startswith(prefix):
        return int(stage_name[len(prefix) :])
    if stage_name.startswith(joined_prefix):
        return int(stage_name[len(joined_prefix) :])
    return None


def build_stage_feature_matrix(
    *,
    stage_name: str,
    row: dict[str, object],
    pca_projection: dict[str, torch.Tensor] | None,
) -> torch.Tensor:
    if stage_name == "selected_dynamic_controls":
        return row["selected_dynamic"]
    if stage_name == "compact_reference":
        return row["compact_reference"]
    if stage_name == "waveform_reference_upper_bound":
        return row["waveform_reference"]
    if stage_name.startswith("waveform_pca_code_dim_"):
        if pca_projection is None:
            raise ValueError(f"PCA projection is required for {stage_name}.")
        return project_pca_code(row["waveform_reference"], pca_projection)
    if stage_name.startswith("selected_dynamic_plus_waveform_pca_code_dim_"):
        if pca_projection is None:
            raise ValueError(f"PCA projection is required for {stage_name}.")
        return torch.cat(
            [row["selected_dynamic"], project_pca_code(row["waveform_reference"], pca_projection)],
            dim=-1,
        )
    raise ValueError(f"Unsupported fine-structure code oracle stage: {stage_name}")


def fit_pca_projection(train_waveform: torch.Tensor, *, code_dim: int) -> dict[str, torch.Tensor]:
    waveform = train_waveform.detach().cpu().to(torch.float32)
    mean = waveform.mean(dim=0, keepdim=True)
    centered = waveform - mean
    max_rank = min(int(centered.shape[0]), int(centered.shape[1]), max(1, int(code_dim)))
    if max_rank <= 0:
        raise ValueError(f"Invalid PCA rank for code_dim={code_dim}.")
    _, _, vh = torch.linalg.svd(centered, full_matrices=False)
    components = vh[:max_rank].transpose(0, 1).contiguous()
    return {
        "mean": mean,
        "components": components,
    }


def project_pca_code(waveform_reference: torch.Tensor, pca_projection: dict[str, torch.Tensor]) -> torch.Tensor:
    centered = waveform_reference.detach().cpu().to(torch.float32) - pca_projection["mean"]
    return centered @ pca_projection["components"]


def build_code_summary(cross_record_stage_aggregates: list[dict[str, object]]) -> dict[str, object]:
    by_stage = {str(item["stage_name"]): item for item in cross_record_stage_aggregates}
    summary: dict[str, object] = {}
    selected_dynamic = by_stage.get("selected_dynamic_controls")
    compact_reference = by_stage.get("compact_reference")
    waveform_reference = by_stage.get("waveform_reference_upper_bound")
    if selected_dynamic is not None:
        summary["selected_dynamic_waveform_mlp"] = float(selected_dynamic["oracle_waveform_mlp_frame_cosine_mean"])
    if compact_reference is not None:
        summary["compact_reference_waveform_mlp"] = float(compact_reference["oracle_waveform_mlp_frame_cosine_mean"])
    if waveform_reference is not None:
        summary["waveform_reference_upper_bound_waveform_mlp"] = float(
            waveform_reference["oracle_waveform_mlp_frame_cosine_mean"]
        )
    pca_rows = [
        item
        for item in cross_record_stage_aggregates
        if str(item["stage_name"]).startswith("waveform_pca_code_dim_")
    ]
    if pca_rows:
        best_pca = max(pca_rows, key=lambda item: float(item.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)))
        summary["best_pca_code_stage"] = str(best_pca["stage_name"])
        summary["best_pca_code_dim"] = parse_waveform_code_dim(str(best_pca["stage_name"]))
        summary["best_pca_code_waveform"] = float(best_pca["oracle_waveform_frame_cosine_mean"])
        summary["best_pca_code_waveform_mlp"] = float(best_pca["oracle_waveform_mlp_frame_cosine_mean"])
        route_open_dim = None
        for row in sorted(pca_rows, key=lambda item: parse_waveform_code_dim(str(item["stage_name"])) or 999999):
            if float(row.get("oracle_waveform_mlp_frame_cosine_mean", 0.0)) >= 0.5:
                route_open_dim = parse_waveform_code_dim(str(row["stage_name"]))
                break
        summary["first_route_open_pca_dim"] = route_open_dim
        if route_open_dim is None:
            summary["diagnosis"] = "tested_pca_code_dims_still_too_small_or_too_weak_for_waveform_geometry"
        else:
            summary["diagnosis"] = "waveform_geometry_can_be_compressed_into_a_compact_learned_linear_code"
    else:
        summary["diagnosis"] = "missing_pca_rows"
    return summary


def mean_rows(rows: list[dict[str, object]], key: str) -> float:
    return round(sum(float(row.get(key, 0.0)) for row in rows) / float(len(rows)), 6)


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Stage5 Fine-Structure Code Oracle Probe",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- dataset_index_path: {summary['dataset_index_path']}",
        f"- split_name: {summary['split_name']}",
        f"- sample_count: {summary['sample_count']}",
        f"- probe_config: {json.dumps(summary['probe_config'], ensure_ascii=False)}",
        f"- fine_structure_code_summary: {json.dumps(summary['fine_structure_code_summary'], ensure_ascii=False)}",
        "",
        "## Cross-Record Stage Aggregates",
    ]
    for row in summary.get("cross_record_stage_aggregates", []):
        lines.append(
            "- "
            + f"{row['stage_name']}: "
            + f"feature_dim={row['feature_dim']}, "
            + f"logspec_cosine={row['oracle_logspec_frame_cosine_mean']}, "
            + f"waveform_frame_cosine={row['oracle_waveform_frame_cosine_mean']}, "
            + f"waveform_mlp_frame_cosine={row['oracle_waveform_mlp_frame_cosine_mean']}, "
            + f"rms_corr={row['oracle_rms_corr_mean']}, "
            + f"vuv_accuracy={row['oracle_vuv_accuracy_mean']}"
        )
    lines.append("")
    lines.append("## Notes")
    for note in summary.get("notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
