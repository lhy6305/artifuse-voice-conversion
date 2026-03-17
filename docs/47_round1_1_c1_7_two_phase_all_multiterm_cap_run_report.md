# `round1.1 / C1.7 / two-phase handoff + all multi-terminal cap` 100-step 报告

## 目的
- `EXP-033` 说明只限额额外 `multi_terminal-only` 尾巴，仍救不回 final special。
- 当前验证：
  - phase1 里所有 `multi_terminal` 样本都限制成每批最多 `1` 条，看看能不能真正改变 final special。

## 关键结果
- final `target_validation.loss_total = 2.669992`
  - 仍然很强
- `step50 zero_e_evt.delta_target_loss_total = -0.556362`
  - 也保住了大半
- final `target_special_eval.delta_loss_total = 0.105375`
  - 仍然几乎和 `EXP-029 / 032 / 033` 一样

## 结论
- 就算 phase1 对所有 `multi_terminal` 做了硬限额，final special 还是没变。
- 这说明继续在 phase1 采样份额上做小变体，短期内已经不太像有高价值方向。
