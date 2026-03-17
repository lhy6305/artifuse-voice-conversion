# offline MVP anchor route analysis

- anchor_count: 6
- derived_thresholds: {'budget_to_minimax_anchor': 0.12514, 'budget_to_special_anchor': 0.126773, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.434833, 'best_z_art_floor': 0.465828}

## leaders
- validation: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)
- special: EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration (val=2.523948, special_delta=0.111144, zero_e_evt=3.271397, zero_z_art=0.434243)
- zero_e_evt: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- zero_z_art: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- minimax: EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration (val=2.522315, special_delta=0.112037, zero_e_evt=3.26795, zero_z_art=0.434833)

## policies
### validation_strict
- description: Use the strongest validation anchor with zero extra validation budget.
- objective: validation
- constraints: {'max_validation_budget_over_best': 0.0, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration']
- selected_anchor: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)

### default_minimax
- description: Use the least-worst final anchor without extra route constraints.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration', 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor', 'EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration', 'EXP-20260316-016-offline-mvp-d60-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration', 'EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration', 'EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration']
- selected_anchor: EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration (val=2.522315, special_delta=0.112037, zero_e_evt=3.26795, zero_z_art=0.434833)

### guarded_default
- description: Allow just enough validation budget to include the minimax anchor, then keep minimax selection.
- objective: minimax
- constraints: {'max_validation_budget_over_best': 0.12514, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration', 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor', 'EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration']
- selected_anchor: EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration (val=2.522315, special_delta=0.112037, zero_e_evt=3.26795, zero_z_art=0.434833)

### e_evt_guard
- description: Require the current best e_evt floor and select the least-worst eligible anchor.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': 3.312339, 'min_zero_z_art_delta_target_loss_total': 0.434833}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration']
- selected_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

### special_push
- description: Allow enough validation budget to include the special/z_art leader and pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.126773, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- is_feasible: True
- eligible_anchor_ids: ['EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration', 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor', 'EXP-20260316-016-offline-mvp-d60-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration', 'EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration', 'EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration']
- selected_anchor: EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration (val=2.523948, special_delta=0.111144, zero_e_evt=3.271397, zero_z_art=0.434243)

### z_art_push
- description: Require the current best z_art floor and enough validation budget to include that anchor, then pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.126773, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': 0.465828}
- is_feasible: False
- eligible_anchor_ids: []
- selected_anchor: unavailable

## recommended policy
- {'default_policy': 'default_minimax', 'route_switch_rules': [{'when': 'max_validation_budget_over_best < 0.12514', 'use_policy': 'validation_strict', 'selected_anchor_id': 'EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.12514 and (special_priority is false and z_art_priority is false)', 'use_policy': 'default_minimax', 'selected_anchor_id': 'EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.126773 and (special_priority is true or z_art_priority is true)', 'use_policy': 'special_push', 'selected_anchor_id': 'EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration'}]}

## notes
- Policies operate on final anchors only and are intended for route/reporting decisions, not new training.
- validation_strict picks D29-like anchors whenever no extra validation budget is allowed.
- default_minimax picks D22-like anchors when a single least-worst default is needed.
- special_push picks D26-like anchors only after enough validation budget is explicitly granted.
