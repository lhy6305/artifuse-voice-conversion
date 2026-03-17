# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d13_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d13_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_exp030/checkpoints/EXP-20260315-030-offline-mvp-d13-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-late-lr-decay-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.27992
- loss_acoustic: 0.858786
- loss_event: 4.741986
- loss_text_aux: 0.114536
- loss_text_aux_effective: 0.114536
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.05125
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.314781
- z_art_delta_abs_mean: 0.01162
- event_prob_mean: 0.460383
- event_presence_prob_mean: 0.60312
- event_delta_prob_mean: 0.365672
- event_rise_prob_mean: 0.47556
- event_fall_prob_mean: 0.413888
- event_energy_prob_mean: 0.576434
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.818122
- acoustic_energy_mean: -3.080981
- acoustic_delta_abs_mean: 0.037205
- text_aux_abs_mean: 0.219668

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.05144
- loss_acoustic: 0.486157
- loss_event: 5.032366
- loss_text_aux: 0.212247
- loss_text_aux_effective: 0.212247
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.217716
- z_art_delta_abs_mean: 0.008312
- event_prob_mean: 0.448497
- event_presence_prob_mean: 0.57253
- event_delta_prob_mean: 0.380051
- event_rise_prob_mean: 0.453929
- event_fall_prob_mean: 0.433275
- event_energy_prob_mean: 0.551593
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.061284
- acoustic_energy_mean: -4.044964
- acoustic_delta_abs_mean: 0.018955
- text_aux_abs_mean: 0.273201

## 对比
- delta_loss_total: -0.22848
- delta_loss_acoustic: -0.372629
- delta_loss_event: 0.29038
- delta_loss_text_aux: 0.097711
- delta_loss_text_aux_effective: 0.097711
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.05125
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.097065
- delta_z_art_delta_abs_mean: -0.003308
- delta_event_prob_mean: -0.011886
- delta_event_presence_prob_mean: -0.03059
- delta_event_delta_prob_mean: 0.014379
- delta_event_rise_prob_mean: -0.021631
- delta_event_fall_prob_mean: 0.019387
- delta_event_energy_prob_mean: -0.024841
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.243162
- delta_acoustic_energy_mean: -0.963983
- delta_acoustic_delta_abs_mean: -0.01825
- delta_text_aux_abs_mean: 0.053533

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
