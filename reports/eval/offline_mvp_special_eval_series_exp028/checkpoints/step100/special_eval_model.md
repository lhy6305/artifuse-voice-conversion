# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.965061
- loss_acoustic: 0.588007
- loss_event: 4.651395
- loss_text_aux: 0.113376
- loss_text_aux_effective: 0.113376
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.053007
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.349132
- z_art_delta_abs_mean: 0.012661
- event_prob_mean: 0.459185
- event_presence_prob_mean: 0.616303
- event_delta_prob_mean: 0.348917
- event_rise_prob_mean: 0.484306
- event_fall_prob_mean: 0.415554
- event_energy_prob_mean: 0.588149
- event_presence_peak_ratio: 0.822171
- acoustic_abs_mean: 0.875936
- acoustic_energy_mean: -3.312923
- acoustic_delta_abs_mean: 0.019146
- text_aux_abs_mean: 0.248401

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.134631
- loss_acoustic: 0.586416
- loss_event: 4.9901
- loss_text_aux: 0.228517
- loss_text_aux_effective: 0.228517
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.242282
- z_art_delta_abs_mean: 0.009326
- event_prob_mean: 0.445874
- event_presence_prob_mean: 0.580978
- event_delta_prob_mean: 0.364103
- event_rise_prob_mean: 0.459383
- event_fall_prob_mean: 0.434021
- event_energy_prob_mean: 0.559103
- event_presence_peak_ratio: 0.95316
- acoustic_abs_mean: 1.096192
- acoustic_energy_mean: -4.188326
- acoustic_delta_abs_mean: 0.01384
- text_aux_abs_mean: 0.298983

## 对比
- delta_loss_total: 0.16957
- delta_loss_acoustic: -0.001591
- delta_loss_event: 0.338705
- delta_loss_text_aux: 0.115141
- delta_loss_text_aux_effective: 0.115141
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.053007
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.10685
- delta_z_art_delta_abs_mean: -0.003335
- delta_event_prob_mean: -0.013311
- delta_event_presence_prob_mean: -0.035325
- delta_event_delta_prob_mean: 0.015186
- delta_event_rise_prob_mean: -0.024923
- delta_event_fall_prob_mean: 0.018467
- delta_event_energy_prob_mean: -0.029046
- delta_event_presence_peak_ratio: 0.130989
- delta_acoustic_abs_mean: 0.220256
- delta_acoustic_energy_mean: -0.875403
- delta_acoustic_delta_abs_mean: -0.005306
- delta_text_aux_abs_mean: 0.050582

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
