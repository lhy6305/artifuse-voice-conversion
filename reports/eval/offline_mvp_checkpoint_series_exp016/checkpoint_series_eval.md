# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_count: 10

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step10.pt
- baseline.target_loss_total: 20.467522
- baseline.source_loss_total: 27.102059
- zero_z_art.delta_target_loss_total: 0.097325
- zero_z_art.delta_source_loss_total: 0.132593
- zero_e_evt.delta_target_loss_total: 1.293285
- zero_e_evt.delta_source_loss_total: 1.709092

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step20.pt
- baseline.target_loss_total: 16.381277
- baseline.source_loss_total: 21.425019
- zero_z_art.delta_target_loss_total: 0.207288
- zero_z_art.delta_source_loss_total: 0.298636
- zero_e_evt.delta_target_loss_total: 1.733764
- zero_e_evt.delta_source_loss_total: 2.452784

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step30.pt
- baseline.target_loss_total: 11.940641
- baseline.source_loss_total: 14.458356
- zero_z_art.delta_target_loss_total: 0.248124
- zero_z_art.delta_source_loss_total: 0.446821
- zero_e_evt.delta_target_loss_total: 1.567714
- zero_e_evt.delta_source_loss_total: 2.670388

### step 40
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step40.pt
- baseline.target_loss_total: 9.441719
- baseline.source_loss_total: 8.607175
- zero_z_art.delta_target_loss_total: 0.023801
- zero_z_art.delta_source_loss_total: 0.35496
- zero_e_evt.delta_target_loss_total: 0.372475
- zero_e_evt.delta_source_loss_total: 1.795708

### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step50.pt
- baseline.target_loss_total: 9.419272
- baseline.source_loss_total: 6.876526
- zero_z_art.delta_target_loss_total: -0.173211
- zero_z_art.delta_source_loss_total: 0.20373
- zero_e_evt.delta_target_loss_total: -0.519059
- zero_e_evt.delta_source_loss_total: 1.102229

### step 60
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step60.pt
- baseline.target_loss_total: 7.98942
- baseline.source_loss_total: 6.992478
- zero_z_art.delta_target_loss_total: 0.218862
- zero_z_art.delta_source_loss_total: 0.272493
- zero_e_evt.delta_target_loss_total: 0.272295
- zero_e_evt.delta_source_loss_total: 1.874387

### step 70
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step70.pt
- baseline.target_loss_total: 6.060462
- baseline.source_loss_total: 5.759219
- zero_z_art.delta_target_loss_total: 0.7084
- zero_z_art.delta_source_loss_total: 0.335482
- zero_e_evt.delta_target_loss_total: 0.351807
- zero_e_evt.delta_source_loss_total: 1.445927

### step 80
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step80.pt
- baseline.target_loss_total: 3.550643
- baseline.source_loss_total: 3.985675
- zero_z_art.delta_target_loss_total: 0.917928
- zero_z_art.delta_source_loss_total: 0.717135
- zero_e_evt.delta_target_loss_total: 1.468729
- zero_e_evt.delta_source_loss_total: 0.840534

### step 90
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step90.pt
- baseline.target_loss_total: 3.382649
- baseline.source_loss_total: 2.822669
- zero_z_art.delta_target_loss_total: -0.164851
- zero_z_art.delta_source_loss_total: 1.083126
- zero_e_evt.delta_target_loss_total: 1.740804
- zero_e_evt.delta_source_loss_total: 1.230089

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step100.pt
- baseline.target_loss_total: 2.680581
- baseline.source_loss_total: 2.686611
- zero_z_art.delta_target_loss_total: 1.330542
- zero_z_art.delta_source_loss_total: 1.979376
- zero_e_evt.delta_target_loss_total: 1.408664
- zero_e_evt.delta_source_loss_total: 1.011982

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
