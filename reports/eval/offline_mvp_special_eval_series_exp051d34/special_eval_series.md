# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d34_round1_1_d22_init_d33_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d34_d22_init_d33_teacher_cross_anchor_fused_hidden_exp051/checkpoints/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.step10.pt
- target_validation.loss_total: 2.386077
- target_special_eval.loss_total: 2.609793
- delta_loss_total: 0.223716
- delta_loss_text_aux: 0.074014
- delta_loss_text_aux_effective: 0.074014
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.445093
- target_special_eval.event_prob_mean: 0.430998
- delta_event_presence_prob_mean: -0.040632
- delta_event_fall_prob_mean: 0.014955
- delta_event_energy_prob_mean: -0.033756
- delta_event_presence_peak_ratio: 0.151987
- delta_z_art_delta_abs_mean: -0.002409
- delta_acoustic_energy_mean: -0.207551
- delta_acoustic_delta_abs_mean: -0.001175

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d34_d22_init_d33_teacher_cross_anchor_fused_hidden_exp051/checkpoints/EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration.step20.pt
- target_validation.loss_total: 2.3506
- target_special_eval.loss_total: 2.552136
- delta_loss_total: 0.201536
- delta_loss_text_aux: 0.072827
- delta_loss_text_aux_effective: 0.072827
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- target_validation.event_prob_mean: 0.442573
- target_special_eval.event_prob_mean: 0.42757
- delta_event_presence_prob_mean: -0.042611
- delta_event_fall_prob_mean: 0.014602
- delta_event_energy_prob_mean: -0.035706
- delta_event_presence_peak_ratio: 0.157673
- delta_z_art_delta_abs_mean: -0.002321
- delta_acoustic_energy_mean: -0.144969
- delta_acoustic_delta_abs_mean: -0.00387

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
