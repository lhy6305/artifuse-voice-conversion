# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.341964
- loss_acoustic: 16.565854
- loss_event: 5.44438
- loss_text_aux: 0.20287
- loss_text_aux_effective: 0.20287
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036792
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.085762
- z_art_delta_abs_mean: 0.000586
- event_prob_mean: 0.50946
- event_presence_prob_mean: 0.525907
- event_delta_prob_mean: 0.527264
- event_rise_prob_mean: 0.52773
- event_fall_prob_mean: 0.523814
- event_energy_prob_mean: 0.525091
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198429
- acoustic_energy_mean: -0.487496
- acoustic_delta_abs_mean: 0.137129
- text_aux_abs_mean: 0.115244

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.630097
- loss_acoustic: 12.869584
- loss_event: 5.47083
- loss_text_aux: 0.124153
- loss_text_aux_effective: 0.124153
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.08485
- z_art_delta_abs_mean: 0.000334
- event_prob_mean: 0.509163
- event_presence_prob_mean: 0.52513
- event_delta_prob_mean: 0.52903
- event_rise_prob_mean: 0.52858
- event_fall_prob_mean: 0.526438
- event_energy_prob_mean: 0.522877
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198873
- acoustic_energy_mean: -0.489488
- acoustic_delta_abs_mean: 0.136643
- text_aux_abs_mean: 0.115213

## 对比
- delta_loss_total: -3.711867
- delta_loss_acoustic: -3.69627
- delta_loss_event: 0.02645
- delta_loss_text_aux: -0.078717
- delta_loss_text_aux_effective: -0.078717
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036792
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.000912
- delta_z_art_delta_abs_mean: -0.000252
- delta_event_prob_mean: -0.000297
- delta_event_presence_prob_mean: -0.000777
- delta_event_delta_prob_mean: 0.001766
- delta_event_rise_prob_mean: 0.00085
- delta_event_fall_prob_mean: 0.002624
- delta_event_energy_prob_mean: -0.002214
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000444
- delta_acoustic_energy_mean: -0.001992
- delta_acoustic_delta_abs_mean: -0.000486
- delta_text_aux_abs_mean: -3.1e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
