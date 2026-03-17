# `round1.1 / D46-D47 / teacher-family + late filter linkage` 报告

## 目的
- `D45` 已经给出一个新的 non-dominated compromise:
  - `D33 step10 -> D29 final`
  - special 比 `D22` 略好
  - 但 validation / control 仍不够
- `D44` 则说明:
  - `D43` 的退化来自 relaxed gate 中混入的 terminal / single-clause 样本

因此下一步最自然的最小 follow-up 就是:
- 保留 `D45` 的 teacher-family handoff
- 但把 late phase 的 teacher / sampler gate
  与 `D44` 式 relaxed-none-other filter 联动起来

这轮只做两个强度不同的 late filter:
- `D46 = late relaxed none-other >= 0.8`
- `D47 = late relaxed none-other >= 0.84`

## 配置设计
### D46
- 配置:
  - `configs/offline_mvp_train_d46_round1_1_d7_init_phase_teacher_family_filter_handoff_d33step10_to_d29_relaxed_none_other_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-063-offline-mvp-d46-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-20step-calibration`
- 设计:
  - `step1-10`
    - teacher source = `D33 step10`
    - gate = `challenge_proxy_core + short_pause_no_terminal`
    - `fused_hidden_weight = 0.05`
  - `step11-20`
    - teacher source = `D29 final`
    - gate = `challenge_proxy_relaxed`
    - `min_special_proximity_score = 0.8`
    - `required_final_terminal_types = ["none"]`
    - `required_utterance_structure_types = ["other"]`
- dry-run:
  - `phase_priority_record_counts = 19 -> 19`

### D47
- 配置:
  - `configs/offline_mvp_train_d47_round1_1_d7_init_phase_teacher_family_filter_handoff_d33step10_to_d29_relaxed_none_other_hi84_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-064-offline-mvp-d47-round1-1-d7-init-phase-teacher-family-filter-handoff-d33step10-to-d29-relaxed-none-other-hi84-20step-calibration`
- 设计:
  - `step1-10` 与 `D46` 相同
  - `step11-20`
    - 与 `D46` 相同
    - 但 `min_special_proximity_score = 0.84`
- dry-run:
  - `phase_priority_record_counts = 19 -> 15`

## 关键事实
### 1. `D46 / D47 step10` 都与 `D45 step10` 完全一致
- `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`

解释:
- 这说明:
  - early phase 没被误改
  - 当前观察到的差异全部来自 late filter linkage

### 2. `D46` 把 `D45` 往 validation 方向推了一点，但 special / control 同步回吐
- `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
- `D46 final = 2.484944 / 0.158502 / 3.091893 / 0.392083`

相对 `D45`:
- validation 改善 `-0.018811`
- special 退化 `+0.024786`
- `e_evt` 变弱 `-0.104416`
- `z_art` 变弱 `-0.01515`

解释:
- 用 `D44` 那套 relaxed-none-other late set 去替换 `D45` 的 late set，
- 并没有保住 `D45` 的 special-compromise 价值
- 它更像是:
  - 沿前沿朝 validation 方向滑了一步
  - 同时丢掉了 `D45` 最珍贵的 special 优势

### 3. `D47` 继续加硬 late filter，只会把这个趋势再放大
- `D47 final = 2.480151 / 0.170562 / 3.014662 / 0.378469`

相对 `D46`:
- validation 再改善 `-0.004793`
- special 再退化 `+0.01206`
- `e_evt` 再变弱 `-0.077231`
- `z_art` 再变弱 `-0.013614`

解释:
- `0.84` 这档更强 late threshold
- 没有产生新的平衡点，
- 只是继续沿相同方向把模型推成:
  - validation 更低
  - 但 special / control 更差

### 4. `D46 / D47` 都没有超过 `D45` 作为这条 family 的最佳 tradeoff
- `D45` 仍是:
  - special 最接近 `D22 / D33` compromise 的点
- `D46 / D47` 虽然 validation 更好，
  但都付出了更差的:
  - special
  - `e_evt`
  - `z_art`

解释:
- 现在可以把这条结论说得更明确:
  - `D45` 不是偶然
  - 它已经是当前这条 teacher-family follow-up 上
    更值得继续引用的 compromise 点
- 继续只靠 late filter 变硬，
  不会自然把它推成更强 route

### 5. route-context comparison 仍未改写当前三锚
- 在包含 `D46 / D47` 的 comparison 中:
  - validation leader 仍是 `D29`
  - default minimax 仍是 `D22`
  - special / `e_evt` / `z_art` leader 仍是 `D33`

## 当前结论
1. `D46 / D47` 证明:
   - 在 `D45` 这条 teacher-family 路线上
   - 继续把 late phase filter 向 `relaxed none-other` 收紧
   - 只会形成更 validation-first 的点
   - 不会自然产生更好的 special-compromise
2. 当前这条 family 内，
   最有价值的 follow-up 仍是 `D45`，
   而不是 `D46 / D47`
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做 `D45` 上的 late filter 阈值 / 筛样硬化小变体。
2. 若继续沿 `D45` 推进，
   下一步不该只是继续缩 late sample set；
   更值得考虑:
   - late teacher family 的更强 target-shape 联动
   - 或单独给 formal special 对齐的监督信号
