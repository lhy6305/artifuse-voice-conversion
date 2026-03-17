# Stage3 Streaming Student Checkpoint Eval

- experiment_id: streaming_student_stage_loop_eventprior025_fullval48_v1
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 6, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.25, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}, "loss_weight_overrides_path": "F:/proj_dev/tmp/workdir4/configs/streaming_student_loss_weights_eventprior_light_v1.json", "use_teacher_confidence": true}

## target_validation
- record_count: 66
- batch_count: 11
- loss_metrics: {"loss_total": 5.978989, "loss_total_default_reference": 7.152429, "loss_teacher_z_art": 0.013478, "loss_teacher_event": 4.677829, "loss_teacher_event_prior": 4.69376, "loss_teacher_energy_proxy": 0.092954, "loss_teacher_vuv_proxy": 0.600527, "loss_teacher_aper_proxy": 0.004687, "loss_log_f0_correction_l1": 0.024589, "loss_aper_correction_l1": 0.020862, "teacher_confidence_weighted": true, "effective_weight_sum": 4941.934959}
- sample_record_id_batches: [['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116', 'target::chapter3_3_firefly_207', 'target::chapter3_30_firefly_101', 'target::chapter3_2_firefly_131'], ['target::chapter3_2_firefly_212', 'target::chapter3_3_firefly_246', 'target::chapter3_20_firefly_145', 'target::chapter3_29_firefly_130', 'target::chapter3_30_firefly_117', 'target::chapter3_3_firefly_115'], ['target::chapter3_29_firefly_113', 'target::chapter3_22_firefly_114', 'target::chapter3_2_firefly_137', 'target::chapter3_3_firefly_234', 'target::chapter3_3_firefly_171', 'target::chapter3_30_firefly_145'], ['target::chapter3_3_firefly_174', 'target::chapter3_26_firefly_114', 'target::chapter3_30_firefly_147', 'target::chapter3_2_firefly_183', 'target::chapter3_4_firefly_126', 'target::chapter3_3_firefly_199']]

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_metrics: {"loss_total": 6.328038, "loss_total_default_reference": 7.573954, "loss_teacher_z_art": 0.022951, "loss_teacher_event": 4.924936, "loss_teacher_event_prior": 4.983659, "loss_teacher_energy_proxy": 0.12645, "loss_teacher_vuv_proxy": 0.679004, "loss_teacher_aper_proxy": 0.003042, "loss_log_f0_correction_l1": 0.013534, "loss_aper_correction_l1": 0.033489, "teacher_confidence_weighted": true, "effective_weight_sum": 556.751251}
- sample_record_id_batches: [['target::no_text_voice/chapter3_17_firefly_106', 'target::no_text_voice/chapter3_18_firefly_101', 'target::no_text_voice/chapter3_21_firefly_108', 'target::no_text_voice/chapter3_22_firefly_115', 'target::no_text_voice/chapter3_29_firefly_139', 'target::no_text_voice/chapter3_2_firefly_102'], ['target::no_text_voice/chapter3_30_firefly_144', 'target::no_text_voice/chapter3_3_firefly_110']]

## Notes
- This evaluation uses the stored Stage3 checkpoint with the current teacher-label and calibration assets.
- Unlike the in-loop sampled validation, this report walks the full selected slice sequentially.
- These losses are still teacher-supervised proxy losses, not final user-facing quality metrics.
