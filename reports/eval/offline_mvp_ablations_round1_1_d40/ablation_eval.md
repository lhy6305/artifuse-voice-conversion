# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d40_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_20step_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d40_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_exp057/checkpoints/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.step20.pt

## none
- batch_count: 14
- target.loss_total: 2.506982
- source.loss_total: 2.487728
- target.loss_text_aux_effective: 0.09742
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.071001
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 2.938016
- source.loss_total: 2.983326
- target.loss_text_aux_effective: 0.093182
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.071001
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.495299
- source_acoustic_mae: 0.580919
- target_text_aux_mae: 0.045259
- source_text_aux_mae: 0.05273

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.609378
- source.loss_total: 6.533174
- target.loss_text_aux_effective: 0.106407
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.071001
- target.loss_structural_clause_transition_aux: 0.0
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_structural_clause_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_structural_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_structural_clause_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 1.664791
- source_acoustic_mae: 2.16011
- target_text_aux_mae: 0.110889
- source_text_aux_mae: 0.152574

## 对比
- zero_z_art: {"delta_target_loss_total": 0.431034, "delta_source_loss_total": 0.495598, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": -0.004238, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.495299, "delta_source_acoustic_mae": 0.580919, "delta_target_text_aux_mae": 0.045259, "delta_source_text_aux_mae": 0.05273}
- zero_e_evt: {"delta_target_loss_total": 3.102396, "delta_source_loss_total": 4.045446, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_structural_clause_transition_aux": 0.0, "delta_source_loss_structural_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_structural_clause_profile_aux": 0.0, "delta_source_loss_structural_clause_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": 0.008987, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.664791, "delta_source_acoustic_mae": 2.16011, "delta_target_text_aux_mae": 0.110889, "delta_source_text_aux_mae": 0.152574}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
