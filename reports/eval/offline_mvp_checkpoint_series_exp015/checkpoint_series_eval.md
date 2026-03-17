# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-015-offline-mvp-b1-100step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_count: 10

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step10.pt
- baseline.target_loss_total: 20.455091
- baseline.source_loss_total: 27.10211
- zero_z_art.delta_target_loss_total: 0.097014
- zero_z_art.delta_source_loss_total: 0.132661
- zero_e_evt.delta_target_loss_total: 1.293825
- zero_e_evt.delta_source_loss_total: 1.70949

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step20.pt
- baseline.target_loss_total: 16.37399
- baseline.source_loss_total: 21.425115
- zero_z_art.delta_target_loss_total: 0.207014
- zero_z_art.delta_source_loss_total: 0.298836
- zero_e_evt.delta_target_loss_total: 1.733871
- zero_e_evt.delta_source_loss_total: 2.455121

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step30.pt
- baseline.target_loss_total: 11.942529
- baseline.source_loss_total: 14.461219
- zero_z_art.delta_target_loss_total: 0.248665
- zero_z_art.delta_source_loss_total: 0.447657
- zero_e_evt.delta_target_loss_total: 1.568373
- zero_e_evt.delta_source_loss_total: 2.677

### step 40
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step40.pt
- baseline.target_loss_total: 9.450107
- baseline.source_loss_total: 8.615387
- zero_z_art.delta_target_loss_total: 0.025216
- zero_z_art.delta_source_loss_total: 0.356673
- zero_e_evt.delta_target_loss_total: 0.373772
- zero_e_evt.delta_source_loss_total: 1.804284

### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step50.pt
- baseline.target_loss_total: 9.426597
- baseline.source_loss_total: 6.876946
- zero_z_art.delta_target_loss_total: -0.17391
- zero_z_art.delta_source_loss_total: 0.204594
- zero_e_evt.delta_target_loss_total: -0.521803
- zero_e_evt.delta_source_loss_total: 1.104932

### step 60
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step60.pt
- baseline.target_loss_total: 7.988705
- baseline.source_loss_total: 6.994324
- zero_z_art.delta_target_loss_total: 0.218725
- zero_z_art.delta_source_loss_total: 0.274261
- zero_e_evt.delta_target_loss_total: 0.269633
- zero_e_evt.delta_source_loss_total: 1.874161

### step 70
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step70.pt
- baseline.target_loss_total: 6.057245
- baseline.source_loss_total: 5.768098
- zero_z_art.delta_target_loss_total: 0.708298
- zero_z_art.delta_source_loss_total: 0.336892
- zero_e_evt.delta_target_loss_total: 0.352005
- zero_e_evt.delta_source_loss_total: 1.445787

### step 80
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step80.pt
- baseline.target_loss_total: 3.544307
- baseline.source_loss_total: 3.990637
- zero_z_art.delta_target_loss_total: 0.917957
- zero_z_art.delta_source_loss_total: 0.717538
- zero_e_evt.delta_target_loss_total: 1.466497
- zero_e_evt.delta_source_loss_total: 0.835429

### step 90
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step90.pt
- baseline.target_loss_total: 3.377886
- baseline.source_loss_total: 2.823662
- zero_z_art.delta_target_loss_total: -0.169832
- zero_z_art.delta_source_loss_total: 1.083875
- zero_e_evt.delta_target_loss_total: 1.734398
- zero_e_evt.delta_source_loss_total: 1.227729

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step100.pt
- baseline.target_loss_total: 2.676195
- baseline.source_loss_total: 2.689358
- zero_z_art.delta_target_loss_total: 1.332663
- zero_z_art.delta_source_loss_total: 1.997582
- zero_e_evt.delta_target_loss_total: 1.407506
- zero_e_evt.delta_source_loss_total: 1.005402

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
