# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.701336
- loss_acoustic: 1.227118
- loss_event: 4.85519
- loss_text_aux: 0.114226
- loss_text_aux_effective: 0.114226
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048102
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.233379
- z_art_delta_abs_mean: 0.008678
- event_prob_mean: 0.461986
- event_presence_prob_mean: 0.58078
- event_delta_prob_mean: 0.394835
- event_rise_prob_mean: 0.472489
- event_fall_prob_mean: 0.429601
- event_energy_prob_mean: 0.559644
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.856961
- acoustic_energy_mean: -3.270874
- acoustic_delta_abs_mean: 0.023523
- text_aux_abs_mean: 0.203179

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.465298
- loss_acoustic: 0.88253
- loss_event: 5.07747
- loss_text_aux: 0.19694
- loss_text_aux_effective: 0.19694
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.168914
- z_art_delta_abs_mean: 0.005806
- event_prob_mean: 0.451903
- event_presence_prob_mean: 0.556612
- event_delta_prob_mean: 0.406912
- event_rise_prob_mean: 0.454114
- event_fall_prob_mean: 0.448203
- event_energy_prob_mean: 0.539806
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.090228
- acoustic_energy_mean: -4.225298
- acoustic_delta_abs_mean: 0.007032
- text_aux_abs_mean: 0.258709

## 对比
- delta_loss_total: -0.236038
- delta_loss_acoustic: -0.344588
- delta_loss_event: 0.22228
- delta_loss_text_aux: 0.082714
- delta_loss_text_aux_effective: 0.082714
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048102
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.064465
- delta_z_art_delta_abs_mean: -0.002872
- delta_event_prob_mean: -0.010083
- delta_event_presence_prob_mean: -0.024168
- delta_event_delta_prob_mean: 0.012077
- delta_event_rise_prob_mean: -0.018375
- delta_event_fall_prob_mean: 0.018602
- delta_event_energy_prob_mean: -0.019838
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.233267
- delta_acoustic_energy_mean: -0.954424
- delta_acoustic_delta_abs_mean: -0.016491
- delta_text_aux_abs_mean: 0.05553

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
