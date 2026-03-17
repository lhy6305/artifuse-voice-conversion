# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d64_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_shorttail_15step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 5
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step5.pt
- baseline.target_loss_total: 2.647781
- baseline.source_loss_total: 2.661439
- zero_z_art.delta_target_loss_total: 0.486395
- zero_z_art.delta_source_loss_total: 0.528915
- zero_e_evt.delta_target_loss_total: 3.044065
- zero_e_evt.delta_source_loss_total: 3.606023

### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step10.pt
- baseline.target_loss_total: 2.592714
- baseline.source_loss_total: 2.584
- zero_z_art.delta_target_loss_total: 0.42042
- zero_z_art.delta_source_loss_total: 0.470427
- zero_e_evt.delta_target_loss_total: 2.97141
- zero_e_evt.delta_source_loss_total: 3.625847

### step 15
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step15.pt
- baseline.target_loss_total: 2.551966
- baseline.source_loss_total: 2.520576
- zero_z_art.delta_target_loss_total: 0.400641
- zero_z_art.delta_source_loss_total: 0.462322
- zero_e_evt.delta_target_loss_total: 3.012511
- zero_e_evt.delta_source_loss_total: 3.812669

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
