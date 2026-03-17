# `EXP-20260314-016-offline-mvp-b1-1a-100step-calibration`

## Metadata
- experiment_id: `EXP-20260314-016-offline-mvp-b1-1a-100step-calibration`
- date: `2026-03-14T20:27:56`
- owner: `codex`
- config_path: `F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_b1_1a_smallscale_100_seeded_shuffle.json`

## Data
- split_dir: `F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked`
- target train / validation / special: `554 / 62 / 8`
- source train / validation: `483 / 54`
- target text feature version: `b1_1_stats_v2`

## Objective
- baseline_or_change:
  - 验证 `B1.1-A` 这版“更细的整句统计特征”是否比 `B1-offline-minimal` 更值得继续放大。
- hypothesis:
  - 如果 `B1.1-A` 有效，则在 `step100` 时应至少在主验证集或 `z_art / e_evt` 控制敏感度上明显优于 `B1`。

## Model Scope
- offline_or_streaming: `offline`
- uses_text_in_training: `true`
- uses_text_in_runtime: `false`
- r_res_enabled: `false`

## Checks
- data_integrity: formal `hybrid_stratified_blocked` split reused
- z_art_ablation:
  - step100 `delta_target_loss_total = 1.330542`
- e_evt_ablation:
  - step100 `delta_target_loss_total = 1.408664`
- r_res_ablation:
  - not applicable, `r_res` remains disabled
- latency:
  - total wall time `2.886782s`

## Results
- summary:
  - `100 step` 真实训练、ablation、checkpoint-series 和 `special_eval` 系列均已完成。
  - `B1.1-A` 在主验证集上未形成比 `B1` 更明显的增益：
    - `target_loss_total 2.680581`，相比 `B1 = 2.676195`
  - `target_special_eval` 略稳：
    - `delta_loss_total 0.185337`，相比 `B1 = 0.216202`
  - 当前结论是：
    - `B1.1-A` 仍不足以单独支撑继续深挖整句级统计特征，后续应继续进入 route-C。
- failures:
  - 首次错误地把训练与依赖 checkpoint 的评估命令并行启动，导致评估抢先读取尚未写完的 metrics 并报错；之后已按正确顺序补跑完成。
- follow_up:
  - 参考 `docs/24_b1_1a_run_report.md`
  - metrics file -> `F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-016-offline-mvp-b1-1a-100step-calibration.metrics.json`
