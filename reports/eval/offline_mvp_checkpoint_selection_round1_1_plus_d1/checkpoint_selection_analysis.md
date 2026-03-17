# offline MVP checkpoint 选择分析

- experiment_count: 5
- late_step_ratio: 0.8
- validation_guard_ratio: 1.25
- min_positive_control_delta: 0.1

## cross experiment summary
- best_final_validation_experiment: EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration @ step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259)
- best_final_special_experiment: EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration @ step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259)
- best_final_e_evt_experiment: EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration @ step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259)
- best_positive_control_late_special_experiment: EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration @ step 80 (val=4.282626, special_delta=-0.553492, zero_e_evt=0.66439, zero_z_art=0.550914)
- best_validation_guarded_special_experiment: EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration @ step 90 (val=3.522161, special_delta=-0.295714, zero_e_evt=1.520532, zero_z_art=0.005477)

## experiments
### EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.metrics.json
- late_min_step: 80
- validation_guard_threshold: 3.340065
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': False, 'late_best_e_evt_has_low_z_art': False, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 50 (val=9.677146, special_delta=-4.057235, zero_e_evt=-0.556712, zero_z_art=-0.187733) [vs final: val=7.005094, special_delta=-4.160343, zero_e_evt=-2.292209, zero_z_art=-1.462992]
- best_e_evt_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_special_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_late_e_evt_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_positive_control_late_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_guarded_positive_control_checkpoint: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step100: step 100 (val=2.672052, special_delta=0.103108, zero_e_evt=1.735497, zero_z_art=1.275259)

### EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.metrics.json
- late_min_step: 80
- validation_guard_threshold: 3.612136
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': True, 'late_best_e_evt_has_low_z_art': True, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 100 (val=2.889709, special_delta=0.39305, zero_e_evt=0.931855, zero_z_art=0.215737) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 100 (val=2.889709, special_delta=0.39305, zero_e_evt=0.931855, zero_z_art=0.215737) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 40 (val=9.296346, special_delta=-4.117158, zero_e_evt=0.369297, zero_z_art=0.162591) [vs final: val=6.406637, special_delta=-4.510208, zero_e_evt=-0.562558, zero_z_art=-0.053146]
- best_e_evt_checkpoint: step 90 (val=3.522096, special_delta=-0.2803, zero_e_evt=1.513861, zero_z_art=-0.001579) [vs final: val=0.632387, special_delta=-0.67335, zero_e_evt=0.582006, zero_z_art=-0.217316]
- best_late_special_checkpoint: step 80 (val=4.260131, special_delta=-0.528372, zero_e_evt=0.681383, zero_z_art=0.555121) [vs final: val=1.370422, special_delta=-0.921422, zero_e_evt=-0.250472, zero_z_art=0.339384]
- best_late_e_evt_checkpoint: step 90 (val=3.522096, special_delta=-0.2803, zero_e_evt=1.513861, zero_z_art=-0.001579) [vs final: val=0.632387, special_delta=-0.67335, zero_e_evt=0.582006, zero_z_art=-0.217316]
- best_validation_guarded_checkpoint: step 90 (val=3.522096, special_delta=-0.2803, zero_e_evt=1.513861, zero_z_art=-0.001579) [vs final: val=0.632387, special_delta=-0.67335, zero_e_evt=0.582006, zero_z_art=-0.217316]
- best_positive_control_late_checkpoint: step 80 (val=4.260131, special_delta=-0.528372, zero_e_evt=0.681383, zero_z_art=0.555121) [vs final: val=1.370422, special_delta=-0.921422, zero_e_evt=-0.250472, zero_z_art=0.339384]
- best_validation_guarded_positive_control_checkpoint: step 100 (val=2.889709, special_delta=0.39305, zero_e_evt=0.931855, zero_z_art=0.215737) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step80: step 80 (val=4.260131, special_delta=-0.528372, zero_e_evt=0.681383, zero_z_art=0.555121)
  - step90: step 90 (val=3.522096, special_delta=-0.2803, zero_e_evt=1.513861, zero_z_art=-0.001579)
  - step100: step 100 (val=2.889709, special_delta=0.39305, zero_e_evt=0.931855, zero_z_art=0.215737)

### EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.metrics.json
- late_min_step: 80
- validation_guard_threshold: 3.639555
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': True, 'late_best_e_evt_has_low_z_art': True, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 100 (val=2.911644, special_delta=0.354963, zero_e_evt=0.949482, zero_z_art=0.175258) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 100 (val=2.911644, special_delta=0.354963, zero_e_evt=0.949482, zero_z_art=0.175258) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 40 (val=9.311095, special_delta=-4.098338, zero_e_evt=0.362816, zero_z_art=0.16047) [vs final: val=6.399451, special_delta=-4.453301, zero_e_evt=-0.586666, zero_z_art=-0.014788]
- best_e_evt_checkpoint: step 90 (val=3.521361, special_delta=-0.293919, zero_e_evt=1.517961, zero_z_art=0.007022) [vs final: val=0.609717, special_delta=-0.648882, zero_e_evt=0.568479, zero_z_art=-0.168236]
- best_late_special_checkpoint: step 80 (val=4.283327, special_delta=-0.551359, zero_e_evt=0.659585, zero_z_art=0.552126) [vs final: val=1.371683, special_delta=-0.906322, zero_e_evt=-0.289897, zero_z_art=0.376868]
- best_late_e_evt_checkpoint: step 90 (val=3.521361, special_delta=-0.293919, zero_e_evt=1.517961, zero_z_art=0.007022) [vs final: val=0.609717, special_delta=-0.648882, zero_e_evt=0.568479, zero_z_art=-0.168236]
- best_validation_guarded_checkpoint: step 90 (val=3.521361, special_delta=-0.293919, zero_e_evt=1.517961, zero_z_art=0.007022) [vs final: val=0.609717, special_delta=-0.648882, zero_e_evt=0.568479, zero_z_art=-0.168236]
- best_positive_control_late_checkpoint: step 80 (val=4.283327, special_delta=-0.551359, zero_e_evt=0.659585, zero_z_art=0.552126) [vs final: val=1.371683, special_delta=-0.906322, zero_e_evt=-0.289897, zero_z_art=0.376868]
- best_validation_guarded_positive_control_checkpoint: step 100 (val=2.911644, special_delta=0.354963, zero_e_evt=0.949482, zero_z_art=0.175258) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step80: step 80 (val=4.283327, special_delta=-0.551359, zero_e_evt=0.659585, zero_z_art=0.552126)
  - step90: step 90 (val=3.521361, special_delta=-0.293919, zero_e_evt=1.517961, zero_z_art=0.007022)
  - step100: step 100 (val=2.911644, special_delta=0.354963, zero_e_evt=0.949482, zero_z_art=0.175258)

### EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.metrics.json
- late_min_step: 80
- validation_guard_threshold: 3.637696
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': True, 'late_best_e_evt_has_low_z_art': True, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 100 (val=2.910157, special_delta=0.356926, zero_e_evt=0.948263, zero_z_art=0.178659) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 100 (val=2.910157, special_delta=0.356926, zero_e_evt=0.948263, zero_z_art=0.178659) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 40 (val=9.315488, special_delta=-4.102586, zero_e_evt=0.362971, zero_z_art=0.160589) [vs final: val=6.405331, special_delta=-4.459512, zero_e_evt=-0.585292, zero_z_art=-0.01807]
- best_e_evt_checkpoint: step 90 (val=3.522161, special_delta=-0.295714, zero_e_evt=1.520532, zero_z_art=0.005477) [vs final: val=0.612004, special_delta=-0.65264, zero_e_evt=0.572269, zero_z_art=-0.173182]
- best_late_special_checkpoint: step 80 (val=4.282626, special_delta=-0.553492, zero_e_evt=0.66439, zero_z_art=0.550914) [vs final: val=1.372469, special_delta=-0.910418, zero_e_evt=-0.283873, zero_z_art=0.372255]
- best_late_e_evt_checkpoint: step 90 (val=3.522161, special_delta=-0.295714, zero_e_evt=1.520532, zero_z_art=0.005477) [vs final: val=0.612004, special_delta=-0.65264, zero_e_evt=0.572269, zero_z_art=-0.173182]
- best_validation_guarded_checkpoint: step 90 (val=3.522161, special_delta=-0.295714, zero_e_evt=1.520532, zero_z_art=0.005477) [vs final: val=0.612004, special_delta=-0.65264, zero_e_evt=0.572269, zero_z_art=-0.173182]
- best_positive_control_late_checkpoint: step 80 (val=4.282626, special_delta=-0.553492, zero_e_evt=0.66439, zero_z_art=0.550914) [vs final: val=1.372469, special_delta=-0.910418, zero_e_evt=-0.283873, zero_z_art=0.372255]
- best_validation_guarded_positive_control_checkpoint: step 100 (val=2.910157, special_delta=0.356926, zero_e_evt=0.948263, zero_z_art=0.178659) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step80: step 80 (val=4.282626, special_delta=-0.553492, zero_e_evt=0.66439, zero_z_art=0.550914)
  - step90: step 90 (val=3.522161, special_delta=-0.295714, zero_e_evt=1.520532, zero_z_art=0.005477)
  - step100: step 100 (val=2.910157, special_delta=0.356926, zero_e_evt=0.948263, zero_z_art=0.178659)

### EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration.metrics.json
- late_min_step: 80
- validation_guard_threshold: 3.558099
- trajectory_flags: {'final_special_positive': True, 'late_window_contains_negative_special': True, 'late_best_e_evt_has_low_z_art': True, 'validation_guard_excludes_positive_control_special': False}
- final_checkpoint: step 100 (val=2.846479, special_delta=0.412091, zero_e_evt=0.86209, zero_z_art=0.271847) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_validation_checkpoint: step 100 (val=2.846479, special_delta=0.412091, zero_e_evt=0.86209, zero_z_art=0.271847) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- best_special_checkpoint: step 40 (val=9.310667, special_delta=-4.103597, zero_e_evt=0.363313, zero_z_art=0.161265) [vs final: val=6.464188, special_delta=-4.515688, zero_e_evt=-0.498777, zero_z_art=-0.110582]
- best_e_evt_checkpoint: step 90 (val=3.394526, special_delta=-0.066697, zero_e_evt=1.31487, zero_z_art=-0.052776) [vs final: val=0.548047, special_delta=-0.478788, zero_e_evt=0.45278, zero_z_art=-0.324623]
- best_late_special_checkpoint: step 80 (val=3.823698, special_delta=-0.411991, zero_e_evt=1.223908, zero_z_art=0.471141) [vs final: val=0.977219, special_delta=-0.824082, zero_e_evt=0.361818, zero_z_art=0.199294]
- best_late_e_evt_checkpoint: step 90 (val=3.394526, special_delta=-0.066697, zero_e_evt=1.31487, zero_z_art=-0.052776) [vs final: val=0.548047, special_delta=-0.478788, zero_e_evt=0.45278, zero_z_art=-0.324623]
- best_validation_guarded_checkpoint: step 90 (val=3.394526, special_delta=-0.066697, zero_e_evt=1.31487, zero_z_art=-0.052776) [vs final: val=0.548047, special_delta=-0.478788, zero_e_evt=0.45278, zero_z_art=-0.324623]
- best_positive_control_late_checkpoint: step 80 (val=3.823698, special_delta=-0.411991, zero_e_evt=1.223908, zero_z_art=0.471141) [vs final: val=0.977219, special_delta=-0.824082, zero_e_evt=0.361818, zero_z_art=0.199294]
- best_validation_guarded_positive_control_checkpoint: step 100 (val=2.846479, special_delta=0.412091, zero_e_evt=0.86209, zero_z_art=0.271847) [vs final: val=0.0, special_delta=0.0, zero_e_evt=0.0, zero_z_art=0.0]
- late_window:
  - step80: step 80 (val=3.823698, special_delta=-0.411991, zero_e_evt=1.223908, zero_z_art=0.471141)
  - step90: step 90 (val=3.394526, special_delta=-0.066697, zero_e_evt=1.31487, zero_z_art=-0.052776)
  - step100: step 100 (val=2.846479, special_delta=0.412091, zero_e_evt=0.86209, zero_z_art=0.271847)

## notes
- This report merges special_eval_series and checkpoint_series_eval from existing experiment metrics.
- late_step_ratio defines the checkpoint window considered late enough for checkpoint-selection discussion.
- validation_guard_ratio compares a checkpoint against that experiment's best target validation loss.
- min_positive_control_delta is the minimum zero_z_art / zero_e_evt delta required by the positive-control selector.
