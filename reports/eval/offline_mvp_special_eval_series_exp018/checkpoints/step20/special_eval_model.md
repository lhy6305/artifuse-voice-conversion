# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d2_round1_1_special_proxy_core_question_exclaim_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d2_special_proxy_core_question_exclaim_exp018/checkpoints/EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 15.591495
- loss_acoustic: 12.83424
- loss_event: 5.409663
- loss_text_aux: 0.196228
- loss_text_aux_effective: 0.196228
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.036187
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.115212
- z_art_delta_abs_mean: 0.000641
- event_prob_mean: 0.507355
- event_presence_prob_mean: 0.542024
- event_delta_prob_mean: 0.527981
- event_rise_prob_mean: 0.512741
- event_fall_prob_mean: 0.528649
- event_energy_prob_mean: 0.523695
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.373304
- acoustic_energy_mean: -1.145259
- acoustic_delta_abs_mean: 0.153213
- text_aux_abs_mean: 0.184933

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.773216
- loss_acoustic: 9.022866
- loss_event: 5.442155
- loss_text_aux: 0.145102
- loss_text_aux_effective: 0.145102
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.117698
- z_art_delta_abs_mean: 0.000315
- event_prob_mean: 0.506861
- event_presence_prob_mean: 0.541289
- event_delta_prob_mean: 0.530079
- event_rise_prob_mean: 0.51234
- event_fall_prob_mean: 0.53231
- event_energy_prob_mean: 0.520882
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.375348
- acoustic_energy_mean: -1.152821
- acoustic_delta_abs_mean: 0.152476
- text_aux_abs_mean: 0.185987

## 对比
- delta_loss_total: -3.818279
- delta_loss_acoustic: -3.811374
- delta_loss_event: 0.032492
- delta_loss_text_aux: -0.051126
- delta_loss_text_aux_effective: -0.051126
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.036187
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: 0.002486
- delta_z_art_delta_abs_mean: -0.000326
- delta_event_prob_mean: -0.000494
- delta_event_presence_prob_mean: -0.000735
- delta_event_delta_prob_mean: 0.002098
- delta_event_rise_prob_mean: -0.000401
- delta_event_fall_prob_mean: 0.003661
- delta_event_energy_prob_mean: -0.002813
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002044
- delta_acoustic_energy_mean: -0.007562
- delta_acoustic_delta_abs_mean: -0.000737
- delta_text_aux_abs_mean: 0.001054

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
