# Experiment Record

## Metadata
- experiment_id: EXP-20260314-019-offline-mvp-c1-3-100step-calibration
- date: 2026-03-14T21:26:17
- owner: codex
- code_ref: workspace snapshot on 2026-03-14
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_3_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1/manifests/target_train.jsonl
- source_manifest: data_prep/round1/manifests/source_train.jsonl
- data_filters: hybrid_stratified_blocked formal split; target-side weak_event_hints attached
- known_exclusions: target_special_eval remains punctuation-only no_text_voice challenge slice

## Objective
- baseline_or_change: replace auxiliary weak_event-heavy route with event-loss bias plus mild target override on weak boundary frames
- hypothesis: integrating weak hints directly into event supervision should outperform C1.1/C1.2 and better preserve main validation

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: reused confirmed round1 manifests and hybrid_stratified_blocked split; dry-run passed before real run
- z_art_ablation: passed, delta_target_loss_total = 1.329502 at step100
- e_evt_ablation: passed, delta_target_loss_total = 1.409978 at step100
- r_res_ablation: not applicable, r_res remains disabled
- latency: not measured in this experiment

## Results
- summary: C1.3 is the strongest route-C variant so far and clearly better than C1.1/C1.2, but it only nearly matches B1.1-A rather than clearly beating it.
- failures: none
- follow_up: treat C1.3 as the current route-C baseline and move future work toward richer boundary labels or richer pause/terminal expression, not small weight sweeps; metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-019-offline-mvp-c1-3-100step-calibration.metrics.json
