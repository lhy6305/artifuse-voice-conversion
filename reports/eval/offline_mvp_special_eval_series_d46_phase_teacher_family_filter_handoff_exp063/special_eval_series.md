# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d46_round1_1_d7_init_phase_teacher_family_filter_handoff_d33step10_to_d29_relaxed_none_other_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-063-offline-mvp-d46-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d46_phase_teacher_family_filter_handoff_exp063/checkpoints/EXP-20260316-063-offline-mvp-d46-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-20step-calibration.step10.pt
- target_validation.loss_total: 2.578968
- target_special_eval.loss_total: 2.740144
- delta_loss_total: 0.161176
- delta_loss_text_aux: 0.090726
- delta_loss_text_aux_effective: 0.090726
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.454702
- target_special_eval.event_prob_mean: 0.441931
- delta_event_presence_prob_mean: -0.035612
- delta_event_fall_prob_mean: 0.015585
- delta_event_energy_prob_mean: -0.028852
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.00272
- delta_acoustic_energy_mean: -0.479389
- delta_acoustic_delta_abs_mean: 0.003829

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d46_phase_teacher_family_filter_handoff_exp063/checkpoints/EXP-20260316-063-offline-mvp-d46-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-20step-calibration.step20.pt
- target_validation.loss_total: 2.484944
- target_special_eval.loss_total: 2.643446
- delta_loss_total: 0.158502
- delta_loss_text_aux: 0.077713
- delta_loss_text_aux_effective: 0.077713
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451621
- target_special_eval.event_prob_mean: 0.438649
- delta_event_presence_prob_mean: -0.036785
- delta_event_fall_prob_mean: 0.014957
- delta_event_energy_prob_mean: -0.029859
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002656
- delta_acoustic_energy_mean: -0.341321
- delta_acoustic_delta_abs_mean: 0.008219

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
