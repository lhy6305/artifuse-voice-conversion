# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d71_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d71_singleton_sparse_d29_init_exp026/checkpoints/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.step10.pt
- baseline.target_loss_total: 2.368791
- baseline.source_loss_total: 2.328606
- zero_z_art.delta_target_loss_total: 0.274043
- zero_z_art.delta_source_loss_total: 0.323702
- zero_e_evt.delta_target_loss_total: 2.48338
- zero_e_evt.delta_source_loss_total: 3.427896

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d71_singleton_sparse_d29_init_exp026/checkpoints/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.step20.pt
- baseline.target_loss_total: 2.345802
- baseline.source_loss_total: 2.276928
- zero_z_art.delta_target_loss_total: 0.320415
- zero_z_art.delta_source_loss_total: 0.387687
- zero_e_evt.delta_target_loss_total: 2.634231
- zero_e_evt.delta_source_loss_total: 3.70187

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
