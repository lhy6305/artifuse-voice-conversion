# `round1.1 / C1.7 / two-phase handoff + no-multi-terminal pool` 100-step 报告

## 目的
- `EXP-029` 把 main validation 和 `step50` 一起拉起来了，但 final special slice 明显变差。
- 当前验证：
  - 如果保留两段式 handoff，只把 priority pool 里的 `multi_terminal` 全排掉，final special slice 能不能回来。

## 当前配置
- 实验：
  - `EXP-20260315-030-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-no-multiterm-100step-calibration`
- pool 定义：
  - `clause_count >= 3`
  - 且 `exclude_structure_types = ["multi_terminal"]`
- pool 大小：
  - `168 / 592`
- schedule：
  - `step1-25`: `3 priority slots`
  - `step26-45`: `1 priority slot`
  - `step46+`: seeded shuffle

## 关键结果
- final `target_special_eval.delta_loss_total = -0.012386`
  - 相比 `EXP-029` 的 `0.102328` 明显回升
- final `target_validation.loss_total = 2.828666`
  - 明显差于 `EXP-029`
- `step50 zero_e_evt.delta_target_loss_total = -0.823020`
  - 也明显差于 `EXP-029`

## 结论
- 把 `multi_terminal` 全排掉，确实能把 final special slice 拉回来。
- 但代价是 `step50` 和 main validation 一起掉回去。
- 说明 `multi_terminal` 不是单纯的噪声，它同时也在提供 `EXP-029` 的一部分收益。
