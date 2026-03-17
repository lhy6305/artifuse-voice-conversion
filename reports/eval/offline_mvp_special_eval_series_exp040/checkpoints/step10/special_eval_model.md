# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.33989
- loss_acoustic: 16.564585
- loss_event: 5.449222
- loss_text_aux: 0.186408
- loss_text_aux_effective: 0.186408
- loss_text_aux_structural: 0.196461
- loss_text_aux_lexical: 0.170321
- loss_clause_transition_aux: 0.036981
- z_art_abs_mean: 0.085833
- z_art_delta_abs_mean: 0.000587
- event_prob_mean: 0.508182
- event_presence_prob_mean: 0.521848
- event_delta_prob_mean: 0.527298
- event_rise_prob_mean: 0.52881
- event_fall_prob_mean: 0.522678
- event_energy_prob_mean: 0.520473
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198329
- acoustic_energy_mean: -0.487528
- acoustic_delta_abs_mean: 0.138826
- text_aux_abs_mean: 0.087799

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.62696
- loss_acoustic: 12.867918
- loss_event: 5.473351
- loss_text_aux: 0.110501
- loss_text_aux_effective: 0.110501
- loss_text_aux_structural: 0.174354
- loss_text_aux_lexical: 0.008336
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.084972
- z_art_delta_abs_mean: 0.000333
- event_prob_mean: 0.507827
- event_presence_prob_mean: 0.52099
- event_delta_prob_mean: 0.528996
- event_rise_prob_mean: 0.52968
- event_fall_prob_mean: 0.525071
- event_energy_prob_mean: 0.518174
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198827
- acoustic_energy_mean: -0.489701
- acoustic_delta_abs_mean: 0.138296
- text_aux_abs_mean: 0.087966

## 对比
- delta_loss_total: -3.71293
- delta_loss_acoustic: -3.696667
- delta_loss_event: 0.024129
- delta_loss_text_aux: -0.075907
- delta_loss_text_aux_effective: -0.075907
- delta_loss_text_aux_structural: -0.022107
- delta_loss_text_aux_lexical: -0.161985
- delta_loss_clause_transition_aux: -0.036981
- delta_z_art_abs_mean: -0.000861
- delta_z_art_delta_abs_mean: -0.000254
- delta_event_prob_mean: -0.000355
- delta_event_presence_prob_mean: -0.000858
- delta_event_delta_prob_mean: 0.001698
- delta_event_rise_prob_mean: 0.00087
- delta_event_fall_prob_mean: 0.002393
- delta_event_energy_prob_mean: -0.002299
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000498
- delta_acoustic_energy_mean: -0.002173
- delta_acoustic_delta_abs_mean: -0.00053
- delta_text_aux_abs_mean: 0.000167

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
