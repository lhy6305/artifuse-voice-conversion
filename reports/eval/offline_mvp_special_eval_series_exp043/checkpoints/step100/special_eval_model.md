# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d17_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_exp043/checkpoints/EXP-20260315-043-offline-mvp-d17-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-profile-late-only-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.730107
- loss_acoustic: 0.37695
- loss_event: 4.601687
- loss_text_aux: 0.11264
- loss_text_aux_effective: 0.11264
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.056521
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.438434
- z_art_delta_abs_mean: 0.012504
- event_prob_mean: 0.457944
- event_presence_prob_mean: 0.645692
- event_delta_prob_mean: 0.313457
- event_rise_prob_mean: 0.497066
- event_fall_prob_mean: 0.404325
- event_energy_prob_mean: 0.612645
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.860862
- acoustic_energy_mean: -3.270055
- acoustic_delta_abs_mean: 0.01287
- text_aux_abs_mean: 0.242859

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.726955
- loss_acoustic: 0.185014
- loss_event: 4.981786
- loss_text_aux: 0.215648
- loss_text_aux_effective: 0.215648
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_structural_clause_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.341528
- z_art_delta_abs_mean: 0.009899
- event_prob_mean: 0.445615
- event_presence_prob_mean: 0.612504
- event_delta_prob_mean: 0.326533
- event_rise_prob_mean: 0.472197
- event_fall_prob_mean: 0.419776
- event_energy_prob_mean: 0.585954
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998494
- acoustic_energy_mean: -3.788832
- acoustic_delta_abs_mean: 0.014794
- text_aux_abs_mean: 0.270257

## 对比
- delta_loss_total: -0.003152
- delta_loss_acoustic: -0.191936
- delta_loss_event: 0.380099
- delta_loss_text_aux: 0.103008
- delta_loss_text_aux_effective: 0.103008
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.056521
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.096906
- delta_z_art_delta_abs_mean: -0.002605
- delta_event_prob_mean: -0.012329
- delta_event_presence_prob_mean: -0.033188
- delta_event_delta_prob_mean: 0.013076
- delta_event_rise_prob_mean: -0.024869
- delta_event_fall_prob_mean: 0.015451
- delta_event_energy_prob_mean: -0.026691
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137632
- delta_acoustic_energy_mean: -0.518777
- delta_acoustic_delta_abs_mean: 0.001924
- delta_text_aux_abs_mean: 0.027398

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
