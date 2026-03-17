# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.310955
- loss_acoustic: 6.584198
- loss_event: 5.326858
- loss_text_aux: 0.249766
- loss_text_aux_effective: 0.249766
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.035818
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.220868
- z_art_delta_abs_mean: 0.001048
- event_prob_mean: 0.492686
- event_presence_prob_mean: 0.559585
- event_delta_prob_mean: 0.533653
- event_rise_prob_mean: 0.468569
- event_fall_prob_mean: 0.521734
- event_energy_prob_mean: 0.516571
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878212
- acoustic_energy_mean: -3.373358
- acoustic_delta_abs_mean: 0.061972
- text_aux_abs_mean: 0.386404

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.208572
- loss_acoustic: 2.457038
- loss_event: 5.362369
- loss_text_aux: 0.35038
- loss_text_aux_effective: 0.35038
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.228573
- z_art_delta_abs_mean: 0.000343
- event_prob_mean: 0.491605
- event_presence_prob_mean: 0.558952
- event_delta_prob_mean: 0.538243
- event_rise_prob_mean: 0.46479
- event_fall_prob_mean: 0.526595
- event_energy_prob_mean: 0.512468
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.884827
- acoustic_energy_mean: -3.397385
- acoustic_delta_abs_mean: 0.066841
- text_aux_abs_mean: 0.388743

## 对比
- delta_loss_total: -4.102383
- delta_loss_acoustic: -4.12716
- delta_loss_event: 0.035511
- delta_loss_text_aux: 0.100614
- delta_loss_text_aux_effective: 0.100614
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.035818
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.007705
- delta_z_art_delta_abs_mean: -0.000705
- delta_event_prob_mean: -0.001081
- delta_event_presence_prob_mean: -0.000633
- delta_event_delta_prob_mean: 0.00459
- delta_event_rise_prob_mean: -0.003779
- delta_event_fall_prob_mean: 0.004861
- delta_event_energy_prob_mean: -0.004103
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006615
- delta_acoustic_energy_mean: -0.024027
- delta_acoustic_delta_abs_mean: 0.004869
- delta_text_aux_abs_mean: 0.002339

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
