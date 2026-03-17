# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.289033
- loss_acoustic: 1.799096
- loss_event: 4.890612
- loss_text_aux: 0.113773
- loss_text_aux_effective: 0.113773
- loss_text_aux_structural: 0.125866
- loss_text_aux_lexical: 0.094424
- loss_clause_transition_aux: 0.046885
- z_art_abs_mean: 0.199501
- z_art_delta_abs_mean: 0.006833
- event_prob_mean: 0.464496
- event_presence_prob_mean: 0.575805
- event_delta_prob_mean: 0.405977
- event_rise_prob_mean: 0.473337
- event_fall_prob_mean: 0.441594
- event_energy_prob_mean: 0.559213
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.900009
- acoustic_energy_mean: -3.444779
- acoustic_delta_abs_mean: 0.01029
- text_aux_abs_mean: 0.217064

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.738851
- loss_acoustic: 1.152477
- loss_event: 5.094754
- loss_text_aux: 0.177054
- loss_text_aux_effective: 0.177054
- loss_text_aux_structural: 0.248128
- loss_text_aux_lexical: 0.063336
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.154336
- z_art_delta_abs_mean: 0.004483
- event_prob_mean: 0.455182
- event_presence_prob_mean: 0.554339
- event_delta_prob_mean: 0.416063
- event_rise_prob_mean: 0.457465
- event_fall_prob_mean: 0.456577
- event_energy_prob_mean: 0.541036
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.087362
- acoustic_energy_mean: -4.216316
- acoustic_delta_abs_mean: 0.009048
- text_aux_abs_mean: 0.256905

## 对比
- delta_loss_total: -0.550182
- delta_loss_acoustic: -0.646619
- delta_loss_event: 0.204142
- delta_loss_text_aux: 0.063281
- delta_loss_text_aux_effective: 0.063281
- delta_loss_text_aux_structural: 0.122262
- delta_loss_text_aux_lexical: -0.031088
- delta_loss_clause_transition_aux: -0.046885
- delta_z_art_abs_mean: -0.045165
- delta_z_art_delta_abs_mean: -0.00235
- delta_event_prob_mean: -0.009314
- delta_event_presence_prob_mean: -0.021466
- delta_event_delta_prob_mean: 0.010086
- delta_event_rise_prob_mean: -0.015872
- delta_event_fall_prob_mean: 0.014983
- delta_event_energy_prob_mean: -0.018177
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.187353
- delta_acoustic_energy_mean: -0.771537
- delta_acoustic_delta_abs_mean: -0.001242
- delta_text_aux_abs_mean: 0.039841

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
