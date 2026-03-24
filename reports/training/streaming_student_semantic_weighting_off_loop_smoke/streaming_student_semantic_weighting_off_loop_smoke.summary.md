# Stage3 Streaming Student Training Loop Scaffold

- experiment_id: streaming_student_semantic_weighting_off_loop_smoke
- generated_at: 2026-03-24T22:15:30
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- teacher_label_index_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_teacher_labels_semantic_smoke/teacher_label_index.jsonl
- calibration_asset_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json
- conditioning: {"asset_version": "stage3_calibration_asset_v1", "asset_status": "heuristic_bootstrap_estimated", "speaker_dim": 16, "geom_dim": 8, "alpha_value": 1.15, "source": "F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json"}
- training: {"batch_size": 1, "validation_batch_size": 1, "num_steps": 4, "validation_interval": 1, "checkpoint_interval": 4, "validation_batches": 1, "validation_mode": "full", "learning_rate": 0.001, "max_grad_norm": 1.0, "use_teacher_confidence": true, "loss_weights": {"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01}, "semantic_supervision": {"enabled": true, "required_contract_version": "target_event_semantic_sidecar_v1", "clean_text_bonus": 0.08, "multi_clause_bonus": 0.08, "multi_terminal_bonus": 0.1, "clause_ge4_bonus": 0.08, "pause_multi_bonus": 0.05, "terminal_present_bonus": 0.05, "nonverbal_penalty": 0.2, "event_prior_alpha": 1.0, "event_alpha": 0.35, "z_art_alpha": 0.2, "min_multiplier": 0.75, "max_multiplier": 1.45}, "loss_weight_schedule": {}, "loss_weight_overrides_path": "F:/proj_dev/tmp/workdir4/reports/config_overrides/streaming_student_semantic_weighting_disabled.json"}

## Step History
- step=1 loss_total=21.081259 grad_norm=62.58271 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} record_ids=['target::archive_firefly_1']
- step=2 loss_total=15.340199 grad_norm=34.583042 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} record_ids=['target::archive_firefly_1']
- step=3 loss_total=12.715452 grad_norm=21.119459 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} record_ids=['target::archive_firefly_1']
- step=4 loss_total=11.23148 grad_norm=13.314065 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} record_ids=['target::archive_firefly_1']

## Validation History
- step=1 loss_total=14.118607 validation_mode=full validation_batches=1 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} sampled_record_ids=[['target::chapter3_3_firefly_162']]
- step=2 loss_total=11.234417 validation_mode=full validation_batches=1 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} sampled_record_ids=[['target::chapter3_3_firefly_162']]
- step=3 loss_total=9.733636 validation_mode=full validation_batches=1 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} sampled_record_ids=[['target::chapter3_3_firefly_162']]
- step=4 loss_total=9.037385 validation_mode=full validation_batches=1 effective_loss_weights={"teacher_z_art": 1.0, "teacher_event": 1.0, "teacher_event_prior": 0.5, "teacher_energy_proxy": 0.25, "teacher_vuv_proxy": 0.15, "teacher_aper_proxy": 0.1, "teacher_proxy_acoustic": 0.0, "teacher_proxy_temporal": 0.0, "log_f0_correction_l1": 0.01, "aper_correction_l1": 0.01} sampled_record_ids=[['target::chapter3_3_firefly_162']]

## Artifacts
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_semantic_weighting_off_loop_smoke/checkpoints/streaming_student_semantic_weighting_off_loop_smoke.step4.pt']
- latest_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/streaming_student_semantic_weighting_off_loop_smoke/checkpoints/streaming_student_semantic_weighting_off_loop_smoke.step4.pt
- best_checkpoint: {"selection_rule": "min_validation_loss_total_over_recorded_checkpoints", "step": 4, "validation_mode": "full", "loss_total": 9.037385, "checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_semantic_weighting_off_loop_smoke/checkpoints/streaming_student_semantic_weighting_off_loop_smoke.step4.pt"}

## Notes
- This is a minimal multi-step Stage3 training loop scaffold built on top of the new teacher-supervised contract.
- Validation now walks the full target_validation slice sequentially inside the training loop.
- The purpose is to expose step-wise loss, grad_norm, validation, and checkpoint behavior before adding richer supervision or r_res.

## Next Steps
- Use this fuller validation mode to compare future short-horizon runs without relying on a separate checkpoint-eval pass for every checkpoint.
- Tune learning rate, loss weights, and teacher confidence usage based on short-horizon trajectories instead of a single step.
- Keep hidden distillation and r_res disabled until the base multi-step route is stable.
