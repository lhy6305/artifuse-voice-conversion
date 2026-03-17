# `round1.1 / C1.7 / two-phase handoff + multi-terminal tail cap` 100-step 报告

## 目的
- `EXP-031` 说明直接删掉 `multi_terminal-only` 尾巴会丢掉太多 main validation 和 `step50`。
- 当前验证：
  - 不删除它，只在 phase1 里把这批额外 `multi_terminal-only` 样本限到每批最多 `1` 条，看看能不能减轻 final special 回归。

## 关键结果
- final `target_validation.loss_total = 2.663196`
  - 很强
- `step50 zero_e_evt.delta_target_loss_total = -0.549967`
  - 也保住了大半
- final `target_special_eval.delta_loss_total = 0.111542`
  - 仍然明显在坏侧

## 结论
- 只给 `multi_terminal-only` 尾巴做限额，基本没有救到 final special。
- 这说明问题不是“尾巴数量太多”这么简单。
