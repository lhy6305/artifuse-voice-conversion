from __future__ import annotations

import argparse
from pathlib import Path

from v5vc.ablation_eval import evaluate_offline_mvp_ablations
from v5vc.anchor_route_analysis import analyze_offline_mvp_anchor_routes
from v5vc.anchor_route_selector import select_offline_mvp_anchor_route
from v5vc.anchor_selection_analysis import analyze_offline_mvp_anchor_selection
from v5vc.ai_work_session_registry import (
    VALID_SESSION_STATUSES,
    materialize_ai_work_session_index,
    register_ai_work_session,
)
from v5vc.b1_supervision_inventory import build_b1_supervision_inventory
from v5vc.c1_weak_event_hints import build_c1_weak_event_hints
from v5vc.checkpoint_anchor_materializer import materialize_offline_mvp_checkpoint_anchor
from v5vc.checkpoint_average import average_offline_mvp_checkpoints
from v5vc.checkpoint_gate_replay import analyze_offline_mvp_checkpoint_gates
from v5vc.checkpoint_selection_analysis import analyze_offline_mvp_checkpoint_selection
from v5vc.checkpoint_series_eval import evaluate_offline_mvp_checkpoint_series
from v5vc.data_scan import scan_project_data
from v5vc.eval_baseline import evaluate_round1_baseline
from v5vc.event_semantics import (
    build_paired_parallel_source_semantic_parity_sidecar,
    build_target_event_timing_semantic_sidecar,
    build_target_event_semantic_sidecar,
)
from v5vc.event_target_analysis import analyze_offline_mvp_event_targets
from v5vc.experiment import init_experiment_record
from v5vc.final_experiment_comparison import compare_offline_mvp_final_experiments
from v5vc.audio_audit_gui import launch_audio_audit_gui
from v5vc.handoff_document import materialize_offline_mvp_route_handoff_doc
from v5vc.handoff_summary import build_offline_mvp_route_handoff
from v5vc.horizon_policy_shadow import build_offline_mvp_matched_horizon_shadow
from v5vc.integrity_check import check_round1_data
from v5vc.manifest_builder import build_round1_manifests
from v5vc.nores_vocoder_checkpoint_review import review_offline_mvp_nores_vocoder_checkpoints
from v5vc.nores_vocoder_checkpoint_selection import select_offline_mvp_nores_vocoder_checkpoint
from v5vc.nores_vocoder_low_activity_sensitivity import analyze_offline_mvp_nores_vocoder_low_activity_sensitivity
from v5vc.nores_vocoder_audio_export import (
    DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
    export_offline_mvp_nores_vocoder_audio,
)
from v5vc.offline_teacher_downstream_contract import export_offline_mvp_teacher_downstream_contract
from v5vc.offline_teacher_runtime import run_offline_mvp_teacher_runtime
from v5vc.offline_teacher_vocoder_input_scaffold import build_offline_mvp_teacher_vocoder_input_scaffold
from v5vc.source_acoustic_state_audit import audit_source_acoustic_state_extraction
from v5vc.teacher_first_vc_demo import (
    analyze_teacher_first_vc_applicability,
    analyze_teacher_first_vc_decoder_behavior,
    build_teacher_first_vc_audible_compare_bundle,
    build_teacher_first_vc_audible_smoke_bundle,
    build_teacher_first_vc_review_bundle,
    DEFAULT_AUDIBLE_SMOKE_TARGET_REFERENCE_MAX_AUDIO_SEC,
    DEFAULT_CALIBRATION_ASSET_PATH,
    DEFAULT_SELF_CHECK_INPUT_AUDIO_PATH,
    DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
    DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
    run_teacher_first_vc_demo_self_check,
    run_offline_mvp_teacher_first_vc_demo,
)
from v5vc.offline_vocoder_scaffold import prepare_offline_mvp_nores_vocoder_scaffold
from v5vc.offline_vocoder_training import (
    DEFAULT_STAGE5_SPECTRAL_TARGET_MODE,
    DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
    DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
    build_offline_mvp_nores_vocoder_dataset_packages,
    build_offline_mvp_nores_vocoder_training_package,
    run_offline_mvp_nores_vocoder_dataset_training_loop,
    run_offline_mvp_nores_vocoder_training_loop,
    run_offline_mvp_nores_vocoder_training_step,
)
from v5vc.preprocess import run_preprocessing
from v5vc.proxy_audio_export import export_offline_mvp_proxy_audio
from v5vc.route_recap import recap_offline_mvp_route_context
from v5vc.split_analysis import analyze_round1_split_options
from v5vc.split_materialization import materialize_round1_split
from v5vc.special_eval import evaluate_offline_mvp_special_eval, evaluate_round1_special_eval
from v5vc.special_eval_series import evaluate_offline_mvp_special_eval_series
from v5vc.special_slice_alignment import analyze_offline_mvp_special_slice_alignment
from v5vc.stage5_low_activity_audit_result_report import materialize_stage5_low_activity_audit_result_report
from v5vc.stage5_low_activity_probe import (
    DEFAULT_CANDIDATE_ACTIVITY_THRESHOLD,
    DEFAULT_MAX_AUDIT_WINDOW_SEC,
    DEFAULT_MIN_LOW_ACTIVITY_FRAMES,
    DEFAULT_MIN_AUDIT_WINDOW_SEC,
    DEFAULT_TARGET_ACTIVITY_THRESHOLD,
    DEFAULT_WINDOW_PADDING_SEC,
    analyze_stage5_low_activity_fragments,
)
from v5vc.stage5_low_activity_governance_report import materialize_stage5_low_activity_governance_report
from v5vc.stage5_speech_emergence_probe import analyze_stage5_nores_speech_emergence
from v5vc.stage5_waveform_decoder_structure_probe import analyze_stage5_nores_waveform_decoder_structure
from v5vc.stage5_waveform_objective_collapse_probe import analyze_stage5_nores_waveform_objective_collapse
from v5vc.stage_report import materialize_offline_mvp_stage_report
from v5vc.streaming_student import (
    build_streaming_student_calibration_assets,
    export_streaming_student_downstream_control_packet,
    build_streaming_student_eval_bridge,
    build_streaming_student_teacher_labels,
    evaluate_streaming_student_checkpoint,
    estimate_streaming_student_calibration,
    export_streaming_student_proxy_audio,
    prepare_streaming_student_paired_training_data,
    prepare_streaming_student_stage,
    prepare_streaming_student_supervision,
    prepare_streaming_student_training_data,
    run_streaming_student_training_loop,
    run_streaming_student_training_step,
    select_streaming_student_best_checkpoint,
)
from v5vc.streaming_student.stage5_handoff import build_streaming_student_stage5_dataset_packages
from v5vc.target_special_supervision import analyze_round1_target_special_supervision
from v5vc.target_format_recovery import recover_round1_target_formats
from v5vc.train_entry import prepare_offline_mvp_training


STUDENT_ROUTE_CLI_GUARD_MESSAGE = (
    "Student-line command is blocked by default because native teacher decoded output is still not user-acceptable. "
    "Do not resume student distillation/eval/handoff until the teacher route has first cleared the buzz gate and user review. "
    "If you intentionally need this command anyway, re-run it with --allow-student-line-while-teacher-unsatisfied."
)


def add_student_route_guard_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--allow-student-line-while-teacher-unsatisfied",
        action="store_true",
        help=(
            "Explicitly acknowledge that native teacher quality is still not accepted, and still force this "
            "student-line command to run. Use only for exceptional diagnostics."
        ),
    )


