# offline MVP anchor route analysis

- anchor_count: 10
- derived_thresholds: {'budget_to_minimax_anchor': 0.336258, 'budget_to_special_anchor': 0.420244, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.438936, 'best_z_art_floor': 0.51471}

## leaders
- validation: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)
- special: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- zero_e_evt: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- zero_z_art: EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration (val=2.141317, special_delta=0.232356, zero_e_evt=1.822031, zero_z_art=0.51471)
- minimax: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

## policies
### validation_strict
- description: Use the strongest validation anchor with zero extra validation budget.
- objective: validation
- constraints: {'max_validation_budget_over_best': 0.0, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration']
- selected_anchor: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)

### default_minimax
- description: Use the least-worst final anchor without extra route constraints.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration', 'EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration', 'EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration', 'EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration', 'EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration', 'EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration', 'EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration']
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### guarded_default
- description: Allow just enough validation budget to include the minimax anchor, then keep minimax selection.
- objective: minimax
- constraints: {'max_validation_budget_over_best': 0.336258, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration', 'EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration', 'EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration', 'EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration', 'EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration', 'EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration']
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### e_evt_guard
- description: Require the current best e_evt floor and select the least-worst eligible anchor.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': 3.312339, 'min_zero_z_art_delta_target_loss_total': 0.438936}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration']
- selected_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

### special_push
- description: Allow enough validation budget to include the special/z_art leader and pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.420244, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration', 'EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration', 'EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration', 'EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration', 'EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration', 'EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration', 'EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration', 'EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration']
- selected_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

### z_art_push
- description: Require the current best z_art floor and enough validation budget to include that anchor, then pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.420244, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': 0.51471}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration']
- selected_anchor: EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration (val=2.141317, special_delta=0.232356, zero_e_evt=1.822031, zero_z_art=0.51471)

## recommended policy
- {'default_policy': 'default_minimax', 'route_switch_rules': [{'when': 'max_validation_budget_over_best < 0.336258', 'use_policy': 'validation_strict', 'selected_anchor_id': 'EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.336258 and (special_priority is false and z_art_priority is false)', 'use_policy': 'default_minimax', 'selected_anchor_id': 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.420244 and (special_priority is true or z_art_priority is true)', 'use_policy': 'special_push', 'selected_anchor_id': 'EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration'}]}

## notes
- Policies operate on final anchors only and are intended for route/reporting decisions, not new training.
- validation_strict picks D29-like anchors whenever no extra validation budget is allowed.
- default_minimax picks D22-like anchors when a single least-worst default is needed.
- special_push picks D26-like anchors only after enough validation budget is explicitly granted.
