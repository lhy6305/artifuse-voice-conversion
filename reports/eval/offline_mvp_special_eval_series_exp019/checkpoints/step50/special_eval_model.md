# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.471713
- loss_acoustic: 6.803287
- loss_event: 5.220219
- loss_text_aux: 0.219437
- loss_text_aux_effective: 0.219437
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.038344
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.22923
- z_art_delta_abs_mean: 0.001261
- event_prob_mean: 0.482269
- event_presence_prob_mean: 0.571017
- event_delta_prob_mean: 0.503086
- event_rise_prob_mean: 0.462288
- event_fall_prob_mean: 0.493242
- event_energy_prob_mean: 0.532213
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.148155
- acoustic_energy_mean: -4.38193
- acoustic_delta_abs_mean: 0.049157
- text_aux_abs_mean: 0.448492

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.516789
- loss_acoustic: 2.798924
- loss_event: 5.276742
- loss_text_aux: 0.395522
- loss_text_aux_effective: 0.395522
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.239102
- z_art_delta_abs_mean: 0.000486
- event_prob_mean: 0.480327
- event_presence_prob_mean: 0.569146
- event_delta_prob_mean: 0.508354
- event_rise_prob_mean: 0.456794
- event_fall_prob_mean: 0.498138
- event_energy_prob_mean: 0.527601
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.160281
- acoustic_energy_mean: -4.440676
- acoustic_delta_abs_mean: 0.04322
- text_aux_abs_mean: 0.453598

## 对比
- delta_loss_total: -3.954924
- delta_loss_acoustic: -4.004363
- delta_loss_event: 0.056523
- delta_loss_text_aux: 0.176085
- delta_loss_text_aux_effective: 0.176085
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.038344
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.009872
- delta_z_art_delta_abs_mean: -0.000775
- delta_event_prob_mean: -0.001942
- delta_event_presence_prob_mean: -0.001871
- delta_event_delta_prob_mean: 0.005268
- delta_event_rise_prob_mean: -0.005494
- delta_event_fall_prob_mean: 0.004896
- delta_event_energy_prob_mean: -0.004612
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.012126
- delta_acoustic_energy_mean: -0.058746
- delta_acoustic_delta_abs_mean: -0.005937
- delta_text_aux_abs_mean: 0.005106

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
