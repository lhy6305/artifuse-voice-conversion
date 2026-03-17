# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d33_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_fused_hidden_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_200step_exp015/checkpoints/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.step50.pt
- baseline.target_loss_total: 2.379561
- baseline.source_loss_total: 2.319956
- zero_z_art.delta_target_loss_total: 0.388582
- zero_z_art.delta_source_loss_total: 0.457748
- zero_e_evt.delta_target_loss_total: 2.874014
- zero_e_evt.delta_source_loss_total: 4.02681

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_200step_exp015/checkpoints/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.step100.pt
- baseline.target_loss_total: 2.251813
- baseline.source_loss_total: 2.164776
- zero_z_art.delta_target_loss_total: 0.604163
- zero_z_art.delta_source_loss_total: 0.69612
- zero_e_evt.delta_target_loss_total: 2.354133
- zero_e_evt.delta_source_loss_total: 3.188451

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_200step_exp015/checkpoints/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.step150.pt
- baseline.target_loss_total: 2.167352
- baseline.source_loss_total: 2.070308
- zero_z_art.delta_target_loss_total: 0.664676
- zero_z_art.delta_source_loss_total: 0.749499
- zero_e_evt.delta_target_loss_total: 2.032546
- zero_e_evt.delta_source_loss_total: 2.612659

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_200step_exp015/checkpoints/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.step200.pt
- baseline.target_loss_total: 2.119283
- baseline.source_loss_total: 2.007893
- zero_z_art.delta_target_loss_total: 0.710849
- zero_z_art.delta_source_loss_total: 0.793456
- zero_e_evt.delta_target_loss_total: 1.9703
- zero_e_evt.delta_source_loss_total: 2.440004

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
