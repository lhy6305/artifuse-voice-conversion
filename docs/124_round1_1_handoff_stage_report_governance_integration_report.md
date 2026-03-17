# 124. round1.1 `handoff/stage-report governance integration` 报告

## 背景
`docs/123` 已经把 checkpoint anchor 的制度边界写清了，但代码层面当时还停留在:

- route handoff 只会复述当前 route anchor 和 alternatives
- fixed handoff document 不区分 natural final / synthetic checkpoint
- stage report 的 `executive_status` 也不会提示:
  - 当前 anchor 是否是 formal default eligible
  - alternative 是否只是 shadow option

这意味着即使制度上已经收口，
后续人工生成 handoff / stage-report 时，
仍然可能把:
- matched-horizon shadow 用的 `D22 step20`
- checkpoint-option 用的 `D76 step150`

混写成“当前可切换的正式 anchor”。

## 本轮实现
### 1. 新增 route governance 分类模块
- 文件:
  - `src/v5vc/route_governance.py`
- 现在会先对每个 anchor 做自动分类:
  - `natural_final_anchor`
  - `horizon_equalization_anchor`
  - `checkpoint_option_anchor`

分类依据:
- 是否是 synthetic checkpoint anchor
- 其 `completed_steps` 是否对齐当前 route candidate set 的参考 horizon

当前启发式解释:
- synthetic 且 step 对齐 reference horizon:
  - 视为 horizon equalization
- synthetic 且 step 不对齐 reference horizon:
  - 视为 checkpoint option

## 2. `build-offline-mvp-route-handoff` 已接入治理信息
- 文件:
  - `src/v5vc/handoff_summary.py`

新增效果:
- `route_anchor` / `alternatives` 都会带上 `governance`
- summary json 新增:
  - `route_governance`
- `copy_ready_handoff` 不再只有 summary/tradeoff
- 现在会额外插入:
  - formal default / shadow / option 的 guardrail 句子
- `next_step_guidance` 现在会区分:
  - natural final alternative
  - matched-horizon shadow alternative
  - checkpoint option alternative

## 3. fixed handoff document / stage report 模板已显式渲染治理段
- 代码:
  - `src/v5vc/handoff_document.py`
  - `src/v5vc/stage_report.py`
- 模板:
  - `reports/templates/offline_mvp_handoff_document_template.md`
  - `reports/templates/offline_mvp_stage_report_template.md`

新增字段:
- `route_governance_summary`
- `route_governance_guardrail`
- current anchor governance line
- primary alternatives governance line

直接效果:
- stage report 的 `executive_status` 不再只是:
  - “当前 route 是谁”
- 还会明确写出:
  - synthetic checkpoint alternative 是否只能留在 shadow / option lane

## 真实回放验证
### A. `D76 step150` checkpoint-option 场景
- selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
- 新回放产物:
  - `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_d22_d33_d59_d76_d76step150_governance/`
  - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_longwindow_d22_d33_d59_d76_d76step150_governance/`
  - `reports/stage_reports/offline_mvp_stage_report_round1_1_longwindow_d22_d33_d59_d76_d76step150_governance/`

验证结果:
- route anchor `D33 step200` 被标成:
  - `natural_final_anchor`
- `D76 step150` 被标成:
  - `checkpoint_option_anchor`
- stage report 明确写出:
  - formal default remains final-only
  - `D76 step150` stay option-only
  - 不应升格成 formal default route

### B. `D22 step20` horizon-equalization 场景
- selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`
- 新回放产物:
  - `reports/eval/offline_mvp_route_handoff_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance/`
  - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance/`
  - `reports/stage_reports/offline_mvp_stage_report_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_governance/`

验证结果:
- active anchor `D29 step20` 仍被标成:
  - `natural_final_anchor`
- `D22 step20 anchor` 被标成:
  - `horizon_equalization_anchor`
- stage report 明确写出:
  - 它可支持 matched-horizon shadow
  - 但 official handoff / stage-report wording 仍应保持 final-only

## 结论
这轮的关键不是再发现一个新 anchor，
而是把 `docs/123` 的制度边界变成模板级硬约束。

当前磁盘上已经实现:
1. formal default anchor 与 synthetic alternatives 不再混写
2. horizon-equalization 与 checkpoint-option 不再共用一句“checkpoint anchor 可以进入 route”
3. handoff / stage-report 现在会自动暴露:
   - 这个 anchor 能不能当 formal default
   - 这个 alternative 只能不能只当 shadow / option

## 当前阶段建议
1. 后续若继续生成 handoff / stage-report，
   默认使用这套新模板和新 payload。
2. 若未来真的要让 checkpoint-option anchor 进入正式 route，
   应直接修改 governance 规则，
   而不是绕过模板文案。
3. 下一步更值得做的不是继续改模板，
   而是回到 route policy 本身，判断是否存在需要正式制度升级的证据。
