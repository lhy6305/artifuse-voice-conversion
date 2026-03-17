# `round1.1 / D9 / z_art influence dual-pool follow-up` 报告

## 目的
- 基于 `D7 / D8` 已经确认:
  - 继续抬同一条 `challenge_proxy_core` floor 很快进入收益饱和
- 做一轮新的最小 follow-up:
  - 不再改 strength
  - 改 coverage
- 验证把 `z_art_influence_aux.pool_memberships` 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + structural_clause_ge4`，是否能把 `z_art` 保留从 proxy 样本推广到 `clause_ge4` 主线。

## 实验信息
### D9
- 实验:
  - `EXP-20260315-025-offline-mvp-d9-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-dualpool-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json`
- 训练输出:
  - `reports/training/offline_mvp_d9_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool/`
- 评估输出:
  - `reports/eval/offline_mvp_ablations_exp025/`
  - `reports/eval/offline_mvp_special_eval_exp025/`
  - `reports/eval/offline_mvp_checkpoint_series_exp025/`
  - `reports/eval/offline_mvp_special_eval_series_exp025/`

### 联合分析
- checkpoint selection:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3_d4_d5_d6_d7_d8_d9/`
- checkpoint gate replay:
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3_d4_d5_d6_d7_d8_d9/`

## 配置差异
`D9` 相对 `D7` 的唯一主改动是:
- `z_art_influence_aux.pool_memberships`
  - `D7 = ["challenge_proxy_core"]`
  - `D9 = ["challenge_proxy_core", "structural_clause_ge4"]`

其余 sampler、weight、floor、weight schedule 都保持 `D7` 不变。

## 关键结果
### 1. `D9 final` 仍然几乎是 `D7 / D8` 的同形复现
- `D9 final`
  - `target_validation.loss_total = 2.730334`
  - `target_special_eval.delta_loss_total = -0.003173`
  - `zero_e_evt.delta_target_loss_total = 3.486028`
  - `zero_z_art.delta_target_loss_total = 0.605922`

对比:
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D8 final = 2.730527 / -0.003362 / 3.480331 / 0.611369`

判断很清楚:
- `D9` 没有把 `D7 / D8` 推进到新的行为区间
- 它只是继续停留在同一个 final 平衡带

### 2. `D9 late-window` 也没有产生新形状
`D9 late window`:
- `step80 = 3.688349 / -0.306361 / 2.658349 / 1.084989`
- `step90 = 3.427322 / -0.342677 / 2.804947 / 0.511672`
- `step100 = 2.730334 / -0.003173 / 3.486028 / 0.605922`

对比:
- `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- `D8 step90 = 3.427309 / -0.342909 / 2.798612 / 0.520328`

解释:
- 无论看 final 还是 late-window，
- `D9` 都没有把“只在 proxy 上保留 z_art”推进成“在 clause_ge4 主线上也形成不同 regime”
- 它更像是第三次重复确认这条 influence-hinge family 当前会收敛到同一个解

### 3. 联合 replay 继续不变
并入 `D9` 后:
- `best_final_validation_experiment`
  - 仍然是 `EXP-032 final`
- `best_final_special_experiment`
  - 仍然是 `EXP-021 final`
- `best_final_e_evt_experiment`
  - 仍然是 `EXP-023 final`
- `non_anchor_joint_beating_count`
  - 仍然是 `0`

因此:
- `D9` 不是新 baseline
- 也没有改变全局排序

## 当前结论
- “继续抬 floor”这条线在 `D8` 已经接近饱和。
- “扩大 pool coverage 但不改目标形状”这条线在 `D9` 也没有打开新局面。
- 当前更合理的阶段性判断是:
  - `z_art_influence_aux` 这条 hinge-style explicit-control family 已经完成了它该完成的证明
  - 它证明了机制有效
  - 但它没有证明沿同一家族继续做 strength / coverage sweep 能打穿 anchor

## 当前建议
1. explicit-control 线的默认基线继续保持:
   - `D7`
2. `D8 / D9` 作为边界与复现确认保留，不升为默认方案。
3. 后续若继续追 `z_art`，优先级应转向:
   - 新目标形状
   - 或新的 phase / handoff 机制
   - 而不是继续在当前 influence-hinge family 上做纯 coverage / floor sweep
4. 在没有新证据前，`EXP-032 final` 仍保持全局 anchor。
