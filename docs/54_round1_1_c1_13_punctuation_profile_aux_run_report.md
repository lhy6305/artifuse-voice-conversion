# `round1.1 / C1.13 / punctuation profile aux` 100-step 报告

## 目的
- `EXP-041` 的问题很明确：
  - 新 aux 只在 validation 有值
  - 在 special slice 上是 `0`
  - 所以会制造假改善
- 当前验证：
  - 继续保留 `EXP-039` 的 detached lexical head
  - 但把新 aux 改成真正 special-facing 的 `punctuation_profile_aux`
  - 直接约束整句级 `presence mean / energy mean / peak ratio`
  - 让这项 loss 在 punctuation-only challenge slice 上也能真实激活

## 当前配置
- 实验：
  - `EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
- 主干设置：
  - 复用 `EXP-039` 的 detached lexical head
- 新改动：
  - `losses.punctuation_profile_aux.enabled = true`
  - `weight = 0.2`
  - 依据 clean text 的标点占比，约束：
    - utterance-level `event_presence_prob_mean`
    - utterance-level `event_energy_prob_mean`
    - utterance-level `event_presence_peak_ratio`

## 关键结果
- final `target_validation.loss_total = 2.910157`
  - 与 `EXP-039` 的 `2.911644` 几乎打平
- final `target_special_eval.delta_loss_total = 0.356926`
  - 略差于 `EXP-039` 的 `0.354963`
- final `zero_e_evt.delta_target_loss_total = 0.948263`
  - 仍与 `EXP-039` 的 `0.949482` 基本一致
- `step50 zero_z_art.delta_target_loss_total = -0.358656`
- `step50 zero_e_evt.delta_target_loss_total = -0.533721`
  - 中段回落也几乎没变

## 新发现
- 这轮和 `EXP-041` 最大的区别是：
  - 新 aux 终于在 special slice 上不再是 `0`
- final：
  - validation `loss_punctuation_profile_aux = 0.01164`
  - special `loss_punctuation_profile_aux = 0.001526`
  - `delta_loss_punctuation_profile_aux = -0.010114`
- 这说明：
  - 这次不是“会计口径假改善”
  - 这项 loss 在 challenge slice 上确实被命中了
- 但坏消息也同样明确：
  - 即使 special 上真实激活了
  - 模型的其余核心行为仍几乎不变
  - 例如：
    - `delta_event_presence_prob_mean = -0.035479`
    - `delta_event_energy_prob_mean = -0.030196`
    - `delta_loss_text_aux_structural = 0.143615`
    - `delta_loss_text_aux_lexical = 0.007612`
  - 全都和 `EXP-039` 非常接近

## 结论
- `punctuation_profile_aux` 比 `boundary_contrast_aux` 更干净，因为它在 special 上真的激活了。
- 但即便这样，它仍然没有变成新杠杆。
- 这意味着：
  - 当前问题已经不太像“再加一个更聪明的 auxiliary loss 就能解决”
  - auxiliary-loss 这条线在当前 scaffold 上，基本也接近收口了

## 下一步
- 不再优先继续做：
  - `punctuation_profile_aux` 的 weight / target 小数微调
  - 其他同类 utterance-profile auxiliary
- 更值得转向的方向：
  - checkpoint 选择 / 训练流程层
  - 或更强的训练数据视角改造，而不是继续在现有 loss 上叠 proxy
