# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-014-offline-mvp-b1-smallscale.step20.pt

## none
- batch_count: 14
- target.loss_total: 16.37399
- source.loss_total: 21.425115
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 16.581004
- source.loss_total: 21.723951
- target_acoustic_mae: 0.061145
- source_acoustic_mae: 0.062741
- target_text_aux_mae: 0.009176
- source_text_aux_mae: 0.009704

## zero_e_evt
- batch_count: 14
- target.loss_total: 18.107861
- source.loss_total: 23.880236
- target_acoustic_mae: 0.655007
- source_acoustic_mae: 0.649894
- target_text_aux_mae: 0.057788
- source_text_aux_mae: 0.058166

## 对比
- zero_z_art: {"delta_target_loss_total": 0.207014, "delta_source_loss_total": 0.298836, "delta_target_acoustic_mae": 0.061145, "delta_source_acoustic_mae": 0.062741, "delta_target_text_aux_mae": 0.009176, "delta_source_text_aux_mae": 0.009704}
- zero_e_evt: {"delta_target_loss_total": 1.733871, "delta_source_loss_total": 2.455121, "delta_target_acoustic_mae": 0.655007, "delta_source_acoustic_mae": 0.649894, "delta_target_text_aux_mae": 0.057788, "delta_source_text_aux_mae": 0.058166}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
