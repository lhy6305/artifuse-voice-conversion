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
- z_art_delta_abs_mean: 0.007251
- event_prob_mean: 0.402903
- event_presence_prob_mean: 0.623295
- event_delta_prob_mean: 0.199527
- event_rise_prob_mean: 0.497363
- event_fall_prob_mean: 0.500946
- event_energy_prob_mean: 0.641024
- event_presence_peak_ratio: 0.623853
- acoustic_abs_mean: 0.96894
- acoustic_energy_mean: -3.737195
- acoustic_delta_abs_mean: 0.008849
- text_aux_abs_mean: 0.157326

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 2.118624
- loss_acoustic: 0.036374
- loss_event: 3.952358
- loss_text_aux: 0.504144
- z_art_abs_mean: 0.687601
- z_art_delta_abs_mean: 0.006553
- event_prob_mean: 0.40301
- event_presence_prob_mean: 0.575234
- event_delta_prob_mean: 0.309396
- event_rise_prob_mean: 0.494585
- event_fall_prob_mean: 0.506736
- event_energy_prob_mean: 0.623084
- event_presence_peak_ratio: 0.598973
- acoustic_abs_mean: 0.96732
- acoustic_energy_mean: -3.780926
- acoustic_delta_abs_mean: 0.006459
- text_aux_abs_mean: 0.19124

## 对比
- delta_loss_total: 0.365976
- delta_loss_acoustic: -0.033465
- delta_loss_event: 0.603303
- delta_loss_text_aux: 0.491746
- delta_z_art_abs_mean: 0.059254
- delta_z_art_delta_abs_mean: -0.000698
- delta_event_prob_mean: 0.000107
- delta_event_presence_prob_mean: -0.048061
- delta_event_delta_prob_mean: 0.109869
- delta_event_rise_prob_mean: -0.002778
- delta_event_fall_prob_mean: 0.00579
- delta_event_energy_prob_mean: -0.01794
- delta_event_presence_peak_ratio: -0.02488
- delta_acoustic_abs_mean: -0.00162
- delta_acoustic_energy_mean: -0.043731
- delta_acoustic_delta_abs_mean: -0.00239
- delta_text_aux_abs_mean: 0.033914

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
