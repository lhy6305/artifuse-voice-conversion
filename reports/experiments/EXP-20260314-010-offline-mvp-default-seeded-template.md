# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-010-offline-mvp-default-seeded-template
- date: 2026-03-14T18:02:05
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

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
- summary: default seeded-shuffle template validated
- failures:
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-010-offline-mvp-default-seeded-template.metrics.json
- notes:
  - sampler_mode = seeded_shuffle
  - timing printed to stdout and written to metrics
  - validation loss_total = 52.288879 -> 51.498352 -> 50.715160
