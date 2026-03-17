# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d40_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d40_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_exp057/checkpoints/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.634861
- baseline.source_loss_total: 2.564948
- zero_z_art.delta_target_loss_total: 0.46347
- zero_z_art.delta_source_loss_total: 0.549882
- zero_e_evt.delta_target_loss_total: 3.224344
- zero_e_evt.delta_source_loss_total: 4.074445

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d40_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_exp057/checkpoints/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.506982
- baseline.source_loss_total: 2.487728
- zero_z_art.delta_target_loss_total: 0.431034
- zero_z_art.delta_source_loss_total: 0.495598
- zero_e_evt.delta_target_loss_total: 3.102396
- zero_e_evt.delta_source_loss_total: 4.045446

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
