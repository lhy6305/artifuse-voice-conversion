# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-021-offline-mvp-c1-4-round1-1-100step-calibration
- date: 2026-03-14T22:42:19
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_4_round1_1_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, target-side weak event hints rebuilt for `round1.1`
- known_exclusions: `round1.1` recovered `42` lexical target samples into the main manifest; remaining isolated items are the `5` `no_text_voice` target records still kept out of the main training manifest

## Objective
- baseline_or_change: continue route-C `C1.4`, but move the same sampling/training recipe onto `round1.1` target-only upgraded data
- hypothesis: if the extra `42` lexical target records mainly add usable lexical/event coverage instead of noise, `round1.1` should outperform the old `round1` `C1.4` baseline without changing the split or sampler recipe

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and `C1` weak-event sidecar were both materialized before training; final counts are `target_train = 592`, `target_validation = 66`, `target_special_eval = 8`, `source_train = 483`, `source_validation = 54`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.886715`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.781482`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; `round1.1` does not materially improve the main validation line versus `EXP-020`, but it narrows the final `special_eval` loss gap from `0.181996` to `0.028766` and strengthens final `e_evt` dependence.
- failures: no execution failure after补齐 `EXP-021.metrics.json`; methodological issue remains that route-C still suffers a mid-training dependency dip, and in this run the `step50` dip is worse than `EXP-020` (`zero_e_evt.delta_target_loss_total = -0.854462`, `zero_z_art.delta_target_loss_total = -0.273851`).
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-021-offline-mvp-c1-4-round1-1-100step-calibration.metrics.json
