# `round1.1 / C1.7 / transition-aux + soft priority curriculum` 100-step 报告

## 目的
- 在 `EXP-026` 已确认：
  - aggressive targeted sampling 确实是强杠杆
  - 但它把 special slice 和 `step50` 拉坏了
- 当前验证：
  - 把采样改成更软、更早结束的 curriculum，能不能把 tradeoff 拉回中间

## 当前配置
- 实验：
  - `EXP-20260315-027-offline-mvp-c1-7-round1-1-transition-aux-priority-curriculum-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_curriculum_smallscale_100_seeded_shuffle.json`
- 相比 `EXP-026`：
  - priority 池定义不变：
    - `clause_count >= 4`
    - 或 `multi_terminal`
  - 但改为：
    - `priority_ratio = 0.5`
    - only until `step40`

先说人话：
- 这轮不是继续猛灌。
- 而是开局提一把，然后尽早放手，让后半程回到普通采样。

## 关键结果
### 1. `step50` 终于明显回升
- `EXP-025`
  - `step50 zero_z_art.delta_target_loss_total = -0.274127`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854869`
- `EXP-026`
  - `step50 zero_z_art.delta_target_loss_total = -0.300652`
  - `step50 zero_e_evt.delta_target_loss_total = -0.933602`
- `EXP-027`
  - `step50 zero_z_art.delta_target_loss_total = -0.227706`
  - `step50 zero_e_evt.delta_target_loss_total = -0.688658`

解释：
- 这是当前第一轮真正把 `step50` 负依赖幅度明显缩小的 targeted-sampling 方案。

### 2. final special slice 也转成当前最好
- `EXP-023`
  - final `target_special_eval.delta_loss_total = 0.008379`
- `EXP-025`
  - `0.010553`
- `EXP-026`
  - `0.101163`
- `EXP-027`
  - `-0.075832`

解释：
- `EXP-027` 的 special slice 不只是“不变差”。
- 而是成为当前这条线上最顺的一版。

### 3. 但 main validation 退得最明显
- `EXP-021`
  - final `target_validation.loss_total = 2.760389`
- `EXP-025`
  - `2.778521`
- `EXP-026`
  - `2.648178`
- `EXP-027`
  - `2.813174`

解释：
- 这说明 softer curriculum 并不是 free lunch。
- 它把 special 和中段稳定性拉回来了，但把主验证让出去了。

## 当前结论
- `EXP-026` 和 `EXP-027` 合起来给了一个很清楚的结论：
  - targeted sampling / curriculum 这条方向是对的
  - 它确实能改 route-C 的行为
  - 但当前存在明确三角 tradeoff：
    - main validation
    - special slice
    - `step50` stability
- `EXP-026` 把主验证拉到最好，但 special 和 `step50` 最差。
- `EXP-027` 把 special 和 `step50` 拉到最好，但 main validation 最差。

先说人话：
- 不是这个方向没用。
- 而是现在已经能看见调音台了，只是三个旋钮还没找到平衡点。

## 建议
- 不把 `EXP-027` 升为默认训练配置。
- 下一步更合理的是继续留在采样层做中间档位，而不是再回去改 loss：
  - 例如在 `EXP-026` 和 `EXP-027` 中间做折中 schedule
  - 目标是找：
    - 不明显拉坏 main validation
    - 同时保住 `step50` 和 special slice 改善
