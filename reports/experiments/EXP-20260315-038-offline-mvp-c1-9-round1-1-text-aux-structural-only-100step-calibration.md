# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-038-offline-mvp-c1-9-round1-1-text-aux-structural-only-100step-calibration
- date: 2026-03-15T11:19:07
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_9_round1_1_text_aux_structural_only_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `EXP-032` sampler and clause-transition aux unchanged, but replace whole-vector `text_aux` supervision with split supervision that keeps only structural dimensions active and sets lexical dimensions to zero weight
- hypothesis: if the root problem is that lexical and punctuation/structure targets share one supervision channel and lexical dimensions drag the shared representation away from the challenge slice, then structural-only `text_aux` supervision should improve final special behavior without relying on the failed late-shutdown schedules

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; dry-run and training completed cleanly, and split text-aux metrics were written into all eval artifacts
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.212147`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.935605`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; splitting `text_aux` into structural and lexical groups proved the metrics can be separated, but structural-only supervision on the same head still failed to improve the final checkpoint.
- failures: no execution failure; final `target_validation.loss_total = 2.89193`, final `target_special_eval.delta_loss_total = 0.398875`, and final `zero_e_evt.delta_target_loss_total = 0.935605` remain on the same bad platform as `EXP-035 / 036 / 037`, while lexical-group loss still drifts high even with `lexical_weight = 0.0`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-038-offline-mvp-c1-9-round1-1-text-aux-structural-only-100step-calibration.metrics.json
