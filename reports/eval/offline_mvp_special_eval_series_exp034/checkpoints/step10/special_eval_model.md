# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.576112
- loss_acoustic: 16.769551
- loss_event: 5.507818
- loss_text_aux: 0.194071
- loss_clause_transition_aux: 0.038528
- z_art_abs_mean: 0.088213
- z_art_delta_abs_mean: 0.000442
- event_prob_mean: 0.500806
- event_presence_prob_mean: 0.542718
- event_delta_prob_mean: 0.517694
- event_rise_prob_mean: 0.545649
- event_fall_prob_mean: 0.512056
- event_energy_prob_mean: 0.461918
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.184938
- acoustic_energy_mean: -0.454919
- acoustic_delta_abs_mean: 0.135187
- text_aux_abs_mean: 0.10366

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.836152
- loss_acoustic: 13.053902
- loss_event: 5.501851
- loss_text_aux: 0.155681
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.091062
- z_art_delta_abs_mean: 0.000234
- event_prob_mean: 0.50043
- event_presence_prob_mean: 0.541693
- event_delta_prob_mean: 0.517924
- event_rise_prob_mean: 0.547091
- event_fall_prob_mean: 0.511039
- event_energy_prob_mean: 0.461377
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.18581
- acoustic_energy_mean: -0.458238
- acoustic_delta_abs_mean: 0.136723
- text_aux_abs_mean: 0.103675

## 对比
- delta_loss_total: -3.73996
- delta_loss_acoustic: -3.715649
- delta_loss_event: -0.005967
- delta_loss_text_aux: -0.03839
- delta_loss_clause_transition_aux: -0.038528
- delta_z_art_abs_mean: 0.002849
- delta_z_art_delta_abs_mean: -0.000208
- delta_event_prob_mean: -0.000376
- delta_event_presence_prob_mean: -0.001025
- delta_event_delta_prob_mean: 0.00023
- delta_event_rise_prob_mean: 0.001442
- delta_event_fall_prob_mean: -0.001017
- delta_event_energy_prob_mean: -0.000541
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000872
- delta_acoustic_energy_mean: -0.003319
- delta_acoustic_delta_abs_mean: 0.001536
- delta_text_aux_abs_mean: 1.5e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
