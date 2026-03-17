# `round1.1 / D34+D35 / new-trio cross-anchor follow-up` 报告

## 目的
- `D33` 已经把 special-side anchor 从 `D26` 升级成:
  - `special` 更强
  - `e_evt / z_art` 也更强
- 当前主线最值得验证的问题不再是“`D26` 还能不能再修”，
  而是:
  - 在新两端 `D22 <-> D33` 之间，
  - naive cross-anchor consolidation 能不能自然造出新的 minimax / joint winner

本轮保持最小设计:
- `D34 = D22 init + D33 teacher`
- `D35 = D33 init + D22 teacher`
- 两条线都保留 fused-hidden consistency

## 配置与实验
### D34
- 配置:
  - `configs/offline_mvp_train_d34_round1_1_d22_init_d33_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration`
- 设计:
  - `student init = D22 final`
  - `teacher = D33 final`
  - 保持 `D22` 的 core-only gate / sampler
  - `teacher_consistency.fused_hidden_weight = 0.05`

### D35
- 配置:
  - `configs/offline_mvp_train_d35_round1_1_d33_init_d22_teacher_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration`
- 设计:
  - `student init = D33 final`
  - `teacher = D22 final`
  - 保持 `D33` 的 short-pause gate / sampler
  - `teacher_consistency.fused_hidden_weight = 0.05`

## 关键事实
### 1. 两条线都不是挂空配置
- `D34 step1`
  - `loss_teacher_consistency = 0.052978`
  - `loss_teacher_event_consistency = 0.025337`
  - `loss_teacher_z_art_consistency = 0.013474`
  - `loss_teacher_fused_hidden_consistency = 0.283336`
- `D34 step20`
  - `loss_teacher_consistency = 0.220877`
  - `loss_teacher_event_consistency = 0.144010`
  - `loss_teacher_z_art_consistency = 0.041403`
  - `loss_teacher_fused_hidden_consistency = 0.709285`

- `D35 step1`
  - `loss_teacher_consistency = 0.048250`
  - `loss_teacher_event_consistency = 0.019930`
  - `loss_teacher_z_art_consistency = 0.008927`
  - `loss_teacher_fused_hidden_consistency = 0.387880`
- `D35 step20`
  - `loss_teacher_consistency = 0.049739`
  - `loss_teacher_event_consistency = 0.032132`
  - `loss_teacher_z_art_consistency = 0.016516`
  - `loss_teacher_fused_hidden_consistency = 0.021812`

解释:
- 这轮不是“新 trio cross-anchor 没接上”。
- 两条线都真实感受到了 teacher pull。

### 2. `D34` 直接退化成更极端的 validation compressor
- `D34 final`
  - `target_validation.loss_total = 2.3506`
  - `target_special_eval.delta_loss_total = 0.201536`
  - `zero_e_evt.delta_target_loss_total = 2.633041`
  - `zero_z_art.delta_target_loss_total = 0.310002`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更好 `-0.093594`
- 但 special 更差 `+0.061535`
- `e_evt` 明显更弱 `-0.665994`
- `z_art` 明显更弱 `-0.128934`

对比旧 `D28 final = 2.349798 / 0.200419 / 2.617499 / 0.307252`:
- 数值形状几乎同型
- 甚至更像“新 special teacher 也会被 core-only student 轨迹压成 validation compressor”

解释:
- 把 `D33` 当 teacher 塞进 `D22` 骨架，
  并没有把 `D33` 的 special/control 带过来。
- 它只是把 validation 压得更低，
  同时把 control 再压坏。

### 3. `D35` 没保住 `D33`，而是近乎回到 `D29` 式中间锚点
- `D35 final`
  - `target_validation.loss_total = 2.395609`
  - `target_special_eval.delta_loss_total = 0.173543`
  - `zero_e_evt.delta_target_loss_total = 2.967455`
  - `zero_z_art.delta_target_loss_total = 0.361794`

对比 `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`:
- validation 仅略好 `-0.001566`
- special 略差 `+0.001774`
- `e_evt` 略弱 `-0.011026`
- `z_art` 略弱 `-0.003133`

解释:
- `D35` 没有把 `D33` 的 stronger special/control 保留下来。
- 更接近事实的描述是:
  - `D33 init + D22 teacher`
  - 又把轨迹拉回了 `D29` 式的中间锚点区域

### 4. checkpoint series 也没有隐藏更好的 joint point
- `D34`
  - `step10 = 2.386077 / 0.223716 / 2.562634 / 0.276536`
  - `step20 = 2.3506 / 0.201536 / 2.633041 / 0.310002`
- `D35`
  - `step10 = 2.433376 / 0.204297 / 2.768766 / 0.337547`
  - `step20 = 2.395609 / 0.173543 / 2.967455 / 0.361794`

解释:
- `D34` 没有“早一点就能保 special/control”的隐藏点，
  它全程都在 compressor 方向上。
- `D35` 也没有“早一点还保着 `D33`”的隐藏点，
  它只是从更差的 special/control 中逐步回到 `D29` 附近。

## 当前结论
1. 新 trio `D22 / D29 / D33` 形成后，naive final-to-final cross-anchor consolidation 仍然不能自然造出 joint winner。
2. `D34` 基本复刻了旧 `D28` 的失败类型:
   - 更强 validation
   - 更差 special/control
3. `D35` 基本复刻了旧 `D29` 的中间锚点形状，
   没能继承 `D33` 的 stronger special/control。
4. 当前 route 结构保持不变:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂不继续优先做同构 `D22 <-> D33 final-to-final` cross-anchor 小变体。
2. 若继续推进这条路线，更值得试:
   - checkpoint-level cross-anchor
   - 尤其是显式利用 `D33 step10` 这类 special-only checkpoint
   - 而不是继续只拿 final anchor 对 final anchor 互蒸
