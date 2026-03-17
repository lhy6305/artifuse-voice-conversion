# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-025-offline-mvp-c1-7-round1-1-clause-transition-aux-100step-calibration
- date: 2026-03-14T23:59:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `round1.1 / C1.4` boundary recipe unchanged, but add an independent clause-transition auxiliary loss instead of reusing the same `event_boundary_bias` override path
- hypothesis: if the previous clause-aware attempts were being swallowed by the shared boundary-bias channel, a standalone clause-transition auxiliary loss should create a more independent learning signal and improve the unresolved `step50` dependency dip more clearly than `EXP-024`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were both reused unchanged; final counts remain `target_train = 592`, `target_validation = 66`, `target_special_eval = 8`, `source_train = 483`, `source_validation = 54`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.887237`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.791502`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the independent clause-transition auxiliary loss is no longer being fully swallowed by the old boundary-bias path, but it still does not improve the unresolved `step50` dependency dip and slightly weakens the main validation line relative to `EXP-021`.
- failures: no execution failure; methodologically the target remains unmet because `step50 zero_e_evt.delta_target_loss_total = -0.854869` and `step50 zero_z_art.delta_target_loss_total = -0.274127` remain effectively unchanged, while final `target_validation.loss_total = 2.778521` is worse than `EXP-021` and final `target_special_eval.delta_loss_total = 0.010553` still does not beat `EXP-023`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-025-offline-mvp-c1-7-round1-1-clause-transition-aux-100step-calibration.metrics.json
