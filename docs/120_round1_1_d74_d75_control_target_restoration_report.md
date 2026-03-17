# 120. round1.1 `D74-D75 / D70 control-target restoration` 报告

## 背景
- `D72 / D73` 已经把 `D70 family` 的 late teacher source / handoff 轴基本跑清:
  - 有真实信息
  - 但量级只剩 epsilon 级再平衡
- 所以上一轮确定:
  - 不再继续扫纯 handoff 小变体
  - 而是转向更明确的 control-target restoration

本轮只做两条最小但信息更强的 follow-up:
1. `D74 = late teacher source restore`
2. `D75 = late fused-hidden strength restore`

## 这轮设计
### `D74`
- 配置:
  - `configs/offline_mvp_train_d74_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_late_d33step10_teacher_restore_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-031-offline-mvp-d74-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-late-d33step10-teacher-restore-20step-calibration`
- 设计:
  - 完整继承 `D70`
  - 只把 late `step11-20` teacher source 从:
    - `D29 step10`
    - 改成 `D33 step10`
  - late singleton strict gate / sampler / proxy aux 全部保持原样

### `D75`
- 配置:
  - `configs/offline_mvp_train_d75_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-030-offline-mvp-d75-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-20step-calibration`
- 设计:
  - 完整继承 `D72`
  - 只把 late `step11-20` 的:
    - `fused_hidden_weight: 0.05 -> 0.08`

## 运行补充
- 本轮一开始发现:
  - `init-experiment` 不只会在并发时抢号
  - 当历史目录存在缺号时，
    顺序初始化也会因为“按文件数量 + 1”而重用旧前缀
- 该问题已修复为:
  - 使用“当日最大已存在三位序号 + 1”
- 并已清理错误占位记录:
  - 删除错误的 `029-d74`
  - 重建为 `D74 = EXP-...031`

## 完整执行链
- `D74 / D75` 均已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - 正式训练
  - `evaluate-offline-mvp-ablations`
  - `evaluate-offline-mvp-special-eval`
  - `evaluate-offline-mvp-checkpoint-series`
  - `evaluate-offline-mvp-special-eval-series`
- 并已同步并入:
  - official quick-screen route-analysis / selector / final comparison / recap
  - matched20 shadow bundle

## final 结果
- `D70 = 2.399035 / 0.168635 / 2.941607 / 0.365565`
- `D72 = 2.399071 / 0.167648 / 2.957 / 0.364989`
- `D73 = 2.398942 / 0.168183 / 2.953266 / 0.364179`
- `D74 = 2.401255 / 0.168125 / 2.955904 / 0.368817`
- `D75 = 2.399272 / 0.16719 / 2.960501 / 0.365693`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## 关键结论
### 1. `D74 / D75 step10` 都与 `D70 family` 现有轨迹完全同轨
- 两条线的 `step10` 都仍是:
  - `2.442652 / 0.171144 / 2.985898 / 0.387834`
- 解释:
  - 这轮新增信息全部来自 late `step11-20`
  - 不是 init checkpoint 或前半段训练路径差异

### 2. `D74` 证明 late `D33 step10 teacher` 不是挂空，但代价偏大
- `D74 vs D72`
  - validation 更差 `+0.002184`
  - special 略差 `+0.000477`
  - `zero_e_evt` 略弱 `-0.001096`
  - `zero_z_art` 略强 `+0.003828`

解释:
- 这说明:
  - 把 late teacher 直接换成更强的 control teacher
    确实会继续推高 `z_art`
  - 但它并没有形成更好的 joint point
- 更准确地说:
  - `D74` 不是 no-op
  - 但它更像用明显一点的 validation tax
    去换一小段 `z_art`

### 3. `D75` 是这轮真正的 local winner
- `D75 vs D72`
  - validation 略差 `+0.000201`
  - special 更好 `-0.000458`
  - `zero_e_evt` 更好 `+0.003501`
  - `zero_z_art` 更好 `+0.000704`

- `D75 vs D70`
  - validation 略差 `+0.000237`
  - special 更好 `-0.001445`
  - `zero_e_evt` 更好 `+0.018894`
  - `zero_z_art` 略好 `+0.000128`

解释:
- 这不是 validation 大胜，
  也不是 dramatic breakout。
- 但它第一次在 `D70 family` 里给出一个比较清楚的单点:
  - validation 几乎不变
  - special 更好
  - `e_evt` 更好
  - `z_art` 不回吐

### 4. official quick-screen 仍没有被改写
- official route-analysis(`D22 / D29 / D33 / D60 / D68 / D69 / D70 / D71 / D72 / D73 / D74 / D75`) 继续给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D22`
- selector(`budget=0.05`) 也继续保持:
  - `validation_strict = D71`

解释:
- `D74 / D75` 没有改变 official fixed handoff 的制度判断
- 这轮改写的是:
  - `D70 family` 内部的 shadow 代表点
  - 不是 official route 本身

### 5. matched20 shadow minimax 从 `D72` 切到 `D75`
- shadow route-analysis(`D29 / D22-step20 / D33 / D60 / D68 / D69 / D70 / D71 / D72 / D73 / D74 / D75`) 给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D75`
- 新阈值:
  - `budget_to_minimax_anchor = 0.059075`
- selector:
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D75`

解释:
- 这次不再是 `D70 / D72 / D73` 盆地里纯随机换人。
- 更合理的说法是:
  - `D75` 已经把这条窄盆地的代表点向前推了一格
  - 但量级仍不足以直接改写 official

## 当前阶段正式判断
1. `D74` 提供了真实负结果:
   - late `D33 teacher` 可以再推 `z_art`
   - 但不是更好的 joint winner
2. `D75` 是真实进展:
   - 它把 `D70 family` 的 shadow 代表点从 `D72` 推到了 `D75`
3. official fixed handoff 仍不刷新。
4. 当前更准确的状态应写成:
   - official 继续是旧三锚
   - matched20 shadow 的当前代表点已经收缩到 `D75`

## 下一步
1. 暂停继续做:
   - `D70 family` 内更多 late teacher source / fused-hidden 小幅 sweep
2. 当前更值得优先推进的是:
   - 以 `D75` 作为 `D70 family` 当前代表点
   - 进入 matched long horizon(`200+`) 验证
3. 若 long horizon 仍继续支持 `D75` family，
   才再讨论是否挑战 official fixed handoff

## 产物
- official quick-screen:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_default_minimax/`
- matched20 shadow:
  - `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75/`
