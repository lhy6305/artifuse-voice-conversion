# Stage3 Streaming Student Training Loop Scaffold

- experiment_id: streaming_student_stage_loop_lr3e4_v1
- generated_at: 2026-03-17T12:42:28
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 3, "validation_batch_size": 3, "num_steps": 4, "validation_interval": 2, "checkpoint_interval": 2, "validation_batches": 2, "learning_rate": 0.0003, "max_grad_norm": 1.0, "use_teacher_confidence": true, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}}

## Step History
- step=1 loss_total=20.612329 grad_norm=64.267143 record_ids=['target::archive_firefly_1', 'target::archive_firefly_10', 'target::archive_firefly_11']
- step=2 loss_total=18.587992 grad_norm=55.542522 record_ids=['target::archive_firefly_12', 'target::archive_firefly_13', 'target::archive_firefly_14']
- step=3 loss_total=16.433231 grad_norm=45.96698 record_ids=['target::archive_firefly_15', 'target::archive_firefly_16', 'target::archive_firefly_17']
- step=4 loss_total=15.229719 grad_norm=38.657425 record_ids=['target::archive_firefly_18', 'target::archive_firefly_19', 'target::archive_firefly_20']

## Validation History
- step=2 loss_total=17.405603 validation_batches=2 sampled_record_ids=[['target::chapter3_2_firefly_212', 'target::chapter3_3_firefly_246', 'target::chapter3_20_firefly_145'], ['target::chapter3_29_firefly_130', 'target::chapter3_30_firefly_117', 'target::chapter3_3_firefly_115']]
- step=4 loss_total=13.698695 validation_batches=2 sampled_record_ids=[['target::chapter3_3_firefly_174', 'target::chapter3_26_firefly_114', 'target::chapter3_30_firefly_147'], ['target::chapter3_2_firefly_183', 'target::chapter3_4_firefly_126', 'target::chapter3_3_firefly_199']]

## Artifacts
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_lr3e4_v1.step2.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_lr3e4_v1.step4.pt']
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_lr3e4_v1.step4.pt

## Notes
- This is a minimal multi-step Stage3 training loop scaffold built on top of the new teacher-supervised contract.
- Validation currently averages a small sampled subset of target_validation batches for speed; it is not a full-slice evaluation.
- The purpose is to expose step-wise loss, grad_norm, validation, and checkpoint behavior before adding richer supervision or r_res.

## Next Steps
- Decide whether validation should stay as sampled batches or be expanded into a fuller pass before larger runs.
- Tune learning rate, loss weights, and teacher confidence usage based on short-horizon trajectories instead of a single step.
- Keep hidden distillation and r_res disabled until the base multi-step route is stable.
