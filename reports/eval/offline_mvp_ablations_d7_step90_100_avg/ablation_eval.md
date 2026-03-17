# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d7_step90_100/d7_step90_100_avg.pt

## none
- batch_count: 14
- target.loss_total: 2.991316
- source.loss_total: 2.846744
- target.loss_text_aux_effective: 0.101866
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.065543
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.560487
- source.loss_total: 3.523908
- target.loss_text_aux_effective: 0.097198
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.065543
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.570382
- source_acoustic_mae: 0.714744
- target_text_aux_mae: 0.044415
- source_text_aux_mae: 0.062161

## zero_e_evt
- batch_count: 14
- target.loss_total: 6.026745
- source.loss_total: 5.990279
- target.loss_text_aux_effective: 0.111453
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.065543
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 1.527999
- source_acoustic_mae: 2.006463
- target_text_aux_mae: 0.102626
- source_text_aux_mae: 0.145672

## 对比
- zero_z_art: {"delta_target_loss_total": 0.569171, "delta_source_loss_total": 0.677164, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": -0.004668, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.570382, "delta_source_acoustic_mae": 0.714744, "delta_target_text_aux_mae": 0.044415, "delta_source_text_aux_mae": 0.062161}
- zero_e_evt: {"delta_target_loss_total": 3.035429, "delta_source_loss_total": 3.143535, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": 0.009587, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.527999, "delta_source_acoustic_mae": 2.006463, "delta_target_text_aux_mae": 0.102626, "delta_source_text_aux_mae": 0.145672}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
