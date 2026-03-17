# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 19.729883
- loss_acoustic: 16.95789
- loss_event: 5.504408
- loss_text_aux: 0.097273
- z_art_abs_mean: 0.088431
- event_prob_mean: 0.500847
- acoustic_abs_mean: 0.184914
- text_aux_abs_mean: 0.11121

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.867836
- loss_acoustic: 13.052799
- loss_event: 5.501609
- loss_text_aux: 0.320226
- z_art_abs_mean: 0.091144
- event_prob_mean: 0.500485
- acoustic_abs_mean: 0.185761
- text_aux_abs_mean: 0.111308

## 对比
- delta_loss_total: -3.862047
- delta_loss_acoustic: -3.905091
- delta_loss_event: -0.002799
- delta_loss_text_aux: 0.222953
- delta_z_art_abs_mean: 0.002713
- delta_event_prob_mean: -0.000362
- delta_acoustic_abs_mean: 0.000847
- delta_text_aux_abs_mean: 9.8e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
