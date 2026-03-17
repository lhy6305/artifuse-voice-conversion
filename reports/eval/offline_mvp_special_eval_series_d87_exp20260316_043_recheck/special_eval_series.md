# offline MVP special_eval checkpoint 系列汇总

- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d87_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_lateretention_200step_smallscale_seeded_shuffle.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- selected_steps: [50, 100, 150, 200]
- checkpoint_count: 4

## checkpoints
### step 50
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step50.pt
- target_validation.loss_total: 2.310971
- target_special_eval.loss_total: 2.495879
- delta_loss_total: 0.184908
- delta_loss_text_aux: 0.018749
- delta_loss_text_aux_effective: 0.018749
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.44183
- target_special_eval.event_prob_mean: 0.42463
- delta_event_presence_prob_mean: -0.047628
- delta_event_fall_prob_mean: 0.015242
- delta_event_energy_prob_mean: -0.039926
- delta_event_presence_peak_ratio: 0.15202
- delta_z_art_delta_abs_mean: -0.002299
- delta_acoustic_energy_mean: -0.09518
- delta_acoustic_delta_abs_mean: -0.002899

### step 100
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step100.pt
- target_validation.loss_total: 2.214611
- target_special_eval.loss_total: 2.422773
- delta_loss_total: 0.208162
- delta_loss_text_aux: -0.006606
- delta_loss_text_aux_effective: -0.006606
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.435211
- target_special_eval.event_prob_mean: 0.410661
- delta_event_presence_prob_mean: -0.061789
- delta_event_fall_prob_mean: 0.01688
- delta_event_energy_prob_mean: -0.054172
- delta_event_presence_peak_ratio: 0.005594
- delta_z_art_delta_abs_mean: -0.00149
- delta_acoustic_energy_mean: -0.095189
- delta_acoustic_delta_abs_mean: -0.000125

### step 150
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step150.pt
- target_validation.loss_total: 2.167991
- target_special_eval.loss_total: 2.389851
- delta_loss_total: 0.22186
- delta_loss_text_aux: -0.005771
- delta_loss_text_aux_effective: -0.005771
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.434485
- target_special_eval.event_prob_mean: 0.408956
- delta_event_presence_prob_mean: -0.063753
- delta_event_fall_prob_mean: 0.014926
- delta_event_energy_prob_mean: -0.05469
- delta_event_presence_peak_ratio: -0.003322
- delta_z_art_delta_abs_mean: -0.000644
- delta_acoustic_energy_mean: -0.086306
- delta_acoustic_delta_abs_mean: 0.005264

### step 200
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- target_validation.loss_total: 2.131434
- target_special_eval.loss_total: 2.361891
- delta_loss_total: 0.230457
- delta_loss_text_aux: -0.006229
- delta_loss_text_aux_effective: -0.006229
- delta_loss_text_aux_structural: 0.0
- delta_loss_text_aux_lexical: 0.0
- delta_loss_structural_clause_transition_aux: 0.0
- delta_loss_boundary_contrast_aux: 0.0
- delta_loss_punctuation_profile_aux: 0.0
- delta_loss_structural_clause_profile_aux: 0.0
- delta_loss_challenge_proxy_profile_aux: 0.0
- delta_loss_z_art_influence_aux: 0.0
- delta_loss_formal_special_clause_shape_aux: 0.0
- target_validation.event_prob_mean: 0.429308
- target_special_eval.event_prob_mean: 0.404089
- delta_event_presence_prob_mean: -0.064212
- delta_event_fall_prob_mean: 0.014235
- delta_event_energy_prob_mean: -0.053303
- delta_event_presence_peak_ratio: -0.018467
- delta_z_art_delta_abs_mean: -0.000197
- delta_acoustic_energy_mean: -0.084826
- delta_acoustic_delta_abs_mean: -0.001996

## notes
- Special-eval series summarizes challenge-slice behavior across selected checkpoints.
- Each checkpoint also has its own detailed special_eval_model.json and .md under reports/eval.
