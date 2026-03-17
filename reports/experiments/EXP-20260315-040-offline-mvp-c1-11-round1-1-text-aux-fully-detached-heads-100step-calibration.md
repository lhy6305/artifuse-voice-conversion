# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration
- date: 2026-03-15T12:20:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep split supervision and the `EXP-032` sampling skeleton unchanged, but detach both structural and lexical text-aux heads from the shared trunk so `text_aux` no longer backpropagates into the pooled runtime representation
- hypothesis: if `EXP-039` still failed because structural text supervision is the remaining source of shared-trunk drift, then fully detached text-aux heads should reduce the remaining structural special gap and clarify whether text supervision should stop shaping the trunk entirely

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; dry-run, full `100 step` training and all eval passes completed cleanly after wrapping the training plan into the standard experiment metrics format
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.170676`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.949163`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; detaching both structural and lexical text-aux heads produced results that are effectively identical to `EXP-039`, which means the remaining gap is no longer explained by text-aux gradient flow into the shared trunk.
- failures: no execution failure; final `target_validation.loss_total = 2.91453`, final `target_special_eval.delta_loss_total = 0.349915`, final `zero_e_evt.delta_target_loss_total = 0.949163`, and `step50` collapse metrics stayed nearly unchanged from `EXP-039`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration.metrics.json
