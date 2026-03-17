# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.73012
- loss_acoustic: 0.376915
- loss_event: 4.60174
- loss_text_aux: 0.112638
- loss_text_aux_effective: 0.112638
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.05658
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.438523
- z_art_delta_abs_mean: 0.012505
- event_prob_mean: 0.457832
- event_presence_prob_mean: 0.645737
- event_delta_prob_mean: 0.313073
- event_rise_prob_mean: 0.497074
- event_fall_prob_mean: 0.403766
- event_energy_prob_mean: 0.61269
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.860865
- acoustic_energy_mean: -3.270091
- acoustic_delta_abs_mean: 0.01286
- text_aux_abs_mean: 0.242851

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.726989
- loss_acoustic: 0.184993
- loss_event: 4.981897
- loss_text_aux: 0.215636
- loss_text_aux_effective: 0.215636
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.341614
- z_art_delta_abs_mean: 0.0099
- event_prob_mean: 0.445506
- event_presence_prob_mean: 0.612554
- event_delta_prob_mean: 0.326165
- event_rise_prob_mean: 0.472205
- event_fall_prob_mean: 0.419224
- event_energy_prob_mean: 0.585996
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998492
- acoustic_energy_mean: -3.788836
- acoustic_delta_abs_mean: 0.014784
- text_aux_abs_mean: 0.270248

## 对比
- delta_loss_total: -0.003131
- delta_loss_acoustic: -0.191922
- delta_loss_event: 0.380157
- delta_loss_text_aux: 0.102998
- delta_loss_text_aux_effective: 0.102998
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.05658
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.096909
- delta_z_art_delta_abs_mean: -0.002605
- delta_event_prob_mean: -0.012326
- delta_event_presence_prob_mean: -0.033183
- delta_event_delta_prob_mean: 0.013092
- delta_event_rise_prob_mean: -0.024869
- delta_event_fall_prob_mean: 0.015458
- delta_event_energy_prob_mean: -0.026694
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137627
- delta_acoustic_energy_mean: -0.518745
- delta_acoustic_delta_abs_mean: 0.001924
- delta_text_aux_abs_mean: 0.027397

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
