# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d7_step90_100/d7_step90_100_avg.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.978639
- loss_acoustic: 0.599304
- loss_event: 4.654841
- loss_text_aux: 0.114349
- loss_text_aux_effective: 0.114349
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053976
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.377119
- z_art_delta_abs_mean: 0.01269
- event_prob_mean: 0.458389
- event_presence_prob_mean: 0.623188
- event_delta_prob_mean: 0.339091
- event_rise_prob_mean: 0.483878
- event_fall_prob_mean: 0.407575
- event_energy_prob_mean: 0.593255
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.834135
- acoustic_energy_mean: -3.151747
- acoustic_delta_abs_mean: 0.025193
- text_aux_abs_mean: 0.23285

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.880608
- loss_acoustic: 0.331712
- loss_event: 4.996768
- loss_text_aux: 0.2144
- loss_text_aux_effective: 0.2144
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.273659
- z_art_delta_abs_mean: 0.00954
- event_prob_mean: 0.445777
- event_presence_prob_mean: 0.5896
- event_delta_prob_mean: 0.353482
- event_rise_prob_mean: 0.459914
- event_fall_prob_mean: 0.4258
- event_energy_prob_mean: 0.566092
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.029242
- acoustic_energy_mean: -3.897219
- acoustic_delta_abs_mean: 0.018556
- text_aux_abs_mean: 0.272675

## 对比
- delta_loss_total: -0.098031
- delta_loss_acoustic: -0.267592
- delta_loss_event: 0.341927
- delta_loss_text_aux: 0.100051
- delta_loss_text_aux_effective: 0.100051
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053976
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.10346
- delta_z_art_delta_abs_mean: -0.00315
- delta_event_prob_mean: -0.012612
- delta_event_presence_prob_mean: -0.033588
- delta_event_delta_prob_mean: 0.014391
- delta_event_rise_prob_mean: -0.023964
- delta_event_fall_prob_mean: 0.018225
- delta_event_energy_prob_mean: -0.027163
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.195107
- delta_acoustic_energy_mean: -0.745472
- delta_acoustic_delta_abs_mean: -0.006637
- delta_text_aux_abs_mean: 0.039825

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
