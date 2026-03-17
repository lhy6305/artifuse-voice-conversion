# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d25_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 30]
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step10.pt
- target_validation.loss_total: 2.620166
- target_special_eval.loss_total: 2.701583
- delta_loss_total: 0.081417
- delta_loss_text_aux: 0.080839
- delta_loss_text_aux_effective: 0.080839
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.45443
- target_special_eval.event_prob_mean: 0.441734
- delta_event_presence_prob_mean: -0.035332
- delta_event_fall_prob_mean: 0.01554
- delta_event_energy_prob_mean: -0.028697
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002682
- delta_acoustic_energy_mean: -0.453748
- delta_acoustic_delta_abs_mean: 0.000715

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step20.pt
- target_validation.loss_total: 2.523898
- target_special_eval.loss_total: 2.641792
- delta_loss_total: 0.117894
- delta_loss_text_aux: 0.071023
- delta_loss_text_aux_effective: 0.071023
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451974
- target_special_eval.event_prob_mean: 0.439099
- delta_event_presence_prob_mean: -0.03633
- delta_event_fall_prob_mean: 0.015067
- delta_event_energy_prob_mean: -0.029553
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.00253
- delta_acoustic_energy_mean: -0.344626
- delta_acoustic_delta_abs_mean: 0.008261

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d25_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp042/checkpoints/EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration.step30.pt
- target_validation.loss_total: 2.444897
- target_special_eval.loss_total: 2.621254
- delta_loss_total: 0.176357
- delta_loss_text_aux: 0.078017
- delta_loss_text_aux_effective: 0.078017
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.450686
- target_special_eval.event_prob_mean: 0.437499
- delta_event_presence_prob_mean: -0.03747
- delta_event_fall_prob_mean: 0.014749
- delta_event_energy_prob_mean: -0.030571
- delta_event_presence_peak_ratio: 0.127511
- delta_z_art_delta_abs_mean: -0.002409
- delta_acoustic_energy_mean: -0.288013
- delta_acoustic_delta_abs_mean: 0.007701

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
