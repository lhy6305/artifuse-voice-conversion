# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.0, 'budget_to_special_anchor': 0.017686, 'best_e_evt_floor': 1.9703, 'minimax_z_art_floor': 0.424651, 'best_z_art_floor': 0.710849}
- selected_policy: default_minimax
- selected_anchor: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration (val=2.107936, special_delta=0.246555, zero_e_evt=1.937766, zero_z_art=0.424651)
- unmet_intents: []

## reasons
- budget allows the minimax route and no stronger special route is both requested and feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
