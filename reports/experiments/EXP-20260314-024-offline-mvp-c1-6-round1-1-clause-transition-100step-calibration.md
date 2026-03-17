# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-024-offline-mvp-c1-6-round1-1-clause-transition-100step-calibration
- date: 2026-03-14T23:45:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_6_round1_1_clause_transition_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `round1.1` data and sampling fixed, but replace the clause-body floor recipe with clause-end transition supervision that differentiates middle vs final endings
- hypothesis: if the unresolved `step50` dip mainly comes from under-modeled clause-end transitions rather than clause-body activity, a role-aware clause-transition recipe should preserve final `e_evt` dependence while improving mid-training stability more directly than `EXP-023`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were both reused unchanged; final counts remain `target_train = 592`, `target_validation = 66`, `target_special_eval = 8`, `source_train = 483`, `source_validation = 54`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.886746`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.781535`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; the clause-transition route is operational, but this recipe does not materially change the training trajectory and lands almost exactly on the old `EXP-021` profile instead of improving the unresolved `step50` dependency dip.
- failures: no execution failure; methodologically the target remains unmet because `step50 zero_e_evt.delta_target_loss_total = -0.854465` and `step50 zero_z_art.delta_target_loss_total = -0.273854`, effectively identical to `EXP-021`, while final `target_special_eval.delta_loss_total = 0.028482` also stays on the same old level.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-024-offline-mvp-c1-6-round1-1-clause-transition-100step-calibration.metrics.json
