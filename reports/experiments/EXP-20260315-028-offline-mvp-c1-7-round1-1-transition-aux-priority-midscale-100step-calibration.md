# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-028-offline-mvp-c1-7-round1-1-transition-aux-priority-midscale-100step-calibration
- date: 2026-03-15T00:38:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_midscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the independent clause-transition auxiliary loss and same priority pool, but choose an explicit middle schedule between `EXP-026` and `EXP-027`
- hypothesis: if the current tradeoff is mainly controlled by sampling intensity and duration, a middle schedule should recover part of `EXP-026` main-validation gain while preserving part of `EXP-027` special-slice and `step50` improvement

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were both reused unchanged; priority pool count remains `234 / 592`, with the schedule set to `priority_ratio = 0.625` and only through `step55`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.608278`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.869191`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the middle schedule keeps the strong special-slice gain and partially relieves the `step50` dip compared with the aggressive sampler, but it fails to recover main validation and is not a balanced midpoint over `EXP-026 / EXP-027`.
- failures: no execution failure; methodologically this midpoint is dominated for balance because final `target_validation.loss_total = 2.861962` is even worse than `EXP-027`, while `step50 zero_e_evt.delta_target_loss_total = -0.778543` and `step50 zero_z_art.delta_target_loss_total = -0.254093` still do not beat the softer curriculum, even though final `target_special_eval.delta_loss_total = -0.093905` becomes the strongest special-slice result so far.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-028-offline-mvp-c1-7-round1-1-transition-aux-priority-midscale-100step-calibration.metrics.json
