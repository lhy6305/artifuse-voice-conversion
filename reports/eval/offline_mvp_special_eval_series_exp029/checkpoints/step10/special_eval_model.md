# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d14_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d14_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_exp029/checkpoints/EXP-20260315-029-offline-mvp-d14-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-late-lr-decay-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 19.341937
- loss_acoustic: 16.565844
- loss_event: 5.444352
- loss_text_aux: 0.202867
- loss_text_aux_effective: 0.202867
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036788
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.085778
- z_art_delta_abs_mean: 0.000586
- event_prob_mean: 0.509482
- event_presence_prob_mean: 0.525984
- event_delta_prob_mean: 0.527266
- event_rise_prob_mean: 0.527741
- event_fall_prob_mean: 0.523873
- event_energy_prob_mean: 0.525109
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198433
- acoustic_energy_mean: -0.487499
- acoustic_delta_abs_mean: 0.13714
- text_aux_abs_mean: 0.115242

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.630081
- loss_acoustic: 12.869575
- loss_event: 5.470818
- loss_text_aux: 0.124151
- loss_text_aux_effective: 0.124151
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.084865
- z_art_delta_abs_mean: 0.000334
- event_prob_mean: 0.509185
- event_presence_prob_mean: 0.525209
- event_delta_prob_mean: 0.529031
- event_rise_prob_mean: 0.52859
- event_fall_prob_mean: 0.526498
- event_energy_prob_mean: 0.522896
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.198877
- acoustic_energy_mean: -0.48949
- acoustic_delta_abs_mean: 0.136654
- text_aux_abs_mean: 0.115211

## 对比
- delta_loss_total: -3.711856
- delta_loss_acoustic: -3.696269
- delta_loss_event: 0.026466
- delta_loss_text_aux: -0.078716
- delta_loss_text_aux_effective: -0.078716
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036788
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.000913
- delta_z_art_delta_abs_mean: -0.000252
- delta_event_prob_mean: -0.000297
- delta_event_presence_prob_mean: -0.000775
- delta_event_delta_prob_mean: 0.001765
- delta_event_rise_prob_mean: 0.000849
- delta_event_fall_prob_mean: 0.002625
- delta_event_energy_prob_mean: -0.002213
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.000444
- delta_acoustic_energy_mean: -0.001991
- delta_acoustic_delta_abs_mean: -0.000486
- delta_text_aux_abs_mean: -3.1e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
