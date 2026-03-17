# 118. round1.1 `D72-D73 / D70 late-restore transfer` 报告

## 背景
- `D70` 已经证明:
  - 更强 checkpoint backbone
  - 可以显著削掉 `D60` 的 validation tax
- 但它相对 `D68 / D69` 仍明显缺:
  - special push
  - `e_evt / z_art` control
- 所以上一轮确定的下一手是:
  - 不继续沿 `D71` 那条 validation-first 方向外推
  - 而是把 `D68 / D69` 的 late teacher source / handoff 旋钮迁移到 `D70`

## 这轮设计
### `D72`
- 配置:
  - `configs/offline_mvp_train_d72_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 完整继承 `D70`
  - 只把 late teacher source 从:
    - `D29 step10`
    - 改成 `D22 step30`

### `D73`
- 配置:
  - `configs/offline_mvp_train_d73_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22like_latehandoff_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 在 `D72` 基础上进一步把 late handoff shape 调成更 `D22-like`
  - 具体为:
    - late `fused_hidden_weight: 0.05 -> 0.0`
    - late teacher pool:
      - `micro_pause_none_singleton_strict -> challenge_proxy_core`

## 运行补充
- 本轮一开始把 `D72 / D73` 的 `init-experiment` 并行执行，
  触发了 experiment id 抢号:
  - `D72` 和第一次 `D73` 都拿到了 `EXP-...027`
- 后续已处理为:
  - 保留正确的 `D72 = EXP-...027`
  - 重新顺序生成 `D73 = EXP-...029`
  - 删除错误的 `027-d73` 占位记录

## 完整执行链
- `D72 / D73` 均已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - 正式训练
  - `evaluate-offline-mvp-ablations`
  - `evaluate-offline-mvp-special-eval`
  - `evaluate-offline-mvp-checkpoint-series`
  - `evaluate-offline-mvp-special-eval-series`
- 并已同步并入:
  - official quick-screen route-analysis / selector / final comparison
  - matched20 shadow bundle

## final 结果
- `D70 = 2.399035 / 0.168635 / 2.941607 / 0.365565`
- `D72 = 2.399071 / 0.167648 / 2.957 / 0.364989`
- `D73 = 2.398942 / 0.168183 / 2.953266 / 0.364179`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## 关键结论
### 1. `D72 / D73 step10` 与 `D70` 完全同轨
- 三条线的 `step10` 都是:
  - `2.442652 / 0.171144 / 2.985898?` 这里不做单独 route 解释
  - 更重要的是 `target_validation_loss_total` 与 `special delta` 完全相同
- 解释:
  - 这轮新增信息全部来自 late `step11-20`
  - 不是 init checkpoint 或前半段训练路径差异

### 2. `D72` 是 `D70` 的 epsilon 级改良，而不是新的 regime
- `D72 vs D70`
  - validation 略差 `+0.000036`
  - special 略好 `-0.000987`
  - `zero_e_evt` 略好 `+0.015393`
  - `zero_z_art` 略差 `-0.000576`

解释:
- 把 late teacher source 从 `D29 step10` 改回 `D22 step30`，
  在 `D70` backbone 上确实不再是 no-op
- 但改善量级仍只有 epsilon 级
- 更合理的解释是:
  - `D72` 在 `D70` 盆地里做了一个轻微再平衡
  - 而不是打开新路线

### 3. `D73` 同样只是在 `D70` 盆地里做另一种 epsilon 级再平衡
- `D73 vs D70`
  - validation 略好 `-0.000093`
  - special 略好 `-0.000452`
  - `zero_e_evt` 略好 `+0.011659`
  - `zero_z_art` 略差 `-0.001386`

解释:
- 把 late handoff shape 进一步调成 `D22-like`，
  也没有把这条线推入新的 regime
- `D73` 更像:
  - 用极小幅的 validation / special / `e_evt`
    交换一点 `z_art`

### 4. official quick-screen 口径没有被 `D72 / D73` 改写
- official route-analysis(`D22 / D29 / D33 / D60 / D68 / D69 / D70 / D71 / D72 / D73`) 继续给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D22`
- official selector(`budget=0.05`) 也继续保持:
  - `validation_strict = D71`

解释:
- `D72 / D73` 没有改变上一轮对 official quick-screen 的制度判断
- 它们只是证明:
  - 在 `D70` 盆地里
  - `D68 / D69` 那类 late 恢复旋钮依然只有弱杠杆

### 5. matched20 shadow minimax 从 `D70` epsilon 级切到 `D72`
- shadow route-analysis(`D29 / D22-step20 / D33 / D60 / D68 / D69 / D70 / D71 / D72 / D73`) 给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D72`
- 新阈值:
  - `budget_to_minimax_anchor = 0.058874`
- selector:
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D72`

解释:
- 这不是 shadow 主线从 `D70 family` 跳到新 family
- 更准确地说:
  - shadow minimax 现在收缩到 `D70 / D72 / D73` 这一个窄盆地里
  - 其中 `D72` 以极小优势暂时领先

## 当前阶段正式判断
1. `D72 / D73` 都提供了真实信息，
   但信息量属于 epsilon 级再平衡，不是新路线。
2. `D70` family 的 late-restore 轴目前已经基本跑清:
   - `D72` 更偏 `special + e_evt`
   - `D73` 更偏 `validation + special`
   - 但三者量级都非常接近
3. official fixed handoff 仍不刷新。
4. shadow minimax 当前可更精确地表述为:
   - 已稳定收缩到 `D70 family`
   - 但 family 内部仍在 `D70 / D72 / D73` 间做 epsilon 级换人

## 下一步
1. 暂停继续做:
   - `D70 family` 的 late teacher source / handoff 小变体
2. 当前更值得优先推进的是:
   - 先把这条 family 视为已收缩盆地
   - 再决定是否需要更强一级的 control restoration
   - 或进入 `matched long horizon(200+)` 前的最后一轮确认
3. 如果下一手仍要沿这条 family 推，
   更合理的方向应是:
   - 不再做纯 handoff 旋钮
   - 而是更明确的 control-target restoration 设计
4. 若准备挑战 official fixed handoff，
   当前更合理的候选 family 应写成:
   - `D70 / D72 / D73`
   - 而不是只盯单点

## 产物
- official quick-screen:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_default_minimax/`
- matched20 shadow:
  - `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/`
