# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d43_round1_1_d7_init_d10_teacher_consistency_highproximity_relaxed_gate_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d43_highproximity_relaxed_gate_exp060/checkpoints/EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.58299
- baseline.source_loss_total: 2.567212
- zero_z_art.delta_target_loss_total: 0.396639
- zero_z_art.delta_source_loss_total: 0.441585
- zero_e_evt.delta_target_loss_total: 2.956201
- zero_e_evt.delta_source_loss_total: 3.631546

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d43_highproximity_relaxed_gate_exp060/checkpoints/EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.476013
- baseline.source_loss_total: 2.471677
- zero_z_art.delta_target_loss_total: 0.374309
- zero_z_art.delta_source_loss_total: 0.419542
- zero_e_evt.delta_target_loss_total: 2.927122
- zero_e_evt.delta_source_loss_total: 3.81363

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
