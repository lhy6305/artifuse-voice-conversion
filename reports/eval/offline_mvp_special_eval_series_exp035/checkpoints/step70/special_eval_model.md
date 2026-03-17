# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.37992
- loss_acoustic: 3.843858
- loss_event: 4.991193
- loss_text_aux: 0.11069
- loss_text_aux_effective: 0.108361
- loss_clause_transition_aux: 0.046274
- z_art_abs_mean: 0.182615
- z_art_delta_abs_mean: 0.003246
- event_prob_mean: 0.472019
- event_presence_prob_mean: 0.586889
- event_delta_prob_mean: 0.413241
- event_rise_prob_mean: 0.490891
- event_fall_prob_mean: 0.439959
- event_energy_prob_mean: 0.566862
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.87016
- acoustic_energy_mean: -3.349507
- acoustic_delta_abs_mean: 0.021624
- text_aux_abs_mean: 0.239455

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.162429
- loss_acoustic: 1.54614
- loss_event: 5.144192
- loss_text_aux: 0.219593
- loss_text_aux_effective: 0.212122
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.16272
- z_art_delta_abs_mean: 0.00221
- event_prob_mean: 0.465596
- event_presence_prob_mean: 0.574895
- event_delta_prob_mean: 0.418055
- event_rise_prob_mean: 0.479262
- event_fall_prob_mean: 0.447674
- event_energy_prob_mean: 0.55678
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.952015
- acoustic_energy_mean: -3.693343
- acoustic_delta_abs_mean: 0.028006
- text_aux_abs_mean: 0.262714

## 对比
- delta_loss_total: -2.217491
- delta_loss_acoustic: -2.297718
- delta_loss_event: 0.152999
- delta_loss_text_aux: 0.108903
- delta_loss_text_aux_effective: 0.103761
- delta_loss_clause_transition_aux: -0.046274
- delta_z_art_abs_mean: -0.019895
- delta_z_art_delta_abs_mean: -0.001036
- delta_event_prob_mean: -0.006423
- delta_event_presence_prob_mean: -0.011994
- delta_event_delta_prob_mean: 0.004814
- delta_event_rise_prob_mean: -0.011629
- delta_event_fall_prob_mean: 0.007715
- delta_event_energy_prob_mean: -0.010082
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.081855
- delta_acoustic_energy_mean: -0.343836
- delta_acoustic_delta_abs_mean: 0.006382
- delta_text_aux_abs_mean: 0.023259

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
