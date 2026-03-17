# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d32_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_fused_hidden_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d32_d7_init_d10_teacher_consistency_fused_hidden_exp049/checkpoints/EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration.step10.pt
- baseline.target_loss_total: 2.605301
- baseline.source_loss_total: 2.565378
- zero_z_art.delta_target_loss_total: 0.416722
- zero_z_art.delta_source_loss_total: 0.475235
- zero_e_evt.delta_target_loss_total: 3.042418
- zero_e_evt.delta_source_loss_total: 3.760166

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d32_d7_init_d10_teacher_consistency_fused_hidden_exp049/checkpoints/EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration.step20.pt
- baseline.target_loss_total: 2.486517
- baseline.source_loss_total: 2.465955
- zero_z_art.delta_target_loss_total: 0.405321
- zero_z_art.delta_source_loss_total: 0.46218
- zero_e_evt.delta_target_loss_total: 3.063655
- zero_e_evt.delta_source_loss_total: 4.028806

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d32_d7_init_d10_teacher_consistency_fused_hidden_exp049/checkpoints/EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration.step30.pt
- baseline.target_loss_total: 2.45553
- baseline.source_loss_total: 2.409599
- zero_z_art.delta_target_loss_total: 0.434057
- zero_z_art.delta_source_loss_total: 0.514563
- zero_e_evt.delta_target_loss_total: 3.299576
- zero_e_evt.delta_source_loss_total: 4.545316

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
