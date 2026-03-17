# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.262372
- loss_acoustic: 5.672441
- loss_event: 5.102672
- loss_text_aux: 0.13445
- loss_text_aux_effective: 0.111228
- loss_clause_transition_aux: 0.043137
- z_art_abs_mean: 0.177256
- z_art_delta_abs_mean: 0.001564
- event_prob_mean: 0.475243
- event_presence_prob_mean: 0.575718
- event_delta_prob_mean: 0.449606
- event_rise_prob_mean: 0.484246
- event_fall_prob_mean: 0.45826
- event_energy_prob_mean: 0.550847
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.080346
- acoustic_energy_mean: -4.18433
- acoustic_delta_abs_mean: 0.018516
- text_aux_abs_mean: 0.338433

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.052798
- loss_acoustic: 2.400858
- loss_event: 5.200349
- loss_text_aux: 0.299234
- loss_text_aux_effective: 0.255369
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.180927
- z_art_delta_abs_mean: 0.000865
- event_prob_mean: 0.471231
- event_presence_prob_mean: 0.57022
- event_delta_prob_mean: 0.45313
- event_rise_prob_mean: 0.476545
- event_fall_prob_mean: 0.462434
- event_energy_prob_mean: 0.544772
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.113186
- acoustic_energy_mean: -4.335782
- acoustic_delta_abs_mean: 0.007515
- text_aux_abs_mean: 0.350022

## 对比
- delta_loss_total: -3.209574
- delta_loss_acoustic: -3.271583
- delta_loss_event: 0.097677
- delta_loss_text_aux: 0.164784
- delta_loss_text_aux_effective: 0.144141
- delta_loss_clause_transition_aux: -0.043137
- delta_z_art_abs_mean: 0.003671
- delta_z_art_delta_abs_mean: -0.000699
- delta_event_prob_mean: -0.004012
- delta_event_presence_prob_mean: -0.005498
- delta_event_delta_prob_mean: 0.003524
- delta_event_rise_prob_mean: -0.007701
- delta_event_fall_prob_mean: 0.004174
- delta_event_energy_prob_mean: -0.006075
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.03284
- delta_acoustic_energy_mean: -0.151452
- delta_acoustic_delta_abs_mean: -0.011001
- delta_text_aux_abs_mean: 0.011589

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
