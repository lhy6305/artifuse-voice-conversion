# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427092
- loss_acoustic: 1.015722
- loss_event: 4.719082
- loss_text_aux: 0.117976
- loss_text_aux_effective: 0.117976
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051546
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.328993
- z_art_delta_abs_mean: 0.012741
- event_prob_mean: 0.459487
- event_presence_prob_mean: 0.602657
- event_delta_prob_mean: 0.364343
- event_rise_prob_mean: 0.472702
- event_fall_prob_mean: 0.412991
- event_energy_prob_mean: 0.576208
- event_presence_peak_ratio: 0.814595
- acoustic_abs_mean: 0.802476
- acoustic_energy_mean: -2.998661
- acoustic_delta_abs_mean: 0.045126
- text_aux_abs_mean: 0.223071

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.08411
- loss_acoustic: 0.523151
- loss_event: 5.022349
- loss_text_aux: 0.212619
- loss_text_aux_effective: 0.212619
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.220871
- z_art_delta_abs_mean: 0.009076
- event_prob_mean: 0.446867
- event_presence_prob_mean: 0.569747
- event_delta_prob_mean: 0.379773
- event_rise_prob_mean: 0.450058
- event_fall_prob_mean: 0.434041
- event_energy_prob_mean: 0.549203
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056718
- acoustic_energy_mean: -4.000191
- acoustic_delta_abs_mean: 0.024087
- text_aux_abs_mean: 0.274954

## 对比
- delta_loss_total: -0.342982
- delta_loss_acoustic: -0.492571
- delta_loss_event: 0.303267
- delta_loss_text_aux: 0.094643
- delta_loss_text_aux_effective: 0.094643
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051546
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.108122
- delta_z_art_delta_abs_mean: -0.003665
- delta_event_prob_mean: -0.01262
- delta_event_presence_prob_mean: -0.03291
- delta_event_delta_prob_mean: 0.01543
- delta_event_rise_prob_mean: -0.022644
- delta_event_fall_prob_mean: 0.02105
- delta_event_energy_prob_mean: -0.027005
- delta_event_presence_peak_ratio: 0.134712
- delta_acoustic_abs_mean: 0.254242
- delta_acoustic_energy_mean: -1.00153
- delta_acoustic_delta_abs_mean: -0.021039
- delta_text_aux_abs_mean: 0.051883

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
