# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.779425
- loss_acoustic: 7.10658
- loss_event: 5.224648
- loss_text_aux: 0.229654
- loss_text_aux_effective: 0.229654
- loss_text_aux_structural: 0.229476
- loss_text_aux_lexical: 0.229937
- loss_clause_transition_aux: 0.038729
- z_art_abs_mean: 0.227955
- z_art_delta_abs_mean: 0.001293
- event_prob_mean: 0.478518
- event_presence_prob_mean: 0.556573
- event_delta_prob_mean: 0.503714
- event_rise_prob_mean: 0.462089
- event_fall_prob_mean: 0.491354
- event_energy_prob_mean: 0.522778
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.185881
- acoustic_energy_mean: -4.579262
- acoustic_delta_abs_mean: 0.035522
- text_aux_abs_mean: 0.470952

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.843176
- loss_acoustic: 3.1195
- loss_event: 5.279771
- loss_text_aux: 0.416943
- loss_text_aux_effective: 0.416943
- loss_text_aux_structural: 0.495565
- loss_text_aux_lexical: 0.291148
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.238153
- z_art_delta_abs_mean: 0.000502
- event_prob_mean: 0.476324
- event_presence_prob_mean: 0.554161
- event_delta_prob_mean: 0.508877
- event_rise_prob_mean: 0.456588
- event_fall_prob_mean: 0.49572
- event_energy_prob_mean: 0.517675
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.198639
- acoustic_energy_mean: -4.642608
- acoustic_delta_abs_mean: 0.028734
- text_aux_abs_mean: 0.476769

## 对比
- delta_loss_total: -3.936249
- delta_loss_acoustic: -3.98708
- delta_loss_event: 0.055123
- delta_loss_text_aux: 0.187289
- delta_loss_text_aux_effective: 0.187289
- delta_loss_text_aux_structural: 0.266089
- delta_loss_text_aux_lexical: 0.061211
- delta_loss_clause_transition_aux: -0.038729
- delta_z_art_abs_mean: 0.010198
- delta_z_art_delta_abs_mean: -0.000791
- delta_event_prob_mean: -0.002194
- delta_event_presence_prob_mean: -0.002412
- delta_event_delta_prob_mean: 0.005163
- delta_event_rise_prob_mean: -0.005501
- delta_event_fall_prob_mean: 0.004366
- delta_event_energy_prob_mean: -0.005103
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.012758
- delta_acoustic_energy_mean: -0.063346
- delta_acoustic_delta_abs_mean: -0.006788
- delta_text_aux_abs_mean: 0.005817

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
