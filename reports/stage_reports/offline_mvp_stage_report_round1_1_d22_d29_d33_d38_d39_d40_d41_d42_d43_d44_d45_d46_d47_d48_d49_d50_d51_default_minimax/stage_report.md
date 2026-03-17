# offline MVP stage report - round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax

## Metadata
- generated_at: 2026-03-16T01:15:17
- stage_label: round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax
- route_policy: default_minimax
- anchor_reference: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}

## Executive Status
- executive_status: Current route is default_minimax; active anchor remains EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration; the current phase summary should keep this anchor unless route policy changes.

## Current Anchor
- current_anchor: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936)

## Primary Tradeoff
- validation_alternative: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (delta_vs_route: val=-0.047019, special=0.031768, zero_e_evt=-0.320554, zero_z_art=-0.074009)
- special_alternative: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (delta_vs_route: val=0.083986, special=-0.028324, zero_e_evt=0.013304, zero_z_art=0.026892)

## Carry Forward Handoff
- Current route is default_minimax, so the active reference anchor is EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936).
- Relative to EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration, the strongest validation alternative is EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=-0.047019, special=0.031768, zero_e_evt=-0.320554, zero_z_art=-0.074009), while the strongest special alternative is EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=0.083986, special=-0.028324, zero_e_evt=0.013304, zero_z_art=0.026892).
- Keep EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration as the default reference; cite EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration only when special/z_art-first routing is explicitly requested.

## Next Step
- next_step_guidance: Keep EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration as the default reference; cite EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration only when validation-first routing is explicitly requested, and cite EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration only when special/z_art-first routing is explicitly requested.

## Source Artifacts
- handoff_document_path: F:/proj_dev/tmp/workdir4/reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/handoff_document.json
- route_handoff_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/route_handoff.json
- route_selection_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_default_minimax/anchor_route_selection.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-064-offline-mvp-d47-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-hi84-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-063-offline-mvp-d46-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-004-offline-mvp-d51-round1-1-d7-init-phase-teacher-family-structural-transition-late-secondary-d33step10-to-d29-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-055-offline-mvp-d38-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-062-offline-mvp-d45-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29-shortpause-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-002-offline-mvp-d48-round1-1-d7-init-phase-teacher-family-softweight-handoff-d33step10-to-d29-late-targetshape-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-003-offline-mvp-d50-round1-1-d7-init-phase-teacher-family-structural-transition-late-only-d33step10-to-d29-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-061-offline-mvp-d44-round1-1-d7-init-d10-teacher-consistency-relaxed-none-other-gate-fused-hidden-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-001-offline-mvp-d49-round1-1-d7-init-phase-teacher-family-punctuation-aux-handoff-d33step10-to-d29-late-only-20step-calibration.metrics.json
- experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.metrics.json

## Notes
- This stage report is derived from the fixed-format handoff document rather than raw selector/comparison outputs.
- Use executive_status for status updates; use carry_forward_handoff when the full route-aware wording is needed.
