# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d28_round1_1_d22_init_d26_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d28_d22_init_d26_teacher_cross_anchor_consolidation_exp046/checkpoints/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.step10.pt
- target_validation.loss_total: 2.384933
- target_special_eval.loss_total: 2.60716
- delta_loss_total: 0.222227
- delta_loss_text_aux: 0.073512
- delta_loss_text_aux_effective: 0.073512
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.445114
- target_special_eval.event_prob_mean: 0.431027
- delta_event_presence_prob_mean: -0.040623
- delta_event_fall_prob_mean: 0.014952
- delta_event_energy_prob_mean: -0.033738
- delta_event_presence_peak_ratio: 0.152599
- delta_z_art_delta_abs_mean: -0.002406
- delta_acoustic_energy_mean: -0.204504
- delta_acoustic_delta_abs_mean: -0.000631

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d28_d22_init_d26_teacher_cross_anchor_consolidation_exp046/checkpoints/EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration.step20.pt
- target_validation.loss_total: 2.349798
- target_special_eval.loss_total: 2.550217
- delta_loss_total: 0.200419
- delta_loss_text_aux: 0.072007
- delta_loss_text_aux_effective: 0.072007
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.442563
- target_special_eval.event_prob_mean: 0.427558
- delta_event_presence_prob_mean: -0.042646
- delta_event_fall_prob_mean: 0.014608
- delta_event_energy_prob_mean: -0.035721
- delta_event_presence_peak_ratio: 0.157036
- delta_z_art_delta_abs_mean: -0.002321
- delta_acoustic_energy_mean: -0.139012
- delta_acoustic_delta_abs_mean: -0.003561

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
