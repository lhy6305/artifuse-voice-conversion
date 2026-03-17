# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 2.677671
- loss_acoustic: 0.311511
- loss_event: 4.678162
- loss_text_aux: 0.099318
- z_art_abs_mean: 0.28149
- event_prob_mean: 0.439741
- acoustic_abs_mean: 0.907636
- text_aux_abs_mean: 0.254619

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.863008
- loss_acoustic: 0.357177
- loss_event: 4.902297
- loss_text_aux: 0.241694
- z_art_abs_mean: 0.231372
- event_prob_mean: 0.430695
- acoustic_abs_mean: 1.059344
- text_aux_abs_mean: 0.281534

## 对比
- delta_loss_total: 0.185337
- delta_loss_acoustic: 0.045666
- delta_loss_event: 0.224135
- delta_loss_text_aux: 0.142376
- delta_z_art_abs_mean: -0.050118
- delta_event_prob_mean: -0.009046
- delta_acoustic_abs_mean: 0.151708
- delta_text_aux_abs_mean: 0.026915

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
