# 项目总览与实施计划

## 文档定位
- 本文档只保留当前接班所需的项目目标、阶段判断、主线和下一步。
- 详细实验流水、逐轮追记、旧阶段长历史不再继续堆进这里。
- 当前归档快照：
  - `docs/archive/01_project_overview_and_plan_snapshot_20260326.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260328.md`

## 项目目标摘要
- 基于 `initial_design.md`，当前目标仍是构建兼顾离线高质量与在线低延迟的工业化变声系统。
- 核心控制链设计态为：`z_art`、`e_evt`、`F0 / vuv / aper / E`，以及被严格限权的 `r_res`。
- 当前原则不变：
  - 无残差主干必须先成立。
  - 不允许把系统做成披着可解释外壳的神经编解码器。
  - 在线流式闭环晚于离线主干验证。

## 当前仓库结构
- `initial_design.md`：主设计稿。
- `initial_design_judg.md`：风险与去魅评估。
- `manage.py`：统一命令入口。
- `python.exe`：项目固定解释器。
- `src/v5vc/`：项目源码，覆盖 Stage3 / Stage5 / teacher-first / streaming_student 主线实现。
- `configs/`：配置与模板。
- `reports/`：训练、评估、导出产物，以及实验结论对应的结构化报告。
- `docs/`：主文档与编号报告。
- `docs/archive/`：旧阶段快照归档。

## 当前阶段总判断
- Stage3 generation-side 当前最新、最强的 reference 是 `acoustic_directional_targetstate_bridge_v1`。
- 旧 `Stage5 no-res downstream` 已不再是值得继续默认回流的 Stage5 candidate 承接 route。
- `student_control_packet -> minimal Stage5 adapter` 已经跑到真实 `decoded.wav` 级别 smoke，但 obvious-buzz 已给出更硬的 fail-fast 负结论。
- paired Stage3 仍缺 frame bridge / alignment contract，当前不能直接开 paired 训练。

## 当前主线
### 主线 A：继续做 teacher-label / target-state generation-side completion
- 当前 reference：`acoustic_directional_targetstate_bridge_v1`
- 当前动作：
  - 继续做 generation-side bridge / target-state completion
  - 不回头扫旧 `acoustic_contextual` 小 patch
  - 不回头扫 loss-side imitation 微调，也不把 loss 下降误写成 readiness 提升

### 主线 B：重新识别 handoff family，而不是继续回流旧 Stage5 route
- 当前最高优先级候选是 `Stage3 student-control packet v1`。
- 进入新的 Stage5 route 前，先过：
  - `proxy-acoustic / proxy-audio` cheap screen
  - `named-control readiness negative gate`
- 当前 gate 结论是：
  - `e_evt / z_art` 已 ready
  - `F0 / vuv / aper / E` 仍未 handoff-ready

### 主线 C：paired Stage3 先补齐接线与对齐前提
- 当前前置条件包括：
  - `source_semantic_parity_sidecar` 需要 `source_record_id` attach
  - target teacher label 需要 formal split 对齐约束
- 当前关键限制是：
  - source waveform 与 target teacher frame 不天然对齐

## 当前维护规则
- 全部文档保持 `UTF-8`。
- 统一使用 `python.exe manage.py ...` 作为命令入口。
- 历史长上下文进入 `docs/archive/`，不再回流主文档。
- `skip_existing` 只在确认复用身份正确时启用，避免静默复用旧产物。
- 关键实验与资产变更必须能在最终 summary/json 等可追溯产物中落点。

## 当前推荐下一步
1. 围绕 `acoustic_directional_targetstate_bridge_v1` 继续做 generation-side completion。
2. 先把 handoff candidate 的 cheap screen 和 readiness gate 做硬，再决定是否进入新的 Stage5 adapter。
3. 在 paired Stage3 上先补 frame bridge / alignment contract，再决定是否开启 paired 训练。
4. 继续把长期有效结论写回 `01/02`，把局部实验细节留在编号报告。

## 关键参考报告
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
- `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
- `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- `docs/447_repo_health_and_compliance_audit_20260328.md`
