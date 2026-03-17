# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step30.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 11.602346
- loss_acoustic: 8.859487
- loss_event: 5.373251
- loss_text_aux: 0.215967
- loss_text_aux_effective: 0.215967
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035406
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.163314
- z_art_delta_abs_mean: 0.000811
- event_prob_mean: 0.503308
- event_presence_prob_mean: 0.555996
- event_delta_prob_mean: 0.533289
- event_rise_prob_mean: 0.490744
- event_fall_prob_mean: 0.53354
- event_energy_prob_mean: 0.522512
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.575356
- acoustic_energy_mean: -2.120278
- acoustic_delta_abs_mean: 0.072651
- text_aux_abs_mean: 0.272513

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 7.64036
- loss_acoustic: 4.891656
- loss_event: 5.409466
- loss_text_aux: 0.218654
- loss_text_aux_effective: 0.218654
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.167132
- z_art_delta_abs_mean: 0.000301
- event_prob_mean: 0.502663
- event_presence_prob_mean: 0.555492
- event_delta_prob_mean: 0.536462
- event_rise_prob_mean: 0.488691
- event_fall_prob_mean: 0.53825
- event_energy_prob_mean: 0.519247
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.578496
- acoustic_energy_mean: -2.1352
- acoustic_delta_abs_mean: 0.070145
- text_aux_abs_mean: 0.274577

## 对比
- delta_loss_total: -3.961986
- delta_loss_acoustic: -3.967831
- delta_loss_event: 0.036215
- delta_loss_text_aux: 0.002687
- delta_loss_text_aux_effective: 0.002687
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035406
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.003818
- delta_z_art_delta_abs_mean: -0.00051
- delta_event_prob_mean: -0.000645
- delta_event_presence_prob_mean: -0.000504
- delta_event_delta_prob_mean: 0.003173
- delta_event_rise_prob_mean: -0.002053
- delta_event_fall_prob_mean: 0.00471
- delta_event_energy_prob_mean: -0.003265
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.00314
- delta_acoustic_energy_mean: -0.014922
- delta_acoustic_delta_abs_mean: -0.002506
- delta_text_aux_abs_mean: 0.002064

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
