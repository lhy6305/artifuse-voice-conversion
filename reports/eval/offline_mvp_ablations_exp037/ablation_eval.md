# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.906289
- source.loss_total: 3.140923
- target.loss_text_aux_effective: 0.116591
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 3.121609
- source.loss_total: 3.91323
- target.loss_text_aux_effective: 0.117716
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 0.736028
- source_acoustic_mae: 0.502542
- target_text_aux_mae: 0.043638
- source_text_aux_mae: 0.025517

## zero_e_evt
- batch_count: 14
- target.loss_total: 3.837695
- source.loss_total: 3.075868
- target.loss_text_aux_effective: 0.111197
- source.loss_text_aux_effective: 0.0
- target.loss_clause_transition_aux: 0.064393
- source.loss_clause_transition_aux: 0.0
- target_acoustic_mae: 1.011118
- source_acoustic_mae: 1.167722
- target_text_aux_mae: 0.068373
- source_text_aux_mae: 0.07869

## 对比
- zero_z_art: {"delta_target_loss_total": 0.21532, "delta_source_loss_total": 0.772307, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": 0.001125, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 0.736028, "delta_source_acoustic_mae": 0.502542, "delta_target_text_aux_mae": 0.043638, "delta_source_text_aux_mae": 0.025517}
- zero_e_evt: {"delta_target_loss_total": 0.931406, "delta_source_loss_total": -0.065055, "delta_target_loss_clause_transition_aux": 0.0, "delta_source_loss_clause_transition_aux": 0.0, "delta_target_loss_text_aux_effective": -0.005394, "delta_source_loss_text_aux_effective": 0.0, "delta_target_acoustic_mae": 1.011118, "delta_source_acoustic_mae": 1.167722, "delta_target_text_aux_mae": 0.068373, "delta_source_text_aux_mae": 0.07869}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