def require_student_route_explicit_ack(command: str, allowed: bool) -> None:
    if bool(allowed):
        return
    raise RuntimeError(f"{command}: {STUDENT_ROUTE_CLI_GUARD_MESSAGE}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project management entrypoint for the V5.1 voice conversion workspace."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser(
        "scan-data",
        help="Scan current datasets and generate manifests plus summary reports.",
    )
    scan_parser.add_argument(
        "--firefly-dir",
        type=Path,
        default=Path("data_convert/dataset_firefly_raw"),
        help="Directory containing target-speaker wav/lab pairs.",
    )
    scan_parser.add_argument(
        "--source-audio",
        type=Path,
        default=Path("data_convert/dataset_ly65_raw.wav"),
        help="Source-speaker raw wav file.",
    )
    scan_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/data/initial_scan"),
        help="Directory for generated reports.",
    )
    scan_parser.add_argument(
        "--window-ms",
        type=int,
        default=100,
        help="Chunk size for source-audio loudness analysis.",
    )

    preprocess_parser = subparsers.add_parser(
        "preprocess-data",
        help="Run the confirmed first-round preprocessing pipeline.",
    )
    preprocess_parser.add_argument(
        "--firefly-dir",
        type=Path,
        default=Path("data_convert/dataset_firefly_raw"),
        help="Directory containing target-speaker wav/lab pairs.",
    )
    preprocess_parser.add_argument(
        "--source-audio",
        type=Path,
        default=Path("data_convert/dataset_ly65_raw.wav"),
        help="Source-speaker raw wav file.",
    )
    preprocess_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/preprocess_default.json"),
        help="JSON config for preprocessing decisions.",
    )
    preprocess_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1"),
        help="Directory for processed training inputs and clips.",
    )
    preprocess_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/preprocess_round1"),
        help="Directory for preprocessing reports.",
    )

    manifest_parser = subparsers.add_parser(
        "build-round1-manifests",
        help="Build standardized training manifests from round1 preprocessing outputs.",
    )
    manifest_parser.add_argument(
        "--round1-dir",
        type=Path,
        default=None,
        help="Directory containing round1 preprocessing outputs.",
    )
    manifest_parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Optional target directory override. Defaults to <round1-dir>/firefly_mainstream.",
    )
    manifest_parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Optional source directory override. Defaults to <round1-dir>/source_segments.",
    )
    manifest_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data_prep/round1/manifests"),
        help="Directory for standardized manifest outputs.",
    )
    manifest_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_manifests"),
        help="Directory for manifest summary reports.",
    )

    recovery_parser = subparsers.add_parser(
        "recover-round1-target-formats",
        help="Recover lexical target samples from the excluded round1 set by normalizing sample rate and channels.",
    )
    recovery_parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data_prep/round1/firefly_mainstream"),
        help="Directory containing round1 target manifests.",
    )
    recovery_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data_prep/round1_1/firefly_mainstream"),
        help="Directory for recovered round1.1 target outputs.",
    )
    recovery_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_1_target_recovery"),
        help="Directory for round1.1 target recovery reports.",
    )
    recovery_parser.add_argument(
        "--target-sample-rate",
        type=int,
        default=44100,
        help="Recovered target sample rate.",
    )
    recovery_parser.add_argument(
        "--target-channels",
        type=int,
        default=1,
        help="Recovered target channel count. Current implementation supports mono only.",
    )
    recovery_parser.add_argument(
        "--include-no-text-voice",
        action="store_true",
        help="Include no_text_voice exclusions in recovery instead of keeping them isolated.",
    )

    integrity_parser = subparsers.add_parser(
        "check-round1-data",
        help="Validate round1 preprocessing outputs and standardized manifests.",
    )
    integrity_parser.add_argument(
        "--round1-dir",
        type=Path,
        default=Path("data_prep/round1"),
        help="Directory containing round1 preprocessing outputs.",
    )
    integrity_parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=Path("data_prep/round1/manifests"),
        help="Directory containing standardized manifests.",
    )
    integrity_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_integrity"),
        help="Directory for integrity reports.",
    )

    experiment_parser = subparsers.add_parser(
        "init-experiment",
        help="Create a new experiment record and metrics skeleton from the standard template.",
    )
    experiment_parser.add_argument(
        "--slug",
        required=True,
        help="Short experiment slug, for example offline-mvp-baseline.",
    )
    experiment_parser.add_argument(
        "--owner",
        default="codex",
        help="Owner name to place in the experiment record.",
    )
    experiment_parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("configs/eval_baseline_template.json"),
        help="Config path to reference in the experiment record.",
    )
    experiment_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/experiments"),
        help="Directory for experiment records.",
    )
    experiment_parser.add_argument(
        "--template-path",
        type=Path,
        default=Path("reports/templates/experiment_record_template.md"),
        help="Markdown template path for the experiment record.",
    )
    experiment_parser.add_argument(
        "--route-selection",
        type=Path,
        default=None,
        help="Optional anchor-route selection json used to prefill route fields in the experiment record.",
    )

    eval_parser = subparsers.add_parser(
        "evaluate-round1-baseline",
        help="Run the round1 offline-MVP baseline evaluation scaffold.",
    )
    eval_parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=Path("data_prep/round1/manifests"),
        help="Directory containing standardized round1 manifests.",
    )
    eval_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/round1_baseline"),
        help="Directory for baseline evaluation outputs.",
    )
    eval_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional metrics json file to update with baseline scaffold results.",
    )
    eval_parser.add_argument(
        "--r-res-enabled",
        action="store_true",
        help="Whether residual branch is enabled. Offline MVP baseline expects this to remain disabled.",
    )

    train_parser = subparsers.add_parser(
        "train-offline-mvp",
        help="Prepare the offline MVP training run configuration and dry-run plan.",
    )
    train_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    train_parser.add_argument(
        "--experiment-id",
        required=True,
        help="Experiment id to attach the training plan to.",
    )
    train_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/training/offline_mvp"),
        help="Directory for training dry-run outputs.",
    )
    train_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate config and data inputs, then write a training plan.",
    )

    streaming_student_parser = subparsers.add_parser(
        "prepare-streaming-student-stage",
        help="Prepare the Stage3 streaming frontend/student scaffold plan and contract summary.",
    )
    streaming_student_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/plans/streaming_student_stage"),
        help="Directory for Stage3 scaffold plan outputs.",
    )
    streaming_student_parser.add_argument(
        "--experiment-id",
        default="streaming_student_stage_scaffold",
        help="Experiment id used for plan artifact names and optional metrics updates.",
    )
    add_student_route_guard_argument(streaming_student_parser)

    streaming_student_calibration_parser = subparsers.add_parser(
        "build-streaming-student-calibration-assets",
        help="Build Stage3 calibration record selection and placeholder conditioning asset templates.",
    )
    streaming_student_calibration_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_calibration_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_calibration_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration"),
        help="Directory for machine-readable calibration asset scaffolds.",
    )
    streaming_student_calibration_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/streaming_student_calibration"),
        help="Directory for calibration planning summaries.",
    )
    streaming_student_calibration_parser.add_argument(
        "--target-duration-sec",
        type=float,
        default=120.0,
        help="Soft duration budget for the target-side calibration subset.",
    )
    streaming_student_calibration_parser.add_argument(
        "--max-records",
        type=int,
        default=12,
        help="Maximum number of target records to keep in the calibration subset.",
    )
    add_student_route_guard_argument(streaming_student_calibration_parser)

    streaming_student_bridge_parser = subparsers.add_parser(
        "build-streaming-student-eval-bridge",
        help="Summarize Stage3 scaffold outputs into offline_mvp-style control summaries.",
    )
    streaming_student_bridge_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_bridge_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_bridge_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Estimated conditioning asset path. Falls back to placeholder behavior if the file does not exist.",
    )
    streaming_student_bridge_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/streaming_student_eval_bridge"),
        help="Directory for Stage3 eval bridge summaries.",
    )
    streaming_student_bridge_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size used for Stage3 target-slice summarization.",
    )
    streaming_student_bridge_parser.add_argument(
        "--max-records-per-slice",
        type=int,
        default=None,
        help="Optional cap on target_validation and target_special_eval records for quick bridge checks.",
    )
    add_student_route_guard_argument(streaming_student_bridge_parser)

    streaming_student_estimate_parser = subparsers.add_parser(
        "estimate-streaming-student-calibration",
        help="Estimate non-placeholder Stage3 calibration assets from the selected calibration subset.",
    )
    streaming_student_estimate_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_estimate_parser.add_argument(
        "--calibration-records",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/target_calibration_records.jsonl"),
        help="Calibration record subset selected for Stage3 asset estimation.",
    )
    streaming_student_estimate_parser.add_argument(
        "--calibration-template",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_template.json"),
        help="Placeholder calibration asset template to upgrade with estimated values.",
    )
    streaming_student_estimate_parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Output path for the estimated Stage3 calibration asset.",
    )
    streaming_student_estimate_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/streaming_student_calibration_estimate"),
        help="Directory for calibration estimation summaries.",
    )
    add_student_route_guard_argument(streaming_student_estimate_parser)

    streaming_student_teacher_parser = subparsers.add_parser(
        "build-streaming-student-teacher-labels",
        help="Export offline_mvp teacher pseudo labels as Stage3 streaming_student training assets.",
    )
    streaming_student_teacher_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels"),
        help="Directory for machine-readable teacher-label assets.",
    )
    streaming_student_teacher_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/streaming_student_teacher_labels"),
        help="Directory for teacher-label export summaries.",
    )
    streaming_student_teacher_parser.add_argument(
        "--route-handoff",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"),
        help="Route handoff json used to resolve the formal offline_mvp teacher anchor.",
    )
    streaming_student_teacher_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional experiment metrics path override. Falls back to the route handoff anchor when omitted.",
    )
    streaming_student_teacher_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint override. Falls back to experiment metrics or route handoff anchor when omitted.",
    )
    streaming_student_teacher_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Falls back to experiment metrics when omitted.",
    )
    streaming_student_teacher_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size used for offline_mvp teacher pseudo-label export.",
    )
    streaming_student_teacher_parser.add_argument(
        "--max-records-per-slice",
        type=int,
        default=None,
        help="Optional cap on target_train/validation/special_eval record counts for quick checks.",
    )
    streaming_student_teacher_parser.add_argument(
        "--teacher-eevt-bridge-mode",
        type=str,
        default="legacy_event_probs_v1",
        help=(
            "Generation-side bridge mode for the first 5 bootstrap teacher e_evt acoustic dims. "
            "Examples: legacy_event_probs_v1, acoustic_guided_event_bridge_v1."
        ),
    )
    streaming_student_teacher_parser.add_argument(
        "--teacher-eevt-target-shaping-mode",
        type=str,
        default="hard_box_v1",
        help=(
            "Generation-side shaping mode for bootstrap teacher_e_evt labels. "
            "Examples: hard_box_v1, center_weighted_boundary_progressive_final_clause_v1."
        ),
    )
    add_student_route_guard_argument(streaming_student_teacher_parser)

    streaming_student_training_data_parser = subparsers.add_parser(
        "prepare-streaming-student-training-data",
        help="Build the Stage3 teacher-label plus conditioning data contract and dry-run batch summary.",
    )
    streaming_student_training_data_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_training_data_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_training_data_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_training_data_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_training_data_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/plans/streaming_student_training_data"),
        help="Directory for Stage3 training-data dry-run summaries.",
    )
    streaming_student_training_data_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Dry-run batch size used per target slice.",
    )
    add_student_route_guard_argument(streaming_student_training_data_parser)

    streaming_student_paired_training_data_parser = subparsers.add_parser(
        "prepare-streaming-student-paired-training-data",
        help="Build the paired Stage3 source-input plus target-teacher contract and quantify frame mismatch.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--train-pair-spec",
        type=Path,
        default=Path("data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl"),
        help="Paired source-to-target jsonl used for the train dry-run slice.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--validation-pair-spec",
        type=Path,
        default=Path("data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl"),
        help="Optional paired source-to-target jsonl used for the validation dry-run slice.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/plans/streaming_student_paired_training_data"),
        help="Directory for paired Stage3 training-data dry-run summaries.",
    )
    streaming_student_paired_training_data_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Dry-run batch size used per paired slice.",
    )
    add_student_route_guard_argument(streaming_student_paired_training_data_parser)

    streaming_student_supervision_parser = subparsers.add_parser(
        "prepare-streaming-student-supervision",
        help="Build the minimal Stage3 teacher-supervised loss dry-run summary.",
    )
    streaming_student_supervision_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_supervision_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_supervision_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_supervision_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_supervision_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/plans/streaming_student_supervision"),
        help="Directory for Stage3 supervision dry-run summaries.",
    )
    streaming_student_supervision_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Dry-run batch size used per target slice.",
    )
    add_student_route_guard_argument(streaming_student_supervision_parser)
    streaming_student_supervision_parser.add_argument(
        "--disable-teacher-confidence",
        action="store_true",
        help="Disable teacher_frame_confidence weighting and use only the frame mask.",
    )
    streaming_student_supervision_parser.add_argument(
        "--loss-weight-overrides",
        type=Path,
        default=None,
        help="Optional JSON file that overrides part of the default Stage3 loss weight table.",
    )

    streaming_student_train_step_parser = subparsers.add_parser(
        "run-streaming-student-training-step",
        help="Run a one-step Stage3 training scaffold on top of the new teacher-supervised contract.",
    )
    streaming_student_train_step_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_train_step_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_train_step_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_train_step_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_train_step_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/training/streaming_student"),
        help="Directory for one-step Stage3 training scaffold artifacts.",
    )
    streaming_student_train_step_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size used for the one-step training scaffold.",
    )
    streaming_student_train_step_parser.add_argument(
        "--learning-rate",
        type=float,
        default=1.0e-3,
        help="Learning rate used for the one-step training scaffold.",
    )
    streaming_student_train_step_parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=1.0,
        help="Gradient clipping threshold used for the one-step training scaffold.",
    )
    streaming_student_train_step_parser.add_argument(
        "--experiment-id",
        default="streaming_student_stage_step_scaffold",
        help="Artifact prefix for the one-step training scaffold.",
    )
    streaming_student_train_step_parser.add_argument(
        "--disable-teacher-confidence",
        action="store_true",
        help="Disable teacher_frame_confidence weighting and use only the frame mask.",
    )
    streaming_student_train_step_parser.add_argument(
        "--loss-weight-overrides",
        type=Path,
        default=None,
        help="Optional JSON file that overrides part of the default Stage3 loss weight table.",
    )
    add_student_route_guard_argument(streaming_student_train_step_parser)

    streaming_student_train_loop_parser = subparsers.add_parser(
        "run-streaming-student-training-loop",
        help="Run a minimal multi-step Stage3 training loop with periodic validation and checkpoints.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/streaming_student_stage_template.json"),
        help="Stage3 scaffold config template path.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/training/streaming_student_loop"),
        help="Directory for minimal multi-step Stage3 training loop artifacts.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size used for the multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--validation-batch-size",
        type=int,
        default=4,
        help="Validation batch size used for the multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--num-steps",
        type=int,
        default=4,
        help="Number of training steps for the minimal multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--validation-interval",
        type=int,
        default=2,
        help="Run validation every N steps.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=2,
        help="Write a checkpoint every N steps.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--validation-batches",
        type=int,
        default=2,
        help="Number of sampled validation batches to average per validation pass when --validation-mode=sampled.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--validation-mode",
        choices=("sampled", "full"),
        default="sampled",
        help="Validation mode used inside the Stage3 training loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--learning-rate",
        type=float,
        default=1.0e-3,
        help="Learning rate used for the minimal multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=1.0,
        help="Gradient clipping threshold used for the minimal multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--experiment-id",
        default="streaming_student_stage_loop_scaffold",
        help="Artifact prefix for the minimal multi-step Stage3 loop.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--disable-teacher-confidence",
        action="store_true",
        help="Disable teacher_frame_confidence weighting and use only the frame mask.",
    )
    streaming_student_train_loop_parser.add_argument(
        "--loss-weight-overrides",
        type=Path,
        default=None,
        help="Optional JSON file that overrides part of the default Stage3 loss weight table.",
    )
    add_student_route_guard_argument(streaming_student_train_loop_parser)

    streaming_student_checkpoint_eval_parser = subparsers.add_parser(
        "evaluate-streaming-student-checkpoint",
        help="Evaluate a Stage3 checkpoint on full validation and optional special_eval slices.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Checkpoint path produced by the Stage3 training step or loop scaffold.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/streaming_student_checkpoint_eval"),
        help="Directory for Stage3 checkpoint evaluation summaries.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--batch-size",
        type=int,
        default=6,
        help="Batch size used for checkpoint evaluation.",
    )
    streaming_student_checkpoint_eval_parser.add_argument(
        "--skip-special-eval",
        action="store_true",
        help="Evaluate target_validation only.",
    )
    add_student_route_guard_argument(streaming_student_checkpoint_eval_parser)

    streaming_student_checkpoint_select_parser = subparsers.add_parser(
        "select-streaming-student-best-checkpoint",
        help="Rank multiple Stage3 checkpoints using fuller checkpoint evaluation.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--checkpoints",
        type=Path,
        nargs="+",
        required=True,
        help="One or more Stage3 checkpoint paths to compare.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/streaming_student_checkpoint_selection"),
        help="Directory for Stage3 checkpoint selection summaries.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--batch-size",
        type=int,
        default=6,
        help="Batch size used for fuller checkpoint comparison.",
    )
    add_student_route_guard_argument(streaming_student_checkpoint_select_parser)
    streaming_student_proxy_audio_parser = subparsers.add_parser(
        "export-streaming-student-proxy-audio",
        help="Export Stage3 input, teacher proxy, and student proxy audio for structural listening audits.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Checkpoint path produced by the Stage3 training loop scaffold.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from checkpoint config.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--split-name",
        default="target_validation",
        choices=["target_train", "target_validation", "target_special_eval"],
        help="Target split to sample for proxy audio export.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/audio/streaming_student_proxy_audio"),
        help="Directory for exported Stage3 proxy audio and metadata.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="Number of evenly spaced records to export when target_record_ids are omitted.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--target-record-ids",
        nargs="+",
        default=None,
        help="Optional explicit target record_ids to export instead of evenly spaced sampling.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--branch-label",
        default=None,
        help="Optional label prefix for exported wav filenames. Defaults to checkpoint experiment_id.",
    )
    streaming_student_proxy_audio_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration for each exported audio item.",
    )
    add_student_route_guard_argument(streaming_student_proxy_audio_parser)
    streaming_student_downstream_control_parser = subparsers.add_parser(
        "export-streaming-student-downstream-control-packet",
        help="Export Stage3 named-control packet candidates for downstream handoff screening.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
        help="Checkpoint path produced by the Stage3 training loop scaffold.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--teacher-label-index",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl"),
        help="Teacher-label index jsonl exported for Stage3.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset consumed as global conditioning for Stage3 batches.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from checkpoint config.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--split-name",
        default="target_validation",
        choices=["target_train", "target_validation", "target_special_eval"],
        help="Target split to sample for downstream packet export.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/streaming_student_downstream_control_packet"),
        help="Directory for exported Stage3 downstream packet records and metadata.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="Number of evenly spaced records to export when target_record_ids are omitted.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--target-record-ids",
        nargs="+",
        default=None,
        help="Optional explicit target record_ids to export instead of evenly spaced sampling.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--branch-label",
        default=None,
        help="Optional label prefix for exported packet metadata. Defaults to checkpoint experiment_id.",
    )
    streaming_student_downstream_control_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration for each exported audio item.",
    )
    add_student_route_guard_argument(streaming_student_downstream_control_parser)
    audio_audit_gui_parser = subparsers.add_parser(
        "launch-audio-audit-gui",
        help="Launch the proxy-audio audit GUI for manual listening review.",
    )
    audio_audit_gui_parser.add_argument(
        "--bundle",
        type=Path,
        nargs="*",
        default=[],
        help="Bundle directories or proxy_audio_export.json files to load on startup.",
    )
    audio_audit_gui_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/audio/audio_audit_gui_exports"),
        help="Directory for GUI progress and exported review files.",
    )
    audio_audit_gui_parser.add_argument(
        "--auto-close-ms",
        type=int,
        default=None,
        help="Optional smoke-test mode: auto-close the GUI after the given number of milliseconds.",
    )
    stage5_low_activity_probe_parser = subparsers.add_parser(
        "analyze-stage5-low-activity-fragments",
        help="Compare Stage5 bundles on target low-activity segments and export fragmentation diagnostics.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--bundle",
        type=Path,
        nargs="+",
        required=True,
        help="Stage5 bundle directories or bundle manifest files to compare.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/audio/stage5_low_activity_fragmentation_probe"),
        help="Directory for low-activity probe summaries and exported segment clips.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--analysis-audio-sources",
        nargs="+",
        default=["decoded_pitch_matched"],
        choices=["listening", "decoded", "decoded_pitch_matched", "audit_proxy"],
        help="One or more Stage5 bundle audio sources to analyze.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--target-activity-threshold",
        type=float,
        default=DEFAULT_TARGET_ACTIVITY_THRESHOLD,
        help="Threshold used to identify low-activity windows on aligned_target.wav.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--candidate-activity-threshold",
        type=float,
        default=DEFAULT_CANDIDATE_ACTIVITY_THRESHOLD,
        help="Threshold used to count candidate bursts inside target low-activity windows.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--min-low-activity-frames",
        type=int,
        default=DEFAULT_MIN_LOW_ACTIVITY_FRAMES,
        help="Minimum number of consecutive low-activity frames required to keep a segment.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--top-k-windows",
        type=int,
        default=12,
        help="Maximum suspicious windows to keep per audio source in the summary output.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--window-padding-sec",
        type=float,
        default=DEFAULT_WINDOW_PADDING_SEC,
        help="Minimum context padding applied on both sides when exporting suspicious segment clips.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--min-audit-window-sec",
        type=float,
        default=DEFAULT_MIN_AUDIT_WINDOW_SEC,
        help="Minimum exported listening window length for each suspicious segment.",
    )
    stage5_low_activity_probe_parser.add_argument(
        "--max-audit-window-sec",
        type=float,
        default=DEFAULT_MAX_AUDIT_WINDOW_SEC,
        help="Soft cap for exported listening window length when the suspicious core fits inside it.",
    )
    streaming_student_checkpoint_select_parser.add_argument(
        "--skip-special-eval",
        action="store_true",
        help="Rank checkpoints using target_validation only.",
    )

    checkpoint_average_parser = subparsers.add_parser(
        "average-offline-mvp-checkpoints",
        help="Average multiple offline MVP checkpoints into a single checkpoint payload.",
    )
    checkpoint_average_parser.add_argument(
        "--checkpoints",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more checkpoint paths to average.",
    )
    checkpoint_average_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_checkpoint_average"),
        help="Directory for the averaged checkpoint and summary files.",
    )
    checkpoint_average_parser.add_argument(
        "--output-name",
        default="averaged_checkpoint",
        help="Basename for the averaged checkpoint and summary files.",
    )

    split_parser = subparsers.add_parser(
        "analyze-round1-splits",
        help="Analyze round1 train/validation split candidates without modifying manifests.",
    )
    split_parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=Path("data_prep/round1/manifests"),
        help="Directory containing standardized round1 manifests.",
    )
    split_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/data/round1_split_analysis"),
        help="Directory for split analysis reports and candidate option files.",
    )

    materialize_split_parser = subparsers.add_parser(
        "materialize-round1-split",
        help="Materialize a confirmed round1 split option into dedicated split manifests.",
    )
    materialize_split_parser.add_argument(
        "--manifest-dir",
        type=Path,
        default=Path("data_prep/round1/manifests"),
        help="Directory containing standardized round1 manifests.",
    )
    materialize_split_parser.add_argument(
        "--option-path",
        type=Path,
        default=Path("reports/data/round1_split_analysis/options/hybrid_stratified_blocked.json"),
        help="Confirmed split option json file.",
    )
    materialize_split_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data_prep/round1/splits/hybrid_stratified_blocked"),
        help="Directory for materialized split manifests.",
    )

    special_eval_parser = subparsers.add_parser(
        "evaluate-round1-special-eval",
        help="Evaluate the target special_eval slice from a confirmed round1 split.",
    )
    special_eval_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1/splits/hybrid_stratified_blocked"),
        help="Directory containing materialized split manifests.",
    )
    special_eval_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/round1_special_eval"),
        help="Directory for special eval reports.",
    )
    special_eval_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional metrics json file to update with special eval results.",
    )

    special_eval_model_parser = subparsers.add_parser(
        "evaluate-offline-mvp-special-eval",
        help="Run model-level evaluation on target_special_eval and compare it with regular validation.",
    )
    special_eval_model_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    special_eval_model_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    special_eval_model_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_special_eval"),
        help="Directory for model-level special eval outputs.",
    )
    special_eval_model_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint path override.",
    )
    special_eval_model_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional experiment metrics json used for checkpoint resolution and metric updates.",
    )

    ablation_parser = subparsers.add_parser(
        "evaluate-offline-mvp-ablations",
        help="Run offline MVP z_art / e_evt ablation evaluation on the formal validation split.",
    )
    ablation_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    ablation_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    ablation_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_ablations"),
        help="Directory for ablation evaluation outputs.",
    )
    ablation_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint path override.",
    )
    ablation_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional experiment metrics json used for checkpoint resolution and metric updates.",
    )

    checkpoint_series_parser = subparsers.add_parser(
        "evaluate-offline-mvp-checkpoint-series",
        help="Run ablation summaries across all checkpoints recorded for an experiment.",
    )
    checkpoint_series_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    checkpoint_series_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        required=True,
        help="Experiment metrics json containing checkpoint_paths.",
    )
    checkpoint_series_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_checkpoint_series"),
        help="Directory for checkpoint-series evaluation outputs.",
    )
    checkpoint_series_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )

    special_eval_series_parser = subparsers.add_parser(
        "evaluate-offline-mvp-special-eval-series",
        help="Run model-level target_special_eval comparisons across selected checkpoints for an experiment.",
    )
    special_eval_series_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    special_eval_series_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        required=True,
        help="Experiment metrics json containing checkpoint_paths.",
    )
    special_eval_series_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_special_eval_series"),
        help="Directory for checkpoint-series special eval outputs.",
    )
    special_eval_series_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    special_eval_series_parser.add_argument(
        "--steps",
        type=int,
        nargs="*",
        default=None,
        help="Optional selected checkpoint steps, for example --steps 25 100 250 500.",
    )

    proxy_audio_parser = subparsers.add_parser(
        "export-offline-mvp-proxy-audio",
        help="Export proxy audio reconstructed from predicted acoustic features for human audit.",
    )
    proxy_audio_parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/offline_mvp_train_template.json"),
        help="Training config template path.",
    )
    proxy_audio_parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="Optional split directory override. Defaults to data.split_dir from config.",
    )
    proxy_audio_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/audio/offline_mvp_proxy_audio"),
        help="Directory for exported proxy audio and metadata.",
    )
    proxy_audio_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint path override.",
    )
    proxy_audio_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        default=None,
        help="Optional experiment metrics json used for checkpoint resolution.",
    )
    proxy_audio_parser.add_argument(
        "--source-manifest",
        type=Path,
        default=None,
        help="Optional source manifest override. Defaults to source_validation.jsonl in split_dir.",
    )
    proxy_audio_parser.add_argument(
        "--source-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit source record ids to export.",
    )
    proxy_audio_parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="Number of source records to export when source_record_ids is not provided.",
    )
    proxy_audio_parser.add_argument(
        "--branch-label",
        default=None,
        help="Optional label used in output filenames and metadata.",
    )
    proxy_audio_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max audio duration override for exported samples.",
    )

    teacher_runtime_parser = subparsers.add_parser(
        "run-offline-mvp-teacher-runtime",
        help="Run the formal offline teacher through a chunked runtime wrapper and export control outputs.",
    )
    teacher_runtime_parser.add_argument(
        "--input-audio",
        type=Path,
        required=True,
        help="Input wav path to process with the teacher runtime wrapper.",
    )
    teacher_runtime_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_runtime"),
        help="Directory for runtime output tensors and summary files.",
    )
    teacher_runtime_parser.add_argument(
        "--route-handoff",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"),
        help="Route handoff used to resolve the formal teacher checkpoint when --checkpoint is omitted.",
    )
    teacher_runtime_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit teacher checkpoint override.",
    )
    teacher_runtime_parser.add_argument(
        "--chunk-samples",
        type=int,
        default=None,
        help="Optional runtime chunk size in samples. Mutually exclusive with --chunk-ms.",
    )
    teacher_runtime_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=None,
        help="Optional runtime chunk size in milliseconds when --chunk-samples is omitted.",
    )
    teacher_runtime_parser.add_argument(
        "--device",
        default="auto",
        help="Runtime device. Use auto, cpu, cuda, or cuda:0.",
    )
    teacher_runtime_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from the input wav.",
    )
    teacher_runtime_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the full-utterance verification pass and export only chunked runtime outputs.",
    )

    teacher_contract_parser = subparsers.add_parser(
        "export-offline-mvp-teacher-downstream-contract",
        help="Export a teacher-first downstream control contract for the next integration stage.",
    )
    teacher_contract_parser.add_argument(
        "--input-audio",
        type=Path,
        required=True,
        help="Input wav path to process with the teacher runtime wrapper.",
    )
    teacher_contract_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_downstream_contract"),
        help="Directory for downstream control contract outputs.",
    )
    teacher_contract_parser.add_argument(
        "--route-handoff",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"),
        help="Route handoff used to resolve the formal teacher checkpoint when --checkpoint is omitted.",
    )
    teacher_contract_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit teacher checkpoint override.",
    )
    teacher_contract_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset providing s_spk_target, s_geom_target, and alpha.",
    )
    teacher_contract_parser.add_argument(
        "--chunk-samples",
        type=int,
        default=None,
        help="Optional runtime chunk size in samples. Mutually exclusive with --chunk-ms.",
    )
    teacher_contract_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=None,
        help="Optional runtime chunk size in milliseconds when --chunk-samples is omitted.",
    )
    teacher_contract_parser.add_argument(
        "--device",
        default="auto",
        help="Runtime device. Use auto, cpu, cuda, or cuda:0.",
    )
    teacher_contract_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from the input wav.",
    )
    teacher_contract_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the full-utterance verification pass and export only chunked control outputs.",
    )
    teacher_contract_parser.add_argument(
        "--teacher-eevt-bridge-mode",
        type=str,
        default="legacy_event_probs_v1",
        help=(
            "Generation-side bridge mode used when explicit teacher e_evt is rasterized into the downstream contract. "
            "Examples: legacy_event_probs_v1, acoustic_guided_event_bridge_v1."
        ),
    )
    teacher_contract_parser.add_argument(
        "--teacher-eevt-target-shaping-mode",
        type=str,
        default="hard_box_v1",
        help=(
            "Generation-side shaping mode used when explicit teacher e_evt is rasterized into the downstream contract. "
            "Examples: hard_box_v1, center_weighted_boundary_progressive_final_clause_v1."
        ),
    )

    teacher_vocoder_scaffold_parser = subparsers.add_parser(
        "build-offline-mvp-teacher-vocoder-input-scaffold",
        help="Build a minimal consumer-side scaffold from the teacher downstream contract.",
    )
    teacher_vocoder_scaffold_parser.add_argument(
        "--contract",
        type=Path,
        required=True,
        help="teacher_downstream_control_contract.pt path produced by the teacher-first contract exporter.",
    )
    teacher_vocoder_scaffold_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_vocoder_input_scaffold"),
        help="Directory for consumer-side scaffold outputs.",
    )
    source_acoustic_state_audit_parser = subparsers.add_parser(
        "audit-source-acoustic-state",
        help="Audit the v2-core source acoustic state extraction chain on real short-form inputs.",
    )
    source_acoustic_state_audit_parser.add_argument(
        "--input-audio",
        type=Path,
        nargs="*",
        default=[],
        help="Optional wav paths to audit. Defaults to the fixed short smoke triplet when omitted.",
    )
    source_acoustic_state_audit_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/source_acoustic_state_audit"),
        help="Directory for audit summaries and per-case outputs.",
    )
    source_acoustic_state_audit_parser.add_argument(
        "--route-handoff",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"),
        help="Route handoff used to resolve the formal teacher checkpoint when --checkpoint is omitted.",
    )
    source_acoustic_state_audit_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit teacher checkpoint override.",
    )
    source_acoustic_state_audit_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from each input wav.",
    )
    teacher_first_vc_demo_parser = subparsers.add_parser(
        "run-offline-mvp-teacher-first-vc-demo",
        help="Run the teacher-first single-target source-to-target demo path and export decoded audio.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--input-audio",
        type=Path,
        required=True,
        help="Source wav path used as the terminal-user input.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_first_vc_demo"),
        help="Directory for the decoded wav, summary, and optional intermediates.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--teacher-route-handoff",
        type=Path,
        default=DEFAULT_TEACHER_ROUTE_HANDOFF_PATH,
        help="Route handoff used to resolve the formal teacher checkpoint when --teacher-checkpoint is omitted.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--teacher-checkpoint",
        type=Path,
        default=None,
        help="Optional explicit teacher checkpoint override.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=DEFAULT_CALIBRATION_ASSET_PATH,
        help="Calibration asset providing the fixed single-target conditioning preset.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--vocoder-checkpoint",
        type=Path,
        default=None,
        help="Optional explicit Stage5 no-res vocoder checkpoint override.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--vocoder-checkpoint-selection",
        type=Path,
        default=DEFAULT_VOCODER_CHECKPOINT_SELECTION_PATH,
        help="Checkpoint-selection json used when --vocoder-checkpoint is omitted.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--selection-target",
        default="best_validation",
        help="Checkpoint role to use when resolving --vocoder-checkpoint-selection: best_validation, stable_late_stop, or best_rms.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--chunk-samples",
        type=int,
        default=None,
        help="Optional runtime chunk size in samples. Mutually exclusive with --chunk-ms.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=None,
        help="Optional runtime chunk size in milliseconds when --chunk-samples is omitted.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--device",
        default="auto",
        help="Runtime device. Use auto, cpu, cuda, or cuda:0.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from the input wav.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the full-utterance verification pass during teacher contract export.",
    )
    teacher_first_vc_demo_parser.set_defaults(
        save_intermediates=True,
        use_predicted_activity_gate=True,
    )
    teacher_first_vc_demo_parser.add_argument(
        "--save-intermediates",
        dest="save_intermediates",
        action="store_true",
        help="Keep teacher contract and vocoder scaffold intermediates under the output directory.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--no-save-intermediates",
        dest="save_intermediates",
        action="store_false",
        help="Remove intermediate contract/scaffold assets after decoded.wav is exported.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply predicted frame activity during waveform reconstruction.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--no-use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Disable predicted frame activity during waveform reconstruction.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--predicted-activity-gate-floor",
        type=float,
        default=0.0,
        help="Optional minimum frame gain applied after predicted activity gating.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--predicted-activity-gate-smoothing-frames",
        type=int,
        default=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        help=(
            "Moving-average radius for export-side predicted activity gate smoothing across neighboring frames. "
            "Defaults to the current promoted Stage5 decode setting."
        ),
    )
    teacher_first_vc_demo_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help=(
            "How predicted activity gains are applied during waveform reconstruction: "
            "pre_overlap_add or post_ola_envelope."
        ),
    )
    teacher_first_vc_demo_parser.add_argument(
        "--reference-package",
        dest="reference_package_list",
        action="append",
        type=Path,
        default=[],
        help="Optional Stage5 training-package path used for inference-only normalization. Can be passed multiple times.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--reference-package-limit",
        type=int,
        default=32,
        help="When inference-only normalization is enabled without explicit reference packages, use up to this many default Stage5 train packages.",
    )
    teacher_first_vc_demo_parser.add_argument(
        "--normalization-strategy",
        default="none",
        help=(
            "Optional inference-only scaffold normalization strategy: none, conditioning_reference_mean, "
            "reference_q01_q99_clip, reference_affine_match, or "
            "conditioning_reference_mean_plus_reference_q01_q99_clip."
        ),
    )
    teacher_first_vc_demo_parser.add_argument(
        "--control-family-override",
        dest="control_family_overrides",
        action="append",
        default=[],
        help=(
            "Optional inference-only family-level override. "
            "Format: family=mode, for example event_probs=reference_mean. "
            "Can be passed multiple times."
        ),
    )
    teacher_first_vc_demo_self_check_parser = subparsers.add_parser(
        "self-check-offline-mvp-teacher-first-vc-demo",
        help="Run a short success/failure regression bundle for the teacher-first single-target demo path.",
    )
    teacher_first_vc_demo_self_check_parser.add_argument(
        "--input-audio",
        type=Path,
        default=DEFAULT_SELF_CHECK_INPUT_AUDIO_PATH,
        help="Short source wav used for the self-check bundle.",
    )
    teacher_first_vc_demo_self_check_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/teacher_first_vc_demo_self_check"),
        help="Directory for case outputs and the aggregate self-check summary.",
    )
    teacher_first_vc_demo_self_check_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the self-check bundle. Defaults to cpu for reproducibility.",
    )
    teacher_first_vc_demo_self_check_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=0.1,
        help="Optional max duration to read from the input wav for each self-check case.",
    )
    teacher_first_vc_review_bundle_parser = subparsers.add_parser(
        "build-offline-mvp-teacher-first-vc-review-bundle",
        help="Export a multi-case terminal-user listening bundle on top of the teacher-first single-target runtime.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--input-audio",
        dest="input_audio_list",
        action="append",
        type=Path,
        default=[],
        help="Input wav path to include in the review bundle. Can be passed multiple times.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--input-spec-jsonl",
        type=Path,
        default=None,
        help="Optional jsonl spec with case_id, input_audio_path, max_audio_sec, and notes fields.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_first_vc_demo_review_bundle"),
        help="Directory for bundle summaries, per-case runs, and flattened listening wav files.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the review bundle. Defaults to cpu for reproducibility.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--max-audio-sec-default",
        type=float,
        default=None,
        help="Fallback max duration when --input-audio is used directly without per-case max_audio_sec.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=33.333333,
        help="Teacher runtime chunk window in milliseconds for each bundle case.",
    )
    teacher_first_vc_review_bundle_parser.set_defaults(
        save_intermediates=False,
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--save-intermediates",
        dest="save_intermediates",
        action="store_true",
        help="Keep per-case teacher contract and vocoder scaffold intermediates.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--no-save-intermediates",
        dest="save_intermediates",
        action="store_false",
        help="Remove per-case intermediates after decoded wav export.",
    )
    teacher_first_vc_review_bundle_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the teacher full-pass verification stage for each bundle case.",
    )
    teacher_first_vc_audible_smoke_parser = subparsers.add_parser(
        "build-offline-mvp-teacher-first-vc-audible-smoke-bundle",
        help="Export a teacher-first audible smoke bundle with positive-control listening assets plus the current experimental decoded wav.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--input-audio",
        dest="input_audio_list",
        action="append",
        type=Path,
        default=[],
        help="Input wav path to include in the audible smoke bundle. Can be passed multiple times.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--input-spec-jsonl",
        type=Path,
        default=None,
        help="Optional jsonl spec with case_id, input_audio_path, max_audio_sec, and notes fields.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle"),
        help="Directory for per-case runs, positive-control audio, and the aggregate audible smoke summary.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the audible smoke bundle. Defaults to cpu for reproducibility.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--max-audio-sec-default",
        type=float,
        default=None,
        help="Fallback max duration when --input-audio is used directly without per-case max_audio_sec.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=33.333333,
        help="Teacher runtime chunk window in milliseconds for each audible smoke case.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=DEFAULT_CALIBRATION_ASSET_PATH,
        help="Calibration asset used both for demo conditioning and default target-reference resolution.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--target-reference-audio",
        type=Path,
        default=None,
        help="Optional explicit target-reference wav. Defaults to the first selected record from the calibration asset.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--target-reference-max-audio-sec",
        type=float,
        default=DEFAULT_AUDIBLE_SMOKE_TARGET_REFERENCE_MAX_AUDIO_SEC,
        help="Optional max duration for the shared target-reference listening asset.",
    )
    teacher_first_vc_audible_smoke_parser.set_defaults(
        save_intermediates=False,
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--save-intermediates",
        dest="save_intermediates",
        action="store_true",
        help="Keep per-case teacher contract and vocoder scaffold intermediates.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--no-save-intermediates",
        dest="save_intermediates",
        action="store_false",
        help="Remove per-case intermediates after decoded wav export.",
    )
    teacher_first_vc_audible_smoke_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the teacher full-pass verification stage for each audible smoke case.",
    )
    teacher_first_vc_audible_compare_parser = subparsers.add_parser(
        "build-offline-mvp-teacher-first-vc-audible-compare-bundle",
        help="Export a teacher-first audible compare bundle with shared positive controls plus one decoded_<variant>.wav per configured checkpoint.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--input-audio",
        dest="input_audio_list",
        action="append",
        type=Path,
        default=[],
        help="Input wav path to include in the audible compare bundle. Can be passed multiple times.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--input-spec-jsonl",
        type=Path,
        default=None,
        help="Optional jsonl spec with case_id, input_audio_path, max_audio_sec, and notes fields.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle"),
        help="Directory for per-case runs, shared positive-control audio, per-variant decoded wavs, and the aggregate compare summary.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the audible compare bundle. Defaults to cpu for reproducibility.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--max-audio-sec-default",
        type=float,
        default=None,
        help="Fallback max duration when --input-audio is used directly without per-case max_audio_sec.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=33.333333,
        help="Teacher runtime chunk window in milliseconds for each audible compare case.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=DEFAULT_CALIBRATION_ASSET_PATH,
        help="Calibration asset used both for demo conditioning and default target-reference resolution.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--target-reference-audio",
        type=Path,
        default=None,
        help="Optional explicit target-reference wav. Defaults to the first selected record from the calibration asset.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--target-reference-max-audio-sec",
        type=float,
        default=DEFAULT_AUDIBLE_SMOKE_TARGET_REFERENCE_MAX_AUDIO_SEC,
        help="Optional max duration for the shared target-reference listening asset.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--vocoder-spec-jsonl",
        type=Path,
        default=None,
        help=(
            "Optional jsonl spec with label, optional variant_id, checkpoint_path or checkpoint_selection_path "
            "or checkpoint_source_summary_path, plus optional selection_target, use_predicted_activity_gate, "
            "predicted_activity_gate_apply_mode, normalization_strategy, control_family_overrides, "
            "checkpoint_source_key, and notes fields."
        ),
    )
    teacher_first_vc_audible_compare_parser.set_defaults(
        save_intermediates=False,
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--save-intermediates",
        dest="save_intermediates",
        action="store_true",
        help="Keep per-case teacher contract and vocoder scaffold intermediates.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--no-save-intermediates",
        dest="save_intermediates",
        action="store_false",
        help="Remove per-case intermediates after decoded wav export.",
    )
    teacher_first_vc_audible_compare_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the teacher full-pass verification stage for each audible compare variant run.",
    )
    teacher_first_vc_applicability_parser = subparsers.add_parser(
        "analyze-offline-mvp-teacher-first-vc-applicability",
        help="Compare teacher-first user-line scaffold features against Stage5 reference training-package distributions.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--input-audio",
        dest="input_audio_list",
        action="append",
        type=Path,
        required=True,
        help="Input wav path to diagnose. Can be passed multiple times.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe"),
        help="Directory for per-case runs and applicability summaries.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--reference-package",
        dest="reference_package_list",
        action="append",
        type=Path,
        default=[],
        help="Optional explicit Stage5 training-package path. Can be passed multiple times.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--reference-package-limit",
        type=int,
        default=32,
        help="When explicit reference packages are omitted, use up to this many default Stage5 train packages.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the diagnostic case exports. Defaults to cpu.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from each diagnostic input wav.",
    )
    teacher_first_vc_applicability_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=33.333333,
        help="Teacher runtime chunk window in milliseconds for each diagnostic export.",
    )
    teacher_first_vc_decoder_behavior_parser = subparsers.add_parser(
        "analyze-offline-mvp-teacher-first-vc-decoder-behavior",
        help="Compare teacher-first user-line decoder outputs against the same Stage5 checkpoint on in-distribution training packages.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--input-audio",
        dest="input_audio_list",
        action="append",
        type=Path,
        required=True,
        help="Input wav path to diagnose. Can be passed multiple times.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/decoder_behavior_probe"
        ),
        help="Directory for per-case runs and decoder-behavior summaries.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--reference-package",
        dest="reference_package_list",
        action="append",
        type=Path,
        default=[],
        help="Optional explicit Stage5 training-package path. Can be passed multiple times.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--reference-package-limit",
        type=int,
        default=32,
        help="When explicit reference packages are omitted, use up to this many default Stage5 train packages.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--device",
        default="cpu",
        help="Runtime device for the diagnostic case exports. Defaults to cpu.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from each diagnostic input wav.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=33.333333,
        help="Teacher runtime chunk window in milliseconds for each diagnostic export.",
    )
    teacher_first_vc_decoder_behavior_parser.set_defaults(
        use_predicted_activity_gate=True,
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply the predicted activity gate during decoder-behavior reconstruction.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--disable-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Bypass the predicted activity gate so the probe reconstructs directly from waveform_frames.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help="How predicted activity gains are applied when the gate is enabled: pre_overlap_add or post_ola_envelope.",
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--normalization-strategy",
        default="none",
        help=(
            "Optional inference-only scaffold normalization strategy for the probe: "
            "none, conditioning_reference_mean, reference_q01_q99_clip, reference_affine_match, or "
            "conditioning_reference_mean_plus_reference_q01_q99_clip."
        ),
    )
    teacher_first_vc_decoder_behavior_parser.add_argument(
        "--control-family-override",
        dest="control_family_overrides",
        action="append",
        default=[],
        help=(
            "Optional inference-only family-level override for root-cause isolation. "
            "Format: family=mode, for example z_art=reference_mean or proxy_family=zero. "
            "Can be passed multiple times."
        ),
    )

    nores_vocoder_parser = subparsers.add_parser(
        "prepare-offline-mvp-nores-vocoder-scaffold",
        help="Prepare a no-residual source-filter vocoder scaffold on top of the teacher consumer scaffold.",
    )
    nores_vocoder_parser.add_argument(
        "--input-scaffold",
        type=Path,
        required=True,
        help="teacher_vocoder_input_scaffold.pt path produced by the consumer-side scaffold builder.",
    )
    nores_vocoder_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_scaffold"),
        help="Directory for no-residual vocoder scaffold outputs.",
    )
    nores_vocoder_parser.add_argument(
        "--hidden-dim",
        type=int,
        default=64,
        help="Hidden dimension used by the dual-branch vocoder scaffold.",
    )
    nores_vocoder_parser.add_argument(
        "--harmonic-bins",
        type=int,
        default=32,
        help="Output dimension of the periodic/harmonic envelope head.",
    )
    nores_vocoder_parser.add_argument(
        "--noise-bins",
        type=int,
        default=32,
        help="Output dimension of the noise envelope head.",
    )
    nores_vocoder_targets_parser = subparsers.add_parser(
        "build-offline-mvp-nores-vocoder-train-targets",
        help="Build a minimal Stage5 spectral/gate training package for the no-residual vocoder route.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--input-scaffold",
        type=Path,
        required=True,
        help="teacher_vocoder_input_scaffold.pt path produced by the consumer-side scaffold builder.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--target-audio",
        type=Path,
        required=True,
        help="Reference waveform used to build aligned spectral targets.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_train_targets"),
        help="Directory for the no-residual vocoder train-target package.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--harmonic-bins",
        type=int,
        default=32,
        help="Output dimension for the harmonic branch target envelope.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--noise-bins",
        type=int,
        default=32,
        help="Output dimension for the noise branch target envelope.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--sample-rate",
        type=int,
        default=None,
        help="Optional override when older scaffold payloads do not carry runtime sample_rate metadata.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--frame-length",
        type=int,
        default=None,
        help="Optional override when older scaffold payloads do not carry runtime frame_length metadata.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--hop-length",
        type=int,
        default=None,
        help="Optional override when older scaffold payloads do not carry runtime hop_length metadata.",
    )
    nores_vocoder_targets_parser.add_argument(
        "--target-contract-mode",
        default=DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
        help=(
            "How Stage5 periodic_gate_target / noise_gate_target are built inside the package: "
            "legacy_proxy, v2core_aper_energy_only_v1, or teacher_e_evt_gate_targets_v1."
        ),
    )
    nores_vocoder_train_step_parser = subparsers.add_parser(
        "run-offline-mvp-nores-vocoder-train-step",
        help="Run one training step on the minimal no-residual vocoder target package.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--train-targets",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_train_targets.pt path produced by the train-target builder.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_train_step"),
        help="Directory for the no-residual vocoder train-step outputs.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--device",
        default="auto",
        help="Training device. Use auto, cpu, cuda, or cuda:0.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--seed",
        type=int,
        default=20260317,
        help="Random seed used for model initialization and any stochastic training components.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--deterministic",
        action="store_true",
        help="Enable deterministic Torch/CuDNN execution for stricter reproducibility at some runtime cost.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--hidden-dim",
        type=int,
        default=64,
        help="Hidden dimension used by the no-residual vocoder scaffold during the train step.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-3,
        help="Adam learning rate for the single train-step smoke run.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=5.0,
        help="Gradient clipping threshold for the single train-step smoke run.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--harmonic-weight",
        type=float,
        default=1.0,
        help="Loss weight for the harmonic envelope target.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--noise-weight",
        type=float,
        default=1.0,
        help="Loss weight for the noise envelope target.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the periodic gate target.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--noise-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the noise gate target.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--waveform-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for aligned waveform L1 reconstruction.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on the aligned waveform.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--rms-guard-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for keeping decoded waveform RMS close to target RMS.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--activity-gate-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for frame-activity supervision derived from aligned target waveform energy.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--active-template-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for active-frame template-excess suppression on reconstructed waveform frames.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching on reconstructed waveform frames.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--frame-spectral-flux-zero-target-jitter-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing decoded frame spectral-flux jitter when the aligned target transition is near zero.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--use-predicted-activity-gate",
        action="store_true",
        help="Apply predicted frame activity as a gate on waveform-frame reconstruction during loss computation.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--reconstruction-frame-gain-apply-mode",
        default=DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
        help=(
            "How predicted frame gains are applied during training-side waveform reconstruction: "
            "pre_overlap_add or post_ola_envelope. "
            "Defaults to the current explicit training semantics."
        ),
    )
    nores_vocoder_train_step_parser.add_argument(
        "--decoder-branch-mean-mix-alpha",
        type=float,
        default=0.0,
        help="Optional forward-path mix coefficient that blends fused_hidden with the equal-weight branch mean before the waveform decoder.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--fusion-mode",
        default="plain",
        help="Fusion structure before waveform decoding: plain, branch_mean_residual_v1, periodic_residual_v1, or branch_mean_contrast_residual_v1.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--waveform-decoder-mode",
        default="fused_single",
        help="Waveform decoder structure: fused_single, dual_branch_mix, periodic_plus_noise_residual, periodic_plus_noise_residual_shape, periodic_plus_noise_factorized_residual, periodic_plus_noise_residual_shape_temporal, or periodic_plus_noise_residual_shape_recurrent.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--use-decoder-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned decoder adapter built from fused_hidden, branch_mean_hidden, and their difference.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--use-residual-shape-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned correction applied only to the residual-shape / residual-envelope path.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-waveform-frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching applied directly to periodic_waveform_frames.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-waveform-frame-adjacent-cosine-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic_waveform_frames adjacent-frame cosine similarity above the aligned target on active transitions.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-waveform-frame-rms-floor-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for preventing periodic_waveform_frames active-frame log-RMS from falling below the aligned target floor.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-waveform-stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on periodic_waveform_frames reconstructed with periodic_gate gains.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--periodic-waveform-high-band-excess-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic-only reconstructed waveform high-band energy ratio above the aligned target.",
    )
    nores_vocoder_train_step_parser.add_argument(
        "--multires-stft-short-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for short-window MRSTFT supervision on decoded waveform.",
    )
    nores_vocoder_train_loop_parser = subparsers.add_parser(
        "run-offline-mvp-nores-vocoder-training-loop",
        help="Run a minimal multi-step training loop on the no-residual vocoder target package.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--train-targets",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_train_targets.pt path used for training.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--validation-targets",
        type=Path,
        default=None,
        help="Optional validation target package. If omitted, the training package is reused for validation.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_training_loop"),
        help="Directory for the no-residual vocoder training-loop outputs.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--device",
        default="auto",
        help="Training device. Use auto, cpu, cuda, or cuda:0.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--seed",
        type=int,
        default=20260317,
        help="Random seed used for model initialization and any stochastic training components.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--deterministic",
        action="store_true",
        help="Enable deterministic Torch/CuDNN execution for stricter reproducibility at some runtime cost.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--num-steps",
        type=int,
        default=3,
        help="Number of training steps for the minimal loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--validation-interval",
        type=int,
        default=1,
        help="Validation interval in steps for the minimal loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1,
        help="Checkpoint interval in steps for the minimal loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--hidden-dim",
        type=int,
        default=64,
        help="Hidden dimension used by the no-residual vocoder scaffold during the loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-3,
        help="Adam learning rate for the minimal loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=5.0,
        help="Gradient clipping threshold for the minimal loop.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--harmonic-weight",
        type=float,
        default=1.0,
        help="Loss weight for the harmonic envelope target.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--noise-weight",
        type=float,
        default=1.0,
        help="Loss weight for the noise envelope target.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the periodic gate target.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--noise-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the noise gate target.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--waveform-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for aligned waveform L1 reconstruction.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on the aligned waveform.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--rms-guard-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for keeping decoded waveform RMS close to target RMS.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--activity-gate-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for frame-activity supervision derived from aligned target waveform energy.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--active-template-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for active-frame template-excess suppression on reconstructed waveform frames.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching on reconstructed waveform frames.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--frame-spectral-flux-zero-target-jitter-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing decoded frame spectral-flux jitter when the aligned target transition is near zero.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--use-predicted-activity-gate",
        action="store_true",
        help="Apply predicted frame activity as a gate on waveform-frame reconstruction during loss computation.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--reconstruction-frame-gain-apply-mode",
        default=DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
        help=(
            "How predicted frame gains are applied during training-side waveform reconstruction: "
            "pre_overlap_add or post_ola_envelope. "
            "Defaults to the current explicit training semantics."
        ),
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--decoder-branch-mean-mix-alpha",
        type=float,
        default=0.0,
        help="Optional forward-path mix coefficient that blends fused_hidden with the equal-weight branch mean before the waveform decoder.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--fusion-mode",
        default="plain",
        help="Fusion structure before waveform decoding: plain, branch_mean_residual_v1, periodic_residual_v1, or branch_mean_contrast_residual_v1.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--waveform-decoder-mode",
        default="fused_single",
        help="Waveform decoder structure: fused_single, dual_branch_mix, periodic_plus_noise_residual, periodic_plus_noise_residual_shape, periodic_plus_noise_factorized_residual, periodic_plus_noise_residual_shape_temporal, or periodic_plus_noise_residual_shape_recurrent.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--use-decoder-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned decoder adapter built from fused_hidden, branch_mean_hidden, and their difference.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--use-residual-shape-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned correction applied only to the residual-shape / residual-envelope path.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-waveform-frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching applied directly to periodic_waveform_frames.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-waveform-frame-adjacent-cosine-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic_waveform_frames adjacent-frame cosine similarity above the aligned target on active transitions.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-waveform-frame-rms-floor-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for preventing periodic_waveform_frames active-frame log-RMS from falling below the aligned target floor.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-waveform-stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on periodic_waveform_frames reconstructed with periodic_gate gains.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--periodic-waveform-high-band-excess-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic-only reconstructed waveform high-band energy ratio above the aligned target.",
    )
    nores_vocoder_train_loop_parser.add_argument(
        "--multires-stft-short-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for short-window MRSTFT supervision on decoded waveform.",
    )
    nores_vocoder_dataset_packages_parser = subparsers.add_parser(
        "build-offline-mvp-nores-vocoder-dataset-packages",
        help="Build split-backed Stage5 train-target packages and a dataset index for the no-residual vocoder route.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--train-split",
        type=Path,
        default=Path("data_prep/round1_1/splits/hybrid_stratified_blocked/target_train.jsonl"),
        help="Training split jsonl used to materialize aligned Stage5 target packages.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--validation-split",
        type=Path,
        default=Path("data_prep/round1_1/splits/hybrid_stratified_blocked/target_validation.jsonl"),
        help="Optional validation split jsonl used to materialize aligned validation packages.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--train-pair-spec",
        type=Path,
        default=None,
        help=(
            "Optional train pair-spec jsonl override. "
            "Each row must provide source_audio_path and target_audio_path; when set, it overrides --train-split."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--validation-pair-spec",
        type=Path,
        default=None,
        help=(
            "Optional validation pair-spec jsonl override. "
            "Each row must provide source_audio_path and target_audio_path; when set, it overrides --validation-split."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_dataset_packages"),
        help="Directory for dataset-level Stage5 package exports and the dataset index.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--route-handoff",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json"),
        help="Route handoff used to resolve the formal teacher checkpoint when --checkpoint is omitted.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit teacher checkpoint override.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--calibration-asset",
        type=Path,
        default=Path("data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"),
        help="Calibration asset providing s_spk_target, s_geom_target, and alpha.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--target-event-semantic-sidecar",
        type=Path,
        default=None,
        help=(
            "Optional target_event_semantic_sidecar jsonl. When omitted, Stage5 will infer the standard "
            "round1_1 sidecar from the split directory when available."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--target-event-timing-semantic-sidecar",
        type=Path,
        default=None,
        help=(
            "Optional target_event_timing_semantic_sidecar jsonl. When omitted, Stage5 will infer the standard "
            "round1_1 timing sidecar from the split directory when available."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--source-semantic-parity-sidecar",
        type=Path,
        default=None,
        help=(
            "Optional paired_parallel_source_semantic_parity_sidecar jsonl. When omitted, Stage5 will infer the "
            "standard round1_1 parity sidecar from the split directory when available."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--semantic-consumer-mode",
        default="none",
        help=(
            "How target_event_semantic_sidecar is consumed during package build: "
            "none, target_sidecar_broadcast_v1, target_timing_sidecar_framewise_v1, or "
            "source_semantic_parity_framewise_v1."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--target-contract-mode",
        default=DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
        help=(
            "How Stage5 periodic_gate_target / noise_gate_target are built inside each package: "
            "legacy_proxy, v2core_aper_energy_only_v1, or teacher_e_evt_gate_targets_v1."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--spectral-target-mode",
        default=DEFAULT_STAGE5_SPECTRAL_TARGET_MODE,
        help=(
            "How Stage5 harmonic/noise spectral targets are built inside each package: "
            "legacy_halfsplit, gate_masked_halfsplit_v1, or f0_harmonicity_split_v1."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--teacher-eevt-bridge-mode",
        type=str,
        default="legacy_event_probs_v1",
        help=(
            "Generation-side bridge mode used when Stage5 exports explicit teacher e_evt into the downstream contract. "
            "Examples: legacy_event_probs_v1, acoustic_guided_event_bridge_v1."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--teacher-eevt-target-shaping-mode",
        type=str,
        default="hard_box_v1",
        help=(
            "Generation-side shaping mode used when Stage5 exports explicit teacher e_evt into the downstream contract. "
            "Examples: hard_box_v1, center_weighted_boundary_progressive_final_clause_v1."
        ),
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--chunk-samples",
        type=int,
        default=None,
        help="Optional runtime chunk size in samples. Mutually exclusive with --chunk-ms.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--chunk-ms",
        type=float,
        default=None,
        help="Optional runtime chunk size in milliseconds when --chunk-samples is omitted.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--device",
        default="auto",
        help="Runtime device. Use auto, cpu, cuda, or cuda:0.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--worker-processes",
        type=int,
        default=1,
        help="How many record-level worker processes to use during package export.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=None,
        help="Optional max duration to read from each wav during package export.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--skip-full-pass-verify",
        action="store_true",
        help="Skip the full-utterance verification pass while materializing teacher contracts.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--max-train-records",
        type=int,
        default=None,
        help="Optional cap on how many train records to materialize from the split.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--max-validation-records",
        type=int,
        default=None,
        help="Optional cap on how many validation records to materialize from the split.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--selection-mode",
        default="file_order",
        help="Subset selection mode for capped exports. Use file_order or shortest_duration.",
    )
    nores_vocoder_dataset_packages_parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Reuse existing package artifacts when the output package already exists.",
    )
    nores_vocoder_dataset_loop_parser = subparsers.add_parser(
        "run-offline-mvp-nores-vocoder-dataset-training-loop",
        help="Run the dataset-level Stage5 training loop on a split-backed no-residual vocoder dataset index.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--dataset-index",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_dataset_index.json path produced by the dataset package builder.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop"),
        help="Directory for dataset-level no-residual vocoder loop outputs.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--device",
        default="auto",
        help="Training device. Use auto, cpu, cuda, or cuda:0.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--num-steps",
        type=int,
        default=3,
        help="Number of dataset-level training steps for the loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--packages-per-step",
        type=int,
        default=2,
        help="How many aligned training packages to sample per optimizer step.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--validation-interval",
        type=int,
        default=1,
        help="Validation interval in steps for the dataset-level loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1,
        help="Checkpoint interval in steps for the dataset-level loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--sampler-mode",
        default="shuffle",
        help="Dataset package sampler mode. Use sequential or shuffle.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--seed",
        type=int,
        default=20260317,
        help="Random seed used for package shuffling, model initialization, and any stochastic training components.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--deterministic",
        action="store_true",
        help="Enable deterministic Torch/CuDNN execution for stricter reproducibility at some runtime cost.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--hidden-dim",
        type=int,
        default=64,
        help="Hidden dimension used by the no-residual vocoder scaffold during the dataset loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-3,
        help="Adam learning rate for the dataset-level loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--max-grad-norm",
        type=float,
        default=5.0,
        help="Gradient clipping threshold for the dataset-level loop.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--harmonic-weight",
        type=float,
        default=1.0,
        help="Loss weight for the harmonic envelope target.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--noise-weight",
        type=float,
        default=1.0,
        help="Loss weight for the noise envelope target.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the periodic gate target.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--noise-gate-weight",
        type=float,
        default=0.2,
        help="Loss weight for the noise gate target.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--waveform-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for aligned waveform L1 reconstruction.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on the aligned waveform.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--rms-guard-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for keeping decoded waveform RMS close to target RMS.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--activity-gate-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for frame-activity supervision derived from aligned target waveform energy.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--active-template-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for active-frame template-excess suppression on reconstructed waveform frames.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching on reconstructed waveform frames.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--frame-adjacent-cosine-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing decoded adjacent-frame cosine similarity above the aligned target on active transitions.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--frame-spectral-flux-zero-target-jitter-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing decoded frame spectral-flux jitter when the aligned target transition is near zero.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--fused-hidden-template-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing fused_hidden template collapse relative to the branch hidden states.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--fused-hidden-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for preventing fused_hidden adjacent-frame delta magnitude from collapsing below the branch hidden floor.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--fused-hidden-branch-mean-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for pulling fused_hidden toward the equal-weight branch mean in unit-RMS space on active frames.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--use-predicted-activity-gate",
        action="store_true",
        help="Apply predicted frame activity as a gate on waveform-frame reconstruction during loss computation.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--reconstruction-frame-gain-apply-mode",
        default=DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE,
        help=(
            "How predicted frame gains are applied during training-side waveform reconstruction: "
            "pre_overlap_add or post_ola_envelope. "
            "Defaults to the current explicit training semantics."
        ),
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--decoder-branch-mean-mix-alpha",
        type=float,
        default=0.0,
        help="Optional forward-path mix coefficient that blends fused_hidden with the equal-weight branch mean before the waveform decoder.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--fusion-mode",
        default="plain",
        help="Fusion structure before waveform decoding: plain, branch_mean_residual_v1, periodic_residual_v1, or branch_mean_contrast_residual_v1.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--waveform-decoder-mode",
        default="fused_single",
        help="Waveform decoder structure: fused_single, dual_branch_mix, periodic_plus_noise_residual, periodic_plus_noise_residual_shape, periodic_plus_noise_factorized_residual, periodic_plus_noise_residual_shape_temporal, or periodic_plus_noise_residual_shape_recurrent.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--use-decoder-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned decoder adapter built from fused_hidden, branch_mean_hidden, and their difference.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--use-residual-shape-branch-condition-adapter",
        action="store_true",
        help="Enable a learned non-linear branch-conditioned correction applied only to the residual-shape / residual-envelope path.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-waveform-frame-delta-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for unit-RMS adjacent-frame delta matching applied directly to periodic_waveform_frames.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-waveform-frame-adjacent-cosine-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic_waveform_frames adjacent-frame cosine similarity above the aligned target on active transitions.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-waveform-frame-rms-floor-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for preventing periodic_waveform_frames active-frame log-RMS from falling below the aligned target floor.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-waveform-stft-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for log-STFT reconstruction on periodic_waveform_frames reconstructed with periodic_gate gains.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--periodic-waveform-high-band-excess-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for suppressing periodic-only reconstructed waveform high-band energy ratio above the aligned target.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--multires-stft-short-weight",
        type=float,
        default=0.0,
        help="Optional loss weight for short-window MRSTFT reconstruction using frame lengths 256, 512, and the runtime frame length.",
    )
    nores_vocoder_dataset_loop_parser.add_argument(
        "--semantic-supervision-enabled",
        action="store_true",
        help="Enable conservative package-level weighting derived from target_event_semantic_sidecar metadata.",
    )
    nores_vocoder_review_parser = subparsers.add_parser(
        "review-offline-mvp-nores-vocoder-checkpoints",
        help="Review validation checkpoint trajectories for the no-residual vocoder dataset loop summary.",
    )
    nores_vocoder_review_parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="Path to offline_mvp_nores_vocoder_dataset_loop.summary.json.",
    )
    nores_vocoder_review_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_checkpoint_review"),
        help="Directory for checkpoint review outputs.",
    )
    nores_vocoder_review_parser.add_argument(
        "--top-k",
        type=int,
        default=8,
        help="Number of most-improved and most-worsened validation records to list per review window.",
    )
    nores_vocoder_selection_parser = subparsers.add_parser(
        "select-offline-mvp-nores-vocoder-checkpoint",
        help="Select best-by-loss and stable late-stop checkpoints from a Stage5 no-residual vocoder dataset-loop summary.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--summary",
        type=Path,
        required=True,
        help="Path to offline_mvp_nores_vocoder_dataset_loop.summary.json.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection"),
        help="Directory for Stage5 checkpoint-selection outputs.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--late-step-ratio",
        type=float,
        default=0.5,
        help="Fraction of max step used to define the late-window checkpoint range.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--validation-guard-ratio",
        type=float,
        default=1.03,
        help="Maximum validation-loss ratio relative to the best checkpoint allowed for stable late-stop selection.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--max-pairwise-worsened-ratio",
        type=float,
        default=0.2,
        help="Maximum allowed worsened package ratio between the previous checkpoint and the candidate late-stop checkpoint.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--max-rms-ratio-deviation",
        type=float,
        default=0.03,
        help="Maximum allowed absolute deviation of decoded_to_target_rms_ratio from 1.0 for stable late-stop selection.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--low-activity-probe",
        type=Path,
        default=None,
        help="Optional stage5_low_activity_fragmentation_probe.json used to annotate checkpoint governance with low-activity tradeoffs.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--low-activity-audio-source",
        choices=["decoded", "decoded_pitch_matched", "audit_proxy", "listening"],
        default="decoded",
        help="Audio source to read from the optional low-activity probe payload.",
    )
    nores_vocoder_selection_parser.add_argument(
        "--low-activity-soft-validation-ratio",
        type=float,
        default=1.05,
        help="Near-best validation budget used by the optional low-activity soft rerank inside late candidates.",
    )
    nores_vocoder_audio_export_parser = subparsers.add_parser(
        "export-offline-mvp-nores-vocoder-audio",
        help="Export aligned target and decoded audio for selected Stage5 no-residual vocoder packages.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/offline_mvp_nores_vocoder_audio_export"),
        help="Directory for Stage5 no-residual vocoder audio export outputs.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit checkpoint path. When omitted, --checkpoint-selection must be provided.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        default=None,
        help="Optional Stage5 checkpoint-selection json used to resolve the export checkpoint.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--dataset-index",
        type=Path,
        default=None,
        help="Optional dataset index override. When omitted, the export uses the dataset index recorded inside the checkpoint payload.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--selection-target",
        default="stable_late_stop",
        help="Checkpoint role to export from the selection payload: stable_late_stop, best_validation, or best_rms.",
    )
    student_stage5_dataset_parser = subparsers.add_parser(
        "build-streaming-student-stage5-dataset-packages",
        help="Adapt exported Stage3 student_control_packet records into minimal Stage5 packages for fail-fast decoded.wav export.",
    )
    student_stage5_dataset_parser.add_argument(
        "--packet-export",
        type=Path,
        required=True,
        help="streaming_student_downstream_control_packet.json produced by the Stage3 packet exporter.",
    )
    student_stage5_dataset_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/runtime/streaming_student_stage5_dataset_packages"),
        help="Directory for scaffold/package artifacts and the synthetic dataset index.",
    )
    student_stage5_dataset_parser.add_argument(
        "--split-name",
        default="validation",
        help="Synthetic split name to write into the dataset index: validation or train.",
    )
    student_stage5_dataset_parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="How many packet records to adapt when --target-record-ids is omitted.",
    )
    student_stage5_dataset_parser.add_argument(
        "--target-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit record ids to adapt from the packet export.",
    )
    student_stage5_dataset_parser.add_argument(
        "--semantic-consumer-mode",
        default="none",
        help="How Stage5 semantic sidecar features are consumed inside each synthetic package. Keep none for the minimal route.",
    )
    student_stage5_dataset_parser.add_argument(
        "--target-contract-mode",
        default=DEFAULT_STAGE5_TARGET_CONTRACT_MODE,
        help="How package gate targets are built inside each synthetic Stage5 package.",
    )
    student_stage5_dataset_parser.add_argument(
        "--noise-event-family",
        default="e_evt",
        help="Which Stage3 packet family populates the Stage5 noise-branch first 8 dims: e_evt or legacy_event_probs.",
    )
    student_stage5_dataset_parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Reuse existing scaffold/package artifacts when the synthetic package already exists.",
    )
    add_student_route_guard_argument(student_stage5_dataset_parser)
    nores_vocoder_audio_export_parser.add_argument(
        "--split-name",
        default="validation",
        help="Dataset split to export from: validation or train.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--sample-count",
        type=int,
        default=6,
        help="How many packages to export when --target-record-ids is omitted.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--target-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit target record ids to export.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--audit-carrier-frequency",
        type=float,
        default=185.0,
        help="Carrier frequency in Hz for the low-frequency audit proxy written for GUI listening.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--listening-audio-source",
        default="decoded",
        help="Primary listening source written into the GUI-compatible manifest: decoded, decoded_pitch_matched, or audit_proxy.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--pitch-match-reference",
        default="none",
        help="Optional pitch-matching reference for decoded listening audio: none or aligned_target.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--pitch-match-fmin-hz",
        type=float,
        default=65.0,
        help="Lower voiced F0 bound in Hz used by pitch-matching analysis.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--pitch-match-fmax-hz",
        type=float,
        default=440.0,
        help="Upper voiced F0 bound in Hz used by pitch-matching analysis.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--pitch-match-max-semitones",
        type=float,
        default=8.0,
        help="Maximum absolute semitone shift allowed during decoded pitch matching.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--activity-gate-weight",
        type=float,
        default=None,
        help=(
            "Optional activity-gate loss weight override used when recomputing export metrics. "
            "When omitted, inherit the checkpoint training summary value when available."
        ),
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--active-template-weight",
        type=float,
        default=None,
        help=(
            "Optional active-template loss weight override used when recomputing export metrics. "
            "When omitted, inherit the checkpoint training summary value when available."
        ),
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--frame-delta-weight",
        type=float,
        default=None,
        help=(
            "Optional frame-delta loss weight override used when recomputing export metrics. "
            "When omitted, inherit the checkpoint training summary value when available."
        ),
    )
    nores_vocoder_audio_export_parser.set_defaults(use_predicted_activity_gate=None)
    nores_vocoder_audio_export_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply predicted frame activity during export-side waveform reconstruction.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--disable-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Disable predicted frame activity during export-side waveform reconstruction.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--predicted-activity-gate-floor",
        type=float,
        default=0.0,
        help="Optional minimum export-side frame gain applied after predicted activity gating; use this to soften hard zeroing without disabling the gate.",
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--predicted-activity-gate-smoothing-frames",
        type=int,
        default=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        help=(
            "Moving-average radius for export-side predicted activity gate smoothing across neighboring frames. "
            "Defaults to the current promoted Stage5 decode setting; pass 0 to recover the legacy hard-gate export."
        ),
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help=(
            "How export-side predicted activity gains are applied during waveform reconstruction: "
            "pre_overlap_add or post_ola_envelope."
        ),
    )
    nores_vocoder_audio_export_parser.add_argument(
        "--decoder-branch-mean-mix-alpha",
        type=float,
        default=0.0,
        help="Optional forward-path mix coefficient used when recomputing waveform_frames from the exported checkpoint.",
    )
    stage5_speech_emergence_probe_parser = subparsers.add_parser(
        "analyze-stage5-nores-speech-emergence",
        help="Run route-level Stage5 no-res speech-emergence root-cause probe variants over selected training packages.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for Stage5 speech-emergence probe outputs.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit checkpoint path. When omitted, --checkpoint-selection must be provided.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        default=None,
        help="Optional Stage5 checkpoint-selection json used to resolve the probe checkpoint.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--selection-target",
        default="best_validation",
        help="Checkpoint role to probe from the selection payload: stable_late_stop, best_validation, or best_rms.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--dataset-index",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_dataset_index.json used to resolve probe packages.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--split-name",
        default="validation",
        help="Dataset split to probe from: validation or train.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--sample-count",
        type=int,
        default=12,
        help="How many packages to probe when --target-record-ids is omitted.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--target-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit target record ids to probe.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device used for the probe, for example cpu or cuda:0.",
    )
    stage5_speech_emergence_probe_parser.set_defaults(use_predicted_activity_gate=True)
    stage5_speech_emergence_probe_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply predicted frame activity during waveform reconstruction to match the heard Stage5 route.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--disable-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Disable predicted frame activity during waveform reconstruction.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--predicted-activity-gate-floor",
        type=float,
        default=0.0,
        help="Minimum frame gain applied after predicted activity gating.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--predicted-activity-gate-smoothing-frames",
        type=int,
        default=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        help="Moving-average radius for predicted activity gate smoothing across neighboring frames.",
    )
    stage5_speech_emergence_probe_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help="How predicted activity gains are applied during waveform reconstruction: pre_overlap_add or post_ola_envelope.",
    )
    stage5_waveform_decoder_structure_parser = subparsers.add_parser(
        "analyze-stage5-nores-waveform-decoder-structure",
        help="Probe whether temporal diversity collapse happens before fusion or inside the Stage5 waveform decoder head.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for Stage5 waveform-decoder structure probe outputs.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit checkpoint path. When omitted, --checkpoint-selection must be provided.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        default=None,
        help="Optional Stage5 checkpoint-selection json used to resolve the probe checkpoint.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--selection-target",
        default="best_validation",
        help="Checkpoint role to probe from the selection payload: stable_late_stop, best_validation, or best_rms.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--dataset-index",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_dataset_index.json used to resolve probe packages.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--split-name",
        default="validation",
        help="Dataset split to probe from: validation or train.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--sample-count",
        type=int,
        default=12,
        help="How many packages to probe when --target-record-ids is omitted.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--target-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit target record ids to probe.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device used for the probe, for example cpu or cuda:0.",
    )
    stage5_waveform_decoder_structure_parser.set_defaults(use_predicted_activity_gate=True)
    stage5_waveform_decoder_structure_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply predicted frame activity during waveform reconstruction to match the heard Stage5 route.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--disable-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Disable predicted frame activity during waveform reconstruction.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--predicted-activity-gate-floor",
        type=float,
        default=0.0,
        help="Minimum frame gain applied after predicted activity gating.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--predicted-activity-gate-smoothing-frames",
        type=int,
        default=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        help="Moving-average radius for predicted activity gate smoothing across neighboring frames.",
    )
    stage5_waveform_decoder_structure_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help="How predicted activity gains are applied during waveform reconstruction: pre_overlap_add or post_ola_envelope.",
    )
    stage5_waveform_objective_collapse_parser = subparsers.add_parser(
        "analyze-stage5-nores-waveform-objective-collapse",
        help="Probe whether fixed-template counterexamples can still land at low Stage5 waveform objective on selected packages.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for Stage5 waveform-objective collapse probe outputs.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Optional explicit checkpoint path. When omitted, --checkpoint-selection must be provided.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        default=None,
        help="Optional Stage5 checkpoint-selection json used to resolve the probe checkpoint.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--selection-target",
        default="best_validation",
        help="Checkpoint role to probe from the selection payload: stable_late_stop, best_validation, or best_rms.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--dataset-index",
        type=Path,
        required=True,
        help="offline_mvp_nores_vocoder_dataset_index.json used to resolve probe packages.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--split-name",
        default="validation",
        help="Dataset split to probe from: validation or train.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--sample-count",
        type=int,
        default=12,
        help="How many packages to probe when --target-record-ids is omitted.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--target-record-ids",
        nargs="*",
        default=None,
        help="Optional explicit target record ids to probe.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device used to decode the baseline route, for example cpu or cuda:0.",
    )
    stage5_waveform_objective_collapse_parser.set_defaults(use_predicted_activity_gate=True)
    stage5_waveform_objective_collapse_parser.add_argument(
        "--use-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_true",
        help="Apply predicted frame activity during baseline waveform reconstruction to match the heard Stage5 route.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--disable-predicted-activity-gate",
        dest="use_predicted_activity_gate",
        action="store_false",
        help="Disable predicted frame activity during baseline waveform reconstruction.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--predicted-activity-gate-floor",
        type=float,
        default=0.0,
        help="Minimum frame gain applied after predicted activity gating.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--predicted-activity-gate-smoothing-frames",
        type=int,
        default=DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES,
        help="Moving-average radius for predicted activity gate smoothing across neighboring frames.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--predicted-activity-gate-apply-mode",
        default="post_ola_envelope",
        help="How predicted activity gains are applied during baseline waveform reconstruction: pre_overlap_add or post_ola_envelope.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--waveform-weight",
        type=float,
        default=0.5,
        help="Waveform L1 weight used when materializing the weighted Stage5 waveform objective.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--stft-weight",
        type=float,
        default=0.5,
        help="Log-STFT weight used when materializing the weighted Stage5 waveform objective.",
    )
    stage5_waveform_objective_collapse_parser.add_argument(
        "--rms-guard-weight",
        type=float,
        default=0.2,
        help="RMS guard weight used when materializing the weighted Stage5 waveform objective.",
    )
    ai_work_session_parser = subparsers.add_parser(
        "register-ai-work-session",
        help="Register or update an AI work session for parallel collaboration.",
    )
    ai_work_session_parser.add_argument(
        "--session-id",
        required=True,
        help="Stable session id used as the registry filename.",
    )
    ai_work_session_parser.add_argument(
        "--owner",
        required=True,
        help="Short owner label, for example codex-a or user-line-worker.",
    )
    ai_work_session_parser.add_argument(
        "--lane",
        required=True,
        help="Collaboration lane, for example experiment_line, user_line, or infra.",
    )
    ai_work_session_parser.add_argument(
        "--status",
        default="active",
        choices=list(VALID_SESSION_STATUSES),
        help="Session status used by the shared registry index.",
    )
    ai_work_session_parser.add_argument(
        "--objective",
        required=True,
        help="Current concrete objective of this session.",
    )
    ai_work_session_parser.add_argument(
        "--write-root",
        type=Path,
        action="append",
        default=[],
        help="Write root claimed by this session. Repeat the flag for multiple roots.",
    )
    ai_work_session_parser.add_argument(
        "--read-root",
        type=Path,
        action="append",
        default=[],
        help="Read-only root relevant to this session. Repeat the flag for multiple roots.",
    )
    ai_work_session_parser.add_argument(
        "--handoff-doc",
        type=Path,
        action="append",
        default=[],
        help="Handoff or status doc this session depends on. Repeat the flag for multiple docs.",
    )
    ai_work_session_parser.add_argument(
        "--depends-on",
        action="append",
        default=[],
        help="Upstream session id or blocker. Repeat the flag for multiple items.",
    )
    ai_work_session_parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="Flat note captured in the session card. Repeat the flag for multiple notes.",
    )
    ai_work_session_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/collab/ai_work_sessions"),
        help="Directory for AI work-session registry files.",
    )
    ai_work_session_index_parser = subparsers.add_parser(
        "materialize-ai-work-session-index",
        help="Rebuild the shared AI work-session index from existing session cards.",
    )
    ai_work_session_index_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/collab/ai_work_sessions"),
        help="Directory containing AI work-session cards.",
    )
    nores_vocoder_low_activity_sensitivity_parser = subparsers.add_parser(
        "analyze-offline-mvp-nores-vocoder-low-activity-sensitivity",
        help="Analyze low-activity soft-rerank sensitivity over an existing Stage5 no-residual vocoder checkpoint-selection payload.",
    )
    nores_vocoder_low_activity_sensitivity_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        required=True,
        help="Existing nores_vocoder_checkpoint_selection.json payload that already contains low-activity soft rerank.",
    )
    nores_vocoder_low_activity_sensitivity_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for low-activity soft-rerank sensitivity outputs.",
    )
    nores_vocoder_low_activity_sensitivity_parser.add_argument(
        "--weight-step",
        type=float,
        default=0.05,
        help="Simplex/grid step for weight sensitivity, for example 0.1 or 0.05.",
    )
    stage5_low_activity_governance_report_parser = subparsers.add_parser(
        "materialize-stage5-low-activity-governance-report",
        help="Materialize a fixed-format Stage5 low-activity governance report from a checkpoint-selection payload.",
    )
    stage5_low_activity_governance_report_parser.add_argument(
        "--checkpoint-selection",
        type=Path,
        required=True,
        help="Path to nores_vocoder_checkpoint_selection.json that already embeds low_activity_probe_analysis.",
    )
    stage5_low_activity_governance_report_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for the fixed-format governance report outputs.",
    )
    stage5_low_activity_governance_report_parser.add_argument(
        "--template",
        type=Path,
        default=Path("reports/templates/stage5_low_activity_governance_report_template.md"),
        help="Markdown template used to render the governance report.",
    )
    stage5_low_activity_governance_report_parser.add_argument(
        "--title",
        default=None,
        help="Optional override title written into the governance report.",
    )
    stage5_low_activity_audit_result_report_parser = subparsers.add_parser(
        "materialize-stage5-low-activity-audit-result-report",
        help="Materialize a fixed-format Stage5 low-activity audit result report by joining audio_audit_review.json with a governance report.",
    )
    stage5_low_activity_audit_result_report_parser.add_argument(
        "--audio-audit-review",
        type=Path,
        required=True,
        help="Path to audio_audit_review.json exported by the Stage5 listening GUI.",
    )
    stage5_low_activity_audit_result_report_parser.add_argument(
        "--governance-report",
        type=Path,
        required=True,
        help="Path to stage5_low_activity_governance_report.json that defines the dual-axis quantitative context.",
    )
    stage5_low_activity_audit_result_report_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for the fixed-format audit result report outputs.",
    )
    stage5_low_activity_audit_result_report_parser.add_argument(
        "--template",
        type=Path,
        default=Path("reports/templates/stage5_low_activity_audit_result_report_template.md"),
        help="Markdown template used to render the audit result report.",
    )
    stage5_low_activity_audit_result_report_parser.add_argument(
        "--title",
        default=None,
        help="Optional override title written into the audit result report.",
    )

    checkpoint_selection_parser = subparsers.add_parser(
        "analyze-offline-mvp-checkpoint-selection",
        help="Compare multiple experiment checkpoint series and summarize checkpoint-selection tradeoffs.",
    )
    checkpoint_selection_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="One or more experiment metrics json files that already contain special_eval_series and checkpoint_series_eval.",
    )
    checkpoint_selection_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_checkpoint_selection"),
        help="Directory for checkpoint-selection analysis outputs.",
    )
    checkpoint_selection_parser.add_argument(
        "--late-step-ratio",
        type=float,
        default=0.8,
        help="Fraction of max step used to define the late-window checkpoint range.",
    )
    checkpoint_selection_parser.add_argument(
        "--validation-guard-ratio",
        type=float,
        default=1.25,
        help="Maximum target-validation ratio relative to an experiment's best validation checkpoint for guarded selection.",
    )
    checkpoint_selection_parser.add_argument(
        "--min-positive-control-delta",
        type=float,
        default=0.1,
        help="Minimum zero_z_art / zero_e_evt target-loss delta required by the positive-control selector.",
    )

    checkpoint_anchor_parser = subparsers.add_parser(
        "materialize-offline-mvp-checkpoint-anchor",
        help="Materialize one checkpoint-series step as a synthetic anchor metrics payload.",
    )
    checkpoint_anchor_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        required=True,
        help="Experiment metrics json containing both special_eval_series and checkpoint_series_eval.",
    )
    checkpoint_anchor_parser.add_argument(
        "--step",
        type=int,
        required=True,
        help="Checkpoint step to materialize as an anchor.",
    )
    checkpoint_anchor_parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Output path for the synthetic checkpoint-anchor metrics json.",
    )

    matched_shadow_parser = subparsers.add_parser(
        "build-offline-mvp-matched-horizon-shadow",
        help="Materialize one checkpoint anchor and generate the matched-horizon shadow selector bundle.",
    )
    matched_shadow_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Matched-horizon experiment metrics list. The materialized checkpoint anchor will be inserted after the first item.",
    )
    matched_shadow_parser.add_argument(
        "--checkpoint-anchor-experiment-metrics",
        type=Path,
        required=True,
        help="Experiment metrics json used to materialize the checkpoint anchor.",
    )
    matched_shadow_parser.add_argument(
        "--checkpoint-anchor-step",
        type=int,
        required=True,
        help="Checkpoint step to materialize as the matched anchor.",
    )
    matched_shadow_parser.add_argument(
        "--validation-budgets",
        type=float,
        nargs="+",
        default=[0.05, 0.13],
        help="Validation budgets used to build matched-horizon selector/recap outputs.",
    )
    matched_shadow_parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for the full matched-horizon shadow bundle outputs.",
    )

    checkpoint_gate_parser = subparsers.add_parser(
        "analyze-offline-mvp-checkpoint-gates",
        help="Replay interpretable checkpoint-gate prototypes across multiple experiments.",
    )
    checkpoint_gate_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="One or more experiment metrics json files that already contain special_eval_series and checkpoint_series_eval.",
    )
    checkpoint_gate_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_checkpoint_gate_replay"),
        help="Directory for checkpoint-gate replay outputs.",
    )
    checkpoint_gate_parser.add_argument(
        "--late-step-ratio",
        type=float,
        default=0.8,
        help="Fraction of max step used to define the late-window checkpoint range.",
    )

    anchor_selection_parser = subparsers.add_parser(
        "analyze-offline-mvp-anchor-selection",
        help="Compare final anchor experiments and summarize metric leaders, minimax tradeoffs, and selection thresholds.",
    )
    anchor_selection_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    anchor_selection_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_anchor_selection"),
        help="Directory for anchor-selection analysis outputs.",
    )

    anchor_route_parser = subparsers.add_parser(
        "analyze-offline-mvp-anchor-routes",
        help="Build standard route-selector policies over final anchor experiments.",
    )
    anchor_route_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    anchor_route_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_anchor_routes"),
        help="Directory for anchor-route analysis outputs.",
    )

    anchor_route_selector_parser = subparsers.add_parser(
        "select-offline-mvp-anchor-route",
        help="Resolve one concrete anchor route from the current three-anchor policy set.",
    )
    anchor_route_selector_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    anchor_route_selector_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_anchor_route_selection"),
        help="Directory for anchor-route selection outputs.",
    )
    anchor_route_selector_parser.add_argument(
        "--max-validation-budget-over-best",
        type=float,
        required=True,
        help="Maximum allowed validation loss increase over the best-validation anchor.",
    )
    anchor_route_selector_parser.add_argument(
        "--special-priority",
        action="store_true",
        help="Prefer the special/z_art route when budget allows.",
    )
    anchor_route_selector_parser.add_argument(
        "--z-art-priority",
        action="store_true",
        help="Alias of special priority focused on z_art-sensitive routing.",
    )
    anchor_route_selector_parser.add_argument(
        "--require-best-e-evt-floor",
        action="store_true",
        help="Require the strongest current e_evt floor, even if this narrows to a single anchor.",
    )
    anchor_route_selector_parser.add_argument(
        "--require-best-z-art-floor",
        action="store_true",
        help="Require the strongest current z_art floor when budget allows.",
    )

    final_comparison_parser = subparsers.add_parser(
        "compare-offline-mvp-final-experiments",
        help="Compare final experiment metrics and optionally contextualize them with a selected route anchor.",
    )
    final_comparison_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    final_comparison_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_final_experiment_comparison"),
        help="Directory for final experiment comparison outputs.",
    )
    final_comparison_parser.add_argument(
        "--route-selection",
        type=Path,
        default=None,
        help="Optional selector json used to mark and compare against the chosen route anchor.",
    )

    route_recap_parser = subparsers.add_parser(
        "recap-offline-mvp-route-context",
        help="Generate a route-aware recap summary for experiment review or phase handoff.",
    )
    route_recap_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    route_recap_parser.add_argument(
        "--route-selection",
        type=Path,
        required=True,
        help="Selector json used to define the current route anchor.",
    )
    route_recap_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_recap"),
        help="Directory for route recap outputs.",
    )

    route_handoff_parser = subparsers.add_parser(
        "build-offline-mvp-route-handoff",
        help="Generate a copy-ready route-aware handoff summary for the current anchor route.",
    )
    route_handoff_parser.add_argument(
        "--experiment-metrics",
        type=Path,
        nargs="+",
        required=True,
        help="Two or more experiment metrics json files containing target_special_eval_model and ablation_eval.",
    )
    route_handoff_parser.add_argument(
        "--route-selection",
        type=Path,
        required=True,
        help="Selector json used to define the current route anchor.",
    )
    route_handoff_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/eval/offline_mvp_route_handoff"),
        help="Directory for route handoff outputs.",
    )
    route_handoff_parser.add_argument(
        "--stage-label",
        default=None,
        help="Optional stage label to place in the handoff summary.",
    )

    handoff_doc_parser = subparsers.add_parser(
        "materialize-offline-mvp-route-handoff-doc",
        help="Materialize a fixed-format handoff document from a route_handoff json summary.",
    )
    handoff_doc_parser.add_argument(
        "--route-handoff",
        type=Path,
        required=True,
        help="Path to route_handoff.json generated by build-offline-mvp-route-handoff.",
    )
    handoff_doc_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/handoffs/offline_mvp_route_handoff_doc"),
        help="Directory for the fixed-format handoff document outputs.",
    )
    handoff_doc_parser.add_argument(
        "--template-path",
        type=Path,
        default=Path("reports/templates/offline_mvp_handoff_document_template.md"),
        help="Markdown template path for the fixed-format handoff document.",
    )
    handoff_doc_parser.add_argument(
        "--title",
        default=None,
        help="Optional title override for the materialized handoff document.",
    )

    stage_report_parser = subparsers.add_parser(
        "materialize-offline-mvp-stage-report",
        help="Materialize a fixed-format stage report from a handoff_document json payload.",
    )
    stage_report_parser.add_argument(
        "--handoff-document",
        type=Path,
        required=True,
        help="Path to handoff_document.json generated by materialize-offline-mvp-route-handoff-doc.",
    )
    stage_report_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/stage_reports/offline_mvp_stage_report"),
        help="Directory for the fixed-format stage report outputs.",
    )
    stage_report_parser.add_argument(
        "--template-path",
        type=Path,
        default=Path("reports/templates/offline_mvp_stage_report_template.md"),
        help="Markdown template path for the fixed-format stage report.",
    )
    stage_report_parser.add_argument(
        "--title",
        default=None,
        help="Optional title override for the materialized stage report.",
    )

    event_target_analysis_parser = subparsers.add_parser(
        "analyze-offline-mvp-event-targets",
        help="Analyze current heuristic event targets for imbalance, redundancy, and target/source mismatch.",
    )
    event_target_analysis_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1/splits/hybrid_stratified_blocked"),
        help="Directory containing the materialized split manifests.",
    )
    event_target_analysis_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/data/offline_mvp_event_targets"),
        help="Directory for event-target analysis outputs.",
    )
    event_target_analysis_parser.add_argument(
        "--max-audio-sec",
        type=float,
        default=2.0,
        help="Maximum per-record audio duration used for the analysis.",
    )

    b1_inventory_parser = subparsers.add_parser(
        "build-b1-supervision-inventory",
        help="Build the round1 route-B supervision inventory and sidecar files.",
    )
    b1_inventory_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1/splits/hybrid_stratified_blocked"),
        help="Directory containing the materialized split manifests.",
    )
    b1_inventory_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1/b1_supervision"),
        help="Directory for machine-readable supervision inventory sidecars.",
    )
    b1_inventory_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/b1_supervision_inventory"),
        help="Directory for supervision inventory reports.",
    )

    c1_hints_parser = subparsers.add_parser(
        "build-c1-weak-event-hints",
        help="Build target-side weak event hint sidecars from punctuation and lexical progress.",
    )
    c1_hints_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1/splits/hybrid_stratified_blocked"),
        help="Directory containing the materialized split manifests.",
    )
    c1_hints_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1/c1_weak_event_hints"),
        help="Directory for machine-readable weak event hint sidecars.",
    )
    c1_hints_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/c1_weak_event_hints"),
        help="Directory for weak event hint reports.",
    )
    c1_hints_parser.add_argument(
        "--frame-length",
        type=int,
        default=400,
        help="Frame length used to estimate frame-level boundary indices.",
    )
    c1_hints_parser.add_argument(
        "--hop-length",
        type=int,
        default=160,
        help="Hop length used to estimate frame-level boundary indices.",
    )

    event_semantic_sidecar_parser = subparsers.add_parser(
        "build-target-event-semantic-sidecar",
        help="Build a formal target-side semantic sidecar by separating lexical/structure semantics from heuristic frame event targets.",
    )
    event_semantic_sidecar_parser.add_argument(
        "--weak-event-hints-path",
        type=Path,
        default=Path("data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl"),
        help="Path to the target-side weak event hints sidecar.",
    )
    event_semantic_sidecar_parser.add_argument(
        "--target-supervision-inventory-path",
        type=Path,
        default=Path("data_prep/round1_1/b1_supervision/target_supervision_inventory.jsonl"),
        help="Path to the target-side supervision inventory jsonl.",
    )
    event_semantic_sidecar_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/target_event_semantic_sidecar"),
        help="Directory for machine-readable target event semantic sidecars.",
    )
    event_semantic_sidecar_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_1_target_event_semantic_sidecar"),
        help="Directory for target event semantic sidecar reports.",
    )

    event_timing_semantic_sidecar_parser = subparsers.add_parser(
        "build-target-event-timing-semantic-sidecar",
        help="Build a sparse frame/event-aware target semantic bridge sidecar from weak boundary/clause timing hints.",
    )
    event_timing_semantic_sidecar_parser.add_argument(
        "--weak-event-hints-path",
        type=Path,
        default=Path("data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl"),
        help="Path to the target-side weak event hints sidecar.",
    )
    event_timing_semantic_sidecar_parser.add_argument(
        "--target-event-semantic-sidecar-path",
        type=Path,
        default=Path("data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl"),
        help="Path to the utterance-level target event semantic sidecar jsonl.",
    )
    event_timing_semantic_sidecar_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/target_event_timing_semantic_sidecar"),
        help="Directory for machine-readable target event timing semantic sidecars.",
    )
    event_timing_semantic_sidecar_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_1_target_event_timing_semantic_sidecar"),
        help="Directory for target event timing semantic sidecar reports.",
    )
    event_timing_semantic_sidecar_parser.add_argument(
        "--boundary-half-width-frames",
        type=int,
        default=2,
        help="Half width for sparse boundary windows around weak boundary frame indices.",
    )

    paired_parallel_source_parity_parser = subparsers.add_parser(
        "build-paired-parallel-source-semantic-parity-sidecar",
        help="Build a source-side parity bootstrap semantic sidecar by transferring paired target semantic/timing assets onto source frame axes.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--pair-spec-path",
        type=Path,
        action="append",
        default=None,
        help="Paired source-to-target jsonl. Repeat this flag to include multiple pair-spec files.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--target-event-semantic-sidecar-path",
        type=Path,
        default=Path("data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl"),
        help="Path to the target-side utterance semantic sidecar jsonl.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--target-event-timing-semantic-sidecar-path",
        type=Path,
        default=Path("data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl"),
        help="Path to the target-side timing semantic sidecar jsonl.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar"),
        help="Directory for machine-readable source-side parity semantic sidecars.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar"),
        help="Directory for source-side parity semantic reports.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--frame-length",
        type=int,
        default=400,
        help="Frame length used for source-side frame-count estimation.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--hop-length",
        type=int,
        default=160,
        help="Hop length used for source-side frame-count estimation.",
    )
    paired_parallel_source_parity_parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Sample rate used for source-side frame-count estimation.",
    )

    special_supervision_parser = subparsers.add_parser(
        "analyze-round1-target-special-supervision",
        help="Build a target-side special-supervision blueprint from split manifests and weak event hints.",
    )
    special_supervision_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
        help="Directory containing the materialized target split manifests.",
    )
    special_supervision_parser.add_argument(
        "--weak-event-hints-path",
        type=Path,
        default=Path("data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl"),
        help="Path to the target-side weak event hints sidecar.",
    )
    special_supervision_parser.add_argument(
        "--data-output-dir",
        type=Path,
        default=Path("data_prep/round1_1/target_special_supervision"),
        help="Directory for machine-readable target special-supervision sidecars.",
    )
    special_supervision_parser.add_argument(
        "--report-output-dir",
        type=Path,
        default=Path("reports/data/round1_1_target_special_supervision"),
        help="Directory for target special-supervision reports.",
    )
    special_supervision_parser.add_argument(
        "--proxy-core-top-k",
        type=int,
        default=16,
        help="Number of highest-proximity train/validation records to keep in the core challenge proxy pool.",
    )
    special_supervision_parser.add_argument(
        "--proxy-relaxed-top-k",
        type=int,
        default=48,
        help="Number of highest-proximity train/validation records to keep in the relaxed challenge proxy pool.",
    )

    special_slice_alignment_parser = subparsers.add_parser(
        "analyze-offline-mvp-special-slice-alignment",
        help="Compare target_special_eval against train-side proxy cohorts and nearest records.",
    )
    special_slice_alignment_parser.add_argument(
        "--split-dir",
        type=Path,
        default=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
        help="Directory containing the materialized target split manifests.",
    )
    special_slice_alignment_parser.add_argument(
        "--weak-event-hints-path",
        type=Path,
        default=Path("data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl"),
        help="Path to the target-side weak event hints sidecar.",
    )
    special_slice_alignment_parser.add_argument(
        "--target-special-supervision-path",
        type=Path,
        default=Path("data_prep/round1_1/target_special_supervision/target_special_supervision_sidecar.jsonl"),
        help="Path to the target-side special supervision sidecar.",
    )
    special_slice_alignment_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/data/round1_1_special_slice_alignment"),
        help="Directory for special-slice alignment outputs.",
    )
    special_slice_alignment_parser.add_argument(
        "--top-nearest",
        type=int,
        default=16,
        help="Number of nearest target_train records to include in the diagnostic report.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan-data":
        scan_project_data(
            firefly_dir=args.firefly_dir,
            source_audio=args.source_audio,
            output_dir=args.output_dir,
            window_ms=args.window_ms,
        )
        return 0
    if args.command == "preprocess-data":
        run_preprocessing(
            firefly_dir=args.firefly_dir,
            source_audio=args.source_audio,
            config_path=args.config,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
        )
        return 0
    if args.command == "build-round1-manifests":
        round1_dir = args.round1_dir
        if round1_dir is None and (args.target_dir is None or args.source_dir is None):
            round1_dir = Path("data_prep/round1")
        build_round1_manifests(
            round1_dir=round1_dir,
            output_dir=args.output_dir,
            report_output_dir=args.report_output_dir,
            target_dir=args.target_dir,
            source_dir=args.source_dir,
        )
        return 0
    if args.command == "recover-round1-target-formats":
        recover_round1_target_formats(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            report_output_dir=args.report_output_dir,
            target_sample_rate=args.target_sample_rate,
            target_channels=args.target_channels,
            keep_no_text_voice_isolated=not args.include_no_text_voice,
        )
        return 0
    if args.command == "check-round1-data":
        check_round1_data(
            round1_dir=args.round1_dir,
            manifest_dir=args.manifest_dir,
            report_output_dir=args.report_output_dir,
        )
        return 0
    if args.command == "init-experiment":
        init_experiment_record(
            slug=args.slug,
            owner=args.owner,
            config_path=args.config_path,
            output_dir=args.output_dir,
            template_path=args.template_path,
            route_selection_path=args.route_selection,
        )
        return 0
    if args.command == "evaluate-round1-baseline":
        evaluate_round1_baseline(
            manifest_dir=args.manifest_dir,
            output_dir=args.output_dir,
            experiment_metrics_path=args.experiment_metrics,
            r_res_enabled=args.r_res_enabled,
        )
        return 0
    if args.command == "train-offline-mvp":
        prepare_offline_mvp_training(
            config_path=args.config,
            experiment_id=args.experiment_id,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
        )
        return 0
    if args.command == "prepare-streaming-student-stage":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        prepare_streaming_student_stage(
            config_path=args.config,
            output_dir=args.output_dir,
            experiment_id=args.experiment_id,
        )
        return 0
    if args.command == "build-streaming-student-calibration-assets":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        build_streaming_student_calibration_assets(
            config_path=args.config,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            split_dir=args.split_dir,
            target_duration_sec=args.target_duration_sec,
            max_records=args.max_records,
        )
        return 0
    if args.command == "build-streaming-student-eval-bridge":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        build_streaming_student_eval_bridge(
            config_path=args.config,
            output_dir=args.output_dir,
            split_dir=args.split_dir,
            calibration_asset_path=args.calibration_asset,
            batch_size=args.batch_size,
            max_records_per_slice=args.max_records_per_slice,
        )
        return 0
    if args.command == "estimate-streaming-student-calibration":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        estimate_streaming_student_calibration(
            config_path=args.config,
            calibration_records_path=args.calibration_records,
            calibration_template_path=args.calibration_template,
            output_path=args.output_path,
            report_output_dir=args.report_output_dir,
        )
        return 0
    if args.command == "build-streaming-student-teacher-labels":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        build_streaming_student_teacher_labels(
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            route_handoff_path=args.route_handoff,
            experiment_metrics_path=args.experiment_metrics,
            checkpoint_path=args.checkpoint,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            max_records_per_slice=args.max_records_per_slice,
            teacher_e_evt_bridge_mode=args.teacher_eevt_bridge_mode,
            teacher_e_evt_target_shaping_mode=args.teacher_eevt_target_shaping_mode,
        )
        return 0
    if args.command == "prepare-streaming-student-training-data":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        prepare_streaming_student_training_data(
            config_path=args.config,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
        )
        return 0
    if args.command == "prepare-streaming-student-paired-training-data":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        prepare_streaming_student_paired_training_data(
            config_path=args.config,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            train_pair_spec_path=args.train_pair_spec,
            validation_pair_spec_path=args.validation_pair_spec,
            batch_size=args.batch_size,
        )
        return 0
    if args.command == "prepare-streaming-student-supervision":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        prepare_streaming_student_supervision(
            config_path=args.config,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            use_teacher_confidence=not args.disable_teacher_confidence,
            loss_weight_overrides_path=args.loss_weight_overrides,
        )
        return 0
    if args.command == "run-streaming-student-training-step":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        run_streaming_student_training_step(
            config_path=args.config,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            max_grad_norm=args.max_grad_norm,
            experiment_id=args.experiment_id,
            use_teacher_confidence=not args.disable_teacher_confidence,
            loss_weight_overrides_path=args.loss_weight_overrides,
        )
        return 0
    if args.command == "run-streaming-student-training-loop":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        run_streaming_student_training_loop(
            config_path=args.config,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            validation_batch_size=args.validation_batch_size,
            num_steps=args.num_steps,
            validation_interval=args.validation_interval,
            checkpoint_interval=args.checkpoint_interval,
            validation_batches=args.validation_batches,
            validation_mode=args.validation_mode,
            learning_rate=args.learning_rate,
            max_grad_norm=args.max_grad_norm,
            experiment_id=args.experiment_id,
            use_teacher_confidence=not args.disable_teacher_confidence,
            loss_weight_overrides_path=args.loss_weight_overrides,
        )
        return 0
    if args.command == "evaluate-streaming-student-checkpoint":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        evaluate_streaming_student_checkpoint(
            checkpoint_path=args.checkpoint,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            include_special_eval=not args.skip_special_eval,
        )
        return 0
    if args.command == "select-streaming-student-best-checkpoint":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        select_streaming_student_best_checkpoint(
            checkpoint_paths=args.checkpoints,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            batch_size=args.batch_size,
            include_special_eval=not args.skip_special_eval,
        )
        return 0
    if args.command == "export-streaming-student-proxy-audio":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        export_streaming_student_proxy_audio(
            checkpoint_path=args.checkpoint,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            branch_label=args.branch_label,
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "export-streaming-student-downstream-control-packet":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        export_streaming_student_downstream_control_packet(
            checkpoint_path=args.checkpoint,
            output_dir=args.output_dir,
            teacher_label_index_path=args.teacher_label_index,
            calibration_asset_path=args.calibration_asset,
            split_dir=args.split_dir,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            branch_label=args.branch_label,
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "launch-audio-audit-gui":
        launch_audio_audit_gui(
            bundle_paths=list(args.bundle),
            output_dir=args.output_dir,
            auto_close_ms=args.auto_close_ms,
        )
        return 0
    if args.command == "analyze-stage5-low-activity-fragments":
        analyze_stage5_low_activity_fragments(
            bundle_paths=list(args.bundle),
            output_dir=args.output_dir,
            analysis_audio_sources=list(args.analysis_audio_sources),
            target_activity_threshold=args.target_activity_threshold,
            candidate_activity_threshold=args.candidate_activity_threshold,
            min_low_activity_frames=args.min_low_activity_frames,
            top_k_windows=args.top_k_windows,
            window_padding_sec=args.window_padding_sec,
            min_audit_window_sec=args.min_audit_window_sec,
            max_audit_window_sec=args.max_audit_window_sec,
        )
        return 0
    if args.command == "average-offline-mvp-checkpoints":
        average_offline_mvp_checkpoints(
            checkpoint_paths=args.checkpoints,
            output_dir=args.output_dir,
            output_name=args.output_name,
        )
        return 0
    if args.command == "analyze-round1-splits":
        analyze_round1_split_options(
            manifest_dir=args.manifest_dir,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "materialize-round1-split":
        materialize_round1_split(
            manifest_dir=args.manifest_dir,
            option_path=args.option_path,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "evaluate-round1-special-eval":
        evaluate_round1_special_eval(
            split_dir=args.split_dir,
            output_dir=args.output_dir,
            experiment_metrics_path=args.experiment_metrics,
        )
        return 0
    if args.command == "evaluate-offline-mvp-special-eval":
        evaluate_offline_mvp_special_eval(
            config_path=args.config,
            split_dir=args.split_dir,
            output_dir=args.output_dir,
            experiment_metrics_path=args.experiment_metrics,
            checkpoint_path=args.checkpoint,
        )
        return 0
    if args.command == "evaluate-offline-mvp-ablations":
        evaluate_offline_mvp_ablations(
            config_path=args.config,
            split_dir=args.split_dir,
            output_dir=args.output_dir,
            experiment_metrics_path=args.experiment_metrics,
            checkpoint_path=args.checkpoint,
        )
        return 0
    if args.command == "evaluate-offline-mvp-checkpoint-series":
        evaluate_offline_mvp_checkpoint_series(
            config_path=args.config,
            experiment_metrics_path=args.experiment_metrics,
            output_dir=args.output_dir,
            split_dir=args.split_dir,
        )
        return 0
    if args.command == "evaluate-offline-mvp-special-eval-series":
        evaluate_offline_mvp_special_eval_series(
            config_path=args.config,
            experiment_metrics_path=args.experiment_metrics,
            output_dir=args.output_dir,
            split_dir=args.split_dir,
            steps=args.steps,
        )
        return 0
    if args.command == "export-offline-mvp-proxy-audio":
        export_offline_mvp_proxy_audio(
            config_path=args.config,
            split_dir=args.split_dir,
            output_dir=args.output_dir,
            experiment_metrics_path=args.experiment_metrics,
            checkpoint_path=args.checkpoint,
            source_manifest_path=args.source_manifest,
            source_record_ids=args.source_record_ids,
            sample_count=args.sample_count,
            branch_label=args.branch_label,
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "run-offline-mvp-teacher-runtime":
        run_offline_mvp_teacher_runtime(
            input_audio_path=args.input_audio,
            output_dir=args.output_dir,
            route_handoff_path=args.route_handoff,
            checkpoint_path=args.checkpoint,
            chunk_samples=args.chunk_samples,
            chunk_ms=args.chunk_ms,
            device=args.device,
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "export-offline-mvp-teacher-downstream-contract":
        export_offline_mvp_teacher_downstream_contract(
            input_audio_path=args.input_audio,
            output_dir=args.output_dir,
            route_handoff_path=args.route_handoff,
            checkpoint_path=args.checkpoint,
            calibration_asset_path=args.calibration_asset,
            chunk_samples=args.chunk_samples,
            chunk_ms=args.chunk_ms,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            teacher_e_evt_bridge_mode=args.teacher_eevt_bridge_mode,
            teacher_e_evt_target_shaping_mode=args.teacher_eevt_target_shaping_mode,
        )
        return 0
    if args.command == "audit-source-acoustic-state":
        audit_source_acoustic_state_extraction(
            input_audio_paths=list(args.input_audio),
            output_dir=args.output_dir,
            route_handoff_path=args.route_handoff,
            checkpoint_path=args.checkpoint,
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "build-offline-mvp-teacher-vocoder-input-scaffold":
        build_offline_mvp_teacher_vocoder_input_scaffold(
            contract_path=args.contract,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "run-offline-mvp-teacher-first-vc-demo":
        run_offline_mvp_teacher_first_vc_demo(
            input_audio_path=args.input_audio,
            output_dir=args.output_dir,
            teacher_route_handoff_path=args.teacher_route_handoff,
            teacher_checkpoint_path=args.teacher_checkpoint,
            calibration_asset_path=args.calibration_asset,
            vocoder_checkpoint_path=args.vocoder_checkpoint,
            vocoder_checkpoint_selection_path=args.vocoder_checkpoint_selection,
            selection_target=args.selection_target,
            chunk_samples=args.chunk_samples,
            chunk_ms=args.chunk_ms,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            save_intermediates=bool(args.save_intermediates),
            use_predicted_activity_gate=bool(args.use_predicted_activity_gate),
            predicted_activity_gate_floor=args.predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=args.predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
            reference_package_paths=list(args.reference_package_list),
            reference_package_limit=int(args.reference_package_limit),
            normalization_strategy=str(args.normalization_strategy),
            control_family_overrides=list(args.control_family_overrides),
        )
        return 0
    if args.command == "self-check-offline-mvp-teacher-first-vc-demo":
        run_teacher_first_vc_demo_self_check(
            input_audio_path=args.input_audio,
            output_dir=args.output_dir,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "build-offline-mvp-teacher-first-vc-review-bundle":
        build_teacher_first_vc_review_bundle(
            output_dir=args.output_dir,
            input_audio_paths=list(args.input_audio_list),
            input_spec_jsonl_path=args.input_spec_jsonl,
            device=args.device,
            max_audio_sec_default=args.max_audio_sec_default,
            save_intermediates=bool(args.save_intermediates),
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            chunk_ms=args.chunk_ms,
        )
        return 0
    if args.command == "build-offline-mvp-teacher-first-vc-audible-smoke-bundle":
        build_teacher_first_vc_audible_smoke_bundle(
            output_dir=args.output_dir,
            input_audio_paths=list(args.input_audio_list),
            input_spec_jsonl_path=args.input_spec_jsonl,
            device=args.device,
            max_audio_sec_default=args.max_audio_sec_default,
            save_intermediates=bool(args.save_intermediates),
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            chunk_ms=args.chunk_ms,
            calibration_asset_path=args.calibration_asset,
            target_reference_audio_path=args.target_reference_audio,
            target_reference_max_audio_sec=args.target_reference_max_audio_sec,
        )
        return 0
    if args.command == "build-offline-mvp-teacher-first-vc-audible-compare-bundle":
        build_teacher_first_vc_audible_compare_bundle(
            output_dir=args.output_dir,
            input_audio_paths=list(args.input_audio_list),
            input_spec_jsonl_path=args.input_spec_jsonl,
            device=args.device,
            max_audio_sec_default=args.max_audio_sec_default,
            save_intermediates=bool(args.save_intermediates),
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            chunk_ms=args.chunk_ms,
            calibration_asset_path=args.calibration_asset,
            target_reference_audio_path=args.target_reference_audio,
            target_reference_max_audio_sec=args.target_reference_max_audio_sec,
            vocoder_spec_jsonl_path=args.vocoder_spec_jsonl,
        )
        return 0
    if args.command == "analyze-offline-mvp-teacher-first-vc-applicability":
        analyze_teacher_first_vc_applicability(
            input_audio_paths=list(args.input_audio_list),
            output_dir=args.output_dir,
            reference_package_paths=list(args.reference_package_list),
            reference_package_limit=args.reference_package_limit,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
            chunk_ms=args.chunk_ms,
        )
        return 0
    if args.command == "analyze-offline-mvp-teacher-first-vc-decoder-behavior":
        analyze_teacher_first_vc_decoder_behavior(
            input_audio_paths=list(args.input_audio_list),
            output_dir=args.output_dir,
            reference_package_paths=list(args.reference_package_list),
            reference_package_limit=args.reference_package_limit,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
            chunk_ms=args.chunk_ms,
            use_predicted_activity_gate=bool(args.use_predicted_activity_gate),
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
            normalization_strategy=args.normalization_strategy,
            control_family_overrides=list(args.control_family_overrides),
        )
        return 0
    if args.command == "prepare-offline-mvp-nores-vocoder-scaffold":
        prepare_offline_mvp_nores_vocoder_scaffold(
            scaffold_path=args.input_scaffold,
            output_dir=args.output_dir,
            hidden_dim=args.hidden_dim,
            harmonic_bins=args.harmonic_bins,
            noise_bins=args.noise_bins,
        )
        return 0
    if args.command == "build-offline-mvp-nores-vocoder-train-targets":
        build_offline_mvp_nores_vocoder_training_package(
            scaffold_path=args.input_scaffold,
            target_audio_path=args.target_audio,
            output_dir=args.output_dir,
            harmonic_bins=args.harmonic_bins,
            noise_bins=args.noise_bins,
            sample_rate=args.sample_rate,
            frame_length=args.frame_length,
            hop_length=args.hop_length,
            target_contract_mode=args.target_contract_mode,
        )
        return 0
    if args.command == "run-offline-mvp-nores-vocoder-train-step":
        run_offline_mvp_nores_vocoder_training_step(
            training_package_path=args.train_targets,
            output_dir=args.output_dir,
            device=args.device,
            seed=args.seed,
            deterministic=bool(args.deterministic),
            hidden_dim=args.hidden_dim,
            learning_rate=args.learning_rate,
            max_grad_norm=args.max_grad_norm,
            harmonic_weight=args.harmonic_weight,
            noise_weight=args.noise_weight,
            periodic_gate_weight=args.periodic_gate_weight,
            noise_gate_weight=args.noise_gate_weight,
            activity_gate_weight=args.activity_gate_weight,
            waveform_weight=args.waveform_weight,
            stft_weight=args.stft_weight,
            rms_guard_weight=args.rms_guard_weight,
            active_template_weight=args.active_template_weight,
            frame_delta_weight=args.frame_delta_weight,
            frame_spectral_flux_zero_target_jitter_weight=args.frame_spectral_flux_zero_target_jitter_weight,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            reconstruction_frame_gain_apply_mode=args.reconstruction_frame_gain_apply_mode,
            decoder_branch_mean_mix_alpha=args.decoder_branch_mean_mix_alpha,
            fusion_mode=args.fusion_mode,
            waveform_decoder_mode=args.waveform_decoder_mode,
            use_decoder_branch_condition_adapter=bool(args.use_decoder_branch_condition_adapter),
            use_residual_shape_branch_condition_adapter=bool(args.use_residual_shape_branch_condition_adapter),
            periodic_waveform_frame_delta_weight=args.periodic_waveform_frame_delta_weight,
            periodic_waveform_frame_adjacent_cosine_weight=args.periodic_waveform_frame_adjacent_cosine_weight,
            periodic_waveform_frame_rms_floor_weight=args.periodic_waveform_frame_rms_floor_weight,
            periodic_waveform_stft_weight=args.periodic_waveform_stft_weight,
            periodic_waveform_high_band_excess_weight=args.periodic_waveform_high_band_excess_weight,
            multires_stft_short_weight=args.multires_stft_short_weight,
        )
        return 0
    if args.command == "run-offline-mvp-nores-vocoder-training-loop":
        run_offline_mvp_nores_vocoder_training_loop(
            training_package_path=args.train_targets,
            output_dir=args.output_dir,
            validation_package_path=args.validation_targets,
            device=args.device,
            seed=args.seed,
            deterministic=bool(args.deterministic),
            num_steps=args.num_steps,
            validation_interval=args.validation_interval,
            checkpoint_interval=args.checkpoint_interval,
            hidden_dim=args.hidden_dim,
            learning_rate=args.learning_rate,
            max_grad_norm=args.max_grad_norm,
            harmonic_weight=args.harmonic_weight,
            noise_weight=args.noise_weight,
            periodic_gate_weight=args.periodic_gate_weight,
            noise_gate_weight=args.noise_gate_weight,
            activity_gate_weight=args.activity_gate_weight,
            waveform_weight=args.waveform_weight,
            stft_weight=args.stft_weight,
            rms_guard_weight=args.rms_guard_weight,
            active_template_weight=args.active_template_weight,
            frame_delta_weight=args.frame_delta_weight,
            frame_spectral_flux_zero_target_jitter_weight=args.frame_spectral_flux_zero_target_jitter_weight,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            reconstruction_frame_gain_apply_mode=args.reconstruction_frame_gain_apply_mode,
            decoder_branch_mean_mix_alpha=args.decoder_branch_mean_mix_alpha,
            fusion_mode=args.fusion_mode,
            waveform_decoder_mode=args.waveform_decoder_mode,
            use_decoder_branch_condition_adapter=bool(args.use_decoder_branch_condition_adapter),
            use_residual_shape_branch_condition_adapter=bool(args.use_residual_shape_branch_condition_adapter),
            periodic_waveform_frame_delta_weight=args.periodic_waveform_frame_delta_weight,
            periodic_waveform_frame_adjacent_cosine_weight=args.periodic_waveform_frame_adjacent_cosine_weight,
            periodic_waveform_frame_rms_floor_weight=args.periodic_waveform_frame_rms_floor_weight,
            periodic_waveform_stft_weight=args.periodic_waveform_stft_weight,
            periodic_waveform_high_band_excess_weight=args.periodic_waveform_high_band_excess_weight,
            multires_stft_short_weight=args.multires_stft_short_weight,
        )
        return 0
    if args.command == "build-offline-mvp-nores-vocoder-dataset-packages":
        build_offline_mvp_nores_vocoder_dataset_packages(
            train_split_path=args.train_split,
            validation_split_path=args.validation_split,
            train_pair_spec_path=args.train_pair_spec,
            validation_pair_spec_path=args.validation_pair_spec,
            output_dir=args.output_dir,
            route_handoff_path=args.route_handoff,
            checkpoint_path=args.checkpoint,
            calibration_asset_path=args.calibration_asset,
            chunk_samples=args.chunk_samples,
            chunk_ms=args.chunk_ms,
            device=args.device,
            max_audio_sec=args.max_audio_sec,
            verify_against_full_pass=not bool(args.skip_full_pass_verify),
            max_train_records=args.max_train_records,
            max_validation_records=args.max_validation_records,
            selection_mode=args.selection_mode,
            skip_existing=bool(args.skip_existing),
            worker_processes=args.worker_processes,
            target_event_semantic_sidecar_path=args.target_event_semantic_sidecar,
            target_event_timing_semantic_sidecar_path=args.target_event_timing_semantic_sidecar,
            source_semantic_parity_sidecar_path=args.source_semantic_parity_sidecar,
            semantic_consumer_mode=args.semantic_consumer_mode,
            target_contract_mode=args.target_contract_mode,
            spectral_target_mode=args.spectral_target_mode,
            teacher_e_evt_bridge_mode=args.teacher_eevt_bridge_mode,
            teacher_e_evt_target_shaping_mode=args.teacher_eevt_target_shaping_mode,
        )
        return 0
    if args.command == "run-offline-mvp-nores-vocoder-dataset-training-loop":
        run_offline_mvp_nores_vocoder_dataset_training_loop(
            dataset_index_path=args.dataset_index,
            output_dir=args.output_dir,
            device=args.device,
            num_steps=args.num_steps,
            packages_per_step=args.packages_per_step,
            validation_interval=args.validation_interval,
            checkpoint_interval=args.checkpoint_interval,
            sampler_mode=args.sampler_mode,
            seed=args.seed,
            deterministic=bool(args.deterministic),
            hidden_dim=args.hidden_dim,
            learning_rate=args.learning_rate,
            max_grad_norm=args.max_grad_norm,
            harmonic_weight=args.harmonic_weight,
            noise_weight=args.noise_weight,
            periodic_gate_weight=args.periodic_gate_weight,
            noise_gate_weight=args.noise_gate_weight,
            activity_gate_weight=args.activity_gate_weight,
            waveform_weight=args.waveform_weight,
            stft_weight=args.stft_weight,
            rms_guard_weight=args.rms_guard_weight,
            active_template_weight=args.active_template_weight,
            frame_delta_weight=args.frame_delta_weight,
            frame_adjacent_cosine_weight=args.frame_adjacent_cosine_weight,
            frame_spectral_flux_zero_target_jitter_weight=args.frame_spectral_flux_zero_target_jitter_weight,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            reconstruction_frame_gain_apply_mode=args.reconstruction_frame_gain_apply_mode,
            fused_hidden_template_weight=args.fused_hidden_template_weight,
            fused_hidden_delta_weight=args.fused_hidden_delta_weight,
            fused_hidden_branch_mean_weight=args.fused_hidden_branch_mean_weight,
            decoder_branch_mean_mix_alpha=args.decoder_branch_mean_mix_alpha,
            fusion_mode=args.fusion_mode,
            waveform_decoder_mode=args.waveform_decoder_mode,
            use_decoder_branch_condition_adapter=bool(args.use_decoder_branch_condition_adapter),
            use_residual_shape_branch_condition_adapter=bool(args.use_residual_shape_branch_condition_adapter),
            periodic_waveform_frame_delta_weight=args.periodic_waveform_frame_delta_weight,
            periodic_waveform_frame_adjacent_cosine_weight=args.periodic_waveform_frame_adjacent_cosine_weight,
            periodic_waveform_frame_rms_floor_weight=args.periodic_waveform_frame_rms_floor_weight,
            periodic_waveform_stft_weight=args.periodic_waveform_stft_weight,
            periodic_waveform_high_band_excess_weight=args.periodic_waveform_high_band_excess_weight,
            multires_stft_short_weight=args.multires_stft_short_weight,
            semantic_supervision_enabled=bool(args.semantic_supervision_enabled),
        )
        return 0
    if args.command == "review-offline-mvp-nores-vocoder-checkpoints":
        review_offline_mvp_nores_vocoder_checkpoints(
            summary_path=args.summary,
            output_dir=args.output_dir,
            top_k=args.top_k,
        )
        return 0
    if args.command == "select-offline-mvp-nores-vocoder-checkpoint":
        select_offline_mvp_nores_vocoder_checkpoint(
            summary_path=args.summary,
            output_dir=args.output_dir,
            late_step_ratio=args.late_step_ratio,
            validation_guard_ratio=args.validation_guard_ratio,
            max_pairwise_worsened_ratio=args.max_pairwise_worsened_ratio,
            max_rms_ratio_deviation=args.max_rms_ratio_deviation,
            low_activity_probe_path=args.low_activity_probe,
            low_activity_audio_source=args.low_activity_audio_source,
            low_activity_soft_validation_ratio=args.low_activity_soft_validation_ratio,
        )
        return 0
    if args.command == "export-offline-mvp-nores-vocoder-audio":
        export_offline_mvp_nores_vocoder_audio(
            output_dir=args.output_dir,
            checkpoint_path=args.checkpoint,
            checkpoint_selection_path=args.checkpoint_selection,
            dataset_index_path=args.dataset_index,
            selection_target=args.selection_target,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            audit_carrier_frequency=args.audit_carrier_frequency,
            listening_audio_source=args.listening_audio_source,
            pitch_match_reference=args.pitch_match_reference,
            pitch_match_fmin_hz=args.pitch_match_fmin_hz,
            pitch_match_fmax_hz=args.pitch_match_fmax_hz,
            pitch_match_max_semitones=args.pitch_match_max_semitones,
            activity_gate_weight=args.activity_gate_weight,
            active_template_weight=args.active_template_weight,
            frame_delta_weight=args.frame_delta_weight,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            predicted_activity_gate_floor=args.predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=args.predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
            decoder_branch_mean_mix_alpha=args.decoder_branch_mean_mix_alpha,
        )
        return 0
    if args.command == "build-streaming-student-stage5-dataset-packages":
        require_student_route_explicit_ack(
            args.command,
            args.allow_student_line_while_teacher_unsatisfied,
        )
        build_streaming_student_stage5_dataset_packages(
            packet_export_path=args.packet_export,
            output_dir=args.output_dir,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            semantic_consumer_mode=args.semantic_consumer_mode,
            target_contract_mode=args.target_contract_mode,
            noise_event_family=args.noise_event_family,
            skip_existing=args.skip_existing,
        )
        return 0
    if args.command == "analyze-stage5-nores-speech-emergence":
        analyze_stage5_nores_speech_emergence(
            output_dir=args.output_dir,
            checkpoint_path=args.checkpoint,
            checkpoint_selection_path=args.checkpoint_selection,
            selection_target=args.selection_target,
            dataset_index_path=args.dataset_index,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            device=args.device,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            predicted_activity_gate_floor=args.predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=args.predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
        )
        return 0
    if args.command == "analyze-stage5-nores-waveform-decoder-structure":
        analyze_stage5_nores_waveform_decoder_structure(
            output_dir=args.output_dir,
            checkpoint_path=args.checkpoint,
            checkpoint_selection_path=args.checkpoint_selection,
            selection_target=args.selection_target,
            dataset_index_path=args.dataset_index,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            device=args.device,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            predicted_activity_gate_floor=args.predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=args.predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
        )
        return 0
    if args.command == "analyze-stage5-nores-waveform-objective-collapse":
        analyze_stage5_nores_waveform_objective_collapse(
            output_dir=args.output_dir,
            checkpoint_path=args.checkpoint,
            checkpoint_selection_path=args.checkpoint_selection,
            selection_target=args.selection_target,
            dataset_index_path=args.dataset_index,
            split_name=args.split_name,
            sample_count=args.sample_count,
            target_record_ids=args.target_record_ids,
            device=args.device,
            use_predicted_activity_gate=args.use_predicted_activity_gate,
            predicted_activity_gate_floor=args.predicted_activity_gate_floor,
            predicted_activity_gate_smoothing_frames=args.predicted_activity_gate_smoothing_frames,
            predicted_activity_gate_apply_mode=args.predicted_activity_gate_apply_mode,
            waveform_weight=args.waveform_weight,
            stft_weight=args.stft_weight,
            rms_guard_weight=args.rms_guard_weight,
        )
        return 0
    if args.command == "analyze-offline-mvp-nores-vocoder-low-activity-sensitivity":
        analyze_offline_mvp_nores_vocoder_low_activity_sensitivity(
            checkpoint_selection_path=args.checkpoint_selection,
            output_dir=args.output_dir,
            weight_step=args.weight_step,
        )
        return 0
    if args.command == "materialize-stage5-low-activity-governance-report":
        materialize_stage5_low_activity_governance_report(
            checkpoint_selection_path=args.checkpoint_selection,
            output_dir=args.output_dir,
            template_path=args.template,
            title=args.title,
        )
        return 0
    if args.command == "materialize-stage5-low-activity-audit-result-report":
        materialize_stage5_low_activity_audit_result_report(
            audio_audit_review_path=args.audio_audit_review,
            governance_report_path=args.governance_report,
            output_dir=args.output_dir,
            template_path=args.template,
            title=args.title,
        )
        return 0
    if args.command == "register-ai-work-session":
        register_ai_work_session(
            session_id=args.session_id,
            owner=args.owner,
            lane=args.lane,
            status=args.status,
            objective=args.objective,
            output_dir=args.output_dir,
            write_roots=list(args.write_root),
            read_roots=list(args.read_root),
            handoff_docs=list(args.handoff_doc),
            depends_on=list(args.depends_on),
            notes=list(args.note),
        )
        return 0
    if args.command == "materialize-ai-work-session-index":
        materialize_ai_work_session_index(
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "analyze-offline-mvp-checkpoint-selection":
        analyze_offline_mvp_checkpoint_selection(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
            late_step_ratio=args.late_step_ratio,
            validation_guard_ratio=args.validation_guard_ratio,
            min_positive_control_delta=args.min_positive_control_delta,
        )
        return 0
    if args.command == "materialize-offline-mvp-checkpoint-anchor":
        materialize_offline_mvp_checkpoint_anchor(
            experiment_metrics_path=args.experiment_metrics,
            step=args.step,
            output_path=args.output_path,
        )
        return 0
    if args.command == "build-offline-mvp-matched-horizon-shadow":
        build_offline_mvp_matched_horizon_shadow(
            experiment_metrics_paths=args.experiment_metrics,
            checkpoint_anchor_experiment_metrics_path=args.checkpoint_anchor_experiment_metrics,
            checkpoint_anchor_step=args.checkpoint_anchor_step,
            validation_budgets=args.validation_budgets,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "analyze-offline-mvp-checkpoint-gates":
        analyze_offline_mvp_checkpoint_gates(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
            late_step_ratio=args.late_step_ratio,
        )
        return 0
    if args.command == "analyze-offline-mvp-anchor-selection":
        analyze_offline_mvp_anchor_selection(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "analyze-offline-mvp-anchor-routes":
        analyze_offline_mvp_anchor_routes(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
        )
        return 0
    if args.command == "select-offline-mvp-anchor-route":
        select_offline_mvp_anchor_route(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
            max_validation_budget_over_best=args.max_validation_budget_over_best,
            special_priority=args.special_priority,
            z_art_priority=args.z_art_priority,
            require_best_e_evt_floor=args.require_best_e_evt_floor,
            require_best_z_art_floor=args.require_best_z_art_floor,
        )
        return 0
    if args.command == "compare-offline-mvp-final-experiments":
        compare_offline_mvp_final_experiments(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
            route_selection_path=args.route_selection,
        )
        return 0
    if args.command == "recap-offline-mvp-route-context":
        recap_offline_mvp_route_context(
            experiment_metrics_paths=args.experiment_metrics,
            output_dir=args.output_dir,
            route_selection_path=args.route_selection,
        )
        return 0
    if args.command == "build-offline-mvp-route-handoff":
        build_offline_mvp_route_handoff(
            experiment_metrics_paths=args.experiment_metrics,
            route_selection_path=args.route_selection,
            output_dir=args.output_dir,
            stage_label=args.stage_label,
        )
        return 0
    if args.command == "materialize-offline-mvp-route-handoff-doc":
        materialize_offline_mvp_route_handoff_doc(
            route_handoff_path=args.route_handoff,
            output_dir=args.output_dir,
            template_path=args.template_path,
            title=args.title,
        )
        return 0
    if args.command == "materialize-offline-mvp-stage-report":
        materialize_offline_mvp_stage_report(
            handoff_document_path=args.handoff_document,
            output_dir=args.output_dir,
            template_path=args.template_path,
            title=args.title,
        )
        return 0
    if args.command == "analyze-offline-mvp-event-targets":
        analyze_offline_mvp_event_targets(
            split_dir=args.split_dir,
            output_dir=args.output_dir,
            max_duration_sec=args.max_audio_sec,
        )
        return 0
    if args.command == "build-b1-supervision-inventory":
        build_b1_supervision_inventory(
            split_dir=args.split_dir,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
        )
        return 0
    if args.command == "build-c1-weak-event-hints":
        build_c1_weak_event_hints(
            split_dir=args.split_dir,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            frame_length=args.frame_length,
            hop_length=args.hop_length,
        )
        return 0
    if args.command == "build-target-event-semantic-sidecar":
        build_target_event_semantic_sidecar(
            weak_event_hints_path=args.weak_event_hints_path,
            target_supervision_inventory_path=args.target_supervision_inventory_path,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
        )
        return 0
    if args.command == "build-target-event-timing-semantic-sidecar":
        build_target_event_timing_semantic_sidecar(
            weak_event_hints_path=args.weak_event_hints_path,
            target_event_semantic_sidecar_path=args.target_event_semantic_sidecar_path,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            boundary_half_width_frames=args.boundary_half_width_frames,
        )
        return 0
    if args.command == "build-paired-parallel-source-semantic-parity-sidecar":
        build_paired_parallel_source_semantic_parity_sidecar(
            pair_spec_paths=[] if args.pair_spec_path is None else list(args.pair_spec_path),
            target_event_semantic_sidecar_path=args.target_event_semantic_sidecar_path,
            target_event_timing_semantic_sidecar_path=args.target_event_timing_semantic_sidecar_path,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            frame_length=args.frame_length,
            hop_length=args.hop_length,
            sample_rate=args.sample_rate,
        )
        return 0
    if args.command == "analyze-round1-target-special-supervision":
        analyze_round1_target_special_supervision(
            split_dir=args.split_dir,
            weak_event_hints_path=args.weak_event_hints_path,
            data_output_dir=args.data_output_dir,
            report_output_dir=args.report_output_dir,
            proxy_core_top_k=args.proxy_core_top_k,
            proxy_relaxed_top_k=args.proxy_relaxed_top_k,
        )
        return 0
    if args.command == "analyze-offline-mvp-special-slice-alignment":
        analyze_offline_mvp_special_slice_alignment(
            split_dir=args.split_dir,
            weak_event_hints_path=args.weak_event_hints_path,
            target_special_supervision_path=args.target_special_supervision_path,
            output_dir=args.output_dir,
            top_nearest=args.top_nearest,
        )
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
