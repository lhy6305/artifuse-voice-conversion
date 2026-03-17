# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d76_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/checkpoints/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.step50.pt
- baseline.target_loss_total: 2.309977
- baseline.source_loss_total: 2.223894
- zero_z_art.delta_target_loss_total: 0.299145
- zero_z_art.delta_source_loss_total: 0.359678
- zero_e_evt.delta_target_loss_total: 2.548418
- zero_e_evt.delta_source_loss_total: 3.584124

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/checkpoints/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.step100.pt
- baseline.target_loss_total: 2.220601
- baseline.source_loss_total: 2.114013
- zero_z_art.delta_target_loss_total: 0.436968
- zero_z_art.delta_source_loss_total: 0.478924
- zero_e_evt.delta_target_loss_total: 2.36021
- zero_e_evt.delta_source_loss_total: 3.160625

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/checkpoints/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.step150.pt
- baseline.target_loss_total: 2.14267
- baseline.source_loss_total: 2.024242
- zero_z_art.delta_target_loss_total: 0.44088
- zero_z_art.delta_source_loss_total: 0.467355
- zero_e_evt.delta_target_loss_total: 2.062923
- zero_e_evt.delta_source_loss_total: 2.652791

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/checkpoints/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.step200.pt
- baseline.target_loss_total: 2.103109
- baseline.source_loss_total: 1.963847
- zero_z_art.delta_target_loss_total: 0.424651
- zero_z_art.delta_source_loss_total: 0.419681
- zero_e_evt.delta_target_loss_total: 1.937766
- zero_e_evt.delta_source_loss_total: 2.398549

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
