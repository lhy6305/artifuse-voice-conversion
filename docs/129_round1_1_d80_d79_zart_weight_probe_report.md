# 129. round1.1 `D80 / D79 z_art-weight probe` 报告

## 背景
`D79` 已经把当前问题收束到一个更窄的点:

- 在 `D22 late` 骨架里，
  单纯提高 late teacher 总权重，
  可以把:
  - `special`
  - `e_evt`
  一起拉回来
- 但 pure long-horizon default/minimax 仍被:
  - `D33`
  卡住
- 当前最明显缺口被写成:
  - `z_art`

因此这轮不再改:
- teacher source
- sampler
- teacher total weight

只做一个最小的 `z_art` 定向 probe:
- 在 `D79` 上轻量抬高 late `z_art_weight`

## 本轮设计
### `D80`
- 配置:
  - `configs/offline_mvp_train_d80_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_zartboost_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-036-offline-mvp-d80-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartboost-200step-calibration`

设计原则:
- 完整继承 `D79`
- 唯一变量:
  - late `step11-200`
    - `teacher_consistency.z_art_weight: 1.0 -> 1.25`

它回答的问题很纯:
- 在 `D79` 已经把 teacher force 提高的前提下，
  轻量增加 `z_art` 蒸馏权重，
  能否继续补 `z_art`
  而不回吐 `special / e_evt`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并已并入 full long-horizon route:
  - `anchor_route_analysis(D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80)`
  - `anchor_route_selection`
  - `final comparison`
  - `route recap`

## 指标口径
- validation
- special delta
- `zero_e_evt_delta`
- `zero_z_art_delta`

## `D80` 结果
- `step50 = 2.31319 / 0.190516 / 2.631278 / 0.332789`
- `step100 = 2.237649 / 0.19908 / 2.45153 / 0.482801`
- `step150 = 2.169401 / 0.226305 / 2.142377 / 0.446129`
- `step200 = 2.140498 / 0.233658 / 2.130963 / 0.441535`

## 与 `D79` 的关键对比
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`
- `D80 = 2.140498 / 0.233658 / 2.130963 / 0.441535`

`D80 - D79`:
- validation `+0.002092`
- special `+0.001664`
- `e_evt` `-0.039331`
- `z_art` `-0.027894`

解释:
- 这轮没有出现想要的:
  - `z_art` 补回
- 反而出现了:
  - validation 略差
  - special 略差
  - `e_evt` 更差
  - `z_art` 也更差

所以 `D80` 不是:
- `D79 + z_art` 增强版

更准确地说它是:
- 被 `D79` 完整支配的负结果

## 与 `D76` 的位置关系
`D80 vs D76`:
- validation `+0.032562`
- special `-0.012897`
- `e_evt` `+0.193197`
- `z_art` `+0.016884`

解释:
- 它对 `D76` 仍然保留了一部分:
  - special / `e_evt`
  收益
- 但这已经没有制度意义，
  因为同一方向上有更强且更干净的:
  - `D79`

## full long-horizon route 的决定性结果
把 `D80` 并入 full long-horizon route 后，
所有 route 角色都保持不变:

- validation = `D76`
- special = `D79`
- `zero_e_evt = D79`
- `zero_z_art = D33`
- minimax = `D33`

selector(`budget=0.05`) 继续给出:
- `selected_policy = default_minimax`
- `selected_anchor = D33`

derived thresholds 也保持不变:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.03047`
- `best_e_evt_floor = 2.170294`
- `best_z_art_floor = 0.710849`

解释:
- `D80` 没有改写任何 route-level 结论
- 它甚至没有改变:
  - special-push anchor
  - best `e_evt` floor anchor

这说明当前这条:
- `late z_art_weight` 轻量抬升

并不是有效杠杆

## 当前阶段正式判断
1. `D80` 是明确负结果。
2. 在 `D79` 骨架上，
   轻量提高 late `z_art_weight`
   不能补回 `z_art`，
   反而会轻微回吐已有收益。
3. 当前更准确的收束是:
   - `D79` 继续保留为 `special + e_evt` leader
   - `D80` 不进入后续主线 family

## 先说人话
- 这轮已经把一个误导性方向排干净了。
- 问题不是:
  - `D79` 只差一点点 `z_art_weight`
- 更像是:
  - 这条轴本身就不是当前缺口的有效补法

## 下一步建议
1. 停止继续扩:
   - `late z_art_weight` 小幅调节
2. 若继续沿 `D79` 主线推进，
   下一个更值得试的问题应改成:
   - 是否存在比 `teacher-consistency z_art_weight` 更外层的 `z_art` restoration 机制
3. 当前更合理的后续方向是:
   - 保留 `D79` 骨架
   - 改试非 teacher-per-head 权重类的 `z_art` 定向 restoration

## 产物
- 配置:
  - `configs/offline_mvp_train_d80_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_zartboost_200step_smallscale_seeded_shuffle.json`
- full long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_default_minimax/`
