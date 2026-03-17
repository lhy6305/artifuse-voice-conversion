# `round1.1 / D42-D43 / phase-specific teacher source + high-proximity relaxed gate` 报告

## 目的
- `D41` 已经证明:
  - 同一条 `D10 teacher` family 里
  - 即使显式切 `teacher gate` 和 target shape
  - 也还不足以把 `D33 step10` 固化成新的 final winner
- 所以下一轮只验证两个改动最小、但方向不同的 follow-up:
  - `D42 = phase-specific teacher checkpoint / teacher source handoff`
  - `D43 = target-side high-proximity relaxed gate`

这轮的目标不是再做大重构，
而是先确认:
- 更换 teacher source 本身是否足以改变后半段收敛形态
- 以及只做更强一点的 target-side gate，是否能低成本改写当前 route

## 代码与配置
### 新增训练能力
- `src/v5vc/train_entry.py`
  - `teacher_consistency` 进一步支持按 phase 切换:
    - `teacher_checkpoint_path`
    - `min_special_proximity_score`
    - `max_special_proximity_score`
    - `required_final_terminal_types`
    - `required_utterance_structure_types`
  - 训练计划和 step 指标中也会落出:
    - `teacher_checkpoint_paths`
    - 当前 phase 生效的 teacher source 与 gate 过滤器
- `src/v5vc/offline_mvp/data.py`
  - `targeted_sampling` 新增 target-side gate:
    - `min_special_proximity_score`
    - `max_special_proximity_score`
    - `required_final_terminal_types`
    - `required_utterance_structure_types`
- `src/v5vc/offline_mvp/losses.py`
  - `build_special_supervision_sample_mask(...)` 同步接入上述过滤器

### D42
- 配置:
  - `configs/offline_mvp_train_d42_round1_1_d7_init_phase_teacher_source_handoff_d33step10_to_d22_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration`
- 设计:
  - `student init = D7 final`
  - `step1-10`
    - teacher source = `D33 step10`
    - teacher gate = `challenge_proxy_core + short_pause_no_terminal`
    - `fused_hidden_weight = 0.05`
  - `step11-20`
    - teacher source = `D22 final`
    - teacher gate = `challenge_proxy_core`
    - `fused_hidden_weight = 0.0`

### D43
- 配置:
  - `configs/offline_mvp_train_d43_round1_1_d7_init_d10_teacher_consistency_highproximity_relaxed_gate_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - teacher gate / targeted sampling:
    - `priority_pool_memberships = ["challenge_proxy_relaxed"]`
    - `min_special_proximity_score = 0.8`
  - 目标是用比 `core-only` 更宽、但仍明显偏 special 的 target-side gate

## 关键事实
### 1. `D42` 的 phase-specific teacher source 不是挂空配置
- dry-run 训练计划已记录:
  - `teacher_checkpoint_paths` 同时包含:
    - `D33 step10`
    - `D22 final`
  - `step1-10` 与 `step11-20` 的 phase 配置也已分别落盘

解释:
- 这轮不是“teacher source 其实没换”。
- `D42` 的最小 teacher-source handoff 已经真实接入训练闭环。

### 2. 但 `D42` 没有复刻 `D33 step10`，final 也仍落回中间盆地
- `D42 step10 = 2.61436 / 0.085473 / 3.218836 / 0.455237`
- `D42 final = 2.488031 / 0.15944 / 3.115116 / 0.417186`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.043837`
- special 更差 `+0.019439`
- `e_evt` 更弱 `-0.183919`
- `z_art` 更弱 `-0.02175`

对比 `D38 / D40 / D41`:
- validation 略好一些
- 但 special、`e_evt`、`z_art` 仍没有反超 `D22`

解释:
- 最小 teacher-source handoff 甚至没有把轨迹重新钉在 `D33 step10` 上。
- 它提供的是:
  - 比 `D38-D41` 略靠近 `D22` 的中间点
  - 不是新的 breakout route

### 3. `D43` 的 high-proximity relaxed gate 也不是空放宽
- dry-run 训练计划已记录:
  - `priority_pool_memberships = ["challenge_proxy_relaxed"]`
  - `min_special_proximity_score = 0.8`
  - `priority_record_count = 24`

解释:
- 这轮不是简单把 `challenge_proxy_relaxed` 整包放进来。
- 它确实做了一个更窄的 high-proximity relaxed gate。

### 4. 但 `D43` 主要只是把形状推向 validation / e_evt，不是 special winner
- `D43 step10 = 2.570519 / 0.167371 / 2.956201 / 0.396639`
- `D43 final = 2.46381 / 0.200946 / 2.927122 / 0.374309`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.019616`
- special 更差 `+0.060945`
- `e_evt` 更强 `+0.371913`
- `z_art` 更弱 `-0.064627`

对比 `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`:
- validation 仍更差 `+0.066635`
- special 更差 `+0.029177`
- `e_evt` 略弱 `-0.051359`
- `z_art` 略强 `+0.009382`

解释:
- `D43` 不是 special 改善，
- 也不是新的 minimax，
- 它更像一个:
  - validation / `e_evt` 倾向更强
  - 但 special 明显退化
  的折中点

### 5. checkpoint / special series 没给“只是 final 选坏了”的借口
- `D42`
  - `step10 -> step20`:
    - validation 从 `2.61436` 降到 `2.488031`
    - special delta 从 `0.085473` 升到 `0.15944`
    - `e_evt` 从 `3.218836` 降到 `3.115116`
    - `z_art` 从 `0.455237` 降到 `0.417186`
- `D43`
  - `step10 -> step20`:
    - validation 从 `2.570519` 降到 `2.46381`
    - special delta 从 `0.167371` 升到 `0.200946`
    - `e_evt` 从 `2.956201` 降到 `2.927122`
    - `z_art` 从 `0.396639` 降到 `0.374309`

解释:
- 两条线都不是“最后挑错 checkpoint”。
- 它们在 `10 -> 20` 的走势都很稳定:
  - validation 继续下降
  - 但 special / control 形状同步向已知盆地内收缩

### 6. route-context comparison 没有改写当前三锚
- 在 `D22 / D29 / D33 / D38 / D39 / D40 / D41 / D42 / D43` comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

解释:
- `D42` 和 `D43` 都没有改写 route。
- 但它们一起补完了两个最小 follow-up 的负结果:
  - 最小 teacher-source handoff 不够
  - 最小 high-proximity target gate 也不够

## 当前结论
1. `D42` 证明:
   - phase-specific teacher checkpoint / source 切换已经真实接上
   - 但最小的 `D33 step10 -> D22 final` handoff 仍不会自然长出新的 final winner
2. `D43` 证明:
   - 更强一点的 target-side high-proximity relaxed gate
   - 会把模型推向 validation / `e_evt` 折中
   - 但不会带来更好的 special route
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做:
   - 最小 phase-specific teacher source 小变体
   - 最小 high-proximity relaxed gate 小变体
2. 若继续走 teacher 路线，下一步不该只是继续换 handoff 时点；
   应考虑更强的:
   - phase-specific teacher family / checkpoint 组合
   - 或 phase-specific teacher gate + source + filter 联动
3. 若继续走 target-side 路线，不该只加 proximity 阈值；
   应考虑更强的:
   - structure / terminal 显式 gating
   - 或独立的 special-target supervision 重构
