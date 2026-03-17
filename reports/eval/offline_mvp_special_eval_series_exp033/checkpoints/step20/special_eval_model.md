# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.687762
- loss_acoustic: 12.909272
- loss_event: 5.451337
- loss_text_aux: 0.193388
- loss_clause_transition_aux: 0.039029
- z_art_abs_mean: 0.134164
- z_art_delta_abs_mean: 0.000604
- event_prob_mean: 0.492228
- event_presence_prob_mean: 0.546213
- event_delta_prob_mean: 0.512588
- event_rise_prob_mean: 0.540302
- event_fall_prob_mean: 0.508931
- event_energy_prob_mean: 0.4549
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.40988
- acoustic_energy_mean: -1.14388
- acoustic_delta_abs_mean: 0.08243
- text_aux_abs_mean: 0.17029

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.837738
- loss_acoustic: 9.065186
- loss_event: 5.455678
- loss_text_aux: 0.222543
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.13899
- z_art_delta_abs_mean: 0.000256
- event_prob_mean: 0.491427
- event_presence_prob_mean: 0.54511
- event_delta_prob_mean: 0.51287
- event_rise_prob_mean: 0.541329
- event_fall_prob_mean: 0.507782
- event_energy_prob_mean: 0.45397
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.412039
- acoustic_energy_mean: -1.149405
- acoustic_delta_abs_mean: 0.084443
- text_aux_abs_mean: 0.170612

## 对比
- delta_loss_total: -3.850024
- delta_loss_acoustic: -3.844086
- delta_loss_event: 0.004341
- delta_loss_text_aux: 0.029155
- delta_loss_clause_transition_aux: -0.039029
- delta_z_art_abs_mean: 0.004826
- delta_z_art_delta_abs_mean: -0.000348
- delta_event_prob_mean: -0.000801
- delta_event_presence_prob_mean: -0.001103
- delta_event_delta_prob_mean: 0.000282
- delta_event_rise_prob_mean: 0.001027
- delta_event_fall_prob_mean: -0.001149
- delta_event_energy_prob_mean: -0.00093
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002159
- delta_acoustic_energy_mean: -0.005525
- delta_acoustic_delta_abs_mean: 0.002013
- delta_text_aux_abs_mean: 0.000322

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
