# 127. round1.1 `D78 / D76 near-neighbor control restore probe` 报告

## 背景
上一轮已经把主问题收束到:

- `D76`:
  - pure `200-step` long-horizon validation / minimax anchor
- `D77`:
  - official validation-family 的 matched long-horizon representative

因此当前更高信息量的问题不再是:
- 继续扩 `D29-init` family

而是:
- 是否存在一个 `D76` 近邻，
  能在基本不丢 validation 的前提下，
  补回一部分 `special / e_evt / z_art`

## 本轮设计
### `D78`
- 配置:
  - `configs/offline_mvp_train_d78_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33late_late_fusedhidden_boost_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-034-offline-mvp-d78-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d33late-late-fusedhidden-boost-200step-calibration`

设计原则:
- 完整继承 `D76`
- 不改 horizon
- 不改 sampler
- 不改 late fused-hidden boost
- 只把 late `step11-200` teacher source 从:
  - `D22 step30`
  - 改成 `D33 step10`

也就是把:
- `D75/D76` 的 `D22 late + fused_hidden_weight=0.08`

改成:
- `D33 late + fused_hidden_weight=0.08`

它回答的问题很纯:
- `D74` 型 control teacher restore
  在 `D76` 的长窗骨架里，
  能否补回 control，
  且不把 validation 税推得过大

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并已并入 pure long-horizon route:
  - `anchor_route_analysis(D22 / D33 / D59 / D76 / D77 / D78)`
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

## `D78` 轨迹
- `step50 = 2.332573 / 0.177148 / 2.673272 / 0.369034`
- `step100 = 2.257266 / 0.189461 / 2.428461 / 0.530758`
- `step150 = 2.172056 / 0.222927 / 2.018289 / 0.538029`
- `step200 = 2.141317 / 0.232356 / 1.822031 / 0.51471`

解释:
- `D78` 的 late dynamics 仍然是:
  - validation 持续变好
  - special 持续变差
- 但与 `D76` 不同的是:
  - `z_art` 在整个 late window 都明显更高
  - `validation` 终点也被显著抬高

这说明:
- late `D33 teacher` 不是挂空
- 它在 long horizon 下确实在持续拉 control
- 但代价不是 epsilon 级，
  而是足以改变 route 结构的 validation 税

## 与 `D76` 的关键 final 对比
- `D76 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- `D78 = 2.141317 / 0.232356 / 1.822031 / 0.51471`

`D78 - D76`:
- validation `+0.033381`
- special `-0.014199`
- `e_evt` `-0.115735`
- `z_art` `+0.090059`

解释:
- `D78` 确实补回了:
  - special
  - `z_art`
- 但它没有补回:
  - `e_evt`
- 同时 validation 税已经大到:
  - 不能再被写成“基本不丢 validation”

所以它不是:
- `D76 + control free lunch`

更准确地说它是:
- 用明显 validation 税，
  去换更强的 special / `z_art` 形状

## 与 `D22 / D33 / D77` 的位置关系
### 1. `D78` 没有压过 `D33`
`D78 vs D33`:
- validation `+0.018618`
- special `-0.00749`
- `e_evt` `-0.148269`
- `z_art` `-0.196139`

解释:
- `D78` 虽然是这轮 special leader，
  但它并没有成为新的 joint control winner
- 在 default/minimax 问题上，
  它反而会把 route 重新推回 `D33`

### 2. `D78` 比 `D22` 更偏 special-only，且不再保住 `z_art`
`D78 vs D22`:
- validation `+0.015695`
- special `-0.006222`
- `e_evt` `-0.042191`
- `z_art` `-0.154757`

解释:
- `D78` 的优势只剩:
  - special 更低
- 但它没有形成对 `D22` 的完整替代

### 3. `D78` 也不是 `D77` 的升级版
`D78 vs D77`:
- validation `+0.031248`
- special `-0.012923`
- `e_evt` `-0.010752`
- `z_art` `+0.049284`

解释:
- `D78` 的形状更像:
  - 明确偏 special / `z_art`
- 不是更稳的 long-horizon default

## 纯 `200-step` route 的决定性结果
当把 `D78` 并入:
- `D22 / D33 / D59 / D76 / D77`

之后，
pure long-horizon route 改写为:
- validation = `D76`
- special = `D78`
- `zero_e_evt / zero_z_art = D33`
- minimax = `D33`

selector(`budget=0.05`) 给出:
- `selected_policy = default_minimax`
- `selected_anchor = D33`

derived thresholds:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.033381`

解释:
- 这轮最重要的结果不是:
  - `D78` 成为新 default
- 而是:
  - 只要把这种 late `D33 teacher restore` 近邻并入候选池，
    pure long-horizon minimax 就会从 `D76` 切回 `D33`

因此 `D78` 回答出的不是:
- “`D76` 已经补 control 成功”

而是:
- “这种 control restore 方向会把 route 重新拉回 old control anchor”

## 当前阶段正式判断
1. `D78` 证明 late `D33 teacher` 在 `200-step` 下仍然是强控制杠杆。
2. 但它不是 `D76` 的无痛升级版。
3. 当前更准确的制度角色是:
   - `D76 = long-horizon validation-first default`
   - `D78 = long-horizon special-oriented probe`
   - `D33 = 被 `D78` 重新显化出来的 minimax/control anchor`
4. 这意味着:
   - 以 `D33 teacher restore` 为核心的 `D76` 近邻，
     当前不值得继续做同方向小修小补

## 先说人话
- 这轮不是白跑。
- 它把问题回答得更清楚了:
  - `D76` 想补 control，
    不能直接把 late teacher 拉回 `D33`
- 这么做虽然能让 `special / z_art` 好看一些，
  但代价已经大到:
  - default/minimax 会直接退回 `D33`

## 下一步建议
1. 暂停继续扩:
   - `late D33 teacher restore`
   - 或其同向小变体
2. 若继续找 `D76` 近邻，
   应优先尝试:
   - 不改 late teacher source
   - 只在 `D76` 的现有 `D22 late` 骨架内，
     做更弱的 control-target restoration
3. 更准确地说，
   下一轮值得问的是:
   - 能否在不触发 `D33` 式 minimax 回退的前提下，
     只补一小段 `z_art / e_evt`

## 产物
- 配置:
  - `configs/offline_mvp_train_d78_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33late_late_fusedhidden_boost_200step_smallscale_seeded_shuffle.json`
- 训练:
  - `reports/training/offline_mvp/`
- 评估:
  - `reports/eval/offline_mvp_ablations/`
  - `reports/eval/offline_mvp_special_eval/`
  - `reports/eval/offline_mvp_checkpoint_series/`
  - `reports/eval/offline_mvp_special_eval_series/`
- pure long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_default_minimax/`
