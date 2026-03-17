# offline MVP checkpoint 系列消融汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_smallscale_longer.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-008-offline-mvp-longer-smallscale.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_count: 4

## checkpoints
### step 5
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-008-offline-mvp-longer-smallscale.step5.pt
- baseline.target_loss_total: 21.312295
- baseline.source_loss_total: 28.314068
- zero_z_art.delta_target_loss_total: -0.004283
- zero_z_art.delta_source_loss_total: -0.008403
- zero_e_evt.delta_target_loss_total: 0.290621
- zero_e_evt.delta_source_loss_total: 0.394811

### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-008-offline-mvp-longer-smallscale.step10.pt
- baseline.target_loss_total: 19.493267
- baseline.source_loss_total: 25.83994
- zero_z_art.delta_target_loss_total: 0.020028
- zero_z_art.delta_source_loss_total: 0.024396
- zero_e_evt.delta_target_loss_total: 0.62501
- zero_e_evt.delta_source_loss_total: 0.861151

### step 15
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-008-offline-mvp-longer-smallscale.step15.pt
- baseline.target_loss_total: 17.565876
- baseline.source_loss_total: 23.149627
- zero_z_art.delta_target_loss_total: 0.046879
- zero_z_art.delta_source_loss_total: 0.063001
- zero_e_evt.delta_target_loss_total: 0.868924
- zero_e_evt.delta_source_loss_total: 1.231779

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-008-offline-mvp-longer-smallscale.step20.pt
- baseline.target_loss_total: 15.533262
- baseline.source_loss_total: 20.202567
- zero_z_art.delta_target_loss_total: 0.079066
- zero_z_art.delta_source_loss_total: 0.114091
- zero_e_evt.delta_target_loss_total: 1.015739
- zero_e_evt.delta_source_loss_total: 1.504668

## notes
- Checkpoint-series evaluation summarizes z_art / e_evt ablation deltas across saved checkpoints.
- Only checkpoints referenced by experiment metrics.training_run.artifacts.checkpoint_paths are included.
