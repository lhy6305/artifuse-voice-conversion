# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-027-offline-mvp-c1-7-round1-1-transition-aux-priority-curriculum-100step-calibration
- date: 2026-03-15T00:26:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_curriculum_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the independent clause-transition auxiliary loss and the same priority definition as `EXP-026`, but soften the curriculum to `priority_ratio = 0.5` and stop it after `step40`
- hypothesis: if `EXP-026` proves targeted sampling is a real lever but over-pulls the model toward transition-rich lexical records, a softer early-only curriculum should preserve part of the main-validation gain while reducing the special-slice regression and the mid-training dip distortion

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were both reused unchanged; priority pool count remains `234 / 592`, but curriculum is softened to `priority_ratio = 0.5` and only through `step40`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.739009`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.873269`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the softer early-only priority curriculum reverses the `EXP-026` special-slice regression and improves the `step50` dip substantially, but it gives back the main-validation win and becomes the weakest formal validation among the recent `C1.7` variants.
- failures: no execution failure; the key tradeoff remains unresolved because final `target_validation.loss_total = 2.813174` is worse than `EXP-025 / EXP-026`, even though `step50 zero_e_evt.delta_target_loss_total = -0.688658` and final `target_special_eval.delta_loss_total = -0.075832` both move in the desired direction.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-027-offline-mvp-c1-7-round1-1-transition-aux-priority-curriculum-100step-calibration.metrics.json
