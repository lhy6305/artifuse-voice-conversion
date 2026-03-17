# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.522185
- loss_acoustic: 1.088836
- loss_event: 4.763561
- loss_text_aux: 0.122599
- loss_text_aux_effective: 0.126455
- loss_clause_transition_aux: 0.049486
- z_art_abs_mean: 0.272649
- z_art_delta_abs_mean: 0.011196
- event_prob_mean: 0.461257
- event_presence_prob_mean: 0.587851
- event_delta_prob_mean: 0.384704
- event_rise_prob_mean: 0.464811
- event_fall_prob_mean: 0.427411
- event_energy_prob_mean: 0.569336
- event_presence_peak_ratio: 0.770264
- acoustic_abs_mean: 0.80735
- acoustic_energy_mean: -3.040604
- acoustic_delta_abs_mean: 0.035095
- text_aux_abs_mean: 0.216396

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.241678
- loss_acoustic: 0.669498
- loss_event: 5.041529
- loss_text_aux: 0.212864
- loss_text_aux_effective: 0.226336
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.180111
- z_art_delta_abs_mean: 0.007685
- event_prob_mean: 0.448837
- event_presence_prob_mean: 0.556604
- event_delta_prob_mean: 0.399132
- event_rise_prob_mean: 0.444864
- event_fall_prob_mean: 0.446763
- event_energy_prob_mean: 0.542493
- event_presence_peak_ratio: 0.92344
- acoustic_abs_mean: 1.082851
- acoustic_energy_mean: -4.168178
- acoustic_delta_abs_mean: 0.016162
- text_aux_abs_mean: 0.272037

## 对比
- delta_loss_total: -0.280507
- delta_loss_acoustic: -0.419338
- delta_loss_event: 0.277968
- delta_loss_text_aux: 0.090265
- delta_loss_text_aux_effective: 0.099881
- delta_loss_clause_transition_aux: -0.049486
- delta_z_art_abs_mean: -0.092538
- delta_z_art_delta_abs_mean: -0.003511
- delta_event_prob_mean: -0.01242
- delta_event_presence_prob_mean: -0.031247
- delta_event_delta_prob_mean: 0.014428
- delta_event_rise_prob_mean: -0.019947
- delta_event_fall_prob_mean: 0.019352
- delta_event_energy_prob_mean: -0.026843
- delta_event_presence_peak_ratio: 0.153176
- delta_acoustic_abs_mean: 0.275501
- delta_acoustic_energy_mean: -1.127574
- delta_acoustic_delta_abs_mean: -0.018933
- delta_text_aux_abs_mean: 0.055641

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
