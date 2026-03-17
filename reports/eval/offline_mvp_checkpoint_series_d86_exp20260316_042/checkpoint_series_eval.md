# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d86_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-042.step50.pt
- baseline.target_loss_total: 2.313514
- baseline.source_loss_total: 2.233429
- zero_z_art.delta_target_loss_total: 0.308605
- zero_z_art.delta_source_loss_total: 0.377963
- zero_e_evt.delta_target_loss_total: 2.570719
- zero_e_evt.delta_source_loss_total: 3.620581

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-042.step100.pt
- baseline.target_loss_total: 2.203182
- baseline.source_loss_total: 2.098242
- zero_z_art.delta_target_loss_total: 0.461504
- zero_z_art.delta_source_loss_total: 0.503475
- zero_e_evt.delta_target_loss_total: 2.198116
- zero_e_evt.delta_source_loss_total: 2.923765

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-042.step150.pt
- baseline.target_loss_total: 2.154244
- baseline.source_loss_total: 2.039952
- zero_z_art.delta_target_loss_total: 0.50498
- zero_z_art.delta_source_loss_total: 0.531484
- zero_e_evt.delta_target_loss_total: 2.186293
- zero_e_evt.delta_source_loss_total: 2.828208

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-042.step200.pt
- baseline.target_loss_total: 2.130019
- baseline.source_loss_total: 2.001553
- zero_z_art.delta_target_loss_total: 0.395586
- zero_z_art.delta_source_loss_total: 0.38302
- zero_e_evt.delta_target_loss_total: 1.816795
- zero_e_evt.delta_source_loss_total: 2.269345

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
