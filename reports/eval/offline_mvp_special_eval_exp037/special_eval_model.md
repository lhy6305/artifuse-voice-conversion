# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.890341
- loss_acoustic: 0.517814
- loss_event: 4.639446
- loss_text_aux: 0.117689
- loss_text_aux_effective: 0.122385
- loss_clause_transition_aux: 0.053029
- z_art_abs_mean: 0.345424
- z_art_delta_abs_mean: 0.012208
- event_prob_mean: 0.459377
- event_presence_prob_mean: 0.616139
- event_delta_prob_mean: 0.348821
- event_rise_prob_mean: 0.479179
- event_fall_prob_mean: 0.420271
- event_energy_prob_mean: 0.591996
- event_presence_peak_ratio: 0.813844
- acoustic_abs_mean: 0.913381
- acoustic_energy_mean: -3.453076
- acoustic_delta_abs_mean: 0.021329
- text_aux_abs_mean: 0.256674

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.282535
- loss_acoustic: 0.72727
- loss_event: 4.98762
- loss_text_aux: 0.248679
- loss_text_aux_effective: 0.270761
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.243415
- z_art_delta_abs_mean: 0.009128
- event_prob_mean: 0.446025
- event_presence_prob_mean: 0.580928
- event_delta_prob_mean: 0.363517
- event_rise_prob_mean: 0.455655
- event_fall_prob_mean: 0.436111
- event_energy_prob_mean: 0.562396
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.134023
- acoustic_energy_mean: -4.327417
- acoustic_delta_abs_mean: 0.016995
- text_aux_abs_mean: 0.305924

## 对比
- delta_loss_total: 0.392194
- delta_loss_acoustic: 0.209456
- delta_loss_event: 0.348174
- delta_loss_text_aux: 0.13099
- delta_loss_text_aux_effective: 0.148376
- delta_loss_clause_transition_aux: -0.053029
- delta_z_art_abs_mean: -0.102009
- delta_z_art_delta_abs_mean: -0.00308
- delta_event_prob_mean: -0.013352
- delta_event_presence_prob_mean: -0.035211
- delta_event_delta_prob_mean: 0.014696
- delta_event_rise_prob_mean: -0.023524
- delta_event_fall_prob_mean: 0.01584
- delta_event_energy_prob_mean: -0.0296
- delta_event_presence_peak_ratio: 0.135463
- delta_acoustic_abs_mean: 0.220642
- delta_acoustic_energy_mean: -0.874341
- delta_acoustic_delta_abs_mean: -0.004334
- delta_text_aux_abs_mean: 0.04925

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
