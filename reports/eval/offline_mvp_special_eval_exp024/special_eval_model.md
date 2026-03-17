# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.730527
- loss_acoustic: 0.377181
- loss_event: 4.602053
- loss_text_aux: 0.112645
- loss_text_aux_effective: 0.112645
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.056581
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.437739
- z_art_delta_abs_mean: 0.012484
- event_prob_mean: 0.45786
- event_presence_prob_mean: 0.645723
- event_delta_prob_mean: 0.313048
- event_rise_prob_mean: 0.49715
- event_fall_prob_mean: 0.403795
- event_energy_prob_mean: 0.612716
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.860796
- acoustic_energy_mean: -3.269982
- acoustic_delta_abs_mean: 0.012576
- text_aux_abs_mean: 0.242853

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.727165
- loss_acoustic: 0.185085
- loss_event: 4.982089
- loss_text_aux: 0.215644
- loss_text_aux_effective: 0.215644
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.340986
- z_art_delta_abs_mean: 0.009884
- event_prob_mean: 0.445539
- event_presence_prob_mean: 0.612569
- event_delta_prob_mean: 0.326128
- event_rise_prob_mean: 0.472281
- event_fall_prob_mean: 0.419205
- event_energy_prob_mean: 0.586049
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998524
- acoustic_energy_mean: -3.788915
- acoustic_delta_abs_mean: 0.014535
- text_aux_abs_mean: 0.270218

## 对比
- delta_loss_total: -0.003362
- delta_loss_acoustic: -0.192096
- delta_loss_event: 0.380036
- delta_loss_text_aux: 0.102999
- delta_loss_text_aux_effective: 0.102999
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.056581
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.096753
- delta_z_art_delta_abs_mean: -0.0026
- delta_event_prob_mean: -0.012321
- delta_event_presence_prob_mean: -0.033154
- delta_event_delta_prob_mean: 0.01308
- delta_event_rise_prob_mean: -0.024869
- delta_event_fall_prob_mean: 0.01541
- delta_event_energy_prob_mean: -0.026667
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137728
- delta_acoustic_energy_mean: -0.518933
- delta_acoustic_delta_abs_mean: 0.001959
- delta_text_aux_abs_mean: 0.027365

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
