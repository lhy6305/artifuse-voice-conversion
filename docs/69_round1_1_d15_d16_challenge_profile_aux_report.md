# `round1.1 / D15+D16 / challenge-profile aux` 报告

## 目的
- 在 `late mechanics` 已基本收口后，转向新的目标形状。
- 本轮不再改 optimizer，也不再改 late checkpoint 选择。
- 直接利用 `target_special_supervision` sidecar 中的:
  - `special_proximity_score`
  - `final_terminal_type`
  - `pool_memberships`
- 为 `challenge_proxy_core` 新增一个更直接的 sample-level event profile 约束。

## 代码与配置
### 新增代码
- `src/v5vc/offline_mvp/losses.py`
  - 新增 `challenge_proxy_profile_aux`
- 同步更新:
  - `src/v5vc/train_entry.py`
  - `src/v5vc/special_eval.py`
  - `src/v5vc/ablation_eval.py`
  - `src/v5vc/special_eval_series.py`

### D15
- 实验:
  - `EXP-20260315-031-offline-mvp-d15-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d15_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_smallscale_100_seeded_shuffle.json`
- 基线:
  - `D7`

### D16
- 实验:
  - `EXP-20260315-032-offline-mvp-d16-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-challenge-profile-late-proxy-tail-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d16_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_challenge_profile_late_proxy_tail_smallscale_100_seeded_shuffle.json`
- 与 `D15` 唯一差别:
  - 让 `challenge_proxy_core` 在 `step60-100` 继续以 `priority_ratio = 0.125` 低比例出现

## 关键结果
### 1. `D15` 证明新 aux 工程上生效，但 final 近乎复刻 `D7`
- dry-run 已确认:
  - `loss_challenge_proxy_profile_aux = 0.010237276554107666`
- `D15 final`
  - `target_validation.loss_total = 2.730729`
  - `target_special_eval.delta_loss_total = -0.003582`
  - `zero_e_evt.delta_target_loss_total = 3.489731`
  - `zero_z_art.delta_target_loss_total = 0.599471`

对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
- validation 近乎相同
- special 近乎相同
- `e_evt / z_art` 也近乎相同

解释:
- 这说明新目标形状在当前 `D7` 采样日程下没有形成新 regime。
- 问题不是代码没生效，而是:
  - 它没有改出可见行为差异

### 2. `D15` 的关键负证据是：新 aux 在 late window 基本失活
- `D15` step70 / 80 / 90 / 100 的 step log 里:
  - `loss_challenge_proxy_profile_aux = 0.0`
- 原因不是实现错误，而是:
  - `challenge_proxy_core` 在 `step60` 后不再被 sampler 持续送入训练 batch

解释:
- 所以 `D15` 还不能直接得出“这条 target-shape 无效”的结论。
- 更准确的说法是:
  - 在当前 handoff 下，它没有进入 late phase 主导行为

### 3. `D16` 专门验证了“late proxy tail”之后，结论反而更差
- `D16 final`
  - `target_validation.loss_total = 2.727232`
  - `target_special_eval.delta_loss_total = 0.157422`
  - `zero_e_evt.delta_target_loss_total = 2.781072`
  - `zero_z_art.delta_target_loss_total = 0.533725`

对比:
- `D15 final = 2.730729 / -0.003582 / 3.489731 / 0.599471`
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`

解释:
- `D16` 确实改变了 late-window 轨迹，说明 late proxy tail 不是空操作
- 但它改出来的不是更优解，而是:
  - validation 只略好
  - final special 直接翻正
  - `e_evt / z_art` 一起回落

### 4. `D16` 说明问题不在“新 aux 没有 late exposure”，而在“这种目标形状本身会把轨迹推偏”
- `D16 late window`
  - `step80 = 3.701336 / -0.236038 / 2.49006 / 1.065938`
  - `step90 = 3.387037 / -0.291327 / 2.793031 / 0.589962`
  - `step100 = 2.727232 / 0.157422 / 2.781072 / 0.533725`

解释:
- 这条轨迹在 `step80 / 90` 仍有负 special
- 但 final 明显翻坏
- 同时 `e_evt / z_art` consolidation 也没守住
- 说明“把 challenge-proxy profile 继续拖进后段”不是当前正确方向

## 当前结论
- `challenge_proxy_profile_aux` 作为新目标形状，工程上是成立的。
- 但在当前 explicit-control 主线上:
  - `D15` 只给出近似重跑
  - `D16` 则给出明确负证据
- 所以这条 family 当前可以正式收口:
  - 不是因为没实现
  - 也不是因为 late phase 没吃到样本
  - 而是因为它一旦持续主导 late phase，就会把 final 推向更差平衡

## 当前建议
1. 保留 `challenge_proxy_profile_aux` 代码，但不继续优先扩展这一 family。
2. 不把 `D15 / D16` 升为默认方案。
3. 当前更值得的下一步，应从“challenge 邻域 profile”转向:
   - 更强的结构监督定义变化
   - 或 challenge proxy 与结构轴之间更明确的 phase 分离

