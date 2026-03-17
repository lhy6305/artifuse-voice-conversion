# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.342274
- loss_acoustic: 16.565257
- loss_event: 5.446042
- loss_text_aux: 0.202924
- loss_text_aux_effective: 0.202924
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036976
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.085531
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508554
- event_presence_prob_mean: 0.524402
- event_delta_prob_mean: 0.527016
- event_rise_prob_mean: 0.528134
- event_fall_prob_mean: 0.521163
- event_energy_prob_mean: 0.523247
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198294
- acoustic_energy_mean: -0.487562
- acoustic_delta_abs_mean: 0.13824
- text_aux_abs_mean: 0.114822

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.629069
- loss_acoustic: 12.868668
- loss_event: 5.470555
- loss_text_aux: 0.124278
- loss_text_aux_effective: 0.124278
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.084683
- z_art_delta_abs_mean: 0.000335
- event_prob_mean: 0.508211
- event_presence_prob_mean: 0.523637
- event_delta_prob_mean: 0.528714
- event_rise_prob_mean: 0.529006
- event_fall_prob_mean: 0.52351
- event_energy_prob_mean: 0.520991
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198752
- acoustic_energy_mean: -0.489611
- acoustic_delta_abs_mean: 0.137712
- text_aux_abs_mean: 0.114786

## 对比
- delta_loss_total: -3.713205
- delta_loss_acoustic: -3.696589
- delta_loss_event: 0.024513
- delta_loss_text_aux: -0.078646
- delta_loss_text_aux_effective: -0.078646
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036976
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.000848
- delta_z_art_delta_abs_mean: -0.000252
- delta_event_prob_mean: -0.000343
- delta_event_presence_prob_mean: -0.000765
- delta_event_delta_prob_mean: 0.001698
- delta_event_rise_prob_mean: 0.000872
- delta_event_fall_prob_mean: 0.002347
- delta_event_energy_prob_mean: -0.002256
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000458
- delta_acoustic_energy_mean: -0.002049
- delta_acoustic_delta_abs_mean: -0.000528
- delta_text_aux_abs_mean: -3.6e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
