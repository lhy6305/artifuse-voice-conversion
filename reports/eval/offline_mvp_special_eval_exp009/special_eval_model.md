# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_smallscale_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-009-offline-mvp-seeded-shuffle.step20.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 15.770239
- loss_acoustic: 13.031809
- loss_event: 5.450413
- loss_text_aux: 0.063874
- z_art_abs_mean: 0.133934
- event_prob_mean: 0.492518
- acoustic_abs_mean: 0.409574
- text_aux_abs_mean: 0.133805

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 11.934946
- loss_acoustic: 9.063388
- loss_event: 5.456944
- loss_text_aux: 0.714419
- z_art_abs_mean: 0.138525
- event_prob_mean: 0.491758
- acoustic_abs_mean: 0.411651
- text_aux_abs_mean: 0.134469

## 对比
- delta_loss_total: -3.835293
- delta_loss_acoustic: -3.968421
- delta_loss_event: 0.006531
- delta_loss_text_aux: 0.650545
- delta_z_art_abs_mean: 0.004591
- delta_event_prob_mean: -0.00076
- delta_acoustic_abs_mean: 0.002077
- delta_text_aux_abs_mean: 0.000664

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
