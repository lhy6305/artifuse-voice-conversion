# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d41_round1_1_d7_init_d10_teacher_consistency_phase_teacher_gate_target_handoff_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d41_phase_teacher_gate_target_handoff_exp058/checkpoints/EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.621019
- target_special_eval.loss_total: 2.702524
- delta_loss_total: 0.081505
- delta_loss_text_aux: 0.080833
- delta_loss_text_aux_effective: 0.080833
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.454433
- target_special_eval.event_prob_mean: 0.441732
- delta_event_presence_prob_mean: -0.035339
- delta_event_fall_prob_mean: 0.015552
- delta_event_energy_prob_mean: -0.028711
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002683
- delta_acoustic_energy_mean: -0.455079
- delta_acoustic_delta_abs_mean: 0.000799

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d41_phase_teacher_gate_target_handoff_exp058/checkpoints/EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.493233
- target_special_eval.loss_total: 2.65683
- delta_loss_total: 0.163597
- delta_loss_text_aux: 0.085685
- delta_loss_text_aux_effective: 0.085685
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.452396
- target_special_eval.event_prob_mean: 0.439523
- delta_event_presence_prob_mean: -0.036336
- delta_event_fall_prob_mean: 0.015021
- delta_event_energy_prob_mean: -0.029555
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002502
- delta_acoustic_energy_mean: -0.354932
- delta_acoustic_delta_abs_mean: 0.007357

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
