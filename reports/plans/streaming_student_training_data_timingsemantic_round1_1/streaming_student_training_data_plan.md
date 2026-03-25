# Stage3 Streaming Student Training Data Plan

- generated_at: 2026-03-25T21:07:47
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- frame_contract: {"frame_length": 400, "hop_length": 160, "r_res_enabled": false, "available_target_sidecars": ["weak_event_hints", "target_special_supervision", "target_event_semantic_sidecar", "target_event_timing_semantic_sidecar"], "teacher_label_required_keys": ["teacher_hidden", "teacher_fused_hidden", "teacher_z_art", "teacher_event_logits", "teacher_event_probs", "teacher_acoustic", "teacher_frame_confidence"]}

## target_train
- record_count: 592
- dry_run_batch_size: 4
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11', 'target::archive_firefly_12']
- waveform_shape: [4, 776997]
- teacher_shapes: {"teacher_hidden": [4, 4854, 64], "teacher_fused_hidden": [4, 4854, 64], "teacher_z_art": [4, 4854, 8], "teacher_event_logits": [4, 4854, 8], "teacher_acoustic": [4, 4854, 4], "teacher_frame_confidence": [4, 4854, 1]}
- student_shapes: {"shared_hidden": [4, 4854, 96], "z_art": [4, 4854, 8], "event_logits": [4, 4854, 8], "coarse_log_f0": [4, 4854, 1], "aperiodicity": [4, 4854, 1], "energy": [4, 4854, 1], "log_f0_correction": [4, 4854, 1], "aper_correction": [4, 4854, 1], "r_res": [4, 4854, 0]}
- conditioning_shapes: {"speaker_embedding": [4, 16], "geom_embedding": [4, 8], "alpha": [4, 1]}
- teacher_confidence: {"mean_of_means": 0.463398, "mean_low_confidence_frame_ratio": 0.416582}
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}, "semantic_utterance_structure_type_counts": {"multi_terminal": 3, "other": 1}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 4, "timing_pause_present_count": 4, "timing_terminal_present_count": 3}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [3054, 4735, 4364, 4854], "model_frame_lengths": [3054, 4735, 4364, 4854], "delta_per_sample": [0, 0, 0, 0]}
- status: frame_contract_aligned

## target_validation
- record_count: 66
- dry_run_batch_size: 4
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116', 'target::chapter3_3_firefly_207']
- waveform_shape: [4, 59975]
- teacher_shapes: {"teacher_hidden": [4, 373, 64], "teacher_fused_hidden": [4, 373, 64], "teacher_z_art": [4, 373, 8], "teacher_event_logits": [4, 373, 8], "teacher_acoustic": [4, 373, 4], "teacher_frame_confidence": [4, 373, 1]}
- student_shapes: {"shared_hidden": [4, 373, 96], "z_art": [4, 373, 8], "event_logits": [4, 373, 8], "coarse_log_f0": [4, 373, 1], "aperiodicity": [4, 373, 1], "energy": [4, 373, 1], "log_f0_correction": [4, 373, 1], "aper_correction": [4, 373, 1], "r_res": [4, 373, 0]}
- conditioning_shapes: {"speaker_embedding": [4, 16], "geom_embedding": [4, 8], "alpha": [4, 1]}
- teacher_confidence: {"mean_of_means": 0.535711, "mean_low_confidence_frame_ratio": 0.142733}
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}, "semantic_utterance_structure_type_counts": {"single_clause_terminal": 4}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 0, "timing_pause_present_count": 0, "timing_terminal_present_count": 4}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [167, 267, 320, 373], "model_frame_lengths": [167, 267, 320, 373], "delta_per_sample": [0, 0, 0, 0]}
- status: frame_contract_aligned

## target_special_eval
- record_count: 8
- dry_run_batch_size: 4
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108', 'target::no_text_voice/chapter3_22_firefly_115']
- waveform_shape: [4, 93271]
- teacher_shapes: {"teacher_hidden": [4, 581, 64], "teacher_fused_hidden": [4, 581, 64], "teacher_z_art": [4, 581, 8], "teacher_event_logits": [4, 581, 8], "teacher_acoustic": [4, 581, 4], "teacher_frame_confidence": [4, 581, 1]}
- student_shapes: {"shared_hidden": [4, 581, 96], "z_art": [4, 581, 8], "event_logits": [4, 581, 8], "coarse_log_f0": [4, 581, 1], "aperiodicity": [4, 581, 1], "energy": [4, 581, 1], "log_f0_correction": [4, 581, 1], "aper_correction": [4, 581, 1], "r_res": [4, 581, 0]}
- conditioning_shapes: {"speaker_embedding": [4, 16], "geom_embedding": [4, 8], "alpha": [4, 1]}
- teacher_confidence: {"mean_of_means": 0.496987, "mean_low_confidence_frame_ratio": 0.131536}
- semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 4}, "semantic_label_status_counts": {"pending_upgrade": 4}, "semantic_utterance_structure_type_counts": {"nonverbal": 4}}
- timing_semantic_sidecar_summary: {"present_count": 4, "missing_count": 0, "timing_contract_version_counts": {"target_event_timing_semantic_sidecar_v1": 4}, "timing_label_status_counts": {"pending_upgrade": 4}, "timing_alignment_type_counts": {"weak_punctuation_lexical_progress_v1": 4}, "timing_multi_clause_count": 0, "timing_pause_present_count": 0, "timing_terminal_present_count": 0}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [128, 188, 581, 226], "model_frame_lengths": [128, 188, 581, 226], "delta_per_sample": [0, 0, 0, 0]}
- status: frame_contract_aligned

## Notes
- This stage wires split records, sidecars, teacher-label assets, and conditioning assets into a reusable Stage3 batch contract.
- Current dry-run keeps full audio intact so the waveform-to-frame contract stays aligned with exported teacher labels.
- The output is a data-layer contract check, not a real Student training loop.

## Next Steps
- Use teacher_frame_confidence explicitly for weighting or filtering instead of treating it as an always-on final confidence target.
- Add Stage3 loss definitions on top of this batch contract without reusing offline_mvp training steps directly.
- Keep r_res disabled until the base Student supervision path is stable.
