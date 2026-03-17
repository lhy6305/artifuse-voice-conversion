# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.349996
- loss_acoustic: 16.565118
- loss_event: 5.449018
- loss_text_aux: 0.203145
- loss_text_aux_effective: 0.234782
- loss_clause_transition_aux: 0.036979
- z_art_abs_mean: 0.085686
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508181
- event_presence_prob_mean: 0.521824
- event_delta_prob_mean: 0.52727
- event_rise_prob_mean: 0.528731
- event_fall_prob_mean: 0.522789
- event_energy_prob_mean: 0.520567
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198317
- acoustic_energy_mean: -0.487441
- acoustic_delta_abs_mean: 0.138902
- text_aux_abs_mean: 0.117464

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.632459
- loss_acoustic: 12.868478
- loss_event: 5.473164
- loss_text_aux: 0.125198
- loss_text_aux_effective: 0.13566
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.084832
- z_art_delta_abs_mean: 0.000333
- event_prob_mean: 0.507824
- event_presence_prob_mean: 0.520965
- event_delta_prob_mean: 0.528965
- event_rise_prob_mean: 0.529602
- event_fall_prob_mean: 0.525174
- event_energy_prob_mean: 0.51826
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198819
- acoustic_energy_mean: -0.489614
- acoustic_delta_abs_mean: 0.138375
- text_aux_abs_mean: 0.117445

## 对比
- delta_loss_total: -3.717537
- delta_loss_acoustic: -3.69664
- delta_loss_event: 0.024146
- delta_loss_text_aux: -0.077947
- delta_loss_text_aux_effective: -0.099122
- delta_loss_clause_transition_aux: -0.036979
- delta_z_art_abs_mean: -0.000854
- delta_z_art_delta_abs_mean: -0.000254
- delta_event_prob_mean: -0.000357
- delta_event_presence_prob_mean: -0.000859
- delta_event_delta_prob_mean: 0.001695
- delta_event_rise_prob_mean: 0.000871
- delta_event_fall_prob_mean: 0.002385
- delta_event_energy_prob_mean: -0.002307
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000502
- delta_acoustic_energy_mean: -0.002173
- delta_acoustic_delta_abs_mean: -0.000527
- delta_text_aux_abs_mean: -1.9e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
