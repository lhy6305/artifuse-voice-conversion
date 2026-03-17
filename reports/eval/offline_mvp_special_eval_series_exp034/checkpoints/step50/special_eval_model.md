# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.675093
- loss_acoustic: 7.050841
- loss_event: 5.146257
- loss_text_aux: 0.177353
- loss_clause_transition_aux: 0.04193
- z_art_abs_mean: 0.16009
- z_art_delta_abs_mean: 0.001221
- event_prob_mean: 0.461681
- event_presence_prob_mean: 0.56586
- event_delta_prob_mean: 0.4463
- event_rise_prob_mean: 0.489737
- event_fall_prob_mean: 0.51181
- event_energy_prob_mean: 0.491946
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.168871
- acoustic_energy_mean: -4.463454
- acoustic_delta_abs_mean: 0.033222
- text_aux_abs_mean: 0.341209

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.618261
- loss_acoustic: 2.930776
- loss_event: 5.207102
- loss_text_aux: 0.417394
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.169616
- z_art_delta_abs_mean: 0.00057
- event_prob_mean: 0.458848
- event_presence_prob_mean: 0.564057
- event_delta_prob_mean: 0.445218
- event_rise_prob_mean: 0.488621
- event_fall_prob_mean: 0.509247
- event_energy_prob_mean: 0.490539
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.178648
- acoustic_energy_mean: -4.502892
- acoustic_delta_abs_mean: 0.035364
- text_aux_abs_mean: 0.343392

## 对比
- delta_loss_total: -4.056832
- delta_loss_acoustic: -4.120065
- delta_loss_event: 0.060845
- delta_loss_text_aux: 0.240041
- delta_loss_clause_transition_aux: -0.04193
- delta_z_art_abs_mean: 0.009526
- delta_z_art_delta_abs_mean: -0.000651
- delta_event_prob_mean: -0.002833
- delta_event_presence_prob_mean: -0.001803
- delta_event_delta_prob_mean: -0.001082
- delta_event_rise_prob_mean: -0.001116
- delta_event_fall_prob_mean: -0.002563
- delta_event_energy_prob_mean: -0.001407
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.009777
- delta_acoustic_energy_mean: -0.039438
- delta_acoustic_delta_abs_mean: 0.002142
- delta_text_aux_abs_mean: 0.002183

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
