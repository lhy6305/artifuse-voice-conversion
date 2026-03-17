# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.690022
- loss_acoustic: 12.912136
- loss_event: 5.450036
- loss_text_aux: 0.193706
- loss_clause_transition_aux: 0.038995
- z_art_abs_mean: 0.133753
- z_art_delta_abs_mean: 0.000599
- event_prob_mean: 0.492752
- event_presence_prob_mean: 0.54854
- event_delta_prob_mean: 0.512551
- event_rise_prob_mean: 0.53958
- event_fall_prob_mean: 0.508602
- event_energy_prob_mean: 0.455068
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.409928
- acoustic_energy_mean: -1.143421
- acoustic_delta_abs_mean: 0.084467
- text_aux_abs_mean: 0.17135

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.841368
- loss_acoustic: 9.068198
- loss_event: 5.456678
- loss_text_aux: 0.223147
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.138538
- z_art_delta_abs_mean: 0.000251
- event_prob_mean: 0.491974
- event_presence_prob_mean: 0.547516
- event_delta_prob_mean: 0.51285
- event_rise_prob_mean: 0.540589
- event_fall_prob_mean: 0.507449
- event_energy_prob_mean: 0.454134
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.412078
- acoustic_energy_mean: -1.148899
- acoustic_delta_abs_mean: 0.086519
- text_aux_abs_mean: 0.171672

## 对比
- delta_loss_total: -3.848654
- delta_loss_acoustic: -3.843938
- delta_loss_event: 0.006642
- delta_loss_text_aux: 0.029441
- delta_loss_clause_transition_aux: -0.038995
- delta_z_art_abs_mean: 0.004785
- delta_z_art_delta_abs_mean: -0.000348
- delta_event_prob_mean: -0.000778
- delta_event_presence_prob_mean: -0.001024
- delta_event_delta_prob_mean: 0.000299
- delta_event_rise_prob_mean: 0.001009
- delta_event_fall_prob_mean: -0.001153
- delta_event_energy_prob_mean: -0.000934
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.00215
- delta_acoustic_energy_mean: -0.005478
- delta_acoustic_delta_abs_mean: 0.002052
- delta_text_aux_abs_mean: 0.000322

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
