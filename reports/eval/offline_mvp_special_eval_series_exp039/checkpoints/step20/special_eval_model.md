# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.582369
- loss_acoustic: 12.828376
- loss_event: 5.414243
- loss_text_aux: 0.168298
- loss_text_aux_effective: 0.168298
- loss_text_aux_structural: 0.173028
- loss_text_aux_lexical: 0.160731
- loss_clause_transition_aux: 0.03629
- z_art_abs_mean: 0.115689
- z_art_delta_abs_mean: 0.000639
- event_prob_mean: 0.506308
- event_presence_prob_mean: 0.537166
- event_delta_prob_mean: 0.528449
- event_rise_prob_mean: 0.51357
- event_fall_prob_mean: 0.528851
- event_energy_prob_mean: 0.519537
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373108
- acoustic_energy_mean: -1.14606
- acoustic_delta_abs_mean: 0.152998
- text_aux_abs_mean: 0.182647

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.768332
- loss_acoustic: 9.016935
- loss_event: 5.445479
- loss_text_aux: 0.14204
- loss_text_aux_effective: 0.14204
- loss_text_aux_structural: 0.205646
- loss_text_aux_lexical: 0.040271
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.118224
- z_art_delta_abs_mean: 0.000312
- event_prob_mean: 0.505787
- event_presence_prob_mean: 0.536349
- event_delta_prob_mean: 0.530556
- event_rise_prob_mean: 0.513188
- event_fall_prob_mean: 0.53241
- event_energy_prob_mean: 0.516692
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375207
- acoustic_energy_mean: -1.153809
- acoustic_delta_abs_mean: 0.152296
- text_aux_abs_mean: 0.183869

## 对比
- delta_loss_total: -3.814037
- delta_loss_acoustic: -3.811441
- delta_loss_event: 0.031236
- delta_loss_text_aux: -0.026258
- delta_loss_text_aux_effective: -0.026258
- delta_loss_text_aux_structural: 0.032618
- delta_loss_text_aux_lexical: -0.12046
- delta_loss_clause_transition_aux: -0.03629
- delta_z_art_abs_mean: 0.002535
- delta_z_art_delta_abs_mean: -0.000327
- delta_event_prob_mean: -0.000521
- delta_event_presence_prob_mean: -0.000817
- delta_event_delta_prob_mean: 0.002107
- delta_event_rise_prob_mean: -0.000382
- delta_event_fall_prob_mean: 0.003559
- delta_event_energy_prob_mean: -0.002845
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002099
- delta_acoustic_energy_mean: -0.007749
- delta_acoustic_delta_abs_mean: -0.000702
- delta_text_aux_abs_mean: 0.001222

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
