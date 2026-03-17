# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d85_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-041.step50.pt
- baseline.target_loss_total: 2.313937
- baseline.source_loss_total: 2.233747
- zero_z_art.delta_target_loss_total: 0.311158
- zero_z_art.delta_source_loss_total: 0.379622
- zero_e_evt.delta_target_loss_total: 2.582539
- zero_e_evt.delta_source_loss_total: 3.636898

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-041.step100.pt
- baseline.target_loss_total: 2.212279
- baseline.source_loss_total: 2.110925
- zero_z_art.delta_target_loss_total: 0.448169
- zero_z_art.delta_source_loss_total: 0.490848
- zero_e_evt.delta_target_loss_total: 2.291469
- zero_e_evt.delta_source_loss_total: 3.069982

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-041.step150.pt
- baseline.target_loss_total: 2.158484
- baseline.source_loss_total: 2.045608
- zero_z_art.delta_target_loss_total: 0.424634
- zero_z_art.delta_source_loss_total: 0.438481
- zero_e_evt.delta_target_loss_total: 2.066232
- zero_e_evt.delta_source_loss_total: 2.662439

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-041.step200.pt
- baseline.target_loss_total: 2.129306
- baseline.source_loss_total: 2.005655
- zero_z_art.delta_target_loss_total: 0.433882
- zero_z_art.delta_source_loss_total: 0.43989
- zero_e_evt.delta_target_loss_total: 2.027351
- zero_e_evt.delta_source_loss_total: 2.565846

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
