# Experiment Record

## Metadata
- experiment_id: EXP-20260314-018-offline-mvp-c1-2-100step-calibration
- date: 2026-03-14T21:14:41
- owner: codex
- code_ref: workspace snapshot on 2026-03-14
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_2_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1/manifests/target_train.jsonl
- source_manifest: data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked formal split; same target-side weak_event_hints as C1.1
- known_exclusions: target_special_eval remains punctuation-only no_text_voice challenge slice

## Objective
- baseline_or_change: reduce weak_event weight from 0.2 to 0.1 after C1.1
- hypothesis: lighter weak-event pressure may recover main validation while preserving most of the control-path gain

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: reused confirmed round1 manifests and hybrid_stratified_blocked split
- z_art_ablation: passed, delta_target_loss_total = 1.337895 at step100
- e_evt_ablation: passed, delta_target_loss_total = 1.419051 at step100
- r_res_ablation: not applicable, r_res remains disabled
- latency: not measured in this experiment

## Results
- summary: C1.2 slightly improved main validation over C1.1, but remained behind B1.1-A and stayed nearly identical to C1.1 overall, so weight-only tuning is not enough to justify promotion.
- failures: none
- follow_up: current route-C status should be summarized back into docs before any further event-supervision design changes; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-018-offline-mvp-c1-2-100step-calibration.metrics.json
