# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.393943
- loss_acoustic: 0.972227
- loss_event: 4.74253
- loss_text_aux: 0.115643
- loss_text_aux_effective: 0.115643
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.050178
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.293541
- z_art_delta_abs_mean: 0.012199
- event_prob_mean: 0.458914
- event_presence_prob_mean: 0.59143
- event_delta_prob_mean: 0.377086
- event_rise_prob_mean: 0.468527
- event_fall_prob_mean: 0.421816
- event_energy_prob_mean: 0.567371
- event_presence_peak_ratio: 0.766327
- acoustic_abs_mean: 0.84813
- acoustic_energy_mean: -3.195237
- acoustic_delta_abs_mean: 0.044747
- text_aux_abs_mean: 0.227903

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.468894
- loss_acoustic: 0.903971
- loss_event: 5.028905
- loss_text_aux: 0.218518
- loss_text_aux_effective: 0.218518
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.191721
- z_art_delta_abs_mean: 0.008458
- event_prob_mean: 0.446406
- event_presence_prob_mean: 0.558865
- event_delta_prob_mean: 0.392877
- event_rise_prob_mean: 0.446428
- event_fall_prob_mean: 0.443768
- event_energy_prob_mean: 0.540223
- event_presence_peak_ratio: 0.919968
- acoustic_abs_mean: 1.136439
- acoustic_energy_mean: -4.362502
- acoustic_delta_abs_mean: 0.020803
- text_aux_abs_mean: 0.292034

## 对比
- delta_loss_total: 0.074951
- delta_loss_acoustic: -0.068256
- delta_loss_event: 0.286375
- delta_loss_text_aux: 0.102875
- delta_loss_text_aux_effective: 0.102875
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.050178
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.10182
- delta_z_art_delta_abs_mean: -0.003741
- delta_event_prob_mean: -0.012508
- delta_event_presence_prob_mean: -0.032565
- delta_event_delta_prob_mean: 0.015791
- delta_event_rise_prob_mean: -0.022099
- delta_event_fall_prob_mean: 0.021952
- delta_event_energy_prob_mean: -0.027148
- delta_event_presence_peak_ratio: 0.153641
- delta_acoustic_abs_mean: 0.288309
- delta_acoustic_energy_mean: -1.167265
- delta_acoustic_delta_abs_mean: -0.023944
- delta_text_aux_abs_mean: 0.064131

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
