# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-040-offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-040.step10.pt
- baseline.target_loss_total: 2.453608
- baseline.source_loss_total: 2.416647
- zero_z_art.delta_target_loss_total: 0.387834
- zero_z_art.delta_source_loss_total: 0.453983
- zero_e_evt.delta_target_loss_total: 2.985898
- zero_e_evt.delta_source_loss_total: 4.013562

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-040.step20.pt
- baseline.target_loss_total: 2.417702
- baseline.source_loss_total: 2.364048
- zero_z_art.delta_target_loss_total: 0.381618
- zero_z_art.delta_source_loss_total: 0.457969
- zero_e_evt.delta_target_loss_total: 3.089381
- zero_e_evt.delta_source_loss_total: 4.289749

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
