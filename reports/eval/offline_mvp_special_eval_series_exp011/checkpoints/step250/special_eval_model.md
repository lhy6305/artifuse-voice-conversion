# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step250.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 1.862349
- loss_acoustic: 0.081549
- loss_event: 3.532567
- loss_text_aux: 0.014018
- z_art_abs_mean: 0.713281
- z_art_delta_abs_mean: 0.014641
- event_prob_mean: 0.417956
- event_presence_prob_mean: 0.63069
- event_delta_prob_mean: 0.231436
- event_rise_prob_mean: 0.491212
- event_fall_prob_mean: 0.498656
- event_energy_prob_mean: 0.653023
- event_presence_peak_ratio: 0.632063
- acoustic_abs_mean: 0.951735
- acoustic_energy_mean: -3.640604
- acoustic_delta_abs_mean: 0.015999
- text_aux_abs_mean: 0.148913

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.236273
- loss_acoustic: 0.04791
- loss_event: 4.128834
- loss_text_aux: 0.55343
- z_art_abs_mean: 0.664749
- z_art_delta_abs_mean: 0.016575
- event_prob_mean: 0.393636
- event_presence_prob_mean: 0.58313
- event_delta_prob_mean: 0.25762
- event_rise_prob_mean: 0.506862
- event_fall_prob_mean: 0.502002
- event_energy_prob_mean: 0.624946
- event_presence_peak_ratio: 0.616987
- acoustic_abs_mean: 0.944628
- acoustic_energy_mean: -3.644199
- acoustic_delta_abs_mean: 0.021595
- text_aux_abs_mean: 0.181045

## 对比
- delta_loss_total: 0.373924
- delta_loss_acoustic: -0.033639
- delta_loss_event: 0.596267
- delta_loss_text_aux: 0.539412
- delta_z_art_abs_mean: -0.048532
- delta_z_art_delta_abs_mean: 0.001934
- delta_event_prob_mean: -0.02432
- delta_event_presence_prob_mean: -0.04756
- delta_event_delta_prob_mean: 0.026184
- delta_event_rise_prob_mean: 0.01565
- delta_event_fall_prob_mean: 0.003346
- delta_event_energy_prob_mean: -0.028077
- delta_event_presence_peak_ratio: -0.015076
- delta_acoustic_abs_mean: -0.007107
- delta_acoustic_energy_mean: -0.003595
- delta_acoustic_delta_abs_mean: 0.005596
- delta_text_aux_abs_mean: 0.032132

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
