# Stage3 Streaming Student Training Data Plan

- generated_at: 2026-03-24T21:59:02
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- frame_contract: {"frame_length": 400, "hop_length": 160, "r_res_enabled": false, "available_target_sidecars": ["weak_event_hints", "target_special_supervision", "target_event_semantic_sidecar"], "teacher_label_required_keys": ["teacher_hidden", "teacher_fused_hidden", "teacher_z_art", "teacher_event_logits", "teacher_event_probs", "teacher_acoustic", "teacher_frame_confidence"]}

## target_train
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::archive_firefly_1']
- waveform_shape: [1, 488980]
- teacher_shapes: {"teacher_hidden": [1, 3054, 64], "teacher_fused_hidden": [1, 3054, 64], "teacher_z_art": [1, 3054, 8], "teacher_event_logits": [1, 3054, 8], "teacher_acoustic": [1, 3054, 4], "teacher_frame_confidence": [1, 3054, 1]}
- student_shapes: {"shared_hidden": [1, 3054, 96], "z_art": [1, 3054, 8], "event_logits": [1, 3054, 8], "coarse_log_f0": [1, 3054, 1], "aperiodicity": [1, 3054, 1], "energy": [1, 3054, 1], "log_f0_correction": [1, 3054, 1], "aper_correction": [1, 3054, 1], "r_res": [1, 3054, 0]}
- conditioning_shapes: {"speaker_embedding": [1, 16], "geom_embedding": [1, 8], "alpha": [1, 1]}
- teacher_confidence: {"mean_of_means": 0.44205, "mean_low_confidence_frame_ratio": 0.483955}
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}, "semantic_utterance_structure_type_counts": {"multi_terminal": 1}}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [3054], "model_frame_lengths": [3054], "delta_per_sample": [0]}
- status: frame_contract_aligned

## target_validation
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::chapter3_3_firefly_162']
- waveform_shape: [1, 27033]
- teacher_shapes: {"teacher_hidden": [1, 167, 64], "teacher_fused_hidden": [1, 167, 64], "teacher_z_art": [1, 167, 8], "teacher_event_logits": [1, 167, 8], "teacher_acoustic": [1, 167, 4], "teacher_frame_confidence": [1, 167, 1]}
- student_shapes: {"shared_hidden": [1, 167, 96], "z_art": [1, 167, 8], "event_logits": [1, 167, 8], "coarse_log_f0": [1, 167, 1], "aperiodicity": [1, 167, 1], "energy": [1, 167, 1], "log_f0_correction": [1, 167, 1], "aper_correction": [1, 167, 1], "r_res": [1, 167, 0]}
- conditioning_shapes: {"speaker_embedding": [1, 16], "geom_embedding": [1, 8], "alpha": [1, 1]}
- teacher_confidence: {"mean_of_means": 0.542329, "mean_low_confidence_frame_ratio": 0.161677}
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}, "semantic_utterance_structure_type_counts": {"single_clause_terminal": 1}}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [167], "model_frame_lengths": [167], "delta_per_sample": [0]}
- status: frame_contract_aligned

## target_special_eval
- record_count: 1
- dry_run_batch_size: 1
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106']
- waveform_shape: [1, 20771]
- teacher_shapes: {"teacher_hidden": [1, 128, 64], "teacher_fused_hidden": [1, 128, 64], "teacher_z_art": [1, 128, 8], "teacher_event_logits": [1, 128, 8], "teacher_acoustic": [1, 128, 4], "teacher_frame_confidence": [1, 128, 1]}
- student_shapes: {"shared_hidden": [1, 128, 96], "z_art": [1, 128, 8], "event_logits": [1, 128, 8], "coarse_log_f0": [1, 128, 1], "aperiodicity": [1, 128, 1], "energy": [1, 128, 1], "log_f0_correction": [1, 128, 1], "aper_correction": [1, 128, 1], "r_res": [1, 128, 0]}
- conditioning_shapes: {"speaker_embedding": [1, 16], "geom_embedding": [1, 8], "alpha": [1, 1]}
- teacher_confidence: {"mean_of_means": 0.556913, "mean_low_confidence_frame_ratio": 0.039062}
- semantic_sidecar_summary: {"present_count": 1, "missing_count": 0, "semantic_contract_version_counts": {"target_event_semantic_sidecar_v1": 1}, "semantic_label_status_counts": {"pending_upgrade": 1}, "semantic_utterance_structure_type_counts": {"nonverbal": 1}}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [128], "model_frame_lengths": [128], "delta_per_sample": [0]}
- status: frame_contract_aligned

## Notes
- This stage wires split records, sidecars, teacher-label assets, and conditioning assets into a reusable Stage3 batch contract.
- Current dry-run keeps full audio intact so the waveform-to-frame contract stays aligned with exported teacher labels.
- The output is a data-layer contract check, not a real Student training loop.

## Next Steps
- Use teacher_frame_confidence explicitly for weighting or filtering instead of treating it as an always-on final confidence target.
- Add Stage3 loss definitions on top of this batch contract without reusing offline_mvp training steps directly.
- Keep r_res disabled until the base Student supervision path is stable.
