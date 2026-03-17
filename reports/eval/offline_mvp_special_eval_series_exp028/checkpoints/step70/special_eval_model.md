# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.787945
- loss_acoustic: 3.262845
- loss_event: 4.965725
- loss_text_aux: 0.113197
- loss_text_aux_effective: 0.113197
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046664
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.194499
- z_art_delta_abs_mean: 0.004082
- event_prob_mean: 0.469683
- event_presence_prob_mean: 0.588972
- event_delta_prob_mean: 0.407719
- event_rise_prob_mean: 0.488485
- event_fall_prob_mean: 0.436556
- event_energy_prob_mean: 0.565636
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.905563
- acoustic_energy_mean: -3.514426
- acoustic_delta_abs_mean: 0.013818
- text_aux_abs_mean: 0.229606

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.041533
- loss_acoustic: 1.434401
- loss_event: 5.128779
- loss_text_aux: 0.202658
- loss_text_aux_effective: 0.202658
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169871
- z_art_delta_abs_mean: 0.002763
- event_prob_mean: 0.462804
- event_presence_prob_mean: 0.57519
- event_delta_prob_mean: 0.414104
- event_rise_prob_mean: 0.475095
- event_fall_prob_mean: 0.446949
- event_energy_prob_mean: 0.554424
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.006229
- acoustic_energy_mean: -3.943209
- acoustic_delta_abs_mean: 0.007591
- text_aux_abs_mean: 0.256036

## 对比
- delta_loss_total: -1.746412
- delta_loss_acoustic: -1.828444
- delta_loss_event: 0.163054
- delta_loss_text_aux: 0.089461
- delta_loss_text_aux_effective: 0.089461
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046664
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.024628
- delta_z_art_delta_abs_mean: -0.001319
- delta_event_prob_mean: -0.006879
- delta_event_presence_prob_mean: -0.013782
- delta_event_delta_prob_mean: 0.006385
- delta_event_rise_prob_mean: -0.01339
- delta_event_fall_prob_mean: 0.010393
- delta_event_energy_prob_mean: -0.011212
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.100666
- delta_acoustic_energy_mean: -0.428783
- delta_acoustic_delta_abs_mean: -0.006227
- delta_text_aux_abs_mean: 0.02643

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
