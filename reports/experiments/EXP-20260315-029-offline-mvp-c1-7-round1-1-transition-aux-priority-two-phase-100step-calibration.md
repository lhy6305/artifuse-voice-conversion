# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-029-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-100step-calibration
- date: 2026-03-15T00:48:06
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `C1.7` independent clause-transition auxiliary loss and priority pool definition, but replace the single-stage sampler with an explicit two-phase handoff: `priority_ratio = 0.75` through `step25`, then `0.25` through `step45`, then return to uniform seeded shuffle
- hypothesis: if the current conflict is really about when transition-rich records appear rather than only how many appear overall, an early strong burst followed by a clear taper should recover more main-validation signal than `EXP-027` while still preserving the mid-training stability gain that `EXP-026` lost

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run plus direct batch-plan inspection confirmed the actual schedule is `3 priority slots` for `step1-25`, `1 priority slot` for `step26-45`, and seeded shuffle afterwards under the same `234 / 592` priority pool
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.129481`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.641754`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the two-phase handoff is the first sampling variant that improves main validation and `step50` together, but it still regresses the punctuation-only special slice almost back to the aggressive `EXP-026` level.
- failures: no execution failure; the remaining method gap moved from `step50` to special-slice robustness, because final `target_validation.loss_total = 2.702175` and `step50 zero_e_evt.delta_target_loss_total = -0.463404` are both strong moves, but final `target_special_eval.delta_loss_total = 0.102328` remains sharply worse than `EXP-027 / EXP-028`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-029-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-100step-calibration.metrics.json
