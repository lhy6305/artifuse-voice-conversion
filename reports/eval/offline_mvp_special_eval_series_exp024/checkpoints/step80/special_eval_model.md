# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688259
- loss_acoustic: 1.217894
- loss_event: 4.847951
- loss_text_aux: 0.111214
- loss_text_aux_effective: 0.111214
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0483
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240654
- z_art_delta_abs_mean: 0.009052
- event_prob_mean: 0.462056
- event_presence_prob_mean: 0.583138
- event_delta_prob_mean: 0.393228
- event_rise_prob_mean: 0.471884
- event_fall_prob_mean: 0.427437
- event_energy_prob_mean: 0.560388
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838493
- acoustic_energy_mean: -3.19401
- acoustic_delta_abs_mean: 0.028391
- text_aux_abs_mean: 0.215871

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381785
- loss_acoustic: 0.796025
- loss_event: 5.076111
- loss_text_aux: 0.214267
- loss_text_aux_effective: 0.214267
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.172217
- z_art_delta_abs_mean: 0.006064
- event_prob_mean: 0.451798
- event_presence_prob_mean: 0.55831
- event_delta_prob_mean: 0.405746
- event_rise_prob_mean: 0.453209
- event_fall_prob_mean: 0.446549
- event_energy_prob_mean: 0.54018
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073543
- acoustic_energy_mean: -4.168576
- acoustic_delta_abs_mean: 0.007891
- text_aux_abs_mean: 0.276634

## 对比
- delta_loss_total: -0.306474
- delta_loss_acoustic: -0.421869
- delta_loss_event: 0.22816
- delta_loss_text_aux: 0.103053
- delta_loss_text_aux_effective: 0.103053
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.0483
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.068437
- delta_z_art_delta_abs_mean: -0.002988
- delta_event_prob_mean: -0.010258
- delta_event_presence_prob_mean: -0.024828
- delta_event_delta_prob_mean: 0.012518
- delta_event_rise_prob_mean: -0.018675
- delta_event_fall_prob_mean: 0.019112
- delta_event_energy_prob_mean: -0.020208
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.23505
- delta_acoustic_energy_mean: -0.974566
- delta_acoustic_delta_abs_mean: -0.0205
- delta_text_aux_abs_mean: 0.060763

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
