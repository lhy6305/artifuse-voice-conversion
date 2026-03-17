# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-031-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-clause-ge4-only-100step-calibration
- date: 2026-03-15T01:03:29
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_clause_ge4_only_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-029` two-phase schedule but remove the explicit `multi_terminal` inclusion, leaving a cleaner `clause_count >= 4` priority pool
- hypothesis: if the main culprit is the extra `49` `multi_terminal-only` records added by `OR multi_terminal`, removing just that tail should recover more final special-slice robustness without losing as much `step50` and main-validation benefit as `EXP-030`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run and direct batch-plan inspection confirmed the priority pool is now `185 / 592`, with the same `3-slot -> 1-slot -> seeded shuffle` handoff as `EXP-029`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.726667`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.763830`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; removing only the explicit `multi_terminal-only` tail slightly improves the final challenge slice versus `EXP-030`, but it still fails to preserve the `step50` and main-validation advantages of `EXP-029`.
- failures: no execution failure; this cleaner ablation is still not a balanced point because final `target_special_eval.delta_loss_total = -0.029908` improves over `EXP-029`, yet final `target_validation.loss_total = 2.843136` and `step50 zero_e_evt.delta_target_loss_total = -0.843525` remain much worse than `EXP-029`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-031-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-clause-ge4-only-100step-calibration.metrics.json
