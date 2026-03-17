# offline MVP handoff document - round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance

## Metadata
- generated_at: 2026-03-16T17:31:21
- stage_label: round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance
- route_policy: validation_strict
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}
- anchor_reference: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration

## Source Artifacts
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance/route_handoff.json
- route_selection_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/anchor_route_selection.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.checkpoint-step20-anchor.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-016-offline-mvp-d60-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.metrics.json

## Route Governance
- route_governance_summary: Formal default remains final-only: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration is a natural final anchor and remains eligible for official handoff/stage-report wording.
- route_governance_guardrail: Synthetic checkpoint alternatives EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor align to the matched horizon and can support shadow comparisons, but official handoff/stage-report wording should remain final-only.

## Copy Ready Handoff
- Current route is validation_strict, so the active reference anchor is EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927).
- Relative to EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration, the strongest validation alternative is EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor (val=0.073451, special=0.006332, zero_e_evt=0.04273, zero_z_art=0.033512), while the strongest special alternative is EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration (val=0.126773, special=-0.060625, zero_e_evt=0.292916, zero_z_art=0.069316).
- Formal default remains final-only: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration is a natural final anchor and remains eligible for official handoff/stage-report wording.
- Synthetic checkpoint alternatives EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor align to the matched horizon and can support shadow comparisons, but official handoff/stage-report wording should remain final-only.
- Keep EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration as the active validation-first reference; cite EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration only when special/z_art-side tradeoff exploration is explicitly requested.

## Current Anchor
- route_anchor: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)
- route_anchor_governance: natural_final_anchor: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.

## Alternatives
- best_validation_alternative: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor (delta_vs_route: val=0.073451, special=0.006332, zero_e_evt=0.04273, zero_z_art=0.033512)
- best_validation_alternative_governance: horizon_equalization_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration-checkpoint-step20-anchor is a synthetic checkpoint anchor aligned to the 20-step reference horizon; use it for matched-horizon shadow comparisons, not as the formal default anchor.
- best_special_alternative: EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration (delta_vs_route: val=0.126773, special=-0.060625, zero_e_evt=0.292916, zero_z_art=0.069316)
- best_special_alternative_governance: natural_final_anchor: EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.
- best_e_evt_alternative: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (delta_vs_route: val=0.131005, special=-0.060092, zero_e_evt=0.333858, zero_z_art=0.100901)
- best_e_evt_alternative_governance: natural_final_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.
- best_z_art_alternative: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (delta_vs_route: val=0.131005, special=-0.060092, zero_e_evt=0.333858, zero_z_art=0.100901)
- best_z_art_alternative_governance: natural_final_anchor: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.

## Next Step
- next_step_guidance: Keep EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration as the active validation-first reference; cite EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration only when special/z_art-side tradeoff exploration is explicitly requested.

## Notes
- This handoff is route-aware and should be preferred over manual anchor summaries.
- Synthetic checkpoint anchors are classified before they enter handoff wording so shadow tools and formal defaults do not get mixed.
- copy_ready_handoff can be pasted into a phase summary, handoff note, or experiment update with minimal editing.
