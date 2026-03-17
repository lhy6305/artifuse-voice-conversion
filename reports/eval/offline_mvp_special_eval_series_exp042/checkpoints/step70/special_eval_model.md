# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 6.398609
- loss_acoustic: 3.859036
- loss_event: 4.988426
- loss_text_aux: 0.114084
- loss_text_aux_effective: 0.114084
- loss_text_aux_structural: 0.125038
- loss_text_aux_lexical: 0.096559
- loss_clause_transition_aux: 0.04627
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.018864
- z_art_abs_mean: 0.18196
- z_art_delta_abs_mean: 0.00322
- event_prob_mean: 0.47205
- event_presence_prob_mean: 0.588411
- event_delta_prob_mean: 0.413221
- event_rise_prob_mean: 0.489628
- event_fall_prob_mean: 0.4399
- event_energy_prob_mean: 0.569005
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.8712
- acoustic_energy_mean: -3.353999
- acoustic_delta_abs_mean: 0.022156
- text_aux_abs_mean: 0.218941

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.159521
- loss_acoustic: 1.550657
- loss_event: 5.14189
- loss_text_aux: 0.180235
- loss_text_aux_effective: 0.180235
- loss_text_aux_structural: 0.253841
- loss_text_aux_lexical: 0.062466
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.000586
- z_art_abs_mean: 0.162884
- z_art_delta_abs_mean: 0.002192
- event_prob_mean: 0.465681
- event_presence_prob_mean: 0.57643
- event_delta_prob_mean: 0.417966
- event_rise_prob_mean: 0.478242
- event_fall_prob_mean: 0.447639
- event_energy_prob_mean: 0.558862
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.952282
- acoustic_energy_mean: -3.694683
- acoustic_delta_abs_mean: 0.028641
- text_aux_abs_mean: 0.23797

## 对比
- delta_loss_total: -2.239088
- delta_loss_acoustic: -2.308379
- delta_loss_event: 0.153464
- delta_loss_text_aux: 0.066151
- delta_loss_text_aux_effective: 0.066151
- delta_loss_text_aux_structural: 0.128803
- delta_loss_text_aux_lexical: -0.034093
- delta_loss_clause_transition_aux: -0.04627
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.018278
- delta_z_art_abs_mean: -0.019076
- delta_z_art_delta_abs_mean: -0.001028
- delta_event_prob_mean: -0.006369
- delta_event_presence_prob_mean: -0.011981
- delta_event_delta_prob_mean: 0.004745
- delta_event_rise_prob_mean: -0.011386
- delta_event_fall_prob_mean: 0.007739
- delta_event_energy_prob_mean: -0.010143
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.081082
- delta_acoustic_energy_mean: -0.340684
- delta_acoustic_delta_abs_mean: 0.006485
- delta_text_aux_abs_mean: 0.019029

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
