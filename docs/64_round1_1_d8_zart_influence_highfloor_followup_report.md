# `round1.1 / D8 / z_art influence high-floor follow-up` 报告

## 目的
- 基于 `D7` 已经证明显式 `z_art` 保留机制有效，
- 做一轮最小 follow-up，
- 验证把 `min_influence` 从 `0.12` 提到 `0.18`，是否能继续把 final `z_art` 依赖往上推，而不破坏 `D7` 的平衡。

## 实验信息
### D8
- 实验:
  - `EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json`
- 训练输出:
  - `reports/training/offline_mvp_d8_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_exp024/`
- 评估输出:
  - `reports/eval/offline_mvp_ablations_exp024/`
  - `reports/eval/offline_mvp_special_eval_exp024/`
  - `reports/eval/offline_mvp_checkpoint_series_exp024/`
  - `reports/eval/offline_mvp_special_eval_series_exp024/`

### 联合分析
- checkpoint selection:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3_d4_d5_d6_d7_d8/`
- checkpoint gate replay:
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3_d4_d5_d6_d7_d8/`

## 配置差异
`D8` 相对 `D7` 只改一处:
- `z_art_influence_aux.min_influence`
  - `D7 = 0.12`
  - `D8 = 0.18`

其余 sampler、weight、weight schedule 都保持不变。

dry-run 也印证了这真的是“同机制更高 floor”:
- `D7` dry-run `loss_z_art_influence_aux = 0.091814...`
- `D8` dry-run `loss_z_art_influence_aux = 0.151814...`

## 关键结果
### 1. `D8` 和 `D7` 几乎是同一条轨迹，只把 final `z_art` 略抬了一点
- `D8 final`
  - `target_validation.loss_total = 2.730527`
  - `target_special_eval.delta_loss_total = -0.003362`
  - `zero_e_evt.delta_target_loss_total = 3.480331`
  - `zero_z_art.delta_target_loss_total = 0.611369`

对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
- validation 略差
- special 略差
- `zero_e_evt` 略差
- `zero_z_art` 略好

也就是说:
- `D8` 没有把 `D7` 推进到新的行为区间
- 它更像是 `D7` 的高 floor 近似平手重跑

### 2. `D8 late-window` 也几乎复制了 `D7`
`D8 late window`:
- `step80 = 3.688259 / -0.306474 / 2.651286 / 1.0954`
- `step90 = 3.427309 / -0.342909 / 2.798612 / 0.520328`
- `step100 = 2.730527 / -0.003362 / 3.480331 / 0.611369`

对比 `D7 late window`:
- `step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
- `step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- `step100 = 2.73012 / -0.003131 / 3.489725 / 0.59961`

判断很明确:
- 更高 floor 没有把轨迹从 `D7` 推开
- 只是把 `z_art` 轻微往上推了一点
- 同时把 validation / special / `e_evt` 轻微拉回去一点

### 3. 联合 replay 的结论没有变
并入 `D8` 后:
- `best_final_validation_experiment`
  - 仍然是 `EXP-032 final`
- `best_final_special_experiment`
  - 仍然是 `EXP-021 final`
- `best_final_e_evt_experiment`
  - 仍然是 `EXP-023 final`
- `non_anchor_joint_beating_count`
  - 仍然是 `0`

这说明:
- `D8` 没有成为新的默认基线
- `D7` 仍然是 explicit-control 线里更值得保留的版本

## 当前结论
- 提高 `min_influence` 的方向不是完全无效。
- 它确实还能把 final `z_art` 稍微往上推。
- 但这条一维 sweep 已经很明显进入收益饱和区:
  - 它没有带来新的轨迹形状
  - 也没有改变全局排序

更准确地说:
- `D8` 证明了机制是稳定、可调的
- 但它没有证明“继续抬同一条 floor 就能打穿 anchor”

## 当前建议
1. `D7` 继续作为 explicit-control 线的首选基线。
2. `D8` 不升为默认配置。
3. 后续若继续沿 `z_art_influence` 线，优先级应从“继续抬 floor”转向:
   - 扩大 aux 覆盖范围
   - 或改目标覆盖层级，让 `z_art` 保留不只发生在 `challenge_proxy_core`
4. 在没有新证据前，`EXP-032 final` 仍保持全局 anchor。
