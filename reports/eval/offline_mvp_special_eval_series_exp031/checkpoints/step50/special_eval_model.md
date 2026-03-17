# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.431576
- loss_acoustic: 6.772564
- loss_event: 5.211109
- loss_text_aux: 0.194365
- loss_text_aux_effective: 0.194365
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.038814
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.223475
- z_art_delta_abs_mean: 0.001251
- event_prob_mean: 0.481437
- event_presence_prob_mean: 0.568085
- event_delta_prob_mean: 0.498011
- event_rise_prob_mean: 0.46428
- event_fall_prob_mean: 0.490306
- event_energy_prob_mean: 0.533321
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.149937
- acoustic_energy_mean: -4.395501
- acoustic_delta_abs_mean: 0.055335
- text_aux_abs_mean: 0.399851

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.515603
- loss_acoustic: 2.809559
- loss_event: 5.271993
- loss_text_aux: 0.348275
- loss_text_aux_effective: 0.348275
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.233168
- z_art_delta_abs_mean: 0.00049
- event_prob_mean: 0.479355
- event_presence_prob_mean: 0.565901
- event_delta_prob_mean: 0.503042
- event_rise_prob_mean: 0.458775
- event_fall_prob_mean: 0.494965
- event_energy_prob_mean: 0.528596
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.163285
- acoustic_energy_mean: -4.459879
- acoustic_delta_abs_mean: 0.049129
- text_aux_abs_mean: 0.4048

## 对比
- delta_loss_total: -3.915973
- delta_loss_acoustic: -3.963005
- delta_loss_event: 0.060884
- delta_loss_text_aux: 0.15391
- delta_loss_text_aux_effective: 0.15391
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.038814
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.009693
- delta_z_art_delta_abs_mean: -0.000761
- delta_event_prob_mean: -0.002082
- delta_event_presence_prob_mean: -0.002184
- delta_event_delta_prob_mean: 0.005031
- delta_event_rise_prob_mean: -0.005505
- delta_event_fall_prob_mean: 0.004659
- delta_event_energy_prob_mean: -0.004725
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.013348
- delta_acoustic_energy_mean: -0.064378
- delta_acoustic_delta_abs_mean: -0.006206
- delta_text_aux_abs_mean: 0.004949

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
