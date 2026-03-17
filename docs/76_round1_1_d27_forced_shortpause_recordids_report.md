# `round1.1 / D27 / forced short-pause record ids` 报告

## 目的
- 在 `D24 / D25 / D26` 之后，当前最关键的未决问题已经非常具体:
  - `short_pause_only` 的新增样本到底是“没真正进训练”，
  - 还是“真进了训练，但方向就是会推坏主线”。
- 因此本轮只做一件事:
  - 给 targeted sampling 新增最小能力 `priority_record_ids`
  - 让 short-pause-only 样本在 priority slot 中被前置抽取
  - 正式验证“显式 short-only 注入”的真实效果

## 代码与配置
### 新增 sampler 能力
- `src/v5vc/offline_mvp/data.py`
  - 新增 `priority_record_ids` 支持
  - 在 `priority_interleave` 中先消费这些 record ids，再回到常规 priority pool
- `src/v5vc/train_entry.py`
  - 训练计划摘要与 markdown 输出补充 `priority_record_ids`

### D27
- 配置:
  - `configs/offline_mvp_train_d27_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_recordids_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-044-offline-mvp-d27-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-recordids-20step-calibration`
- 设计:
  - 以 `D26` 为骨架
  - 继续保留:
    - `teacher_consistency.pool_memberships = ["challenge_proxy_core", "short_pause_no_terminal"]`
    - `targeted_sampling.priority_pool_memberships = ["challenge_proxy_core", "short_pause_no_terminal"]`
  - 新增:
    - `priority_record_ids = short_pause_only`

## 关键事实
### 1. 这轮不是“记录强塞失败”，而是确实把 train-side short-only 样本打进了训练
- `short_pause_only` 候选共有 `4` 条:
  - `target::chapter3_2_firefly_191`
  - `target::chapter3_2_firefly_212`
  - `target::chapter3_3_firefly_125`
  - `target::chapter3_3_firefly_148`
- 其中:
  - `target::chapter3_2_firefly_212` 实际位于 formal `target_validation`
  - 真正可训练的 short-only 样本只有 `3` 条
- `D27` 正式训练日志里，这 `3` 条 train-side short-only 样本都被反复抽到:
  - `step1`: `target::chapter3_2_firefly_191`
  - `step2`: `target::chapter3_3_firefly_148`
  - `step3`: `target::chapter3_3_firefly_125`
  - 后续 `step4-20` 继续循环命中这三条

解释:
- 这轮已经排除了“只是 dry-run 命中了、正式训练没命中”的借口。
- `D27` 是对 short-only 显式注入的有效实验。

### 2. 一旦 short-only 真正进入训练，轨迹会明显往坏处偏
- `D27 final`
  - `target_validation.loss_total = 2.466208`
  - `target_special_eval.delta_loss_total = 0.206141`
  - `zero_e_evt.delta_target_loss_total = 2.863938`
  - `zero_z_art.delta_target_loss_total = 0.356843`

对比 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`:
- validation 变好
- 但 final special 明显更差
- `e_evt / z_art` 都明显回落

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 仍没好到明显打赢 `D22`
- special 更差
- `e_evt / z_art` 更差

解释:
- `D27` 不是新的 family winner。
- 它更像把模型推向:
  - validation 稍改善
  - 但 challenge/control 明显变弱

### 3. late-window 也没有藏着更好的 checkpoint
- `D27 step10 = 2.573033 / 0.177756 / 2.89979 / 0.379443`
- `D27 step20 = 2.466208 / 0.206141 / 2.863938 / 0.356843`

解释:
- 这不是“step20 overshoot 了，step10 更好”的情况
- `step10` 比 final special 还要更差
- 所以这条 forced short-only 注入线没有隐藏 sweet spot

## 当前结论
- `D27` 给出了这条短暂停顿 short-only 注入路线的硬负证据:
  - 一旦 train-side short-only 样本真正进入训练，
  - 轨迹不会朝更好的 special/control 平衡走，
  - 反而会把 `D26` 这条 family 点推坏。
- 因此:
  - short-pause family 不应再继续沿“显式强塞 short-only 样本”方向深挖

## 当前建议
1. 保留 `priority_record_ids` 代码能力，不回退。
2. 不把 `D27` 升为默认方案。
3. `D22` 继续保持 teacher-consistency family 的 validation-oriented 参考点。
4. `D26` 继续保持 teacher-consistency family 的 special / `z_art`-leaning 参考点。
5. 当前不再继续优先做:
   - short-pause-only 的更强注入
   - short-pause-only 的更长 consolidation
   - short-pause-only 的更高 priority ratio
6. 若下一步继续推进 teacher-consistency family，更值得转向:
   - family 参考点之间的 cross-anchor consolidation
   - 或更不同的 distillation target shape

