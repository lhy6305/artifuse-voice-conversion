# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.595035
- loss_acoustic: 8.850573
- loss_event: 5.378909
- loss_text_aux: 0.18535
- loss_text_aux_effective: 0.18535
- loss_text_aux_structural: 0.188557
- loss_text_aux_lexical: 0.180217
- loss_clause_transition_aux: 0.035614
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.024098
- z_art_abs_mean: 0.163827
- z_art_delta_abs_mean: 0.000816
- event_prob_mean: 0.501451
- event_presence_prob_mean: 0.549248
- event_delta_prob_mean: 0.533996
- event_rise_prob_mean: 0.492342
- event_fall_prob_mean: 0.532205
- event_energy_prob_mean: 0.515942
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.574705
- acoustic_energy_mean: -2.122171
- acoustic_delta_abs_mean: 0.071469
- text_aux_abs_mean: 0.314514

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.637752
- loss_acoustic: 4.883172
- loss_event: 5.412462
- loss_text_aux: 0.239129
- loss_text_aux_effective: 0.239129
- loss_text_aux_structural: 0.300044
- loss_text_aux_lexical: 0.141666
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001422
- z_art_abs_mean: 0.167692
- z_art_delta_abs_mean: 0.000297
- event_prob_mean: 0.500728
- event_presence_prob_mean: 0.548641
- event_delta_prob_mean: 0.537091
- event_rise_prob_mean: 0.490368
- event_fall_prob_mean: 0.536645
- event_energy_prob_mean: 0.512493
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.577935
- acoustic_energy_mean: -2.137368
- acoustic_delta_abs_mean: 0.06902
- text_aux_abs_mean: 0.316745

## 对比
- delta_loss_total: -3.957283
- delta_loss_acoustic: -3.967401
- delta_loss_event: 0.033553
- delta_loss_text_aux: 0.053779
- delta_loss_text_aux_effective: 0.053779
- delta_loss_text_aux_structural: 0.111487
- delta_loss_text_aux_lexical: -0.038551
- delta_loss_clause_transition_aux: -0.035614
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.022676
- delta_z_art_abs_mean: 0.003865
- delta_z_art_delta_abs_mean: -0.000519
- delta_event_prob_mean: -0.000723
- delta_event_presence_prob_mean: -0.000607
- delta_event_delta_prob_mean: 0.003095
- delta_event_rise_prob_mean: -0.001974
- delta_event_fall_prob_mean: 0.00444
- delta_event_energy_prob_mean: -0.003449
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.00323
- delta_acoustic_energy_mean: -0.015197
- delta_acoustic_delta_abs_mean: -0.002449
- delta_text_aux_abs_mean: 0.002231

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
