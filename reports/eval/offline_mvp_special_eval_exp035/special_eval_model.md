# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.889709
- loss_acoustic: 0.517385
- loss_event: 4.639396
- loss_text_aux: 0.118208
- loss_text_aux_effective: 0.121494
- loss_clause_transition_aux: 0.05303
- z_art_abs_mean: 0.345518
- z_art_delta_abs_mean: 0.012208
- event_prob_mean: 0.459379
- event_presence_prob_mean: 0.616167
- event_delta_prob_mean: 0.348799
- event_rise_prob_mean: 0.479177
- event_fall_prob_mean: 0.420281
- event_energy_prob_mean: 0.592007
- event_presence_peak_ratio: 0.813924
- acoustic_abs_mean: 0.913382
- acoustic_energy_mean: -3.453053
- acoustic_delta_abs_mean: 0.021026
- text_aux_abs_mean: 0.258385

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.282759
- loss_acoustic: 0.726435
- loss_event: 4.987605
- loss_text_aux: 0.252422
- loss_text_aux_effective: 0.276093
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.243508
- z_art_delta_abs_mean: 0.009129
- event_prob_mean: 0.446026
- event_presence_prob_mean: 0.580958
- event_delta_prob_mean: 0.363489
- event_rise_prob_mean: 0.455648
- event_fall_prob_mean: 0.436117
- event_energy_prob_mean: 0.562411
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.133867
- acoustic_energy_mean: -4.326916
- acoustic_delta_abs_mean: 0.016773
- text_aux_abs_mean: 0.30618

## 对比
- delta_loss_total: 0.39305
- delta_loss_acoustic: 0.20905
- delta_loss_event: 0.348209
- delta_loss_text_aux: 0.134214
- delta_loss_text_aux_effective: 0.154599
- delta_loss_clause_transition_aux: -0.05303
- delta_z_art_abs_mean: -0.10201
- delta_z_art_delta_abs_mean: -0.003079
- delta_event_prob_mean: -0.013353
- delta_event_presence_prob_mean: -0.035209
- delta_event_delta_prob_mean: 0.01469
- delta_event_rise_prob_mean: -0.023529
- delta_event_fall_prob_mean: 0.015836
- delta_event_energy_prob_mean: -0.029596
- delta_event_presence_peak_ratio: 0.135383
- delta_acoustic_abs_mean: 0.220485
- delta_acoustic_energy_mean: -0.873863
- delta_acoustic_delta_abs_mean: -0.004253
- delta_text_aux_abs_mean: 0.047795

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
