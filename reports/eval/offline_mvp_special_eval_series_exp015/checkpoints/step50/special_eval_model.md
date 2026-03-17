# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 9.470963
- loss_acoustic: 6.849853
- loss_event: 5.171181
- loss_text_aux: 0.172962
- z_art_abs_mean: 0.156806
- event_prob_mean: 0.46127
- acoustic_abs_mean: 1.166051
- text_aux_abs_mean: 0.364237

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.650607
- loss_acoustic: 2.904229
- loss_event: 5.212624
- loss_text_aux: 0.69798
- z_art_abs_mean: 0.165938
- event_prob_mean: 0.45846
- acoustic_abs_mean: 1.175828
- text_aux_abs_mean: 0.366069

## 对比
- delta_loss_total: -3.820356
- delta_loss_acoustic: -3.945624
- delta_loss_event: 0.041443
- delta_loss_text_aux: 0.525018
- delta_z_art_abs_mean: 0.009132
- delta_event_prob_mean: -0.00281
- delta_acoustic_abs_mean: 0.009777
- delta_text_aux_abs_mean: 0.001832

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
