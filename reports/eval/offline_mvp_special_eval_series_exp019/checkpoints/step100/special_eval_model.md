# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.901056
- loss_acoustic: 0.522073
- loss_event: 4.655784
- loss_text_aux: 0.112459
- loss_text_aux_effective: 0.112459
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053458
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.356964
- z_art_delta_abs_mean: 0.012361
- event_prob_mean: 0.459888
- event_presence_prob_mean: 0.625469
- event_delta_prob_mean: 0.34165
- event_rise_prob_mean: 0.486836
- event_fall_prob_mean: 0.411358
- event_energy_prob_mean: 0.592611
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.876493
- acoustic_energy_mean: -3.312582
- acoustic_delta_abs_mean: 0.017617
- text_aux_abs_mean: 0.240961

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.034262
- loss_acoustic: 0.48203
- loss_event: 4.998231
- loss_text_aux: 0.228691
- loss_text_aux_effective: 0.228691
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.254899
- z_art_delta_abs_mean: 0.009223
- event_prob_mean: 0.447253
- event_presence_prob_mean: 0.592358
- event_delta_prob_mean: 0.357052
- event_rise_prob_mean: 0.461742
- event_fall_prob_mean: 0.429847
- event_energy_prob_mean: 0.565194
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.078679
- acoustic_energy_mean: -4.126376
- acoustic_delta_abs_mean: 0.01298
- text_aux_abs_mean: 0.288116

## 对比
- delta_loss_total: 0.133206
- delta_loss_acoustic: -0.040043
- delta_loss_event: 0.342447
- delta_loss_text_aux: 0.116232
- delta_loss_text_aux_effective: 0.116232
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053458
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.102065
- delta_z_art_delta_abs_mean: -0.003138
- delta_event_prob_mean: -0.012635
- delta_event_presence_prob_mean: -0.033111
- delta_event_delta_prob_mean: 0.015402
- delta_event_rise_prob_mean: -0.025094
- delta_event_fall_prob_mean: 0.018489
- delta_event_energy_prob_mean: -0.027417
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.202186
- delta_acoustic_energy_mean: -0.813794
- delta_acoustic_delta_abs_mean: -0.004637
- delta_text_aux_abs_mean: 0.047155

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
