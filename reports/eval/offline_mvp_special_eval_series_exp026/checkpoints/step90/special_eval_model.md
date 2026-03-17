# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.35247
- loss_acoustic: 0.940469
- loss_event: 4.722152
- loss_text_aux: 0.116505
- loss_text_aux_effective: 0.116505
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051128
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.312403
- z_art_delta_abs_mean: 0.012162
- event_prob_mean: 0.45977
- event_presence_prob_mean: 0.602438
- event_delta_prob_mean: 0.366875
- event_rise_prob_mean: 0.471143
- event_fall_prob_mean: 0.417057
- event_energy_prob_mean: 0.577473
- event_presence_peak_ratio: 0.825697
- acoustic_abs_mean: 0.816391
- acoustic_energy_mean: -3.069415
- acoustic_delta_abs_mean: 0.040588
- text_aux_abs_mean: 0.215516

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.13213
- loss_acoustic: 0.573545
- loss_event: 5.020856
- loss_text_aux: 0.206286
- loss_text_aux_effective: 0.206286
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.209373
- z_art_delta_abs_mean: 0.008625
- event_prob_mean: 0.447387
- event_presence_prob_mean: 0.57006
- event_delta_prob_mean: 0.382067
- event_rise_prob_mean: 0.449016
- event_fall_prob_mean: 0.43796
- event_energy_prob_mean: 0.550739
- event_presence_peak_ratio: 0.954418
- acoustic_abs_mean: 1.074425
- acoustic_energy_mean: -4.099688
- acoustic_delta_abs_mean: 0.020377
- text_aux_abs_mean: 0.268835

## 对比
- delta_loss_total: -0.22034
- delta_loss_acoustic: -0.366924
- delta_loss_event: 0.298704
- delta_loss_text_aux: 0.089781
- delta_loss_text_aux_effective: 0.089781
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051128
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.10303
- delta_z_art_delta_abs_mean: -0.003537
- delta_event_prob_mean: -0.012383
- delta_event_presence_prob_mean: -0.032378
- delta_event_delta_prob_mean: 0.015192
- delta_event_rise_prob_mean: -0.022127
- delta_event_fall_prob_mean: 0.020903
- delta_event_energy_prob_mean: -0.026734
- delta_event_presence_peak_ratio: 0.128721
- delta_acoustic_abs_mean: 0.258034
- delta_acoustic_energy_mean: -1.030273
- delta_acoustic_delta_abs_mean: -0.020211
- delta_text_aux_abs_mean: 0.053319

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
