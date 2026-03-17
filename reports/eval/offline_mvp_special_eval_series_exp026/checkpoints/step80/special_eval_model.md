# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.792123
- loss_acoustic: 1.321521
- loss_event: 4.846687
- loss_text_aux: 0.116264
- loss_text_aux_effective: 0.116264
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048486
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.240547
- z_art_delta_abs_mean: 0.008795
- event_prob_mean: 0.462767
- event_presence_prob_mean: 0.586367
- event_delta_prob_mean: 0.390829
- event_rise_prob_mean: 0.472891
- event_fall_prob_mean: 0.426604
- event_energy_prob_mean: 0.564123
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.811097
- acoustic_energy_mean: -3.081017
- acoustic_delta_abs_mean: 0.028461
- text_aux_abs_mean: 0.191213

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.250017
- loss_acoustic: 0.670092
- loss_event: 5.074464
- loss_text_aux: 0.189724
- loss_text_aux_effective: 0.189724
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.173538
- z_art_delta_abs_mean: 0.005935
- event_prob_mean: 0.452638
- event_presence_prob_mean: 0.561974
- event_delta_prob_mean: 0.402715
- event_rise_prob_mean: 0.454606
- event_fall_prob_mean: 0.44517
- event_energy_prob_mean: 0.544219
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.039776
- acoustic_energy_mean: -4.011399
- acoustic_delta_abs_mean: 0.0092
- text_aux_abs_mean: 0.24428

## 对比
- delta_loss_total: -0.542106
- delta_loss_acoustic: -0.651429
- delta_loss_event: 0.227777
- delta_loss_text_aux: 0.07346
- delta_loss_text_aux_effective: 0.07346
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048486
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.067009
- delta_z_art_delta_abs_mean: -0.00286
- delta_event_prob_mean: -0.010129
- delta_event_presence_prob_mean: -0.024393
- delta_event_delta_prob_mean: 0.011886
- delta_event_rise_prob_mean: -0.018285
- delta_event_fall_prob_mean: 0.018566
- delta_event_energy_prob_mean: -0.019904
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.228679
- delta_acoustic_energy_mean: -0.930382
- delta_acoustic_delta_abs_mean: -0.019261
- delta_text_aux_abs_mean: 0.053067

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
