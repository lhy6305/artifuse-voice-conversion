# `round1.1 / C1.12 / boundary contrast aux` 100-step 报告

## 目的
- `EXP-040` 已经把 `text_aux head surgery` 这条线收口了。
- 当前验证：
  - 不再改 `text_aux head`
  - 直接在 runtime event 路径上加一层 boundary contrast aux
  - 用边界前后 `presence / energy` 的相对跌落关系，替代继续堆 `text_aux` 结构手术

## 当前配置
- 实验：
  - `EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
- 主干设置：
  - 复用 `EXP-039` 的 detached lexical head
- 新改动：
  - `losses.boundary_contrast_aux.enabled = true`
  - `weight = 0.25`
  - 对 `pause / terminal` 边界分别约束：
    - `pre_post_presence_margin`
    - `pre_post_energy_margin`

## 关键结果
- final `target_validation.loss_total = 2.924252`
  - 比 `EXP-039` 的 `2.911644` 更差
- final `target_special_eval.delta_loss_total = 0.342355`
  - 表面上比 `EXP-039` 的 `0.354963` 略好
  - 但这不是行为改善
- final `zero_e_evt.delta_target_loss_total = 0.949482`
  - 和 `EXP-039` 完全一样
- `step50 zero_z_art.delta_target_loss_total = -0.358804`
- `step50 zero_e_evt.delta_target_loss_total = -0.532724`
  - 也和 `EXP-039` 完全一样

## 新发现
- 这轮最大的结论不是“新 aux 有效”，而是“这个改善基本是记账改善，不是行为改善”。
- 证据非常硬：
  - validation `loss_boundary_contrast_aux = 0.050434`
  - special `loss_boundary_contrast_aux = 0.0`
  - 所以 `delta_loss_total` 会被机械拉低 `0.050434`
- 同时其余关键行为指标几乎和 `EXP-039` 重合：
  - `delta_loss_text_aux_structural = 0.143281`
  - `delta_loss_text_aux_lexical = 0.007416`
  - `delta_event_presence_prob_mean = -0.035345`
  - `delta_event_energy_prob_mean = -0.030103`
  - `step50 / final` ablation 依赖也没有变化
- 这说明：
  - `boundary_contrast_aux` 本身不是没接上
  - 它在 formal validation 上确实有非零值
  - 但它没有给模型带来独立的新行为变化
  - 更像是和现有 `event_boundary_bias / clause_transition_aux` 高度重叠

## 结论
- 这轮不支持把 `boundary_contrast_aux` 升为主线。
- 它没有修 final special，也没有修 `step50`。
- 更重要的是：
  - 以后不能只看 `delta_loss_total`
  - 因为如果新 aux 只在 validation 生效、不在 special slice 生效，就会制造“看起来更好”的假象

## 下一步
- 不再优先继续做：
  - `boundary_contrast_aux` 的 margin / weight 小变体
- 更值得试的方向：
  - 直接做 special-oriented 的 runtime proxy
  - 要求训练和 special slice 两边都能真正命中
  - 例如 punctuation-only consistency 或显式 challenge-like target 约束
