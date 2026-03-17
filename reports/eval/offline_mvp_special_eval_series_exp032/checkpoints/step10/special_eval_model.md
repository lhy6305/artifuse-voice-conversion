# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.575983
- loss_acoustic: 16.769736
- loss_event: 5.507167
- loss_text_aux: 0.194148
- loss_clause_transition_aux: 0.038516
- z_art_abs_mean: 0.088227
- z_art_delta_abs_mean: 0.000442
- event_prob_mean: 0.500962
- event_presence_prob_mean: 0.543312
- event_delta_prob_mean: 0.517692
- event_rise_prob_mean: 0.545532
- event_fall_prob_mean: 0.512034
- event_energy_prob_mean: 0.461987
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.184748
- acoustic_energy_mean: -0.454902
- acoustic_delta_abs_mean: 0.135692
- text_aux_abs_mean: 0.103723

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.836424
- loss_acoustic: 13.05412
- loss_event: 5.50201
- loss_text_aux: 0.15555
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.091076
- z_art_delta_abs_mean: 0.000234
- event_prob_mean: 0.500587
- event_presence_prob_mean: 0.542293
- event_delta_prob_mean: 0.51794
- event_rise_prob_mean: 0.546971
- event_fall_prob_mean: 0.511017
- event_energy_prob_mean: 0.461431
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.18562
- acoustic_energy_mean: -0.458217
- acoustic_delta_abs_mean: 0.137232
- text_aux_abs_mean: 0.103738

## 对比
- delta_loss_total: -3.739559
- delta_loss_acoustic: -3.715616
- delta_loss_event: -0.005157
- delta_loss_text_aux: -0.038598
- delta_loss_clause_transition_aux: -0.038516
- delta_z_art_abs_mean: 0.002849
- delta_z_art_delta_abs_mean: -0.000208
- delta_event_prob_mean: -0.000375
- delta_event_presence_prob_mean: -0.001019
- delta_event_delta_prob_mean: 0.000248
- delta_event_rise_prob_mean: 0.001439
- delta_event_fall_prob_mean: -0.001017
- delta_event_energy_prob_mean: -0.000556
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000872
- delta_acoustic_energy_mean: -0.003315
- delta_acoustic_delta_abs_mean: 0.00154
- delta_text_aux_abs_mean: 1.5e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
