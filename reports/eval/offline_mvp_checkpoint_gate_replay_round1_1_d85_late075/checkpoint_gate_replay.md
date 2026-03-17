# offline MVP checkpoint gate replay

- experiment_count: 1
- gate_count: 6
- late_step_ratio: 0.75

## anchor
- anchor_final_checkpoint: step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882)

## recommendation
- strongest_special_gate: {'name': 'late_special_unconstrained', 'aggregate': {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}}
- most_conservative_gate: {'name': 'final_validation', 'aggregate': {'mean_delta_vs_final_validation': 0.0, 'mean_delta_vs_final_special': 0.0, 'mean_delta_vs_final_e_evt': 0.0, 'mean_delta_vs_final_z_art': 0.0, 'improved_special_vs_final_count': 0, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 1, 'non_anchor_joint_beating_count': 0}}
- strict_positive_control_gate: {'name': 'late_special_strict_positive_control', 'aggregate': {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}}

## gates
### final_validation
- description: Pick the best validation checkpoint across the whole trajectory.
- parameters: {'late_only': False, 'validation_guard_ratio': None, 'min_zero_z_art_delta': None, 'min_zero_e_evt_delta': None, 'objective': 'validation'}
- aggregate: {'mean_delta_vs_final_validation': 0.0, 'mean_delta_vs_final_special': 0.0, 'mean_delta_vs_final_e_evt': 0.0, 'mean_delta_vs_final_z_art': 0.0, 'improved_special_vs_final_count': 0, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 1, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 200 (val=2.133474, special_delta=0.231295, zero_e_evt=2.027351, zero_z_art=0.433882, selected_is_final=True, candidate_pool_size=4, delta_vs_final={'target_validation_loss_total': 0.0, 'delta_loss_total': 0.0, 'zero_e_evt_delta_target_loss_total': 0.0, 'zero_z_art_delta_target_loss_total': 0.0}, beats_anchor_jointly=True)

### late_special_unconstrained
- description: Pick the best special checkpoint in the late window without any guard.
- parameters: {'late_only': True, 'validation_guard_ratio': None, 'min_zero_z_art_delta': None, 'min_zero_e_evt_delta': None, 'objective': 'special'}
- aggregate: {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634, selected_is_final=False, candidate_pool_size=2, delta_vs_final={'target_validation_loss_total': 0.027925, 'delta_loss_total': -0.007382, 'zero_e_evt_delta_target_loss_total': 0.038881, 'zero_z_art_delta_target_loss_total': -0.009248}, beats_anchor_jointly=False)

### late_special_validation_guard_1p25
- description: Late-window special gate with a 1.25x validation guard relative to the experiment's best validation.
- parameters: {'late_only': True, 'validation_guard_ratio': 1.25, 'min_zero_z_art_delta': None, 'min_zero_e_evt_delta': None, 'objective': 'special'}
- aggregate: {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634, selected_is_final=False, candidate_pool_size=2, delta_vs_final={'target_validation_loss_total': 0.027925, 'delta_loss_total': -0.007382, 'zero_e_evt_delta_target_loss_total': 0.038881, 'zero_z_art_delta_target_loss_total': -0.009248}, beats_anchor_jointly=False)

### late_special_event_priority
- description: Late-window special gate with validation guard 1.25x and strong e_evt floor 1.0.
- parameters: {'late_only': True, 'validation_guard_ratio': 1.25, 'min_zero_z_art_delta': None, 'min_zero_e_evt_delta': 1.0, 'objective': 'special'}
- aggregate: {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634, selected_is_final=False, candidate_pool_size=2, delta_vs_final={'target_validation_loss_total': 0.027925, 'delta_loss_total': -0.007382, 'zero_e_evt_delta_target_loss_total': 0.038881, 'zero_z_art_delta_target_loss_total': -0.009248}, beats_anchor_jointly=False)

### late_special_dual_control_relaxed
- description: Late-window special gate with relaxed 1.5x validation guard plus dual-control floors z_art>=0.3 and e_evt>=0.5.
- parameters: {'late_only': True, 'validation_guard_ratio': 1.5, 'min_zero_z_art_delta': 0.3, 'min_zero_e_evt_delta': 0.5, 'objective': 'special'}
- aggregate: {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634, selected_is_final=False, candidate_pool_size=2, delta_vs_final={'target_validation_loss_total': 0.027925, 'delta_loss_total': -0.007382, 'zero_e_evt_delta_target_loss_total': 0.038881, 'zero_z_art_delta_target_loss_total': -0.009248}, beats_anchor_jointly=False)

### late_special_strict_positive_control
- description: Late-window special gate with 1.25x validation guard and positive-control floors z_art>=0.1 and e_evt>=0.5.
- parameters: {'late_only': True, 'validation_guard_ratio': 1.25, 'min_zero_z_art_delta': 0.1, 'min_zero_e_evt_delta': 0.5, 'objective': 'special'}
- aggregate: {'mean_delta_vs_final_validation': 0.027925, 'mean_delta_vs_final_special': -0.007382, 'mean_delta_vs_final_e_evt': 0.038881, 'mean_delta_vs_final_z_art': -0.009248, 'improved_special_vs_final_count': 1, 'improved_validation_vs_final_count': 0, 'joint_anchor_beating_count': 0, 'non_anchor_joint_beating_count': 0}
- selections:
  - EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration: step 150 (val=2.161399, special_delta=0.223913, zero_e_evt=2.066232, zero_z_art=0.424634, selected_is_final=False, candidate_pool_size=2, delta_vs_final={'target_validation_loss_total': 0.027925, 'delta_loss_total': -0.007382, 'zero_e_evt_delta_target_loss_total': 0.038881, 'zero_z_art_delta_target_loss_total': -0.009248}, beats_anchor_jointly=False)

## notes
- This report replays several interpretable checkpoint-gate prototypes over the late-window checkpoints.
- Each gate either optimizes validation, optimizes special behavior, or constrains dual-control behavior before selecting the best special checkpoint.
- anchor_final_checkpoint is the strongest final checkpoint among the compared experiments and is used as the current default reference.
