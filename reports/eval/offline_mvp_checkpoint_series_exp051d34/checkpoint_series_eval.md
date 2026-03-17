# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d34_round1_1_d22_init_d33_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d34_d22_init_d33_teacher_cross_anchor_fused_hidden_exp051/checkpoints/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.step10.pt
- baseline.target_loss_total: 2.392564
- baseline.source_loss_total: 2.355399
- zero_z_art.delta_target_loss_total: 0.276536
- zero_z_art.delta_source_loss_total: 0.314347
- zero_e_evt.delta_target_loss_total: 2.562634
- zero_e_evt.delta_source_loss_total: 3.503777

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d34_d22_init_d33_teacher_cross_anchor_fused_hidden_exp051/checkpoints/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.step20.pt
- baseline.target_loss_total: 2.356601
- baseline.source_loss_total: 2.291224
- zero_z_art.delta_target_loss_total: 0.310002
- zero_z_art.delta_source_loss_total: 0.370338
- zero_e_evt.delta_target_loss_total: 2.633041
- zero_e_evt.delta_source_loss_total: 3.682444

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
