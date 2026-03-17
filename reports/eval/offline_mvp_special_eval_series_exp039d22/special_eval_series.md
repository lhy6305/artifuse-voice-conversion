# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d22_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 30]
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_d7_init_d10_teacher_consolidation_teacher_consistency_exp039/checkpoints/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.step10.pt
- target_validation.loss_total: 2.592393
- target_special_eval.loss_total: 2.727557
- delta_loss_total: 0.135164
- delta_loss_text_aux: 0.088415
- delta_loss_text_aux_effective: 0.088415
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.45389
- target_special_eval.event_prob_mean: 0.441118
- delta_event_presence_prob_mean: -0.035513
- delta_event_fall_prob_mean: 0.01572
- delta_event_energy_prob_mean: -0.028909
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002704
- delta_acoustic_energy_mean: -0.467673
- delta_acoustic_delta_abs_mean: 0.000603

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_d7_init_d10_teacher_consolidation_teacher_consistency_exp039/checkpoints/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.step20.pt
- target_validation.loss_total: 2.470626
- target_special_eval.loss_total: 2.648727
- delta_loss_total: 0.178101
- delta_loss_text_aux: 0.083416
- delta_loss_text_aux_effective: 0.083416
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451622
- target_special_eval.event_prob_mean: 0.438651
- delta_event_presence_prob_mean: -0.036747
- delta_event_fall_prob_mean: 0.01511
- delta_event_energy_prob_mean: -0.029959
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002513
- delta_acoustic_energy_mean: -0.329678
- delta_acoustic_delta_abs_mean: 0.001652

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_d7_init_d10_teacher_consolidation_teacher_consistency_exp039/checkpoints/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.step30.pt
- target_validation.loss_total: 2.444194
- target_special_eval.loss_total: 2.584195
- delta_loss_total: 0.140001
- delta_loss_text_aux: 0.075322
- delta_loss_text_aux_effective: 0.075322
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.450378
- target_special_eval.event_prob_mean: 0.437157
- delta_event_presence_prob_mean: -0.037921
- delta_event_fall_prob_mean: 0.014681
- delta_event_energy_prob_mean: -0.031008
- delta_event_presence_peak_ratio: 0.130426
- delta_z_art_delta_abs_mean: -0.002327
- delta_acoustic_energy_mean: -0.213629
- delta_acoustic_delta_abs_mean: 0.011369

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
