# 500 Step Large-Scale 训练报告

## 目的
- 记录首个 `500 step` large-scale seeded-shuffle 训练的实际结果。
- 记录训练耗时、validation 趋势、checkpoint-series 消融趋势和 final special_eval 行为。

## 实验信息
- 实验：
  - `EXP-20260314-011-offline-mvp-large-scale-500`
- 配置：
  - `configs/offline_mvp_train_large_scale_seeded_500.json`
- 前置实验：
  - `EXP-20260314-010-offline-mvp-default-seeded-template`
- 运行阶段：
  - `run_stage = large_scale`
- 采样策略：
  - `sampler_mode = seeded_shuffle`
  - `seed = 20260314`

## 训练结果
- 总耗时：
  - `10.505491s`
- 总步数：
  - `500`
- checkpoint 数量：
  - `20`
- validation 次数：
  - `20`
- 最终 train `loss_total`：
  - `3.156266`
- validation `loss_total`：
  - `30.473316 -> 16.476933 -> 9.352869 -> 5.409974 -> ... -> 3.321292`

## 当前结论
### 1. 训练速度
- 在当前模型规模、当前 batch 和当前数据配置下，`500 step` large-scale 训练速度可接受。
- 本轮没有出现明显卡顿、写盘异常或 large_scale 门禁问题。

### 2. 主 validation 收敛
- validation `loss_total` 从 `30.473316` 持续下降到 `3.321292`。
- 到 `300` step 之后仍继续缓慢改善，但边际收益明显低于前 `100` 到 `150` step。

### 3. `z_art` 控制贡献
- checkpoint-series 显示：
  - `step25`: `zero_z_art.delta_target_loss_total = 0.25163`
  - `step250`: `0.642675`
  - `step500`: `1.4106`
- 当前解释：
  - `z_art` 在 large-scale 训练后期不但没有消失，反而成为更强的有效控制量。

### 4. `e_evt` 控制贡献
- checkpoint-series 显示：
  - `step25`: `zero_e_evt.delta_target_loss_total = 1.79018`
  - `step250`: `0.333262`
  - `step500`: `0.286237`
- 当前解释：
  - `e_evt` 并未完全失效，因为到 `step500` 仍保持正退化。
  - 但它不像 earlier small-scale 结果那样随训练继续增强，而是早期很强、后期明显回落。
- 这说明：
  - large-scale 后期模型对 `e_evt` 的依赖度下降，或被其他路径部分替代。

## final special_eval
- final `target_validation.loss_total = 1.752648`
- final `target_special_eval.loss_total = 2.118624`
- `delta_loss_total = 0.365976`
- `delta_loss_text_aux = 0.491746`
- `event_prob_mean`：
  - validation `0.402903`
  - special_eval `0.40301`

## 当前解释
- 和 earlier 小规模结果相比，final large-scale checkpoint 上：
  - `target_special_eval` 不再表现为“总 loss 更低的简单切片”
  - 而是开始表现出更高的总 loss
- 这与该 slice 的非完整发声属性并不矛盾。
- 当前更合理的解释是：
  - 模型在常规 validation 上进一步收敛后，challenge slice 的 stress 开始更明显暴露。

## 当前风险
### 1. `e_evt` 后期依赖下降
- 这是当前最需要继续跟踪的新现象。
- 风险不在于它已经失效，而在于：
  - 如果继续训练更久，可能进一步边缘化。

### 2. special slice 压力开始更明显
- `target_special_eval` 的总 loss 已高于常规 validation。
- 但因为该集合本身不是正常语音验证集，不能把这点直接解释成运行时质量退化。

## 建议的下一步
1. 以 `EXP-011` 为基线，继续做一次 focused 分析：
- 专看 `e_evt` 在 large-scale 后期为何回落。

2. 补一份“early vs late checkpoint 对比报告”：
- 对比 `step25 / step100 / step250 / step500`
- 重点看：
  - `z_art`
  - `e_evt`
  - validation
  - special_eval

3. 暂不直接继续加长训练步数：
- 先理解 `e_evt` 回落现象，再决定是否继续扩步数。
