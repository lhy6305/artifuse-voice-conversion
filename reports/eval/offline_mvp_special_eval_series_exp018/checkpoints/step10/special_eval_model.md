# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.342969
- loss_acoustic: 16.566298
- loss_event: 5.445377
- loss_text_aux: 0.202974
- loss_text_aux_effective: 0.202974
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036908
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.085621
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508785
- event_presence_prob_mean: 0.524639
- event_delta_prob_mean: 0.527106
- event_rise_prob_mean: 0.528081
- event_fall_prob_mean: 0.522451
- event_energy_prob_mean: 0.523333
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198446
- acoustic_energy_mean: -0.487351
- acoustic_delta_abs_mean: 0.138078
- text_aux_abs_mean: 0.114844

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.630374
- loss_acoustic: 12.869913
- loss_event: 5.470723
- loss_text_aux: 0.124158
- loss_text_aux_effective: 0.124158
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.084759
- z_art_delta_abs_mean: 0.000334
- event_prob_mean: 0.508453
- event_presence_prob_mean: 0.523832
- event_delta_prob_mean: 0.528812
- event_rise_prob_mean: 0.528953
- event_fall_prob_mean: 0.524939
- event_energy_prob_mean: 0.521038
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198915
- acoustic_energy_mean: -0.489427
- acoustic_delta_abs_mean: 0.137566
- text_aux_abs_mean: 0.11482

## 对比
- delta_loss_total: -3.712595
- delta_loss_acoustic: -3.696385
- delta_loss_event: 0.025346
- delta_loss_text_aux: -0.078816
- delta_loss_text_aux_effective: -0.078816
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036908
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.000862
- delta_z_art_delta_abs_mean: -0.000253
- delta_event_prob_mean: -0.000332
- delta_event_presence_prob_mean: -0.000807
- delta_event_delta_prob_mean: 0.001706
- delta_event_rise_prob_mean: 0.000872
- delta_event_fall_prob_mean: 0.002488
- delta_event_energy_prob_mean: -0.002295
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000469
- delta_acoustic_energy_mean: -0.002076
- delta_acoustic_delta_abs_mean: -0.000512
- delta_text_aux_abs_mean: -2.4e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
