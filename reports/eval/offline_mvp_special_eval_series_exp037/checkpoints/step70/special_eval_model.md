# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.380006
- loss_acoustic: 3.843955
- loss_event: 4.991194
- loss_text_aux: 0.110241
- loss_text_aux_effective: 0.108303
- loss_clause_transition_aux: 0.046274
- z_art_abs_mean: 0.182611
- z_art_delta_abs_mean: 0.003246
- event_prob_mean: 0.47202
- event_presence_prob_mean: 0.586888
- event_delta_prob_mean: 0.413236
- event_rise_prob_mean: 0.490893
- event_fall_prob_mean: 0.439954
- event_energy_prob_mean: 0.566867
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.870108
- acoustic_energy_mean: -3.34931
- acoustic_delta_abs_mean: 0.021566
- text_aux_abs_mean: 0.239314

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.162432
- loss_acoustic: 1.546141
- loss_event: 5.144193
- loss_text_aux: 0.218816
- loss_text_aux_effective: 0.212128
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.162714
- z_art_delta_abs_mean: 0.00221
- event_prob_mean: 0.465597
- event_presence_prob_mean: 0.574895
- event_delta_prob_mean: 0.41805
- event_rise_prob_mean: 0.479264
- event_fall_prob_mean: 0.447668
- event_energy_prob_mean: 0.556785
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.951956
- acoustic_energy_mean: -3.69314
- acoustic_delta_abs_mean: 0.027918
- text_aux_abs_mean: 0.262562

## 对比
- delta_loss_total: -2.217574
- delta_loss_acoustic: -2.297814
- delta_loss_event: 0.152999
- delta_loss_text_aux: 0.108575
- delta_loss_text_aux_effective: 0.103825
- delta_loss_clause_transition_aux: -0.046274
- delta_z_art_abs_mean: -0.019897
- delta_z_art_delta_abs_mean: -0.001036
- delta_event_prob_mean: -0.006423
- delta_event_presence_prob_mean: -0.011993
- delta_event_delta_prob_mean: 0.004814
- delta_event_rise_prob_mean: -0.011629
- delta_event_fall_prob_mean: 0.007714
- delta_event_energy_prob_mean: -0.010082
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.081848
- delta_acoustic_energy_mean: -0.34383
- delta_acoustic_delta_abs_mean: 0.006352
- delta_text_aux_abs_mean: 0.023248

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
