# offline MVP anchor route analysis

- anchor_count: 3
- derived_thresholds: {'budget_to_minimax_anchor': 0.047019, 'budget_to_special_anchor': 0.126723, 'best_e_evt_floor': 3.299035, 'minimax_z_art_floor': 0.438936, 'best_z_art_floor': 0.460259}

## leaders
- validation: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)
- special: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)
- zero_e_evt: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)
- zero_z_art: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)
- minimax: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

## policies
### validation_strict
- description: Use the strongest validation anchor with zero extra validation budget.
- objective: validation
- constraints: {'max_validation_budget_over_best': 0.0, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- eligible_anchor_ids: ['EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration']
- selected_anchor: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)

### default_minimax
- description: Use the least-worst final anchor without extra route constraints.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration', 'EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration']
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### guarded_default
- description: Allow just enough validation budget to include the minimax anchor, then keep minimax selection.
- objective: minimax
- constraints: {'max_validation_budget_over_best': 0.047019, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration']
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### e_evt_guard
- description: Require the current best e_evt floor and select the least-worst eligible anchor.
- objective: minimax
- constraints: {'max_validation_budget_over_best': None, 'min_zero_e_evt_delta_target_loss_total': 3.299035, 'min_zero_z_art_delta_target_loss_total': 0.438936}
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration']
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

### special_push
- description: Allow enough validation budget to include the special/z_art leader and pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.126723, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': None}
- eligible_anchor_ids: ['EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration', 'EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration', 'EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration']
- selected_anchor: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)

### z_art_push
- description: Require the current best z_art floor and enough validation budget to include that anchor, then pick the best special eligible anchor.
- objective: special
- constraints: {'max_validation_budget_over_best': 0.126723, 'min_zero_e_evt_delta_target_loss_total': None, 'min_zero_z_art_delta_target_loss_total': 0.460259}
- eligible_anchor_ids: ['EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration']
- selected_anchor: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)

## recommended policy
- {'default_policy': 'default_minimax', 'route_switch_rules': [{'when': 'max_validation_budget_over_best < 0.047019', 'use_policy': 'validation_strict', 'selected_anchor_id': 'EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.047019 and (special_priority is false and z_art_priority is false)', 'use_policy': 'default_minimax', 'selected_anchor_id': 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration'}, {'when': 'max_validation_budget_over_best >= 0.126723 and (special_priority is true or z_art_priority is true)', 'use_policy': 'special_push', 'selected_anchor_id': 'EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration'}]}

## notes
- Policies operate on final anchors only and are intended for route/reporting decisions, not new training.
- validation_strict picks D29-like anchors whenever no extra validation budget is allowed.
- default_minimax picks D22-like anchors when a single least-worst default is needed.
- special_push picks D26-like anchors only after enough validation budget is explicitly granted.
