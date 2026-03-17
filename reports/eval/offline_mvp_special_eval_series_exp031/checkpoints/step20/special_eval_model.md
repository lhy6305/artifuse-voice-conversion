# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d15_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_exp031/checkpoints/EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.592519
- loss_acoustic: 12.835991
- loss_event: 5.408711
- loss_text_aux: 0.195184
- loss_text_aux_effective: 0.195184
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036069
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.115115
- z_art_delta_abs_mean: 0.000639
- event_prob_mean: 0.508012
- event_presence_prob_mean: 0.543028
- event_delta_prob_mean: 0.528114
- event_rise_prob_mean: 0.512083
- event_fall_prob_mean: 0.530346
- event_energy_prob_mean: 0.525492
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373344
- acoustic_energy_mean: -1.145008
- acoustic_delta_abs_mean: 0.152014
- text_aux_abs_mean: 0.183279

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.775078
- loss_acoustic: 9.024739
- loss_event: 5.442559
- loss_text_aux: 0.144036
- loss_text_aux_effective: 0.144036
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_challenge_proxy_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.117567
- z_art_delta_abs_mean: 0.000315
- event_prob_mean: 0.507556
- event_presence_prob_mean: 0.542293
- event_delta_prob_mean: 0.530287
- event_rise_prob_mean: 0.511644
- event_fall_prob_mean: 0.534176
- event_energy_prob_mean: 0.522771
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375362
- acoustic_energy_mean: -1.152494
- acoustic_delta_abs_mean: 0.151302
- text_aux_abs_mean: 0.184318

## 对比
- delta_loss_total: -3.817441
- delta_loss_acoustic: -3.811252
- delta_loss_event: 0.033848
- delta_loss_text_aux: -0.051148
- delta_loss_text_aux_effective: -0.051148
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036069
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.002452
- delta_z_art_delta_abs_mean: -0.000324
- delta_event_prob_mean: -0.000456
- delta_event_presence_prob_mean: -0.000735
- delta_event_delta_prob_mean: 0.002173
- delta_event_rise_prob_mean: -0.000439
- delta_event_fall_prob_mean: 0.00383
- delta_event_energy_prob_mean: -0.002721
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002018
- delta_acoustic_energy_mean: -0.007486
- delta_acoustic_delta_abs_mean: -0.000712
- delta_text_aux_abs_mean: 0.001039

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
