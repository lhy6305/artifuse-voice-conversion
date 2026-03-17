# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.848954
- loss_acoustic: 0.474897
- loss_event: 4.645674
- loss_text_aux: 0.11377
- loss_text_aux_effective: 0.11377
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053201
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.351865
- z_art_delta_abs_mean: 0.012307
- event_prob_mean: 0.460555
- event_presence_prob_mean: 0.6241
- event_delta_prob_mean: 0.346037
- event_rise_prob_mean: 0.487914
- event_fall_prob_mean: 0.41626
- event_energy_prob_mean: 0.592151
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.917924
- acoustic_energy_mean: -3.481893
- acoustic_delta_abs_mean: 0.014536
- text_aux_abs_mean: 0.258675

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.260322
- loss_acoustic: 0.707128
- loss_event: 4.99097
- loss_text_aux: 0.251718
- loss_text_aux_effective: 0.251718
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.249457
- z_art_delta_abs_mean: 0.009207
- event_prob_mean: 0.447169
- event_presence_prob_mean: 0.589587
- event_delta_prob_mean: 0.360821
- event_rise_prob_mean: 0.461742
- event_fall_prob_mean: 0.432713
- event_energy_prob_mean: 0.564073
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.130525
- acoustic_energy_mean: -4.329484
- acoustic_delta_abs_mean: 0.011644
- text_aux_abs_mean: 0.310106

## 对比
- delta_loss_total: 0.411368
- delta_loss_acoustic: 0.232231
- delta_loss_event: 0.345296
- delta_loss_text_aux: 0.137948
- delta_loss_text_aux_effective: 0.137948
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053201
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.102408
- delta_z_art_delta_abs_mean: -0.0031
- delta_event_prob_mean: -0.013386
- delta_event_presence_prob_mean: -0.034513
- delta_event_delta_prob_mean: 0.014784
- delta_event_rise_prob_mean: -0.026172
- delta_event_fall_prob_mean: 0.016453
- delta_event_energy_prob_mean: -0.028078
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.212601
- delta_acoustic_energy_mean: -0.847591
- delta_acoustic_delta_abs_mean: -0.002892
- delta_text_aux_abs_mean: 0.051431

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
