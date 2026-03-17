# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.603078
- loss_acoustic: 8.85692
- loss_event: 5.376063
- loss_text_aux: 0.225321
- loss_text_aux_effective: 0.225321
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035456
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.16301
- z_art_delta_abs_mean: 0.000816
- event_prob_mean: 0.50277
- event_presence_prob_mean: 0.554282
- event_delta_prob_mean: 0.533722
- event_rise_prob_mean: 0.491628
- event_fall_prob_mean: 0.533113
- event_energy_prob_mean: 0.520312
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.575954
- acoustic_energy_mean: -2.120825
- acoustic_delta_abs_mean: 0.073985
- text_aux_abs_mean: 0.2763

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.639941
- loss_acoustic: 4.889328
- loss_event: 5.410025
- loss_text_aux: 0.226792
- loss_text_aux_effective: 0.226792
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.166844
- z_art_delta_abs_mean: 0.000302
- event_prob_mean: 0.502095
- event_presence_prob_mean: 0.553816
- event_delta_prob_mean: 0.536828
- event_rise_prob_mean: 0.489617
- event_fall_prob_mean: 0.537691
- event_energy_prob_mean: 0.516959
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.579138
- acoustic_energy_mean: -2.135864
- acoustic_delta_abs_mean: 0.071482
- text_aux_abs_mean: 0.278255

## 对比
- delta_loss_total: -3.963137
- delta_loss_acoustic: -3.967592
- delta_loss_event: 0.033962
- delta_loss_text_aux: 0.001471
- delta_loss_text_aux_effective: 0.001471
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035456
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.003834
- delta_z_art_delta_abs_mean: -0.000514
- delta_event_prob_mean: -0.000675
- delta_event_presence_prob_mean: -0.000466
- delta_event_delta_prob_mean: 0.003106
- delta_event_rise_prob_mean: -0.002011
- delta_event_fall_prob_mean: 0.004578
- delta_event_energy_prob_mean: -0.003353
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.003184
- delta_acoustic_energy_mean: -0.015039
- delta_acoustic_delta_abs_mean: -0.002503
- delta_text_aux_abs_mean: 0.001955

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
