# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.589536
- loss_acoustic: 12.832235
- loss_event: 5.409707
- loss_text_aux: 0.196224
- loss_text_aux_effective: 0.196224
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036261
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.11504
- z_art_delta_abs_mean: 0.00064
- event_prob_mean: 0.507157
- event_presence_prob_mean: 0.542215
- event_delta_prob_mean: 0.527916
- event_rise_prob_mean: 0.512686
- event_fall_prob_mean: 0.52686
- event_energy_prob_mean: 0.524019
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.37273
- acoustic_energy_mean: -1.145745
- acoustic_delta_abs_mean: 0.152687
- text_aux_abs_mean: 0.181248

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.770295
- loss_acoustic: 9.020452
- loss_event: 5.44153
- loss_text_aux: 0.144132
- loss_text_aux_effective: 0.144132
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.117541
- z_art_delta_abs_mean: 0.000316
- event_prob_mean: 0.506651
- event_presence_prob_mean: 0.541532
- event_delta_prob_mean: 0.530004
- event_rise_prob_mean: 0.512276
- event_fall_prob_mean: 0.530376
- event_energy_prob_mean: 0.521243
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.374738
- acoustic_energy_mean: -1.153199
- acoustic_delta_abs_mean: 0.151929
- text_aux_abs_mean: 0.182259

## 对比
- delta_loss_total: -3.819241
- delta_loss_acoustic: -3.811783
- delta_loss_event: 0.031823
- delta_loss_text_aux: -0.052092
- delta_loss_text_aux_effective: -0.052092
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036261
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.002501
- delta_z_art_delta_abs_mean: -0.000324
- delta_event_prob_mean: -0.000506
- delta_event_presence_prob_mean: -0.000683
- delta_event_delta_prob_mean: 0.002088
- delta_event_rise_prob_mean: -0.00041
- delta_event_fall_prob_mean: 0.003516
- delta_event_energy_prob_mean: -0.002776
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002008
- delta_acoustic_energy_mean: -0.007454
- delta_acoustic_delta_abs_mean: -0.000758
- delta_text_aux_abs_mean: 0.001011

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
