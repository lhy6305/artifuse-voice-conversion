# Stage3 Streaming Student Supervision Plan

- generated_at: 2026-03-17T16:15:53
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- loss_weights: {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.15, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}
- loss_weight_overrides_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_loss_weights_energyproxy_light_v1.json
- use_teacher_confidence: True

## target_train
- record_count: 592
- dry_run_batch_size: 3
- sample_record_ids: ['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11']
- loss_metrics: {"loss_total": 15.074208, "loss_total_default_reference": 16.855604, "loss_teacher_z_art": 3.975356, "loss_teacher_event": 5.620279, "loss_teacher_event_prior": 5.389267, "loss_teacher_energy_proxy": 17.813971, "loss_teacher_vuv_proxy": 0.679779, "loss_teacher_aper_proxy": 0.084486, "loss_log_f0_correction_l1": 0.096189, "loss_aper_correction_l1": 0.046642, "teacher_confidence_weighted": true, "effective_weight_sum": 5661.639648}

## target_validation
- record_count: 66
- dry_run_batch_size: 3
- sample_record_ids: ['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116']
- loss_metrics: {"loss_total": 14.675997, "loss_total_default_reference": 15.632492, "loss_teacher_z_art": 4.763379, "loss_teacher_event": 5.705399, "loss_teacher_event_prior": 5.328018, "loss_teacher_energy_proxy": 9.564948, "loss_teacher_vuv_proxy": 0.648206, "loss_teacher_aper_proxy": 0.096919, "loss_log_f0_correction_l1": 0.096115, "loss_aper_correction_l1": 0.058429, "teacher_confidence_weighted": true, "effective_weight_sum": 392.8172}

## target_special_eval
- record_count: 8
- dry_run_batch_size: 3
- sample_record_ids: ['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108']
- loss_metrics: {"loss_total": 13.732573, "loss_total_default_reference": 15.24766, "loss_teacher_z_art": 3.068141, "loss_teacher_event": 5.54681, "loss_teacher_event_prior": 5.465405, "loss_teacher_energy_proxy": 15.150872, "loss_teacher_vuv_proxy": 0.703869, "loss_teacher_aper_proxy": 0.059303, "loss_log_f0_correction_l1": 0.04787, "loss_aper_correction_l1": 0.030065, "teacher_confidence_weighted": true, "effective_weight_sum": 429.664124}

## Notes
- This stage defines only the minimum teacher-supervised dry-run losses needed to move beyond pure data wiring.
- Current supervision intentionally avoids forcing a hidden-state distillation term because Stage3 and offline_mvp hidden dimensions are not yet aligned.
- Frontend proxy terms are heuristic and should be treated as bootstrap supervision, not final semantic commitments.

## Next Steps
- Decide which teacher_frame_confidence behaviors become actual weighting or filtering policy in real training.
- Add explicit Stage3 hidden-space projection only if hidden distillation is still needed after the base loss route is validated.
- Build a real training loop on top of this dry-run contract without opening r_res yet.
