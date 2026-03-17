# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d27_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d27_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_exp044/checkpoints/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.step10.pt
- baseline.target_loss_total: 2.584663
- baseline.source_loss_total: 2.57089
- zero_z_art.delta_target_loss_total: 0.379443
- zero_z_art.delta_source_loss_total: 0.419197
- zero_e_evt.delta_target_loss_total: 2.89979
- zero_e_evt.delta_source_loss_total: 3.533133

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d27_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_exp044/checkpoints/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.step20.pt
- baseline.target_loss_total: 2.478063
- baseline.source_loss_total: 2.471555
- zero_z_art.delta_target_loss_total: 0.356843
- zero_z_art.delta_source_loss_total: 0.399543
- zero_e_evt.delta_target_loss_total: 2.863938
- zero_e_evt.delta_source_loss_total: 3.71847

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
