# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d4_round1_1_special_proxy_core_clause_ge4_early_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d4_special_proxy_core_clause_ge4_early_handoff_exp020/checkpoints/EXP-20260315-020-offline-mvp-d4-round1-1-special-proxy-core-clause-ge4-early-handoff-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.688603
- loss_acoustic: 1.218294
- loss_event: 4.847831
- loss_text_aux: 0.111228
- loss_text_aux_effective: 0.111228
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048295
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.240874
- z_art_delta_abs_mean: 0.009056
- event_prob_mean: 0.46206
- event_presence_prob_mean: 0.583167
- event_delta_prob_mean: 0.39324
- event_rise_prob_mean: 0.471901
- event_fall_prob_mean: 0.427491
- event_energy_prob_mean: 0.560346
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.838425
- acoustic_energy_mean: -3.194009
- acoustic_delta_abs_mean: 0.028233
- text_aux_abs_mean: 0.215775

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.381433
- loss_acoustic: 0.795709
- loss_event: 5.076055
- loss_text_aux: 0.214212
- loss_text_aux_effective: 0.214212
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.172386
- z_art_delta_abs_mean: 0.006067
- event_prob_mean: 0.451805
- event_presence_prob_mean: 0.558321
- event_delta_prob_mean: 0.405768
- event_rise_prob_mean: 0.453231
- event_fall_prob_mean: 0.446639
- event_energy_prob_mean: 0.540131
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.073387
- acoustic_energy_mean: -4.16806
- acoustic_delta_abs_mean: 0.007852
- text_aux_abs_mean: 0.276557

## 对比
- delta_loss_total: -0.30717
- delta_loss_acoustic: -0.422585
- delta_loss_event: 0.228224
- delta_loss_text_aux: 0.102984
- delta_loss_text_aux_effective: 0.102984
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048295
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.068488
- delta_z_art_delta_abs_mean: -0.002989
- delta_event_prob_mean: -0.010255
- delta_event_presence_prob_mean: -0.024846
- delta_event_delta_prob_mean: 0.012528
- delta_event_rise_prob_mean: -0.01867
- delta_event_fall_prob_mean: 0.019148
- delta_event_energy_prob_mean: -0.020215
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.234962
- delta_acoustic_energy_mean: -0.974051
- delta_acoustic_delta_abs_mean: -0.020381
- delta_text_aux_abs_mean: 0.060782

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
