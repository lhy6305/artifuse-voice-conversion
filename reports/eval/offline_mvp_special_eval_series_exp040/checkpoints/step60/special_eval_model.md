# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.step60.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 8.281567
- loss_acoustic: 5.684279
- loss_event: 5.102859
- loss_text_aux: 0.147614
- loss_text_aux_effective: 0.147614
- loss_text_aux_structural: 0.162651
- loss_text_aux_lexical: 0.123554
- loss_clause_transition_aux: 0.043135
- z_art_abs_mean: 0.178911
- z_art_delta_abs_mean: 0.001547
- event_prob_mean: 0.475081
- event_presence_prob_mean: 0.575712
- event_delta_prob_mean: 0.449685
- event_rise_prob_mean: 0.48392
- event_fall_prob_mean: 0.458174
- event_energy_prob_mean: 0.550624
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.082066
- acoustic_energy_mean: -4.188827
- acoustic_delta_abs_mean: 0.019029
- text_aux_abs_mean: 0.323206

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 5.063248
- loss_acoustic: 2.40678
- loss_event: 5.200212
- loss_text_aux: 0.278391
- loss_text_aux_effective: 0.278391
- loss_text_aux_structural: 0.36719
- loss_text_aux_lexical: 0.136313
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.182775
- z_art_delta_abs_mean: 0.000854
- event_prob_mean: 0.471091
- event_presence_prob_mean: 0.570258
- event_delta_prob_mean: 0.453186
- event_rise_prob_mean: 0.476268
- event_fall_prob_mean: 0.462355
- event_energy_prob_mean: 0.544582
- event_presence_peak_ratio: 1.0
- acoustic_abs_mean: 1.114443
- acoustic_energy_mean: -4.339282
- acoustic_delta_abs_mean: 0.007313
- text_aux_abs_mean: 0.333883

## 对比
- delta_loss_total: -3.218319
- delta_loss_acoustic: -3.277499
- delta_loss_event: 0.097353
- delta_loss_text_aux: 0.130777
- delta_loss_text_aux_effective: 0.130777
- delta_loss_text_aux_structural: 0.204539
- delta_loss_text_aux_lexical: 0.012759
- delta_loss_clause_transition_aux: -0.043135
- delta_z_art_abs_mean: 0.003864
- delta_z_art_delta_abs_mean: -0.000693
- delta_event_prob_mean: -0.00399
- delta_event_presence_prob_mean: -0.005454
- delta_event_delta_prob_mean: 0.003501
- delta_event_rise_prob_mean: -0.007652
- delta_event_fall_prob_mean: 0.004181
- delta_event_energy_prob_mean: -0.006042
- delta_event_presence_peak_ratio: 0.0
- delta_acoustic_abs_mean: 0.032377
- delta_acoustic_energy_mean: -0.150455
- delta_acoustic_delta_abs_mean: -0.011716
- delta_text_aux_abs_mean: 0.010677

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
