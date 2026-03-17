# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d42_round1_1_d7_init_phase_teacher_source_handoff_d33step10_to_d22_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d42_phase_teacher_source_handoff_exp059/checkpoints/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.61436
- target_special_eval.loss_total: 2.699833
- delta_loss_total: 0.085473
- delta_loss_text_aux: 0.080641
- delta_loss_text_aux_effective: 0.080641
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.454148
- target_special_eval.event_prob_mean: 0.441435
- delta_event_presence_prob_mean: -0.03547
- delta_event_fall_prob_mean: 0.015544
- delta_event_energy_prob_mean: -0.028752
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002718
- delta_acoustic_energy_mean: -0.451967
- delta_acoustic_delta_abs_mean: 0.000736

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d42_phase_teacher_source_handoff_exp059/checkpoints/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.488031
- target_special_eval.loss_total: 2.647471
- delta_loss_total: 0.15944
- delta_loss_text_aux: 0.083679
- delta_loss_text_aux_effective: 0.083679
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451118
- target_special_eval.event_prob_mean: 0.438187
- delta_event_presence_prob_mean: -0.03661
- delta_event_fall_prob_mean: 0.015061
- delta_event_energy_prob_mean: -0.029704
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002617
- delta_acoustic_energy_mean: -0.347296
- delta_acoustic_delta_abs_mean: 0.007199

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
