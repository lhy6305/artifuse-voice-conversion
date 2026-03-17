# 114. round1.1 `matched20 checkpoint-anchor` 报告

## 背景
- 在 `D68 / D69` 之后，
  下一步候选有两条:
  - `checkpoint-selected late stop`
  - `matched-horizon comparison`
- 这轮先把两者拆开:
  1. 先看 `D60` family 自己有没有值得 early-stop 的 checkpoint
  2. 如果没有，再把 `D22` 拉回 `step20`，与 `D29 / D33 / D60 / D68 / D69` 做公平 horizon 比较

## 先验检查: `D60` family 值不值得做 checkpoint-selected late stop
- `D60 / D68 / D69 step10` 完全同轨:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- 对应 `step20` 分别为:
  - `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
  - `D69 = 2.523948 / 0.111144 / 3.271397 / 0.434243`

结论:
- 这条主线没有出现:
  - `step10 special 更好`
  - 但 `step20 validation 更好`
  的 checkpoint-selection tradeoff
- 相反，
  `step20` 相对 `step10` 同时改善:
  - validation
  - special
  - `e_evt`
  - `z_art`
- 所以:
  - `D60` family 当前不值得继续做 `checkpoint-selected late stop`
  - 下一手应转向 `matched-horizon`

## 工具补充
- 为了做 matched-horizon，
  新增命令:
  - `materialize-offline-mvp-checkpoint-anchor`
- 代码位置:
  - `src/v5vc/checkpoint_anchor_materializer.py`
  - `src/v5vc/cli.py`
- 作用:
  - 从现有实验 metrics 的
    - `special_eval_series`
    - `checkpoint_series_eval`
  - 中抽取指定 step，
    物化成可直接喂给现有 selector / comparison 的 synthetic anchor metrics

本轮实际物化:
- `D22 step20 anchor`
  - `reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.checkpoint-step20-anchor.metrics.json`

## matched20 比较集
- `D29 final(20step)`
- `D22 step20 anchor`
- `D33 final(20step)`
- `D60 final(20step)`
- `D68 final(20step)`
- `D69 final(20step)`

## matched20 关键结果
- `D29 = 2.397175 / 0.171769 / 2.978481 / 0.364927`
- `D22-step20 = 2.470626 / 0.178101 / 3.021211 / 0.398439`
- `D33 = 2.52818 / 0.111677 / 3.312339 / 0.465828`
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
- `D69 = 2.523948 / 0.111144 / 3.271397 / 0.434243`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## route analysis 结论
- matched20 leader:
  - validation = `D29`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D68`
- 新阈值:
  - `budget_to_minimax_anchor = 0.12514`
  - `budget_to_special_anchor = 0.126773`

这两个阈值都明显高于当前 quick-screen 的默认预算 `0.05`。

## selector 结论
### 当前默认预算 `0.05`
- selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`
- 结果:
  - `selected_policy = validation_strict`
  - `selected_anchor = D29`

含义:
- 一旦把 horizon 真正拉平到 `20 / 20 / 20`,
  当前 `default_minimax @ budget=0.05`
  已经不再会选到 `D22` 或 `D68`
- 它会直接退化成 validation-first

### 放宽预算到 `0.13`
- selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_budget013/`
- 结果:
  - `selected_policy = default_minimax`
  - `selected_anchor = D68`

含义:
- 如果把 matched20 当正式制度，
  且愿意把 validation budget 从 `0.05` 放宽到至少 `0.12514`,
  当前最合理的 minimax anchor 已经不再是 `D22-step20`
  而是 `D68`

## 解释
- 这轮最重要的不是 `D68` 比 `D60` 强了多少，
  而是:
  - 当前官方 `D22 = default_minimax`
    这个结论，
    明显依赖于 `D22` 用的是 `30 step`
    而别的候选大多还是 `20 step`
- 一旦把 `D22` 拉回 matched20，
  它的形态会变成:
  - validation 比 `D29` 差不少
  - special 比 `D60 / D68 / D69 / D33` 明显更差
  - control 也没有压过 `D60` family
- 所以:
  - `D22` 当前的 minimax 地位，
    至少部分是 horizon advantage
  - 而不是它在 `20 step` 公平比较里仍然占优

先说人话:
- 这轮把一件事跑明白了:
  - 不是 `D60` family 需要早停
  - 而是 `D22` 现在的 default_minimax 身份，本身带着 horizon 不对称
- 如果要讲“公平的 20step quick-screen”，
  `D22` 已经站不住；
  新的 minimax 候选会变成 `D68`，
  但代价是必须承认当前 `0.05` validation budget 太紧

## 当前阶段正式结论
1. `checkpoint-selected late stop` 在当前 `D60` family 上没有杠杆，`step20` 全面优于 `step10`。
2. `matched20` 下，当前 minimax anchor 已从 `D22` 切到 `D68`。
3. 但这只在:
   - 接受 matched-horizon 制度
   - 且把 validation budget 放宽到 `>= 0.12514`
   时才成立。
4. 因此当前正式 handoff 还不能直接刷新成 `D68`；
   先要决定的是:
   - 是否把 selector 制度改成 matched-horizon
   - 以及是否重设 validation budget

## 下一步
- 暂停继续做:
  - `D60` family 的 checkpoint-selected late stop
  - `D60 / D68 / D69` 的 teacher-handoff 微调
- 更值得推进:
  1. 正式整理 quick-screen horizon policy:
     - 保持当前不对称 quick-screen
     - 还是迁移到 matched-horizon
  2. 若迁移到 matched-horizon，
     再决定 validation budget 是否从 `0.05` 重设到更宽区间
  3. 只有制度口径定下来后，
     才值得继续判断 `D68` 是否应升格为正式 minimax anchor
