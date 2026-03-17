# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.12514, 'budget_to_special_anchor': 0.126773, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.434833, 'best_z_art_floor': 0.465828}
- selected_policy: validation_strict
- selected_anchor: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)
- unmet_intents: []

## reasons
- budget is below the minimax threshold, so only the strict validation route is feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
