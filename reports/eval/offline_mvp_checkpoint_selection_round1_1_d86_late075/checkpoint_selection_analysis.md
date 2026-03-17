# offline MVP checkpoint 选择分析

- experiment_count: 1
- late_step_ratio: 0.75
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration @ step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586)
- best_final_special_experiment: EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration @ step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586)
- best_final_e_evt_experiment: EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration @ step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586)
- best_positive_control_late_special_experiment: EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration @ step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498)
- best_validation_guarded_special_experiment: EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration @ step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498)

## experiments
### EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.668876
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.310507, special_delta=0.186087, zero_e_evt=2.570719, zero_z_art=0.308605) [vs final: val=0.175406, special_delta=-0.045483, zero_e_evt=0.753924, zero_z_art=-0.086981]
- best_e_evt_checkpoint: step 50 (val=2.310507, special_delta=0.186087, zero_e_evt=2.570719, zero_z_art=0.308605) [vs final: val=0.175406, special_delta=-0.045483, zero_e_evt=0.753924, zero_z_art=-0.086981]
- best_late_special_checkpoint: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498) [vs final: val=0.021863, special_delta=-0.00612, zero_e_evt=0.369498, zero_z_art=0.109394]
- best_late_e_evt_checkpoint: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498) [vs final: val=0.021863, special_delta=-0.00612, zero_e_evt=0.369498, zero_z_art=0.109394]
- best_validation_guarded_checkpoint: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498) [vs final: val=0.021863, special_delta=-0.00612, zero_e_evt=0.369498, zero_z_art=0.109394]
- best_positive_control_late_checkpoint: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498) [vs final: val=0.021863, special_delta=-0.00612, zero_e_evt=0.369498, zero_z_art=0.109394]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498) [vs final: val=0.021863, special_delta=-0.00612, zero_e_evt=0.369498, zero_z_art=0.109394]
- late_window:
  - step150: step 150 (val=2.156964, special_delta=0.22545, zero_e_evt=2.186293, zero_z_art=0.50498)
  - step200: step 200 (val=2.135101, special_delta=0.23157, zero_e_evt=1.816795, zero_z_art=0.395586)

## notes
- This report merges special_eval_series and checkpoint_series_eval from existing experiment metrics.
- late_step_ratio defines the checkpoint window considered late enough for checkpoint-selection discussion.
- validation_guard_ratio compares a checkpoint against that experiment's best target validation loss.
- min_positive_control_delta is the minimum zero_z_art / zero_e_evt delta required by the positive-control selector.
