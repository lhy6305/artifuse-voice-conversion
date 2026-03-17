# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d17_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_exp043/checkpoints/EXP-20260315-043-offline-mvp-d17-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-profile-late-only-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427158
- loss_acoustic: 1.015802
- loss_event: 4.719073
- loss_text_aux: 0.117977
- loss_text_aux_effective: 0.117977
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051518
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.328948
- z_art_delta_abs_mean: 0.01274
- event_prob_mean: 0.459545
- event_presence_prob_mean: 0.602632
- event_delta_prob_mean: 0.364499
- event_rise_prob_mean: 0.472698
- event_fall_prob_mean: 0.413318
- event_energy_prob_mean: 0.576194
- event_presence_peak_ratio: 0.814353
- acoustic_abs_mean: 0.802472
- acoustic_energy_mean: -2.998646
- acoustic_delta_abs_mean: 0.045124
- text_aux_abs_mean: 0.223073

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.084165
- loss_acoustic: 0.523217
- loss_event: 5.022326
- loss_text_aux: 0.212623
- loss_text_aux_effective: 0.212623
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.220829
- z_art_delta_abs_mean: 0.009076
- event_prob_mean: 0.446924
- event_presence_prob_mean: 0.569718
- event_delta_prob_mean: 0.379925
- event_rise_prob_mean: 0.450053
- event_fall_prob_mean: 0.434367
- event_energy_prob_mean: 0.549191
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056726
- acoustic_energy_mean: -4.000227
- acoustic_delta_abs_mean: 0.024087
- text_aux_abs_mean: 0.274959

## 对比
- delta_loss_total: -0.342993
- delta_loss_acoustic: -0.492585
- delta_loss_event: 0.303253
- delta_loss_text_aux: 0.094646
- delta_loss_text_aux_effective: 0.094646
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051518
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.108119
- delta_z_art_delta_abs_mean: -0.003664
- delta_event_prob_mean: -0.012621
- delta_event_presence_prob_mean: -0.032914
- delta_event_delta_prob_mean: 0.015426
- delta_event_rise_prob_mean: -0.022645
- delta_event_fall_prob_mean: 0.021049
- delta_event_energy_prob_mean: -0.027003
- delta_event_presence_peak_ratio: 0.134954
- delta_acoustic_abs_mean: 0.254254
- delta_acoustic_energy_mean: -1.001581
- delta_acoustic_delta_abs_mean: -0.021037
- delta_text_aux_abs_mean: 0.051886

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
