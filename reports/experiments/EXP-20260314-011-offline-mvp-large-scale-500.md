# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-011-offline-mvp-large-scale-500
- date: 2026-03-14T18:09:47
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_large_scale_seeded_500.json

## Data
- target_manifest:
- source_manifest:
- data_filters:
- known_exclusions:

## Objective
- baseline_or_change:
- hypothesis:

## Model Scope
- offline_or_streaming:
- uses_text_in_training:
- uses_text_in_runtime:
- r_res_enabled:

## Checks
- data_integrity:
- z_art_ablation:
- e_evt_ablation:
- r_res_ablation:
- latency:

## Results
- summary: first 500-step large-scale seeded-shuffle run completed
- failures:
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-011-offline-mvp-large-scale-500.metrics.json
- notes:
  - total duration = 10.505491s
  - validation loss_total = 30.473316 -> 3.321292
  - checkpoint-series and final special_eval completed
