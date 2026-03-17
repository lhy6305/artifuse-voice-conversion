# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.295936
- loss_acoustic: 1.794197
- loss_event: 4.889707
- loss_text_aux: 0.112069
- loss_text_aux_effective: 0.112069
- loss_text_aux_structural: 0.122603
- loss_text_aux_lexical: 0.095215
- loss_clause_transition_aux: 0.046877
- loss_boundary_contrast_aux: 0.050434
- z_art_abs_mean: 0.198477
- z_art_delta_abs_mean: 0.006819
- event_prob_mean: 0.464406
- event_presence_prob_mean: 0.57553
- event_delta_prob_mean: 0.406046
- event_rise_prob_mean: 0.472782
- event_fall_prob_mean: 0.441877
- event_energy_prob_mean: 0.559785
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.89892
- acoustic_energy_mean: -3.439397
- acoustic_delta_abs_mean: 0.010238
- text_aux_abs_mean: 0.212102

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.731968
- loss_acoustic: 1.147166
- loss_event: 5.09383
- loss_text_aux: 0.17154
- loss_text_aux_effective: 0.17154
- loss_text_aux_structural: 0.239722
- loss_text_aux_lexical: 0.062449
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- z_art_abs_mean: 0.153052
- z_art_delta_abs_mean: 0.004474
- event_prob_mean: 0.455114
- event_presence_prob_mean: 0.554114
- event_delta_prob_mean: 0.4161
- event_rise_prob_mean: 0.457079
- event_fall_prob_mean: 0.456748
- event_energy_prob_mean: 0.541522
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.086607
- acoustic_energy_mean: -4.213293
- acoustic_delta_abs_mean: 0.008673
- text_aux_abs_mean: 0.251169

## 对比
- delta_loss_total: -0.563968
- delta_loss_acoustic: -0.647031
- delta_loss_event: 0.204123
- delta_loss_text_aux: 0.059471
- delta_loss_text_aux_effective: 0.059471
- delta_loss_text_aux_structural: 0.117119
- delta_loss_text_aux_lexical: -0.032766
- delta_loss_clause_transition_aux: -0.046877
- delta_loss_boundary_contrast_aux: -0.050434
- delta_z_art_abs_mean: -0.045425
- delta_z_art_delta_abs_mean: -0.002345
- delta_event_prob_mean: -0.009292
- delta_event_presence_prob_mean: -0.021416
- delta_event_delta_prob_mean: 0.010054
- delta_event_rise_prob_mean: -0.015703
- delta_event_fall_prob_mean: 0.014871
- delta_event_energy_prob_mean: -0.018263
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.187687
- delta_acoustic_energy_mean: -0.773896
- delta_acoustic_delta_abs_mean: -0.001565
- delta_text_aux_abs_mean: 0.039067

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
