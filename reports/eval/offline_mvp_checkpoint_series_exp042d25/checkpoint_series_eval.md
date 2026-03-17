# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d25_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step10.pt
- baseline.target_loss_total: 2.634191
- baseline.source_loss_total: 2.565548
- zero_z_art.delta_target_loss_total: 0.465696
- zero_z_art.delta_source_loss_total: 0.55238
- zero_e_evt.delta_target_loss_total: 3.227018
- zero_e_evt.delta_source_loss_total: 4.079644

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step20.pt
- baseline.target_loss_total: 2.538388
- baseline.source_loss_total: 2.49205
- zero_z_art.delta_target_loss_total: 0.460259
- zero_z_art.delta_source_loss_total: 0.543095
- zero_e_evt.delta_target_loss_total: 3.27265
- zero_e_evt.delta_source_loss_total: 4.317131

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step30.pt
- baseline.target_loss_total: 2.457136
- baseline.source_loss_total: 2.433605
- zero_z_art.delta_target_loss_total: 0.403509
- zero_z_art.delta_source_loss_total: 0.464938
- zero_e_evt.delta_target_loss_total: 2.993643
- zero_e_evt.delta_source_loss_total: 3.998996

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
