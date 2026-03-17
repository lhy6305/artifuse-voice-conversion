# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d64_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_shorttail_15step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [5, 10, 15]
- checkpoint_count: 3

## checkpoints
### step 5
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step5.pt
- target_validation.loss_total: 2.629542
- target_special_eval.loss_total: 2.766957
- delta_loss_total: 0.137415
- delta_loss_text_aux: 0.104161
- delta_loss_text_aux_effective: 0.104161
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.456114
- target_special_eval.event_prob_mean: 0.443529
- delta_event_presence_prob_mean: -0.034505
- delta_event_fall_prob_mean: 0.015605
- delta_event_energy_prob_mean: -0.027891
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002684
- delta_acoustic_energy_mean: -0.531719
- delta_acoustic_delta_abs_mean: 0.002046

### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step10.pt
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
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.454702
- target_special_eval.event_prob_mean: 0.441931
- delta_event_presence_prob_mean: -0.035612
- delta_event_fall_prob_mean: 0.015585
- delta_event_energy_prob_mean: -0.028852
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.00272
- delta_acoustic_energy_mean: -0.479389
- delta_acoustic_delta_abs_mean: 0.003829

### step 15
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d64_singleton_sparse_micropause_shorttail_exp019/checkpoints/EXP-20260316-019-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration.step15.pt
- target_validation.loss_total: 2.539564
- target_special_eval.loss_total: 2.693567
- delta_loss_total: 0.154003
- delta_loss_text_aux: 0.076693
- delta_loss_text_aux_effective: 0.076693
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.453121
- target_special_eval.event_prob_mean: 0.440238
- delta_event_presence_prob_mean: -0.036319
- delta_event_fall_prob_mean: 0.015402
- delta_event_energy_prob_mean: -0.029471
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002709
- delta_acoustic_energy_mean: -0.417884
- delta_acoustic_delta_abs_mean: 0.001319

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
