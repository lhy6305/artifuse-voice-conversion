# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.589934
- loss_acoustic: 8.849926
- loss_event: 5.379567
- loss_text_aux: 0.185509
- loss_text_aux_effective: 0.185509
- loss_text_aux_structural: 0.188791
- loss_text_aux_lexical: 0.180258
- loss_clause_transition_aux: 0.03563
- z_art_abs_mean: 0.163901
- z_art_delta_abs_mean: 0.000815
- event_prob_mean: 0.501315
- event_presence_prob_mean: 0.548514
- event_delta_prob_mean: 0.534
- event_rise_prob_mean: 0.492377
- event_fall_prob_mean: 0.532194
- event_energy_prob_mean: 0.515527
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.574612
- acoustic_energy_mean: -2.122333
- acoustic_delta_abs_mean: 0.071223
- text_aux_abs_mean: 0.314677

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.637006
- loss_acoustic: 4.882453
- loss_event: 5.412922
- loss_text_aux: 0.239273
- loss_text_aux_effective: 0.239273
- loss_text_aux_structural: 0.300231
- loss_text_aux_lexical: 0.14174
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.16776
- z_art_delta_abs_mean: 0.000297
- event_prob_mean: 0.500595
- event_presence_prob_mean: 0.547909
- event_delta_prob_mean: 0.537104
- event_rise_prob_mean: 0.490398
- event_fall_prob_mean: 0.53664
- event_energy_prob_mean: 0.512093
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.577855
- acoustic_energy_mean: -2.137544
- acoustic_delta_abs_mean: 0.068788
- text_aux_abs_mean: 0.316916

## 对比
- delta_loss_total: -3.952928
- delta_loss_acoustic: -3.967473
- delta_loss_event: 0.033355
- delta_loss_text_aux: 0.053764
- delta_loss_text_aux_effective: 0.053764
- delta_loss_text_aux_structural: 0.11144
- delta_loss_text_aux_lexical: -0.038518
- delta_loss_clause_transition_aux: -0.03563
- delta_z_art_abs_mean: 0.003859
- delta_z_art_delta_abs_mean: -0.000518
- delta_event_prob_mean: -0.00072
- delta_event_presence_prob_mean: -0.000605
- delta_event_delta_prob_mean: 0.003104
- delta_event_rise_prob_mean: -0.001979
- delta_event_fall_prob_mean: 0.004446
- delta_event_energy_prob_mean: -0.003434
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.003243
- delta_acoustic_energy_mean: -0.015211
- delta_acoustic_delta_abs_mean: -0.002435
- delta_text_aux_abs_mean: 0.002239

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
