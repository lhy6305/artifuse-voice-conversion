# offline MVP anchor route selection

- inputs: {'max_validation_budget_over_best': 0.13, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}
- derived_thresholds: {'budget_to_minimax_anchor': 0.059075, 'budget_to_special_anchor': 0.183751, 'best_e_evt_floor': 3.312339, 'minimax_z_art_floor': 0.365693, 'best_z_art_floor': 0.465828}
- selected_policy: default_minimax
- selected_anchor: EXP-20260316-030-offline-mvp-d75-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-20step-calibration (val=2.399272, special_delta=0.16719, zero_e_evt=2.960501, zero_z_art=0.365693)
- unmet_intents: []

## reasons
- budget allows the minimax route and no stronger special route is both requested and feasible.

## notes
- This selector resolves one concrete route decision from the current three-anchor policy set.
- If unmet_intents is non-empty, the requested intent could not be honored under the provided validation budget.
