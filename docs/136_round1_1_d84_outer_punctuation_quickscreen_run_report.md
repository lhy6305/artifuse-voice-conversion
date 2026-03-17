# 136. round1.1 `D84 / outer punctuation quick-screen` 正式运行与 route 归位报告

## 背景
- `docs/135` 已完成 `D84` 的设计、sidecar 扩展与 dry-run。
- 但磁盘上的真实状态已经继续推进到了:
  - 正式 quick-screen 训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series`
  - `special_eval_series`
  - official quick-screen route 归位
  - matched20 shadow bundle 归位

本报告用于把这段“dry-run 之后实际又向前跑完了什么”补成正式口径。

## 执行链
- 已完成:
  - `.\python.exe manage.py train-offline-mvp --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-id EXP-20260316-040`
  - `.\python.exe manage.py evaluate-offline-mvp-ablations --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260316-040-offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration.metrics.json --output-dir reports/eval/offline_mvp_ablations_d84_exp20260316_040`
  - `.\python.exe manage.py evaluate-offline-mvp-special-eval --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260316-040-offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration.metrics.json --output-dir reports/eval/offline_mvp_special_eval_d84_exp20260316_040`
  - `.\python.exe manage.py evaluate-offline-mvp-checkpoint-series --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260316-040-offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration.metrics.json --output-dir reports/eval/offline_mvp_checkpoint_series_d84_exp20260316_040`
  - `.\python.exe manage.py evaluate-offline-mvp-special-eval-series --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260316-040-offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration.metrics.json --output-dir reports/eval/offline_mvp_special_eval_series_d84_exp20260316_040`
  - `.\python.exe manage.py analyze-offline-mvp-anchor-routes ... --output-dir reports/eval/offline_mvp_anchor_routes_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_d84`
  - `.\python.exe manage.py select-offline-mvp-anchor-route ... --max-validation-budget-over-best 0.05 --output-dir reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_d84_default_minimax`
  - `.\python.exe manage.py compare-offline-mvp-final-experiments ...`
  - `.\python.exe manage.py recap-offline-mvp-route-context ...`
  - `.\python.exe manage.py build-offline-mvp-matched-horizon-shadow ... --output-dir reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_d84`

## 正式结果
- `D84 final = 2.417702 / 0.156619 / 3.089381 / 0.381618`
- 指标顺序固定为:
  - `target_validation / special_delta / zero_e_evt / zero_z_art`

### 与 `D75` 的直接对比
- `D75 = 2.399272 / 0.16719 / 2.960501 / 0.365693`
- `D84 vs D75`:
  - validation `+0.007910`
  - special `-0.010571`
  - `zero_e_evt` `+0.128880`
  - `zero_z_art` `+0.015925`

解释:
- `D84` 不是 validation winner。
- 但它也不是“只换一点 special、其它全回吐”的局部点。
- 它在接受一小段 validation tax 的同时，
  把 `special / e_evt / z_art` 三项一起往更平衡的方向推了一步。

## 机制是否真实生效
训练日志显示:
- `step12 loss_punctuation_profile_aux = 0.009319`
- `step15 loss_punctuation_profile_aux = 0.003821`
- `step20 loss_punctuation_profile_aux = 0.008741`

同时 late effective config 持续包含:
- `secondary_sampling.priority_pool_memberships = ['micro_singleton_anypunct_expansion']`
- `punctuation_profile_aux.pool_memberships = ['micro_singleton_anypunct_expansion']`

解释:
- 这轮不是“配置里写了 outer pool，但训练时没有命中”。
- 新 sampler 和新 punctuation aux 都是真的活着。

## official quick-screen 归位结果
并入 official quick-screen 后，正式角色仍保持:
- validation = `D71`
- special = `D69`
- `zero_e_evt / zero_z_art = D33`
- minimax = `D22`

阈值保持:
- `budget_to_minimax_anchor = 0.103997`
- `budget_to_special_anchor = 0.183751`
- `best_e_evt_floor = 3.312339`
- `best_z_art_floor = 0.465828`

解释:
- `D84` 没有改写 official quick-screen。
- 当前还不能把它写成新的正式 default / minimax。

## matched20 shadow 归位结果
并入 matched20 shadow 后，route 更新为:
- validation = `D71`
- special = `D69`
- `zero_e_evt / zero_z_art = D33`
- minimax = `D84`

新阈值变成:
- `budget_to_minimax_anchor = 0.066985`
- `budget_to_special_anchor = 0.183751`
- `best_e_evt_floor = 3.312339`
- `best_z_art_floor = 0.465828`

selector 结果:
- `matched20@0.05 -> D71`
- `matched20@0.13 -> D84`

解释:
- `D84` 已经把 matched20 shadow representative 从 `D75` 再往前推了一格。
- 这说明 outer punctuation 这条题不是纯负结果，
  至少在 matched20 口径下打开了新的 joint point。

## 当前阶段判断
1. `D84` 是有效实验，不是假 gate，也不是旧 `punctuation_profile_aux` 的重跑。
2. `D84` 没有改写 official quick-screen。
3. `D84` 已经改写 matched20 shadow minimax，从 `D75` 切到 `D84`。
4. 因此当前更准确的制度口径应写成:
   - official quick-screen 继续不变
   - matched20 shadow representative 更新为 `D84`

先说人话:
- 这轮不是“新题也失败了”。
- 更像是:
  - 它还不够强到推翻正式 quick-screen
  - 但已经强到说明这条 outer punctuation 路线值得继续往 matched long-horizon 看

## 下一步
1. 不要把 `D84` 直接写成新的 official anchor。
2. 若继续推进这条线，下一步更高信息量的问题应是:
   - `D84 family` 拉长到 `200-step` 后是否还能保持 matched20 里的 joint-point 优势
3. 若长窗外推后仍站得住，
   再讨论它是否有资格进入更高层 route 竞争。
