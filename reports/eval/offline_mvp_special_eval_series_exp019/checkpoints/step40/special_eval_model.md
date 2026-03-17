# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.317741
- loss_acoustic: 6.592417
- loss_event: 5.324613
- loss_text_aux: 0.248491
- loss_text_aux_effective: 0.248491
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0357
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.221583
- z_art_delta_abs_mean: 0.001031
- event_prob_mean: 0.493227
- event_presence_prob_mean: 0.562814
- event_delta_prob_mean: 0.534003
- event_rise_prob_mean: 0.466762
- event_fall_prob_mean: 0.522025
- event_energy_prob_mean: 0.519439
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.876092
- acoustic_energy_mean: -3.375092
- acoustic_delta_abs_mean: 0.067069
- text_aux_abs_mean: 0.390786

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.211399
- loss_acoustic: 2.459666
- loss_event: 5.360599
- loss_text_aux: 0.355813
- loss_text_aux_effective: 0.355813
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.229176
- z_art_delta_abs_mean: 0.000339
- event_prob_mean: 0.492196
- event_presence_prob_mean: 0.562192
- event_delta_prob_mean: 0.538694
- event_rise_prob_mean: 0.462931
- event_fall_prob_mean: 0.527071
- event_energy_prob_mean: 0.515452
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.882378
- acoustic_energy_mean: -3.398294
- acoustic_delta_abs_mean: 0.071957
- text_aux_abs_mean: 0.393062

## 对比
- delta_loss_total: -4.106342
- delta_loss_acoustic: -4.132751
- delta_loss_event: 0.035986
- delta_loss_text_aux: 0.107322
- delta_loss_text_aux_effective: 0.107322
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.0357
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.007593
- delta_z_art_delta_abs_mean: -0.000692
- delta_event_prob_mean: -0.001031
- delta_event_presence_prob_mean: -0.000622
- delta_event_delta_prob_mean: 0.004691
- delta_event_rise_prob_mean: -0.003831
- delta_event_fall_prob_mean: 0.005046
- delta_event_energy_prob_mean: -0.003987
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006286
- delta_acoustic_energy_mean: -0.023202
- delta_acoustic_delta_abs_mean: 0.004888
- delta_text_aux_abs_mean: 0.002276

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
