# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.785127
- loss_acoustic: 7.111553
- loss_event: 5.224886
- loss_text_aux: 0.232718
- loss_text_aux_effective: 0.232718
- loss_text_aux_structural: 0.234735
- loss_text_aux_lexical: 0.229491
- loss_clause_transition_aux: 0.038727
- z_art_abs_mean: 0.22861
- z_art_delta_abs_mean: 0.001292
- event_prob_mean: 0.478547
- event_presence_prob_mean: 0.556731
- event_delta_prob_mean: 0.50381
- event_rise_prob_mean: 0.46219
- event_fall_prob_mean: 0.491213
- event_energy_prob_mean: 0.522643
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.185831
- acoustic_energy_mean: -4.581856
- acoustic_delta_abs_mean: 0.034674
- text_aux_abs_mean: 0.47348

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.848873
- loss_acoustic: 3.124171
- loss_event: 5.28009
- loss_text_aux: 0.421281
- loss_text_aux_effective: 0.421281
- loss_text_aux_structural: 0.502658
- loss_text_aux_lexical: 0.291077
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.238795
- z_art_delta_abs_mean: 0.000501
- event_prob_mean: 0.476352
- event_presence_prob_mean: 0.554313
- event_delta_prob_mean: 0.508981
- event_rise_prob_mean: 0.456664
- event_fall_prob_mean: 0.49561
- event_energy_prob_mean: 0.517545
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.198579
- acoustic_energy_mean: -4.645205
- acoustic_delta_abs_mean: 0.027872
- text_aux_abs_mean: 0.479334

## 对比
- delta_loss_total: -3.936254
- delta_loss_acoustic: -3.987382
- delta_loss_event: 0.055204
- delta_loss_text_aux: 0.188563
- delta_loss_text_aux_effective: 0.188563
- delta_loss_text_aux_structural: 0.267923
- delta_loss_text_aux_lexical: 0.061586
- delta_loss_clause_transition_aux: -0.038727
- delta_z_art_abs_mean: 0.010185
- delta_z_art_delta_abs_mean: -0.000791
- delta_event_prob_mean: -0.002195
- delta_event_presence_prob_mean: -0.002418
- delta_event_delta_prob_mean: 0.005171
- delta_event_rise_prob_mean: -0.005526
- delta_event_fall_prob_mean: 0.004397
- delta_event_energy_prob_mean: -0.005098
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.012748
- delta_acoustic_energy_mean: -0.063349
- delta_acoustic_delta_abs_mean: -0.006802
- delta_text_aux_abs_mean: 0.005854

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
