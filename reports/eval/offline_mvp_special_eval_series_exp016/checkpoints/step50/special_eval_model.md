# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 9.464871
- loss_acoustic: 6.846429
- loss_event: 5.170455
- loss_text_aux: 0.161442
- z_art_abs_mean: 0.157006
- event_prob_mean: 0.461112
- acoustic_abs_mean: 1.166
- text_aux_abs_mean: 0.346574

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.592163
- loss_acoustic: 2.901947
- loss_event: 5.211816
- loss_text_aux: 0.419193
- z_art_abs_mean: 0.166152
- event_prob_mean: 0.458311
- acoustic_abs_mean: 1.175766
- text_aux_abs_mean: 0.34881

## 对比
- delta_loss_total: -3.872708
- delta_loss_acoustic: -3.944482
- delta_loss_event: 0.041361
- delta_loss_text_aux: 0.257751
- delta_z_art_abs_mean: 0.009146
- delta_event_prob_mean: -0.002801
- delta_acoustic_abs_mean: 0.009766
- delta_text_aux_abs_mean: 0.002236

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
