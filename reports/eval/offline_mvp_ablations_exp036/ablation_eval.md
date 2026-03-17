# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.905926
- source.loss_total: 3.140868
- target.loss_text_aux_effective: 0.115879
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.121556
- source.loss_total: 3.913362
- target.loss_text_aux_effective: 0.11751
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.735965
- source_acoustic_mae: 0.50259
- target_text_aux_mae: 0.044124
- source_text_aux_mae: 0.0256

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.837113
- source.loss_total: 3.075783
- target.loss_text_aux_effective: 0.110183
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.011236
- source_acoustic_mae: 1.167817
- target_text_aux_mae: 0.069293
- source_text_aux_mae: 0.079544

## 对比
- zero_z_art: {"delta_target_loss_total": 0.21563, "delta_source_loss_total": 0.772494, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": 0.001631, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 0.735965, "delta_source_acoustic_mae": 0.50259, "delta_target_text_aux_mae": 0.044124, "delta_source_text_aux_mae": 0.0256}
- zero_e_evt: {"delta_target_loss_total": 0.931187, "delta_source_loss_total": -0.065085, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": -0.005696, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 1.011236, "delta_source_acoustic_mae": 1.167817, "delta_target_text_aux_mae": 0.069293, "delta_source_text_aux_mae": 0.079544}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
