# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d57_round1_1_d7_init_d54_formal_special_clause_shape_middle_late_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-010-offline-mvp-d57-round1-1-d7-init-d54-formal-special-clause-shape-middle-late-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d57_formal_special_clause_shape_middle_exp010/checkpoints/EXP-20260316-010-offline-mvp-d57-round1-1-d7-init-d54-formal-special-clause-shape-middle-late-20step-calibration.step10.pt
- baseline.target_loss_total: 2.592714
- baseline.source_loss_total: 2.584
- zero_z_art.delta_target_loss_total: 0.42042
- zero_z_art.delta_source_loss_total: 0.470427
- zero_e_evt.delta_target_loss_total: 2.97141
- zero_e_evt.delta_source_loss_total: 3.625847

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d57_formal_special_clause_shape_middle_exp010/checkpoints/EXP-20260316-010-offline-mvp-d57-round1-1-d7-init-d54-formal-special-clause-shape-middle-late-20step-calibration.step20.pt
- baseline.target_loss_total: 2.519026
- baseline.source_loss_total: 2.468472
- zero_z_art.delta_target_loss_total: 0.41264
- zero_z_art.delta_source_loss_total: 0.493293
- zero_e_evt.delta_target_loss_total: 3.199882
- zero_e_evt.delta_source_loss_total: 4.230839

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
