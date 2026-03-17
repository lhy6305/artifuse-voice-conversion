# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 2.661784
- loss_acoustic: 0.311434
- loss_event: 4.678802
- loss_text_aux: 0.018797
- z_art_abs_mean: 0.281659
- z_art_delta_abs_mean: 0.008987
- event_prob_mean: 0.43997
- event_presence_prob_mean: 0.584674
- event_delta_prob_mean: 0.317876
- event_rise_prob_mean: 0.476813
- event_fall_prob_mean: 0.524054
- event_energy_prob_mean: 0.58273
- event_presence_peak_ratio: 0.840437
- acoustic_abs_mean: 0.907375
- acoustic_energy_mean: -3.522275
- acoustic_delta_abs_mean: 0.008404
- text_aux_abs_mean: 0.175301

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.924799
- loss_acoustic: 0.355776
- loss_event: 4.90275
- loss_text_aux: 0.556598
- z_art_abs_mean: 0.231596
- z_art_delta_abs_mean: 0.00791
- event_prob_mean: 0.43091
- event_presence_prob_mean: 0.56588
- event_delta_prob_mean: 0.323077
- event_rise_prob_mean: 0.473498
- event_fall_prob_mean: 0.511512
- event_energy_prob_mean: 0.565061
- event_presence_peak_ratio: 0.954418
- acoustic_abs_mean: 1.058748
- acoustic_energy_mean: -4.085671
- acoustic_delta_abs_mean: 0.006711
- text_aux_abs_mean: 0.180534

## 对比
- delta_loss_total: 0.263015
- delta_loss_acoustic: 0.044342
- delta_loss_event: 0.223948
- delta_loss_text_aux: 0.537801
- delta_z_art_abs_mean: -0.050063
- delta_z_art_delta_abs_mean: -0.001077
- delta_event_prob_mean: -0.00906
- delta_event_presence_prob_mean: -0.018794
- delta_event_delta_prob_mean: 0.005201
- delta_event_rise_prob_mean: -0.003315
- delta_event_fall_prob_mean: -0.012542
- delta_event_energy_prob_mean: -0.017669
- delta_event_presence_peak_ratio: 0.113981
- delta_acoustic_abs_mean: 0.151373
- delta_acoustic_energy_mean: -0.563396
- delta_acoustic_delta_abs_mean: -0.001693
- delta_text_aux_abs_mean: 0.005233

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
