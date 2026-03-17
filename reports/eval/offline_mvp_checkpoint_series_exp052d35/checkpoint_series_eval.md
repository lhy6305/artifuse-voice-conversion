# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d35_round1_1_d33_init_d22_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d35_d33_init_d22_teacher_cross_anchor_fused_hidden_exp052/checkpoints/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.442669
- baseline.source_loss_total: 2.414282
- zero_z_art.delta_target_loss_total: 0.337547
- zero_z_art.delta_source_loss_total: 0.387143
- zero_e_evt.delta_target_loss_total: 2.768766
- zero_e_evt.delta_source_loss_total: 3.668438

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d35_d33_init_d22_teacher_cross_anchor_fused_hidden_exp052/checkpoints/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.404967
- baseline.source_loss_total: 2.346103
- zero_z_art.delta_target_loss_total: 0.361794
- zero_z_art.delta_source_loss_total: 0.434229
- zero_e_evt.delta_target_loss_total: 2.967455
- zero_e_evt.delta_source_loss_total: 4.107667

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
