# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427576
- loss_acoustic: 1.015889
- loss_event: 4.719746
- loss_text_aux: 0.117993
- loss_text_aux_effective: 0.117993
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051541
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.328391
- z_art_delta_abs_mean: 0.01272
- event_prob_mean: 0.459384
- event_presence_prob_mean: 0.601755
- event_delta_prob_mean: 0.364376
- event_rise_prob_mean: 0.472653
- event_fall_prob_mean: 0.413084
- event_energy_prob_mean: 0.576046
- event_presence_peak_ratio: 0.810316
- acoustic_abs_mean: 0.802462
- acoustic_energy_mean: -2.998565
- acoustic_delta_abs_mean: 0.045022
- text_aux_abs_mean: 0.222946

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.084407
- loss_acoustic: 0.523284
- loss_event: 5.022732
- loss_text_aux: 0.212532
- loss_text_aux_effective: 0.212532
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.22044
- z_art_delta_abs_mean: 0.009063
- event_prob_mean: 0.446767
- event_presence_prob_mean: 0.568929
- event_delta_prob_mean: 0.379809
- event_rise_prob_mean: 0.450008
- event_fall_prob_mean: 0.434062
- event_energy_prob_mean: 0.549062
- event_presence_peak_ratio: 0.948429
- acoustic_abs_mean: 1.056782
- acoustic_energy_mean: -4.000191
- acoustic_delta_abs_mean: 0.024061
- text_aux_abs_mean: 0.274863

## 对比
- delta_loss_total: -0.343169
- delta_loss_acoustic: -0.492605
- delta_loss_event: 0.302986
- delta_loss_text_aux: 0.094539
- delta_loss_text_aux_effective: 0.094539
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051541
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.107951
- delta_z_art_delta_abs_mean: -0.003657
- delta_event_prob_mean: -0.012617
- delta_event_presence_prob_mean: -0.032826
- delta_event_delta_prob_mean: 0.015433
- delta_event_rise_prob_mean: -0.022645
- delta_event_fall_prob_mean: 0.020978
- delta_event_energy_prob_mean: -0.026984
- delta_event_presence_peak_ratio: 0.138113
- delta_acoustic_abs_mean: 0.25432
- delta_acoustic_energy_mean: -1.001626
- delta_acoustic_delta_abs_mean: -0.020961
- delta_text_aux_abs_mean: 0.051917

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
