# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d9_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool/checkpoints/EXP-20260315-025-offline-mvp-d9-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-dualpool-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.730334
- loss_acoustic: 0.377077
- loss_event: 4.601832
- loss_text_aux: 0.112671
- loss_text_aux_effective: 0.112671
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.056576
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.438107
- z_art_delta_abs_mean: 0.012507
- event_prob_mean: 0.457849
- event_presence_prob_mean: 0.645733
- event_delta_prob_mean: 0.313093
- event_rise_prob_mean: 0.497072
- event_fall_prob_mean: 0.403823
- event_energy_prob_mean: 0.612709
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.860832
- acoustic_energy_mean: -3.269933
- acoustic_delta_abs_mean: 0.012955
- text_aux_abs_mean: 0.243045

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.727161
- loss_acoustic: 0.185108
- loss_event: 4.981956
- loss_text_aux: 0.215776
- loss_text_aux_effective: 0.215776
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.341163
- z_art_delta_abs_mean: 0.0099
- event_prob_mean: 0.445524
- event_presence_prob_mean: 0.612558
- event_delta_prob_mean: 0.326175
- event_rise_prob_mean: 0.47221
- event_fall_prob_mean: 0.419276
- event_energy_prob_mean: 0.58602
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998526
- acoustic_energy_mean: -3.788893
- acoustic_delta_abs_mean: 0.014906
- text_aux_abs_mean: 0.270445

## 对比
- delta_loss_total: -0.003173
- delta_loss_acoustic: -0.191969
- delta_loss_event: 0.380124
- delta_loss_text_aux: 0.103105
- delta_loss_text_aux_effective: 0.103105
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.056576
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.096944
- delta_z_art_delta_abs_mean: -0.002607
- delta_event_prob_mean: -0.012325
- delta_event_presence_prob_mean: -0.033175
- delta_event_delta_prob_mean: 0.013082
- delta_event_rise_prob_mean: -0.024862
- delta_event_fall_prob_mean: 0.015453
- delta_event_energy_prob_mean: -0.026689
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137694
- delta_acoustic_energy_mean: -0.51896
- delta_acoustic_delta_abs_mean: 0.001951
- delta_text_aux_abs_mean: 0.0274

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
