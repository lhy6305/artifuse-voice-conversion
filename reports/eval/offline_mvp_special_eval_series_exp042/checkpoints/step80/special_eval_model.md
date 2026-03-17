# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.282626
- loss_acoustic: 1.790662
- loss_event: 4.887393
- loss_text_aux: 0.1121
- loss_text_aux_effective: 0.1121
- loss_text_aux_structural: 0.122646
- loss_text_aux_lexical: 0.095226
- loss_clause_transition_aux: 0.046879
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.019817
- z_art_abs_mean: 0.199598
- z_art_delta_abs_mean: 0.006845
- event_prob_mean: 0.464729
- event_presence_prob_mean: 0.577459
- event_delta_prob_mean: 0.405917
- event_rise_prob_mean: 0.472704
- event_fall_prob_mean: 0.441611
- event_energy_prob_mean: 0.561304
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.898614
- acoustic_energy_mean: -3.438473
- acoustic_delta_abs_mean: 0.010243
- text_aux_abs_mean: 0.212227

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.729134
- loss_acoustic: 1.144901
- loss_event: 5.092381
- loss_text_aux: 0.171521
- loss_text_aux_effective: 0.171521
- loss_text_aux_structural: 0.239712
- loss_text_aux_lexical: 0.062417
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.000724
- z_art_abs_mean: 0.154078
- z_art_delta_abs_mean: 0.004491
- event_prob_mean: 0.455441
- event_presence_prob_mean: 0.555902
- event_delta_prob_mean: 0.415971
- event_rise_prob_mean: 0.45705
- event_fall_prob_mean: 0.456609
- event_energy_prob_mean: 0.542975
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.086498
- acoustic_energy_mean: -4.212777
- acoustic_delta_abs_mean: 0.00861
- text_aux_abs_mean: 0.251219

## 对比
- delta_loss_total: -0.553492
- delta_loss_acoustic: -0.645761
- delta_loss_event: 0.204988
- delta_loss_text_aux: 0.059421
- delta_loss_text_aux_effective: 0.059421
- delta_loss_text_aux_structural: 0.117066
- delta_loss_text_aux_lexical: -0.032809
- delta_loss_clause_transition_aux: -0.046879
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.019093
- delta_z_art_abs_mean: -0.04552
- delta_z_art_delta_abs_mean: -0.002354
- delta_event_prob_mean: -0.009288
- delta_event_presence_prob_mean: -0.021557
- delta_event_delta_prob_mean: 0.010054
- delta_event_rise_prob_mean: -0.015654
- delta_event_fall_prob_mean: 0.014998
- delta_event_energy_prob_mean: -0.018329
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.187884
- delta_acoustic_energy_mean: -0.774304
- delta_acoustic_delta_abs_mean: -0.001633
- delta_text_aux_abs_mean: 0.038992

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
