# `e_evt` Early-vs-Late Focused 分析

## 目的
- 专门分析 `EXP-20260314-011-offline-mvp-large-scale-500` 中 `e_evt` 为何表现为：
  - early checkpoint 很强
  - late checkpoint 仍有效，但依赖明显回落
- 同时对照 `target_special_eval`，避免只看常规 validation 得出片面结论。

## 使用数据
### 1. checkpoint-series 消融
- 来源：
  - `reports/eval/offline_mvp_checkpoint_series_exp011/checkpoint_series_eval.json`
- 核心对比步点：
  - `step25`
  - `step100`
  - `step250`
  - `step500`

### 2. special-eval series
- 来源：
  - `reports/eval/offline_mvp_special_eval_series_exp011/special_eval_series.json`
- 同样使用：
  - `step25`
  - `step100`
  - `step250`
  - `step500`

## 关键事实
### 1. `e_evt` 消融敏感度
- `step25`
  - `zero_e_evt.delta_target_loss_total = 1.79018`
- `step100`
  - `1.404717`
- `step250`
  - `0.333262`
- `step500`
  - `0.286237`

### 2. `z_art` 消融敏感度
- `step25`
  - `zero_z_art.delta_target_loss_total = 0.25163`
- `step100`
  - `1.306952`
- `step250`
  - `0.642675`
- `step500`
  - `1.4106`

### 3. special slice 总 loss 相对常规 validation 的变化
- `step25`
  - `delta_loss_total = -3.877301`
  - 说明 special slice 当时仍显得“更容易”
- `step100`
  - `delta_loss_total = 0.263015`
  - 这里已经翻转成“special slice 更难”
- `step250`
  - `delta_loss_total = 0.373924`
- `step500`
  - `delta_loss_total = 0.365976`

### 4. `event_prob_mean` 的变化
- validation:
  - `0.487313 -> 0.43997 -> 0.417956 -> 0.402903`
- special_eval:
  - `0.486317 -> 0.43091 -> 0.393636 -> 0.40301`

## 当前解释
### 1. `e_evt` 更像 early training 的强控制支架
- 在 `step25` 时，模型仍明显依赖 `e_evt`。
- 这符合事件路径在训练早期提供粗粒度结构约束的直觉。

### 2. 到中后期，`z_art` 承担了更多可替代信息
- 到 `step100`，`z_art` 与 `e_evt` 已接近同量级。
- 到 `step250 / 500`，`z_art` 明显比 `e_evt` 更关键。
- 当前更合理的解释是：
  - 随着模型收敛，`z_art` 和基础声学路径吸收了更多原先依赖事件路径的可预测结构。

### 3. `e_evt` 不是失效，而是“退到次要但仍有效”
- `step500` 时 `zero_e_evt.delta_target_loss_total` 仍为正。
- 所以不能解释成：
  - `e_evt` 没用
- 更应解释成：
  - `e_evt` 仍提供增益，但不再是主导控制量。

### 4. special slice 的翻转很关键
- `step25` 时 special slice 总 loss 更低。
- 从 `step100` 开始，它稳定高于常规 validation。
- 这说明随着模型在正常验证集上继续收敛，nonverbal challenge slice 的 stress 被更真实地暴露出来。
- 这和 `e_evt` 回落并不矛盾：
  - 事件路径变弱，不代表 challenge slice 会更容易。
  - 恰恰可能说明模型在后期更偏向主分布内容结构，而对非完整发声的事件样式不再额外强化。

## 当前最合理的暂时结论
- `e_evt` 在当前系统里更像：
  - early-stage 结构支架
  - late-stage 次要增益项
- `z_art` 则更像：
  - late-stage 主控制量

这不是最终定论，但已经足够说明：
- 后续若继续优化控制链，不能只看“有没有事件头”。
- 更重要的是判断：
  - 为什么事件信息在后期没有继续保持高依赖
  - 是否需要专门的 loss 或结构，防止 `e_evt` 被后期弱化

## 当前风险
### 1. `e_evt` 可能被主干路径部分吞并
- 若继续训练更久，`e_evt` 可能进一步边缘化。

### 2. 单看最终 loss 会掩盖这个问题
- 因为总 validation loss 仍在变好。
- 如果不看消融，只会误判为“控制链整体越来越好”。

## 建议下一步
1. 做一次 `e_evt` 约束增强方案调研
- 只做数据收集和方案报告，不先改结构。

2. 在后续实验里固定加入两类观察
- `z_art / e_evt` checkpoint-series
- selected checkpoint 的 special-eval series

3. 在引入新损失前，先确认是否存在“事件标签过粗或过易被其他路径替代”的数据层原因
