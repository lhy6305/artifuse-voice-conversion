# offline MVP checkpoint 选择分析

- experiment_count: 5
- late_step_ratio: 0.75
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration @ step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)
- best_final_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)
- best_final_e_evt_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)
- best_positive_control_late_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634)
- best_validation_guarded_special_experiment: EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration @ step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634)

## experiments
### EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.657027
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.125622, special_delta=0.238578, zero_e_evt=1.864222, zero_z_art=0.669467) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.125622, special_delta=0.238578, zero_e_evt=1.864222, zero_z_art=0.669467) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.358588, special_delta=0.177657, zero_e_evt=2.773641, zero_z_art=0.38195) [vs final: val=0.232966, special_delta=-0.060921, zero_e_evt=0.909419, zero_z_art=-0.287517]
- best_e_evt_checkpoint: step 50 (val=2.358588, special_delta=0.177657, zero_e_evt=2.773641, zero_z_art=0.38195) [vs final: val=0.232966, special_delta=-0.060921, zero_e_evt=0.909419, zero_z_art=-0.287517]
- best_late_special_checkpoint: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879) [vs final: val=0.041438, special_delta=-0.008364, zero_e_evt=0.096244, zero_z_art=-0.010677]
- best_late_e_evt_checkpoint: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879) [vs final: val=0.041438, special_delta=-0.008364, zero_e_evt=0.096244, zero_z_art=-0.010677]
- best_validation_guarded_checkpoint: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879) [vs final: val=0.041438, special_delta=-0.008364, zero_e_evt=0.096244, zero_z_art=-0.010677]
- best_positive_control_late_checkpoint: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879) [vs final: val=0.041438, special_delta=-0.008364, zero_e_evt=0.096244, zero_z_art=-0.010677]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879) [vs final: val=0.041438, special_delta=-0.008364, zero_e_evt=0.096244, zero_z_art=-0.010677]
- late_window:
  - step150: step 150 (val=2.16706, special_delta=0.230214, zero_e_evt=1.960466, zero_z_art=0.65879)
  - step200: step 200 (val=2.125622, special_delta=0.238578, zero_e_evt=1.864222, zero_z_art=0.669467)

### EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.653374
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.372053, special_delta=0.184745, zero_e_evt=2.874014, zero_z_art=0.388582) [vs final: val=0.249354, special_delta=-0.055101, zero_e_evt=0.903714, zero_z_art=-0.322267]
- best_e_evt_checkpoint: step 50 (val=2.372053, special_delta=0.184745, zero_e_evt=2.874014, zero_z_art=0.388582) [vs final: val=0.249354, special_delta=-0.055101, zero_e_evt=0.903714, zero_z_art=-0.322267]
- best_late_special_checkpoint: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676) [vs final: val=0.04579, special_delta=-0.010421, zero_e_evt=0.062246, zero_z_art=-0.046173]
- best_late_e_evt_checkpoint: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676) [vs final: val=0.04579, special_delta=-0.010421, zero_e_evt=0.062246, zero_z_art=-0.046173]
- best_validation_guarded_checkpoint: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676) [vs final: val=0.04579, special_delta=-0.010421, zero_e_evt=0.062246, zero_z_art=-0.046173]
- best_positive_control_late_checkpoint: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676) [vs final: val=0.04579, special_delta=-0.010421, zero_e_evt=0.062246, zero_z_art=-0.046173]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676) [vs final: val=0.04579, special_delta=-0.010421, zero_e_evt=0.062246, zero_z_art=-0.046173]
- late_window:
  - step150: step 150 (val=2.168489, special_delta=0.229425, zero_e_evt=2.032546, zero_z_art=0.664676)
  - step200: step 200 (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849)

### EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.65818
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.126544, special_delta=0.258922, zero_e_evt=1.927875, zero_z_art=0.311379) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.126544, special_delta=0.258922, zero_e_evt=1.927875, zero_z_art=0.311379) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.329353, special_delta=0.198428, zero_e_evt=2.590052, zero_z_art=0.262747) [vs final: val=0.202809, special_delta=-0.060494, zero_e_evt=0.662177, zero_z_art=-0.048632]
- best_e_evt_checkpoint: step 50 (val=2.329353, special_delta=0.198428, zero_e_evt=2.590052, zero_z_art=0.262747) [vs final: val=0.202809, special_delta=-0.060494, zero_e_evt=0.662177, zero_z_art=-0.048632]
- best_late_special_checkpoint: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357) [vs final: val=0.019519, special_delta=-0.006347, zero_e_evt=0.043562, zero_z_art=0.033978]
- best_late_e_evt_checkpoint: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357) [vs final: val=0.019519, special_delta=-0.006347, zero_e_evt=0.043562, zero_z_art=0.033978]
- best_validation_guarded_checkpoint: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357) [vs final: val=0.019519, special_delta=-0.006347, zero_e_evt=0.043562, zero_z_art=0.033978]
- best_positive_control_late_checkpoint: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357) [vs final: val=0.019519, special_delta=-0.006347, zero_e_evt=0.043562, zero_z_art=0.033978]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357) [vs final: val=0.019519, special_delta=-0.006347, zero_e_evt=0.043562, zero_z_art=0.033978]
- late_window:
  - step150: step 150 (val=2.146063, special_delta=0.252575, zero_e_evt=1.971437, zero_z_art=0.345357)
  - step200: step 200 (val=2.126544, special_delta=0.258922, zero_e_evt=1.927875, zero_z_art=0.311379)

### EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.63492
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.307368, special_delta=0.196444, zero_e_evt=2.548418, zero_z_art=0.299145) [vs final: val=0.199432, special_delta=-0.050111, zero_e_evt=0.610652, zero_z_art=-0.125506]
- best_e_evt_checkpoint: step 50 (val=2.307368, special_delta=0.196444, zero_e_evt=2.548418, zero_z_art=0.299145) [vs final: val=0.199432, special_delta=-0.050111, zero_e_evt=0.610652, zero_z_art=-0.125506]
- best_late_special_checkpoint: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088) [vs final: val=0.037223, special_delta=-0.011267, zero_e_evt=0.125157, zero_z_art=0.016229]
- best_late_e_evt_checkpoint: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088) [vs final: val=0.037223, special_delta=-0.011267, zero_e_evt=0.125157, zero_z_art=0.016229]
- best_validation_guarded_checkpoint: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088) [vs final: val=0.037223, special_delta=-0.011267, zero_e_evt=0.125157, zero_z_art=0.016229]
- best_positive_control_late_checkpoint: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088) [vs final: val=0.037223, special_delta=-0.011267, zero_e_evt=0.125157, zero_z_art=0.016229]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088) [vs final: val=0.037223, special_delta=-0.011267, zero_e_evt=0.125157, zero_z_art=0.016229]
- late_window:
  - step150: step 150 (val=2.145159, special_delta=0.235288, zero_e_evt=2.062923, zero_z_art=0.44088)
  - step200: step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)

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
