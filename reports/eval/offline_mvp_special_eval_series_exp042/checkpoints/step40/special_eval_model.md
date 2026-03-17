# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.315488
- loss_acoustic: 6.585218
- loss_event: 5.331681
- loss_text_aux: 0.230709
- loss_text_aux_effective: 0.230709
- loss_text_aux_structural: 0.231898
- loss_text_aux_lexical: 0.228805
- loss_clause_transition_aux: 0.035994
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.024235
- z_art_abs_mean: 0.222075
- z_art_delta_abs_mean: 0.001054
- event_prob_mean: 0.491157
- event_presence_prob_mean: 0.553198
- event_delta_prob_mean: 0.534548
- event_rise_prob_mean: 0.469435
- event_fall_prob_mean: 0.520602
- event_energy_prob_mean: 0.510911
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878114
- acoustic_energy_mean: -3.376638
- acoustic_delta_abs_mean: 0.068287
- text_aux_abs_mean: 0.435221

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.212902
- loss_acoustic: 2.456667
- loss_event: 5.366788
- loss_text_aux: 0.361276
- loss_text_aux_effective: 0.361276
- loss_text_aux_structural: 0.417264
- loss_text_aux_lexical: 0.271694
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001566
- z_art_abs_mean: 0.229843
- z_art_delta_abs_mean: 0.000341
- event_prob_mean: 0.490018
- event_presence_prob_mean: 0.552369
- event_delta_prob_mean: 0.539135
- event_rise_prob_mean: 0.465736
- event_fall_prob_mean: 0.525317
- event_energy_prob_mean: 0.506628
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884645
- acoustic_energy_mean: -3.400552
- acoustic_delta_abs_mean: 0.07311
- text_aux_abs_mean: 0.438195

## 对比
- delta_loss_total: -4.102586
- delta_loss_acoustic: -4.128551
- delta_loss_event: 0.035107
- delta_loss_text_aux: 0.130567
- delta_loss_text_aux_effective: 0.130567
- delta_loss_text_aux_structural: 0.185366
- delta_loss_text_aux_lexical: 0.042889
- delta_loss_clause_transition_aux: -0.035994
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.022669
- delta_z_art_abs_mean: 0.007768
- delta_z_art_delta_abs_mean: -0.000713
- delta_event_prob_mean: -0.001139
- delta_event_presence_prob_mean: -0.000829
- delta_event_delta_prob_mean: 0.004587
- delta_event_rise_prob_mean: -0.003699
- delta_event_fall_prob_mean: 0.004715
- delta_event_energy_prob_mean: -0.004283
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006531
- delta_acoustic_energy_mean: -0.023914
- delta_acoustic_delta_abs_mean: 0.004823
- delta_text_aux_abs_mean: 0.002974

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
