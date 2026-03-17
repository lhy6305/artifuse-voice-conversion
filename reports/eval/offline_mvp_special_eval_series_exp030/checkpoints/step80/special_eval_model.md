# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d13_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d13_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_exp030/checkpoints/EXP-20260315-030-offline-mvp-d13-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-late-lr-decay-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.819581
- loss_acoustic: 1.342123
- loss_event: 4.864004
- loss_text_aux: 0.109836
- loss_text_aux_effective: 0.109836
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048057
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.232257
- z_art_delta_abs_mean: 0.008336
- event_prob_mean: 0.462824
- event_presence_prob_mean: 0.583219
- event_delta_prob_mean: 0.395172
- event_rise_prob_mean: 0.474004
- event_fall_prob_mean: 0.42866
- event_energy_prob_mean: 0.5603
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.851744
- acoustic_energy_mean: -3.255505
- acoustic_delta_abs_mean: 0.022741
- text_aux_abs_mean: 0.217923

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.451247
- loss_acoustic: 0.862562
- loss_event: 5.083067
- loss_text_aux: 0.213447
- loss_text_aux_effective: 0.213447
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.170697
- z_art_delta_abs_mean: 0.005578
- event_prob_mean: 0.453016
- event_presence_prob_mean: 0.559884
- event_delta_prob_mean: 0.406905
- event_rise_prob_mean: 0.455958
- event_fall_prob_mean: 0.446657
- event_energy_prob_mean: 0.541377
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.068162
- acoustic_energy_mean: -4.159219
- acoustic_delta_abs_mean: 0.005515
- text_aux_abs_mean: 0.275092

## 对比
- delta_loss_total: -0.368334
- delta_loss_acoustic: -0.479561
- delta_loss_event: 0.219063
- delta_loss_text_aux: 0.103611
- delta_loss_text_aux_effective: 0.103611
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048057
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.06156
- delta_z_art_delta_abs_mean: -0.002758
- delta_event_prob_mean: -0.009808
- delta_event_presence_prob_mean: -0.023335
- delta_event_delta_prob_mean: 0.011733
- delta_event_rise_prob_mean: -0.018046
- delta_event_fall_prob_mean: 0.017997
- delta_event_energy_prob_mean: -0.018923
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.216418
- delta_acoustic_energy_mean: -0.903714
- delta_acoustic_delta_abs_mean: -0.017226
- delta_text_aux_abs_mean: 0.057169

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
