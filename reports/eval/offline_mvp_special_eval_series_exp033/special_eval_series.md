# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 50, 100]
- checkpoint_count: 4

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step10.pt
- target_validation.loss_total: 19.575129
- target_special_eval.loss_total: 15.834148
- delta_loss_total: -3.740981
- delta_loss_text_aux: -0.038913
- target_validation.event_prob_mean: 0.500487
- target_special_eval.event_prob_mean: 0.500095
- delta_event_presence_prob_mean: -0.001075
- delta_event_fall_prob_mean: -0.001014
- delta_event_energy_prob_mean: -0.000537
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.000207
- delta_acoustic_energy_mean: -0.003341
- delta_acoustic_delta_abs_mean: 0.001526

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step20.pt
- target_validation.loss_total: 15.687762
- target_special_eval.loss_total: 11.837738
- delta_loss_total: -3.850024
- delta_loss_text_aux: 0.029155
- target_validation.event_prob_mean: 0.492228
- target_special_eval.event_prob_mean: 0.491427
- delta_event_presence_prob_mean: -0.001103
- delta_event_fall_prob_mean: -0.001149
- delta_event_energy_prob_mean: -0.00093
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.000348
- delta_acoustic_energy_mean: -0.005525
- delta_acoustic_delta_abs_mean: 0.002013

### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step50.pt
- target_validation.loss_total: 9.662671
- target_special_eval.loss_total: 5.611953
- delta_loss_total: -4.050718
- delta_loss_text_aux: 0.242159
- target_validation.event_prob_mean: 0.461188
- target_special_eval.event_prob_mean: 0.458307
- delta_event_presence_prob_mean: -0.001947
- delta_event_fall_prob_mean: -0.002636
- delta_event_energy_prob_mean: -0.001346
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.000653
- delta_acoustic_energy_mean: -0.040218
- delta_acoustic_delta_abs_mean: 0.001762

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.step100.pt
- target_validation.loss_total: 2.663196
- target_special_eval.loss_total: 2.774738
- delta_loss_total: 0.111542
- delta_loss_text_aux: 0.130491
- target_validation.event_prob_mean: 0.442438
- target_special_eval.event_prob_mean: 0.433759
- delta_event_presence_prob_mean: -0.01913
- delta_event_fall_prob_mean: -0.011684
- delta_event_energy_prob_mean: -0.017652
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.001288
- delta_acoustic_energy_mean: -0.57932
- delta_acoustic_delta_abs_mean: -0.004017

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
