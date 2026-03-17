# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.311314
- loss_acoustic: 6.585296
- loss_event: 5.332565
- loss_text_aux: 0.231439
- loss_text_aux_effective: 0.231439
- loss_text_aux_structural: 0.232991
- loss_text_aux_lexical: 0.228958
- loss_clause_transition_aux: 0.036012
- z_art_abs_mean: 0.222239
- z_art_delta_abs_mean: 0.001054
- event_prob_mean: 0.491007
- event_presence_prob_mean: 0.552378
- event_delta_prob_mean: 0.534598
- event_rise_prob_mean: 0.46952
- event_fall_prob_mean: 0.520538
- event_energy_prob_mean: 0.510371
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878327
- acoustic_energy_mean: -3.376964
- acoustic_delta_abs_mean: 0.068617
- text_aux_abs_mean: 0.435582

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.213014
- loss_acoustic: 2.45657
- loss_event: 5.367433
- loss_text_aux: 0.362279
- loss_text_aux_effective: 0.362279
- loss_text_aux_structural: 0.418801
- loss_text_aux_lexical: 0.271844
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.230005
- z_art_delta_abs_mean: 0.000341
- event_prob_mean: 0.489872
- event_presence_prob_mean: 0.551556
- event_delta_prob_mean: 0.539195
- event_rise_prob_mean: 0.465817
- event_fall_prob_mean: 0.525255
- event_energy_prob_mean: 0.506107
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884856
- acoustic_energy_mean: -3.400861
- acoustic_delta_abs_mean: 0.073428
- text_aux_abs_mean: 0.438555

## 对比
- delta_loss_total: -4.0983
- delta_loss_acoustic: -4.128726
- delta_loss_event: 0.034868
- delta_loss_text_aux: 0.13084
- delta_loss_text_aux_effective: 0.13084
- delta_loss_text_aux_structural: 0.18581
- delta_loss_text_aux_lexical: 0.042886
- delta_loss_clause_transition_aux: -0.036012
- delta_z_art_abs_mean: 0.007766
- delta_z_art_delta_abs_mean: -0.000713
- delta_event_prob_mean: -0.001135
- delta_event_presence_prob_mean: -0.000822
- delta_event_delta_prob_mean: 0.004597
- delta_event_rise_prob_mean: -0.003703
- delta_event_fall_prob_mean: 0.004717
- delta_event_energy_prob_mean: -0.004264
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006529
- delta_acoustic_energy_mean: -0.023897
- delta_acoustic_delta_abs_mean: 0.004811
- delta_text_aux_abs_mean: 0.002973

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
