# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-030-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-no-multiterm-100step-calibration
- date: 2026-03-15T00:59:06
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_no_multiterm_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the `EXP-029` two-phase schedule, but redefine the priority pool as `clause_count >= 3` while excluding `multi_terminal`, so the sampler still sees transition-rich records without the explicit multi-terminal lexical bias
- hypothesis: if the final special-slice regression of `EXP-029` is mostly caused by the multi-terminal subset, removing that subset should recover punctuation-only robustness while keeping at least part of the `step50` and main-validation gains from the two-phase handoff

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were reused unchanged; dry-run and direct batch-plan inspection confirmed the narrowed priority pool is `168 / 592`, with `3 priority slots` for `step1-25`, `1 priority slot` for `step26-45`, and seeded shuffle afterwards
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.732808`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.717955`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; excluding `multi_terminal` from the two-phase priority pool almost fully removes the final special-slice regression, but it also gives back most of the `step50` and main-validation gains that made `EXP-029` interesting.
- failures: no execution failure; the narrowed pool fails as a balanced replacement because final `target_special_eval.delta_loss_total = -0.012386` is much better than `EXP-029`, but final `target_validation.loss_total = 2.828666` and `step50 zero_e_evt.delta_target_loss_total = -0.823020` both collapse toward the weaker side.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-030-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-no-multiterm-100step-calibration.metrics.json
