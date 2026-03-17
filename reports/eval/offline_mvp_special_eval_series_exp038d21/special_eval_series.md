# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d21_round1_1_d10_final_consolidation_teacher_consistency_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 30]
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step10.pt
- target_validation.loss_total: 2.635733
- target_special_eval.loss_total: 2.798306
- delta_loss_total: 0.162573
- delta_loss_text_aux: 0.090407
- delta_loss_text_aux_effective: 0.090407
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.455895
- target_special_eval.event_prob_mean: 0.443111
- delta_event_presence_prob_mean: -0.03523
- delta_event_fall_prob_mean: 0.016082
- delta_event_energy_prob_mean: -0.028742
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.00277
- delta_acoustic_energy_mean: -0.551533
- delta_acoustic_delta_abs_mean: -0.000676

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step20.pt
- target_validation.loss_total: 2.523079
- target_special_eval.loss_total: 2.666242
- delta_loss_total: 0.143163
- delta_loss_text_aux: 0.080678
- delta_loss_text_aux_effective: 0.080678
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.454114
- target_special_eval.event_prob_mean: 0.44127
- delta_event_presence_prob_mean: -0.036034
- delta_event_fall_prob_mean: 0.01528
- delta_event_energy_prob_mean: -0.02938
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002563
- delta_acoustic_energy_mean: -0.383343
- delta_acoustic_delta_abs_mean: 0.000804

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d21_d10_final_consolidation_teacher_consistency_exp038/checkpoints/EXP-20260315-038-offline-mvp-d21-round1-1-d10-final-consolidation-teacher-consistency-30step-calibration.step30.pt
- target_validation.loss_total: 2.441712
- target_special_eval.loss_total: 2.623613
- delta_loss_total: 0.181901
- delta_loss_text_aux: 0.078005
- delta_loss_text_aux_effective: 0.078005
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451639
- target_special_eval.event_prob_mean: 0.438513
- delta_event_presence_prob_mean: -0.037669
- delta_event_fall_prob_mean: 0.015033
- delta_event_energy_prob_mean: -0.030817
- delta_event_presence_peak_ratio: 0.127213
- delta_z_art_delta_abs_mean: -0.002451
- delta_acoustic_energy_mean: -0.283381
- delta_acoustic_delta_abs_mean: 0.009509

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
