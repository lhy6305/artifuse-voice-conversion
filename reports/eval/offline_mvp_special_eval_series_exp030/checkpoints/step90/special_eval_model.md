# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d13_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d13_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_exp030/checkpoints/EXP-20260315-030-offline-mvp-d13-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-late-lr-decay-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.493639
- loss_acoustic: 1.05127
- loss_event: 4.785809
- loss_text_aux: 0.115622
- loss_text_aux_effective: 0.115622
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.04972
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.28187
- z_art_delta_abs_mean: 0.011172
- event_prob_mean: 0.460324
- event_presence_prob_mean: 0.590111
- event_delta_prob_mean: 0.381027
- event_rise_prob_mean: 0.46932
- event_fall_prob_mean: 0.42008
- event_energy_prob_mean: 0.56624
- event_presence_peak_ratio: 0.828756
- acoustic_abs_mean: 0.81229
- acoustic_energy_mean: -3.04908
- acoustic_delta_abs_mean: 0.047656
- text_aux_abs_mean: 0.215213

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.197564
- loss_acoustic: 0.623818
- loss_event: 5.049611
- loss_text_aux: 0.213933
- loss_text_aux_effective: 0.213933
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.189916
- z_art_delta_abs_mean: 0.007693
- event_prob_mean: 0.448759
- event_presence_prob_mean: 0.560865
- event_delta_prob_mean: 0.395503
- event_rise_prob_mean: 0.448754
- event_fall_prob_mean: 0.440876
- event_energy_prob_mean: 0.542223
- event_presence_peak_ratio: 0.956096
- acoustic_abs_mean: 1.082476
- acoustic_energy_mean: -4.136888
- acoustic_delta_abs_mean: 0.019888
- text_aux_abs_mean: 0.276755

## 对比
- delta_loss_total: -0.296075
- delta_loss_acoustic: -0.427452
- delta_loss_event: 0.263802
- delta_loss_text_aux: 0.098311
- delta_loss_text_aux_effective: 0.098311
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.04972
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.091954
- delta_z_art_delta_abs_mean: -0.003479
- delta_event_prob_mean: -0.011565
- delta_event_presence_prob_mean: -0.029246
- delta_event_delta_prob_mean: 0.014476
- delta_event_rise_prob_mean: -0.020566
- delta_event_fall_prob_mean: 0.020796
- delta_event_energy_prob_mean: -0.024017
- delta_event_presence_peak_ratio: 0.12734
- delta_acoustic_abs_mean: 0.270186
- delta_acoustic_energy_mean: -1.087808
- delta_acoustic_delta_abs_mean: -0.027768
- delta_text_aux_abs_mean: 0.061542

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
