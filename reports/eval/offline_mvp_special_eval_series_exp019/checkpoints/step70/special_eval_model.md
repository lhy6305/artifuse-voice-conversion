# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.217128
- loss_acoustic: 3.684436
- loss_event: 4.982881
- loss_text_aux: 0.110581
- loss_text_aux_effective: 0.110581
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046477
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.193589
- z_art_delta_abs_mean: 0.003585
- event_prob_mean: 0.47148
- event_presence_prob_mean: 0.594349
- event_delta_prob_mean: 0.409393
- event_rise_prob_mean: 0.491979
- event_fall_prob_mean: 0.43593
- event_energy_prob_mean: 0.56634
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.909892
- acoustic_energy_mean: -3.509617
- acoustic_delta_abs_mean: 0.01503
- text_aux_abs_mean: 0.254697

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.159442
- loss_acoustic: 1.542512
- loss_event: 5.138759
- loss_text_aux: 0.228026
- loss_text_aux_effective: 0.228026
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.172884
- z_art_delta_abs_mean: 0.002431
- event_prob_mean: 0.465093
- event_presence_prob_mean: 0.582422
- event_delta_prob_mean: 0.415297
- event_rise_prob_mean: 0.47901
- event_fall_prob_mean: 0.445709
- event_energy_prob_mean: 0.556455
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.995698
- acoustic_energy_mean: -3.874157
- acoustic_delta_abs_mean: 0.007734
- text_aux_abs_mean: 0.280246

## 对比
- delta_loss_total: -2.057686
- delta_loss_acoustic: -2.141924
- delta_loss_event: 0.155878
- delta_loss_text_aux: 0.117445
- delta_loss_text_aux_effective: 0.117445
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046477
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.020705
- delta_z_art_delta_abs_mean: -0.001154
- delta_event_prob_mean: -0.006387
- delta_event_presence_prob_mean: -0.011927
- delta_event_delta_prob_mean: 0.005904
- delta_event_rise_prob_mean: -0.012969
- delta_event_fall_prob_mean: 0.009779
- delta_event_energy_prob_mean: -0.009885
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.085806
- delta_acoustic_energy_mean: -0.36454
- delta_acoustic_delta_abs_mean: -0.007296
- delta_text_aux_abs_mean: 0.025549

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
