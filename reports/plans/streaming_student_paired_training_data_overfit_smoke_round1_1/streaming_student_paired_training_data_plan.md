# Stage3 Paired Streaming Student Training Data Plan

- generated_at: 2026-03-25T21:41:50
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- frame_contract: {"record_mode": "paired_source_to_target_stage3_contract", "frame_length": 400, "hop_length": 160, "r_res_enabled": false, "available_source_sidecars": ["source_semantic_parity_sidecar"], "available_target_sidecars": ["target_event_timing_semantic_sidecar"], "teacher_label_required_keys": ["teacher_hidden", "teacher_fused_hidden", "teacher_z_art", "teacher_event_logits", "teacher_event_probs", "teacher_acoustic", "teacher_frame_confidence"]}
- split: {"record_mode": "paired_source_to_target_stage3_contract", "train_pair_spec_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl", "validation_pair_spec_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl", "target_event_timing_semantic_sidecar_path": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl", "source_semantic_parity_sidecar_path": null, "train_pair_count": 2, "validation_pair_count": 2}

## train
- record_count: 2
- dry_run_batch_size: 2
- sample_pair_record_ids: ['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- sample_source_record_ids: ['source::parallel/chapter3_17_firefly_107', 'source::parallel/chapter3_17_firefly_132']
- sample_target_record_ids: ['target::chapter3_17_firefly_107', 'target::chapter3_17_firefly_132']
- waveform_shape: [2, 105840]
- teacher_shapes: {"teacher_hidden": [2, 723, 64], "teacher_fused_hidden": [2, 723, 64], "teacher_z_art": [2, 723, 8], "teacher_event_logits": [2, 723, 8], "teacher_acoustic": [2, 723, 4], "teacher_frame_confidence": [2, 723, 1]}
- student_shapes: {"shared_hidden": [2, 660, 96], "z_art": [2, 660, 8], "event_logits": [2, 660, 8], "coarse_log_f0": [2, 660, 1], "aperiodicity": [2, 660, 1], "energy": [2, 660, 1], "log_f0_correction": [2, 660, 1], "aper_correction": [2, 660, 1], "r_res": [2, 660, 0]}
- conditioning_shapes: {"speaker_embedding": [2, 16], "geom_embedding": [2, 8], "alpha": [2, 1]}
- teacher_confidence: {"mean_of_means": 0.506963, "mean_low_confidence_frame_ratio": 0.259468}
- teacher_split_name_counts: {"target_train": 2}
- source_sample_rate_counts: {"44100": 2}
- source_semantic_parity_sidecar_summary: {"present_count": 0, "missing_count": 2, "semantic_ready_for_source_side_bootstrap_count": 0, "parity_contract_version_counts": {}, "parity_status_counts": {}, "semantic_label_status_counts": {}, "semantic_utterance_structure_type_counts": {}}
- source_parity_alignment: {"source_parity_duration_sec": [0.0, 0.0], "source_parity_estimated_frame_counts": [0, 0], "source_parity_duration_metadata_drift_sec": [-2.39, -2.4], "source_parity_frame_delta_per_sample": [657, 660], "source_parity_duration_metadata_drift_stats": {"count": 2, "min": -2.4, "max": -2.39, "mean": -2.395, "median": -2.395, "stdev": 0.005}, "source_parity_frame_delta_stats": {"count": 2, "min": 657, "max": 660, "mean": 658.5, "median": 658.5, "stdev": 1.5}}
- timing_semantic_sidecar_summary: {"present_count": 2, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 2}, "timing_label_status_counts": {"pending_upgrade": 2}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 2}, "timing_multi_clause_count": 1, "timing_pause_present_count": 1, "timing_terminal_present_count": 2}
- duration_alignment: {"source_audio_duration_sec_actual": [2.39, 2.4], "source_audio_duration_sec_pair_spec": [3.881224, 3.51873], "target_audio_duration_sec_actual": [2.62898, 2.519977], "target_audio_duration_sec_pair_spec": [2.62898, 2.519977], "source_to_target_duration_ratio": [0.909098, 0.95239], "source_duration_sec_stats_actual": {"count": 2, "min": 2.39, "max": 2.4, "mean": 2.395, "median": 2.395, "stdev": 0.005}, "source_duration_sec_stats_pair_spec": {"count": 2, "min": 3.51873, "max": 3.881224, "mean": 3.699977, "median": 3.699977, "stdev": 0.181247}, "target_duration_sec_stats_actual": {"count": 2, "min": 2.519977, "max": 2.62898, "mean": 2.574478, "median": 2.574478, "stdev": 0.054501}, "target_duration_sec_stats_pair_spec": {"count": 2, "min": 2.519977, "max": 2.62898, "mean": 2.574478, "median": 2.574478, "stdev": 0.054501}, "source_to_target_duration_ratio_stats": {"count": 2, "min": 0.909098, "max": 0.95239, "mean": 0.930744, "median": 0.930744, "stdev": 0.021646}, "source_duration_metadata_drift_sec": [1.491224, 1.11873], "target_duration_metadata_drift_sec": [0.0, 0.0], "source_duration_metadata_drift_stats": {"count": 2, "min": 1.11873, "max": 1.491224, "mean": 1.304977, "median": 1.304977, "stdev": 0.186247}, "target_duration_metadata_drift_stats": {"count": 2, "min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0, "stdev": 0.0}, "source_longer_than_target_count": 0}
- frame_alignment: {"all_equal": false, "teacher_frame_lengths": [723, 693], "model_frame_lengths": [657, 660], "delta_per_sample": [-66, -33], "abs_delta_stats": {"count": 2, "min": 33, "max": 66, "mean": 49.5, "median": 49.5, "stdev": 16.5}, "model_to_teacher_frame_ratio": [0.908714, 0.952381], "model_to_teacher_frame_ratio_stats": {"count": 2, "min": 0.908714, "max": 0.952381, "mean": 0.930548, "median": 0.930548, "stdev": 0.021834}, "model_longer_than_teacher_count": 0}
- status: paired_source_target_frame_contract_mismatch

## validation
- record_count: 2
- dry_run_batch_size: 2
- sample_pair_record_ids: ['paired::parallel_firefly_107_to_target_firefly_107', 'paired::parallel_firefly_132_to_target_firefly_132']
- sample_source_record_ids: ['source::parallel/chapter3_17_firefly_107', 'source::parallel/chapter3_17_firefly_132']
- sample_target_record_ids: ['target::chapter3_17_firefly_107', 'target::chapter3_17_firefly_132']
- waveform_shape: [2, 105840]
- teacher_shapes: {"teacher_hidden": [2, 723, 64], "teacher_fused_hidden": [2, 723, 64], "teacher_z_art": [2, 723, 8], "teacher_event_logits": [2, 723, 8], "teacher_acoustic": [2, 723, 4], "teacher_frame_confidence": [2, 723, 1]}
- student_shapes: {"shared_hidden": [2, 660, 96], "z_art": [2, 660, 8], "event_logits": [2, 660, 8], "coarse_log_f0": [2, 660, 1], "aperiodicity": [2, 660, 1], "energy": [2, 660, 1], "log_f0_correction": [2, 660, 1], "aper_correction": [2, 660, 1], "r_res": [2, 660, 0]}
- conditioning_shapes: {"speaker_embedding": [2, 16], "geom_embedding": [2, 8], "alpha": [2, 1]}
- teacher_confidence: {"mean_of_means": 0.506963, "mean_low_confidence_frame_ratio": 0.259468}
- teacher_split_name_counts: {"target_train": 2}
- source_sample_rate_counts: {"44100": 2}
- source_semantic_parity_sidecar_summary: {"present_count": 0, "missing_count": 2, "semantic_ready_for_source_side_bootstrap_count": 0, "parity_contract_version_counts": {}, "parity_status_counts": {}, "semantic_label_status_counts": {}, "semantic_utterance_structure_type_counts": {}}
- source_parity_alignment: {"source_parity_duration_sec": [0.0, 0.0], "source_parity_estimated_frame_counts": [0, 0], "source_parity_duration_metadata_drift_sec": [-2.39, -2.4], "source_parity_frame_delta_per_sample": [657, 660], "source_parity_duration_metadata_drift_stats": {"count": 2, "min": -2.4, "max": -2.39, "mean": -2.395, "median": -2.395, "stdev": 0.005}, "source_parity_frame_delta_stats": {"count": 2, "min": 657, "max": 660, "mean": 658.5, "median": 658.5, "stdev": 1.5}}
- timing_semantic_sidecar_summary: {"present_count": 2, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 2}, "timing_label_status_counts": {"pending_upgrade": 2}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 2}, "timing_multi_clause_count": 1, "timing_pause_present_count": 1, "timing_terminal_present_count": 2}
- duration_alignment: {"source_audio_duration_sec_actual": [2.39, 2.4], "source_audio_duration_sec_pair_spec": [3.881224, 3.51873], "target_audio_duration_sec_actual": [2.62898, 2.519977], "target_audio_duration_sec_pair_spec": [2.62898, 2.519977], "source_to_target_duration_ratio": [0.909098, 0.95239], "source_duration_sec_stats_actual": {"count": 2, "min": 2.39, "max": 2.4, "mean": 2.395, "median": 2.395, "stdev": 0.005}, "source_duration_sec_stats_pair_spec": {"count": 2, "min": 3.51873, "max": 3.881224, "mean": 3.699977, "median": 3.699977, "stdev": 0.181247}, "target_duration_sec_stats_actual": {"count": 2, "min": 2.519977, "max": 2.62898, "mean": 2.574478, "median": 2.574478, "stdev": 0.054501}, "target_duration_sec_stats_pair_spec": {"count": 2, "min": 2.519977, "max": 2.62898, "mean": 2.574478, "median": 2.574478, "stdev": 0.054501}, "source_to_target_duration_ratio_stats": {"count": 2, "min": 0.909098, "max": 0.95239, "mean": 0.930744, "median": 0.930744, "stdev": 0.021646}, "source_duration_metadata_drift_sec": [1.491224, 1.11873], "target_duration_metadata_drift_sec": [0.0, 0.0], "source_duration_metadata_drift_stats": {"count": 2, "min": 1.11873, "max": 1.491224, "mean": 1.304977, "median": 1.304977, "stdev": 0.186247}, "target_duration_metadata_drift_stats": {"count": 2, "min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0, "stdev": 0.0}, "source_longer_than_target_count": 0}
- frame_alignment: {"all_equal": false, "teacher_frame_lengths": [723, 693], "model_frame_lengths": [657, 660], "delta_per_sample": [-66, -33], "abs_delta_stats": {"count": 2, "min": 33, "max": 66, "mean": 49.5, "median": 49.5, "stdev": 16.5}, "model_to_teacher_frame_ratio": [0.908714, 0.952381], "model_to_teacher_frame_ratio_stats": {"count": 2, "min": 0.908714, "max": 0.952381, "mean": 0.930548, "median": 0.930548, "stdev": 0.021834}, "model_longer_than_teacher_count": 0}
- status: paired_source_target_frame_contract_mismatch

## Notes
- This paired Stage3 dry-run uses source waveform as Student input and target teacher labels as supervision assets.
- The goal is to quantify source-target duration and frame-count mismatch honestly before proposing any paired Stage3 training route.
- Current output is a contract audit, not a claim that source-side parity is already train-ready supervision.

## Next Steps
- If source model frames and target teacher frames mismatch materially, add an explicit source-target frame bridge instead of forcing direct supervision.
- Keep source_semantic_parity_sidecar attached by source_record_id only; do not remap it onto target ids.
- Do not start paired Stage3 training loops until this contract summary is accepted as the current ground truth.
