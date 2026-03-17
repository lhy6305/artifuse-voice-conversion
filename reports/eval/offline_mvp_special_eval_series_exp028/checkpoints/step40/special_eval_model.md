# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.308845
- loss_acoustic: 6.588131
- loss_event: 5.323331
- loss_text_aux: 0.228435
- loss_text_aux_effective: 0.228435
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035802
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.221852
- z_art_delta_abs_mean: 0.001039
- event_prob_mean: 0.493212
- event_presence_prob_mean: 0.561742
- event_delta_prob_mean: 0.532919
- event_rise_prob_mean: 0.46758
- event_fall_prob_mean: 0.521488
- event_energy_prob_mean: 0.518955
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878221
- acoustic_energy_mean: -3.374073
- acoustic_delta_abs_mean: 0.067964
- text_aux_abs_mean: 0.37619

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.206448
- loss_acoustic: 2.458524
- loss_event: 5.361679
- loss_text_aux: 0.33406
- loss_text_aux_effective: 0.33406
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.229527
- z_art_delta_abs_mean: 0.000341
- event_prob_mean: 0.492169
- event_presence_prob_mean: 0.561049
- event_delta_prob_mean: 0.537584
- event_rise_prob_mean: 0.463794
- event_fall_prob_mean: 0.526471
- event_energy_prob_mean: 0.514922
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884748
- acoustic_energy_mean: -3.397771
- acoustic_delta_abs_mean: 0.072879
- text_aux_abs_mean: 0.378427

## 对比
- delta_loss_total: -4.102397
- delta_loss_acoustic: -4.129607
- delta_loss_event: 0.038348
- delta_loss_text_aux: 0.105625
- delta_loss_text_aux_effective: 0.105625
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035802
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: 0.007675
- delta_z_art_delta_abs_mean: -0.000698
- delta_event_prob_mean: -0.001043
- delta_event_presence_prob_mean: -0.000693
- delta_event_delta_prob_mean: 0.004665
- delta_event_rise_prob_mean: -0.003786
- delta_event_fall_prob_mean: 0.004983
- delta_event_energy_prob_mean: -0.004033
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006527
- delta_acoustic_energy_mean: -0.023698
- delta_acoustic_delta_abs_mean: 0.004915
- delta_text_aux_abs_mean: 0.002237

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
