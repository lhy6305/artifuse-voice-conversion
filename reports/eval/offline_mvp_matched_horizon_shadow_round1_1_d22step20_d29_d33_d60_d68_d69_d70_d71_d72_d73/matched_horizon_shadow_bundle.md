# offline MVP matched-horizon shadow bundle

- output_dir: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73
- checkpoint_anchor_experiment_metrics_path: F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.json
- checkpoint_anchor_step: 20
- materialized_anchor_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/materialized_anchor/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.metrics.checkpoint-step20-anchor.metrics.json
- route_analysis_dir: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/anchor_routes
- validation_budgets: [0.05, 0.13]

## matched inputs
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-016-offline-mvp-d60-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-024-offline-mvp-d68-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-023-offline-mvp-d69-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-025-offline-mvp-d70-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-027-offline-mvp-d72-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.metrics.json
- F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-029-offline-mvp-d73-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22like-latehandoff-20step-calibration.metrics.json

## budget runs
- budget=0.05: selector=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/anchor_route_selection_budget_0p05, comparison=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/final_comparison_budget_0p05, recap=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/route_recap_budget_0p05
- budget=0.13: selector=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/anchor_route_selection_budget_0p13, comparison=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/final_comparison_budget_0p13, recap=F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/route_recap_budget_0p13

## notes
- This bundle materializes one checkpoint anchor, then runs matched-horizon route-analysis, selector, final comparison, and route recap for each requested validation budget.
- Budget runs always use default_minimax inputs with no special/z_art/e_evt override flags.
