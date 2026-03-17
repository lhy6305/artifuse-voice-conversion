# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.457301
- loss_acoustic: 1.023185
- loss_event: 4.76823
- loss_text_aux: 0.115971
- loss_text_aux_effective: 0.115971
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.049733
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.285609
- z_art_delta_abs_mean: 0.011749
- event_prob_mean: 0.460059
- event_presence_prob_mean: 0.593252
- event_delta_prob_mean: 0.37908
- event_rise_prob_mean: 0.469808
- event_fall_prob_mean: 0.42094
- event_energy_prob_mean: 0.565996
- event_presence_peak_ratio: 0.83776
- acoustic_abs_mean: 0.825375
- acoustic_energy_mean: -3.114477
- acoustic_delta_abs_mean: 0.048658
- text_aux_abs_mean: 0.210085

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.329188
- loss_acoustic: 0.759773
- loss_event: 5.041764
- loss_text_aux: 0.210386
- loss_text_aux_effective: 0.210386
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.189462
- z_art_delta_abs_mean: 0.00807
- event_prob_mean: 0.448143
- event_presence_prob_mean: 0.56332
- event_delta_prob_mean: 0.394928
- event_rise_prob_mean: 0.447815
- event_fall_prob_mean: 0.443457
- event_energy_prob_mean: 0.540667
- event_presence_peak_ratio: 0.967235
- acoustic_abs_mean: 1.105555
- acoustic_energy_mean: -4.253904
- acoustic_delta_abs_mean: 0.022194
- text_aux_abs_mean: 0.271969

## 对比
- delta_loss_total: -0.128113
- delta_loss_acoustic: -0.263412
- delta_loss_event: 0.273534
- delta_loss_text_aux: 0.094415
- delta_loss_text_aux_effective: 0.094415
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.049733
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.096147
- delta_z_art_delta_abs_mean: -0.003679
- delta_event_prob_mean: -0.011916
- delta_event_presence_prob_mean: -0.029932
- delta_event_delta_prob_mean: 0.015848
- delta_event_rise_prob_mean: -0.021993
- delta_event_fall_prob_mean: 0.022517
- delta_event_energy_prob_mean: -0.025329
- delta_event_presence_peak_ratio: 0.129475
- delta_acoustic_abs_mean: 0.28018
- delta_acoustic_energy_mean: -1.139427
- delta_acoustic_delta_abs_mean: -0.026464
- delta_text_aux_abs_mean: 0.061884

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
