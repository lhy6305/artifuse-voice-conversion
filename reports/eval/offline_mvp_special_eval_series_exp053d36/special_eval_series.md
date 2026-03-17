# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d36_round1_1_d33_step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d36_d33step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_exp053/checkpoints/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.511061
- target_special_eval.loss_total: 2.640756
- delta_loss_total: 0.129695
- delta_loss_text_aux: 0.072928
- delta_loss_text_aux_effective: 0.072928
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.450358
- target_special_eval.event_prob_mean: 0.437343
- delta_event_presence_prob_mean: -0.036712
- delta_event_fall_prob_mean: 0.015153
- delta_event_energy_prob_mean: -0.029825
- delta_event_presence_peak_ratio: 0.0
- delta_z_art_delta_abs_mean: -0.002619
- delta_acoustic_energy_mean: -0.34683
- delta_acoustic_delta_abs_mean: 0.003733

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d36_d33step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_exp053/checkpoints/EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.450632
- target_special_eval.loss_total: 2.595293
- delta_loss_total: 0.144661
- delta_loss_text_aux: 0.065503
- delta_loss_text_aux_effective: 0.065503
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.447367
- target_special_eval.event_prob_mean: 0.433987
- delta_event_presence_prob_mean: -0.038187
- delta_event_fall_prob_mean: 0.014954
- delta_event_energy_prob_mean: -0.031185
- delta_event_presence_peak_ratio: 0.127721
- delta_z_art_delta_abs_mean: -0.002581
- delta_acoustic_energy_mean: -0.251308
- delta_acoustic_delta_abs_mean: 0.009003

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
