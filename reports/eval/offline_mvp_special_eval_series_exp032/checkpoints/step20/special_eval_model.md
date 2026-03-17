# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.688137
- loss_acoustic: 12.910309
- loss_event: 5.450013
- loss_text_aux: 0.19346
- loss_clause_transition_aux: 0.039002
- z_art_abs_mean: 0.133985
- z_art_delta_abs_mean: 0.000598
- event_prob_mean: 0.492763
- event_presence_prob_mean: 0.548023
- event_delta_prob_mean: 0.512519
- event_rise_prob_mean: 0.539462
- event_fall_prob_mean: 0.508764
- event_energy_prob_mean: 0.454988
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.409578
- acoustic_energy_mean: -1.143567
- acoustic_delta_abs_mean: 0.085901
- text_aux_abs_mean: 0.169653

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.839758
- loss_acoustic: 9.066363
- loss_event: 5.457168
- loss_text_aux: 0.223055
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.138763
- z_art_delta_abs_mean: 0.000251
- event_prob_mean: 0.491976
- event_presence_prob_mean: 0.546979
- event_delta_prob_mean: 0.512825
- event_rise_prob_mean: 0.54046
- event_fall_prob_mean: 0.50761
- event_energy_prob_mean: 0.454036
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.41172
- acoustic_energy_mean: -1.149043
- acoustic_delta_abs_mean: 0.08796
- text_aux_abs_mean: 0.169969

## 对比
- delta_loss_total: -3.848379
- delta_loss_acoustic: -3.843946
- delta_loss_event: 0.007155
- delta_loss_text_aux: 0.029595
- delta_loss_clause_transition_aux: -0.039002
- delta_z_art_abs_mean: 0.004778
- delta_z_art_delta_abs_mean: -0.000347
- delta_event_prob_mean: -0.000787
- delta_event_presence_prob_mean: -0.001044
- delta_event_delta_prob_mean: 0.000306
- delta_event_rise_prob_mean: 0.000998
- delta_event_fall_prob_mean: -0.001154
- delta_event_energy_prob_mean: -0.000952
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002142
- delta_acoustic_energy_mean: -0.005476
- delta_acoustic_delta_abs_mean: 0.002059
- delta_text_aux_abs_mean: 0.000316

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
