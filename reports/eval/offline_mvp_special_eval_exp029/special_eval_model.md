# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d14_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d14_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_exp029/checkpoints/EXP-20260315-029-offline-mvp-d14-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-late-lr-decay-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.307872
- loss_acoustic: 0.886763
- loss_event: 4.742455
- loss_text_aux: 0.114963
- loss_text_aux_effective: 0.114963
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.050924
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.303815
- z_art_delta_abs_mean: 0.011333
- event_prob_mean: 0.460576
- event_presence_prob_mean: 0.602423
- event_delta_prob_mean: 0.367843
- event_rise_prob_mean: 0.473505
- event_fall_prob_mean: 0.417395
- event_energy_prob_mean: 0.577463
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.815869
- acoustic_energy_mean: -3.077468
- acoustic_delta_abs_mean: 0.037373
- text_aux_abs_mean: 0.213895

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.067379
- loss_acoustic: 0.505156
- loss_event: 5.030228
- loss_text_aux: 0.203303
- loss_text_aux_effective: 0.203303
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.20908
- z_art_delta_abs_mean: 0.008061
- event_prob_mean: 0.448752
- event_presence_prob_mean: 0.571972
- event_delta_prob_mean: 0.382097
- event_rise_prob_mean: 0.452207
- event_fall_prob_mean: 0.436758
- event_energy_prob_mean: 0.552531
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.063118
- acoustic_energy_mean: -4.060768
- acoustic_delta_abs_mean: 0.019105
- text_aux_abs_mean: 0.267046

## 对比
- delta_loss_total: -0.240493
- delta_loss_acoustic: -0.381607
- delta_loss_event: 0.287773
- delta_loss_text_aux: 0.08834
- delta_loss_text_aux_effective: 0.08834
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.050924
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.094735
- delta_z_art_delta_abs_mean: -0.003272
- delta_event_prob_mean: -0.011824
- delta_event_presence_prob_mean: -0.030451
- delta_event_delta_prob_mean: 0.014254
- delta_event_rise_prob_mean: -0.021298
- delta_event_fall_prob_mean: 0.019363
- delta_event_energy_prob_mean: -0.024932
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.247249
- delta_acoustic_energy_mean: -0.9833
- delta_acoustic_delta_abs_mean: -0.018268
- delta_text_aux_abs_mean: 0.053151

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
