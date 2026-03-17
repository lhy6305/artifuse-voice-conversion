# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.760997
- loss_acoustic: 7.108171
- loss_event: 5.224542
- loss_text_aux: 0.196163
- loss_text_aux_effective: 0.129826
- loss_clause_transition_aux: 0.038716
- z_art_abs_mean: 0.227003
- z_art_delta_abs_mean: 0.001299
- event_prob_mean: 0.478606
- event_presence_prob_mean: 0.556605
- event_delta_prob_mean: 0.503811
- event_rise_prob_mean: 0.462052
- event_fall_prob_mean: 0.491494
- event_energy_prob_mean: 0.522961
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.185695
- acoustic_energy_mean: -4.580763
- acoustic_delta_abs_mean: 0.034327
- text_aux_abs_mean: 0.452389

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.819993
- loss_acoustic: 3.122438
- loss_event: 5.279957
- loss_text_aux: 0.40838
- loss_text_aux_effective: 0.28586
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.237238
- z_art_delta_abs_mean: 0.000507
- event_prob_mean: 0.476397
- event_presence_prob_mean: 0.554168
- event_delta_prob_mean: 0.508982
- event_rise_prob_mean: 0.456503
- event_fall_prob_mean: 0.495889
- event_energy_prob_mean: 0.517832
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.198562
- acoustic_energy_mean: -4.644309
- acoustic_delta_abs_mean: 0.027658
- text_aux_abs_mean: 0.457695

## 对比
- delta_loss_total: -3.941004
- delta_loss_acoustic: -3.985733
- delta_loss_event: 0.055415
- delta_loss_text_aux: 0.212217
- delta_loss_text_aux_effective: 0.156034
- delta_loss_clause_transition_aux: -0.038716
- delta_z_art_abs_mean: 0.010235
- delta_z_art_delta_abs_mean: -0.000792
- delta_event_prob_mean: -0.002209
- delta_event_presence_prob_mean: -0.002437
- delta_event_delta_prob_mean: 0.005171
- delta_event_rise_prob_mean: -0.005549
- delta_event_fall_prob_mean: 0.004395
- delta_event_energy_prob_mean: -0.005129
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.012867
- delta_acoustic_energy_mean: -0.063546
- delta_acoustic_delta_abs_mean: -0.006669
- delta_text_aux_abs_mean: 0.005306

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
