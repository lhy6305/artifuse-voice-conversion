# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.825348
- loss_acoustic: 1.350447
- loss_event: 4.856291
- loss_text_aux: 0.114647
- loss_text_aux_effective: 0.114647
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048497
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.238658
- z_art_delta_abs_mean: 0.008566
- event_prob_mean: 0.46313
- event_presence_prob_mean: 0.585828
- event_delta_prob_mean: 0.391432
- event_rise_prob_mean: 0.474894
- event_fall_prob_mean: 0.425349
- event_energy_prob_mean: 0.562722
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.814234
- acoustic_energy_mean: -3.088414
- acoustic_delta_abs_mean: 0.028555
- text_aux_abs_mean: 0.197161

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.257555
- loss_acoustic: 0.673922
- loss_event: 5.080558
- loss_text_aux: 0.193613
- loss_text_aux_effective: 0.193613
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.17365
- z_art_delta_abs_mean: 0.005789
- event_prob_mean: 0.453124
- event_presence_prob_mean: 0.562095
- event_delta_prob_mean: 0.402843
- event_rise_prob_mean: 0.456803
- event_fall_prob_mean: 0.443398
- event_energy_prob_mean: 0.543385
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.038038
- acoustic_energy_mean: -3.994067
- acoustic_delta_abs_mean: 0.009362
- text_aux_abs_mean: 0.250734

## 对比
- delta_loss_total: -0.567793
- delta_loss_acoustic: -0.676525
- delta_loss_event: 0.224267
- delta_loss_text_aux: 0.078966
- delta_loss_text_aux_effective: 0.078966
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048497
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.065008
- delta_z_art_delta_abs_mean: -0.002777
- delta_event_prob_mean: -0.010006
- delta_event_presence_prob_mean: -0.023733
- delta_event_delta_prob_mean: 0.011411
- delta_event_rise_prob_mean: -0.018091
- delta_event_fall_prob_mean: 0.018049
- delta_event_energy_prob_mean: -0.019337
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.223804
- delta_acoustic_energy_mean: -0.905653
- delta_acoustic_delta_abs_mean: -0.019193
- delta_text_aux_abs_mean: 0.053573

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
