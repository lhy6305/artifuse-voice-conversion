# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d14_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d14_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_exp029/checkpoints/EXP-20260315-029-offline-mvp-d14-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-late-lr-decay-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.86839
- loss_acoustic: 1.391105
- loss_event: 4.862335
- loss_text_aux: 0.113895
- loss_text_aux_effective: 0.113895
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048065
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.229726
- z_art_delta_abs_mean: 0.008146
- event_prob_mean: 0.46309
- event_presence_prob_mean: 0.584506
- event_delta_prob_mean: 0.394324
- event_rise_prob_mean: 0.474068
- event_fall_prob_mean: 0.429631
- event_energy_prob_mean: 0.562429
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.842682
- acoustic_energy_mean: -3.220761
- acoustic_delta_abs_mean: 0.021401
- text_aux_abs_mean: 0.199185

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.407566
- loss_acoustic: 0.824113
- loss_event: 5.080479
- loss_text_aux: 0.194213
- loss_text_aux_effective: 0.194213
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.169873
- z_art_delta_abs_mean: 0.005463
- event_prob_mean: 0.453367
- event_presence_prob_mean: 0.561379
- event_delta_prob_mean: 0.405732
- event_rise_prob_mean: 0.456268
- event_fall_prob_mean: 0.447346
- event_energy_prob_mean: 0.543583
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.056446
- acoustic_energy_mean: -4.104578
- acoustic_delta_abs_mean: 0.005471
- text_aux_abs_mean: 0.251274

## 对比
- delta_loss_total: -0.460824
- delta_loss_acoustic: -0.566992
- delta_loss_event: 0.218144
- delta_loss_text_aux: 0.080318
- delta_loss_text_aux_effective: 0.080318
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048065
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.059853
- delta_z_art_delta_abs_mean: -0.002683
- delta_event_prob_mean: -0.009723
- delta_event_presence_prob_mean: -0.023127
- delta_event_delta_prob_mean: 0.011408
- delta_event_rise_prob_mean: -0.0178
- delta_event_fall_prob_mean: 0.017715
- delta_event_energy_prob_mean: -0.018846
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.213764
- delta_acoustic_energy_mean: -0.883817
- delta_acoustic_delta_abs_mean: -0.01593
- delta_text_aux_abs_mean: 0.052089

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
