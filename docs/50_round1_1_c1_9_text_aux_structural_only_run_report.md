# `round1.1 / C1.9 / text_aux structural-only split` 100-step 报告

## 目的
- `EXP-035 / 036 / 037` 已经说明：
  - `text_aux` 这条监督轴确实能改行为
  - 但整段重加权和 late shutdown 都救不回 final
- 当前验证：
  - 不再做整体 reweight
  - 直接把 `text_aux` supervision 拆成：
    - structural 组
    - lexical 组
  - 第一轮先做最强对照：
    - structural 组保留
    - lexical 组权重直接归零

## 当前配置
- 实验：
  - `EXP-20260315-038-offline-mvp-c1-9-round1-1-text-aux-structural-only-100step-calibration`
- 采样骨架：
  - 完全复用 `EXP-032`
- 新改动：
  - `losses.text_aux_split.enabled = true`
  - structural 组：
    - `2, 3, 4, 5, 6, 7, 11, 12`
  - lexical 组：
    - `0, 1, 8, 9, 10`
  - 权重：
    - `structural_weight = 1.0`
    - `lexical_weight = 0.0`

## 关键结果
- final `target_validation.loss_total = 2.89193`
  - 比 `EXP-032` 的 `2.672052` 更差
- final `target_special_eval.delta_loss_total = 0.398875`
  - 比 `EXP-035 / 036 / 037` 还略差
- final `zero_e_evt.delta_target_loss_total = 0.935605`
  - 仍显著弱于 `EXP-032` 的 `1.735497`
- `step90 target_special_eval.delta_loss_total = -0.269544`
  - 仍然只是在 late checkpoint 有收益
  - 最终 checkpoint 还是翻回坏侧

## 新发现
- 这轮不是“split 没接上”。
- 新指标已经明确分离：
  - final validation `loss_text_aux_structural = 0.123682`
  - final validation `loss_text_aux_lexical = 0.359214`
  - final special `loss_text_aux_structural = 0.329909`
  - final special `loss_text_aux_lexical = 0.621452`
- 也就是说：
  - structural 组确实被单独监督了
  - lexical 组虽然不参与 effective loss，但在同一个 head 里仍然明显漂移

## 结论
- “把 lexical 组权重打零”这一步本身不够。
- 它没有把 final special 从坏平台里拉出来。
- 当前更像的根因是：
  - 不是简单的组权重问题
  - 而是 lexical / structural 仍共用同一个 `text_aux` 头和同一套表示通道
  - 所以就算 lexical 组不计入 effective loss，它仍可能通过同头输出行为和共享表示耦合影响整体训练

## 下一步
- 这条线如果继续，不该再做：
  - lexical 权重从 `0.0` 改 `0.1`
  - 这类小数微调
- 更值得试的是：
  - 把 lexical supervision 从 shared trunk 上拆开
  - 例如 lexical 头走 detached hidden，或直接拆成独立 head / 独立梯度路径
