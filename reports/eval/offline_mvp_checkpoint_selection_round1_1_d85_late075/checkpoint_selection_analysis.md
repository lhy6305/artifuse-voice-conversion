# offline MVP checkpoint 选择分析

- experiment_count: 1
- late_step_ratio: 0.75
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)
- best_final_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)
- best_final_e_evt_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)
- best_positive_control_late_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634)
- best_validation_guarded_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634)

## experiments
### EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.666843
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.310868, special_delta=0.185493, zero_e_evt=2.582539, zero_z_art=0.311158) [vs final: val=0.177394, special_delta=-0.045802, zero_e_evt=0.555188, zero_z_art=-0.122724]
- best_e_evt_checkpoint: step 50 (val=2.310868, special_delta=0.185493, zero_e_evt=2.582539, zero_z_art=0.311158) [vs final: val=0.177394, special_delta=-0.045802, zero_e_evt=0.555188, zero_z_art=-0.122724]
- best_late_special_checkpoint: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634) [vs final: val=0.027925, special_delta=-0.007382, zero_e_evt=0.038881, zero_z_art=-0.009248]
- best_late_e_evt_checkpoint: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634) [vs final: val=0.027925, special_delta=-0.007382, zero_e_evt=0.038881, zero_z_art=-0.009248]
- best_validation_guarded_checkpoint: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634) [vs final: val=0.027925, special_delta=-0.007382, zero_e_evt=0.038881, zero_z_art=-0.009248]
- best_positive_control_late_checkpoint: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634) [vs final: val=0.027925, special_delta=-0.007382, zero_e_evt=0.038881, zero_z_art=-0.009248]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634) [vs final: val=0.027925, special_delta=-0.007382, zero_e_evt=0.038881, zero_z_art=-0.009248]
- late_window:
  - step150: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634)
  - step200: step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)

## notes
- This report merges special_eval_series and checkpoint_series_eval from existing experiment metrics.
- late_step_ratio defines the checkpoint window considered late enough for checkpoint-selection discussion.
- validation_guard_ratio compares a checkpoint against that experiment's best target validation loss.
- min_positive_control_delta is the minimum zero_z_art / zero_e_evt delta required by the positive-control selector.
