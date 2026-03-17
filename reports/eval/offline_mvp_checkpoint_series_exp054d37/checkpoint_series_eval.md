# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d37_round1_1_d22_init_d33_step10_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d37_d22_init_d33step10_teacher_checkpoint_cross_anchor_fused_hidden_exp054/checkpoints/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.396097
- baseline.source_loss_total: 2.360208
- zero_z_art.delta_target_loss_total: 0.278469
- zero_z_art.delta_source_loss_total: 0.314206
- zero_e_evt.delta_target_loss_total: 2.564125
- zero_e_evt.delta_source_loss_total: 3.5013

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d37_d22_init_d33step10_teacher_checkpoint_cross_anchor_fused_hidden_exp054/checkpoints/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.361688
- baseline.source_loss_total: 2.299024
- zero_z_art.delta_target_loss_total: 0.321586
- zero_z_art.delta_source_loss_total: 0.380642
- zero_e_evt.delta_target_loss_total: 2.652109
- zero_e_evt.delta_source_loss_total: 3.703019

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
