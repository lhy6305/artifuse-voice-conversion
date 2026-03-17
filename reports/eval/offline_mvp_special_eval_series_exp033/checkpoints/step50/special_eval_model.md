# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.662671
- loss_acoustic: 7.0372
- loss_event: 5.149077
- loss_text_aux: 0.176273
- loss_clause_transition_aux: 0.041975
- z_art_abs_mean: 0.158945
- z_art_delta_abs_mean: 0.001233
- event_prob_mean: 0.461188
- event_presence_prob_mean: 0.561737
- event_delta_prob_mean: 0.446603
- event_rise_prob_mean: 0.49114
- event_fall_prob_mean: 0.511994
- event_energy_prob_mean: 0.491814
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.17093
- acoustic_energy_mean: -4.458315
- acoustic_delta_abs_mean: 0.038217
- text_aux_abs_mean: 0.345225

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.611953
- loss_acoustic: 2.924376
- loss_event: 5.206854
- loss_text_aux: 0.418432
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.168548
- z_art_delta_abs_mean: 0.00058
- event_prob_mean: 0.458307
- event_presence_prob_mean: 0.55979
- event_delta_prob_mean: 0.445507
- event_rise_prob_mean: 0.490044
- event_fall_prob_mean: 0.509358
- event_energy_prob_mean: 0.490468
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.180838
- acoustic_energy_mean: -4.498533
- acoustic_delta_abs_mean: 0.039979
- text_aux_abs_mean: 0.347472

## 对比
- delta_loss_total: -4.050718
- delta_loss_acoustic: -4.112824
- delta_loss_event: 0.057777
- delta_loss_text_aux: 0.242159
- delta_loss_clause_transition_aux: -0.041975
- delta_z_art_abs_mean: 0.009603
- delta_z_art_delta_abs_mean: -0.000653
- delta_event_prob_mean: -0.002881
- delta_event_presence_prob_mean: -0.001947
- delta_event_delta_prob_mean: -0.001096
- delta_event_rise_prob_mean: -0.001096
- delta_event_fall_prob_mean: -0.002636
- delta_event_energy_prob_mean: -0.001346
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.009908
- delta_acoustic_energy_mean: -0.040218
- delta_acoustic_delta_abs_mean: 0.001762
- delta_text_aux_abs_mean: 0.002247

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
