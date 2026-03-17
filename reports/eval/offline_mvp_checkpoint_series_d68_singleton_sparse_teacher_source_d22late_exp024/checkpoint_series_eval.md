# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d68_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d68_singleton_sparse_teacher_source_d22late_exp024/checkpoints/EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.step10.pt
- baseline.target_loss_total: 2.592714
- baseline.source_loss_total: 2.584
- zero_z_art.delta_target_loss_total: 0.42042
- zero_z_art.delta_source_loss_total: 0.470427
- zero_e_evt.delta_target_loss_total: 2.97141
- zero_e_evt.delta_source_loss_total: 3.625847

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d68_singleton_sparse_teacher_source_d22late_exp024/checkpoints/EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.step20.pt
- baseline.target_loss_total: 2.536503
- baseline.source_loss_total: 2.482547
- zero_z_art.delta_target_loss_total: 0.434833
- zero_z_art.delta_source_loss_total: 0.520755
- zero_e_evt.delta_target_loss_total: 3.26795
- zero_e_evt.delta_source_loss_total: 4.319623

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
