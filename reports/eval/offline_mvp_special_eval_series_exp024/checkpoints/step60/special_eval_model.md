# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.088128
- loss_acoustic: 5.503355
- loss_event: 5.082537
- loss_text_aux: 0.134831
- loss_text_aux_effective: 0.134831
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.043245
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.183881
- z_art_delta_abs_mean: 0.001754
- event_prob_mean: 0.475428
- event_presence_prob_mean: 0.581636
- event_delta_prob_mean: 0.444745
- event_rise_prob_mean: 0.48289
- event_fall_prob_mean: 0.458888
- event_energy_prob_mean: 0.557043
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.067198
- acoustic_energy_mean: -4.127226
- acoustic_delta_abs_mean: 0.02254
- text_aux_abs_mean: 0.290312

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.969057
- loss_acoustic: 2.32588
- loss_event: 5.187392
- loss_text_aux: 0.24331
- loss_text_aux_effective: 0.24331
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.188186
- z_art_delta_abs_mean: 0.001025
- event_prob_mean: 0.471321
- event_presence_prob_mean: 0.575425
- event_delta_prob_mean: 0.448901
- event_rise_prob_mean: 0.474433
- event_fall_prob_mean: 0.464516
- event_energy_prob_mean: 0.550755
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.107528
- acoustic_energy_mean: -4.293835
- acoustic_delta_abs_mean: 0.027304
- text_aux_abs_mean: 0.301794

## 对比
- delta_loss_total: -3.119071
- delta_loss_acoustic: -3.177475
- delta_loss_event: 0.104855
- delta_loss_text_aux: 0.108479
- delta_loss_text_aux_effective: 0.108479
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.043245
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.004305
- delta_z_art_delta_abs_mean: -0.000729
- delta_event_prob_mean: -0.004107
- delta_event_presence_prob_mean: -0.006211
- delta_event_delta_prob_mean: 0.004156
- delta_event_rise_prob_mean: -0.008457
- delta_event_fall_prob_mean: 0.005628
- delta_event_energy_prob_mean: -0.006288
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.04033
- delta_acoustic_energy_mean: -0.166609
- delta_acoustic_delta_abs_mean: 0.004764
- delta_text_aux_abs_mean: 0.011482

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
