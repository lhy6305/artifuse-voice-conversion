# `round1.1 / C1.7 / transition-aux + two-phase priority handoff` 100-step 报告

## 目的
- `EXP-026` 说明 aggressive single-stage 采样能把 main validation 拉高，但会把 special slice 和 `step50` 拉坏。
- `EXP-027` 说明 softer early curriculum 能把 special slice 和 `step50` 拉回来，但 main validation 会掉下去。
- `EXP-028` 说明单段式中间插值并不会自动给出平衡点。
- 当前验证：
  - 把 schedule 改成明确的两段式 handoff，能不能同时保住 main validation 和 `step50`。

## 当前配置
- 实验：
  - `EXP-20260315-029-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_smallscale_100_seeded_shuffle.json`
- priority 池定义不变：
  - `clause_count >= 4`
  - 或 `multi_terminal`
- schedule 改成两段：
  - `step1-25`: `priority_ratio = 0.75`
  - `step26-45`: `priority_ratio = 0.25`
  - `step46+`: 回普通 seeded shuffle

先说人话：
- 这轮不是“轻一点”或“重一点”。
- 而是先猛推一段，把该学的先塞进去，再在 `step50` 之前明显放手。

## 关键结果
### 1. `step50` 这次真的拉起来了，而且是当前最好
- `EXP-026`
  - `step50 zero_z_art.delta_target_loss_total = -0.300652`
  - `step50 zero_e_evt.delta_target_loss_total = -0.933602`
- `EXP-027`
  - `step50 zero_z_art.delta_target_loss_total = -0.227706`
  - `step50 zero_e_evt.delta_target_loss_total = -0.688658`
- `EXP-028`
  - `step50 zero_z_art.delta_target_loss_total = -0.254093`
  - `step50 zero_e_evt.delta_target_loss_total = -0.778543`
- `EXP-029`
  - `step50 zero_z_art.delta_target_loss_total = -0.163512`
  - `step50 zero_e_evt.delta_target_loss_total = -0.463404`

解释：
- 这不是小修补。
- 是当前第一版真正把 `step50` 负依赖幅度大幅收窄的采样 handoff。

### 2. main validation 也一起回升了
- `EXP-026`
  - final `target_validation.loss_total = 2.648178`
- `EXP-027`
  - `2.813174`
- `EXP-028`
  - `2.861962`
- `EXP-029`
  - `2.702175`

解释：
- 它没有超过 `EXP-026` 的最强 main validation。
- 但已经明显好于 `EXP-027 / EXP-028`，也好于 `EXP-021 / EXP-025`。

### 3. 但 final special slice 又退回 aggressive 一侧
- `EXP-026`
  - final `target_special_eval.delta_loss_total = 0.101163`
- `EXP-027`
  - `-0.075832`
- `EXP-028`
  - `-0.093905`
- `EXP-029`
  - `0.102328`

解释：
- 这轮把 `step50` 和 main validation 一起救回来了。
- 但代价是 final punctuation-only challenge slice 又明显变差，几乎贴着 `EXP-026`。

## 当前结论
- `EXP-029` 给了一个很重要的新结论：
  - 两段式 handoff 比单段式 ratio / duration 更有力
  - 它已经能同时改善 main validation 和 `step50`
  - 当前没被解决的核心，收缩到了 final special slice
- 所以现在的主矛盾不再只是“schedule 怎么调”，而更像是：
  - priority 池里到底塞了什么样的 transition-rich 记录
  - 以及 early aggressive burst 会不会把模型往 lexical multi-clause 一侧拉得太狠

先说人话：
- 之前像是三个旋钮互相打架。
- 这轮把其中两个旋钮先拧顺了，但第三个 special slice 还在单独闹脾气。

## 建议
- 不把 `EXP-029` 直接升为默认训练配置。
- 但当前最值得保留的骨架，已经从单段式 schedule 变成了：
  - `C1.7 + two-phase targeted sampling handoff`
- 下一步如果继续推进，更合理的是：
  - 保留这套两段式 schedule
  - 不优先再扫 ratio / duration
  - 改去收窄或重定义 priority pool，重点观察能否减轻 special-slice 回归
