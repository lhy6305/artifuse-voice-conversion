# 128. round1.1 `D79 / D76 near-neighbor teacher-weight probe` 报告

## 背景
`D78` 已经把一个重要问题回答清楚:

- 若在 `D76` 骨架里直接把 late teacher source 改成 `D33 step10`
- 虽然能补回一部分 `special / z_art`
- 但会把 pure long-horizon minimax 重新拉回 `D33`

因此下一步不再碰:
- late teacher source

而是改问:
- 在完全保留 `D22 late` 骨架的前提下，
  仅增强 late teacher 推力，
  是否能补回 `special / e_evt / z_art`
  而不再触发 `D33 source-restore` 那种强回退

## 本轮设计
### `D79`
- 配置:
  - `configs/offline_mvp_train_d79_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_boost_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-035-offline-mvp-d79-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-boost-200step-calibration`

设计原则:
- 完整继承 `D76`
- 不改 horizon
- 不改 late teacher source
- 不改 sampler
- 不改 `fused_hidden_weight`
- 唯一变量:
  - late `step11-200` `teacher_consistency.weight`
    - `0.15 -> 0.20`

它回答的问题非常纯:
- `D22 late` 这条线如果只加强 teacher force，
  能不能补回 control，
  且不需要回到 `D33 teacher source`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并已并入包含 `D78` 在内的 full long-horizon route:
  - `anchor_route_analysis(D22 / D33 / D59 / D76 / D77 / D78 / D79)`
  - `anchor_route_selection`
  - `final comparison`
  - `route recap`

## 指标口径
- validation
- special delta
- `zero_e_evt_delta`
- `zero_z_art_delta`

即:
- validation = regular validation loss
- special = `target_special_eval - target_validation`
- `zero_*` = ablation 相对 baseline 的 target loss delta

## `D79` 轨迹
- `step50 = 2.309448 / 0.193405 / 2.558445 / 0.310273`
- `step100 = 2.226 / 0.209555 / 2.301442 / 0.424609`
- `step150 = 2.163048 / 0.227855 / 2.255625 / 0.471536`
- `step200 = 2.138406 / 0.231994 / 2.170294 / 0.469429`

解释:
- `D79` 仍有典型 late slide:
  - validation 持续变好
  - special 持续变差
- 但和 `D76` 相比，
  它在整个 long window 都把:
  - `e_evt`
  - `z_art`
  整体抬高了一层

尤其是:
- `e_evt` 在 `step200` 仍显著高于 `D76`

这说明:
- 在不改 teacher source 的情况下，
  late teacher strength 仍然是有效杠杆

## 与 `D76` 的关键 final 对比
- `D76 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`

`D79 - D76`:
- validation `+0.03047`
- special `-0.014561`
- `e_evt` `+0.232528`
- `z_art` `+0.044778`

解释:
- 这是一个比 `D78` 更干净的结论:
  - 不需要切换 teacher source
  - 也能把 `special + e_evt` 一起显著拉回来
- 但它也清楚表明:
  - 当前主要瓶颈仍是 validation 税
  - `z_art` 虽有回补，
    但量级明显小于 `e_evt`

所以它不是:
- `D76` 的新 default

更准确地说它是:
- `D76` 骨架里的 special / `e_evt` 强化版近邻

## 与 `D33 / D78` 的位置关系
### 1. `D79` 没有打赢 `D33`
`D79 vs D33`:
- validation `+0.015707`
- special `-0.007852`
- `e_evt` `+0.199994`
- `z_art` `-0.24142`

解释:
- `D79` 的优势很鲜明:
  - special 更好
  - `e_evt` 更好
- 但它仍然被:
  - `z_art`
  卡住
- 所以 default/minimax 仍不会从 `D33` 手里切走

### 2. `D79` 相对 `D78` 更像可用近邻
`D79 vs D78`:
- validation `-0.002911`
- special `-0.000362`
- `e_evt` `+0.348263`
- `z_art` `-0.045281`

解释:
- `D79` 基本同时压过 `D78` 的:
  - validation
  - special
  - `e_evt`
- 唯一回吐的是:
  - `z_art`

这说明:
- 如果目标是不再用 `D33 source-restore`，
  而是在 `D22 late` 骨架内找更稳的近邻，
  `D79` 比 `D78` 更像有效方向

## full long-horizon route 的决定性结果
当把 `D79` 并入:
- `D22 / D33 / D59 / D76 / D77 / D78`

之后，
route 结果变成:
- validation = `D76`
- special = `D79`
- `zero_e_evt = D79`
- `zero_z_art = D33`
- minimax = `D33`

selector(`budget=0.05`) 继续给出:
- `selected_policy = default_minimax`
- `selected_anchor = D33`

derived thresholds:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.03047`
- `best_e_evt_floor = 2.170294`
- `best_z_art_floor = 0.710849`

解释:
- `D79` 没有把 minimax 从 `D33` 切走
- 但它把 special-push 代表点从:
  - `D78`
  切成了:
  - `D79`
- 更重要的是:
  - 它把最强 `e_evt` floor 也一起拿走了

也就是说，
当前更准确的制度角色是:
- `D76 = validation-first anchor`
- `D33 = default/minimax + z_art anchor`
- `D79 = special + e_evt anchor`

## 当前阶段正式判断
1. 在 `D76` 骨架里，提高 late teacher 总权重是有效杠杆。
2. `D79` 比 `D78` 更像可继续挖的近邻方向。
3. 但当前 pure long-horizon default/minimax 仍然是:
   - `D33`
4. `D79` 最清楚暴露出的剩余缺口是:
   - `z_art` 仍不够高，
     所以它只能做 special / `e_evt` leader，
     还不能接 default/minimax

## 先说人话
- `D79` 这轮是有进展的。
- 它说明:
  - 不改 teacher source，
    只加强 `D22 late` 的 teacher force，
    也能把 `special + e_evt` 拉回来
- 但也正因为它把问题变得更清楚，
  现在剩下的主缺口几乎只剩:
  - `z_art`

## 下一步建议
1. 暂停继续扩:
   - `D33 late source restore`
2. 若继续沿 `D79` 这条线推进，
   更高信息量的问题应改成:
   - 能否在基本保留 `D79` 的 `special + e_evt` 收益下，
     再补一点 `z_art`
3. 更具体地说，
   下一轮最值得试的是:
   - 仍保留 `D22 late`
   - 仍保留 teacher weight lift
   - 但改成更轻量的 `z_art` 定向 restoration，
     而不是再次切 teacher source

## 产物
- 配置:
  - `configs/offline_mvp_train_d79_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_boost_200step_smallscale_seeded_shuffle.json`
- 训练:
  - `reports/training/offline_mvp/`
- 评估:
  - `reports/eval/offline_mvp_ablations/`
  - `reports/eval/offline_mvp_special_eval/`
  - `reports/eval/offline_mvp_checkpoint_series/`
  - `reports/eval/offline_mvp_special_eval_series/`
- full long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_default_minimax/`
