# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.669992
- loss_acoustic: 0.304018
- loss_event: 4.635342
- loss_text_aux: 0.11568
- loss_clause_transition_aux: 0.051619
- z_art_abs_mean: 0.28382
- z_art_delta_abs_mean: 0.008876
- event_prob_mean: 0.441612
- event_presence_prob_mean: 0.598073
- event_delta_prob_mean: 0.318857
- event_rise_prob_mean: 0.476553
- event_fall_prob_mean: 0.527601
- event_energy_prob_mean: 0.590649
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.886769
- acoustic_energy_mean: -3.424555
- acoustic_delta_abs_mean: 0.008099
- text_aux_abs_mean: 0.259947

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.775367
- loss_acoustic: 0.267044
- loss_event: 4.905879
- loss_text_aux: 0.2466
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.232921
- z_art_delta_abs_mean: 0.00758
- event_prob_mean: 0.433267
- event_presence_prob_mean: 0.57954
- event_delta_prob_mean: 0.32512
- event_rise_prob_mean: 0.473549
- event_fall_prob_mean: 0.516186
- event_energy_prob_mean: 0.572856
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.040981
- acoustic_energy_mean: -4.008404
- acoustic_delta_abs_mean: 0.004608
- text_aux_abs_mean: 0.287264

## 对比
- delta_loss_total: 0.105375
- delta_loss_acoustic: -0.036974
- delta_loss_event: 0.270537
- delta_loss_text_aux: 0.13092
- delta_loss_clause_transition_aux: -0.051619
- delta_z_art_abs_mean: -0.050899
- delta_z_art_delta_abs_mean: -0.001296
- delta_event_prob_mean: -0.008345
- delta_event_presence_prob_mean: -0.018533
- delta_event_delta_prob_mean: 0.006263
- delta_event_rise_prob_mean: -0.003004
- delta_event_fall_prob_mean: -0.011415
- delta_event_energy_prob_mean: -0.017793
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.154212
- delta_acoustic_energy_mean: -0.583849
- delta_acoustic_delta_abs_mean: -0.003491
- delta_text_aux_abs_mean: 0.027317

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
