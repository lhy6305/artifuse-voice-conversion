# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.727232
- loss_acoustic: 0.366285
- loss_event: 4.618966
- loss_text_aux: 0.111513
- loss_text_aux_effective: 0.111513
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.055139
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.395839
- z_art_delta_abs_mean: 0.012328
- event_prob_mean: 0.457218
- event_presence_prob_mean: 0.631406
- event_delta_prob_mean: 0.325708
- event_rise_prob_mean: 0.491172
- event_fall_prob_mean: 0.409487
- event_energy_prob_mean: 0.602662
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.891857
- acoustic_energy_mean: -3.385149
- acoustic_delta_abs_mean: 0.014554
- text_aux_abs_mean: 0.241491

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.884654
- loss_acoustic: 0.344176
- loss_event: 4.982301
- loss_text_aux: 0.208438
- loss_text_aux_effective: 0.208438
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.297313
- z_art_delta_abs_mean: 0.00955
- event_prob_mean: 0.444637
- event_presence_prob_mean: 0.597892
- event_delta_prob_mean: 0.339508
- event_rise_prob_mean: 0.466189
- event_fall_prob_mean: 0.425636
- event_energy_prob_mean: 0.575425
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.06132
- acoustic_energy_mean: -4.044011
- acoustic_delta_abs_mean: 0.011754
- text_aux_abs_mean: 0.279315

## 对比
- delta_loss_total: 0.157422
- delta_loss_acoustic: -0.022109
- delta_loss_event: 0.363335
- delta_loss_text_aux: 0.096925
- delta_loss_text_aux_effective: 0.096925
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.055139
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.098526
- delta_z_art_delta_abs_mean: -0.002778
- delta_event_prob_mean: -0.012581
- delta_event_presence_prob_mean: -0.033514
- delta_event_delta_prob_mean: 0.0138
- delta_event_rise_prob_mean: -0.024983
- delta_event_fall_prob_mean: 0.016149
- delta_event_energy_prob_mean: -0.027237
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.169463
- delta_acoustic_energy_mean: -0.658862
- delta_acoustic_delta_abs_mean: -0.0028
- delta_text_aux_abs_mean: 0.037824

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
