# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d5_special_proxy_core_clause_ge4_late_handoff_exp021/checkpoints/EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.810181
- loss_acoustic: 0.449346
- loss_event: 4.618171
- loss_text_aux: 0.112507
- loss_text_aux_effective: 0.112507
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.055458
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.402307
- z_art_delta_abs_mean: 0.012298
- event_prob_mean: 0.459361
- event_presence_prob_mean: 0.639291
- event_delta_prob_mean: 0.323579
- event_rise_prob_mean: 0.491879
- event_fall_prob_mean: 0.407357
- event_energy_prob_mean: 0.608928
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.850725
- acoustic_energy_mean: -3.220041
- acoustic_delta_abs_mean: 0.015743
- text_aux_abs_mean: 0.236996

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.778494
- loss_acoustic: 0.23564
- loss_event: 4.986567
- loss_text_aux: 0.209676
- loss_text_aux_effective: 0.209676
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.30502
- z_art_delta_abs_mean: 0.009544
- event_prob_mean: 0.446973
- event_presence_prob_mean: 0.605982
- event_delta_prob_mean: 0.337101
- event_rise_prob_mean: 0.467549
- event_fall_prob_mean: 0.423476
- event_energy_prob_mean: 0.581915
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.011112
- acoustic_energy_mean: -3.831307
- acoustic_delta_abs_mean: 0.016158
- text_aux_abs_mean: 0.26963

## 对比
- delta_loss_total: -0.031687
- delta_loss_acoustic: -0.213706
- delta_loss_event: 0.368396
- delta_loss_text_aux: 0.097169
- delta_loss_text_aux_effective: 0.097169
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.055458
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.097287
- delta_z_art_delta_abs_mean: -0.002754
- delta_event_prob_mean: -0.012388
- delta_event_presence_prob_mean: -0.033309
- delta_event_delta_prob_mean: 0.013522
- delta_event_rise_prob_mean: -0.02433
- delta_event_fall_prob_mean: 0.016119
- delta_event_energy_prob_mean: -0.027013
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.160387
- delta_acoustic_energy_mean: -0.611266
- delta_acoustic_delta_abs_mean: 0.000415
- delta_text_aux_abs_mean: 0.032634

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
