# 117. round1.1 `D70-D71 / stronger checkpoint backbone singleton sparse` 报告

## 背景
- `D60-D69` 已经把这条 post-`D59` singleton sparse 主线的几个浅层旋钮基本收口:
  - tail 长短 / 强弱
  - late teacher gate
  - `D22-like` late teacher source / handoff shape
- 当前剩余问题是:
  - 能否不用把 singleton principle 再 graft 到 `D22` 后半段，
  - 而是直接把整条 `20 step` quick-screen 建立在更强 validation backbone 上，
  - 从更上游削掉 `D60` 的 validation tax

## 这轮设计
### `D70`
- 配置:
  - `configs/offline_mvp_train_d70_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 完整继承 `D60` 的:
    - teacher schedule
    - late singleton targeted sampling
    - `singleton_sparse_proxy_aux`
  - 只把 `init_checkpoint_path` 从:
    - `D7 step100`
    - 改成 `D26 step20`

### `D71`
- 配置:
  - `configs/offline_mvp_train_d71_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 完整继承 `D70`
  - 只把 `init_checkpoint_path` 再从:
    - `D26 step20`
    - 改成 `D29 step20`

## 运行补充
- 本轮一开始误用了系统 `python`，已在继续前纠正回仓库根目录 `.\python.exe`。
- 这次异常属于解释器误用，不属于代码兼容性修复任务。
- 本轮后续全部命令均已显式改回:
  - `.\python.exe manage.py ...`

## 完整执行链
- `D70 / D71` 均已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - 正式训练
  - `evaluate-offline-mvp-ablations`
  - `evaluate-offline-mvp-special-eval`
  - `evaluate-offline-mvp-checkpoint-series`
  - `evaluate-offline-mvp-special-eval-series`
- 并已同步并入:
  - official quick-screen route-analysis / selector / final comparison / recap
  - `matched20 shadow bundle`

## final 结果
- `D29 = 2.397175 / 0.171769 / 2.978481 / 0.364927`
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D70 = 2.399035 / 0.168635 / 2.941607 / 0.365565`
- `D71 = 2.340197 / 0.190968 / 2.634231 / 0.320415`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## 关键结论
### 1. `D70` 是这条主线第一次真正把 `D60` 的 validation tax 大幅削掉
- `D70 vs D60`
  - validation 明显更好 `-0.123705`
  - special 明显回吐 `+0.056498`
  - `zero_e_evt` 明显回吐 `-0.318644`
  - `zero_z_art` 明显回吐 `-0.069826`

解释:
- `D70` 不是 `D60` 的小修小补，
  而是一次真正的 backbone 级再定位
- 它已经基本回到 `D29` 一档的 validation 区间
- 同时仍保留了一点 singleton sparse 的 special / `z_art` 收益痕迹

### 2. `D70` 更像 `D29+epsilon`，不是直接超过 `D29`
- `D70 vs D29`
  - validation 略差 `+0.00186`
  - special 略好 `-0.003134`
  - `zero_e_evt` 略差 `-0.036874`
  - `zero_z_art` 略好 `+0.000638`

解释:
- `D70` 的信息价值不在于“全面赢过 `D29`”
- 而在于:
  - 它说明 `D60` 那种 special-aware principle
    并不一定要以 `0.12+` validation tax 为代价
  - 一旦 backbone 换到 `D26 step20`，
    就能把代价压到非常接近 `D29`

### 3. `D71` 证明再把 backbone 推到 `D29 step20` 会直接滑成 validation-first
- `D71 vs D70`
  - validation 更好 `-0.058838`
  - 但 special 更差 `+0.022333`
  - `zero_e_evt` 更差 `-0.307376`
  - `zero_z_art` 更差 `-0.04515`

解释:
- `D71` 不是更强 minimax，
  而是更纯的 validation leader
- 它说明这条 backbone 轴不是单调改进:
  - `D26-init` 还有 balanced tradeoff
  - `D29-init` 就已经明显过冲

### 4. official quick-screen 下，`D70/D71` 没有改写 minimax 本身，但把旧 selector contract 直接挤塌了
- official route-analysis(`D22 / D29 / D33 / D60 / D68 / D69 / D70 / D71`) 给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D22`
- 但因为:
  - `best_validation` 被 `D71` 推到 `2.340197`
  - `budget_to_minimax_anchor` 抬到 `0.103997`
- 所以 official selector 在 `budget = 0.05` 下直接变成:
  - `selected_policy = validation_strict`
  - `selected_anchor = D71`

解释:
- 这不是 `D71` 自动变成了新的 minimax
- 而是:
  - 当前旧 quick-screen 预算
  - 面对更强 validation backbone 时
  - 会把 route 语义直接压成 validation-first

### 5. matched20 shadow 下，minimax 已从 `D68` 切到 `D70`
- shadow route-analysis(`D29 / D22-step20 / D33 / D60 / D68 / D69 / D70 / D71`) 给出:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D70`
- 新阈值:
  - `budget_to_minimax_anchor = 0.058838`
- selector:
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D70`

解释:
- 这说明 shadow minimax 还远没稳定
- 它已经从上一轮的 `D68`
  直接切到这一轮的 `D70`
- 因此当前还不具备上 `matched long horizon(200+)`
  去挑战 fixed handoff 的条件

## 当前阶段正式判断
1. `D70` 是真实进展:
   - 它证明 backbone-level 变化确实能显著削掉 `D60` validation tax
2. `D71` 也是有效信息:
   - 它把这条 backbone 轴的过冲边界跑清楚了
3. 当前不应把 `D71` 的 raw selector 结果直接解释成:
   - official fixed handoff 应立刻刷新成 validation-first
4. 当前也不应把 `D70` 直接解释成:
   - shadow minimax 已稳定坐实
5. 更准确的结论应是:
   - `D70` 打开了一条比 `D68` 更有价值的新 shadow 主线
   - 但 `D71` 同时证明这条 backbone 轴很容易过冲

## 下一步
1. official fixed handoff / stage-report 暂不刷新，继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 下一手不继续做:
   - `D71` 这类更强 validation-first backbone 延伸
3. 更值得继续的是:
   - 以 `D70` 为新主线
   - 做最小幅的 control restoration
   - 例如把 `D68 / D69` 那类 late teacher source / handoff 旋钮迁移到 `D70` 上
4. 只有当:
   - shadow minimax 连续几轮都稳定落在 `D70` family
   才再补:
   - `matched long horizon(200+)`

## 产物
- official quick-screen:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d29_d33_d60_d68_d69_d70_d71/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_default_minimax/`
- matched20 shadow:
  - `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71/`
