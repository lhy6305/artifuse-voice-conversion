# `round1.1 / route selector -> init-experiment integration` 报告

## 背景
- selector 已经能输出当前 route 下应选的 anchor。
- experiment record 模板也已经补了 route 字段。
- 当前缺的最后一步是:
  - `init-experiment` 能不能直接消费 selector 产物
  - 这样立项时不再手工抄 route 信息

## 本轮产物
- `init-experiment` 新增:
  - `--route-selection`
- 填充逻辑更新:
  - 若提供 selector json，
    - 自动写入 `route_policy`
    - 自动写入 `route_budget_or_floor`
    - 自动写入 `anchor_reference`

## Smoke 验证
- selector 输入:
  - `reports/eval/offline_mvp_anchor_route_selection_default_minimax/anchor_route_selection.json`
- smoke 产物:
  - `reports/tmp/route_selector_init_smoke/EXP-20260315-001-offline-mvp-route-selector-smoke.md`
  - `reports/tmp/route_selector_init_smoke/EXP-20260315-001-offline-mvp-route-selector-smoke.metrics.json`
- 结果:
  - `route_policy: default_minimax`
  - `route_budget_or_floor: {"max_validation_budget_over_best": 0.05, ...}`
  - `anchor_reference: EXP-20260315-039-...-d22-...`

这说明:
- selector -> `init-experiment` 的链已经跑通
- 后续新实验立项不再需要手工复制 route 条件

## 当前结论
1. 三锚选择链现在已经形成:
   - analysis
   - route policy
   - selector
   - `init-experiment` 自动写入
2. 后续若继续开新实验，推荐流程应改为:
   - 先跑 selector
   - 再用 `init-experiment --route-selection ...`
   - 最后再补 baseline/change 与 hypothesis

## 下一步建议
1. 暂不继续扩 selector 家族。
2. 若继续推进流程层集成，更值得把 selector 结果接到后续联合比较或实验复盘入口。
