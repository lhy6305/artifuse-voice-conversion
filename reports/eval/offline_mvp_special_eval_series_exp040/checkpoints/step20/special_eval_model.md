# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.581928
- loss_acoustic: 12.827874
- loss_event: 5.414345
- loss_text_aux: 0.168343
- loss_text_aux_effective: 0.168343
- loss_text_aux_structural: 0.17314
- loss_text_aux_lexical: 0.160667
- loss_clause_transition_aux: 0.03629
- z_art_abs_mean: 0.115783
- z_art_delta_abs_mean: 0.000638
- event_prob_mean: 0.506316
- event_presence_prob_mean: 0.537169
- event_delta_prob_mean: 0.528454
- event_rise_prob_mean: 0.51361
- event_fall_prob_mean: 0.528853
- event_energy_prob_mean: 0.519496
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373037
- acoustic_energy_mean: -1.146143
- acoustic_delta_abs_mean: 0.153209
- text_aux_abs_mean: 0.182605

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.767813
- loss_acoustic: 9.016356
- loss_event: 5.445581
- loss_text_aux: 0.142082
- loss_text_aux_effective: 0.142082
- loss_text_aux_structural: 0.205735
- loss_text_aux_lexical: 0.040238
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.118304
- z_art_delta_abs_mean: 0.000312
- event_prob_mean: 0.505795
- event_presence_prob_mean: 0.536348
- event_delta_prob_mean: 0.530564
- event_rise_prob_mean: 0.51322
- event_fall_prob_mean: 0.532426
- event_energy_prob_mean: 0.516655
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375138
- acoustic_energy_mean: -1.153904
- acoustic_delta_abs_mean: 0.152511
- text_aux_abs_mean: 0.18383

## 对比
- delta_loss_total: -3.814115
- delta_loss_acoustic: -3.811518
- delta_loss_event: 0.031236
- delta_loss_text_aux: -0.026261
- delta_loss_text_aux_effective: -0.026261
- delta_loss_text_aux_structural: 0.032595
- delta_loss_text_aux_lexical: -0.120429
- delta_loss_clause_transition_aux: -0.03629
- delta_z_art_abs_mean: 0.002521
- delta_z_art_delta_abs_mean: -0.000326
- delta_event_prob_mean: -0.000521
- delta_event_presence_prob_mean: -0.000821
- delta_event_delta_prob_mean: 0.00211
- delta_event_rise_prob_mean: -0.00039
- delta_event_fall_prob_mean: 0.003573
- delta_event_energy_prob_mean: -0.002841
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002101
- delta_acoustic_energy_mean: -0.007761
- delta_acoustic_delta_abs_mean: -0.000698
- delta_text_aux_abs_mean: 0.001225

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
