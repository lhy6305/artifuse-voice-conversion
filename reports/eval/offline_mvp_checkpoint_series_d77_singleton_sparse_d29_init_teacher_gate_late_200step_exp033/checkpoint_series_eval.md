# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d77_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/checkpoints/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.step50.pt
- baseline.target_loss_total: 2.298601
- baseline.source_loss_total: 2.206601
- zero_z_art.delta_target_loss_total: 0.402836
- zero_z_art.delta_source_loss_total: 0.468836
- zero_e_evt.delta_target_loss_total: 2.689036
- zero_e_evt.delta_source_loss_total: 3.754628

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/checkpoints/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.step100.pt
- baseline.target_loss_total: 2.191997
- baseline.source_loss_total: 2.073611
- zero_z_art.delta_target_loss_total: 0.460361
- zero_z_art.delta_source_loss_total: 0.500305
- zero_e_evt.delta_target_loss_total: 2.145994
- zero_e_evt.delta_source_loss_total: 2.840839

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/checkpoints/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.step150.pt
- baseline.target_loss_total: 2.145315
- baseline.source_loss_total: 2.026206
- zero_z_art.delta_target_loss_total: 0.39523
- zero_z_art.delta_source_loss_total: 0.396588
- zero_e_evt.delta_target_loss_total: 1.736167
- zero_e_evt.delta_source_loss_total: 2.181825

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/checkpoints/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.step200.pt
- baseline.target_loss_total: 2.104891
- baseline.source_loss_total: 1.9694
- zero_z_art.delta_target_loss_total: 0.465426
- zero_z_art.delta_source_loss_total: 0.460403
- zero_e_evt.delta_target_loss_total: 1.832783
- zero_e_evt.delta_source_loss_total: 2.257209

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
