# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration
- date: 2026-03-15T14:10:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-039` detached lexical head and current event/clause supervision unchanged, but add a special-facing punctuation profile auxiliary that supervises utterance-level `presence mean / energy mean / peak ratio` as a function of punctuation density so the new loss also activates on punctuation-only challenge slices
- hypothesis: if the current remaining error is really about punctuation-only runtime behavior, then a punctuation-profile auxiliary should change final special behavior more honestly than `boundary_contrast_aux`, because it supervises a profile that exists on both regular target records and the special challenge slice

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; dry-run, full `100 step` training and all eval passes completed cleanly, and the wrapped metrics payload preserved checkpoint resolution for follow-up evaluations
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.178659`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.948263`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; punctuation-profile supervision successfully activated on both regular validation and the punctuation-only special slice, but it still failed to produce meaningful behavior changes relative to `EXP-039`.
- failures: no execution failure; final `target_validation.loss_total = 2.910157` only tied the prior detached-head baseline, final `target_special_eval.delta_loss_total = 0.356926` got slightly worse, and `step50` / final control dependence remained effectively unchanged even though `loss_punctuation_profile_aux` was non-zero on the special slice.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration.metrics.json
