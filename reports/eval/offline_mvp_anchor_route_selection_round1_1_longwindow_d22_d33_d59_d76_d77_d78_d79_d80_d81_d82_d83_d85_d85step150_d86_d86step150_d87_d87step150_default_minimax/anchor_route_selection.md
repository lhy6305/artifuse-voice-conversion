# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.023498, 'budget_to_special_anchor': 0.040968, 'best_e_evt_floor': 2.330918, 'minimax_z_art_floor': 0.484435, 'best_z_art_floor': 0.710849}
- selected_policy: default_minimax
- selected_anchor: EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration (val=2.131434, special_delta=0.230457, zero_e_evt=2.069828, zero_z_art=0.484435)
- unmet_intents: []

## reasons
- budget allows the minimax route and no stronger special route is both requested and feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
