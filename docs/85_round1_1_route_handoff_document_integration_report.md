# `round1.1 / route handoff -> fixed handoff document integration` 报告

## 背景
- `build-offline-mvp-route-handoff` 已经能直接生成 copy-ready handoff。
- 当前还缺最后一层固定流程:
  - 能不能把 `route_handoff.json` 进一步落成固定格式的正式交接文档
  - 让接班入口不再直接消费原始摘要 markdown

## 本轮产物
- 新增正式命令:
  - `materialize-offline-mvp-route-handoff-doc`
- 新增模板:
  - `reports/templates/offline_mvp_handoff_document_template.md`
- 输出:
  - `handoff_document.json`
  - `handoff_document.md`

## 设计要点
- 不重复实现 selector / comparison / recap / handoff 的分析逻辑。
- 直接消费上游 `route_handoff.json`。
- 固定交接文档默认包含:
  - metadata
  - source artifacts
  - copy-ready handoff
  - current anchor
  - alternatives
  - next-step guidance

## 实跑验证
- 输入:
  - `reports/eval/offline_mvp_route_handoff_round1_1_d22_d26_d29_default_minimax/route_handoff.json`
- 输出:
  - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_default_minimax/handoff_document.md`

## 当前结果
- route-aware handoff 现在已经形成两层正式产物:
  1. `route_handoff.*`
     - 负责 route-aware 交接摘要与 artifact bundle
  2. `handoff_document.*`
     - 负责固定格式的正式交接文档

- 这意味着:
  - 后续正式接班可以稳定引用固定格式文档
  - 原始 `route_handoff.md` 不再需要兼任“最终交接件”

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
2. 后续若做正式接班或阶段交接，优先使用固定格式 handoff document，而不是直接贴原始 `route_handoff.md`。

## 下一步建议
1. 暂不继续扩更多 handoff 文档模板。
2. 若继续推进流程层集成，更值得把该固定交接文档直接接进阶段报告或固定周报入口。
