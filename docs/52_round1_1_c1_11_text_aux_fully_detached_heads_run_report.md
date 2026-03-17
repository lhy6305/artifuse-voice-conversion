# `round1.1 / C1.11 / fully detached text_aux heads` 100-step 报告

## 目的
- `EXP-039` 已经说明：
  - detached lexical head 能把 lexical special gap 压下去
  - 但剩下仍有 structural gap 和 `step50` 回落
- 当前验证：
  - 不只 detach lexical head
  - 连 structural head 也一起 detach
  - 直接看 `text_aux` 整体停止回灌 shared trunk 后，final special 会不会继续改善

## 当前配置
- 实验：
  - `EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
- 新改动：
  - `model.text_aux_head_config.structural_detach_shared_input = true`
  - `model.text_aux_head_config.lexical_detach_shared_input = true`
  - loss 侧仍保留 split supervision：
    - `structural_weight = 8.0`
    - `lexical_weight = 5.0`

## 关键结果
- final `target_validation.loss_total = 2.91453`
  - 与 `EXP-039` 的 `2.911644` 几乎重合
- final `target_special_eval.delta_loss_total = 0.349915`
  - 只比 `EXP-039` 的 `0.354963` 略好
  - 改变量小到不足以说明 structural detach 是新杠杆
- final `zero_e_evt.delta_target_loss_total = 0.949163`
  - 与 `EXP-039` 的 `0.949482` 基本一致
- `step50 zero_z_art.delta_target_loss_total = -0.360537`
- `step50 zero_e_evt.delta_target_loss_total = -0.535462`
  - 也与 `EXP-039` 的中段回落几乎一致

## 新发现
- detached lexical head 之后，再把 structural head 也 detach，几乎没有额外收益。
- final special 的拆组差值仍是：
  - `delta_loss_text_aux_structural = 0.144724`
  - `delta_loss_text_aux_lexical = 0.005451`
- 这说明：
  - lexical gap 仍然已经不是主矛盾
  - 但 structural gap 也不是靠“继续切断 text_aux 梯度”就能解决的
- 换句话说：
  - 当前剩下的问题，不太像 `text_aux` head 梯度路径的问题
  - 更像 runtime 主干里的 event / clause-transition 学习本身仍和 challenge slice 不对齐

## 结论
- `EXP-040` 基本把 `text_aux head surgery` 这条线收口了。
- 现在可以更有把握地说：
  - lexical gradient 拖拽确实存在，`EXP-039` 已经证明
  - 但进一步把 structural gradient 也切掉，并没有继续改善
- 所以后续主线不该再继续做：
  - detached head 变体
  - `text_aux` head 路径级小修补

## 下一步
- 更值得转向的方向：
  - 直接改 runtime 主干侧的 structural proxy
  - 例如围绕 `event / clause_transition_aux / punctuation-only consistency` 做更贴近运行时的监督
- 简单说：
  - 后面要打的不是“text_aux 怎么接头”
  - 而是“event 路径本身怎样更稳地学到 punctuation-only 的结构行为”
