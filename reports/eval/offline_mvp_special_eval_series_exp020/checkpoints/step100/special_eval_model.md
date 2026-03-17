# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d4_round1_1_special_proxy_core_clause_ge4_early_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d4_special_proxy_core_clause_ge4_early_handoff_exp020/checkpoints/EXP-20260315-020-offline-mvp-d4-round1-1-special-proxy-core-clause-ge4-early-handoff-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.729466
- loss_acoustic: 0.376292
- loss_event: 4.601682
- loss_text_aux: 0.112627
- loss_text_aux_effective: 0.112627
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.05658
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.438686
- z_art_delta_abs_mean: 0.012506
- event_prob_mean: 0.457817
- event_presence_prob_mean: 0.645713
- event_delta_prob_mean: 0.313085
- event_rise_prob_mean: 0.497064
- event_fall_prob_mean: 0.403758
- event_energy_prob_mean: 0.612655
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.861095
- acoustic_energy_mean: -3.270998
- acoustic_delta_abs_mean: 0.012837
- text_aux_abs_mean: 0.242852

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.727186
- loss_acoustic: 0.185216
- loss_event: 4.981835
- loss_text_aux: 0.215656
- loss_text_aux_effective: 0.215656
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.341772
- z_art_delta_abs_mean: 0.009901
- event_prob_mean: 0.44549
- event_presence_prob_mean: 0.612522
- event_delta_prob_mean: 0.326184
- event_rise_prob_mean: 0.472189
- event_fall_prob_mean: 0.419221
- event_energy_prob_mean: 0.585956
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.998758
- acoustic_energy_mean: -3.789977
- acoustic_delta_abs_mean: 0.014724
- text_aux_abs_mean: 0.270273

## 对比
- delta_loss_total: -0.00228
- delta_loss_acoustic: -0.191076
- delta_loss_event: 0.380153
- delta_loss_text_aux: 0.103029
- delta_loss_text_aux_effective: 0.103029
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.05658
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.096914
- delta_z_art_delta_abs_mean: -0.002605
- delta_event_prob_mean: -0.012327
- delta_event_presence_prob_mean: -0.033191
- delta_event_delta_prob_mean: 0.013099
- delta_event_rise_prob_mean: -0.024875
- delta_event_fall_prob_mean: 0.015463
- delta_event_energy_prob_mean: -0.026699
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.137663
- delta_acoustic_energy_mean: -0.518979
- delta_acoustic_delta_abs_mean: 0.001887
- delta_text_aux_abs_mean: 0.027421

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
