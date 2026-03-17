# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d39_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d39_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_exp056/checkpoints/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.605301
- baseline.source_loss_total: 2.565378
- zero_z_art.delta_target_loss_total: 0.416722
- zero_z_art.delta_source_loss_total: 0.475235
- zero_e_evt.delta_target_loss_total: 3.042418
- zero_e_evt.delta_source_loss_total: 3.760166

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d39_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_exp056/checkpoints/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.502799
- baseline.source_loss_total: 2.479737
- zero_z_art.delta_target_loss_total: 0.407912
- zero_z_art.delta_source_loss_total: 0.46531
- zero_e_evt.delta_target_loss_total: 3.048095
- zero_e_evt.delta_source_loss_total: 3.971164

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
