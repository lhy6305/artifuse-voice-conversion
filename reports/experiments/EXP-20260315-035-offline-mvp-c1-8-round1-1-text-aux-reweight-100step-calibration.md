# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration
- date: 2026-03-15T01:42:43
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `EXP-032` sampler and clause-transition aux unchanged, but reweight `text_aux` supervision away from lexical-heavy dimensions and toward punctuation / structure dimensions inside `b1_1_stats_v2`
- hypothesis: if the final special-slice regression mainly comes from shared representation drift induced by lexical-heavy `text_aux` supervision, then punctuation-oriented `text_aux` reweighting should improve final `target_special_eval` without fully giving back `EXP-032` main-validation and `step50` gains

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` two-phase pool-handoff sampler were reused unchanged; dry-run and training both completed cleanly, and effective `text_aux` metrics were written into train/eval artifacts
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.215737`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.931855`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; punctuation-oriented `text_aux` reweight proved to be a real late-stage behavior lever, but the always-on version failed as a final configuration because final main validation, final special slice and final `e_evt` dependence all regressed against `EXP-032`.
- failures: no execution failure; final `target_validation.loss_total = 2.889709`, final `target_special_eval.delta_loss_total = 0.39305`, and final `zero_e_evt.delta_target_loss_total = 0.931855` are all worse than `EXP-032`, although `special_eval_series` still shows a strong late checkpoint at `step90` with `delta_loss_total = -0.2803`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration.metrics.json
