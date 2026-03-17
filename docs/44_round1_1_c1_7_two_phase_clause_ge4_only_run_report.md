# `round1.1 / C1.7 / two-phase handoff + clause>=4-only pool` 100-step 报告

## 目的
- `EXP-030` 说明把 `multi_terminal` 全排掉太伤 main validation 和 `step50`。
- 当前验证：
  - 只去掉原先额外补进来的 `multi_terminal-only` 尾巴，保留 `clause_count >= 4`，能不能形成更干净的折中。

## 当前配置
- 实验：
  - `EXP-20260315-031-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-clause-ge4-only-100step-calibration`
- pool 定义：
  - `clause_count >= 4`
- pool 大小：
  - `185 / 592`
- schedule：
  - `step1-25`: `3 priority slots`
  - `step26-45`: `1 priority slot`
  - `step46+`: seeded shuffle

## 关键结果
- final `target_special_eval.delta_loss_total = -0.029908`
  - 比 `EXP-030` 还略好一点
- final `target_validation.loss_total = 2.843136`
  - 依然很差
- `step50 zero_e_evt.delta_target_loss_total = -0.843525`
  - 依然明显差于 `EXP-029`

## 结论
- 只去掉 `multi_terminal-only` 这条尾巴，也能改善 final special slice。
- 但还是保不住 `step50` 和 main validation。
- 这说明问题不只是那 `49` 条额外样本，长句里的 `multi_terminal` 子集本身也参与了收益和副作用。
