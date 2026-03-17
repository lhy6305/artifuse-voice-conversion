# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.926816
- source.loss_total: 3.134204
- target.loss_text_aux_effective: 0.094903
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.102279
- target.loss_text_aux_lexical: 0.083102
- target.loss_clause_transition_aux: 0.0644
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.097492
- source.loss_total: 3.883029
- target.loss_text_aux_effective: 0.092479
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.10152
- target.loss_text_aux_lexical: 0.078014
- target.loss_clause_transition_aux: 0.0644
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.739338
- source_acoustic_mae: 0.503958
- target_text_aux_mae: 0.035113
- source_text_aux_mae: 0.023457

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.875979
- source.loss_total: 3.077822
- target.loss_text_aux_effective: 0.097534
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.103323
- target.loss_text_aux_lexical: 0.088272
- target.loss_clause_transition_aux: 0.0644
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.998581
- source_acoustic_mae: 1.16547
- target_text_aux_mae: 0.061832
- source_text_aux_mae: 0.081198

## 对比
- zero_z_art: {"delta_target_loss_total": 0.170676, "delta_source_loss_total": 0.748825, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": -0.002424, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": -0.000759, "delta_target_loss_text_aux_lexical": -0.005088, "delta_target_acoustic_mae": 0.739338, "delta_source_acoustic_mae": 0.503958, "delta_target_text_aux_mae": 0.035113, "delta_source_text_aux_mae": 0.023457}
- zero_e_evt: {"delta_target_loss_total": 0.949163, "delta_source_loss_total": -0.056382, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002631, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.001044, "delta_target_loss_text_aux_lexical": 0.00517, "delta_target_acoustic_mae": 0.998581, "delta_source_acoustic_mae": 1.16547, "delta_target_text_aux_mae": 0.061832, "delta_source_text_aux_mae": 0.081198}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
