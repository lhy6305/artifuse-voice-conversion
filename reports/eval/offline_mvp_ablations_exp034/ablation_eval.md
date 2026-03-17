# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.683255
- source.loss_total: 2.691008
- target.loss_clause_transition_aux: 0.062681
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.988163
- source.loss_total: 4.386627
- target.loss_clause_transition_aux: 0.062681
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.18482
- source_acoustic_mae: 0.994964
- target_text_aux_mae: 0.087152
- source_text_aux_mae: 0.069014

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.418362
- source.loss_total: 4.220745
- target.loss_clause_transition_aux: 0.062681
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.355491
- source_acoustic_mae: 1.619118
- target_text_aux_mae: 0.067177
- source_text_aux_mae: 0.088803

## 对比
- zero_z_art: {"delta_target_loss_total": 1.304908, "delta_source_loss_total": 1.695619, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.18482, "delta_source_acoustic_mae": 0.994964, "delta_target_text_aux_mae": 0.087152, "delta_source_text_aux_mae": 0.069014}
- zero_e_evt: {"delta_target_loss_total": 1.735107, "delta_source_loss_total": 1.529737, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.355491, "delta_source_acoustic_mae": 1.619118, "delta_target_text_aux_mae": 0.067177, "delta_source_text_aux_mae": 0.088803}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
