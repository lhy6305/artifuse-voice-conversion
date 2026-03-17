# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.78218
- loss_acoustic: 7.105336
- loss_event: 5.223496
- loss_text_aux: 0.229617
- loss_text_aux_effective: 0.229617
- loss_text_aux_structural: 0.229474
- loss_text_aux_lexical: 0.229847
- loss_clause_transition_aux: 0.038704
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.022963
- z_art_abs_mean: 0.22821
- z_art_delta_abs_mean: 0.001292
- event_prob_mean: 0.478788
- event_presence_prob_mean: 0.557895
- event_delta_prob_mean: 0.503695
- event_rise_prob_mean: 0.462086
- event_fall_prob_mean: 0.491304
- event_energy_prob_mean: 0.523701
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.185832
- acoustic_energy_mean: -4.578933
- acoustic_delta_abs_mean: 0.03557
- text_aux_abs_mean: 0.4709

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.842296
- loss_acoustic: 3.118803
- loss_event: 5.278974
- loss_text_aux: 0.416867
- loss_text_aux_effective: 0.416867
- loss_text_aux_structural: 0.495528
- loss_text_aux_lexical: 0.29101
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001155
- z_art_abs_mean: 0.23839
- z_art_delta_abs_mean: 0.000502
- event_prob_mean: 0.476593
- event_presence_prob_mean: 0.555467
- event_delta_prob_mean: 0.508856
- event_rise_prob_mean: 0.456572
- event_fall_prob_mean: 0.495703
- event_energy_prob_mean: 0.518593
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.1986
- acoustic_energy_mean: -4.642333
- acoustic_delta_abs_mean: 0.028763
- text_aux_abs_mean: 0.476721

## 对比
- delta_loss_total: -3.939884
- delta_loss_acoustic: -3.986533
- delta_loss_event: 0.055478
- delta_loss_text_aux: 0.18725
- delta_loss_text_aux_effective: 0.18725
- delta_loss_text_aux_structural: 0.266054
- delta_loss_text_aux_lexical: 0.061163
- delta_loss_clause_transition_aux: -0.038704
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.021808
- delta_z_art_abs_mean: 0.01018
- delta_z_art_delta_abs_mean: -0.00079
- delta_event_prob_mean: -0.002195
- delta_event_presence_prob_mean: -0.002428
- delta_event_delta_prob_mean: 0.005161
- delta_event_rise_prob_mean: -0.005514
- delta_event_fall_prob_mean: 0.004399
- delta_event_energy_prob_mean: -0.005108
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.012768
- delta_acoustic_energy_mean: -0.0634
- delta_acoustic_delta_abs_mean: -0.006807
- delta_text_aux_abs_mean: 0.005821

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
