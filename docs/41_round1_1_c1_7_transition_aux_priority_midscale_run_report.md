# `round1.1 / C1.7 / transition-aux + midpoint priority schedule` 100-step 报告

## 目的
- `EXP-026` 已经证明 aggressive targeted sampling 会把 main validation 拉高，但 special slice 和 `step50` 会明显变差。
- `EXP-027` 反过来证明 softer early curriculum 能把 special slice 和 `step50` 拉回来，但会让出 main validation。
- 当前验证：
  - 如果直接在两者中间取一个显式 midpoint schedule，能不能形成更均衡的折中点。

## 当前配置
- 实验：
  - `EXP-20260315-028-offline-mvp-c1-7-round1-1-transition-aux-priority-midscale-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_midscale_100_seeded_shuffle.json`
- 相比 `EXP-026 / EXP-027`：
  - priority 池定义不变：
    - `clause_count >= 4`
    - 或 `multi_terminal`
  - 但 schedule 取中间档：
    - `priority_ratio = 0.625`
    - until `step55`

先说人话：
- 这轮就是把旋钮拧到中间，看看能不能自动得到一个平衡点。

## 关键结果
### 1. final special slice 继续变好，而且是当前最好
- `EXP-026`
  - final `target_special_eval.delta_loss_total = 0.101163`
- `EXP-027`
  - `-0.075832`
- `EXP-028`
  - `-0.093905`

解释：
- 这说明 midpoint schedule 没有丢掉 `EXP-027` 的 special-slice 优势，反而还往前推了一点。

### 2. `step50` 比 aggressive 版好，但还是不如 softer curriculum
- `EXP-026`
  - `step50 zero_z_art.delta_target_loss_total = -0.300652`
  - `step50 zero_e_evt.delta_target_loss_total = -0.933602`
- `EXP-027`
  - `step50 zero_z_art.delta_target_loss_total = -0.227706`
  - `step50 zero_e_evt.delta_target_loss_total = -0.688658`
- `EXP-028`
  - `step50 zero_z_art.delta_target_loss_total = -0.254093`
  - `step50 zero_e_evt.delta_target_loss_total = -0.778543`

解释：
- 它确实比 aggressive 版回升了一截。
- 但回升幅度还不够，仍然没有追上 `EXP-027`。

### 3. main validation 没有回到中间，反而更差
- `EXP-026`
  - final `target_validation.loss_total = 2.648178`
- `EXP-027`
  - `2.813174`
- `EXP-028`
  - `2.861962`

解释：
- 这轮最关键的坏消息在这里。
- 本来希望中间档位能拿回一部分 `EXP-026` 的 main-validation 优势，但实际上连 `EXP-027` 都没保住。

## 当前结论
- `EXP-028` 说明一个事：
  - schedule 参数做简单中间插值，不会自动得到“折中最好”的点。
- 它在当前三角 tradeoff 里形成了这种位置：
  - final special slice 最好
  - `step50` 介于 `EXP-026` 和 `EXP-027` 之间
  - main validation 最差
- 所以从“找平衡点”的角度看，`EXP-028` 不是当前最优折中。

先说人话：
- 不是所有旋钮都能靠取平均解决。
- 这轮更像证明了“线性折中”本身不够聪明。

## 建议
- 不把 `EXP-028` 升为默认训练配置。
- 当前采样层的结论可以先钉死为：
  - 如果更看重 main validation，`EXP-026` 更接近那个方向。
  - 如果更看重 special slice 和 `step50`，`EXP-027` 仍是当前更合理的选择。
- 下一步如果还继续做 sampling / curriculum，更合理的是：
  - 不再只做单段式 ratio / duration 的线性插值
  - 考虑两段式 handoff 或更明确的 phase schedule
