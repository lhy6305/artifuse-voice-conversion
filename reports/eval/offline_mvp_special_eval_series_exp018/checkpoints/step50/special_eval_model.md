# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.43606
- loss_acoustic: 6.774105
- loss_event: 5.208651
- loss_text_aux: 0.215065
- loss_text_aux_effective: 0.215065
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.03884
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.220847
- z_art_delta_abs_mean: 0.001277
- event_prob_mean: 0.48117
- event_presence_prob_mean: 0.568823
- event_delta_prob_mean: 0.497902
- event_rise_prob_mean: 0.464266
- event_fall_prob_mean: 0.489751
- event_energy_prob_mean: 0.533641
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.135146
- acoustic_energy_mean: -4.412477
- acoustic_delta_abs_mean: 0.025363
- text_aux_abs_mean: 0.437652

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.54571
- loss_acoustic: 2.833303
- loss_event: 5.26877
- loss_text_aux: 0.388062
- loss_text_aux_effective: 0.388062
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.230781
- z_art_delta_abs_mean: 0.000512
- event_prob_mean: 0.478971
- event_presence_prob_mean: 0.566631
- event_delta_prob_mean: 0.502892
- event_rise_prob_mean: 0.458505
- event_fall_prob_mean: 0.494316
- event_energy_prob_mean: 0.528868
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.148944
- acoustic_energy_mean: -4.480284
- acoustic_delta_abs_mean: 0.018438
- text_aux_abs_mean: 0.443423

## 对比
- delta_loss_total: -3.89035
- delta_loss_acoustic: -3.940802
- delta_loss_event: 0.060119
- delta_loss_text_aux: 0.172997
- delta_loss_text_aux_effective: 0.172997
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.03884
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.009934
- delta_z_art_delta_abs_mean: -0.000765
- delta_event_prob_mean: -0.002199
- delta_event_presence_prob_mean: -0.002192
- delta_event_delta_prob_mean: 0.00499
- delta_event_rise_prob_mean: -0.005761
- delta_event_fall_prob_mean: 0.004565
- delta_event_energy_prob_mean: -0.004773
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.013798
- delta_acoustic_energy_mean: -0.067807
- delta_acoustic_delta_abs_mean: -0.006925
- delta_text_aux_abs_mean: 0.005771

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
