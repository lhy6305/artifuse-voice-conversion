# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step70.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 5.959069
- loss_acoustic: 3.431411
- loss_event: 4.973392
- loss_text_aux: 0.108435
- loss_text_aux_effective: 0.108435
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.046334
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.186406
- z_art_delta_abs_mean: 0.003822
- event_prob_mean: 0.471096
- event_presence_prob_mean: 0.59072
- event_delta_prob_mean: 0.412358
- event_rise_prob_mean: 0.489659
- event_fall_prob_mean: 0.437927
- event_energy_prob_mean: 0.567558
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.917887
- acoustic_energy_mean: -3.580308
- acoustic_delta_abs_mean: 0.013452
- text_aux_abs_mean: 0.276939

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 4.138526
- loss_acoustic: 1.520232
- loss_event: 5.132279
- loss_text_aux: 0.250492
- loss_text_aux_effective: 0.250492
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.164791
- z_art_delta_abs_mean: 0.00257
- event_prob_mean: 0.46421
- event_presence_prob_mean: 0.577555
- event_delta_prob_mean: 0.418259
- event_rise_prob_mean: 0.47634
- event_fall_prob_mean: 0.4471
- event_energy_prob_mean: 0.556725
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.012897
- acoustic_energy_mean: -3.986476
- acoustic_delta_abs_mean: 0.013072
- text_aux_abs_mean: 0.30619

## 对比
- delta_loss_total: -1.820543
- delta_loss_acoustic: -1.911179
- delta_loss_event: 0.158887
- delta_loss_text_aux: 0.142057
- delta_loss_text_aux_effective: 0.142057
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.046334
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.021615
- delta_z_art_delta_abs_mean: -0.001252
- delta_event_prob_mean: -0.006886
- delta_event_presence_prob_mean: -0.013165
- delta_event_delta_prob_mean: 0.005901
- delta_event_rise_prob_mean: -0.013319
- delta_event_fall_prob_mean: 0.009173
- delta_event_energy_prob_mean: -0.010833
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.09501
- delta_acoustic_energy_mean: -0.406168
- delta_acoustic_delta_abs_mean: -0.00038
- delta_text_aux_abs_mean: 0.029251

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
