# 132. round1.1 `D83 / D79 phase-specific late teacher handoff` 报告

## 背景
- `D78` 已证明:
  - 全程 late `D33` teacher
  - 能明显抬高 `z_art`
  - 但 validation 税过大，且会把 minimax 重新拉回 `D33`
- `D79` 已证明:
  - 全程 late `D22` teacher weight lift
  - 能稳定拿到 `special + e_evt`
  - 但 `z_art` 仍不够
- `D80 / D81 / D82` 又把:
  - `late z_art_weight`
  - `late z_art_influence retarget`
  - `full-priority singleton exposure`
  这三条近邻轴基本排干净

因此这轮改问:
- 能否把 `D78` 的 early-late `z_art` restore
- 和 `D79` 的 late-late stability
- 用 phase-specific teacher handoff 拼成一个更好的 joint point

## 本轮设计
### `D83`
- 配置:
  - `configs/offline_mvp_train_d83_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33to22late_teacher_handoff_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration`

设计原则:
- 完整继承 `D79`
- 不改:
  - horizon
  - singleton sampler
  - `singleton_sparse_proxy_aux`
  - `z_art_influence_aux`
- 唯一主改动是把 late `teacher_consistency` 拆成两段:
  - `step11-100`
    - teacher = `D33 step10`
    - `weight = 0.15`
    - `fused_hidden_weight = 0.08`
    - gate = `micro_pause_none_singleton_strict`
  - `step101-200`
    - teacher = `D22 step30`
    - `weight = 0.20`
    - `fused_hidden_weight = 0.08`
    - gate = `micro_pause_none_singleton_strict`

这轮问题很纯:
- `D33 -> D22` 的 long-horizon late handoff
- 是否能先留下 `z_art`
- 再用 `D22` 收尾保住 validation / `e_evt`

## 执行链
- 已完成:
  - `init-experiment --route-selection`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并已并入 full long-horizon route:
  - `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83`

## 关键事实
### 1. `step100 -> 101` 的 teacher handoff 真实生效，不是挂空配置
- `step100 effective_teacher_consistency.teacher_checkpoint_path`
  - `D33 step10`
- `step101 effective_teacher_consistency.teacher_checkpoint_path`
  - `D22 step30`
- 同时:
  - `teacher_weight: 0.15 -> 0.20`
  - `fused_hidden_weight` 保持 `0.08`
  - gate 都保持 `micro_pause_none_singleton_strict`

解释:
- 这轮不是“phase-specific handoff 配了但没吃进去”。
- `D83` 的 source 切换在训练日志里有明确证据。

### 2. `D83` 的 `step100` 确实长在 `D78` 附近，但后半段没把 `z_art` 留住
- `step100 = 2.256422 / 0.190305 / 2.428461 / 0.530758`
- `step150 = 2.174416 / 0.221924 / 2.197493 / 0.463976`
- `step200 = 2.140033 / 0.23583 / 2.011104 / 0.42172`

解释:
- `step100` 时:
  - `z_art` 已经被抬到明显高于 `D79` 的水平
- 但切回 `D22` 后:
  - `z_art` 从 `0.530758`
    持续掉到 `0.42172`
  - `e_evt` 也从 `2.428461`
    掉到 `2.011104`
- 这说明:
  - handoff 不是没作用
  - 而是后半段会把前半段积累的大部分 control 重新洗掉

### 3. `D83` final 被 `D79` 完整支配
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`
- `D83 = 2.140033 / 0.23583 / 2.011104 / 0.42172`

`D83 - D79`:
- validation `+0.001627`
- special `+0.003836`
- `e_evt` `-0.15919`
- `z_art` `-0.047709`

解释:
- `D83` 四项里没有一项赢过 `D79`
- 所以它不是:
  - `D79 + z_art restore`
- 更准确地说，它是:
  - 一条被父骨架 `D79` 完整支配的负结果

### 4. `D83` 也没有形成新的 route 角色
- 相对 `D76`:
  - validation `+0.032097`
  - special `-0.010725`
  - `e_evt` `+0.073338`
  - `z_art` `-0.002931`
- 相对 `D33`:
  - validation `+0.017334`
  - special `-0.004016`
  - `e_evt` `+0.040804`
  - `z_art` `-0.289129`
- 相对 `D82`:
  - validation `-0.008871`
  - special `+0.017601`
  - `e_evt` `-0.115353`
  - `z_art` `-0.014489`

解释:
- `D83` 有一点:
  - 比 `D76` 更偏 special / `e_evt`
- 但它既没拿走 `D79` 的 `e_evt`
- 也没拿走 `D82` 的 special
- 更没靠近 `D33` 的 `z_art`

### 5. full long-horizon route 完全不变
- route 仍是:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`
- selector 继续给出:
  - `selected_policy = default_minimax`
  - `selected_anchor = D33`
- 阈值保持:
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.040968`
  - `best_e_evt_floor = 2.170294`
  - `best_z_art_floor = 0.710849`

## 当前结论
1. `D83` 证明:
   - long-horizon 的 `D33 -> D22` late teacher handoff 能真实命中
   - 但不会自然留下前半段拉起的 `z_art`
2. 当前问题不是:
   - source handoff 没接上
3. 更像是:
   - `D22` 收尾会把这条 phase handoff 的 control 收益重新冲掉
4. 因此这条轴当前应被判定为:
   - 真实负结果
   - 且被 `D79` 完整支配

## 当前建议
1. 停止继续扩:
   - `D33 -> D22` late teacher handoff
   - 或其 handoff step 小幅前后平移
2. 当前主线继续保持:
   - `D76 = validation`
   - `D82 = special`
   - `D79 = e_evt`
   - `D33 = default_minimax + z_art`
3. 若继续追 `z_art`，更高信息量的问题应改成:
   - 是否存在不依赖 `late teacher source handoff` 的更外层 `z_art` restoration 机制

## 产物
- 配置:
  - `configs/offline_mvp_train_d83_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33to22late_teacher_handoff_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `reports/experiments/EXP-20260316-039-offline-mvp-d83-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33to22late-teacher-handoff-200step-calibration.metrics.json`
- full route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_default_minimax/`
