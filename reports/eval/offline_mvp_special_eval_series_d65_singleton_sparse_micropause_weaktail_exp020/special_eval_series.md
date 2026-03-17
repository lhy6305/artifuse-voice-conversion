# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d65_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_weaktail_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-020-offline-mvp-d65-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-weaktail-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d65_singleton_sparse_micropause_weaktail_exp020/checkpoints/EXP-20260316-020-offline-mvp-d65-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-weaktail-20step-calibration.step10.pt
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

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d65_singleton_sparse_micropause_weaktail_exp020/checkpoints/EXP-20260316-020-offline-mvp-d65-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-weaktail-20step-calibration.step20.pt
- target_validation.loss_total: 2.482579
- target_special_eval.loss_total: 2.655026
- delta_loss_total: 0.172447
- delta_loss_text_aux: 0.067937
- delta_loss_text_aux_effective: 0.067937
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.450791
- target_special_eval.event_prob_mean: 0.437751
- delta_event_presence_prob_mean: -0.037104
- delta_event_fall_prob_mean: 0.015147
- delta_event_energy_prob_mean: -0.03016
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002673
- delta_acoustic_energy_mean: -0.350341
- delta_acoustic_delta_abs_mean: 0.006019

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
