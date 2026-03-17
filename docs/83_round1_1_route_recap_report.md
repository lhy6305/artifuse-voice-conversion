# `round1.1 / route-aware recap entrypoint` 报告

## 背景
- route selector 已接到 experiment 立项。
- final comparison 也已经支持 route context。
- 当前还缺一个真正面向“复盘/阶段汇总”的入口:
  - 能不能直接给出当前 route 的一句总结
  - 以及主要替代锚点各自付出的代价

## 本轮产物
- 新增正式命令:
  - `recap-offline-mvp-route-context`
- 输出:
  - `route_recap.json`
  - `route_recap.md`
- 特点:
  - 直接消费 `--route-selection`
  - 自动识别当前 route anchor
  - 自动挑出:
    - best validation alternative
    - best special alternative
  - 自动生成可直接复用的:
    - `summary_line`
    - `tradeoff_line`

## 实跑验证
- 输入实验:
  - `D22`
  - `D26`
  - `D29`
- route:
  - `default_minimax`
- 输出:
  - `reports/eval/offline_mvp_route_recap_round1_1_d22_d26_d29_default_minimax/route_recap.md`

## 当前结果
- 当前 route anchor:
  - `D22`
- 自动生成的 recap 语义已经正确:
  - `summary_line` 会明确说明:
    - 当前 route 是 `default_minimax`
    - 当前 active reference anchor 是 `D22`
  - `tradeoff_line` 会明确说明:
    - `D29` 是最强 validation alternative，但相对 `D22` 要付出 special / `e_evt` / `z_art` 代价
    - `D26` 是最强 special alternative，但相对 `D22` 要付出 validation 代价

这一步的价值是:
- 后续阶段汇总不必再手写同一套“三锚怎么取舍”的说明
- 可以直接复用 route-aware recap 输出

## 当前结论
1. 三锚流程现在已经形成:
   - analysis
   - route policy
   - selector
   - init-experiment integration
   - final comparison
   - route-aware recap
2. 后续如果做实验复盘或阶段总结，优先使用 route recap，而不是手工重新组织 tradeoff 描述。

## 下一步建议
1. 暂不继续扩 recap 命令家族。
2. 若继续推进流程层集成，更值得把 route recap 直接接进阶段汇总或 handoff 文档流程。
