# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.395798
- loss_acoustic: 0.971928
- loss_event: 4.746452
- loss_text_aux: 0.116933
- loss_text_aux_effective: 0.116933
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.050285
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.29677
- z_art_delta_abs_mean: 0.012072
- event_prob_mean: 0.461313
- event_presence_prob_mean: 0.597537
- event_delta_prob_mean: 0.377352
- event_rise_prob_mean: 0.47268
- event_fall_prob_mean: 0.419294
- event_energy_prob_mean: 0.570405
- event_presence_peak_ratio: 0.813254
- acoustic_abs_mean: 0.831806
- acoustic_energy_mean: -3.13352
- acoustic_delta_abs_mean: 0.041985
- text_aux_abs_mean: 0.222089

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.322959
- loss_acoustic: 0.754318
- loss_event: 5.033248
- loss_text_aux: 0.226281
- loss_text_aux_effective: 0.226281
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.195206
- z_art_delta_abs_mean: 0.008451
- event_prob_mean: 0.448432
- event_presence_prob_mean: 0.565545
- event_delta_prob_mean: 0.392422
- event_rise_prob_mean: 0.449408
- event_fall_prob_mean: 0.439205
- event_energy_prob_mean: 0.543966
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.107326
- acoustic_energy_mean: -4.251565
- acoustic_delta_abs_mean: 0.021464
- text_aux_abs_mean: 0.284657

## 对比
- delta_loss_total: -0.072839
- delta_loss_acoustic: -0.21761
- delta_loss_event: 0.286796
- delta_loss_text_aux: 0.109348
- delta_loss_text_aux_effective: 0.109348
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.050285
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.101564
- delta_z_art_delta_abs_mean: -0.003621
- delta_event_prob_mean: -0.012881
- delta_event_presence_prob_mean: -0.031992
- delta_event_delta_prob_mean: 0.01507
- delta_event_rise_prob_mean: -0.023272
- delta_event_fall_prob_mean: 0.019911
- delta_event_energy_prob_mean: -0.026439
- delta_event_presence_peak_ratio: 0.136053
- delta_acoustic_abs_mean: 0.27552
- delta_acoustic_energy_mean: -1.118045
- delta_acoustic_delta_abs_mean: -0.020521
- delta_text_aux_abs_mean: 0.062568

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
