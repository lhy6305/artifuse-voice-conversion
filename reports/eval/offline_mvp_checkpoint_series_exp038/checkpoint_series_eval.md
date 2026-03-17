# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d82_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_fullpriority_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.step50.pt
- baseline.target_loss_total: 2.325566
- baseline.source_loss_total: 2.235636
- zero_z_art.delta_target_loss_total: 0.364517
- zero_z_art.delta_source_loss_total: 0.440115
- zero_e_evt.delta_target_loss_total: 2.796732
- zero_e_evt.delta_source_loss_total: 3.921188

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.step100.pt
- baseline.target_loss_total: 2.235057
- baseline.source_loss_total: 2.136808
- zero_z_art.delta_target_loss_total: 0.440124
- zero_z_art.delta_source_loss_total: 0.479381
- zero_e_evt.delta_target_loss_total: 2.378748
- zero_e_evt.delta_source_loss_total: 3.186128

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.step150.pt
- baseline.target_loss_total: 2.190394
- baseline.source_loss_total: 2.069306
- zero_z_art.delta_target_loss_total: 0.470433
- zero_z_art.delta_source_loss_total: 0.499187
- zero_e_evt.delta_target_loss_total: 2.313778
- zero_e_evt.delta_source_loss_total: 3.002749

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.step200.pt
- baseline.target_loss_total: 2.1446
- baseline.source_loss_total: 2.012848
- zero_z_art.delta_target_loss_total: 0.436209
- zero_z_art.delta_source_loss_total: 0.443061
- zero_e_evt.delta_target_loss_total: 2.126457
- zero_e_evt.delta_source_loss_total: 2.676537

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
