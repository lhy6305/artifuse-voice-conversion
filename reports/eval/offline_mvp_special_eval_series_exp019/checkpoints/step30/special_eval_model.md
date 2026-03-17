# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.603755
- loss_acoustic: 8.860081
- loss_event: 5.371697
- loss_text_aux: 0.223954
- loss_text_aux_effective: 0.223954
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035402
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.163346
- z_art_delta_abs_mean: 0.000805
- event_prob_mean: 0.503139
- event_presence_prob_mean: 0.557422
- event_delta_prob_mean: 0.533409
- event_rise_prob_mean: 0.489818
- event_fall_prob_mean: 0.532657
- event_energy_prob_mean: 0.523419
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.575426
- acoustic_energy_mean: -2.120378
- acoustic_delta_abs_mean: 0.07247
- text_aux_abs_mean: 0.275992

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.640964
- loss_acoustic: 4.891828
- loss_event: 5.407009
- loss_text_aux: 0.226961
- loss_text_aux_effective: 0.226961
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.167129
- z_art_delta_abs_mean: 0.000299
- event_prob_mean: 0.502494
- event_presence_prob_mean: 0.556966
- event_delta_prob_mean: 0.536586
- event_rise_prob_mean: 0.487729
- event_fall_prob_mean: 0.53738
- event_energy_prob_mean: 0.520178
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.578535
- acoustic_energy_mean: -2.135158
- acoustic_delta_abs_mean: 0.069935
- text_aux_abs_mean: 0.278057

## 对比
- delta_loss_total: -3.962791
- delta_loss_acoustic: -3.968253
- delta_loss_event: 0.035312
- delta_loss_text_aux: 0.003007
- delta_loss_text_aux_effective: 0.003007
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035402
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.003783
- delta_z_art_delta_abs_mean: -0.000506
- delta_event_prob_mean: -0.000645
- delta_event_presence_prob_mean: -0.000456
- delta_event_delta_prob_mean: 0.003177
- delta_event_rise_prob_mean: -0.002089
- delta_event_fall_prob_mean: 0.004723
- delta_event_energy_prob_mean: -0.003241
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.003109
- delta_acoustic_energy_mean: -0.01478
- delta_acoustic_delta_abs_mean: -0.002535
- delta_text_aux_abs_mean: 0.002065

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
