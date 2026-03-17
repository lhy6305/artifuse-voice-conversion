# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d35_round1_1_d33_init_d22_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d35_d33_init_d22_teacher_cross_anchor_fused_hidden_exp052/checkpoints/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.433376
- target_special_eval.loss_total: 2.637673
- delta_loss_total: 0.204297
- delta_loss_text_aux: 0.067785
- delta_loss_text_aux_effective: 0.067785
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.447735
- target_special_eval.event_prob_mean: 0.434333
- delta_event_presence_prob_mean: -0.038574
- delta_event_fall_prob_mean: 0.015042
- delta_event_energy_prob_mean: -0.031659
- delta_event_presence_peak_ratio: 0.136671
- delta_z_art_delta_abs_mean: -0.002598
- delta_acoustic_energy_mean: -0.295503
- delta_acoustic_delta_abs_mean: 0.002676

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d35_d33_init_d22_teacher_cross_anchor_fused_hidden_exp052/checkpoints/EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.395609
- target_special_eval.loss_total: 2.569152
- delta_loss_total: 0.173543
- delta_loss_text_aux: 0.055202
- delta_loss_text_aux_effective: 0.055202
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.445
- target_special_eval.event_prob_mean: 0.431069
- delta_event_presence_prob_mean: -0.040166
- delta_event_fall_prob_mean: 0.014611
- delta_event_energy_prob_mean: -0.033163
- delta_event_presence_peak_ratio: 0.142949
- delta_z_art_delta_abs_mean: -0.002555
- delta_acoustic_energy_mean: -0.188162
- delta_acoustic_delta_abs_mean: 0.002101

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
