# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d4_round1_1_special_proxy_core_clause_ge4_early_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d4_special_proxy_core_clause_ge4_early_handoff_exp020/checkpoints/EXP-20260315-020-offline-mvp-d4-round1-1-special-proxy-core-clause-ge4-early-handoff-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427096
- loss_acoustic: 1.015734
- loss_event: 4.719066
- loss_text_aux: 0.117976
- loss_text_aux_effective: 0.117976
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051546
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.329054
- z_art_delta_abs_mean: 0.012742
- event_prob_mean: 0.459487
- event_presence_prob_mean: 0.602661
- event_delta_prob_mean: 0.364339
- event_rise_prob_mean: 0.472703
- event_fall_prob_mean: 0.412988
- event_energy_prob_mean: 0.576206
- event_presence_peak_ratio: 0.814595
- acoustic_abs_mean: 0.802452
- acoustic_energy_mean: -2.998564
- acoustic_delta_abs_mean: 0.045122
- text_aux_abs_mean: 0.223047

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.083968
- loss_acoustic: 0.523017
- loss_event: 5.022342
- loss_text_aux: 0.212591
- loss_text_aux_effective: 0.212591
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.220921
- z_art_delta_abs_mean: 0.009077
- event_prob_mean: 0.446867
- event_presence_prob_mean: 0.569749
- event_delta_prob_mean: 0.379772
- event_rise_prob_mean: 0.450057
- event_fall_prob_mean: 0.434039
- event_energy_prob_mean: 0.5492
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056674
- acoustic_energy_mean: -3.999981
- acoustic_delta_abs_mean: 0.024082
- text_aux_abs_mean: 0.274925

## 对比
- delta_loss_total: -0.343128
- delta_loss_acoustic: -0.492717
- delta_loss_event: 0.303276
- delta_loss_text_aux: 0.094615
- delta_loss_text_aux_effective: 0.094615
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051546
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.108133
- delta_z_art_delta_abs_mean: -0.003665
- delta_event_prob_mean: -0.01262
- delta_event_presence_prob_mean: -0.032912
- delta_event_delta_prob_mean: 0.015433
- delta_event_rise_prob_mean: -0.022646
- delta_event_fall_prob_mean: 0.021051
- delta_event_energy_prob_mean: -0.027006
- delta_event_presence_peak_ratio: 0.134712
- delta_acoustic_abs_mean: 0.254222
- delta_acoustic_energy_mean: -1.001417
- delta_acoustic_delta_abs_mean: -0.02104
- delta_text_aux_abs_mean: 0.051878

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
