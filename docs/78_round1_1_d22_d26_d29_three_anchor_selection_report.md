# `round1.1 / D22+D26+D29 / three-anchor selection analysis` 报告

## 背景
- 在 `D22 / D26 / D29` 已经形成三锚结构之后，当前缺的不是再跑一个很近的小变体，
  - 而是把这三个 final anchor 的职责边界正式定清楚。
- 本轮目标:
  - 不再凭肉眼读表
  - 用正式分析产物回答:
    - 哪个 anchor 是 validation leader
    - 哪个 anchor 是 special / control leader
    - 如果只能保留一个默认参考点，哪个是 least-worst final anchor
    - validation budget 和 dual-control floor 一旦变化，anchor 应该如何切换

## 本轮产物
- 新增正式命令:
  - `analyze-offline-mvp-anchor-selection`
- 分析输出:
  - `reports/eval/offline_mvp_anchor_selection_round1_1_d22_d26_d29/anchor_selection_analysis.json`
  - `reports/eval/offline_mvp_anchor_selection_round1_1_d22_d26_d29/anchor_selection_analysis.md`
- 输入 experiment metrics:
  - `EXP-20260315-039 / D22`
  - `EXP-20260315-043 / D26`
  - `EXP-20260315-045 / D29`

## 关键结论

### 1. 三锚没有 joint final winner，而是各赢一项
- `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`
  - 当前三锚里 validation 最强
- `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`
  - 当前三锚里 final special 与 `z_art` 最强
- `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
  - 当前三锚里 `e_evt` 最强

这说明:
- 现在已经不能再沿用旧口径把 `D22` 叫做“validation-oriented anchor”
- 更准确的结构应该是:
  - `D29 = validation anchor`
  - `D26 = special / z_art anchor`
  - `D22 = e_evt-leading guarded anchor`

### 2. 如果只能保留一个默认参考点，`D22` 是 minimax anchor
- 正式分析里的 normalized regret 显示:
  - `D22 max_regret = 0.410339`
  - `D26 max_regret = 1.0`
  - `D29 max_regret = 1.0`
- 也就是说:
  - `D22` 虽然不是任何单一指标的全局冠军
  - 但它是三锚里 least-worst 的 final reference

先说人话:
- `D29` 太偏 validation
- `D26` 太偏 special / `z_art`
- `D22` 是当前最像“默认站位”的折中点

### 3. validation budget switchpoint 已经很清楚
- 以 `D29` 的 validation 为基准:
  - `budget = 0.0`
    - 只有 `D29` 可选
  - `budget = 0.047019`
    - `D22` 才进入可选集
    - 且在这个 tight budget 下:
      - best special = `D22`
      - best `e_evt` = `D22`
      - best `z_art` = `D22`
      - best minimax = `D22`
  - `budget = 0.126723`
    - `D26` 才进入可选集
    - 从这一步开始:
      - best special = `D26`
      - best `z_art` = `D26`
      - best `e_evt` 仍是 `D22`
      - best minimax 仍是 `D22`

这条线的解释非常直接:
- 只要 validation budget 很紧，默认就不该碰 `D26`
- `D26` 只有在你明确接受大约 `+0.126723` 的 validation 代价时，才值得进入正式候选

### 4. dual-control floor 下，`D22` 与 `D26` 是互斥强锚
- 以 `D22` 自己的 floor:
  - `e_evt >= 3.299035`
  - `z_art >= 0.438936`
  - 只有 `D22` 自己还能满足
- 以 `D26` 自己的 floor:
  - `e_evt >= 3.27265`
  - `z_art >= 0.460259`
  - 只有 `D26` 自己还能满足

这说明:
- 当前不存在一个 final anchor 同时覆盖 `D22` 级 `e_evt` 与 `D26` 级 `z_art`
- 所以下一步若继续训练，不该再幻想用一个很小的 cross-anchor tweak 就把这两个 floor 自动并起来

## 结论更新
1. `D29` 正式升格为当前 teacher-consistency family 的 validation anchor。
2. `D26` 继续作为 special / `z_art` anchor。
3. `D22` 不再沿用“validation-oriented”旧标签，改记为:
   - `e_evt-leading`
   - 同时也是当前三锚里的 minimax default anchor。
4. 三锚 selection 现在可以按目标直接做:
   - 要最强 validation: 选 `D29`
   - 要最强 special / `z_art`: 选 `D26`
   - 要最稳妥默认参考点: 选 `D22`

## 下一步建议
1. 不再优先继续做近邻 cross-anchor 小变体。
2. 若继续训练，应围绕这三锚里某一个明确目标来设计新 target shape 或 selector，而不是再试图用一个模糊中间点一次性全拿。
3. 若继续分析，则更值得做:
   - 面向三锚的正式 route selector / reporting policy
   - 而不是继续手工沿用过时的 anchor 标签
