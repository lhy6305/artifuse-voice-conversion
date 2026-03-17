# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration
- date: 2026-03-15T01:54:38
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `EXP-035` 的 punctuation-oriented `text_aux` 维度重加权，但不再整段常开，而是从 `step81` 到 `step100` 线性衰减到普通 MSE
- hypothesis: if `EXP-035` 的失败主要来自后段 reweight 常开过久，那么保留前中段 reweight、并在末段线性退回普通 `text_aux`，应当比 `EXP-035` 更好地兼顾 final special、final validation 和 final `e_evt` dependence

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; training logs confirm `text_aux_reweight.reweight_strength` decays to `0.0` at `step100`
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.21563`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.931187`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; delaying the shutdown to `step81-100` produced a final checkpoint almost identical to `EXP-035`, so this schedule is too late to matter.
- failures: no execution failure; despite a real shutdown (`step90 reweight_strength = 0.5263157894736843`, `step100 = 0.0`), final `target_validation.loss_total = 2.889944`, final `target_special_eval.delta_loss_total = 0.393366`, and final `zero_e_evt.delta_target_loss_total = 0.931187` remain effectively unchanged from `EXP-035`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration.metrics.json
