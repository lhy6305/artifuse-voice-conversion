# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d59_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_teacher_gate_late_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d59_200step_exp014/checkpoints/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.step50.pt
- baseline.target_loss_total: 2.333717
- baseline.source_loss_total: 2.242224
- zero_z_art.delta_target_loss_total: 0.262747
- zero_z_art.delta_source_loss_total: 0.332041
- zero_e_evt.delta_target_loss_total: 2.590052
- zero_e_evt.delta_source_loss_total: 3.676603

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d59_200step_exp014/checkpoints/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.step100.pt
- baseline.target_loss_total: 2.208711
- baseline.source_loss_total: 2.096979
- zero_z_art.delta_target_loss_total: 0.328164
- zero_z_art.delta_source_loss_total: 0.39439
- zero_e_evt.delta_target_loss_total: 2.069441
- zero_e_evt.delta_source_loss_total: 2.815252

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d59_200step_exp014/checkpoints/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.step150.pt
- baseline.target_loss_total: 2.145679
- baseline.source_loss_total: 2.02956
- zero_z_art.delta_target_loss_total: 0.345357
- zero_z_art.delta_source_loss_total: 0.391492
- zero_e_evt.delta_target_loss_total: 1.971437
- zero_e_evt.delta_source_loss_total: 2.570875

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d59_200step_exp014/checkpoints/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.step200.pt
- baseline.target_loss_total: 2.125538
- baseline.source_loss_total: 2.003358
- zero_z_art.delta_target_loss_total: 0.311379
- zero_z_art.delta_source_loss_total: 0.341049
- zero_e_evt.delta_target_loss_total: 1.927875
- zero_e_evt.delta_source_loss_total: 2.459831

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
