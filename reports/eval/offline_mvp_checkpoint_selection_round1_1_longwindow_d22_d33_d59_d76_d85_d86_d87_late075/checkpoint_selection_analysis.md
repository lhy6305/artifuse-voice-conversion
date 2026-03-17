# offline MVP checkpoint 选择分析

- experiment_count: 7
- late_step_ratio: 0.75
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration @ step 200 (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)
- best_final_special_experiment: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration @ step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- best_final_e_evt_experiment: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration @ step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- best_positive_control_late_special_experiment: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration @ step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- best_validation_guarded_special_experiment: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration @ step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

## experiments
### EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.json
- late_min_step: 23
- validation_guard_threshold: 3.055242
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 10 (val=2.592393, special_delta=0.135164, zero_e_evt=3.053715, zero_z_art=0.419647) [vs final: val=0.148199, special_delta=-0.004837, zero_e_evt=-0.24532, zero_z_art=-0.019289]
- best_e_evt_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_special_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_e_evt_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_positive_control_late_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_positive_control_checkpoint: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step30: step 30 (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.metrics.json
- late_min_step: 15
- validation_guard_threshold: 3.160225
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 10 (val=2.621019, special_delta=0.081505, zero_e_evt=3.224344, zero_z_art=0.46347) [vs final: val=0.092839, special_delta=-0.030172, zero_e_evt=-0.087995, zero_z_art=-0.002358]
- best_e_evt_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_special_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_e_evt_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_positive_control_late_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_positive_control_checkpoint: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step20: step 20 (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

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
