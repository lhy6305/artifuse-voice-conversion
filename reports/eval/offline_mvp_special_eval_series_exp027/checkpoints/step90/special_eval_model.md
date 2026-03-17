# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d11_round1_1_special_proxy_core_clause_ge4_mid_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d11_special_proxy_core_clause_ge4_mid_handoff_zart_influence/checkpoints/EXP-20260315-027-offline-mvp-d11-round1-1-special-proxy-core-clause-ge4-mid-handoff-zart-influence-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.472929
- loss_acoustic: 1.058069
- loss_event: 4.726789
- loss_text_aux: 0.118121
- loss_text_aux_effective: 0.118121
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.051096
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.315357
- z_art_delta_abs_mean: 0.012447
- event_prob_mean: 0.459795
- event_presence_prob_mean: 0.599916
- event_delta_prob_mean: 0.367637
- event_rise_prob_mean: 0.471078
- event_fall_prob_mean: 0.416796
- event_energy_prob_mean: 0.575032
- event_presence_peak_ratio: 0.809885
- acoustic_abs_mean: 0.795917
- acoustic_energy_mean: -2.980317
- acoustic_delta_abs_mean: 0.045982
- text_aux_abs_mean: 0.221537

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.091949
- loss_acoustic: 0.530737
- loss_event: 5.02435
- loss_text_aux: 0.210006
- loss_text_aux_effective: 0.210006
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.209655
- z_art_delta_abs_mean: 0.008795
- event_prob_mean: 0.447225
- event_presence_prob_mean: 0.567377
- event_delta_prob_mean: 0.382827
- event_rise_prob_mean: 0.448805
- event_fall_prob_mean: 0.437939
- event_energy_prob_mean: 0.548128
- event_presence_peak_ratio: 0.948429
- acoustic_abs_mean: 1.053712
- acoustic_energy_mean: -4.011018
- acoustic_delta_abs_mean: 0.023888
- text_aux_abs_mean: 0.275656

## 对比
- delta_loss_total: -0.38098
- delta_loss_acoustic: -0.527332
- delta_loss_event: 0.297561
- delta_loss_text_aux: 0.091885
- delta_loss_text_aux_effective: 0.091885
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.051096
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.105702
- delta_z_art_delta_abs_mean: -0.003652
- delta_event_prob_mean: -0.01257
- delta_event_presence_prob_mean: -0.032539
- delta_event_delta_prob_mean: 0.01519
- delta_event_rise_prob_mean: -0.022273
- delta_event_fall_prob_mean: 0.021143
- delta_event_energy_prob_mean: -0.026904
- delta_event_presence_peak_ratio: 0.138544
- delta_acoustic_abs_mean: 0.257795
- delta_acoustic_energy_mean: -1.030701
- delta_acoustic_delta_abs_mean: -0.022094
- delta_text_aux_abs_mean: 0.054119

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
