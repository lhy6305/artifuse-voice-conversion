# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d23_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d23_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_exp040/checkpoints/EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration.step10.pt
- baseline.target_loss_total: 2.604974
- baseline.source_loss_total: 2.564201
- zero_z_art.delta_target_loss_total: 0.419647
- zero_z_art.delta_source_loss_total: 0.479597
- zero_e_evt.delta_target_loss_total: 3.053715
- zero_e_evt.delta_source_loss_total: 3.78143

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d23_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_exp040/checkpoints/EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration.step20.pt
- baseline.target_loss_total: 2.48449
- baseline.source_loss_total: 2.465087
- zero_z_art.delta_target_loss_total: 0.401863
- zero_z_art.delta_source_loss_total: 0.457987
- zero_e_evt.delta_target_loss_total: 3.042276
- zero_e_evt.delta_source_loss_total: 3.998244

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d23_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_exp040/checkpoints/EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration.step30.pt
- baseline.target_loss_total: 2.45546
- baseline.source_loss_total: 2.411326
- zero_z_art.delta_target_loss_total: 0.43533
- zero_z_art.delta_source_loss_total: 0.517139
- zero_e_evt.delta_target_loss_total: 3.289808
- zero_e_evt.delta_source_loss_total: 4.532717

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
