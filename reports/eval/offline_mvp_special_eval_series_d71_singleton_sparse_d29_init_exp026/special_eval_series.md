# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d71_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d71_singleton_sparse_d29_init_exp026/checkpoints/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.step10.pt
- target_validation.loss_total: 2.36262
- target_special_eval.loss_total: 2.583934
- delta_loss_total: 0.221314
- delta_loss_text_aux: 0.065727
- delta_loss_text_aux_effective: 0.065727
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.444696
- target_special_eval.event_prob_mean: 0.4299
- delta_event_presence_prob_mean: -0.042282
- delta_event_fall_prob_mean: 0.01467
- delta_event_energy_prob_mean: -0.035178
- delta_event_presence_peak_ratio: 0.153048
- delta_z_art_delta_abs_mean: -0.002538
- delta_acoustic_energy_mean: -0.187329
- delta_acoustic_delta_abs_mean: 0.005549

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d71_singleton_sparse_d29_init_exp026/checkpoints/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.step20.pt
- target_validation.loss_total: 2.340197
- target_special_eval.loss_total: 2.531165
- delta_loss_total: 0.190968
- delta_loss_text_aux: 0.047404
- delta_loss_text_aux_effective: 0.047404
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.441998
- target_special_eval.event_prob_mean: 0.426365
- delta_event_presence_prob_mean: -0.044198
- delta_event_fall_prob_mean: 0.014206
- delta_event_energy_prob_mean: -0.036925
- delta_event_presence_peak_ratio: 0.158689
- delta_z_art_delta_abs_mean: -0.002446
- delta_acoustic_energy_mean: -0.135317
- delta_acoustic_delta_abs_mean: 0.00111

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
