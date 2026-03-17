# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.846479
- loss_acoustic: 0.474246
- loss_event: 4.641875
- loss_text_aux: 0.113751
- loss_text_aux_effective: 0.113751
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053278
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.354243
- z_art_delta_abs_mean: 0.012372
- event_prob_mean: 0.460641
- event_presence_prob_mean: 0.626124
- event_delta_prob_mean: 0.345231
- event_rise_prob_mean: 0.487422
- event_fall_prob_mean: 0.416465
- event_energy_prob_mean: 0.594128
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.917948
- acoustic_energy_mean: -3.482434
- acoustic_delta_abs_mean: 0.01342
- text_aux_abs_mean: 0.25925

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.25857
- loss_acoustic: 0.706317
- loss_event: 4.988913
- loss_text_aux: 0.251971
- loss_text_aux_effective: 0.251971
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.251804
- z_art_delta_abs_mean: 0.009253
- event_prob_mean: 0.447316
- event_presence_prob_mean: 0.591549
- event_delta_prob_mean: 0.360149
- event_rise_prob_mean: 0.461496
- event_fall_prob_mean: 0.432845
- event_energy_prob_mean: 0.565769
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.130549
- acoustic_energy_mean: -4.330406
- acoustic_delta_abs_mean: 0.010942
- text_aux_abs_mean: 0.310574

## 对比
- delta_loss_total: 0.412091
- delta_loss_acoustic: 0.232071
- delta_loss_event: 0.347038
- delta_loss_text_aux: 0.13822
- delta_loss_text_aux_effective: 0.13822
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053278
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.102439
- delta_z_art_delta_abs_mean: -0.003119
- delta_event_prob_mean: -0.013325
- delta_event_presence_prob_mean: -0.034575
- delta_event_delta_prob_mean: 0.014918
- delta_event_rise_prob_mean: -0.025926
- delta_event_fall_prob_mean: 0.01638
- delta_event_energy_prob_mean: -0.028359
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.212601
- delta_acoustic_energy_mean: -0.847972
- delta_acoustic_delta_abs_mean: -0.002478
- delta_text_aux_abs_mean: 0.051324

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
