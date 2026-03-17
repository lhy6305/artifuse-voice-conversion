# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.404872
- loss_acoustic: 3.867166
- loss_event: 4.99131
- loss_text_aux: 0.116394
- loss_text_aux_effective: 0.116394
- loss_text_aux_structural: 0.129219
- loss_text_aux_lexical: 0.095873
- loss_clause_transition_aux: 0.046288
- z_art_abs_mean: 0.18235
- z_art_delta_abs_mean: 0.003214
- event_prob_mean: 0.471865
- event_presence_prob_mean: 0.586851
- event_delta_prob_mean: 0.413186
- event_rise_prob_mean: 0.490482
- event_fall_prob_mean: 0.439719
- event_energy_prob_mean: 0.56697
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.870947
- acoustic_energy_mean: -3.353206
- acoustic_delta_abs_mean: 0.022641
- text_aux_abs_mean: 0.224528

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.164292
- loss_acoustic: 1.553106
- loss_event: 5.144284
- loss_text_aux: 0.186465
- loss_text_aux_effective: 0.186465
- loss_text_aux_structural: 0.263415
- loss_text_aux_lexical: 0.063346
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.163135
- z_art_delta_abs_mean: 0.00219
- event_prob_mean: 0.465479
- event_presence_prob_mean: 0.574933
- event_delta_prob_mean: 0.417942
- event_rise_prob_mean: 0.47897
- event_fall_prob_mean: 0.447447
- event_energy_prob_mean: 0.556911
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.951764
- acoustic_energy_mean: -3.692725
- acoustic_delta_abs_mean: 0.029233
- text_aux_abs_mean: 0.243741

## 对比
- delta_loss_total: -2.24058
- delta_loss_acoustic: -2.31406
- delta_loss_event: 0.152974
- delta_loss_text_aux: 0.070071
- delta_loss_text_aux_effective: 0.070071
- delta_loss_text_aux_structural: 0.134196
- delta_loss_text_aux_lexical: -0.032527
- delta_loss_clause_transition_aux: -0.046288
- delta_z_art_abs_mean: -0.019215
- delta_z_art_delta_abs_mean: -0.001024
- delta_event_prob_mean: -0.006386
- delta_event_presence_prob_mean: -0.011918
- delta_event_delta_prob_mean: 0.004756
- delta_event_rise_prob_mean: -0.011512
- delta_event_fall_prob_mean: 0.007728
- delta_event_energy_prob_mean: -0.010059
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.080817
- delta_acoustic_energy_mean: -0.339519
- delta_acoustic_delta_abs_mean: 0.006592
- delta_text_aux_abs_mean: 0.019213

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
