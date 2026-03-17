# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.522161
- loss_acoustic: 1.08958
- loss_event: 4.760102
- loss_text_aux: 0.118282
- loss_text_aux_effective: 0.118282
- loss_text_aux_structural: 0.12597
- loss_text_aux_lexical: 0.105982
- loss_clause_transition_aux: 0.04953
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.012618
- z_art_abs_mean: 0.27342
- z_art_delta_abs_mean: 0.011268
- event_prob_mean: 0.461324
- event_presence_prob_mean: 0.589493
- event_delta_prob_mean: 0.38466
- event_rise_prob_mean: 0.463366
- event_fall_prob_mean: 0.426663
- event_energy_prob_mean: 0.571541
- event_presence_peak_ratio: 0.776774
- acoustic_abs_mean: 0.804981
- acoustic_energy_mean: -3.039327
- acoustic_delta_abs_mean: 0.037813
- text_aux_abs_mean: 0.200179

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.226447
- loss_acoustic: 0.666749
- loss_event: 5.039564
- loss_text_aux: 0.166174
- loss_text_aux_effective: 0.166174
- loss_text_aux_structural: 0.230938
- loss_text_aux_lexical: 0.062553
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.002482
- z_art_abs_mean: 0.180348
- z_art_delta_abs_mean: 0.007731
- event_prob_mean: 0.448949
- event_presence_prob_mean: 0.55814
- event_delta_prob_mean: 0.399054
- event_rise_prob_mean: 0.44392
- event_fall_prob_mean: 0.446284
- event_energy_prob_mean: 0.544355
- event_presence_peak_ratio: 0.927635
- acoustic_abs_mean: 1.080099
- acoustic_energy_mean: -4.164393
- acoustic_delta_abs_mean: 0.015028
- text_aux_abs_mean: 0.247558

## 对比
- delta_loss_total: -0.295714
- delta_loss_acoustic: -0.422831
- delta_loss_event: 0.279462
- delta_loss_text_aux: 0.047892
- delta_loss_text_aux_effective: 0.047892
- delta_loss_text_aux_structural: 0.104968
- delta_loss_text_aux_lexical: -0.043429
- delta_loss_clause_transition_aux: -0.04953
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.010136
- delta_z_art_abs_mean: -0.093072
- delta_z_art_delta_abs_mean: -0.003537
- delta_event_prob_mean: -0.012375
- delta_event_presence_prob_mean: -0.031353
- delta_event_delta_prob_mean: 0.014394
- delta_event_rise_prob_mean: -0.019446
- delta_event_fall_prob_mean: 0.019621
- delta_event_energy_prob_mean: -0.027186
- delta_event_presence_peak_ratio: 0.150861
- delta_acoustic_abs_mean: 0.275118
- delta_acoustic_energy_mean: -1.125066
- delta_acoustic_delta_abs_mean: -0.022785
- delta_text_aux_abs_mean: 0.047379

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
