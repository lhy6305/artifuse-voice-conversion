# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d30_round1_1_d26_init_d22_teacher_cross_anchor_event_only_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d30_d26_init_d22_teacher_cross_anchor_event_only_exp047/checkpoints/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.step10.pt
- baseline.target_loss_total: 2.442384
- baseline.source_loss_total: 2.416087
- zero_z_art.delta_target_loss_total: 0.33734
- zero_z_art.delta_source_loss_total: 0.384235
- zero_e_evt.delta_target_loss_total: 2.736144
- zero_e_evt.delta_source_loss_total: 3.617152

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d30_d26_init_d22_teacher_cross_anchor_event_only_exp047/checkpoints/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.step20.pt
- baseline.target_loss_total: 2.40904
- baseline.source_loss_total: 2.349457
- zero_z_art.delta_target_loss_total: 0.377184
- zero_z_art.delta_source_loss_total: 0.451239
- zero_e_evt.delta_target_loss_total: 2.982002
- zero_e_evt.delta_source_loss_total: 4.128084

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
