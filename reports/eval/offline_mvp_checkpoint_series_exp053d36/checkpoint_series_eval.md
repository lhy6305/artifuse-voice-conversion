# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d36_round1_1_d33_step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d36_d33step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_exp053/checkpoints/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.524827
- baseline.source_loss_total: 2.475695
- zero_z_art.delta_target_loss_total: 0.43039
- zero_z_art.delta_source_loss_total: 0.507511
- zero_e_evt.delta_target_loss_total: 3.195542
- zero_e_evt.delta_source_loss_total: 4.197735

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d36_d33step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_exp053/checkpoints/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.463763
- baseline.source_loss_total: 2.412579
- zero_z_art.delta_target_loss_total: 0.407633
- zero_z_art.delta_source_loss_total: 0.48837
- zero_e_evt.delta_target_loss_total: 3.221708
- zero_e_evt.delta_source_loss_total: 4.372582

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
