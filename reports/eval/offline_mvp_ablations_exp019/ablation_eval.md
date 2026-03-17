# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d3_round1_1_special_proxy_core_clause_ge4_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d3_special_proxy_core_clause_ge4_exp019/checkpoints/EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.919729
- source.loss_total: 2.99398
- target.loss_text_aux_effective: 0.099881
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064913
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
- target.loss_total: 3.099137
- source.loss_total: 3.710536
- target.loss_text_aux_effective: 0.100105
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064913
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.7097
- source_acoustic_mae: 0.499686
- target_text_aux_mae: 0.045422
- source_text_aux_mae: 0.027603

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.055624
- source.loss_total: 3.390446
- target.loss_text_aux_effective: 0.101165
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064913
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.966065
- source_acoustic_mae: 1.138009
- target_text_aux_mae: 0.064797
- source_text_aux_mae: 0.074552

## 对比
- zero_z_art: {"delta_target_loss_total": 0.179408, "delta_source_loss_total": 0.716556, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.000224, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.7097, "delta_source_acoustic_mae": 0.499686, "delta_target_text_aux_mae": 0.045422, "delta_source_text_aux_mae": 0.027603}
- zero_e_evt: {"delta_target_loss_total": 1.135895, "delta_source_loss_total": 0.396466, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.001284, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.966065, "delta_source_acoustic_mae": 1.138009, "delta_target_text_aux_mae": 0.064797, "delta_source_text_aux_mae": 0.074552}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
