# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.591851
- loss_acoustic: 12.835758
- loss_event: 5.407503
- loss_text_aux: 0.195976
- loss_text_aux_effective: 0.195976
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036108
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.114908
- z_art_delta_abs_mean: 0.000636
- event_prob_mean: 0.507632
- event_presence_prob_mean: 0.543499
- event_delta_prob_mean: 0.528221
- event_rise_prob_mean: 0.511248
- event_fall_prob_mean: 0.528916
- event_energy_prob_mean: 0.525961
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.37327
- acoustic_energy_mean: -1.145175
- acoustic_delta_abs_mean: 0.152157
- text_aux_abs_mean: 0.183875

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.773661
- loss_acoustic: 9.024294
- loss_event: 5.440388
- loss_text_aux: 0.144606
- loss_text_aux_effective: 0.144606
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.117332
- z_art_delta_abs_mean: 0.000315
- event_prob_mean: 0.507169
- event_presence_prob_mean: 0.542792
- event_delta_prob_mean: 0.530381
- event_rise_prob_mean: 0.510773
- event_fall_prob_mean: 0.532727
- event_energy_prob_mean: 0.523262
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375261
- acoustic_energy_mean: -1.152589
- acoustic_delta_abs_mean: 0.151416
- text_aux_abs_mean: 0.184898

## 对比
- delta_loss_total: -3.81819
- delta_loss_acoustic: -3.811464
- delta_loss_event: 0.032885
- delta_loss_text_aux: -0.05137
- delta_loss_text_aux_effective: -0.05137
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036108
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.002424
- delta_z_art_delta_abs_mean: -0.000321
- delta_event_prob_mean: -0.000463
- delta_event_presence_prob_mean: -0.000707
- delta_event_delta_prob_mean: 0.00216
- delta_event_rise_prob_mean: -0.000475
- delta_event_fall_prob_mean: 0.003811
- delta_event_energy_prob_mean: -0.002699
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.001991
- delta_acoustic_energy_mean: -0.007414
- delta_acoustic_delta_abs_mean: -0.000741
- delta_text_aux_abs_mean: 0.001023

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
