# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d63_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_teacheraligned_30step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-019-offline-mvp-d63-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-teacheraligned-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d63_d22_singleton_latepulse_teacheraligned_exp019/checkpoints/EXP-20260316-019-offline-mvp-d63-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-teacheraligned-30step-calibration.step10.pt
- baseline.target_loss_total: 2.60535
- baseline.source_loss_total: 2.603301
- zero_z_art.delta_target_loss_total: 0.414234
- zero_z_art.delta_source_loss_total: 0.452843
- zero_e_evt.delta_target_loss_total: 2.891888
- zero_e_evt.delta_source_loss_total: 3.464346

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d63_d22_singleton_latepulse_teacheraligned_exp019/checkpoints/EXP-20260316-019-offline-mvp-d63-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-teacheraligned-30step-calibration.step20.pt
- baseline.target_loss_total: 2.521748
- baseline.source_loss_total: 2.484406
- zero_z_art.delta_target_loss_total: 0.397983
- zero_z_art.delta_source_loss_total: 0.456787
- zero_e_evt.delta_target_loss_total: 2.988662
- zero_e_evt.delta_source_loss_total: 3.866284

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d63_d22_singleton_latepulse_teacheraligned_exp019/checkpoints/EXP-20260316-019-offline-mvp-d63-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-teacheraligned-30step-calibration.step30.pt
- baseline.target_loss_total: 2.432608
- baseline.source_loss_total: 2.435188
- zero_z_art.delta_target_loss_total: 0.316145
- zero_z_art.delta_source_loss_total: 0.348011
- zero_e_evt.delta_target_loss_total: 2.603584
- zero_e_evt.delta_source_loss_total: 3.444091

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
