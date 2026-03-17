# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.244328
- loss_acoustic: 5.651824
- loss_event: 5.095415
- loss_text_aux: 0.142392
- loss_text_aux_effective: 0.142392
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.042967
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.187618
- z_art_delta_abs_mean: 0.001601
- event_prob_mean: 0.476691
- event_presence_prob_mean: 0.585914
- event_delta_prob_mean: 0.447956
- event_rise_prob_mean: 0.483445
- event_fall_prob_mean: 0.459046
- event_energy_prob_mean: 0.556072
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.065152
- acoustic_energy_mean: -4.124862
- acoustic_delta_abs_mean: 0.024624
- text_aux_abs_mean: 0.351923

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.998142
- loss_acoustic: 2.342235
- loss_event: 5.194574
- loss_text_aux: 0.289483
- loss_text_aux_effective: 0.289483
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.192031
- z_art_delta_abs_mean: 0.000904
- event_prob_mean: 0.47288
- event_presence_prob_mean: 0.580759
- event_delta_prob_mean: 0.451952
- event_rise_prob_mean: 0.475302
- event_fall_prob_mean: 0.464454
- event_energy_prob_mean: 0.550346
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.102132
- acoustic_energy_mean: -4.272766
- acoustic_delta_abs_mean: 0.032777
- text_aux_abs_mean: 0.364122

## 对比
- delta_loss_total: -3.246186
- delta_loss_acoustic: -3.309589
- delta_loss_event: 0.099159
- delta_loss_text_aux: 0.147091
- delta_loss_text_aux_effective: 0.147091
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.042967
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.004413
- delta_z_art_delta_abs_mean: -0.000697
- delta_event_prob_mean: -0.003811
- delta_event_presence_prob_mean: -0.005155
- delta_event_delta_prob_mean: 0.003996
- delta_event_rise_prob_mean: -0.008143
- delta_event_fall_prob_mean: 0.005408
- delta_event_energy_prob_mean: -0.005726
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.03698
- delta_acoustic_energy_mean: -0.147904
- delta_acoustic_delta_abs_mean: 0.008153
- delta_text_aux_abs_mean: 0.012199

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
