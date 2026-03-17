# offline MVP checkpoint 选择分析

- experiment_count: 14
- late_step_ratio: 0.75
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration @ step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)
- best_final_special_experiment: EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration @ step 200 (val=2.148904, special_delta=0.218229, zero_e_evt=2.126457, zero_z_art=0.436209)
- best_final_e_evt_experiment: EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration @ step 200 (val=2.138406, special_delta=0.231994, zero_e_evt=2.170294, zero_z_art=0.469429)
- best_positive_control_late_special_experiment: EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration @ step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433)
- best_validation_guarded_special_experiment: EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration @ step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433)

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

### EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.637586
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.110069, special_delta=0.245279, zero_e_evt=1.832783, zero_z_art=0.465426) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.110069, special_delta=0.245279, zero_e_evt=1.832783, zero_z_art=0.465426) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.294811, special_delta=0.192851, zero_e_evt=2.689036, zero_z_art=0.402836) [vs final: val=0.184742, special_delta=-0.052428, zero_e_evt=0.856253, zero_z_art=-0.06259]
- best_e_evt_checkpoint: step 50 (val=2.294811, special_delta=0.192851, zero_e_evt=2.689036, zero_z_art=0.402836) [vs final: val=0.184742, special_delta=-0.052428, zero_e_evt=0.856253, zero_z_art=-0.06259]
- best_late_special_checkpoint: step 150 (val=2.149293, special_delta=0.235859, zero_e_evt=1.736167, zero_z_art=0.39523) [vs final: val=0.039224, special_delta=-0.00942, zero_e_evt=-0.096616, zero_z_art=-0.070196]
- best_late_e_evt_checkpoint: step 200 (val=2.110069, special_delta=0.245279, zero_e_evt=1.832783, zero_z_art=0.465426) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_checkpoint: step 150 (val=2.149293, special_delta=0.235859, zero_e_evt=1.736167, zero_z_art=0.39523) [vs final: val=0.039224, special_delta=-0.00942, zero_e_evt=-0.096616, zero_z_art=-0.070196]
- best_positive_control_late_checkpoint: step 150 (val=2.149293, special_delta=0.235859, zero_e_evt=1.736167, zero_z_art=0.39523) [vs final: val=0.039224, special_delta=-0.00942, zero_e_evt=-0.096616, zero_z_art=-0.070196]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.149293, special_delta=0.235859, zero_e_evt=1.736167, zero_z_art=0.39523) [vs final: val=0.039224, special_delta=-0.00942, zero_e_evt=-0.096616, zero_z_art=-0.070196]
- late_window:
  - step150: step 150 (val=2.149293, special_delta=0.235859, zero_e_evt=1.736167, zero_z_art=0.39523)
  - step200: step 200 (val=2.110069, special_delta=0.245279, zero_e_evt=1.832783, zero_z_art=0.465426)

### EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.676646
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.141317, special_delta=0.232356, zero_e_evt=1.822031, zero_z_art=0.51471) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.141317, special_delta=0.232356, zero_e_evt=1.822031, zero_z_art=0.51471) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.32889, special_delta=0.180831, zero_e_evt=2.673272, zero_z_art=0.369034) [vs final: val=0.187573, special_delta=-0.051525, zero_e_evt=0.851241, zero_z_art=-0.145676]
- best_e_evt_checkpoint: step 50 (val=2.32889, special_delta=0.180831, zero_e_evt=2.673272, zero_z_art=0.369034) [vs final: val=0.187573, special_delta=-0.051525, zero_e_evt=0.851241, zero_z_art=-0.145676]
- best_late_special_checkpoint: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029) [vs final: val=0.033528, special_delta=-0.012218, zero_e_evt=0.196258, zero_z_art=0.023319]
- best_late_e_evt_checkpoint: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029) [vs final: val=0.033528, special_delta=-0.012218, zero_e_evt=0.196258, zero_z_art=0.023319]
- best_validation_guarded_checkpoint: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029) [vs final: val=0.033528, special_delta=-0.012218, zero_e_evt=0.196258, zero_z_art=0.023319]
- best_positive_control_late_checkpoint: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029) [vs final: val=0.033528, special_delta=-0.012218, zero_e_evt=0.196258, zero_z_art=0.023319]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029) [vs final: val=0.033528, special_delta=-0.012218, zero_e_evt=0.196258, zero_z_art=0.023319]
- late_window:
  - step150: step 150 (val=2.174845, special_delta=0.220138, zero_e_evt=2.018289, zero_z_art=0.538029)
  - step200: step 200 (val=2.141317, special_delta=0.232356, zero_e_evt=1.822031, zero_z_art=0.51471)

### EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.673007
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.138406, special_delta=0.231994, zero_e_evt=2.170294, zero_z_art=0.469429) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.138406, special_delta=0.231994, zero_e_evt=2.170294, zero_z_art=0.469429) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.306957, special_delta=0.195896, zero_e_evt=2.558445, zero_z_art=0.310273) [vs final: val=0.168551, special_delta=-0.036098, zero_e_evt=0.388151, zero_z_art=-0.159156]
- best_e_evt_checkpoint: step 50 (val=2.306957, special_delta=0.195896, zero_e_evt=2.558445, zero_z_art=0.310273) [vs final: val=0.168551, special_delta=-0.036098, zero_e_evt=0.388151, zero_z_art=-0.159156]
- best_late_special_checkpoint: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536) [vs final: val=0.026819, special_delta=-0.006316, zero_e_evt=0.085331, zero_z_art=0.002107]
- best_late_e_evt_checkpoint: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536) [vs final: val=0.026819, special_delta=-0.006316, zero_e_evt=0.085331, zero_z_art=0.002107]
- best_validation_guarded_checkpoint: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536) [vs final: val=0.026819, special_delta=-0.006316, zero_e_evt=0.085331, zero_z_art=0.002107]
- best_positive_control_late_checkpoint: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536) [vs final: val=0.026819, special_delta=-0.006316, zero_e_evt=0.085331, zero_z_art=0.002107]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536) [vs final: val=0.026819, special_delta=-0.006316, zero_e_evt=0.085331, zero_z_art=0.002107]
- late_window:
  - step150: step 150 (val=2.165225, special_delta=0.225678, zero_e_evt=2.255625, zero_z_art=0.471536)
  - step200: step 200 (val=2.138406, special_delta=0.231994, zero_e_evt=2.170294, zero_z_art=0.469429)

### EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.675623
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.140498, special_delta=0.233658, zero_e_evt=2.130963, zero_z_art=0.441535) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.140498, special_delta=0.233658, zero_e_evt=2.130963, zero_z_art=0.441535) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.31019, special_delta=0.193516, zero_e_evt=2.631278, zero_z_art=0.332789) [vs final: val=0.169692, special_delta=-0.040142, zero_e_evt=0.500315, zero_z_art=-0.108746]
- best_e_evt_checkpoint: step 50 (val=2.31019, special_delta=0.193516, zero_e_evt=2.631278, zero_z_art=0.332789) [vs final: val=0.169692, special_delta=-0.040142, zero_e_evt=0.500315, zero_z_art=-0.108746]
- best_late_special_checkpoint: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129) [vs final: val=0.03118, special_delta=-0.00963, zero_e_evt=0.011414, zero_z_art=0.004594]
- best_late_e_evt_checkpoint: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129) [vs final: val=0.03118, special_delta=-0.00963, zero_e_evt=0.011414, zero_z_art=0.004594]
- best_validation_guarded_checkpoint: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129) [vs final: val=0.03118, special_delta=-0.00963, zero_e_evt=0.011414, zero_z_art=0.004594]
- best_positive_control_late_checkpoint: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129) [vs final: val=0.03118, special_delta=-0.00963, zero_e_evt=0.011414, zero_z_art=0.004594]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129) [vs final: val=0.03118, special_delta=-0.00963, zero_e_evt=0.011414, zero_z_art=0.004594]
- late_window:
  - step150: step 150 (val=2.171678, special_delta=0.224028, zero_e_evt=2.142377, zero_z_art=0.446129)
  - step200: step 200 (val=2.140498, special_delta=0.233658, zero_e_evt=2.130963, zero_z_art=0.441535)

### EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.671921
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.137537, special_delta=0.235312, zero_e_evt=2.00519, zero_z_art=0.422542) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.137537, special_delta=0.235312, zero_e_evt=2.00519, zero_z_art=0.422542) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.308752, special_delta=0.194434, zero_e_evt=2.620212, zero_z_art=0.312178) [vs final: val=0.171215, special_delta=-0.040878, zero_e_evt=0.615022, zero_z_art=-0.110364]
- best_e_evt_checkpoint: step 50 (val=2.308752, special_delta=0.194434, zero_e_evt=2.620212, zero_z_art=0.312178) [vs final: val=0.171215, special_delta=-0.040878, zero_e_evt=0.615022, zero_z_art=-0.110364]
- best_late_special_checkpoint: step 150 (val=2.178446, special_delta=0.226566, zero_e_evt=1.939391, zero_z_art=0.370093) [vs final: val=0.040909, special_delta=-0.008746, zero_e_evt=-0.065799, zero_z_art=-0.052449]
- best_late_e_evt_checkpoint: step 200 (val=2.137537, special_delta=0.235312, zero_e_evt=2.00519, zero_z_art=0.422542) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_checkpoint: step 150 (val=2.178446, special_delta=0.226566, zero_e_evt=1.939391, zero_z_art=0.370093) [vs final: val=0.040909, special_delta=-0.008746, zero_e_evt=-0.065799, zero_z_art=-0.052449]
- best_positive_control_late_checkpoint: step 150 (val=2.178446, special_delta=0.226566, zero_e_evt=1.939391, zero_z_art=0.370093) [vs final: val=0.040909, special_delta=-0.008746, zero_e_evt=-0.065799, zero_z_art=-0.052449]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.178446, special_delta=0.226566, zero_e_evt=1.939391, zero_z_art=0.370093) [vs final: val=0.040909, special_delta=-0.008746, zero_e_evt=-0.065799, zero_z_art=-0.052449]
- late_window:
  - step150: step 150 (val=2.178446, special_delta=0.226566, zero_e_evt=1.939391, zero_z_art=0.370093)
  - step200: step 200 (val=2.137537, special_delta=0.235312, zero_e_evt=2.00519, zero_z_art=0.422542)

### EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.68613
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.148904, special_delta=0.218229, zero_e_evt=2.126457, zero_z_art=0.436209) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.148904, special_delta=0.218229, zero_e_evt=2.126457, zero_z_art=0.436209) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.321273, special_delta=0.167559, zero_e_evt=2.796732, zero_z_art=0.364517) [vs final: val=0.172369, special_delta=-0.05067, zero_e_evt=0.670275, zero_z_art=-0.071692]
- best_e_evt_checkpoint: step 50 (val=2.321273, special_delta=0.167559, zero_e_evt=2.796732, zero_z_art=0.364517) [vs final: val=0.172369, special_delta=-0.05067, zero_e_evt=0.670275, zero_z_art=-0.071692]
- best_late_special_checkpoint: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433) [vs final: val=0.043077, special_delta=-0.007313, zero_e_evt=0.187321, zero_z_art=0.034224]
- best_late_e_evt_checkpoint: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433) [vs final: val=0.043077, special_delta=-0.007313, zero_e_evt=0.187321, zero_z_art=0.034224]
- best_validation_guarded_checkpoint: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433) [vs final: val=0.043077, special_delta=-0.007313, zero_e_evt=0.187321, zero_z_art=0.034224]
- best_positive_control_late_checkpoint: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433) [vs final: val=0.043077, special_delta=-0.007313, zero_e_evt=0.187321, zero_z_art=0.034224]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433) [vs final: val=0.043077, special_delta=-0.007313, zero_e_evt=0.187321, zero_z_art=0.034224]
- late_window:
  - step150: step 150 (val=2.191981, special_delta=0.210916, zero_e_evt=2.313778, zero_z_art=0.470433)
  - step200: step 200 (val=2.148904, special_delta=0.218229, zero_e_evt=2.126457, zero_z_art=0.436209)

### EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.675041
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.140033, special_delta=0.23583, zero_e_evt=2.011104, zero_z_art=0.42172) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.140033, special_delta=0.23583, zero_e_evt=2.011104, zero_z_art=0.42172) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.32889, special_delta=0.180831, zero_e_evt=2.673272, zero_z_art=0.369034) [vs final: val=0.188857, special_delta=-0.054999, zero_e_evt=0.662168, zero_z_art=-0.052686]
- best_e_evt_checkpoint: step 50 (val=2.32889, special_delta=0.180831, zero_e_evt=2.673272, zero_z_art=0.369034) [vs final: val=0.188857, special_delta=-0.054999, zero_e_evt=0.662168, zero_z_art=-0.052686]
- best_late_special_checkpoint: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976) [vs final: val=0.034383, special_delta=-0.013906, zero_e_evt=0.186389, zero_z_art=0.042256]
- best_late_e_evt_checkpoint: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976) [vs final: val=0.034383, special_delta=-0.013906, zero_e_evt=0.186389, zero_z_art=0.042256]
- best_validation_guarded_checkpoint: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976) [vs final: val=0.034383, special_delta=-0.013906, zero_e_evt=0.186389, zero_z_art=0.042256]
- best_positive_control_late_checkpoint: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976) [vs final: val=0.034383, special_delta=-0.013906, zero_e_evt=0.186389, zero_z_art=0.042256]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976) [vs final: val=0.034383, special_delta=-0.013906, zero_e_evt=0.186389, zero_z_art=0.042256]
- late_window:
  - step150: step 150 (val=2.174416, special_delta=0.221924, zero_e_evt=2.197493, zero_z_art=0.463976)
  - step200: step 200 (val=2.140033, special_delta=0.23583, zero_e_evt=2.011104, zero_z_art=0.42172)

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

### EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration.metrics.json
- late_min_step: 150
- validation_guard_threshold: 2.664293
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 200 (val=2.131434, special_delta=0.230457, zero_e_evt=2.069828, zero_z_art=0.484435) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 200 (val=2.131434, special_delta=0.230457, zero_e_evt=2.069828, zero_z_art=0.484435) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=2.310971, special_delta=0.184908, zero_e_evt=2.603668, zero_z_art=0.283247) [vs final: val=0.179537, special_delta=-0.045549, zero_e_evt=0.53384, zero_z_art=-0.201188]
- best_e_evt_checkpoint: step 50 (val=2.310971, special_delta=0.184908, zero_e_evt=2.603668, zero_z_art=0.283247) [vs final: val=0.179537, special_delta=-0.045549, zero_e_evt=0.53384, zero_z_art=-0.201188]
- best_late_special_checkpoint: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314) [vs final: val=0.036557, special_delta=-0.008597, zero_e_evt=0.26109, zero_z_art=0.013879]
- best_late_e_evt_checkpoint: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314) [vs final: val=0.036557, special_delta=-0.008597, zero_e_evt=0.26109, zero_z_art=0.013879]
- best_validation_guarded_checkpoint: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314) [vs final: val=0.036557, special_delta=-0.008597, zero_e_evt=0.26109, zero_z_art=0.013879]
- best_positive_control_late_checkpoint: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314) [vs final: val=0.036557, special_delta=-0.008597, zero_e_evt=0.26109, zero_z_art=0.013879]
- best_validation_guarded_positive_control_checkpoint: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314) [vs final: val=0.036557, special_delta=-0.008597, zero_e_evt=0.26109, zero_z_art=0.013879]
- late_window:
  - step150: step 150 (val=2.167991, special_delta=0.22186, zero_e_evt=2.330918, zero_z_art=0.498314)
  - step200: step 200 (val=2.131434, special_delta=0.230457, zero_e_evt=2.069828, zero_z_art=0.484435)

## notes
- This report merges special_eval_series and checkpoint_series_eval from existing experiment metrics.
- late_step_ratio defines the checkpoint window considered late enough for checkpoint-selection discussion.
- validation_guard_ratio compares a checkpoint against that experiment's best target validation loss.
- min_positive_control_delta is the minimum zero_z_art / zero_e_evt delta required by the positive-control selector.
