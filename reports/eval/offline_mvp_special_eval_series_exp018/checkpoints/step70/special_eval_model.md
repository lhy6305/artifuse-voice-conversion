# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.944619
- loss_acoustic: 3.414453
- loss_event: 4.978374
- loss_text_aux: 0.108625
- loss_text_aux_effective: 0.108625
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.04627
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.184503
- z_art_delta_abs_mean: 0.003824
- event_prob_mean: 0.471064
- event_presence_prob_mean: 0.588245
- event_delta_prob_mean: 0.413366
- event_rise_prob_mean: 0.490407
- event_fall_prob_mean: 0.438081
- event_energy_prob_mean: 0.565384
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.916773
- acoustic_energy_mean: -3.573607
- acoustic_delta_abs_mean: 0.014203
- text_aux_abs_mean: 0.277574

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.134111
- loss_acoustic: 1.514257
- loss_event: 5.135678
- loss_text_aux: 0.249798
- loss_text_aux_effective: 0.249798
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.162413
- z_art_delta_abs_mean: 0.00257
- event_prob_mean: 0.464154
- event_presence_prob_mean: 0.575169
- event_delta_prob_mean: 0.419189
- event_rise_prob_mean: 0.476993
- event_fall_prob_mean: 0.447267
- event_energy_prob_mean: 0.554696
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.012337
- acoustic_energy_mean: -3.983617
- acoustic_delta_abs_mean: 0.013195
- text_aux_abs_mean: 0.306975

## 对比
- delta_loss_total: -1.810508
- delta_loss_acoustic: -1.900196
- delta_loss_event: 0.157304
- delta_loss_text_aux: 0.141173
- delta_loss_text_aux_effective: 0.141173
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.04627
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.02209
- delta_z_art_delta_abs_mean: -0.001254
- delta_event_prob_mean: -0.00691
- delta_event_presence_prob_mean: -0.013076
- delta_event_delta_prob_mean: 0.005823
- delta_event_rise_prob_mean: -0.013414
- delta_event_fall_prob_mean: 0.009186
- delta_event_energy_prob_mean: -0.010688
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.095564
- delta_acoustic_energy_mean: -0.41001
- delta_acoustic_delta_abs_mean: -0.001008
- delta_text_aux_abs_mean: 0.029401

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
