# `round1.1 / D24+D25+D26 / short-pause teacher-gate follow-ups` 报告

## 目的
- 在 `D23` 已经证明 `challenge_proxy_relaxed` 这层 coverage 扩展信息增益很低之后，
- 改试一个更有结构差异的 teacher gate:
  - `challenge_proxy_core + short_pause_no_terminal`
- 并验证两件事:
  1. 单纯扩 teacher gate 是否足够；
  2. 如果不够，是否需要同时让 sampler 真的把这类样本拉进来。

## 配置与实验
### D24
- 配置:
  - `configs/offline_mvp_train_d24_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_smallscale_30_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-041-offline-mvp-d24-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-30step-calibration`
- 设计:
  - `D22` 同构
  - 只把 `teacher_consistency.pool_memberships` 扩到
    `["challenge_proxy_core", "short_pause_no_terminal"]`
  - sampler 仍只优先 `challenge_proxy_core`

### D25
- 配置:
  - `configs/offline_mvp_train_d25_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_smallscale_30_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-042-offline-mvp-d25-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-30step-calibration`
- 设计:
  - 保持 `D24` 的 short-pause teacher gate
  - 同时把 `targeted_sampling.priority_pool_memberships` 扩到
    `["challenge_proxy_core", "short_pause_no_terminal"]`

### D26
- 配置:
  - `configs/offline_mvp_train_d26_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration`
- 设计:
  - 直接把 `D25` 截到 `20` step
  - 目标是把 `D25 step20` 这个更好的中段点固化为 final

## 关键事实
### 1. `short_pause_no_terminal` 的新增信息其实很小，而且大部分已被 `challenge_proxy_core` 覆盖
- `challenge_proxy_core = 16`
- `short_pause_no_terminal = 19`
- 交集 `core ∩ short_pause = 15`
- `short_pause_only = 4`

这意味着:
- short-pause gate 的真正新增样本只有 `4` 条
- 所以如果这 `4` 条进不了 batch，`D24` 基本就不会真的偏离 `D22`

### 2. `D24` 实际上是一个“空覆盖”负例
- `D24 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
- 与 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936` 数值级完全一致
- 更关键的是:
  - `short_pause_only` 的 `4` 条样本在 `D24` 的 30-step target batch 中一次都没有出现

解释:
- 这轮不是“short-pause gate 方向错了”
- 而是这轮根本没有真正测到新增的 `4` 条样本
- 因此 `D24` 只能被视为:
  - 一个确认“只扩 teacher gate、不改 sampler 时，实验可能完全退化成旧轨迹”的负例

### 3. `D25` 不是空跑，它真的改变了轨迹
- `D25 final = 2.444897 / 0.176357 / 2.993643 / 0.403509`
- 相对 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
  - validation 近似持平
  - final special 变差
  - `e_evt / z_art` 都回落

但 `D25` 的真正价值不在 final，而在前段:
- `D25 step10 = 2.620166 / 0.081417 / 3.227018 / 0.465696`
- `D25 step20 = 2.523898 / 0.117894 / 3.27265 / 0.460259`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- `D25 step20`
  - special 更好
  - `z_art` 更强
  - `e_evt` 接近
  - validation 更差

解释:
- `D25` 没有把 final 推向更优点
- 但它确实把轨迹改成了另一种更有意思的 tradeoff:
  - 更偏 special / `z_art`
  - 更不偏 validation

### 4. `D25` 的变化并不是因为 `short_pause_only` 真的被采到了
- `short_pause_only` 的 `4` 条样本在 `D25` 的 30-step target batch 里也仍然一次都没出现
- 但训练轨迹已经明显不同于 `D22 / D24`
- 更合理的解释是:
  - 把 priority pool 从 `core` 扩到 `core + short_pause`
  - 改变了 priority sampler 对重叠样本的抽样顺序与组合
  - 虽然没采到那 `4` 条 short-only 样本
  - 但仍通过 overlap-driven reordering 改变了轨迹

### 5. `D26` 证明 `D25 step20` 可以被稳定固化成 final
- `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`
- 与 `D25 step20` 完全一致

解释:
- 这不是一个偶然 checkpoint
- 它可以通过更短 consolidation 直接稳定复现

## 当前结论
- `D24` 可以正式视为“只扩 short-pause teacher gate，但不改 sampler”的空覆盖负例。
- `D25` 是这条 short-pause family 里第一个真正改变轨迹的点。
- `D26` 则把 `D25 step20` 固化成了稳定 final。

当前 teacher-consistency family 的结构可以更新为:
- `D22`:
  - validation-oriented family reference
- `D26`:
  - 更偏 special / `z_art` 的 family reference

也就是说:
- teacher-consistency family 现在已经不是单点
- 而是出现了一个清晰的双参考点分叉

## 当前建议
1. 保留 `teacher_consistency` 能力，不回退代码。
2. `D24` 不升为默认方案。
3. `D25` 不升为默认 final，但保留为关键轨迹证据。
4. `D26` 升为 teacher-consistency family 的第二参考点。
5. 若继续沿 short-pause family 推进，下一步更值得优先试的是:
   - 显式确保 `short_pause_only` 这 `4` 条样本真的进入训练
   - 而不是继续只做 pool 名称层面的 coverage 扩展
6. 当前不建议优先做:
   - `D24` 类型的“只扩 teacher gate、不改 sampler”重复实验
   - `D25` 类型的更多无约束 30-step 延长

