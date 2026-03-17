# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d44_round1_1_d7_init_d10_teacher_consistency_relaxed_none_other_gate_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-061-offline-mvp-d44-round1-1-d7-init-d10-teacher-consistency-relaxed-none-other-gate-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d44_relaxed_none_other_gate_exp061/checkpoints/EXP-20260316-061-offline-mvp-d44-round1-1-d7-init-d10-teacher-consistency-relaxed-none-other-gate-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.601569
- baseline.source_loss_total: 2.593792
- zero_z_art.delta_target_loss_total: 0.463527
- zero_z_art.delta_source_loss_total: 0.518274
- zero_e_evt.delta_target_loss_total: 3.060794
- zero_e_evt.delta_source_loss_total: 3.765768

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d44_relaxed_none_other_gate_exp061/checkpoints/EXP-20260316-061-offline-mvp-d44-round1-1-d7-init-d10-teacher-consistency-relaxed-none-other-gate-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.51739
- baseline.source_loss_total: 2.476544
- zero_z_art.delta_target_loss_total: 0.422595
- zero_z_art.delta_source_loss_total: 0.490487
- zero_e_evt.delta_target_loss_total: 3.100172
- zero_e_evt.delta_source_loss_total: 4.075521

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
