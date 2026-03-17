# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.689418
- loss_acoustic: 1.218785
- loss_event: 4.848508
- loss_text_aux: 0.111225
- loss_text_aux_effective: 0.111225
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048295
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240273
- z_art_delta_abs_mean: 0.009039
- event_prob_mean: 0.46194
- event_presence_prob_mean: 0.582168
- event_delta_prob_mean: 0.393296
- event_rise_prob_mean: 0.471791
- event_fall_prob_mean: 0.427617
- event_energy_prob_mean: 0.560203
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838567
- acoustic_energy_mean: -3.19425
- acoustic_delta_abs_mean: 0.028083
- text_aux_abs_mean: 0.215691

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.38217
- loss_acoustic: 0.796278
- loss_event: 5.076433
- loss_text_aux: 0.214155
- loss_text_aux_effective: 0.214155
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.171835
- z_art_delta_abs_mean: 0.006056
- event_prob_mean: 0.451685
- event_presence_prob_mean: 0.557398
- event_delta_prob_mean: 0.405821
- event_rise_prob_mean: 0.453124
- event_fall_prob_mean: 0.446698
- event_energy_prob_mean: 0.540003
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073456
- acoustic_energy_mean: -4.168254
- acoustic_delta_abs_mean: 0.007807
- text_aux_abs_mean: 0.276502

## 对比
- delta_loss_total: -0.307248
- delta_loss_acoustic: -0.422507
- delta_loss_event: 0.227925
- delta_loss_text_aux: 0.10293
- delta_loss_text_aux_effective: 0.10293
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048295
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.068438
- delta_z_art_delta_abs_mean: -0.002983
- delta_event_prob_mean: -0.010255
- delta_event_presence_prob_mean: -0.02477
- delta_event_delta_prob_mean: 0.012525
- delta_event_rise_prob_mean: -0.018667
- delta_event_fall_prob_mean: 0.019081
- delta_event_energy_prob_mean: -0.0202
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234889
- delta_acoustic_energy_mean: -0.974004
- delta_acoustic_delta_abs_mean: -0.020276
- delta_text_aux_abs_mean: 0.060811

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
