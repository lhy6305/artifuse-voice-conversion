# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.394526
- loss_acoustic: 0.972846
- loss_event: 4.741937
- loss_text_aux: 0.116915
- loss_text_aux_effective: 0.116915
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.050341
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.298933
- z_art_delta_abs_mean: 0.012137
- event_prob_mean: 0.461212
- event_presence_prob_mean: 0.599069
- event_delta_prob_mean: 0.376566
- event_rise_prob_mean: 0.471869
- event_fall_prob_mean: 0.419557
- event_energy_prob_mean: 0.57205
- event_presence_peak_ratio: 0.821287
- acoustic_abs_mean: 0.832597
- acoustic_energy_mean: -3.136378
- acoustic_delta_abs_mean: 0.043243
- text_aux_abs_mean: 0.223114

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.327829
- loss_acoustic: 0.760305
- loss_event: 5.03057
- loss_text_aux: 0.227228
- loss_text_aux_effective: 0.227228
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.197468
- z_art_delta_abs_mean: 0.008492
- event_prob_mean: 0.448382
- event_presence_prob_mean: 0.566944
- event_delta_prob_mean: 0.391816
- event_rise_prob_mean: 0.448861
- event_fall_prob_mean: 0.439411
- event_energy_prob_mean: 0.545269
- event_presence_peak_ratio: 0.95316
- acoustic_abs_mean: 1.108873
- acoustic_energy_mean: -4.257728
- acoustic_delta_abs_mean: 0.022193
- text_aux_abs_mean: 0.286156

## 对比
- delta_loss_total: -0.066697
- delta_loss_acoustic: -0.212541
- delta_loss_event: 0.288633
- delta_loss_text_aux: 0.110313
- delta_loss_text_aux_effective: 0.110313
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.050341
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.101465
- delta_z_art_delta_abs_mean: -0.003645
- delta_event_prob_mean: -0.01283
- delta_event_presence_prob_mean: -0.032125
- delta_event_delta_prob_mean: 0.01525
- delta_event_rise_prob_mean: -0.023008
- delta_event_fall_prob_mean: 0.019854
- delta_event_energy_prob_mean: -0.026781
- delta_event_presence_peak_ratio: 0.131873
- delta_acoustic_abs_mean: 0.276276
- delta_acoustic_energy_mean: -1.12135
- delta_acoustic_delta_abs_mean: -0.02105
- delta_text_aux_abs_mean: 0.063042

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
