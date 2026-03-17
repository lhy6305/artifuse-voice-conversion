# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.587308
- loss_acoustic: 12.828615
- loss_event: 5.413803
- loss_text_aux: 0.168293
- loss_text_aux_effective: 0.168293
- loss_text_aux_structural: 0.173022
- loss_text_aux_lexical: 0.160725
- loss_clause_transition_aux: 0.036278
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.024623
- z_art_abs_mean: 0.115737
- z_art_delta_abs_mean: 0.000639
- event_prob_mean: 0.506416
- event_presence_prob_mean: 0.537735
- event_delta_prob_mean: 0.528449
- event_rise_prob_mean: 0.513597
- event_fall_prob_mean: 0.528812
- event_energy_prob_mean: 0.519811
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373117
- acoustic_energy_mean: -1.146016
- acoustic_delta_abs_mean: 0.153057
- text_aux_abs_mean: 0.18265

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.768747
- loss_acoustic: 9.017188
- loss_event: 5.445199
- loss_text_aux: 0.142049
- loss_text_aux_effective: 0.142049
- loss_text_aux_structural: 0.205661
- loss_text_aux_lexical: 0.04027
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001501
- z_art_abs_mean: 0.118267
- z_art_delta_abs_mean: 0.000312
- event_prob_mean: 0.505892
- event_presence_prob_mean: 0.536914
- event_delta_prob_mean: 0.530553
- event_rise_prob_mean: 0.51321
- event_fall_prob_mean: 0.532375
- event_energy_prob_mean: 0.516956
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375213
- acoustic_energy_mean: -1.153764
- acoustic_delta_abs_mean: 0.152352
- text_aux_abs_mean: 0.183871

## 对比
- delta_loss_total: -3.818561
- delta_loss_acoustic: -3.811427
- delta_loss_event: 0.031396
- delta_loss_text_aux: -0.026244
- delta_loss_text_aux_effective: -0.026244
- delta_loss_text_aux_structural: 0.032639
- delta_loss_text_aux_lexical: -0.120455
- delta_loss_clause_transition_aux: -0.036278
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.023122
- delta_z_art_abs_mean: 0.00253
- delta_z_art_delta_abs_mean: -0.000327
- delta_event_prob_mean: -0.000524
- delta_event_presence_prob_mean: -0.000821
- delta_event_delta_prob_mean: 0.002104
- delta_event_rise_prob_mean: -0.000387
- delta_event_fall_prob_mean: 0.003563
- delta_event_energy_prob_mean: -0.002855
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002096
- delta_acoustic_energy_mean: -0.007748
- delta_acoustic_delta_abs_mean: -0.000705
- delta_text_aux_abs_mean: 0.001221

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
