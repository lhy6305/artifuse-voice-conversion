# offline MVP target_special_eval 模型级评估

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration.step90.pt
- split_option_name: hybrid_stratified_blocked

## target_validation
- record_count: 66
- batch_count: 17
- loss_total: 3.53397
- loss_acoustic: 1.090062
- loss_event: 4.762654
- loss_text_aux: 0.118294
- loss_text_aux_effective: 0.118294
- loss_text_aux_structural: 0.125964
- loss_text_aux_lexical: 0.106023
- loss_clause_transition_aux: 0.049518
- loss_boundary_contrast_aux: 0.050434
- z_art_abs_mean: 0.272299
- z_art_delta_abs_mean: 0.011229
- event_prob_mean: 0.461019
- event_presence_prob_mean: 0.587562
- event_delta_prob_mean: 0.384786
- event_rise_prob_mean: 0.463554
- event_fall_prob_mean: 0.42684
- event_energy_prob_mean: 0.569947
- event_presence_peak_ratio: 0.769434
- acoustic_abs_mean: 0.804951
- acoustic_energy_mean: -3.039349
- acoustic_delta_abs_mean: 0.037521
- text_aux_abs_mean: 0.199909

## target_special_eval
- record_count: 8
- batch_count: 2
- loss_total: 3.227442
- loss_acoustic: 0.667469
- loss_event: 5.041191
- loss_text_aux: 0.166063
- loss_text_aux_effective: 0.166063
- loss_text_aux_structural: 0.230799
- loss_text_aux_lexical: 0.062486
- loss_clause_transition_aux: 0.0
- loss_boundary_contrast_aux: 0.0
- z_art_abs_mean: 0.179447
- z_art_delta_abs_mean: 0.007706
- event_prob_mean: 0.448636
- event_presence_prob_mean: 0.556381
- event_delta_prob_mean: 0.399187
- event_rise_prob_mean: 0.444028
- event_fall_prob_mean: 0.446322
- event_energy_prob_mean: 0.542853
- event_presence_peak_ratio: 0.92344
- acoustic_abs_mean: 1.08016
- acoustic_energy_mean: -4.164681
- acoustic_delta_abs_mean: 0.014879
- text_aux_abs_mean: 0.247454

## 对比
- delta_loss_total: -0.306528
- delta_loss_acoustic: -0.422593
- delta_loss_event: 0.278537
- delta_loss_text_aux: 0.047769
- delta_loss_text_aux_effective: 0.047769
- delta_loss_text_aux_structural: 0.104835
- delta_loss_text_aux_lexical: -0.043537
- delta_loss_clause_transition_aux: -0.049518
- delta_loss_boundary_contrast_aux: -0.050434
- delta_z_art_abs_mean: -0.092852
- delta_z_art_delta_abs_mean: -0.003523
- delta_event_prob_mean: -0.012383
- delta_event_presence_prob_mean: -0.031181
- delta_event_delta_prob_mean: 0.014401
- delta_event_rise_prob_mean: -0.019526
- delta_event_fall_prob_mean: 0.019482
- delta_event_energy_prob_mean: -0.027094
- delta_event_presence_peak_ratio: 0.154006
- delta_acoustic_abs_mean: 0.275209
- delta_acoustic_energy_mean: -1.125332
- delta_acoustic_delta_abs_mean: -0.022642
- delta_text_aux_abs_mean: 0.047545

## 备注
- Model-level special_eval is reported separately from regular validation.
- Current target_special_eval remains a punctuation-only challenge slice from no_text_voice.
- Loss comparisons here indicate relative stress behavior on the current checkpoint, not final model quality.
