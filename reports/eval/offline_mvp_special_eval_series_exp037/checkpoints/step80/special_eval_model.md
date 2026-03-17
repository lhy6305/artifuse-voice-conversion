# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.260156
- loss_acoustic: 1.770704
- loss_event: 4.890248
- loss_text_aux: 0.109704
- loss_text_aux_effective: 0.112116
- loss_clause_transition_aux: 0.046875
- z_art_abs_mean: 0.200063
- z_art_delta_abs_mean: 0.006873
- event_prob_mean: 0.464645
- event_presence_prob_mean: 0.575943
- event_delta_prob_mean: 0.405952
- event_rise_prob_mean: 0.473733
- event_fall_prob_mean: 0.441873
- event_energy_prob_mean: 0.559187
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.896811
- acoustic_energy_mean: -3.429826
- acoustic_delta_abs_mean: 0.009671
- text_aux_abs_mean: 0.231136

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.731947
- loss_acoustic: 1.136887
- loss_event: 5.094328
- loss_text_aux: 0.219341
- loss_text_aux_effective: 0.221442
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.154234
- z_art_delta_abs_mean: 0.004509
- event_prob_mean: 0.455288
- event_presence_prob_mean: 0.554402
- event_delta_prob_mean: 0.416086
- event_rise_prob_mean: 0.4577
- event_fall_prob_mean: 0.456799
- event_energy_prob_mean: 0.541011
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.08571
- acoustic_energy_mean: -4.212385
- acoustic_delta_abs_mean: 0.00731
- text_aux_abs_mean: 0.280174

## 对比
- delta_loss_total: -0.528209
- delta_loss_acoustic: -0.633817
- delta_loss_event: 0.20408
- delta_loss_text_aux: 0.109637
- delta_loss_text_aux_effective: 0.109326
- delta_loss_clause_transition_aux: -0.046875
- delta_z_art_abs_mean: -0.045829
- delta_z_art_delta_abs_mean: -0.002364
- delta_event_prob_mean: -0.009357
- delta_event_presence_prob_mean: -0.021541
- delta_event_delta_prob_mean: 0.010134
- delta_event_rise_prob_mean: -0.016033
- delta_event_fall_prob_mean: 0.014926
- delta_event_energy_prob_mean: -0.018176
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.188899
- delta_acoustic_energy_mean: -0.782559
- delta_acoustic_delta_abs_mean: -0.002361
- delta_text_aux_abs_mean: 0.049038

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
