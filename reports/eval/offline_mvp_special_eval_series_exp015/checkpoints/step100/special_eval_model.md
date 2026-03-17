# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 2.670612
- loss_acoustic: 0.316997
- loss_event: 4.679714
- loss_text_aux: 0.032697
- z_art_abs_mean: 0.281568
- event_prob_mean: 0.440296
- acoustic_abs_mean: 0.906629
- text_aux_abs_mean: 0.23975

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.886814
- loss_acoustic: 0.359928
- loss_event: 4.903627
- loss_text_aux: 0.343595
- z_art_abs_mean: 0.231217
- event_prob_mean: 0.431139
- acoustic_abs_mean: 1.059959
- text_aux_abs_mean: 0.269818

## 对比
- delta_loss_total: 0.216202
- delta_loss_acoustic: 0.042931
- delta_loss_event: 0.223913
- delta_loss_text_aux: 0.310898
- delta_z_art_abs_mean: -0.050351
- delta_event_prob_mean: -0.009157
- delta_acoustic_abs_mean: 0.15333
- delta_text_aux_abs_mean: 0.030068

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
