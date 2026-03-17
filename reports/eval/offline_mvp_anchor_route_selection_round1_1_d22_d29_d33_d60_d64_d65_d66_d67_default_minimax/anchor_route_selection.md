# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.047019, 'budget_to_special_anchor': 0.131005, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.438936, 'best_z_art_floor': 0.465828}
- selected_policy: default_minimax
- selected_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)
- unmet_intents: []

## reasons
- budget allows the minimax route and no stronger special route is both requested and feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
