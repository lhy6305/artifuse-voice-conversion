# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.30896
- loss_acoustic: 6.588134
- loss_event: 5.323541
- loss_text_aux: 0.228436
- loss_text_aux_effective: 0.228436
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035817
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.221784
- z_art_delta_abs_mean: 0.00104
- event_prob_mean: 0.493119
- event_presence_prob_mean: 0.561315
- event_delta_prob_mean: 0.53293
- event_rise_prob_mean: 0.467561
- event_fall_prob_mean: 0.521277
- event_energy_prob_mean: 0.518871
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878249
- acoustic_energy_mean: -3.374156
- acoustic_delta_abs_mean: 0.067987
- text_aux_abs_mean: 0.376189

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.206463
- loss_acoustic: 2.458489
- loss_event: 5.361778
- loss_text_aux: 0.334057
- loss_text_aux_effective: 0.334057
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.229466
- z_art_delta_abs_mean: 0.000341
- event_prob_mean: 0.492077
- event_presence_prob_mean: 0.560624
- event_delta_prob_mean: 0.537596
- event_rise_prob_mean: 0.463778
- event_fall_prob_mean: 0.526252
- event_energy_prob_mean: 0.514839
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884772
- acoustic_energy_mean: -3.397851
- acoustic_delta_abs_mean: 0.072893
- text_aux_abs_mean: 0.378426

## 对比
- delta_loss_total: -4.102497
- delta_loss_acoustic: -4.129645
- delta_loss_event: 0.038237
- delta_loss_text_aux: 0.105621
- delta_loss_text_aux_effective: 0.105621
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035817
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.007682
- delta_z_art_delta_abs_mean: -0.000699
- delta_event_prob_mean: -0.001042
- delta_event_presence_prob_mean: -0.000691
- delta_event_delta_prob_mean: 0.004666
- delta_event_rise_prob_mean: -0.003783
- delta_event_fall_prob_mean: 0.004975
- delta_event_energy_prob_mean: -0.004032
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006523
- delta_acoustic_energy_mean: -0.023695
- delta_acoustic_delta_abs_mean: 0.004906
- delta_text_aux_abs_mean: 0.002237

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
