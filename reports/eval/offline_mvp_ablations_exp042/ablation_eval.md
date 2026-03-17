# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.923236
- source.loss_total: 3.138425
- target.loss_text_aux_effective: 0.094723
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.101738
- target.loss_text_aux_lexical: 0.083498
- target.loss_clause_transition_aux: 0.064456
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.011974
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.101895
- source.loss_total: 3.889366
- target.loss_text_aux_effective: 0.092183
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.100831
- target.loss_text_aux_lexical: 0.078345
- target.loss_clause_transition_aux: 0.064456
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.011974
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.738602
- source_acoustic_mae: 0.502342
- target_text_aux_mae: 0.034981
- source_text_aux_mae: 0.023159

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.871499
- source.loss_total: 3.079153
- target.loss_text_aux_effective: 0.097681
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.103469
- target.loss_text_aux_lexical: 0.088419
- target.loss_clause_transition_aux: 0.064456
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.011974
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 1.004026
- source_acoustic_mae: 1.170813
- target_text_aux_mae: 0.061897
- source_text_aux_mae: 0.080872

## 对比
- zero_z_art: {"delta_target_loss_total": 0.178659, "delta_source_loss_total": 0.750941, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": -0.00254, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": -0.000907, "delta_target_loss_text_aux_lexical": -0.005153, "delta_target_acoustic_mae": 0.738602, "delta_source_acoustic_mae": 0.502342, "delta_target_text_aux_mae": 0.034981, "delta_source_text_aux_mae": 0.023159}
- zero_e_evt: {"delta_target_loss_total": 0.948263, "delta_source_loss_total": -0.059272, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002958, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.001731, "delta_target_loss_text_aux_lexical": 0.004921, "delta_target_acoustic_mae": 1.004026, "delta_source_acoustic_mae": 1.170813, "delta_target_text_aux_mae": 0.061897, "delta_source_text_aux_mae": 0.080872}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
