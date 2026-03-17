# `round1.1 / D10+D11+D12 / explicit-control handoff sweep` 报告

## 目的
- 基于 `D7 / D8 / D9` 已确认:
  - 当前 `z_art_influence` family 在同一 handoff 下已经接近饱和
- 转向新的变量:
  - 在保留 explicit-control 的前提下，重新扫 `clause_ge4` handoff
- 核心问题是:
  - `D5` 那种更强 special 是否能在 explicit-control 条件下保留下来，而不再伴随 `z_art / e_evt` 塌缩

## 实验信息
### D10
- 实验:
  - `EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d10_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_smallscale_100_seeded_shuffle.json`

### D11
- 实验:
  - `EXP-20260315-027-offline-mvp-d11-round1-1-special-proxy-core-clause-ge4-mid-handoff-zart-influence-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d11_round1_1_special_proxy_core_clause_ge4_mid_handoff_zart_influence_smallscale_100_seeded_shuffle.json`

### D12
- 实验:
  - `EXP-20260315-028-offline-mvp-d12-round1-1-special-proxy-core-clause-ge4-handoff68-zart-influence-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d12_round1_1_special_proxy_core_clause_ge4_handoff68_zart_influence_smallscale_100_seeded_shuffle.json`

## 扫描变量
三轮共用:
- `D7` 的 explicit-control 机制
  - `z_art_influence_aux`
- 相同的 `challenge_proxy_core + structural_clause_ge4`
- 相同 loss 权重与 influence floor

唯一变量是 primary-only handoff:
- `D7`: `60`
- `D11`: `65`
- `D12`: `68`
- `D10`: `70`

## 关键结果
### 1. `D10` 证明了“晚 handoff + explicit-control”不再是纯负收益
- `D10 final`
  - `target_validation.loss_total = 2.809966`
  - `target_special_eval.delta_loss_total = -0.0312`
  - `zero_e_evt.delta_target_loss_total = 3.227099`
  - `zero_z_art.delta_target_loss_total = 0.603582`

对比:
- `D5 final = 2.810181 / -0.031687 / 1.462891 / 0.137204`
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`

解释:
- `D10` 几乎拿到了 `D5` 级别的 final special
- 同时把 `z_art / e_evt` 依赖保留在 `D7` 量级
- 这说明 explicit-control 确实改写了原先 `D5` 的负结论

### 2. `D11` 和 `D12` 说明这个 sweet spot 非常窄，而且不在 `65 / 68`
- `D11 final`
  - `2.762797 / 0.14741 / 2.706989 / 0.536627`
- `D12 final`
  - `2.965061 / 0.16957 / 2.31394 / 0.465272`

对比 `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`:
- `D11`
  - validation 更好
  - 但 final special 直接翻坏
  - `e_evt / z_art` 也同步回落
- `D12`
  - validation 更差
  - final special 同样翻坏
  - `e_evt / z_art` 继续回落

这说明:
- 当前 explicit-control 条件下的有效 late-handoff sweet spot 非常窄
- `65` 和 `68` 都没有保住 `D10` 的解

### 3. `D10 / D11 / D12` 的 late-window 进一步证明了 cliff 真实存在
- `D10`
  - `step80 = 3.792123 / -0.542106 / 2.921083 / 1.174149`
  - `step90 = 3.35247 / -0.22034 / 2.692698 / 0.583798`
  - `step100 = 2.809966 / -0.0312 / 3.227099 / 0.603582`
- `D11`
  - `step80 = 3.942573 / -0.788429 / 3.328405 / 1.25246`
  - `step90 = 3.472929 / -0.38098 / 2.779205 / 0.579741`
  - `step100 = 2.762797 / 0.14741 / 2.706989 / 0.536627`
- `D12`
  - `step80 = 3.825348 / -0.567793 / 2.945109 / 1.195045`
  - `step90 = 3.393943 / 0.074951 / 2.322209 / 0.499909`
  - `step100 = 2.965061 / 0.16957 / 2.31394 / 0.465272`

解释:
- `D11` 在 step80 / step90 都有很强 special
- 但 final 翻坏，说明 `65` 没有把这条轨迹平稳带到终点
- `D12` 更糟:
  - 到 step90 就已经把 special 翻成正值
- 因而这条 sweep 不是平滑插值，而是明显存在 cliff

## 当前结论
- `D10` 是这一组 handoff sweep 里唯一有价值的新点。
- 它证明了:
  - explicit-control 机制可以让 `late handoff` 不再重演 `D5` 的 control collapse
- 但 `D10` 也没有打赢 `D7` 或 anchor:
  - 它主要是用约 `+0.08` 的 validation 代价
  - 换来接近 `D5` 的 final special
- `D11 / D12` 证明:
  - 这条线的 sweet spot 很窄
  - 并且不值得再继续细抠 `65 / 68` 这种中间点

## 当前建议
1. `D7` 继续保持 explicit-control 主基线。
2. `D10` 保留为“更强 final special、但 validation 更贵”的次基线。
3. 暂不继续扩展更多 handoff 微调点。
4. 下一步若继续推进，应从 handoff sweep 转向:
   - 新的目标形状
   - 或新的训练 phase 机制
   - 不再优先在当前 `60-70` 区间做更密的插值搜索
