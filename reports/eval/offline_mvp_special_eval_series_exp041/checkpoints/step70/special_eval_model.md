# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.410866
- loss_acoustic: 3.86149
- loss_event: 4.990391
- loss_text_aux: 0.114065
- loss_text_aux_effective: 0.114065
- loss_text_aux_structural: 0.125006
- loss_text_aux_lexical: 0.096558
- loss_clause_transition_aux: 0.046266
- loss_boundary_contrast_aux: 0.050434
- z_art_abs_mean: 0.180612
- z_art_delta_abs_mean: 0.003208
- event_prob_mean: 0.471734
- event_presence_prob_mean: 0.586347
- event_delta_prob_mean: 0.413293
- event_rise_prob_mean: 0.489745
- event_fall_prob_mean: 0.440261
- event_energy_prob_mean: 0.567459
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.87103
- acoustic_energy_mean: -3.35308
- acoustic_delta_abs_mean: 0.022046
- text_aux_abs_mean: 0.218854

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.160835
- loss_acoustic: 1.551485
- loss_event: 5.143126
- loss_text_aux: 0.180199
- loss_text_aux_effective: 0.180199
- loss_text_aux_structural: 0.253781
- loss_text_aux_lexical: 0.062468
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- z_art_abs_mean: 0.161533
- z_art_delta_abs_mean: 0.002184
- event_prob_mean: 0.465361
- event_presence_prob_mean: 0.574443
- event_delta_prob_mean: 0.41803
- event_rise_prob_mean: 0.478348
- event_fall_prob_mean: 0.447911
- event_energy_prob_mean: 0.557347
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.952033
- acoustic_energy_mean: -3.69367
- acoustic_delta_abs_mean: 0.028484
- text_aux_abs_mean: 0.237898

## 对比
- delta_loss_total: -2.250031
- delta_loss_acoustic: -2.310005
- delta_loss_event: 0.152735
- delta_loss_text_aux: 0.066134
- delta_loss_text_aux_effective: 0.066134
- delta_loss_text_aux_structural: 0.128775
- delta_loss_text_aux_lexical: -0.03409
- delta_loss_clause_transition_aux: -0.046266
- delta_loss_boundary_contrast_aux: -0.050434
- delta_z_art_abs_mean: -0.019079
- delta_z_art_delta_abs_mean: -0.001024
- delta_event_prob_mean: -0.006373
- delta_event_presence_prob_mean: -0.011904
- delta_event_delta_prob_mean: 0.004737
- delta_event_rise_prob_mean: -0.011397
- delta_event_fall_prob_mean: 0.00765
- delta_event_energy_prob_mean: -0.010112
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.081003
- delta_acoustic_energy_mean: -0.34059
- delta_acoustic_delta_abs_mean: 0.006438
- delta_text_aux_abs_mean: 0.019044

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
