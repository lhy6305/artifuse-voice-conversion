# `round1.1 / C1.8 / text_aux reweight schedule` 跟进报告

## 目的
- `EXP-035` 已经说明：
  - punctuation-oriented `text_aux` reweight 是真杠杆
  - 但整段 `100 step` 常开会把 final checkpoint 带坏
- 当前跟进想验证一个更窄的问题：
  - 问题是不是只出在“后段关得太晚”

## 本轮实验
- `EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration`
  - `step81-100` 线性衰减到普通 MSE
- `EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration`
  - `step61-90` 线性衰减到普通 MSE
  - `step91-100` 完全回到普通 MSE

## 实现核对
- schedule 不是“配了但没生效”。
- 训练日志已确认：
  - `EXP-036 step90 reweight_strength = 0.5263157894736843`
  - `EXP-036 step100 reweight_strength = 0.0`
  - `EXP-037 step70 reweight_strength = 0.6896551724137931`
  - `EXP-037 step100 reweight_strength = 0.0`
- 也就是说，这两轮确实都在后段把 reweight 退回了普通 `text_aux`。

## 关键结果
- `EXP-036`
  - final `target_validation.loss_total = 2.889944`
  - final `target_special_eval.delta_loss_total = 0.393366`
  - final `zero_e_evt.delta_target_loss_total = 0.931187`
- `EXP-037`
  - final `target_validation.loss_total = 2.890341`
  - final `target_special_eval.delta_loss_total = 0.392194`
  - final `zero_e_evt.delta_target_loss_total = 0.931406`
- 对照：
  - `EXP-035`
    - final `target_validation.loss_total = 2.889709`
    - final `target_special_eval.delta_loss_total = 0.39305`
    - final `zero_e_evt.delta_target_loss_total = 0.931855`

## 结论
- `EXP-036 / 037` 和 `EXP-035` 几乎重合。
- 这说明：
  - 单纯在训练后段关闭 `text_aux reweight`
  - 即使真的关掉了
  - 也几乎救不回 final checkpoint
- 更直白地说：
  - 问题不是“尾巴多开了十几二十步”
  - 而是 reweight 在更早阶段就已经把表示空间写定了

## 当前判断
- 这条线下一步如果还要继续，不该再做：
  - `step80+` 才开始 decay
  - `step60+` 才开始 decay
- 更值得试的方向是：
  - 更早的 phase handoff
  - 或不再做纯时间 schedule，而改成更细的 supervision target 拆分
  - 例如只对 punctuation / structure 子维度保留监督，而不是继续整体共用一个 `text_aux` 头
