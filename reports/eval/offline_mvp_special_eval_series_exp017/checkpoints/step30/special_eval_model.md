# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.601516
- loss_acoustic: 8.8573
- loss_event: 5.372972
- loss_text_aux: 0.223194
- loss_text_aux_effective: 0.223194
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035546
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.162891
- z_art_delta_abs_mean: 0.000812
- event_prob_mean: 0.502684
- event_presence_prob_mean: 0.556197
- event_delta_prob_mean: 0.53308
- event_rise_prob_mean: 0.491207
- event_fall_prob_mean: 0.53074
- event_energy_prob_mean: 0.521543
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.575701
- acoustic_energy_mean: -2.121134
- acoustic_delta_abs_mean: 0.071943
- text_aux_abs_mean: 0.268029

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.637702
- loss_acoustic: 4.888872
- loss_event: 5.407542
- loss_text_aux: 0.22409
- loss_text_aux_effective: 0.22409
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.166691
- z_art_delta_abs_mean: 0.000301
- event_prob_mean: 0.501992
- event_presence_prob_mean: 0.555756
- event_delta_prob_mean: 0.536162
- event_rise_prob_mean: 0.489187
- event_fall_prob_mean: 0.535192
- event_energy_prob_mean: 0.518204
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.578834
- acoustic_energy_mean: -2.135914
- acoustic_delta_abs_mean: 0.069441
- text_aux_abs_mean: 0.269904

## 对比
- delta_loss_total: -3.963814
- delta_loss_acoustic: -3.968428
- delta_loss_event: 0.03457
- delta_loss_text_aux: 0.000896
- delta_loss_text_aux_effective: 0.000896
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035546
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.0038
- delta_z_art_delta_abs_mean: -0.000511
- delta_event_prob_mean: -0.000692
- delta_event_presence_prob_mean: -0.000441
- delta_event_delta_prob_mean: 0.003082
- delta_event_rise_prob_mean: -0.00202
- delta_event_fall_prob_mean: 0.004452
- delta_event_energy_prob_mean: -0.003339
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.003133
- delta_acoustic_energy_mean: -0.01478
- delta_acoustic_delta_abs_mean: -0.002502
- delta_text_aux_abs_mean: 0.001875

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
