# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.809966
- loss_acoustic: 0.449129
- loss_event: 4.618172
- loss_text_aux: 0.112511
- loss_text_aux_effective: 0.112511
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.055457
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.402237
- z_art_delta_abs_mean: 0.012299
- event_prob_mean: 0.459359
- event_presence_prob_mean: 0.639277
- event_delta_prob_mean: 0.323589
- event_rise_prob_mean: 0.49187
- event_fall_prob_mean: 0.407369
- event_energy_prob_mean: 0.60892
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.850829
- acoustic_energy_mean: -3.220427
- acoustic_delta_abs_mean: 0.015761
- text_aux_abs_mean: 0.237054

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.778766
- loss_acoustic: 0.235903
- loss_event: 4.98656
- loss_text_aux: 0.209733
- loss_text_aux_effective: 0.209733
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.304928
- z_art_delta_abs_mean: 0.009544
- event_prob_mean: 0.446971
- event_presence_prob_mean: 0.605968
- event_delta_prob_mean: 0.337113
- event_rise_prob_mean: 0.467541
- event_fall_prob_mean: 0.423489
- event_energy_prob_mean: 0.581906
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.011276
- acoustic_energy_mean: -3.831939
- acoustic_delta_abs_mean: 0.016176
- text_aux_abs_mean: 0.269702

## 对比
- delta_loss_total: -0.0312
- delta_loss_acoustic: -0.213226
- delta_loss_event: 0.368388
- delta_loss_text_aux: 0.097222
- delta_loss_text_aux_effective: 0.097222
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.055457
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.097309
- delta_z_art_delta_abs_mean: -0.002755
- delta_event_prob_mean: -0.012388
- delta_event_presence_prob_mean: -0.033309
- delta_event_delta_prob_mean: 0.013524
- delta_event_rise_prob_mean: -0.024329
- delta_event_fall_prob_mean: 0.01612
- delta_event_energy_prob_mean: -0.027014
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.160447
- delta_acoustic_energy_mean: -0.611512
- delta_acoustic_delta_abs_mean: 0.000415
- delta_text_aux_abs_mean: 0.032648

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
