# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.823698
- loss_acoustic: 1.345096
- loss_event: 4.866042
- loss_text_aux: 0.111021
- loss_text_aux_effective: 0.111021
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.047964
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.229065
- z_art_delta_abs_mean: 0.008237
- event_prob_mean: 0.464699
- event_presence_prob_mean: 0.587091
- event_delta_prob_mean: 0.397718
- event_rise_prob_mean: 0.475927
- event_fall_prob_mean: 0.428185
- event_energy_prob_mean: 0.563225
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.846247
- acoustic_energy_mean: -3.215937
- acoustic_delta_abs_mean: 0.025076
- text_aux_abs_mean: 0.228105

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.411707
- loss_acoustic: 0.818587
- loss_event: 5.084425
- loss_text_aux: 0.232467
- loss_text_aux_effective: 0.232467
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.166495
- z_art_delta_abs_mean: 0.005518
- event_prob_mean: 0.454552
- event_presence_prob_mean: 0.563915
- event_delta_prob_mean: 0.408799
- event_rise_prob_mean: 0.457464
- event_fall_prob_mean: 0.444702
- event_energy_prob_mean: 0.544203
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.071648
- acoustic_energy_mean: -4.122687
- acoustic_delta_abs_mean: 0.009514
- text_aux_abs_mean: 0.288258

## 对比
- delta_loss_total: -0.411991
- delta_loss_acoustic: -0.526509
- delta_loss_event: 0.218383
- delta_loss_text_aux: 0.121446
- delta_loss_text_aux_effective: 0.121446
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.047964
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.06257
- delta_z_art_delta_abs_mean: -0.002719
- delta_event_prob_mean: -0.010147
- delta_event_presence_prob_mean: -0.023176
- delta_event_delta_prob_mean: 0.011081
- delta_event_rise_prob_mean: -0.018463
- delta_event_fall_prob_mean: 0.016517
- delta_event_energy_prob_mean: -0.019022
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.225401
- delta_acoustic_energy_mean: -0.90675
- delta_acoustic_delta_abs_mean: -0.015562
- delta_text_aux_abs_mean: 0.060153

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
