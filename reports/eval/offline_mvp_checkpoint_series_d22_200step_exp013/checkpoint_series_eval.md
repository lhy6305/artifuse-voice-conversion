# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d22_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_smallscale_200_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_200step_exp013/checkpoints/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.step50.pt
- baseline.target_loss_total: 2.364733
- baseline.source_loss_total: 2.304073
- zero_z_art.delta_target_loss_total: 0.38195
- zero_z_art.delta_source_loss_total: 0.457399
- zero_e_evt.delta_target_loss_total: 2.773641
- zero_e_evt.delta_source_loss_total: 3.909179

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_200step_exp013/checkpoints/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.step100.pt
- baseline.target_loss_total: 2.25195
- baseline.source_loss_total: 2.16822
- zero_z_art.delta_target_loss_total: 0.534144
- zero_z_art.delta_source_loss_total: 0.586028
- zero_e_evt.delta_target_loss_total: 2.135677
- zero_e_evt.delta_source_loss_total: 2.851829

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_200step_exp013/checkpoints/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.step150.pt
- baseline.target_loss_total: 2.165483
- baseline.source_loss_total: 2.059419
- zero_z_art.delta_target_loss_total: 0.65879
- zero_z_art.delta_source_loss_total: 0.712097
- zero_e_evt.delta_target_loss_total: 1.960466
- zero_e_evt.delta_source_loss_total: 2.443292

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_200step_exp013/checkpoints/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.step200.pt
- baseline.target_loss_total: 2.123385
- baseline.source_loss_total: 2.020978
- zero_z_art.delta_target_loss_total: 0.669467
- zero_z_art.delta_source_loss_total: 0.690812
- zero_e_evt.delta_target_loss_total: 1.864222
- zero_e_evt.delta_source_loss_total: 2.211045

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
