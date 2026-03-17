# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.427309
- loss_acoustic: 1.015869
- loss_event: 4.719252
- loss_text_aux: 0.117949
- loss_text_aux_effective: 0.117949
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051551
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.328526
- z_art_delta_abs_mean: 0.012726
- event_prob_mean: 0.459491
- event_presence_prob_mean: 0.60265
- event_delta_prob_mean: 0.3643
- event_rise_prob_mean: 0.472732
- event_fall_prob_mean: 0.41296
- event_energy_prob_mean: 0.576266
- event_presence_peak_ratio: 0.815052
- acoustic_abs_mean: 0.80257
- acoustic_energy_mean: -2.998787
- acoustic_delta_abs_mean: 0.045245
- text_aux_abs_mean: 0.223283

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.0844
- loss_acoustic: 0.523373
- loss_event: 5.022444
- loss_text_aux: 0.212757
- loss_text_aux_effective: 0.212757
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.220539
- z_art_delta_abs_mean: 0.009066
- event_prob_mean: 0.446873
- event_presence_prob_mean: 0.56977
- event_delta_prob_mean: 0.379714
- event_rise_prob_mean: 0.450083
- event_fall_prob_mean: 0.433951
- event_energy_prob_mean: 0.549279
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056836
- acoustic_energy_mean: -4.000582
- acoustic_delta_abs_mean: 0.024057
- text_aux_abs_mean: 0.275128

## 对比
- delta_loss_total: -0.342909
- delta_loss_acoustic: -0.492496
- delta_loss_event: 0.303192
- delta_loss_text_aux: 0.094808
- delta_loss_text_aux_effective: 0.094808
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051551
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.107987
- delta_z_art_delta_abs_mean: -0.00366
- delta_event_prob_mean: -0.012618
- delta_event_presence_prob_mean: -0.03288
- delta_event_delta_prob_mean: 0.015414
- delta_event_rise_prob_mean: -0.022649
- delta_event_fall_prob_mean: 0.020991
- delta_event_energy_prob_mean: -0.026987
- delta_event_presence_peak_ratio: 0.134255
- delta_acoustic_abs_mean: 0.254266
- delta_acoustic_energy_mean: -1.001795
- delta_acoustic_delta_abs_mean: -0.021188
- delta_text_aux_abs_mean: 0.051845

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
