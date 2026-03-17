# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration
- date: 2026-03-15T21:30:24
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d40_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_20step_smallscale_seeded_shuffle.json

## Data
- target_manifest:
- source_manifest:
- data_filters:
- known_exclusions:

## Objective
- baseline_or_change:
- hypothesis:
- route_policy: default_minimax
- route_budget_or_floor: {"max_validation_budget_over_best": 0.05, "require_best_e_evt_floor": false, "require_best_z_art_floor": false, "special_priority": false, "z_art_priority": false}
- anchor_reference: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration

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
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration.metrics.json
