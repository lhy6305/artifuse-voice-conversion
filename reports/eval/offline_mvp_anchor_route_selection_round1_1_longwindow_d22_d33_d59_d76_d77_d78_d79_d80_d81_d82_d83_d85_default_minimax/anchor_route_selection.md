# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.014763, 'budget_to_special_anchor': 0.040968, 'best_e_evt_floor': 2.170294, 'minimax_z_art_floor': 0.710849, 'best_z_art_floor': 0.710849}
- selected_policy: default_minimax
- selected_anchor: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849)
- unmet_intents: []

## reasons
- budget allows the minimax route and no stronger special route is both requested and feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
