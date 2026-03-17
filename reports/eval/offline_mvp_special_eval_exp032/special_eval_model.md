# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.672052
- loss_acoustic: 0.306239
- loss_event: 4.635071
- loss_text_aux: 0.115681
- loss_clause_transition_aux: 0.05166
- z_art_abs_mean: 0.282362
- z_art_delta_abs_mean: 0.008826
- event_prob_mean: 0.441794
- event_presence_prob_mean: 0.596028
- event_delta_prob_mean: 0.318746
- event_rise_prob_mean: 0.476992
- event_fall_prob_mean: 0.527627
- event_energy_prob_mean: 0.590429
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.885709
- acoustic_energy_mean: -3.421501
- acoustic_delta_abs_mean: 0.007201
- text_aux_abs_mean: 0.256587

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.77516
- loss_acoustic: 0.267066
- loss_event: 4.906329
- loss_text_aux: 0.244485
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.231653
- z_art_delta_abs_mean: 0.007542
- event_prob_mean: 0.433333
- event_presence_prob_mean: 0.577443
- event_delta_prob_mean: 0.324936
- event_rise_prob_mean: 0.473894
- event_fall_prob_mean: 0.516156
- event_energy_prob_mean: 0.57264
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.040821
- acoustic_energy_mean: -4.007228
- acoustic_delta_abs_mean: 0.004443
- text_aux_abs_mean: 0.283561

## 对比
- delta_loss_total: 0.103108
- delta_loss_acoustic: -0.039173
- delta_loss_event: 0.271258
- delta_loss_text_aux: 0.128804
- delta_loss_clause_transition_aux: -0.05166
- delta_z_art_abs_mean: -0.050709
- delta_z_art_delta_abs_mean: -0.001284
- delta_event_prob_mean: -0.008461
- delta_event_presence_prob_mean: -0.018585
- delta_event_delta_prob_mean: 0.00619
- delta_event_rise_prob_mean: -0.003098
- delta_event_fall_prob_mean: -0.011471
- delta_event_energy_prob_mean: -0.017789
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.155112
- delta_acoustic_energy_mean: -0.585727
- delta_acoustic_delta_abs_mean: -0.002758
- delta_text_aux_abs_mean: 0.026974

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
