# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.821265
- loss_acoustic: 1.340331
- loss_event: 4.87073
- loss_text_aux: 0.111143
- loss_text_aux_effective: 0.111143
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.047899
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.226274
- z_art_delta_abs_mean: 0.008219
- event_prob_mean: 0.464741
- event_presence_prob_mean: 0.585249
- event_delta_prob_mean: 0.398745
- event_rise_prob_mean: 0.476601
- event_fall_prob_mean: 0.428114
- event_energy_prob_mean: 0.561357
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.846131
- acoustic_energy_mean: -3.214269
- acoustic_delta_abs_mean: 0.02292
- text_aux_abs_mean: 0.226767

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.413255
- loss_acoustic: 0.81875
- loss_event: 5.087374
- loss_text_aux: 0.232071
- loss_text_aux_effective: 0.232071
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.164348
- z_art_delta_abs_mean: 0.005506
- event_prob_mean: 0.45455
- event_presence_prob_mean: 0.562176
- event_delta_prob_mean: 0.409716
- event_rise_prob_mean: 0.457933
- event_fall_prob_mean: 0.444684
- event_energy_prob_mean: 0.542583
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.0727
- acoustic_energy_mean: -4.125037
- acoustic_delta_abs_mean: 0.008895
- text_aux_abs_mean: 0.286912

## 对比
- delta_loss_total: -0.40801
- delta_loss_acoustic: -0.521581
- delta_loss_event: 0.216644
- delta_loss_text_aux: 0.120928
- delta_loss_text_aux_effective: 0.120928
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.047899
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.061926
- delta_z_art_delta_abs_mean: -0.002713
- delta_event_prob_mean: -0.010191
- delta_event_presence_prob_mean: -0.023073
- delta_event_delta_prob_mean: 0.010971
- delta_event_rise_prob_mean: -0.018668
- delta_event_fall_prob_mean: 0.01657
- delta_event_energy_prob_mean: -0.018774
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.226569
- delta_acoustic_energy_mean: -0.910768
- delta_acoustic_delta_abs_mean: -0.014025
- delta_text_aux_abs_mean: 0.060145

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
