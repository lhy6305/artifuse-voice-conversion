# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.341712
- loss_acoustic: 16.565713
- loss_event: 5.444066
- loss_text_aux: 0.203005
- loss_text_aux_effective: 0.203005
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036849
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.085492
- z_art_delta_abs_mean: 0.000586
- event_prob_mean: 0.509025
- event_presence_prob_mean: 0.525689
- event_delta_prob_mean: 0.527202
- event_rise_prob_mean: 0.527071
- event_fall_prob_mean: 0.522636
- event_energy_prob_mean: 0.5251
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.19837
- acoustic_energy_mean: -0.487537
- acoustic_delta_abs_mean: 0.137459
- text_aux_abs_mean: 0.114541

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.62906
- loss_acoustic: 12.869347
- loss_event: 5.469306
- loss_text_aux: 0.123962
- loss_text_aux_effective: 0.123962
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.08458
- z_art_delta_abs_mean: 0.000334
- event_prob_mean: 0.508719
- event_presence_prob_mean: 0.524922
- event_delta_prob_mean: 0.528948
- event_rise_prob_mean: 0.527892
- event_fall_prob_mean: 0.525249
- event_energy_prob_mean: 0.5229
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198808
- acoustic_energy_mean: -0.489521
- acoustic_delta_abs_mean: 0.13696
- text_aux_abs_mean: 0.114499

## 对比
- delta_loss_total: -3.712652
- delta_loss_acoustic: -3.696366
- delta_loss_event: 0.02524
- delta_loss_text_aux: -0.079043
- delta_loss_text_aux_effective: -0.079043
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036849
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.000912
- delta_z_art_delta_abs_mean: -0.000252
- delta_event_prob_mean: -0.000306
- delta_event_presence_prob_mean: -0.000767
- delta_event_delta_prob_mean: 0.001746
- delta_event_rise_prob_mean: 0.000821
- delta_event_fall_prob_mean: 0.002613
- delta_event_energy_prob_mean: -0.0022
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000438
- delta_acoustic_energy_mean: -0.001984
- delta_acoustic_delta_abs_mean: -0.000499
- delta_text_aux_abs_mean: -4.2e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
