# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d30_round1_1_d26_init_d22_teacher_cross_anchor_event_only_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d30_d26_init_d22_teacher_cross_anchor_event_only_exp047/checkpoints/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.step10.pt
- target_validation.loss_total: 2.433206
- target_special_eval.loss_total: 2.641373
- delta_loss_total: 0.208167
- delta_loss_text_aux: 0.068678
- delta_loss_text_aux_effective: 0.068678
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.447556
- target_special_eval.event_prob_mean: 0.434136
- delta_event_presence_prob_mean: -0.038633
- delta_event_fall_prob_mean: 0.015079
- delta_event_energy_prob_mean: -0.03173
- delta_event_presence_peak_ratio: 0.138476
- delta_z_art_delta_abs_mean: -0.002593
- delta_acoustic_energy_mean: -0.297621
- delta_acoustic_delta_abs_mean: 0.003403

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d30_d26_init_d22_teacher_cross_anchor_event_only_exp047/checkpoints/EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration.step20.pt
- target_validation.loss_total: 2.399277
- target_special_eval.loss_total: 2.569025
- delta_loss_total: 0.169748
- delta_loss_text_aux: 0.055707
- delta_loss_text_aux_effective: 0.055707
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.444871
- target_special_eval.event_prob_mean: 0.430934
- delta_event_presence_prob_mean: -0.040132
- delta_event_fall_prob_mean: 0.014638
- delta_event_energy_prob_mean: -0.033163
- delta_event_presence_peak_ratio: 0.142607
- delta_z_art_delta_abs_mean: -0.002548
- delta_acoustic_energy_mean: -0.188016
- delta_acoustic_delta_abs_mean: 0.001767

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
