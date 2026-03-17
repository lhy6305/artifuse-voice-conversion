# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.593907
- loss_acoustic: 12.828944
- loss_event: 5.414017
- loss_text_aux: 0.194414
- loss_text_aux_effective: 0.223713
- loss_clause_transition_aux: 0.036285
- z_art_abs_mean: 0.115358
- z_art_delta_abs_mean: 0.000639
- event_prob_mean: 0.50633
- event_presence_prob_mean: 0.537183
- event_delta_prob_mean: 0.528435
- event_rise_prob_mean: 0.513519
- event_fall_prob_mean: 0.528974
- event_energy_prob_mean: 0.519665
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373203
- acoustic_energy_mean: -1.145967
- acoustic_delta_abs_mean: 0.153257
- text_aux_abs_mean: 0.186863

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.765262
- loss_acoustic: 9.017519
- loss_event: 5.445348
- loss_text_aux: 0.145938
- loss_text_aux_effective: 0.124099
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.117873
- z_art_delta_abs_mean: 0.000312
- event_prob_mean: 0.505805
- event_presence_prob_mean: 0.536358
- event_delta_prob_mean: 0.53054
- event_rise_prob_mean: 0.513128
- event_fall_prob_mean: 0.532539
- event_energy_prob_mean: 0.51681
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375294
- acoustic_energy_mean: -1.153719
- acoustic_delta_abs_mean: 0.15256
- text_aux_abs_mean: 0.187952

## 对比
- delta_loss_total: -3.828645
- delta_loss_acoustic: -3.811425
- delta_loss_event: 0.031331
- delta_loss_text_aux: -0.048476
- delta_loss_text_aux_effective: -0.099614
- delta_loss_clause_transition_aux: -0.036285
- delta_z_art_abs_mean: 0.002515
- delta_z_art_delta_abs_mean: -0.000327
- delta_event_prob_mean: -0.000525
- delta_event_presence_prob_mean: -0.000825
- delta_event_delta_prob_mean: 0.002105
- delta_event_rise_prob_mean: -0.000391
- delta_event_fall_prob_mean: 0.003565
- delta_event_energy_prob_mean: -0.002855
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002091
- delta_acoustic_energy_mean: -0.007752
- delta_acoustic_delta_abs_mean: -0.000697
- delta_text_aux_abs_mean: 0.001089

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
