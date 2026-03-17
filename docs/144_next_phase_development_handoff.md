# 144. 下一阶段开发交接

## 本文目的
- 本文用于把当前项目状态从:
  - offline MVP 验证 / route 收口
  切换到:
  - 下一阶段开发准备
- 本文不是新实验草案，
  而是交接文档。

## 当前已确认的阶段切换结论

### 1. offline MVP 当前默认收口
- 当前 full long-horizon formal route 已冻结为:
  - validation = `D76`
  - special = `D82`
  - `zero_e_evt checkpoint-option = D87 step150`
  - `zero_z_art = D33`
  - `default/minimax = D87`
- 该结论已被:
  - formal handoff
  - handoff document
  - stage report
  统一写实。

### 2. 当前不建议继续修补同 family 的 offline MVP 实验
- 不再默认继续:
  - late teacher source handoff
  - late `z_art_weight`
  - late `z_art_influence` retarget
  - full-priority singleton exposure
  - old-family late gate / checkpoint-option 扩展
- 若没有新的、更外层 `z_art restoration / supervision` 机制，
  不建议再开新的 offline MVP 近邻实验。

### 3. 当前阶段切换为“下一环节开发”
- 默认理解为:
  - 不再把主要时间用于当前 offline MVP family 的实验扩展
  - 开始转入设计稿后续阶段的工程开发准备

## 对下一阶段的默认建议

### 1. 默认先进入前端 / Student 侧开发准备
- 依据当前总路线，
  更合理的下一阶段不是先打开 `r_res`，
  而是先准备:
  - 共享前端 / Student / 控制头
  - 与现有 offline MVP 评估链兼容的接口骨架
- 原因:
  - 当前 offline MVP 已经回答了“无残差主干是否可被验证”这一阶段问题
  - 但 `r_res` 尚未实装，
    直接开启残差线会把结构风险同时叠加进来

### 2. 下一阶段的默认工程目标
- 把现有 offline MVP 视为:
  - 控制变量有效性的离线参考系
- 下一阶段优先补:
  - 新阶段模块边界
  - 输入输出 contract
  - 与现有评估/日志/实验记录兼容的脚手架
- 暂不优先补:
  - 新一轮 offline MVP 训练 sweep

### 3. 下次恢复时的默认起手动作
1. 先读取:
   - `docs/00_context_bootstrap.md`
   - `docs/01_project_overview_and_plan.md`
   - `docs/143_offline_mvp_structure_sensitivity_and_applicability_boundary.md`
   - 本文 `docs/144_next_phase_development_handoff.md`
2. 再回看:
   - `initial_design.md`
   - `initial_design_judg.md`
3. 然后只做一件事:
   - 明确下一阶段首个工程落点，
     不直接开训练

## 下次开工时建议先做什么

### 方案 A: 先写下一阶段技术草案
- 内容包括:
  - 目标模块
  - 输入输出
  - 与现有 offline MVP 的复用关系
  - 与未来 `r_res` 的边界
- 适用情况:
  - 希望先把阶段边界写清，
    再开代码

### 方案 B: 直接搭下一阶段代码骨架
- 默认优先级更高。
- 起手内容应是:
  - 新模块目录
  - config schema
  - CLI / 训练计划 / 评估入口的最小骨架
- 但仍应满足:
  - 不直接引入 `r_res`
  - 不直接开始新训练

## 当前明确不要做的事
- 不要再读取临时 `1.md` / `2.md`
- 不要把 `D87 step150` 混写成 formal default
- 不要把当前 offline MVP route 结论外推成完整设计稿已验证
- 不要在没有新机制的前提下继续补同 family 训练实验

## 当前交接所依赖的正式入口
- `docs/140_round1_1_d87_outer_punctuation_zartretarget_lateretention_route_capture_report.md`
- `docs/141_system_assessment_response_to_temp_1_2.md`
- `docs/142_old_long_horizon_experiments_recheck_report.md`
- `docs/143_offline_mvp_structure_sensitivity_and_applicability_boundary.md`
- `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.md`
- `reports/handoffs/offline_mvp_route_handoff_doc_round1_1_longwindow_final/handoff_document.md`
- `reports/stage_reports/offline_mvp_stage_report_round1_1_longwindow_final/stage_report.md`

## 一句话交接
- offline MVP 当前默认收口；
  下一次恢复工作时，
  应把主线切到“下一阶段工程骨架 / 前端-Student 侧开发准备”，
  而不是继续在当前 offline MVP family 上补近邻实验。
