# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.323704
- loss_acoustic: 6.585286
- loss_event: 5.332431
- loss_text_aux: 0.230725
- loss_text_aux_effective: 0.230725
- loss_text_aux_structural: 0.231898
- loss_text_aux_lexical: 0.228848
- loss_clause_transition_aux: 0.036013
- loss_boundary_contrast_aux: 0.050434
- z_art_abs_mean: 0.222004
- z_art_delta_abs_mean: 0.001056
- event_prob_mean: 0.490984
- event_presence_prob_mean: 0.552313
- event_delta_prob_mean: 0.534582
- event_rise_prob_mean: 0.469427
- event_fall_prob_mean: 0.520573
- event_energy_prob_mean: 0.510447
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878176
- acoustic_energy_mean: -3.376854
- acoustic_delta_abs_mean: 0.068321
- text_aux_abs_mean: 0.435252

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.212757
- loss_acoustic: 2.456588
- loss_event: 5.36727
- loss_text_aux: 0.361307
- loss_text_aux_effective: 0.361307
- loss_text_aux_structural: 0.417279
- loss_text_aux_lexical: 0.27175
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- z_art_abs_mean: 0.229785
- z_art_delta_abs_mean: 0.000341
- event_prob_mean: 0.489849
- event_presence_prob_mean: 0.551496
- event_delta_prob_mean: 0.539174
- event_rise_prob_mean: 0.465736
- event_fall_prob_mean: 0.52527
- event_energy_prob_mean: 0.50618
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884695
- acoustic_energy_mean: -3.400746
- acoustic_delta_abs_mean: 0.073124
- text_aux_abs_mean: 0.438223

## 对比
- delta_loss_total: -4.110947
- delta_loss_acoustic: -4.128698
- delta_loss_event: 0.034839
- delta_loss_text_aux: 0.130582
- delta_loss_text_aux_effective: 0.130582
- delta_loss_text_aux_structural: 0.185381
- delta_loss_text_aux_lexical: 0.042902
- delta_loss_clause_transition_aux: -0.036013
- delta_loss_boundary_contrast_aux: -0.050434
- delta_z_art_abs_mean: 0.007781
- delta_z_art_delta_abs_mean: -0.000715
- delta_event_prob_mean: -0.001135
- delta_event_presence_prob_mean: -0.000817
- delta_event_delta_prob_mean: 0.004592
- delta_event_rise_prob_mean: -0.003691
- delta_event_fall_prob_mean: 0.004697
- delta_event_energy_prob_mean: -0.004267
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006519
- delta_acoustic_energy_mean: -0.023892
- delta_acoustic_delta_abs_mean: 0.004803
- delta_text_aux_abs_mean: 0.002971

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
