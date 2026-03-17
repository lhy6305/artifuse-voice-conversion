# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.131005, 'special_priority': True, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.047019, 'budget_to_special_anchor': 0.131005, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.438936, 'best_z_art_floor': 0.465828}
- selected_policy: special_push
- selected_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- unmet_intents: []

## reasons
- special/z_art priority is enabled and budget is sufficient for the special route.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
