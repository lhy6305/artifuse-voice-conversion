# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/checkpoints/EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.8291
- loss_acoustic: 3.302424
- loss_event: 4.969931
- loss_text_aux: 0.110901
- loss_text_aux_effective: 0.110901
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046539
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.193605
- z_art_delta_abs_mean: 0.004052
- event_prob_mean: 0.469391
- event_presence_prob_mean: 0.587326
- event_delta_prob_mean: 0.409689
- event_rise_prob_mean: 0.488226
- event_fall_prob_mean: 0.436627
- event_energy_prob_mean: 0.563873
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.933105
- acoustic_energy_mean: -3.620529
- acoustic_delta_abs_mean: 0.016349
- text_aux_abs_mean: 0.235871

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.121969
- loss_acoustic: 1.511955
- loss_event: 5.131013
- loss_text_aux: 0.211617
- loss_text_aux_effective: 0.211617
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.169605
- z_art_delta_abs_mean: 0.002731
- event_prob_mean: 0.462542
- event_presence_prob_mean: 0.57368
- event_delta_prob_mean: 0.416126
- event_rise_prob_mean: 0.474835
- event_fall_prob_mean: 0.446945
- event_energy_prob_mean: 0.552788
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.032089
- acoustic_energy_mean: -4.045944
- acoustic_delta_abs_mean: 0.008413
- text_aux_abs_mean: 0.262575

## 对比
- delta_loss_total: -1.707131
- delta_loss_acoustic: -1.790469
- delta_loss_event: 0.161082
- delta_loss_text_aux: 0.100716
- delta_loss_text_aux_effective: 0.100716
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046539
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.024
- delta_z_art_delta_abs_mean: -0.001321
- delta_event_prob_mean: -0.006849
- delta_event_presence_prob_mean: -0.013646
- delta_event_delta_prob_mean: 0.006437
- delta_event_rise_prob_mean: -0.013391
- delta_event_fall_prob_mean: 0.010318
- delta_event_energy_prob_mean: -0.011085
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.098984
- delta_acoustic_energy_mean: -0.425415
- delta_acoustic_delta_abs_mean: -0.007936
- delta_text_aux_abs_mean: 0.026704

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
