# offline MVP 控制消融评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step500.pt

## none
- batch_count: 14
- target.loss_total: 1.904774
- source.loss_total: 1.609765
- target_acoustic_mae: 0.0
- source_acoustic_mae: 0.0
- target_text_aux_mae: 0.0
- source_text_aux_mae: 0.0

## zero_z_art
- batch_count: 14
- target.loss_total: 2.854097
- source.loss_total: 3.205398
- target_acoustic_mae: 0.776747
- source_acoustic_mae: 1.204631
- target_text_aux_mae: 0.0249
- source_text_aux_mae: 0.034963

## zero_e_evt
- batch_count: 14
- target.loss_total: 2.282955
- source.loss_total: 1.902574
- target_acoustic_mae: 0.600055
- source_acoustic_mae: 0.485213
- target_text_aux_mae: 0.030612
- source_text_aux_mae: 0.015282

## 对比
- zero_z_art: {"delta_target_loss_total": 0.949323, "delta_source_loss_total": 1.595633, "delta_target_acoustic_mae": 0.776747, "delta_source_acoustic_mae": 1.204631, "delta_target_text_aux_mae": 0.0249, "delta_source_text_aux_mae": 0.034963}
- zero_e_evt: {"delta_target_loss_total": 0.378181, "delta_source_loss_total": 0.292809, "delta_target_acoustic_mae": 0.600055, "delta_source_acoustic_mae": 0.485213, "delta_target_text_aux_mae": 0.030612, "delta_source_text_aux_mae": 0.015282}

## 备注
- Ablation results are computed on the formal hybrid validation split only.
- zero_z_art zeroes the articulatory control before control fusion.
- zero_e_evt zeroes the event control path before control fusion.
