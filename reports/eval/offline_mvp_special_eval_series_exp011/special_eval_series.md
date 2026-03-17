# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-011-offline-mvp-large-scale-500.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- selected_steps: [25, 100, 250, 500]
- checkpoint_count: 4

## checkpoints
### step 25
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step25.pt
- target_validation.loss_total: 13.585217
- target_special_eval.loss_total: 9.707916
- delta_loss_total: -3.877301
- delta_loss_text_aux: 0.634326
- target_validation.event_prob_mean: 0.487313
- target_special_eval.event_prob_mean: 0.486317
- delta_event_presence_prob_mean: -0.000977
- delta_event_fall_prob_mean: -0.00117
- delta_event_energy_prob_mean: -0.000934
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.000399
- delta_acoustic_energy_mean: -0.006891
- delta_acoustic_delta_abs_mean: 0.002468

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step100.pt
- target_validation.loss_total: 2.661784
- target_special_eval.loss_total: 2.924799
- delta_loss_total: 0.263015
- delta_loss_text_aux: 0.537801
- target_validation.event_prob_mean: 0.43997
- target_special_eval.event_prob_mean: 0.43091
- delta_event_presence_prob_mean: -0.018794
- delta_event_fall_prob_mean: -0.012542
- delta_event_energy_prob_mean: -0.017669
- delta_event_presence_peak_ratio: 0.113981
- delta_z_art_delta_abs_mean: -0.001077
- delta_acoustic_energy_mean: -0.563396
- delta_acoustic_delta_abs_mean: -0.001693

### step 250
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step250.pt
- target_validation.loss_total: 1.862349
- target_special_eval.loss_total: 2.236273
- delta_loss_total: 0.373924
- delta_loss_text_aux: 0.539412
- target_validation.event_prob_mean: 0.417956
- target_special_eval.event_prob_mean: 0.393636
- delta_event_presence_prob_mean: -0.04756
- delta_event_fall_prob_mean: 0.003346
- delta_event_energy_prob_mean: -0.028077
- delta_event_presence_peak_ratio: -0.015076
- delta_z_art_delta_abs_mean: 0.001934
- delta_acoustic_energy_mean: -0.003595
- delta_acoustic_delta_abs_mean: 0.005596

### step 500
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step500.pt
- target_validation.loss_total: 1.752648
- target_special_eval.loss_total: 2.118624
- delta_loss_total: 0.365976
- delta_loss_text_aux: 0.491746
- target_validation.event_prob_mean: 0.402903
- target_special_eval.event_prob_mean: 0.40301
- delta_event_presence_prob_mean: -0.048061
- delta_event_fall_prob_mean: 0.00579
- delta_event_energy_prob_mean: -0.01794
- delta_event_presence_peak_ratio: -0.02488
- delta_z_art_delta_abs_mean: -0.000698
- delta_acoustic_energy_mean: -0.043731
- delta_acoustic_delta_abs_mean: -0.00239

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
