# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d74_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_late_d33step10_teacher_restore_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d74_singleton_sparse_d26_init_d33late_restore_exp031/checkpoints/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.step10.pt
- baseline.target_loss_total: 2.453608
- baseline.source_loss_total: 2.416647
- zero_z_art.delta_target_loss_total: 0.387834
- zero_z_art.delta_source_loss_total: 0.453983
- zero_e_evt.delta_target_loss_total: 2.985898
- zero_e_evt.delta_source_loss_total: 4.013562

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d74_singleton_sparse_d26_init_d33late_restore_exp031/checkpoints/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.step20.pt
- baseline.target_loss_total: 2.410508
- baseline.source_loss_total: 2.359195
- zero_z_art.delta_target_loss_total: 0.368817
- zero_z_art.delta_source_loss_total: 0.439291
- zero_e_evt.delta_target_loss_total: 2.955904
- zero_e_evt.delta_source_loss_total: 4.0837

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
