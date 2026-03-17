# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-014-offline-mvp-b1-smallscale.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 15.784263
- loss_acoustic: 13.033449
- loss_event: 5.450412
- loss_text_aux: 0.125794
- z_art_abs_mean: 0.134086
- event_prob_mean: 0.49253
- acoustic_abs_mean: 0.409578
- text_aux_abs_mean: 0.216895

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.882978
- loss_acoustic: 9.065033
- loss_event: 5.456971
- loss_text_aux: 0.44629
- z_art_abs_mean: 0.138682
- event_prob_mean: 0.491771
- acoustic_abs_mean: 0.41165
- text_aux_abs_mean: 0.217875

## 对比
- delta_loss_total: -3.901285
- delta_loss_acoustic: -3.968416
- delta_loss_event: 0.006559
- delta_loss_text_aux: 0.320496
- delta_z_art_abs_mean: 0.004596
- delta_event_prob_mean: -0.000759
- delta_acoustic_abs_mean: 0.002072
- delta_text_aux_abs_mean: 0.00098

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
