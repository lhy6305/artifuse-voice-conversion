# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 50, 100]
- checkpoint_count: 4

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step10.pt
- target_validation.loss_total: 19.746407
- target_special_eval.loss_total: 15.83483
- delta_loss_total: -3.911577
- delta_loss_text_aux: -0.024686
- target_validation.event_prob_mean: 0.500847
- target_special_eval.event_prob_mean: 0.500485

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step20.pt
- target_validation.loss_total: 15.79531
- target_special_eval.loss_total: 11.838068
- delta_loss_total: -3.957242
- delta_loss_text_aux: 0.040963
- target_validation.event_prob_mean: 0.492527
- target_special_eval.event_prob_mean: 0.491768

### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step50.pt
- target_validation.loss_total: 9.464871
- target_special_eval.loss_total: 5.592163
- delta_loss_total: -3.872708
- delta_loss_text_aux: 0.257751
- target_validation.event_prob_mean: 0.461112
- target_special_eval.event_prob_mean: 0.458311

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step100.pt
- target_validation.loss_total: 2.677671
- target_special_eval.loss_total: 2.863008
- delta_loss_total: 0.185337
- delta_loss_text_aux: 0.142376
- target_validation.event_prob_mean: 0.439741
- target_special_eval.event_prob_mean: 0.430695

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
