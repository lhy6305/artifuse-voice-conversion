# `round1.1 / handoff document -> fixed stage report integration` 报告

## 背景
- `handoff_document.*` 已经能作为固定格式的正式交接件。
- 当前还缺更上层的一步:
  - 能不能把交接件继续物化成固定格式的阶段汇总文档
  - 让阶段状态更新也不再手工重写

## 本轮产物
- 新增正式命令:
  - `materialize-offline-mvp-stage-report`
- 新增模板:
  - `reports/templates/offline_mvp_stage_report_template.md`
- 输出:
  - `stage_report.json`
  - `stage_report.md`

## 设计要点
- 不重复实现 route selector / comparison / recap / handoff 逻辑。
- 直接消费上游 `handoff_document.json`。
- 固定 stage report 默认包含:
  - executive status
  - current anchor
  - primary tradeoff
  - carry-forward handoff
  - next-step guidance
  - source artifacts

## 实跑验证
- 输入:
  - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_default_minimax/handoff_document.json`
- 输出:
  - `reports/stage_reports/offline_mvp_stage_report_round1_1_default_minimax/stage_report.md`

## 当前结果
- 三锚流程现在已经形成三层正式汇总产物:
  1. `route_handoff.*`
     - route-aware 交接摘要
  2. `handoff_document.*`
     - 固定格式交接文档
  3. `stage_report.*`
     - 固定格式阶段状态报告

- 这意味着:
  - 正式接班与阶段汇总都已经有统一入口
  - 不再需要在不同层级文档之间手工改写同一套 route 取舍描述

## 当前结论
1. 三锚流程现在已经形成:
   - analysis
   - route policy
   - selector
   - init-experiment integration
   - final comparison
   - recap
   - handoff
   - fixed handoff document
   - fixed stage report
2. 后续若做阶段总结，优先使用固定格式 stage report，而不是手工从 handoff document 提炼一层新摘要。

## 下一步建议
1. 暂不继续扩更多 stage report 模板。
2. 若继续推进流程层集成，更值得把 stage report 直接接进固定周报或里程碑汇总入口。
