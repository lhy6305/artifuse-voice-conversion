# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/checkpoints/EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688544
- loss_acoustic: 1.218237
- loss_event: 4.847809
- loss_text_aux: 0.111231
- loss_text_aux_effective: 0.111231
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048296
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.240983
- z_art_delta_abs_mean: 0.009065
- event_prob_mean: 0.46206
- event_presence_prob_mean: 0.583177
- event_delta_prob_mean: 0.393232
- event_rise_prob_mean: 0.471911
- event_fall_prob_mean: 0.427483
- event_energy_prob_mean: 0.560335
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838388
- acoustic_energy_mean: -3.193874
- acoustic_delta_abs_mean: 0.028254
- text_aux_abs_mean: 0.215765

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381355
- loss_acoustic: 0.79563
- loss_event: 5.076047
- loss_text_aux: 0.214212
- loss_text_aux_effective: 0.214212
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.172441
- z_art_delta_abs_mean: 0.006073
- event_prob_mean: 0.451804
- event_presence_prob_mean: 0.558326
- event_delta_prob_mean: 0.405765
- event_rise_prob_mean: 0.453237
- event_fall_prob_mean: 0.446639
- event_energy_prob_mean: 0.540123
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073379
- acoustic_energy_mean: -4.168047
- acoustic_delta_abs_mean: 0.007858
- text_aux_abs_mean: 0.276551

## 对比
- delta_loss_total: -0.307189
- delta_loss_acoustic: -0.422607
- delta_loss_event: 0.228238
- delta_loss_text_aux: 0.102981
- delta_loss_text_aux_effective: 0.102981
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048296
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.068542
- delta_z_art_delta_abs_mean: -0.002992
- delta_event_prob_mean: -0.010256
- delta_event_presence_prob_mean: -0.024851
- delta_event_delta_prob_mean: 0.012533
- delta_event_rise_prob_mean: -0.018674
- delta_event_fall_prob_mean: 0.019156
- delta_event_energy_prob_mean: -0.020212
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234991
- delta_acoustic_energy_mean: -0.974173
- delta_acoustic_delta_abs_mean: -0.020396
- delta_text_aux_abs_mean: 0.060786

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
