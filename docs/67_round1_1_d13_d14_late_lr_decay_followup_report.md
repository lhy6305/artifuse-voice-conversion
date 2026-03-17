# `round1.1 / D13+D14 / explicit-control late learning-rate decay follow-up` 报告

## 目的
- 在 `D7 / D10` 已确认:
  - explicit-control 机制本身有效
  - 但 final 落点仍存在 validation / special 的硬 tradeoff
- 尝试新的更高层 phase 机制:
  - 不改 sampler
  - 不改 loss family
  - 只在 late window 引入全局 `learning_rate_schedule`
- 核心问题是:
  - 终段是否主要因为固定 LR 继续过冲
  - 如果在 `step71-100` 做全局 LR decay，能否保住更多 special，同时守住 validation 与 control

## 实验信息
### D13
- 实验:
  - `EXP-20260315-030-offline-mvp-d13-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-late-lr-decay-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d13_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json`
- 基线:
  - `D7`

### D14
- 实验:
  - `EXP-20260315-029-offline-mvp-d14-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-late-lr-decay-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d14_round1_1_special_proxy_core_clause_ge4_late_handoff_zart_influence_late_lr_decay_smallscale_100_seeded_shuffle.json`
- 基线:
  - `D10`

## 共同改动
- 新增 `training.learning_rate_schedule`
- 两轮都使用:
  - `mode = linear_ramp`
  - `start_step = 71`
  - `end_step = 100`
  - `start_learning_rate = 0.0003`
  - `end_learning_rate = 0.00006`

## schedule 生效确认
- `D13` step log 已明确记录:
  - `step70 effective_learning_rate = 0.0003`
  - `step80 effective_learning_rate = 0.00022551724137931031`
  - `step90 effective_learning_rate = 0.00014275862068965515`
  - `step100 effective_learning_rate = 0.00006`
- 因而这轮不是“配置没挂上”，而是:
  - schedule 确实生效
  - 且行为变化必须按真实优化轨迹变化来解释

## 关键结果
### 1. `D13 / D14` 都没有成为更平滑的 `D7 / D10`
- `D13 final`
  - `target_validation.loss_total = 3.27992`
  - `target_special_eval.delta_loss_total = -0.22848`
  - `zero_e_evt.delta_target_loss_total = 2.950196`
  - `zero_z_art.delta_target_loss_total = 0.683167`
- `D14 final`
  - `target_validation.loss_total = 3.307872`
  - `target_special_eval.delta_loss_total = -0.240493`
  - `zero_e_evt.delta_target_loss_total = 2.892546`
  - `zero_z_art.delta_target_loss_total = 0.714912`

对比:
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`

解释:
- `D13 / D14` 确实保住了更负的 final special
- 但代价不是“小幅 validation 变差”
- 而是 final validation 直接退回到 `3.28+`
- 同时 `e_evt` 也明显弱于各自基线

### 2. 这不是“解决过冲”，而更像“把 late window 压进欠收敛”
- `D13 late window`
  - `step80 = 3.819581 / -0.368334 / 2.537093 / 1.116163`
  - `step90 = 3.493639 / -0.296075 / 2.862847 / 0.776917`
  - `step100 = 3.27992 / -0.22848 / 2.950196 / 0.683167`
- `D14 late window`
  - `step80 = 3.86839 / -0.460824 / 2.596255 / 1.154311`
  - `step90 = 3.460588 / -0.217319 / 2.754145 / 0.82428`
  - `step100 = 3.307872 / -0.240493 / 2.892546 / 0.714912`

解释:
- final special 仍保持负值
- 但 validation 改善速度明显被截断
- `e_evt` 也没有继续长到 `D7 / D10 final` 的水平
- 这说明当前问题并不是:
  - “late window 只需要更小的全局步长”
- 更像是:
  - 当前显式 control 线仍需要足够大的 late 更新来完成 validation 与 control consolidation

### 3. `D13` 还证明了全局 LR decay 会把 `D7` 从“均衡解”拉回“更早 checkpoint 形状”
- `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D13 final = 3.27992 / -0.22848 / 2.950196 / 0.683167`

解释:
- `D13` 看起来像在保留 `D7 step90` 附近的 special 负值
- 但没有把 validation 和 `e_evt` 继续推进到 `D7 final`
- 这不是更好的折中
- 而是把 final 重新拉回了一个更早、更粗糙的 late-window 区间

## 当前结论
- 新增 `learning_rate_schedule` 的工程能力本身是有效的。
- 但在当前 explicit-control 主线里:
  - `step71-100` 的全局 late LR decay 不是有效杠杆
- 它带来的不是:
  - 更好的 final balance
- 而是:
  - 更负的 special
  - 但更差的 validation
  - 更弱的 `e_evt`
  - 整体更像 under-converged final

## 当前建议
1. 不把 `D13 / D14` 升为默认方案。
2. 暂不继续优先扩展更多纯全局 `learning_rate_schedule` sweep。
3. 当前更合理的下一步不再是:
   - 继续抠全局 optimizer-level smoothing
4. 而应转去:
   - 不需要重训的新 phase 机制
   - 例如 late checkpoint averaging / weight interpolation 这类能在现有 late-window 上做折中的方法

