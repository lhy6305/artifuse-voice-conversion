# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.663196
- loss_acoustic: 0.298871
- loss_event: 4.631983
- loss_text_aux: 0.115973
- loss_clause_transition_aux: 0.051605
- z_art_abs_mean: 0.284639
- z_art_delta_abs_mean: 0.008846
- event_prob_mean: 0.442438
- event_presence_prob_mean: 0.597853
- event_delta_prob_mean: 0.319686
- event_rise_prob_mean: 0.475957
- event_fall_prob_mean: 0.528209
- event_energy_prob_mean: 0.589621
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.889108
- acoustic_energy_mean: -3.432531
- acoustic_delta_abs_mean: 0.008712
- text_aux_abs_mean: 0.258216

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.774738
- loss_acoustic: 0.266885
- loss_event: 4.905027
- loss_text_aux: 0.246464
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.234061
- z_art_delta_abs_mean: 0.007558
- event_prob_mean: 0.433759
- event_presence_prob_mean: 0.578723
- event_delta_prob_mean: 0.325822
- event_rise_prob_mean: 0.472982
- event_fall_prob_mean: 0.516525
- event_energy_prob_mean: 0.571969
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.041906
- acoustic_energy_mean: -4.011851
- acoustic_delta_abs_mean: 0.004695
- text_aux_abs_mean: 0.284895

## 对比
- delta_loss_total: 0.111542
- delta_loss_acoustic: -0.031986
- delta_loss_event: 0.273044
- delta_loss_text_aux: 0.130491
- delta_loss_clause_transition_aux: -0.051605
- delta_z_art_abs_mean: -0.050578
- delta_z_art_delta_abs_mean: -0.001288
- delta_event_prob_mean: -0.008679
- delta_event_presence_prob_mean: -0.01913
- delta_event_delta_prob_mean: 0.006136
- delta_event_rise_prob_mean: -0.002975
- delta_event_fall_prob_mean: -0.011684
- delta_event_energy_prob_mean: -0.017652
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.152798
- delta_acoustic_energy_mean: -0.57932
- delta_acoustic_delta_abs_mean: -0.004017
- delta_text_aux_abs_mean: 0.026679

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
