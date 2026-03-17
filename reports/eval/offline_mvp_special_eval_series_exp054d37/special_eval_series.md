# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d37_round1_1_d22_init_d33_step10_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d37_d22_init_d33step10_teacher_checkpoint_cross_anchor_fused_hidden_exp054/checkpoints/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.389709
- target_special_eval.loss_total: 2.613464
- delta_loss_total: 0.223755
- delta_loss_text_aux: 0.07434
- delta_loss_text_aux_effective: 0.07434
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.445362
- target_special_eval.event_prob_mean: 0.431254
- delta_event_presence_prob_mean: -0.040575
- delta_event_fall_prob_mean: 0.015052
- delta_event_energy_prob_mean: -0.033562
- delta_event_presence_peak_ratio: 0.153167
- delta_z_art_delta_abs_mean: -0.002369
- delta_acoustic_energy_mean: -0.211201
- delta_acoustic_delta_abs_mean: -0.001193

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d37_d22_init_d33step10_teacher_checkpoint_cross_anchor_fused_hidden_exp054/checkpoints/EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.35571
- target_special_eval.loss_total: 2.555409
- delta_loss_total: 0.199699
- delta_loss_text_aux: 0.073316
- delta_loss_text_aux_effective: 0.073316
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.443383
- target_special_eval.event_prob_mean: 0.428362
- delta_event_presence_prob_mean: -0.042446
- delta_event_fall_prob_mean: 0.014728
- delta_event_energy_prob_mean: -0.03542
- delta_event_presence_peak_ratio: 0.157517
- delta_z_art_delta_abs_mean: -0.002232
- delta_acoustic_energy_mean: -0.151294
- delta_acoustic_delta_abs_mean: -0.003895

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
