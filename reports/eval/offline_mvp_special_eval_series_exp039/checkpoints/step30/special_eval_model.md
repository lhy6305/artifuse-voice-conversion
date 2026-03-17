# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.590206
- loss_acoustic: 8.85027
- loss_event: 5.379482
- loss_text_aux: 0.18536
- loss_text_aux_effective: 0.18536
- loss_text_aux_structural: 0.188562
- loss_text_aux_lexical: 0.180237
- loss_clause_transition_aux: 0.03563
- z_art_abs_mean: 0.163791
- z_art_delta_abs_mean: 0.000817
- event_prob_mean: 0.501307
- event_presence_prob_mean: 0.5485
- event_delta_prob_mean: 0.534009
- event_rise_prob_mean: 0.492323
- event_fall_prob_mean: 0.532203
- event_energy_prob_mean: 0.515584
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.574681
- acoustic_energy_mean: -2.122281
- acoustic_delta_abs_mean: 0.071398
- text_aux_abs_mean: 0.314523

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.63731
- loss_acoustic: 4.882835
- loss_event: 5.412823
- loss_text_aux: 0.239132
- loss_text_aux_effective: 0.239132
- loss_text_aux_structural: 0.300036
- loss_text_aux_lexical: 0.141686
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.167664
- z_art_delta_abs_mean: 0.000297
- event_prob_mean: 0.500587
- event_presence_prob_mean: 0.547899
- event_delta_prob_mean: 0.537109
- event_rise_prob_mean: 0.490356
- event_fall_prob_mean: 0.536633
- event_energy_prob_mean: 0.512146
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.577912
- acoustic_energy_mean: -2.137474
- acoustic_delta_abs_mean: 0.068959
- text_aux_abs_mean: 0.316753

## 对比
- delta_loss_total: -3.952896
- delta_loss_acoustic: -3.967435
- delta_loss_event: 0.033341
- delta_loss_text_aux: 0.053772
- delta_loss_text_aux_effective: 0.053772
- delta_loss_text_aux_structural: 0.111474
- delta_loss_text_aux_lexical: -0.038551
- delta_loss_clause_transition_aux: -0.03563
- delta_z_art_abs_mean: 0.003873
- delta_z_art_delta_abs_mean: -0.00052
- delta_event_prob_mean: -0.00072
- delta_event_presence_prob_mean: -0.000601
- delta_event_delta_prob_mean: 0.0031
- delta_event_rise_prob_mean: -0.001967
- delta_event_fall_prob_mean: 0.00443
- delta_event_energy_prob_mean: -0.003438
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.003231
- delta_acoustic_energy_mean: -0.015193
- delta_acoustic_delta_abs_mean: -0.002439
- delta_text_aux_abs_mean: 0.00223

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
