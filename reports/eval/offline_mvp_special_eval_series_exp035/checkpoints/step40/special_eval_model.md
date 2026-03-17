# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.step40.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 9.296346
- loss_acoustic: 6.584765
- loss_event: 5.332237
- loss_text_aux: 0.215751
- loss_text_aux_effective: 0.160086
- loss_clause_transition_aux: 0.035999
- z_art_abs_mean: 0.22133
- z_art_delta_abs_mean: 0.001057
- event_prob_mean: 0.491038
- event_presence_prob_mean: 0.552272
- event_delta_prob_mean: 0.534615
- event_rise_prob_mean: 0.469291
- event_fall_prob_mean: 0.520831
- event_energy_prob_mean: 0.510693
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.878033
- acoustic_energy_mean: -3.377072
- acoustic_delta_abs_mean: 0.067566
- text_aux_abs_mean: 0.379687

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.179188
- loss_acoustic: 2.456268
- loss_event: 5.367246
- loss_text_aux: 0.339427
- loss_text_aux_effective: 0.195114
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.229127
- z_art_delta_abs_mean: 0.000343
- event_prob_mean: 0.489896
- event_presence_prob_mean: 0.551441
- event_delta_prob_mean: 0.539204
- event_rise_prob_mean: 0.465581
- event_fall_prob_mean: 0.525547
- event_energy_prob_mean: 0.506406
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 0.88456
- acoustic_energy_mean: -3.401015
- acoustic_delta_abs_mean: 0.072251
- text_aux_abs_mean: 0.381975

## 对比
- delta_loss_total: -4.117158
- delta_loss_acoustic: -4.128497
- delta_loss_event: 0.035009
- delta_loss_text_aux: 0.123676
- delta_loss_text_aux_effective: 0.035028
- delta_loss_clause_transition_aux: -0.035999
- delta_z_art_abs_mean: 0.007797
- delta_z_art_delta_abs_mean: -0.000714
- delta_event_prob_mean: -0.001142
- delta_event_presence_prob_mean: -0.000831
- delta_event_delta_prob_mean: 0.004589
- delta_event_rise_prob_mean: -0.00371
- delta_event_fall_prob_mean: 0.004716
- delta_event_energy_prob_mean: -0.004287
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.006527
- delta_acoustic_energy_mean: -0.023943
- delta_acoustic_delta_abs_mean: 0.004685
- delta_text_aux_abs_mean: 0.002288

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
