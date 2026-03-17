# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.592522
- loss_acoustic: 12.83604
- loss_event: 5.408626
- loss_text_aux: 0.195177
- loss_text_aux_effective: 0.195177
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036061
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.11515
- z_art_delta_abs_mean: 0.000639
- event_prob_mean: 0.508056
- event_presence_prob_mean: 0.543224
- event_delta_prob_mean: 0.528116
- event_rise_prob_mean: 0.512098
- event_fall_prob_mean: 0.530428
- event_energy_prob_mean: 0.525535
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.37335
- acoustic_energy_mean: -1.145001
- acoustic_delta_abs_mean: 0.152034
- text_aux_abs_mean: 0.183275

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.775107
- loss_acoustic: 9.024788
- loss_event: 5.442519
- loss_text_aux: 0.144033
- loss_text_aux_effective: 0.144033
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.1176
- z_art_delta_abs_mean: 0.000315
- event_prob_mean: 0.5076
- event_presence_prob_mean: 0.542491
- event_delta_prob_mean: 0.530288
- event_rise_prob_mean: 0.511658
- event_fall_prob_mean: 0.534259
- event_energy_prob_mean: 0.522814
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375367
- acoustic_energy_mean: -1.152486
- acoustic_delta_abs_mean: 0.151321
- text_aux_abs_mean: 0.184314

## 对比
- delta_loss_total: -3.817415
- delta_loss_acoustic: -3.811252
- delta_loss_event: 0.033893
- delta_loss_text_aux: -0.051144
- delta_loss_text_aux_effective: -0.051144
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036061
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.00245
- delta_z_art_delta_abs_mean: -0.000324
- delta_event_prob_mean: -0.000456
- delta_event_presence_prob_mean: -0.000733
- delta_event_delta_prob_mean: 0.002172
- delta_event_rise_prob_mean: -0.00044
- delta_event_fall_prob_mean: 0.003831
- delta_event_energy_prob_mean: -0.002721
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002017
- delta_acoustic_energy_mean: -0.007485
- delta_acoustic_delta_abs_mean: -0.000713
- delta_text_aux_abs_mean: 0.001039

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
