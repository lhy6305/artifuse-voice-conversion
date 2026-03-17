# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.602314
- loss_acoustic: 8.859386
- loss_event: 5.373377
- loss_text_aux: 0.215974
- loss_text_aux_effective: 0.215974
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035417
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.16328
- z_art_delta_abs_mean: 0.000811
- event_prob_mean: 0.503239
- event_presence_prob_mean: 0.555694
- event_delta_prob_mean: 0.533292
- event_rise_prob_mean: 0.490728
- event_fall_prob_mean: 0.53338
- event_energy_prob_mean: 0.522452
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.575355
- acoustic_energy_mean: -2.120311
- acoustic_delta_abs_mean: 0.072625
- text_aux_abs_mean: 0.272512

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.640278
- loss_acoustic: 4.891547
- loss_event: 5.409519
- loss_text_aux: 0.218654
- loss_text_aux_effective: 0.218654
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.167102
- z_art_delta_abs_mean: 0.000301
- event_prob_mean: 0.502595
- event_presence_prob_mean: 0.555189
- event_delta_prob_mean: 0.536466
- event_rise_prob_mean: 0.488677
- event_fall_prob_mean: 0.538086
- event_energy_prob_mean: 0.519187
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.578495
- acoustic_energy_mean: -2.135233
- acoustic_delta_abs_mean: 0.070123
- text_aux_abs_mean: 0.274577

## 对比
- delta_loss_total: -3.962036
- delta_loss_acoustic: -3.967839
- delta_loss_event: 0.036142
- delta_loss_text_aux: 0.00268
- delta_loss_text_aux_effective: 0.00268
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035417
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.003822
- delta_z_art_delta_abs_mean: -0.00051
- delta_event_prob_mean: -0.000644
- delta_event_presence_prob_mean: -0.000505
- delta_event_delta_prob_mean: 0.003174
- delta_event_rise_prob_mean: -0.002051
- delta_event_fall_prob_mean: 0.004706
- delta_event_energy_prob_mean: -0.003265
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.00314
- delta_acoustic_energy_mean: -0.014922
- delta_acoustic_delta_abs_mean: -0.002502
- delta_text_aux_abs_mean: 0.002065

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
