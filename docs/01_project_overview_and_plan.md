# 项目总览与实施计划

## 项目目标摘要
基于 `initial_design.md`，当前项目目标是构建一个兼顾离线高质量与在线低延迟的工业化变声系统。核心控制链为：

- 低维伪发音潜变量 `z_art`
- 事件向量 `e_evt`
- 基础声学控制 `F0 / vuv / aper / E`
- 被严格限权的残差码 `r_res`

设计稿明确要求避免两类失败：

- 把系统做成“披着可解释外壳的神经编解码器”
- 在在线模式里堆叠过重模块，导致延迟和稳定性不可控

## 当前仓库结构
截至 2026-03-14，仓库内可见结构如下：

- `initial_design.md`
  - V5.1 主设计稿，定义总体架构、训练阶段、推理链路和验收方向。
- `initial_design_judg.md`
  - 风险与去魅评估文档，用来矫正过度乐观判断，明确真正高风险项。
- `python.exe`
  - 本项目唯一允许使用的 Python 解释器。
- `data_convert/`
  - 当前原始数据目录。
- `data_convert/dataset_ly65_raw.wav`
  - 单个大体积音频文件。
- `data_convert/dataset_firefly_raw/`
  - 大量 `.wav/.lab` 配对样本，后续可作为预处理与清单构建输入。
- `docs/`
  - 持续维护的协作文档目录。
- `manage.py`
  - 当前统一命令入口，后续脚本通过该入口调用。
- `src/v5vc/`
  - 项目源码目录。
- `configs/`
  - 长期配置与配置模板目录。
- `reports/`
  - 正式保留的扫描结果、实验记录和评估报告目录。
- `tmp/`
  - 明确标记的临时文件目录。

## 当前数据集说明
- `data_convert/dataset_firefly_raw/`
  - 目标说话人的高质量音频数据。
  - 来源为游戏提取。
  - 每个 `.wav` 对应一个 UTF-8 无 BOM 编码的同名 `.lab` 文本文件。
  - 文本保留标点符号，后续预处理不能默认去标点，需先统计再决定策略。
- `data_convert/dataset_ly65_raw.wav`
  - 源说话人音频，即用户本人办公场景录音。
  - 录音已尽量保证清晰，但存在大量静音片段。
  - 可能夹杂少量突发杂音，后续需专项统计静音占比与异常片段。

## 从设计文档提炼出的落地原则
### 必须优先验证的结论
- 无残差主干必须先能说清楚，残差支路只能后加。
- 离线 MVP 要先证明 `z_art + e_evt + F0/vuv/aper/E` 这条主链有效。
- 在线流式前端是第二阶段重点，不应在第一阶段就追求全量在线闭环。
- Teacher 伪标签只是训练信号，不是真实物理真值，必须配套置信度与过滤机制。
- 存在明显取舍的方案必须先做数据收集和优缺点报告，再交由用户确认。

### 不能过早承诺的结论
- 不能先假定 8 到 12 维 `z_art` 一定足够。
- 不能先假定低自由度目标校准足以还原细腻个体音色。
- 不能先假定高频隔离残差就能彻底阻断音色泄露。

## 代码落地优先级
以下顺序按“对整个项目成败影响最大”排序，而非按论文章节顺序排序。

### P0. 工程骨架与可恢复文档
目标：
- 建立目录结构、配置入口、命令入口、日志与实验记录规范。
- 明确所有脚本只能使用根目录 `python.exe`。
- 为后续数据处理、训练、评估提供统一命令模式。

验收标准：
- 有明确的代码目录规划与命令入口。
- 文档能让新接手者在无对话上下文情况下恢复工作。

### P1. 数据清单与预处理管线
目标：
- 扫描 `data_convert` 下现有原始音频和标签。
- 生成统一 manifest。
- 明确采样率、切分、归一化、标签配对和异常样本记录。

原因：
- 没有稳定的数据层，后续 Teacher、Student、Vocoder 都无法可靠推进。

验收标准：
- 可重复运行的数据扫描脚本。
- 清晰的 manifest 输出格式。
- 异常样本、缺失标签、长度异常都有日志。

### P2. 评估与回归基线
目标：
- 在真正训练模型前，先建立最小评估框架和实验记录模板。
- 把“无残差主干是否成立”的验证条件写成可执行的检查项。

原因：
- 风险文档强调，中间控制变量可能“名义存在但实际没被用到”，没有评估框架就无法识别。

验收标准：
- 有固定实验记录格式。
- 有针对 `z_art`、`e_evt`、`r_res` 的消融检查位。
- 能记录延迟、样本质量、标签覆盖率等基础指标。

### P3. 离线 MVP 主干
目标：
- 先做离线模式。
- 构建不含 `r_res` 的主干控制路径，验证 `z_art + e_evt + F0/vuv/aper/E` 是否能支撑基本可懂度和稳定性。

原因：
- 这是整个方案最关键的生死线。

验收标准：
- 在无残差条件下，输出可懂且稳定。
- 去掉 `z_art` 或 `e_evt` 后有可观测退化。
- 结果能沉淀为可复现实验记录。

### P4. Teacher 与伪标签置信度机制
目标：
- 为离线 MVP 补足可训练监督链路。
- 特别关注辅音、爆破和高非周期段是否被过度降权。

验收标准：
- 伪标签产出流程可重复。
- 置信度过滤逻辑有统计输出。
- 能单独检查元音段和辅音段保留率。

### P5. 流式前端与 Student
目标：
- 在离线主干成立后，再推进统一流式前端。
- 将多个串行模块合并为共享流式编码器与 Student 控制头。

验收标准：
- 在线前端能输出基础控制量和共享表示。
- 延迟、吞吐和稳定性有独立记录。

### P6. 残差支路与反捷径约束
目标：
- 仅在主干成立后引入 `r_res`。
- 同步做遮盖、消融和泄露检测。

验收标准：
- 去掉 `r_res` 时不允许整句崩溃。
- `r_res` 不应恢复出过强的说话人或完整内容信息。

### P7. 目标说话人校准与产品化封装
目标：
- 补齐 `s_spk / s_geom / α` 校准流程。
- 再考虑多目标切换、服务化和并发。

验收标准：
- 校准流程稳定可重复。
- 多目标切换无需重训主模型。

## 当前任务进度
截至 2026-03-14，当前已完成：

- 已阅读 `initial_design.md`
- 已阅读 `initial_design_judg.md`
- 已提炼当前落地顺序和高风险验证点
- 已建立文档基线与恢复入口
- 已补充目录管理与方案决策规范
- 已补充当前数据集说明
- 已建立工程目录骨架和统一命令入口
- 已实现首版数据扫描脚本
- 已生成首版 manifest 与数据扫描报告
- 已实现首版预处理管线
- 已生成 round1 目标样本清洗结果、源录音切分结果和峰值试听片段
- 已根据人工试听反馈将异常峰值规则固化进预处理配置
- 已加入源片段边界静区过滤规则
- 已生成 round1 标准训练 manifest
- 已建立评估基线模板与实验记录模板
- 已实现 round1 数据完整性检查命令并通过检查
- 已初始化第一份正式实验记录
- 已实现离线 MVP 基线评估命令并完成首轮评估
- 已实现离线 MVP 训练 dry-run 入口并生成训练计划
- 已实现真实数据加载、词表构建与无残差模型前向 dry-run
- 已实现首版无残差模型、损失函数、优化器与单步训练闭环
- 已完成首个真实单步训练、checkpoint 落盘、step log 落盘和实验 metrics 回写
- 已实现最小多步训练循环、固定验证切片与周期 checkpoint
- 已完成首个 3 step 真实训练运行并产出训练历史与验证历史
- 已实现训练开始时间、结束时间、总耗时和 step 耗时落盘
- 已实现大规模训练前置校验门禁，要求引用已成功的小规模训练实验
- 已验证训练命令会在标准输出打印时间信息
- 已通过受控失败验证确认大规模训练门禁会拒绝无前置实验的执行
- 已实现 round1 拆分分析命令，并产出正式候选方案报告
- 已物化用户确认的 `hybrid_stratified_blocked` 正式 split
- 已验证训练入口读取正式 split，而不是尾部切片
- 已实现 `target_special_eval` 独立评估命令并回写实验 metrics
- 已实现 offline MVP 的 `z_art / e_evt` 控制消融评估命令
- 已完成与新控制融合结构兼容的小规模训练并产出新 checkpoint
- 已完成首轮正式消融评估并确认 `e_evt` 对当前输出与损失有实质影响
- 已实现 `target_special_eval` 的模型级评估命令并完成首轮 checkpoint 评估
- 已完成 20 step 更长小规模训练，并确认 `z_art` 在更晚 checkpoint 上开始体现稳定 loss 退化
- 已实现离线 MVP 训练的固定 seed 与可选 shuffle 采样能力
- 已实现多 checkpoint 系列消融汇总命令，并完成首轮 step5/10/15/20 趋势验证
- 已完成顺序采样与 seeded-shuffle 的对比决策报告，等待用户拍板默认方案
- 已收到用户拍板，默认训练采样方案切换为 seeded-shuffle
- 已完成默认 seeded-shuffle 模板的小规模验证，确认默认入口生效
- 已完成大规模训练配置与耗时边界报告，等待用户选择保守或激进路线
- 已收到用户拍板，直接进入 `500 step` large_scale 训练路线
- 已完成首个 `500 step` large_scale 训练，并补齐 checkpoint-series 与 final special_eval

当前未开始：

- 训练数据标准化规则的二轮调参
- latency 实测逻辑

## 当前开发计划
当前开发计划已从 `P0/P1` 转入 `P2/P3` 过渡阶段，重点是把离线无残差 MVP 从单步闭环推进到最小可训练版本。

1. 已完成：建立清晰目录结构。
2. 已完成：放置统一命令入口和基础包结构。
3. 已完成：实现数据扫描脚本，产出首版 manifest 与统计报告。
4. 已完成：检查目标数据集的配对完整性、文本编码和文本分布。
5. 已完成：检查源说话人录音的时长、静音占比和基础音频参数。
6. 进行中：将观察结果回写文档，并向用户汇报需要决策的预处理方案分歧。
7. 已完成：根据已确认方案，实现数据清洗和 manifest 标准化管线。
8. 已完成：用户确认当前边界静区过滤强度可接受。
9. 已完成：生成 round1 标准训练 manifest。
10. 已完成：建立评估基线模板和实验记录模板。
11. 已完成：补数据完整性检查与实验记录初始化流程。
12. 已完成：搭离线 MVP 的评估代码骨架。
13. 已完成：搭离线 MVP 的训练 dry-run 入口。
14. 已完成：让训练 dry-run 真实读取数据并跑通模型前向。
15. 已完成：把 scaffold 过渡到真实损失、优化器和单步训练循环。
16. 已完成：验证 checkpoint、step log 和实验 metrics 三处产物一致。
17. 已完成：从单步训练过渡到多步训练和最小验证流程。
18. 已完成：为训练计划、step log 和实验 metrics 增加时间记录。
19. 已完成：为大规模训练增加前置小规模实验门禁。
20. 已完成：产出 round1 训练/验证拆分候选方案报告。
21. 已完成：用户确认并落地 `hybrid_stratified_blocked` 正式 split。
22. 已完成：为 `target_special_eval` 增加独立数据级评估入口。
23. 已完成：将 `z_art / e_evt` 消融入口接入正式评估流程。
24. 已完成：将模型级 `target_special_eval` 接入评估流程。
25. 已完成：拉长小规模训练步数并确认 `z_art` 退化开始显现。
26. 已完成：接入训练 seed 与 shuffle 能力，并完成首轮 seeded-shuffle 小规模实验。
27. 已完成：接入多 checkpoint 系列消融汇总命令。
28. 已完成：整理顺序采样与 seeded-shuffle 的默认方案决策报告。
29. 已完成：用户确认 seeded-shuffle 为默认训练采样方案。
30. 已完成：基于默认模板完成 seeded-shuffle 小规模验证。
31. 已完成：整理大规模训练配置与耗时边界报告。
32. 已完成：用户确认直接进入 `500 step` large_scale 训练路线。
33. 已完成：运行首个 `500 step` large_scale 训练并补齐后续评估。
34. 已完成：补 special-eval checkpoint series 并完成 `e_evt` early-vs-late focused 分析。
35. 已完成：整理 `e_evt` 约束增强候选方案报告，等待用户拍板路线。

## 当前阶段验收标准
当前阶段定义为“P0 完成，P1 首轮预处理与标准 manifest 完成”。完成标准如下：

- 协作规范已落盘，且明确为上下文恢复入口。
- 项目结构、任务大纲、进度、验收标准、下一阶段任务已落盘。
- 实施顺序已经按风险优先级而不是章节顺序重新排序。
- 工程目录结构和统一命令入口已建立。
- 首版数据扫描结果已落盘到正式报告目录。
- 首版预处理结果已落盘到 `data_prep/round1` 和 `reports/data/preprocess_round1`。
- 标准训练 manifest 已落盘到 `data_prep/round1/manifests`。
- 评估与实验记录模板已落盘。
- round1 数据完整性检查已通过。
- 第一份正式实验记录已初始化。
- 首轮离线 MVP 基线评估已通过。
- 首版训练 dry-run 计划已落盘。
- 真实数据加载与前向 dry-run 已跑通。
- 单步真实训练已跑通。
- checkpoint、step log、实验 metrics 回写已验证一致。
- 多步真实训练已跑通。
- 固定验证切片、周期 checkpoint 和训练历史已落盘。
- 训练开始时间、结束时间、总耗时和单 step 耗时已落盘并已打印验证。
- 大规模训练配置若未引用成功的小规模实验，将被代码级阻止。
- round1 拆分方案分析报告已落盘，且已确认当前固定切片存在明显分布偏差。
- 正式 split 已落盘到 `data_prep/round1/splits/hybrid_stratified_blocked/`。
- 训练入口已验证使用正式 split，当前不再依赖尾部切片。
- `target_special_eval` 已有独立数据级评估报告，并已确认当前 8 条全部是 punctuation-only challenge slice。
- offline MVP 的控制消融命令已落盘并实际运行。
- 已用与新结构兼容的小规模 checkpoint 完成首轮 `z_art / e_evt` 消融。
- 当前首轮消融已确认 `zero_e_evt` 会显著提高验证损失并带来更大输出偏移。
- `target_special_eval` 已有模型级评估结果，并已确认它与常规 validation 的差异主要体现在 `text_aux` stress，而不是控制输出整体崩坏。
- 已确认 `no_text_voice` 子集不含完整音节，只能作为非完整发声 challenge slice。
- 训练入口已支持固定 seed 和可选 shuffle，且训练计划会显式记录 `reproducibility` 字段。
- 多 checkpoint 系列消融已确认：在 seeded-shuffle 实验中，`z_art / e_evt` 的 loss 退化会随 step 单调增大。
- 顺序采样与 seeded-shuffle 的事实对比报告已落盘，且用户已确认 seeded-shuffle 为默认采样方案。
- 默认训练模板已实际跑通 seeded-shuffle 小规模验证，当前默认入口与文档口径一致。
- 大规模训练配置与耗时边界报告已落盘，用户已拍板 `500 step` large_scale 路线。
- 首个 `500 step` large_scale 已完成，当前重点转向解释 `e_evt` 后期回落现象。
- `e_evt` early-vs-late focused 分析已落盘，当前重点转向“是否需要专门增强事件路径约束”的方案调研。
- `e_evt` 约束增强候选方案报告已落盘，当前等待用户选择 A / B / D 路线。

## 下一阶段任务
下一阶段开始从 P2 过渡到 P3：

1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 根据 `docs/16_e_evt_constraint_options_report.md`，由用户决定 `e_evt` 约束增强路线。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 视用户所选路线，开始训练约束增强或数据层标签调查。

## 文档清单
- `docs/00_context_bootstrap.md`
  - 上下文恢复入口与硬性规范。
- `docs/01_project_overview_and_plan.md`
  - 项目总览、实施顺序、当前进度与下一步。
- `docs/02_pitfalls_log.md`
  - 开发期间持续维护的踩坑记录。
- `docs/03_data_scan_report.md`
  - 首轮数据扫描结论、待决策项和方案优缺点报告。
- `docs/04_decision_log.md`
  - 用户已确认的方案决策和实现边界。
- `docs/05_preprocess_round1_report.md`
  - round1 预处理实际结果、当前参数效果与人工复核重点。
- `docs/06_training_input_and_eval_baseline.md`
  - 训练输入标准与评估基线骨架。
- `docs/07_offline_mvp_scaffold.md`
  - 离线 MVP 评估命令、训练 dry-run 命令和当前产物说明。
- `docs/08_round1_split_strategy_analysis.md`
  - round1 正式训练/验证拆分候选方案分析与待确认结论。
- `docs/09_target_special_eval_report.md`
  - target special_eval 的独立数据级评估结论与后续边界。
- `docs/10_ablation_report.md`
  - offline MVP 首轮 `z_art / e_evt` 控制消融结果与当前解释口径。
- `docs/11_training_sampler_and_checkpoint_series.md`
  - seed/shuffle 训练采样能力、首轮 seeded-shuffle 实验，以及多 checkpoint 趋势汇总。
- `docs/12_default_sampler_decision_report.md`
  - 顺序采样与 seeded-shuffle 的对比事实、优缺点和默认方案决策口径。
- `docs/13_large_scale_training_boundary_report.md`
  - 大规模训练进入边界、时间数据解释范围与下一阶段候选路线。
- `docs/14_large_scale_run_report.md`
  - 首个 `500 step` large-scale 训练结果、消融趋势与 final special_eval 结论。
- `docs/15_e_evt_early_late_analysis.md`
  - `e_evt` 在 early 与 late checkpoint 上的对比分析，以及与 special slice 翻转现象的联读。
- `docs/16_e_evt_constraint_options_report.md`
  - `e_evt` 约束增强候选方案、优缺点与待用户拍板路线。
- `docs/55_round1_1_checkpoint_selection_report.md`
  - `EXP-032 / 035 / 039 / 042` 的联合 checkpoint 选择分析，以及当前 checkpoint 选择问题的收口结论。
- `docs/56_round1_1_checkpoint_gate_replay_report.md`
  - 多种 checkpoint gate 原型的离线回放结果，以及“gate 暂不应直接接入训练默认流程”的结论。

## 2026-03-14 `A1` 实跑更新
### 当前进度补充
36. 已完成：用户确认按方案 `D` 推进，并已跑通 `A1` 的 dry-run 与真实 `500 step` large-scale 实验。
37. 已完成：补齐 `A1` 的 final ablation、checkpoint-series、final special-eval 与 selected checkpoint `special_eval series`。
38. 已完成：确认 `A1` 当前参数组合不适合作为默认方案，原因是 `e_evt` 回升有限，但整体 validation 明显恶化且 `z_art` 后期贡献被压弱。

### 当前阶段结论补充
- `方案 D` 的总方向保持不变，但 `D` 的第一步 `A1` 当前参数组合已得到一个明确的负结论：
  - 不能直接升为默认训练路线。
- 当前最有价值的下一阶段任务，不是继续放大这组 `A1` 参数，而是先整理：
  - 是否继续做 `A2`
  - 还是转向 `B` 的事件标签/监督升级

先说人话：
- 这轮不是“训练失败”，而是“方案试验给出了明确否定结果”。
- 这很有价值，因为后面不用再在同一组参数上浪费时间。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 基于 `docs/18_e_evt_constraint_a1_run_report.md`，整理 `A2` 与 `B` 的对比决策报告。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 由用户决定下一步是继续 `A` 系约束调优，还是转向 `B` 的标签/监督升级。

### 文档补充
- `docs/17_e_evt_constraint_a1_draft.md`
  - `A1` 开跑前草案，现已追加状态更新。
- `docs/18_e_evt_constraint_a1_run_report.md`
  - `A1` 首轮真实 `500 step` 实跑结果、通过标准核对与后续建议。

## 2026-03-14 `A2` vs `B` 决策准备更新
### 当前进度补充
39. 已完成：接入 `analyze-offline-mvp-event-targets` 正式分析命令，并生成可复核的事件标签体检报告。
40. 已完成：基于 `A1` 实跑结论与事件标签分析结果，整理 `A2` vs `B` 决策报告。

### 当前阶段结论补充
- 当前证据更支持把下一步重点转向 `B`，而不是继续深挖 `A2`。
- 但是否直接转向 `B`，仍然属于方案决策，必须由用户拍板。

先说人话：
- 现在不是没路走。
- 而是证据已经越来越像在说：问题更像“老师出的题不够好”，不是“学生还要再多背一点纪律”。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 由用户基于 `docs/19_a2_vs_b_decision_report.md` 拍板下一步走 `A2` 还是 `B`。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若用户选择 `B`，则进入事件标签/监督升级的事实收集与实施拆分。

### 文档补充
- `docs/19_a2_vs_b_decision_report.md`
  - 基于 `A1` 实跑结果和事件标签体检结果整理的下一步决策报告。

## 2026-03-14 `方案 B` 启动更新
### 当前进度补充
41. 已完成：用户确认直接转向方案 `B`。
42. 已完成：新增 `build-b1-supervision-inventory` 命令，并生成 round1 的正式 supervision inventory sidecar。
43. 已完成：确认当前离线条件下，目标侧文本监督已可直接利用，源侧文本监督仍为空白。

### 当前阶段结论补充
- 方案 `B` 现在可以从一个真实可落的 `B1-offline-minimal` 起步，而不是停留在抽象讨论。
- 但 `B1-offline-minimal` 与 `B2` 长线接口优先级，仍需要用户拍板。

先说人话：
- 现在已经把“新老师的花名册”整理好了。
- 下一步就是决定先让这位老师直接进课堂，还是先继续搭更大的教务系统。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 由用户基于 `docs/20_b_route_bootstrap_report.md` 拍板先走 `B1-offline-minimal` 还是先搭 `B2` 接口。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若用户选择 `B1-offline-minimal`，则把 target-side 文本/标点监督正式接入训练代码。

### 文档补充
- `docs/20_b_route_bootstrap_report.md`
  - 方案 `B` 的启动状态、当前离线可用监督源，以及 `B1` / `B2` 的分叉说明。

## 2026-03-14 `B1-offline-minimal` 实现更新
### 当前进度补充
44. 已完成：用户确认源侧当前不做手工全文本标注，`B1` 采用“目标侧文本监督 + 源侧纯音频监督”的不对称路线。
45. 已完成：把 `B1` 目标侧文本/标点特征接入 offline MVP 数据与模型配置。
46. 已完成：新增 `configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json`，并跑通 `EXP-20260314-014-offline-mvp-b1-smallscale`。
47. 已完成：补齐 `EXP-014` 的小规模训练、ablation 和 `special_eval`。

### 当前阶段结论补充
- `B1-offline-minimal` 已通过“能稳定进入训练与评估”的门槛。
- 当前证据显示：
  - 总体验证 loss 与旧 seeded-shuffle 小规模基线基本打平；
  - `z_art / e_evt` 消融敏感度更强。
- 这意味着 `B1` 至少值得继续做更大一点的验证，而不是就地回退。

先说人话：
- 新老师已经能正常上课。
- 现在还没证明它一定更强，但已经证明它不是坏老师。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 由用户决定：
   - 继续放大 `B1` 训练验证
   - 或先细化 `B1` 文本监督口径
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若继续放大 `B1`，优先做更长小规模或受控 large-scale 实验，而不是直接改默认模板。

### 文档补充
- `docs/21_b1_offline_minimal_report.md`
  - `B1-offline-minimal` 的首轮实现、训练结果和当前解释口径。

## 2026-03-14 `B1` 100 step 校准更新
### 当前进度补充
48. 已完成：新增 `configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json`，并创建 `EXP-20260314-015-offline-mvp-b1-100step-calibration`。
49. 已完成：跑通 `B1` 的 `100 step` 真实训练、ablation、checkpoint-series 与 `special_eval` 系列。
50. 已完成：完成 `B1 step100` 与无 `B1 step100` 的对照整理。

### 当前阶段结论补充
- `B1-offline-minimal` 到 `100 step` 仍然稳定可训练，没有把主流程拖坏。
- 但到 `step100`，它与无 `B1` 基线在主验证集上的总体表现基本打平。
- `20 step` 时看到的控制链敏感度优势，到 `100 step` 没有继续扩大。
- `target_special_eval` 上 `B1` 略稳一点，但幅度不足以单独支撑直接放大到 `500 step`。

先说人话：
- 这条路不是错路。
- 但现在更像“方向对了，教案还不够强”，而不是“已经可以直接全面推广”。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 由用户基于 `docs/22_b1_100step_calibration_report.md` 拍板：
   - 直接放大当前 `B1-offline-minimal`
   - 或先细化 `B1.1` 文本监督
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若用户选择 `B1.1`，则优先细化 target-side 文本监督，而不是继续给 source 侧补全文字。

### 文档补充
- `docs/22_b1_100step_calibration_report.md`
  - `B1` 在 `100 step` 下的校准结果、与无 `B1` 的直接对照，以及下一步建议。

## 2026-03-14 `B1.1` 细化准备更新
### 当前进度补充
51. 已完成：基于 target-side 文本分布和 `B1 step100` 结果，整理 `B1.1` 的文本监督细化选项。

### 当前阶段结论补充
- 当前更像是“监督内容偏粗”，而不只是“训练步数不够”。
- `B1.1` 更合理的优先级是：
  - 先扩展 target-side 统计特征
  - 再视结果决定是否做更贴近 `e_evt` 的弱对齐标签

先说人话：
- 现在该优先修教材，不是先把课时无限加长。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 由用户基于 `docs/23_b1_1_text_supervision_options_report.md` 拍板：
   - 先做 `B1.1-A`
   - 或直接尝试更激进的 `B1.1-C`
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若用户选择 `B1.1-A`，则优先只扩 target-side 文本统计，不改 source-side 监督口径。

### 文档补充
- `docs/23_b1_1_text_supervision_options_report.md`
  - `B1.1` 的候选细化路线、目标侧文本分布事实与当前建议。

## 2026-03-14 `B1.1-A` 实跑与 `C1` 启动更新
### 当前进度补充
52. 已完成：实现 `B1.1-A` 的 13 维 target-side 文本统计特征与专用配置。
53. 已完成：跑通 `EXP-20260314-016-offline-mvp-b1-1a-100step-calibration`，并补齐 ablation、checkpoint-series 与 `special_eval` 系列。
54. 已完成：确认 `B1.1-A` 在 `step100` 下未形成比 `B1` 更明确的主验证增益。
55. 已完成：按既定路线继续进入 `C1`，生成 target-side 弱事件提示 sidecar。

### 当前阶段结论补充
- `B1.1-A` 证明了“更细的整句统计”可稳定接入，但仍不足以单独把 route-B 拉出明确领先。
- 当前更合理的下一步是继续 route-C，不再继续单独深挖整句级统计特征。
- `C1` 的第一批 target-side 弱事件提示已经落盘，且覆盖度足够高，可以作为后续训练接入的监督底账。

先说人话：
- `A` 这步没有白做，但也没强到能单独翻盘。
- 现在该把重点转到“哪里该停、哪里像句末”这种更接近事件边界的老师上。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 基于 `data_prep/round1/c1_weak_event_hints/target_weak_event_hints.jsonl` 设计 `C1.1` 的 target-side weak event 接入方式。
3. 对 `C1.1` 跑首轮 `100 step` 对照验证，重点检查：
   - 主验证 loss
   - `zero_e_evt`
   - `zero_z_art`
4. 继续保持 source-side 为 audio-only，不引入源侧全文本监督。

### 文档补充
- `docs/24_b1_1a_run_report.md`
  - `B1.1-A` 的 `100 step` 实跑结果与对照结论。
- `docs/25_c1_weak_event_hints_bootstrap_report.md`
  - `C1` 弱事件提示 sidecar 的启动状态与当前可用性。

## 2026-03-14 `C1.1` 首轮实跑更新
### 当前进度补充
56. 已完成：把 target-side weak event hints 以额外 `weak_event` 损失的形式接入 offline MVP 训练与评估代码。
57. 已完成：新增 `configs/offline_mvp_train_c1_1_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260314-017-offline-mvp-c1-1-100step-calibration`。
58. 已完成：补齐 `EXP-017` 的 `ablation`、`checkpoint-series`、`special_eval` 与 `special_eval_series`。

### 当前阶段结论补充
- `C1.1` 证明了：
  - 当前这版弱事件提示可以稳定接进训练；
  - 到 `step100`，`e_evt / z_art` 消融敏感度比 `B1.1-A` 略强。
- 但当前也同时确认：
  - `C1.1 step100` 的主验证 `target_loss_total = 2.716403`；
  - 比 `B1.1-A step100 = 2.680581` 更差；
  - 因此还不能把 `C1.1` 判定为值得直接升级的默认路线。
- `checkpoint-series` 仍然显示：
  - 中期存在 `zero_e_evt` 回落甚至转负的区段；
  - 到 `step90/100` 才重新回升到较强依赖。

先说人话：
- 这说明“告诉模型哪里像停顿/句末”这位新老师是能进课堂的。
- 但第一版教法还不够强，至少还没强到能打赢上一版。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 在不改 sidecar 的前提下，先做更轻的 `C1.2` 权重回调，确认当前结果是不是单纯因为 `weak_event` 权重偏重。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若 `C1.2` 仍不能形成清晰领先，则不要把后续时间继续花在 `0.1/0.2` 这类小范围权重扫参上。

### 文档补充
- `docs/26_c1_1_run_report.md`
  - `C1.1` 的 `100 step` 实跑结果、与 `B1.1-A` 的对照，以及是否值得继续的当前结论。

## 2026-03-14 `C1.2` 轻权重回调更新
### 当前进度补充
59. 已完成：新增 `EXP-20260314-018-offline-mvp-c1-2-100step-calibration`，对 `weak_event = 0.1` 做同级 `100 step` 对照。
60. 已完成：补齐 `EXP-018` 的 `ablation`、`checkpoint-series`、`special_eval` 与 `special_eval_series`。
61. 已完成：整理 `C1.1` 与 `C1.2` 的直接对照结论。

### 当前阶段结论补充
- `C1.2 step100` 的主验证 `target_loss_total = 2.699184`：
  - 比 `C1.1 = 2.716403` 略好；
  - 但仍未超过 `B1.1-A = 2.680581`。
- `C1.2` 的控制链敏感度与 `C1.1` 几乎重合：
  - `zero_z_art.delta_target_loss_total = 1.337895`
  - `zero_e_evt.delta_target_loss_total = 1.419051`
- `target_special_eval` 也与 `C1.1` 基本打平：
  - `delta_loss_total = 0.166072`
  - `delta_loss_text_aux = 0.142518`
- 当前更合理的解释是：
  - route-C 的弱边界提示已经证明“可接、可稳、略有帮助”；
  - 但仅靠 `weak_event` 标量权重在 `0.1` 到 `0.2` 之间微调，不足以形成新的明确突破。

先说人话：
- 这轮不是没收获。
- 收获是已经知道：这位新老师不是没用，但光靠“加一点分、减一点分”还不足以翻盘。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 基于 `docs/26_c1_1_run_report.md` 与 `docs/27_c1_2_run_report.md`，向用户汇报当前 route-C 的事实边界。
3. 若继续 route-C，优先改变：
   - 弱事件监督的注入方式
   - 或弱标签本身的表达形式
   而不是继续围绕 `weak_event` 标量做小步扫参。
4. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。

### 文档补充
- `docs/27_c1_2_run_report.md`
  - `C1.2` 的轻权重回调结果、与 `C1.1 / B1.1-A` 的直接对照，以及当前建议。

## 2026-03-14 `C1.3` event-target bias/override 更新
### 当前进度补充
62. 已完成：把 route-C 的弱边界提示从“独立 `weak_event` 辅助损失”为主，扩展为“target-side event loss bias + 温和 event target override”的新接入方式。
63. 已完成：新增 `configs/offline_mvp_train_c1_3_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260314-019-offline-mvp-c1-3-100step-calibration` 的 `dry-run` 与真实 `100 step`。
64. 已完成：补齐 `EXP-019` 的 `ablation`、`checkpoint-series`、`special_eval` 与 `special_eval_series`。

### 当前阶段结论补充
- `C1.3` 当前是 route-C 里最合理的一版接入方式：
  - `target_loss_total = 2.683692`
  - 明显优于 `C1.1 = 2.716403`
  - 也优于 `C1.2 = 2.699184`
- 但当前也仍然只能说“几乎追平 `B1.1-A`”，还不能说“已经明确超过”：
  - `B1.1-A = 2.680581`
  - `C1.3 = 2.683692`
- `C1.3` 的控制消融几乎与 `B1.1-A` 打平：
  - `zero_z_art.delta_target_loss_total = 1.329502`
  - `zero_e_evt.delta_target_loss_total = 1.409978`
- 这说明：
  - 相比 `C1.1 / C1.2` 的“独立辅助损失”接法，
  - 把弱边界提示直接并入 `event loss / event_target` 的主判卷流程，方向更对。
- 但它仍未形成足以单独升默认方案的清晰领先。

先说人话：
- 这次不是简单地把老师声音调大调小。
- 而是把老师直接拉进了主考卷流程里。结果确实更对路了，但目前也只是“追上”，还不是“反超”。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 若继续 route-C，优先升级弱标签表达本身，而不是继续围绕当前同一份 sidecar 做轻量调参。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若要继续做训练实验，优先考虑：
   - richer boundary label expression
   - 或更明确的 pause / terminal 区分
   而不是继续在当前 `C1.3` 附近做小步权重扫参。

### 文档补充
- `docs/28_c1_3_event_bias_run_report.md`
  - `C1.3` 的 event-target bias/override 接入方式、与 `B1.1-A / C1.1 / C1.2` 的直接对照，以及当前建议。

## 2026-03-14 `C1.4` boundary pre/post target 显式化更新
### 当前进度补充
65. 已完成：新增 `configs/offline_mvp_train_c1_4_smallscale_100_seeded_shuffle.json`，对 route-C 的 boundary pre/post target 显式化版本做 `100 step` 对照。
66. 已完成：跑通 `EXP-20260314-020-offline-mvp-c1-4-100step-calibration`，并补齐 `ablation`、`checkpoint-series`、`special_eval` 与 `special_eval_series`。
67. 已完成：确认 `C1.4` 相比 `C1.3` 只带来极小幅度改善，但仍未形成对 `B1.1-A` 的明确反超。

### 当前阶段结论补充
- `C1.4 step100` 的主验证 `target_loss_total = 2.681003`：
  - 比 `C1.3 = 2.683692` 略好；
  - 但与 `B1.1-A = 2.680581` 仍基本打平。
- `C1.4` 的控制消融也只比 `C1.3` 微弱前进：
  - `zero_z_art.delta_target_loss_total = 1.329629`
  - `zero_e_evt.delta_target_loss_total = 1.410986`
  - 当前仍更像“数值抖动范围内的微调收益”，不是“路线级跃迁”。
- `target_special_eval` 维持轻微更稳：
  - `delta_loss_total = 0.181996`
  - 比 `C1.3 = 0.182364` 略好；
  - 但量级仍不足以单独支撑“route-C 已显著领先”的结论。
- `checkpoint-series` 依然保留 route-C 的中期问题：
  - `step50 zero_e_evt.delta_target_loss_total = -0.519136`
  - 说明这轮没有真正解决“中期事件路径依赖回落”的老问题。

先说人话：
- `C1.4` 不是坏结果。
- 但它更像把 `C1.3` 稍微磨平了一点，还谈不上把 route-C 推到一个新的台阶。

### 更新后的下一阶段任务
1. 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本。
2. 若继续 route-C，优先升级弱标签表达本身，或引入更明确的 pause / terminal / punctuation-type 区分，而不是继续围绕当前同一份 sidecar 做小步 target 常数微调。
3. 评估 `target_special_eval` 是否需要加入更贴近运行时的非文本指标。
4. 若要继续做训练实验，当前更合理的对照基线可记为：
   - route-B 参考：`B1.1-A`
   - route-C 最新参考：`C1.4`
   但二者当前仍属于“基本打平，尚无明确胜负”。

### 文档补充
- `docs/29_c1_4_boundary_prepost_run_report.md`
  - `C1.4` 的 `100 step` 实跑结果、与 `B1.1-A / C1.3` 的直接对照，以及当前建议。

## 2026-03-14 隔离样本复核更新
### 当前进度补充
68. 已完成：复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 47 条隔离样本，并核对 `preprocess.py` 的真实排除逻辑。
69. 已完成：确认这 47 条当前全部属于格式隔离，而非 `missing_lab / empty_cleaned_text` 等数据内容硬伤。
70. 已完成：整理 lexical-only recovery 与继续冻结 round1 的事实对比。

### 当前阶段结论补充
- 当前 47 条隔离样本里：
  - `37` 条属于 `mono_resample_only`
  - `5` 条属于 `stereo_downmix_plus_resample`
  - `5` 条属于 `no_text_voice`
- 当前可通过格式统一回收的 lexical 样本合计约：
  - `42` 条
  - `235.471s`
  - 约占当前 round1 target 总时长的 `6.2%`
- 这说明：
  - `manifest_round1_excluded.jsonl` 目前更像 format quarantine，而不是 junk bin。
- 但当前也同样确认：
  - 这 `5` 条 `no_text_voice` 即使做格式统一，也不应直接混回正常 lexical training split。

先说人话：
- 隔离区里大部分不是坏料。
- 但现在要不要回收，已经变成“要不要开一个新数据版本”的问题，而不是“这些东西还能不能用”的问题。

### 更新后的下一阶段任务
1. 由用户决定是否保持当前 round1 数据冻结，还是新开 `round1.1` 做 lexical-only target format normalization。
2. 若保持 round1 冻结，则继续评估 `target_special_eval` 的非文本指标补强方案。
3. 若用户确认进入 `round1.1`，则只回收 `42` 条 lexical 隔离样本，`5` 条 `no_text_voice` 继续保持 isolated。
4. 无论走哪条路线，都不要把 `manifest_round1_excluded.jsonl` 再笼统视作“坏样本清单”。

### 文档补充
- `docs/30_excluded_samples_review_report.md`
  - 47 条隔离样本的排除原因、可回收性分组、时长影响与后续建议。

## 2026-03-14 `target_special_eval` 非文本指标补强更新
### 当前进度补充
71. 已完成：在 `src/v5vc/special_eval.py` 中补入更贴近运行时的非文本输出统计。
72. 已完成：对 `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 重跑模型级 `special_eval`，产出带新指标的评估结果。
73. 已完成：确认这些新指标能补足 `loss_text_aux / event_prob_mean` 口径的解释盲区。

### 当前阶段结论补充
- 当前 `target_special_eval` 确实值得保留非文本指标补强。
- 在 `EXP-020` 上，新指标显示 special slice 不只是“文本更难”，还表现为：
  - 更低的 `z_art` 时序变化
  - 更低的 `event presence / fall / energy` 平均值
  - 更低的 `acoustic energy`
  - 更低的 `acoustic delta`
  - 但更高的 `event presence peak ratio`
- 当前更合理的解释是：
  - special slice 是“更稀疏、更低能量、更平，但局部峰值更尖”的 nonverbal challenge slice。

先说人话：
- 现在终于不只是知道“这批样本文字上难”。
- 还知道了它在声音动态上更像“平时轻，偶尔尖一下”的那类片段。

### 更新后的下一阶段任务
1. 由用户决定是否保持当前 round1 数据冻结，还是新开 `round1.1` 做 lexical-only target format normalization。
2. 若保持 round1 冻结，则优先考虑是否把这批非文本指标继续扩到 `special_eval_series`，用于早中晚 checkpoint 连续观察。
3. 若用户确认进入 `round1.1`，则只回收 `42` 条 lexical 隔离样本，`5` 条 `no_text_voice` 继续保持 isolated。
4. 后续所有 `target_special_eval` 汇报，默认同时给出：
   - 文本相关压力
   - 非文本运行态统计

### 文档补充
- `docs/31_target_special_eval_nontext_metrics_report.md`
  - `target_special_eval` 的非文本指标补强原因、`EXP-020` 上的新观察，以及后续建议。

## 2026-03-14 `special_eval_series` 口径固定更新
### 当前进度补充
74. 已完成：把非文本指标摘要接入 `special_eval_series`。
75. 已完成：重跑 `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 的 `special_eval_series`。
76. 已完成：重跑 `EXP-20260314-011-offline-mvp-large-scale-500` 的 `special_eval_series`，固定旧数据线的早中晚 checkpoint 解释口径。

### 当前阶段结论补充
- 现在 `special_eval_series` 不再只看：
  - `delta_loss_total`
  - `delta_loss_text_aux`
  - `event_prob_mean`
- 当前已能连续追踪：
  - `event presence`
  - `event fall`
  - `event energy`
  - `presence peak ratio`
  - `z_art` 时序变化
  - `acoustic energy / delta`
- 这意味着：
  - A 方案“先把旧实验数据钉死”的目标已经完成。

先说人话：
- 现在旧实验不是只有总分。
- 连“每个阶段声音动态怎么变”也有连续记录了。

### 更新后的下一阶段任务
1. 继续推进 `round1.1` 数据升级事实收集与落盘。
2. 由用户决定是否正式把后续训练基线切到 `round1.1`。

### 文档补充
- `docs/31_target_special_eval_nontext_metrics_report.md`
  - 已追加 `special_eval_series` 口径固定更新。

## 2026-03-14 `round1.1` lexical-only target recovery 更新
### 当前进度补充
77. 已完成：新增 `recover-round1-target-formats` 命令，实现 lexical target 隔离样本的格式回收。
78. 已完成：实际生成 `data_prep/round1_1/firefly_mainstream/`，恢复 `42` 条 lexical target 样本，保留 `5` 条 `no_text_voice` 继续隔离。
79. 已完成：新增 manifest 构建入口的 `target-dir / source-dir` 组合支持，生成 `data_prep/round1_1/manifests/`。
80. 已完成：对 `round1.1` manifests 跑通 split analysis，当前推荐方案仍为 `hybrid_stratified_blocked`。

### 当前阶段结论补充
- 当前 `round1.1` 已经不是想法，而是磁盘上真实存在的新数据版本。
- 当前 recovery 结果：
  - target 从 `624` 条增到 `666` 条
  - 新增 lexical target 时长约 `235.470887s`
  - `5` 条 `no_text_voice` 仍保持 isolated
- 当前 `round1.1 split analysis` 继续支持：
  - target 主验证集与 `no_text_voice` challenge slice 分离
  - source 仍采用 blocked holdout 而不是随机拆分

先说人话：
- B 方案已经从“准备切”变成“底座已搭好”。
- 现在差的不是数据准备，而是要不要正式用这套新底座开第一轮实验。

### 更新后的下一阶段任务
1. 由用户决定是否正式采用 `round1.1` 的 `hybrid_stratified_blocked` 作为新训练拆分。
2. 若用户确认，则 materialize `round1.1` 正式 split。
3. 初始化第一份 `round1.1` 训练实验，并先做小规模验证，不直接上 large-scale。
4. 若用户暂不确认，则保留 `round1.1` 当前产物，继续维持 `round1` 为主线实验底座。

### 文档补充
- `docs/32_round1_1_bootstrap_report.md`
  - `round1.1` 的 target recovery、manifest 结果、split facts 与当前建议。

## 2026-03-14 `round1.1 / C1.4 / 100-step` 首轮实验更新
### 当前进度补充
81. 已完成：materialize `data_prep/round1_1/splits/hybrid_stratified_blocked/`，正式固定 `round1.1` 训练拆分。
82. 已完成：重建 `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`，让新回收的 `42` 条 lexical target 也进入 route-C sidecar 口径。
83. 已完成：新增 `configs/offline_mvp_train_c1_4_round1_1_smallscale_100_seeded_shuffle.json`，保持原采样与训练配方不变。
84. 已完成：跑通 `EXP-20260314-021-offline-mvp-c1-4-round1-1-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `round1.1` 首轮结果不支持“数据一升级，route-C 就直接赢了”的说法。
- 相比 `EXP-020`：
  - final formal target validation 基本打平，未见明确提升
  - final `target_special_eval` 压力差明显收窄：
    - `delta_loss_total: 0.181996 -> 0.028766`
  - final `e_evt` 依赖更强：
    - `zero_e_evt.delta_target_loss_total: 1.410986 -> 1.781482`
  - 但 final `z_art` 依赖更弱：
    - `zero_z_art.delta_target_loss_total: 1.329629 -> 0.886715`
- 更关键的是：
  - `step50` 的中期依赖回落问题没有消失
  - 且这次更重：
    - `zero_e_evt.delta_target_loss_total: -0.519136 -> -0.854462`
    - `zero_z_art.delta_target_loss_total: -0.173311 -> -0.273851`

先说人话：
- `round1.1` 让终点看起来更顺了一点。
- 但 route-C 中途还是会掉链子，而且这次掉得更明显。

### 更新后的下一阶段任务
1. 不直接把 `EXP-021` 升成 `round1.1` 默认胜出证据。
2. 继续围绕 `step50` 的 route-C 依赖回落做稳定性修正，不优先上 large-scale。
3. 若继续走 `round1.1`，下一轮优先做“稳定性修正”而不是再做常数级小调参。

### 文档补充
- `docs/33_round1_1_c1_4_smallscale_run_report.md`
  - `round1.1` 首轮 `C1.4` 小规模训练、配套评估、与 `EXP-020` 的同口径对照结论。

## 2026-03-14 `round1.1 / C1.4 / A2-min` 更新
### 当前进度补充
85. 已完成：新增最小变量稳定性修正配置 `configs/offline_mvp_train_c1_4_round1_1_evt_a2_dimonly_smallscale_100_seeded_shuffle.json`，只引入 `event_dimension_weights`，不引入全局 `event` ramp。
86. 已完成：跑通 `EXP-20260314-022-offline-mvp-c1-4-round1-1-evt-a2-dimonly-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `A2-min` 比旧 `A1` 健康得多：
  - 没有明显拖垮整体收敛
  - final `z_art` 也没有被明显打散
- 但它依然没有解决当前主问题：
  - formal full-validation 比 `EXP-021` 略差
  - `step50` 的 route-C 依赖回落几乎没变
- 相比 `EXP-021`：
  - final `target_special_eval.delta_loss_total`
    - `0.028766 -> -0.025956`
  - final `zero_e_evt.delta_target_loss_total`
    - `1.781482 -> 1.803449`
  - 但 `step50 zero_e_evt.delta_target_loss_total`
    - `-0.854462 -> -0.846723`
  - 这说明：
    - 纯维度重权只是在终点上略有修饰
    - 没有真正改写中期稳定性

先说人话：
- 这轮证明“纯约束还有一点点尾部收益”。
- 但也基本证明了：只靠这层小修小补，救不回 `step50` 的核心问题。

### 更新后的下一阶段任务
1. 结束 `A` 路线内部的轻量小修小补，不继续围绕 `event_dimension_weights / event ramp` 做同层扫参。
2. 若继续沿当前总计划推进，下一步优先转向：
   - 更明确的标签表达升级
   - 或更贴近设计稿的事件监督定义升级
3. 保持 `round1.1` 为当前数据底座，但不把 `EXP-022` 升为默认训练配置。

### 文档补充
- `docs/34_round1_1_evt_a2_dimonly_run_report.md`
  - `A2-min` 的配置、结果、与 `EXP-021` 的同口径对比，以及当前判断。

## 2026-03-14 `round1.1` `C1` 标签表达升级更新
### 当前进度补充
87. 已完成：扩展 `src/v5vc/c1_weak_event_hints.py`，让 `C1` sidecar 除边界点外，再输出 `clause_count / clause_spans / utterance_structure_type`。
88. 已完成：重建 `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl` 和 `reports/data/round1_1_c1_weak_event_hints/weak_event_hints_summary.md`。

### 当前阶段结论补充
- 当前 route-C 的下一层动作已经从“继续调约束”切到“升级标签表达底座”。
- `round1.1` 新 sidecar 现在不再只告诉模型：
  - 哪一帧附近像边界
- 还额外告诉我们：
  - 这句话有几个 clause
  - 每个 clause 大概落在什么帧区间
  - 它是 initial / middle / final 角色
  - 整句属于哪类结构
- 当前 `round1.1` 统计说明：
  - `multi_clause_single_terminal = 307`
  - `multi_terminal = 174`
  - `clause_count.mean = 3.010511`
- 这进一步支持先前判断：
  - 旧 sidecar 的标签表达偏扁
  - 下一步更适合做结构化监督升级，而不是继续同层 loss 微调

### 更新后的下一阶段任务
1. 设计第一版真正消费 `clause_spans / utterance_structure_type` 的训练接法。
2. 保持 `round1.1` 数据和采样方案不变，先做一轮小规模结构化监督验证。
3. 不再把当前主要时间投入在：
   - `event_dimension_weights`
   - `event_weight_schedule`
   - 或同层常数 tweak

### 文档补充
- `docs/35_round1_1_c1_label_expression_upgrade_report.md`
  - `round1.1` 新 sidecar 的 clause 级字段、统计结果和下一步意义。

## 2026-03-14 `round1.1 / C1.5 / clause-aware` 首轮实验更新
### 当前进度补充
89. 已完成：扩展 `offline_mvp` loss 路径，支持在 `event_boundary_bias` 下消费 `clause_role_target_overrides`。
90. 已完成：新增 clause-aware 配置 `configs/offline_mvp_train_c1_5_round1_1_clause_span_smallscale_100_seeded_shuffle.json`。
91. 已完成：跑通 `EXP-20260314-023-offline-mvp-c1-5-round1-1-clause-span-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- 第一版 clause-aware 接线已经证明：
  - `clause_spans / utterance_structure_type` 可以被真实消费
  - route-C 已经进入“结构化标签试验”阶段，而不只是边界点试验
- 但当前这版具体接法没有解决主问题：
  - `step50 zero_e_evt.delta_target_loss_total`
    - `EXP-021: -0.854462`
    - `EXP-022: -0.846723`
    - `EXP-023: -0.853283`
  - `step50 zero_z_art.delta_target_loss_total`
    - `EXP-021: -0.273851`
    - `EXP-022: -0.265417`
    - `EXP-023: -0.273785`
- final checkpoint 上：
  - `EXP-023` 的 `zero_e_evt.delta_target_loss_total = 1.807451`
    - 略高于 `EXP-021 / EXP-022`
  - 但 `target_special_eval.delta_loss_total = 0.008379`
    - 不如 `EXP-022`
  - formal validation 也未优于 `EXP-021`

先说人话：
- 这轮说明“结构化标签”这条大方向没错。
- 但第一版 clause-aware 教法还是没打到真正的问题点上。

### 更新后的下一阶段任务
1. 不把 `EXP-023` 升为默认训练配置。
2. 继续沿“结构化标签表达升级”推进，但更换 clause-aware 接法，不回退到纯约束小修补。
3. 下一轮优先考虑：
   - 更贴近 clause end / inter-clause transition 的监督
   - 而不是继续对 clause body 做温和 `presence / energy` floor

### 文档补充
- `docs/36_round1_1_c1_5_clause_span_run_report.md`
  - clause-aware 首轮实验的接法、结果和下一步判断。

## 2026-03-14 `round1.1 / C1.6 / clause-transition` 实验更新
### 当前进度补充
92. 已完成：扩展 `offline_mvp` loss 路径，新增 `clause_transition_strengths`，支持在 `event_boundary_bias` 下消费 `clause_transition_target_overrides`。
93. 已完成：新增 clause-transition 配置 `configs/offline_mvp_train_c1_6_round1_1_clause_transition_smallscale_100_seeded_shuffle.json`。
94. 已完成：跑通 `EXP-20260314-024-offline-mvp-c1-6-round1-1-clause-transition-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- 第二版结构化标签接线已经证明：
  - clause end / final-vs-middle transition 也可以被真实接入现有 loss 框架
- 但当前这版接法几乎没有改变训练轨迹：
  - final `target_validation.loss_total`
    - `EXP-021: 2.760389`
    - `EXP-024: 2.760679`
  - final `target_special_eval.delta_loss_total`
    - `EXP-021: 0.028766`
    - `EXP-024: 0.028482`
  - final `zero_e_evt.delta_target_loss_total`
    - `EXP-021: 1.781482`
    - `EXP-024: 1.781535`
  - `step50 zero_e_evt.delta_target_loss_total`
    - `EXP-021: -0.854462`
    - `EXP-024: -0.854465`
  - `step50 zero_z_art.delta_target_loss_total`
    - `EXP-021: -0.273851`
    - `EXP-024: -0.273854`
- 相比 `EXP-023`：
  - `EXP-024` 没有把 `step50` 修好
  - 也没有保住 `EXP-023` 那种更小的 final `special_eval` gap
  - 更像是回到了 `EXP-021` 的原轨道

先说人话：
- 这不是“有一点作用，但还不够强”。
- 更准确地说，是这版 clause-transition 教法几乎没起独立作用。

从结果推断：
- 当前 `clause_transition_target_overrides` 虽然已经生效，
- 但由于多数 clause end 与原有 `pause / terminal` 边界高度重合，
- 在同一个 `event_boundary_bias` 框架里，新增信号没有形成足够独立的学习压力。

### 更新后的下一阶段任务
1. 不把 `EXP-024` 升为默认训练配置。
2. 若继续推进 route-C，暂停继续在 `event_boundary_bias` 里叠更多 role-specific override。
3. 下一轮优先考虑：
   - 独立的 clause-transition auxiliary loss
   - 或单独抽样的 clause-end frame supervision
   - 而不是继续把结构化信号挤进现有 boundary bias 通道

### 文档补充
- `docs/37_round1_1_c1_6_clause_transition_run_report.md`
  - clause-transition 第二版结构化监督的接法、结果和下一步判断。

## 2026-03-14 `round1.1 / C1.7 / clause-transition auxiliary` 实验更新
### 当前进度补充
95. 已完成：在 `offline_mvp` loss 路径中新增独立 `clause_transition_aux`，不再复用 `event_boundary_bias` override 通道。
96. 已完成：扩展 `special_eval` / `ablation_eval` 汇总，增加 `loss_clause_transition_aux` 指标。
97. 已完成：新增配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260314-025-offline-mvp-c1-7-round1-1-clause-transition-aux-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-025` 证明了：
  - 独立 clause-transition auxiliary loss 确实形成了新信号
  - 它不再像 `EXP-024` 那样完全被旧 boundary bias 吞掉
- 证据包括：
  - final `target_validation.loss_clause_transition_aux = 0.051682`
  - final `target_special_eval.loss_clause_transition_aux = 0.0`
  - 说明它只在带 lexical clause 结构的切片上生效，而不是假接线
- 但当前它仍没有解决主问题：
  - final `target_validation.loss_total`
    - `EXP-021: 2.760389`
    - `EXP-025: 2.778521`
  - final `target_special_eval.delta_loss_total`
    - `EXP-021: 0.028766`
    - `EXP-024: 0.028482`
    - `EXP-025: 0.010553`
    - `EXP-023: 0.008379`
  - `step50 zero_e_evt.delta_target_loss_total`
    - `EXP-021: -0.854462`
    - `EXP-024: -0.854465`
    - `EXP-025: -0.854869`
  - `step50 zero_z_art.delta_target_loss_total`
    - `EXP-021: -0.273851`
    - `EXP-024: -0.273854`
    - `EXP-025: -0.274127`
- 这说明：
  - “独立通道”这一步是必要的
  - 但还不够
  - 当前更可能缺的是 clause-transition-rich 样本在训练前中期的出现密度，而不只是监督公式

先说人话：
- 这轮终于能确认结构化监督不是完全白加。
- 但它只是发出了独立声音，还没有抢到主导节奏。

### 更新后的下一阶段任务
1. 不把 `EXP-025` 升为默认训练配置。
2. 若继续推进 route-C，保留独立 auxiliary loss 方向，不回退到 `event_boundary_bias` 叠常数。
3. 下一轮优先考虑：
   - multi-clause target 记录的 targeted sampling / curriculum
   - 或提高 clause-transition-rich 样本在前中期训练中的出现密度
   - 而不是继续只调 auxiliary loss 常数

### 文档补充
- `docs/38_round1_1_c1_7_clause_transition_aux_run_report.md`
  - 独立 clause-transition auxiliary loss 的接法、结果和下一步判断。

## 2026-03-15 `round1.1 / C1.7 / targeted sampling & curriculum` 更新
### 当前进度补充
98. 已完成：扩展 target 侧 batch planner，支持 `priority_interleave`，可按 `weak_event_hints` 中的 clause / structure 条件提升 target 样本出现密度。
99. 已完成：新增 aggressive priority sampling 配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_sampling_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260314-026-offline-mvp-c1-7-round1-1-transition-aux-priority-sampling-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。
100. 已完成：新增 soft priority curriculum 配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_curriculum_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-027-offline-mvp-c1-7-round1-1-transition-aux-priority-curriculum-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-026 / EXP-027` 共同证明：
  - targeted sampling / curriculum 是当前第一条真正能显著改写 route-C 行为的杠杆
  - 当前问题已不再是“这个方向有没有效果”，而是“如何在三个指标之间找平衡”
- `EXP-026` aggressive 版：
  - final `target_validation.loss_total = 2.648178`
    - 当前最好
  - final `target_special_eval.delta_loss_total = 0.101163`
    - 明显变差
  - `step50 zero_e_evt.delta_target_loss_total = -0.933602`
    - 也更差
- `EXP-027` soft curriculum 版：
  - final `target_validation.loss_total = 2.813174`
    - 当前较差
  - final `target_special_eval.delta_loss_total = -0.075832`
    - 当前最好
  - `step50 zero_e_evt.delta_target_loss_total = -0.688658`
    - 明显优于 `EXP-021 / EXP-025 / EXP-026`
  - `step50 zero_z_art.delta_target_loss_total = -0.227706`
    - 也明显优于前几轮
- 这说明当前已经出现清晰三角 tradeoff：
  - main validation
  - special slice
  - `step50` stability

先说人话：
- 现在不是“还没找到有效杠杆”。
- 而是已经摸到有效杠杆了，但旋钮拧大拧小，出来的是不同偏向。

### 更新后的下一阶段任务
1. 不把 `EXP-026` 或 `EXP-027` 直接升为默认训练配置。
2. 保留 `C1.7 + independent clause_transition_aux` 为当前底座，不再回退。
3. 下一轮优先考虑：
   - 在 `EXP-026` 和 `EXP-027` 之间做中间档位 schedule
   - 继续只动采样 / curriculum，不回去改 loss 公式
   - 目标是找兼顾 main validation、special slice 和 `step50` 的平衡点

### 文档补充
- `docs/39_round1_1_c1_7_transition_aux_priority_sampling_run_report.md`
  - aggressive priority sampling 的接法、结果和 tradeoff。
- `docs/40_round1_1_c1_7_transition_aux_priority_curriculum_run_report.md`
  - soft priority curriculum 的接法、结果和 tradeoff。

## 2026-03-15 `round1.1 / C1.7 / midpoint priority schedule` 更新
### 当前进度补充
101. 已完成：新增中间档位 priority schedule 配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_midscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-028-offline-mvp-c1-7-round1-1-transition-aux-priority-midscale-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-028` 的目标是验证：
  - 在 `EXP-026` 和 `EXP-027` 之间做简单中间档位 schedule，能否得到更均衡的点
- 结果不是“中间更平衡”，而是：
  - final `target_special_eval.delta_loss_total = -0.093905`
    - 当前最好
  - `step50 zero_e_evt.delta_target_loss_total = -0.778543`
    - 比 `EXP-026` 好
    - 但不如 `EXP-027`
  - final `target_validation.loss_total = 2.861962`
    - 比 `EXP-027` 还差
- 这说明：
  - 采样 schedule 的简单线性插值，不会自动产生当前想要的 balance point
  - `EXP-028` 保住了 special-slice 优势，但没有保住 main validation，也没有把 `step50` 拉到 `EXP-027` 水平

先说人话：
- 中间档不等于中间结果。
- 这轮更像是在证明“取平均”本身不够。

### 更新后的下一阶段任务
1. 不把 `EXP-028` 升为默认训练配置。
2. 当前 `C1.7 + independent clause_transition_aux + targeted sampling` 的结论先钉死为：
   - `EXP-026` 更偏 main validation
   - `EXP-027` 更偏 special slice 和 `step50`
   - `EXP-028` 不是更优平衡点
3. 下一轮若继续推进采样 / curriculum，优先考虑：
   - 两段式 handoff 或更明确的 phase schedule
   - 不再只做单段式 ratio / duration 的中间插值

### 文档补充
- `docs/41_round1_1_c1_7_transition_aux_priority_midscale_run_report.md`
  - 中间档位 priority schedule 的结果和“线性折中并不自动平衡”的结论。

## 2026-03-15 `round1.1 / C1.7 / two-phase priority handoff` 更新
### 当前进度补充
102. 已完成：扩展 `targeted_sampling` 支持 `schedule_phases` 多阶段配置，并保持原有单段式 `priority_interleave` 兼容。
103. 已完成：新增两段式 handoff 配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-029-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-029` 证明：
  - 两段式 handoff 比单段式 ratio / duration 插值更有效
  - 它已经能同时改善 main validation 和 `step50`
- 关键结果：
  - final `target_validation.loss_total = 2.702175`
    - 明显优于 `EXP-027 / EXP-028`
    - 但仍不及 `EXP-026`
  - `step50 zero_e_evt.delta_target_loss_total = -0.463404`
    - 当前最好
  - `step50 zero_z_art.delta_target_loss_total = -0.163512`
    - 当前也最好
  - final `target_special_eval.delta_loss_total = 0.102328`
    - 几乎回到 `EXP-026` 的坏侧
- 这说明：
  - 当前主矛盾已经从“怎么让 `step50` 回升”转移到“怎么在保住这套 handoff 的同时，不把 final special slice 拉坏”
  - 下一轮更值得动的，不再是 schedule 的单纯强弱，而是 priority pool 的组成

先说人话：
- 两段式 handoff 这条路是有料的。
- 但它解决的是前中段动力学，不是 special slice 本身。

### 更新后的下一阶段任务
1. 不把 `EXP-029` 直接升为默认训练配置。
2. 保留 `C1.7 + independent clause_transition_aux + two-phase targeted sampling handoff` 作为当前最值得继续的骨架。
3. 下一轮若继续推进，优先考虑：
   - 保留两段式 schedule
   - 收窄或重定义 priority pool
   - 优先观察 final special slice 能否回升，而不是先继续扫 ratio / duration

### 文档补充
- `docs/42_round1_1_c1_7_transition_aux_priority_two_phase_run_report.md`
  - 两段式 handoff 的结果和“主矛盾已转向 priority pool 组成”的结论。

## 2026-03-15 `round1.1 / C1.7 / priority pool refinement` 更新
### 当前进度补充
104. 已完成：扩展 `targeted_sampling` 支持 `exclude_structure_types`，并跑通 `EXP-20260315-030-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-no-multiterm-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。
105. 已完成：新增 `clause>=4-only` 配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_clause_ge4_only_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-031-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-clause-ge4-only-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。
106. 已完成：扩展 `targeted_sampling.schedule_phases` 支持 phase-specific pool 过滤条件，并跑通 `EXP-20260315-032-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-pool-handoff-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-030 / EXP-031 / EXP-032` 把问题进一步钉死了：
  - `multi_terminal` 子池既是收益源，也是副作用源
  - final special slice 的坏影响大概率在前段就已经写进训练动力学
- `EXP-030`：
  - final `target_special_eval.delta_loss_total = -0.012386`
    - 明显好于 `EXP-029`
  - 但 final `target_validation.loss_total = 2.828666`
    - 明显更差
  - `step50 zero_e_evt.delta_target_loss_total = -0.823020`
    - 也明显更差
- `EXP-031`：
  - final `target_special_eval.delta_loss_total = -0.029908`
    - 比 `EXP-030` 再略好一点
  - 但 final `target_validation.loss_total = 2.843136`
    - 仍差
  - `step50 zero_e_evt.delta_target_loss_total = -0.843525`
    - 仍差
- `EXP-032`：
  - final `target_validation.loss_total = 2.672052`
    - 比 `EXP-029` 还更好
  - `step50 zero_e_evt.delta_target_loss_total = -0.556712`
    - 明显好于 `EXP-030 / EXP-031`
  - 但 final `target_special_eval.delta_loss_total = 0.103108`
    - 几乎和 `EXP-029` 一样差
- 这说明：
  - 后段再切换 pool，救不回 final special slice
  - 真正需要动的，已经不是 phase2 清理，而是 phase1 里 `multi_terminal` 的暴露方式本身

先说人话：
- 现在已经能确认，不是“后面补救不够”。
- 而是前面第一段怎么喂，基本已经把后面的 special 命运写下来了。

### 更新后的下一阶段任务
1. 不把 `EXP-030 / EXP-031 / EXP-032` 升为默认训练配置。
2. 当前更值得保留的骨架是：
   - `EXP-029` 的两段式 handoff
   - 以及 `EXP-032` 证明的“后段 cleanup 不够解决问题”
3. 下一轮若继续推进，优先考虑：
   - 直接改 phase1 的 `multi_terminal` 暴露方式
   - 例如单独限制 phase1 的 `multi_terminal` 份额
   - 而不是继续主要动 phase2 或后段 cleanup

### 文档补充
- `docs/43_round1_1_c1_7_two_phase_no_multiterm_run_report.md`
  - 全排 `multi_terminal` 后的结果。
- `docs/44_round1_1_c1_7_two_phase_clause_ge4_only_run_report.md`
  - 仅保留 `clause>=4` pool 的结果。
- `docs/45_round1_1_c1_7_two_phase_pool_handoff_run_report.md`
  - phase-specific pool handoff 的结果。

## 2026-03-15 `round1.1 / C1.7 / phase1 multi_terminal cap` 更新
### 当前进度补充
107. 已完成：扩展 `targeted_sampling` 支持 phase-specific `secondary_sampling` 子池与 `max_slots` 限额，并跑通 `EXP-20260315-033-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-multiterm-cap1-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。
108. 已完成：新增全 `multi_terminal` phase1 限额配置 `configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-033 / EXP-034` 共同说明：
  - phase1 给 `multi_terminal` 做份额限额，几乎救不回 final special
  - 但也不会明显破坏 `EXP-032` 的 main validation 与 `step50`
- `EXP-033`：
  - final `target_validation.loss_total = 2.663196`
    - 很强
  - `step50 zero_e_evt.delta_target_loss_total = -0.549967`
    - 也较强
  - final `target_special_eval.delta_loss_total = 0.111542`
    - 仍明显在坏侧
- `EXP-034`：
  - final `target_validation.loss_total = 2.669992`
    - 同样很强
  - `step50 zero_e_evt.delta_target_loss_total = -0.556362`
    - 与 `EXP-032 / 033` 同量级
  - final `target_special_eval.delta_loss_total = 0.105375`
    - 仍几乎不动
- 这说明：
  - final special 的坏影响不是简单的“phase1 里 `multi_terminal` 数量太多”
  - 继续在 phase1 采样份额上扫小变体，短期内已经不像高价值方向

先说人话：
- 现在已经不是“再把份额拧小一点就能变好”。
- 这条旋钮基本已经拧到头了。

### 更新后的下一阶段任务
1. 不把 `EXP-033 / EXP-034` 升为默认训练配置。
2. 当前 route-C 采样层先收口为：
   - `EXP-029 / EXP-032` 是 main validation + `step50` 的较强点
   - `EXP-030 / EXP-031` 是 final special 的较强点
   - `EXP-033 / EXP-034` 证明 phase1 限额微调不够解决冲突
3. 下一轮若继续推进，优先考虑：
   - 暂停继续扫采样细节
   - 回到评估定义或 special slice 表达本身
   - 或设计更直接的 special-oriented 监督，而不是继续在同一采样轴上抠

### 文档补充
- `docs/46_round1_1_c1_7_two_phase_multiterm_tail_cap_run_report.md`
  - `multi_terminal-only` 尾巴限额结果。
- `docs/47_round1_1_c1_7_two_phase_all_multiterm_cap_run_report.md`
  - phase1 全 `multi_terminal` 限额结果。

## 2026-03-15 `round1.1 / C1.8 / text_aux reweight` 更新
### 当前进度补充
109. 已完成：扩展 `offline_mvp.losses` 支持可选 `text_aux_reweight`，并补齐 `special_eval / ablation / special_eval_series` 的 effective `text_aux` 指标透传；新增配置 `configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-035-offline-mvp-c1-8-round1-1-text-aux-reweight-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-035` 证明：
  - punctuation-oriented `text_aux` reweight 确实是个真杠杆
  - 但“整段 100 step 常开”这版会把 late-stage 行为拉弯，不能直接当最终配置
- final 结果：
  - final `target_validation.loss_total = 2.889709`
    - 明显差于 `EXP-032` 的 `2.672052`
  - final `target_special_eval.delta_loss_total = 0.39305`
    - 明显差于 `EXP-032` 的 `0.103108`
  - final `zero_e_evt.delta_target_loss_total = 0.931855`
    - 明显弱于 `EXP-032` 的 `1.735497`
- 但它不是“完全失败”，因为 `special_eval_series` 还显示：
  - `step90 target_special_eval.delta_loss_total = -0.2803`
    - 比当前所有已落盘 final small-scale 结果都更强
  - 到 `step100` 才翻到 `0.39305`
  - 说明这条监督更像“需要阶段性收口”，而不是“方向本身没信号”
- `step50` 也呈现混合信号：
  - `zero_e_evt.delta_target_loss_total = -0.52895`
    - 比 `EXP-032` 的 `-0.556712` 略好
  - 但 `zero_z_art.delta_target_loss_total = -0.353743`
    - 比 `EXP-032` 的 `-0.187733` 更差
  - 说明中段回落没有被真正解决，只是换了表现方式

先说人话：
- 这次终于碰到一个“真的能把行为掰动”的非采样杠杆了。
- 但这版开得太久，后段把终点又带偏了。

### 更新后的下一阶段任务
1. 不把 `EXP-035` 升为默认训练配置。
2. 保留 `EXP-032` 的采样骨架，不回去继续抠 phase1 配额。
3. 下一轮若继续推进，优先考虑：
   - 把 `text_aux_reweight` 改成有阶段的 schedule
   - 例如前中段开启、后段衰减或关闭
   - 目标是保留 `step90` 附近的 special 收益，同时避免 `step100` 的 final 翻车

### 文档补充
- `docs/48_round1_1_c1_8_text_aux_reweight_run_report.md`
  - `EXP-035` 的结果与“常开 reweight 不成立，但阶段化 reweight 值得继续”的结论。

## 2026-03-15 `round1.1 / C1.8 / text_aux reweight schedule` 更新
### 当前进度补充
110. 已完成：扩展 `text_aux_reweight` 支持 `strength_schedule`，并新增配置 `configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_decay_smallscale_100_seeded_shuffle.json`，跑通 `EXP-20260315-036-offline-mvp-c1-8-round1-1-text-aux-reweight-decay-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。
111. 已完成：新增更早收口配置 `configs/offline_mvp_train_c1_8_round1_1_text_aux_reweight_early_decay_smallscale_100_seeded_shuffle.json`，跑通 `EXP-20260315-037-offline-mvp-c1-8-round1-1-text-aux-reweight-early-decay-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-036 / 037` 把 `EXP-035` 的尾段假设基本钉死了：
  - schedule 确实生效
  - 但 final 行为几乎不变
- `EXP-036`：
  - `step81-100` 线性衰减到普通 `text_aux`
  - final `target_validation.loss_total = 2.889944`
  - final `target_special_eval.delta_loss_total = 0.393366`
  - final `zero_e_evt.delta_target_loss_total = 0.931187`
- `EXP-037`：
  - `step61-90` 线性衰减到普通 `text_aux`
  - final `target_validation.loss_total = 2.890341`
  - final `target_special_eval.delta_loss_total = 0.392194`
  - final `zero_e_evt.delta_target_loss_total = 0.931406`
- 对照 `EXP-035`：
  - final `target_validation.loss_total = 2.889709`
  - final `target_special_eval.delta_loss_total = 0.39305`
  - final `zero_e_evt.delta_target_loss_total = 0.931855`
- 这说明：
  - 问题不是“后段多开了一点 reweight”
  - 而是更早阶段已经把共享表示空间写定了
  - 单纯做 late shutdown 几乎救不回 final

先说人话：
- 现在可以排除一种很诱人的解释了。
- 不是“最后二三十步尾巴没收干净”，而是更早就已经定型。

### 更新后的下一阶段任务
1. 不把 `EXP-036 / 037` 升为默认训练配置。
2. `C1.8` 这条线如果继续推进，不再优先做：
   - `step60+` 或 `step80+` 的 late decay 小变体
3. 下一轮更值得试的方向：
   - 更早的 phase handoff
   - 或直接拆 supervision target，而不是继续整体共用一个 `text_aux` 头做 reweight

### 文档补充
- `docs/49_round1_1_c1_8_text_aux_reweight_schedule_followup_report.md`
  - `EXP-036 / 037` 的合并结果与“late shutdown 基本无效”的结论。

## 2026-03-15 `round1.1 / C1.9 / text_aux split supervision` 更新
### 当前进度补充
112. 已完成：扩展 `offline_mvp.losses` 支持 `text_aux_split`，新增结构组 / 词汇组分离指标，并跑通 `EXP-20260315-038-offline-mvp-c1-9-round1-1-text-aux-structural-only-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-038` 说明：
  - 仅仅把 lexical 组权重打到 `0.0`
  - 还不足以把 final special 从坏平台里拉出来
- final 结果：
  - final `target_validation.loss_total = 2.89193`
  - final `target_special_eval.delta_loss_total = 0.398875`
  - final `zero_e_evt.delta_target_loss_total = 0.935605`
  - 都没有优于 `EXP-035 / 036 / 037`
- 但这轮也提供了新的结构性信息：
  - final validation `loss_text_aux_structural = 0.123682`
  - final validation `loss_text_aux_lexical = 0.359214`
  - final special `loss_text_aux_structural = 0.329909`
  - final special `loss_text_aux_lexical = 0.621452`
- 这说明：
  - structural supervision 确实被单独压住了
  - 但 lexical 组即使不参与 effective loss，仍在同一个 head 里明显漂移
  - 所以问题更像是“共享头 / 共享梯度路径”本身，而不只是 group weight 设多少

先说人话：
- 现在已经能确认，“把 lexical loss 关掉”这一步还不够。
- 更可能要把 lexical supervision 从 shared trunk 上真正拆开，而不是只在 loss 里不计分。

### 更新后的下一阶段任务
1. 不把 `EXP-038` 升为默认训练配置。
2. `text_aux` 这条线如果继续推进，不再优先做：
   - lexical 权重 `0.0 / 0.1 / 0.2` 这类小数微调
3. 下一轮更值得试的方向：
   - lexical head 走 detached hidden
   - 或直接拆成独立 head / 独立梯度路径
   - 目标是验证“lexical supervision 拖共享表示”是不是根因本体

### 文档补充
- `docs/50_round1_1_c1_9_text_aux_structural_only_run_report.md`
  - `EXP-038` 的结果与“同头 structural-only 仍不够”的结论。

## 2026-03-15 `round1.1 / C1.10 / detached lexical text_aux head` 更新
### 当前进度补充
113. 已完成：扩展 `offline_mvp.model` 支持 `text_aux` split heads，并新增配置 `configs/offline_mvp_train_c1_10_round1_1_text_aux_detached_lexical_head_smallscale_100_seeded_shuffle.json`，跑通 `EXP-20260315-039-offline-mvp-c1-10-round1-1-text-aux-detached-lexical-head-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-039` 是这条监督线第一次给出“方向被收窄”的硬证据：
  - detached lexical head 后
  - final `target_special_eval.delta_loss_total = 0.354963`
  - 虽然仍为正，但已经好于 `EXP-038` 的 `0.398875`
  - 也好于 `EXP-035 / 036 / 037` 的 `0.39x`
- 更关键的是 special gap 的成分变了：
  - final `delta_loss_text_aux_structural = 0.143281`
  - final `delta_loss_text_aux_lexical = 0.007416`
  - 说明 lexical 侧漂移已经基本被压住
  - 剩余主要矛盾转成了 structural 侧
- 但这轮并没有修掉另外两个核心问题：
  - final `target_validation.loss_total = 2.911644`
    - 仍弱于 `EXP-032` 的 `2.672052`
  - final `zero_e_evt.delta_target_loss_total = 0.949482`
    - 仍远弱于 `EXP-032` 的 `1.735497`
  - `step50 zero_z_art.delta_target_loss_total = -0.358804`
  - `step50 zero_e_evt.delta_target_loss_total = -0.532724`
    - 中段控制依赖回落仍在

先说人话：
- 这轮终于把“是不是 lexical 在拖 shared trunk”这件事打得更清楚了。
- 结论是：有，而且不小；但把 lexical 梯度切开以后，剩下暴露出来的是 structural 监督本身还不对。

### 更新后的下一阶段任务
1. 不把 `EXP-039` 升为默认训练配置。
2. `text_aux` 这条线如果继续推进，不再优先做：
   - lexical 权重小数微调
   - late schedule 小变体
   - sampler phase 配额微调
3. 下一轮更值得试的方向：
   - 把 structural supervision 再做独立路径或更细粒度拆分
   - 目标从“继续压 lexical”转到“直接重做 structural 侧的 runtime-proxy 对齐”

### 文档补充
- `docs/51_round1_1_c1_10_text_aux_detached_lexical_head_run_report.md`
  - `EXP-039` 的结果与“lexical gap 被削弱，但 structural gap 和 step50 仍未解决”的结论。

## 2026-03-15 `round1.1 / C1.11 / fully detached text_aux heads` 更新
### 当前进度补充
114. 已完成：扩展 `offline_mvp.model` 支持 `structural_detach_shared_input`，新增配置 `configs/offline_mvp_train_c1_11_round1_1_text_aux_fully_detached_heads_smallscale_100_seeded_shuffle.json`，并跑通 `EXP-20260315-040-offline-mvp-c1-11-round1-1-text-aux-fully-detached-heads-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-040` 基本把 `text_aux head` 这条结构改造线收口了：
  - 在 `EXP-039` 已经 detach lexical head 的前提下
  - 再把 structural head 也 detach
  - final 结果几乎不变
- 关键对照：
  - `EXP-039 final target_validation.loss_total = 2.911644`
  - `EXP-040 final target_validation.loss_total = 2.91453`
  - `EXP-039 final target_special_eval.delta_loss_total = 0.354963`
  - `EXP-040 final target_special_eval.delta_loss_total = 0.349915`
  - `EXP-039 final zero_e_evt.delta_target_loss_total = 0.949482`
  - `EXP-040 final zero_e_evt.delta_target_loss_total = 0.949163`
  - `step50` 的 `zero_z_art / zero_e_evt` 也几乎重合
- 同时 special gap 的成分并没有发生新变化：
  - final `delta_loss_text_aux_structural = 0.144724`
  - final `delta_loss_text_aux_lexical = 0.005451`
- 这说明：
  - lexical gradient 拖拽这件事已经被 `EXP-039` 基本处理掉
  - 但剩余 structural gap 并不是继续切 `text_aux` 梯度就能解决
  - 当前主矛盾更像 runtime 主干本身的 event / transition 学习还没对上 punctuation-only challenge

先说人话：
- 这轮的价值不是分数更高，而是把一条很可能浪费轮次的路彻底关掉了。
- 以后不用再围着 `text_aux head` 怎么 detach 继续打转了。

### 更新后的下一阶段任务
1. 不把 `EXP-040` 升为默认训练配置。
2. `text_aux` 这条线后续不再优先做：
   - detached head 变体
   - head 路径级小修补
3. 下一轮更值得试的方向：
   - 直接改 runtime 主干侧的 structural proxy
   - 重点放在 `event / clause_transition_aux / punctuation-only consistency`
   - 目标是直接打 final structural gap 和 `step50` 稳定性

### 文档补充
- `docs/52_round1_1_c1_11_text_aux_fully_detached_heads_run_report.md`
  - `EXP-040` 的结果与“text_aux head surgery 已收口，应转向 runtime structural proxy”的结论。

## 2026-03-15 `round1.1 / C1.12 / boundary contrast aux` 更新
### 当前进度补充
115. 已完成：扩展 `offline_mvp.losses` 支持 `boundary_contrast_aux`，并新增配置 `configs/offline_mvp_train_c1_12_round1_1_boundary_contrast_aux_smallscale_100_seeded_shuffle.json`，跑通 `EXP-20260315-041-offline-mvp-c1-12-round1-1-boundary-contrast-aux-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-041` 没有带来独立行为变化：
  - final `target_validation.loss_total = 2.924252`
    - 比 `EXP-039` 的 `2.911644` 更差
  - final `zero_e_evt.delta_target_loss_total = 0.949482`
    - 与 `EXP-039` 完全一样
  - `step50 zero_z_art / zero_e_evt` 也与 `EXP-039` 完全一样
- final `target_special_eval.delta_loss_total = 0.342355`
  - 表面上比 `EXP-039` 的 `0.354963` 略好
  - 但这是记账改善，不是行为改善
- 关键证据：
  - validation `loss_boundary_contrast_aux = 0.050434`
  - special `loss_boundary_contrast_aux = 0.0`
  - 其余 special 行为指标几乎全部重合：
    - `delta_loss_text_aux_structural = 0.143281`
    - `delta_loss_text_aux_lexical = 0.007416`
    - `delta_event_presence_prob_mean = -0.035345`
    - `delta_event_energy_prob_mean = -0.030103`
- 这说明：
  - `boundary_contrast_aux` 不是没接上
  - 但它与现有 `event_boundary_bias / clause_transition_aux` 高度重叠
  - 更重要的是，当前 special slice 上它并不激活，所以会把 `delta_loss_total` 人为拉好看

先说人话：
- 这轮最大的价值不是拿到更好结果，而是抓出了一个很容易误判的坑。
- 以后凡是新增只在 validation 生效、在 special 不生效的 loss，都不能再拿 `delta_loss_total` 直接下结论。

### 更新后的下一阶段任务
1. 不把 `EXP-041` 升为默认训练配置。
2. runtime structural proxy 这条线后续不再优先做：
   - `boundary_contrast_aux` 的 margin / weight 小变体
3. 下一轮更值得试的方向：
   - 直接做 special-oriented runtime proxy
   - 要求训练和 punctuation-only challenge slice 两边都能真实命中
   - 例如 punctuation-only consistency 或更显式的 challenge-like 目标约束

### 文档补充
- `docs/53_round1_1_c1_12_boundary_contrast_aux_run_report.md`
  - `EXP-041` 的结果与“boundary contrast 主要带来记账改善，不带来独立行为变化”的结论。

## 2026-03-15 `round1.1 / C1.13 / punctuation profile aux` 更新
### 当前进度补充
116. 已完成：扩展 `offline_mvp.losses` 支持 `punctuation_profile_aux`，并新增配置 `configs/offline_mvp_train_c1_13_round1_1_punctuation_profile_aux_smallscale_100_seeded_shuffle.json`，跑通 `EXP-20260315-042-offline-mvp-c1-13-round1-1-punctuation-profile-aux-100step-calibration` 的 dry-run、正式 `100 step`、final ablation、checkpoint-series ablation、final `special_eval` 和 `special_eval_series`。

### 当前阶段结论补充
- `EXP-042` 至少解决了 `EXP-041` 的一个口径问题：
  - 新 aux 不再只在 validation 生效
  - final validation `loss_punctuation_profile_aux = 0.01164`
  - final special `loss_punctuation_profile_aux = 0.001526`
  - 说明它在 challenge slice 上也真的激活了
- 但行为上仍然几乎没变化：
  - final `target_validation.loss_total = 2.910157`
    - 只比 `EXP-039` 的 `2.911644` 略好一点，基本打平
  - final `target_special_eval.delta_loss_total = 0.356926`
    - 反而略差于 `EXP-039` 的 `0.354963`
  - final `zero_e_evt.delta_target_loss_total = 0.948263`
    - 与 `EXP-039` 基本一致
  - `step50 zero_z_art = -0.358656`
  - `step50 zero_e_evt = -0.533721`
    - 中段回落也仍在
- 更关键的是，special 侧核心行为指标依旧没被改写：
  - `delta_event_presence_prob_mean = -0.035479`
  - `delta_event_energy_prob_mean = -0.030196`
  - `delta_loss_text_aux_structural = 0.143615`
  - `delta_loss_text_aux_lexical = 0.007612`
- 这说明：
  - 现在不是“special-oriented aux 没命中 challenge”
  - 而是即便命中了，它也没有变成新杠杆
  - auxiliary-loss 这条线在当前 scaffold 上，基本也接近收口了

先说人话：
- 这轮把最后一个很合理的疑问也打掉了。
- 不是因为之前的 aux 没打到 special；现在打到了，结果还是基本不动。

### 更新后的下一阶段任务
1. 不把 `EXP-042` 升为默认训练配置。
2. auxiliary-loss 这条线后续不再优先做：
   - `punctuation_profile_aux` 常数微调
   - 其他同类 utterance-profile proxy
3. 下一轮更值得试的方向：
   - checkpoint 选择 / 训练流程层
   - 或更强的数据视角改造
   - 不再优先继续堆新的小 aux

### 文档补充
- `docs/54_round1_1_c1_13_punctuation_profile_aux_run_report.md`
  - `EXP-042` 的结果与“special-oriented aux 已命中 challenge，但仍未形成新杠杆”的结论。

## 2026-03-15 `round1.1 / checkpoint selection` 更新
### 当前进度补充
117. 已完成：新增 `analyze-offline-mvp-checkpoint-selection` 正式分析命令，并对 `EXP-032 / 035 / 039 / 042` 的 `special_eval_series + checkpoint_series_eval` 做联合分析，产出 `reports/eval/offline_mvp_checkpoint_selection_round1_1/`。

### 当前阶段结论补充
- 这轮把“先做 checkpoint 选择 / 训练流程层”从猜测推进成了可复核结论：
  - `EXP-035 / 039 / 042` 都不是“完全没学到”
  - 而是 late window 内部存在稳定分叉
- 当前最关键的事实是：
  - `EXP-032 final` 仍是这四条轨迹里最强的 final checkpoint
  - 指标为：
    - `target_validation.loss_total = 2.672052`
    - `target_special_eval.delta_loss_total = 0.103108`
    - `zero_e_evt.delta_target_loss_total = 1.735497`
    - `zero_z_art.delta_target_loss_total = 1.275259`
- 但 `EXP-035 / 039 / 042` 都在 `step80/90/100` 呈现几乎同构的 late-window tradeoff：
  - `step80`
    - special 最好
    - `z_art / e_evt` 都仍为正且不弱
    - 但 validation 明显更差
  - `step90`
    - validation 与 `e_evt` 更强
    - special 仍为负
    - 但 `z_art` 已接近 `0`
  - `step100`
    - validation 达到本实验最好
    - 但 special 翻回正值
    - `e_evt` 也从 `step90` 回落
- 以 `EXP-042` 为例：
  - `step80`
    - `target_validation.loss_total = 4.282626`
    - `target_special_eval.delta_loss_total = -0.553492`
    - `zero_e_evt.delta_target_loss_total = 0.66439`
    - `zero_z_art.delta_target_loss_total = 0.550914`
  - `step90`
    - `target_validation.loss_total = 3.522161`
    - `target_special_eval.delta_loss_total = -0.295714`
    - `zero_e_evt.delta_target_loss_total = 1.520532`
    - `zero_z_art.delta_target_loss_total = 0.005477`
  - `step100`
    - `target_validation.loss_total = 2.910157`
    - `target_special_eval.delta_loss_total = 0.356926`
    - `zero_e_evt.delta_target_loss_total = 0.948263`
    - `zero_z_art.delta_target_loss_total = 0.178659`
- 这说明：
  - 简单的 validation-only early-stop 不够
  - 也不能直接凭 special 最低去选 checkpoint
  - 需要正式设计一个同时约束：
    - `target_validation`
    - `target_special_eval.delta_loss_total`
    - `zero_e_evt`
    - `zero_z_art`
    的联合 gate

先说人话：
- 现在不是“模型没学会”，而是“后段已经走到几个不同岔路口，但我们还没有靠谱的选点规则”。

### 更新后的下一阶段任务
1. 不直接把 `EXP-035 / 039 / 042` 的 early checkpoint 升为默认模型。
2. 下一轮优先做 checkpoint gate / early-stop 规则设计与离线复盘。
3. 若联合 gate 仍不能让 `EXP-035 / 039 / 042` 在可接受 validation 代价下稳定超过 `EXP-032 final`，再转更强的数据视角改造。

### 文档补充
- `docs/55_round1_1_checkpoint_selection_report.md`
  - `EXP-032 / 035 / 039 / 042` 的联合 checkpoint 选择分析，以及“当前需要联合 gate，而不是直接选 `step80` 或 `step90`”的结论。

## 2026-03-15 `round1.1 / checkpoint gate replay` 更新
### 当前进度补充
118. 已完成：新增 `analyze-offline-mvp-checkpoint-gates` 正式命令，并对 `EXP-032 / 035 / 039 / 042` 回放多种可解释的 checkpoint gate 原型，产出 `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1/`。

### 当前阶段结论补充
- 这轮把 gate 设计继续往前推了一步，但结论仍然偏收口而不是放量：
  - checkpoint 选择确实是个真问题
  - 但 gate 本身还不足以单独救回主线
- 当前 gate replay 的核心事实是：
  - 只要 gate 足够严格，结果就会退化回 final
  - 只要 gate 想明显救回 special，当前就只能在 `step80` 和 `step90` 两种代价之间二选一
- `late_special_unconstrained`
  - `035 / 039 / 042` 都会选到 `step80`
  - 平均相对 final：
    - `validation` 恶化 `+1.028644`
    - `special` 改善 `-0.68454`
    - `e_evt` 下降 `-0.20606`
    - `z_art` 回升 `+0.272127`
- `late_special_validation_guard_1p25`
  - `035 / 039 / 042` 都会选到 `step90`
  - 平均相对 final：
    - `validation` 恶化 `+0.463527`
    - `special` 改善 `-0.493718`
    - `e_evt` 回升 `+0.430689`
    - `z_art` 下降 `-0.139684`
- `late_special_strict_positive_control`
  - 结果直接退化回 final
  - 说明当前一旦同时要求：
    - 较严的 validation guard
    - `z_art` 不太低
    - `e_evt` 仍为正
    现有 late checkpoint 基本就只剩 `step100`
- 更关键的是：
  - 对非 `EXP-032` 实验来说
  - 当前没有任何一个 gate replay 选出的 checkpoint 能整体打赢 `EXP-032 final`

先说人话：
- 现在可以排除一种很省事的幻想了。
- 不是“发明一个更聪明的 early-stop”就能把后面几条实验自动扶正。

### 更新后的下一阶段任务
1. 不把当前 gate 直接写进训练主流程作为默认 checkpoint 选择器。
2. gate replay 先保留为离线诊断工具。
3. 下一轮优先级从“继续抠选点规则”转向：
   - 更强的数据视角改造
   - 或监督定义层级的更实质变化

### 文档补充
- `docs/56_round1_1_checkpoint_gate_replay_report.md`
  - 多种 checkpoint gate 原型的离线回放结果，以及“gate 不能单独救回主线，不应直接接入训练默认流程”的结论。

## 2026-03-15 `round1.1 / target special supervision blueprint` 更新
### 当前进度补充
119. 已完成：新增 `analyze-round1-target-special-supervision` 正式命令，并基于 `round1.1` split manifests + `c1_weak_event_hints` 生成 target-side special supervision sidecar，产出 `data_prep/round1_1/target_special_supervision/` 与 `reports/data/round1_1_target_special_supervision/`。

### 当前阶段结论补充
- 这轮把“更强的数据视角改造”从抽象方向推进成了可直接复用的数据底账。
- 关键事实已经明确：
  - `target_special_eval` 仍然是 `8` 条纯 nonverbal challenge：
    - lexical char 全为 `0`
    - pause / terminal / clause 全为 `0`
    - 时长范围 `0.470998 ~ 2.114989` 秒
    - 中位数 `0.956985` 秒
  - 训练/验证中最接近它的代理池已经被正式抽出来：
    - `challenge_proxy_core = 16`
    - 全部来自 `target_train`
    - lexical char 中位数 `1`
    - 时长中位数 `0.920998`
    - clause 中位数 `1`
    - pause / terminal 中位数 `1 / 0`
    - `final_terminal_type = none` 全部成立
  - 第二层放宽池：
    - `challenge_proxy_relaxed = 48`
    - lexical char 中位数 `4`
    - 时长中位数 `1.265986`
  - 另外三条规模已经足够大的结构 supervision 轴也被正式拆开：
    - `structural_multi_terminal = 174`
    - `structural_question_exclaim = 144`
    - `structural_clause_ge4 = 206`
- 这说明：
  - 下一轮不该再把“special 邻域压力”和“复杂结构表达”混成同一种 structural proxy
  - 数据/监督层至少应该拆成两层：
    - 一层是 `challenge_proxy_core`
    - 另一层是大规模结构 bucket

先说人话：
- 现在终于知道下一轮该重点喂什么样的样本了。
- `special` 邻域不是那几百条复杂长句，而是一小撮很短、很轻、没有真正句末收束的片段。

### 更新后的下一阶段任务
1. 保持 `target_special_eval` 为 `eval-only`。
2. 下一轮最小实验优先使用 `EXP-032` 骨架，只改数据/监督入口。
3. 优先尝试：
   - `challenge_proxy_core` 的 proxy-aware sampling / supervision
   - 加一条独立结构轴（优先级可在 `multi_terminal / question_exclaim / clause_ge4` 里单选）
4. 暂不建议把：
   - `challenge_proxy_core`
   - `structural_multi_terminal`
   - `structural_question_exclaim`
   - `structural_clause_ge4`
   直接混成一个统一权重的大 bucket。

### 文档补充
- `docs/57_round1_1_target_special_supervision_blueprint_report.md`
  - `round1.1` target-side special supervision sidecar、proxy pool 和结构 supervision bucket 的正式结论。

## 2026-03-15 `round1.1 / D1 / pool-aware sampling bootstrap` 更新
### 当前进度补充
120. 已完成：把 `target special supervision` sidecar 正式接入训练 sampler，并新增一份基于 `EXP-032` 骨架的候选配置 `offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json`，完成 dry-run 校验。

### 当前阶段结论补充
- 这轮最大的推进不是又多了一个分析报告，而是：
  - 训练代码现在真的支持按 pool membership 采样了。
- 当前已落地的能力：
  - `targeted_sampling` 主采样条件可直接使用：
    - `priority_pool_memberships`
    - `exclude_pool_memberships`
  - `secondary_sampling` 也支持同样的 pool membership 逻辑
  - `train plan` 会显式记录：
    - `target_special_supervision_path`
    - `priority_pool_memberships`
    - `exclude_pool_memberships`
- 当前候选配置的设计是：
  - 继续复用 `EXP-032` 的 `clause_transition_aux + event_boundary_bias`
  - 采样上改成：
    - phase1 `step1-25`
      - primary: `challenge_proxy_core`
      - secondary: `structural_multi_terminal`
      - `priority_ratio = 0.75`
    - phase2 `step26-45`
      - primary: `challenge_proxy_core`
      - `priority_ratio = 0.25`
    - `step46+`
      - seeded shuffle
- dry-run 已确认：
  - `target_special_supervision_path` 正常挂载
  - primary `challenge_proxy_core` 计数 `16`
  - phase1 priority union 计数 `172`
  - phase2 priority 计数 `16`
  - 训练前向与 loss 均正常

先说人话：
- 现在已经不是“知道该抽哪些样本”，而是“代码真的能按这些样本去抽了”。

### 更新后的下一阶段任务
1. 若继续推进实验线，优先直接起这份 `D1` 小规模验证。
2. 首轮只保留：
   - `challenge_proxy_core`
   - `structural_multi_terminal`
   这一主一次两层结构。
3. 若首轮无明显收益，再考虑把 secondary 结构轴切到：
   - `structural_question_exclaim`
   - 或 `structural_clause_ge4`

### 文档补充
- `docs/58_round1_1_special_proxy_core_multiterm_bootstrap_report.md`
  - pool-aware sampling 能力接入、候选配置与 dry-run 摘要。

## 2026-03-15 `round1.1 / D1 / special-proxy-core + multi-terminal` 更新
### 当前进度补充
121. 已完成：正式实跑 `EXP-20260315-017-offline-mvp-d1-round1-1-special-proxy-core-multiterm-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series，以及并入 `032 / 035 / 039 / 042` 的联合 checkpoint-selection / gate replay 对比。

### 当前阶段结论补充
- `D1` 没有成为新的主线解。
- final 指标为：
  - `target_validation.loss_total = 2.846479`
  - `target_special_eval.delta_loss_total = 0.412091`
  - `zero_e_evt.delta_target_loss_total = 0.86209`
  - `zero_z_art.delta_target_loss_total = 0.271847`
- 对比当前 anchor `EXP-032 final`：
  - validation 更差
  - special 更差
  - `e_evt / z_art` 也都更差
- 但 `D1` 不是纯无效轮次，它确实改了 late-window 形状：
  - `step80`
    - `target_validation.loss_total = 3.823698`
    - `target_special_eval.delta_loss_total = -0.411991`
    - `zero_e_evt.delta_target_loss_total = 1.223908`
    - `zero_z_art.delta_target_loss_total = 0.471141`
  - 相比 `035 / 039 / 042` 的 `step80`：
    - validation 代价更小
    - `e_evt` 更强
    - 但 special 改善没有那么深
- 把它并入联合分析后，结论仍然成立：
  - `EXP-032 final` 仍是 best final anchor
  - `non_anchor_joint_beating_count = 0` 仍未被打破

先说人话：
- `challenge_proxy_core` 这条线确实在改轨迹。
- 但当前 `challenge_proxy_core + multi_terminal` 这个组合，还不够把轨迹推到 anchor 之上。

### 更新后的下一阶段任务
1. 不把 `D1` 升为默认训练方案。
2. 若继续沿 pool-aware sampling 推进，primary 默认保留：
   - `challenge_proxy_core`
3. 下一轮更值得换的是 secondary 结构轴，而不是 primary：
   - `structural_multi_terminal`
   - `structural_question_exclaim`
   - `structural_clause_ge4`
   三者做最小对照。
4. 若只做一轮优先级最高的 follow-up，建议先试：
   - `challenge_proxy_core + structural_question_exclaim`
   因为它比 `multi_terminal` 更轻、更表达导向，也更可能避免再次被长复杂句主导。

### 文档补充
- `docs/59_round1_1_d1_special_proxy_core_multiterm_run_report.md`
  - `D1` 实跑结果，以及“primary 已证明有用，下一轮应优先换 secondary 结构轴”的结论。

## 2026-03-15 `round1.1 / D2+D3 / secondary axis comparison` 更新
### 当前进度补充
122. 已完成：正式实跑
    - `EXP-20260315-018-offline-mvp-d2-round1-1-special-proxy-core-question-exclaim-100step-calibration`
    - `EXP-20260315-019-offline-mvp-d3-round1-1-special-proxy-core-clause-ge4-100step-calibration`
    并将两者并入 `032 / 035 / 039 / 042 / 017` 的联合 checkpoint-selection / gate replay 对比。

### 当前阶段结论补充
- `D2` 基本没有提供新信息。
- 它和 `D1` 在 final 与 late-window 上几乎重合：
  - `D1 final = 2.846479 / 0.412091 / 0.86209 / 0.271847`
  - `D2 final = 2.848954 / 0.411368 / 0.855047 / 0.26885`
- 这说明：
  - 在当前 `25 / 45 / shuffle` 调度下，
  - secondary 从 `multi_terminal` 换成 `question_exclaim`，几乎不改变行为。

- `D3` 则是第一条真正改变 final 形状的 secondary axis：
  - final `target_validation.loss_total = 2.901056`
  - final `target_special_eval.delta_loss_total = 0.133206`
  - final `zero_e_evt.delta_target_loss_total = 1.135895`
  - final `zero_z_art.delta_target_loss_total = 0.179408`
- 对比 `D1 / D2`：
  - validation 更差
  - special 明显更好
  - `e_evt` 明显更强
  - `z_art` 更弱
- 对比 anchor `EXP-032 final = 2.672052 / 0.103108 / 1.735497 / 1.275259`：
  - `D3 final` 仍没有整体打赢 anchor
  - 但它是目前第一条把 final special 拉回到接近 anchor 区间的 pool-aware 线

- `D3` 的 late-window 也形成了新的最强 non-anchor positive-control special 点：
  - `step80 = 4.119759 / -0.642442 / 1.107988 / 0.513753`
- 联合 selection 明确给出：
  - `best_positive_control_late_special_experiment = EXP-019 step80`
- 但联合 gate replay 也仍然给出：
  - `non_anchor_joint_beating_count = 0`

先说人话：
- `question_exclaim` 这条线可以先停了。
- `clause_ge4` 才是当前最值得继续深挖的 secondary。
- 但现在还不是“换 checkpoint 就能赢”，而是“这条 secondary 终于真的改了 final 行为，下一步该围绕它调 schedule”。

### 更新后的下一阶段任务
1. primary 继续保留：
   - `challenge_proxy_core`
2. secondary 默认优先收敛到：
   - `structural_clause_ge4`
3. 下一轮更值得试的是：
   - `challenge_proxy_core + structural_clause_ge4`
   - 调 phase ratio / handoff / late shuffle 进入点
4. 暂不继续优先扩展：
   - `structural_question_exclaim`
5. 在没有新证据前，不把任何 D 系 gate 直接接入默认 checkpoint 选择流程。

### 文档补充
- `docs/60_round1_1_d2_d3_secondary_axis_comparison_report.md`
  - `D2 / D3` 实跑、联合 selection / gate replay，以及“当前 secondary 应收敛到 `clause_ge4`”的正式结论。

## 2026-03-15 `round1.1 / D4+D5 / clause_ge4 schedule follow-ups` 更新
### 当前进度补充
123. 已完成：新增 `D4` 配置 `offline_mvp_train_d4_round1_1_special_proxy_core_clause_ge4_early_handoff_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式实跑 `EXP-20260315-020-offline-mvp-d4-round1-1-special-proxy-core-clause-ge4-early-handoff-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series。
124. 已完成：新增 `D5` 配置 `offline_mvp_train_d5_round1_1_special_proxy_core_clause_ge4_late_handoff_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式实跑 `EXP-20260315-021-offline-mvp-d5-round1-1-special-proxy-core-clause-ge4-late-handoff-100step-calibration`，并将 `D4 / D5` 一起并入联合 checkpoint-selection / gate replay。

### 当前阶段结论补充
- `D4` 是当前最均衡的 `clause_ge4` schedule：
  - final `2.729466 / -0.00228 / 1.527013 / 0.199795`
- 对比 `D3 final = 2.901056 / 0.133206 / 1.135895 / 0.179408`：
  - validation 更好
  - special 更好
  - `e_evt` 更强
  - `z_art` 也略好
- 对比 anchor `EXP-032 final = 2.672052 / 0.103108 / 1.735497 / 1.275259`：
  - validation 已非常接近
  - final special 已经优于 anchor
  - 但 `e_evt` 与尤其 `z_art` 仍未追上

- `D5` 则证明继续延后 handoff 不是正路：
  - final `2.810181 / -0.031687 / 1.462891 / 0.137204`
- 它虽然拿到了当前全集里最好的 final special，
  但同时把 validation、`e_evt`、`z_art` 都拉回去了。

- 联合 selection / gate replay 的正式状态是：
  - `best_final_validation_experiment = EXP-032 final`
  - `best_final_e_evt_experiment = EXP-032 final`
  - `best_final_special_experiment = EXP-021 final`
  - `non_anchor_joint_beating_count = 0`

先说人话：
- `D4` 已经把这条线推进到“几乎够用了”的位置。
- `D5` 说明问题不再是 handoff 不够晚，而是继续追 special 会直接开始伤平衡。
- 所以下一步不该再横向扫 `D6 / D7` handoff，而该转去补 `z_art`。

### 更新后的下一阶段任务
1. `clause_ge4` 线的默认 schedule 基线更新为：
   - `D4`
2. 暂不继续优先扩展：
   - 更晚 handoff 的纯 schedule 变体
3. 下一轮若继续，优先方向应改为：
   - 在 `D4` 基线上补 `z_art` 保留
   - 或显式 dual-control 约束
4. `EXP-032 final` 仍保持当前 anchor。

### 文档补充
- `docs/61_round1_1_d4_d5_clause_ge4_schedule_followups_report.md`
  - `D4 / D5` 实跑、联合 replay，以及“`D4` 是当前最佳平衡 schedule，后续应从 schedule 调参转向补 `z_art`”的正式结论。

## 2026-03-15 `round1.1 / D6 / z_smooth decay follow-up` 更新
### 当前进度补充
125. 已完成：在 `offline_mvp` loss 权重解析中新增 `z_smooth_weight_schedule` 支持，并统一抽象 scalar schedule resolver；基于 `D4` sampler 新增配置 `offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式实跑 `EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series。
126. 已完成：将 `D6` 并入 `032 / 035 / 039 / 042 / 017 / 018 / 019 / 020 / 021` 的联合 checkpoint-selection / gate replay，对 `z_smooth` late decay 是否改变主线判断做正式回放。

### 当前阶段结论补充
- `D6` 的 schedule 确实生效，不是挂空配置：
  - `step60 z_smooth = 0.1`
  - `step70 z_smooth = 0.07`
  - `step80 z_smooth = 0.03666666666666668`
  - `step90 z_smooth = 0.02`
  - `step100 z_smooth = 0.02`
- 但它对行为几乎没有造成可用影响。
- `D6 final` 为：
  - `2.728306 / -0.001608 / 1.52269 / 0.20107`
- 对比 `D4 final = 2.729466 / -0.00228 / 1.527013 / 0.199795`：
  - validation 只略好
  - special 只略差
  - `e_evt` 只略差
  - `z_art` 只略好
- `D6 late window` 也几乎完全复刻 `D4`：
  - `step80 = 3.688544 / -0.307189 / 1.315578 / 0.412773`
  - `step90 = 3.428308 / -0.344274 / 1.520919 / -0.185088`
  - `step100 = 2.728306 / -0.001608 / 1.52269 / 0.20107`
- 联合 replay 的大图景不变：
  - `best_final_validation_experiment = EXP-032 final`
  - `best_final_e_evt_experiment = EXP-032 final`
  - `best_final_special_experiment = EXP-021 final`
  - `non_anchor_joint_beating_count = 0`

先说人话：
- `z_smooth` late decay 这条想法在工程上已经验证完了。
- 它不是 bug，也不是没生效。
- 但它没有成为当前 `z_art` 瓶颈的有效杠杆。

### 更新后的下一阶段任务
1. 不把 `D6` 升为默认方案。
2. 不继续优先扩展更多纯 `z_smooth` schedule sweep。
3. `clause_ge4` 线的默认 schedule 基线继续保持：
   - `D4`
4. 下一轮若继续，优先方向应从“平滑权重微调”转向：
   - 更显式的 `z_art` 保留机制
   - 或更明确的 dual-control-preservation 约束
5. 在没有新证据前，`EXP-032 final` 仍保持当前 anchor。

### 文档补充
- `docs/62_round1_1_d6_zsmooth_decay_followup_report.md`
  - `D6` 实跑、联合 replay，以及“schedule 生效但行为近乎不动，late `z_smooth` decay 不是当前主杠杆”的正式结论。
## 2026-03-15 `round1.1 / D7 / z_art influence run` 更新
### 当前进度补充
127. 已完成: 在 `offline_mvp` 中正式接入显式 `z_art` 保留机制 `z_art_influence_aux`，包括 target-side special supervision 挂载、fused control counterfactual hidden 导出，以及 target-pool-aware influence floor 计算；基于 `D4` sampler 新增配置 `offline_mvp_train_d7_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式实跑 `EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series。
128. 已完成: 将 `D7` 并入 `032 / 035 / 039 / 042 / 017 / 018 / 019 / 020 / 021 / 022` 的联合 checkpoint-selection / gate replay，对 explicit-control 机制是否改变主线判断做正式回放。
### 当前阶段结论补充
- `D7` 是当前第一条明确改出“行为级控制保留”的线:
  - final `2.73012 / -0.003131 / 3.489725 / 0.59961`
- 对比 `D4 final = 2.729466 / -0.00228 / 1.527013 / 0.199795`:
  - validation 基本持平
  - final special 基本持平
  - `zero_e_evt` 大幅抬升
  - `zero_z_art` 也明显抬升
- 这轮最关键的判断不是 `z_art_abs_mean`，而是:
  - final ablation sensitivity 真变强了
- 同时还确认了一点:
  - `loss_z_art_influence_aux` 在 final validation / special_eval 上为 `0.0`
  - 不是机制失效
  - 而是当前 aux 只挂在 `challenge_proxy_core`，eval slices 不包含这些样本
  - 因而 `D7` 的收益不能解释成“把 aux loss 算进 eval”
- `D7 late window` 也和 `D4 / D6` 不再同形:
  - `step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
  - `step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
  - `step100 = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- 联合 replay 的正式状态更新为:
  - `best_final_validation_experiment = EXP-032 final`
  - `best_final_special_experiment = EXP-021 final`
  - `best_final_e_evt_experiment = EXP-023 final`
  - `non_anchor_joint_beating_count = 0`

先说人话:
- `D7` 没有打赢 anchor。
- 但它已经不是“换个 schedule 看看”的近似平手轮次了。
- 它是当前第一条证明“显式 control-preservation 机制本身有杠杆”的线。
### 更新后的下一阶段任务
1. `clause_ge4 + explicit-control` 方向的默认新基线更新为:
   - `D7`
2. 暂不把 `D7` 直接升为全局 anchor。
3. 下一轮若继续沿这条线推进，优先级不再是:
   - 继续扫纯 `z_smooth` schedule
4. 而应优先验证:
   - 更高 `z_art` influence floor 是否还能继续抬 `z_art`
   - 或扩大 influence 覆盖范围，看看它能否从 proxy 样本推广到 `clause_ge4` 主线
### 文档补充
- `docs/63_round1_1_d7_zart_influence_run_report.md`
  - `D7` 实跑、联合 replay，以及“第一条真正改变控制行为的 explicit-control-preservation 机制”的正式结论。
## 2026-03-15 `round1.1 / D8 / z_art influence high-floor follow-up` 更新
### 当前进度补充
129. 已完成: 基于 `D7` 新增配置 `offline_mvp_train_d8_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_highfloor_smallscale_100_seeded_shuffle.json`，只把 `z_art_influence_aux.min_influence` 从 `0.12` 提到 `0.18`，完成 dry-run、正式实跑 `EXP-20260315-024-offline-mvp-d8-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-highfloor-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series。
130. 已完成: 将 `D8` 并入包含 `D7` 的联合 checkpoint-selection / gate replay，验证“继续抬同一条 floor”是否改变全局排序或轨迹形状。
### 当前阶段结论补充
- `D8 final` 为:
  - `2.730527 / -0.003362 / 3.480331 / 0.611369`
- 对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
  - validation 略差
  - special 略差
  - `e_evt` 略差
  - `z_art` 略好
- `D8 late window` 也几乎复制了 `D7`:
  - `step80 = 3.688259 / -0.306474 / 2.651286 / 1.0954`
  - `step90 = 3.427309 / -0.342909 / 2.798612 / 0.520328`
  - `step100 = 2.730527 / -0.003362 / 3.480331 / 0.611369`
- 联合 replay 的大图景不变:
  - `best_final_validation_experiment = EXP-032 final`
  - `best_final_special_experiment = EXP-021 final`
  - `best_final_e_evt_experiment = EXP-023 final`
  - `non_anchor_joint_beating_count = 0`

先说人话:
- `D8` 不是新 regime。
- 它更像 `D7` 的高 floor 近似重跑。
- 这说明“继续抬同一条 floor”已经很接近收益饱和。
### 更新后的下一阶段任务
1. `D7` 继续保持 explicit-control 线首选基线。
2. `D8` 不升为默认配置。
3. 后续若继续沿 `z_art_influence` 推进，优先级应从“继续抬 floor”转向:
   - 扩大 influence 覆盖范围
   - 或改变 influence 覆盖层级
4. 当前已新增一个待验证的下一轮候选:
   - `offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json`
   - 核心变化是把 `z_art_influence_aux.pool_memberships` 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + structural_clause_ge4`
### 文档补充
- `docs/64_round1_1_d8_zart_influence_highfloor_followup_report.md`
  - `D8` 实跑、联合 replay，以及“同形高 floor 已接近收益饱和，应转向 coverage 而非继续纯强度 sweep”的正式结论。
## 2026-03-15 `round1.1 / D9 / z_art influence dual-pool follow-up` 更新
### 当前进度补充
131. 已完成: 基于 `D7` 新增配置 `offline_mvp_train_d9_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_dualpool_smallscale_100_seeded_shuffle.json`，只把 `z_art_influence_aux.pool_memberships` 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + structural_clause_ge4`，完成 dry-run、正式实跑 `EXP-20260315-025-offline-mvp-d9-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-dualpool-100step-calibration`，并补齐 final ablation、final special_eval、checkpoint_series、special_eval_series。
132. 已完成: 将 `D9` 并入包含 `D7 / D8` 的联合 checkpoint-selection / gate replay，验证“扩大 influence 覆盖范围但不改目标形状”是否改变轨迹或全局排序。
### 当前阶段结论补充
- `D9 final` 为:
  - `2.730334 / -0.003173 / 3.486028 / 0.605922`
- 对比:
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `D8 final = 2.730527 / -0.003362 / 3.480331 / 0.611369`
- 结论很明确:
  - `D9` 没有把 `D7 / D8` 推离当前轨迹家族
  - 它只是再次停留在相同的 final balance 带
- `D9 late window` 也近乎同形:
  - `step80 = 3.688349 / -0.306361 / 2.658349 / 1.084989`
  - `step90 = 3.427322 / -0.342677 / 2.804947 / 0.511672`
  - `step100 = 2.730334 / -0.003173 / 3.486028 / 0.605922`
- 联合 replay 的大图景仍不变:
  - `best_final_validation_experiment = EXP-032 final`
  - `best_final_special_experiment = EXP-021 final`
  - `best_final_e_evt_experiment = EXP-023 final`
  - `non_anchor_joint_beating_count = 0`

先说人话:
- `D9` 把“扩大 coverage”这个猜想也验证完了。
- 这条 influence-hinge family 到现在为止，已经连续给出 `D7 / D8 / D9` 三个近同形答案。
- 所以接下来再在这条家族里继续抠 floor 或 pool，信息增益已经很低。
### 更新后的下一阶段任务
1. explicit-control 线默认基线继续保持:
   - `D7`
2. `D8 / D9` 作为边界确认与复现确认保留，不升为默认方案。
3. 下一轮若继续追 `z_art`，优先级应从当前 influence-hinge family 转向:
   - 新的目标形状
   - 或新的 phase / handoff 机制
   - 而不是继续做纯 floor / pure coverage sweep
4. 在没有新证据前，`EXP-032 final` 仍保持全局 anchor。
### 文档补充
- `docs/65_round1_1_d9_zart_influence_dualpool_followup_report.md`
  - `D9` 实跑、联合 replay，以及“扩大 coverage 但不改机制形状，仍会收敛到 `D7 / D8` 同一家族解”的正式结论。
## 2026-03-15 `round1.1 / D10+D11+D12 / explicit-control handoff sweep` 更新
### 当前进度补充
133. 已完成: 基于 `D7` explicit-control 基线新增三份 handoff 变体配置，并全部完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series:
   - `D10 = handoff 70`
   - `D11 = handoff 65`
   - `D12 = handoff 68`
### 当前阶段结论补充
- `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
  - 这是当前第一条把 `D5` 级别 final special 基本保留下来、
  - 同时不再重演 `D5` 控制塌缩的 explicit-control handoff 变体
- 但 `D10` 也没有打赢 `D7`
  - 相比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - 它是用约 `+0.08` validation 代价换来了更强 final special
- `D11 final = 2.762797 / 0.14741 / 2.706989 / 0.536627`
- `D12 final = 2.965061 / 0.16957 / 2.31394 / 0.465272`
- 这说明当前 explicit-control 条件下:
  - 有效 sweet spot 非常窄
  - 并且不在 `65 / 68`
  - `60 -> 70` 不是平滑插值，而是存在明显 cliff

先说人话:
- `D10` 是有用的。
- `D11 / D12` 则把这条线的有效区间收窄了。
- 现在不值得继续在 `60-70` 里做更密的 handoff 插值搜索。
### 更新后的下一阶段任务
1. explicit-control 主基线继续保持:
   - `D7`
2. `D10` 保留为:
   - “更强 final special、但 validation 更贵”的次基线
3. 暂不继续扩展更多 handoff 微调点。
4. 下一步若继续，应从 handoff sweep 转向:
   - 新的目标形状
   - 或新的训练 phase 机制
### 文档补充
- `docs/66_round1_1_d10_d11_d12_explicit_control_handoff_sweep_report.md`
  - `D10 / D11 / D12` 实跑，以及“D10 有效、D11/D12 证明 sweet spot 很窄”的正式结论。
## 2026-03-15 `round1.1 / D13+D14 / explicit-control late learning-rate decay` 更新
### 当前进度补充
134. 已完成: 在 `offline_mvp` 训练入口新增 `training.learning_rate_schedule` 支持，并把 effective learning rate 记入 dry-run、step log 与 validation history；新增两份 follow-up 配置:
   - `D13 = D7 + step71-100 late LR decay`
   - `D14 = D10 + step71-100 late LR decay`
   两轮均已完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- 新增的 optimizer-level schedule 工程能力是有效的，不是挂空配置:
  - `D13 step70 lr = 0.0003`
  - `step80 lr = 0.00022551724137931031`
  - `step90 lr = 0.00014275862068965515`
  - `step100 lr = 0.00006`
- 但 `D13 / D14` 都没有成为更平滑的 `D7 / D10`：
  - `D13 final = 3.27992 / -0.22848 / 2.950196 / 0.683167`
  - `D14 final = 3.307872 / -0.240493 / 2.892546 / 0.714912`
- 对比:
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
- 解释很明确:
  - 全局 late LR decay 确实保住了更负的 final special
  - 但它同时把 final validation 明显拉坏
  - `e_evt` 也没有继续长到原基线的 final 水平
  - 这更像“late under-convergence”，不是“修复过冲”

先说人话:
- 这轮不是找到更平滑的终段轨迹。
- 它更像是把 `D7 / D10` 的 late window 按在了一个更早、更粗糙的状态。
- 所以接下来不该继续扫全局 LR decay。

### 更新后的下一阶段任务
1. 不把 `D13 / D14` 升为默认方案。
2. 暂不继续优先扩展更多纯 `learning_rate_schedule` sweep。
3. 下一步若继续，应从“重训式 optimizer 调参”转向:
   - 不需要重训的新 phase 机制
   - 例如 late checkpoint averaging / weight interpolation
4. `D7` 继续保持 explicit-control 主基线。
5. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/67_round1_1_d13_d14_late_lr_decay_followup_report.md`
  - `D13 / D14` 实跑，以及“全局 late LR decay 会把 explicit-control 线拖进 under-converged final，不应继续纯 sweep”的正式结论。
## 2026-03-15 `round1.1 / D7+D10 / late checkpoint averaging probe` 更新
### 当前进度补充
135. 已完成: 新增正式命令 `average-offline-mvp-checkpoints`，支持对多个同构 offline MVP checkpoint 做均匀权重平均；基于该能力生成并评估了两组 late averaged checkpoints:
   - `D7 step90 + step100`
   - `D10 step90 + step100`
   两组 averaged checkpoint 都已完成 special_eval 与 ablation。

### 当前阶段结论补充
- averaged checkpoint 没有创造出新的主线解:
  - `D7 step90+100 avg = 2.978639 / -0.098031 / 3.035429 / 0.569171`
  - `D10 step90+100 avg = 3.030039 / -0.090497 / 2.858374 / 0.59141`
- 对比:
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
- 解释:
  - averaging 的确能把 `step90` 与 `step100` 之间的 tradeoff 做成中间态
  - 但它没有打出新的 joint winner
  - 依旧只是:
    - 更负的 final special
    - 换来更差的 validation
    - 同时 `e_evt` 也回落

先说人话:
- gate 不行
- global late LR decay 不行
- late checkpoint averaging 也不行
- 这说明当前瓶颈已经不在 late mechanics 本身了

### 更新后的下一阶段任务
1. 保留 `average-offline-mvp-checkpoints` 作为正式工具，但不把 averaged checkpoints 升为默认方案。
2. 暂不继续优先扩展更多 late averaging sweep。
3. 下一步若继续，应明确转回:
   - 新的目标形状
   - 或更强的 supervision 变化
4. `D7` 继续保持 explicit-control 主基线。
5. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/68_round1_1_d7_d10_late_checkpoint_averaging_report.md`
  - `D7 / D10` late averaging probe，以及“averaging 只能产生中间态，不能单独打破当前 tradeoff”的正式结论。
## 2026-03-15 `round1.1 / D15+D16 / challenge-profile aux` 更新
### 当前进度补充
136. 已完成: 在 `offline_mvp` 中新增 `challenge_proxy_profile_aux`，直接利用 `target_special_supervision` sidecar 中的 `special_proximity_score + final_terminal_type + pool_memberships` 对 `challenge_proxy_core` 样本施加 sample-level event profile 约束；基于 `D7` 新增并实跑:
   - `D15 = challenge profile aux`
   - `D16 = challenge profile aux + late proxy tail`
   两轮均已完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D15` 证明:
  - 新 aux 工程上生效
  - 但 final 近乎复刻 `D7`
  - `D15 final = 2.730729 / -0.003582 / 3.489731 / 0.599471`
- 进一步检查 step log 后确认:
  - `D15` 在 `step60` 后 `loss_challenge_proxy_profile_aux` 基本为 `0.0`
  - 原因是 late phase 已不再持续抽到 `challenge_proxy_core`
- `D16` 专门补了这件事:
  - 在 `step60-100` 保留 `priority_ratio = 0.125` 的 late proxy tail
  - 结果 `D16 final = 2.727232 / 0.157422 / 2.781072 / 0.533725`
- 这说明:
  - 一旦让这条 challenge-profile 目标形状持续进入 late phase
  - 它并不会产生更优解
  - 反而会把 final special 翻坏，并削弱 `e_evt / z_art`

先说人话:
- `D15` 不是正解，只是近似重跑。
- `D16` 则给了更关键的负证据:
  - 问题不在“late 没吃到样本”
  - 而在“这种 profile 目标一旦持续生效，会把轨迹推偏”

### 更新后的下一阶段任务
1. 保留 `challenge_proxy_profile_aux` 代码，但不继续优先扩展这一 family。
2. 不把 `D15 / D16` 升为默认方案。
3. 下一步若继续，应从:
   - challenge 邻域 profile
   转向:
   - 更强的结构监督定义变化
   - 或 challenge proxy 与结构轴之间更明确的 phase 分离
4. `D7` 继续保持 explicit-control 主基线。
5. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/69_round1_1_d15_d16_challenge_profile_aux_report.md`
  - `D15 / D16` 实跑，以及“challenge-profile target shape 不形成新解，持续进入 late phase 反而推坏 final”的正式结论。
## 2026-03-15 `round1.1 / D17 / structural_clause_profile late-only` 更新
### 当前进度补充
137. 已完成: 在 `offline_mvp` 中新增 `structural_clause_profile_aux`，支持 `structural_clause_ge4` pool-gated 的 late-only sample-level structural profile 约束，并同步扩展 `train_entry / special_eval / ablation_eval / special_eval_series` 的指标透传；基于 `D7` 新增配置 `offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D17` 不是挂空配置:
  - `step70 loss_structural_clause_profile_aux = 0.04029`, effective `weight = 0.0378947`
  - `step80 loss_structural_clause_profile_aux = 0.009333`, effective `weight = 0.08`
  - `step90 loss_structural_clause_profile_aux = 0.013067`, effective `weight = 0.08`
  - `step100 loss_structural_clause_profile_aux = 0.073294`, effective `weight = 0.08`
- 但 `D17 final` 近似数值级复刻 `D7 final`:
  - `D17 final = 2.730107 / -0.003152 / 3.491084 / 0.599597`
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D17` 的 late-window 也近似重合:
  - `D17 step80 = 3.688579 / -0.306971 / 2.659684 / 1.084378`
  - `D17 step90 = 3.427158 / -0.342993 / 2.807291 / 0.509014`
  - 对比 `D7 step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
  - 对比 `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- 这说明:
  - 当前这类基于 sidecar 的 sample-level structural profile，
  - 即使只挂在 `structural_clause_ge4`,
  - 即使只在 late phase 开启，
  - 也没有把 `D7` 推到新的行为 regime

先说人话:
- 这轮不是“结构监督终于起作用了，只是收益很小”。
- 更准确的说法是:
  - 它确实参与了后段优化，
  - 但几乎没有改变轨迹。
- 所以该停的不是“结构监督方向”，而是“这种 sample-level structural profile 形状”。

### 更新后的下一阶段任务
1. 保留 `structural_clause_profile_aux` 代码，但不继续优先扩展这一 family。
2. 不把 `D17` 升为默认方案。
3. 暂不继续优先做:
   - `structural_clause_profile_aux` 纯 weight sweep
   - `structural_clause_profile_aux` 纯启动步位 sweep
4. 下一步若继续沿结构监督推进，应转向:
   - boundary-local / frame-local 的结构监督
   - 不再继续停留在 sample-level event mean profile
5. `D7` 继续保持 explicit-control 主基线。
6. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/70_round1_1_d17_structural_clause_profile_late_only_report.md`
  - `D17` 实跑，以及“late-only structural sample-level profile 已被证明不能改写 D7 轨迹”的正式结论。
## 2026-03-15 `round1.1 / D18+D19 / structural_clause_transition follow-ups` 更新
### 当前进度补充
138. 已完成: 在 `offline_mvp` 中新增 `structural_clause_transition_aux`，把 clause-transition 的 boundary-local 结构监督改成 `structural_clause_ge4` pool-gated 的 late-only auxiliary，并同步扩展 `train_entry / special_eval / ablation_eval / special_eval_series` 的指标透传；基于 `D7` 新增 `D18` 配置 `offline_mvp_train_d18_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_transition_late_only_smallscale_100_seeded_shuffle.json`，完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
139. 已完成: 基于 `D18` 再新增 `D19` 配置 `offline_mvp_train_d19_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_transition_late_only_late_clause_tail_smallscale_100_seeded_shuffle.json`，仅增加 `step61-100` 的 `structural_clause_ge4` late tail，完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series，用于验证“不是目标本身无效，而只是 late exposure 不足”的假设。

### 当前阶段结论补充
- `D18` 不是挂空配置:
  - `step90 loss_structural_clause_transition_aux = 0.126826`, effective `weight = 0.18`
  - 说明 boundary-local structural aux 在 late window 确实命中过目标 batch
- 但 `D18 final` 近似数值级复刻 `D7 final`:
  - `D18 final = 2.729923 / -0.002973 / 3.490768 / 0.599433`
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- `D18` 的 late-window 也近似重合:
  - `D18 step80 = 3.68858 / -0.306975 / 2.65965 / 1.084377`
  - `D18 step90 = 3.42724 / -0.3432 / 2.807716 / 0.509011`
  - `D18 step100 = 2.729923 / -0.002973 / 3.490768 / 0.599433`
- `D19` 则给了更硬的负证据:
  - train plan 已确认 `step61-100` 新增 `priority_pool_memberships = ["structural_clause_ge4"]`
  - `phase_priority_record_counts` 末段是 `185`
  - 训练总时长也从 `D18` 的 `17.357207s` 增到 `44.900339s`
- 但 `D19 final` 明显更差:
  - `D19 final = 2.84661 / 0.219234 / 2.363735 / 0.441742`
  - 即 validation 变差、final special 翻正、`e_evt / z_art` 双回落
- 这说明:
  - `D18` 证明了 boundary-local structural aux 可以命中 late structural batch
  - `D19` 证明了即使强制 late structural exposure，这条 family 也不会自动形成新主线
  - 因而当前这类基于既有 sidecar pool 的 `structural_clause_transition_aux` 也应正式收口

先说人话:
- `D18` 还可以解释成“偶尔命中，但命中得不够稳定”。
- `D19` 把这个借口也补完了。
- 结论不是“再多喂一点 structural tail 就行”，而是“这条 boundary-local structural target shape 本身也没有形成新杠杆”。

### 更新后的下一阶段任务
1. 保留 `structural_clause_transition_aux` 代码，但不继续优先扩展这一 family。
2. 不把 `D18 / D19` 升为默认方案。
3. 暂不继续优先做:
   - `structural_clause_transition_aux` 纯 weight sweep
   - `structural_clause_transition_aux` 纯启动步位 sweep
   - `structural_clause_ge4` 纯 late-tail sweep
4. 下一步若继续推进“新目标形状 / 更强监督变化”，应转向:
   - 更高层级的 supervision-definition 跳变
   - 或不同的 phase / training decomposition
   - 而不是继续在当前 sidecar pool 上做 boundary-local 小变体
5. `D7` 继续保持 explicit-control 主基线。
6. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/71_round1_1_d18_d19_structural_clause_transition_followups_report.md`
  - `D18 / D19` 实跑，以及“boundary-local structural transition family 在现有 sidecar pool 上也已被证明不能打破 D7 tradeoff”的正式结论。
## 2026-03-15 `round1.1 / D20 / clause_ge4_no_final_terminal` 更新
### 当前进度补充
140. 已完成: 扩展 `target_special_supervision` sidecar，新增正式 pool `structural_clause_ge4_no_final_terminal`，并重跑 `analyze-round1-target-special-supervision`，将 `structural_clause_ge4 ∩ structural_no_final_terminal` 落成可复用 supervision bucket；新池当前画像为 `46` 条（`target_train = 38`, `target_validation = 8`）。
141. 已完成: 基于 `D7` 新增配置 `offline_mvp_train_d20_round1_1_special_proxy_core_clause_ge4_no_final_terminal_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json`，唯一主改动是将 phase1 secondary structural pool 从 `structural_clause_ge4` 换为 `structural_clause_ge4_no_final_terminal`；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D20 final` 没有打赢 `D7`:
  - `D20 final = 2.792781 / 0.277193 / 2.448193 / 0.430398`
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- 相对 `D19 final = 2.84661 / 0.219234 / 2.363735 / 0.441742`
  - `D20` 确实更温和
  - 但 final special 仍然翻正
  - `e_evt / z_art` 也仍低于 `D7`
- `D20` 的 late-window 也没有形成对 `D7` 的优势:
  - `D20 step80 = 3.932341 / -0.241696 / 2.122064 / 1.022158`
  - `D20 step90 = 3.508358 / -0.298419 / 2.730087 / 0.551189`
  - `D20 step100 = 2.792781 / 0.277193 / 2.448193 / 0.430398`
- 这说明:
  - 问题不只是整包 `clause_ge4` 里掺了太多 terminal-rich 样本
  - 即使把它拆成更干净的 `no_final_terminal` 子池，
  - 当前 clause-rich secondary axis 在 `D7` scaffold 上仍然会把 final 推向较差终盘

先说人话:
- 这轮不是“split 方向对了，但比例还没调好”。
- 更接近事实的说法是:
  - `clause_ge4` 家族已经被拆到一个很合理的小池，
  - 但它还是没把主线带出来。
- 所以当前不该继续在 `clause-rich` family 里做更细 sweep。

### 更新后的下一阶段任务
1. 保留 `structural_clause_ge4_no_final_terminal` sidecar pool，作为正式分析产物。
2. 不把 `D20` 升为默认方案。
3. 暂不继续优先做:
   - `clause_ge4` 子池切分 sweep
   - `no_final_terminal` 子池上的 handoff / ratio 微调
4. 下一步若继续推进，应转向:
   - 更不同的 supervision-definition 维度
   - 或不同的 phase / training decomposition
   - 而不是继续在 clause-rich family 内做更细拆分
5. `D7` 继续保持 explicit-control 主基线。
6. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/72_round1_1_d20_clause_ge4_no_final_terminal_run_report.md`
  - `D20` 实跑，以及“把 clause_ge4 拆成 no-final-terminal 子池也不足以打破 D7 tradeoff”的正式结论。
## 2026-03-15 `round1.1 / D21+D22 / teacher-consistency consolidation` 更新
### 当前进度补充
142. 已完成: 在 `offline_mvp` 训练入口新增 `training.init_checkpoint_path` 与 `training.teacher_consistency`，支持从 checkpoint 初始化 student，并对 target batch 施加 pool-gated、frozen-teacher 的 `event_logits + z_art` consistency；本轮不改评估逻辑，只新增训练能力与 step 指标透传。
143. 已完成: 基于该能力新增并实跑两条最小 consolidation 线，均完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series:
   - `D21 = D10 init + D10 teacher`
   - `D22 = D7 init + D10 teacher`

### 当前阶段结论补充
- `D21 / D22` 的 teacher consistency 都不是挂空:
  - `D21 step30 loss_teacher_consistency = 0.28094`
  - `D22 step30 loss_teacher_consistency = 0.385431`
- `D21 final`:
  - `2.441712 / 0.181901 / 2.919652 / 0.391864`
  - 说明单锚 `D10 -> D10` 会显著改善 validation，
  - 但保不住 `D10` 的 final special，也会削弱控制保留
- `D22 final`:
  - `2.444194 / 0.140001 / 3.299035 / 0.438936`
  - 相对 `D21`:
    - validation 近似持平
    - special 更好
    - `e_evt / z_art` 都更强
  - 相对 `D7`:
    - validation 显著更好
    - 但 special 仍翻正
    - `z_art` 仍明显偏低
- 这说明:
  - teacher-consistency consolidation 这条大方向不是纯负例
  - 它已经能产生新的高-validation / 高-e_evt 行为
  - 但当前 `challenge_proxy_core` 窄 gate 还不足以保住 formal special 与 `z_art`

先说人话:
- `D21` 证明“拿 D10 自己蒸自己”不行。
- `D22` 则说明这条 family 还没死，它确实能拉出新的行为。
- 当前问题更像“teacher gate 太窄”，而不是“teacher consistency 机制本身没用”。

### 更新后的下一阶段任务
1. 保留 `teacher_consistency` 代码，不回退这条能力。
2. 不把 `D21 / D22` 升为默认方案。
3. 暂不继续优先做:
   - 单锚 `D10 -> D10` 的更多微调
   - 当前窄 gate 上的纯 `weight / lr` sweep
4. 下一步若继续沿这条 family 推进，优先转向:
   - `D7 init + D10 teacher`
   - 扩 teacher gate 覆盖
   - 例如 `challenge_proxy_core + challenge_proxy_relaxed`
   - 或 `challenge_proxy_core + short_pause_no_terminal`
5. `D7` 继续保持 explicit-control 主基线。
6. `D10` 继续保持“更强 final special、但 validation 更贵”的次基线。

### 文档补充
- `docs/73_round1_1_d21_d22_teacher_consistency_consolidation_report.md`
  - `D21 / D22` 实跑，以及“teacher-consistency 方向值得保留，但当前 `challenge_proxy_core` 窄 gate 还不足以保住 formal special”的正式结论。
## 2026-03-15 `round1.1 / D23 / teacher-consistency relaxed gate` 更新
### 当前进度补充
144. 已完成: 新增并实跑 `D23 = D7 init + D10 teacher + (challenge_proxy_core + challenge_proxy_relaxed)`，配置为 `offline_mvp_train_d23_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_smallscale_30_seeded_shuffle.json`；已完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D23` 的 broadened teacher gate 确实持续 active:
  - `step10 loss_teacher_consistency = 0.078484`
  - `step30 loss_teacher_consistency = 0.387194`
- `D23 final`:
  - `2.442024 / 0.142199 / 3.289808 / 0.43533`
- 对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation 只有极小幅改善
  - final special 略差
  - `e_evt / z_art` 也都略弱
- `D23` 的 late-window 也没有隐藏新解:
  - `D23 step10 = 2.592393 / 0.135164 / 3.053715 / 0.419647`
  - `D23 step20 = 2.471498 / 0.174403 / 3.042276 / 0.401863`
  - `D23 step30 = 2.442024 / 0.142199 / 3.289808 / 0.43533`
- 这说明:
  - `challenge_proxy_relaxed` 并没有把 `D22` 推成新的 Pareto 点
  - 问题已经不再能简单归结为“coverage 还不够宽”
  - 当前更准确的判断是:
    - `challenge_proxy_relaxed` 这层 gate 扩展本身信息增益不高
    - teacher-consistency 若继续推进，应改试更有结构差异的 teacher gate 或更不同的蒸馏目标

先说人话:
- `D22` 像是已经找到了这条 family 的一个有意义站位。
- `D23` 只是把同一站位轻微抖了一下，没有走到新地方。
- 所以下一步不该继续平铺更宽的 challenge-relaxed coverage。

### 更新后的下一阶段任务
1. 保留 `teacher_consistency` 代码，不回退。
2. 不把 `D23` 升为默认方案。
3. `D22` 暂时保持 teacher-consistency family 主参考点。
4. 暂不继续优先做:
   - `challenge_proxy_relaxed` 方向的更多 weight sweep
   - `challenge_proxy_relaxed` 方向的更多 coverage 扩展
5. 下一步若继续沿 teacher-consistency family 推进，优先转向:
   - 更有结构差异的 teacher gate
   - 例如 `challenge_proxy_core + short_pause_no_terminal`
   - 或改变蒸馏目标形状，而不是继续只扩 challenge-relaxed coverage

### 文档补充
- `docs/74_round1_1_d23_teacher_consistency_relaxedgate_report.md`
  - `D23` 实跑，以及“`challenge_proxy_core + challenge_proxy_relaxed` 扩 gate 基本复刻 `D22`，不形成新 joint winner”的正式结论。
## 2026-03-15 `round1.1 / D24+D25+D26 / short-pause teacher gate` 更新
### 当前进度补充
145. 已完成: 新增并实跑 `D24 = D22 + (teacher gate -> challenge_proxy_core + short_pause_no_terminal)`；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
146. 已完成: 在 `D24` 基础上新增并实跑 `D25`，把 `targeted_sampling.priority_pool_memberships` 也扩到 `["challenge_proxy_core", "short_pause_no_terminal"]`；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
147. 已完成: 新增并实跑 `D26`，将 `D25` 的 consolidation 截到 `20` step，验证 `D25 step20` 是否可稳定固化为 final；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `short_pause_no_terminal = 19`，其中与 `challenge_proxy_core` 重叠 `15`，真正新增样本只有 `4` 条。
- `D24 final` 与 `D22 final` 数值级完全一致:
  - `D24 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
  - 而且那 `4` 条 `short_pause_only` 样本在 30-step target batch 中一次都没出现
  - 说明“只扩 teacher gate、不改 sampler”在这条 short-pause family 上会直接退化成空覆盖负例
- `D25 final` 没有打赢 `D22`:
  - `D25 final = 2.444897 / 0.176357 / 2.993643 / 0.403509`
  - 但 `D25` 的价值在中段:
    - `D25 step10 = 2.620166 / 0.081417 / 3.227018 / 0.465696`
    - `D25 step20 = 2.523898 / 0.117894 / 3.27265 / 0.460259`
  - 它形成了一条更偏 special / `z_art`、但 validation 更贵的新轨迹
- `D25` 的轨迹改变并不是因为 `short_pause_only` 真被采到了:
  - 这 `4` 条样本在 `D25` 的 30-step target batch 里也仍然一次都没出现
  - 更合理的解释是:
    - 扩大 priority pool 改变了 overlap 样本的抽样顺序与组合
    - 从而通过 overlap-driven reordering 改变了轨迹
- `D26 final`:
  - `2.523898 / 0.117894 / 3.27265 / 0.460259`
  - 与 `D25 step20` 完全一致
  - 说明 `D25 step20` 不是偶然 checkpoint，而是可稳定复现的新 family 点

先说人话:
- `D24` 告诉我们: 只改 gate 名字不够。
- `D25` 告诉我们: sampler 的 pool 组成即使没把新增样本采进来，也能通过重排 overlap 样本改变轨迹。
- `D26` 则把这个中段好点正式固定了下来。

### 更新后的下一阶段任务
1. 保留 `teacher_consistency` 能力，不回退代码。
2. `D22` 保持 teacher-consistency family 的 validation-oriented 参考点。
3. `D26` 升为 teacher-consistency family 的 special / `z_art`-leaning 参考点。
4. `D24` 不升为默认方案。
5. `D25` 保留为关键轨迹证据，但不作为默认 final。
6. 若继续沿 short-pause family 推进，优先改去:
   - 显式确保 `short_pause_only` 的 `4` 条样本真正进入训练
   - 而不是继续只改 pool 名称层面的 coverage

### 文档补充
- `docs/75_round1_1_d24_d25_d26_shortpause_teacher_gate_followups_report.md`
  - `D24 / D25 / D26` 实跑，以及“`D24` 是空覆盖负例、`D25` 改变轨迹、`D26` 固化 `D25 step20` 为新 family 点”的正式结论。
## 2026-03-15 `round1.1 / D27 / forced short-pause record ids` 更新
### 当前进度补充
148. 已完成: 为 `targeted_sampling.priority_interleave` 新增最小能力 `priority_record_ids`，支持在 priority slot 中先消耗指定 record ids；训练计划摘要也已同步暴露该字段。
149. 已完成: 基于 `D26` 新增并实跑 `D27`，将 `short_pause_only` record ids 显式注入 priority slot；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D27` 不再是“只改 pool 名称”的实验:
  - dry-run step0 已命中 `target::chapter3_2_firefly_191`
  - 正式训练 step1/2/3 也分别命中:
    - `target::chapter3_2_firefly_191`
    - `target::chapter3_3_firefly_148`
    - `target::chapter3_3_firefly_125`
- `short_pause_only` 候选共 `4` 条，但其中 `target::chapter3_2_firefly_212` 在 formal `target_validation`
  - 所以 `D27` 实际上已经把 train-side short-only 样本打满了
- `D27 final`:
  - `2.466208 / 0.206141 / 2.863938 / 0.356843`
- 对比 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`:
  - validation 更好
  - 但 final special 更差
  - `e_evt / z_art` 都明显回落
- 对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation 也没有形成足够优势
  - special / `e_evt` / `z_art` 全部更弱
- `D27 step10 = 2.573033 / 0.177756 / 2.89979 / 0.379443`
  - 说明这条 forced short-only 注入线也没有隐藏更好的 early checkpoint

先说人话:
- `D27` 已经把“是不是根本没见到 short-only 样本”这个问题彻底排除了。
- 现在可以更硬地说:
  - 不是 short-only 没进训练
  - 而是它一旦真进来，方向就是会把 `D26` 这条线推坏

### 更新后的下一阶段任务
1. 保留 `priority_record_ids` 代码能力，不回退。
2. 不把 `D27` 升为默认方案。
3. `D22` 继续保持 teacher-consistency family 的 validation-oriented 参考点。
4. `D26` 继续保持 teacher-consistency family 的 special / `z_art`-leaning 参考点。
5. 暂不继续优先做:
   - short-pause-only 的更强注入
   - short-pause-only 的更高 priority ratio
   - short-pause-only 的更长 consolidation
6. 下一步若继续推进 teacher-consistency family，优先转向:
   - family 参考点之间的 cross-anchor consolidation
   - 或更不同的 distillation target shape

### 文档补充
- `docs/76_round1_1_d27_forced_shortpause_recordids_report.md`
  - `D27` 实跑，以及“train-side short-only 样本一旦真正进入训练，会把 `D26` 这条 family 点推坏”的正式结论。
## 2026-03-15 `round1.1 / D28+D29+D30 / cross-anchor consolidation` 更新
### 当前进度补充
150. 已完成: 新增并实跑 `D28 = D22 init + D26 teacher` 与 `D29 = D26 init + D22 teacher`，两条线均完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
151. 已完成: 在 `D29` 基础上新增并实跑 `D30 event-only`，唯一变量为 `teacher_consistency.z_art_weight = 0.0`；完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。

### 当前阶段结论补充
- `D28 final`:
  - `2.349798 / 0.200419 / 2.617499 / 0.307252`
  - 是当前 teacher-consistency family 里最强 validation 压缩点
  - 但 special / `e_evt` / `z_art` 代价过大
- `D29 final`:
  - `2.397175 / 0.171769 / 2.978481 / 0.364927`
  - 比 `D28` 更平衡
  - 比 `D26` 明显更强 validation
  - 又没有像 `D28` 那样把控制压得太狠
  - 形成了一个清晰的 cross-anchor middle anchor
- `D30 final`:
  - `2.399277 / 0.169748 / 2.982002 / 0.377184`
  - 与 `D29 final` 基本数值级重合
  - 说明 `D29` 的 tradeoff 不是由 teacher `z_art` term 单独主导
- `D28 / D29 / D30` 都没有隐藏更好的 checkpoint:
  - 各自 final 已是本轮最佳 tradeoff

先说人话:
- 参考点互蒸是有用的，但它现在更像“造一个中间锚点”，不是“直接打出新冠军”。
- `D29` 是这条线里目前最像可保留资产的点。
- `D30` 则把一个常见猜测也测掉了:
  - 问题不只是 teacher `z_art` 拉得太多

### 更新后的下一阶段任务
1. 保留 cross-anchor consolidation 路线，不回退代码。
2. `D29` 升为 cross-anchor family 主参考点。
3. `D22 / D26 / D29` 现在形成三锚结构:
   - validation-oriented
   - special / `z_art`-leaning
   - cross-anchor middle
4. `D28` 不升为默认方案。
5. `D30` 不再继续扩 family。
6. 下一步若继续推进，优先转向:
   - 更不同的 distillation target shape
   - 或基于三锚结构的明确 gate / selection
   - 而不是继续抠单条 cross-anchor 小变体

### 文档补充
- `docs/77_round1_1_d28_d29_d30_cross_anchor_consolidation_report.md`
  - `D28 / D29 / D30` 实跑，以及“cross-anchor 能造出中间锚点，但目前仍主要是在 validation 与 special/control 之间做更可控 tradeoff”的正式结论。
## 2026-03-15 `round1.1 / D22+D26+D29 / three-anchor selection analysis` 更新
### 当前进度补充
152. 已完成: 新增 `analyze-offline-mvp-anchor-selection` 正式命令，并对 `D22 / D26 / D29` 的 final anchors 做正式 selection 分析，产出 `reports/eval/offline_mvp_anchor_selection_round1_1_d22_d26_d29/`。

### 当前阶段结论补充
- `D29 final` 现在是三锚里的 validation leader:
  - `2.397175 / 0.171769 / 2.978481 / 0.364927`
- `D26 final` 现在是三锚里的 special / `z_art` leader:
  - `2.523898 / 0.117894 / 3.27265 / 0.460259`
- `D22 final` 现在是三锚里的 `e_evt` leader:
  - `2.444194 / 0.140001 / 3.299035 / 0.438936`
- 形式化 regret 分析表明:
  - `D22` 是当前三锚里的 minimax anchor
  - 它不是单项冠军
  - 但它是 least-worst 的默认 final reference
- validation budget switchpoint 已经收口:
  - `+0.0` 只能选 `D29`
  - `+0.047019` 之后 `D22` 才进入可选集，并成为 tight-budget 下的 best special / best `e_evt` / best minimax
  - `+0.126723` 之后 `D26` 才进入可选集，并接管 best special / best `z_art`
- dual-control floor 也已收口:
  - `D22` floor 与 `D26` floor 互斥
  - 当前不存在一个 final anchor 同时覆盖 `D22` 级 `e_evt` 与 `D26` 级 `z_art`

先说人话:
- 现在不是“三个锚里谁整体最好”。
- 更准确的是:
  - `D29` 负责 validation
  - `D26` 负责 special / `z_art`
  - `D22` 负责最稳的默认折中

### 更新后的下一阶段任务
1. 停止沿用过时的锚点标签，特别是不再把 `D22` 记作当前 validation anchor。
2. 若继续做 route / reporting policy，默认以三锚结构为准:
   - `D29 = validation anchor`
   - `D26 = special / z_art anchor`
   - `D22 = minimax default anchor`
3. 若继续开新训练，优先围绕某一个明确 anchor objective 设计新的 target shape 或 selector。
4. 暂不优先继续做:
   - 更密的 cross-anchor 小变体
   - 继续猜测某一个小 loss tweak 能自然合并 `D22 floor` 与 `D26 floor`

### 文档补充
- `docs/78_round1_1_d22_d26_d29_three_anchor_selection_report.md`
  - `D22 / D26 / D29` 的正式 final-anchor selection 分析，以及“`D29` 是 validation leader、`D26` 是 special / `z_art` leader、`D22` 是 minimax default anchor”的收口结论。
## 2026-03-15 `round1.1 / D22+D26+D29 / anchor route policy` 更新
### 当前进度补充
153. 已完成: 新增 `analyze-offline-mvp-anchor-routes` 正式命令，并将三锚 final 结论固化为标准 route-selector / reporting policy，产出 `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d26_d29/`。

### 当前阶段结论补充
- 标准 policy profile 已经固定:
  - `validation_strict -> D29`
  - `default_minimax -> D22`
  - `guarded_default -> D22`
  - `e_evt_guard -> D22`
  - `special_push -> D26`
  - `z_art_push -> D26`
- 当前最有价值的 route switch 规则也已经固定:
  - `max_validation_budget_over_best < 0.047019`
    - 走 `validation_strict`
    - 选 `D29`
  - `max_validation_budget_over_best >= 0.047019`
    - 且没有强 `special / z_art` 优先级
    - 走 `default_minimax`
    - 选 `D22`
  - `max_validation_budget_over_best >= 0.126723`
    - 且明确 `special_priority` 或 `z_art_priority`
    - 走 `special_push`
    - 选 `D26`

先说人话:
- 这一步之后，三锚已经不只是“分析上成立”。
- 它已经可以作为正式 reporting policy 使用。

### 更新后的下一阶段任务
1. 后续若继续做评估或汇总，默认先声明 route，再声明 anchor。
2. 若继续开新训练，必须先声明想打的 route:
   - `validation_strict`
   - `default_minimax`
   - `special_push`
3. 暂不优先继续做:
   - 没有 route 目标声明的中间态 follow-up
   - 继续手工用自然语言猜“这轮更像哪个 anchor”

### 文档补充
- `docs/79_round1_1_d22_d26_d29_anchor_route_policy_report.md`
  - 三锚 route-selector / reporting policy 的正式固化，以及“`D29 -> D22 -> D26`”的预算驱动切换规则。
## 2026-03-15 `round1.1 / anchor route selector + template update` 更新
### 当前进度补充
154. 已完成: 新增 `select-offline-mvp-anchor-route` 正式命令，支持按 budget / priority / floor 选择当前三锚 route；并完成三种典型场景实跑验证。
155. 已完成: 更新 `reports/templates/experiment_record_template.md`，加入 `route_policy / route_budget_or_floor / anchor_reference` 字段。

### 当前阶段结论补充
- selector 已实跑验证:
  - `budget = 0.0 -> validation_strict -> D29`
  - `budget = 0.05 -> default_minimax -> D22`
  - `budget = 0.13 + special_priority -> special_push -> D26`
- 这意味着:
  - 三锚 route 现在不只是“能分析”
  - 也已经能被单次调用、直接执行
- 模板层也已经补齐:
  - 后续 experiment record 应显式记录 route policy、route budget/floor、anchor reference

先说人话:
- 到这一步，三锚的“分析 -> policy -> selector -> 模板记录”链已经闭环了。

### 更新后的下一阶段任务
1. 后续若继续做新实验或新一轮比较，默认先跑 selector，再写 experiment record。
2. 后续报告若引用 reference anchor，默认附上 selector 输入或 route 条件。
3. 暂不优先继续扩更多三锚选择器变体。

### 文档补充
- `docs/80_round1_1_anchor_route_selector_and_template_report.md`
  - selector 命令、三种典型 route 实跑验证，以及 experiment record 模板 route 字段更新。
## 2026-03-15 `round1.1 / route selector -> init-experiment integration` 更新
### 当前进度补充
156. 已完成: 为 `init-experiment` 新增 `--route-selection`，支持直接消费 selector json，并自动填充 `route_policy / route_budget_or_floor / anchor_reference`。
157. 已完成: 用 `default_minimax` selector 产物做 smoke 验证，确认 experiment record 自动落入 route 字段。

### 当前阶段结论补充
- `init-experiment` 已正式接通 selector:
  - 不再需要手工抄 route policy
  - 不再需要手工抄 budget/floor
  - 不再需要手工抄 anchor reference
- smoke 结果已经确认:
  - `route_policy = default_minimax`
  - `route_budget_or_floor` 已自动写入 selector 输入
  - `anchor_reference` 已自动写入 `D22`

先说人话:
- 到这一步，三锚选择链已经从“分析基础设施”真正接进了实验立项。

### 更新后的下一阶段任务
1. 后续如需新建实验记录，默认使用:
   - `select-offline-mvp-anchor-route`
   - `init-experiment --route-selection ...`
2. 暂不优先继续扩更多 route selector 变体。
3. 若继续推进流程层集成，更值得把 selector 结果接到联合比较或复盘入口。

### 文档补充
- `docs/81_round1_1_route_selector_init_experiment_integration_report.md`
  - `init-experiment` 消费 selector 产物的正式集成，以及 smoke 验证结果。
## 2026-03-15 `round1.1 / final comparison with route context` 更新
### 当前进度补充
158. 已完成: 新增 `compare-offline-mvp-final-experiments` 正式命令，支持在多实验 final comparison 中消费 `--route-selection`，并标出当前 route anchor。
159. 已完成: 对 `D22 / D26 / D29` + `default_minimax` route 做实跑 comparison，产出 `reports/eval/offline_mvp_final_comparison_round1_1_d22_d26_d29_default_minimax/`。

### 当前阶段结论补充
- final comparison 现在已经不只是“按 validation 排序”。
- 在带 route context 的情况下，可以直接读出:
  - `D29` 相对当前 route anchor `D22` 的 validation gain
  - 以及它在 special / `e_evt` / `z_art` 上付出的代价
- 同样也能直接读出:
  - `D26` 相对 `D22` 的 validation 代价
  - 以及它换来的 special / `z_art` 收益

先说人话:
- 到这一步，三锚链已经从“怎么选”进一步变成“选完以后怎么比”。

### 更新后的下一阶段任务
1. 后续若做 final comparison，默认优先带 `--route-selection`。
2. 若继续推进流程层集成，更值得把 route-context comparison 接进后续实验复盘或阶段汇总。
3. 暂不优先继续扩新的 comparison 命令家族。

### 文档补充
- `docs/82_round1_1_final_comparison_route_context_report.md`
  - route-context final comparison 的正式命令、三锚实跑验证，以及相对 route anchor 的 delta 读取方式。
## 2026-03-15 `round1.1 / route-aware recap entrypoint` 更新
### 当前进度补充
160. 已完成: 新增 `recap-offline-mvp-route-context` 正式命令，支持基于 `--route-selection` 直接生成 route-aware recap。
161. 已完成: 对 `D22 / D26 / D29` + `default_minimax` route 做实跑验证，产出 `reports/eval/offline_mvp_route_recap_round1_1_d22_d26_d29_default_minimax/`。

### 当前阶段结论补充
- route recap 现在已经能直接输出:
  - 当前 route anchor
  - best validation alternative
  - best special alternative
  - 可直接复用的 `summary_line`
  - 可直接复用的 `tradeoff_line`
- 这意味着:
  - 后续实验复盘或阶段汇总不必再手工重写三锚 tradeoff 说明
  - 可以直接消费 route-aware recap

先说人话:
- 到这一步，三锚流程已经不只是“能选、能比”，还已经“能总结”。

### 更新后的下一阶段任务
1. 后续若做实验复盘或阶段总结，默认优先用 route recap。
2. 若继续推进流程层集成，更值得把 recap 接进 handoff 或阶段汇总流程。
3. 暂不优先继续扩新的三锚 recap 变体。

### 文档补充
- `docs/83_round1_1_route_recap_report.md`
  - route-aware recap 入口、三锚实跑验证，以及 summary/tradeoff 复用方式。
## 2026-03-15 `round1.1 / route-aware handoff entrypoint` 更新
### 当前进度补充
162. 已完成: 新增 `build-offline-mvp-route-handoff` 正式命令，支持基于 `--route-selection` 直接生成 copy-ready handoff。
163. 已完成: 对 `D22 / D26 / D29` + `default_minimax` route 做实跑验证，产出 `reports/eval/offline_mvp_route_handoff_round1_1_d22_d26_d29_default_minimax/`。

### 当前阶段结论补充
- handoff 现在已经能直接输出:
  - 当前 route / active anchor
  - validation alternative 与 special alternative 的核心取舍
  - 当前 route 下如何继续引用默认 anchor
- 这意味着:
  - 后续接班不必再手工拼接 selector、comparison、recap 三份产物
  - 可以直接用 handoff 输出

先说人话:
- 到这一步，三锚流程已经不仅能“分析、选、比、总结”，还已经能“正式交接”。

### 更新后的下一阶段任务
1. 后续若做接班或阶段交接，默认优先用 route-aware handoff。
2. 若继续推进流程层集成，更值得把 handoff 接进固定交接文档流程。
3. 暂不优先继续扩新的 handoff 变体。

### 文档补充
- `docs/84_round1_1_route_handoff_report.md`
  - route-aware handoff 入口、三锚实跑验证，以及 copy-ready handoff 用法。
## 2026-03-15 `round1.1 / route handoff -> fixed handoff document integration` 更新
### 当前进度补充
164. 已完成: 新增 `materialize-offline-mvp-route-handoff-doc` 正式命令，支持把 `route_handoff.json` 物化成固定格式的正式交接文档。
165. 已完成: 新增模板 `reports/templates/offline_mvp_handoff_document_template.md`，并基于现有 `D22 / D26 / D29` `default_minimax` handoff 产物完成 smoke 验证，产出 `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_default_minimax/`。

### 当前阶段结论补充
- handoff 现在不再只是“一份可复制摘要”。
- 它已经能接进固定格式的交接文档流程，稳定落盘:
  - route 前提
  - 当前 anchor
  - alternatives
  - artifact bundle
  - next-step guidance
- 这意味着:
  - 正式接班入口不必再直接引用原始 `route_handoff.md`
  - 也不需要手工从 json 里二次整理成一份交接文档

先说人话:
- 到这一步，三锚流程已经从“能交接”进一步变成“能按固定格式交接”。

### 更新后的下一阶段任务
1. 后续若做正式接班或阶段交接，默认使用:
   - `build-offline-mvp-route-handoff`
   - `materialize-offline-mvp-route-handoff-doc`
2. 若继续推进流程层集成，更值得把该固定交接文档直接纳入固定周报或阶段报告入口。
3. 暂不优先扩更多 handoff 文档变体。

### 文档补充
- `docs/85_round1_1_route_handoff_document_integration_report.md`
  - route_handoff 接入固定格式交接文档流程的命令、模板和 smoke 验证结果。
## 2026-03-15 `round1.1 / handoff document -> fixed stage report integration` 更新
### 当前进度补充
166. 已完成: 新增 `materialize-offline-mvp-stage-report` 正式命令，支持把 `handoff_document.json` 物化成固定格式的阶段汇总文档。
167. 已完成: 新增模板 `reports/templates/offline_mvp_stage_report_template.md`，并基于现有 `default_minimax` handoff document 完成 smoke 验证，产出 `reports/stage_reports/offline_mvp_stage_report_round1_1_default_minimax/`。

### 当前阶段结论补充
- 当前流程已经不只是“能交接”，也不只是“能产固定交接文档”。
- 它已经能继续往上游汇总成固定格式的阶段状态报告，稳定落盘:
  - executive status
  - current anchor
  - validation / special primary tradeoff
  - carry-forward handoff
  - next-step guidance
- 这意味着:
  - 后续阶段总结不必再手工从交接文档里提炼一层状态摘要
  - 固定周报/阶段报告现在已经有可复用入口

先说人话:
- 到这一步，三锚流程已经从“能交接”进一步变成“能出标准阶段汇总件”。

### 更新后的下一阶段任务
1. 后续若做阶段总结，默认使用:
   - `materialize-offline-mvp-route-handoff-doc`
   - `materialize-offline-mvp-stage-report`
2. 若继续推进流程层集成，更值得把 stage report 直接接进固定周报或里程碑汇总入口。
3. 暂不优先扩更多 stage report 变体。

### 文档补充
- `docs/86_round1_1_stage_report_integration_report.md`
  - handoff document 接入固定 stage report 流程的命令、模板和 smoke 验证结果。
## 2026-03-15 `round1.1 / D31 / teacher-consistency acoustic target-shape probe` 更新
### 当前进度补充
168. 已完成: 在 `teacher_consistency` 中新增 `acoustic_weight` 与 `loss_teacher_acoustic_consistency` 指标透传，支持把 distillation target shape 从 `event + z_art` 扩成 `event + z_art + acoustic`。
169. 已完成: 新增配置 `configs/offline_mvp_train_d31_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_acoustic_smallscale_30_seeded_shuffle.json`，并按 `default_minimax` route 初始化正式实验 `EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration`。
170. 已完成: 跑通 `D31` 的 dry-run、正式 `30 step` 训练、final ablation、final special_eval、checkpoint_series 与 special_eval_series。
171. 已完成: 产出 `D22 / D26 / D29 / D31` 的 route-context final comparison，确认 `D31` 相对当前 minimax anchor `D22` 只形成数值级轻微波动，没有改写 route 结论。

### 当前阶段结论补充
- `acoustic` distillation 不是挂空配置:
  - `step1 loss_teacher_acoustic_consistency = 0.019613`
  - `step30 loss_teacher_acoustic_consistency = 0.108633`
- `D31 final = 2.442793 / 0.142472 / 3.298481 / 0.436225`
- 相对 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation 略好 `-0.001401`
  - final special 略差 `+0.002471`
  - `e_evt` 略弱 `-0.000554`
  - `z_art` 略弱 `-0.002711`

这说明:
- `D31` 不是坏实验；
- 但它也没有把 `default_minimax` 路线推到一个新的 Pareto 点；
- 更接近事实的描述是:
  - 在 `challenge_proxy_core` 这条 gate 上追加温和 acoustic consistency，
  - 只把 `D22` 复刻成了一个近似数值副本。

checkpoint / special series 也没有给出“只是 final 选坏了”的借口:
- `step10 = 2.593177 / 0.136837`
- `step20 = 2.472389 / 0.172539`
- `step30 = 2.442793 / 0.142472`

先说人话:
- 这轮说明“换一种更不同的监督形状”这个方向没错，
- 但“只在同一条 core gate 上多蒸一个 acoustic 头”这一下，还不够成为新杠杆。

### 更新后的下一阶段任务
1. `D22` 继续保持 `default_minimax` / minimax anchor。
2. `D31` 不升为新 anchor，也不优先继续做同构 `acoustic_weight` 小 sweep。
3. 若继续推进 target-shape 路线，更值得试:
   - 更有结构差异的 distillation target shape
   - 而不是继续在同一 `challenge_proxy_core` gate 上做轻量 acoustic 加项微调

### 文档补充
- `docs/87_round1_1_d31_teacher_consistency_acoustic_target_shape_report.md`
  - `D31` 的代码改动、正式实验链路、关键结果，以及为何它没有改写当前 minimax route。
## 2026-03-15 `round1.1 / D32 / teacher-consistency fused-hidden target-shape probe` 更新
### 当前进度补充
172. 已完成: 在 `teacher_consistency` 中新增 `fused_hidden_weight` 与 `loss_teacher_fused_hidden_consistency` 指标透传，支持把 distillation target shape 从 `event + z_art` 扩成 `event + z_art + fused_hidden`。
173. 已完成: 新增配置 `configs/offline_mvp_train_d32_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_fused_hidden_smallscale_30_seeded_shuffle.json`，并按 `default_minimax` route 初始化正式实验 `EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration`。
174. 已完成: 跑通 `D32` 的 dry-run、正式 `30 step` 训练、final ablation、final special_eval、checkpoint_series 与 special_eval_series；同时确认先前评估失败只是并行触发过早，不是 checkpoint 缺失。
175. 已完成: 产出 `D22 / D26 / D29 / D31 / D32` 的 route-context final comparison，确认 `D32` 虽然拿到当前 `zero_e_evt` leader，但仍未改写 `D22` 的 minimax 结论。

### 当前阶段结论补充
- fused-hidden consistency 不是挂空配置:
  - `step1 loss_teacher_fused_hidden_consistency = 0.104925`
  - `step30 loss_teacher_fused_hidden_consistency = 1.811542`
- `D32 final = 2.442393 / 0.143828 / 3.299576 / 0.434057`
- 相对 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation 略好 `-0.001801`
  - final special 略差 `+0.003827`
  - `e_evt` 略强 `+0.000541`
  - `z_art` 略弱 `-0.004879`

这说明:
- `D32` 比 `D31` 更有独立价值，
- 它不是简单数值复刻，
- 而是真正把 control-side gain 推到了一个新的局部点:
  - validation 仍稳
  - `e_evt` 还略升
- 但它仍没有把 special gap 一起补回来，
  因此还不足以改写当前 minimax anchor。

checkpoint / special series 也没有给出“只是 final 选坏了”的借口:
- `step10 = 2.592867 / 0.137444`
- `step20 = 2.473411 / 0.171443`
- `step30 = 2.442393 / 0.143828`

先说人话:
- fused-hidden 这条 target shape 比 `acoustic` 加项更像真杠杆，
- 但它在当前 core gate 上只把 `e_evt` 顶上去了，
- 还没把 special 一起带过线。

### 更新后的下一阶段任务
1. `D22` 继续保持 `default_minimax` / minimax anchor。
2. `D32` 保留为 fused-hidden target-shape reference，但不升为新 anchor。
3. 若继续推进 fused-hidden 路线，更值得试:
   - `D32` 的 target shape
   - 与 `D26` 已验证有效的 short-pause gate / sampler 组合
4. 暂不优先继续做:
   - 当前 core gate 下的 fused_hidden 权重小 sweep

### 文档补充
- `docs/88_round1_1_d32_teacher_consistency_fused_hidden_target_shape_report.md`
  - `D32` 的代码改动、正式实验链路、关键结果，以及为何它成为新的 control-side reference、但仍没有改写当前 minimax route。
## 2026-03-15 `round1.1 / D33 / short-pause fused-hidden anchor reset` 更新
### 当前进度补充
176. 已完成: 新增配置 `configs/offline_mvp_train_d33_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_fused_hidden_20step_smallscale_seeded_shuffle.json`，把 `D32` 的 fused-hidden target shape 与 `D26` 的 short-pause gate / sampler 组合。
177. 已完成: 按 `default_minimax` route 初始化正式实验 `EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration`，并跑通 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series 与 special_eval_series。
178. 已完成: 产出 `D22 / D26 / D29 / D31 / D32 / D33` 的 route-context final comparison，确认 `D33` 已拿到当前 `special / zero_e_evt / zero_z_art` 三项 leader。
179. 已完成: 基于 `D22 / D29 / D33` 重跑正式三锚资产:
   - `analyze-offline-mvp-anchor-selection`
   - `analyze-offline-mvp-anchor-routes`
   - `select-offline-mvp-anchor-route`
   确认 `D33` 正式替换 `D26` 成为新的 special-first anchor，而 `D22` 仍保持 minimax。
180. 已完成: 基于新 trio 重新物化默认交接链:
   - `route_handoff`
   - `handoff_document`
   - `stage_report`

### 当前阶段结论补充
- `D33 final = 2.52818 / 0.111677 / 3.312339 / 0.465828`
- 相对 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`:
  - validation 仅略差 `+0.004282`
  - final special 更好 `-0.006217`
  - `e_evt` 更强 `+0.039689`
  - `z_art` 更强 `+0.005569`
- 相对 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation `+0.083986`
  - special `-0.028324`
  - `e_evt +0.013304`
  - `z_art +0.026892`

这说明:
- `D33` 没有改写 minimax；
- 但它已经明确改写了 special-side anchor 格局；
- 当前正式三锚结构应更新为:
  - `D29 = validation`
  - `D22 = default_minimax`
  - `D33 = special / e_evt / z_art`

`D33 step10` 也给了更极端的 special-only 点:
- `step10 = 2.621019 / 0.081505`
- 但 `step20 = 2.52818 / 0.111677 / 3.312339 / 0.465828`
  才是这轮更稳定的 special/control joint anchor

先说人话:
- `D32` 单独看时，像是“快摸到 special 了但还差一点”；
- `D33` 说明缺的确实不是 fused-hidden 本身，
- 而是 fused-hidden 需要放进对的 gate / sampler 结构里。
- 一旦放对了，`D26` 这一侧的旧锚点就被整体升级掉了。

### 更新后的下一阶段任务
1. `D22` 继续保持 `default_minimax` anchor。
2. `D33` 正式替换 `D26`，成为新的 `special / e_evt / z_art` anchor。
3. 后续默认交接、route selector、阶段汇总统一切到 `D22 / D29 / D33` 新 trio。
4. 若继续推进训练主线，更值得试:
   - 以 `D22` 和 `D33` 为两端的新 minimax / cross-anchor 组合
   - 而不是继续围绕旧的 `D26` family 做 follow-up

### 文档补充
- `docs/89_round1_1_d33_shortpause_fused_hidden_anchor_reset_report.md`
  - `D33` 的正式实验链路、关键结果，以及为何它已经替换 `D26` 成为新的 special/control anchor，并触发三锚与 handoff 资产更新。
## 2026-03-15 `round1.1 / D34+D35 / new-trio cross-anchor follow-up` 更新
### 当前进度补充
181. 已完成: 新增 `D34 = D22 init + D33 teacher` 与 `D35 = D33 init + D22 teacher` 两条新 trio cross-anchor 配置，统一保留 `fused_hidden_weight = 0.05`。
182. 已完成: 初始化并实跑正式实验:
   - `EXP-20260315-051 / D34`
   - `EXP-20260315-052 / D35`
   两条线均完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
183. 已完成: 产出 `D22 / D29 / D33 / D34 / D35` 的 route-context final comparison，确认新 trio 下 naive final-to-final cross-anchor 仍未形成新的 joint winner。

### 当前阶段结论补充
- `D34 final = 2.3506 / 0.201536 / 2.633041 / 0.310002`
  - 是当前 comparison 里的 validation leader
  - 但 special / `e_evt` / `z_art` 全面恶化
  - 形状上几乎复刻旧 `D28` 的 validation compressor
- `D35 final = 2.395609 / 0.173543 / 2.967455 / 0.361794`
  - 基本回到 `D29` 式中间锚点
  - 没有把 `D33` 的 stronger special/control 保下来

这说明:
- `D33` 虽然已经成功升级了 special-side anchor，
- 但把它直接拿来和 `D22` 做 final-to-final 互蒸，
- 仍然只会落回两种旧形状:
  - validation compressor
  - 中间锚点
- 当前仍没有新的 joint final winner

checkpoint / special series 也没有给出“只是 final 选坏了”的借口:
- `D34 step10 = 2.386077 / 0.223716 / 2.562634 / 0.276536`
- `D34 step20 = 2.3506 / 0.201536 / 2.633041 / 0.310002`
- `D35 step10 = 2.433376 / 0.204297 / 2.768766 / 0.337547`
- `D35 step20 = 2.395609 / 0.173543 / 2.967455 / 0.361794`

先说人话:
- special anchor 虽然升级了，
- 但“拿两个 final 参考点互蒸一下”这条招数本身并没有升级。
- 它还是只会把轨迹压向旧的两种已知形状。

### 更新后的下一阶段任务
1. 当前 route 结构保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂不继续优先做同构 `D22 <-> D33 final-to-final` cross-anchor 变体。
3. 若继续推进，更值得试:
   - checkpoint-level cross-anchor
   - 尤其是显式利用 `D33 step10` 这类 special-only checkpoint
   - 而不是继续只拿 final anchor 对 final anchor 互蒸

### 文档补充
- `docs/90_round1_1_d34_d35_new_trio_cross_anchor_report.md`
  - `D34 / D35` 的正式实验链路、关键结果，以及为何新 trio 下 naive cross-anchor 仍然不能自然造出新的 minimax / joint winner。
## 2026-03-15 `round1.1 / D36+D37 / checkpoint-level cross-anchor follow-up` 更新
### 当前进度补充
184. 已完成: 新增 `D36 = D33 step10 init + D22 teacher` 与 `D37 = D22 init + D33 step10 teacher` 两条 checkpoint-level cross-anchor 配置，继续保留 `fused_hidden_weight = 0.05`。
185. 已完成: 初始化并实跑正式实验:
   - `EXP-20260315-053 / D36`
   - `EXP-20260315-054 / D37`
   两条线均完成 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
186. 已完成: 产出 `D22 / D29 / D33 / D36 / D37` 的 route-context final comparison，确认 `D33 step10` 也不能自然打开新的 cross-anchor joint winner。

### 当前阶段结论补充
- `D36 final = 2.450632 / 0.144661 / 3.221708 / 0.407633`
  - 相对 `D22` 四项全弱
  - 只是一个比 `D22` 更差的近邻复制品
- `D37 final = 2.35571 / 0.199699 / 2.652109 / 0.321586`
  - 是当前 comparison 里的 validation leader
  - 但 special / `e_evt` / `z_art` 全面恶化
  - 形状上几乎复刻 `D34` / 旧 `D28` 的 compressor

这说明:
- `D33 step10` 虽然是更极端的 special-only checkpoint，
- 但它不是一个可以通过最小互蒸直接收敛成新中间点的入口。
- checkpoint-level 的最小同构 follow-up 也已经给出负结果。

先说人话:
- 到这一步，`D22 <-> D33` 这条线不只是 final-to-final 不行，
- 连拿 `D33 step10` 当 checkpoint 入口也不行。
- 这条支线里“简单互蒸”能提供的信息已经基本榨干了。

### 更新后的下一阶段任务
1. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做 `D33 step10` 的 checkpoint-level 同构 cross-anchor 变体。
3. 若继续推进，更值得转向:
   - 更结构化的 checkpoint selection / routing
   - 或更强的 target / gate 级重构
   - 而不是继续做 `step10` 与 final 的简单互蒸

### 文档补充
- `docs/91_round1_1_d36_d37_checkpoint_cross_anchor_report.md`
  - `D36 / D37` 的正式实验链路、关键结果，以及为何 `D33 step10` 也不能自然打开新的 checkpoint-level cross-anchor joint winner。
## 2026-03-15 `round1.1 / inference-audio audit and human-review gate` 更新
### 当前进度补充
187. 已完成: 对当前 MVP 是否支持“checkpoint 直接导出推理音频”做正式代码与流程审计。
188. 已确认: 当前系统还不具备推理音频导出能力，原因不是命令缺失，而是整个 `acoustic -> waveform` synthesis / vocoder 链路尚未接入。
189. 已完成: 在 `reports/audio/README.md` 落盘当前审核状态，明确本轮没有可供用户试听的推理音频产物。
190. 已完成: 将“数据突破后必须跑用户人耳试听；用户确认前不得直接升为当前最优解”的 gate 正式写入流程文档。

### 当前阶段结论补充
- 当前 MVP 不能直接导出推理音频。
- 直接证据是:
  - `src/v5vc/offline_mvp/model.py` 只输出 `acoustic` 等中间特征，不输出 waveform
  - `src/v5vc/cli.py` 当前没有 inference / synthesis / export-audio 命令
  - 全部训练配置当前仍是 `vocoder_required = false`
- 因此这轮无法为 `D22 / D29 / D33` 或其它分支直接生成 `reports/audio/` 试听音频。

先说人话:
- 当前系统能比较数据，能选 route，能出交接件，
- 但还不能把模型结果直接变成给人耳听的音频。
- 所以“数据最优”与“听感最优”现在还不是同一件事。

### 更新后的下一阶段任务
1. 在任何新的数据突破之后，必须追加一次人耳试听流程。
2. 最小试听规格固定为:
   - 选择当前数据最好或次好的几个分支
   - 每个分支至少导出 `3` 段不同输入音频
   - 统一落到 `reports/audio/`
3. 在用户明确确认前，禁止把该分支直接升为当前最优解。
4. 若要真正执行该 gate，下一步先补:
   - inference 命令
   - synthesis / vocoder 链路
   - 正式的 `reports/audio/` 导出流程

### 文档补充
- `docs/92_round1_1_inference_audio_audit_and_human_review_gate_report.md`
  - 当前 MVP 的推理音频导出能力审计，以及“人耳试听先于最优解晋升”的正式流程约束。
## 2026-03-15 `round1.1 / proxy-audio export bootstrap` 更新
### 当前进度补充
191. 已完成: 新增 `export-offline-mvp-proxy-audio` 正式命令，支持从 checkpoint 前向得到 `acoustic` 后重建可试听的 proxy waveform。
192. 已完成: 以当前主分支 `D22 / D29 / D33` 为首轮人工审核包，各自导出 `3` 段共享 source 输入的 `input.wav + proxy.wav` 到 `reports/audio/`。

### 当前阶段结论补充
- 当前系统已经不再是“完全不能导出音频”。
- 但当前能导出的仍是:
  - `proxy audio`
  - 不是完整 vocoder / runtime inference waveform
- 当前首轮试听包目录:
  - `reports/audio/offline_mvp_proxy_audit_d22_exp039/`
  - `reports/audio/offline_mvp_proxy_audit_d29_exp045/`
  - `reports/audio/offline_mvp_proxy_audit_d33_exp050/`

当前断点明确为:
- 停止继续做 `step10` 与 `final` 的同构互蒸。
- 下一步优先转向:
  - 更结构化的 checkpoint selection / routing
  - 或更强的 target / gate 级重构
- 当前补出的 proxy-audio 导出链，
  是为了让后续任何数据突破都必须经过一次用户人耳审核，
  而不是继续给简单互蒸支线加预算。

先说人话:
- 现在已经有东西可以听了，
- 但还不能把这些 wav 当成“最终成品音质”。
- 它们的角色是:
  - 给用户做分支间相对审核
  - 不给数据侧 leader 直接开绿灯

### 更新后的下一阶段任务
1. 由用户先试听 `D22 / D29 / D33` 首轮 proxy audio。
2. 在用户确认前，不把任何单个数据 leader 直接升为最终最优解。
3. 后续若继续建设音频链路，再补:
   - 更接近 runtime 的 waveform synthesis
   - inference manifest / batch export
   - 正式 vocoder 接入

### 文档补充
- `docs/93_round1_1_proxy_audio_export_bootstrap_report.md`
  - proxy-audio 导出命令、当前首轮试听包，以及本轮明确写入的“断点”与人工审核使用边界。
## 2026-03-15 `round1.1 / proxy-audio user-audit follow-up and re-synthesis` 更新
### 当前进度补充
193. 已完成: 记录用户对首版 `proxy audio` 的人工试听结论，确认该版本因高频啸叫而基本失去比较价值。
194. 已完成: 重写 `src/v5vc/proxy_audio_export.py` 中的代理重建逻辑，停止把 `zero_cross` 直接映射为可听主频，改为更保守的低频包络代理。
195. 已完成: 基于修正后的重建器，重新导出 `D22 / D29 / D33` 三组试听包，等待用户重新试听确认。

### 当前阶段结论补充
- 首版 `proxy audio` 虽然技术上“能导出 wav”，
  但从人工审核角度看并不合格。
- 用户反馈很明确:
  - 音频基本是高频啸叫
  - 几乎无法比较差异
  - 只能粗听到 `D22 < D29 < D33` 的基准频率排序
  - `D33` 略有不稳定感
- 这说明:
  - 第一版重建器保留的是“刺耳频率差异”，
  - 不是我们真正想审核的结构差异

先说人话:
- 首版试听包不算失败在“没声音”，
- 但算失败在“有声音却没法审”。
- 所以这轮正确动作不是强行解读结果，
- 而是先修导出器，再让用户重新听。

### 更新后的下一阶段任务
1. 由用户重新试听重导后的 `D22 / D29 / D33` bundle。
2. 若新版仍然只能听到刺耳高频，而听不出节奏 / 边界 / 稳定性差异，
   则当前 proxy 路线仍视为不合格。
3. 在用户给出有效听感结论前，
   仍不把任何数据侧 leader 直接升为当前最优解。

### 文档补充
- `docs/94_round1_1_proxy_audio_resynthesis_after_user_audit_report.md`
  - 首轮用户试听反馈、首版失败根因、重建器修正方案，以及重导状态。
## 2026-03-15 `round1.1 / proxy-audio second user audit and depitch` 更新
### 当前进度补充
196. 已完成: 记录第二轮用户试听反馈，确认第二版 `proxy audio` 虽已能让用户听到停顿和音量结构，但仍被分支间音调差异污染。
197. 已完成: 将 `proxy audio` 重建逻辑继续收紧为去音调化结构代理，统一 audible carrier frequency，避免 `D33` 之类通过更高音调主导比较。

### 当前阶段结论补充
- 第二版 `proxy audio` 的进步是:
  - 用户已经能听到:
    - 停顿
    - 音量结构
    - 与原音频的粗对应关系
- 第二版 `proxy audio` 的不足是:
  - `D22 / D29` 的差异仍细微到难以稳定区分
  - `D33` 的更高频率 / 更高音调仍然是主导差异

这说明:
- 当前 proxy 路线开始具备“粗结构校验”能力，
- 但还不具备“稳定 branch ranking”能力。

先说人话:
- 第二版已经不是完全不能听，
- 但它仍然很容易把你带到“谁更高音”这种假问题上。
- 所以这一步该做的不是急着下结论，
- 而是把可听音调再压平，只留下停顿和能量结构。

### 更新后的下一阶段任务
1. 重新导出去音调化后的 `D22 / D29 / D33` bundle。
2. 让用户再试听一轮，重点只看:
   - 停顿
   - 音量结构
   - 边界收束
   - 稳定性
3. 如果在去音调化后 `D22 / D29` 仍基本不可区分，
   则接受当前 proxy 音频只足够做粗结构审核，不足以做细粒度 branch ranking。

### 文档补充
- `docs/95_round1_1_proxy_audio_second_user_audit_and_depitch_report.md`
  - 第二轮用户试听反馈、当前有效与无效信息边界，以及去音调化修正方向。
## 2026-03-15 `round1.1 / proxy-audio third user audit boundary` 更新
### 当前进度补充
198. 已完成: 记录第三轮用户试听结论，确认三分支音调已对齐。
199. 已完成: 明确当前 proxy 路线下，`D22 / D29` 几乎不可稳定区分，而 `D33` 表现出更明显不稳定性。
200. 已完成: 收口当前人工审核能力边界，确认 proxy audio 只足够做粗结构审核与稳定性异常排查。

### 当前阶段结论补充
- 当前可保留的听感结论是:
  - `D22 / D29` 基本打平
  - 若硬要分，`D29` 相对 `D22` 只体现为非常轻微的“更柔和”
  - `D33` 明显更不稳定
- 当前不能保留的结论是:
  - `D33` 因此一定更差
  - `D33` 因此一定更真实
  - `D22` 或 `D29` 在真实 runtime 音频里一定没有差异

这说明:
- proxy 路线已经完成了它最核心的 gate 任务:
  - 不让数据 leader 自动越过人工审核
  - 发现明显异常分支
- 但它还没有达到:
  - 细粒度 branch ranking
  - 原音频真实性判定
 这两个层级

先说人话:
- 现在这条链路已经够用来挡风险，
- 但还不够用来定冠军。
- `D33` 的“不稳”值得记，
- 但现在还不能把它翻译成“淘汰”或“更真实”。

### 更新后的下一阶段任务
1. 当前人工审核口径先固定为:
   - `D22 / D29` 听感上基本打平
   - `D33` 更不稳
2. 在没有更接近 runtime 的 waveform 链路前，
   不继续尝试用 proxy audio 做细粒度 `D22 / D29` 判优。
3. 若下一步继续建设音频链路，
   优先目标应改为:
   - 更接近真实结构的 synthesis
   - 或正式 vocoder 接入
   而不是继续微调当前 proxy 重建器。

### 文档补充
- `docs/96_round1_1_proxy_audio_third_user_audit_boundary_report.md`
  - 第三轮用户试听结论，以及当前 proxy-audio 路线的正式能力边界。
## 2026-03-15 `round1.1 / D38+D39+D40 / phase-handoff routing follow-up` 更新
### 当前进度补充
201. 已完成: 新增并实跑 `D38 = early short_pause -> late core`，把 `D33` family 的 broad sampler 只保留到前 `10` step，后 `10` step 明确 handoff 回 `core`。
202. 已完成: 新增并实跑 `D39 = early core -> late short_pause`，验证 late short-pause tail 能否把 core-only family 重新拉回 `D33` 家族。
203. 已完成: 新增并实跑 `D40 = D38 + teacher_off_after_step10`，验证 `D38` 的退化是否主要由 late teacher pull 持续造成。
204. 已完成: 为 `D38 / D39 / D40` 全部补齐 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series，并产出与 `D22 / D29 / D33` 的 route-context final comparison。

### 当前阶段结论补充
- `D38 step10` 精确复刻 `D33 step10`:
  - `2.621019 / 0.081505 / 3.224344 / 0.46347`
  - 说明 early short-pause routing 确实真实接上了 special checkpoint
- 但 `D38 final = 2.494434 / 0.161978 / 3.096622 / 0.436892`
  - 最终只回到一个比 `D22` 更差的中间点
- `D39 final = 2.489906 / 0.169107 / 3.048095 / 0.407912`
  - 说明 late short-pause tail 也不能把早期 core-only 轨迹自然补回 `D33`
- `D40 final = 2.492335 / 0.160804 / 3.102396 / 0.431034`
  - 与 `D38` 几乎同型
  - 说明把 teacher 在 `step10` 后完全关掉，也不能把 `D33 step10` 稳定收敛成新的 minimax

这说明:
- phase-handoff routing 这条线已经给出相当清楚的负结果:
  - 仅靠 sampler handoff
  - 或 sampler handoff + teacher off
 还不足以在 `D22 / D33` 之间造出新的 joint winner。

先说人话:
- 这条线不是“没接上”，
- 而是“接上了，但只是在重放已知形状，然后再退回中间点”。
- `D33 step10` 这个 special-only 点确实能被 phase routing 复刻，
- 但当前没有任何一种最小 handoff 能把它顺利落到新的终点。

### 更新后的下一阶段任务
1. 暂停继续做同 family 的 sampler-handoff / teacher-off 小变体。
2. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
3. 若继续推进，更值得转向:
   - 更强的 target / gate 级重构
   - 或更明确的 phase-specific teacher target/gate 机制
   - 而不是继续只改 sampler 顺序

### 文档补充
- `docs/97_round1_1_d38_d39_d40_phase_handoff_routing_report.md`
  - `D38 / D39 / D40` 的正式实验链路，以及为何 phase-handoff routing 不能自然造出新的 final joint winner。
## 2026-03-15 `round1.1 / post-D40 fixed handoff assets refresh` 更新
### 当前进度补充
205. 已完成: 基于 `D22 / D29 / D33 / D38 / D39 / D40` 重建最新 `route-aware handoff`，产出 `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`。
206. 已完成: 将上述 handoff 物化为固定格式正式交接件，产出 `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`。
207. 已完成: 将正式交接件继续物化为固定格式阶段报告，产出 `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`。

### 当前阶段结论补充
- 固定格式接班入口现已刷新到 `D40` 之后的最新状态:
  - route anchor 仍是 `D22`
  - validation alternative 仍是 `D29`
  - special / `e_evt` / `z_art` alternative 仍是 `D33`
- `D38 / D39 / D40` 已被纳入最新 handoff / stage-report 的 source artifacts:
  - 说明当前固定交接件不再只覆盖“三锚结论”
  - 也覆盖了最近这轮 phase-handoff routing 的负结果封口

这说明:
- 现在接班不需要同时翻:
  - route selector
  - final comparison
  - `docs/97`
  才能确认“最新阶段已经收口到哪里”
- 直接从固定 handoff / stage-report 入口，
  就能拿到:
  - 当前默认 anchor
  - 主 tradeoff
  - 以及最新纳入比较的实验集合

先说人话:
- 这一步不是在继续开新实验，
- 而是在把“最新结论的入口”补齐。
- 下次如果上下文再断，
- 先看新的固定交接件就能知道:
  - 目前默认该引用谁
  - 以及 `D38-D40` 已经做过，且没有改写格局。

### 更新后的下一阶段任务
1. 当前正式接班入口优先改用:
   - `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`
   - `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`
2. 若继续推进实验，不再优先补 handoff 同 family 小变体；
   优先准备更强的 target / gate 级重构方案选项。
3. 在给用户报下一轮方案前，默认同时引用:
   - 最新固定 stage report
   - `docs/97_round1_1_d38_d39_d40_phase_handoff_routing_report.md`

### 文档补充
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`
  - `D22 / D29 / D33 / D38 / D39 / D40` 最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`
  - `D40` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_default_minimax/`
  - `D40` 之后的固定格式阶段报告。
## 2026-03-15 `round1.1 / D41 / phase-specific teacher gate-target handoff` 更新
### 当前进度补充
208. 已完成: 在 `src/v5vc/train_entry.py` 中为 `teacher_consistency` 新增 `schedule_phases`，支持按 phase 切换 `pool_memberships` 与 target-shape 权重。
209. 已完成: 新增配置 `configs/offline_mvp_train_d41_round1_1_d7_init_d10_teacher_consistency_phase_teacher_gate_target_handoff_fused_hidden_20step_smallscale_seeded_shuffle.json`，并初始化正式实验 `EXP-20260315-058-offline-mvp-d41-round1-1-d7-init-d10-teacher-consistency-phase-teacher-gate-target-handoff-fused-hidden-20step-calibration`。
210. 已完成: 跑通 `D41` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series，以及与 `D22 / D29 / D33 / D38 / D39 / D40` 的 route-context final comparison。
211. 已完成: 基于包含 `D41` 的最新实验集合，重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D41 step10` 仍精确复刻 `D33 step10`:
  - `2.621019 / 0.081505 / 3.224344 / 0.46347`
- 同时 `step11` 日志已明确显示:
  - `teacher gate` 从 `challenge_proxy_core + short_pause_no_terminal`
  - 切到 `challenge_proxy_core`
  - `fused_hidden_weight` 从 `0.05`
  - 切到 `0.0`
- 但 `D41 final = 2.493233 / 0.163597 / 3.088342 / 0.435649`
  - 仍只回到和 `D38 / D40` 同型的中间点

这说明:
- 现在不是“phase-specific teacher 还没试到位”
- 而是:
  - 即使 teacher 自身的 gate 与 target shape 已明确切相，
  - 同一条 `D10 teacher` family 仍不足以把 `D33 step10` 固化成新的 final winner

先说人话:
- 这轮比 `D38-D40` 更狠一点，
- 因为它不是简单把 teacher 关掉，
- 而是让 teacher 自己在中途换工作方式。
- 但结果还是没翻盘，
- 所以同一 teacher 家族下继续抠 phase 排布，价值已经明显下降了。

### 更新后的下一阶段任务
1. 暂停继续做同一 `D10 teacher` 下的 phase-specific gate / target-shape 小变体。
2. 若继续走 teacher 路线，更值得转向:
   - phase-specific teacher checkpoint / teacher source
   - 而不是继续只改同一 teacher 的 mask、weight 和 fused-hidden 开关。
3. 或直接回到更强的 target-side supervision / gate 级重构。

### 文档补充
- `docs/98_round1_1_d41_phase_teacher_gate_target_handoff_run_report.md`
  - `D41` 的正式实验链路，以及为何更明确的 phase-specific teacher gate-target handoff 仍未形成新终点。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_default_minimax/`
  - 包含 `D41` 的最新 route-context final comparison。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_default_minimax/`
  - `D41` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_default_minimax/`
  - `D41` 之后的固定格式阶段报告。
## 2026-03-15 `round1.1 / D42-D43 / phase-specific teacher source + high-proximity relaxed gate` 更新
### 当前进度补充
212. 已完成: 在 `src/v5vc/train_entry.py` 中继续扩展 `teacher_consistency.schedule_phases`，支持按 phase 切换 `teacher_checkpoint_path`，并同步落盘 `teacher_checkpoint_paths` 与 phase-specific target gate 过滤器。
213. 已完成: 在 `src/v5vc/offline_mvp/data.py` 与 `src/v5vc/offline_mvp/losses.py` 中扩展 target-side gate 过滤能力，支持 `min/max_special_proximity_score`、`required_final_terminal_types` 与 `required_utterance_structure_types`。
214. 已完成: 新增配置 `configs/offline_mvp_train_d42_round1_1_d7_init_phase_teacher_source_handoff_d33step10_to_d22_fused_hidden_20step_smallscale_seeded_shuffle.json`，并跑通 `D42` dry-run 与正式实验 `EXP-20260315-059-offline-mvp-d42-round1-1-d7-init-phase-teacher-source-handoff-d33step10-to-d22-fused-hidden-20step-calibration` 的完整评估链。
215. 已完成: 新增配置 `configs/offline_mvp_train_d43_round1_1_d7_init_d10_teacher_consistency_highproximity_relaxed_gate_fused_hidden_20step_smallscale_seeded_shuffle.json`，并跑通 `D43` dry-run 与正式实验 `EXP-20260315-060-offline-mvp-d43-round1-1-d7-init-d10-teacher-consistency-highproximity-relaxed-gate-fused-hidden-20step-calibration` 的完整评估链。
216. 已完成: 产出包含 `D42 / D43` 的最新 route-context final comparison，目录为 `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_default_minimax/`。
217. 已完成: 基于包含 `D42 / D43` 的最新实验集合，重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D42` 的最小 phase-specific teacher source handoff 已真实接上:
  - `step1-10 = D33 step10 teacher + broad gate + fused_hidden`
  - `step11-20 = D22 final teacher + core-only + no fused_hidden`
- 但 `D42 final = 2.488031 / 0.15944 / 3.115116 / 0.417186`
  - 仍只是比 `D38-D41` 略靠近 `D22` 的中间点
  - 没有改写 route
- `D43` 的 high-proximity relaxed gate 也真实生效:
  - `challenge_proxy_relaxed + min_special_proximity_score >= 0.8`
  - `priority_record_count = 24`
- 但 `D43 final = 2.46381 / 0.200946 / 2.927122 / 0.374309`
  - 主要只是把形状推向 validation / `e_evt` 折中
  - special 明显退化
  - 同样没有改写 route

这说明:
- `D42` 和 `D43` 已经把上轮提出的两个“最小后续方向”都做完了，
- 且两条线都给出了负结果:
  - 最小 teacher-source handoff 不够
  - 最小 high-proximity target gate 也不够

先说人话:
- 这一步不是又补了两个“可能还差一点点”的小变体，
- 而是把 `D41` 后面最自然的两条最小 follow-up 都正式封口了。
- 从现在开始，
- 如果还继续推进，
- 就不该再默认“小改一下 source / gate 阈值”会自然翻盘。

### 更新后的下一阶段任务
1. 暂停继续做:
   - 最小 phase-specific teacher source 小变体
   - 最小 high-proximity relaxed gate 小变体
2. 若继续走 teacher 路线，优先考虑:
   - 更强的 phase-specific teacher family / checkpoint 组合
   - 或 teacher source 与 phase filter 的联动重构
3. 若继续走 target-side 路线，优先考虑:
   - 更强的 structure / terminal 显式 gating
   - 或独立的 special-target supervision 重构
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/99_round1_1_d42_d43_phase_teacher_source_and_highproximity_gate_report.md`
  - `D42 / D43` 的正式实验链路，以及为何这两个最小 follow-up 都未改写当前 route。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_default_minimax/`
  - 包含 `D42 / D43` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_default_minimax/`
  - `D43` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_default_minimax/`
  - `D43` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_default_minimax/`
  - `D43` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D44-D45 / structural gate + teacher-family handoff` 更新
### 当前进度补充
218. 已完成: 新增配置 `configs/offline_mvp_train_d44_round1_1_d7_init_d10_teacher_consistency_relaxed_none_other_gate_fused_hidden_20step_smallscale_seeded_shuffle.json`，在 `D43` 基础上加入 `required_final_terminal_types=["none"] + required_utterance_structure_types=["other"]` 的更硬 relaxed gate。
219. 已完成: 新增配置 `configs/offline_mvp_train_d45_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29_shortpause_20step_smallscale_seeded_shuffle.json`，把 phase-specific teacher source 从 `D33 step10 -> D22 final` 改为 `D33 step10 -> D29 final`。
220. 已完成: 跑通 `D44 / D45` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series，以及包含这两条线的 latest final comparison。
221. 已完成: 基于包含 `D44 / D45` 的最新实验集合，重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D44` dry-run 已确认:
  - `challenge_proxy_relaxed + min_special_proximity_score >= 0.8`
  - 再叠 `required_final_terminal_types=["none"]`
  - 与 `required_utterance_structure_types=["other"]`
  - 得到 `priority_record_count = 19`
- `D44 final = 2.504646 / 0.14823 / 3.100172 / 0.422595`
  - 相比 `D43`
    - special / `e_evt` / `z_art` 明显修复
  - 但相比 `D22`
    - 仍是四项里全面更弱的 dominated 点
- `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
  - 相比 `D22`
    - special 略好 `-0.006285`
    - 但 validation / `e_evt` / `z_art` 都更差
  - 相比 `D33`
    - validation 更好
    - 但 special / control 都更弱
  - 因而它是一个新的 non-dominated compromise 点
  - 但仍不足以改写 default route

这说明:
- `D44` 已经把 `D43` 的退化来源基本钉在:
  - relaxed gate 中混入的 `terminal_* / single_clause_terminal` 样本
- `D45` 则说明:
  - phase-specific teacher family 方向比 `D42` 更有价值
  - 但当前仍需要更强的 late gate / filter 联动，才可能真正冲击 route

先说人话:
- `D44` 是“定位问题”的实验，不是“解决问题”的实验。
- `D45` 才是这轮真正有后续价值的点:
  - 它没有翻盘，
  - 但它第一次在 `post-D41` 路线里给出了一个像样的新 tradeoff，
  - 而不是单纯回放旧盆地。

### 更新后的下一阶段任务
1. 暂停继续做 relaxed gate 只加 / 只减筛样条件的小变体。
2. 若继续走 target-side 路线，优先考虑:
   - 更明确的 `none / nonverbal` 目标监督
   - 而不是继续在 `relaxed` pool 上轻量调阈值
3. 若继续走 teacher 路线，优先沿 `D45` 方向继续增强:
   - phase-specific teacher family + phase-specific filter 联动
   - 或 late teacher family 的更强 gate 约束
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/100_round1_1_d44_d45_structural_gate_and_teacher_family_report.md`
  - `D44 / D45` 的正式实验链路，以及为何 `D44` 只是定位性负结果，而 `D45` 虽形成新 tradeoff 但仍未改写 route。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_default_minimax/`
  - 包含 `D44 / D45` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_default_minimax/`
  - `D45` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_default_minimax/`
  - `D45` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_default_minimax/`
  - `D45` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D46-D47 / teacher-family late filter linkage` 更新
### 当前进度补充
222. 已完成: 新增配置 `configs/offline_mvp_train_d46_round1_1_d7_init_phase_teacher_family_filter_handoff_d33step10_to_d29_relaxed_none_other_20step_smallscale_seeded_shuffle.json`，在 `D45` 基础上把 late phase 的 teacher / sampler gate 联动切到 `challenge_proxy_relaxed + none/other + proximity>=0.8`。
223. 已完成: 新增配置 `configs/offline_mvp_train_d47_round1_1_d7_init_phase_teacher_family_filter_handoff_d33step10_to_d29_relaxed_none_other_hi84_20step_smallscale_seeded_shuffle.json`，进一步把 late phase proximity 阈值抬到 `0.84`。
224. 已完成: 跑通 `D46 / D47` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series，以及包含这两条线的 latest final comparison。

### 当前阶段结论补充
- `D46 step10` 与 `D45 step10` 完全一致:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D46 final = 2.484944 / 0.158502 / 3.091893 / 0.392083`
  - 相比 `D45`
    - validation 更低
    - 但 special / `e_evt` / `z_art` 都更差
- `D47 final = 2.480151 / 0.170562 / 3.014662 / 0.378469`
  - 相比 `D46`
    - validation 再低一点
    - 但 special / `e_evt` / `z_art` 再差一点

这说明:
- 在 `D45` 这条 teacher-family 路线里，
- 把 late filter 继续向 `relaxed none-other` 收紧，
- 只是在沿同一前沿往 validation 方向滑，
- 并没有产生比 `D45` 更强的 special-compromise。

先说人话:
- `D46 / D47` 不是没价值，
- 它们把 `D45` 这条线的局部前沿形状补清楚了。
- 但现在已经足够确认:
- 继续只缩 late sample set，
- 不会把 `D45` 推成新的 route。

### 更新后的下一阶段任务
1. 暂停继续做 `D45` 上的 late filter 阈值 / 筛样硬化小变体。
2. 若继续沿 `D45` 路线推进，优先考虑:
   - late teacher family 的更强 target-shape 联动
   - 或单独给 formal special 对齐的监督信号
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/101_round1_1_d46_d47_teacher_family_filter_linkage_report.md`
  - `D46 / D47` 的正式实验链路，以及为何 late filter linkage 继续加硬只会削弱 `D45` 的 compromise 价值。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_default_minimax/`
  - 包含 `D46 / D47` 的最新 route-context final comparison。
## 2026-03-16 `round1.1 / D48-D49 / late target-shape softweight + punctuation supervision` 更新
### 当前进度补充
225. 已完成: 在 `src/v5vc/offline_mvp/losses.py` 中新增 `build_special_supervision_sample_weights`，并在 `src/v5vc/train_entry.py` 中把 `teacher_consistency` 扩展为支持 `base_sample_weight / proximity_weight_scale / terminal/structure weight overrides`。
226. 已完成: 为 `punctuation_profile_aux` 接入 `weight_schedule`，并新增配置 `configs/offline_mvp_train_d48_round1_1_d7_init_phase_teacher_family_softweight_handoff_d33step10_to_d29_late_targetshape_20step_smallscale_seeded_shuffle.json` 与 `configs/offline_mvp_train_d49_round1_1_d7_init_phase_teacher_family_punctuation_aux_handoff_d33step10_to_d29_late_only_20step_smallscale_seeded_shuffle.json`。
227. 已完成: 跑通 `D48 / D49` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
228. 已完成: 产出包含 `D48 / D49` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D48` 的 late teacher softweight 已真实生效:
  - `step11-20 effective_teacher_consistency`
    - `base_sample_weight = 0.35`
    - `proximity_weight_scale = 1.0`
    - `final_terminal_type_weight_overrides = {"none": 0.2}`
    - `utterance_structure_type_weight_overrides = {"other": 0.15, "nonverbal": 0.15}`
- 但 `D48 step10 / final` 都与 `D45` 精确重合:
  - `step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
  - `final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
- `D49` 的 late-only `punctuation_profile_aux` 也已真实激活:
  - `step10 weight = 0.0`
  - `step12 weight = 0.05`
  - `step15/20 weight = 0.2`
  - final validation `loss_punctuation_profile_aux = 0.017141`
  - final special `loss_punctuation_profile_aux = 0.002731`
- 但 `D49 final = 2.507186 / 0.130834 / 3.196306 / 0.407234`
  - 相比 `D45`
    - special 略好
    - validation 略差
    - `e_evt / z_art` 基本不变

这说明:
- `D48` 已经把“late teacher softweight 也许能推开 `D45`”这条最小 follow-up 封口了。
- `D49` 则说明:
  - formal-special-facing punctuation supervision 确实能命中
  - 但当前只给出极轻微 tradeoff
  - 还不足以改写 route

先说人话:
- `D48` 不是“差一点点”，而是“完全没把轨迹推开”。
- `D49` 也不是没生效，
- 但它只是把 `D45` 稍微往 special 那边挪了一小格，
- 没有把控制保留一起抬上来。

### 更新后的下一阶段任务
1. 暂停继续做 `D45` 上的:
   - late teacher softweight 小变体
   - late punctuation-profile 小变体
2. 若继续沿 `D45` 路线推进，优先考虑:
   - 更强的 late teacher family decomposition
   - 或 frame-local / boundary-local 的 formal special supervision
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/102_round1_1_d48_d49_softweight_and_punctuation_followup_report.md`
  - `D48 / D49` 的正式实验链路，以及为何这两个最小 follow-up 仍未推动 `D45` 路线突破当前 route。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
  - 包含 `D48 / D49` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
  - `D49` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
  - `D49` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_default_minimax/`
  - `D49` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D50-D51 / structural transition supervision on D45 family` 更新
### 当前进度补充
229. 已完成: 新增配置 `configs/offline_mvp_train_d50_round1_1_d7_init_phase_teacher_family_structural_transition_late_only_d33step10_to_d29_20step_smallscale_seeded_shuffle.json`，把 `structural_clause_transition_aux` 以 late-only 方式接到 `D45` family 上。
230. 已完成: 新增配置 `configs/offline_mvp_train_d51_round1_1_d7_init_phase_teacher_family_structural_transition_late_secondary_d33step10_to_d29_20step_smallscale_seeded_shuffle.json`，在 `D50` 基础上只补 late structural secondary slot，用于验证是否只是 late exposure 不足。
231. 已完成: 跑通 `D50 / D51` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
232. 已完成: 产出包含 `D50 / D51` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D50 step10` 仍精确复刻 `D45 step10`:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D50` 的 late structural aux 不是挂空:
  - `step14 loss_structural_clause_transition_aux = 0.182235`
- 但 `D50 final = 2.503763 / 0.133735 / 3.196203 / 0.407221`
  - 与 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
  - 仍是数值级重合
- `D51` 则明确补足了 late structural exposure:
  - dry-run late `phase_priority_record_count = 204`
  - training `step12 / 19 / 20` 的 `loss_structural_clause_transition_aux` 都为非零
- 但 `D51 final = 2.493466 / 0.148358 / 3.130833 / 0.403129`
  - 相比 `D45`
    - validation 更低
    - 但 special / `e_evt` / `z_art` 都更差

这说明:
- `D50` 已经把“只把 boundary-local structural aux 挂到 `D45` 上会不会自然起杠杆”这条最小 follow-up 封口了。
- `D51` 则进一步说明:
  - 即使补最小 late structural exposure
  - 当前这条 sidecar-pool boundary-local family 在 `D45` 路线上仍只会把轨迹往 validation-first 推

先说人话:
- `D50` 是“命中过，但没推动”。
- `D51` 是“喂得更多了，但方向还是往 validation-first 滑”。
- 所以这条 family 在 `D45` 上也可以正式收口。

### 更新后的下一阶段任务
1. 暂停继续做 `D45` 上的:
   - `structural_clause_transition_aux` 纯 weight sweep
   - late structural secondary slot sweep
2. 若继续推进，优先考虑:
   - 更强的 late teacher family decomposition
   - 或真正新的 frame-local formal special supervision 定义
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/103_round1_1_d50_d51_structural_transition_on_d45_report.md`
  - `D50 / D51` 的正式实验链路，以及为何现有 sidecar-pool 的 boundary-local structural transition family 在 `D45` 路线上仍未形成新杠杆。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
  - 包含 `D50 / D51` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
  - `D51` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
  - `D51` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_default_minimax/`
  - `D51` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D52-D53 / late teacher checkpoint decomposition on D45 family` 更新
### 当前进度补充
233. 已完成: 新增配置 `configs/offline_mvp_train_d52_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29step10_shortpause_20step_smallscale_seeded_shuffle.json`，把 `D45` 的 late teacher 从 `D29 step20` 改为 `D29 step10`。
234. 已完成: 新增配置 `configs/offline_mvp_train_d53_round1_1_d7_init_phase_teacher_family_decomposition_d33step10_d29step10_d29step20_shortpause_20step_smallscale_seeded_shuffle.json`，把 late teacher family 进一步拆成 `D29 step10 -> D29 step20` 三段式 handoff。
235. 已完成: 跑通 `D52 / D53` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
236. 已完成: 产出包含 `D52 / D53` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D52 / D53 step10` 都精确复刻 `D45 step10`:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D52` 的 `step11 effective_teacher_consistency.teacher_checkpoint_path`
  - 已切为 `D29 step10`
- `D53` 的 `step15 -> step16`
  - 则已真实从 `D29 step10` 切到 `D29 step20`
- `D52 final = 2.506383 / 0.131541 / 3.201443 / 0.411876`
  - 相比 `D45`
    - validation 略差
    - special 略好
    - `e_evt / z_art` 略强
- `D53 final = 2.505593 / 0.132377 / 3.198097 / 0.410493`
  - 相比 `D52`
    - validation 略好
    - 但 special / `e_evt` / `z_art` 略回吐

这说明:
- `late teacher checkpoint decomposition` 不是完全没作用，
  但当前只形成了 `D45` 附近的 epsilon 级 tradeoff。
- `D52` 像是把 `D45` 稍微往 early compromise 拉回一点。
- `D53` 的三段式 handoff 则没有把这条线再真正推开。

先说人话:
- 这轮不是“切了也没切到”。
- 是“切得很真实，但只得到非常小的形状扰动”。
- 所以它更像封口 `late checkpoint micro-decomposition`，
  而不是打开新路线。

### 更新后的下一阶段任务
1. 暂停继续做 `D45` 上的:
   - late checkpoint 小步切分
   - `D29 step10 / step20` handoff 时点 sweep
2. 若继续推进，优先考虑:
   - teacher family 与 phase-specific target shape / gate 的更强联动
   - 或真正新的 frame-local formal special supervision
3. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/104_round1_1_d52_d53_late_teacher_checkpoint_decomposition_report.md`
  - `D52 / D53` 的正式实验链路，以及为何 late teacher checkpoint decomposition 目前只在 `D45` 附近形成 epsilon 级 tradeoff。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
  - 包含 `D52 / D53` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
  - `D53` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
  - `D53` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_default_minimax/`
  - `D53` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D54-D55 / teacher-family fused-hidden + gate-target linkage` 更新
### 当前进度补充
237. 已完成: 新增配置 `configs/offline_mvp_train_d54_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29step10_late_fusedhidden_shortpause_20step_smallscale_seeded_shuffle.json`，在 `D52` 基础上测试 late `D29 step10 + fused_hidden`。
238. 已完成: 新增配置 `configs/offline_mvp_train_d55_round1_1_d7_init_phase_teacher_family_gate_target_linkage_d33step10_d29step10_fused_to_d29step20_core_20step_smallscale_seeded_shuffle.json`，把 `D53` 升级成 mid short-pause fused-hidden -> late core-only no-fused 的更强 phase linkage。
239. 已完成: 跑通 `D54 / D55` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
240. 已完成: 产出包含 `D54 / D55` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D54 / D55 step10` 都精确复刻 `D45 step10`:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D54 step11`
  - 已真实切到 `D29 step10`
  - 且 `fused_hidden_weight = 0.05`
- `D55 step16`
  - 已真实切到 `D29 step20`
  - `fused_hidden_weight = 0.0`
  - teacher gate / sampler 也同步缩回 `challenge_proxy_core`
- `D54 final = 2.505569 / 0.131888 / 3.199683 / 0.412614`
  - 相比 `D45`
    - validation 略差
    - 但 special / `e_evt` / `z_art` 略好
- `D55 final = 2.506311 / 0.133216 / 3.190822 / 0.405426`
  - 被 `D54` 直接压住

这说明:
- `D54` 的 late fused-hidden 确实不是空作用，
  但仍只形成 epsilon 级 compromise。
- `D55` 的更强 phase-specific gate-target linkage
  没有把 `D54` 推开，反而把那点收益回吐掉了。

先说人话:
- `D54` 是“有一点点，但还是太小”。
- `D55` 是“切得更复杂了，但不比 `D54` 更好”。
- 所以这条线也更接近封口，而不是 breakout。

### 更新后的下一阶段任务
1. 暂停继续做 `D29 step10` late fused-hidden 小 sweep。
2. 暂停继续做 `D55` 这种 mid/late gate-target linkage 小排列。
3. 若继续推进，优先考虑:
   - 真正新的 frame-local formal special supervision
   - 或更强的 teacher family + supervision 联合定义
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/105_round1_1_d54_d55_teacher_family_fusedhidden_and_gate_target_linkage_report.md`
  - `D54 / D55` 的正式实验链路，以及为何这条更强 phase linkage 仍未突破 `D45 / D52` 附近的 epsilon tradeoff。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
  - 包含 `D54 / D55` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
  - `D55` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
  - `D55` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_default_minimax/`
  - `D55` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D56-D57 / formal special clause-shape aux` 更新
### 当前进度补充
241. 已完成: 在 `src/v5vc/offline_mvp/losses.py` 中新增 `formal_special_clause_shape_aux`，把 `target_weak_event_hints` 的 `clause_spans / clause_transition` 与 `target_special_supervision` pool gate 组合成新的 frame-local formal special supervision。
242. 已完成: 新增配置 `configs/offline_mvp_train_d56_round1_1_d7_init_d54_formal_special_clause_shape_finalsingle_late_20step_smallscale_seeded_shuffle.json` 与 `configs/offline_mvp_train_d57_round1_1_d7_init_d54_formal_special_clause_shape_middle_late_20step_smallscale_seeded_shuffle.json`，分别测试 `final/single` 版与 `middle` 扩展版。
243. 已完成: 跑通 `D56 / D57` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
244. 已完成: 产出包含 `D56 / D57` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D56 / D57 step10` 都精确复刻:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D56 dry-run step0`
  - `loss_formal_special_clause_shape_aux = 0.02187`
  - 但 effective `weight = 0.0`
- `D57 dry-run step0`
  - `loss_formal_special_clause_shape_aux = 0.025937`
  - 但 effective `weight = 0.0`
- `D56 step15`
  - `formal_special_clause_shape_aux.weight = 0.08`
  - `loss_formal_special_clause_shape_aux = 0.031738`
- `D57 step15`
  - `formal_special_clause_shape_aux.weight = 0.08`
  - `loss_formal_special_clause_shape_aux = 0.036294`
- `D56 final = 2.505586 / 0.131862 / 3.19987 / 0.412639`
- `D57 final = 2.505587 / 0.131861 / 3.199882 / 0.41264`

这说明:
- 第一版真正基于 `clause-span` 的 frame-local formal special supervision 已经工程打通，
  不是 sidecar 摆设。
- 但它在当前 sampler / route 下只在少数 late batch 命中，
  没有稳定渗透成 final behavior。
- `D56 / D57` 本质上都只是 `D54` 附近的万分位级再平衡。

先说人话:
- 新教法接上了。
- 但只偶尔命中，没形成持续杠杆。
- 所以这不是 breakout，而是第一版正式负证据。

### 更新后的下一阶段任务
1. 暂停继续做 `D56 / D57` 的小 weight sweep。
2. 暂停继续做 `single/final/middle` 小排列。
3. 若继续推进 formal special supervision，优先考虑:
   - 更稳定命中的 frame-local target 定义
   - 或先把 sampler / gate 改成能保证 late exposure 的版本
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/106_round1_1_d56_d57_formal_special_clause_shape_report.md`
  - `D56 / D57` 的正式实验链路，以及为何第一版 `clause-span` frame-local formal special supervision 仍只给出稀疏、不可持续的 late 扰动。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
  - 包含 `D56 / D57` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
  - `D57` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
  - `D57` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_default_minimax/`
  - `D57` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / D58-D59 / formal special sampler-gate alignment` 更新
### 当前进度补充
245. 已完成: 在 `src/v5vc/offline_mvp/data.py`、`src/v5vc/offline_mvp/losses.py`、`src/v5vc/train_entry.py` 中补齐 `required_within_special_duration_ceiling + min_clause_count` 级过滤，让 targeted sampling、formal special gate、teacher gate 能共用同一 cohort 定义。
246. 已完成: 新增配置 `configs/offline_mvp_train_d58_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_gate_late_20step_smallscale_seeded_shuffle.json` 与 `configs/offline_mvp_train_d59_round1_1_d7_init_d57_formal_special_clause2_shortpause_ceiling_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`，分别测试 sampler/formal gate 对齐版和再叠 late teacher gate 对齐版。
247. 已完成: 跑通 `D58 / D59` 的 dry-run、正式 `20 step`、final ablation、final special_eval、checkpoint_series、special_eval_series。
248. 已完成: 产出包含 `D58 / D59` 的 latest final comparison，并重新物化 fixed `route_handoff -> handoff_document -> stage_report` 资产。

### 当前阶段结论补充
- `D58 / D59 dry-run`
  - `phase_priority_record_counts = 19 -> 3`
  - late cohort 已显式收紧到:
    - `target::chapter3_2_firefly_191`
    - `target::chapter3_3_firefly_125`
    - `target::chapter3_3_firefly_148`
- `D58 / D59 step10`
  - 仍精确复刻:
  - `2.578968 / 0.161176 / 2.97141 / 0.42042`
- `D58 step11-20`
  - `loss_formal_special_clause_shape_aux` 全部非零
  - 约为 `0.032209 -> 0.030982`
- `D59 step11-20`
  - formal aux 同样全程非零
  - 且 late `teacher_consistency`
    - `pool_memberships = ['short_pause_no_terminal']`
    - `min_clause_count = 2`
    - `required_within_special_duration_ceiling = true`
- `D58 final = 2.480056 / 0.171798 / 2.994445 / 0.374825`
- `D59 final = 2.480048 / 0.171791 / 2.994481 / 0.374835`

这说明:
- `D56 / D57` 的“late exposure 太稀疏”问题，这轮已经工程上解决了。
- 但稳定命中同一短样本 cohort 之后，轨迹明显往 validation-first 方向滑，
  没有把 special / `e_evt` / `z_art` 推起来。
- `D59` 对 `D58` 基本只是 epsilon 级重放，
  说明 teacher gate 再对齐也没有打开新 regime。

先说人话:
- 这轮不是“还是没喂到样本”。
- 是“已经稳定喂满了，但这批样本本身不对路”。
- 所以当前这条 `short_pause + clause>=2 + duration ceiling` cohort 可以正式视作 validation-first 负证据。

### 更新后的下一阶段任务
1. 暂停继续做这 3 条短样本 cohort 的 priority ratio / teacher gate 小 sweep。
2. 暂停继续做 `D58 / D59` 同一路径上的微型 sampler 排列。
3. 若继续推进 formal special supervision，优先考虑:
   - 与 final special slice 更接近的新 cohort 定义
   - 或直接覆盖 special/no-text slice 的 frame-local supervision
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/107_round1_1_d58_d59_formal_special_sampler_gate_alignment_report.md`
  - `D58 / D59` 的正式实验链路，以及为何这次即使把 formal special exposure 稳定打满，也仍然只得到 validation-first compromise。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
  - 包含 `D58 / D59` 的最新 route-context final comparison。
- `reports/eval/offline_mvp_route_handoff_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
  - `D59` 之后的最新 route-aware handoff 产物。
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
  - `D59` 之后的固定格式正式交接件。
- `reports/stage_reports/offline_mvp_stage_report_round1_1_d22_d29_d33_d38_d39_d40_d41_d42_d43_d44_d45_d46_d47_d48_d49_d50_d51_d52_d53_d54_d55_d56_d57_d58_d59_default_minimax/`
  - `D59` 之后的固定格式阶段报告。
## 2026-03-16 `round1.1 / post-D59 / target special slice alignment diagnostic` 更新
### 当前进度补充
249. 已完成: 新增 `src/v5vc/special_slice_alignment.py`，并接入 `src/v5vc/cli.py` 正式命令 `analyze-offline-mvp-special-slice-alignment`，支持合并 `split + target_weak_event_hints + target_special_supervision` sidecar，对 `target_special_eval` 与 train-side proxy cohort 做结构距离诊断。
250. 已完成: 使用 `.\python.exe manage.py analyze-offline-mvp-special-slice-alignment` 在 `round1_1` 数据上实跑，产出 `reports/data/round1_1_special_slice_alignment/`。

### 当前阶段结论补充
- `target_special_eval`
  - 共 `8` 条
  - 全部满足:
    - `nonverbal_only = true`
    - `lexical_char_count = 0`
    - `pause_boundary_count = 0`
    - `terminal_boundary_count = 0`
    - `clause_count = 0`
    - `clause_span_count = 0`
- `target_train`
  - 共 `592` 条
  - `nonverbal_only_count = 0`
  - `lexical_char_count_zero = 0`
  - `clause_span_count_zero = 0`
  - `special_signature_count = 0`
- 当前最接近 `target_special_eval` 的现有 pool 仍是:
  - `challenge_proxy_core`
    - `count = 16`
    - `mean_special_distance = 3.184231`
  - `short_pause_no_terminal`
    - `count = 18`
    - `mean_special_distance = 3.732884`
- 但按新的启发式 cohort 重排后，更接近的 train-side proxy 已显式变成:
  - `micro_pause_none_singleton_strict`
    - `count = 8`
    - `mean_special_distance = 2.047626`
    - 条件为:
      - `duration <= special ceiling`
      - `lexical <= 1`
      - `pause = 1`
      - `terminal = 0`
      - `clause = 1`
      - `final_terminal_type = none`
- 最近邻 train records 也都指向同一类微短句:
  - `唔， / 二， / 一， / 欸， / 三， / 这，`
  - 它们共同特征是:
    - `lexical = 1`
    - `pause = 1`
    - `terminal = 0`
    - `clause = 1`
    - `clause_span = 1`
- 诊断推荐已明确给出:
  - `continue_current_d58_d59_line = false`
  - `principle_change_required = true`
  - `recommended_supervision_direction = Pivot from clause-shape supervision to clause-free singleton sparse-frame supervision over the closest micro-utterance cohort.`

这说明:
- `D56-D59` 当前不是“命中率还差一点”，也不是“cohort 还可以继续微调”。
- 真正的问题是:
  - `target_special_eval` 的结构签名是完全 `clause-free / lexical-free / nonverbal-only`
  - 而 train 侧最接近的代理样本依然是 `lexical=1 + clause_span=1` 的微短句
- 所以当前矛盾已经从:
  - “怎么把 formal special clause-shape 命中得更稳定”
- 转成:
  - “要不要承认现有 clause-shape 代理原则本身就错位”

先说人话:
- 我们终于把“特殊切片到底像什么”这件事看清了。
- 它不是短句，不是双 clause，也不是轻微 formal。
- 它本质上更像一批没有正文、没有结构骨架的极稀疏非言语片段。

### 更新后的下一阶段任务
1. 暂停继续做 `D56-D59` family 的 weight / sampler / teacher 微调。
2. 若继续推进 formal special 监督，优先转向:
   - `clause-free singleton sparse-frame supervision`
   - 以 `micro_pause_none_singleton_strict` 为首个 train-side proxy cohort
3. 若继续做 cohort 设计，优先围绕:
   - `duration <= special ceiling`
   - `lexical <= 1`
   - `single pause`
   - `no terminal`
   - `singleton clause`
   做更贴近 nonverbal slice 的代理定义，而不是继续 `clause>=2` family。
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

### 文档补充
- `docs/108_round1_1_post_d59_special_slice_alignment_report.md`
  - `D59` 之后的 special-slice 诊断报告，以及为何当前矛盾已从“命中率”转成“代理原则错位”。
- `reports/data/round1_1_special_slice_alignment/`
  - 新的 machine-readable / markdown 诊断产物。
## 2026-03-16 `round1.1 / 200step long-window trajectory probe` 更新
### 当前进度补充
251. 已完成: 为 `D22 / D33 / D59` 三条代表路线补齐 `200 step` trajectory probe 配置，并全部通过 dry-run，确认 checkpoint、sidecar、phase schedule 与评估入口可用。
252. 已完成: 跑通 `EXP-20260316-013(D22-200step)`、`EXP-20260316-015(D33-200step)`、`EXP-20260316-014(D59-200step)` 的正式训练、final `special_eval`、final `ablation_eval`、`checkpoint_series` 与 `special_eval_series(step50/100/150/200)`。
253. 已完成: 产出六实验 mixed-horizon `route_selection` 与 final comparison，覆盖旧锚点 `D22 / D29 / D33` 与新长窗 `D22 / D33 / D59`。

### 当前阶段结论补充
- 三条 `200 step` probe 都给出同一方向:
  - validation 持续下降
  - special delta 持续变差
  - `zero_e_evt` 持续走弱
- 这说明:
  - 当前 `20/30 step` quick-screen 并没有截断一个“late special breakout”
  - late dynamics 的主方向反而是更强的 validation-first compromise
- `D22` 与 `D33` 到 `step200` 基本收敛:
  - `D33 step200 = 2.122699 / 0.239846 / 1.9703 / 0.710849`
  - `D22 step200 = 2.125622 / 0.238578 / 1.864222 / 0.669467`
  - 两者 validation 几乎打平，但旧 quick-screen 阶段更清楚的 route 分工明显被压扁
- `D59 step200 = 2.126544 / 0.258922 / 1.927875 / 0.311379`
  - 说明把原则错位的 `clause-shape` 线继续拉长，并不会自然翻盘
  - 它仍然不是 post-D59 应继续追加预算的主线
- 六实验 mixed-horizon selector 会直接塌成:
  - `selected_policy = validation_strict`
  - `selected_anchor = D33(200step)`
- 这不应被解释为“当前正式默认 route 改成 D33-200”；
  更合理的解释是:
  - `20/30 step` quick-screen anchor
  - 与 `200 step` trajectory probe final
  - 不能直接混进同一个 `default_minimax` selector 里做正式 handoff 选点

先说人话:
- 长窗确实值得补。
- 但它回答的是“后面还会怎么滑”，不是“现在默认冠军要不要立刻换人”。
- 这批 `200 step` 更像望远镜，不像新的正式交接锚点。

### 更新后的下一阶段任务
1. 当前固定 handoff / stage-report 继续保持 quick-screen 口径:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 后续实验制度优先收敛成两段式:
   - quick-screen 负责接线与 route 粗筛
   - `200 step` 只给少数代表路线做 trajectory probe
3. 若继续推进 `post-D59` 新方向，优先在 quick-screen 里先验证:
   - `clause-free singleton sparse-frame supervision`
   - 或更贴近 `micro_pause_none_singleton_strict` 的新 proxy principle
4. 若后续还要做长窗选点，优先改成:
   - matched-horizon comparison
   - 或 checkpoint-selected late stop
   - 不再把 `20/30 step` final 和 `200 step` final 直接混进同一个默认 selector

### 文档补充
- `docs/109_round1_1_longwindow_200step_trajectory_probe_report.md`
  - 三条 `200 step` trajectory probe 的正式报告，以及为何这批结果更适合作为长窗观测，而不是直接替换当前 handoff anchor。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d29_d33_d59_default_minimax/`
  - 六实验 mixed-horizon route selector 结果，显示默认预算在 mixed-horizon 条件下会塌成 `validation_strict`。
- `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d29_d33_d59_default_minimax/`
  - 旧锚点与三条 `200 step` probe 的正式 final comparison。
## 2026-03-16 `round1.1 / D60-D61 / singleton sparse proxy pivot` 更新
### 当前进度补充
254. 已完成: 在 `src/v5vc/offline_mvp/losses.py` 新增 `singleton_sparse_proxy_aux`，并接入 `compute_offline_mvp_loss`、effective loss resolve 与训练摘要；同时重生成 `target_special_supervision` sidecar，正式纳入 `micro_pause_none_singleton_strict / relaxed` pool。
255. 已完成: 新增 `D60` 配置 `configs/offline_mvp_train_d60_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`，并跑通 dry-run、正式 `20 step`、final `special_eval`、final `ablation_eval`、`checkpoint_series` 与 `special_eval_series`。
256. 已完成: 新增最小 teacher-gate 对照 `D61` 配置 `configs/offline_mvp_train_d61_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_relaxed_late_20step_smallscale_seeded_shuffle.json`，并跑通同级完整实验链。
257. 已完成: 产出 `D22 / D29 / D33 / D60` selector 与 `D22 / D29 / D33 / D59 / D60 / D61` final comparison，确认当前 route 不变但 singleton sparse proxy pivot 已形成新的可复用 special principle。

### 当前阶段结论补充
- `D60 final = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - 相对 `D59 = 2.480048 / 0.171791 / 2.994481 / 0.374835`
    - validation 更差 `+0.042692`
    - 但 special 明显更好 `-0.059654`
    - `zero_e_evt / zero_z_art` 也明显回升
- 这说明:
  - `post-D59` 的原则切换是对的
  - `clause-free singleton sparse proxy`
    不是“另一个 validation-first proxy”
  - 它已经能把轨迹重新拉回接近 `D33` 的 special-aware 区间
- `D60` 与 `D33` 已非常接近:
  - `D33 = 2.52818 / 0.111677 / 3.312339 / 0.465828`
  - `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - 即:
    - validation 略优
    - special 近乎打平
    - control floor 略弱
- `D61` 与 `D60` 四项指标完全一致:
  - 说明当前收益不是由 late teacher gate 从 relaxed 再收紧到 strict 带来的
  - 更主要的有效变量是:
    - late singleton targeted sampling
    - `singleton_sparse_proxy_aux`
- route selector(`D22 / D29 / D33 / D60`, `budget = 0.05`) 仍保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`
- 这说明:
  - singleton sparse proxy principle 已经对了
  - 但目前 validation tax 仍偏高
  - 还不能直接刷新当前 fixed handoff

先说人话:
- 这轮终于把“原则对不对”这件事跑清楚了。
- 现在不是继续修 `D59`，也不是继续抠 teacher gate。
- 下一步更像是把这条对的 singleton principle，移植到更强 validation backbone 上。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D60 / D61` 的 strict-vs-relaxed teacher gate 微调
   - 同一骨架上的 gate 小排列
3. 更值得优先推进:
   - `D22 backbone + singleton sparse late pulse`
   - 或更短 / 更早衰减的 singleton late tail，用来削掉 validation tax
4. 当前对 `post-D59` 的正式解释应更新为:
   - 原则切换有效
   - route 暂未刷新
   - 下一手要从“对的 principle”转向“更低 validation 代价的集成方式”

### 文档补充
- `docs/110_round1_1_d60_d61_singleton_sparse_proxy_pivot_report.md`
  - `D60 / D61` 的正式报告，以及为何这轮收益应归因于 singleton sparse proxy principle，而不是 teacher gate 再收紧。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_default_minimax/`
  - 最新 quick-screen selector，确认当前 `default_minimax` 仍为 `D22`。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_default_minimax/`
  - `D59 / D60 / D61` 与当前 anchor 的正式 final comparison。
## 2026-03-16 `round1.1 / D62-D63 / D22 backbone singleton late-pulse integration` 更新
### 当前进度补充
258. 已完成: 新增 `D62` 配置 `configs/offline_mvp_train_d62_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_30step_smallscale_seeded_shuffle.json`，把 `singleton_sparse_proxy_aux` 与 `step21-30` singleton targeted sampling 接到 `D22 backbone`，并跑通 dry-run、正式训练与完整评估链。
259. 已完成: 新增 `D63` 配置 `configs/offline_mvp_train_d63_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_teacheraligned_30step_smallscale_seeded_shuffle.json`，将 late `teacher_consistency` 也对齐到 `micro_pause_none_singleton_strict`，并跑通 dry-run、正式训练与完整评估链。
260. 已完成: 产出纳入 `D62 / D63` 的最新 selector 与 final comparison，确认 `D22` route 不变，且 `teacher-aligned late gate` 在这条 family 上是 no-op。

### 当前阶段结论补充
- `D62 final = 2.42375 / 0.234048 / 2.603584 / 0.316145`
- `D63 final = 2.42375 / 0.234048 / 2.603584 / 0.316145`
- 相对当前 route anchor `D22 = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
  - validation 虽更低
  - 但 special 明显变差
  - `zero_e_evt / zero_z_art` 也明显塌陷
- 这说明:
  - `singleton sparse proxy` principle 本身没有被否定
  - 但“把它直接 graft 到 `D22` 后半段”这条集成形状不对
  - 它不会形成新的 minimax anchor
- `D63` 与 `D62` 在:
  - final 四项
  - checkpoint series
  - step loss 轨迹
  - late `loss_singleton_sparse_proxy_aux`
  上都逐点一致
- 这进一步说明:
  - 当前坏轨迹不能简单归因于
    - `D62` 的 late `core-only teacher`
    - 与 singleton sampler 不对齐
  - 把 late teacher gate 对齐到 singleton strict cohort
    在这条 family 上仍是近似 no-op
- 最新 selector(`D22 / D29 / D33 / D60 / D62 / D63`, `budget = 0.05`) 继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`

先说人话:
- `D60` 告诉我们 principle 是对的。
- `D62` 告诉我们接法不对。
- `D63` 告诉我们这不是再补一层 late teacher 对齐就能修好的问题。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D22 backbone + singleton late pulse`
   - 这条 family 上的 late teacher gate 小排列
3. 若继续削减 singleton principle 的 validation tax，优先回到:
   - `D60` 这一类已验证有效的 post-`D59` backbone
   - 再做更短、更弱或 checkpoint-selected 的 late tail
4. 当前对这轮实验的正式解释应更新为:
   - principle 仍成立
   - `D22` graft 失败
   - teacher-aligned late gate 也是 no-op

### 文档补充
- `docs/111_round1_1_d62_d63_d22_singleton_sparse_latepulse_integration_report.md`
  - `D62 / D63` 的正式报告，以及为何这轮应把 `D22 backbone + singleton late pulse` family 暂时停掉。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d62_d63_default_minimax/`
  - 纳入 `D62 / D63` 后的最新 selector，确认当前 `default_minimax` 仍为 `D22`。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d62_d63_default_minimax/`
  - `D59 / D60 / D61 / D62 / D63` 与当前 anchor 的正式 final comparison。
## 2026-03-16 `round1.1 / D64-D67 / D60 tail-strength decomposition` 更新
### 当前进度补充
261. 已完成: 新增 `D64` 配置 `configs/offline_mvp_train_d64_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_shorttail_15step_smallscale_seeded_shuffle.json`，验证 `D60 short-tail`，并跑通 dry-run、正式训练与完整评估链。
262. 已完成: 新增 `D65` 配置 `configs/offline_mvp_train_d65_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_weaktail_20step_smallscale_seeded_shuffle.json`，验证 `D60 weaker-tail`，并跑通 dry-run、正式训练与完整评估链。
263. 已完成: 新增 `D66 / D67` 配置，分别只降低 `singleton_sparse_proxy_aux.weight` 与只降低 late `priority_ratio`，并跑通两条 dry-run、正式训练与完整评估链。
264. 已完成: 产出纳入 `D64 / D65 / D66 / D67` 的最新 selector 与 final comparison，确认 `D22` route 不变，同时把 `D60` family 的 tail-strength 主变量拆清楚。

### 当前阶段结论补充
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D64 = 2.539564 / 0.154003 / 3.012511 / 0.400641`
- `D65 = 2.482579 / 0.172447 / 2.980073 / 0.375719`
- `D66 = 2.522723 / 0.11214 / 3.260339 / 0.435397`
- `D67 = 2.482594 / 0.172458 / 2.979895 / 0.375695`
- 这说明:
  - `short-tail` 不能削 validation tax
  - 它反而连 validation 本身也没保住，同时伤 special/control floor
  - `weaker-tail` 虽能换来 validation
  - 但 special / `e_evt` / `z_art` 会明显掉回接近 `D59` 的区间
- 更重要的是:
  - `D66 ~= D60`
  - `D67 ~= D65`
- 这把 `D65` 的主变量直接拆清楚了:
  - aux weight 从 `0.10 -> 0.08` 基本是 no-op
  - 真正有杠杆的是 late singleton `priority_ratio`
  - 但这个杠杆往下调时，会明显把 singleton principle 收益打掉
- 最新 selector(`D22 / D29 / D33 / D60 / D64 / D65 / D66 / D67`, `budget = 0.05`) 继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`

先说人话:
- `D60` 这条线现在不是“tail 太长”或“aux 稍重”的问题。
- 真正顶住收益的是 late singleton batch 占比。
- 一旦把这部分占比往下拉，validation 会更好一点，但 route 会立刻退回 validation-first compromise。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D60` family 的 short-tail
   - `D60` family 的 aux-weight 微调
   - `D60` family 的 sampler-ratio 下调 sweep
3. 若继续削 singleton principle 的 validation tax，
   下一手应离开这条 simple tail-strength 轴，转向:
   - 更上游的 backbone / handoff 形状
   - 或 matched-horizon / checkpoint-selected 设计
4. 当前对 `D60` family 的正式解释应更新为:
   - `D60` 是当前 local optimum
   - late singleton sampler ratio 是主杠杆
   - 但它不是当前可继续安全下调的旋钮

### 文档补充
- `docs/112_round1_1_d64_d65_d66_d67_d60_tail_strength_decomposition_report.md`
  - `D64 / D65 / D66 / D67` 的正式报告，以及为何 `D60` family 的 simple tail-strength sweep 可以暂时收口。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d64_d65_d66_d67_default_minimax/`
  - 纳入 `D64-D67` 后的最新 selector，确认当前 `default_minimax` 仍为 `D22`。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d64_d65_d66_d67_default_minimax/`
  - `D59 / D60 / D61 / D64 / D65 / D66 / D67` 与当前 anchor 的正式 final comparison。
## 2026-03-16 `round1.1 / D68-D69 / upstream D22 late-handoff on D60` 更新
### 当前进度补充
265. 已完成: 新增 `D68` 配置 `configs/offline_mvp_train_d68_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json`，把 `D60` 的 late teacher source 从 `D29 step10` 切到 `D22 step30`，并跑通 dry-run、正式训练与完整评估链。
266. 已完成: 新增 `D69` 配置 `configs/offline_mvp_train_d69_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_d22like_latehandoff_20step_smallscale_seeded_shuffle.json`，进一步把 late handoff shape 调成更 `D22-like`，并跑通 dry-run、正式训练与完整评估链。
267. 已完成: 修复 `anchor_route_analysis / selector` 在某 policy 无 eligible anchors 时直接异常退出的问题，当前会将该 policy 记为不可行而不是中断 route 产物生成；随后已补齐纳入 `D68 / D69` 的最新 selector 与 final comparison。

### 当前阶段结论补充
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
- `D69 = 2.523948 / 0.111144 / 3.271397 / 0.434243`
- 这说明:
  - `D68` 与 `D60` 相比，
    只有 epsilon 级再平衡:
    - validation 略好
    - special 略好
    - `e_evt` 略好
    - `z_art` 略差
  - `D69` 再往更 `D22-like late handoff` 推一步后，
    也只是:
    - special / `e_evt` 再往前拽一小点
    - validation / `z_art` 再吐回去一小点
- 更重要的是:
  - 两条线都没有形成新的 route
  - 也没有证据表明:
    - 把 late teacher source 改成 `D22`
    - 或把 late handoff shape 调得更 `D22-like`
    - 就能自然消掉 `D60` 的 validation tax
- 同时要注意一个细口径变化:
  - 纳入 `D68 / D69` 后，
    raw `special_push` anchor 已变成 `D69`
  - 但这只建立在:
    - `special_delta 0.111144 vs 0.111677`
    - 这种 epsilon 级领先上
  - `D33` 仍保持:
    - `best zero_e_evt`
    - `best zero_z_art`
  - 因此当前更合理的解释是:
    - special-route selector 上出现了微弱换人
    - 但 fixed handoff 的 `D33 = special / e_evt / z_art` 口径暂不刷新
- 最新 selector(`D22 / D29 / D33 / D60 / D68 / D69`, `budget = 0.05`) 继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`

先说人话:
- 这轮不是完全没动。
- 但所有变化都还停留在 `D60` 周围的极小摇摆。
- 这条“更上游 D22 late-handoff”轴现在也可以先收口了。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
   - `D69` 当前只视为 raw `special_push` 的 epsilon 级领先者
2. 暂停继续做:
   - `D60 -> D22 late teacher source` 小变体
   - `D60 -> D22-like late handoff shape` 小变体
3. 若继续推进 singleton sparse 主线，
   下一手更值得转向:
   - matched-horizon / checkpoint-selected 设计
   - 或比当前 handoff 微调更强的 backbone 级变化
4. 当前对 `D68 / D69` 的正式解释应更新为:
   - upstream late-handoff axis 已验证很弱
   - `D60` 仍是当前 local optimum
   - route 继续不变

### 文档补充
- `docs/113_round1_1_d68_d69_upstream_d22_late_handoff_on_d60_report.md`
  - `D68 / D69` 的正式报告，以及为何这条 upstream D22 late-handoff 轴应解释为 epsilon 级再平衡，而不是新 route。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_default_minimax/`
  - 纳入 `D68 / D69` 后的最新 selector，确认当前 `default_minimax` 仍为 `D22`。
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d64_d65_d66_d67_d68_d69_default_minimax/`
  - `D59 / D60 / D61 / D64 / D65 / D66 / D67 / D68 / D69` 与当前 anchor 的最新 final comparison。
## 2026-03-16 `round1.1 / matched20 checkpoint-anchor` 更新
### 当前进度补充
268. 已完成: 新增 `src/v5vc/checkpoint_anchor_materializer.py`，并在 `src/v5vc/cli.py` 接入正式命令 `materialize-offline-mvp-checkpoint-anchor`，用于把已有实验的指定 checkpoint step 物化成 synthetic anchor metrics。
269. 已完成: 物化 `D22 step20 anchor`，产物为 `reports/experiments/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.checkpoint-step20-anchor.metrics.json`。
270. 已完成: 基于 `D29 / D22-step20 / D33 / D60 / D68 / D69` 跑通 matched20 route-analysis、default selector、`budget=0.13` selector smoke 与 matched20 final comparison。

### 当前阶段结论补充
- 先验检查已经说明:
  - `D60 / D68 / D69 step10` 完全同轨
  - 而且 `step20` 相对 `step10` 同时改善:
    - validation
    - special
    - `e_evt`
    - `z_art`
  - 所以这条主线当前不值得继续做 `checkpoint-selected late stop`
- 真正有结论的是 matched20:
  - `D29 = 2.397175 / 0.171769 / 2.978481 / 0.364927`
  - `D22-step20 = 2.470626 / 0.178101 / 3.021211 / 0.398439`
  - `D33 = 2.52818 / 0.111677 / 3.312339 / 0.465828`
  - `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
  - `D69 = 2.523948 / 0.111144 / 3.271397 / 0.434243`
- matched20 route-analysis 给出:
  - `validation = D29`
  - `special = D69`
  - `zero_e_evt / zero_z_art = D33`
  - `minimax = D68`
- 但同时:
  - `budget_to_minimax_anchor = 0.12514`
  - `budget_to_special_anchor = 0.126773`
- 这意味着:
  - 在 matched20 下，
    当前默认 `budget = 0.05` 不再允许 minimax
  - selector 会直接退化成:
    - `selected_policy = validation_strict`
    - `selected_anchor = D29`
  - 若把预算放宽到 `0.13`,
    才会切到:
    - `selected_policy = default_minimax`
    - `selected_anchor = D68`

先说人话:
- 这轮真正跑明白的是:
  - `D60` family 不需要 early-stop
  - 需要被质疑的是当前 `D22 = default_minimax` 这件事本身带着 horizon advantage
- 一旦把 horizon 拉平到 `20 step`,
  `D22-step20` 已经压不住 `D60/D68/D69`
  这条 post-`D59` 主线。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 先保持旧 quick-screen 口径不动:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D60` family 的 checkpoint-selected late stop
   - `D60 / D68 / D69` 的 teacher-handoff 微调
3. 更值得优先推进:
   - 正式收口 quick-screen horizon policy
   - 即:
     - 保持当前不对称 quick-screen
     - 还是迁移到 matched-horizon
4. 若后续接受 matched-horizon，
   还必须同时决定:
   - validation budget 是否从 `0.05` 重设到更宽区间
   - 否则 selector 会直接塌回 `D29`

### 文档补充
- `docs/114_round1_1_matched20_checkpoint_anchor_report.md`
  - matched20 的正式报告，以及为何这轮真正的问题是 horizon policy，而不是 D60 family 的 early-stop。
- `reports/eval/offline_mvp_anchor_routes_round1_1_matched20_d22step20_d29_d33_d60_d68_d69/`
  - matched20 route-analysis，确认 `minimax = D68`。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`
  - matched20 下沿用当前 `budget = 0.05` 的 selector，显示其会退化成 `validation_strict = D29`。
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_budget013/`
  - matched20 下 `budget = 0.13` 的 selector smoke，显示 minimax 会切到 `D68`。
- `reports/eval/offline_mvp_final_comparison_round1_1_matched20_d22step20_d29_d33_d60_d68_d69_default_minimax/`
  - matched20 候选集的 final comparison。
## 2026-03-16 `round1.1 / quick-screen horizon policy decision` 更新
### 当前进度补充
271. 已完成: 基于现口径 quick-screen、`matched20@0.05` 和 `matched20@0.13` 三套 selector，分别生成 route recap，用于并排比较制度差异。
272. 已完成: 产出 `quick-screen horizon policy` 正式决策报告，明确当前不应立即迁移官方 selector，而应先进入 `matched20 shadow policy` 阶段。

### 当前阶段结论补充
- 当前三套制度已经可以清楚分开:
  - 现口径 quick-screen:
    - `default_minimax = D22`
  - `matched20@0.05`:
    - selector 直接塌成 `validation_strict = D29`
  - `matched20@0.13`:
    - `default_minimax = D68`
- 这说明:
  - 方案 B(`matched20` 但仍保留 `budget = 0.05`) 不值得采用
  - 方案 C(`matched20 + budget reset`) 在分析上成立，
    但当前若直接升为官方制度，
    会同时改:
    - horizon
    - validation budget
    - minimax anchor
    变化面过大
- 因此当前最稳妥的执行方式应是:
  - 官方 fixed handoff 继续保持旧 quick-screen
  - `matched20` 作为 shadow policy 并行跟踪

先说人话:
- 现在最需要改的不是模型，
  而是我们怎么解释 selector。
- 但这次也还没到“今天就把官方规则全换掉”的程度。
- 更合理的是先让 matched20 当影子规则跑几轮，
  看它是不是稳定把 `D68` 这条线推成新 minimax。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 从本轮开始，
   每条新主线候选同步追加 shadow 产物:
   - `matched20 route-analysis`
   - `matched20 selector @ budget 0.05`
   - `matched20 selector @ budget 0.13`
3. 只有当:
   - `matched20 minimax` 连续稳定指向同一条新主线
   - 且 budget reset 也被接受
   才考虑把官方 selector 从旧 quick-screen 迁移到 matched-horizon
4. 在此之前，
   不再把当前 `D22 = default_minimax` 解释成“公平 horizon 下仍然占优”

### 文档补充
- `docs/115_round1_1_horizon_policy_decision_report.md`
  - 三套 horizon policy 的并排比较，以及为何当前更合理的是保留旧 quick-screen 官方口径、并行跟踪 matched20 shadow policy。
## 2026-03-16 `round1.1 / 1.md review + shadow bundle automation` 更新
### 当前进度补充
273. 已完成: 只读审查 `1.md`，并给出接受但收缩的正式结论：接受其制度思想，不接受把 `500` 写成默认标准，也不接受“凡挑战官方 anchor 必须 matched200/500”的过强规则。
274. 已完成: 新增 `src/v5vc/horizon_policy_shadow.py`，并在 `src/v5vc/cli.py` 接入正式命令 `build-offline-mvp-matched-horizon-shadow`，用于自动生成 matched-horizon shadow bundle。
275. 已完成: 用当前 `D29 / D33 / D60 / D68 / D69 + D22-step20` 实跑新命令，产出 `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69/`，并验证结果与上一轮手工 matched20 结论一致。

### 当前阶段结论补充
- `1.md` 的大方向被接受:
  - `step20` 只负责 quick-screen
  - long-horizon 问题必须与 quick-screen 问题分开
- 但当前正式口径做了两点收缩:
  - 不把 `500` 设为默认标准，改写成:
    - `matched long horizon(200+)`
  - 不把规则写成:
    - “任何挑战官方 default anchor 都必须 matched200/500”
  - 更精确的执行条件是:
    - 只有当结论要改写官方 fixed handoff 时，
      才必须补 matched long horizon 佐证
- 更重要的是:
  - `matched20 shadow policy` 现在已经被工具化
  - 后续不需要再手工拼:
    - checkpoint anchor
    - route-analysis
    - selector
    - comparison
    - recap

先说人话:
- 这轮不是在模型上继续拧参数，
  而是在把“正确的问题怎么问”这件事固化成流程。
- 现在这套 shadow policy 已经不是讨论口号，
  而是可重复执行的正式命令了。

### 更新后的下一阶段任务
1. 当前 fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 后续每条新主线候选，默认同步追加:
   - `build-offline-mvp-matched-horizon-shadow`
3. 只有当 shadow policy 连续稳定指向同一条新主线时，
   才继续补 matched long horizon(`200+`)
   去挑战官方 fixed handoff
4. 在此之前，
   不再把任何单次 `matched20` 结果直接解释成“官方 anchor 已刷新”

### 文档补充
- `docs/116_round1_1_horizon_policy_review_and_shadow_bundle_report.md`
  - `1.md` 的正式审查结论，以及为何当前采纳的是其制度思想的收缩版；同时记录 matched-horizon shadow bundle 已正式工具化。
## 2026-03-16 `round1.1 / D70+D71 / stronger checkpoint backbone singleton sparse` 更新
### 当前进度补充
276. 已完成: 新增两份 backbone-level quick-screen 配置:
   - `offline_mvp_train_d70_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
   - `offline_mvp_train_d71_round1_1_d29_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
277. 已完成: 纠正本轮一开始误用系统 `python` 的执行错误，确认仓库根目录 `.\python.exe = Python 3.10.11`，并在继续前补充踩坑记录。
278. 已完成: `D70 / D71` 全部跑通 `init-experiment`、dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
279. 已完成: 将 `D70 / D71` 并入 official quick-screen route-analysis / selector / final comparison / route recap，并同步补齐 matched20 shadow bundle。

### 当前阶段结论补充
- `D70 = 2.399035 / 0.168635 / 2.941607 / 0.365565`
- `D71 = 2.340197 / 0.190968 / 2.634231 / 0.320415`
- `D70` 是这条 post-`D59` 主线第一次真正通过 backbone 级变化把 `D60` validation tax 压回接近 `D29` 的区间。
- `D71` 则证明:
  - 再把 backbone 推到 `D29 step20`
  - 会直接过冲成 validation-first
- official quick-screen 下:
  - minimax 仍是 `D22`
  - 但 `best_validation` 已被 `D71` 拉到 `2.340197`
  - 导致 `budget_to_minimax_anchor` 抬到 `0.103997`
  - 所以 raw selector 在 `budget=0.05` 下会直接塌成:
    - `validation_strict = D71`
- matched20 shadow 下:
  - `validation = D71`
  - `special = D69`
  - `zero_e_evt / zero_z_art = D33`
  - `minimax = D70`
  - `budget_to_minimax_anchor = 0.058838`
  - selector:
    - `matched20@0.05 -> D71`
    - `matched20@0.13 -> D70`

先说人话:
- `D70` 是真进展，
  不是 epsilon 摇摆。
- 但 `D71` 同时提醒我们:
  - 这条 backbone 轴很容易一路滑成纯 validation。
- 现在能说的是:
  - `D70` 比 `D68` 更值得继续
  - 但 shadow minimax 还没稳定到可以上 `200+` 的程度

### 更新后的下一阶段任务
1. official fixed handoff / stage-report 暂不刷新，继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D71` 一类更强 validation-first backbone 延伸
3. 下一手更值得优先推进:
   - 以 `D70` 为新主线
   - 把 `D68 / D69` 那类 late teacher source / handoff 恢复旋钮迁移到 `D70`
   - 看能否在不丢掉 `D70` validation 的前提下补回一部分 `e_evt / z_art`
4. 只有当 shadow minimax 连续稳定指向 `D70` family 时，
   才继续补:
   - matched long horizon(`200+`)

### 文档补充
- `docs/117_round1_1_d70_d71_stronger_backbone_singleton_sparse_report.md`
  - `D70 / D71` 的正式报告，以及为何 `D70` 是真实 backbone-level 进展，而 `D71` 更应解释成 validation-first 过冲与 selector contract 告警。
## 2026-03-16 `round1.1 / python interpreter warning guard` 更新
### 当前进度补充
280. 已完成: 在项目入口 `manage.py` 增加轻量 Python 运行时告警；若当前解释器路径不是仓库根目录 `python.exe`，或版本低于当前项目基线 `3.10`，会在启动时打印 warning。

### 当前阶段结论补充
- 这次不再依赖人工记忆 pitfall 文档来避免解释器误用。
- 入口现在会主动提醒两类问题:
  - 当前不是仓库根目录 `.\python.exe`
  - 当前版本低于项目实际使用基线 `3.10`
- 该改动只加告警，不改变任何命令执行逻辑。

先说人话:
- 以后如果我或者别人又手滑用成系统 `python`，
  命令一启动就会先看到 warning。
- 这样能把“环境用错了”挡在最前面，
  不再那么容易误判成代码问题。

### 更新后的下一阶段任务
1. 后续所有 Python 命令继续显式使用:
   - `.\python.exe manage.py ...`
2. 若再出现 Python 运行时异常，
   先看入口 warning，
   再决定是否需要进入实现层排查。

### 文档补充
- `manage.py`
  - 新增 Python 解释器路径 / 版本轻量告警。
## 2026-03-16 `round1.1 / D72+D73 / D70 late-restore transfer` 更新
### 当前进度补充
281. 已完成: 基于 `D70` 新增两份 late-restore 迁移配置:
   - `offline_mvp_train_d72_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json`
   - `offline_mvp_train_d73_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22like_latehandoff_20step_smallscale_seeded_shuffle.json`
282. 已完成: 修复本轮并行 `init-experiment` 触发的 experiment id 抢号问题，保留正确的 `D72 = EXP-...027`，重建 `D73 = EXP-...029`，并删除错误的 `027-d73` 占位记录。
283. 已完成: `D72 / D73` 全部跑通 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series，并并入 official quick-screen 与 matched20 shadow 产物。

### 当前阶段结论补充
- `D72 = 2.399071 / 0.167648 / 2.957 / 0.364989`
- `D73 = 2.398942 / 0.168183 / 2.953266 / 0.364179`
- 两条线的 `step10` 都与 `D70` 完全同轨，说明本轮新增信息只来自 late `step11-20`。
- `D72 / D73` 都没有形成新 regime，
  而是在 `D70` 盆地里做 epsilon 级再平衡:
  - `D72` 更偏 `special + e_evt`
  - `D73` 更偏 `validation + special`
- official quick-screen 继续不变:
  - validation = `D71`
  - minimax = `D22`
  - selector(`budget=0.05`) 仍是 `validation_strict = D71`
- matched20 shadow 则从上一轮的 `D70`，
  epsilon 级切到:
  - `minimax = D72`
  - `budget_to_minimax_anchor = 0.058874`
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D72`

先说人话:
- `D70 family` 现在已经不是散的，
  而是收缩成一个很窄的盆地了。
- 但这个盆地内部还在 `D70 / D72 / D73` 之间做很小的换人，
  还没到“单点已经完全坐稳”的程度。

### 更新后的下一阶段任务
1. official fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D70 family` 的 late teacher source / handoff 小变体
3. 下一手若继续沿这条 family 推进，
   更值得优先转向:
   - 更明确的 control-target restoration
   - 而不是继续做纯 handoff 旋钮
4. 若准备挑战 official fixed handoff，
   当前候选应按 family 解释为:
   - `D70 / D72 / D73`
   再决定是否补 `matched long horizon(200+)`

### 文档补充
- `docs/118_round1_1_d72_d73_d70_late_restore_report.md`
  - `D72 / D73` 的正式报告，以及为何应把它们解释成 `D70` 盆地内的 epsilon 级 late-restore 再平衡，而不是新路线。
## 2026-03-16 `round1.1 / context restore and takeover state` 更新
### 当前进度补充
284. 已完成: 按 `docs/00_context_bootstrap.md` 规定顺序恢复上下文，使用 UTF-8 显式复读 `docs/00_context_bootstrap.md`、`docs/01_project_overview_and_plan.md`、`docs/02_pitfalls_log.md`、`initial_design.md`、`initial_design_judg.md`，并核对 `manage.py`、`src/v5vc/cli.py`、`src/v5vc/horizon_policy_shadow.py` 与最新实验配置。
285. 已完成: 直接复核最新 official quick-screen 与 matched20 shadow 产物，确认当前真实工作状态为:
   - official quick-screen 仍保持 `validation = D71 / default_minimax = D22 / special-e_evt-z_art = D33`
   - matched20 shadow 已收缩到 `D70 family`，当前 `minimax = D72`
   - `D70 / D72 / D73` 属于同一窄盆地，尚未出现脱离该 family 的新 regime

### 当前阶段结论补充
- 当前接班不再依赖“记得最新文档标题”这种弱记忆。
- 已确认应以磁盘产物为准来描述现状:
  - official 问的是 fixed handoff 是否改写
  - matched20 shadow 问的是早期 matched horizon 下哪条新 family 更像 minimax
- 这两个问题当前答案不同，不能混写成一句“最新最好的是谁”。

先说人话:
- 现在项目没有断在代码半改状态，
  也没有断在实验没落盘。
- 真正需要接手的是一个“该往哪条分叉继续”的决策点，
  不是补漏。

### 更新后的下一阶段任务
1. 若目标是继续优化 `D70 family` 本身，
   下一手优先考虑:
   - 更明确的 control-target restoration
   - 不再继续做纯 late teacher source / handoff 小变体
2. 若目标是开始挑战 official fixed handoff，
   应先把候选写成 family:
   - `D70 / D72 / D73`
   再决定是否补 matched long horizon(`200+`)
3. 当前默认建议仍是:
   - 先做 family 级 control restoration 方案筛选
   - 等 family 内部代表点更明确后再上 `200+`

### 文档补充
- `docs/119_round1_1_context_restore_takeover_report.md`
  - 本次上下文恢复、代码与产物核对结果、当前真实状态和下一步分叉建议。
## 2026-03-16 `round1.1 / init-experiment gap-safe numbering fix` 更新
### 当前进度补充
286. 已完成: 修复 `src/v5vc/experiment.py` 中 `build_experiment_id(...)` 的顺序编号缺陷；编号规则从“按当日已有 md 数量 + 1”改为“按当日已存在最大三位序号 + 1”。
287. 已完成: 清理本轮因该缺陷生成的错误 `D74 = EXP-...029` 占位记录，并在修复后重建为唯一编号:
   - `D74 = EXP-...031`
   - `D75 = EXP-...030`

### 当前阶段结论补充
- 当前 `init-experiment` 的主要风险不再只有“并行抢号”。
- 还要额外防:
  - 历史错误记录被删除后留下缺号
  - 导致顺序初始化也重用旧前缀
- 这个问题现在已经在代码层修掉，不再依赖人工数文件。

先说人话:
- 这次不是人手快了并发撞号，
  而是编号算法本身有洞。
- 现在这个洞已经补上了。

### 更新后的下一阶段任务
1. 后续 `init-experiment` 仍继续顺序执行。
2. 但即使历史目录里有缺号，
   新实验也会自动拿到真正未使用的新序号。

### 文档补充
- `src/v5vc/experiment.py`
  - `build_experiment_id(...)` 改为使用当日最大已存在序号。
## 2026-03-16 `round1.1 / D74+D75 / D70 control-target restoration follow-up` 更新
### 当前进度补充
288. 已完成: 新增两份 `D70 family` control-target restoration 配置:
   - `offline_mvp_train_d74_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_late_d33step10_teacher_restore_20step_smallscale_seeded_shuffle.json`
   - `offline_mvp_train_d75_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_20step_smallscale_seeded_shuffle.json`
289. 已完成: `D74 / D75` 顺序初始化实验、跑通 dry-run、正式训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
290. 已完成: 将 `D74 / D75` 并入 official quick-screen route-analysis / selector / final comparison / route recap，以及 matched20 shadow bundle。

### 当前阶段结论补充
- `D74 = 2.401255 / 0.168125 / 2.955904 / 0.368817`
- `D75 = 2.399272 / 0.16719 / 2.960501 / 0.365693`
- `D74` 说明:
  - late `D33 step10 teacher` 在 singleton strict gate 上确实能接入
  - 会把 `z_art` 再往上推一点
  - 但 validation tax 比 `D70 / D72 / D73` 更明显，不是新 winner
- `D75` 说明:
  - 在 `D72` 的 `D22 late` 路线上，仅把 late `fused_hidden_weight` 从 `0.05` 提到 `0.08`
  - 就能得到:
    - 几乎不变的 validation
    - 更好的 special
    - 更好的 `e_evt`
    - 略更好的 `z_art`
- official quick-screen 继续不变:
  - validation = `D71`
  - minimax = `D22`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
- matched20 shadow 则从上一轮的 `D72`，切到:
  - `minimax = D75`
  - `budget_to_minimax_anchor = 0.059075`
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D75`

先说人话:
- `D74` 证明“换成更强 control teacher”这招不是完全没料，
  但代价偏大。
- 真正更像新代表点的是 `D75`:
  - 它不是大胜，
  - 但第一次把这整个窄盆地里的代表点，较清楚地推到了一个新单点上。

### 更新后的下一阶段任务
1. official fixed handoff / stage-report 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 暂停继续做:
   - `D70 family` 内更多 late teacher source / fused-hidden 小幅 sweep
3. 当前更值得优先推进的是:
   - 把 `D75` 作为 `D70 family` 的当前代表点
   - 准备 matched long horizon(`200+`) 验证
4. 若继续挑战 official fixed handoff，
   现在更合理的表述是:
   - family 已基本收缩到 `D75`
   - 而不是仍停留在 `D70 / D72 / D73` 三点并列

### 文档补充
- `docs/120_round1_1_d74_d75_control_target_restoration_report.md`
  - `D74 / D75` 的正式实验链路、结果，以及为何当前应把 `D75` 视为 `D70 family` 的新 shadow 代表点。
## 2026-03-16 `round1.1 / D76 / D75 family matched long horizon probe` 更新
### 当前进度补充
291. 已完成: 新增 `D76` 长视野配置:
   - `offline_mvp_train_d76_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_fusedhidden_boost_200step_smallscale_seeded_shuffle.json`
292. 已完成: `D76 = EXP-20260316-032-...` 顺序初始化、跑通 dry-run、正式 `200 step` 训练、final ablation、final special_eval、checkpoint_series、special_eval_series。
293. 已完成: 将 `D76` 并入纯 `200-step` 同 horizon route-analysis / selector / final comparison / route recap，与 `D22 / D33 / D59` 做正式长视野比较。

### 当前阶段结论补充
- `D76 step200 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- `D76` 长窗轨迹:
  - `step50 = 2.307368 / 0.196444 / 2.548418 / 0.299145`
  - `step100 = 2.220376 / 0.21171 / 2.36021 / 0.436968`
  - `step150 = 2.145159 / 0.235288 / 2.062923 / 0.44088`
  - `step200 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- 纯 `200-step` 同 horizon route 现已变成:
  - validation = `D76`
  - minimax = `D76`
  - special = `D22`
  - `zero_e_evt / zero_z_art = D33`
  - `budget_to_minimax_anchor = 0.0`

先说人话:
- `D75 family` 拉长到 `200 step` 以后没有塌掉。
- 但它也没有保住 quick-screen 里的“special 更好”形状，
  而是和旧长窗 probe 一样继续往 validation-first 滑。
- 区别在于:
  - 这次它滑到的终点更强，
  - 已经足够把纯 `200-step` 的 minimax 也接过去。

### 更新后的下一阶段任务
1. official fixed handoff 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
2. 但 family 级 shadow 口径现在可以更明确地写成:
   - matched20 representative = `D75`
   - matched long-horizon representative = `D76`
3. 若下一步要继续追问“是否足以挑战 official”，
   更高信息量的动作应是:
   - `D76` checkpoint-selected late-stop 复核
   - 或与 official anchor 的 matched-horizon 对照
4. 不要把:
   - `D76 step200 = pure long-horizon minimax`
   直接翻译成:
   - official default 立刻刷新

### 文档补充
- `docs/121_round1_1_d76_matched_long_horizon_probe_report.md`
  - `D76` 的最小长视野外推、同 horizon route 结论，以及为何它当前只能被表述为 long-horizon 代表点，而不是直接替代 official handoff。
## 2026-03-16 `round1.1 / D76 checkpoint-selected late stop review` 更新
### 当前进度补充
294. 已完成: 对 `D76` 单独运行 checkpoint-selection / gate replay，并把 `late_step_ratio` 从默认 `0.8` 调整为 `0.75`，使 `step150 / step200` 都进入 late window。
295. 已完成: 对 `D22 / D33 / D59 / D76` 运行联合 long-horizon checkpoint-selection / gate replay，确认 `step150 -> step200` 的 tradeoff 是否为 `D76` 独有。
296. 已完成: 物化 `D76 step150` synthetic anchor，并重新跑 pure long-horizon route-analysis / selector / comparison / recap，检查它是否能成为正式 route anchor。

### 当前阶段结论补充
- 单看 `D76`:
  - `step150` 是真实 late-stop 候选
  - 相对 `step200`:
    - validation `+0.037223`
    - special `-0.011267`
    - `e_evt` `+0.125157`
    - `z_art` `+0.016229`
- 但联合 long-horizon gate replay 说明:
  - 这种 `step150` 改善不是 `D76` 独有
  - 更像所有 `200-step` 轨迹共有的 late tradeoff
- 更关键的是:
  - 一旦把 `D76 step150` 作为正式 synthetic anchor 并入 pure long-horizon route
  - minimax 会从 `D76 step200` 切回 `D33 step200`

先说人话:
- `D76 step150` 确实更像“好看的 late stop”，
  但它不够强到成为新的默认点。
- 真把它放进正式选路，
  反而会把 long-horizon minimax 重新推回 `D33`。

### 更新后的下一阶段任务
1. 当前 long-horizon 应分成两种口径:
   - `D76 step200 = validation-first default`
   - `D76 step150 = special-oriented late stop option`
2. 暂不把 `D76 step150` 升格成新的默认 anchor。
3. 若后续继续推进，
   更高信息量的方向应是:
   - 明确把“checkpoint-anchor 是否允许进入正式 route”当成制度问题单独处理
   - 而不是继续只在 `D76` 内部做更细的 late-step sweep

### 文档补充
- `docs/122_round1_1_d76_checkpoint_selected_late_stop_review.md`
  - `D76 step150` 为何是有效 late-stop 候选，但不能直接作为新的 long-horizon default。
## 2026-03-16 `round1.1 / checkpoint anchor route governance` 更新
### 当前进度补充
297. 已完成: 汇总当前三类 route 口径的真实磁盘状态:
   - official quick-screen
   - pure long-horizon final-only
   - long-horizon + synthetic checkpoint-anchor
298. 已完成: 把 `D22 step20 anchor` 与 `D76 step150 anchor` 的制度角色拆开，明确前者属于 horizon equalization，后者属于 checkpoint-option。
299. 已完成: 形成新的 route-governance 建议，限定 synthetic checkpoint anchor 的默认使用边界。

### 当前阶段结论补充
- synthetic checkpoint anchor 现在不能再被笼统写成“可用于 route”
- 必须分成两类:
  - horizon-equalization anchor
  - checkpoint-option anchor
- 当前默认制度应是:
  - official / handoff / stage-report 只允许 natural final anchors
  - matched-horizon shadow 允许 horizon-equalization anchor
  - checkpoint-option anchor 只保留给 diagnostic / option study，不默认进入正式 route

先说人话:
- `D22 step20` 和 `D76 step150` 虽然都叫 checkpoint anchor，
  但不是一回事。
- 前者是在补公平比较条件，
  后者是在往制度里新增“可选 checkpoint”这一整类候选。
- 这两种东西如果不分开，
  route 语义会越来越乱。

### 更新后的下一阶段任务
1. 当前默认继续保持:
   - official = final-only quick-screen
   - matched20 shadow = 可用 horizon-equalization anchor
   - long-horizon default = final-only
2. 若后续还要推进 checkpoint-option，
   应先单独定义:
   - 是否允许一个实验提供多个正式 route 候选
   - 以及对应的 validation / control floors
3. 在未立这套制度之前，
   不再把 `step150` 这类 synthetic late-stop anchor 直接并入默认 route 讨论

### 文档补充
- `docs/123_round1_1_checkpoint_anchor_route_governance_report.md`
  - synthetic checkpoint anchor 何时可用于 shadow，何时不能默认进入正式 route。
## 2026-03-16 `round1.1 / handoff-stage-report governance integration` 更新
### 当前进度补充
300. 已完成: 为 route handoff / fixed handoff document / stage report 新增统一的 governance 分类逻辑，自动区分:
   - `natural_final_anchor`
   - `horizon_equalization_anchor`
   - `checkpoint_option_anchor`
301. 已完成: 更新 handoff/stage-report 模板与 payload，使 `route_governance_summary / guardrail`、current anchor governance、alternative governance 都会显式渲染。
302. 已完成: 用两组真实产物回放验证:
   - `D76 step150` long-horizon checkpoint-option 场景
   - `D22 step20` matched20 horizon-equalization 场景

### 当前阶段结论补充
- `docs/123` 里的制度边界现在不再只存在于人工说明，
  而是已经进入生成链路:
  - handoff json
  - handoff document
  - stage report
- 当前模板会自动提示:
  - formal default 是否仍是 natural final anchor
  - synthetic alternative 是 shadow-only 还是 option-only
- 这意味着后续再生成 handoff / stage-report 时，
  不容易再把:
  - `D22 step20`
  - `D76 step150`
  混写成同一种“可直接接班的默认 anchor”

先说人话:
- 之前制度结论已经有了，
  但模板不会说人话，
  所以人工汇报时还是容易写乱。
- 这轮做的就是把“哪些能进正式口径、哪些只能当 shadow/option”
  直接焊进产物生成器。

### 更新后的下一阶段任务
1. 后续 handoff / stage-report 默认沿用这套治理增强后的生成链路。
2. 若未来要让 checkpoint-option anchor 真进入正式 route，
   优先改 governance 规则本身，
   不要绕过模板人工口头升级。
3. 当前更高信息量的下一步，
   应重新回到 route policy / anchor family 本身，
   而不是继续在 handoff 文案层做局部修饰。

### 文档补充
- `docs/124_round1_1_handoff_stage_report_governance_integration_report.md`
  - route governance 如何被接入 handoff/stage-report 生成器，以及两组真实回放验证结果。
## 2026-03-16 `public repo bootstrap and index boundary` 更新
### 当前进度补充
303. 已完成: 在项目根目录初始化 Git 仓库，默认分支为 `main`，并将 `origin` 指向:
   - `https://github.com/lhy6305/artifuse-voice-conversion.git`
304. 已完成: 新增建仓基础文件:
   - `.gitignore`
   - `LICENSE`
   - `README.md`
   - `NOTICE`
305. 已完成: 在用户修改 `.gitignore` 并放置根目录敏感文件后，仅检查 Git 状态，确认该文件:
   - 已被忽略
   - 未进入索引
   - 未进入任何提交历史

### 当前阶段结论补充
- 当前项目已经具备公开备份仓的基础边界:
  - 公开代码 / 方案 / 评估 / 中间模型
  - 排除原始音频 / 分段音频 / 代理音频 / 本地运行环境
- 当前根目录敏感文件没有进入可上传范围
- 当前仓库仍无提交历史，
  所以这次核验结果是干净的起点状态

先说人话:
- 这轮不是改实验，
  是把“什么能公开、什么不能公开”先焊进仓库。
- 现在仓库层面的默认行为已经是:
  - 音频不上库
  - 敏感文件不上索引
  - 代码和阶段产物可以继续积累

### 更新后的下一阶段任务
1. 后续做首次提交前，
   继续沿用:
   - `git status --short --ignored`
   - `git ls-files`
   这套最小索引核验。
2. 若后续再新增本地敏感文件或音频目录，
   先补 `.gitignore`，再做索引检查。
3. 实验主线可继续独立推进；
   公开仓边界当前已足够稳定，
   不需要再为此单独中断实验工作流。

### 文档补充
- `docs/125_public_repo_bootstrap_and_index_boundary_report.md`
  - 公开仓库初始化、忽略边界，以及敏感文件未进入索引/历史的检查结果。
## 2026-03-16 `round1.1 / D77 official validation-family matched long horizon probe` 更新
### 当前进度补充
306. 已完成: 新建 `D77` 配置，作为 `D71` 的最小 `200-step` 外推，不新增新 supervision principle，只拉长 horizon。
307. 已完成: 跑通 `D77` 的整条链路:
   - `init-experiment`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
308. 已完成: 将 `D77` 并入 pure long-horizon comparison / selector / recap，直接复核它是否足以挑战 `D76`。

### 当前阶段结论补充
- `D77` 现在可以被写成:
  - official validation-family 的 matched long-horizon representative
- 但 pure `200-step` route 仍保持:
  - validation = `D76`
  - minimax = `D76`
  - special = `D22`
  - `zero_e_evt / zero_z_art = D33`
- `D77 vs D76` 的真实差值是:
  - validation `+0.002133`
  - special `-0.001276`
  - `e_evt` `-0.104983`
  - `z_art` `+0.040775`

先说人话:
- `D77` 证明 official validation 这条线拉到 `200-step` 以后并不会塌。
- 但它也没强到把 `D76` 从 long-horizon 默认位子上赶下来。
- 目前更准确的是:
  - `D77` 很像 official validation-family 在长窗里的代表点
  - `D76` 仍是 pure long-horizon 的默认点

### 更新后的下一阶段任务
1. 不再继续扩 `D29-init` 同 family 的长窗小修小补。
2. 若继续推进，
   更高信息量的问题应改成:
   - 是否存在 `D76` 近邻，
     能在不丢 validation 的前提下补回 `e_evt / z_art`
3. official / matched20 / pure long-horizon 三条口径继续分开写，
   不把 `D77` 直接混写成新的 official default。

### 文档补充
- `docs/126_round1_1_d77_official_validation_family_long_horizon_probe_report.md`
  - `D71` family 拉到 `200-step` 后的真实位置，以及为何它仍不足以替代 `D76`。
## 2026-03-16 `round1.1 / D78 D76 near-neighbor control restore probe` 更新
### 当前进度补充
309. 已完成: 新建 `D78` 配置，作为 `D76` 的单候选近邻，只把 late `step11-200` teacher source 从 `D22 step30` 切到 `D33 step10`，保留 `fused_hidden_weight=0.08` 与现有 sampler。
310. 已完成: 跑通 `D78` 的整条链路:
   - `init-experiment`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
311. 已完成: 将 `D78` 并入 pure long-horizon comparison / selector / recap，直接判断它是不是可接受的 `D76` control-restore 近邻。

### 当前阶段结论补充
- `D78 = 2.141317 / 0.232356 / 1.822031 / 0.51471`
- `D78 vs D76` 的真实差值是:
  - validation `+0.033381`
  - special `-0.014199`
  - `e_evt` `-0.115735`
  - `z_art` `+0.090059`
- 这说明:
  - `D78` 确实补回了 `special / z_art`
  - 但 validation 税已经不再是“近乎免费”
  - `e_evt` 也没有补回来
- 当把 `D78` 并入 pure `200-step` route 后，
  route 会改写成:
  - validation = `D76`
  - special = `D78`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D33`

先说人话:
- `D78` 不是 `D76` 的无痛升级版。
- 它回答出的真正信息是:
  - `late D33 teacher restore` 在长窗里确实有力，
    但这股力会把 route 重新拉回 `D33`
- 所以当前不该继续沿这个方向做同向小修小补。

### 更新后的下一阶段任务
1. 暂停继续扩:
   - `late D33 teacher restore`
   - 或其同向小变体
2. 如果继续找 `D76` 近邻，
   优先限制在:
   - 不改 late teacher source
   - 只在现有 `D22 late` 骨架内做更弱的 control-target restoration
3. 后续若再出现“局部 special/control 变好”的近邻，
   必须先并入 full long-horizon route，
   再判断它是不是更好的 default/minimax 候选。

### 文档补充
- `docs/127_round1_1_d78_d76_near_neighbor_control_restore_probe_report.md`
  - `D76` 近邻 `D78` 的真实 tradeoff，以及为什么它会把 pure long-horizon minimax 切回 `D33`。
## 2026-03-16 `round1.1 / D79 D76 near-neighbor teacher-weight probe` 更新
### 当前进度补充
312. 已完成: 新建 `D79` 配置，完整继承 `D76`，唯一改动为 late `step11-200` 的 `teacher_consistency.weight: 0.15 -> 0.20`。
313. 已完成: 跑通 `D79` 的整条链路:
   - `init-experiment`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
314. 已完成: 将 `D79` 并入包含 `D78` 在内的 full long-horizon route，复核它到底是 new default 候选，还是更清晰的 special/e_evt 近邻。

### 当前阶段结论补充
- `D79 = 2.138406 / 0.231994 / 2.170294 / 0.469429`
- `D79 vs D76` 的真实差值是:
  - validation `+0.03047`
  - special `-0.014561`
  - `e_evt` `+0.232528`
  - `z_art` `+0.044778`
- full long-horizon route 现在更准确的结构是:
  - validation = `D76`
  - special = `D79`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`
- 这说明:
  - `D79` 比 `D78` 更像可继续挖的近邻
  - 但 pure long-horizon default/minimax 仍没有从 `D33` 切走

先说人话:
- `D79` 把问题继续缩窄了。
- 现在几乎可以确认:
  - 在 `D22 late` 骨架里，
    teacher weight lift 能补回 `special + e_evt`
  - 真正还卡住升级的主要缺口，
    已经变成 `z_art`

### 更新后的下一阶段任务
1. 不再继续扩:
   - `D33 late source restore`
2. 若继续推进，
   更高信息量的问题应改成:
   - 能否在保留 `D79` 的 `special + e_evt` 收益下，
     再补一点 `z_art`
3. 下一轮更值得试的是:
   - 仍保留 `D22 late`
   - 仍保留 teacher weight lift
   - 再做更轻量的 `z_art` 定向 restoration

### 文档补充
- `docs/128_round1_1_d79_d76_near_neighbor_teacherweight_probe_report.md`
  - `D79` 的真实位置，以及为什么它把问题进一步缩窄到 `z_art` 缺口。
## 2026-03-16 `round1.1 / D80 D79 z_art-weight probe` 更新
### 当前进度补充
315. 已完成: 新建 `D80` 配置，完整继承 `D79`，唯一改动为 late `step11-200` 的 `teacher_consistency.z_art_weight: 1.0 -> 1.25`。
316. 已完成: 跑通 `D80` 的整条链路:
   - `init-experiment`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
317. 已完成: 将 `D80` 并入 full long-horizon route，正式验证它是否能在 `D79` 基础上补回 `z_art`。

### 当前阶段结论补充
- `D80 = 2.140498 / 0.233658 / 2.130963 / 0.441535`
- `D80 vs D79` 的真实差值是:
  - validation `+0.002092`
  - special `+0.001664`
  - `e_evt` `-0.039331`
  - `z_art` `-0.027894`
- 也就是说:
  - `D80` 没有补回 `z_art`
  - 反而轻微回吐了 `D79` 的现有收益
- full route 结果完全不变:
  - validation = `D76`
  - special = `D79`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`

先说人话:
- 这轮是明确负结果。
- 它把一个容易继续误扫的方向排干净了:
  - 当前缺口不是“再给 `D79` 多一点 `z_art_weight` 就能补齐”

### 更新后的下一阶段任务
1. 停止继续扩:
   - `late z_art_weight` 小幅调节
2. 若继续沿 `D79` 主线推进，
   更值得试的问题应改成:
   - 是否存在非 teacher-per-head 权重类的 `z_art` restoration 机制
3. 当前主线可写成:
   - `D79` 保留为 `special + e_evt` leader
   - `D80` 作为被 `D79` 完整支配的负结果收档

### 文档补充
- `docs/129_round1_1_d80_d79_zart_weight_probe_report.md`
  - `D80` 的负结果，以及为什么 `late z_art_weight` 不应继续作为当前主线优先轴。
## 2026-03-16 `round1.1 / D81 D79 z_art-influence retarget probe` 更新
### 当前进度补充
318. 已完成: 新建 `D81` 配置，完整继承 `D79`，只把 `z_art_influence_aux` 从 `challenge_proxy_core` retarget 到 late `micro_pause_none_singleton_strict` pool，并将其 weight schedule 改成 `step11-25` late ramp。
319. 已完成: 跑通 `D81` 的整条链路:
   - `init-experiment`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
320. 已完成: 将 `D81` 并入 full long-horizon route，正式验证“late-pool `z_art_influence` retarget”是否会改变当前 `D76 / D79 / D33` 三角结构。

### 当前阶段结论补充
- `D81 = 2.137537 / 0.235312 / 2.00519 / 0.422542`
- `D81 vs D79` 的真实差值是:
  - validation `-0.000869`
  - special `+0.003318`
  - `e_evt` `-0.165104`
  - `z_art` `-0.046887`
- 也就是说:
  - `D81` 只换来极小 validation 改善
  - 但同时回吐了 `special / e_evt / z_art`
- 更关键的是:
  - `loss_z_art_influence_aux` 在 late 日志里持续非零，
    说明这不是“配置挂空”
- full route 结果仍完全不变:
  - validation = `D76`
  - special = `D79`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`

先说人话:
- 这轮把“把 explicit `z_art` influence 直接转到当前 late micro-pause pool”这条猜想也排干净了。
- 问题不是:
  - 之前 `z_art_influence_aux` 只是 pool 没对准
- 更像是:
  - 当前 `D79` 的剩余 `z_art` 缺口，不是靠这条机制的 late retarget 就能补齐

### 更新后的下一阶段任务
1. 停止继续扩:
   - `z_art_influence_aux` 的 late-pool retarget
   - 或其 coverage 近邻 sweep
2. `D79` 继续保留为当前 long-horizon 的 `special + e_evt` leader。
3. 若继续追 `z_art`，更高信息量的问题应改成:
   - 是否存在比 `teacher_consistency` 与 `z_art_influence_aux` 都更外层的 `z_art` restoration 机制

### 文档补充
- `docs/130_round1_1_d81_d79_zart_influence_retarget_probe_report.md`
  - `D81` 的负结果，以及为什么即使机制命中 late pool，`z_art_influence` retarget 仍不足以改写当前 long-horizon 结构。
## 2026-03-16 `round1.1 / 上下文恢复与接班状态确认` 更新
### 当前进度补充
321. 已完成: 按 `UTF-8` 显式读取 `docs/00_context_bootstrap.md`，并补读 `docs/01_project_overview_and_plan.md`、`docs/02_pitfalls_log.md`、`initial_design.md`、`initial_design_judg.md` 的当前阶段约束与结论。
322. 已完成: 核对 `D79 / D80 / D81` 的配置差异、`manage.py` 与 `src/v5vc/cli.py` 训练评估入口，以及 shared `reports/training/offline_mvp/`、`reports/eval/offline_mvp_*` 下的训练日志、final eval、checkpoint series、route-analysis / selector / comparison / recap 产物。
323. 已完成: 确认当前工作区 `git status --short` 为空，最近主线已完整落盘到 `docs/128`、`docs/129`、`docs/130` 与对应产物目录，不存在“只写文档未跑产物”的断层。

### 当前阶段结论补充
- 当前 long-horizon 三角结构已经稳定:
  - `D76 = validation-first representative`
  - `D79 = special + e_evt leader`
  - `D33 = default_minimax + z_art anchor`
- `D80` 与 `D81` 都是明确负结果，且已经把两条低信息量近邻轴排干净:
  - `late teacher_consistency.z_art_weight` 小幅调节
  - `z_art_influence_aux` 的 late-pool retarget / coverage 近邻 sweep
- 当前 selector 真实状态已核对:
  - full long-horizon `default_minimax`
  - 仍选 `D33`
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.03047`
  - `best_e_evt_floor = D79`
  - `best_z_art_floor = D33`

先说人话:
- 现在不是“仓库里还有一条没核实完的旧线”，而是上一轮已经把 `D79` 周边两条最像样的 `z_art` 补法都验证过了，而且都失败了。
- 真正还没回答的问题，已经收束成:
  - 是否存在比 `teacher_consistency` 和 `z_art_influence_aux` 更外层的 `z_art` restoration 机制

### 更新后的下一阶段任务
1. 继续保留当前主线口径:
   - `D79` 作为 long-horizon 的 `special + e_evt` leader
   - `D33` 作为当前 `default_minimax + z_art` anchor
2. 不再继续扩:
   - `late z_art_weight` 微调
   - `z_art_influence_aux` late-pool retarget
   - 这两条轴的 coverage 近邻 sweep
3. 若接着推进实验，下一轮应直接改问:
   - 是否存在更外层的 `z_art` restoration 机制
   - 且该机制不依赖把 late teacher source 切回 `D33`

### 文档补充
- 本段用于说明本次上下文恢复后核对到的真实仓库状态，避免后续把 `D79-D81` 误判成“只写了报告、没有完整训练与评估产物”。
## 2026-03-16 `round1.1 / D82 D79 full-priority singleton exposure probe` 更新
### 当前进度补充
324. 已完成: 新建 `D82` 配置，完整继承 `D79`，唯一改动为 late `step11-200 targeted_sampling.priority_ratio: 0.75 -> 1.0`。
325. 已完成: 跑通 `D82` 的整条链路:
   - `init-experiment --route-selection`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
326. 已完成: 将 `D82` 并入 full long-horizon route，正式验证“强化当前 singleton proxy cohort 的 late exposure”是否会补回 `z_art`。

### 当前阶段结论补充
- `D82 = 2.148904 / 0.218229 / 2.126457 / 0.436209`
- `D82 vs D79` 的真实差值是:
  - validation `+0.010498`
  - special `-0.013765`
  - `e_evt` `-0.043837`
  - `z_art` `-0.03322`
- 也就是说:
  - `D82` 确实把 special 再往前推了一段
  - 但没有补回 `z_art`
  - 同时还回吐了 validation 与 `e_evt`
- full route 结果更新为:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`
- selector 仍保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D33`
- 新阈值变为:
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.040968`
  - `best_e_evt_floor = D79`
  - `best_z_art_floor = D33`

先说人话:
- 这轮说明“把当前 singleton proxy cohort 曝光再拉满”确实是个 special 杠杆，
  但它不是 `z_art` 补法。
- 问题不是当前 late batch 还不够偏，
  而是这条 cohort / proxy principle 本身更像在往 special-only 方向继续推。

### 更新后的下一阶段任务
1. 停止继续扩:
   - late singleton `priority_ratio` 上调
   - 或 full-priority / stronger-exposure 近邻 sweep
2. 当前主线口径更新为:
   - `D76 = validation`
   - `D82 = special`
   - `D79 = e_evt`
   - `D33 = default_minimax + z_art`
3. 若继续追 `z_art`，更高信息量的问题应改成:
   - 是否需要一个比“强化当前 singleton cohort 曝光”更换代价更大的新 proxy principle
   - 或一个真正直接面向 `z_art` 的更外层 supervision 机制

### 文档补充
- `docs/131_round1_1_d82_d79_fullpriority_singleton_exposure_probe_report.md`
  - `D82` 的结果，以及为什么更强 singleton exposure 只能把这条线推成 special leader，仍不足以补回 `z_art`。
## 2026-03-16 `round1.1 / D83 D79 phase-specific late teacher handoff probe` 更新
### 当前进度补充
327. 已完成: 新建 `D83` 配置，完整继承 `D79`，唯一主改动为把 late `teacher_consistency` 从单段 `D22` teacher 改成两段 handoff:
   - `step11-100 = D33 step10 teacher, weight=0.15`
   - `step101-200 = D22 step30 teacher, weight=0.20`
328. 已完成: 跑通 `D83` 的整条链路:
   - `init-experiment --route-selection`
   - `dry-run`
   - `200-step` 训练
   - final `ablation/special_eval`
   - `checkpoint_series`
   - `special_eval_series`
329. 已完成: 将 `D83` 并入 full long-horizon route，正式验证“phase-specific `D33 -> D22` late teacher handoff”是否能把 `D78` 的早段 `z_art` restore 和 `D79` 的收尾稳定性拼成更好的 joint point。

### 当前阶段结论补充
- `D83 = 2.140033 / 0.23583 / 2.011104 / 0.42172`
- `step100 -> step101` 的 effective teacher 已明确切换:
  - `D33 step10 -> D22 step30`
  - `weight 0.15 -> 0.20`
- `D83` 的关键轨迹是:
  - `step100 = 2.256422 / 0.190305 / 2.428461 / 0.530758`
  - `step150 = 2.174416 / 0.221924 / 2.197493 / 0.463976`
  - `step200 = 2.140033 / 0.23583 / 2.011104 / 0.42172`
- 也就是说:
  - handoff 不是没命中
  - 但切回 `D22` 之后，
    `z_art` 会从 `0.530758` 持续掉到 `0.42172`
  - `e_evt` 也从 `2.428461` 掉到 `2.011104`
- `D83 vs D79` 的真实差值是:
  - validation `+0.001627`
  - special `+0.003836`
  - `e_evt` `-0.15919`
  - `z_art` `-0.047709`
- 所以 `D83` 被 `D79` 完整支配，不形成新的 route 角色。
- full route 结果保持不变:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art = D33`
  - minimax = `D33`
- selector 继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D33`
  - `budget_to_minimax_anchor = 0.014763`
  - `budget_to_special_anchor = 0.040968`

先说人话:
- 这轮把“先用 `D33` 抬 `z_art`，再切回 `D22` 收尾”这条想法也排干净了。
- 问题不是 handoff 没接上，
  而是这条收尾会把前半段积累的大部分 control 重新洗掉。

### 更新后的下一阶段任务
1. 停止继续扩:
   - `D33 -> D22` late teacher handoff
   - 或其 handoff step 小幅前后平移
2. 当前主线继续保持:
   - `D76 = validation`
   - `D82 = special`
   - `D79 = e_evt`
   - `D33 = default_minimax + z_art`
3. 若继续追 `z_art`，更高信息量的问题应改成:
   - 是否存在不依赖 `late teacher source handoff` 的更外层 `z_art` restoration 机制

### 文档补充
- `docs/132_round1_1_d83_d79_phase_late_teacher_handoff_probe_report.md`
  - `D83` 的结果，以及为什么 long-horizon 的 `D33 -> D22` late handoff 会被 `D79` 完整支配。
## 2026-03-16 `round1.1 / context restore continuation` 更新
### 当前进度补充
330. 已完成: 按 `docs/00_context_bootstrap.md` 规定重新用 UTF-8 显式读取恢复入口、总览、踩坑和设计文档，并补读 `docs/126` 到 `docs/132` 的最新 long-horizon 实验链。
331. 已完成: 重新核对关键代码入口与治理模块:
   - `manage.py`
   - `src/v5vc/cli.py`
   - `src/v5vc/horizon_policy_shadow.py`
   - `src/v5vc/route_governance.py`
   - `src/v5vc/handoff_summary.py`
   - `src/v5vc/stage_report.py`
   - `src/v5vc/experiment.py`
332. 已完成: 直接复核当前正式产物口径:
   - official quick-screen 仍是 `D71 / D22 / D33`
   - matched20 shadow 仍是 `D71 / D72` 这一窄 family
   - full long-horizon route 已更新到 `D83`
333. 已完成: 从最新 route json 再次确认当前 long-horizon 四角色:
   - validation = `D76`
   - special = `D82`
   - `e_evt` = `D79`
   - default_minimax + `z_art` = `D33`

### 当前阶段结论补充
- 当前仓库已不处于“上下文丢失、只能靠猜”的状态。
- 接班后可以直接复用的能力已经落地:
  - matched-horizon shadow bundle
  - route selection / recap
  - handoff governance 分类
  - fixed handoff document / stage report 模板化输出
- 当前真正未决的，不是:
  - official quick-screen 要不要切 anchor
  - matched20 shadow 要不要继续改模板
  - `D33 -> D22` handoff 是否再扫一圈
- 当前真正未决的是:
  - 若还要继续追 long-horizon 的 `z_art` 缺口，
    应该进入哪一类“更外层 supervision / proxy principle”问题，
    而不是继续拧 late teacher source / weight / current singleton exposure 这组已基本排干净的近邻轴。

先说人话:
- 现在磁盘上的事实已经够清楚了。
- 不是接着把旧旋钮再拧细一点，
  而是该换题目了。
- 目前最像“下一轮真有信息量”的方向，
  是找一个不靠 late teacher source handoff 的新 `z_art` 补法。

### 更新后的下一阶段任务
1. 继续把当前主线口径固定为:
   - official quick-screen = `D71 / D22 / D33`
   - matched20 shadow family = `D70 / D72 / D73`
   - full long-horizon = `D76 / D82 / D79 / D33`
2. 若下一步继续训练实验，优先从“更外层 `z_art` restoration 机制”立题，
   不再优先扩:
   - `late teacher source handoff`
   - `late z_art_weight`
   - `late z_art_influence retarget`
   - `full-priority singleton exposure`
3. 若下一步需要生成阶段汇报或交接文档，默认走:
   - `build-offline-mvp-route-handoff`
   - `materialize-offline-mvp-route-handoff-doc`
   - `materialize-offline-mvp-stage-report`
   并保留 governance guardrail。
4. 若下一步要初始化新实验，继续顺序执行 `init-experiment`，
   且评估命令对非模板实验必须显式传对应 `--config`。

### 文档补充
- `docs/133_round1_1_context_restore_continuation_report.md`
  - 本次接班恢复实际读取范围、代码核对结果、当前三条口径状态和下一步建议。
## 2026-03-16 `round1.1 / stage progress + route assessment` 更新
### 当前阶段结论补充
- 从旧三锚 `D22 / D29 / D33` 到当前 `D80+`，
  已经取得阶段性进展，
  但进展主要体现为:
  - route 结构更清晰
  - validation frontier 前移
  - `e_evt` / special 角色拆分得更明确
  - 而不是已经出现新的单点总冠军
- 当前 long-horizon 更准确的正式口径仍是:
  - `D76 = validation`
  - `D82 = special`
  - `D79 = e_evt`
  - `D33 = default_minimax + z_art`
- 当前总路线仍正确，
  但战术上应停止继续优先扩:
  - late teacher source handoff
  - late `z_art_weight`
  - late `z_art_influence` retarget
  - stronger singleton exposure
- 下一步应转向:
  - 更外层的 `z_art` restoration / supervision 机制
  - 且继续遵守 quick-screen -> matched -> long-horizon 的验证顺序

先说人话:
- 现在已经不是“有没有进展”的问题，
  而是“进展体现在路线收口，不体现在单点封王”。
- 所以下一步该换题，
  不该继续围着 `D80-D83` 这组旧旋钮打转。

### 更新后的下一阶段任务
1. 保持当前三条口径分开:
   - official quick-screen
   - matched20 shadow
   - full long-horizon
2. 停止继续优先扩 `D80-D83` 同类近邻轴。
3. 设计一轮新的 quick-screen probe，
   重点验证:
   - 更外层 `z_art` supervision / restoration 机制
   - 以及比当前 `micro_pause_none_singleton_strict` 更对路的新 cohort 定义
4. 只有 quick-screen 出现明确信号后，
   再继续补 matched / `200-step` 长窗验证。

### 文档补充
- `docs/134_round1_1_stage_progress_route_assessment_report.md`
  - 从旧三锚到 `D80+` 的阶段性进展评估、当前路线判断和下一步建议。
## 2026-03-16 `round1.1 / D84 outer punctuation quick-screen` 更新
330. 已完成: 扩展 `target_special_supervision` 正式 sidecar，新增:
   - `micro_singleton_anypunct_relaxed = 13`
   - `micro_singleton_anypunct_expansion = 5`
   并重跑:
   - `analyze-round1-target-special-supervision`
   - `analyze-offline-mvp-special-slice-alignment`
331. 已完成: 修正 `punctuation_profile_aux`，使其真实消费 `target_special_supervision` sidecar，并支持按 `pool_memberships` 做样本 gate，而不是只看文本标点比例。
332. 已完成: 新增 `D84` quick-screen 配置:
   - `configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json`
333. 已完成: 顺序初始化:
   - `EXP-20260316-040`
   并跑通:
   - `train-offline-mvp --dry-run`
334. 当前 `D84` dry-run 已确认:
   - late `teacher_consistency.weight = 0.20`
   - late primary sampling 仍是 `micro_pause_none_singleton_strict`
   - 但新增 `secondary_sampling(max_slots=1)` 指向 `micro_singleton_anypunct_expansion`
   - `punctuation_profile_aux` 也已真实挂到该 outer pool

先说人话:
- 这轮已经不是旧 `punctuation_profile_aux` 的重跑。
- 我们先把“strict sparse 内层样本”和“outer punctuation 外层样本”拆开了，
  再把 gate 补到 loss 里，
  这样 `D84` 才真的在问一个新问题。

### 当前阶段结论补充
- `micro_singleton_anypunct_relaxed` 虽然更接近想要的 outer cohort，
  但它包含 strict singleton 本身，
  不能直接拿来做外层 supervision pool。
- 因此本轮正式采用的是差分 outer pool:
  - `micro_singleton_anypunct_expansion`
- 当前 `D84` 只是设计与 dry-run ready，
  还没有正式 quick-screen 结果，
  所以 route 结论暂不变化:
  - official quick-screen = `D71 / D22 / D33`
  - full long-horizon = `D76 / D82 / D79 / D33`

### 更新后的下一阶段任务
1. 正式运行 `D84` quick-screen 训练。
2. 完成配套:
   - final `ablation_eval`
   - final `special_eval`
   - checkpoint series
   - special eval series
3. 若 `D84` 出现新形状，
   再补 matched / long-horizon；
   若没有，
   则把“outer punctuation restoration”也视为已基本排干净的一条题。

### 文档补充
- `docs/135_round1_1_d84_outer_punctuation_quickscreen_design_report.md`
  - `D84` 的 sidecar 扩展、loss gate 修正、配置设计与 dry-run 状态。
## 2026-03-16 `round1.1 / D84 outer punctuation quick-screen` 正式结果更新
335. 已完成: 运行 `D84 = EXP-20260316-040` 正式 quick-screen 训练，并补齐:
   - final `ablation_eval`
   - final `special_eval`
   - `checkpoint_series(step10/20)`
   - `special_eval_series(step10/20)`
336. 已完成: 读取训练日志确认本轮新机制真实生效，而不是假 gate:
   - `step12 loss_punctuation_profile_aux = 0.009319`
   - `step15 loss_punctuation_profile_aux = 0.003821`
   - `step20 loss_punctuation_profile_aux = 0.008741`
   - late effective config 持续包含:
     - `secondary_sampling -> micro_singleton_anypunct_expansion`
     - `punctuation_profile_aux.pool_memberships = ['micro_singleton_anypunct_expansion']`
337. 已完成: 将 `D84` 正式并入:
   - official quick-screen route-analysis / selector / final comparison / recap
   - matched20 shadow bundle

### 当前阶段结论补充
- `D84 final = 2.417702 / 0.156619 / 3.089381 / 0.381618`
- 指标顺序固定为:
  - `target_validation / special_delta / zero_e_evt / zero_z_art`
- `D84 vs D75` 的真实差值是:
  - validation `+0.007910`
  - special `-0.010571`
  - `zero_e_evt` `+0.128880`
  - `zero_z_art` `+0.015925`

- 也就是说:
  - 这轮不是没打中新机制
  - 它确实比 `D75` 更像一个新的 matched20-level joint point
  - 但它还不够强到改写 official quick-screen 的正式制度角色

- official quick-screen 并入 `D84` 后仍保持:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D22`
  - `budget_to_minimax_anchor = 0.103997`
  - `budget_to_special_anchor = 0.183751`

- matched20 shadow 并入 `D84` 后更新为:
  - validation = `D71`
  - special = `D69`
  - `zero_e_evt / zero_z_art = D33`
  - minimax = `D84`
  - `budget_to_minimax_anchor = 0.066985`
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D84`

先说人话:
- `D84` 没有把 official quick-screen 推翻。
- 但它已经不只是“有点意思的新 quick-screen 点”。
- 当前更准确的写法是:
  - official 继续不变
  - matched20 shadow 代表点从 `D75` 再前推到 `D84`

### 更新后的下一阶段任务
1. 不要把 `D84` 直接混写成新的 official default / minimax。
2. 若继续推进 `D84` 这条题，下一步应进入:
   - matched long-horizon / `200-step` 验证
3. 若 `D84` family 的长窗外推还能站住，
   再讨论它是否只是新的 matched20 shadow 代表点，
   还是有资格继续挑战更高一层路线。

### 文档补充
- `docs/136_round1_1_d84_outer_punctuation_quickscreen_run_report.md`
  - `D84` 的正式训练结果、official / matched20 route 归位，以及当前阶段判断。
## 2026-03-16 `round1.1 / D85 outer punctuation 200-step verification` 更新
338. 已完成: 新增 `D85` 长窗配置:
   - `configs/offline_mvp_train_d85_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_200step_smallscale_seeded_shuffle.json`
   并顺序完成:
   - `init-experiment`
   - `train-offline-mvp --dry-run`
   - `200-step` 正式训练
   - final `ablation_eval`
   - final `special_eval`
   - `checkpoint_series(step50/100/150/200)`
   - `special_eval_series(step50/100/150/200)`
339. 已完成: 修复训练入口 `experiment metrics` 回写路径解析。
   - 现支持:
     - `EXP-...metrics.json`
     - 以及 `EXP-...-slug.metrics.json`
   - 并已用现有 `train_plan` 对 `EXP-20260316-041` 做一次回填，
     使训练状态从卡在 `initialized` 恢复为真实完成状态。
340. 已完成: 将 `D85` 正式并入两层 `200-step` route:
   - minimal family:
     - `D22 / D33 / D59 / D76 / D85`
   - full long-horizon:
     - `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85`

### 当前阶段结论补充
- `D85` 的现有 shorthand final 可记为:
  - `2.129306 / 0.231295 / 2.027351 / 0.433882`
- 对 route 系统来说，本轮用于 selector 的 validation 列为:
  - `2.133474`
- `D85` 的 `200-step` 轨迹为:
  - `step50 = 2.310868 / 0.185493 / 2.582539 / 0.311158`
  - `step100 = 2.213002 / 0.204854 / 2.291469 / 0.448169`
  - `step150 = 2.161399 / 0.223913 / 2.066232 / 0.424634`
  - `step200 = 2.133474 / 0.231295 / 2.027351 / 0.433882`

- 这说明:
  - validation 继续随长窗改善
  - special 继续随长窗变差
  - `e_evt` floor 继续回落
  - 但最终仍保留了比 `D76` 更像 special / `e_evt` tradeoff 点的形状

- `D85 vs D76` 的 route 级差值是:
  - validation `+0.025538`
  - special `-0.015260`
  - `zero_e_evt` `+0.089585`
  - `zero_z_art` `+0.009231`

- 也就是说:
  - `D85` 不是新的 validation 点
  - 但它也不是长窗一拉就完全塌回旧形状
  - 它确实在支付一段 validation tax 的同时，
    把 `special / e_evt / z_art` 维持在比 `D76` 更平衡的位置

- minimal family route(`D22 / D33 / D59 / D76 / D85`) 给出:
  - validation = `D76`
  - special = `D85`
  - `zero_e_evt = D85`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.025538`

- 但并入 full long-horizon route 后，正式四角色仍保持:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.040968`

先说人话:
- `D85` 站住了 `D84 family` 的长窗有效性，
  说明这条 outer punctuation 题不是只在 matched20 才有局部信号。
- 但它还不够强到改写 full long-horizon 的正式角色。
- 更准确的制度写法是:
  - `D85` 成为这条 family 在 pure `200-step` 下的一个可信 special / `e_evt` tradeoff 点
  - full long-horizon 仍旧是 `D76 / D82 / D79 / D33`

### 更新后的下一阶段任务
1. 不要把 minimal family 中的 `D85 = special / e_evt` 误写成 full long-horizon 刷新。
2. 若继续追 `D84 / D85 family`，优先问的新问题应是:
   - 有没有办法在保留当前 special / `e_evt` 形状时，
     把 `z_art` floor 拉回到更接近 `D33`
   - 或把 validation tax 再压低一截
3. 若没有新的外层 restoration 机制，
   不要只继续重复:
   - outer punctuation 同 family 小改权重
   - 或同一 `200-step` family 的近邻 sweep

### 文档补充
- `docs/137_round1_1_d85_outer_punctuation_long_horizon_verification_report.md`
  - `D85` 的正式 `200-step` 训练、minimal/full long-horizon route 归位，以及训练入口 metrics 回写修复。
## 2026-03-16 `round1.1 / D85 checkpoint-selected late-stop review` 更新
341. 已完成: 对 `D85 = EXP-20260316-041` 运行:
   - 单实验 `checkpoint_selection(late075)`
   - 单实验 `checkpoint_gate_replay(late075)`
342. 已完成: 将 `D22 / D33 / D59 / D76 / D85` 一起并入:
   - 联合 `checkpoint_selection(late075)`
   - 联合 `checkpoint_gate_replay(late075)`
343. 已完成: 物化:
   - `D85 step150 synthetic anchor`
   并分别并入:
   - minimal family route
   - full long-horizon route

### 当前阶段结论补充
- `D85 step150` 相对 `D85 step200` 的真实差值是:
  - validation `+0.027925`
  - special `-0.007382`
  - `zero_e_evt` `+0.038881`
  - `zero_z_art` `-0.009248`

- 这说明:
  - `step150` 是真实 late-stop 候选
  - 它不是 no-op
  - 但它也不是 joint-beating 新默认点
  - 更准确的形状是:
    - special 更好
    - `e_evt` 更好
    - `z_art` 略回吐
    - validation 更差

- `D22 / D33 / D59 / D76 / D85` 联合 late-stop replay 的 aggregate 为:
  - `mean_delta_vs_final_validation = +0.034379`
  - `mean_delta_vs_final_special = -0.008756`
  - `mean_delta_vs_final_e_evt = +0.073218`
  - `mean_delta_vs_final_z_art = -0.003178`

- 也就是说:
  - `D85 step150` 不是孤例
  - 这组 long-horizon late-stop 继续表现为:
    - 稳定换回 better special / `e_evt`
    - 几乎持平但略弱的 `z_art`
    - 和持续更差的 validation

- 把 `D85 step150` 作为 synthetic anchor 并入 minimal family 后:
  - validation = `D76`
  - special = `D85 step150`
  - `zero_e_evt = D85 step150`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.053463`

- 这比不引入 checkpoint anchor 时的:
  - `budget_to_special_anchor = 0.025538`
  还更高。

- 解释:
  - `D85 step150` 虽然比 `D85 step200` 更 special-oriented，
    但它把 validation tax 再抬高了一截。
  - 所以它只能被写成:
    - stronger special option
  - 不能被写成:
    - 更好的 minimal-family default

- 把 `D85 step150` 并入 full long-horizon 后，
  正式四角色完全不变:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D79`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.040968`

先说人话:
- `D85 step150` 是有效 late-stop，
  但它没有把这条 family 抬到新的制度位置。
- 在 minimal family 里，
  它只是把 `D85` 自己的 special / `e_evt` option 再推激进一点，
  同时把预算要求抬到了默认 `0.05` 之上。
- 在 full route 里，
  它连角色都没改写。

### 更新后的下一阶段任务
1. 不要把 `D85 step150` 混写成新的 long-horizon anchor。
2. 更准确的制度写法应是:
   - `D85 step200 = family-level long-horizon representative`
   - `D85 step150 = 更激进的 special-oriented late-stop option`
3. 若继续推进 outer punctuation 这条题，
   下一步不应再优先做:
   - `step150/200` 附近的 late-stop 微调
   - 同 family 的 checkpoint-option 堆叠
4. 若要继续训练新实验，
   信息量更高的仍是:
   - 找新的 outer restoration 机制，
     重点补 `z_art`，而不是继续放大当前 validation tax

### 文档补充
- `docs/138_round1_1_d85_checkpoint_selected_late_stop_review.md`
  - `D85` 的 late-stop 复核、synthetic anchor route 对照，以及当前制度判断。
## 2026-03-16 `round1.1 / D86 outer punctuation z_art-retarget 200-step` 更新
344. 已完成: 新增 `D86` 配置:
   - `configs/offline_mvp_train_d86_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_200step_smallscale_seeded_shuffle.json`
   核心改动为:
   - 把 late `z_art_influence_aux`
     从 `challenge_proxy_core`
     改挂到 `micro_singleton_anypunct_expansion`
   - 并完成:
     - `init-experiment`
     - `train-offline-mvp --dry-run`
     - `200-step` 正式训练
     - final `ablation_eval`
     - final `special_eval`
     - `checkpoint_series(step50/100/150/200)`
     - `special_eval_series(step50/100/150/200)`
345. 已完成: 对 `D86` 运行:
   - 单实验 `checkpoint_selection(late075)`
   - 单实验 `checkpoint_gate_replay(late075)`
   - 以及 `D22 / D33 / D59 / D76 / D85 / D86`
     联合 `checkpoint_selection(late075)` / `checkpoint_gate_replay(late075)`。
346. 已完成: 物化:
   - `D86 step150 synthetic anchor`
   并把它与既有 `D85 step150` 一起并入:
   - minimal family route
   - full long-horizon route

### 当前阶段结论补充
- `D86` 的 shorthand final 为:
  - `2.130019 / 0.231570 / 1.816795 / 0.395586`
- route validation 列为:
  - `2.135101`
- 其 `200-step` 轨迹为:
  - `step50 = 2.313514 / 0.186087 / 2.570719 / 0.308605`
  - `step100 = 2.203182 / 0.209780 / 2.198116 / 0.461504`
  - `step150 = 2.154244 / 0.225450 / 2.186293 / 0.504980`
  - `step200 = 2.130019 / 0.231570 / 1.816795 / 0.395586`

- 这说明:
  - `D86 final` 没有形成新的 final anchor
  - 相对 `D85 final`，
    它没有保住 `e_evt / z_art`
  - 但它把更强的 dual-control 形状
    提前推到了 `step150`

- `D86 step150 - D86 step200` 的真实差值是:
  - validation `+0.021863`
  - special `-0.006120`
  - `zero_e_evt` `+0.369498`
  - `zero_z_art` `+0.109394`

- 对比现有 `D85 step150`:
  - validation `-0.004435`
  - special `+0.001537`
  - `zero_e_evt` `+0.120061`
  - `zero_z_art` `+0.080346`

- 更准确地说:
  - `D85 step150` 仍是这条 family 里更低的 special 点
  - `D86 step150` 则成为更强的 dual-control late-stop 点，
    尤其把 `e_evt + z_art` 一起往上推了一截

- `D22 / D33 / D59 / D76 / D85 / D86`
  联合 late-stop replay 的 aggregate 为:
  - `mean_delta_vs_final_validation = +0.032293`
  - `mean_delta_vs_final_special = -0.008317`
  - `mean_delta_vs_final_e_evt = +0.122598`
  - `mean_delta_vs_final_z_art = +0.015584`

- 这比之前包含 `D85` 的 aggregate 更关键的一点是:
  - `z_art` 平均项重新回到正值
  - 也就是说，
    `D86 step150` 不只是把 `e_evt` 拉高，
    而是真的把这组 late-stop option 的 `z_art` 形状也一起带回来

- 把 `D85 step150 + D86 step150` 一起并入 minimal family 后:
  - validation = `D76`
  - special = `D85 step150`
  - `zero_e_evt = D86 step150`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.053463`

- 把两者一起并入 full long-horizon 后:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D86 step150`
  - `zero_z_art + default_minimax = D33`
  - `budget_to_special_anchor = 0.040968`

先说人话:
- `D86 final` 不是新的正式 route anchor。
- 但 `D86 step150` 已经成为当前 checkpoint-option 层里
  更强的 `zero_e_evt` leader，
  并且是这条 outer punctuation family 里
  最像 dual-control restoration 的 late-stop 点。
- 当前 full long-horizon 的 final-route 主框架仍保持:
  - validation = `D76`
  - special = `D82`
  - default/minimax = `D33`
- 变化发生在 checkpoint-option 层，
  不是 final-route default 层。

### 更新后的下一阶段任务
1. 不要把 `D86 final` 混写成对 `D85 final` 的正式刷新。
2. 更准确的制度写法应是:
   - `D85 step150 = family-level stronger special option`
   - `D86 step150 = family-level stronger dual-control / e_evt option`
3. 若继续训练新实验，
   优先问题已经不是:
   - `D85 / D86` 同 family 小 sweep
   - 或继续堆新的 checkpoint option
4. 信息量更高的问题是:
   - 能否把 `D86 step150` 这种 late-window dual-control 形状，
     更稳定地保到 final

### 文档补充
- `docs/139_round1_1_d86_outer_punctuation_zartretarget_long_horizon_report.md`
  - `D86` 的正式 `200-step` 训练、late-stop 复核、`D86 step150` synthetic anchor route 对照，以及当前制度判断。
## 2026-03-16 `round1.1 / D87 outer punctuation z_art-retarget late-retention 200-step` 更新
347. 已完成: 新增 `D87` 配置:
   - `configs/offline_mvp_train_d87_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_lateretention_200step_smallscale_seeded_shuffle.json`
   相对 `D86` 的唯一主改动是:
   - `losses.z_art_influence_aux.weight_schedule.end_step`
     - `25 -> 200`
   并完成:
   - `init-experiment`
   - `train-offline-mvp --dry-run`
   - `200-step` 正式训练
   - final `ablation_eval`
   - final `special_eval`
   - `checkpoint_series(step50/100/150/200)`
   - `special_eval_series(step50/100/150/200)`
348. 已完成: 对 `D87` 运行:
   - 单实验 `checkpoint_selection(late075)`
   - 单实验 `checkpoint_gate_replay(late075)`
   - 以及 `D22 / D33 / D59 / D76 / D85 / D86 / D87`
     联合 `checkpoint_selection(late075)` / `checkpoint_gate_replay(late075)`。
349. 已完成: 物化:
   - `D87 step150 synthetic anchor`
   并把它与既有:
   - `D85 step150`
   - `D86 step150`
   一起并入:
   - minimal family route
   - full long-horizon route

### 当前阶段结论补充
- `D87` 的 shorthand final 为:
  - `2.127392 / 0.230457 / 4.197220 / 2.611827`
- route validation 列为:
  - `2.131434`
- 其 `200-step` 轨迹为:
  - `step50 = 2.314084 / 0.184908 / 4.917752 / 2.597331`
  - `step100 = 2.213228 / 0.208162 / 4.411053 / 2.554730`
  - `step150 = 2.166759 / 0.221860 / 4.497677 / 2.665073`
  - `step200 = 2.127392 / 0.230457 / 4.197220 / 2.611827`

- `D87 final - D86 final` 为:
  - validation `-0.002627`
  - special `-0.001113`
  - `zero_e_evt` `+0.250406`
  - `zero_z_art` `+0.086222`

- `D87 final - D85 final` 为:
  - validation `-0.001914`
  - special `-0.000838`
  - `zero_e_evt` `+0.040563`
  - `zero_z_art` `+0.048639`

- 这说明:
  - `D87 final` 仍没有把 `z_art` top floor 从 `D33` 手里抢走
  - 但它已经相对 `D85 / D86 final`
    同时改善了 validation / special / `e_evt` floor / `z_art` floor
  - 更准确地说，
    late-retention 这次没有把 `step150` 全量保到 final，
    但已经把一部分 dual-control 形状吞进了 final

- `D87 step150 - D87 step200` 的真实差值是:
  - validation `+0.036557`
  - special `-0.008597`
  - `zero_e_evt` `+0.261090`
  - `zero_z_art` `+0.013879`

- 对比 `D86 step150`:
  - validation `+0.011027`
  - special `-0.003590`
  - `zero_e_evt` `+0.144625`
  - `zero_z_art` `-0.006666`

- 更准确地说:
  - `D87 step150`
    成了这条 family 里更强的 special / `e_evt` checkpoint option
  - 但它不是更强的 `z_art` top-floor option；
    `z_art` 顶点仍在 `D33`

- `D22 / D33 / D59 / D76 / D85 / D86 / D87`
  联合 late-stop replay 的 aggregate 为:
  - `mean_delta_vs_final_validation = +0.020441`
  - `mean_delta_vs_final_special = -0.005673`
  - `mean_delta_vs_final_e_evt = +0.119741`
  - `mean_delta_vs_final_z_art = +0.023462`

- 把 `D87 final + D87 step150`
  并入 minimal family 后:
  - validation = `D76`
  - special = `D87 step150`
  - `zero_e_evt = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`
  - `budget_to_special_anchor = 0.060055`

- 把同一集合并入 full long-horizon 后:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`
  - `budget_to_special_anchor = 0.040968`

先说人话:
- `D87 final` 没有改写 `validation / special / zero_z_art` 这三条正式角色。
- 但它已经正式改写了:
  - `default/minimax`
- 同时:
  - `D87 step150`
    已经接管 checkpoint-option 层的 `zero_e_evt`
  - 在 minimal family 内，
    它还接管了 `special`

350. 当前阶段可以把制度口径更新为:
   - validation = `D76`
   - special = `D82`
   - `zero_e_evt checkpoint-option = D87 step150`
   - `zero_z_art = D33`
   - `default/minimax = D87`
   这意味着:
   - 前一阶段“再做 1 个高信息量实验，判断 offline MVP 是否收口”的问题
     已经被回答
   - `D87` 虽然没有拿下 `z_art` top floor，
     但已经把 final-route 的正式 default 层改写掉
   - 因而离线 MVP 验证环节已经具备收口条件；
     若无额外约束，
     更合理的下一步应是:
     - 冻结当前 route
     - 输出 final handoff / stage report
     - 结束这段 offline MVP validation

### 文档补充
- `docs/140_round1_1_d87_outer_punctuation_zartretarget_lateretention_route_capture_report.md`
  - `D87` 的正式 `200-step` 训练、late-retention 验证、`D87 step150` synthetic anchor route 对照，以及收口判断。
- `docs/141_system_assessment_response_to_temp_1_2.md`
  - 对临时评审文档问题的正式回应、当前真实状态恢复，以及“立刻需要检测/约束”的事项。
- `docs/142_old_long_horizon_experiments_recheck_report.md`
  - 对 `D22 / D33 / D59 / D76-D87` 旧 long-horizon 实验补做的 `special_eval_series + checkpoint-selection + gate replay` 复核结果。

351. 已完成: 对 `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85 / D86 / D87`
   顺序补跑 `special_eval_series(step50/100/150/200)`，
   修复这一批旧 `200-step` 实验缺少 `special_eval_series`，
   导致无法统一做 checkpoint review 的历史缺口。
352. 已完成: 基于补齐后的 metrics，
   重新运行:
   - `checkpoint_selection(late075)`
   - `checkpoint_gate_replay(late075)`
   范围覆盖:
   - `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85 / D86 / D87`
353. 本轮旧实验补验证后的结论是:
   - 没有推翻当前阶段制度口径
   - 但显著提高了旧 long-horizon 实验的可复核性
   - cross-experiment old-family 口径继续保持:
     - best final validation = `D76 final`
     - best final special = `D82 final`
     - best final `e_evt` = `D79 final`
     - best positive-control late special = `D82 step150`
   - gate replay 在 `late075` 下全部收敛到同一组 aggregate，
     说明当前 old-family late gate 逻辑已基本饱和，
     不再是高信息量分叉点。
354. 已完成: 基于当前 formal route selection，
   物化并核对:
   - `build-offline-mvp-route-handoff`
   - `materialize-offline-mvp-route-handoff-doc`
   - `materialize-offline-mvp-stage-report`
   产物确认:
   - formal default/minimax = `D87 final`
   - validation-first alternative = `D76 final`
   - special-first alternative = `D82 final`
   - `D87 step150` 保持 `checkpoint_option_anchor`，
     未被混写成 formal default。
355. 已完成: 新增正式文档
   - `docs/143_offline_mvp_structure_sensitivity_and_applicability_boundary.md`
   用于统一说明:
   - 当前 offline MVP 骨架的结构敏感性
   - 已验证边界与未验证边界
   - family 收口纪律
   - 当前 route 结论的适用范围

### 当前阶段结论补充
- 当前 formal route 与 handoff/stage report 已一致收口为:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt checkpoint-option = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`
- 当前最重要的补充口径不是“又刷新了一个实验赢家”，
  而是:
  - 这些结论成立于当前 offline MVP 骨架，
    不应自动外推到未来完整设计稿结构
- 更准确地说:
  - 当前冻结的是
    shared-encoder + no-`r_res` + single-fusion MVP
    上的制度结论
  - 不是跨结构总定理

先说人话:
- route 已经够稳定，可以按 formal handoff 交接。
- 但文档里必须同时写清，
  这是“当前骨架下成立”，
  不是“未来所有版本都已证明”。

### 更新后的下一阶段任务
1. 若当前阶段仅做收口与交接，优先引用 formal handoff / stage report，不再手工重写 route 口径。
2. 若后续继续训练新实验，立题范围应严格收窄到:
   - 更外层 `z_art` restoration / supervision 机制
3. 不再优先继续:
   - late teacher source handoff
   - late `z_art_weight`
   - late `z_art_influence` retarget
   - full-priority singleton exposure
   - old-family late gate / checkpoint-option 近邻扩展

### 文档补充
- `docs/143_offline_mvp_structure_sensitivity_and_applicability_boundary.md`
  - 当前 offline MVP 的结构敏感性、适用边界、family 收口纪律，以及 formal route 的适用范围。
356. 已完成: 用户确认当前默认不再继续修补 offline MVP 近邻实验，
   当前项目主线切换为:
   - 先写交接
   - 下一次恢复时进入下一阶段开发
357. 已完成: 新增交接文档
   - `docs/144_next_phase_development_handoff.md`
   用于固定:
   - 当前为何收口 offline MVP
   - 下一阶段为什么默认不先开新实验
   - 下次恢复时的默认起手动作

### 当前阶段结论补充
- 当前 offline MVP 的合理默认状态是:
  - 收口
  - 以 formal handoff/stage report 作为固定参考
  - 不再继续同 family 的近邻实验扩展
- 下一阶段默认转向:
  - 前端 / Student 侧工程开发准备
  - 先搭模块边界与接口骨架
  - 暂不直接打开 `r_res`

先说人话:
- 这一步不是“项目暂停”，
  而是“offline MVP 这段验证工作先封箱，下一次直接进新阶段”。

### 更新后的下一阶段任务
1. 下次恢复时，先按 `docs/144_next_phase_development_handoff.md` 的读取顺序恢复上下文。
2. 默认先确定下一阶段首个工程落点:
   - 前端 / Student / 控制头骨架
   - 以及其 config / CLI / eval contract
3. 若无新的外层 `z_art` restoration 机制，不再优先重开 offline MVP 训练实验。

### 文档补充
- `docs/144_next_phase_development_handoff.md`
  - offline MVP 收口后的正式交接，以及下一阶段开发的默认起手动作。
358. 已完成: 将 Stage3 `streaming_student` 骨架正式接入 CLI，
   新增命令:
   - `.\python.exe manage.py prepare-streaming-student-stage`
359. 已完成: 新增 Stage3 scaffold 配置模板
   - `configs/streaming_student_stage_template.json`
   用于固定:
   - `streaming_student_stage`
   - `scaffold_bootstrap`
   - `r_res_enabled = false`
   - 与 `offline_mvp` 对齐的 `frame_length / hop_length`
360. 已完成: 跑通首个 Stage3 scaffold bootstrap，
   生成正式计划产物:
   - `reports/plans/streaming_student_stage/streaming_student_stage_scaffold.plan.json`
   - `reports/plans/streaming_student_stage/streaming_student_stage_scaffold.plan.md`
361. 已完成: 新增正式文档
   - `docs/145_stage3_streaming_student_scaffold_bootstrap_report.md`
   用于固定:
   - 当前 Stage3 骨架已落地到什么程度
   - 已确认的接口 contract
   - 当前仍未进入真实训练的部分

### 当前阶段结论补充
- 当前下一阶段主线已经从“只写交接”推进到:
  - Stage3 `streaming_student` scaffold 已可执行
  - 前端 / Student / 条件输入 / 输出 contract 已有正式落盘产物
- 当前已确认:
  - `streaming_student` scaffold 可以读取 `round1_1` manifest 与正式 split
  - 可以消费:
    - `target_weak_event_hints`
    - `target_special_supervision`
  - 可以在不打开 `r_res` 的前提下跑通最小 dry-run
- 当前尚未开始:
  - 真实 Teacher 标签监督训练
  - `s_spk_target / s_geom_target / alpha` 校准资产格式
  - Stage3 到 `offline_mvp` 指标体系的正式 eval bridge

先说人话:
- 现在不是只停在“想做 Student”。
- 而是已经有了一个能跑、能出计划、能说明输入输出边界的正式骨架。
- 但它还只是工程起点，不是新一轮训练系统。

### 更新后的下一阶段任务
1. 为 Stage3 明确 Teacher-label 数据接线，
   但不要直接复用 `offline_mvp` 训练循环去假装已经进入真实 Student 训练。
2. 先定义:
   - `s_spk_target`
   - `s_geom_target`
   - `alpha`
   的校准资产格式与落盘位置。
3. 优先补一个 Stage3 eval bridge，
   把 `streaming_student` 输出映射到 `offline_mvp` 风格控制汇总，
   再决定是否打开真实训练。
4. 继续保持:
   - `r_res` 关闭
   - `frame_length / hop_length` 与 `offline_mvp` 对齐
   直到前端 / Student contract 与校准资产稳定。

### 文档补充
- `docs/145_stage3_streaming_student_scaffold_bootstrap_report.md`
  - Stage3 scaffold 的代码入口、配置模板、dry-run 结果、当前边界和下一步。
362. 已完成: 新增 Stage3 校准资产构建入口
   - `.\python.exe manage.py build-streaming-student-calibration-assets`
   并生成正式产物:
   - `data_prep/round1_1/streaming_student_calibration/target_calibration_records.jsonl`
   - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_template.json`
   - `reports/data/streaming_student_calibration/streaming_student_calibration_summary.md`
363. 已完成: 新增 Stage3 eval bridge 入口
   - `.\python.exe manage.py build-streaming-student-eval-bridge`
   并生成正式产物:
   - `reports/eval/streaming_student_eval_bridge/streaming_student_eval_bridge.json`
   - `reports/eval/streaming_student_eval_bridge/streaming_student_eval_bridge.md`
364. 已完成: 新增正式文档
   - `docs/146_stage3_calibration_asset_and_eval_bridge_report.md`
   用于固定:
   - 当前 calibration asset schema
   - 当前选出的校准子集
   - 当前 eval bridge 能汇总哪些 Stage3 输出
   - 当前仍未进入真实校准估计和 Student 训练的边界

### 当前阶段结论补充
- 当前 Stage3 不再只有 scaffold plan，
  还新增了两类正式可复用产物:
  - calibration asset scaffold
  - eval bridge summary
- 当前 calibration asset 已固定 machine-readable schema:
  - `s_spk_target`
  - `s_geom_target`
  - `alpha`
  但都还是 placeholder，
  还不是估计结果
- 当前 target-side calibration subset 已在 `max_records = 12` 约束下，
  选出:
  - `11` 条
  - 总时长 `135.964922 sec`
  的结构覆盖子集，
  已基本进入设计稿要求的 `1-3` 分钟范围
- 当前 eval bridge 已能把 Stage3 输出汇总成:
  - `z_art`
  - `event`
  - `coarse_log_f0`
  - `vuv`
  - `aperiodicity`
  - `energy`
  - correction heads
  的 summary，
  并对:
  - `target_validation`
  - `target_special_eval`
  给出对照摘要

先说人话:
- 现在这条线已经不是“先想想校准怎么做”。
- 你已经有:
  - 一个正式校准集
  - 一个正式资产模板
  - 一个能把 Stage3 输出整理成旧口径摘要的桥
- 但这三样都还停在“把接口和边界钉牢”，
  不是“真实校准和真实 Student 已经开训”。

### 更新后的下一阶段任务
1. 在现有 calibration asset schema 之上，
   实现真实的:
   - `s_spk_target`
   - `s_geom_target`
   - `alpha`
   估计步骤，
   替换 placeholder 值。
2. 为 Stage3 补 teacher-label 数据接线，
   但继续避免直接借用 `offline_mvp` 训练循环。
3. 把当前 eval bridge 的 summary keys
   进一步对齐到后续真实 Student 训练会直接依赖的指标集合。
4. 在真实 calibration asset 出来前，
   继续把当前 bridge 输出解释为:
   - contract / plumbing check
   而不是:
   - 模型质量结论

### 文档补充
- `docs/146_stage3_calibration_asset_and_eval_bridge_report.md`
  - Stage3 校准资产模板、校准子集选择结果、eval bridge 摘要，以及当前边界。
365. 已完成: 新增 Stage3 calibration heuristic estimate 入口
   - `.\python.exe manage.py estimate-streaming-student-calibration`
   并生成正式产物:
   - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json`
   - `reports/data/streaming_student_calibration_estimate/streaming_student_calibration_estimate_summary.md`
366. 已完成: 用 estimated calibration asset 重跑 Stage3 eval bridge，
   当前默认 bridge 已优先读取:
   - `streaming_student_calibration_asset_estimated.json`
367. 已完成: 新增正式文档
   - `docs/147_stage3_heuristic_calibration_estimate_report.md`
   用于固定:
   - 当前 heuristic calibration estimator 的输入
   - 估计出的 `s_spk_target / s_geom_target / alpha`
   - 以及它仍然只是 bootstrap prior 的边界

### 当前阶段结论补充
- 当前 Stage3 calibration asset 已从:
  - placeholder template
  推进到:
  - heuristic bootstrap estimated asset
- 当前已落盘的 estimated asset 状态为:
  - `status = heuristic_bootstrap_estimated`
  - `s_spk_target.status = heuristic_estimated`
  - `s_geom_target.status = heuristic_estimated`
  - `alpha.status = heuristic_estimated`
- 当前 bridge 已确认真正读到了 estimated asset，
  不再默认退回 zero-vector placeholder
- 但当前仍必须明确:
  - 这不是 dedicated calibration estimator
  - 只是把 Stage3 conditioning 从“全零占位”推进到“数据驱动 bootstrap prior”

先说人话:
- 现在 Stage3 已经不只是“知道以后要校准”。
- 它已经真的有一份非零、可被 bridge 消费的 conditioning asset。
- 但这份资产的定位仍然是:
  - 先让工程链路摆脱占位值
  - 不是宣告目标说话人校准问题已经被认真解决

### 更新后的下一阶段任务
1. 继续把当前 heuristic estimate 当作 bootstrap prior，
   不要把它冻结成最终校准方案。
2. 下一步更高优先级是:
   - 引入更明确的低频 / 共振峰 / 几何代理约束
   - 让 `alpha` 与 `s_geom_target` 的估计更像设计稿中的 calibration objective
3. 在此基础上，
   再把 teacher-label 数据接线接进真实 Student 训练入口。

### 文档补充
- `docs/147_stage3_heuristic_calibration_estimate_report.md`
  - heuristic calibration estimator、estimated asset、bridge 重新接线后的状态与边界。

## 2026-03-17 Stage3 `streaming_student` teacher-label 数据接线更新
### 当前进度补充
368. 已完成: 将 Stage3 teacher-label 导出正式接入 CLI，
   新增命令:
   - `.\python.exe manage.py build-streaming-student-teacher-labels`
369. 已完成: 用 formal offline MVP route handoff 默认锚点
   - `D87 step200`
   全量导出 Stage3 teacher-label 资产，
   生成正式产物:
   - `data_prep/round1_1/streaming_student_teacher_labels/teacher_label_index.jsonl`
   - `data_prep/round1_1/streaming_student_teacher_labels/records/*.pt`
   - `reports/data/streaming_student_teacher_labels/streaming_student_teacher_label_summary.json`
   - `reports/data/streaming_student_teacher_labels/streaming_student_teacher_label_summary.md`
370. 已完成: 新增正式文档
   - `docs/148_stage3_teacher_label_export_report.md`
   用于固定:
   - teacher anchor 来源
   - teacher-label 资产格式
   - 全量导出统计
   - 当前边界与下一步

### 当前阶段结论补充
- 当前 Stage3 已不再只是:
  - scaffold
  - calibration asset
  - eval bridge
- 还新增了一套正式可复用的 teacher-label 资产，
  可供后续真实 Student 训练入口消费。
- 当前导出使用的默认 teacher anchor 为:
  - `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json`
    指向的 formal route anchor
  - 即 `EXP-20260316-043 ... D87 ... step200`
- 当前全量导出结果为:
  - `record_count = 666`
  - `frame_count = 1118127`
  - `target_train = 592`
  - `target_validation = 66`
  - `target_special_eval = 8`
- 当前 teacher-label 记录内已落盘:
  - `hidden`
  - `fused_hidden`
  - `z_art`
  - `event_logits`
  - `event_probs`
  - `acoustic`
  - `frame_confidence`
- 当前必须继续明确:
  - 这些是 pseudo labels，不是物理真值
  - `frame_confidence` 是 `bootstrap_v1` 启发式权重，不是最终置信度设计
  - Stage3 仍不能直接借用 `offline_mvp` 旧训练循环

先说人话:
- 现在 Stage3 已经不仅有“该学什么”的接口草稿，
  还真的有了“拿什么去监督 Student”的正式资产。
- 但这些监督仍然来自旧 Teacher，
  所以它们的定位是训练资产，不是最终真理。

### 更新后的下一阶段任务
1. 以当前 `teacher_label_index.jsonl + records/*.pt` 为输入合同，
   新建 Stage3 Student 训练数据层与批处理入口，
   不把它硬塞进 `offline_mvp` 训练循环。
2. 把 `frame_confidence`
   明确接成:
   - loss weighting
   - filtering
   - curriculum
   三者里哪些真的需要，
   不要默认全开。
3. 继续把当前 heuristic calibration asset 当作 bootstrap prior，
   再补更像正式 calibration objective 的估计逻辑。
4. 在 teacher-label 数据层与基础 Student loss 稳定前，
   继续保持:
   - `r_res_enabled = false`
   - `frame_length / hop_length` 与 `offline_mvp` 对齐

### 文档补充
- `docs/148_stage3_teacher_label_export_report.md`
  - Stage3 teacher-label 导出入口、资产格式、全量统计、边界和下一步。

## 2026-03-17 Stage3 `streaming_student` 数据合同与最小监督 dry-run 更新
### 当前进度补充
371. 已完成: 新增 Stage3 数据装载模块，
   正式把:
   - split
   - sidecar
   - teacher-label index / records
   - calibration conditioning asset
   焊成统一 batch contract。
372. 已完成: 新增命令
   - `.\python.exe manage.py prepare-streaming-student-training-data`
   并生成正式产物:
   - `reports/plans/streaming_student_training_data/streaming_student_training_data_plan.json`
   - `reports/plans/streaming_student_training_data/streaming_student_training_data_plan.md`
373. 已完成: 新增最小 teacher-supervised loss dry-run，
   新增命令:
   - `.\python.exe manage.py prepare-streaming-student-supervision`
   并生成正式产物:
   - `reports/plans/streaming_student_supervision/streaming_student_supervision_plan.json`
   - `reports/plans/streaming_student_supervision/streaming_student_supervision_plan.md`
374. 已完成: 新增正式文档
   - `docs/149_stage3_training_data_contract_report.md`
   - `docs/150_stage3_minimal_teacher_supervision_report.md`

### 当前阶段结论补充
- 当前 Stage3 已经拥有正式训练前置三件套:
  - teacher-label assets
  - training-data batch contract
  - minimal teacher-supervised loss dry-run
- 当前 `prepare-streaming-student-training-data`
  已确认:
  - `target_train`
  - `target_validation`
  - `target_special_eval`
  三个 slice 的 sample batch
  都满足:
  - `frame_contract_aligned = true`
  - teacher frame count 与 Student 前端输出 frame count 逐样本一致
- 当前最小监督 dry-run 已确认可稳定计算:
  - `teacher_z_art`
  - `teacher_event`
  - `teacher_event_prior`
  - `teacher_energy_proxy`
  - `teacher_vuv_proxy`
  - `teacher_aper_proxy`
  - correction L1 regularization
- 当前 supervision 刻意没有强行加入:
  - hidden distillation
  - fused_hidden distillation
  因为当前 Stage3 `96d`
  与 offline MVP teacher `64d`
  还没有统一投影合同

先说人话:
- 现在已经不只是“数据能读进来”。
- 还进一步确认了:
  - teacher 标签和新前端的帧是对齐的
  - 最小监督项也真的能算出来
- 所以主线可以从“接线”继续往“真实训练入口”推进了。

### 更新后的下一阶段任务
1. 基于当前 batch contract 与最小监督定义，
   新建真正的 Stage3 training step / optimizer / checkpoint scaffold。
2. 在真实训练前先决定:
   - `teacher_frame_confidence`
   到底用于 weighting、filtering、还是 curriculum；
   不要默认三者全启。
3. 若后续确实需要 hidden distillation，
   先定义 Stage3 与 offline MVP teacher 的投影桥，
   再引入对应 loss。
4. 在真实 training step 稳定前，
   继续保持:
   - 全音频读取，不做会破坏 teacher frame 对齐的截断
   - `r_res_enabled = false`

### 文档补充
- `docs/149_stage3_training_data_contract_report.md`
  - Stage3 数据装载合同、dry-run batch shapes、frame alignment 结果与边界。
- `docs/150_stage3_minimal_teacher_supervision_report.md`
  - 最小 teacher-supervised loss 设计、dry-run 数值、当前没接的项与下一步。

375. 已完成: 新增 Stage3 单步训练 scaffold 入口
   - `.\python.exe manage.py run-streaming-student-training-step`
376. 已完成: 实跑单步训练 scaffold
   - `experiment_id = streaming_student_stage_step_scaffold_v1`
   生成正式产物:
   - `reports/training/streaming_student/checkpoints/streaming_student_stage_step_scaffold_v1.step1.pt`
   - `reports/training/streaming_student/logs/streaming_student_stage_step_scaffold_v1.step1.json`
   - `reports/training/streaming_student/streaming_student_stage_step_scaffold_v1.step1.md`
377. 已完成: 新增正式文档
   - `docs/151_stage3_training_step_scaffold_report.md`

### 当前阶段结论补充
- 当前 Stage3 已经不只是:
  - scaffold
  - calibration asset
  - eval bridge
  - teacher-label assets
  - training-data contract
  - minimal supervision dry-run
- 还新增了一个真实执行过的:
  - 单步训练 scaffold
- 这意味着当前已确认打通:
  - forward
  - loss
  - backward
  - optimizer
  - checkpoint
  - train/validation step 日志落盘
- 当前单步训练 scaffold 关键结果:
  - `train loss_total = 20.612329`
  - `validation loss_total = 14.115878`
  - `grad_norm = 64.267143`
  - checkpoint 已落盘

先说人话:
- 现在不是“离真实训练还差很多接口”。
- 而是已经真的把训练主干的最小闭环跑了一次。
- 下一步该补的是多 step 训练循环和策略细化，
  不是再回到只做数据接线。

### 更新后的下一阶段任务
1. 把当前 one-step scaffold
   扩成:
   - 多 step
   - 周期验证
   - 周期 checkpoint
   - step 日志
   的最小训练循环。
2. 基于当前 `grad_norm = 64.267143`
   与 loss 规模，
   重新评估:
   - learning rate
   - loss 权重
   - teacher confidence 使用方式
3. 在多 step 稳定前，
   不要引入:
   - hidden distillation
   - `r_res`
   - 更复杂的 frontend 头语义

### 文档补充
- `docs/151_stage3_training_step_scaffold_report.md`
  - 单步训练 scaffold 命令、实际运行结果、checkpoint 与当前边界。

378. 已完成: 新增 Stage3 最小多 step 训练循环入口
   - `.\python.exe manage.py run-streaming-student-training-loop`
379. 已完成: 实跑最小多 step 训练循环
   - `experiment_id = streaming_student_stage_loop_scaffold_v1`
   - `num_steps = 4`
   - `validation_interval = 2`
   - `checkpoint_interval = 2`
   - `validation_batches = 2`
   生成正式产物:
   - `reports/training/streaming_student_loop/streaming_student_stage_loop_scaffold_v1.summary.md`
   - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.summary.json`
   - `reports/training/streaming_student_loop/logs/streaming_student_stage_loop_scaffold_v1.step*.json`
   - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_scaffold_v1.step2.pt`
   - `reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_scaffold_v1.step4.pt`
380. 已完成: 新增正式文档
   - `docs/152_stage3_training_loop_scaffold_report.md`

### 当前阶段结论补充
- 当前 Stage3 已经从:
  - 单步训练 scaffold
  推进到:
  - 最小多 step 训练循环 scaffold
- 这意味着当前已新增:
  - step 级日志序列
  - 周期 validation
  - 周期 checkpoint
  - run summary
- 本轮 `4 step` 短程轨迹显示:
  - train `loss_total`
    从 `20.612329`
    到 `10.774693`
  - `grad_norm`
    从 `64.267143`
    到 `13.034104`
  - sampled validation `loss_total`
    从 `13.13162`
    到 `9.656614`
- 但当前必须继续明确:
  - 这只是短程 scaffold run
  - 当前 validation 只覆盖 sampled `2` 个 batch
  - 不能把这组数值写成“Stage3 已获得稳定训练策略”

先说人话:
- 现在 Stage3 已经不是只会跑一步。
- 它已经能连续跑几步、定期看 validation、定期存 checkpoint。
- 所以下一个真正的工作重点，
  已经变成“怎么把这个短程循环稳定下来”，
  而不是“训练入口能不能跑”。

### 更新后的下一阶段任务
1. 把当前 `4 step` scaffold
   扩成更像真实小规模训练的短程 loop，
   例如:
   - 更多 step
   - 更明确的 validation 口径
   - 更清晰的 best-checkpoint 规则
2. 先围绕当前短程轨迹，
   调:
   - learning rate
   - teacher loss 权重
   - teacher confidence 用法
   再考虑加新 supervision。
3. 在 sampled validation 口径没稳定前，
   不把当前 loss 下降轨迹直接升级成阶段胜利结论。

### 文档补充
- `docs/152_stage3_training_loop_scaffold_report.md`
  - 最小多 step 训练循环命令、step 轨迹、validation 口径、checkpoint 与当前边界。

## 2026-03-17 Stage3 短程稳定化对照与 fuller checkpoint eval 更新
### 当前进度补充
381. 已完成: 新增 Stage3 checkpoint fuller eval 入口
   - `.\python.exe manage.py evaluate-streaming-student-checkpoint`
382. 已完成: 修正 Stage3 fuller eval 两个关键问题
   - checkpoint 现在会保留:
     - `config_path`
     - `training.use_teacher_confidence`
     - `training.loss_weights`
   - full-slice eval 不再在最后一个 batch 回绕重复采样
383. 已完成: 基于 `4 step` loop 做三组短程对照
   - baseline:
     - `streaming_student_stage_loop_scaffold_v2`
   - no confidence:
     - `streaming_student_stage_loop_no_conf_v2`
   - lower lr:
     - `streaming_student_stage_loop_lr3e4_v2`
384. 已完成: 对三组 `step4` checkpoint
   跑 fuller eval，
   生成正式产物:
   - `reports/eval/streaming_student_checkpoint_eval/*.checkpoint_eval.{json,md}`
385. 已完成: 新增正式文档
   - `docs/153_stage3_short_horizon_stabilization_comparison_report.md`

### 当前阶段结论补充
- 当前短程稳定化对照已给出一个明确结论:
  - 保留:
    - `learning_rate = 1e-3`
    - `teacher_confidence = on`
  - 暂不切到:
    - `learning_rate = 3e-4`
    - `teacher_confidence = off`
- fuller checkpoint eval 结果:
  - baseline `v2`
    - `target_validation.loss_total = 9.94085`
    - `target_special_eval.loss_total = 9.144604`
  - no confidence `v2`
    - `target_validation.loss_total = 10.533068`
    - `target_special_eval.loss_total = 9.372594`
  - lower lr `v2`
    - `target_validation.loss_total = 13.962363`
    - `target_special_eval.loss_total = 12.267866`
- 当前可暂时认为:
  - `teacher_confidence` weighting
    在这条最小 Stage3 route 上是有价值的
  - `3e-4`
    对当前 `4 step` 短程 horizon 来说过慢

先说人话:
- 现在不是“几个方案都差不多”。
- 这轮对照已经把方向收窄了:
  - 先别关 `teacher_confidence`
  - 先别把学习率降到 `3e-4`
- 也就是说，
  下一步可以围绕当前 baseline 继续细化，
  而不是重新分三条路线一起试。

### 更新后的下一阶段任务
1. 以当前 baseline:
   - `lr = 1e-3`
   - `teacher_confidence = on`
   作为默认短程训练配置继续推进。
2. 下一轮优先调的，
   不再是:
   - 是否关掉 teacher confidence
   - 是否直接把 lr 降到 `3e-4`
   而是:
   - loss 权重
   - validation 口径
   - 更长一点的短程 horizon
3. 若后续继续做对照，
   必须统一使用:
   - 不回绕的 fuller checkpoint eval
   - 带完整训练元数据的 checkpoint

### 文档补充
- `docs/153_stage3_short_horizon_stabilization_comparison_report.md`
  - baseline / no_conf / lr3e4 三组短程 loop 与 fuller checkpoint eval 的对照结论。

## 2026-03-17 Stage3 baseline 12-step 短程 run 更新
### 当前进度补充
386. 已完成: 基于当前默认 baseline 配置
   运行更长一点的短程 loop
   - `experiment_id = streaming_student_stage_loop_baseline12_v1`
   - `num_steps = 12`
   - `validation_interval = 4`
   - `checkpoint_interval = 4`
   - `validation_batches = 4`
387. 已完成: 对 `step12` checkpoint
   运行 fuller checkpoint eval，
   生成正式产物:
   - `reports/eval/streaming_student_checkpoint_eval/streaming_student_stage_loop_baseline12_v1.checkpoint_eval.{json,md}`
388. 已完成: 新增正式文档
   - `docs/154_stage3_baseline12_short_run_report.md`

### 当前阶段结论补充
- 当前 baseline 不只是:
  - 在 `4 step` 短程里优于 `no_conf / lr3e4`
- 还进一步在 `12 step` 上继续下降，
  没有看到明显炸梯度或回升失稳:
  - train `loss_total: 20.612329 -> 8.203006`
  - `grad_norm: 64.267143 -> 4.994916`
  - sampled validation `loss_total: 10.005472 -> 8.099716`
- fuller checkpoint eval 也继续支持这一方向:
  - `target_validation.loss_total = 8.134648`
  - `target_special_eval.loss_total = 8.11794`
- 相比当前 `4 step baseline v2`
  的 fuller eval:
  - validation 从 `9.94085` 下降到 `8.134648`
  - special 从 `9.144604` 下降到 `8.11794`

先说人话:
- 现在这条 baseline 不只是“4 步里看起来还行”。
- 它在更长一点的短程 run 里也还在继续变好。
- 所以下一轮主线可以更坚定地围绕 baseline 做，
  不需要再回头怀疑“是不是一开始那 4 步只是巧合”。

### 更新后的下一阶段任务
1. 继续沿 baseline 配置推进更正式的小规模训练，
   并开始考虑:
   - 更像完整 validation 的口径
   - best-checkpoint 选择规则
2. 下一轮优先调的对象
   可以收窄到:
   - loss 权重
   - validation 设计
   - 短程 horizon 长度
3. 暂不优先回头再试:
   - `teacher_confidence off`
   - `lr = 3e-4`

### 文档补充
- `docs/154_stage3_baseline12_short_run_report.md`
  - baseline `12 step` 短程轨迹、fuller eval 结果与当前默认结论。

389. 已完成: 新增 Stage3 checkpoint 排名入口
   - `.\python.exe manage.py select-streaming-student-best-checkpoint`
390. 已完成: 对 baseline12 的
   - `step4 / step8 / step12`
   跑 fuller checkpoint ranking，
   生成正式产物:
   - `reports/eval/streaming_student_checkpoint_selection/streaming_student_checkpoint_selection.json`
   - `reports/eval/streaming_student_checkpoint_selection/streaming_student_checkpoint_selection.md`
391. 已完成: 新增正式文档
   - `docs/155_stage3_checkpoint_selection_report.md`

### 当前阶段结论补充
- baseline12 当前默认 best checkpoint
  已不再靠口头判断，
  而是有了正式 ranking 产物。
- 当前 ranking rule 为:
  - `lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)`
- 当前 baseline12 排名结果:
  - `step12`
    - `target_validation = 8.134648`
    - `target_special_eval = 8.11794`
  - `step8`
    - `8.879169 / 8.446648`
  - `step4`
    - `9.94085 / 9.144604`
- 因而当前 baseline12 的正式默认选点
  可以先固定为:
  - `step12`

先说人话:
- 现在不仅知道“这条 baseline 在变好”，
  还已经明确知道:
  - 在现有 checkpoint 里该先拿哪一个
- 这让下一轮工作可以直接围绕默认 best checkpoint 往前推，
  不需要再反复比 `step4/8/12`。

### 更新后的下一阶段任务
1. 以 baseline12 `step12`
   作为当前默认 best checkpoint，
   继续推进下一轮更正式的小规模训练。
2. 若下一轮 checkpoint 更多，
   继续沿用当前 fuller ranking 机制，
   不再退回手工目测。
3. 下一轮更值得调的对象
   继续集中在:
   - loss 权重
   - validation 口径
   - horizon 长度

### 文档补充
- `docs/155_stage3_checkpoint_selection_report.md`
  - baseline12 `step4/8/12` 的 fuller ranking 与默认 best checkpoint 结论。

## 2026-03-17 Stage3 loss-weight override 与 eventprior025 对照更新
### 当前进度补充
392. 已完成: 新增 Stage3 loss weight override 入口
   - `prepare-streaming-student-supervision`
   - `run-streaming-student-training-step`
   - `run-streaming-student-training-loop`
   现支持:
   - `--loss-weight-overrides <json>`
393. 已完成: 所有 Stage3 teacher-supervised loss
   新增固定参考指标:
   - `loss_total_default_reference`
   用于跨权重配置做 apples-to-apples 对照；
   同时 checkpoint / summary
   会记录:
   - `loss_weight_overrides_path`
394. 已完成: 新增权重配置
   - `configs/streaming_student_loss_weights_eventprior_light_v1.json`
   其中当前唯一 override 为:
   - `teacher_event_prior = 0.25`
395. 已完成: 基于该配置
   跑完一条与 baseline12 同口径的短程对照:
   - `experiment_id = streaming_student_stage_loop_eventprior025_v1`
   - `num_steps = 12`
   - `validation_interval = 4`
   - `checkpoint_interval = 4`
   - `validation_batches = 4`
   并补齐:
   - fuller checkpoint selection
   - best checkpoint fuller eval
396. 已完成: 新增正式文档
   - `docs/156_stage3_loss_weight_override_and_eventprior025_report.md`

### 当前阶段结论补充
- `eventprior025`
  在它自己的有效训练目标下
  下降更快:
  - train `loss_total: 19.2505 -> 6.985175`
  - sampled validation `loss_total: 8.713638 -> 6.886201`
- 但跨权重配置时，
  不能直接用 `loss_total`
  横向判断优劣；
  必须看:
  - `loss_total_default_reference`
  - 或各项未加权 component loss
- 按默认参考权重回算后的 `step12` fuller eval:
  - baseline12
    - validation `8.134648`
    - special `8.11794`
  - eventprior025
    - validation `8.150748`
    - special `8.115334`
- 这说明:
  - `eventprior025` 目前还不能直接升级成
    新默认 baseline
  - 但它已经成为一个
    非常接近 baseline 的可继续推进候选，
    尤其在 special 上没有恶化

先说人话:
- 这轮最有价值的成果
  不是“已经找到新 baseline”，
  而是:
  - 权重 sweep 现在可配置、可追踪、可复现
  - 且后续比较终于有了
    不受权重缩放误导的统一口径

### 更新后的下一阶段任务
1. baseline12 仍保持当前默认基线，
   不因 `eventprior025`
   的更低有效 `loss_total`
   就仓促换线。
2. 下一轮若继续调 loss 权重，
   必须统一使用:
   - `loss_total_default_reference`
   - fuller checkpoint eval
   做横向比较。
3. 更值得继续试的方向
   已收敛到:
   - `eventprior025` 更长一点 horizon
   - `energy_proxy` 轻量化
   - validation 口径继续规范化

### 文档补充
- `docs/156_stage3_loss_weight_override_and_eventprior025_report.md`
  - override 入口、参考指标、eventprior025 对照与当前保守结论。

## 2026-03-17 Stage3 full-validation loop integration 更新
### 当前进度补充
397. 已完成: 为 Stage3 训练 loop 新增可配置 validation 口径
   - `run-streaming-student-training-loop`
   现支持:
   - `--validation-mode sampled`
   - `--validation-mode full`
398. 已完成: 在 loop summary / checkpoint training metadata 中新增:
   - `validation_mode`
399. 已完成: 基于 baseline12 同一训练轨迹
   跑通 full-slice validation 版本:
   - `experiment_id = streaming_student_stage_loop_baseline12_fullval_v1`
400. 已完成: 对 `step12` checkpoint
   追加外部 fuller checkpoint eval，
   验证 loop 内 full validation
   与外部 full-slice eval 数值一致。
401. 已完成: 新增正式文档
   - `docs/157_stage3_full_validation_loop_report.md`

### 当前阶段结论补充
- 当前 Stage3 不再只有:
  - sampled validation + 外挂 fuller eval
- 还新增了:
  - loop 内 full-slice sequential validation
- 这意味着:
  - 训练循环内部
    已经可以直接给出
    不回绕、不抽样的 `target_validation`
    轨迹
  - 后续短程对照
    不必每次都先靠 sampled validation
    再额外补一轮 checkpoint eval

- 当前 `baseline12_fullval_v1`
  在 `step4 / step8 / step12`
  的 loop 内 full validation
  分别为:
  - `9.94085`
  - `8.879169`
  - `8.134648`
- 对应 `step12` 外部 checkpoint eval
  的 `target_validation.loss_total`
  也为:
  - `8.134648`
- 这说明:
  - 当前 full-validation loop
    与现有 fuller checkpoint eval
    在 `target_validation` 口径上
    已经对齐

- 当前 loop 内 `best_checkpoint`
  也已不再只依赖 sampled subset，
  而是可以在:
  - `validation_mode = full`
  下
  直接基于整条 `target_validation`
  轨迹选出:
  - `step12`

先说人话:
- 现在 Stage3 的训练循环
  已经不只是“跑几步顺便抽几批看看”。
- 它已经可以在循环内部
  直接把整个验证集走一遍，
  给出和外挂 fuller eval
  对得上的数值。
- 这样下一轮做 baseline / 权重对照时，
  validation 口径会更硬，
  不容易再被 sampled 波动带偏。

### 更新后的下一阶段任务
1. 以后凡是需要正式比较 Stage3 短程 run，
   优先使用:
   - `--validation-mode full`
   尤其是:
   - baseline 续跑
   - loss weight sweep
2. 下一轮更值得做的对照，
   继续收敛到:
   - `eventprior025` 更长一点 horizon
   - `energy_proxy` 轻量化
   - 都统一使用 full validation
3. 当前仍不把这组结果外推成:
   - 长程训练已稳定
   - `r_res` 可直接打开
   - 最终听感已经成立

### 文档补充
- `docs/157_stage3_full_validation_loop_report.md`
  - Stage3 训练 loop 的 full-validation 集成、baseline12 fullval 对照，以及与外部 checkpoint eval 的对齐结果。

## 2026-03-17 Stage3 energyproxy015 full-validation 对照更新

### 本轮推进
402. 已完成: 新增权重覆盖配置
   - `configs/streaming_student_loss_weights_energyproxy_light_v1.json`
   - 仅把
     - `teacher_energy_proxy`
       从 `0.25`
       下调到 `0.15`
403. 已完成: 对新权重配置先做 supervision smoke test，
   确认 `--loss-weight-overrides`
   可正常被 Stage3 supervision pipeline 读取。
404. 已完成: 跑通 full-validation short-horizon 对照:
   - `experiment_id = streaming_student_stage_loop_energyproxy015_fullval_v1`
405. 已完成: 对
   - `step4`
   - `step8`
   - `step12`
   做 fuller checkpoint ranking，
   并对 `step12`
   追加外部 checkpoint eval。
406. 已完成: 新增正式文档
   - `docs/158_stage3_energyproxy015_full_validation_report.md`

### 当前阶段结论补充
- 这轮 `energyproxy015`
  short-horizon full-validation run
  本身是稳定的:
  - train `loss_total`
    从:
    - `19.314896`
    降到:
    - `7.954313`
  - `grad_norm`
    从:
    - `62.632622`
    降到:
    - `3.887995`

- loop 内 full validation
  的 `step4 / step8 / step12`
  分别为:
  - `9.405372`
  - `8.459062`
  - `7.8875`
- 其统一参考权重口径
  `loss_total_default_reference`
  分别为:
  - `10.037295`
  - `8.92416`
  - `8.17354`

- 外部 checkpoint ranking
  结果为:
  - `step12`
    最优
  - `step8`
    次之
  - `step4`
    再次
- 外部 `step12` eval:
  - `target_validation.loss_total_default_reference = 8.17354`
  - `target_special_eval.loss_total_default_reference = 8.164811`

- 与默认 baseline
  `baseline12_fullval_v1.step12`
  对比:
  - baseline
    `target_validation.loss_total_default_reference`
    为:
    - `8.134648`
  - baseline
    `target_special_eval.loss_total_default_reference`
    为:
    - `8.11794`

- 这说明:
  - `energyproxy015`
    在覆盖后权重下
    自己的 `loss_total`
    会更好看，
    这是预期内现象
  - 但回到统一参考权重后，
    它并没有超过 baseline
  - 目前还不能升级成
    默认 Stage3 short-horizon baseline

先说人话:
- 这轮不是坏结果，
  但也不是胜出的结果。
- 它证明了:
  - 把 `teacher_energy_proxy`
    轻一点
    不会立刻把训练弄坏
- 但同时也说明:
  - 仅靠把这项权重从 `0.25`
    降到 `0.15`
    还换不来更好的统一参考指标

### 更新后的下一阶段任务
1. 默认比较基线
   继续保留:
   - `streaming_student_stage_loop_baseline12_fullval_v1.step12.pt`
2. 之后 loss weight sweep
   继续统一使用:
   - `--validation-mode full`
3. 下一轮更值得优先推进:
   - `eventprior025`
     更长一点 horizon
   - 或保持当前 baseline
     继续向更长 horizon
     验证短程趋势是否延续

### 文档补充
- `docs/158_stage3_energyproxy015_full_validation_report.md`
  - `teacher_energy_proxy = 0.15`
    的 full-validation 对照、checkpoint ranking，以及与 baseline12 的统一参考口径比较。

## 2026-03-17 Stage3 baseline24 与 eventprior025 full-validation 对照更新

### 本轮推进
407. 已完成: 跑通默认权重的
   - `streaming_student_stage_loop_baseline24_fullval_v1`
   采用:
   - `24 steps`
   - `validation_mode = full`
   - checkpoints at `step8/16/24`
408. 已完成: 跑通同 horizon 的
   - `streaming_student_stage_loop_eventprior025_fullval24_v1`
   除
   - `teacher_event_prior = 0.25`
   外其余参数保持一致。
409. 已完成: 为两条 24-step run
   分别做 fuller checkpoint ranking，
   并确认最佳 checkpoint
   都落在:
   - `step24`
410. 已完成: 为两条 24-step run
   的 `step24`
   追加外部 best-checkpoint eval。
411. 已完成: 新增正式文档
   - `docs/159_stage3_baseline24_vs_eventprior025_full_validation_report.md`

### 当前阶段结论补充
- 默认 baseline
  在更长 horizon
  下继续明显改善:
  - `baseline12_fullval.step12`
    的
    `target_validation.loss_total_default_reference`
    为:
    - `8.134648`
  - `baseline24_fullval.step24`
    已降到:
    - `7.292622`

- `eventprior025`
  在更长 horizon
  下同样继续改善:
  - `eventprior025.step12`
    的
    `target_validation.loss_total_default_reference`
    为:
    - `8.150748`
  - `eventprior025_fullval24.step24`
    已降到:
    - `7.30326`

- 但两者在 `24-step`
  下的关系
  仍没有翻转:
  - baseline24 validation:
    - `7.292622`
  - eventprior025 fullval24 validation:
    - `7.30326`
  - 差值:
    - `+0.010638`

  - baseline24 special:
    - `7.804316`
  - eventprior025 fullval24 special:
    - `7.803009`
  - 差值:
    - `-0.001307`

- 这说明:
  - 更长 horizon
    并没有把
    `eventprior025`
    推成明确更优解
  - 它仍然是:
    - validation 略差
    - special 略好
    的近似平手候选

- 按当前正式规则:
  - validation-first
  - special 作次级排序
  当前默认 best checkpoint
  应更新为:
  - `streaming_student_stage_loop_baseline24_fullval_v1.step24.pt`

先说人话:
- 24-step 是实打实前进了一步，
  不是原地踏步。
- 默认 baseline 明显变好了，
  而 `eventprior025`
  也继续跟得很近，
  但还是没有反超。
- 所以现在最稳妥的主线
  已经从
  - `baseline12 step12`
  切到
  - `baseline24 step24`

### 更新后的下一阶段任务
1. 默认基线
   先更新到:
   - `streaming_student_stage_loop_baseline24_fullval_v1.step24.pt`
2. 下一轮优先做:
   - baseline 主线继续扩一点 horizon
   - 或围绕更接近成品链路的后续门槛推进
3. `eventprior025`
   可保留为:
   - 高接近度候选分支
   但暂不替换默认 baseline

### 文档补充
- `docs/159_stage3_baseline24_vs_eventprior025_full_validation_report.md`
  - baseline24 与 eventprior025 fullval24 的同 horizon 对照、ranking、外部 eval 与当前默认基线更新结论。

## 2026-03-17 Stage3 baseline48 与 eventprior025 full-validation 对照更新

### 本轮推进
412. 已完成: 把默认主线继续推进到
   - `streaming_student_stage_loop_baseline48_fullval_v1`
   使用:
   - `48 steps`
   - `validation_mode = full`
   - checkpoints at `step12/24/36/48`
413. 已完成: 对 baseline48
   做 fuller checkpoint ranking
   与 best-checkpoint 外部 eval，
   当前最佳点落在:
   - `step48`
414. 已完成: 跑同 horizon 的影子对照
   - `streaming_student_stage_loop_eventprior025_fullval48_v1`
415. 已完成: 对 eventprior025 fullval48
   做 fuller ranking
   与 best-checkpoint 外部 eval，
   当前最佳点同样落在:
   - `step48`
416. 已完成: 新增正式文档
   - `docs/160_stage3_baseline48_vs_eventprior025_full_validation_report.md`

### 当前阶段结论补充
- baseline 主线继续改善:
  - baseline24 `step24`
    validation:
    - `7.292622`
  - baseline48 `step48`
    validation:
    - `7.141462`
  - 改善:
    - `-0.15116`

- eventprior025
  也继续改善:
  - eventprior025 fullval24 `step24`
    validation:
    - `7.30326`
  - eventprior025 fullval48 `step48`
    validation:
    - `7.152429`
  - 改善:
    - `-0.150831`

- 但到 `48-step`
  为止，
  `eventprior025`
  仍没有完成反超:
  - baseline48 validation:
    - `7.141462`
  - eventprior025 fullval48 validation:
    - `7.152429`
  - 差值:
    - `+0.010967`

  - baseline48 special:
    - `7.572382`
  - eventprior025 fullval48 special:
    - `7.573954`
  - 差值:
    - `+0.001572`

- 这意味着:
  - `eventprior025`
    依旧是高接近度候选
  - 但按当前 validation-first 规则，
    默认主线仍应留在:
    - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`

先说人话:
- 默认主线还能往前走，
  而且不是虚降。
- `eventprior025`
  仍然很近，
  但已经连续两个更长 horizon
  都没翻过去。
- 所以下一步不再优先继续纠缠
  这组近邻权重，
  应该开始把资源转去试听导出链路。

### 更新后的下一阶段任务
1. 当前默认 best checkpoint
   更新为:
   - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
2. 之后若继续拉长 horizon，
   `eventprior025`
   继续只保留为影子分支
3. 更值得优先推进的下一步
   切换为:
   - 从当前默认 checkpoint
     接出正式的试听导出链路

### 文档补充
- `docs/160_stage3_baseline48_vs_eventprior025_full_validation_report.md`
  - baseline48 与 eventprior025 fullval48 的同 horizon 对照、ranking、外部 eval，以及默认主线仍保持 baseline 的结论。

## 2026-03-17 Stage3 proxy audio export bootstrap 更新

### 本轮推进
417. 已完成: 新增正式命令
   - `export-streaming-student-proxy-audio`
   用于从 Stage3 checkpoint
   导出:
   - `input.wav`
   - `teacher_proxy.wav`
   - `student_proxy.wav`
418. 已完成: 新增实现
   - `src/v5vc/streaming_student/proxy_audio_export.py`
419. 已完成: 用当前默认 checkpoint
   - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
   导出 validation bundle:
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
420. 已完成: 用同一 checkpoint
   导出 special bundle:
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
421. 已完成: 新增正式文档
   - `docs/161_stage3_proxy_audio_export_bootstrap_report.md`

### 当前阶段结论补充
- Stage3 现在已经不再只有:
  - proxy loss
  - fuller checkpoint eval
- 还首次具备了:
  - 正式可试听代理导出链路

- 当前 validation bundle:
  - `split_name = target_validation`
  - `sample_count = 3`
  - 每条都导出:
    - `input`
    - `teacher_proxy`
    - `student_proxy`

- 当前 special bundle:
  - `split_name = target_special_eval`
  - `sample_count = 3`
  - 每条同样导出:
    - `input`
    - `teacher_proxy`
    - `student_proxy`

- 当前 `student_proxy`
  不是最终 vocoder，
  而是把 Stage3 预测的:
  - `energy`
  - `vuv_logits`
  - `aperiodicity`
  - `event_probs`
  映射回一个低频、去音调化、
  结构优先的 audible proxy

- 这意味着:
  - 现在已经可以做人耳结构 gate
  - 可以直接听:
    - 原始输入结构
    - teacher 结构代理
    - student 结构代理
    之间的差距
  - 但还不能把这些 wav
    误读成:
    - 最终成品音质试听

先说人话:
- 项目现在终于不只是“看 loss 曲线”了。
- 已经可以把当前默认 Stage3 checkpoint
  导成一包能听的结构代理，
  用人耳检查:
  - student 有没有跟上 teacher
  - 有没有明显停顿、能量、稳定性异常
- 这一步很关键，
  因为后面是否继续猛推 horizon
  或接更复杂链路，
  现在终于可以有一层听感 gate 了。

### 更新后的下一阶段任务
1. 先对当前两组 Stage3 proxy bundle
   做一轮人工试听
2. 根据试听结果，
   再决定是:
   - 继续沿默认主线扩 horizon
   - 还是优先修 student/teacher 的结构 gap
3. 在没有听审结论前，
   仍不把当前 Stage3
   解释成最终用户可用音质

### 文档补充
- `docs/161_stage3_proxy_audio_export_bootstrap_report.md`
  - Stage3 proxy audio 命令、新增导出链路、validation/special bundles，以及当前听审边界。

## 2026-03-17 Stage3 上下文恢复与 GUI 接管更新

### 当前进度补充
422. 已完成: 按恢复规范重新读取
   - `docs/00_context_bootstrap.md`
   - `docs/01_project_overview_and_plan.md`
   - `docs/02_pitfalls_log.md`
   - `docs/144_next_phase_development_handoff.md`
   - `docs/161_stage3_proxy_audio_export_bootstrap_report.md`
   - `initial_design.md`
   - `initial_design_judg.md`
   以恢复当前工作状态
423. 已完成: 重新核对当前未提交代码与 Stage3 试听链状态，
   确认:
   - `export-streaming-student-proxy-audio`
     已正式接入并可用
   - `src/v5vc/audio_audit_gui.py`
     已写出独立 GUI scaffold，
     但尚未接入 `manage.py` 正式入口
424. 已完成: 新增正式接管文档
   - `docs/162_stage3_context_restore_and_gui_takeover_report.md`

### 当前阶段结论补充
- 当前主线仍保持在:
  - Stage3 default checkpoint
    `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
  - 以及与之配套的
    proxy audio human-review gate

- 当前 `proxy audio` 导出链
  已经正式闭环:
  - 命令存在
  - 产物存在
  - 文档存在

- 但新写的
  - `src/v5vc/audio_audit_gui.py`
  当前仍只处于:
  - 独立脚本可运行
  - 能读取当前 bundle 格式
  - 但未完成正式 CLI 集成 / 文档交接 / 使用产物留档
  的状态

先说人话:
- 现在不是“完全没有 GUI”，
  也不是“GUI 已正式接好”。
- 更准确地说，
  上次中断时已经把 GUI 骨架写出来了，
  但还没把它变成项目里正式可接手的流程入口。

### 更新后的下一阶段任务
1. 若继续推进听审工作流，
   优先补完:
   - GUI 正式入口
   - GUI 使用文档
   - 一次真实 review 导出样例
2. 若先只做模型路线判断，
   也可直接人工试听:
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
3. 在没有新听审记录前，
   当前仍不把 Stage3 解释成:
   - 最终用户可用音质
   - 或已完成正式人耳 gate

### 文档补充
- `docs/162_stage3_context_restore_and_gui_takeover_report.md`
  - 本轮恢复读取入口、当前正式主线、GUI 当前状态，以及下一步建议。

## 2026-03-17 Stage3 audio audit GUI bootstrap 与听审启动更新

### 当前进度补充
425. 已完成: 为音频听审工具新增正式命令入口
   - `.\python.exe manage.py launch-audio-audit-gui`
426. 已完成: 修正 GUI 中影响真实听审流程的关键问题，
   包括:
   - filter 后当前记录索引失配
   - 无法仅凭 progress 文件恢复上次 bundle 列表
427. 已完成: 用当前 Stage3 两组 bundle
   跑通 GUI smoke test，
   并生成会话目录:
   - `reports/audio/audio_audit_gui_stage3_baseline48_session/`
428. 已完成: 新增正式文档
   - `docs/163_stage3_audio_audit_gui_bootstrap_report.md`
   - `docs/164_stage3_audio_audit_gui_smoke_test_and_human_review_kickoff_report.md`

### 当前阶段结论补充
- 当前 Stage3 不再只是:
  - 有 proxy audio 导出命令
  - 但人工听审只能手工点文件
- 现在已经补到:
  - 有正式 GUI 入口
  - 有进度续接
  - 有 review 导出目录约定

- 当前听审会话目录
  已固定为:
  - `reports/audio/audio_audit_gui_stage3_baseline48_session/`

- 这意味着:
  - 项目当前已经正式进入
    `GUI + proxy bundle`
    的人工听审阶段
  - 但“听审结论”本身
    仍需要用户实际试听后才能形成

先说人话:
- 现在不是“我帮你拼好几条命令，你自己想办法记记录”。
- 现在已经有一个能直接打开、能接着上次进度继续听、还能把结果导出的 GUI 入口了。
- 阶段上已经进入人工听审，
  但真正的主观结论还是得靠你听。

### 更新后的下一阶段任务
1. 由用户使用 GUI
   对当前 Stage3 validation / special bundles
   做首轮正式人工听审
2. 产出并回收:
   - `audio_audit_review.json`
   - `audio_audit_review.md`
3. 根据听审结果，
   再决定是:
   - 继续拉长 Stage3 horizon
   - 还是优先修 student / teacher 结构 gap

### 文档补充
- `docs/163_stage3_audio_audit_gui_bootstrap_report.md`
  - GUI 正式入口、修复项与当前使用方式
- `docs/164_stage3_audio_audit_gui_smoke_test_and_human_review_kickoff_report.md`
  - smoke test、会话目录与人工听审启动状态

## 2026-03-17 Stage3 audio audit loudness-match 修正更新

### 当前进度补充
429. 已完成: 修正 Stage3 proxy bundle 中
   - `teacher_proxy`
   - `student_proxy`
   的全局响度不一致问题
430. 已完成: 在导出链路中新增
   - 同记录 teacher/student 成对响度匹配
   - 匹配元数据回写到 `proxy_audio_export.json/.md`
431. 已完成: 重导当前正式听审 bundle
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
   - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
432. 已完成: 验证重导后的 teacher/student
   在同一条记录内 RMS 已对齐到
   - `delta_db ~= 0`
433. 已完成: 新增正式文档
   - `docs/165_stage3_audio_audit_loudness_match_fix_report.md`

### 当前阶段结论补充
- 之前 Stage3 proxy bundle
  的主要问题不是:
  - GUI 播放器本身音量错乱
- 而是:
  - 导出时 teacher/student
    各自按原始代理幅度直接写 wav
  - 没做听审口径下的全局响度对齐

- 这会导致:
  - 人耳在比较结构差异前，
    先被 2 到 5 dB 级别的总体音量差干扰

- 当前修正后:
  - 同一条记录里的
    `teacher_proxy.wav`
    与
    `student_proxy.wav`
    会先做成对 loudness match
  - 只消除全局播放音量偏置，
    不改每条内部的能量起伏轮廓

先说人话:
- 之前的问题不是“模型一定更差”，
  而是“一个更响，一个更轻”，
  人耳很容易被这种差别带偏。
- 现在导出的试听包里，
  teacher 和 student
  已经被拉到同一档音量，
  再听时更接近在比结构，
  而不是在比谁更响。

### 更新后的下一阶段任务
1. 继续使用当前正式会话目录
   - `reports/audio/audio_audit_gui_stage3_baseline48_session/`
   做人工听审
2. 听审时以重导后的 bundle 为准，
   不再参考旧的未对齐 wav
3. 若后续再导出新的 Stage3 bundle，
   默认沿用当前 loudness-match 规则

### 文档补充
- `docs/165_stage3_audio_audit_loudness_match_fix_report.md`
  - 问题来源、修复方式、重导命令与验证结果

## 2026-03-17 Stage3 proxy 音调对齐与适用边界复核更新

### 当前进度补充
434. 已完成: 复核 Stage3 proxy synthesis
   的载频定义，
   确认当前使用固定 carrier
   - `185 Hz`
435. 已完成: 对当前正式 validation / special bundle
   做 dominant-frequency 检查，
   确认同记录 teacher/student
   的 `delta = 0.000 Hz`
436. 已完成: 对当前 bundle
   做频带集中度复核，
   确认 proxy 主体能量高度集中在
   - `150-230 Hz`
437. 已完成: 更新 GUI 帮助文本，
   明确当前 proxy
   不适合做音节级判断
438. 已完成: 新增正式文档
   - `docs/166_stage3_proxy_pitch_alignment_and_applicability_check_report.md`

### 当前阶段结论补充
- 这次用户听到的
  “几乎都是单调频率”
  不是:
  - teacher/student pitch 没对齐
- 而是:
  - 当前 proxy 合成
    本来就用固定载频
  - 它天生就更像
    低频结构监听信号

- 当前可以明确确认:
  - teacher_proxy
  - student_proxy
    在 pitch / carrier 上
    没有新的额外偏差

- 但同时也必须收紧口径:
  - 当前 proxy
    仍可用于:
    - 停顿
    - 包络
    - 稳定性
      的粗审核
  - 不再适合被解释成:
    - 音节结构代理
    - 可懂度代理

先说人话:
- 这次不是“一个更高一个更低”。
- 更准确地说，
  它俩都被固定在差不多同一个调子上，
  所以当然会听起来像单调嗡声。
- 这能避免 pitch 带偏，
  但也说明这版 proxy
  只能听很粗的结构，
  听不了音节。

### 更新后的下一阶段任务
1. 当前人工听审若继续进行，
   只把结论限定在:
   - 停顿
   - 能量包络
   - 稳定性
2. 若下一步需要判断
   - 音节结构
   - 可懂度
   则应优先改 proxy 表达，
   而不是继续拿当前 bundle 硬听
3. 后续若继续沿 Stage3 听审主线推进，
   需要单独设计:
   - 更有音节感的 proxy
   - 或非音频可视化辅助手段

### 文档补充
- `docs/166_stage3_proxy_pitch_alignment_and_applicability_check_report.md`
  - 固定载频事实、dominant-frequency 复核、频带集中度结果与适用边界

## 2026-03-17 Stage3 proxy audio 首轮人工听审结果更新

### 当前进度补充
439. 已完成: 读取正式听审导出
   - `reports/audio/audio_audit_gui_stage3_baseline48_session/audio_audit_review.json`
   - `reports/audio/audio_audit_gui_stage3_baseline48_session/audio_audit_review.md`
440. 已完成: 记录用户对首轮 Stage3 proxy bundle
   的正式主观结论
441. 已完成: 新增正式文档
   - `docs/167_stage3_proxy_audio_human_review_round1_report.md`

### 当前阶段结论补充
- 当前 `6 / 6` 条记录
  都被标记为:
  - 可比较

- 用户当前正式结论是:
  - `student` 除了有一定毛刺感之外，
    与 `teacher` 基本差不多
  - 未填写的条目，
    解释为:
    - 平手

- 当前汇总结果为:
  - `best_rhythm`
    - teacher 明确胜出 `2`
    - 其余 `4` 条平手
  - `best_boundary`
    - `6` 条全部平手
  - `most_stable`
    - teacher 胜出 `6 / 6`
  - `overall_pick`
    - teacher 胜出 `6 / 6`

- 这说明:
  - 当前 student
    已经大体跟上 teacher
  - 但剩余差距
    主要集中在:
    - 毛刺
    - 瞬态更不稳
    - 整体平滑性偏弱

先说人话:
- 这轮听下来，
  不是“student 完全不行”，
  也不是“已经和 teacher 没差别”。
- 更接近的真实状态是:
  - 大方向已经接近
  - 但 teacher 还是更稳，
    student 还有毛刺感

### 更新后的下一阶段任务
1. 后续若继续沿当前 Stage3 主线推进，
   优先考虑:
   - student 毛刺 / 稳定性
     的改进
2. 不再把主要注意力放在:
   - teacher/student 是否已经完全脱轨
   因为当前人工听审不支持这个判断
3. 若下一轮要继续做人工 gate，
   仍需注意:
   - 当前 proxy 不适合判断音节级结构

### 文档补充
- `docs/167_stage3_proxy_audio_human_review_round1_report.md`
  - 首轮正式人工听审的导出结果、用户主观结论与当前主线启发

## 2026-03-17 Stage3 proxy 稳定性 probe 与 temporal supervision 更新

### 当前进度补充
442. 已完成: 对当前 Stage3 主线追加 proxy-level 动态 probe，
   确认毛刺更可能与
   - proxy 动态变化
   尤其是
   - `delta_energy`
     有关
443. 已完成: 把 Stage3 `proxy_acoustic`
   提炼为共享 helper
   - `src/v5vc/streaming_student/proxy_acoustic.py`
444. 已完成: 为 Stage3 teacher supervision
   新增两项可开关 loss
   - `teacher_proxy_acoustic`
   - `teacher_proxy_temporal`
445. 已完成: 跑通三组 `12-step full-validation`
   短程对照
   - `proxyacoustic020`
   - `proxytemporal020`
   - `proxytemporal50`
446. 已完成: 为当前更值得复听的分支
   `proxytemporal50`
   导出新一轮 proxy bundle
447. 已完成: 新增正式文档
   - `docs/168_stage3_proxy_stability_probe_and_temporal_supervision_report.md`

### 当前阶段结论补充
- 当前自动 probe 支持这样一个更细的判断:
  - “student 有毛刺”
    不是空泛印象
  - 它更可能与
    proxy-level 动态变化
    有关

- `proxyacoustic020`
  的结果说明:
  - 把 proxy feature 本身拉近 teacher
    是可行的
  - validation 改善最多
  - 但这还不等于
    人耳毛刺就真的更少

- `proxytemporal020`
  基本等于没动，
  原因主要是:
  - raw temporal loss
    量级太小
  - `0.2`
    权重几乎起不到训练作用

- `proxytemporal50`
  的结果说明:
  - 当 temporal supervision
    提到足够量级后，
    validation / special
    都能出现小幅改善
  - 但当前自动 jitter probe
    还没给出“毛刺必然更少”的硬证据

先说人话:
- 这轮不是白忙。
- 它把问题进一步缩小成:
  - 不是简单多加一点 supervision
    就自然更稳
  - 也不是完全没得调
- 现在最合理的动作
  是拿更对症的
  `proxytemporal50`
  去做下一轮复听，
  而不是光盯着 loss 数字就拍板

### 更新后的下一阶段任务
1. 对
   - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
   - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`
   做一轮定向复听
2. 重点只比较:
   - baseline48 step48
   vs
   - proxytemporal50 step12
   在毛刺 / 稳定性上的差异
3. 若人耳确认 `proxytemporal50`
   更稳，
   再考虑把 temporal supervision
   扩到更长 horizon
4. 若人耳没有确认改善，
   下一步应转向:
   - 更直接的 proxy 重建平滑策略
   - 或训练外的重建侧去毛刺手段

### 文档补充
- `docs/168_stage3_proxy_stability_probe_and_temporal_supervision_report.md`
  - probe 依据、新增 loss、三组短程对照、结果解释与下一步建议

## 2026-03-17 Stage3 上下文恢复续接与 `proxytemporal50` 听审启动更新

### 当前进度补充
448. 已完成: 按 `UTF-8` 明确读取
   - `docs/00_context_bootstrap.md`
   并结合近期 Stage3 文档、
   代码入口和产物目录
   恢复当前真实工作状态
449. 已完成: 确认当前真实停点
   已不是:
   - GUI 未集成
   - baseline48 首轮听审待做
   而是:
   - `proxytemporal50`
     候选 bundle
     已导出、待正式复听
450. 已完成: 为
   - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
   - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`
   创建正式 GUI 会话目录
   - `reports/audio/audio_audit_gui_stage3_proxytemporal50_session/`
451. 已完成: 用
   `.\python.exe manage.py launch-audio-audit-gui`
   对上述新会话做自动关闭 smoke test，
   成功写出:
   - `audio_audit_progress.json`
452. 已完成: 新增正式续接报告
   - `docs/169_stage3_context_restore_continuation_and_proxytemporal50_audit_kickoff_report.md`

### 当前阶段结论补充
- 当前接班后确认的真实主线是:
  - baseline48 首轮听审
    已经完成
  - `proxytemporal50`
    已是当前最值得继续复听的候选
  - 下一步工作
    应直接围绕它的人耳结论展开

- 这次恢复时最容易误判的点是:
  - 看到
    `docs/162`
    就以为 GUI 仍未闭环
  - 但后续
    `docs/163 ~ 168`
    已经把:
    - GUI 接入
    - smoke test
    - baseline48 听审
    - `proxytemporal50` 候选导出
      全部补齐

先说人话:
- 现在不是“还得先把工具修好”。
- 工具已经够用了，
  候选试听包也已经有了。
- 当前最值钱的下一步，
  就是让
  `proxytemporal50`
  进入正式人工复听，
  看它是不是真的比 baseline48 更稳。

### 更新后的下一阶段任务
1. 直接启动:
   - `reports/audio/audio_audit_gui_stage3_proxytemporal50_session/`
   对
   `proxytemporal50`
   做正式复听
2. 复听重点保持在:
   - 毛刺
   - 瞬态稳定性
   - 能量起伏
3. 若人耳确认它更稳，
   再考虑把 temporal supervision
   扩到更长 horizon
4. 若人耳没有确认改善，
   下一步转回:
   - 更直接的 proxy 平滑策略
   - 或重建侧去毛刺手段

### 文档补充
- `docs/169_stage3_context_restore_continuation_and_proxytemporal50_audit_kickoff_report.md`
  - 本次恢复读取范围、当前真实停点、`proxytemporal50` 会话创建结果与继续方式

## 2026-03-17 Stage3 baseline48 vs `proxytemporal50` 人工复听结果更新

### 当前进度补充
453. 已完成: 建立并完成
   - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal50_session/`
   的正式人工复听
454. 已完成: 明确本轮比较口径
   - 两个 `teacher_proxy`
     只作锚点，
     不作为主要胜负对象
   - 主体只在两个
     `student_proxy`
     之间比较
455. 已完成: 记录本轮人工约定
   - 未选择的维度
     解释为:
     平手 / 无明显差异
456. 已完成: 新增正式结果报告
   - `docs/170_stage3_baseline48_vs_proxytemporal50_human_review_report.md`

### 当前阶段结论补充
- 本轮人耳结果不是
  `proxytemporal50`
  全面胜出，
  也不是全面失败

- 当前更准确的结论是:
  - baseline48
    在 validation 三条里，
    对:
    - 节奏
    - 边界
    - 综合
      更占优
  - `proxytemporal50`
    在 special 两条里，
    对:
    - 稳定性
    - 综合
      更占优
  - 另有一条 special
    基本无差别

- 这说明:
  - temporal supervision
    方向不是错的
  - 但当前
    `weight = 50`
    的短程版本
    还带着:
    - validation 侧边界代价
    - 不能直接替代默认基线

先说人话:
- 这轮听审给出的答案不是
  “换了就更好”，
  而是
  “有些地方更稳，
   但也把有些地方搞糊了”。
- 所以现在不能直接把
  `proxytemporal50`
  升级成默认主线。

### 更新后的下一阶段任务
1. 继续保留:
   - baseline48
     作为当前默认 Stage3 checkpoint
2. 若继续深挖 temporal supervision，
   下一步优先尝试:
   - 更温和的权重
   - 更细的 schedule
   - 或局部化的稳定性约束
3. 暂不直接把:
   - `proxytemporal50`
     拉长到更长 horizon
   因为当前人耳证据
   不支持直接升级

### 文档补充
- `docs/170_stage3_baseline48_vs_proxytemporal50_human_review_report.md`
  - 本轮 A/B 听审口径、单条结果、总判断与下一步建议

## 2026-03-17 Stage3 `proxytemporal20 + warmup6` schedule probe 更新

### 当前进度补充
457. 已完成: 为 Stage3 training loop
   新增 loss-weight schedule 支持，
   当前已支持:
   - `linear_warmup_hold`
458. 已完成: 把每一步实际生效的
   loss weights
   写入:
   - step history
   - validation history
   - checkpoint metadata
459. 已完成: 新增温和 temporal 配置
   - `configs/streaming_student_loss_weights_proxytemporal20_warmup6_v1.json`
460. 已完成: 跑通
   - `streaming_student_stage_loop_proxytemporal20warm6_fullval12_v1`
   的正式 `12-step full-validation`
   对照
461. 已完成: 产出 checkpoint ranking 与 fuller eval
   - `reports/eval/streaming_student_checkpoint_selection_proxytemporal20warm6_fullval12_v1/`
   - `reports/eval/streaming_student_checkpoint_eval_proxytemporal20warm6_fullval12_v1/`
462. 已完成: 导出新的 proxy bundle
   并建立下一轮 A/B 听审会话
   - `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_v1/`
   - `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_special_v1/`
   - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`
463. 已完成: 新增正式报告
   - `docs/171_stage3_proxytemporal20_warmup_schedule_probe_report.md`

### 当前阶段结论补充
- 这轮推进不再只是
  “换一个常数权重再试”
- 当前已经把 Stage3
  temporal supervision
  推到:
  - 可做 step-level warmup
  - 可记录实际有效权重
  - 可正式复现

- 第一条温和 schedule 候选
  当前结果是:
  - 比 baseline12
    在统一参考权重下
    略好
  - 但没有超过
    `proxytemporal50`
    的自动指标改善幅度

- 更准确地说:
  - `proxytemporal50`
    还是更强刺激
  - `proxytemporal20 + warmup6`
    则更像
    “把副作用往回收”的版本

先说人话:
- 现在不是在原地兜圈子。
- 这次已经补出了
  “更温和 temporal 方案”
  所需要的正式工程能力，
  也已经拿到第一条可听的候选。
- 下一步最值钱的，
  就是看它在人耳上
  能不能比
  `proxytemporal50`
  更稳妥地接近 baseline48。

### 更新后的下一阶段任务
1. 对
   - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`
   做下一轮 A/B 复听
2. 重点观察:
   - 是否比 baseline48
     少掉节奏/边界副作用
   - 是否还能保留
     一部分稳定性收益
3. 若人耳仍不支持，
   下一步再考虑:
   - 更短 warmup
   - 更低峰值
   - 或局部化 temporal 约束

### 文档补充
- `docs/171_stage3_proxytemporal20_warmup_schedule_probe_report.md`
  - schedule 能力、温和 temporal 实验、数值对照、新试听包与新会话入口

## 2026-03-17 Stage3 proxy 静音泄漏审计与导出修正更新

### 当前进度补充
464. 已完成: 对 baseline48 / warm20
   当前试听 bundle
   做静音段量化复核，
   确认:
   - `teacher_proxy`
     旧版也存在静音底噪
465. 已完成: 在
   - `src/v5vc/proxy_audio_export.py`
   为 proxy 合成新增静音 gate，
   压低极低活动帧的系统性伪底噪
466. 已完成: 新增 export 专用的
   student proxy 映射，
   避免低能量静音帧
   被 `event / voiced`
   直接抬成有声帧
467. 已完成: 重导当前将用于试听的
   baseline48 / warm20
   validation + special bundles
468. 已完成: 复核并保留当前 A/B 会话入口
   - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`
469. 已完成: 新增正式报告
   - `docs/172_stage3_proxy_silence_leakage_audit_and_export_fix_report.md`

### 当前阶段结论补充
- 用户提出的
  “teacher 在静音段也有底噪”
  不是错觉
- 旧版 bundle
  确实被导出链本身
  带入了静音伪底噪

- 当前修正后的更准确状态是:
  - `teacher_proxy`
    的静音伪底噪
    已明显降低
  - warm `student_proxy`
    也改善了，
    但相较 baseline
    仍更容易在静音段保留活动

先说人话:
- 之前那部分“静音也在响”的问题，
  不是你听错了。
- 其中有一大块确实是我们导出工具自己造出来的，
  现在已经先修掉。
- 眼下如果再听到 warm 更吵，
  就更值得把它当成模型真实问题来看。

- 当前同时可以明确排除的一点是:
  - 这次旧版合成器的最小底噪
    没有直接污染 Stage3 训练本身
  - 因为它只存在于导出/试听链
  - 不存在“因此必须回头重训 baseline48”
    这种情况

### 更新后的下一阶段任务
1. 若继续 A/B 试听，
   必须以修正后的 bundle 为准
2. 继续使用:
   - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`
3. 若人耳仍确认 warm
   在静音段更容易出声，
   下一步应把问题正式收敛到:
   - Stage3 静音稳定性 / 静音抑制

### 文档补充
- `docs/172_stage3_proxy_silence_leakage_audit_and_export_fix_report.md`
  - 量化证据、根因拆解、导出修正与当前试听建议

## 2026-03-17 Stage3 baseline48 默认参数重跑复现确认更新

### 当前进度补充
470. 已完成: 按 Stage3
   当前正式默认参数
   重新执行一遍
   `baseline48 full-validation`
   训练，
   新实验 id 为:
   - `streaming_student_stage_loop_baseline48_fullval_rerun_v1`
471. 已完成: 对 rerun 的
   `step12 / step24 / step36 / step48`
   补做 checkpoint selection
472. 已完成: 对 rerun 的
   `step48`
   补做 full checkpoint eval
473. 已完成: 对比原始
   `baseline48_fullval_v1`
   与 rerun 的
   - step 级 record 顺序
   - step 级 `loss_total`
   - validation 级 record 顺序
   - validation 级 `loss_total`
   均完全一致
474. 已完成: 对比原始 run
   与 rerun 的 checkpoint 内容，
   确认:
   - 文件哈希不同
   - 但 `model_state_dict`
     四个 step
     都逐元素完全一致
475. 已完成: 新增正式报告
   - `docs/173_stage3_baseline48_default_rerun_reproducibility_report.md`

### 当前阶段结论补充
- 这次“按默认参数直接重跑”
  已经做完了，
  结果不是新候选，
  而是复现确认

- 当前可确认:
  - `baseline48_fullval_v1`
    与
    `baseline48_fullval_rerun_v1`
    在训练轨迹、
    checkpoint selection、
    final eval
    上都完全一致
  - checkpoint 文件哈希不同，
    只是因为 run metadata
    不同，
    不是训练漂移

先说人话:
- 这次不是“重跑后自然变好了”。
- 也不是“同参多跑一遍能把静音问题洗掉”。
- 更准确的结论是:
  当前 baseline48
  本来就稳定可复现，
  所以如果下一步还要继续训练，
  必须换真正新的假设，
  而不是继续做同参 rerun。

### 更新后的下一阶段任务
1. 当前默认 Stage3 checkpoint
   继续保持:
   - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
2. 若继续训练实验，
   下一步优先转向:
   - Stage3 静音稳定性 / 静音抑制
   - 或更局部化的 temporal 约束
3. 不再优先做:
   - 同一默认参数的重复 rerun

### 文档补充
- `docs/173_stage3_baseline48_default_rerun_reproducibility_report.md`
  - 默认参数重跑命令、复现结果、checkpoint 内容比对与下一步判断

## 2026-03-17 teacher 本机 runtime feasibility probe 更新

### 当前进度补充
476. 已完成: 对当前正式
   offline teacher
   `D87 step200`
   做本机 runtime probe，
   目标是判断:
   - 是否还需要
     继续依赖 student 线
     解决速度问题
477. 已完成: 同时复核
   teacher 结构边界，
   确认:
   - runtime 配置里
     `uses_text_in_runtime = false`
   - 主控制路径没有
     RNN / attention /
     整句级 future stack
478. 已完成: 在当前机器上
   对 `74` 条
   validation + special
   样本做单条推理 benchmark，
   结果落盘到:
   - `reports/eval/offline_mvp_teacher_runtime_probe_current_machine_d87/teacher_runtime_probe.json`
479. 已完成: 新增正式报告
   - `docs/174_stage3_teacher_runtime_feasibility_probe_report.md`

### 当前阶段结论补充
- 现在可以明确说:
  - teacher 速度不是瓶颈

- 当前本机实测下:
  - CPU:
    - `avg_latency_ms = 6.952321`
    - `p95_latency_ms = 11.633498`
    - `avg_rtf = 0.003812657`
  - GPU:
    - `avg_latency_ms = 1.481529`
    - `p95_latency_ms = 2.46726`
    - `avg_rtf = 0.000949361`

- 配合当前帧设置:
  - `sample_rate = 44100`
  - `frame_length = 400`
  - `hop_length = 160`
  - `hop_ms = 3.628118`
- 这说明 teacher
  作为控制预测器，
  已明显快于实时预算

先说人话:
- 这条 student 线
  现在不能再拿
  “teacher 太慢”
  当主理由了。
- 如果只是为了
  下一环节的控制预测，
  当前更合理的动作
  是直接用 teacher，
  暂停继续训练 student。

### 更新后的下一阶段任务
1. 暂停把
   Stage3 student 训练
   作为当前最高优先级
2. 直接以当前正式 teacher
   作为下一环节的
   控制预测基线
3. 工程上优先转向:
   - teacher runtime wrapper
   - teacher 控制输出接线
   - 最小在线缓存 / 滑窗接口
4. 只有在后续明确出现:
   - 部署约束
   - 统一前端需求
   - `r_res` 路线需求
   时，
   再重新评估
   student 线必要性

### 文档补充
- `docs/174_stage3_teacher_runtime_feasibility_probe_report.md`
  - 本机 benchmark、结构适配性判断与是否可跳过 student 的正式结论

## 2026-03-17 teacher-first runtime wrapper 落地更新

### 当前进度补充
480. 已完成: 正式新增
   teacher runtime 模块
   - `src/v5vc/offline_teacher_runtime.py`
481. 已完成: 正式新增 CLI
   - `run-offline-mvp-teacher-runtime`
   支持:
   - 分块输入
   - 尾样本缓存
   - 控制张量导出
   - full-pass 一致性验证
482. 已完成: 对短样本
   `chapter3_3_firefly_162`
   做 runtime smoke test，
   验证:
   - `streaming_frame_count = 167`
   - `frame_count_equal = true`
   - `frame_alignment_equal = true`
483. 已完成: 对 2 秒长样本
   `chapter3_2_firefly_178`
   做更严格 smoke test，
   验证:
   - `streaming_frame_count = 549`
   - 各控制张量
     都满足
     `allclose_atol_5e-6 = true`
484. 已完成: 新增正式报告
   - `docs/175_teacher_runtime_wrapper_and_streaming_smoke_test_report.md`

### 当前阶段结论补充
- 现在主线已经不是
  “建议以后考虑 teacher-first”
- 而是:
  - teacher-first
    已经落到
    正式可跑命令

- 当前可以正式依赖:
  - `run-offline-mvp-teacher-runtime`
    导出的控制张量
    作为下一环节输入

先说人话:
- 这一步已经不再停留在判断题。
- student 线现在确实可以先放下。
- 当前最小可用 teacher runtime
  已经在真实音频上
  跑通并对齐了整句前向。

### 更新后的下一阶段任务
1. 明确以下产物
   作为下一环节默认入口:
   - `run-offline-mvp-teacher-runtime`
   - `teacher_runtime_streaming_outputs.pt`
2. 下一步继续转向:
   - 下游模块输入合同
   - teacher 控制输出接线
3. 不再把
   Stage3 student 训练
   作为当前主任务

### 文档补充
- `docs/175_teacher_runtime_wrapper_and_streaming_smoke_test_report.md`
  - wrapper 设计、CLI、新 smoke test 与当前主线切换结果

## 2026-03-17 teacher downstream control contract 更新

### 当前进度补充
485. 已完成: 新增
   teacher-first 下游输入合同模块
   - `src/v5vc/offline_teacher_downstream_contract.py`
486. 已完成: 新增 CLI
   - `export-offline-mvp-teacher-downstream-contract`
487. 已完成: 把当前 teacher
   可稳定提供的字段
   与 calibration 条件
   打包成正式 contract，
   并显式列出:
   - 当前可用字段
   - proxy 字段
   - 当前缺失字段
488. 已完成: 对样本
   `chapter3_3_firefly_162`
   导出 smoke contract，
   产物落盘到:
   - `reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/`
489. 已完成: 新增正式报告
   - `docs/176_teacher_downstream_control_contract_report.md`

### 当前阶段结论补充
- 现在主线默认入口
  应进一步明确成:
  - `export-offline-mvp-teacher-downstream-contract`

- 当前这份 contract
  已足以支撑
  “下游模块先开始接线”，
  因为它同时提供了:
  - teacher 控制帧
  - 目标说话人 calibration 条件
  - 明确的缺失项说明

先说人话:
- 现在不只是“teacher 跑得动”。
- 也不只是“teacher 能分块输出”。
- 而是下一环节已经有了
  一份可读、可落盘、可复用的
  正式输入包。

### 更新后的下一阶段任务
1. 后续下游模块
   默认读取:
   - `teacher_downstream_control_contract.pt`
2. 当前更合适的开发方向是:
   - 基于这份 contract
     接下游消费者
3. 在真正开始
   Stage5 vocoder 开发前，
   不要把当前 contract
   误写成:
   - 最终 `F0 / vuv / aper / E / r_res`
     全量条件合同

### 文档补充
- `docs/176_teacher_downstream_control_contract_report.md`
  - contract 字段定义、proxy 边界、smoke 导出与当前默认入口

## 2026-03-17 no-residual vocoder scaffold bootstrap 更新

### 当前进度补充
490. 已完成: 新增
   consumer-side vocoder input scaffold
   - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
491. 已完成: 新增 CLI
   - `build-offline-mvp-teacher-vocoder-input-scaffold`
492. 已完成: 新增
   no-residual source-filter vocoder scaffold
   - `src/v5vc/offline_vocoder_scaffold.py`
493. 已完成: 新增 CLI
   - `prepare-offline-mvp-nores-vocoder-scaffold`
494. 已完成: 基于真实 teacher contract
   跑通 consumer-side scaffold
   与 no-residual vocoder scaffold
   的 dry-run
495. 已完成: 新增正式报告
   - `docs/177_nores_vocoder_scaffold_bootstrap_report.md`

### 当前阶段结论补充
- 现在 Stage5
  不再是纯设计稿
- 当前仓库已经具备:
  - teacher-first contract
  - consumer-side branch scaffold
  - no-residual vocoder scaffold

先说人话:
- 这一步已经把“下一环节”
  从接口讨论
  推到了真正的代码锚点。
- 后面再往前走，
  就是补训练合同和 decoder，
  而不是再去争论入口叫什么。

### 更新后的下一阶段任务
1. 基于
   `prepare-offline-mvp-nores-vocoder-scaffold`
   补最小训练合同
2. 继续坚持:
   - no-residual baseline
   先行
3. 在显式 `f0_hz / r_res`
   还没补齐前，
   不要提前把这条 scaffold
   误写成 final vocoder

### 文档补充
- `docs/177_nores_vocoder_scaffold_bootstrap_report.md`
  - Stage5 scaffold 代码入口、dry-run 结果与当前边界

## 2026-03-17 no-residual vocoder 最小训练合同与单步 smoke 更新

### 当前进度补充
496. 已完成: 基于
   `offline_teacher_vocoder_input_scaffold`
   新增 Stage5 最小训练目标构建模块
   - `src/v5vc/offline_vocoder_training.py`
497. 已完成: 新增 CLI
   - `build-offline-mvp-nores-vocoder-train-targets`
498. 已完成: 新增 CLI
   - `run-offline-mvp-nores-vocoder-train-step`
499. 已完成: 为 teacher downstream contract
   与 consumer-side scaffold
   补齐:
   - `input_audio_path`
   - `source_audio_path`
   - `runtime sample_rate/frame_length/hop_length`
   等对齐元数据，
   以支持后续训练目标构建
500. 已完成: 以真实样本
   `chapter3_3_firefly_162.wav`
   跑通:
   - contract v2 重导
   - vocoder input scaffold 重建
   - no-residual train targets 构建
   - no-residual 单步 train step smoke
501. 已完成: 新增正式报告
   - `docs/178_nores_vocoder_training_contract_and_single_step_smoke_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经不只是:
  - teacher-first contract
  - branch scaffold
  - shape-only dry-run

- 当前仓库还已经具备:
  - 最小 spectral/gate train-target package
  - 单步反向传播
  - optimizer / grad clipping / checkpoint
    的正式 smoke 验证

先说人话:
- 这次已经把
  “Stage5 训练到底有没有入口”
  这个问题回答成:
  - 有
- 但它现在回答的是
  “训练 plumbing 已成立”，
  不是
  “声码器已经能出最终音频”。

### 更新后的下一阶段任务
1. 在当前
   proxy spectral/gate contract
   之上，
   补最小多步训练循环
2. 在补 loop 之前或同时，
   明确下一步主目标是:
   - 继续走频域 envelope 重建
   - 还是切到更接近 waveform 的 decoder 目标
3. 继续坚持:
   - no-residual baseline
   先行，
   不把当前 proxy target
   误写成 final vocoder objective

### 文档补充
- `docs/178_nores_vocoder_training_contract_and_single_step_smoke_report.md`
  - 最小训练包格式、单步训练 smoke 结果与当前 Stage5 边界

## 2026-03-17 no-residual vocoder 最小多步 loop smoke 更新

### 当前进度补充
502. 已完成: 在
   `src/v5vc/offline_vocoder_training.py`
   上新增最小多步训练 loop
503. 已完成: 新增 CLI
   - `run-offline-mvp-nores-vocoder-training-loop`
504. 已完成: 支持
   - step history
   - validation history
   - checkpoint series
   - best checkpoint 选择
   的正式落盘
505. 已完成: 用
   `chapter3_3_firefly_162`
   对同一 train-target package
   跑通 `3-step` loop smoke
506. 已完成: 新增正式报告
   - `docs/179_nores_vocoder_training_loop_smoke_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经不只具备:
  - 单步 backward smoke
- 还已经具备:
  - 最小可迭代训练 loop
  - step / validation / checkpoint
    的持续记录能力

先说人话:
- 这表示 Stage5
  不会再卡在
  “能训一下，但不能持续跑”。
- 但当前 loop
  仍只是拿
  一个对齐好的 package
  反复练手，
  主要验证 plumbing，
  不是正式数据集训练。

### 更新后的下一阶段任务
1. 从
   单 package loop
   进入:
   - 多 package / dataset-level
     采样训练
2. 同步准备:
   - 独立 validation package
   避免继续把
   `train_targets_reused`
   当成泛化结论
3. 在此基础上，
   再决定下一步主目标更偏向:
   - spectral/gate proxy
   - 还是更接近 waveform 的 decoder 重建

### 文档补充
- `docs/179_nores_vocoder_training_loop_smoke_report.md`
  - 最小多步 loop、3-step smoke 结果与当前 Stage5 可迭代边界

## 2026-03-17 no-residual vocoder dataset path smoke 更新

### 当前进度补充
507. 已完成: 将
   `src/v5vc/offline_vocoder_training.py`
   中已存在的 dataset-level package builder
   正式接入 CLI
   - `build-offline-mvp-nores-vocoder-dataset-packages`
508. 已完成: 将
   dataset-level training loop
   正式接入 CLI
   - `run-offline-mvp-nores-vocoder-dataset-training-loop`
509. 已完成: 基于
   `round1_1` 正式 split
   跑通最小 dataset package 物化，
   产出:
   - `offline_mvp_nores_vocoder_dataset_index.json/.md`
510. 已完成: 用
   `2 train + 1 validation`
   package
   跑通 Stage5 dataset-level
   `3-step` smoke
511. 已完成: 新增正式报告
   - `docs/180_nores_vocoder_dataset_path_smoke_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经不只具备:
  - 单 package train-target
  - 单 package loop
- 还已经具备:
  - split-backed dataset package builder
  - dataset index
  - 多 package 采样训练 loop
  - 独立 validation package

先说人话:
- 这表示 Stage5
  已经从
  “拿一个包反复练手”
  走到了
  “可以沿正式 split
     组织 dataset 训练”。
- 但现在回答的仍是
  “dataset plumbing 成立”，
  不是
  “全量训练吞吐已经优化好”。

### 更新后的下一阶段任务
1. 把当前 dataset path
   从超小 subset smoke
   推到更大的 split-backed package 池
2. 补清:
   - package export 耗时
   - package cache / loader
     的必要性
3. 在 dataset path
   稳定后，
   再决定下一步主目标更偏向:
   - 继续保留 spectral/gate proxy
   - 还是切向 decoder / waveform-STFT
     重建

### 文档补充
- `docs/180_nores_vocoder_dataset_path_smoke_report.md`
  - Stage5 dataset builder、dataset loop、最小 split-backed smoke 与当前边界

## 2026-03-17 no-residual vocoder dataset throughput probe 更新

### 当前进度补充
512. 已完成: 在
   `src/v5vc/offline_vocoder_training.py`
   为 Stage5 dataset index
   补充:
   - package_build_sec
   - package_size_bytes
   - timing
   - split summary
513. 已完成: 用
   `shortest_duration`
   跑通
   `8 train + 2 validation`
   lower-bound throughput probe
514. 已完成: 用
   `file_order`
   跑通
   `3 train + 1 validation`
   较长样本对照 probe
515. 已完成: 用
   `8 train + 2 validation`
   package 池跑通
   `4-step` dataset loop probe
516. 已完成: 新增正式报告
   - `docs/181_nores_vocoder_dataset_throughput_probe_report.md`

### 当前阶段结论补充
- 现在 Stage5
  不只知道:
  - dataset path 能不能跑
- 还已经开始知道:
  - 每包大概多大
  - 每包大概多久
  - 短句与较长样本的导出边界差异

先说人话:
- 这一步把
  “有没有 dataset path”
  往前推进成了
  “这条 path 大概要花多少代价”。
- 现在最需要判断的，
  已经不是命令有没有，
  而是后面要不要补
  package cache / packed loader。

### 更新后的下一阶段任务
1. 做更接近 full split
   的 package export 预算
2. 评估是否需要优先补:
   - package cache
   - packed loader
   - frame bucket
3. 在 throughput 边界清楚后，
   再决定 Stage5
   是否继续沿 proxy target
   稳定化，
   还是切向 decoder / waveform-STFT
   目标

### 文档补充
- `docs/181_nores_vocoder_dataset_throughput_probe_report.md`
  - Stage5 dataset index 统计字段、throughput probe、loop probe 与当前边界

## 2026-03-17 no-residual vocoder full-split export budget 更新

### 当前进度补充
517. 已完成: 统计
   `round1_1`
   正式 target split
   的总记录数与总音频时长
518. 已完成: 基于
   shortest probe
   与 file-order probe
   做 Stage5 package export
   的最小线性粗拟合
519. 已完成: 给出
   `target_train + target_validation`
   的 first-pass full-split
   导出预算
   - `~194 sec`
   - `~2.26 GiB`
520. 已完成: 新增正式报告
   - `docs/182_nores_vocoder_fullsplit_export_budget_report.md`

### 当前阶段结论补充
- 现在 Stage5
  不只知道:
  - throughput probe
    大概长什么样
- 还已经对正式 split
  有了 first-pass 预算

先说人话:
- 这一步已经把
  “后面会不会太重”
  从纯感觉
  推到了可量化区间。
- 当前看下来，
  还没有重到
  必须先停下来重写 loader，
  但已经足够提醒我们
  不能对包体积失去警觉。

### 更新后的下一阶段任务
1. 跑更接近 full split
   的 package export 实测
2. 对照预算，
   判断是否需要提前补:
   - cache
   - packed loader
   - bucket 化
3. 若实测仍在可接受区间内，
   继续推进 Stage5
   dataset-level proxy training

### 文档补充
- `docs/182_nores_vocoder_fullsplit_export_budget_report.md`
  - Stage5 正式 split 预算、拟合口径与当前工程判断

## 2026-03-17 no-residual vocoder full-split export measurement 更新

### 当前进度补充
521. 已完成: 对
   `target_train + target_validation`
   跑通 Stage5 full-split package export 实测
522. 已完成: 确认 full-split export
   实测结果为:
   - `253.765723 sec`
   - `2.263 GiB`
523. 已完成: 对同一 full-split package 池
   跑通
   `--skip-existing`
   复用实测
524. 已完成: 确认 package 复用重跑
   只需:
   - `3.983004 sec`
525. 已完成: 新增正式报告
   - `docs/183_nores_vocoder_fullsplit_export_measurement_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已不只是:
  - 有预算
- 还已经有:
  - full-split 实测
  - package 复用实测

先说人话:
- 这一步已经把
  “会不会太重”
  从估算
  推到了真实落地结果。
- 结论是:
  - 首次全量导出不算轻，
    但还能接受
  - 重复使用已有 package
    则非常快

### 更新后的下一阶段任务
1. 直接基于当前 full-split package 池，
   推进 Stage5
   dataset-level proxy training
2. 在训练侧继续观察:
   - 逐包加载
   - validation
   - checkpoint
     是否成为瓶颈
3. 若训练吞吐
   真正开始吃紧，
   再升级:
   - packed loader
   - package cache

### 文档补充
- `docs/183_nores_vocoder_fullsplit_export_measurement_report.md`
  - full-split package export 实测、skip-existing 复用实测与当前优先级判断

## 2026-03-17 no-residual vocoder full-split training baseline 更新

### 当前进度补充
526. 已完成: 基于
   full-split Stage5 package 池
   跑通 dataset-level baseline loop
527. 已完成: 覆盖
   `592 train + 66 validation`
   package 池的正式 baseline
   `6-step` 训练
528. 已完成: 确认 full-split baseline
   支持:
   - 多 package 采样训练
   - 全 validation package 评估
   - checkpoint 落盘
529. 已完成: 新增正式报告
   - `docs/184_nores_vocoder_fullsplit_training_baseline_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已不只是:
  - full-split export ready
- 还已经具备:
  - full-split dataset-level proxy baseline

先说人话:
- 这表示 Stage5
  终于从
  “能导、能估、能复用”
  走到了
  “能基于整套 package 池
     真正开始训练”。
- 当前主线不该再回头
  讨论 export 是否存在，
  而是继续往训练稳定化推进。

### 更新后的下一阶段任务
1. 在 full-split proxy baseline
   上继续拉长训练
2. 视训练侧瓶颈情况，
   再决定是否补:
   - packed loader
   - bucket 化
3. proxy baseline
   稳定后，
   再决定何时切向:
   - decoder / waveform-STFT
     目标

### 文档补充
- `docs/184_nores_vocoder_fullsplit_training_baseline_report.md`
  - Stage5 full-split baseline loop、validation 结果与当前训练停点

## 2026-03-17 Stage5 GPU seed 可复现性与长程 baseline 更新

### 当前进度补充
530. 已恢复: 识别并核对
   尚未写入正式文档的
   Stage5 GPU runtime 产物:
   - `2-step GPU smoke`
   - `12-step GPU baseline`
531. 已完成: 为
   Stage5 no-res vocoder
   三个训练入口
   补齐统一 seed 语义，
   让 seed 同时覆盖:
   - sampler
   - model initialization
   - Torch / CUDA 随机状态
532. 已完成: 基于
   full-split package 池
   跑通
   seeded GPU `24-step`
   baseline
533. 已完成: 继续跑通
   seeded GPU `48-step`
   baseline
534. 已完成: 新增正式报告
   - `docs/185_stage5_gpu_seed_reproducibility_and_long_horizon_baseline_report.md`

### 当前阶段结论补充
- 现在 Stage5
  的真实停点
  已不再是:
  - `6-step` baseline
- 而是:
  - full-split
  - seeded GPU
  - `48-step`
  - long-horizon proxy baseline

先说人话:
- 这一步把
  “已经能训练”
  继续推进成了
  “已经能稳定地在 GPU 上
     拉长训练并持续下降”。
- 当前更像是在逼近
  proxy baseline 的
  更强停点，
  还不是卡在
  loader 基础设施上。

### 更新后的下一阶段任务
1. 若继续沿当前 proxy objective
   推进，
   优先做:
   - 更长 horizon baseline
   - 或 checkpoint review
2. 暂不把主线切回:
   - packed loader
   - cache 重构
3. 当 horizon 收益开始放缓后，
   再决定何时切向:
   - decoder / waveform-STFT
     目标

### 文档补充
- `docs/185_stage5_gpu_seed_reproducibility_and_long_horizon_baseline_report.md`
  - Stage5 GPU 隐藏进展恢复、seed 可复现性补齐与 `48-step` baseline 最新停点

## 2026-03-17 Stage5 seeded GPU baseline96 边际收益复核更新

### 当前进度补充
535. 已完成: 基于同一
   full-split package 池
   跑通 seeded GPU
   `96-step`
   baseline
536. 已完成: 确认 validation
   继续下降到:
   - step24 = `0.469644`
   - step48 = `0.441292`
   - step72 = `0.435399`
   - step96 = `0.432645`
537. 已完成: 确认
   `48 -> 96`
   仍有收益，
   但边际改善
   已明显收窄
538. 已完成: 新增正式报告
   - `docs/186_stage5_seeded_gpu_baseline96_marginal_gain_review_report.md`

### 当前阶段结论补充
- 现在 Stage5
  还不能写成:
  - proxy baseline 已平台化
- 但也不该写成:
  - 继续加步数
    还会保持同样陡的收益

先说人话:
- 这一步说明
  继续训练
  还是有效，
  只是已经开始变成
  “慢慢挤出剩余收益”，
  而不是前面那种
  一拉长就大幅变好。
- 所以下一步更适合
  精细看 checkpoint，
  而不是只靠蛮力翻倍步数。

### 更新后的下一阶段任务
1. 优先做:
   - `96-step`
     checkpoint review
   - 或低频 validation 的更长程 probe
2. 若阶段切换优先级更高，
   也可开始准备:
   - decoder / waveform-STFT
     目标接入
3. 暂不因当前结果
   把主线切回:
   - packed loader
   - cache 重构

### 文档补充
- `docs/186_stage5_seeded_gpu_baseline96_marginal_gain_review_report.md`
  - `96-step` baseline、`48 -> 96` 边际收益判断与当前 Stage5 主线建议

## 2026-03-17 Stage5 checkpoint review 广覆盖收益更新

### 当前进度补充
539. 已完成: 新增
   Stage5 no-res vocoder
   checkpoint review
   可复用入口:
   - `src/v5vc/nores_vocoder_checkpoint_review.py`
   - `review-offline-mvp-nores-vocoder-checkpoints`
540. 已完成: 对
   seeded GPU `96-step`
   summary
   跑通正式 checkpoint review
541. 已完成: 确认
   `24 -> 48`
   为:
   - `66 / 66`
     validation package
     全量改善
542. 已完成: 确认
   `72 -> 96`
   仍为:
   - `66 / 66`
     validation package
     全量改善
543. 已完成: 新增正式报告
   - `docs/187_stage5_checkpoint_review_broad_based_gain_report.md`

### 当前阶段结论补充
- 现在 Stage5
  不只知道:
  - `96-step`
    仍有 marginal gain
- 还知道:
  - 这份 gain
    不是局部样本特例
  - 而是 broad-based gain

先说人话:
- 这一步把
  “平均值在变好”
  进一步核实成了
  “大多数，甚至全部 validation 包
     都在一起变好”。
- 所以当前不能把
  `96-step`
  的收益误写成
  偶然或过拟合式改善。

### 更新后的下一阶段任务
1. 继续优先做:
   - checkpoint review
   - 低频更远程 probe
2. 若要阶段切换，
   当前已有更充分依据
   开始准备:
   - decoder / waveform-STFT
     目标
3. 不把主线切回:
   - loader / cache
     争论

### 文档补充
- `docs/187_stage5_checkpoint_review_broad_based_gain_report.md`
  - Stage5 checkpoint review 入口、broad-based gain 证据与当前判断

## 2026-03-17 Stage5 seeded GPU baseline192 低频长程 probe 更新

### 当前进度补充
544. 已完成: 跑通
   seeded GPU
   `192-step`
   low-frequency probe
545. 已完成: 确认
   validation `loss_total`
   继续下降到:
   - step144 = `0.428461`
   - step192 = `0.425898`
546. 已完成: 对
   `192-step`
   summary
   跑通正式 checkpoint review
547. 已完成: 确认后段收益分布:
   - `96 -> 144`
     为 `65 / 66`
     improved
   - `144 -> 192`
     为 `64 / 66`
     improved
548. 已完成: 新增正式报告
   - `docs/188_stage5_seeded_gpu_baseline192_low_frequency_probe_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已能更谨慎地写成:
  - proxy baseline
    到 `192-step`
    仍有非零收益
  - 且这份收益
    仍主要是 broad-based gain
- 但同时也必须补上:
  - 局部轻微回退
    已开始出现
  - marginal gain
    已进一步缩小

先说人话:
- 这说明当前
  “继续训练”
  不是完全没用，
  但已经越来越不像
  最高收益动作。
- 所以现在更合理的是
  把 brute-force
  horizon scaling
  收住，
  转向下一阶段目标准备。

### 更新后的下一阶段任务
1. 默认优先开始准备:
   - decoder / waveform-STFT
     目标接入
2. 若仍需补验证，
   优先做:
   - 更细 checkpoint review
   - 小成本对照实验
3. 不建议把主线继续切到:
   - `384-step`
   - 或更远 horizon

### 文档补充
- `docs/188_stage5_seeded_gpu_baseline192_low_frequency_probe_report.md`
  - `192-step` low-frequency probe、后段 broad-based gain 与收束建议

## 2026-03-18 Stage5 waveform-STFT bootstrap decoder 更新

### 当前进度补充
549. 已完成: 在
   `src/v5vc/offline_vocoder_scaffold.py`
   为 no-res scaffold
   接入最小
   waveform decoder head
550. 已完成: 在
   `src/v5vc/offline_vocoder_training.py`
   接入:
   - `aligned_waveform`
   - waveform L1
   - log-STFT bootstrap loss
551. 已完成: 在
   `src/v5vc/cli.py`
   为 Stage5 三个训练入口
   新增:
   - `--waveform-weight`
   - `--stft-weight`
552. 已完成: 跑通
   单包 waveform/STFT
   train-step smoke
553. 已完成: 跑通
   dataset-level
   waveform/STFT
   `2-step` smoke
554. 已完成: 跑通
   full-split seeded GPU
   waveform/STFT
   `12-step` baseline
555. 已完成: 新增正式报告
   - `docs/189_stage5_waveform_stft_bootstrap_decoder_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经不能再写成:
  - 只是“准备接
     decoder / waveform-STFT”
- 更准确的口径是:
  - minimal decoder
    已接入
  - waveform/STFT
    dataset-level baseline
    已跑通
- 但也必须同时补上:
  - 当前 bootstrap objective
    出现了
    loudness collapse 风险

先说人话:
- 这一步说明
  新 decoder 不是假的，
  它已经真能训练。
- 但它现在有一个很具体的问题:
  - 学着学着
    声音会越变越小
- 所以下一步更合理的
  不是无脑拉长步数，
  而是先补幅度约束。

### 更新后的下一阶段任务
1. 优先补:
   - loudness / RMS guard
   - 或等价幅度约束
2. 再决定是否继续做:
   - waveform/STFT
     更长 horizon baseline
3. 仍不建议现在就写成:
   - final Stage5 vocoder
   - 或 MRSTFT/GAN
     已成立

### 文档补充
- `docs/189_stage5_waveform_stft_bootstrap_decoder_report.md`
  - minimal decoder 接入、waveform/STFT smoke、`12-step` baseline 与 loudness collapse 信号

## 2026-03-18 Stage5 waveform RMS guard 权衡更新

### 当前进度补充
556. 已完成: 在
   `src/v5vc/offline_vocoder_training.py`
   新增:
   - `loss_rms_guard`
   - `decoded_to_target_rms_ratio`
557. 已完成: 在
   `src/v5vc/cli.py`
   为 Stage5 三个训练入口
   新增:
   - `--rms-guard-weight`
558. 已完成: 跑通
   单包 waveform
   RMS guard smoke
559. 已完成: 跑通
   full-split seeded GPU
   `0.5` guard
   `12-step` 对照
560. 已完成: 跑通
   full-split seeded GPU
   `0.2` guard
   `12-step` 与 `24-step`
   对照
561. 已完成: 新增正式报告
   - `docs/190_stage5_waveform_rms_guard_tradeoff_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经知道:
  - waveform bootstrap
    的 loudness collapse
    不是只能看着发生
- 还知道:
  - `rms_guard = 0.2`
    能把 RMS
    拉回目标附近
  - `rms_guard = 0.5`
    则明显过强

先说人话:
- 这一步把
  “声音越训越小”
  这个问题，
  从纯观察
  推进成了
  有可落地修正方案。
- 当前最像样的
  工程配方
  已经不是
  无 guard，
  也不是
  过强 guard，
  而是中等强度的
  `0.2`。

### 更新后的下一阶段任务
1. 默认沿
   `rms_guard_weight = 0.2`
   继续做:
   - waveform/STFT
     更长 baseline
2. 优先候选:
   - `48-step`
     low-frequency baseline
   - 或 checkpoint review
3. 不建议继续把时间花在:
   - `0.5`
     这类过强 guard
     的微调上

### 文档补充
- `docs/190_stage5_waveform_rms_guard_tradeoff_report.md`
  - RMS guard 接入、`0.5` vs `0.2` 权衡与 `24-step` 最新停点

## 2026-03-18 仓库恢复性与忽略边界评估更新

### 当前进度补充
562. 已完成: 评估
   根目录 `.gitignore`
   与 `.git/info/exclude`
   对仓库恢复性的影响
563. 已完成: 确认
   `.gitattributes`
   当前无须修改，
   主要问题集中在
   `.gitignore`
564. 已完成: 确认
   旧规则对
   “最大可恢复目标”
   不够合理，
   主要误伤:
   - 正式 checkpoint
   - dataset index
   - checkpoint review
   - 其他正式恢复元数据
565. 已完成: 修正
   根目录 `.gitignore`
   的 runtime / training
   保留边界
566. 已完成: 将
   Git 忽略与恢复边界
   规范写入:
   - `docs/00_context_bootstrap.md`
567. 已完成: 新增正式报告
   - `docs/191_repository_recoverability_ignore_policy_report.md`

### 当前阶段结论补充
- 当前仓库的忽略策略
  现在更接近:
  - 保留关键恢复状态
  - 忽略批量可重建包体
- 这比之前那种
  “runtime 基本全忽略”
  更符合项目的
  真实备份目标

先说人话:
- 以前的规则
  容易把真正值钱的
  checkpoint 和索引
  一起挡掉。
- 现在改成了:
  - 大量可重建包体继续忽略
  - 但关键 checkpoint
    和恢复元数据
    留下来

### 更新后的下一阶段任务
1. 后续若继续扩
   `.gitignore`
   边界，
   默认按:
   - 恢复价值
   - 可重建性
   先做分类
2. 不再使用
   粗粒度
   `reports/runtime/**`
   全挡的思路
3. 正式 checkpoint
   与恢复元数据
   默认视为高价值保留项

### 文档补充
- `docs/191_repository_recoverability_ignore_policy_report.md`
  - `.gitignore` 恢复性评估、修正规则与规范落盘结果

## 2026-03-18 Stage5 waveform `rms_guard=0.2` baseline48 与确定性复现修正更新

### 当前进度补充
568. 已完成: 跑通
   Stage5 waveform/STFT
   `rms_guard = 0.2`
   的
   `48-step`
   baseline
569. 已完成: 产出
   baseline48 的
   checkpoint review，
   覆盖:
   - `12 -> 24`
   - `24 -> 36`
   - `36 -> 48`
570. 已完成: 确认
   `step48`
   validation:
   - `loss_total = 0.655545`
   - `loss_stft = 0.238908`
   - `decoded_to_target_rms_ratio = 0.994095`
571. 已完成: 确认
   baseline48 的
   三段增益
   都是:
   - `66 / 66`
     validation package
     全量改善
572. 已完成: 发现
   “只设 seed”
   在 CUDA 上
   不能直接等同于
   strict deterministic，
   新旧 `step24`
   存在轻微漂移
573. 已完成: 在
   `src/v5vc/offline_vocoder_training.py`
   新增:
   - deterministic 复现配置
   - `CUBLAS_WORKSPACE_CONFIG`
     自动设置
574. 已完成: 在
   `src/v5vc/cli.py`
   为 Stage5 三个训练入口
   新增:
   - `--deterministic`
575. 已完成: 用
   两次 `2-step`
   GPU deterministic smoke
   确认:
   - `training`
   - `validation_history`
     完全一致
576. 已完成: 新增正式报告
   - `docs/192_stage5_waveform_rmsguard02_baseline48_and_deterministic_reproducibility_fix_report.md`

### 当前阶段结论补充
- 现在 Stage5
  已经不能只写成:
  - `rms_guard = 0.2`
    在 `24-step`
    更平衡
- 更准确的口径是:
  - 这条配方
    到 `48-step`
    仍持续改善
  - 且改善不是
    少数 package
    拖均值，
    而是
    `66 / 66`
    全量广覆盖
- 同时也必须补上:
  - 之前
    “同 seed”
    还不等于
    strict deterministic
  - 该缺口
    现在已补
    `--deterministic`
    入口

先说人话:
- 这一步说明
  当前 waveform 方案
  还没到头，
  继续训练
  仍然在稳定变好。
- 另外，
  以前那种
  “seed 一样
   就算完全复现”
  的说法
  现在也修正了，
  以后要做严格对照
  可以直接开
  `--deterministic`。

### 更新后的下一阶段任务
1. 若继续沿
   当前 waveform 配方
   深挖，
   默认启用:
   - `--deterministic`
   再做:
   - `72-step`
     或 `96-step`
     baseline
2. 若更看重
   objective 升级，
   可开始准备:
   - 更强的
     multi-resolution STFT
   - 或后续
     adversarial / feature-matching
     接入
3. 不建议继续把时间花在:
   - 更重的
     RMS guard
   - 未开启
     deterministic
     的严格对照实验

### 文档补充
- `docs/192_stage5_waveform_rmsguard02_baseline48_and_deterministic_reproducibility_fix_report.md`
  - baseline48、checkpoint review 与 deterministic 复现修正
