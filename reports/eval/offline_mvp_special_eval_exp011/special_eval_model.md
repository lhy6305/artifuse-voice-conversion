# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step500.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 1.752648
- loss_acoustic: 0.069839
- loss_event: 3.349055
- loss_text_aux: 0.012398
- z_art_abs_mean: 0.628347
- event_prob_mean: 0.402903
- acoustic_abs_mean: 0.96894
- text_aux_abs_mean: 0.157326

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.118624
- loss_acoustic: 0.036374
- loss_event: 3.952358
- loss_text_aux: 0.504144
- z_art_abs_mean: 0.687601
- event_prob_mean: 0.40301
- acoustic_abs_mean: 0.96732
- text_aux_abs_mean: 0.19124

## 对比
- delta_loss_total: 0.365976
- delta_loss_acoustic: -0.033465
- delta_loss_event: 0.603303
- delta_loss_text_aux: 0.491746
- delta_z_art_abs_mean: 0.059254
- delta_event_prob_mean: 0.000107
- delta_acoustic_abs_mean: -0.00162
- delta_text_aux_abs_mean: 0.033914

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
