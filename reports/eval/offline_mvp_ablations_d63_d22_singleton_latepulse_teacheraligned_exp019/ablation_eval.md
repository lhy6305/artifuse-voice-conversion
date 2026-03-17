# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d63_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_teacheraligned_30step_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d63_d22_singleton_latepulse_teacheraligned_exp019/checkpoints/EXP-20260316-019-offline-mvp-d63-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-teacheraligned-30step-calibration.step30.pt

## none
- batch_count: 14
- target.loss_total: 2.432608
- source.loss_total: 2.435188
- target.loss_text_aux_effective: 0.096693
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.070342
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
- target.loss_total: 2.748753
- source.loss_total: 2.783199
- target.loss_text_aux_effective: 0.092678
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.070342
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
- target_acoustic_mae: 0.543398
- source_acoustic_mae: 0.607569
- target_text_aux_mae: 0.047641
- source_text_aux_mae: 0.053337

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.036192
- source.loss_total: 5.879279
- target.loss_text_aux_effective: 0.106437
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.070342
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
- target_acoustic_mae: 1.672334
- source_acoustic_mae: 2.14876
- target_text_aux_mae: 0.104574
- source_text_aux_mae: 0.140917

## 对比
- zero_z_art: {"delta_target_loss_total": 0.316145, "delta_source_loss_total": 0.348011, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": -0.004015, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.543398, "delta_source_acoustic_mae": 0.607569, "delta_target_text_aux_mae": 0.047641, "delta_source_text_aux_mae": 0.053337}
- zero_e_evt: {"delta_target_loss_total": 2.603584, "delta_source_loss_total": 3.444091, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": 0.009744, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.672334, "delta_source_acoustic_mae": 2.14876, "delta_target_text_aux_mae": 0.104574, "delta_source_text_aux_mae": 0.140917}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
