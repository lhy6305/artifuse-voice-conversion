# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d5_special_proxy_core_clause_ge4_late_handoff_exp021/checkpoints/EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.772292
- loss_acoustic: 3.247648
- loss_event: 4.964567
- loss_text_aux: 0.11359
- loss_text_aux_effective: 0.11359
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046735
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.195218
- z_art_delta_abs_mean: 0.004107
- event_prob_mean: 0.469705
- event_presence_prob_mean: 0.589487
- event_delta_prob_mean: 0.407044
- event_rise_prob_mean: 0.488526
- event_fall_prob_mean: 0.435965
- event_energy_prob_mean: 0.566131
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.898316
- acoustic_energy_mean: -3.485454
- acoustic_delta_abs_mean: 0.013129
- text_aux_abs_mean: 0.227408

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.020983
- loss_acoustic: 1.414339
- loss_event: 5.128448
- loss_text_aux: 0.200966
- loss_text_aux_effective: 0.200966
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.17014
- z_art_delta_abs_mean: 0.002784
- event_prob_mean: 0.46281
- event_presence_prob_mean: 0.575675
- event_delta_prob_mean: 0.413414
- event_rise_prob_mean: 0.475121
- event_fall_prob_mean: 0.446369
- event_energy_prob_mean: 0.554906
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.999706
- acoustic_energy_mean: -3.916143
- acoustic_delta_abs_mean: 0.007571
- text_aux_abs_mean: 0.253957

## 对比
- delta_loss_total: -1.751309
- delta_loss_acoustic: -1.833309
- delta_loss_event: 0.163881
- delta_loss_text_aux: 0.087376
- delta_loss_text_aux_effective: 0.087376
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046735
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.025078
- delta_z_art_delta_abs_mean: -0.001323
- delta_event_prob_mean: -0.006895
- delta_event_presence_prob_mean: -0.013812
- delta_event_delta_prob_mean: 0.00637
- delta_event_rise_prob_mean: -0.013405
- delta_event_fall_prob_mean: 0.010404
- delta_event_energy_prob_mean: -0.011225
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.10139
- delta_acoustic_energy_mean: -0.430689
- delta_acoustic_delta_abs_mean: -0.005558
- delta_text_aux_abs_mean: 0.026549

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
