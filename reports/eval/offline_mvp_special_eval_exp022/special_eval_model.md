# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/checkpoints/EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.728306
- loss_acoustic: 0.375369
- loss_event: 4.600978
- loss_text_aux: 0.112644
- loss_text_aux_effective: 0.112644
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0566
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.441453
- z_art_delta_abs_mean: 0.012637
- event_prob_mean: 0.457821
- event_presence_prob_mean: 0.646045
- event_delta_prob_mean: 0.312981
- event_rise_prob_mean: 0.497217
- event_fall_prob_mean: 0.403601
- event_energy_prob_mean: 0.612651
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.861013
- acoustic_energy_mean: -3.270997
- acoustic_delta_abs_mean: 0.012798
- text_aux_abs_mean: 0.242864

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.726698
- loss_acoustic: 0.184816
- loss_event: 4.981524
- loss_text_aux: 0.215622
- loss_text_aux_effective: 0.215622
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.343446
- z_art_delta_abs_mean: 0.009995
- event_prob_mean: 0.44547
- event_presence_prob_mean: 0.612769
- event_delta_prob_mean: 0.326103
- event_rise_prob_mean: 0.472259
- event_fall_prob_mean: 0.419127
- event_energy_prob_mean: 0.585911
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998459
- acoustic_energy_mean: -3.78903
- acoustic_delta_abs_mean: 0.014681
- text_aux_abs_mean: 0.27021

## 对比
- delta_loss_total: -0.001608
- delta_loss_acoustic: -0.190553
- delta_loss_event: 0.380546
- delta_loss_text_aux: 0.102978
- delta_loss_text_aux_effective: 0.102978
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.0566
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.098007
- delta_z_art_delta_abs_mean: -0.002642
- delta_event_prob_mean: -0.012351
- delta_event_presence_prob_mean: -0.033276
- delta_event_delta_prob_mean: 0.013122
- delta_event_rise_prob_mean: -0.024958
- delta_event_fall_prob_mean: 0.015526
- delta_event_energy_prob_mean: -0.02674
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137446
- delta_acoustic_energy_mean: -0.518033
- delta_acoustic_delta_abs_mean: 0.001883
- delta_text_aux_abs_mean: 0.027346

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
