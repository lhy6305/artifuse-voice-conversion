# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.103997, 'budget_to_special_anchor': 0.183751, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.438936, 'best_z_art_floor': 0.465828}
- selected_policy: validation_strict
- selected_anchor: EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration (val=2.340197, special_delta=0.190968, zero_e_evt=2.634231, zero_z_art=0.320415)
- unmet_intents: []

## reasons
- budget is below the minimax threshold, so only the strict validation route is feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
