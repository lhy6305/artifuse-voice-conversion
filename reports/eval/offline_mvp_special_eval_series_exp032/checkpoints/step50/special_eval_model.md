# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.677146
- loss_acoustic: 7.051135
- loss_event: 5.148501
- loss_text_aux: 0.180475
- loss_clause_transition_aux: 0.041972
- z_art_abs_mean: 0.160466
- z_art_delta_abs_mean: 0.00122
- event_prob_mean: 0.461137
- event_presence_prob_mean: 0.562459
- event_delta_prob_mean: 0.446552
- event_rise_prob_mean: 0.489916
- event_fall_prob_mean: 0.511904
- event_energy_prob_mean: 0.491331
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.168953
- acoustic_energy_mean: -4.463631
- acoustic_delta_abs_mean: 0.031595
- text_aux_abs_mean: 0.348133

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.619911
- loss_acoustic: 2.931246
- loss_event: 5.207426
- loss_text_aux: 0.422485
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.169968
- z_art_delta_abs_mean: 0.000568
- event_prob_mean: 0.45826
- event_presence_prob_mean: 0.560569
- event_delta_prob_mean: 0.445452
- event_rise_prob_mean: 0.488771
- event_fall_prob_mean: 0.509339
- event_energy_prob_mean: 0.489937
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.178776
- acoustic_energy_mean: -4.503058
- acoustic_delta_abs_mean: 0.033811
- text_aux_abs_mean: 0.350377

## 对比
- delta_loss_total: -4.057235
- delta_loss_acoustic: -4.119889
- delta_loss_event: 0.058925
- delta_loss_text_aux: 0.24201
- delta_loss_clause_transition_aux: -0.041972
- delta_z_art_abs_mean: 0.009502
- delta_z_art_delta_abs_mean: -0.000652
- delta_event_prob_mean: -0.002877
- delta_event_presence_prob_mean: -0.00189
- delta_event_delta_prob_mean: -0.0011
- delta_event_rise_prob_mean: -0.001145
- delta_event_fall_prob_mean: -0.002565
- delta_event_energy_prob_mean: -0.001394
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.009823
- delta_acoustic_energy_mean: -0.039427
- delta_acoustic_delta_abs_mean: 0.002216
- delta_text_aux_abs_mean: 0.002244

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
