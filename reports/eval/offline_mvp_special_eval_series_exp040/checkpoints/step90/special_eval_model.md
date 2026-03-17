# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.520506
- loss_acoustic: 1.088403
- loss_event: 4.763694
- loss_text_aux: 0.119551
- loss_text_aux_effective: 0.119551
- loss_text_aux_structural: 0.128015
- loss_text_aux_lexical: 0.106007
- loss_clause_transition_aux: 0.049526
- z_art_abs_mean: 0.273158
- z_art_delta_abs_mean: 0.011264
- event_prob_mean: 0.461119
- event_presence_prob_mean: 0.587731
- event_delta_prob_mean: 0.384715
- event_rise_prob_mean: 0.463997
- event_fall_prob_mean: 0.426575
- event_energy_prob_mean: 0.569282
- event_presence_peak_ratio: 0.76898
- acoustic_abs_mean: 0.805017
- acoustic_energy_mean: -3.040464
- acoustic_delta_abs_mean: 0.038226
- text_aux_abs_mean: 0.202726

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.228738
- loss_acoustic: 0.667613
- loss_event: 5.042216
- loss_text_aux: 0.169179
- loss_text_aux_effective: 0.169179
- loss_text_aux_structural: 0.235665
- loss_text_aux_lexical: 0.0628
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.180045
- z_art_delta_abs_mean: 0.007726
- event_prob_mean: 0.448692
- event_presence_prob_mean: 0.556446
- event_delta_prob_mean: 0.399163
- event_rise_prob_mean: 0.444271
- event_fall_prob_mean: 0.446211
- event_energy_prob_mean: 0.54226
- event_presence_peak_ratio: 0.92344
- acoustic_abs_mean: 1.080022
- acoustic_energy_mean: -4.165327
- acoustic_delta_abs_mean: 0.015357
- text_aux_abs_mean: 0.250867

## 对比
- delta_loss_total: -0.291768
- delta_loss_acoustic: -0.42079
- delta_loss_event: 0.278522
- delta_loss_text_aux: 0.049628
- delta_loss_text_aux_effective: 0.049628
- delta_loss_text_aux_structural: 0.10765
- delta_loss_text_aux_lexical: -0.043207
- delta_loss_clause_transition_aux: -0.049526
- delta_z_art_abs_mean: -0.093113
- delta_z_art_delta_abs_mean: -0.003538
- delta_event_prob_mean: -0.012427
- delta_event_presence_prob_mean: -0.031285
- delta_event_delta_prob_mean: 0.014448
- delta_event_rise_prob_mean: -0.019726
- delta_event_fall_prob_mean: 0.019636
- delta_event_energy_prob_mean: -0.027022
- delta_event_presence_peak_ratio: 0.15446
- delta_acoustic_abs_mean: 0.275005
- delta_acoustic_energy_mean: -1.124863
- delta_acoustic_delta_abs_mean: -0.022869
- delta_text_aux_abs_mean: 0.048141

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
