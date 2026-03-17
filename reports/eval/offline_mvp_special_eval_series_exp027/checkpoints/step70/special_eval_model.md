# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d11_round1_1_special_proxy_core_clause_ge4_mid_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d11_special_proxy_core_clause_ge4_mid_handoff_zart_influence/checkpoints/EXP-20260315-027-offline-mvp-d11-round1-1-special-proxy-core-clause-ge4-mid-handoff-zart-influence-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.807788
- loss_acoustic: 3.282366
- loss_event: 4.967159
- loss_text_aux: 0.111558
- loss_text_aux_effective: 0.111558
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046501
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.192937
- z_art_delta_abs_mean: 0.00407
- event_prob_mean: 0.469389
- event_presence_prob_mean: 0.587284
- event_delta_prob_mean: 0.409273
- event_rise_prob_mean: 0.487926
- event_fall_prob_mean: 0.437998
- event_energy_prob_mean: 0.564193
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.926388
- acoustic_energy_mean: -3.598802
- acoustic_delta_abs_mean: 0.015459
- text_aux_abs_mean: 0.239473

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.102646
- loss_acoustic: 1.493968
- loss_event: 5.128887
- loss_text_aux: 0.210214
- loss_text_aux_effective: 0.210214
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169246
- z_art_delta_abs_mean: 0.002739
- event_prob_mean: 0.462514
- event_presence_prob_mean: 0.573483
- event_delta_prob_mean: 0.415755
- event_rise_prob_mean: 0.474506
- event_fall_prob_mean: 0.448462
- event_energy_prob_mean: 0.552936
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.026097
- acoustic_energy_mean: -4.027807
- acoustic_delta_abs_mean: 0.008059
- text_aux_abs_mean: 0.266237

## 对比
- delta_loss_total: -1.705142
- delta_loss_acoustic: -1.788398
- delta_loss_event: 0.161728
- delta_loss_text_aux: 0.098656
- delta_loss_text_aux_effective: 0.098656
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046501
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.023691
- delta_z_art_delta_abs_mean: -0.001331
- delta_event_prob_mean: -0.006875
- delta_event_presence_prob_mean: -0.013801
- delta_event_delta_prob_mean: 0.006482
- delta_event_rise_prob_mean: -0.01342
- delta_event_fall_prob_mean: 0.010464
- delta_event_energy_prob_mean: -0.011257
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.099709
- delta_acoustic_energy_mean: -0.429005
- delta_acoustic_delta_abs_mean: -0.0074
- delta_text_aux_abs_mean: 0.026764

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
