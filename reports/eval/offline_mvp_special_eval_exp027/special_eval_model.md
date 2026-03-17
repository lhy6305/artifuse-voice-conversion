# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d11_round1_1_special_proxy_core_clause_ge4_mid_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d11_special_proxy_core_clause_ge4_mid_handoff_zart_influence/checkpoints/EXP-20260315-027-offline-mvp-d11-round1-1-special-proxy-core-clause-ge4-mid-handoff-zart-influence-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.762797
- loss_acoustic: 0.400598
- loss_event: 4.621059
- loss_text_aux: 0.112645
- loss_text_aux_effective: 0.112645
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.054908
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.38619
- z_art_delta_abs_mean: 0.012403
- event_prob_mean: 0.457863
- event_presence_prob_mean: 0.630915
- event_delta_prob_mean: 0.329136
- event_rise_prob_mean: 0.490398
- event_fall_prob_mean: 0.409588
- event_energy_prob_mean: 0.600908
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.887206
- acoustic_energy_mean: -3.358197
- acoustic_delta_abs_mean: 0.015165
- text_aux_abs_mean: 0.249222

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.910207
- loss_acoustic: 0.366237
- loss_event: 4.981503
- loss_text_aux: 0.228096
- loss_text_aux_effective: 0.228096
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.286087
- z_art_delta_abs_mean: 0.009499
- event_prob_mean: 0.444985
- event_presence_prob_mean: 0.596711
- event_delta_prob_mean: 0.34303
- event_rise_prob_mean: 0.465405
- event_fall_prob_mean: 0.426265
- event_energy_prob_mean: 0.573061
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.066662
- acoustic_energy_mean: -4.048708
- acoustic_delta_abs_mean: 0.012224
- text_aux_abs_mean: 0.288527

## 对比
- delta_loss_total: 0.14741
- delta_loss_acoustic: -0.034361
- delta_loss_event: 0.360444
- delta_loss_text_aux: 0.115451
- delta_loss_text_aux_effective: 0.115451
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.054908
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.100103
- delta_z_art_delta_abs_mean: -0.002904
- delta_event_prob_mean: -0.012878
- delta_event_presence_prob_mean: -0.034204
- delta_event_delta_prob_mean: 0.013894
- delta_event_rise_prob_mean: -0.024993
- delta_event_fall_prob_mean: 0.016677
- delta_event_energy_prob_mean: -0.027847
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.179456
- delta_acoustic_energy_mean: -0.690511
- delta_acoustic_delta_abs_mean: -0.002941
- delta_text_aux_abs_mean: 0.039305

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
