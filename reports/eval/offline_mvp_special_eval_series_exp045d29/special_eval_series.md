# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d29_round1_1_d26_init_d22_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt
- target_validation.loss_total: 2.432519
- target_special_eval.loss_total: 2.639976
- delta_loss_total: 0.207457
- delta_loss_text_aux: 0.068589
- delta_loss_text_aux_effective: 0.068589
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.447605
- target_special_eval.event_prob_mean: 0.434185
- delta_event_presence_prob_mean: -0.038664
- delta_event_fall_prob_mean: 0.015082
- delta_event_energy_prob_mean: -0.031724
- delta_event_presence_peak_ratio: 0.137897
- delta_z_art_delta_abs_mean: -0.002611
- delta_acoustic_energy_mean: -0.29587
- delta_acoustic_delta_abs_mean: 0.003437

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step20.pt
- target_validation.loss_total: 2.397175
- target_special_eval.loss_total: 2.568944
- delta_loss_total: 0.171769
- delta_loss_text_aux: 0.055737
- delta_loss_text_aux_effective: 0.055737
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.444938
- target_special_eval.event_prob_mean: 0.431001
- delta_event_presence_prob_mean: -0.040206
- delta_event_fall_prob_mean: 0.014644
- delta_event_energy_prob_mean: -0.03318
- delta_event_presence_peak_ratio: 0.142887
- delta_z_art_delta_abs_mean: -0.002564
- delta_acoustic_energy_mean: -0.187651
- delta_acoustic_delta_abs_mean: 0.001326

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
