# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.522448
- loss_acoustic: 1.088889
- loss_event: 4.763571
- loss_text_aux: 0.122299
- loss_text_aux_effective: 0.12748
- loss_clause_transition_aux: 0.049486
- z_art_abs_mean: 0.272624
- z_art_delta_abs_mean: 0.011196
- event_prob_mean: 0.461253
- event_presence_prob_mean: 0.587833
- event_delta_prob_mean: 0.384705
- event_rise_prob_mean: 0.464806
- event_fall_prob_mean: 0.427409
- event_energy_prob_mean: 0.569336
- event_presence_peak_ratio: 0.770211
- acoustic_abs_mean: 0.80739
- acoustic_energy_mean: -3.040689
- acoustic_delta_abs_mean: 0.035158
- text_aux_abs_mean: 0.214249

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.241758
- loss_acoustic: 0.669749
- loss_event: 5.041528
- loss_text_aux: 0.209764
- loss_text_aux_effective: 0.225489
- loss_clause_transition_aux: 0.0
- z_art_abs_mean: 0.180096
- z_art_delta_abs_mean: 0.007685
- event_prob_mean: 0.448834
- event_presence_prob_mean: 0.556587
- event_delta_prob_mean: 0.399135
- event_rise_prob_mean: 0.444862
- event_fall_prob_mean: 0.446763
- event_energy_prob_mean: 0.542492
- event_presence_peak_ratio: 0.92344
- acoustic_abs_mean: 1.082893
- acoustic_energy_mean: -4.168395
- acoustic_delta_abs_mean: 0.016214
- text_aux_abs_mean: 0.268967

## 对比
- delta_loss_total: -0.28069
- delta_loss_acoustic: -0.41914
- delta_loss_event: 0.277957
- delta_loss_text_aux: 0.087465
- delta_loss_text_aux_effective: 0.098009
- delta_loss_clause_transition_aux: -0.049486
- delta_z_art_abs_mean: -0.092528
- delta_z_art_delta_abs_mean: -0.003511
- delta_event_prob_mean: -0.012419
- delta_event_presence_prob_mean: -0.031246
- delta_event_delta_prob_mean: 0.01443
- delta_event_rise_prob_mean: -0.019944
- delta_event_fall_prob_mean: 0.019354
- delta_event_energy_prob_mean: -0.026844
- delta_event_presence_peak_ratio: 0.153229
- delta_acoustic_abs_mean: 0.275503
- delta_acoustic_energy_mean: -1.127706
- delta_acoustic_delta_abs_mean: -0.018944
- delta_text_aux_abs_mean: 0.054718

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
