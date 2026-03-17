# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d1_special_proxy_core_multiterm_exp017/checkpoints/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.865467
- source.loss_total: 3.136504
- target.loss_text_aux_effective: 0.103633
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064695
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
- target.loss_total: 3.137314
- source.loss_total: 3.910821
- target.loss_text_aux_effective: 0.106148
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064695
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.713714
- source_acoustic_mae: 0.496391
- target_text_aux_mae: 0.045135
- source_text_aux_mae: 0.026443

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.727557
- source.loss_total: 3.074371
- target.loss_text_aux_effective: 0.101215
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064695
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- target_acoustic_mae: 0.97856
- source_acoustic_mae: 1.133231
- target_text_aux_mae: 0.070592
- source_text_aux_mae: 0.078723

## 对比
- zero_z_art: {"delta_target_loss_total": 0.271847, "delta_source_loss_total": 0.774317, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002515, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.713714, "delta_source_acoustic_mae": 0.496391, "delta_target_text_aux_mae": 0.045135, "delta_source_text_aux_mae": 0.026443}
- zero_e_evt: {"delta_target_loss_total": 0.86209, "delta_source_loss_total": -0.062133, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_text_aux_effective": -0.002418, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.97856, "delta_source_acoustic_mae": 1.133231, "delta_target_text_aux_mae": 0.070592, "delta_source_text_aux_mae": 0.078723}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
