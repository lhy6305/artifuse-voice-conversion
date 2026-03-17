# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d10_step90_100/d10_step90_100_avg.pt

## none
- batch_count: 14
- target.loss_total: 3.043907
- source.loss_total: 2.936844
- target.loss_text_aux_effective: 0.099788
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064627
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
- target.loss_total: 3.635317
- source.loss_total: 3.603492
- target.loss_text_aux_effective: 0.096059
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064627
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 0.588088
- source_acoustic_mae: 0.761483
- target_text_aux_mae: 0.044839
- source_text_aux_mae: 0.063655

## zero_e_evt
- batch_count: 14
- target.loss_total: 5.902281
- source.loss_total: 5.601555
- target.loss_text_aux_effective: 0.110219
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.0
- target.loss_text_aux_lexical: 0.0
- target.loss_clause_transition_aux: 0.064627
- target.loss_boundary_contrast_aux: 0.0
- target.loss_punctuation_profile_aux: 0.0
- target.loss_z_art_influence_aux: 0.0
- source.loss_clause_transition_aux: 0.0
- source.loss_boundary_contrast_aux: 0.0
- source.loss_punctuation_profile_aux: 0.0
- source.loss_z_art_influence_aux: 0.0
- target_acoustic_mae: 1.499107
- source_acoustic_mae: 1.933303
- target_text_aux_mae: 0.097038
- source_text_aux_mae: 0.136171

## 对比
- zero_z_art: {"delta_target_loss_total": 0.59141, "delta_source_loss_total": 0.666648, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": -0.003729, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 0.588088, "delta_source_acoustic_mae": 0.761483, "delta_target_text_aux_mae": 0.044839, "delta_source_text_aux_mae": 0.063655}
- zero_e_evt: {"delta_target_loss_total": 2.858374, "delta_source_loss_total": 2.664711, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_boundary_contrast_aux": 0.0, "delta_source_loss_boundary_contrast_aux": 0.0, "delta_target_loss_punctuation_profile_aux": 0.0, "delta_source_loss_punctuation_profile_aux": 0.0, "delta_target_loss_z_art_influence_aux": 0.0, "delta_source_loss_z_art_influence_aux": 0.0, "delta_target_loss_text_aux_effective": 0.010431, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.0, "delta_target_loss_text_aux_lexical": 0.0, "delta_target_acoustic_mae": 1.499107, "delta_source_acoustic_mae": 1.933303, "delta_target_text_aux_mae": 0.097038, "delta_source_text_aux_mae": 0.136171}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
