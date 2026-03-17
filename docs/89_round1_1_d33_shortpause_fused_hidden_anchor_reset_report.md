# `round1.1 / D33 / short-pause fused-hidden follow-up and anchor reset` 报告

## 目的
- `D32` 已经证明:
  - fused-hidden target shape 比 `acoustic` 加项更有信息增益
  - 但在 `challenge_proxy_core` 单 gate 下，还不够把 special gap 补回来
- `D26` 则已经证明:
  - `short_pause_no_terminal` gate / sampler 组合确实能把轨迹推向更好的 special / `z_art`

所以本轮只做一个最合理的结构化 follow-up:
- 不再继续扫同一条 core gate
- 而是把:
  - `D32` 的 fused-hidden target shape
  - 和 `D26` 的 short-pause gate / sampler
  直接组合起来

本轮真正要回答的问题是:
- `D32` 的 control gain
- 能不能在 `D26` 这条 family 上转化成真正更强的 special / control anchor

## 配置与实验
### D33
- 配置:
  - `configs/offline_mvp_train_d33_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration`
- route:
  - `default_minimax`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - `teacher_consistency.pool_memberships = ["challenge_proxy_core", "short_pause_no_terminal"]`
  - `targeted_sampling.priority_pool_memberships = ["challenge_proxy_core", "short_pause_no_terminal"]`
  - `teacher_consistency.fused_hidden_weight = 0.05`
  - `teacher_consistency.acoustic_weight = 0.0`
  - `num_steps = 20`

## 关键事实
### 1. fused-hidden consistency 在 short-pause gate 下同样真实生效
- `step1`
  - `loss_teacher_consistency = 0.028494`
  - `loss_teacher_event_consistency = 0.007515`
  - `loss_teacher_z_art_consistency = 0.014875`
  - `loss_teacher_fused_hidden_consistency = 0.122075`
- `step20`
  - `loss_teacher_consistency = 0.237666`
  - `loss_teacher_event_consistency = 0.110167`
  - `loss_teacher_z_art_consistency = 0.097574`
  - `loss_teacher_fused_hidden_consistency = 0.598500`

解释:
- 这轮不是“换了 short-pause gate 以后 fused-hidden 又挂空”。
- `D33` 的 target shape 在训练闭环里持续 active。

### 2. `D33 final` 基本把 `D26` 升级成了新的 special / control 强锚
- `D33 final`
  - `target_validation.loss_total = 2.52818`
  - `target_special_eval.delta_loss_total = 0.111677`
  - `zero_e_evt.delta_target_loss_total = 3.312339`
  - `zero_z_art.delta_target_loss_total = 0.465828`

对比 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`:
- validation 只略差 `+0.004282`
- final special 更好 `-0.006217`
- `e_evt` 更强 `+0.039689`
- `z_art` 更强 `+0.005569`

解释:
- `D33` 没有改写 minimax，
  但它已经基本把 `D26` 这条旧的 special / `z_art` anchor 升级掉了。
- 更准确的说法是:
  - `D26` 证明了 short-pause route 值得保留
  - `D33` 则把 fused-hidden gain 成功转译成了这一侧真正更强的 final anchor

### 3. `D33` 相对当前 route anchor `D22` 不是 minimax 胜者，但已形成新的 special-first route 终点
- 对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation `+0.083986`
  - special `-0.028324`
  - `e_evt +0.013304`
  - `z_art +0.026892`

解释:
- `D33` 的问题已经不再是 control 不够，
  而是 validation 代价仍明显高于 `D22`。
- 所以它不替代 `D22` 作为 `default_minimax`，
  但它已经成为比 `D26` 更干净、更强的 special-first anchor。

### 4. checkpoint series 说明 `D33 step10` 是更极端的 special 点，但 `step20` 才是更稳定的 special/control final
- special eval series:
  - `step10 = 2.621019 / 0.081505`
  - `step20 = 2.52818 / 0.111677`
- checkpoint ablation series:
  - `step10 zero_e_evt / zero_z_art = 3.224344 / 0.46347`
  - `step20 zero_e_evt / zero_z_art = 3.312339 / 0.465828`

解释:
- `step10` 的确给了一个更极端的 special-only 点
- 但它没有把 `e_evt` 一起保到 `step20` 的水平
- `step20` 才是这轮“special 更强，同时 control 也更强”的 joint point
- 所以 `D33` 的结论不是“终点选坏了”，
  而是:
  - `step10` 属于更偏 special-only 的 checkpoint
  - `step20` 则是当前更适合作为 formal special/control anchor 的 final

### 5. 三锚结构与 handoff 资产已经正式改写
- 新三锚 selection:
  - `D29 = validation anchor`
  - `D22 = default_minimax anchor`
  - `D33 = special / e_evt / z_art anchor`
- 新 route thresholds:
  - `budget_to_minimax_anchor = 0.047019`
  - `budget_to_special_anchor = 0.131005`
- 新默认 handoff 链已重新物化:
  - `route_handoff -> handoff_document -> stage_report`
  - 全部从 `D22 / D29 / D33` 新 trio 生成

这说明:
- `D26` 不再是当前正式 special anchor
- 后续交接、阶段总结、route selection 都必须切到 `D33`

## 当前结论
1. `D33` 是一次有效的结构组合成功例:
   - `D32` 的 fused-hidden target shape
   - 成功通过 `D26` 的 short-pause gate / sampler 结构转化成了新的 final anchor
2. `D33` 正式替换 `D26` 成为当前:
   - best special
   - best `e_evt`
   - best `z_art`
   anchor。
3. `D22` 仍保持 `default_minimax` anchor。
4. 当前正式 route 结构更新为:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 后续默认交接与阶段汇总，统一改用 `D22 / D29 / D33` 新 trio 资产。
2. `D26` 保留为已被超越的历史 reference，不再作为当前 special anchor 引用。
3. 若继续推进训练主线，更值得试:
   - 以 `D22` 和 `D33` 为两端的新 minimax / cross-anchor 组合
   - 而不是继续围绕 `D26` 做旧 family follow-up
