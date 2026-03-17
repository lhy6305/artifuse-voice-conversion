# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.step10.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 19.746407
- loss_acoustic: 16.95783
- loss_event: 5.504425
- loss_text_aux: 0.180147
- z_art_abs_mean: 0.088454
- event_prob_mean: 0.500847
- acoustic_abs_mean: 0.184894
- text_aux_abs_mean: 0.102586

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 15.83483
- loss_acoustic: 13.052741
- loss_event: 5.501617
- loss_text_aux: 0.155461
- z_art_abs_mean: 0.091169
- event_prob_mean: 0.500485
- acoustic_abs_mean: 0.18574
- text_aux_abs_mean: 0.102621

## 对比
- delta_loss_total: -3.911577
- delta_loss_acoustic: -3.905089
- delta_loss_event: -0.002808
- delta_loss_text_aux: -0.024686
- delta_z_art_abs_mean: 0.002715
- delta_event_prob_mean: -0.000362
- delta_acoustic_abs_mean: 0.000846
- delta_text_aux_abs_mean: 3.5e-05

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
