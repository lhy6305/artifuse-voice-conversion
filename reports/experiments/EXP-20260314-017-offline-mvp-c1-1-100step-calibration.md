# Experiment Record

## Metadata
- experiment_id: EXP-20260314-017-offline-mvp-c1-1-100step-calibration
- date: 2026-03-14T20:47:02
- owner: codex
- code_ref: workspace snapshot on 2026-03-14
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_1_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1/manifests/target_train.jsonl
- source_manifest: data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked formal split; target-side weak_event_hints attached
- known_exclusions: target_special_eval remains punctuation-only no_text_voice challenge slice

## Objective
- baseline_or_change: add target-side weak boundary supervision on top of B1.1-A
- hypothesis: weak_event hints may strengthen e_evt dependence beyond B1.1-A without hurting main validation

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: reused confirmed round1 manifests and hybrid_stratified_blocked split
- z_art_ablation: passed, delta_target_loss_total = 1.350602 at step100
- e_evt_ablation: passed, delta_target_loss_total = 1.433922 at step100
- r_res_ablation: not applicable, r_res remains disabled
- latency: not measured in this experiment

## Results
- summary: C1.1 completed and proved weak-event hints can be stably integrated, but step100 main validation stayed worse than B1.1-A while control gains were only slight.
- failures: none
- follow_up: compare with lighter weak_event weight via EXP-20260314-018-offline-mvp-c1-2-100step-calibration; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-017-offline-mvp-c1-1-100step-calibration.metrics.json
