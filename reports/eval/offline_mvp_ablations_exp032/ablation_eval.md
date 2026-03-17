# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.685245
- source.loss_total: 2.691438
- target.loss_clause_transition_aux: 0.06273
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.960504
- source.loss_total: 4.361903
- target.loss_clause_transition_aux: 0.06273
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.174284
- source_acoustic_mae: 0.98444
- target_text_aux_mae: 0.085425
- source_text_aux_mae: 0.067755

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.420742
- source.loss_total: 4.214776
- target.loss_clause_transition_aux: 0.06273
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.354795
- source_acoustic_mae: 1.615941
- target_text_aux_mae: 0.066566
- source_text_aux_mae: 0.087929

## 对比
- zero_z_art: {"delta_target_loss_total": 1.275259, "delta_source_loss_total": 1.670465, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.174284, "delta_source_acoustic_mae": 0.98444, "delta_target_text_aux_mae": 0.085425, "delta_source_text_aux_mae": 0.067755}
- zero_e_evt: {"delta_target_loss_total": 1.735497, "delta_source_loss_total": 1.523338, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_acoustic_mae": 1.354795, "delta_source_acoustic_mae": 1.615941, "delta_target_text_aux_mae": 0.066566, "delta_source_text_aux_mae": 0.087929}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
