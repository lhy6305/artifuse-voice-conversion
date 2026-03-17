# `round1.1 / D7 / z_art influence run` 报告

## 目的
- 在 `D4` 已经把 `challenge_proxy_core + structural_clause_ge4` 推到较均衡区间之后，
- 不再继续微调 sampler 或 `z_smooth`，
- 而是直接验证一个更显式的 `z_art` 保留机制，看看它能不能在不打坏 final validation / final special 的前提下，把控制依赖真正拉起来。

## 实验信息
### D7
- 实验:
  - `EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json`
- 训练输出:
  - `reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/`
- 评估输出:
  - `reports/eval/offline_mvp_ablations_exp023/`
  - `reports/eval/offline_mvp_special_eval_exp023/`
  - `reports/eval/offline_mvp_checkpoint_series_exp023/`
  - `reports/eval/offline_mvp_special_eval_series_exp023/`

### 联合分析
- checkpoint selection:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_plus_d1_d2_d3_d4_d5_d6_d7/`
- checkpoint gate replay:
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_plus_d1_d2_d3_d4_d5_d6_d7/`

## 机制变更
这轮不是纯配置花活，而是引入了一条新的显式控制保留路径:
- `TargetExample` / target batch 正式挂载 `target_special_supervision`
- 模型显式暴露:
  - `fused_hidden_with_z_art`
  - `fused_hidden_zero_z_art`
  - `fused_hidden_zero_e_evt`
- 新增 `z_art_influence_aux`
  - 只在配置指定的 target pools 上启用
  - 当前 `D7` 只盯 `challenge_proxy_core`
  - 约束目标是 `with_z_art` 和 `zero_z_art` 的 fused hidden 至少保持一定影响差

配置上，`D7` 相对 `D4` 的唯一主改动是:
- sampler 保持 `D4` 不变
- 新增:
  - `z_art_influence_aux.weight = 0.12`
  - `z_art_influence_aux.pool_memberships = ["challenge_proxy_core"]`
  - `z_art_influence_aux.min_influence = 0.12`
  - `weight_schedule = step41-70 linear ramp to 0.12`

## 关键结果
### 1. `D7` 是第一条真正改出“控制行为”而不只是改出“loss 曲线”的显式保留线
- `D7 final`
  - `target_validation.loss_total = 2.73012`
  - `target_special_eval.delta_loss_total = -0.003131`
  - `zero_e_evt.delta_target_loss_total = 3.489725`
  - `zero_z_art.delta_target_loss_total = 0.59961`

对比 `D4 final = 2.729466 / -0.00228 / 1.527013 / 0.199795`:
- validation 基本持平
- special 基本持平
- `zero_e_evt` 大幅抬升
- `zero_z_art` 也显著抬升

这说明:
- `D7` 没有靠“牺牲 final 平衡”换控制量
- 它是真的把 final control dependence 拉高了

### 2. `D7` 的收益不是评估口径假象
在 final validation / final special_eval 上:
- `loss_z_art_influence_aux = 0.0`

原因不是机制失效，而是:
- 当前 aux 只挂在 `challenge_proxy_core`
- formal validation 和 `target_special_eval` 切片里不包含这批样本

但即便如此:
- `zero_e_evt.delta_target_loss_total`
- `zero_z_art.delta_target_loss_total`
仍然同步上升。

这意味着:
- `D7` 提升的是模型的实际控制依赖
- 不是把额外 aux loss 直接算进 eval 后得到的表面改进

### 3. `D7` 的 late-window 也和 `D4 / D6` 不同
`D7 late window`:
- `step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
- `step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- `step100 = 2.73012 / -0.003131 / 3.489725 / 0.59961`

解释:
- `step80`
  - 仍是较强 special
  - 同时第一次把 `zero_z_art` 也抬到明显正控制区
- `step90`
  - 是 late-window 里最像“special + dual-control 都站住”的点
- `step100`
  - special 回到接近中性
  - 但 final `e_evt` / `z_art` 依赖继续上冲

这和 `D6` 那种“schedule 在跑但轨迹近乎重合”的结果不同。
`D7` 是真改了轨迹形状。

### 4. `D7` 改强了控制，但还没有打赢 anchor
联合 replay 更新后:
- `best_final_validation_experiment`
  - 仍然是 `EXP-032 final`
- `best_final_special_experiment`
  - 仍然是 `EXP-021 final`
- `best_final_e_evt_experiment`
  - 变成了 `EXP-023 final`
- `non_anchor_joint_beating_count`
  - 仍然是 `0`

所以正式判断应该是:
- `D7` 不是新 anchor
- 但它已经是当前最强的 explicit control-preservation baseline

## 当前结论
- `D7` 是 `round1.1` 里第一条明确证明“显式控制保留机制可以改变行为”的线。
- 它守住了 `D4` 级别的 final validation / final special。
- 同时把 final `e_evt` 依赖和 final `z_art` 依赖都显著抬起来了。
- 它没有整体打赢 `EXP-032 final`，主要差距仍在:
  - validation 还略弱
  - `zero_z_art` 还明显低于 anchor 的 `1.275259`

## 当前建议
1. `D7` 应替代 `D4`，成为 `clause_ge4 + explicit-control` 方向的默认新基线。
2. 下一步可以继续沿 `z_art_influence` 线跟进，但不应只做机械式强度 sweep。
3. 如果继续跟进，更有价值的是测试:
   - 更高 floor 是否真能继续抬 `z_art`
   - 或扩大 aux 覆盖范围，看看它能否把 `z_art` 保留从 proxy 样本推广到 `clause_ge4` 主线
4. 在没有新证据前，`EXP-032 final` 仍保持全局 anchor。
