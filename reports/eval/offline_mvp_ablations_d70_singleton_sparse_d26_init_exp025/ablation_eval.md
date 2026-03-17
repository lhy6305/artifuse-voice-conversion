# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d70_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d70_singleton_sparse_d26_init_exp025/checkpoints/EXP-20260316-025-offline-mvp-d70-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.step20.pt

## none
- batch_count: 14
- target.loss_total: 2.408452
- source.loss_total: 2.356441
- target.loss_text_aux_effective: 0.095245
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.072458
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
- target.loss_total: 2.774017
- source.loss_total: 2.793285
- target.loss_text_aux_effective: 0.092779
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.072458
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
- target_acoustic_mae: 0.503935
- source_acoustic_mae: 0.533365
- target_text_aux_mae: 0.045738
- source_text_aux_mae: 0.048966

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.350059
- source.loss_total: 6.417534
- target.loss_text_aux_effective: 0.107933
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.072458
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
- target_acoustic_mae: 1.60932
- source_acoustic_mae: 2.061046
- target_text_aux_mae: 0.097824
- source_text_aux_mae: 0.130476

## 对比
- zero_z_art: {"delta_target_loss_total": 0.365565, "delta_source_loss_total": 0.436844, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": -0.002466, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.503935, "delta_source_acoustic_mae": 0.533365, "delta_target_text_aux_mae": 0.045738, "delta_source_text_aux_mae": 0.048966}
- zero_e_evt: {"delta_target_loss_total": 2.941607, "delta_source_loss_total": 4.061093, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_formal_special_clause_shape_aux": 0.0, "delta_source_loss_formal_special_clause_shape_aux": 0.0, "delta_target_loss_text_aux_effective": 0.012688, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.60932, "delta_source_acoustic_mae": 2.061046, "delta_target_text_aux_mae": 0.097824, "delta_source_text_aux_mae": 0.130476}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
