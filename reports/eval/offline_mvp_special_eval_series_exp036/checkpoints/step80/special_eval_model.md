# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 4.260131
- loss_acoustic: 1.770682
- loss_event: 4.890245
- loss_text_aux: 0.11079
- loss_text_aux_effective: 0.112109
- loss_clause_transition_aux: 0.046874
- z_art_abs_mean: 0.20008
- z_art_delta_abs_mean: 0.006873
- event_prob_mean: 0.464648
- event_presence_prob_mean: 0.575955
- event_delta_prob_mean: 0.405954
- event_rise_prob_mean: 0.473738
- event_fall_prob_mean: 0.441874
- event_energy_prob_mean: 0.559184
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.896809
- acoustic_energy_mean: -3.429815
- acoustic_delta_abs_mean: 0.009642
- text_aux_abs_mean: 0.229609

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.731759
- loss_acoustic: 1.136841
- loss_event: 5.094331
- loss_text_aux: 0.220442
- loss_text_aux_effective: 0.220723
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.154245
- z_art_delta_abs_mean: 0.004509
- event_prob_mean: 0.45529
- event_presence_prob_mean: 0.554414
- event_delta_prob_mean: 0.416088
- event_rise_prob_mean: 0.457704
- event_fall_prob_mean: 0.4568
- event_energy_prob_mean: 0.541009
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.085724
- acoustic_energy_mean: -4.212359
- acoustic_delta_abs_mean: 0.007321
- text_aux_abs_mean: 0.278549

## 对比
- delta_loss_total: -0.528372
- delta_loss_acoustic: -0.633841
- delta_loss_event: 0.204086
- delta_loss_text_aux: 0.109652
- delta_loss_text_aux_effective: 0.108614
- delta_loss_clause_transition_aux: -0.046874
- delta_z_art_abs_mean: -0.045835
- delta_z_art_delta_abs_mean: -0.002364
- delta_event_prob_mean: -0.009358
- delta_event_presence_prob_mean: -0.021541
- delta_event_delta_prob_mean: 0.010134
- delta_event_rise_prob_mean: -0.016034
- delta_event_fall_prob_mean: 0.014926
- delta_event_energy_prob_mean: -0.018175
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.188915
- delta_acoustic_energy_mean: -0.782544
- delta_acoustic_delta_abs_mean: -0.002321
- delta_text_aux_abs_mean: 0.04894

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
