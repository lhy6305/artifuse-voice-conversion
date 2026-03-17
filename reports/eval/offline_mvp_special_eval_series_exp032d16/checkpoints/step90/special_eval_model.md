# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.387037
- loss_acoustic: 0.968251
- loss_event: 4.734935
- loss_text_aux: 0.11854
- loss_text_aux_effective: 0.11854
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051112
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.314446
- z_art_delta_abs_mean: 0.012152
- event_prob_mean: 0.459951
- event_presence_prob_mean: 0.599694
- event_delta_prob_mean: 0.367839
- event_rise_prob_mean: 0.472936
- event_fall_prob_mean: 0.415233
- event_energy_prob_mean: 0.574838
- event_presence_peak_ratio: 0.822225
- acoustic_abs_mean: 0.807628
- acoustic_energy_mean: -3.036035
- acoustic_delta_abs_mean: 0.043936
- text_aux_abs_mean: 0.208523

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.09571
- loss_acoustic: 0.536574
- loss_event: 5.028696
- loss_text_aux: 0.189449
- loss_text_aux_effective: 0.189449
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.211398
- z_art_delta_abs_mean: 0.008623
- event_prob_mean: 0.447632
- event_presence_prob_mean: 0.567965
- event_delta_prob_mean: 0.382742
- event_rise_prob_mean: 0.450845
- event_fall_prob_mean: 0.435845
- event_energy_prob_mean: 0.548611
- event_presence_peak_ratio: 0.95316
- acoustic_abs_mean: 1.062384
- acoustic_energy_mean: -4.054859
- acoustic_delta_abs_mean: 0.022353
- text_aux_abs_mean: 0.260206

## 对比
- delta_loss_total: -0.291327
- delta_loss_acoustic: -0.431677
- delta_loss_event: 0.293761
- delta_loss_text_aux: 0.070909
- delta_loss_text_aux_effective: 0.070909
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051112
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.103048
- delta_z_art_delta_abs_mean: -0.003529
- delta_event_prob_mean: -0.012319
- delta_event_presence_prob_mean: -0.031729
- delta_event_delta_prob_mean: 0.014903
- delta_event_rise_prob_mean: -0.022091
- delta_event_fall_prob_mean: 0.020612
- delta_event_energy_prob_mean: -0.026227
- delta_event_presence_peak_ratio: 0.130935
- delta_acoustic_abs_mean: 0.254756
- delta_acoustic_energy_mean: -1.018824
- delta_acoustic_delta_abs_mean: -0.021583
- delta_text_aux_abs_mean: 0.051683

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
