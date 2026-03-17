# 123. round1.1 `checkpoint anchor route governance` 报告

## 背景
到当前为止，项目里已经同时出现三类 route 口径：

1. official quick-screen / fixed handoff
2. pure long-horizon final-only route
3. long-horizon + synthetic checkpoint-anchor route

其中第 3 类在最近两轮被正式跑实了：
- matched20 shadow:
  - 通过 `D22 step20 anchor` 解决 horizon 不对称
- long-horizon late-stop review:
  - 通过 `D76 step150 anchor` 测试 checkpoint-selected late stop 是否应进入正式 route

问题已经不再是“能不能物化 checkpoint anchor”，
而是:
- 它应不应该被允许进入正式 route 候选集合

## 当前磁盘事实
### 1. official quick-screen 仍是 final-only 制度
- 当前 official quick-screen selector(`budget=0.05`) 输出:
  - `selected_policy = validation_strict`
  - `selected_anchor = D71`
- 它的制度角色一直是:
  - 正式 handoff / stage-report 的默认入口

### 2. matched20 shadow 允许 checkpoint anchor，是因为它在解决 horizon equalization
- `D22 step20 anchor` 的作用不是“挑一个更喜欢的 checkpoint”
- 而是:
  - 把 `D22(30step)` 拉回 `20step`
  - 与其他 `20step` 候选做公平 matched-horizon 比较

这里 checkpoint anchor 解决的是:
- horizon mismatch

### 3. `D76 step150 anchor` 的作用则完全不同
- 它不是拿来做 horizon equalization
- 而是拿来测试:
  - `D76` 的 late-stop 是否值得进入正式 route

而磁盘结果已经明确显示:
- 不引入 checkpoint anchor 时:
  - pure long-horizon minimax = `D76 step200`
- 一旦引入 `D76 step150 anchor`:
  - pure long-horizon minimax = `D33 step200`

这说明 checkpoint anchor 一旦进入正式候选集合，
它改变的已经不是“同一个制度下的公平性”；
而是:
- 候选空间本身
- 以及 minimax 的制度语义

## 关键区分
### A. horizon-equalization anchor
- 代表:
  - `D22 step20 anchor`
- 目的:
  - 补齐不同实验天然 horizon 不一致的问题
- 效果:
  - 让比较更公平
  - 不会把“checkpoint 选点策略”偷偷混进 route 制度里

### B. checkpoint-option anchor
- 代表:
  - `D76 step150 anchor`
- 目的:
  - 把某条轨迹内部的 checkpoint-selected late stop 升格成正式候选
- 效果:
  - 不只是展示 tradeoff
  - 而是直接改写:
    - leader 归属
    - minimax 归属
    - `budget_to_minimax_anchor`

解释:
- A 类 anchor 在解决:
  - 比较条件不对称
- B 类 anchor 在引入:
  - 新的 route option class

这两者不能用同一个制度默认对待。

## 当前正式建议
### 规则 1
- official quick-screen / fixed handoff / stage-report:
  - 默认只允许 natural final anchors
  - 不允许 checkpoint-option anchor 进入正式候选集合

### 规则 2
- matched-horizon shadow:
  - 允许 horizon-equalization anchor
  - 前提是它只用于补齐 horizon 对称性
  - 不把“checkpoint 选点偏好”混进制度语义

### 规则 3
- checkpoint-option anchor:
  - 默认只允许出现在:
    - checkpoint-selection
    - gate replay
    - special-push / late-stop option study
    - 诊断性 route comparison
  - 不默认进入:
    - official route
    - pure long-horizon default route
    - handoff / stage report 的默认 anchor 集

### 规则 4
- 若未来真的要让 checkpoint-option anchor 进入正式 route，
  必须把这件事显式升格为制度切换，
  而不是一次实验结论
- 至少要明确回答:
  1. 是否接受 route 候选从“每实验一个 final 点”变成“每实验多个 checkpoint option”
  2. 是否接受 minimax 语义因此变化
  3. 是否要给 checkpoint option 单独设 validation / control floors

## 对当前项目状态的直接落地
### 应保留的正式口径
- official:
  - 继续保持旧 quick-screen
- long-horizon default:
  - `D76 step200 = validation-first default`

### 应保留但只作为 option 的口径
- `D76 step150`
  - 只写成:
    - special-oriented late stop
  - 不写成:
    - 新默认 long-horizon anchor

### 应继续允许的 synthetic anchor 用法
- `D22 step20 anchor`
  - 继续用于 matched20 shadow

### 当前不应默认允许的 synthetic anchor 用法
- `D76 step150 anchor`
  - 不直接并入正式 long-horizon default selector

## 先说人话
- 不是所有 checkpoint anchor 都一样。
- `D22 step20` 这种是在补公平比较条件。
- `D76 step150` 这种是在往制度里新增“可选 checkpoint”这类新候选。
- 前者可以当 shadow 工具；
  后者如果不单独立规矩，就会把 route 口径越改越散。

## 当前阶段正式判断
1. synthetic checkpoint anchor 不是一律禁用。
2. 但它必须区分:
   - horizon-equalization
   - checkpoint-option
3. 当前项目只应默认接受前者进入 shadow / matched-horizon。
4. 当前项目不应默认接受后者进入正式 route / handoff / stage-report。

## 产物引用
- official quick-screen selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73_d74_d75_default_minimax/`
- pure long-horizon final-only:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_default_minimax/`
- long-horizon + `D76 step150` synthetic anchor:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
