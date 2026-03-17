# `round1.1 / anchor route selector + template update` 报告

## 背景
- 上一轮已经把三锚 route policy 固化为正式规则。
- 当前缺的是最后一层执行入口:
  - 能不能直接给一个 budget / priority 条件，就输出该选哪个 anchor
  - 后续 experiment record 模板能不能直接记录 route 前提，而不是靠人工补充

## 本轮产物
- 新增正式命令:
  - `select-offline-mvp-anchor-route`
- 新增实现:
  - `src/v5vc/anchor_route_selector.py`
- 模板更新:
  - `reports/templates/experiment_record_template.md`
    - 新增:
      - `route_policy`
      - `route_budget_or_floor`
      - `anchor_reference`

## Selector 验证

### 1. strict validation 场景
- 输入:
  - `max_validation_budget_over_best = 0.0`
- 结果:
  - `selected_policy = validation_strict`
  - `selected_anchor = D29`

### 2. default minimax 场景
- 输入:
  - `max_validation_budget_over_best = 0.05`
- 结果:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`

### 3. special push 场景
- 输入:
  - `max_validation_budget_over_best = 0.13`
  - `special_priority = true`
- 结果:
  - `selected_policy = special_push`
  - `selected_anchor = D26`

这说明 selector 已经不是“复述文档”，而是能稳定复现当前 route policy。

## 当前结论
1. 三锚 route policy 现在已经具备:
   - 正式分析命令
   - 正式 route policy 命令
   - 正式单次 selector 命令
2. 后续若做评估、汇总或新实验立项，已经可以直接写:
   - 当前 route policy
   - 当前 budget / floor
   - selector 产出的 anchor reference
3. experiment record 模板已经补齐 route 字段，后面不应再出现“只记 experiment config，不记 route 前提”的记录方式。

## 下一步建议
1. 若继续推进分析基础设施，优先把 selector 输出接进后续联合比较或实验立项流程。
2. 若继续开新训练，建议先用 selector 明确写出目标 route，再起新 experiment。
3. 暂不优先再扩三锚分析命令家族；当前选择链已经够用。
