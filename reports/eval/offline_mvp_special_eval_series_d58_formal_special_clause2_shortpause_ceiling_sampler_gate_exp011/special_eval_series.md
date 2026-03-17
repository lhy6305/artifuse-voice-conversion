# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d58_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_gate_late_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-011-offline-mvp-d58-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-gate-late-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d58_formal_special_clause2_shortpause_ceiling_sampler_gate_exp011/checkpoints/EXP-20260316-011-offline-mvp-d58-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-gate-late-20step-calibration.step10.pt
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
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d58_formal_special_clause2_shortpause_ceiling_sampler_gate_exp011/checkpoints/EXP-20260316-011-offline-mvp-d58-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-gate-late-20step-calibration.step20.pt
- target_validation.loss_total: 2.480056
- target_special_eval.loss_total: 2.651854
- delta_loss_total: 0.171798
- delta_loss_text_aux: 0.066209
- delta_loss_text_aux_effective: 0.066209
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.451315
- target_special_eval.event_prob_mean: 0.43827
- delta_event_presence_prob_mean: -0.036996
- delta_event_fall_prob_mean: 0.015135
- delta_event_energy_prob_mean: -0.030038
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002659
- delta_acoustic_energy_mean: -0.345474
- delta_acoustic_delta_abs_mean: 0.007081

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
