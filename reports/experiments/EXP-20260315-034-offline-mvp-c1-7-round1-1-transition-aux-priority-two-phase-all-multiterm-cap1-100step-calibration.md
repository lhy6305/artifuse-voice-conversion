# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration
- date: 2026-03-15T01:26:44
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-029` two-phase handoff timing, but cap all phase1 `multi_terminal` exposure to at most one record per batch by splitting the phase1 pool into `clause>=4 and not multi_terminal` plus a separate `multi_terminal` subpool
- hypothesis: if the final special regression comes from overexposure to any `multi_terminal` record during phase1 rather than only the short tail, a hard phase1 cap on all `multi_terminal` records should improve the challenge slice without fully sacrificing `step50` and main-validation behavior

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run and batch-plan inspection confirmed phase1 keeps `3 priority slots`, with at most `1` `multi_terminal` record per batch across both long and short subsets
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.304908`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.735107`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; capping all phase1 `multi_terminal` exposure also fails to move the final special slice, and the result again lands almost on top of `EXP-032`.
- failures: no execution failure; this stronger cap still does not solve the target issue because final `target_validation.loss_total = 2.669992` remains strong, `step50 zero_e_evt.delta_target_loss_total = -0.556362` stays close to `EXP-032`, but final `target_special_eval.delta_loss_total = 0.105375` remains effectively unchanged from `EXP-029 / EXP-032`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.metrics.json
