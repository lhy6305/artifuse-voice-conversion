# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d12_special_proxy_core_clause_ge4_handoff68_zart_influence/checkpoints/EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.976731
- source.loss_total: 3.039038
- target.loss_text_aux_effective: 0.102128
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064365
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
- target.loss_total: 3.442003
- source.loss_total: 3.425027
- target.loss_text_aux_effective: 0.096319
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064365
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.605367
- source_acoustic_mae: 0.826939
- target_text_aux_mae: 0.047776
- source_text_aux_mae: 0.06893

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.290671
- source.loss_total: 4.746973
- target.loss_text_aux_effective: 0.107745
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064365
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 1.472446
- source_acoustic_mae: 1.90078
- target_text_aux_mae: 0.098895
- source_text_aux_mae: 0.140817

## 对比
- zero_z_art: {"delta_target_loss_total": 0.465272, "delta_source_loss_total": 0.385989, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": -0.005809, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.605367, "delta_source_acoustic_mae": 0.826939, "delta_target_text_aux_mae": 0.047776, "delta_source_text_aux_mae": 0.06893}
- zero_e_evt: {"delta_target_loss_total": 2.31394, "delta_source_loss_total": 1.707935, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": 0.005617, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.472446, "delta_source_acoustic_mae": 1.90078, "delta_target_text_aux_mae": 0.098895, "delta_source_text_aux_mae": 0.140817}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
