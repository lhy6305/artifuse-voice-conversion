# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-015-offline-mvp-b1-100step-calibration.step100.pt

## none
- batch_count: 14
- target.loss_total: 2.676195
- source.loss_total: 2.689358
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 4.008858
- source.loss_total: 4.68694
- target_acoustic_mae: 1.217411
- source_acoustic_mae: 1.012046
- target_text_aux_mae: 0.074679
- source_text_aux_mae: 0.053423

## zero_e_evt
- batch_count: 14
- target.loss_total: 4.083701
- source.loss_total: 3.69476
- target_acoustic_mae: 1.310195
- source_acoustic_mae: 1.584664
- target_text_aux_mae: 0.057291
- source_text_aux_mae: 0.073275

## 对比
- zero_z_art: {"delta_target_loss_total": 1.332663, "delta_source_loss_total": 1.997582, "delta_target_acoustic_mae": 1.217411, "delta_source_acoustic_mae": 1.012046, "delta_target_text_aux_mae": 0.074679, "delta_source_text_aux_mae": 0.053423}
- zero_e_evt: {"delta_target_loss_total": 1.407506, "delta_source_loss_total": 1.005402, "delta_target_acoustic_mae": 1.310195, "delta_source_acoustic_mae": 1.584664, "delta_target_text_aux_mae": 0.057291, "delta_source_text_aux_mae": 0.073275}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
