# Stage3 Streaming Student Training Loop Scaffold

- experiment_id: streaming_student_stage_loop_eventprior025_v1
- generated_at: 2026-03-17T15:33:41
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 3, "validation_batch_size": 6, "num_steps": 12, "validation_interval": 4, "checkpoint_interval": 4, "validation_batches": 4, "learning_rate": 0.001, "max_grad_norm": 1.0, "use_teacher_confidence": true, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.25, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}, "loss_weight_overrides_path": "F:/proj_dev/tmp/workdir4/configs/streaming_student_loss_weights_eventprior_light_v1.json"}

## Step History
- step=1 loss_total=19.2505 grad_norm=64.24408 record_ids=['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11']
- step=2 loss_total=13.61797 grad_norm=35.846138 record_ids=['target::archive_firefly_12', 'target::archive_firefly_13', 'target::archive_firefly_14']
- step=3 loss_total=10.729006 grad_norm=21.078161 record_ids=['target::archive_firefly_15', 'target::archive_firefly_16', 'target::archive_firefly_17']
- step=4 loss_total=9.459835 grad_norm=12.829979 record_ids=['target::archive_firefly_18', 'target::archive_firefly_19', 'target::archive_firefly_20']
- step=5 loss_total=9.153522 grad_norm=8.3797 record_ids=['target::archive_firefly_3', 'target::archive_firefly_4', 'target::archive_firefly_5']
- step=6 loss_total=8.504943 grad_norm=7.6018 record_ids=['target::archive_firefly_6', 'target::archive_firefly_7', 'target::archive_firefly_8']
- step=7 loss_total=8.043442 grad_norm=6.572475 record_ids=['target::archive_firefly_9', 'target::chapter3_17_firefly_101', 'target::chapter3_17_firefly_102']
- step=8 loss_total=7.566546 grad_norm=7.146733 record_ids=['target::chapter3_17_firefly_103', 'target::chapter3_17_firefly_104', 'target::chapter3_17_firefly_105']
- step=9 loss_total=7.364277 grad_norm=6.366364 record_ids=['target::chapter3_17_firefly_107', 'target::chapter3_17_firefly_108', 'target::chapter3_17_firefly_109']
- step=10 loss_total=7.226331 grad_norm=5.803028 record_ids=['target::chapter3_17_firefly_110', 'target::chapter3_17_firefly_111', 'target::chapter3_17_firefly_113']
- step=11 loss_total=6.98 grad_norm=5.894033 record_ids=['target::chapter3_17_firefly_114', 'target::chapter3_17_firefly_115', 'target::chapter3_17_firefly_116']
- step=12 loss_total=6.985175 grad_norm=4.958564 record_ids=['target::chapter3_17_firefly_117', 'target::chapter3_17_firefly_118', 'target::chapter3_17_firefly_120']

## Validation History
- step=4 loss_total=8.713638 validation_batches=4 sampled_record_ids=[['target::chapter3_2_firefly_212', 'target::chapter3_3_firefly_246', 'target::chapter3_20_firefly_145', 'target::chapter3_29_firefly_130', 'target::chapter3_30_firefly_117', 'target::chapter3_3_firefly_115'], ['target::chapter3_29_firefly_113', 'target::chapter3_22_firefly_114', 'target::chapter3_2_firefly_137', 'target::chapter3_3_firefly_234', 'target::chapter3_3_firefly_171', 'target::chapter3_30_firefly_145'], ['target::chapter3_3_firefly_174', 'target::chapter3_26_firefly_114', 'target::chapter3_30_firefly_147', 'target::chapter3_2_firefly_183', 'target::chapter3_4_firefly_126', 'target::chapter3_3_firefly_199'], ['target::chapter3_20_firefly_133', 'target::chapter3_29_firefly_141', 'target::chapter3_3_firefly_213', 'target::chapter3_2_firefly_164', 'target::chapter3_30_firefly_132', 'target::chapter3_5_firefly_102']]
- step=8 loss_total=7.703854 validation_batches=4 sampled_record_ids=[['target::chapter3_20_firefly_135', 'target::chapter3_2_firefly_220', 'target::chapter3_6_firefly_103', 'target::chapter3_3_firefly_122', 'target::chapter3_2_firefly_170', 'target::chapter3_2_firefly_155'], ['target::chapter3_2_firefly_165', 'target::chapter3_3_firefly_182', 'target::chapter3_4_firefly_112', 'target::chapter3_30_firefly_136', 'target::chapter4_7_firefly_105', 'target::chapter3_3_firefly_245'], ['target::chapter3_3_firefly_197', 'target::chapter3_29_firefly_103', 'target::chapter3_30_firefly_137', 'target::chapter3_3_firefly_212', 'target::chapter3_4_firefly_109', 'target::chapter3_26_firefly_107'], ['target::chapter3_29_firefly_142', 'target::chapter3_3_firefly_215', 'target::chapter3_3_firefly_210', 'target::chapter3_29_firefly_136', 'target::chapter3_4_firefly_105', 'target::chapter3_17_firefly_133']]
- step=12 loss_total=6.886201 validation_batches=4 sampled_record_ids=[['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184', 'target::chapter3_21_firefly_116', 'target::chapter3_3_firefly_207', 'target::chapter3_30_firefly_101', 'target::chapter3_2_firefly_131'], ['target::chapter3_2_firefly_212', 'target::chapter3_3_firefly_246', 'target::chapter3_20_firefly_145', 'target::chapter3_29_firefly_130', 'target::chapter3_30_firefly_117', 'target::chapter3_3_firefly_115'], ['target::chapter3_29_firefly_113', 'target::chapter3_22_firefly_114', 'target::chapter3_2_firefly_137', 'target::chapter3_3_firefly_234', 'target::chapter3_3_firefly_171', 'target::chapter3_30_firefly_145'], ['target::chapter3_3_firefly_174', 'target::chapter3_26_firefly_114', 'target::chapter3_30_firefly_147', 'target::chapter3_2_firefly_183', 'target::chapter3_4_firefly_126', 'target::chapter3_3_firefly_199']]

## Artifacts
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step4.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step8.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt']
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 12, "loss_total": 6.886201, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt"}

## Notes
- This is a minimal multi-step Stage3 training loop scaffold built on top of the new teacher-supervised contract.
- Validation currently averages a small sampled subset of target_validation batches for speed; it is not a full-slice evaluation.
- The purpose is to expose step-wise loss, grad_norm, validation, and checkpoint behavior before adding richer supervision or r_res.

## Next Steps
- Decide whether validation should stay as sampled batches or be expanded into a fuller pass before larger runs.
- Tune learning rate, loss weights, and teacher confidence usage based on short-horizon trajectories instead of a single step.
- Keep hidden distillation and r_res disabled until the base multi-step route is stable.
