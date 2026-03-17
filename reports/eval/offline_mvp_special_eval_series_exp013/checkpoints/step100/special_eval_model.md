# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 2.685433
- loss_acoustic: 0.306417
- loss_event: 4.737016
- loss_text_aux: 0.016934
- z_art_abs_mean: 0.285694
- event_prob_mean: 0.435112
- acoustic_abs_mean: 0.906168
- text_aux_abs_mean: 0.177335

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.893407
- loss_acoustic: 0.352829
- loss_event: 4.855006
- loss_text_aux: 0.533998
- z_art_abs_mean: 0.235696
- event_prob_mean: 0.427426
- acoustic_abs_mean: 1.055127
- text_aux_abs_mean: 0.178749

## 对比
- delta_loss_total: 0.207974
- delta_loss_acoustic: 0.046412
- delta_loss_event: 0.11799
- delta_loss_text_aux: 0.517064
- delta_z_art_abs_mean: -0.049998
- delta_event_prob_mean: -0.007686
- delta_acoustic_abs_mean: 0.148959
- delta_text_aux_abs_mean: 0.001414

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
