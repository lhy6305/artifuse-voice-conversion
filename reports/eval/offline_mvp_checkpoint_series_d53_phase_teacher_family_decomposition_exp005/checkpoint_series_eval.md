# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d53_round1_1_d7_init_phase_teacher_family_decomposition_d33step10_d29step10_d29step20_shortpause_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-005-offline-mvp-d53-round1-1-d7-init-phase-teacher-family-decomposition-d33step10-d29step10-d29step20-shortpause-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d53_phase_teacher_family_decomposition_exp005/checkpoints/EXP-20260316-005-offline-mvp-d53-round1-1-d7-init-phase-teacher-family-decomposition-d33step10-d29step10-d29step20-shortpause-20step-calibration.step10.pt
- baseline.target_loss_total: 2.592714
- baseline.source_loss_total: 2.584
- zero_z_art.delta_target_loss_total: 0.42042
- zero_z_art.delta_source_loss_total: 0.470427
- zero_e_evt.delta_target_loss_total: 2.97141
- zero_e_evt.delta_source_loss_total: 3.625847

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d53_phase_teacher_family_decomposition_exp005/checkpoints/EXP-20260316-005-offline-mvp-d53-round1-1-d7-init-phase-teacher-family-decomposition-d33step10-d29step10-d29step20-shortpause-20step-calibration.step20.pt
- baseline.target_loss_total: 2.518954
- baseline.source_loss_total: 2.467745
- zero_z_art.delta_target_loss_total: 0.410493
- zero_z_art.delta_source_loss_total: 0.491175
- zero_e_evt.delta_target_loss_total: 3.198097
- zero_e_evt.delta_source_loss_total: 4.227512

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
