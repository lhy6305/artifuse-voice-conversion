# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step25.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 13.587198
- loss_acoustic: 10.861688
- loss_event: 5.420372
- loss_text_aux: 0.073916
- z_art_abs_mean: 0.158462
- event_prob_mean: 0.487213
- acoustic_abs_mean: 0.562353
- text_aux_abs_mean: 0.174514

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 9.704168
- loss_acoustic: 6.852811
- loss_event: 5.418629
- loss_text_aux: 0.709104
- z_art_abs_mean: 0.164137
- event_prob_mean: 0.486252
- acoustic_abs_mean: 0.565312
- text_aux_abs_mean: 0.175063

## 对比
- delta_loss_total: -3.88303
- delta_loss_acoustic: -4.008877
- delta_loss_event: -0.001743
- delta_loss_text_aux: 0.635188
- delta_z_art_abs_mean: 0.005675
- delta_event_prob_mean: -0.000961
- delta_acoustic_abs_mean: 0.002959
- delta_text_aux_abs_mean: 0.000549

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
