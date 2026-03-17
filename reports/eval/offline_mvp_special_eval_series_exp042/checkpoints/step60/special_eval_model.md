# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.276855
- loss_acoustic: 5.677456
- loss_event: 5.10073
- loss_text_aux: 0.143403
- loss_text_aux_effective: 0.143403
- loss_text_aux_structural: 0.155293
- loss_text_aux_lexical: 0.124378
- loss_clause_transition_aux: 0.043118
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.020113
- z_art_abs_mean: 0.178293
- z_art_delta_abs_mean: 0.001549
- event_prob_mean: 0.475321
- event_presence_prob_mean: 0.57723
- event_delta_prob_mean: 0.449592
- event_rise_prob_mean: 0.483394
- event_fall_prob_mean: 0.458247
- event_energy_prob_mean: 0.552377
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.080662
- acoustic_energy_mean: -4.184428
- acoustic_delta_abs_mean: 0.018875
- text_aux_abs_mean: 0.318877

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.054871
- loss_acoustic: 2.400821
- loss_event: 5.198375
- loss_text_aux: 0.270292
- loss_text_aux_effective: 0.270292
- loss_text_aux_structural: 0.354519
- loss_text_aux_lexical: 0.135527
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.000599
- z_art_abs_mean: 0.181956
- z_art_delta_abs_mean: 0.000855
- event_prob_mean: 0.471339
- event_presence_prob_mean: 0.571753
- event_delta_prob_mean: 0.453082
- event_rise_prob_mean: 0.47579
- event_fall_prob_mean: 0.462427
- event_energy_prob_mean: 0.54632
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.113101
- acoustic_energy_mean: -4.335008
- acoustic_delta_abs_mean: 0.007268
- text_aux_abs_mean: 0.329869

## 对比
- delta_loss_total: -3.221984
- delta_loss_acoustic: -3.276635
- delta_loss_event: 0.097645
- delta_loss_text_aux: 0.126889
- delta_loss_text_aux_effective: 0.126889
- delta_loss_text_aux_structural: 0.199226
- delta_loss_text_aux_lexical: 0.011149
- delta_loss_clause_transition_aux: -0.043118
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.019514
- delta_z_art_abs_mean: 0.003663
- delta_z_art_delta_abs_mean: -0.000694
- delta_event_prob_mean: -0.003982
- delta_event_presence_prob_mean: -0.005477
- delta_event_delta_prob_mean: 0.00349
- delta_event_rise_prob_mean: -0.007604
- delta_event_fall_prob_mean: 0.00418
- delta_event_energy_prob_mean: -0.006057
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.032439
- delta_acoustic_energy_mean: -0.15058
- delta_acoustic_delta_abs_mean: -0.011607
- delta_text_aux_abs_mean: 0.010992

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
