# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.593971
- loss_acoustic: 8.850491
- loss_event: 5.379209
- loss_text_aux: 0.20864
- loss_text_aux_effective: 0.203771
- loss_clause_transition_aux: 0.035622
- z_art_abs_mean: 0.163212
- z_art_delta_abs_mean: 0.000817
- event_prob_mean: 0.501344
- event_presence_prob_mean: 0.548514
- event_delta_prob_mean: 0.533989
- event_rise_prob_mean: 0.492234
- event_fall_prob_mean: 0.532399
- event_energy_prob_mean: 0.515779
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.574685
- acoustic_energy_mean: -2.122218
- acoustic_delta_abs_mean: 0.071527
- text_aux_abs_mean: 0.269859

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.616385
- loss_acoustic: 4.883172
- loss_event: 5.412691
- loss_text_aux: 0.220813
- loss_text_aux_effective: 0.133146
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.167093
- z_art_delta_abs_mean: 0.000298
- event_prob_mean: 0.500619
- event_presence_prob_mean: 0.547903
- event_delta_prob_mean: 0.537084
- event_rise_prob_mean: 0.490253
- event_fall_prob_mean: 0.536842
- event_energy_prob_mean: 0.512326
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.577925
- acoustic_energy_mean: -2.137429
- acoustic_delta_abs_mean: 0.069119
- text_aux_abs_mean: 0.271816

## 对比
- delta_loss_total: -3.977586
- delta_loss_acoustic: -3.967319
- delta_loss_event: 0.033482
- delta_loss_text_aux: 0.012173
- delta_loss_text_aux_effective: -0.070625
- delta_loss_clause_transition_aux: -0.035622
- delta_z_art_abs_mean: 0.003881
- delta_z_art_delta_abs_mean: -0.000519
- delta_event_prob_mean: -0.000725
- delta_event_presence_prob_mean: -0.000611
- delta_event_delta_prob_mean: 0.003095
- delta_event_rise_prob_mean: -0.001981
- delta_event_fall_prob_mean: 0.004443
- delta_event_energy_prob_mean: -0.003453
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.00324
- delta_acoustic_energy_mean: -0.015211
- delta_acoustic_delta_abs_mean: -0.002408
- delta_text_aux_abs_mean: 0.001957

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
