# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.310667
- loss_acoustic: 6.585896
- loss_event: 5.323493
- loss_text_aux: 0.248114
- loss_text_aux_effective: 0.248114
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035916
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.220917
- z_art_delta_abs_mean: 0.001039
- event_prob_mean: 0.49267
- event_presence_prob_mean: 0.56201
- event_delta_prob_mean: 0.532927
- event_rise_prob_mean: 0.46816
- event_fall_prob_mean: 0.519174
- event_energy_prob_mean: 0.518007
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.877742
- acoustic_energy_mean: -3.373396
- acoustic_delta_abs_mean: 0.061214
- text_aux_abs_mean: 0.379755

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.20707
- loss_acoustic: 2.457443
- loss_event: 5.359731
- loss_text_aux: 0.347448
- loss_text_aux_effective: 0.347448
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.228543
- z_art_delta_abs_mean: 0.00034
- event_prob_mean: 0.491573
- event_presence_prob_mean: 0.56139
- event_delta_prob_mean: 0.537487
- event_rise_prob_mean: 0.464392
- event_fall_prob_mean: 0.523912
- event_energy_prob_mean: 0.513903
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884278
- acoustic_energy_mean: -3.397133
- acoustic_delta_abs_mean: 0.066023
- text_aux_abs_mean: 0.382021

## 对比
- delta_loss_total: -4.103597
- delta_loss_acoustic: -4.128453
- delta_loss_event: 0.036238
- delta_loss_text_aux: 0.099334
- delta_loss_text_aux_effective: 0.099334
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035916
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.007626
- delta_z_art_delta_abs_mean: -0.000699
- delta_event_prob_mean: -0.001097
- delta_event_presence_prob_mean: -0.00062
- delta_event_delta_prob_mean: 0.00456
- delta_event_rise_prob_mean: -0.003768
- delta_event_fall_prob_mean: 0.004738
- delta_event_energy_prob_mean: -0.004104
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006536
- delta_acoustic_energy_mean: -0.023737
- delta_acoustic_delta_abs_mean: 0.004809
- delta_text_aux_abs_mean: 0.002266

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
