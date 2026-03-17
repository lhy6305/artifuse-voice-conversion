# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.910157
- loss_acoustic: 0.540196
- loss_event: 4.634441
- loss_text_aux: 0.109701
- loss_text_aux_effective: 0.109701
- loss_text_aux_structural: 0.116532
- loss_text_aux_lexical: 0.098772
- loss_clause_transition_aux: 0.053081
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.01164
- z_art_abs_mean: 0.346439
- z_art_delta_abs_mean: 0.012367
- event_prob_mean: 0.459514
- event_presence_prob_mean: 0.617655
- event_delta_prob_mean: 0.349128
- event_rise_prob_mean: 0.477098
- event_fall_prob_mean: 0.41973
- event_energy_prob_mean: 0.594371
- event_presence_peak_ratio: 0.816341
- acoustic_abs_mean: 0.907569
- acoustic_energy_mean: -3.431178
- acoustic_delta_abs_mean: 0.01915
- text_aux_abs_mean: 0.225365

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.267083
- loss_acoustic: 0.726664
- loss_event: 4.985048
- loss_text_aux: 0.201008
- loss_text_aux_effective: 0.201008
- loss_text_aux_structural: 0.260147
- loss_text_aux_lexical: 0.106384
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001526
- z_art_abs_mean: 0.24268
- z_art_delta_abs_mean: 0.009236
- event_prob_mean: 0.44613
- event_presence_prob_mean: 0.582176
- event_delta_prob_mean: 0.363926
- event_rise_prob_mean: 0.454027
- event_fall_prob_mean: 0.435916
- event_energy_prob_mean: 0.564175
- event_presence_peak_ratio: 0.950146
- acoustic_abs_mean: 1.131822
- acoustic_energy_mean: -4.315936
- acoustic_delta_abs_mean: 0.013402
- text_aux_abs_mean: 0.266581

## 对比
- delta_loss_total: 0.356926
- delta_loss_acoustic: 0.186468
- delta_loss_event: 0.350607
- delta_loss_text_aux: 0.091307
- delta_loss_text_aux_effective: 0.091307
- delta_loss_text_aux_structural: 0.143615
- delta_loss_text_aux_lexical: 0.007612
- delta_loss_clause_transition_aux: -0.053081
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.010114
- delta_z_art_abs_mean: -0.103759
- delta_z_art_delta_abs_mean: -0.003131
- delta_event_prob_mean: -0.013384
- delta_event_presence_prob_mean: -0.035479
- delta_event_delta_prob_mean: 0.014798
- delta_event_rise_prob_mean: -0.023071
- delta_event_fall_prob_mean: 0.016186
- delta_event_energy_prob_mean: -0.030196
- delta_event_presence_peak_ratio: 0.133805
- delta_acoustic_abs_mean: 0.224253
- delta_acoustic_energy_mean: -0.884758
- delta_acoustic_delta_abs_mean: -0.005748
- delta_text_aux_abs_mean: 0.041216

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
