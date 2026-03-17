# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-015-offline-mvp-b1-100step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 50, 100]
- checkpoint_count: 4

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step10.pt
- target_validation.loss_total: 19.729883
- target_special_eval.loss_total: 15.867836
- delta_loss_total: -3.862047
- delta_loss_text_aux: 0.222953
- target_validation.event_prob_mean: 0.500847
- target_special_eval.event_prob_mean: 0.500485

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step20.pt
- target_validation.loss_total: 15.784263
- target_special_eval.loss_total: 11.882978
- delta_loss_total: -3.901285
- delta_loss_text_aux: 0.320496
- target_validation.event_prob_mean: 0.49253
- target_special_eval.event_prob_mean: 0.491771

### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step50.pt
- target_validation.loss_total: 9.470963
- target_special_eval.loss_total: 5.650607
- delta_loss_total: -3.820356
- delta_loss_text_aux: 0.525018
- target_validation.event_prob_mean: 0.46127
- target_special_eval.event_prob_mean: 0.45846

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step100.pt
- target_validation.loss_total: 2.670612
- target_special_eval.loss_total: 2.886814
- delta_loss_total: 0.216202
- delta_loss_text_aux: 0.310898
- target_validation.event_prob_mean: 0.440296
- target_special_eval.event_prob_mean: 0.431139

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
