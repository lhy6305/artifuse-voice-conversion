# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d9_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool/checkpoints/EXP-20260315-025-offline-mvp-d9-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-dualpool-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688349
- loss_acoustic: 1.21804
- loss_event: 4.847835
- loss_text_aux: 0.111223
- loss_text_aux_effective: 0.111223
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048295
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240846
- z_art_delta_abs_mean: 0.009056
- event_prob_mean: 0.462061
- event_presence_prob_mean: 0.583162
- event_delta_prob_mean: 0.393248
- event_rise_prob_mean: 0.471899
- event_fall_prob_mean: 0.4275
- event_energy_prob_mean: 0.560346
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838526
- acoustic_energy_mean: -3.19445
- acoustic_delta_abs_mean: 0.028209
- text_aux_abs_mean: 0.215819

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381988
- loss_acoustic: 0.796257
- loss_event: 5.076054
- loss_text_aux: 0.214257
- loss_text_aux_effective: 0.214257
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.172373
- z_art_delta_abs_mean: 0.006066
- event_prob_mean: 0.451805
- event_presence_prob_mean: 0.558315
- event_delta_prob_mean: 0.405776
- event_rise_prob_mean: 0.453229
- event_fall_prob_mean: 0.446649
- event_energy_prob_mean: 0.540131
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073508
- acoustic_energy_mean: -4.168589
- acoustic_delta_abs_mean: 0.007848
- text_aux_abs_mean: 0.27661

## 对比
- delta_loss_total: -0.306361
- delta_loss_acoustic: -0.421783
- delta_loss_event: 0.228219
- delta_loss_text_aux: 0.103034
- delta_loss_text_aux_effective: 0.103034
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048295
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.068473
- delta_z_art_delta_abs_mean: -0.00299
- delta_event_prob_mean: -0.010256
- delta_event_presence_prob_mean: -0.024847
- delta_event_delta_prob_mean: 0.012528
- delta_event_rise_prob_mean: -0.01867
- delta_event_fall_prob_mean: 0.019149
- delta_event_energy_prob_mean: -0.020215
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234982
- delta_acoustic_energy_mean: -0.974139
- delta_acoustic_delta_abs_mean: -0.020361
- delta_text_aux_abs_mean: 0.060791

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
