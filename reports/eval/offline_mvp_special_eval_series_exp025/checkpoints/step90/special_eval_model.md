# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d9_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool/checkpoints/EXP-20260315-025-offline-mvp-d9-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-dualpool-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427322
- loss_acoustic: 1.015947
- loss_event: 4.719089
- loss_text_aux: 0.117982
- loss_text_aux_effective: 0.117982
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051544
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.328884
- z_art_delta_abs_mean: 0.012742
- event_prob_mean: 0.459489
- event_presence_prob_mean: 0.602653
- event_delta_prob_mean: 0.364353
- event_rise_prob_mean: 0.472698
- event_fall_prob_mean: 0.413009
- event_energy_prob_mean: 0.576215
- event_presence_peak_ratio: 0.814595
- acoustic_abs_mean: 0.802541
- acoustic_energy_mean: -2.998857
- acoustic_delta_abs_mean: 0.045165
- text_aux_abs_mean: 0.223165

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.084645
- loss_acoustic: 0.523666
- loss_event: 5.02235
- loss_text_aux: 0.212716
- loss_text_aux_effective: 0.212716
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.220754
- z_art_delta_abs_mean: 0.009077
- event_prob_mean: 0.446869
- event_presence_prob_mean: 0.569743
- event_delta_prob_mean: 0.379779
- event_rise_prob_mean: 0.450055
- event_fall_prob_mean: 0.434058
- event_energy_prob_mean: 0.549209
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056848
- acoustic_energy_mean: -4.000746
- acoustic_delta_abs_mean: 0.024118
- text_aux_abs_mean: 0.275063

## 对比
- delta_loss_total: -0.342677
- delta_loss_acoustic: -0.492281
- delta_loss_event: 0.303261
- delta_loss_text_aux: 0.094734
- delta_loss_text_aux_effective: 0.094734
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051544
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.10813
- delta_z_art_delta_abs_mean: -0.003665
- delta_event_prob_mean: -0.01262
- delta_event_presence_prob_mean: -0.03291
- delta_event_delta_prob_mean: 0.015426
- delta_event_rise_prob_mean: -0.022643
- delta_event_fall_prob_mean: 0.021049
- delta_event_energy_prob_mean: -0.027006
- delta_event_presence_peak_ratio: 0.134712
- delta_acoustic_abs_mean: 0.254307
- delta_acoustic_energy_mean: -1.001889
- delta_acoustic_delta_abs_mean: -0.021047
- delta_text_aux_abs_mean: 0.051898

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
