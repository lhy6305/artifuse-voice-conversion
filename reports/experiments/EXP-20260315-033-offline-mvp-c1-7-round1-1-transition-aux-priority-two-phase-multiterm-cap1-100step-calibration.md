# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration
- date: 2026-03-15T01:22:13
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_multiterm_cap1_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-029` two-phase handoff timing, but cap the phase1 `multi_terminal-only` tail to at most one record per batch while leaving the base `clause>=4` pool intact
- hypothesis: if the main special-slice damage is caused by overexposure to the extra `49` `multi_terminal-only` records, a hard `max_slots = 1` cap on that tail should preserve most of `EXP-029`'s main-validation and `step50` benefit while reducing the final special regression

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run and direct batch-plan inspection confirmed phase1 still uses `3 priority slots`, but the extra `multi_terminal-only` tail is capped at `1` record per batch
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.337046`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.714039`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; capping the extra `multi_terminal-only` tail leaves the run almost indistinguishable from `EXP-032`, with strong main validation but no meaningful improvement to the final special slice.
- failures: no execution failure; the cap does not solve the targeted issue because final `target_validation.loss_total = 2.663196` remains strong, `step50 zero_e_evt.delta_target_loss_total = -0.549967` stays solid, but final `target_special_eval.delta_loss_total = 0.111542` is still on the same bad side as `EXP-029 / EXP-032`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration.metrics.json
