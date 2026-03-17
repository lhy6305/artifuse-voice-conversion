# 115. round1.1 `quick-screen horizon policy` 决策报告

## 目的
- 经过 `D68 / D69` 与 `matched20` 之后，
  当前真正需要收口的已经不是某个单独实验，
  而是:
  - quick-screen selector 到底按什么 horizon 比
  - 当前 `validation budget = 0.05` 是否还适配这个比较制度

## 当前可选制度
### 方案 A: 保持当前不对称 quick-screen
- 代表 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_default_minimax/`
- 当前结果:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`
- route recap:
  - `reports/eval/offline_mvp_route_recap_round1_1_d22_d29_d33_d60_d68_d69_default_minimax/`

### 方案 B: 迁移到 matched20，但仍保留 `budget = 0.05`
- 代表 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`
- 当前结果:
  - `selected_policy = validation_strict`
  - `selected_anchor = D29`
- route recap:
  - `reports/eval/offline_mvp_route_recap_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`

### 方案 C: 迁移到 matched20，并把 budget 放宽到 `0.13`
- 代表 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_budget013/`
- 当前结果:
  - `selected_policy = default_minimax`
  - `selected_anchor = D68`
- route recap:
  - `reports/eval/offline_mvp_route_recap_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_budget013/`

## 三套口径的核心差异
### 方案 A
- summary:
  - 当前 route 仍是 `D22`
- tradeoff:
  - 相对 `D22`，
    `D29` 是更强 validation 备选，
    `D69` 是更强 raw special 备选，
    `D33` 是更强 `e_evt / z_art` 备选
- 优点:
  - 延续现有 handoff 口径
  - 不需要立即改 stage-report / handoff 制度
  - `budget = 0.05` 仍有明确语义
- 缺点:
  - `D22` 的 minimax 地位包含明显 horizon advantage
  - 它不是公平 `20 step` 比较下的赢家

### 方案 B
- summary:
  - 一旦 horizon 拉平但 budget 不变，
    selector 会直接塌成 `D29`
- tradeoff:
  - 相对 `D29`，
    `D22-step20` 只带来很小的 control 回升，
    而 `D69 / D33` 虽有明显 special/control 优势，
    但都超出当前 budget
- 优点:
  - 比较制度公平
  - 能暴露当前预算到底有多紧
- 缺点:
  - 会把当前三锚点结构直接压成 validation-first
  - 这不是我们想要的 route 语义

### 方案 C
- summary:
  - 在 matched20 下，
    若接受 `budget >= 0.12514`，
    minimax 会切到 `D68`
- tradeoff:
  - 相对 `D68`，
    `D29` 只是在 validation 上更强，
    但会明显损 special/control；
    `D69` 是极小幅更强 special，
    但 validation / z_art 略回吐；
    `D33` 仍是更强 `e_evt / z_art`
- 优点:
  - 比较制度公平
  - minimax 不再依赖 `D22` 的 30-step 优势
  - `D68` 作为 post-`D59` 新主线的 minimax 候选，解释是自洽的
- 缺点:
  - 需要同时改两件制度:
    - horizon
    - validation budget
  - route 刷新会混合:
    - “模型更强”
    - 与 “制度改写”
    两种来源

## 我对这三套制度的判断
- 方案 B 不值得采用。
  - 它唯一证明的是:
    - 当前 `budget = 0.05` 对 matched20 过紧
  - 但它无法提供我们真正想要的 minimax route
- 方案 C 在分析上是成立的，
  但现在直接升为官方制度还太早。
  - 原因不是 `D68` 不够强，
    而是:
    - 一次性同时改 `horizon + budget + minimax anchor`
    变化面太大
  - 这会让后续很难分辨:
    - 是 `D68` 真正坐稳了
    - 还是 selector contract 被重写了
- 因此当前最稳妥的执行建议是:
  - 官方制度先保持方案 A
  - 同时把方案 C 作为 `shadow policy`
    并行跟踪

## 推荐执行方案
### 正式口径
- 暂时保持:
  - `D29 = validation`
  - `D22 = default_minimax`
  - `D33 = special / e_evt / z_art`
- 也就是说:
  - 继续沿用当前不对称 quick-screen 作为 fixed handoff 口径

### shadow 口径
- 从现在开始，
  每一轮新主线候选都同步追加:
  - `matched20 route-analysis`
  - `matched20 selector @ budget 0.05`
  - `matched20 selector @ budget 0.13`
- 当前 shadow 结论暂记为:
  - `matched20@0.05 -> D29`
  - `matched20@0.13 -> D68`

### 迁移触发条件
- 只有当下面两件事同时成立，
  才建议把官方制度从方案 A 切到方案 C:
  1. `matched20 minimax` 连续稳定指向同一条新主线，
     而不是在 `D60 / D68 / D69` 之间来回摆
  2. 团队接受把 default validation budget
     从 `0.05` 上调到至少 `0.12514` 这一量级

## 结论
- 当前不建议立即把官方 selector 改成 matched-horizon。
- 但也不能再把现有 `D22 = default_minimax` 解释成“公平 horizon 下仍然最优”。
- 最合理的下一阶段制度是:
  - 官方继续旧 quick-screen
  - shadow 并行跟踪 matched20
  - 等 matched20 新 minimax 和新 budget 一起稳定后，再决定是否迁移

先说人话:
- 现在不是该立刻换冠军的时候，
  而是该承认比赛规则本身有偏置。
- 最稳的做法不是马上改规则，
  而是先让新规则并行跑几轮，
  看它是不是稳定地把 `D68` 这条线推成真正的新 minimax。
