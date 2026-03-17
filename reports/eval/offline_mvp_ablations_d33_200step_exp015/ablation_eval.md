# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d33_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_fused_hidden_200step_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_200step_exp015/checkpoints/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.step200.pt

## none
- batch_count: 14
- target.loss_total: 2.119283
- source.loss_total: 2.007893
- target.loss_text_aux_effective: 0.089829
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.086629
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- target.loss_formal_special_clause_shape_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- source.loss_formal_special_clause_shape_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 2.830132
- source.loss_total: 2.801349
- target.loss_text_aux_effective: 0.094734
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.086629
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- target.loss_formal_special_clause_shape_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- source.loss_formal_special_clause_shape_aux: 0.0
- target_acoustic_mae: 0.918679
- source_acoustic_mae: 0.972887
- target_text_aux_mae: 0.070146
- source_text_aux_mae: 0.073031

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.089583
- source.loss_total: 4.447897
- target.loss_text_aux_effective: 0.100172
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.086629
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- target.loss_formal_special_clause_shape_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- source.loss_formal_special_clause_shape_aux: 0.0
- target_acoustic_mae: 1.461011
- source_acoustic_mae: 1.643749
- target_text_aux_mae: 0.083893
- source_text_aux_mae: 0.096257

## 对比
- zero_z_art: {"delta_target_loss_total": 0.710849, "delta_source_loss_total": 0.793456, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": 0.004905, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.918679, "delta_source_acoustic_mae": 0.972887, "delta_target_text_aux_mae": 0.070146, "delta_source_text_aux_mae": 0.073031}
- zero_e_evt: {"delta_target_loss_total": 1.9703, "delta_source_loss_total": 2.440004, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": 0.010343, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.461011, "delta_source_acoustic_mae": 1.643749, "delta_target_text_aux_mae": 0.083893, "delta_source_text_aux_mae": 0.096257}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
