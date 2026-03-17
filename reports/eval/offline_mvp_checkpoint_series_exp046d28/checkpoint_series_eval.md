# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d28_round1_1_d22_init_d26_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d28_d22_init_d26_teacher_cross_anchor_consolidation_exp046/checkpoints/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.step10.pt
- baseline.target_loss_total: 2.391423
- baseline.source_loss_total: 2.353391
- zero_z_art.delta_target_loss_total: 0.278603
- zero_z_art.delta_source_loss_total: 0.31791
- zero_e_evt.delta_target_loss_total: 2.566482
- zero_e_evt.delta_source_loss_total: 3.51295

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d28_d22_init_d26_teacher_cross_anchor_consolidation_exp046/checkpoints/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.step20.pt
- baseline.target_loss_total: 2.355643
- baseline.source_loss_total: 2.289244
- zero_z_art.delta_target_loss_total: 0.307252
- zero_z_art.delta_source_loss_total: 0.36897
- zero_e_evt.delta_target_loss_total: 2.617499
- zero_e_evt.delta_source_loss_total: 3.66634

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
