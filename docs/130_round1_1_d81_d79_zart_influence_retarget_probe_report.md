# 130. round1.1 `D81 / D79 z_art-influence retarget probe` 报告

## 背景
`D80` 已经把一条容易误扫的轴排干净:

- 在 `D79` 骨架上
- 继续小幅提高 late `teacher_consistency.z_art_weight`
- 不能补回 `z_art`

因此这轮不再改:
- teacher source
- teacher total weight
- teacher per-head weight

而是转去测试一条更外层、且曾在早期 `D7` explicit-control 线上证明过有真实信号的机制:
- `z_art_influence_aux`

这轮真正要回答的问题是:
- 如果在 `D79` 上把 `z_art_influence_aux`
  从原先的 `challenge_proxy_core`
  明确转到当前 long-horizon 主战场
  `micro_pause_none_singleton_strict`
- 它能不能在不改 teacher 结构的前提下，
  直接补回一点 `z_art`

## 本轮设计
### `D81`
- 配置:
  - `configs/offline_mvp_train_d81_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_zartretarget_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-037-offline-mvp-d81-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-zartretarget-200step-calibration`

设计原则:
- 完整继承 `D79`
- 保留:
  - `D22 late`
  - late `teacher_consistency.weight = 0.20`
  - `singleton_sparse_proxy_aux`
  - 当前 late sampler
- 唯一主改动:
  - `losses.z_art_influence_aux.pool_memberships`
    - `["challenge_proxy_core"]`
    - 改为 `["micro_pause_none_singleton_strict"]`
  - 并加:
    - `required_within_special_duration_ceiling = true`
  - weight schedule 改成 late-only:
    - `start_step = 11`
    - `end_step = 25`

它回答的问题很纯:
- 若把显式 `z_art` influence floor
  直接对准当前 late 微停顿 singleton pool，
  会不会成为 `D79` 剩余 `z_art` 缺口的有效补法

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
  - `anchor_route_analysis(D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81)`
  - `anchor_route_selection`
  - `final comparison`
  - `route recap`

## 先确认机制确实被激活
`D81` 不是挂空配置。

训练后段日志中:
- `loss_z_art_influence_aux`
  仍持续为正，
  末段可见 `0.0065 -> 0.0003` 量级
- `loss_singleton_sparse_proxy_aux`
  也持续非零，
  末段仍在 `0.18 ~ 0.29`

这说明:
- 本轮并不是“因为新 pool 没吃到样本，所以结果无效”
- 而是在机制已经真实命中 late pool 的前提下，
  依然没有改写终盘排序

## `D81` 结果
- `step50 = 2.308752 / 0.194434 / 2.620212 / 0.312178`
- `step100 = 2.236292 / 0.19992 / 2.458823 / 0.47269`
- `step150 = 2.178446 / 0.226566 / 1.939391 / 0.370093`
- `step200 = 2.137537 / 0.235312 / 2.00519 / 0.422542`

## 与 `D79` 的关键 final 对比
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`
- `D81 = 2.137537 / 0.235312 / 2.00519 / 0.422542`

`D81 - D79`:
- validation `-0.000869`
- special `+0.003318`
- `e_evt` `-0.165104`
- `z_art` `-0.046887`

解释:
- `D81` 只有一个很小的 validation 改善
- 但它同时回吐了:
  - special
  - `e_evt`
  - `z_art`
- 所以它不是:
  - `D79 + z_art restore`

更准确地说:
- 它是一个“为了极小 validation 改善，
  付出明显 control 回吐”的负结果

## 与 `D76` 的位置关系
`D81 vs D76`:
- validation `+0.029601`
- special `-0.011243`
- `e_evt` `+0.067424`
- `z_art` `-0.002109`

解释:
- 它甚至没有把 `z_art` 拉回到 `D76` 之上
- 所以它连“validation 税版的 `z_art` restore 近邻”都谈不上

## checkpoint 形状也没有打开新口子
`D81` 的 checkpoint 里:
- `step100`
  的确出现了全实验最高 `z_art = 0.47269`
- 但同点同时带着:
  - validation `2.236292`
  - special `0.19992`

解释:
- 这不是可用 late-stop
- 更像是:
  - 中段把 control 撑得更高
  - 但整体验证与 special 形状更粗糙

所以这轮不需要把 `D81` 再升格成 checkpoint-option family

## full long-horizon route 的决定性结果
把 `D81` 并入 full route 后，
所有角色都保持不变:

- validation = `D76`
- special = `D79`
- `zero_e_evt = D79`
- `zero_z_art = D33`
- minimax = `D33`

selector(`budget=0.05`) 继续给出:
- `selected_policy = default_minimax`
- `selected_anchor = D33`

derived thresholds 也完全不变:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.03047`
- `best_e_evt_floor = 2.170294`
- `best_z_art_floor = 0.710849`

这说明:
- `D81` 没有碰到任何 route-level leader
- 它连 `D79` 的:
  - special
  - `e_evt`
  位置都没有碰到

## 当前阶段正式判断
1. `D81` 是明确负结果。
2. 在 `D79` 骨架上，把 `z_art_influence_aux` 显式 retarget 到 late `micro_pause_none_singleton_strict` pool，并不能补回 `z_art`。
3. 更重要的是，这个负结果发生在机制已真实激活的前提下，因此不能再把问题解释成“只是没打中样本”。
4. 当前 long-horizon 结构继续维持:
   - `D76 = validation`
   - `D79 = special + e_evt`
   - `D33 = minimax + z_art`

## 先说人话
- 这轮把“把 explicit `z_art` influence 直接转到当前 late pool”这条猜想也排干净了。
- 现在更准确的收束不是:
  - `D79` 还差一个更对口的 influence pool
- 而是:
  - 当前 `D79` 的剩余 `z_art` 缺口，
    不是靠 `z_art_influence_aux` 的 late-pool retarget 就能补齐

## 下一步建议
1. 停止继续扩:
   - `z_art_influence_aux` 的 late-pool retarget
   - 或其近邻 coverage sweep
2. `D79` 继续保留为当前 long-horizon 的 `special + e_evt` leader。
3. 若主线还要追 `z_art`，下一个更高信息量的问题应改成:
   - 是否存在比 `teacher_consistency` 与 `z_art_influence_aux` 都更外层的 `z_art` restoration 机制

## 产物
- 配置:
  - `configs/offline_mvp_train_d81_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_zartretarget_200step_smallscale_seeded_shuffle.json`
- full long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_default_minimax/`
