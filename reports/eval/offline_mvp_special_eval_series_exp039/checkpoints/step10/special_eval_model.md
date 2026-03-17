# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.339987
- loss_acoustic: 16.564729
- loss_event: 5.449138
- loss_text_aux: 0.18638
- loss_text_aux_effective: 0.18638
- loss_text_aux_structural: 0.196403
- loss_text_aux_lexical: 0.170343
- loss_clause_transition_aux: 0.036983
- z_art_abs_mean: 0.085826
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508175
- event_presence_prob_mean: 0.521855
- event_delta_prob_mean: 0.527283
- event_rise_prob_mean: 0.528788
- event_fall_prob_mean: 0.522669
- event_energy_prob_mean: 0.520498
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198321
- acoustic_energy_mean: -0.487496
- acoustic_delta_abs_mean: 0.13859
- text_aux_abs_mean: 0.087779

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.627099
- loss_acoustic: 12.86811
- loss_event: 5.473265
- loss_text_aux: 0.110453
- loss_text_aux_effective: 0.110453
- loss_text_aux_structural: 0.174275
- loss_text_aux_lexical: 0.008338
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.084976
- z_art_delta_abs_mean: 0.000333
- event_prob_mean: 0.50782
- event_presence_prob_mean: 0.521
- event_delta_prob_mean: 0.528979
- event_rise_prob_mean: 0.529663
- event_fall_prob_mean: 0.525052
- event_energy_prob_mean: 0.518194
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.19882
- acoustic_energy_mean: -0.489667
- acoustic_delta_abs_mean: 0.138058
- text_aux_abs_mean: 0.087946

## 对比
- delta_loss_total: -3.712888
- delta_loss_acoustic: -3.696619
- delta_loss_event: 0.024127
- delta_loss_text_aux: -0.075927
- delta_loss_text_aux_effective: -0.075927
- delta_loss_text_aux_structural: -0.022128
- delta_loss_text_aux_lexical: -0.162005
- delta_loss_clause_transition_aux: -0.036983
- delta_z_art_abs_mean: -0.00085
- delta_z_art_delta_abs_mean: -0.000254
- delta_event_prob_mean: -0.000355
- delta_event_presence_prob_mean: -0.000855
- delta_event_delta_prob_mean: 0.001696
- delta_event_rise_prob_mean: 0.000875
- delta_event_fall_prob_mean: 0.002383
- delta_event_energy_prob_mean: -0.002304
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000499
- delta_acoustic_energy_mean: -0.002171
- delta_acoustic_delta_abs_mean: -0.000532
- delta_text_aux_abs_mean: 0.000167

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
