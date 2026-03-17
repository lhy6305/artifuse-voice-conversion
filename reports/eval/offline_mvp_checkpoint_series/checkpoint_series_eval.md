# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d83_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33to22late_teacher_handoff_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.step50.pt
- baseline.target_loss_total: 2.332573
- baseline.source_loss_total: 2.254943
- zero_z_art.delta_target_loss_total: 0.369034
- zero_z_art.delta_source_loss_total: 0.436663
- zero_e_evt.delta_target_loss_total: 2.673272
- zero_e_evt.delta_source_loss_total: 3.752703

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.step100.pt
- baseline.target_loss_total: 2.257266
- baseline.source_loss_total: 2.161593
- zero_z_art.delta_target_loss_total: 0.530758
- zero_z_art.delta_source_loss_total: 0.597417
- zero_e_evt.delta_target_loss_total: 2.428461
- zero_e_evt.delta_source_loss_total: 3.284679

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.step150.pt
- baseline.target_loss_total: 2.172644
- baseline.source_loss_total: 2.060362
- zero_z_art.delta_target_loss_total: 0.463976
- zero_z_art.delta_source_loss_total: 0.502202
- zero_e_evt.delta_target_loss_total: 2.197493
- zero_e_evt.delta_source_loss_total: 2.865599

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.step200.pt
- baseline.target_loss_total: 2.136478
- baseline.source_loss_total: 2.007288
- zero_z_art.delta_target_loss_total: 0.42172
- zero_z_art.delta_source_loss_total: 0.432081
- zero_e_evt.delta_target_loss_total: 2.011104
- zero_e_evt.delta_source_loss_total: 2.539052

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
