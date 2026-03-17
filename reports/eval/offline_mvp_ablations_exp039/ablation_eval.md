# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.924376
- source.loss_total: 3.137307
- target.loss_text_aux_effective: 0.094748
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.101772
- target.loss_text_aux_lexical: 0.083509
- target.loss_clause_transition_aux: 0.064415
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.099634
- source.loss_total: 3.8859
- target.loss_text_aux_effective: 0.092178
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.10082
- target.loss_text_aux_lexical: 0.07835
- target.loss_clause_transition_aux: 0.064415
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.73999
- source_acoustic_mae: 0.502693
- target_text_aux_mae: 0.034941
- source_text_aux_mae: 0.023026

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.873858
- source.loss_total: 3.078942
- target.loss_text_aux_effective: 0.097747
- source.loss_text_aux_effective: 0.0
- target.loss_text_aux_structural: 0.10353
- target.loss_text_aux_lexical: 0.088494
- target.loss_clause_transition_aux: 0.064415
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.002749
- source_acoustic_mae: 1.169464
- target_text_aux_mae: 0.061786
- source_text_aux_mae: 0.080868

## 对比
- zero_z_art: {"delta_target_loss_total": 0.175258, "delta_source_loss_total": 0.748593, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": -0.00257, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": -0.000952, "delta_target_loss_text_aux_lexical": -0.005159, "delta_target_acoustic_mae": 0.73999, "delta_source_acoustic_mae": 0.502693, "delta_target_text_aux_mae": 0.034941, "delta_source_text_aux_mae": 0.023026}
- zero_e_evt: {"delta_target_loss_total": 0.949482, "delta_source_loss_total": -0.058365, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002999, "delta_source_loss_text_aux_effective": 0.0, "delta_target_loss_text_aux_structural": 0.001758, "delta_target_loss_text_aux_lexical": 0.004985, "delta_target_acoustic_mae": 1.002749, "delta_source_acoustic_mae": 1.169464, "delta_target_text_aux_mae": 0.061786, "delta_source_text_aux_mae": 0.080868}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
