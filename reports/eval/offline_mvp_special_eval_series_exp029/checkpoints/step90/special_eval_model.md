# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d14_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d14_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_exp029/checkpoints/EXP-20260315-029-offline-mvp-d14-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-late-lr-decay-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.460588
- loss_acoustic: 1.018589
- loss_event: 4.785842
- loss_text_aux: 0.115768
- loss_text_aux_effective: 0.115768
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.049465
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.272036
- z_art_delta_abs_mean: 0.010764
- event_prob_mean: 0.460498
- event_presence_prob_mean: 0.590335
- event_delta_prob_mean: 0.382217
- event_rise_prob_mean: 0.468491
- event_fall_prob_mean: 0.423451
- event_energy_prob_mean: 0.567631
- event_presence_peak_ratio: 0.837868
- acoustic_abs_mean: 0.821621
- acoustic_energy_mean: -3.100617
- acoustic_delta_abs_mean: 0.043029
- text_aux_abs_mean: 0.206262

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.243269
- loss_acoustic: 0.673233
- loss_event: 5.047093
- loss_text_aux: 0.202872
- loss_text_aux_effective: 0.202872
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.184714
- z_art_delta_abs_mean: 0.007393
- event_prob_mean: 0.449092
- event_presence_prob_mean: 0.561409
- event_delta_prob_mean: 0.396442
- event_rise_prob_mean: 0.44827
- event_fall_prob_mean: 0.443994
- event_energy_prob_mean: 0.543737
- event_presence_peak_ratio: 0.967235
- acoustic_abs_mean: 1.089784
- acoustic_energy_mean: -4.183766
- acoustic_delta_abs_mean: 0.017756
- text_aux_abs_mean: 0.266189

## 对比
- delta_loss_total: -0.217319
- delta_loss_acoustic: -0.345356
- delta_loss_event: 0.261251
- delta_loss_text_aux: 0.087104
- delta_loss_text_aux_effective: 0.087104
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.049465
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.087322
- delta_z_art_delta_abs_mean: -0.003371
- delta_event_prob_mean: -0.011406
- delta_event_presence_prob_mean: -0.028926
- delta_event_delta_prob_mean: 0.014225
- delta_event_rise_prob_mean: -0.020221
- delta_event_fall_prob_mean: 0.020543
- delta_event_energy_prob_mean: -0.023894
- delta_event_presence_peak_ratio: 0.129367
- delta_acoustic_abs_mean: 0.268163
- delta_acoustic_energy_mean: -1.083149
- delta_acoustic_delta_abs_mean: -0.025273
- delta_text_aux_abs_mean: 0.059927

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
