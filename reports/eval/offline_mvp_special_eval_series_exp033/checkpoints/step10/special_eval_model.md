# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.575129
- loss_acoustic: 16.768248
- loss_event: 5.50839
- loss_text_aux: 0.19418
- loss_clause_transition_aux: 0.038551
- z_art_abs_mean: 0.088585
- z_art_delta_abs_mean: 0.000445
- event_prob_mean: 0.500487
- event_presence_prob_mean: 0.541746
- event_delta_prob_mean: 0.51762
- event_rise_prob_mean: 0.546056
- event_fall_prob_mean: 0.512127
- event_energy_prob_mean: 0.461874
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.185089
- acoustic_energy_mean: -0.455094
- acoustic_delta_abs_mean: 0.134247
- text_aux_abs_mean: 0.103007

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.834148
- loss_acoustic: 13.052483
- loss_event: 5.500844
- loss_text_aux: 0.155267
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.091482
- z_art_delta_abs_mean: 0.000238
- event_prob_mean: 0.500095
- event_presence_prob_mean: 0.540671
- event_delta_prob_mean: 0.51783
- event_rise_prob_mean: 0.547514
- event_fall_prob_mean: 0.511113
- event_energy_prob_mean: 0.461337
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.185964
- acoustic_energy_mean: -0.458435
- acoustic_delta_abs_mean: 0.135773
- text_aux_abs_mean: 0.103023

## 对比
- delta_loss_total: -3.740981
- delta_loss_acoustic: -3.715765
- delta_loss_event: -0.007546
- delta_loss_text_aux: -0.038913
- delta_loss_clause_transition_aux: -0.038551
- delta_z_art_abs_mean: 0.002897
- delta_z_art_delta_abs_mean: -0.000207
- delta_event_prob_mean: -0.000392
- delta_event_presence_prob_mean: -0.001075
- delta_event_delta_prob_mean: 0.00021
- delta_event_rise_prob_mean: 0.001458
- delta_event_fall_prob_mean: -0.001014
- delta_event_energy_prob_mean: -0.000537
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000875
- delta_acoustic_energy_mean: -0.003341
- delta_acoustic_delta_abs_mean: 0.001526
- delta_text_aux_abs_mean: 1.6e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
