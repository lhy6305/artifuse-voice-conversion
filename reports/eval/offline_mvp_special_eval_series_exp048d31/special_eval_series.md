# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d31_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_acoustic_smallscale_30_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20, 30]
- checkpoint_count: 3

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step10.pt
- target_validation.loss_total: 2.593177
- target_special_eval.loss_total: 2.730014
- delta_loss_total: 0.136837
- delta_loss_text_aux: 0.088363
- delta_loss_text_aux_effective: 0.088363
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.453844
- target_special_eval.event_prob_mean: 0.441062
- delta_event_presence_prob_mean: -0.035539
- delta_event_fall_prob_mean: 0.015744
- delta_event_energy_prob_mean: -0.028941
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002708
- delta_acoustic_energy_mean: -0.469877
- delta_acoustic_delta_abs_mean: 0.00069

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step20.pt
- target_validation.loss_total: 2.472389
- target_special_eval.loss_total: 2.644928
- delta_loss_total: 0.172539
- delta_loss_text_aux: 0.082511
- delta_loss_text_aux_effective: 0.082511
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.451573
- target_special_eval.event_prob_mean: 0.438601
- delta_event_presence_prob_mean: -0.036734
- delta_event_fall_prob_mean: 0.015103
- delta_event_energy_prob_mean: -0.029959
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002509
- delta_acoustic_energy_mean: -0.327882
- delta_acoustic_delta_abs_mean: 0.001871

### step 30
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d31_d7_init_d10_teacher_consistency_acoustic_exp048/checkpoints/EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration.step30.pt
- target_validation.loss_total: 2.442793
- target_special_eval.loss_total: 2.585265
- delta_loss_total: 0.142472
- delta_loss_text_aux: 0.074013
- delta_loss_text_aux_effective: 0.074013
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.450181
- target_special_eval.event_prob_mean: 0.43691
- delta_event_presence_prob_mean: -0.038066
- delta_event_fall_prob_mean: 0.014734
- delta_event_energy_prob_mean: -0.031158
- delta_event_presence_peak_ratio: 0.131456
- delta_z_art_delta_abs_mean: -0.002334
- delta_acoustic_energy_mean: -0.213587
- delta_acoustic_delta_abs_mean: 0.010867

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
