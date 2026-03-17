# 143. offline MVP 结构敏感性与适用边界

## 背景
- `docs/140_round1_1_d87_outer_punctuation_zartretarget_lateretention_route_capture_report.md`
  已把当前 long-horizon 正式口径收敛到:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt checkpoint-option = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`
- `docs/142_old_long_horizon_experiments_recheck_report.md`
  又补齐了旧 `200-step` 实验的统一复核能力。
- 在此基础上，需要把一个此前只零散出现的前提正式写清:
  - 当前这些结论成立于“仓库现在这版 offline MVP 骨架”，
    不是对未来完整设计稿架构的跨结构证明。

## 先说结论

### 1. 当前 route 结论已经可以正式冻结
- 当前 handoff / stage report 已物化，且和阶段文档一致:
  - formal default/minimax = `D87 final`
  - validation-first reference = `D76 final`
  - special-first reference = `D82 final`
  - `zero_e_evt` strongest option = `D87 step150`
  - `zero_z_art` top floor = `D33 final`

### 2. 这些结论高度依赖当前 offline MVP 结构
- 当前仓库验证到的，
  主要是:
  - shared encoder 下
    `z_art / e_evt`
    是否能形成可观测控制作用
  - teacher consistency、outer supervision、targeted sampling、
    checkpoint review、route governance
    是否能把这些作用组织成稳定制度结论
- 当前没有验证到的，
  是未来完整设计稿里更强模块隔离后的行为上限。

### 3. 因而当前最准确的说法应是“两层结论”
- 第一层:
  - 对当前 offline MVP 骨架成立的实验结论
- 第二层:
  - 对未来完整系统仍待验证的结构假设
- 后续文档若不区分这两层，
  容易把“当前实现观察”误写成“跨结构定理”。

## 当前 offline MVP 的真实结构边界

### 1. 当前模型是 shared encoder + 双控制 head + 单次 fusion
- `OfflineMVPNoResidualModel` 当前结构是:
  - 输入两维 frame 特征
  - 共享 `encoder`
  - 从同一 hidden 预测 `z_art`
  - 从同一 hidden 预测 `event_logits`
  - 再把 `hidden / z_art_hidden / event_hidden`
    共同送入一次 `fusion`
  - 最后进入单个 `acoustic_head`
- 这意味着:
  - `z_art` 与 `e_evt` 都不是独立主支路
  - shared hidden 仍可能成为 strongest path
  - 当前消融观测到的是“控制路径被使用到什么程度”，
    不是“结构上绝不可能绕过控制路径”

### 2. `zero_z_art / zero_e_evt` 是控制消融，不是完整结构隔离证明
- 当前 ablation 方式是在 fusion 前把对应控制 hidden 置零。
- 它能证明:
  - 目标控制路径对当前输出存在可测影响
- 但不能证明:
  - shared encoder 不会以别的方式补回同类信息
  - 或未来换结构后同样结论仍然保持

### 3. `r_res` 目前仍未进入真实验证范围
- 当前训练入口明确要求:
  - `r_res` 必须关闭
- 这使当前 offline MVP 的结论更干净，
  但也意味着:
  - 设计稿里“受限残差是否会绕过主控制链”的核心风险，
    目前尚未进入实证阶段
- 因此:
  - 不能把当前结果写成“`r_res` 风险已被解决”
  - 只能写成“当前通过禁用 `r_res` 回避了该风险”

### 4. 真实已落地的是训练治理结构，不是完整模块化大系统
- 当前仓库已经强落地的，
  反而是以下治理层:
  - teacher consistency runtime
  - target special pool / sample gating
  - checkpoint series / special eval series
  - checkpoint selection / gate replay
  - anchor route analysis / selector
  - route-aware handoff / stage report
- 所以当前阶段真正稳定的，
  是“实验与 route 治理框架”；
  不是“最终架构模块都已实装完毕”。

## 哪些结论可视为当前骨架内已验证

### 1. `z_art / e_evt` 在当前骨架内都不是空变量
- 当前多轮 ablation 与 checkpoint series 已足以说明:
  - 去掉 `e_evt` 会造成稳定可观测退化
  - `z_art` 贡献在更长训练窗内会逐渐显现
- 因此至少对当前 shared-encoder MVP，
  两条控制路径都已进入“真实被使用”范围。

### 2. route/gov 结论在当前 anchor 集内已制度化
- 当前 selector 并不是口头总结，
  而是明确吃:
  - validation budget
  - special / `z_art` priority
  - `e_evt` / `z_art` floor
  来输出 route policy
- 因而:
  - `D76 / D82 / D87 step150 / D33 / D87`
    这一套角色分工
    可以视为当前 anchor 集上的正式制度结论

### 3. synthetic checkpoint option 已和 formal default 分离
- 当前 handoff / stage report 已明确:
  - natural final anchor 才能进入 formal default wording
  - synthetic checkpoint anchor 只能作为 option
- 这条区分现在已经是工具链规则，
  不是仅靠人工记忆维持。

### 4. old-family 的 late gate 逻辑已基本饱和
- `docs/142` 复核后，
  old `200-step` family 的 gate replay
  在 `late075` 下已基本收敛。
- 这意味着:
  - 继续围绕旧 family 做 late gate 名义变化，
    很难再产生高信息量结果

## 哪些结论仍然是结构敏感的

### 1. `D33` 仍掌握 `z_art` top floor，不等于“未来系统也会如此”
- 当前这只是:
  - 在 shared-encoder MVP、
    当前监督和当前指标定义下，
    `D33` 仍是 best `zero_z_art` floor
- 一旦结构变成:
  - 更强的分支隔离
  - 新的外层 supervision
  - 或真正接入 `r_res`
  这一角色完全可能重排

### 2. `D87 = default/minimax` 也不是跨结构真理
- 它成立于:
  - 当前 anchor 集
  - 当前 regret 定义
  - 当前 route selector contract
- 若未来:
  - anchor 集扩展
  - metric 定义变化
  - selector floor / budget contract 变化
  `default/minimax`
  也可能被重新改写

### 3. teacher consistency 的有效性仍是实验事实，不是代码保证
- 当前代码已经支持:
  - 多 teacher checkpoint
  - phase schedule
  - event / `z_art` / acoustic / fused_hidden consistency
  - special-pool sample gating
- 但这只能证明:
  - “我们有能力用 teacher consistency 训练”
- 不能证明:
  - “teacher 教的方向天然正确”

### 4. 当前没有证据证明 shared path 不会吞掉控制分工
- 现阶段更多是依靠:
  - 消融
  - special eval
  - route review
  间接观察 strongest path
- 仓库尚未提供:
  - 对 shared path / control path 竞争关系的直接仪表化

## 哪些问题尚未进入可验证范围

### 1. 完整设计稿里的 `r_res` 限权问题
- 尚未实装，不应提前下结论。

### 2. 更强生成器 / 声码器双分支分工
- 当前仓库没有对应实现，
  所以也没有对应验证。

### 3. 跨结构外推
- 不能把当前 offline MVP 的 anchor 结论，
  直接外推到:
  - 未来流式前端
  - 带残差版本
  - 或更复杂声学后端

## 已收口 family 与当前纪律

### 当前已不值得继续主打的 family / 旋钮
- late teacher source handoff
- late `z_art_weight`
- late `z_art_influence` retarget
- full-priority singleton exposure
- 旧 family 的 late gate / checkpoint-option 名义扩展

### 当前仍允许作为新实验立题的范围
- 只剩真正新的:
  - 更外层 `z_art` restoration / supervision 机制
- 并且必须遵守:
  - 先 quick-screen
  - 有信号再 matched / long-horizon
  - 不把 checkpoint-option 混写成 formal default

## 当前正式工作状态

### 当前可直接引用的 formal route
- official quick-screen:
  - 仍与 long-horizon 分离，不在本文改写
- full long-horizon:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt checkpoint-option = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`

### 当前应优先引用的 formal 文档
- `docs/140_round1_1_d87_outer_punctuation_zartretarget_lateretention_route_capture_report.md`
- `docs/141_system_assessment_response_to_temp_1_2.md`
- `docs/142_old_long_horizon_experiments_recheck_report.md`
- `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.md`
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_longwindow_final/handoff_document.md`
- `reports/stage_reports/offline_mvp_stage_report_round1_1_longwindow_final/stage_report.md`

## 最终口径
- 当前 offline MVP 已经进入“可以冻结 route、以 formal handoff/stage report 交接”的状态。
- 但这次冻结的是:
  - 当前 shared-encoder、no-`r_res`、single-fusion MVP 的制度结论
- 不是:
  - 对完整设计稿最终结构的全面证明
- 若后续继续开训练题，
  合理范围应被严格收窄到:
  - 是否存在新的、更外层的 `z_art` restoration 机制
  - 而不是继续在已收口 family 上做近邻微调
