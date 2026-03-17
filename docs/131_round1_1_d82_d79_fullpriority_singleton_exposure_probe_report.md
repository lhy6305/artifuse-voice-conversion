# 131. round1.1 `D82 / D79 full-priority singleton exposure probe` 报告

## 背景
`D80` 与 `D81` 已把两条更内层的 `z_art` 补法排干净:

- `teacher_consistency.z_art_weight` 小幅抬高
- `z_art_influence_aux` late-pool retarget

因此这轮不再改:

- teacher source
- teacher total weight
- teacher per-head weight
- explicit `z_art_influence` 机制

而是改问一个更外层的问题:

- 如果在 `D79` 骨架上，
  不碰 teacher 内部项，
  只把 late `micro_pause_none_singleton_strict`
  的 targeted sampling 曝光强度继续抬高，
- 能不能把剩余 `z_art` 缺口补回来

先说人话:
- 这轮不是继续拧老师怎么教。
- 是直接让 late 阶段更大比例地“看到”当前最贴近 challenge 的 singleton proxy cohort，
  看看问题是不是其实卡在 cohort 曝光不够强。

## 本轮设计
### `D82`
- 配置:
  - `configs/offline_mvp_train_d82_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_fullpriority_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-038-offline-mvp-d82-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-teacherweight-fullpriority-200step-calibration`

设计原则:
- 完整继承 `D79`
- 保留:
  - `D22 late`
  - late `teacher_consistency.weight = 0.20`
  - `singleton_sparse_proxy_aux`
  - 现有 late teacher gate
- 唯一变量:
  - late `step11-200`
    `targeted_sampling.priority_ratio`
    - `0.75 -> 1.0`

它回答的问题非常纯:
- 当前 `D79` 的剩余缺口，
  是否主要只是:
  - late singleton proxy cohort 曝光还不够强

## 执行链
- 已完成:
  - `init-experiment --route-selection`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
  - full long-horizon:
    - `anchor_route_analysis`
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

## `D82` 结果
- `step50 = 2.321273 / 0.167559 / 2.796732 / 0.364517`
- `step100 = 2.235013 / 0.197046 / 2.378748 / 0.440124`
- `step150 = 2.191981 / 0.210916 / 2.313778 / 0.470433`
- `step200 = 2.148904 / 0.218229 / 2.126457 / 0.436209`

## 与 `D79` 的关键 final 对比
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`
- `D82 = 2.148904 / 0.218229 / 2.126457 / 0.436209`

`D82 - D79`:
- validation `+0.010498`
- special `-0.013765`
- `e_evt` `-0.043837`
- `z_art` `-0.03322`

解释:
- `D82` 不是纯负结果，
  因为它确实把 special 再往前推了一段
- 但它也非常清楚地不是:
  - `D79 + z_art restore`

更准确地说:
- 它是一个
  - 用 validation 税
  - 换更低 special
  - 同时回吐 `e_evt` 与 `z_art`
  的 special-only 近邻

## checkpoint 形状也没有打开 `z_art` 新口子
`D82` 的 checkpoint 里:
- `step150`
  的确出现了全实验最高
  - `z_art = 0.470433`
- 但同点同时带着:
  - validation `2.191981`
  - special `0.210916`

解释:
- 这不是可用的 late-stop
- 更像是:
  - 继续抬高 singleton 曝光后，
    中段 special / control 被一起推起来
  - 但 validation 税显著变大

所以这轮不需要把 `D82` 升格成 checkpoint-option family

## full long-horizon route 的决定性结果
把 `D82` 并入 full route 后，
结构更新为:

- validation = `D76`
- special = `D82`
- `zero_e_evt = D79`
- `zero_z_art = D33`
- minimax = `D33`

selector(`budget=0.05`) 继续给出:
- `selected_policy = default_minimax`
- `selected_anchor = D33`

derived thresholds:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.040968`
- `best_e_evt_floor = 2.170294`
- `best_z_art_floor = 0.710849`

解释:
- `D82` 改写了 special leader，
  但没有改写:
  - default/minimax
  - best `e_evt` floor
  - best `z_art` floor
- 更重要的是:
  - 它把 special 预算门槛从 `0.03047`
    推高到 `0.040968`
  - 说明这条 full-priority 方向的代价比 `D79` 更重

## 当前阶段正式判断
1. `D82` 不是 no-op。
2. 在 `D79` 骨架上，把 late singleton targeted sampling 从 `0.75` 提到 `1.0`，确实是一个真实 special 杠杆。
3. 但它不能补回 `z_art`，反而会同时回吐:
   - validation
   - `e_evt`
   - `z_art`
4. 这说明当前 `D79` 的剩余 `z_art` 缺口，
   不能继续解释成:
   - singleton proxy cohort 曝光还不够强
5. 当前更准确的 long-horizon 结构变为:
   - `D76 = validation`
   - `D82 = special`
   - `D79 = e_evt`
   - `D33 = minimax + z_art`

## 先说人话
- 这轮把“是不是 singleton late batch 还不够偏、再偏一点就能把 `z_art` 补回来”这条猜想也排清了。
- 现在更准确的收束不是:
  - 只要继续强化当前 singleton cohort 的 late exposure 就行
- 而是:
  - 当前这条 cohort / proxy principle，
    更像是在往 special-only 方向继续推，
    不是在补 `z_art`

## 下一步建议
1. 停止继续扩:
   - late singleton `priority_ratio` 上调
   - 或同类 full-priority / stronger-exposure sweep
2. 若继续追 `z_art`，
   更高信息量的问题应改成:
   - 是否需要一个比“强化当前 singleton cohort 曝光”更换代价更大的新 proxy principle
   - 或一个真正直接面向 `z_art` 的更外层 supervision 机制
3. 当前主线口径应更新为:
   - `D82` 保留为 special leader
   - `D79` 保留为 `e_evt` leader
   - `D33` 继续保留为 `default_minimax + z_art` anchor

## 产物
- 配置:
  - `configs/offline_mvp_train_d82_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_fullpriority_200step_smallscale_seeded_shuffle.json`
- 训练:
  - `reports/training/offline_mvp/`
- 评估:
  - `reports/eval/offline_mvp_ablations_exp038/`
  - `reports/eval/offline_mvp_special_eval_exp038/`
  - `reports/eval/offline_mvp_checkpoint_series_exp038/`
  - `reports/eval/offline_mvp_special_eval_series_exp038/`
- full long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_default_minimax/`
