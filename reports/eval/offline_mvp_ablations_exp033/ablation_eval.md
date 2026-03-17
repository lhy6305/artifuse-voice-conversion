# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.676657
- source.loss_total: 2.689348
- target.loss_clause_transition_aux: 0.062664
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 4.013703
- source.loss_total: 4.410067
- target.loss_clause_transition_aux: 0.062664
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.194476
- source_acoustic_mae: 1.008645
- target_text_aux_mae: 0.087705
- source_text_aux_mae: 0.070326

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.390696
- source.loss_total: 4.195556
- target.loss_clause_transition_aux: 0.062664
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.355538
- source_acoustic_mae: 1.613748
- target_text_aux_mae: 0.066596
- source_text_aux_mae: 0.088239

## 对比
- zero_z_art: {"delta_target_loss_total": 1.337046, "delta_source_loss_total": 1.720719, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.194476, "delta_source_acoustic_mae": 1.008645, "delta_target_text_aux_mae": 0.087705, "delta_source_text_aux_mae": 0.070326}
- zero_e_evt: {"delta_target_loss_total": 1.714039, "delta_source_loss_total": 1.506208, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.355538, "delta_source_acoustic_mae": 1.613748, "delta_target_text_aux_mae": 0.066596, "delta_source_text_aux_mae": 0.088239}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
