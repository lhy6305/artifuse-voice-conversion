# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.829156
- loss_acoustic: 3.30248
- loss_event: 4.969933
- loss_text_aux: 0.1109
- loss_text_aux_effective: 0.1109
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046539
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.193598
- z_art_delta_abs_mean: 0.004051
- event_prob_mean: 0.469391
- event_presence_prob_mean: 0.587325
- event_delta_prob_mean: 0.409691
- event_rise_prob_mean: 0.488225
- event_fall_prob_mean: 0.436627
- event_energy_prob_mean: 0.563874
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.933106
- acoustic_energy_mean: -3.620531
- acoustic_delta_abs_mean: 0.01635
- text_aux_abs_mean: 0.235872

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.121977
- loss_acoustic: 1.511962
- loss_event: 5.131014
- loss_text_aux: 0.211616
- loss_text_aux_effective: 0.211616
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169601
- z_art_delta_abs_mean: 0.00273
- event_prob_mean: 0.462543
- event_presence_prob_mean: 0.57368
- event_delta_prob_mean: 0.416126
- event_rise_prob_mean: 0.474835
- event_fall_prob_mean: 0.446945
- event_energy_prob_mean: 0.552789
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.032087
- acoustic_energy_mean: -4.045934
- acoustic_delta_abs_mean: 0.008413
- text_aux_abs_mean: 0.262575

## 对比
- delta_loss_total: -1.707179
- delta_loss_acoustic: -1.790518
- delta_loss_event: 0.161081
- delta_loss_text_aux: 0.100716
- delta_loss_text_aux_effective: 0.100716
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046539
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.023997
- delta_z_art_delta_abs_mean: -0.001321
- delta_event_prob_mean: -0.006848
- delta_event_presence_prob_mean: -0.013645
- delta_event_delta_prob_mean: 0.006435
- delta_event_rise_prob_mean: -0.01339
- delta_event_fall_prob_mean: 0.010318
- delta_event_energy_prob_mean: -0.011085
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.098981
- delta_acoustic_energy_mean: -0.425403
- delta_acoustic_delta_abs_mean: -0.007937
- delta_text_aux_abs_mean: 0.026703

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
