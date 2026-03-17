# `round1.1 / D28+D29+D30 / cross-anchor consolidation` 报告

## 目的
- 在 teacher-consistency family 已经形成两个参考点之后:
  - `D22`: validation-oriented
  - `D26`: special / `z_art`-leaning
- 正式验证 family 参考点之间是否可以互相蒸馏出新的折中点。

本轮做三条最小 cross-anchor 线:
- `D28 = D22 init + D26 teacher`
- `D29 = D26 init + D22 teacher`
- `D30 = D29 event-only`

## 配置与实验
### D28
- 配置:
  - `configs/offline_mvp_train_d28_round1_1_d22_init_d26_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-046-offline-mvp-d28-round1-1-d22-init-d26-teacher-cross-anchor-consolidation-20step-calibration`
- 设计:
  - `student init = D22 final`
  - `teacher = D26 final`
  - 采用 `D22` 的 core-only gate / sampler

### D29
- 配置:
  - `configs/offline_mvp_train_d29_round1_1_d26_init_d22_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration`
- 设计:
  - `student init = D26 final`
  - `teacher = D22 final`
  - 采用 `D26` 的 short-pause family gate / sampler

### D30
- 配置:
  - `configs/offline_mvp_train_d30_round1_1_d26_init_d22_teacher_cross_anchor_event_only_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-047-offline-mvp-d30-round1-1-d26-init-d22-teacher-cross-anchor-event-only-20step-calibration`
- 设计:
  - 基于 `D29`
  - 唯一变动:
    - `teacher_consistency.z_art_weight = 0.0`
  - 用来验证 `D29` 的 tradeoff 是否主要由 teacher `z_art` 蒸馏导致

## 关键结果
### 1. `D28` 是最强 validation 压缩，但代价过大
- `D28 final`
  - `target_validation.loss_total = 2.349798`
  - `target_special_eval.delta_loss_total = 0.200419`
  - `zero_e_evt.delta_target_loss_total = 2.617499`
  - `zero_z_art.delta_target_loss_total = 0.307252`

解释:
- `D28` 拿到了当前 teacher-consistency family 里最强 validation
- 但它也把 special / `e_evt` / `z_art` 一起压掉了
- 因此它更像一个“validation compressor”
  而不是一个可接受的新主参考点

### 2. `D29` 是 cross-anchor 方向里更平衡的点
- `D29 final`
  - `target_validation.loss_total = 2.397175`
  - `target_special_eval.delta_loss_total = 0.171769`
  - `zero_e_evt.delta_target_loss_total = 2.978481`
  - `zero_z_art.delta_target_loss_total = 0.364927`

对比 `D28 final = 2.349798 / 0.200419 / 2.617499 / 0.307252`:
- validation 略差
- 但 special 更好
- `e_evt / z_art` 都明显更强

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更好
- 但 special / `e_evt` / `z_art` 仍更弱

对比 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`:
- validation 明显更好
- 但 special / `e_evt` / `z_art` 也仍更弱

解释:
- `D29` 没有打赢 `D22` 或 `D26`
- 但它形成了一个清晰的中间锚点:
  - validation 比 `D26` 强得多
  - 同时没有像 `D28` 那样把控制压得太狠

### 3. `D30` 基本数值级复刻 `D29`
- `D30 final`
  - `target_validation.loss_total = 2.399277`
  - `target_special_eval.delta_loss_total = 0.169748`
  - `zero_e_evt.delta_target_loss_total = 2.982002`
  - `zero_z_art.delta_target_loss_total = 0.377184`

对比 `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`:
- validation 只差 `+0.002102`
- special 只差 `-0.002021`
- `e_evt` 近乎持平
- `z_art` 也只是轻微波动

解释:
- 去掉 teacher `z_art` 蒸馏后，轨迹基本没有变
- 这说明 `D29` 的 tradeoff 主要不是由 teacher `z_art` term 单独造成的
- 更接近事实的诊断是:
  - cross-anchor 的主要驱动力来自 event-side alignment 与整体轨迹耦合

### 4. `D28 / D29 / D30` 都没有隐藏更好的 checkpoint
- `D28 step10 = 2.384933 / 0.222227 / 2.566482 / 0.278603`
- `D28 step20 = 2.349798 / 0.200419 / 2.617499 / 0.307252`
- `D29 step10 = 2.432519 / 0.207457 / 2.74441 / 0.333095`
- `D29 step20 = 2.397175 / 0.171769 / 2.978481 / 0.364927`
- `D30 step10 = 2.433206 / 0.208167 / 2.89979 / 0.379443`
- `D30 step20 = 2.399277 / 0.169748 / 2.982002 / 0.377184`

解释:
- 这不是“终点选坏了”的问题
- 三条 cross-anchor 都在各自 final 上达到本轮最优 tradeoff

## 当前结论
- cross-anchor consolidation 方向是有效的:
  - 它能稳定地产生新的中间锚点
- 但它目前仍然只是“压 validation 换 special/control”
  的一种更可控方式
- 当前 family 内部的有效结构可以更新为:
  - `D22`: validation-oriented anchor
  - `D26`: special / `z_art`-leaning anchor
  - `D29`: cross-anchor middle anchor
- `D28` 不升为默认方案
- `D30` 说明 event-only 并没有实质改变 `D29` 的形状，因此这条分解优先级不高

## 当前建议
1. 保留 cross-anchor consolidation 路线，但不把 `D28 / D29 / D30` 升为主线默认。
2. `D29` 升为 cross-anchor family 的主参考点。
3. `D28` 保留为“极强 validation compression”参考点，但不继续优先扩。
4. `D30` 不再继续扩 family。
5. 当前不建议继续优先做:
   - `D28` 类似的更强 validation 压缩
   - `D29` 的纯 step / lr 微调
   - `D30` 类似的 event-only / z_art-only 小拆分
6. 若下一步继续推进，更值得转向:
   - 更不同的 distillation target shape
   - 或三锚框架下的明确 gate/selection，而不是继续抠单条 cross-anchor 小变体

