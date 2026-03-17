# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.345066
- loss_acoustic: 16.564781
- loss_event: 5.448877
- loss_text_aux: 0.186376
- loss_text_aux_effective: 0.186376
- loss_text_aux_structural: 0.196398
- loss_text_aux_lexical: 0.170341
- loss_clause_transition_aux: 0.036976
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.025808
- z_art_abs_mean: 0.085873
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508235
- event_presence_prob_mean: 0.52217
- event_delta_prob_mean: 0.527278
- event_rise_prob_mean: 0.528812
- event_fall_prob_mean: 0.522634
- event_energy_prob_mean: 0.520652
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198328
- acoustic_energy_mean: -0.48749
- acoustic_delta_abs_mean: 0.138625
- text_aux_abs_mean: 0.087782

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.627448
- loss_acoustic: 12.868167
- loss_event: 5.473091
- loss_text_aux: 0.110461
- loss_text_aux_effective: 0.110461
- loss_text_aux_structural: 0.174287
- loss_text_aux_lexical: 0.008339
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.001888
- z_art_abs_mean: 0.085019
- z_art_delta_abs_mean: 0.000333
- event_prob_mean: 0.507878
- event_presence_prob_mean: 0.521316
- event_delta_prob_mean: 0.528972
- event_rise_prob_mean: 0.529685
- event_fall_prob_mean: 0.525018
- event_energy_prob_mean: 0.518343
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198825
- acoustic_energy_mean: -0.48966
- acoustic_delta_abs_mean: 0.138094
- text_aux_abs_mean: 0.08795

## 对比
- delta_loss_total: -3.717618
- delta_loss_acoustic: -3.696614
- delta_loss_event: 0.024214
- delta_loss_text_aux: -0.075915
- delta_loss_text_aux_effective: -0.075915
- delta_loss_text_aux_structural: -0.022111
- delta_loss_text_aux_lexical: -0.162002
- delta_loss_clause_transition_aux: -0.036976
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: -0.02392
- delta_z_art_abs_mean: -0.000854
- delta_z_art_delta_abs_mean: -0.000254
- delta_event_prob_mean: -0.000357
- delta_event_presence_prob_mean: -0.000854
- delta_event_delta_prob_mean: 0.001694
- delta_event_rise_prob_mean: 0.000873
- delta_event_fall_prob_mean: 0.002384
- delta_event_energy_prob_mean: -0.002309
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000497
- delta_acoustic_energy_mean: -0.00217
- delta_acoustic_delta_abs_mean: -0.000531
- delta_text_aux_abs_mean: 0.000168

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
