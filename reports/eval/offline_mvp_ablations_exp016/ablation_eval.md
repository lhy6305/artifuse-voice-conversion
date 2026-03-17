# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.680581
- source.loss_total: 2.686611
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 4.011123
- source.loss_total: 4.665987
- target_acoustic_mae: 1.2109
- source_acoustic_mae: 1.006741
- target_text_aux_mae: 0.084586
- source_text_aux_mae: 0.067068

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.089245
- source.loss_total: 3.698593
- target_acoustic_mae: 1.311995
- source_acoustic_mae: 1.58536
- target_text_aux_mae: 0.061774
- source_text_aux_mae: 0.084658

## 对比
- zero_z_art: {"delta_target_loss_total": 1.330542, "delta_source_loss_total": 1.979376, "delta_target_acoustic_mae": 1.2109, "delta_source_acoustic_mae": 1.006741, "delta_target_text_aux_mae": 0.084586, "delta_source_text_aux_mae": 0.067068}
- zero_e_evt: {"delta_target_loss_total": 1.408664, "delta_source_loss_total": 1.011982, "delta_target_acoustic_mae": 1.311995, "delta_source_acoustic_mae": 1.58536, "delta_target_text_aux_mae": 0.061774, "delta_source_text_aux_mae": 0.084658}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
