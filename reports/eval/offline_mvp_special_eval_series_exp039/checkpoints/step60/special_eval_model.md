# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.275516
- loss_acoustic: 5.679353
- loss_event: 5.102298
- loss_text_aux: 0.143414
- loss_text_aux_effective: 0.143413
- loss_text_aux_structural: 0.155284
- loss_text_aux_lexical: 0.124421
- loss_clause_transition_aux: 0.043125
- z_art_abs_mean: 0.177369
- z_art_delta_abs_mean: 0.001547
- event_prob_mean: 0.475003
- event_presence_prob_mean: 0.575346
- event_delta_prob_mean: 0.449638
- event_rise_prob_mean: 0.483449
- event_fall_prob_mean: 0.458602
- event_energy_prob_mean: 0.550965
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.080835
- acoustic_energy_mean: -4.18506
- acoustic_delta_abs_mean: 0.018818
- text_aux_abs_mean: 0.318959

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.056516
- loss_acoustic: 2.402036
- loss_event: 5.199451
- loss_text_aux: 0.270363
- loss_text_aux_effective: 0.270363
- loss_text_aux_structural: 0.354563
- loss_text_aux_lexical: 0.135644
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.181125
- z_art_delta_abs_mean: 0.000852
- event_prob_mean: 0.471019
- event_presence_prob_mean: 0.569896
- event_delta_prob_mean: 0.453124
- event_rise_prob_mean: 0.47586
- event_fall_prob_mean: 0.462731
- event_energy_prob_mean: 0.544906
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.113274
- acoustic_energy_mean: -4.335606
- acoustic_delta_abs_mean: 0.007253
- text_aux_abs_mean: 0.329954

## 对比
- delta_loss_total: -3.219
- delta_loss_acoustic: -3.277317
- delta_loss_event: 0.097153
- delta_loss_text_aux: 0.126949
- delta_loss_text_aux_effective: 0.12695
- delta_loss_text_aux_structural: 0.199279
- delta_loss_text_aux_lexical: 0.011223
- delta_loss_clause_transition_aux: -0.043125
- delta_z_art_abs_mean: 0.003756
- delta_z_art_delta_abs_mean: -0.000695
- delta_event_prob_mean: -0.003984
- delta_event_presence_prob_mean: -0.00545
- delta_event_delta_prob_mean: 0.003486
- delta_event_rise_prob_mean: -0.007589
- delta_event_fall_prob_mean: 0.004129
- delta_event_energy_prob_mean: -0.006059
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.032439
- delta_acoustic_energy_mean: -0.150546
- delta_acoustic_delta_abs_mean: -0.011565
- delta_text_aux_abs_mean: 0.010995

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
