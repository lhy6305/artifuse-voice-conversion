# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d75_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_20step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-030-offline-mvp-d75-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-20step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [10, 20]
- checkpoint_count: 2

## checkpoints
### step 10
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d75_singleton_sparse_d26_init_d22late_fusedhidden_boost_exp030/checkpoints/EXP-20260316-030-offline-mvp-d75-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-20step-calibration.step10.pt
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
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d75_singleton_sparse_d26_init_d22late_fusedhidden_boost_exp030/checkpoints/EXP-20260316-030-offline-mvp-d75-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-20step-calibration.step20.pt
- target_validation.loss_total: 2.399272
- target_special_eval.loss_total: 2.566462
- delta_loss_total: 0.16719
- delta_loss_text_aux: 0.051401
- delta_loss_text_aux_effective: 0.051401
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.446899
- target_special_eval.event_prob_mean: 0.433066
- delta_event_presence_prob_mean: -0.039822
- delta_event_fall_prob_mean: 0.014453
- delta_event_energy_prob_mean: -0.032767
- delta_event_presence_peak_ratio: 0.140849
- delta_z_art_delta_abs_mean: -0.002477
- delta_acoustic_energy_mean: -0.195998
- delta_acoustic_delta_abs_mean: 0.001416

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
