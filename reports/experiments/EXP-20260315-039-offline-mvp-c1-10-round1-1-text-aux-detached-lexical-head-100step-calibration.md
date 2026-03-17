# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration
- date: 2026-03-15T11:33:09
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep split supervision for structural and lexical text targets, but move lexical prediction to a detached head so lexical loss still trains its own head while no longer backpropagating into the shared trunk
- hypothesis: if lexical supervision is hurting final special mainly by dragging the shared trunk rather than by the lexical task existing at all, then detached lexical head should outperform `EXP-038` and ideally recover toward or beyond `EXP-032`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; dry-run, full `100 step` training and all eval passes completed cleanly, and split-head text-aux metrics were written into model-level and checkpoint-series artifacts
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.175258`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.949482`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; detached lexical head materially reduced the lexical-side special gap and improved final special behavior relative to `EXP-038`, but the final checkpoint still remains worse than `EXP-032`, and the remaining gap is now mostly structural rather than lexical.
- failures: no execution failure; final `target_validation.loss_total = 2.911644` stayed weak, final `target_special_eval.delta_loss_total = 0.354963` remained above zero, and `step50` still showed control collapse with `zero_z_art.delta_target_loss_total = -0.358804` and `zero_e_evt.delta_target_loss_total = -0.532724`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration.metrics.json
