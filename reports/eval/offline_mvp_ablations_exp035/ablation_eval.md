# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.905673
- source.loss_total: 3.1401
- target.loss_text_aux_effective: 0.115761
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064394
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.12141
- source.loss_total: 3.912647
- target.loss_text_aux_effective: 0.117918
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064394
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.735883
- source_acoustic_mae: 0.502612
- target_text_aux_mae: 0.044172
- source_text_aux_mae: 0.025555

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.837528
- source.loss_total: 3.076568
- target.loss_text_aux_effective: 0.109777
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064394
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.011392
- source_acoustic_mae: 1.167954
- target_text_aux_mae: 0.068867
- source_text_aux_mae: 0.077959

## 对比
- zero_z_art: {"delta_target_loss_total": 0.215737, "delta_source_loss_total": 0.772547, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": 0.002157, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 0.735883, "delta_source_acoustic_mae": 0.502612, "delta_target_text_aux_mae": 0.044172, "delta_source_text_aux_mae": 0.025555}
- zero_e_evt: {"delta_target_loss_total": 0.931855, "delta_source_loss_total": -0.063532, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": -0.005984, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 1.011392, "delta_source_acoustic_mae": 1.167954, "delta_target_text_aux_mae": 0.068867, "delta_source_text_aux_mae": 0.077959}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
