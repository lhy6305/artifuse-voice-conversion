# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.889944
- loss_acoustic: 0.517606
- loss_event: 4.639409
- loss_text_aux: 0.117327
- loss_text_aux_effective: 0.121526
- loss_clause_transition_aux: 0.05303
- z_art_abs_mean: 0.345487
- z_art_delta_abs_mean: 0.012209
- event_prob_mean: 0.459378
- event_presence_prob_mean: 0.61616
- event_delta_prob_mean: 0.348812
- event_rise_prob_mean: 0.479181
- event_fall_prob_mean: 0.420274
- event_energy_prob_mean: 0.591991
- event_presence_peak_ratio: 0.81387
- acoustic_abs_mean: 0.913441
- acoustic_energy_mean: -3.453318
- acoustic_delta_abs_mean: 0.021213
- text_aux_abs_mean: 0.261633

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.28331
- loss_acoustic: 0.727309
- loss_event: 4.987608
- loss_text_aux: 0.253007
- loss_text_aux_effective: 0.274468
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.243463
- z_art_delta_abs_mean: 0.009129
- event_prob_mean: 0.446025
- event_presence_prob_mean: 0.580948
- event_delta_prob_mean: 0.363506
- event_rise_prob_mean: 0.455652
- event_fall_prob_mean: 0.436112
- event_energy_prob_mean: 0.562393
- event_presence_peak_ratio: 0.949307
- acoustic_abs_mean: 1.134017
- acoustic_energy_mean: -4.327504
- acoustic_delta_abs_mean: 0.016889
- text_aux_abs_mean: 0.311493

## 对比
- delta_loss_total: 0.393366
- delta_loss_acoustic: 0.209703
- delta_loss_event: 0.348199
- delta_loss_text_aux: 0.13568
- delta_loss_text_aux_effective: 0.152942
- delta_loss_clause_transition_aux: -0.05303
- delta_z_art_abs_mean: -0.102024
- delta_z_art_delta_abs_mean: -0.00308
- delta_event_prob_mean: -0.013353
- delta_event_presence_prob_mean: -0.035212
- delta_event_delta_prob_mean: 0.014694
- delta_event_rise_prob_mean: -0.023529
- delta_event_fall_prob_mean: 0.015838
- delta_event_energy_prob_mean: -0.029598
- delta_event_presence_peak_ratio: 0.135437
- delta_acoustic_abs_mean: 0.220576
- delta_acoustic_energy_mean: -0.874186
- delta_acoustic_delta_abs_mean: -0.004324
- delta_text_aux_abs_mean: 0.04986

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
