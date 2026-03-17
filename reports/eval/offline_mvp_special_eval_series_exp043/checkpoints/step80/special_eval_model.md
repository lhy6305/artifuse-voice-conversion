# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d17_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_exp043/checkpoints/EXP-20260315-043-offline-mvp-d17-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-profile-late-only-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688579
- loss_acoustic: 1.218264
- loss_event: 4.847851
- loss_text_aux: 0.111227
- loss_text_aux_effective: 0.111227
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048287
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240848
- z_art_delta_abs_mean: 0.009056
- event_prob_mean: 0.462076
- event_presence_prob_mean: 0.583153
- event_delta_prob_mean: 0.393292
- event_rise_prob_mean: 0.471898
- event_fall_prob_mean: 0.427586
- event_energy_prob_mean: 0.560336
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838447
- acoustic_energy_mean: -3.194104
- acoustic_delta_abs_mean: 0.028228
- text_aux_abs_mean: 0.215784

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381608
- loss_acoustic: 0.79588
- loss_event: 5.076061
- loss_text_aux: 0.214222
- loss_text_aux_effective: 0.214222
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.172365
- z_art_delta_abs_mean: 0.006067
- event_prob_mean: 0.45182
- event_presence_prob_mean: 0.558307
- event_delta_prob_mean: 0.40582
- event_rise_prob_mean: 0.453227
- event_fall_prob_mean: 0.446742
- event_energy_prob_mean: 0.540122
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073422
- acoustic_energy_mean: -4.168211
- acoustic_delta_abs_mean: 0.007851
- text_aux_abs_mean: 0.27657

## 对比
- delta_loss_total: -0.306971
- delta_loss_acoustic: -0.422384
- delta_loss_event: 0.22821
- delta_loss_text_aux: 0.102995
- delta_loss_text_aux_effective: 0.102995
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048287
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.068483
- delta_z_art_delta_abs_mean: -0.002989
- delta_event_prob_mean: -0.010256
- delta_event_presence_prob_mean: -0.024846
- delta_event_delta_prob_mean: 0.012528
- delta_event_rise_prob_mean: -0.018671
- delta_event_fall_prob_mean: 0.019156
- delta_event_energy_prob_mean: -0.020214
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234975
- delta_acoustic_energy_mean: -0.974107
- delta_acoustic_delta_abs_mean: -0.020377
- delta_text_aux_abs_mean: 0.060786

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
