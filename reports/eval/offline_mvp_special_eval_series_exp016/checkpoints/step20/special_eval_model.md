# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 15.79531
- loss_acoustic: 13.033406
- loss_event: 5.450413
- loss_text_aux: 0.181239
- z_art_abs_mean: 0.134164
- event_prob_mean: 0.492527
- acoustic_abs_mean: 0.409508
- text_aux_abs_mean: 0.167342

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.838068
- loss_acoustic: 9.064953
- loss_event: 5.456947
- loss_text_aux: 0.222202
- z_art_abs_mean: 0.138757
- event_prob_mean: 0.491768
- acoustic_abs_mean: 0.411579
- text_aux_abs_mean: 0.167659

## 对比
- delta_loss_total: -3.957242
- delta_loss_acoustic: -3.968453
- delta_loss_event: 0.006534
- delta_loss_text_aux: 0.040963
- delta_z_art_abs_mean: 0.004593
- delta_event_prob_mean: -0.000759
- delta_acoustic_abs_mean: 0.002071
- delta_text_aux_abs_mean: 0.000317

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
