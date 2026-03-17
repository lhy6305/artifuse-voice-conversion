# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration
- date: 2026-03-15T13:20:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-039` detached lexical head and all current split-supervision settings unchanged, but add a runtime-facing boundary contrast auxiliary that directly penalizes insufficient pre/post drops in event presence and event energy around pause and terminal boundaries
- hypothesis: if the remaining special gap is now structural rather than lexical, then pairwise boundary contrast on the event path should improve punctuation-only final behavior and possibly stabilize the mid-training `step50` collapse better than further `text_aux` head changes

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; dry-run, full `100 step` training and all eval passes completed cleanly, and the wrapped metrics payload preserved checkpoint resolution for follow-up evaluations
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.175258`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.949482`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the new boundary contrast auxiliary produced a non-zero formal validation loss, but it did not create measurable behavior changes relative to `EXP-039`, and the apparent final special improvement came mainly from accounting rather than improved event behavior.
- failures: no execution failure; final `target_validation.loss_total = 2.924252` got worse, final `target_special_eval.delta_loss_total = 0.342355` improved only because `loss_boundary_contrast_aux = 0.050434` exists on validation but is `0.0` on the special slice, and `step50` / final ablation dependence stayed effectively unchanged from `EXP-039`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration.metrics.json
