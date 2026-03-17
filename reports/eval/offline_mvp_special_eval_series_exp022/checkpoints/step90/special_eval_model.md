# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/checkpoints/EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.428308
- loss_acoustic: 1.016983
- loss_event: 4.718894
- loss_text_aux: 0.117995
- loss_text_aux_effective: 0.117995
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.05155
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.329926
- z_art_delta_abs_mean: 0.012796
- event_prob_mean: 0.4595
- event_presence_prob_mean: 0.602753
- event_delta_prob_mean: 0.364319
- event_rise_prob_mean: 0.472753
- event_fall_prob_mean: 0.41294
- event_energy_prob_mean: 0.576186
- event_presence_peak_ratio: 0.814568
- acoustic_abs_mean: 0.802271
- acoustic_energy_mean: -2.997815
- acoustic_delta_abs_mean: 0.045182
- text_aux_abs_mean: 0.223024

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.084034
- loss_acoustic: 0.523098
- loss_event: 5.022273
- loss_text_aux: 0.212543
- loss_text_aux_effective: 0.212543
- loss_text_aux_structural: 0.0
- loss_text_aux_lexical: 0.0
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- loss_punctuation_profile_aux: 0.0
- z_art_abs_mean: 0.221249
- z_art_delta_abs_mean: 0.009113
- event_prob_mean: 0.446871
- event_presence_prob_mean: 0.569807
- event_delta_prob_mean: 0.379763
- event_rise_prob_mean: 0.45008
- event_fall_prob_mean: 0.43402
- event_energy_prob_mean: 0.549171
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.056441
- acoustic_energy_mean: -3.999069
- acoustic_delta_abs_mean: 0.024119
- text_aux_abs_mean: 0.27486

## 对比
- delta_loss_total: -0.344274
- delta_loss_acoustic: -0.493885
- delta_loss_event: 0.303379
- delta_loss_text_aux: 0.094548
- delta_loss_text_aux_effective: 0.094548
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_clause_transition_aux: -0.05155
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_z_art_abs_mean: -0.108677
- delta_z_art_delta_abs_mean: -0.003683
- delta_event_prob_mean: -0.012629
- delta_event_presence_prob_mean: -0.032946
- delta_event_delta_prob_mean: 0.015444
- delta_event_rise_prob_mean: -0.022673
- delta_event_fall_prob_mean: 0.02108
- delta_event_energy_prob_mean: -0.027015
- delta_event_presence_peak_ratio: 0.134739
- delta_acoustic_abs_mean: 0.25417
- delta_acoustic_energy_mean: -1.001254
- delta_acoustic_delta_abs_mean: -0.021063
- delta_text_aux_abs_mean: 0.051836

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
