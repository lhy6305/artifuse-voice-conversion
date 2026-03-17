# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration
- date: 2026-03-15T01:10:02
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_pool_handoff_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the two-phase `3-slot -> 1-slot` schedule, but change the pool itself across phases: phase1 keeps `clause_count >= 4 OR multi_terminal`, while phase2 narrows to `clause_count >= 4` only
- hypothesis: if the final special-slice regression is caused mainly by persistent multi-terminal exposure after the early burst, a phase-specific pool handoff should keep most of `EXP-029`'s `step50` and main-validation gains while reducing the final special penalty

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run and plan inspection confirmed phase1 priority pool `234 / 592`, phase2 priority pool `185 / 592`, with the same `3-slot -> 1-slot -> seeded shuffle` timing as `EXP-029`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.275259`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.735497`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; phase-specific pool handoff improves final main validation even beyond `EXP-029`, and it keeps `step50` materially better than `EXP-030 / EXP-031`, but it does not reduce the final special-slice regression at all.
- failures: no execution failure; the hoped-for late cleanup does not materialize because final `target_validation.loss_total = 2.672052` is strong and `step50 zero_e_evt.delta_target_loss_total = -0.556712` stays clearly better than the pool-narrowed variants, yet final `target_special_eval.delta_loss_total = 0.103108` remains effectively identical to `EXP-029`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration.metrics.json
