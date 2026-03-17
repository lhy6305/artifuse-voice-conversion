# Experiment Record Template

## Metadata
- experiment_id: EXP-20260316-027-offline-mvp-d72-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration
- date: 2026-03-16T15:41:58
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d72_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json

## Data
- target_manifest:
- source_manifest:
- data_filters:
- known_exclusions:

## Objective
- baseline_or_change:
- hypothesis:
- route_policy: validation_strict
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}
- anchor_reference: EXP-20260316-026-offline-mvp-d71-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration

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
- summary: initialized
- failures:
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260316-027-offline-mvp-d72-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-teacher-source-d22late-20step-calibration.metrics.json
