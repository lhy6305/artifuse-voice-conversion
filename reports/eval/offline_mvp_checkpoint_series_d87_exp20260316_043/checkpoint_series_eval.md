# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d87_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_lateretention_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step50.pt
- baseline.target_loss_total: 2.314084
- baseline.source_loss_total: 2.233754
- zero_z_art.delta_target_loss_total: 0.283247
- zero_z_art.delta_source_loss_total: 0.353146
- zero_e_evt.delta_target_loss_total: 2.603668
- zero_e_evt.delta_source_loss_total: 3.666091

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step100.pt
- baseline.target_loss_total: 2.213228
- baseline.source_loss_total: 2.107321
- zero_z_art.delta_target_loss_total: 0.341502
- zero_z_art.delta_source_loss_total: 0.39065
- zero_e_evt.delta_target_loss_total: 2.197825
- zero_e_evt.delta_source_loss_total: 2.940973

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step150.pt
- baseline.target_loss_total: 2.166759
- baseline.source_loss_total: 2.056702
- zero_z_art.delta_target_loss_total: 0.498314
- zero_z_art.delta_source_loss_total: 0.541378
- zero_e_evt.delta_target_loss_total: 2.330918
- zero_e_evt.delta_source_loss_total: 3.027708

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- baseline.target_loss_total: 2.127392
- baseline.source_loss_total: 2.005721
- zero_z_art.delta_target_loss_total: 0.484435
- zero_z_art.delta_source_loss_total: 0.491268
- zero_e_evt.delta_target_loss_total: 2.069828
- zero_e_evt.delta_source_loss_total: 2.620858

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
