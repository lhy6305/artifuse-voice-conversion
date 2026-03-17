# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d21_round1_1_d10_final_consolidation_teacher_consistency_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step10.pt
- baseline.target_loss_total: 2.649265
- baseline.source_loss_total: 2.650403
- zero_z_art.delta_target_loss_total: 0.434276
- zero_z_art.delta_source_loss_total: 0.461311
- zero_e_evt.delta_target_loss_total: 2.80066
- zero_e_evt.delta_source_loss_total: 3.216414

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step20.pt
- baseline.target_loss_total: 2.538212
- baseline.source_loss_total: 2.517986
- zero_z_art.delta_target_loss_total: 0.454118
- zero_z_art.delta_source_loss_total: 0.514888
- zero_e_evt.delta_target_loss_total: 3.062874
- zero_e_evt.delta_source_loss_total: 3.933791

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step30.pt
- baseline.target_loss_total: 2.45345
- baseline.source_loss_total: 2.428683
- zero_z_art.delta_target_loss_total: 0.391864
- zero_z_art.delta_source_loss_total: 0.448064
- zero_e_evt.delta_target_loss_total: 2.919652
- zero_e_evt.delta_source_loss_total: 3.901355

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
