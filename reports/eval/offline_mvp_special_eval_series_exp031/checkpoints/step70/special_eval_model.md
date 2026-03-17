# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.829919
- loss_acoustic: 3.302933
- loss_event: 4.970568
- loss_text_aux: 0.110895
- loss_text_aux_effective: 0.110895
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046538
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.192881
- z_art_delta_abs_mean: 0.004043
- event_prob_mean: 0.46925
- event_presence_prob_mean: 0.586123
- event_delta_prob_mean: 0.409754
- event_rise_prob_mean: 0.488109
- event_fall_prob_mean: 0.43682
- event_energy_prob_mean: 0.563688
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.933079
- acoustic_energy_mean: -3.62017
- acoustic_delta_abs_mean: 0.016314
- text_aux_abs_mean: 0.23579

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.122135
- loss_acoustic: 1.51198
- loss_event: 5.131319
- loss_text_aux: 0.211577
- loss_text_aux_effective: 0.211577
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.168899
- z_art_delta_abs_mean: 0.002725
- event_prob_mean: 0.462401
- event_presence_prob_mean: 0.572518
- event_delta_prob_mean: 0.416184
- event_rise_prob_mean: 0.474725
- event_fall_prob_mean: 0.447093
- event_energy_prob_mean: 0.55261
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.032017
- acoustic_energy_mean: -4.045604
- acoustic_delta_abs_mean: 0.008391
- text_aux_abs_mean: 0.262504

## 对比
- delta_loss_total: -1.707784
- delta_loss_acoustic: -1.790953
- delta_loss_event: 0.160751
- delta_loss_text_aux: 0.100682
- delta_loss_text_aux_effective: 0.100682
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046538
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.023982
- delta_z_art_delta_abs_mean: -0.001318
- delta_event_prob_mean: -0.006849
- delta_event_presence_prob_mean: -0.013605
- delta_event_delta_prob_mean: 0.00643
- delta_event_rise_prob_mean: -0.013384
- delta_event_fall_prob_mean: 0.010273
- delta_event_energy_prob_mean: -0.011078
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.098938
- delta_acoustic_energy_mean: -0.425434
- delta_acoustic_delta_abs_mean: -0.007923
- delta_text_aux_abs_mean: 0.026714

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
