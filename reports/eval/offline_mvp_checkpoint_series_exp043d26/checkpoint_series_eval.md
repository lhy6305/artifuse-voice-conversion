# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d26_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d26_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp043/checkpoints/EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration.step10.pt
- baseline.target_loss_total: 2.634191
- baseline.source_loss_total: 2.565548
- zero_z_art.delta_target_loss_total: 0.465696
- zero_z_art.delta_source_loss_total: 0.55238
- zero_e_evt.delta_target_loss_total: 3.227018
- zero_e_evt.delta_source_loss_total: 4.079644

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d26_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp043/checkpoints/EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration.step20.pt
- baseline.target_loss_total: 2.538388
- baseline.source_loss_total: 2.49205
- zero_z_art.delta_target_loss_total: 0.460259
- zero_z_art.delta_source_loss_total: 0.543095
- zero_e_evt.delta_target_loss_total: 3.27265
- zero_e_evt.delta_source_loss_total: 4.317131

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
