# 137. round1.1 `D85 / outer punctuation 200-step verification` 报告

## 背景
- `D84` 已经证明:
  - outer punctuation 这条题不是假 gate
  - 它能把 matched20 shadow representative 从 `D75` 推到 `D84`
- 但这还没有回答更关键的问题:
  - 把同一 family 拉到 `200-step` 后，
    它到底会:
    - 继续保留新的 joint-point 形状
    - 还是重新塌回旧 long-horizon 路线

因此本轮只做最小长窗外推:
- 保留 `D84` 的 outer punctuation supervision 结构
- 不新增新 proxy principle
- 只把训练窗口与 late phase 一起拉到 `200-step`

## 本轮设计
### `D85`
- 配置:
  - `configs/offline_mvp_train_d85_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration`
- 设计原则:
  - 继承 `D84`
  - 保持:
    - late `teacher_consistency.weight = 0.20`
    - primary strict singleton sampler
    - `secondary_sampling -> micro_singleton_anypunct_expansion`
    - `punctuation_profile_aux.pool_memberships = ['micro_singleton_anypunct_expansion']`
  - 只做:
    - `num_steps: 20 -> 200`
    - `validation_interval: 50`
    - `checkpoint_interval: 50`
    - late teacher / targeted sampling phase 拉长到 step `200`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并新增两套 route 产物:
  - minimal family route:
    - `D22 / D33 / D59 / D76 / D85`
  - full long-horizon route:
    - `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85`

## 训练入口补坑
- 本轮还暴露出一个工程问题:
  - 正式训练结束后，
    `EXP-20260316-041` 的 `train_plan`、checkpoints、logs 都已写出
  - 但 experiment metrics 文件仍保持 `initialized`
- 根因:
  - `src/v5vc/train_entry.py`
    的 `update_experiment_metrics(...)`
    原先只查:
    - `EXP-20260316-041.metrics.json`
  - 而 `init-experiment` 实际生成的是:
    - `EXP-20260316-041-<slug>.metrics.json`
- 已修复:
  - 新增 `resolve_experiment_metrics_path(...)`
  - 支持:
    - 精确短名匹配
    - 唯一 slugged 文件匹配
- 随后已直接基于现有 `train_plan`
  对 `EXP-20260316-041` 做回填，
  无需重训。

## 指标口径
- 本报告继续使用:
  - `target_validation`
  - `special_delta`
  - `zero_e_evt_delta`
  - `zero_z_art_delta`
- shorthand final 仍记为:
  - `ablation baseline target_validation / special_delta / zero_e_evt / zero_z_art`
- route 判断则使用 route 产物中的 `target_validation_loss_total`

## `D85` 轨迹
- shorthand final:
  - `D85 = 2.129306 / 0.231295 / 2.027351 / 0.433882`
- route validation 列:
  - `2.133474`

- `step50 = 2.310868 / 0.185493 / 2.582539 / 0.311158`
- `step100 = 2.213002 / 0.204854 / 2.291469 / 0.448169`
- `step150 = 2.161399 / 0.223913 / 2.066232 / 0.424634`
- `step200 = 2.133474 / 0.231295 / 2.027351 / 0.433882`

解释:
- 这条轨迹仍然符合 long-horizon 的典型方向:
  - validation 继续改善
  - special 持续回吐
  - `e_evt` floor 持续变弱
- 但它没有直接塌成旧 `D76` 形状；
  step200 仍保留:
  - 比 `D76` 更好的 special
  - 更好的 `e_evt`
  - 略更好的 `z_art`

## 与 `D76` 的直接对比
- route 级差值:
  - validation `+0.025538`
  - special `-0.015260`
  - `zero_e_evt` `+0.089585`
  - `zero_z_art` `+0.009231`

解释:
- `D85` 明确不是 validation winner。
- 但它也不是“special 好一点、其余全回吐”的弱 tradeoff。
- 它是在支付一段 validation tax 的同时，
  把 `special / e_evt / z_art` 三项一起往更平衡的方向推了一步。

## minimal family route 结果
- `anchor_route_analysis(D22 / D33 / D59 / D76 / D85)` 给出:
  - validation = `D76`
  - special = `D85`
  - `zero_e_evt = D85`
  - `zero_z_art = D33`
  - minimax = `D33`
- selector 同时给出:
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.025538`
  - 若 `special_priority = true` 且 budget 足够，
    选中的就是:
    - `D85`

解释:
- 这说明 `D84 family` 拉长到 `200-step` 后并没有失真到完全无意义。
- 至少在这条 family 自己的 pure long-horizon 子集合里，
  `D85` 已经成为:
  - special leader
  - `e_evt` leader

## full long-horizon route 结果
- 并入当前全量 long-horizon 集合后，正式四角色仍保持:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art + default_minimax = D33`
- 新 selector 阈值也没有被改写:
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.040968`

解释:
- `D85` 在 minimal family 内能赢，
  不代表它足以改写 full route。
- 一旦把 `D82 / D79` 这些更强的 long-horizon 对手放回集合，
  `D85` 仍然只能作为一个可信 tradeoff 点，
  还不能成为正式角色。

## 当前阶段正式判断
1. `D84 / D85 family` 已经证明自己不是 matched20-only 的局部幻觉。
2. `D85` 是这条 family 在 pure `200-step` 下的有效 tradeoff 点。
3. 但 `D85` 还没有改写当前 full long-horizon 四角色:
   - `D76 / D82 / D79 / D33`
4. 因此更准确的制度口径是:
   - `D85` 可以写成 family-level long-horizon representative
   - 不能写成新的 full long-horizon special / minimax anchor

## 下一步
1. 不要把 minimal family 中的 `D85 = special / e_evt` 混写成 full route 刷新。
2. 若继续推进这条题，真正有信息量的问题应是:
   - 能否在保留当前 special / `e_evt` 形状时，
     把 `z_art` floor 拉回到更接近 `D33`
   - 或把 validation tax 再压低
3. 若没有新的更外层 restoration 机制，
   就不应再优先做:
   - 同 family 的小权重 sweep
   - 或 outer punctuation 的近邻变体堆叠

## 产物
- 训练:
  - `reports/training/offline_mvp/EXP-20260316-041.train_plan.json`
- 评估:
  - `reports/eval/offline_mvp_ablations_d85_exp20260316_041/`
  - `reports/eval/offline_mvp_special_eval_d85_exp20260316_041/`
  - `reports/eval/offline_mvp_checkpoint_series_d85_exp20260316_041/`
  - `reports/eval/offline_mvp_special_eval_series_d85_exp20260316_041/`
- minimal family route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d85/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d85_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d85_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d85_default_minimax/`
- full long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_default_minimax/`
