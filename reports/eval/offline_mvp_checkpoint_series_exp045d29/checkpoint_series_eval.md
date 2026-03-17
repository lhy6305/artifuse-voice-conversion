# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d29_round1_1_d26_init_d22_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt
- baseline.target_loss_total: 2.441699
- baseline.source_loss_total: 2.414754
- zero_z_art.delta_target_loss_total: 0.333095
- zero_z_art.delta_source_loss_total: 0.381401
- zero_e_evt.delta_target_loss_total: 2.74441
- zero_e_evt.delta_source_loss_total: 3.631829

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step20.pt
- baseline.target_loss_total: 2.406727
- baseline.source_loss_total: 2.347389
- zero_z_art.delta_target_loss_total: 0.364927
- zero_z_art.delta_source_loss_total: 0.438136
- zero_e_evt.delta_target_loss_total: 2.978481
- zero_e_evt.delta_source_loss_total: 4.123656

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
