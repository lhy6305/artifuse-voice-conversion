# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d5_special_proxy_core_clause_ge4_late_handoff_exp021/checkpoints/EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.43099
- loss_acoustic: 6.772177
- loss_event: 5.210723
- loss_text_aux: 0.194367
- loss_text_aux_effective: 0.194367
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.038796
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.223682
- z_art_delta_abs_mean: 0.00125
- event_prob_mean: 0.481567
- event_presence_prob_mean: 0.568835
- event_delta_prob_mean: 0.497999
- event_rise_prob_mean: 0.464315
- event_fall_prob_mean: 0.49044
- event_energy_prob_mean: 0.533464
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.149907
- acoustic_energy_mean: -4.395367
- acoustic_delta_abs_mean: 0.055358
- text_aux_abs_mean: 0.399854

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.515236
- loss_acoustic: 2.809295
- loss_event: 5.271786
- loss_text_aux: 0.348277
- loss_text_aux_effective: 0.348277
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.233366
- z_art_delta_abs_mean: 0.00049
- event_prob_mean: 0.479485
- event_presence_prob_mean: 0.566648
- event_delta_prob_mean: 0.50303
- event_rise_prob_mean: 0.458806
- event_fall_prob_mean: 0.495116
- event_energy_prob_mean: 0.528739
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.163257
- acoustic_energy_mean: -4.45975
- acoustic_delta_abs_mean: 0.049143
- text_aux_abs_mean: 0.404802

## 对比
- delta_loss_total: -3.915754
- delta_loss_acoustic: -3.962882
- delta_loss_event: 0.061063
- delta_loss_text_aux: 0.15391
- delta_loss_text_aux_effective: 0.15391
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.038796
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.009684
- delta_z_art_delta_abs_mean: -0.00076
- delta_event_prob_mean: -0.002082
- delta_event_presence_prob_mean: -0.002187
- delta_event_delta_prob_mean: 0.005031
- delta_event_rise_prob_mean: -0.005509
- delta_event_fall_prob_mean: 0.004676
- delta_event_energy_prob_mean: -0.004725
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.01335
- delta_acoustic_energy_mean: -0.064383
- delta_acoustic_delta_abs_mean: -0.006215
- delta_text_aux_abs_mean: 0.004948

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
