# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d48_round1_1_d7_init_phase_teacher_family_softweight_handoff_d33step10_to_d29_late_targetshape_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-002-offline-mvp-d48-round1-1-d7-init-phase-teacher-family-softweight-handoff-d33step10-to-d29-late-targetshape-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d48_phase_teacher_family_softweight_exp002/checkpoints/EXP-20260316-002-offline-mvp-d48-round1-1-d7-init-phase-teacher-family-softweight-handoff-d33step10-to-d29-late-targetshape-20step-calibration.step10.pt
- baseline.target_loss_total: 2.592714
- baseline.source_loss_total: 2.584
- zero_z_art.delta_target_loss_total: 0.42042
- zero_z_art.delta_source_loss_total: 0.470427
- zero_e_evt.delta_target_loss_total: 2.97141
- zero_e_evt.delta_source_loss_total: 3.625847

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d48_phase_teacher_family_softweight_exp002/checkpoints/EXP-20260316-002-offline-mvp-d48-round1-1-d7-init-phase-teacher-family-softweight-handoff-d33step10-to-d29-late-targetshape-20step-calibration.step20.pt
- baseline.target_loss_total: 2.51717
- baseline.source_loss_total: 2.466865
- zero_z_art.delta_target_loss_total: 0.407233
- zero_z_art.delta_source_loss_total: 0.487813
- zero_e_evt.delta_target_loss_total: 3.196309
- zero_e_evt.delta_source_loss_total: 4.2227

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
