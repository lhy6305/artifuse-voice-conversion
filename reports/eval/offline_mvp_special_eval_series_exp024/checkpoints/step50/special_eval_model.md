# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/checkpoints/EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration.step50.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.431348
- loss_acoustic: 6.772531
- loss_event: 5.210734
- loss_text_aux: 0.194352
- loss_text_aux_effective: 0.194352
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.038797
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.223716
- z_art_delta_abs_mean: 0.001251
- event_prob_mean: 0.481565
- event_presence_prob_mean: 0.568822
- event_delta_prob_mean: 0.497994
- event_rise_prob_mean: 0.464316
- event_fall_prob_mean: 0.490442
- event_energy_prob_mean: 0.533458
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.149989
- acoustic_energy_mean: -4.395614
- acoustic_delta_abs_mean: 0.055422
- text_aux_abs_mean: 0.399876

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.515622
- loss_acoustic: 2.809674
- loss_event: 5.271793
- loss_text_aux: 0.348297
- loss_text_aux_effective: 0.348297
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.233401
- z_art_delta_abs_mean: 0.00049
- event_prob_mean: 0.479483
- event_presence_prob_mean: 0.566634
- event_delta_prob_mean: 0.503024
- event_rise_prob_mean: 0.458807
- event_fall_prob_mean: 0.495118
- event_energy_prob_mean: 0.528733
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.163339
- acoustic_energy_mean: -4.460006
- acoustic_delta_abs_mean: 0.049205
- text_aux_abs_mean: 0.404824

## 对比
- delta_loss_total: -3.915726
- delta_loss_acoustic: -3.962857
- delta_loss_event: 0.061059
- delta_loss_text_aux: 0.153945
- delta_loss_text_aux_effective: 0.153945
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.038797
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.009685
- delta_z_art_delta_abs_mean: -0.000761
- delta_event_prob_mean: -0.002082
- delta_event_presence_prob_mean: -0.002188
- delta_event_delta_prob_mean: 0.00503
- delta_event_rise_prob_mean: -0.005509
- delta_event_fall_prob_mean: 0.004676
- delta_event_energy_prob_mean: -0.004725
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.01335
- delta_acoustic_energy_mean: -0.064392
- delta_acoustic_delta_abs_mean: -0.006217
- delta_text_aux_abs_mean: 0.004948

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
