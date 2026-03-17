# `round1.1 / D31 / teacher-consistency acoustic target-shape probe` 报告

## 目的
- 在 `D22 / D26 / D29` 三锚已经稳定之后，
- 当前真正值得验证的不是继续做近邻采样小修，
- 而是测试一个更不同的 distillation target shape:
  - 在 teacher-consistency 里不再只蒸馏 `event + z_art`
  - 而是追加 `acoustic`
- 本轮目标很明确:
  - 看看这条更不同的 target shape，能不能把 `default_minimax / D22` 推到新的 Pareto 点

## 代码与配置
### 新增训练能力
- `src/v5vc/train_entry.py`
  - `teacher_consistency` 新增:
    - `acoustic_weight`
    - `loss_teacher_acoustic_consistency`

### D31
- 配置:
  - `configs/offline_mvp_train_d31_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_acoustic_smallscale_30_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration`
- route:
  - `default_minimax`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - `teacher_consistency.pool_memberships = ["challenge_proxy_core"]`
  - 新增:
    - `teacher_consistency.acoustic_weight = 0.25`

## 关键事实
### 1. acoustic consistency 不是挂空配置
- `step1`
  - `loss_teacher_consistency = 0.033924`
  - `loss_teacher_event_consistency = 0.009645`
  - `loss_teacher_z_art_consistency = 0.019376`
  - `loss_teacher_acoustic_consistency = 0.019613`
- `step30`
  - `loss_teacher_consistency = 0.413141`
  - `loss_teacher_event_consistency = 0.214067`
  - `loss_teacher_z_art_consistency = 0.171916`
  - `loss_teacher_acoustic_consistency = 0.108633`

解释:
- 这轮不是“新 target shape 没接上”。
- acoustic consistency 在训练全过程中持续 active。

### 2. `D31 final` 只形成了 `D22` 附近的数值级轻微扰动
- `D31 final`
  - `target_validation.loss_total = 2.442793`
  - `target_special_eval.delta_loss_total = 0.142472`
  - `zero_e_evt.delta_target_loss_total = 3.298481`
  - `zero_z_art.delta_target_loss_total = 0.436225`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 仅略好 `-0.001401`
- final special 略差 `+0.002471`
- `e_evt` 略弱 `-0.000554`
- `z_art` 略弱 `-0.002711`

解释:
- `D31` 不是负例。
- 但它也没有把 `default_minimax` 推到新的 Pareto 点。
- 更准确的描述是:
  - 在同一条 `challenge_proxy_core` gate 上追加温和 acoustic consistency，
  - 只把 `D22` 复刻成了一个近似数值副本。

### 3. checkpoint / special series 也没有给出“只是 final 选坏了”的借口
- special eval series:
  - `step10 = 2.593177 / 0.136837`
  - `step20 = 2.472389 / 0.172539`
  - `step30 = 2.442793 / 0.142472`
- checkpoint ablation series:
  - `step10 zero_e_evt / zero_z_art = 3.043228 / 0.41683`
  - `step20 zero_e_evt / zero_z_art = 3.051932 / 0.404295`
  - `step30 zero_e_evt / zero_z_art = 3.298481 / 0.436225`

解释:
- `step20` 没有给出更好的 joint point:
  - validation 仍更差
  - final special 反而更坏
- `step30` 已经是这轮最接近 `D22` 的点
- 所以 `D31` 的结论不是“终点选坏了”，
  而是这条 target shape 本身信息增益有限

### 4. route-context comparison 已确认 `D31` 没改写当前 minimax 结论
- 在 `D22 / D26 / D29 / D31` 的 `default_minimax` comparison 中:
  - `D31` 相对 route anchor `D22`
    - validation `-0.001401`
    - special `+0.002471`
    - `e_evt -0.000554`
    - `z_art -0.002711`

这说明:
- `D31` 仍不足以取代 `D22` 作为当前 minimax anchor
- 当前 route 结论保持不变:
  - `D22 = default_minimax`
  - `D29 = validation`
  - `D26 = special / z_art`

## 当前结论
1. `D31` 证明了“更不同的 distillation target shape”这条方向可以真实接入代码和训练闭环。
2. 但在当前同一条 `challenge_proxy_core` gate 上，`event + z_art + acoustic` 这版 target shape 只带来了很小的数值波动。
3. `D31` 不升为新 anchor，也不改写当前 minimax route。

## 当前建议
1. `D22` 继续保持当前 `default_minimax` anchor。
2. `D31` 不再继续优先做同构 `acoustic_weight` 小 sweep。
3. 若继续推进 target-shape 路线，更值得试:
   - 更有结构差异的 distillation target shape
   - 而不是继续在同一条 core gate 上追加轻量 acoustic 项
