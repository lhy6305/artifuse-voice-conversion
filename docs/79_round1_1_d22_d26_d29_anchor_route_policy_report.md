# `round1.1 / D22+D26+D29 / anchor route policy` 报告

## 背景
- `D22 / D26 / D29` 的三锚职责已经在上一轮正式收口:
  - `D29 = validation leader`
  - `D26 = special / z_art leader`
  - `D22 = minimax default anchor`
- 当前缺的是:
  - 把这个结论从“文档判断”变成“正式 route selector / reporting policy”
  - 后续不再手工口头挑锚点

## 本轮产物
- 新增正式命令:
  - `analyze-offline-mvp-anchor-routes`
- 分析输出:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d26_d29/anchor_route_analysis.json`
  - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d26_d29/anchor_route_analysis.md`

## 标准 policy profile

### 1. `validation_strict`
- 含义:
  - 不允许任何额外 validation budget
- 结果:
  - 固定选 `D29`

### 2. `default_minimax`
- 含义:
  - 不额外偏置 special / z_art
  - 直接选 least-worst final anchor
- 结果:
  - 固定选 `D22`

### 3. `guarded_default`
- 含义:
  - 只放开到刚好能容纳 minimax anchor 的 validation budget
- 阈值:
  - `max_validation_budget_over_best = 0.047019`
- 结果:
  - 仍选 `D22`

### 4. `e_evt_guard`
- 含义:
  - 要求当前最强 `e_evt` floor
  - 同时维持 minimax 选择逻辑
- 阈值:
  - `zero_e_evt >= 3.299035`
  - `zero_z_art >= 0.438936`
- 结果:
  - 只有 `D22` 还能满足

### 5. `special_push`
- 含义:
  - 明确允许更贵的 validation，换 special / `z_art`
- 阈值:
  - `max_validation_budget_over_best = 0.126723`
- 结果:
  - 选 `D26`

### 6. `z_art_push`
- 含义:
  - 明确要求当前最强 `z_art` floor，并接受对应 validation 代价
- 阈值:
  - `max_validation_budget_over_best = 0.126723`
  - `zero_z_art >= 0.460259`
- 结果:
  - 只有 `D26` 还能满足

## 推荐 route 规则
当前最有价值的正式 route policy 可以直接写成三段:

1. `max_validation_budget_over_best < 0.047019`
   - 选 `validation_strict`
   - 对应 anchor: `D29`

2. `max_validation_budget_over_best >= 0.047019`
   - 且 `special_priority = false`
   - 且 `z_art_priority = false`
   - 选 `default_minimax`
   - 对应 anchor: `D22`

3. `max_validation_budget_over_best >= 0.126723`
   - 且 `special_priority = true` 或 `z_art_priority = true`
   - 选 `special_push`
   - 对应 anchor: `D26`

先说人话:
- budget 很紧时，默认用 `D29`
- budget 稍微放开但没有强 special 诉求时，用 `D22`
- 只有在你明确愿意付出完整 validation 代价、且目标就是 special / `z_art` 时，才切到 `D26`

## 结论更新
1. 三锚已经从“研究结论”升级成“正式 route policy”。
2. 后续所有报告若引用 teacher-consistency family final reference，默认先声明当前 route:
   - `validation_strict`
   - `default_minimax`
   - `special_push`
3. 不再接受只写“当前参考 anchor 是某某”而不写 route 前提的表述。

## 下一步建议
1. 若继续做分析，优先把这个 route policy 接到后续评估报告模板或联合比较报告里。
2. 若继续开新训练，应明确声明是想打哪条 route:
   - 抢 `D29` 的 validation
   - 打 `D22` 的 minimax
   - 还是冲 `D26` 的 special / `z_art`
3. 不再优先继续做“没有 route 目标声明”的中间态变体。
