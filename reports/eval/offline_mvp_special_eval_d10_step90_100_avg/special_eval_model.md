# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d10_step90_100/d10_step90_100_avg.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.030039
- loss_acoustic: 0.645678
- loss_event: 4.666312
- loss_text_aux: 0.11377
- loss_text_aux_effective: 0.11377
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053222
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.353356
- z_art_delta_abs_mean: 0.012278
- event_prob_mean: 0.45935
- event_presence_prob_mean: 0.620065
- event_delta_prob_mean: 0.345563
- event_rise_prob_mean: 0.480739
- event_fall_prob_mean: 0.411626
- event_energy_prob_mean: 0.592297
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.836442
- acoustic_energy_mean: -3.158911
- acoustic_delta_abs_mean: 0.026106
- text_aux_abs_mean: 0.226784

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.939542
- loss_acoustic: 0.390583
- loss_event: 4.999869
- loss_text_aux: 0.208661
- loss_text_aux_effective: 0.208661
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.251548
- z_art_delta_abs_mean: 0.009116
- event_prob_mean: 0.446852
- event_presence_prob_mean: 0.586824
- event_delta_prob_mean: 0.360026
- event_rise_prob_mean: 0.457368
- event_fall_prob_mean: 0.430144
- event_energy_prob_mean: 0.565183
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.045702
- acoustic_energy_mean: -3.975217
- acoustic_delta_abs_mean: 0.017721
- text_aux_abs_mean: 0.270349

## 对比
- delta_loss_total: -0.090497
- delta_loss_acoustic: -0.255095
- delta_loss_event: 0.333557
- delta_loss_text_aux: 0.094891
- delta_loss_text_aux_effective: 0.094891
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053222
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.101808
- delta_z_art_delta_abs_mean: -0.003162
- delta_event_prob_mean: -0.012498
- delta_event_presence_prob_mean: -0.033241
- delta_event_delta_prob_mean: 0.014463
- delta_event_rise_prob_mean: -0.023371
- delta_event_fall_prob_mean: 0.018518
- delta_event_energy_prob_mean: -0.027114
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.20926
- delta_acoustic_energy_mean: -0.816306
- delta_acoustic_delta_abs_mean: -0.008385
- delta_text_aux_abs_mean: 0.043565

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
