# offline MVP handoff document - round1_1_default_minimax_handoff

## Metadata
- generated_at: 2026-03-15T19:33:45
- stage_label: round1_1_default_minimax_handoff
- route_policy: default_minimax
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}
- anchor_reference: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration

## Source Artifacts
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_d22_d26_d29_default_minimax/route_handoff.json
- route_selection_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_default_minimax/anchor_route_selection.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration.metrics.json

## Copy Ready Handoff
- Current route is default_minimax, so the active reference anchor is EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936).
- Relative to EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration, the strongest validation alternative is EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=-0.047019, special=0.031768, zero_e_evt=-0.320554, zero_z_art=-0.074009), while the strongest special alternative is EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=0.079704, special=-0.022107, zero_e_evt=-0.026385, zero_z_art=0.021323).
- Keep EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration as the default reference; cite EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration only when special/z_art-first routing is explicitly requested.

## Current Anchor
- route_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

## Alternatives
- best_validation_alternative: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (delta_vs_route: val=-0.047019, special=0.031768, zero_e_evt=-0.320554, zero_z_art=-0.074009)
- best_special_alternative: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (delta_vs_route: val=0.079704, special=-0.022107, zero_e_evt=-0.026385, zero_z_art=0.021323)
- best_e_evt_alternative: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (delta_vs_route: val=0.079704, special=-0.022107, zero_e_evt=-0.026385, zero_z_art=0.021323)
- best_z_art_alternative: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (delta_vs_route: val=0.079704, special=-0.022107, zero_e_evt=-0.026385, zero_z_art=0.021323)

## Next Step
- next_step_guidance: Keep EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration as the default reference; cite EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration only when special/z_art-first routing is explicitly requested.

## Notes
- This handoff is route-aware and should be preferred over manual anchor summaries.
- copy_ready_handoff can be pasted into a phase summary, handoff note, or experiment update with minimal editing.
