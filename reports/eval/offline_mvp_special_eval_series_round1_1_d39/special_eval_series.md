# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d39_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d39_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_exp056/checkpoints/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.592867
- target_special_eval.loss_total: 2.730311
- delta_loss_total: 0.137444
- delta_loss_text_aux: 0.08859
- delta_loss_text_aux_effective: 0.08859
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.45385
- target_special_eval.event_prob_mean: 0.441072
- delta_event_presence_prob_mean: -0.035527
- delta_event_fall_prob_mean: 0.015738
- delta_event_energy_prob_mean: -0.028932
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002707
- delta_acoustic_energy_mean: -0.470316
- delta_acoustic_delta_abs_mean: 0.000763

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d39_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_exp056/checkpoints/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.489906
- target_special_eval.loss_total: 2.659013
- delta_loss_total: 0.169107
- delta_loss_text_aux: 0.082523
- delta_loss_text_aux_effective: 0.082523
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.45183
- target_special_eval.event_prob_mean: 0.438867
- delta_event_presence_prob_mean: -0.036606
- delta_event_fall_prob_mean: 0.015176
- delta_event_energy_prob_mean: -0.029874
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002551
- delta_acoustic_energy_mean: -0.352856
- delta_acoustic_delta_abs_mean: 0.005055

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
