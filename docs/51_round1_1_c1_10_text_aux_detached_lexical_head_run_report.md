# `round1.1 / C1.10 / detached lexical text_aux head` 100-step 报告

## 目的
- `EXP-038` 已经说明：
  - 仅仅把 lexical 组权重打成 `0.0`
  - 但 lexical / structural 仍共用同一个 `text_aux` head
  - final special 仍然卡在坏平台上
- 当前验证：
  - 保留 split supervision
  - 但把 lexical prediction 改成单独 head
  - 并让 lexical head 只吃 `pooled_hidden.detach()`
  - 直接验证 lexical 梯度是否在拖 shared trunk

## 当前配置
- 实验：
  - `EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
- 新改动：
  - `model.text_aux_head_config.enabled = true`
  - `mode = split_heads`
  - structural 维度：
    - `2, 3, 4, 5, 6, 7, 11, 12`
  - lexical 维度：
    - `0, 1, 8, 9, 10`
  - `lexical_detach_shared_input = true`
  - loss 侧仍保留 split supervision：
    - `structural_weight = 8.0`
    - `lexical_weight = 5.0`

## 关键结果
- final `target_validation.loss_total = 2.911644`
  - 比 `EXP-032` 的 `2.672052` 更差
  - 也比 `EXP-038` 的 `2.89193` 更差一点
- final `target_special_eval.delta_loss_total = 0.354963`
  - 明显好于 `EXP-038` 的 `0.398875`
  - 也好于 `EXP-035 / 036 / 037` 的 `0.39x`
  - 但仍然没有回到 `0` 以下
- final `zero_e_evt.delta_target_loss_total = 0.949482`
  - 比 `EXP-038` 的 `0.935605` 略好
  - 但仍远弱于 `EXP-032` 的 `1.735497`
- `step80 target_special_eval.delta_loss_total = -0.551359`
- `step90 target_special_eval.delta_loss_total = -0.293919`
  - 说明 detached lexical head 仍保留了 late checkpoint 的 special 优势
  - final 虽然翻回坏侧，但翻车幅度比 `EXP-035 / 038` 更小

## 新发现
- 这轮第一次把 lexical gap 真正压下来了。
- final special 的拆组差值已经变成：
  - `delta_loss_text_aux_structural = 0.143281`
  - `delta_loss_text_aux_lexical = 0.007416`
- 对照 `EXP-038`：
  - lexical 组在 challenge slice 上的漂移不再是主矛盾
  - 剩下更像是 structural 监督本身仍把 special slice 拉坏了
- 但 `step50` 问题没有被修掉：
  - `step50 zero_z_art.delta_target_loss_total = -0.358804`
  - `step50 zero_e_evt.delta_target_loss_total = -0.532724`
  - 仍然说明中段控制依赖在回落

## 结论
- `detached lexical head` 是这条线目前最有信息量的一步。
- 它支持了当前的核心判断：
  - lexical supervision 拖 shared trunk，确实是问题的一部分
- 但它也把剩余问题暴露得更清楚了：
  - final special 现在主要不是 lexical gap
  - 而是 structural supervision 和中段控制稳定性还没理顺
- 所以这轮不是“最终解”，但它把根因从“词汇拖拽”进一步收缩到了“结构监督本身”。

## 下一步
- 不再优先做：
  - lexical 权重小数微调
  - late schedule 小变体
  - phase1 sampler 配额微调
- 更值得试的是：
  - structural head 也走独立路径
  - 或对 structural supervision 再细分成更贴 runtime 的子目标
  - 例如把 punctuation / clause-transition 与 lexical 彻底分离后，再单独约束结构侧
