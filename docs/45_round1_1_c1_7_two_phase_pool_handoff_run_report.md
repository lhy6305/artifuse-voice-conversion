# `round1.1 / C1.7 / phase-specific pool handoff` 100-step 报告

## 目的
- `EXP-029` 说明早期 union pool 很能拉 `step50` 和 main validation。
- `EXP-030 / EXP-031` 说明收窄 pool 能救 final special slice，但会丢掉前面的收益。
- 当前验证：
  - 前段保留 `clause>=4 OR multi_terminal`，后段切成 `clause>=4-only`，能不能两边都要一点。

## 当前配置
- 实验：
  - `EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration`
- phase1 pool：
  - `clause_count >= 4 OR multi_terminal`
  - `234 / 592`
- phase2 pool：
  - `clause_count >= 4`
  - `185 / 592`
- schedule：
  - `step1-25`: phase1, `3 priority slots`
  - `step26-45`: phase2, `1 priority slot`
  - `step46+`: seeded shuffle

## 关键结果
- final `target_validation.loss_total = 2.672052`
  - 比 `EXP-029` 还更好
- `step50 zero_e_evt.delta_target_loss_total = -0.556712`
  - 比 `EXP-030 / EXP-031` 好很多
  - 但不如 `EXP-029`
- final `target_special_eval.delta_loss_total = 0.103108`
  - 几乎和 `EXP-029` 一样差

## 结论
- phase-specific pool handoff 能保住大部分 main validation 和 `step50` 收益。
- 但它几乎完全救不回 final special slice。
- 这说明 final special 的坏影响很可能在前段就已经定型，后段再换 pool 已经太晚。
