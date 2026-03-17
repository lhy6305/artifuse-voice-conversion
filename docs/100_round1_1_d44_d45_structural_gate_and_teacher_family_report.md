# `round1.1 / D44-D45 / structural none-other gate + phase-specific teacher family` 报告

## 目的
- `D42` 已证明:
  - 最小 `D33 step10 -> D22 final` teacher-source handoff
  - 只会回到中间盆地
- `D43` 已证明:
  - `challenge_proxy_relaxed + proximity>=0.8`
  - 会把模型推向 validation / `e_evt` 折中
  - 但 special 明显退化

因此这轮继续只做两条纯配置 follow-up:
- `D44 = D43 + 更硬的 structure / terminal gate`
- `D45 = D42 的更强 teacher-family 版本`

目标很直接:
- 先确认 `D43` 的退化是不是来自 relaxed gate 里混入了 terminal / single-clause 样本
- 再确认 late teacher 从 `D22` 换成 `D29`，能否把 `D33` 的 early special shape 接成更有价值的 final compromise

## 配置设计
### D44
- 配置:
  - `configs/offline_mvp_train_d44_round1_1_d7_init_d10_teacher_consistency_relaxed_none_other_gate_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-061-offline-mvp-d44-round1-1-d7-init-d10-teacher-consistency-relaxed-none-other-gate-fused-hidden-20step-calibration`
- 设计:
  - 以 `D43` 为底
  - 保留:
    - `challenge_proxy_relaxed`
    - `min_special_proximity_score = 0.8`
    - `fused_hidden_weight = 0.05`
  - 但新增:
    - `required_final_terminal_types = ["none"]`
    - `required_utterance_structure_types = ["other"]`
- dry-run 结果:
  - `priority_record_count = 19`

### D45
- 配置:
  - `configs/offline_mvp_train_d45_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29_shortpause_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-062-offline-mvp-d45-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29-shortpause-20step-calibration`
- 设计:
  - `student init = D7 final`
  - targeted sampling 全程保持:
    - `challenge_proxy_core + short_pause_no_terminal`
  - `step1-10`
    - teacher source = `D33 step10`
    - `fused_hidden_weight = 0.05`
  - `step11-20`
    - teacher source = `D29 final`
    - `fused_hidden_weight = 0.0`
- dry-run 结果:
  - `teacher_checkpoint_paths = [D29 final, D33 step10]`

## 关键事实
### 1. `D44` 基本坐实了 `D43` 的问题来自 terminal / single-clause contamination
- `D43 final = 2.46381 / 0.200946 / 2.927122 / 0.374309`
- `D44 final = 2.504646 / 0.14823 / 3.100172 / 0.422595`

相对 `D43`:
- validation 变差 `+0.040836`
- special 改善 `-0.052716`
- `e_evt` 增强 `+0.17305`
- `z_art` 增强 `+0.048286`

解释:
- `D44` 唯一关键变化就是:
  - 把 relaxed gate 限制回 `none + other`
- 因此可以合理推断:
  - `D43` 的主要退化来源
  - 确实就是 mixed-in 的 `terminal_* / single_clause_terminal` 样本

### 2. 但 `D44` 仍然只是被 `D22` 压住的修正版，不是新 route
- `D44 final = 2.504646 / 0.14823 / 3.100172 / 0.422595`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.060452`
- special 更差 `+0.008229`
- `e_evt` 更弱 `-0.198863`
- `z_art` 更弱 `-0.016341`

解释:
- `D44` 的意义是:
  - 把 `D43` 的退化来源钉住
- 不是:
  - 形成一个新的可引用 route

### 3. `D45` 给出了一个新的非支配 compromise 点
- `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.059561`
- special 更好 `-0.006285`
- `e_evt` 更弱 `-0.102726`
- `z_art` 更弱 `-0.031703`

对比 `D33 final = 2.52818 / 0.111677 / 3.312339 / 0.465828`:
- validation 更好 `-0.024425`
- special 更差 `+0.022039`
- `e_evt` 更弱 `-0.11603`
- `z_art` 更弱 `-0.058595`

解释:
- `D45` 不是新 minimax
- 但它确实不是简单被 `D22` 或 `D33` 全面支配的点
- 更准确地说:
  - 它是当前所有 `post-D41` follow-up 里
  - 最接近 “把 `D33` 的 special 优势部分带进 final，同时不完全掉回 `D33` validation” 的 compromise

### 4. 但 `D45` 仍然没有满足当前 route policy
- 当前 route policy 仍是:
  - `default_minimax`
  - `max_validation_budget_over_best = 0.05`
- best validation 仍是 `D29 = 2.397175`
- `D45 = 2.503755`

解释:
- `D45` 相对 best validation 的预算超出仍很大，
- 所以即使它比 `D22` 略好一点 special，
- 也还不足以改写当前 default route

### 5. checkpoint series 说明两条线都不是“final 选坏了”
- `D44`
  - `step10 = 2.585727 / 0.141728 / 3.060794 / 0.463527`
  - `step20 = 2.504646 / 0.14823 / 3.100172 / 0.422595`
- `D45`
  - `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
  - `step20 = 2.503755 / 0.133716 / 3.196309 / 0.407233`

解释:
- `D44` 是:
  - validation 继续下降
  - special 略回吐
  - control 部分回升
- `D45` 是:
  - validation 继续下降
  - special 继续改善
  - `e_evt` 在 late phase 明显抬升
- 这说明:
  - `D45` 的 late `D29` teacher family 不是没起作用
  - 只是它仍不够把最终点推成新 route

### 6. route-context comparison 仍未改写三锚
- 在包含 `D44 / D45` 的 comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

## 当前结论
1. `D44` 证明:
   - `D43` 的退化主要来自 relaxed gate 里混入的 terminal / single-clause 样本
   - 但把它们剔掉之后，只会回到一个被 `D22` 压住的点
2. `D45` 证明:
   - `D33 step10 -> D29 final` 的 phase-specific teacher family handoff
   - 确实比 `D42` 更有信息量
   - 也给出了一个新的非支配 compromise 点
   - 但仍不足以改写当前 default route
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做:
   - `relaxed` gate 只加 / 只减结构过滤器的小变体
2. 若继续走 target-side 路线，优先考虑:
   - 更明确的 `none / nonverbal` 目标监督
   - 而不是继续在 relaxed gate 上做轻量筛样
3. 若继续走 teacher 路线，当前最值得继续的不是回到 `D42`，
   而是沿着 `D45` 方向继续增强:
   - phase-specific teacher family + phase-specific filter 联动
   - 或 late teacher family 的更强 gate 约束
