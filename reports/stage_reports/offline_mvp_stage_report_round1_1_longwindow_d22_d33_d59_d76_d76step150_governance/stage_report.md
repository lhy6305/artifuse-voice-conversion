# offline MVP stage report - round1_1_longwindow_d22_d33_d59_d76_d76step150_governance

## Metadata
- generated_at: 2026-03-16T17:31:38
- stage_label: round1_1_longwindow_d22_d33_d59_d76_d76step150_governance
- route_policy: default_minimax
- anchor_reference: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}

## Executive Status
- executive_status: Current route is default_minimax; active anchor remains EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration; Synthetic checkpoint alternatives EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor stay option-only and should not be promoted into the formal default route unless route policy is explicitly upgraded.

## Route Governance
- route_governance_summary: Formal default remains final-only: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration is a natural final anchor and remains eligible for official handoff/stage-report wording.
- route_governance_guardrail: Synthetic checkpoint alternatives EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor stay option-only and should not be promoted into the formal default route unless route policy is explicitly upgraded.

## Current Anchor
- current_anchor: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849)
- current_anchor_governance: natural_final_anchor: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.

## Primary Tradeoff
- validation_alternative: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration (delta_vs_route: val=-0.014763, special=0.006709, zero_e_evt=-0.032534, zero_z_art=-0.286198)
- validation_alternative_governance: natural_final_anchor: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration is a natural final anchor and is eligible for official/fixed handoff wording.
- special_alternative: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor (delta_vs_route: val=0.02246, special=-0.004558, zero_e_evt=0.092623, zero_z_art=-0.269969)
- special_alternative_governance: checkpoint_option_anchor: EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor is a synthetic checkpoint option at step 150; keep it in checkpoint-selection, gate replay, or option-study lanes unless route policy is explicitly upgraded.

## Carry Forward Handoff
- Current route is default_minimax, so the active reference anchor is EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration (val=2.122699, special_delta=0.239846, zero_e_evt=1.9703, zero_z_art=0.710849).
- Relative to EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration, the strongest validation alternative is EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration (val=-0.014763, special=0.006709, zero_e_evt=-0.032534, zero_z_art=-0.286198), while the strongest special alternative is EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor (val=0.02246, special=-0.004558, zero_e_evt=0.092623, zero_z_art=-0.269969).
- Formal default remains final-only: EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration is a natural final anchor and remains eligible for official handoff/stage-report wording.
- Synthetic checkpoint alternatives EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor stay option-only and should not be promoted into the formal default route unless route policy is explicitly upgraded.
- Keep EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration as the default reference; cite EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor only as a checkpoint option when special/z_art-first routing is needed, not as a new default anchor.

## Next Step
- next_step_guidance: Keep EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration as the default reference; cite EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration-checkpoint-step150-anchor only as a checkpoint option when special/z_art-first routing is needed, not as a new default anchor.

## Source Artifacts
- handoff_document_path: F:/proj_dev/tmp/workdir4/reports/handoffs/offline_mvp_route_handoff_doc_round1_1_longwindow_d22_d33_d59_d76_d76step150_governance/handoff_document.json
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_longwindow_d22_d33_d59_d76_d76step150_governance/route_handoff.json
- route_selection_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/anchor_route_selection.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-015-offline-mvp-d33-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-fused-hidden-200step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-013-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-200step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-014-offline-mvp-d59-round1-1-d7-init-d57-formal-special-clause2-shortpause-ceiling-sampler-teacher-gate-late-200step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.checkpoint-step150-anchor.metrics.json

## Notes
- This stage report is derived from the fixed-format handoff document rather than raw selector/comparison outputs.
- Route governance is rendered explicitly so synthetic checkpoint options do not get mistaken for formal default anchors.
- Use executive_status for status updates; use carry_forward_handoff when the full route-aware wording is needed.
