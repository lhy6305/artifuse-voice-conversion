# `EXP-20260314-015-offline-mvp-b1-100step-calibration`

## Metadata
- experiment_id: `EXP-20260314-015-offline-mvp-b1-100step-calibration`
- date: `2026-03-14T20:05:57`
- owner: `codex`
- config_path: `F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json`

## Data
- split_dir: `F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked`
- target train / validation / special: `554 / 62 / 8`
- source train / validation: `483 / 54`
- target text feature version: `b1_punct_v1`

## Objective
- baseline_or_change:
  - 在 `B1-offline-minimal` 已通过 `20 step` 验证后，继续做 `100 step` 校准，判断它是否在更长训练下仍优于无 `B1` 基线。
- hypothesis:
  - 若 `B1` 的文本/标点监督确实有效，则在 `100 step` 时应继续保持或扩大对 `z_art / e_evt` 的正向支撑，而不是只在早期短暂显现。

## Model Scope
- offline_or_streaming: `offline`
- uses_text_in_training: `true`
- uses_text_in_runtime: `false`
- r_res_enabled: `false`

## Checks
- data_integrity: formal `hybrid_stratified_blocked` split reused
- z_art_ablation:
  - step100 `delta_target_loss_total = 1.332663`
- e_evt_ablation:
  - step100 `delta_target_loss_total = 1.407506`
- r_res_ablation:
  - not applicable, `r_res` remains disabled
- latency:
  - total wall time `2.828663s`

## Results
- summary:
  - `100 step` 真实训练、ablation、checkpoint-series 和 `special_eval` 系列均已跑通。
  - `B1` 到 `step100` 与无 `B1` 基线整体基本打平：
    - `target_loss_total 2.676195 vs 2.667123`
    - `source_loss_total 2.689358 vs 2.686110`
  - `target_special_eval` 上 `B1` 略稳：
    - `delta_loss_total 0.216202 vs 0.263015`
  - 当前更像“方向成立但特征版本仍偏弱”，还不足以只凭这一版就直接证明应放大到 `500 step`。
- failures:
  - 无运行失败。
  - 但 `20 step` 时看到的控制链优势，到 `100 step` 未继续显著扩大。
- follow_up:
  - 参考 `docs/22_b1_100step_calibration_report.md`
  - metrics file -> `F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-015-offline-mvp-b1-100step-calibration.metrics.json`
