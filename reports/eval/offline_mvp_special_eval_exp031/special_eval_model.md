# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.730729
- loss_acoustic: 0.377253
- loss_event: 4.602315
- loss_text_aux: 0.112661
- loss_text_aux_effective: 0.112661
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.056569
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.437875
- z_art_delta_abs_mean: 0.012483
- event_prob_mean: 0.457723
- event_presence_prob_mean: 0.644808
- event_delta_prob_mean: 0.313065
- event_rise_prob_mean: 0.497113
- event_fall_prob_mean: 0.403843
- event_energy_prob_mean: 0.612461
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.860742
- acoustic_energy_mean: -3.26963
- acoustic_delta_abs_mean: 0.012961
- text_aux_abs_mean: 0.242759

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.727147
- loss_acoustic: 0.185038
- loss_event: 4.982162
- loss_text_aux: 0.215599
- loss_text_aux_effective: 0.215599
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.341155
- z_art_delta_abs_mean: 0.009885
- event_prob_mean: 0.445403
- event_presence_prob_mean: 0.611681
- event_delta_prob_mean: 0.32616
- event_rise_prob_mean: 0.472248
- event_fall_prob_mean: 0.419243
- event_energy_prob_mean: 0.585795
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998453
- acoustic_energy_mean: -3.788493
- acoustic_delta_abs_mean: 0.014913
- text_aux_abs_mean: 0.270176

## 对比
- delta_loss_total: -0.003582
- delta_loss_acoustic: -0.192215
- delta_loss_event: 0.379847
- delta_loss_text_aux: 0.102938
- delta_loss_text_aux_effective: 0.102938
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.056569
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.09672
- delta_z_art_delta_abs_mean: -0.002598
- delta_event_prob_mean: -0.01232
- delta_event_presence_prob_mean: -0.033127
- delta_event_delta_prob_mean: 0.013095
- delta_event_rise_prob_mean: -0.024865
- delta_event_fall_prob_mean: 0.0154
- delta_event_energy_prob_mean: -0.026666
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137711
- delta_acoustic_energy_mean: -0.518863
- delta_acoustic_delta_abs_mean: 0.001952
- delta_text_aux_abs_mean: 0.027417

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
