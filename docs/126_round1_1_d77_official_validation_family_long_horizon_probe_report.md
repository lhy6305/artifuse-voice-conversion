# 126. round1.1 `D77 official validation-family matched long horizon probe` 报告

## 背景
到上一轮为止，
`D75 / D76 family` 已经完成了 matched20 与 pure long-horizon 两端验证:

- `D75`:
  - 当前 matched20 shadow representative
- `D76`:
  - pure `200-step` long-horizon validation / minimax anchor

但 official quick-screen 当前的 validation-first 默认并不是 `D75 family`，
而是:
- `D71`

也就是说，
如果要判断:
- `D76` 只是“长窗里恰好比旧 trio 强”
- 还是已经实质压过 official validation-family

还缺一个关键对照:
- 把 `D71` 这条 official validation-family 拉到 `200-step`
- 与 `D76` 做同 horizon 直接比较

## 本轮设计
### `D77`
- 配置:
  - `configs/offline_mvp_train_d77_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-033-offline-mvp-d77-round1-1-d29-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-200step-calibration`

设计原则:
- 完整继承 `D71`
- 不新增新 pool / 新 loss / 新 proxy principle
- 只把 `D71` 的 `20-step` horizon 拉长到 `200-step`

具体只改:
- `num_steps: 20 -> 200`
- `validation_interval: 10 -> 50`
- `checkpoint_interval: 10 -> 50`
- late teacher phase `active_until_step: 20 -> 200`
- late targeted sampler `active_until_step: 20 -> 200`

因此 `D77` 回答的问题非常纯:
- official validation-family 在 matched long horizon 下能走到哪里

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
- 并新增 pure long-horizon route 产物:
  - `anchor_route_analysis(D22 / D33 / D59 / D76 / D77)`
  - `anchor_route_selection`
  - `final comparison`
  - `route recap`

## 执行时校正
这轮评估第一次调用时踩到了一个工具口径问题:
- `evaluate-offline-mvp-ablations`
- `evaluate-offline-mvp-special-eval`

如果只传:
- `--experiment-metrics`

而不显式传:
- `--config`

CLI 会退回默认模板 config，
从而把 model 以:
- `text_aux_dim = 3`

实例化，
与本轮 checkpoint 的:
- `text_aux_dim = 13`

发生 shape mismatch。

本轮实际修正方式不是改代码，
而是:
- 对所有 eval / series 命令显式传入 `D77` config

## 指标口径
本报告统一使用:
- validation
- special delta
- `zero_e_evt_delta`
- `zero_z_art_delta`

即:
- validation = regular validation loss
- special = `target_special_eval - target_validation`
- `zero_*` = ablation 相对 baseline 的 target loss delta

## `D77` 轨迹
- `step50 = 2.294811 / 0.192851 / 2.689036 / 0.402836`
- `step100 = 2.19345 / 0.218571 / 2.145994 / 0.460361`
- `step150 = 2.149293 / 0.235859 / 1.736167 / 0.39523`
- `step200 = 2.110069 / 0.245279 / 1.832783 / 0.465426`

解释:
- `D77` 的 late dynamics 和 `D76` 一样，
  仍然是:
  - validation 持续变好
  - special 持续变差
- 但 control 形状不一样:
  - `z_art` 在 `step200` 回升到高于 `step150`
  - `e_evt` 则明显低于 `D76`

这说明 `D77` 更像:
- official validation-family 的 long-horizon 延长版
- 而不是 `D76` 的简单替代

## 与 `D76` 的关键 final 对比
- `D76 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- `D77 = 2.110069 / 0.245279 / 1.832783 / 0.465426`

`D77 - D76`:
- validation `+0.002133`
- special `-0.001276`
- `e_evt` `-0.104983`
- `z_art` `+0.040775`

解释:
- `D77` 确实把 official validation-family 拉到了一个非常接近 `D76` 的长窗点
- 它的 tradeoff 也很清楚:
  - 付出极小 validation 税
  - special 略好
  - `z_art` 略好
  - 但 `e_evt` 明显更弱

因此它不是 no-op，
但也不是对 `D76` 的统治性反超。

## 与旧 long-horizon trio 的位置关系
### 1. `D77` 压过 `D59`
`D77 vs D59`:
- validation 更好 `-0.016475`
- special 更好 `-0.013643`
- `e_evt` 更弱 `-0.095092`
- `z_art` 更好 `+0.154047`

解释:
- `D59` 继续保持明显劣势，
  不是这轮的竞争主轴。

### 2. `D77` 比 `D22 / D33` 更像 validation-family 的长窗延长版
`D77 vs D22`:
- validation 更好 `-0.015553`
- special 更差 `+0.006701`
- `e_evt` 更弱 `-0.031439`
- `z_art` 更弱 `-0.204041`

`D77 vs D33`:
- validation 更好 `-0.01263`
- special 更差 `+0.005433`
- `e_evt` 更弱 `-0.137517`
- `z_art` 更弱 `-0.245423`

解释:
- `D77` 的主要贡献是:
  - 把 official validation-family 的 validation 终点推得更低
- 但它没有保住 `D33` 的 control ceilings，
  也没有形成对 `D76` 的完整反超

## 纯 `200-step` route 的决定性结果
当把 `D77` 并入:
- `D22 / D33 / D59 / D76`

之后，
pure long-horizon route 仍然给出:
- validation = `D76`
- minimax = `D76`
- special = `D22`
- `zero_e_evt / zero_z_art = D33`

`anchor_route_selection(budget=0.05)` 仍为:
- `selected_policy = default_minimax`
- `selected_anchor = D76`

解释:
- `D77` 没有把 pure long-horizon minimax 从 `D76` 切走
- 它当前更准确的制度角色是:
  - official validation-family 的 long-horizon representative
  - 不是新的 pure long-horizon default

## 当前阶段正式判断
1. `D77` 已经成功回答了:
   - official validation-family 拉长到 `200-step` 后并不会塌掉
2. 但 `D77` 也明确没有回答成:
   - official validation-family 足以取代 `D76`
3. 当前更准确的结构是:
   - quick-screen official validation = `D71`
   - long-horizon official validation-family representative = `D77`
   - pure long-horizon minimax/default = `D76`

## 先说人话
- `D77` 证明官方 validation 这条线不是只有短窗有优势。
- 它拉到 `200-step` 后，确实能逼近 `D76`。
- 但它逼近的方式是:
  - validation 几乎追平
  - special / `z_art` 略补回来
  - `e_evt` 明显掉下去
- 所以它还不够把 `D76` 从 long-horizon 默认位子上赶走。

## 当前建议
1. 不要把 `D77` 混写成新的 pure long-horizon default。
2. 当前更准确的写法应是:
   - `D77 = official validation-family matched long-horizon representative`
   - `D76 = pure long-horizon default/minimax`
3. 如果后续继续推进，
   更高信息量的下一步不应再是:
   - 继续扩 `D29-init` 同 family 长窗变体
4. 更值得问的是:
   - 是否存在一个 `D76` 近邻，
     能在不丢 validation 的前提下补回 `e_evt / z_art`

## 产物
- 训练:
  - `reports/training/offline_mvp_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/`
- 评估:
  - `reports/eval/offline_mvp_ablations_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/`
  - `reports/eval/offline_mvp_special_eval_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/`
  - `reports/eval/offline_mvp_checkpoint_series_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/`
  - `reports/eval/offline_mvp_special_eval_series_d77_singleton_sparse_d29_init_teacher_gate_late_200step_exp033/`
- pure long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_default_minimax/`
