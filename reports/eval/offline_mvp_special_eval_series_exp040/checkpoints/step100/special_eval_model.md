# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step100.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 2.91453
- loss_acoustic: 0.544783
- loss_event: 4.63831
- loss_text_aux: 0.110624
- loss_text_aux_effective: 0.110624
- loss_text_aux_structural: 0.117676
- loss_text_aux_lexical: 0.099341
- loss_clause_transition_aux: 0.053035
- z_art_abs_mean: 0.345872
- z_art_delta_abs_mean: 0.01238
- event_prob_mean: 0.459409
- event_presence_prob_mean: 0.615699
- event_delta_prob_mean: 0.349416
- event_rise_prob_mean: 0.477782
- event_fall_prob_mean: 0.419741
- event_energy_prob_mean: 0.591824
- event_presence_peak_ratio: 0.806185
- acoustic_abs_mean: 0.905853
- acoustic_energy_mean: -3.425092
- acoustic_delta_abs_mean: 0.020695
- text_aux_abs_mean: 0.226033

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.264445
- loss_acoustic: 0.722764
- loss_event: 4.987868
- loss_text_aux: 0.201782
- loss_text_aux_effective: 0.201782
- loss_text_aux_structural: 0.2624
- loss_text_aux_lexical: 0.104792
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.241889
- z_art_delta_abs_mean: 0.009238
- event_prob_mean: 0.445942
- event_presence_prob_mean: 0.58021
- event_delta_prob_mean: 0.36429
- event_rise_prob_mean: 0.4544
- event_fall_prob_mean: 0.435977
- event_energy_prob_mean: 0.561752
- event_presence_peak_ratio: 0.945074
- acoustic_abs_mean: 1.130955
- acoustic_energy_mean: -4.310645
- acoustic_delta_abs_mean: 0.014623
- text_aux_abs_mean: 0.267447

## 对比
- delta_loss_total: 0.349915
- delta_loss_acoustic: 0.177981
- delta_loss_event: 0.349558
- delta_loss_text_aux: 0.091158
- delta_loss_text_aux_effective: 0.091158
- delta_loss_text_aux_structural: 0.144724
- delta_loss_text_aux_lexical: 0.005451
- delta_loss_clause_transition_aux: -0.053035
- delta_z_art_abs_mean: -0.103983
- delta_z_art_delta_abs_mean: -0.003142
- delta_event_prob_mean: -0.013467
- delta_event_presence_prob_mean: -0.035489
- delta_event_delta_prob_mean: 0.014874
- delta_event_rise_prob_mean: -0.023382
- delta_event_fall_prob_mean: 0.016236
- delta_event_energy_prob_mean: -0.030072
- delta_event_presence_peak_ratio: 0.138889
- delta_acoustic_abs_mean: 0.225102
- delta_acoustic_energy_mean: -0.885553
- delta_acoustic_delta_abs_mean: -0.006072
- delta_text_aux_abs_mean: 0.041414

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
