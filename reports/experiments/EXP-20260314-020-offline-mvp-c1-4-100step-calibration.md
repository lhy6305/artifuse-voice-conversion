# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-020-offline-mvp-c1-4-100step-calibration
- date: 2026-03-14T21:32:56
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_4_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1/manifests/target_manifest.jsonl
- source_manifest: data_prep/round1/manifests/source_manifest.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, target-side weak event hints enabled
- known_exclusions: current target_special_eval remains the punctuation-only `no_text_voice` challenge slice; `manifest_round1_excluded.jsonl` still has 47 isolated target samples pending separate review

## Objective
- baseline_or_change: continue route-C after `C1.3`, explicitly validate finer boundary pre/post target handling on top of event-target bias / override
- hypothesis: if boundary-adjacent presence / energy targets are made more explicit, route-C may slightly improve main validation and special-eval stability without weakening `z_art / e_evt` dependence

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: reused current round1 materialized split and formal manifests; no new integrity issue observed in this run
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.329629`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.410986`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; `C1.4` is slightly better than `C1.3` on main validation and special-eval, but still only effectively ties `B1.1-A`, so it is not strong enough to promote as the default route-C training setup.
- failures: no execution failure; remaining issue is methodological, not operational. route-C still shows a mid-training dependency dip around `step50`, so the run does not resolve the longer-standing stability concern.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-020-offline-mvp-c1-4-100step-calibration.metrics.json
