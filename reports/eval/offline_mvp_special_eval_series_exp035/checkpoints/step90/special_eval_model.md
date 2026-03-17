# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.522096
- loss_acoustic: 1.088776
- loss_event: 4.763557
- loss_text_aux: 0.122919
- loss_text_aux_effective: 0.12632
- loss_clause_transition_aux: 0.049486
- z_art_abs_mean: 0.272647
- z_art_delta_abs_mean: 0.011196
- event_prob_mean: 0.461257
- event_presence_prob_mean: 0.58785
- event_delta_prob_mean: 0.384704
- event_rise_prob_mean: 0.464807
- event_fall_prob_mean: 0.427415
- event_energy_prob_mean: 0.569339
- event_presence_peak_ratio: 0.770264
- acoustic_abs_mean: 0.807355
- acoustic_energy_mean: -3.040619
- acoustic_delta_abs_mean: 0.035054
- text_aux_abs_mean: 0.215698

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.241796
- loss_acoustic: 0.669479
- loss_event: 5.041525
- loss_text_aux: 0.213017
- loss_text_aux_effective: 0.227031
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.180109
- z_art_delta_abs_mean: 0.007685
- event_prob_mean: 0.448837
- event_presence_prob_mean: 0.556603
- event_delta_prob_mean: 0.399132
- event_rise_prob_mean: 0.44486
- event_fall_prob_mean: 0.446767
- event_energy_prob_mean: 0.542496
- event_presence_peak_ratio: 0.92344
- acoustic_abs_mean: 1.082876
- acoustic_energy_mean: -4.168164
- acoustic_delta_abs_mean: 0.016135
- text_aux_abs_mean: 0.270986

## 对比
- delta_loss_total: -0.2803
- delta_loss_acoustic: -0.419297
- delta_loss_event: 0.277968
- delta_loss_text_aux: 0.090098
- delta_loss_text_aux_effective: 0.100711
- delta_loss_clause_transition_aux: -0.049486
- delta_z_art_abs_mean: -0.092538
- delta_z_art_delta_abs_mean: -0.003511
- delta_event_prob_mean: -0.01242
- delta_event_presence_prob_mean: -0.031247
- delta_event_delta_prob_mean: 0.014428
- delta_event_rise_prob_mean: -0.019947
- delta_event_fall_prob_mean: 0.019352
- delta_event_energy_prob_mean: -0.026843
- delta_event_presence_peak_ratio: 0.153176
- delta_acoustic_abs_mean: 0.275521
- delta_acoustic_energy_mean: -1.127545
- delta_acoustic_delta_abs_mean: -0.018919
- delta_text_aux_abs_mean: 0.055288

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
