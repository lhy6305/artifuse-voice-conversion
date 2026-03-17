# `round1.1 / D38+D39+D40 / phase-handoff routing follow-up` 报告

## 目的
- `D36 / D37` 已经封口:
  - 简单的 checkpoint-level cross-anchor 互蒸打不开新点
- 当前更接近“结构化 checkpoint selection / routing”的最小剩余假设是:
  - 也许不需要换 teacher / 换 init
  - 而是只需要在同一条 `D7 init + D10 teacher` family 内
  - 明确控制:
    - 什么时候优先 short-pause
    - 什么时候回到 core-only
    - 以及 teacher pull 什么时候退场

所以本轮只做三条最小 routing follow-up:
- `D38 = early short_pause -> late core`
- `D39 = early core -> late short_pause`
- `D40 = D38 + teacher_off_after_step10`

## 配置与实验
### D38
- 配置:
  - `configs/offline_mvp_train_d38_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-055-offline-mvp-d38-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-fused-hidden-20step-calibration`
- 设计:
  - teacher gate 保持 `["challenge_proxy_core", "short_pause_no_terminal"]`
  - `step1-10`: sampler priority = `core + short_pause`
  - `step11-20`: sampler priority = `core`

### D39
- 配置:
  - `configs/offline_mvp_train_d39_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_core_late_shortpause_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-056-offline-mvp-d39-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-core-late-shortpause-fused-hidden-20step-calibration`
- 设计:
  - teacher gate 同样保持 `["challenge_proxy_core", "short_pause_no_terminal"]`
  - `step1-10`: sampler priority = `core`
  - `step11-20`: sampler priority = `core + short_pause`

### D40
- 配置:
  - `configs/offline_mvp_train_d40_round1_1_d7_init_d10_teacher_consistency_phase_handoff_early_shortpause_late_core_teacheroff_after_step10_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-057-offline-mvp-d40-round1-1-d7-init-d10-teacher-consistency-phase-handoff-early-shortpause-late-core-teacheroff-after-step10-fused-hidden-20step-calibration`
- 设计:
  - sampler handoff 与 `D38` 完全相同
  - 但 `teacher_consistency.weight_schedule` 设为:
    - `step1-10 = 0.15`
    - `step11-20 = 0.0`

## 关键事实
### 1. `D38 step10` 精确复刻了 `D33 step10`
- `D38 step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
- 与 `D33 step10` 完全一致

解释:
- 这轮不是“phase handoff 没接上”。
- `early short_pause` 的前半段 routing 确实把轨迹推到了已知的 special-only checkpoint。

### 2. `D38` 证明“early short_pause -> late core”只会把 `D33 step10` 拉回更弱的中间点
- `D38 final = 2.494434 / 0.161978 / 3.096622 / 0.436892`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.05024`
- special 更差 `+0.021977`
- `e_evt` 更弱 `-0.202413`
- `z_art` 仅近似持平 `-0.002044`

解释:
- late core handoff 并没有把 `D33 step10` 收敛成新的 minimax。
- 它只是在付出明显 validation 代价的同时，
  把 special / `e_evt` 拉回到比 `D22` 更差的中间点。

### 3. `D39` 证明“late short_pause tail”也救不回 `D33` 家族
- `D39 step10 = 2.592867 / 0.137444 / 3.042418 / 0.416722`
- `D39 final = 2.489906 / 0.169107 / 3.048095 / 0.407912`

对比 `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`:
- 更准确的描述不是“靠 late short_pause 成功拉向 D33”
- 而是:
  - 它只停在一个比 `D29` 更差、比 `D22` 更弱的中间点附近

解释:
- 如果前半段先把轨迹定在 core-only family，
  那么后半段再补 short-pause tail，
  并不能自然恢复 `D33` 的 stronger special/control shape。

### 4. `D40` 证明问题不主要是“late teacher 持续拉扯”
- `D40 step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
- `D40 final = 2.492335 / 0.160804 / 3.102396 / 0.431034`

对比 `D38 final = 2.494434 / 0.161978 / 3.096622 / 0.436892`:
- validation 只略好 `-0.002099`
- special 只略好 `-0.001174`
- `e_evt` 只略好 `+0.005774`
- `z_art` 略弱 `-0.005858`

更关键的是:
- `D40 step20` 的 `loss_teacher_consistency = 0.0`
- 说明 `teacher_off_after_step10` 确实生效了

解释:
- 这轮不是“teacher 没关掉”。
- 即使在 `step10` 之后完全去掉 teacher pull，
  仅靠 late core consolidation，
  轨迹也还是回到和 `D38` 几乎同型的中间点。
- 所以 `D38` 的失败主因，不是“late broad teacher 继续把轨迹拉坏”。

## 当前结论
1. phase-handoff routing 这条线没有产生新的 joint winner。
2. `D38` 说明:
   - `early short_pause -> late core`
   - 只是在重放 `D33 step10` 后，再把它拉回一个比 `D22` 更差的中间点。
3. `D39` 说明:
   - `early core -> late short_pause`
   - 也不能把轨迹补回 `D33` 家族。
4. `D40` 说明:
   - 即使让 teacher 在 `step10` 后退场，
   - 也不能把 `D33 step10` 稳定收敛成新的 minimax。
5. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做同 family 的 sampler-handoff / teacher-off 小变体。
2. 若继续推进，优先转向:
   - 更强的 target / gate 级重构
   - 或更明确的 phase-specific teacher target/gate 机制
   - 而不是继续只改 sampler 顺序
3. 当前 `D38 / D39 / D40` 只应被解释为:
   - 对“结构化 routing 是否足够”的必要封口
   - 不是新的 breakout family
