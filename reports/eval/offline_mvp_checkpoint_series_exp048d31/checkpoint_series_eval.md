# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d31_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_acoustic_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step10.pt
- baseline.target_loss_total: 2.605576
- baseline.source_loss_total: 2.564833
- zero_z_art.delta_target_loss_total: 0.41683
- zero_z_art.delta_source_loss_total: 0.475841
- zero_e_evt.delta_target_loss_total: 3.043228
- zero_e_evt.delta_source_loss_total: 3.761975

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step20.pt
- baseline.target_loss_total: 2.485412
- baseline.source_loss_total: 2.464972
- zero_z_art.delta_target_loss_total: 0.404295
- zero_z_art.delta_source_loss_total: 0.461035
- zero_e_evt.delta_target_loss_total: 3.051932
- zero_e_evt.delta_source_loss_total: 4.010998

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step30.pt
- baseline.target_loss_total: 2.456079
- baseline.source_loss_total: 2.41039
- zero_z_art.delta_target_loss_total: 0.436225
- zero_z_art.delta_source_loss_total: 0.517595
- zero_e_evt.delta_target_loss_total: 3.298481
- zero_e_evt.delta_source_loss_total: 4.543144

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
