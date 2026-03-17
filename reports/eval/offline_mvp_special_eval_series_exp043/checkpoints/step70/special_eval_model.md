# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d17_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_exp043/checkpoints/EXP-20260315-043-offline-mvp-d17-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-profile-late-only-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.829151
- loss_acoustic: 3.302474
- loss_event: 4.969937
- loss_text_aux: 0.1109
- loss_text_aux_effective: 0.1109
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046537
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.193594
- z_art_delta_abs_mean: 0.004051
- event_prob_mean: 0.469394
- event_presence_prob_mean: 0.587322
- event_delta_prob_mean: 0.4097
- event_rise_prob_mean: 0.488225
- event_fall_prob_mean: 0.436647
- event_energy_prob_mean: 0.563872
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.933111
- acoustic_energy_mean: -3.620554
- acoustic_delta_abs_mean: 0.01635
- text_aux_abs_mean: 0.235874

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.121997
- loss_acoustic: 1.511982
- loss_event: 5.131015
- loss_text_aux: 0.211618
- loss_text_aux_effective: 0.211618
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169598
- z_art_delta_abs_mean: 0.00273
- event_prob_mean: 0.462546
- event_presence_prob_mean: 0.573677
- event_delta_prob_mean: 0.416136
- event_rise_prob_mean: 0.474834
- event_fall_prob_mean: 0.446967
- event_energy_prob_mean: 0.552786
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.032093
- acoustic_energy_mean: -4.045963
- acoustic_delta_abs_mean: 0.008413
- text_aux_abs_mean: 0.262577

## 对比
- delta_loss_total: -1.707154
- delta_loss_acoustic: -1.790492
- delta_loss_event: 0.161078
- delta_loss_text_aux: 0.100718
- delta_loss_text_aux_effective: 0.100718
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046537
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.023996
- delta_z_art_delta_abs_mean: -0.001321
- delta_event_prob_mean: -0.006848
- delta_event_presence_prob_mean: -0.013645
- delta_event_delta_prob_mean: 0.006436
- delta_event_rise_prob_mean: -0.013391
- delta_event_fall_prob_mean: 0.01032
- delta_event_energy_prob_mean: -0.011086
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.098982
- delta_acoustic_energy_mean: -0.425409
- delta_acoustic_delta_abs_mean: -0.007937
- delta_text_aux_abs_mean: 0.026703

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
