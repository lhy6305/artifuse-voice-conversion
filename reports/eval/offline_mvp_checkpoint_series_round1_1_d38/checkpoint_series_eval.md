# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d38_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-055-offline-mvp-d38-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d38_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_fused_hidden_exp055/checkpoints/EXP-20260315-055-offline-mvp-d38-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.634861
- baseline.source_loss_total: 2.564948
- zero_z_art.delta_target_loss_total: 0.46347
- zero_z_art.delta_source_loss_total: 0.549882
- zero_e_evt.delta_target_loss_total: 3.224344
- zero_e_evt.delta_source_loss_total: 4.074445

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d38_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_fused_hidden_exp055/checkpoints/EXP-20260315-055-offline-mvp-d38-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.508994
- baseline.source_loss_total: 2.491982
- zero_z_art.delta_target_loss_total: 0.436892
- zero_z_art.delta_source_loss_total: 0.499317
- zero_e_evt.delta_target_loss_total: 3.096622
- zero_e_evt.delta_source_loss_total: 4.03492

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
