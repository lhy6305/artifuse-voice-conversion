# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-013-offline-mvp-evt-a1-large-scale.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- selected_steps: [25, 100, 250, 500]
- checkpoint_count: 4

## checkpoints
### step 25
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step25.pt
- target_validation.loss_total: 13.587198
- target_special_eval.loss_total: 9.704168
- delta_loss_total: -3.88303
- delta_loss_text_aux: 0.635188
- target_validation.event_prob_mean: 0.487213
- target_special_eval.event_prob_mean: 0.486252

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step100.pt
- target_validation.loss_total: 2.685433
- target_special_eval.loss_total: 2.893407
- delta_loss_total: 0.207974
- delta_loss_text_aux: 0.517064
- target_validation.event_prob_mean: 0.435112
- target_special_eval.event_prob_mean: 0.427426

### step 250
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step250.pt
- target_validation.loss_total: 2.016988
- target_special_eval.loss_total: 2.292754
- delta_loss_total: 0.275766
- delta_loss_text_aux: 0.555432
- target_validation.event_prob_mean: 0.417603
- target_special_eval.event_prob_mean: 0.390648

### step 500
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step500.pt
- target_validation.loss_total: 1.903484
- target_special_eval.loss_total: 2.192053
- delta_loss_total: 0.288569
- delta_loss_text_aux: 0.507014
- target_validation.event_prob_mean: 0.403894
- target_special_eval.event_prob_mean: 0.405813

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
