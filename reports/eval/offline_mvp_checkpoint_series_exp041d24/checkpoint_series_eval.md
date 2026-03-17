# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d24_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-041-offline-mvp-d24-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d24_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_exp041/checkpoints/EXP-20260315-041-offline-mvp-d24-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-30step-calibration.step10.pt
- baseline.target_loss_total: 2.604974
- baseline.source_loss_total: 2.564201
- zero_z_art.delta_target_loss_total: 0.419647
- zero_z_art.delta_source_loss_total: 0.479597
- zero_e_evt.delta_target_loss_total: 3.053715
- zero_e_evt.delta_source_loss_total: 3.78143

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d24_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_exp041/checkpoints/EXP-20260315-041-offline-mvp-d24-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-30step-calibration.step20.pt
- baseline.target_loss_total: 2.483471
- baseline.source_loss_total: 2.465916
- zero_z_art.delta_target_loss_total: 0.398439
- zero_z_art.delta_source_loss_total: 0.45262
- zero_e_evt.delta_target_loss_total: 3.021211
- zero_e_evt.delta_source_loss_total: 3.963903

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d24_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_exp041/checkpoints/EXP-20260315-041-offline-mvp-d24-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-30step-calibration.step30.pt
- baseline.target_loss_total: 2.457903
- baseline.source_loss_total: 2.414508
- zero_z_art.delta_target_loss_total: 0.438936
- zero_z_art.delta_source_loss_total: 0.521655
- zero_e_evt.delta_target_loss_total: 3.299035
- zero_e_evt.delta_source_loss_total: 4.54464

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
