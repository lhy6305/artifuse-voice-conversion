# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.438085
- loss_acoustic: 6.777666
- loss_event: 5.205274
- loss_text_aux: 0.215709
- loss_text_aux_effective: 0.215709
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.038933
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.221582
- z_art_delta_abs_mean: 0.001267
- event_prob_mean: 0.481209
- event_presence_prob_mean: 0.571402
- event_delta_prob_mean: 0.497184
- event_rise_prob_mean: 0.463769
- event_fall_prob_mean: 0.48776
- event_energy_prob_mean: 0.535296
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.134908
- acoustic_energy_mean: -4.412826
- acoustic_delta_abs_mean: 0.024709
- text_aux_abs_mean: 0.436753

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.544355
- loss_acoustic: 2.833317
- loss_event: 5.26621
- loss_text_aux: 0.387636
- loss_text_aux_effective: 0.387636
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.231409
- z_art_delta_abs_mean: 0.000508
- event_prob_mean: 0.478998
- event_presence_prob_mean: 0.569177
- event_delta_prob_mean: 0.502164
- event_rise_prob_mean: 0.458017
- event_fall_prob_mean: 0.492234
- event_energy_prob_mean: 0.530503
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.148594
- acoustic_energy_mean: -4.480036
- acoustic_delta_abs_mean: 0.017874
- text_aux_abs_mean: 0.442474

## 对比
- delta_loss_total: -3.89373
- delta_loss_acoustic: -3.944349
- delta_loss_event: 0.060936
- delta_loss_text_aux: 0.171927
- delta_loss_text_aux_effective: 0.171927
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.038933
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.009827
- delta_z_art_delta_abs_mean: -0.000759
- delta_event_prob_mean: -0.002211
- delta_event_presence_prob_mean: -0.002225
- delta_event_delta_prob_mean: 0.00498
- delta_event_rise_prob_mean: -0.005752
- delta_event_fall_prob_mean: 0.004474
- delta_event_energy_prob_mean: -0.004793
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.013686
- delta_acoustic_energy_mean: -0.06721
- delta_acoustic_delta_abs_mean: -0.006835
- delta_text_aux_abs_mean: 0.005721

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
