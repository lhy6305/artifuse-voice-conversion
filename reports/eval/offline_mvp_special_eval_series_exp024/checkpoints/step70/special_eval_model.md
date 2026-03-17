# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.828037
- loss_acoustic: 3.301316
- loss_event: 4.970036
- loss_text_aux: 0.110855
- loss_text_aux_effective: 0.110855
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046545
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.193485
- z_art_delta_abs_mean: 0.004052
- event_prob_mean: 0.469399
- event_presence_prob_mean: 0.587316
- event_delta_prob_mean: 0.409655
- event_rise_prob_mean: 0.488245
- event_fall_prob_mean: 0.436577
- event_energy_prob_mean: 0.56391
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.93305
- acoustic_energy_mean: -3.620038
- acoustic_delta_abs_mean: 0.016422
- text_aux_abs_mean: 0.235789

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.121358
- loss_acoustic: 1.511316
- loss_event: 5.131089
- loss_text_aux: 0.211568
- loss_text_aux_effective: 0.211568
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169534
- z_art_delta_abs_mean: 0.00273
- event_prob_mean: 0.462549
- event_presence_prob_mean: 0.57368
- event_delta_prob_mean: 0.416081
- event_rise_prob_mean: 0.474852
- event_fall_prob_mean: 0.446876
- event_energy_prob_mean: 0.55283
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.031994
- acoustic_energy_mean: -4.04557
- acoustic_delta_abs_mean: 0.008454
- text_aux_abs_mean: 0.262485

## 对比
- delta_loss_total: -1.706679
- delta_loss_acoustic: -1.79
- delta_loss_event: 0.161053
- delta_loss_text_aux: 0.100713
- delta_loss_text_aux_effective: 0.100713
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046545
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.023951
- delta_z_art_delta_abs_mean: -0.001322
- delta_event_prob_mean: -0.00685
- delta_event_presence_prob_mean: -0.013636
- delta_event_delta_prob_mean: 0.006426
- delta_event_rise_prob_mean: -0.013393
- delta_event_fall_prob_mean: 0.010299
- delta_event_energy_prob_mean: -0.01108
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.098944
- delta_acoustic_energy_mean: -0.425532
- delta_acoustic_delta_abs_mean: -0.007968
- delta_text_aux_abs_mean: 0.026696

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
