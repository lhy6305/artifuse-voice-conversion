# 121. round1.1 `D76 / D75 family matched long horizon probe` 报告

## 背景
- `D75` 已经把 `D70 family` 的 matched20 shadow 代表点推到一个更清楚的单点:
  - validation 几乎不变
  - special 更好
  - `e_evt` 更好
  - `z_art` 不回吐
- 但按当前 horizon policy：
  - `20/30 step` 只回答 quick-screen / early-horizon 问题
  - 若要判断这条 family 是否只是 early advantage，
    需要补 matched long horizon(`200+`)

所以本轮不再扩新 supervision family，
只做最小长视野外推：
- 保持 `D75` 的 supervision 结构
- 只把训练窗口与 late phase 生效范围拉长到 `200 step`

## 本轮设计
### `D76`
- 配置:
  - `configs/offline_mvp_train_d76_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration`
- 设计原则:
  - 完整继承 `D75`
  - 不新增新 pool / 新 loss / 新 proxy principle
  - 只做:
    - `num_steps: 20 -> 200`
    - `validation_interval: 10 -> 50`
    - `checkpoint_interval: 10 -> 50`
    - late teacher phase `active_until_step: 20 -> 200`
    - late targeted sampler `active_until_step: 20 -> 200`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200 step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并新增纯 `200-step` 同 horizon route 产物:
  - `anchor_route_analysis`
  - `anchor_route_selection`
  - `final comparison`
  - `route recap`

## 指标口径
- 本报告统一使用:
  - `target_validation`
  - `special_delta`
  - `zero_e_evt_delta`
  - `zero_z_art_delta`
- 即:
  - validation 为 regular validation loss
  - special 为 `target_special_eval - target_validation`
  - `zero_*` 为 ablation 相对 baseline 的 target loss delta

## `D76` 轨迹
- `step50 = 2.307368 / 0.196444 / 2.548418 / 0.299145`
- `step100 = 2.220376 / 0.21171 / 2.36021 / 0.436968`
- `step150 = 2.145159 / 0.235288 / 2.062923 / 0.44088`
- `step200 = 2.107936 / 0.246555 / 1.937766 / 0.424651`

解释:
- 它仍然表现出和旧长窗 probe 相同的 late dynamics:
  - validation 持续变好
  - special 持续变差
  - `e_evt` floor 持续变弱
- 但它不是简单复刻旧 `D22 / D33 / D59` 轨迹；
  它从一个更强的起点进入同样的 late slide，
  最终把 validation 终点整体压得更低。

## 与旧三条 `200-step` probe 的 final 对比
- `D22 = 2.125622 / 0.238578 / 1.864222 / 0.669467`
- `D33 = 2.122699 / 0.239846 / 1.9703 / 0.710849`
- `D59 = 2.126544 / 0.258922 / 1.927875 / 0.311379`
- `D76 = 2.107936 / 0.246555 / 1.937766 / 0.424651`

### 1. `D76` 明显不是 no-op；它把整组 `200-step` validation 终点向下压了一截
- `D76 vs D33`
  - validation 更好 `-0.014763`
  - special 更差 `+0.006709`
  - `e_evt` 略弱 `-0.032534`
  - `z_art` 更弱 `-0.286198`
- `D76 vs D22`
  - validation 更好 `-0.017686`
  - special 更差 `+0.007977`
  - `e_evt` 更好 `+0.073544`
  - `z_art` 更弱 `-0.244816`

解释:
- `D76` 没保住 `D75` quick-screen 的“special 更好”形状。
- 一旦进入长窗，
  它仍然朝 validation-first 滑。
- 但它滑到的终点比旧 `D22 / D33 / D59` 更强，
  不是旧轨迹的简单复制。

### 2. `D76` 长窗下全面压过 `D59`
- `D76 vs D59`
  - validation 更好 `-0.018608`
  - special 更好 `-0.012367`
  - `e_evt` 更好 `+0.009891`
  - `z_art` 更好 `+0.113272`

解释:
- `D59` 在 long horizon 下继续像原则错位的封口负结果。
- `D76` 至少证明:
  - `D75 family` 不是只在 matched20 才有信号
  - 拉长到 `200 step` 后，它仍保留实质竞争力

### 3. 纯 `200-step` 同 horizon route 已经切到 `D76`
- `anchor_route_analysis(D22 / D33 / D59 / D76)` 给出:
  - validation = `D76`
  - special = `D22`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D76`
- `anchor_route_selection(budget=0.05)` 也给出:
  - `selected_policy = default_minimax`
  - `selected_anchor = D76`
  - `budget_to_minimax_anchor = 0.0`

解释:
- 这次和 `docs/109` 很不一样。
- 上次 `D22 / D33 / D59` 的长窗比较里，
  mixed-horizon 会语义塌缩，
  但纯 long-horizon 内部其实没有更强的新 minimax。
- 本轮纯 `200-step` 内部已经出现新的同 horizon minimax:
  - `D76`

### 4. 这仍然不等于 official fixed handoff 已刷新
- 当前 official quick-screen 仍是:
  - validation = `D71`
  - minimax = `D22`
  - special / `e_evt` / `z_art` = `D33`
- `D76` 当前回答的是:
  - `D75 family` 在 matched long horizon 下站得住
- 它还没有回答:
  - 是否应把 official `20/30 step` handoff 直接换成 `200-step final`

解释:
- 不能把:
  - same-horizon `200-step` minimax = `D76`
  直接翻译成:
  - official default anchor = `D76`
- 这两个制度问题仍然不同。

## 当前阶段正式判断
1. `D75 family` 经过 `200-step` 外推后没有塌掉。
2. `D76` 已经成为:
   - 这条 family 的 long-horizon 代表点
   - 纯 `200-step` 同 horizon 下的新 validation / minimax anchor
3. `D76` 的代价也很明确:
   - special 不再是 quick-screen 时的强项
   - `z_art` floor 仍明显低于 `D33`
4. 因此当前更准确的表述是:
   - `D75` 赢得了 matched20 shadow
   - `D76` 赢得了 pure long-horizon minimax
   - official fixed handoff 仍保持旧 quick-screen 口径

## 下一步
1. 不要把 `D76 step200` 直接混写成新的 official default。
2. 当前更高信息量的后续动作是:
   - 做 `D76` 的 checkpoint-selected late-stop 复核
   - 或把 `D76` 与 official quick-screen anchor 做更明确的 matched-horizon 对照
3. 若后续要真正讨论 official 刷新，
   需要继续坚持:
   - quick-screen 问题
   - matched20 shadow 问题
   - matched long horizon 问题
   三者分开表述

## 产物
- 训练:
  - `reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/`
- 评估:
  - `reports/eval/offline_mvp_ablations_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/`
  - `reports/eval/offline_mvp_special_eval_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/`
  - `reports/eval/offline_mvp_checkpoint_series_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/`
  - `reports/eval/offline_mvp_special_eval_series_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/`
- 同 horizon `200-step` route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_default_minimax/`
