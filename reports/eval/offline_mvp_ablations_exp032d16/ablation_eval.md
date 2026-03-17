# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d16_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_exp032d16/checkpoints/EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.746824
- source.loss_total: 2.813854
- target.loss_text_aux_effective: 0.099454
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.066955
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.280549
- source.loss_total: 3.339078
- target.loss_text_aux_effective: 0.095067
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.066955
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.536234
- source_acoustic_mae: 0.730672
- target_text_aux_mae: 0.046954
- source_text_aux_mae: 0.063966

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.527896
- source.loss_total: 5.699505
- target.loss_text_aux_effective: 0.107435
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.066955
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_challenge_proxy_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_challenge_proxy_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 1.594716
- source_acoustic_mae: 2.050058
- target_text_aux_mae: 0.105967
- source_text_aux_mae: 0.146288

## 对比
- zero_z_art: {"delta_target_loss_total": 0.533725, "delta_source_loss_total": 0.525224, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": -0.004387, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.536234, "delta_source_acoustic_mae": 0.730672, "delta_target_text_aux_mae": 0.046954, "delta_source_text_aux_mae": 0.063966}
- zero_e_evt: {"delta_target_loss_total": 2.781072, "delta_source_loss_total": 2.885651, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_challenge_proxy_profile_aux": 0.0, "delta_source_loss_challenge_proxy_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": 0.007981, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.594716, "delta_source_acoustic_mae": 2.050058, "delta_target_text_aux_mae": 0.105967, "delta_source_text_aux_mae": 0.146288}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
