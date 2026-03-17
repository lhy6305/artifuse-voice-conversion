# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d11_round1_1_special_proxy_core_clause_ge4_mid_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d11_special_proxy_core_clause_ge4_mid_handoff_zart_influence/checkpoints/EXP-20260315-027-offline-mvp-d11-round1-1-special-proxy-core-clause-ge4-mid-handoff-zart-influence-100step-calibration.step80.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.942573
- loss_acoustic: 1.469003
- loss_event: 4.852819
- loss_text_aux: 0.115468
- loss_text_aux_effective: 0.115468
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.048879
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.246372
- z_art_delta_abs_mean: 0.008699
- event_prob_mean: 0.463735
- event_presence_prob_mean: 0.58923
- event_delta_prob_mean: 0.388054
- event_rise_prob_mean: 0.475776
- event_fall_prob_mean: 0.421955
- event_energy_prob_mean: 0.565475
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.777962
- acoustic_energy_mean: -2.935091
- acoustic_delta_abs_mean: 0.0339
- text_aux_abs_mean: 0.196523

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.154144
- loss_acoustic: 0.569704
- loss_event: 5.081232
- loss_text_aux: 0.195419
- loss_text_aux_effective: 0.195419
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- loss_z_art_influence_aux: 0.0
- z_art_abs_mean: 0.178889
- z_art_delta_abs_mean: 0.005925
- event_prob_mean: 0.453665
- event_presence_prob_mean: 0.565471
- event_delta_prob_mean: 0.399221
- event_rise_prob_mean: 0.457688
- event_fall_prob_mean: 0.439896
- event_energy_prob_mean: 0.546179
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.99754
- acoustic_energy_mean: -3.8189
- acoustic_delta_abs_mean: 0.014144
- text_aux_abs_mean: 0.24956

## 对比
- delta_loss_total: -0.788429
- delta_loss_acoustic: -0.899299
- delta_loss_event: 0.228413
- delta_loss_text_aux: 0.079951
- delta_loss_text_aux_effective: 0.079951
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.048879
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_z_art_abs_mean: -0.067483
- delta_z_art_delta_abs_mean: -0.002774
- delta_event_prob_mean: -0.01007
- delta_event_presence_prob_mean: -0.023759
- delta_event_delta_prob_mean: 0.011167
- delta_event_rise_prob_mean: -0.018088
- delta_event_fall_prob_mean: 0.017941
- delta_event_energy_prob_mean: -0.019296
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.219578
- delta_acoustic_energy_mean: -0.883809
- delta_acoustic_delta_abs_mean: -0.019756
- delta_text_aux_abs_mean: 0.053037

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
