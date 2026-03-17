# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d27_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d27_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_exp044/checkpoints/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.step10.pt
- target_validation.loss_total: 2.573033
- target_special_eval.loss_total: 2.750789
- delta_loss_total: 0.177756
- delta_loss_text_aux: 0.08557
- delta_loss_text_aux_effective: 0.08557
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.453612
- target_special_eval.event_prob_mean: 0.440811
- delta_event_presence_prob_mean: -0.035571
- delta_event_fall_prob_mean: 0.015636
- delta_event_energy_prob_mean: -0.028894
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002693
- delta_acoustic_energy_mean: -0.472728
- delta_acoustic_delta_abs_mean: 0.002569

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d27_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_exp044/checkpoints/EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration.step20.pt
- target_validation.loss_total: 2.466208
- target_special_eval.loss_total: 2.672349
- delta_loss_total: 0.206141
- delta_loss_text_aux: 0.085689
- delta_loss_text_aux_effective: 0.085689
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451466
- target_special_eval.event_prob_mean: 0.438482
- delta_event_presence_prob_mean: -0.03676
- delta_event_fall_prob_mean: 0.015002
- delta_event_energy_prob_mean: -0.029949
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002532
- delta_acoustic_energy_mean: -0.341049
- delta_acoustic_delta_abs_mean: 0.005788

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
