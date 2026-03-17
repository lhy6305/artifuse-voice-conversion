# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 7.893145
- loss_acoustic: 5.311296
- loss_event: 5.077753
- loss_text_aux: 0.131341
- loss_text_aux_effective: 0.131341
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.043846
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.178061
- z_art_delta_abs_mean: 0.001698
- event_prob_mean: 0.476617
- event_presence_prob_mean: 0.589158
- event_delta_prob_mean: 0.440506
- event_rise_prob_mean: 0.486394
- event_fall_prob_mean: 0.451621
- event_energy_prob_mean: 0.562746
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.044368
- acoustic_energy_mean: -3.992828
- acoustic_delta_abs_mean: 0.016808
- text_aux_abs_mean: 0.335659

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.81578
- loss_acoustic: 2.165303
- loss_event: 5.185966
- loss_text_aux: 0.283363
- loss_text_aux_effective: 0.283363
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.18002
- z_art_delta_abs_mean: 0.001027
- event_prob_mean: 0.472329
- event_presence_prob_mean: 0.583215
- event_delta_prob_mean: 0.444013
- event_rise_prob_mean: 0.477762
- event_fall_prob_mean: 0.456348
- event_energy_prob_mean: 0.556675
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.083281
- acoustic_energy_mean: -4.163641
- acoustic_delta_abs_mean: 0.008019
- text_aux_abs_mean: 0.349282

## 对比
- delta_loss_total: -3.077365
- delta_loss_acoustic: -3.145993
- delta_loss_event: 0.108213
- delta_loss_text_aux: 0.152022
- delta_loss_text_aux_effective: 0.152022
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.043846
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.001959
- delta_z_art_delta_abs_mean: -0.000671
- delta_event_prob_mean: -0.004288
- delta_event_presence_prob_mean: -0.005943
- delta_event_delta_prob_mean: 0.003507
- delta_event_rise_prob_mean: -0.008632
- delta_event_fall_prob_mean: 0.004727
- delta_event_energy_prob_mean: -0.006071
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.038913
- delta_acoustic_energy_mean: -0.170813
- delta_acoustic_delta_abs_mean: -0.008789
- delta_text_aux_abs_mean: 0.013623

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
