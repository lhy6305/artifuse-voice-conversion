# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step500.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 1.903484
- loss_acoustic: 0.0648
- loss_event: 3.659414
- loss_text_aux: 0.013008
- z_art_abs_mean: 0.582312
- event_prob_mean: 0.403894
- acoustic_abs_mean: 0.967009
- text_aux_abs_mean: 0.150285

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.192053
- loss_acoustic: 0.032446
- loss_event: 4.098673
- loss_text_aux: 0.520022
- z_art_abs_mean: 0.648342
- event_prob_mean: 0.405813
- acoustic_abs_mean: 0.967947
- text_aux_abs_mean: 0.170773

## 对比
- delta_loss_total: 0.288569
- delta_loss_acoustic: -0.032354
- delta_loss_event: 0.439259
- delta_loss_text_aux: 0.507014
- delta_z_art_abs_mean: 0.06603
- delta_event_prob_mean: 0.001919
- delta_acoustic_abs_mean: 0.000938
- delta_text_aux_abs_mean: 0.020488

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
