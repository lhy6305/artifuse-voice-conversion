# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.088637
- loss_acoustic: 5.503603
- loss_event: 5.083034
- loss_text_aux: 0.134901
- loss_text_aux_effective: 0.134901
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.043246
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.183251
- z_art_delta_abs_mean: 0.00175
- event_prob_mean: 0.475282
- event_presence_prob_mean: 0.580528
- event_delta_prob_mean: 0.444819
- event_rise_prob_mean: 0.482791
- event_fall_prob_mean: 0.45904
- event_energy_prob_mean: 0.556838
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.067054
- acoustic_energy_mean: -4.126618
- acoustic_delta_abs_mean: 0.02259
- text_aux_abs_mean: 0.290188

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.968726
- loss_acoustic: 2.325432
- loss_event: 5.187626
- loss_text_aux: 0.243317
- loss_text_aux_effective: 0.243317
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.187568
- z_art_delta_abs_mean: 0.001022
- event_prob_mean: 0.471174
- event_presence_prob_mean: 0.574328
- event_delta_prob_mean: 0.448974
- event_rise_prob_mean: 0.474341
- event_fall_prob_mean: 0.464646
- event_energy_prob_mean: 0.550548
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.107408
- acoustic_energy_mean: -4.293169
- acoustic_delta_abs_mean: 0.027505
- text_aux_abs_mean: 0.301667

## 对比
- delta_loss_total: -3.119911
- delta_loss_acoustic: -3.178171
- delta_loss_event: 0.104592
- delta_loss_text_aux: 0.108416
- delta_loss_text_aux_effective: 0.108416
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.043246
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.004317
- delta_z_art_delta_abs_mean: -0.000728
- delta_event_prob_mean: -0.004108
- delta_event_presence_prob_mean: -0.0062
- delta_event_delta_prob_mean: 0.004155
- delta_event_rise_prob_mean: -0.00845
- delta_event_fall_prob_mean: 0.005606
- delta_event_energy_prob_mean: -0.00629
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.040354
- delta_acoustic_energy_mean: -0.166551
- delta_acoustic_delta_abs_mean: 0.004915
- delta_text_aux_abs_mean: 0.011479

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
