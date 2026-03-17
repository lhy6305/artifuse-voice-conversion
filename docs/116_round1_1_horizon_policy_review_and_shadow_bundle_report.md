# 116. round1.1 `1.md 审查结论 + shadow bundle automation` 报告

## 背景
- 用户提供了 `1.md`，要求只读审查并判断是否接受调整。
- 该文档的核心主张是:
  - `step20` 只适合 early-horizon / quick-screen 问题
  - 如果要动摇长期 default anchor，应该补更长的 matched horizon
- 本轮同时把上一轮刚确认的 `matched20 shadow policy` 固化成可复用工具，
  避免后续每轮都手工拼:
  - checkpoint anchor
  - route-analysis
  - selector
  - final comparison
  - route recap

## 对 `1.md` 的审查结论
### 接受的部分
- 接受 `1.md` 的主轴判断:
  1. `step20` 的职责应限定在:
     - early-horizon
     - quick-screen
     - 公平比较早期轨迹
  2. 不应把 `step20` 单独解释成:
     - 长期主线裁决
     - 最终 default anchor 裁决
  3. 需要把:
     - quick-screen question
     - long-horizon question
     - selector / official handoff question
     明确拆开

### 不原样接受的部分
- 不接受把 `500` 写成默认标准 horizon。
  - 更合理的口径是:
    - `matched long horizon`
    - 当前默认写成 `200+`
    - 必要时再更长
- 也不接受把规则写成:
  - “任何挑战官方 default anchor 的结论都必须补 matched200/500”
- 更精确的收缩版是:
  - 只有当结论要改写官方 fixed handoff 时，
    才必须补 matched long horizon 佐证

### 最终采纳口径
- `step20/20-30` 只负责 quick-screen
- `matched long horizon(200+)` 负责:
  - 诊断是否存在 horizon advantage
  - 或在必要时验证是否应改写官方 fixed handoff
- 当前官方制度继续保持旧 quick-screen，
  但从现在开始并行跟踪 `matched20 shadow policy`

## 新增工具
- 新命令:
  - `build-offline-mvp-matched-horizon-shadow`
- 代码位置:
  - `src/v5vc/horizon_policy_shadow.py`
  - `src/v5vc/cli.py`

### 功能
- 自动完成以下整套动作:
  1. 从原实验物化 checkpoint anchor
  2. 生成 matched-horizon `anchor_route_analysis`
  3. 按多个 validation budget 生成:
     - selector
     - final comparison
     - route recap

### 当前实跑验证
- bundle 产物:
  - `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69/`
- 输入为:
  - `D29 / D33 / D60 / D68 / D69`
  - 外加从 `D22` 物化出的 `step20 anchor`
- 预算:
  - `0.05`
  - `0.13`

验证结果与上一轮手工结果一致:
- `budget=0.05`
  - `validation_strict = D29`
- `budget=0.13`
  - `default_minimax = D68`

## 解释
- 这轮真正推进的不是新训练，
  而是把 horizon policy 的结论从“这次手工分析”变成“之后每轮都能机械复现的 shadow workflow”。
- 这样后续每次只要出现新主线候选，
  都能直接产出:
  - 官方 quick-screen 口径
  - matched20 shadow 口径
  并保持完全同构的比较方式。

先说人话:
- `1.md` 的大方向是对的，
  但里面把 long horizon 说得太死了。
- 我们现在采纳的是它的制度思想，
  不是字面上的 `500 step 必选论`。
- 同时，这套思想已经被固化成工具，
  后面不用再靠人工抄命令。

## 当前阶段正式结论
1. `1.md` 的核心制度判断被接受，但按当前项目状态做了收缩修正。
2. 当前不把 `500` 设为默认标准，而采用:
   - quick-screen
   - matched long horizon(`200+`)
   的两层口径。
3. `matched20 shadow policy` 已经从手工流程升级为一键化命令。
4. 后续每轮新主线候选都应使用这套 shadow bundle，而不是再手工拼 route 产物。

## 下一步
- 继续保持:
  - 官方 fixed handoff = 旧 quick-screen
  - shadow policy = matched20
- 后续每条新主线候选:
  - 先跑正常 quick-screen
  - 再补 `build-offline-mvp-matched-horizon-shadow`
- 只有当 shadow policy 连续稳定指向同一条新主线，
  才再讨论是否补 matched long horizon(`200+`) 去挑战官方 fixed handoff
