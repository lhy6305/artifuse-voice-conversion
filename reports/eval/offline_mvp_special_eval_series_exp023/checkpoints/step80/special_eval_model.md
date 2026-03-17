# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688559
- loss_acoustic: 1.218249
- loss_event: 4.847833
- loss_text_aux: 0.111226
- loss_text_aux_effective: 0.111226
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048295
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240867
- z_art_delta_abs_mean: 0.009056
- event_prob_mean: 0.46206
- event_presence_prob_mean: 0.583165
- event_delta_prob_mean: 0.393242
- event_rise_prob_mean: 0.4719
- event_fall_prob_mean: 0.427493
- event_energy_prob_mean: 0.560345
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.83845
- acoustic_energy_mean: -3.194117
- acoustic_delta_abs_mean: 0.028228
- text_aux_abs_mean: 0.215785

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381576
- loss_acoustic: 0.79585
- loss_event: 5.076056
- loss_text_aux: 0.214221
- loss_text_aux_effective: 0.214221
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.172382
- z_art_delta_abs_mean: 0.006067
- event_prob_mean: 0.451804
- event_presence_prob_mean: 0.558319
- event_delta_prob_mean: 0.405771
- event_rise_prob_mean: 0.45323
- event_fall_prob_mean: 0.446642
- event_energy_prob_mean: 0.54013
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073415
- acoustic_energy_mean: -4.168187
- acoustic_delta_abs_mean: 0.007851
- text_aux_abs_mean: 0.276569

## 对比
- delta_loss_total: -0.306983
- delta_loss_acoustic: -0.422399
- delta_loss_event: 0.228223
- delta_loss_text_aux: 0.102995
- delta_loss_text_aux_effective: 0.102995
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048295
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.068485
- delta_z_art_delta_abs_mean: -0.002989
- delta_event_prob_mean: -0.010256
- delta_event_presence_prob_mean: -0.024846
- delta_event_delta_prob_mean: 0.012529
- delta_event_rise_prob_mean: -0.01867
- delta_event_fall_prob_mean: 0.019149
- delta_event_energy_prob_mean: -0.020215
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234965
- delta_acoustic_energy_mean: -0.97407
- delta_acoustic_delta_abs_mean: -0.020377
- delta_text_aux_abs_mean: 0.060784

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
