# Stage3 Streaming Student Training Loop Scaffold

- experiment_id: streaming_student_stage_loop_proxytemporal20warm6_smoketest_v1
- generated_at: 2026-03-17T20:37:33
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 2, "validation_batch_size": 2, "num_steps": 1, "validation_interval": 1, "checkpoint_interval": 1, "validation_batches": 1, "validation_mode": "sampled", "learning_rate": 0.001, "max_grad_norm": 1.0, "use_teacher_confidence": true, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 20.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}, "loss_weight_schedule": {"teacher_proxy_temporal": {"type": "linear_warmup_hold", "start_weight": 0.0, "warmup_steps": 6}}, "loss_weight_overrides_path": "F:/proj_dev/tmp/workdir4/configs/streaming_student_loss_weights_proxytemporal20_warmup6_v1.json"}

## Step History
- step=1 loss_total=20.617382 grad_norm=64.011513 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} record_ids=['target::archive_firefly_1', 'target::archive_firefly_10']

## Validation History
- step=1 loss_total=14.102855 validation_mode=sampled validation_batches=1 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} sampled_record_ids=[['target::chapter3_3_firefly_162', 'target::chapter3_20_firefly_184']]

## Artifacts
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_proxytemporal20warm6_smoketest_v1.step1.pt']
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_proxytemporal20warm6_smoketest_v1.step1.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 1, "validation_mode": "sampled", "loss_total": 14.102855, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_proxytemporal20warm6_smoketest_v1.step1.pt"}

## Notes
- This is a minimal multi-step Stage3 training loop scaffold built on top of the new teacher-supervised contract.
- Validation currently averages a small sampled subset of target_validation batches for speed; it is not a full-slice evaluation.
- The purpose is to expose step-wise loss, grad_norm, validation, and checkpoint behavior before adding richer supervision or r_res.

## Next Steps
- Decide whether sampled validation should remain the default quick-check mode or whether fuller validation should become the default before larger runs.
- Tune learning rate, loss weights, and teacher confidence usage based on short-horizon trajectories instead of a single step.
- Keep hidden distillation and r_res disabled until the base multi-step route is stable.
