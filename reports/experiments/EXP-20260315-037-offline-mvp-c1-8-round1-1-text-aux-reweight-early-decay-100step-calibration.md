# Experiment Record Template

## Metadata
- experiment_id: EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration
- date: 2026-03-15T01:59:18
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, fixed `EXP-032` two-phase pool-handoff sampler, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the same punctuation-oriented `text_aux` reweight as `EXP-035`, but move the decay earlier so it linearly ramps down from `step61` to `step90` and stays off for the final ten steps
- hypothesis: if `EXP-036` failed because the late-stage reweight shutdown started too late, then moving the decay window earlier should preserve more of the `step80-90` special benefit while letting the final checkpoint recover toward `EXP-032`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split, upgraded `C1` sidecar and `EXP-032` sampler were reused unchanged; training logs confirm `text_aux_reweight.reweight_strength` is already down to `0.6896551724137931` at `step70` and reaches `0.0` by `step100`
- z_art_ablation: passed, final `zero_z_art.delta_target_loss_total = 0.21532`
- e_evt_ablation: passed, final `zero_e_evt.delta_target_loss_total = 0.931406`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; moving the decay earlier to `step61-90` still leaves the final checkpoint almost unchanged from `EXP-035 / 036`, so simple late-shutdown schedules are not the real lever.
- failures: no execution failure; even with the earlier decay window, final `target_validation.loss_total = 2.890341`, final `target_special_eval.delta_loss_total = 0.392194`, and final `zero_e_evt.delta_target_loss_total = 0.931406` remain effectively flat against `EXP-035 / 036`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration.metrics.json
