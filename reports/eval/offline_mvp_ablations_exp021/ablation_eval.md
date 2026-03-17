# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d5_special_proxy_core_clause_ge4_late_handoff_exp021/checkpoints/EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.831556
- source.loss_total: 2.770884
- target.loss_text_aux_effective: 0.09949
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.067342
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 2.96876
- source.loss_total: 3.44149
- target.loss_text_aux_effective: 0.099898
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.067342
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.717578
- source_acoustic_mae: 0.603755
- target_text_aux_mae: 0.049386
- source_text_aux_mae: 0.038721

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.294447
- source.loss_total: 4.022162
- target.loss_text_aux_effective: 0.101908
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.067342
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.993715
- source_acoustic_mae: 1.220045
- target_text_aux_mae: 0.067721
- source_text_aux_mae: 0.081624

## 对比
- zero_z_art: {"delta_target_loss_total": 0.137204, "delta_source_loss_total": 0.670606, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.000408, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.717578, "delta_source_acoustic_mae": 0.603755, "delta_target_text_aux_mae": 0.049386, "delta_source_text_aux_mae": 0.038721}
- zero_e_evt: {"delta_target_loss_total": 1.462891, "delta_source_loss_total": 1.251278, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002418, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.993715, "delta_source_acoustic_mae": 1.220045, "delta_target_text_aux_mae": 0.067721, "delta_source_text_aux_mae": 0.081624}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
