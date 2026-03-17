# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d62_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_30step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-018-offline-mvp-d62-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 30]
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d62_d22_singleton_latepulse_exp018/checkpoints/EXP-20260316-018-offline-mvp-d62-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-30step-calibration.step10.pt
- target_validation.loss_total: 2.592379
- target_special_eval.loss_total: 2.766794
- delta_loss_total: 0.174415
- delta_loss_text_aux: 0.090788
- delta_loss_text_aux_effective: 0.090788
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.454665
- target_special_eval.event_prob_mean: 0.441824
- delta_event_presence_prob_mean: -0.035616
- delta_event_fall_prob_mean: 0.015706
- delta_event_energy_prob_mean: -0.028977
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002717
- delta_acoustic_energy_mean: -0.50282
- delta_acoustic_delta_abs_mean: 0.004646

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d62_d22_singleton_latepulse_exp018/checkpoints/EXP-20260316-018-offline-mvp-d62-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-30step-calibration.step20.pt
- target_validation.loss_total: 2.51054
- target_special_eval.loss_total: 2.673242
- delta_loss_total: 0.162702
- delta_loss_text_aux: 0.074489
- delta_loss_text_aux_effective: 0.074489
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.452777
- target_special_eval.event_prob_mean: 0.439688
- delta_event_presence_prob_mean: -0.036849
- delta_event_fall_prob_mean: 0.015184
- delta_event_energy_prob_mean: -0.030042
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.0026
- delta_acoustic_energy_mean: -0.373499
- delta_acoustic_delta_abs_mean: 0.007052

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d62_d22_singleton_latepulse_exp018/checkpoints/EXP-20260316-018-offline-mvp-d62-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-singleton-sparse-latepulse-30step-calibration.step30.pt
- target_validation.loss_total: 2.42375
- target_special_eval.loss_total: 2.657798
- delta_loss_total: 0.234048
- delta_loss_text_aux: 0.068331
- delta_loss_text_aux_effective: 0.068331
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.450264
- target_special_eval.event_prob_mean: 0.43678
- delta_event_presence_prob_mean: -0.038538
- delta_event_fall_prob_mean: 0.014706
- delta_event_energy_prob_mean: -0.031549
- delta_event_presence_peak_ratio: 0.137939
- delta_z_art_delta_abs_mean: -0.002426
- delta_acoustic_energy_mean: -0.286337
- delta_acoustic_delta_abs_mean: 0.002151

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
