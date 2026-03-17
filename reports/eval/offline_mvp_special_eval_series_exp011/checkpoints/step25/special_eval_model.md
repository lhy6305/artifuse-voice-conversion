# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-011-offline-mvp-large-scale-500.step25.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 62
- batch_count: 16
- loss_total: 13.585217
- loss_acoustic: 10.864312
- loss_event: 5.411176
- loss_text_aux: 0.073847
- z_art_abs_mean: 0.158652
- z_art_delta_abs_mean: 0.000683
- event_prob_mean: 0.487313
- event_presence_prob_mean: 0.550058
- event_delta_prob_mean: 0.507425
- event_rise_prob_mean: 0.532928
- event_fall_prob_mean: 0.506437
- event_energy_prob_mean: 0.456279
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.561947
- acoustic_energy_mean: -1.633316
- acoustic_delta_abs_mean: 0.048838
- text_aux_abs_mean: 0.173569

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 9.707916
- loss_acoustic: 6.855166
- loss_event: 5.421776
- loss_text_aux: 0.708173
- z_art_abs_mean: 0.164384
- z_art_delta_abs_mean: 0.000284
- event_prob_mean: 0.486317
- event_presence_prob_mean: 0.549081
- event_delta_prob_mean: 0.507627
- event_rise_prob_mean: 0.533581
- event_fall_prob_mean: 0.505267
- event_energy_prob_mean: 0.455345
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.56486
- acoustic_energy_mean: -1.640207
- acoustic_delta_abs_mean: 0.051306
- text_aux_abs_mean: 0.174122

## 对比
- delta_loss_total: -3.877301
- delta_loss_acoustic: -4.009146
- delta_loss_event: 0.0106
- delta_loss_text_aux: 0.634326
- delta_z_art_abs_mean: 0.005732
- delta_z_art_delta_abs_mean: -0.000399
- delta_event_prob_mean: -0.000996
- delta_event_presence_prob_mean: -0.000977
- delta_event_delta_prob_mean: 0.000202
- delta_event_rise_prob_mean: 0.000653
- delta_event_fall_prob_mean: -0.00117
- delta_event_energy_prob_mean: -0.000934
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.002913
- delta_acoustic_energy_mean: -0.006891
- delta_acoustic_delta_abs_mean: 0.002468
- delta_text_aux_abs_mean: 0.000553

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
