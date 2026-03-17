# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.119759
- loss_acoustic: 1.633902
- loss_event: 4.881459
- loss_text_aux: 0.111463
- loss_text_aux_effective: 0.111463
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.047932
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.226413
- z_art_delta_abs_mean: 0.007574
- event_prob_mean: 0.464654
- event_presence_prob_mean: 0.588455
- event_delta_prob_mean: 0.394457
- event_rise_prob_mean: 0.479714
- event_fall_prob_mean: 0.428339
- event_energy_prob_mean: 0.561477
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.852135
- acoustic_energy_mean: -3.247078
- acoustic_delta_abs_mean: 0.023235
- text_aux_abs_mean: 0.208343

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.477317
- loss_acoustic: 0.886206
- loss_event: 5.091805
- loss_text_aux: 0.205745
- loss_text_aux_effective: 0.205745
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.171236
- z_art_delta_abs_mean: 0.005075
- event_prob_mean: 0.455369
- event_presence_prob_mean: 0.567538
- event_delta_prob_mean: 0.405361
- event_rise_prob_mean: 0.461773
- event_fall_prob_mean: 0.445535
- event_energy_prob_mean: 0.544293
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.047692
- acoustic_energy_mean: -4.046173
- acoustic_delta_abs_mean: 0.010838
- text_aux_abs_mean: 0.258253

## 对比
- delta_loss_total: -0.642442
- delta_loss_acoustic: -0.747696
- delta_loss_event: 0.210346
- delta_loss_text_aux: 0.094282
- delta_loss_text_aux_effective: 0.094282
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.047932
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.055177
- delta_z_art_delta_abs_mean: -0.002499
- delta_event_prob_mean: -0.009285
- delta_event_presence_prob_mean: -0.020917
- delta_event_delta_prob_mean: 0.010904
- delta_event_rise_prob_mean: -0.017941
- delta_event_fall_prob_mean: 0.017196
- delta_event_energy_prob_mean: -0.017184
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.195557
- delta_acoustic_energy_mean: -0.799095
- delta_acoustic_delta_abs_mean: -0.012397
- delta_text_aux_abs_mean: 0.04991

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
