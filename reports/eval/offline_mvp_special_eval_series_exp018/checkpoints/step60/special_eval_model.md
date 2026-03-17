# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 7.886554
- loss_acoustic: 5.302551
- loss_event: 5.082208
- loss_text_aux: 0.131101
- loss_text_aux_effective: 0.131101
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.043762
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.176038
- z_art_delta_abs_mean: 0.001702
- event_prob_mean: 0.476521
- event_presence_prob_mean: 0.586193
- event_delta_prob_mean: 0.441459
- event_rise_prob_mean: 0.487161
- event_fall_prob_mean: 0.452526
- event_energy_prob_mean: 0.560483
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.044481
- acoustic_energy_mean: -3.992632
- acoustic_delta_abs_mean: 0.017179
- text_aux_abs_mean: 0.333289

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.81718
- loss_acoustic: 2.165212
- loss_event: 5.189149
- loss_text_aux: 0.282867
- loss_text_aux_effective: 0.282867
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.178368
- z_art_delta_abs_mean: 0.001025
- event_prob_mean: 0.472231
- event_presence_prob_mean: 0.580308
- event_delta_prob_mean: 0.444929
- event_rise_prob_mean: 0.478518
- event_fall_prob_mean: 0.457287
- event_energy_prob_mean: 0.55446
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.083771
- acoustic_energy_mean: -4.16519
- acoustic_delta_abs_mean: 0.008349
- text_aux_abs_mean: 0.346937

## 对比
- delta_loss_total: -3.069374
- delta_loss_acoustic: -3.137339
- delta_loss_event: 0.106941
- delta_loss_text_aux: 0.151766
- delta_loss_text_aux_effective: 0.151766
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.043762
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.00233
- delta_z_art_delta_abs_mean: -0.000677
- delta_event_prob_mean: -0.00429
- delta_event_presence_prob_mean: -0.005885
- delta_event_delta_prob_mean: 0.00347
- delta_event_rise_prob_mean: -0.008643
- delta_event_fall_prob_mean: 0.004761
- delta_event_energy_prob_mean: -0.006023
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.03929
- delta_acoustic_energy_mean: -0.172558
- delta_acoustic_delta_abs_mean: -0.00883
- delta_text_aux_abs_mean: 0.013648

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
