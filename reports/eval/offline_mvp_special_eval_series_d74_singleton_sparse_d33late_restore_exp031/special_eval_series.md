# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d74_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_late_d33step10_teacher_restore_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d74_singleton_sparse_d26_init_d33late_restore_exp031/checkpoints/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.step10.pt
- target_validation.loss_total: 2.442652
- target_special_eval.loss_total: 2.613796
- delta_loss_total: 0.171144
- delta_loss_text_aux: 0.06828
- delta_loss_text_aux_effective: 0.06828
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.449992
- target_special_eval.event_prob_mean: 0.436607
- delta_event_presence_prob_mean: -0.038216
- delta_event_fall_prob_mean: 0.014864
- delta_event_energy_prob_mean: -0.031335
- delta_event_presence_peak_ratio: 0.129323
- delta_z_art_delta_abs_mean: -0.002522
- delta_acoustic_energy_mean: -0.277883
- delta_acoustic_delta_abs_mean: 0.004308

### step 20
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d74_singleton_sparse_d26_init_d33late_restore_exp031/checkpoints/EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration.step20.pt
- target_validation.loss_total: 2.401255
- target_special_eval.loss_total: 2.56938
- delta_loss_total: 0.168125
- delta_loss_text_aux: 0.051768
- delta_loss_text_aux_effective: 0.051768
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.447362
- target_special_eval.event_prob_mean: 0.433491
- delta_event_presence_prob_mean: -0.039858
- delta_event_fall_prob_mean: 0.014534
- delta_event_energy_prob_mean: -0.032779
- delta_event_presence_peak_ratio: 0.145071
- delta_z_art_delta_abs_mean: -0.002439
- delta_acoustic_energy_mean: -0.19854
- delta_acoustic_delta_abs_mean: 0.000486

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
