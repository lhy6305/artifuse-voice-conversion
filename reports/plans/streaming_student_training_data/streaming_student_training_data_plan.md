# Stage3 Streaming Student Training Data Plan

- generated_at: 2026-03-17T12:20:27
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- frame_contract: {"frame_length": 400, "hop_length": 160, "r_res_enabled": false, "teacher_label_required_keys": ["teacher_hidden", "teacher_fused_hidden", "teacher_z_art", "teacher_event_logits", "teacher_event_probs", "teacher_acoustic", "teacher_frame_confidence"]}

## target_train
- record_count: 592
- dry_run_batch_size: 3
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11']
- waveform_shape: [3, 757858]
- teacher_shapes: {"teacher_hidden": [3, 4735, 64], "teacher_fused_hidden": [3, 4735, 64], "teacher_z_art": [3, 4735, 8], "teacher_event_logits": [3, 4735, 8], "teacher_acoustic": [3, 4735, 4], "teacher_frame_confidence": [3, 4735, 1]}
- student_shapes: {"shared_hidden": [3, 4735, 96], "z_art": [3, 4735, 8], "event_logits": [3, 4735, 8], "coarse_log_f0": [3, 4735, 1], "aperiodicity": [3, 4735, 1], "energy": [3, 4735, 1], "log_f0_correction": [3, 4735, 1], "aper_correction": [3, 4735, 1], "r_res": [3, 4735, 0]}
- conditioning_shapes: {"speaker_embedding": [3, 16], "geom_embedding": [3, 8], "alpha": [3, 1]}
- teacher_confidence: {"mean_of_means": 0.463185, "mean_low_confidence_frame_ratio": 0.417068}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [3054, 4735, 4364], "model_frame_lengths": [3054, 4735, 4364], "delta_per_sample": [0, 0, 0]}
- status: frame_contract_aligned

## target_validation
- record_count: 66
- dry_run_batch_size: 3
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116']
- waveform_shape: [3, 51508]
- teacher_shapes: {"teacher_hidden": [3, 320, 64], "teacher_fused_hidden": [3, 320, 64], "teacher_z_art": [3, 320, 8], "teacher_event_logits": [3, 320, 8], "teacher_acoustic": [3, 320, 4], "teacher_frame_confidence": [3, 320, 1]}
- student_shapes: {"shared_hidden": [3, 320, 96], "z_art": [3, 320, 8], "event_logits": [3, 320, 8], "coarse_log_f0": [3, 320, 1], "aperiodicity": [3, 320, 1], "energy": [3, 320, 1], "log_f0_correction": [3, 320, 1], "aper_correction": [3, 320, 1], "r_res": [3, 320, 0]}
- conditioning_shapes: {"speaker_embedding": [3, 16], "geom_embedding": [3, 8], "alpha": [3, 1]}
- teacher_confidence: {"mean_of_means": 0.524706, "mean_low_confidence_frame_ratio": 0.165288}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [167, 267, 320], "model_frame_lengths": [167, 267, 320], "delta_per_sample": [0, 0, 0]}
- status: frame_contract_aligned

## target_special_eval
- record_count: 8
- dry_run_batch_size: 3
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108']
- waveform_shape: [3, 93271]
- teacher_shapes: {"teacher_hidden": [3, 581, 64], "teacher_fused_hidden": [3, 581, 64], "teacher_z_art": [3, 581, 8], "teacher_event_logits": [3, 581, 8], "teacher_acoustic": [3, 581, 4], "teacher_frame_confidence": [3, 581, 1]}
- student_shapes: {"shared_hidden": [3, 581, 96], "z_art": [3, 581, 8], "event_logits": [3, 581, 8], "coarse_log_f0": [3, 581, 1], "aperiodicity": [3, 581, 1], "energy": [3, 581, 1], "log_f0_correction": [3, 581, 1], "aper_correction": [3, 581, 1], "r_res": [3, 581, 0]}
- conditioning_shapes: {"speaker_embedding": [3, 16], "geom_embedding": [3, 8], "alpha": [3, 1]}
- teacher_confidence: {"mean_of_means": 0.497748, "mean_low_confidence_frame_ratio": 0.137033}
- frame_alignment: {"all_equal": true, "teacher_frame_lengths": [128, 188, 581], "model_frame_lengths": [128, 188, 581], "delta_per_sample": [0, 0, 0]}
- status: frame_contract_aligned

## Notes
- This stage wires split records, sidecars, teacher-label assets, and conditioning assets into a reusable Stage3 batch contract.
- Current dry-run keeps full audio intact so the waveform-to-frame contract stays aligned with exported teacher labels.
- The output is a data-layer contract check, not a real Student training loop.

## Next Steps
- Use teacher_frame_confidence explicitly for weighting or filtering instead of treating it as an always-on final confidence target.
- Add Stage3 loss definitions on top of this batch contract without reusing offline_mvp training steps directly.
- Keep r_res disabled until the base Student supervision path is stable.
