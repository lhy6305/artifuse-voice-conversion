# 141. 系统评估：对临时文档 `1.md` / `2.md` 的回应

## 评估范围
- 本文用于恢复当前工作状态，并回应根目录临时文档 `1.md` 与 `2.md` 提出的建议、问题。
- 本次只做评估，不改业务代码。
- `1.md`、`2.md` 不作为正式长期文档维护对象，因此不直接修改它们。

## 当前工作状态恢复

### 1. 当前阶段真实停点
- 当前最新正式实验已经推进到 `D87`。
- 从最新阶段文档看，当前 long-horizon 口径已收敛到以下角色分工：
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt` checkpoint-option = `D87 step150`
  - `zero_z_art` = `D33`
  - default / minimax = `D87`
- 这说明：
  - `D87` 已经把一部分 late-window dual-control 形状保进 final，并正式改写了 long-horizon 的 default / minimax。
  - 但 `z_art` top floor 仍未从 `D33` 手里转移。

### 2. official 与 long-horizon 仍是两套制度
- 当前不能把 long-horizon 结果直接写成 official 默认。
- official quick-screen 口径仍未被推翻，不能与 matched20 shadow、full long-horizon 混写。

### 3. 仓库当前不是“完整设计稿系统”，而是极简 offline MVP 研究骨架
- 当前主模型仍是 `OfflineMVPNoResidualModel`。
- 从代码现实看：
  - 还没有 `r_res` 分支的真实实现；
  - 还没有设计稿里那种多支路声码器 / 双分支结构验证；
  - 当前主要是在一个共享 trunk 上，验证 `z_art`、`e_evt`、teacher consistency、outer supervision、route governance 是否能形成可辨别行为。
- 所以现在很多结论本来就只能写成：
  - “对当前 offline MVP 骨架成立”
  - 不能写成“对最终系统结构已经被证明成立”

## 对 `1.md` 的回应

### 结论
- `1.md` 的核心判断成立：
  - 当前文档体系不把“几层几宽”的网络结构当主角，这是预期中的；
  - 但“结构会改变结论”这点也成立，而且对当前仓库尤其成立。

### 为什么成立
- 当前代码里的结构事实是：
  - `z_art` 和 `e_evt` 都来自同一个 shared encoder；
  - 然后通过单次 fused control 融合进入 acoustic head；
  - `zero_z_art` / `zero_e_evt` 消融，是在 fusion 前把对应控制路径置零；
  - 这说明当前控制变量的生效，更多依赖：
    - 融合位置
    - loss 设计
    - teacher consistency
    - 结构化 auxiliary
    - route / checkpoint 治理
  - 而不是依赖一个已经被严格模块隔离的大系统。
- 因此：
  - 当前阶段不强调“大 backbone 细节”是合理的；
  - 但后续若把结构换掉，很多结论确实会重排。

### 需要补充的更准确表述
- 现在最准确的说法不是：
  - “方案不关心结构”
- 而是：
  - “当前方案更关心信息流结构、训练治理结构、route 选择结构”
- 同时还必须补一句：
  - “这些结论目前主要适用于当前 offline MVP 骨架，不应自动外推到未来完整架构”

## 对 `2.md` 的回应

## 一、`2.md` 对“结构敏感性”的担心是对的，而且比文档里写得还强

### 1. `z_art / e_evt / r_res` 不是平级自由输入
- 这条在设计稿层面成立。
- 但在当前代码层面，只成立了一半：
  - `z_art / e_evt` 的确被显式拆出，并能做消融；
  - `r_res` 目前根本还没有实现，只存在于配置门禁和设计口径里。
- 所以当前不能写成：
  - “`r_res` 已被结构上限权验证”
- 更准确的写法应是：
  - “当前 offline MVP 通过彻底禁用 `r_res`，回避了该问题；真正的 `r_res` 限权仍是后续结构风险”

### 2. teacher 伪标签是否足够稳定可学
- 当前代码里 teacher consistency 是真实存在的：
  - 支持 checkpoint teacher；
  - 支持 schedule phase；
  - 支持 event / z_art / acoustic / fused_hidden 多项一致性；
  - 支持基于 target special pool 做 sample gating。
- 但这并不等于 teacher 偏差已经被解决。
- 现实上只能说：
  - 仓库已经提供了“teacher 一致性训练能力”
  - 但“teacher 是否在教对的东西”仍然是实验问题，不是代码保证

### 3. “backbone 会不会吞掉控制分工”在当前代码里没有被硬性排除
- 当前模型是共享 encoder + 两个控制 head + 单次 fusion。
- 这意味着：
  - `z_art / e_evt` 并没有独立主支路；
  - shared hidden 本身仍然可能成为 strongest path。
- 这正是 `2.md` 提醒要追问的重点。
- 也就是说：
  - 当前代码没有把“shared path 不能绕过控制变量”焊死；
  - 只是通过消融、aux 和 route 分析去观察是否真的发生了绕路

### 4. “声码器双分支是否真的执行骨架/事件分工”当前根本还没到可验证阶段
- `2.md` 这条提醒很重要。
- 但对当前仓库要补一句现实说明：
  - 现在还没有那个层级的生成器 / 声码器分支实现；
  - 所以这不是“已验证但敏感”，而是“尚未进入可验证范围”

### 5. route / anchor 结论是“制度结论”还是“模型结论”
- 这条 `2.md` 说得对。
- 当前仓库里这件事已经部分被工程化了：
  - route analysis 会显式算 validation / special / `zero_e_evt` / `zero_z_art` / minimax；
  - selector 会显式吃 budget、priority、floor 约束来选 policy。
- 所以这里不是空口提醒，而是已经有代码支持的治理层。
- 但仍要强调：
  - 这些治理结果是建立在当前 anchor 集、当前指标定义、当前 selector contract 上的；
  - 不是跨结构真理

## 二、`2.md` 建议追问的 12 个问题里，哪些已经部分回答，哪些还没被系统化

### 已经部分回答的
- “哪些结论是 route/gov 规则造成的，哪些是模型造成的”
  - 已经有 route analysis / selector 代码支撑。
- “哪些 family 已经不值得继续”
  - 最新阶段文档已经明确：
    - 不应继续主打 late teacher source handoff
    - 不应继续主打 late `z_art_weight`
    - 不应继续主打 late `z_art_influence` retarget
    - 不应继续主打 full-priority singleton exposure
- “当前下一步更像什么问题”
  - 文档已经基本收敛到：
    - 更外层 `z_art` restoration / supervision 机制

### 还没有被系统化落盘的
- 结构假设表
  - 现在散在设计稿、实验报告、代码细节里，但没有一张统一表。
- 结构无关 / 结构敏感结论分层表
  - 现在没有正式总表。
- family 收口表
  - 当前是文档里分散写“该停什么”，还没形成单表。
- 每轮实验的“我要打哪条 route”声明模板
  - 现在大多靠实验报告正文表达，还不是强制模板字段。
- strongest path 的直接观测
  - 目前更多是间接从消融和 route 结果推断，还没有单独仪表化。

## 三、对 `2.md` 的总回应
- `2.md` 不是在挑刺，而是在指出当前项目最该正式化的一层：
  - 结构适用边界
  - route 与 governance 的制度边界
  - family 收口纪律
- 这些建议大方向都应采纳。
- 但要注意按当前实现状态区分：
  - 有些问题是“当前已经进入验证，但结论敏感”
  - 有些问题是“当前还没实现到那个层级，不能假装已经验证”

## 有没有立刻需要检测或调整的部分

### 结论
- 有，而且是流程与口径层面的“立刻需要”，不是再去改模型代码。

### 1. 立刻需要严格执行 eval 串行写回纪律
- 最近已明确踩坑：
  - 多个 eval 命令并行回写同一个 `experiment metrics` 文件，会出现 last-writer-wins 覆写。
- 这不是小问题；
  - 会直接让 checkpoint review、route 分析结论失真。
- 因此后续若还继续评估：
  - 所有会回写同一个 metrics 文件的 eval，必须串行执行。

### 2. 立刻需要固定 long-horizon late-stop 的默认检查口径
- 对只有 `step50 / 100 / 150 / 200` 的实验：
  - `late_step_ratio = 0.8` 会把 late window 错缩到只剩 final。
- 这会误杀真实存在的 `step150` checkpoint-option。
- 所以后续这类复核必须显式使用：
  - `late_step_ratio = 0.75`

### 3. 立刻需要冻结并统一书写当前四套口径
- 至少要严格区分：
  - official quick-screen
  - matched20 shadow
  - full long-horizon
  - checkpoint-option
- 当前最容易再次出错的，不是模型本身，而是把这些制度口径混写。

### 4. 若继续新实验，题目必须升级，不能回到旧旋钮微调
- 这是当前最重要的研发纪律。
- 因为从 `D80` 到 `D83`，以及 `D84` 到 `D87`，已经把大量旧轴跑得很干净。
- 若继续训练实验，新的立题必须直接回答：
  - 怎样补 `z_art` top floor，而不是再去重复争夺 default/minimax 或 family 内近邻 tradeoff

### 5. 立刻值得补一份正式文档，但不是改代码
- 最值得补的不是新实验，而是一份统一的“结构敏感性与适用边界”文档，至少包括：
  - 当前 offline MVP 已验证边界
  - 尚未实现边界
  - 当前正式 route 口径
  - 已收口 / 停止投入的 family
  - 下一轮若继续实验，允许的立题范围

## 本次评估后的直接判断

### 1. 当前项目不是“还没方向”，而是已经到了应当收口整理的阶段
- 当前 long-horizon 已经有制度级收敛。
- 真正剩下的问题已经被压缩到：
  - `z_art` top floor 仍归 `D33`

### 2. `1.md` 和 `2.md` 的核心质疑都成立
- 特别是：
  - 当前结论高度依赖结构和训练制度；
  - 不能把当前实验结论写成跨结构真理。

### 3. 目前最该做的不是立刻继续试新旋钮
- 更合理的是：
  - 先把当前结构敏感性、route 口径、family 收口状态写清；
  - 再决定是否值得继续开一轮真正新的 `z_art` restoration 问题

## 附：本次评估所依据的关键现实
- 最新实验与阶段结论主要依据：
  - `docs/134_round1_1_stage_progress_route_assessment_report.md`
  - `docs/139_round1_1_d86_outer_punctuation_zartretarget_long_horizon_report.md`
  - `docs/140_round1_1_d87_outer_punctuation_zartretarget_lateretention_route_capture_report.md`
- 当前模型实现主要依据：
  - `src/v5vc/offline_mvp/model.py`
  - `src/v5vc/offline_mvp/losses.py`
  - `src/v5vc/train_entry.py`
  - `src/v5vc/anchor_route_analysis.py`
  - `src/v5vc/anchor_route_selector.py`
