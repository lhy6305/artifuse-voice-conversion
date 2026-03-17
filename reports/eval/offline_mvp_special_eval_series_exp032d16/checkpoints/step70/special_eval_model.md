# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.773117
- loss_acoustic: 3.248129
- loss_event: 4.965272
- loss_text_aux: 0.113585
- loss_text_aux_effective: 0.113585
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046732
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.194445
- z_art_delta_abs_mean: 0.004099
- event_prob_mean: 0.469538
- event_presence_prob_mean: 0.588099
- event_delta_prob_mean: 0.407118
- event_rise_prob_mean: 0.488398
- event_fall_prob_mean: 0.436198
- event_energy_prob_mean: 0.565893
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.898269
- acoustic_energy_mean: -3.485147
- acoustic_delta_abs_mean: 0.013093
- text_aux_abs_mean: 0.227334

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.02128
- loss_acoustic: 1.41448
- loss_event: 5.128781
- loss_text_aux: 0.200931
- loss_text_aux_effective: 0.200931
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169388
- z_art_delta_abs_mean: 0.002779
- event_prob_mean: 0.462644
- event_presence_prob_mean: 0.574329
- event_delta_prob_mean: 0.413483
- event_rise_prob_mean: 0.474999
- event_fall_prob_mean: 0.446563
- event_energy_prob_mean: 0.554674
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.99964
- acoustic_energy_mean: -3.915901
- acoustic_delta_abs_mean: 0.007547
- text_aux_abs_mean: 0.253891

## 对比
- delta_loss_total: -1.751837
- delta_loss_acoustic: -1.833649
- delta_loss_event: 0.163509
- delta_loss_text_aux: 0.087346
- delta_loss_text_aux_effective: 0.087346
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046732
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.025057
- delta_z_art_delta_abs_mean: -0.00132
- delta_event_prob_mean: -0.006894
- delta_event_presence_prob_mean: -0.01377
- delta_event_delta_prob_mean: 0.006365
- delta_event_rise_prob_mean: -0.013399
- delta_event_fall_prob_mean: 0.010365
- delta_event_energy_prob_mean: -0.011219
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.101371
- delta_acoustic_energy_mean: -0.430754
- delta_acoustic_delta_abs_mean: -0.005546
- delta_text_aux_abs_mean: 0.026557

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
