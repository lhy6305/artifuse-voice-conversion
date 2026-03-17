# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.911644
- loss_acoustic: 0.542681
- loss_event: 4.637157
- loss_text_aux: 0.109765
- loss_text_aux_effective: 0.109765
- loss_text_aux_structural: 0.116611
- loss_text_aux_lexical: 0.09881
- loss_clause_transition_aux: 0.053048
- z_art_abs_mean: 0.34522
- z_art_delta_abs_mean: 0.01233
- event_prob_mean: 0.459201
- event_presence_prob_mean: 0.615511
- event_delta_prob_mean: 0.349288
- event_rise_prob_mean: 0.477371
- event_fall_prob_mean: 0.419834
- event_energy_prob_mean: 0.592501
- event_presence_peak_ratio: 0.807338
- acoustic_abs_mean: 0.906835
- acoustic_energy_mean: -3.42835
- acoustic_delta_abs_mean: 0.019173
- text_aux_abs_mean: 0.225023

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.266607
- loss_acoustic: 0.725729
- loss_event: 4.986702
- loss_text_aux: 0.20079
- loss_text_aux_effective: 0.20079
- loss_text_aux_structural: 0.259892
- loss_text_aux_lexical: 0.106226
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.241689
- z_art_delta_abs_mean: 0.009211
- event_prob_mean: 0.445804
- event_presence_prob_mean: 0.580166
- event_delta_prob_mean: 0.364103
- event_rise_prob_mean: 0.454217
- event_fall_prob_mean: 0.435912
- event_energy_prob_mean: 0.562398
- event_presence_peak_ratio: 0.946332
- acoustic_abs_mean: 1.131491
- acoustic_energy_mean: -4.314027
- acoustic_delta_abs_mean: 0.013463
- text_aux_abs_mean: 0.266341

## 对比
- delta_loss_total: 0.354963
- delta_loss_acoustic: 0.183048
- delta_loss_event: 0.349545
- delta_loss_text_aux: 0.091025
- delta_loss_text_aux_effective: 0.091025
- delta_loss_text_aux_structural: 0.143281
- delta_loss_text_aux_lexical: 0.007416
- delta_loss_clause_transition_aux: -0.053048
- delta_z_art_abs_mean: -0.103531
- delta_z_art_delta_abs_mean: -0.003119
- delta_event_prob_mean: -0.013397
- delta_event_presence_prob_mean: -0.035345
- delta_event_delta_prob_mean: 0.014815
- delta_event_rise_prob_mean: -0.023154
- delta_event_fall_prob_mean: 0.016078
- delta_event_energy_prob_mean: -0.030103
- delta_event_presence_peak_ratio: 0.138994
- delta_acoustic_abs_mean: 0.224656
- delta_acoustic_energy_mean: -0.885677
- delta_acoustic_delta_abs_mean: -0.00571
- delta_text_aux_abs_mean: 0.041318

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
