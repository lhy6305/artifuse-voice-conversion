# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-013-offline-mvp-evt-a1-large-scale.step250.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 2.016988
- loss_acoustic: 0.075139
- loss_event: 3.85279
- loss_text_aux: 0.014252
- z_art_abs_mean: 0.683981
- event_prob_mean: 0.417603
- acoustic_abs_mean: 0.951822
- text_aux_abs_mean: 0.148285

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.292754
- loss_acoustic: 0.041554
- loss_event: 4.246412
- loss_text_aux: 0.569684
- z_art_abs_mean: 0.628475
- event_prob_mean: 0.390648
- acoustic_abs_mean: 0.953342
- text_aux_abs_mean: 0.163608

## 对比
- delta_loss_total: 0.275766
- delta_loss_acoustic: -0.033585
- delta_loss_event: 0.393622
- delta_loss_text_aux: 0.555432
- delta_z_art_abs_mean: -0.055506
- delta_event_prob_mean: -0.026955
- delta_acoustic_abs_mean: 0.00152
- delta_text_aux_abs_mean: 0.015323

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
