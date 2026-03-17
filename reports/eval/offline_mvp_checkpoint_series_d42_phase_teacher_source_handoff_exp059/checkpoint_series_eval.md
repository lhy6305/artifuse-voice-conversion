# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d42_round1_1_d7_init_phase_teacher_source_handoff_d33step10_to_d22_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d42_phase_teacher_source_handoff_exp059/checkpoints/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.628407
- baseline.source_loss_total: 2.561576
- zero_z_art.delta_target_loss_total: 0.455237
- zero_z_art.delta_source_loss_total: 0.542037
- zero_e_evt.delta_target_loss_total: 3.218836
- zero_e_evt.delta_source_loss_total: 4.067058

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d42_phase_teacher_source_handoff_exp059/checkpoints/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.502762
- baseline.source_loss_total: 2.480068
- zero_z_art.delta_target_loss_total: 0.417186
- zero_z_art.delta_source_loss_total: 0.485889
- zero_e_evt.delta_target_loss_total: 3.115116
- zero_e_evt.delta_source_loss_total: 4.069833

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
