# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-023-offline-mvp-c1-5-round1-1-clause-span-100step-calibration
- date: 2026-03-14T23:13:39
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_5_round1_1_clause_span_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `round1.1 / C1.4` fixed, but add the first clause-aware route-C supervision that consumes `clause_spans` and `utterance_structure_type`
- hypothesis: if route-C instability partly comes from labels being too boundary-only, mild clause-role supervision may preserve final gains while reducing the `step50` dependency dip more meaningfully than pure loss reweighting

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded sidecar were both materialized before training; final counts remain `target_train = 592`, `target_validation = 66`, `target_special_eval = 8`, `source_train = 483`, `source_validation = 54`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.866395`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.807451`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the first clause-aware route-C attempt is operational and keeps final `e_evt` dependence high, but it does not improve the `step50` dependency dip and does not beat the simpler `EXP-021 / EXP-022` round1.1 variants on overall stability.
- failures: no execution failure; methodological target remains unmet because `step50 zero_e_evt.delta_target_loss_total = -0.853283` and `step50 zero_z_art.delta_target_loss_total = -0.273785`, essentially unchanged from `EXP-021`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-023-offline-mvp-c1-5-round1-1-clause-span-100step-calibration.metrics.json
