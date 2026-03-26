# 项目总览与实施计划

## 文档定位
- 本文档只保留：
  - 项目目标
  - 当前阶段状态
  - 已确认的主线结论
  - 当前下一步
- 详细实验流水、逐轮追记、旧阶段长历史不再继续堆进这里。
- 2026-03-26 归档快照：
  - `docs/archive/01_project_overview_and_plan_snapshot_20260326.md`

## 项目目标摘要
- 基于 `initial_design.md`，当前目标是构建一个兼顾离线高质量与在线低延迟的工业化变声系统。
- 核心控制链设计态为：
  - `z_art`
  - `e_evt`
  - `F0 / vuv / aper / E`
  - 被严格限权的 `r_res`
- 当前原则保持不变：
  - 无残差主干必须先成立
  - 不允许把系统做成披着可解释外壳的神经编解码器
  - 在线流式闭环晚于离线主干验证

## 当前仓库结构
- `initial_design.md`
  - 主设计稿。
- `initial_design_judg.md`
  - 风险与去魅评估。
- `manage.py`
  - 统一命令入口。
- `python.exe`
  - 项目固定解释器。
- `src/v5vc/`
  - 项目源码。
- `configs/`
  - 配置与模板。
- `reports/`
  - 训练、评估、导出产物。
- `docs/`
  - 主文档、报告和归档。

## 当前阶段总判断

### 1. 上游 `Stage3 / teacher-label / target-state` 仍在产出真实正向信息
- 当前最新、最强的 generation-side reference 是：
  - `teacher_e_evt_bridge_mode = acoustic_directional_targetstate_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
- 依据：
  - `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
- 关键结果：
  - full-validation step12：
    - `loss_total = 1.732503 -> 1.648929`
    - `loss_total_semantic_disabled_reference = 1.57394 -> 1.501041`
    - `loss_teacher_event = 0.504001 -> 0.449996`
    - `loss_teacher_event_prior = 0.728577 -> 0.695983`
  - full-validation step24：
    - `loss_total = 1.157747 -> 1.044122`
    - `loss_total_semantic_disabled_reference = 1.037303 -> 0.939578`
    - `loss_teacher_event = 0.417492 -> 0.332711`
    - `loss_teacher_event_prior = 0.548517 -> 0.489258`

### 2. 当前旧 `Stage5 no-res downstream` 不是有效承接层
- 这不是猜测，而是多轮 fail-fast 结论：
  - `docs/359_stage5_c3_downstream_eevt_overfit24_fail_fast_report.md`
  - `docs/361_stage5_eevt_target_contract_supervision_route_fail_fast_report.md`
  - `docs/366_stage5_teacher_eevt_acoustic_bridge_downstream_fail_fast_report.md`
- 当前旧 route 的稳定现象是：
  - package / contract / supervision 可以接通
  - 但输出仍落入 `template-buzz + envelope-following` 假解
  - automatic buzz gate 长期给出 `all_records_auto_reject = true`

### 3. 当前问题不是“再补一个小参数”
- 当前已正式停止的线包括：
  - Stage5 decode-side 微调
  - waveform/objective 小 sweep
  - target-only static semantic consumer
  - target timing consumer
  - source parity consumer
  - teacher-first inference-only 小修
  - hidden/fused-hidden imitation 小权重线
- 这些线共同说明：
  - 数值改善不等于人声 emergence
  - 当前主问题在 contract / handoff 层级，而不是末端小修

## 当前主线

### 主线 A：继续强化上游 teacher-label / target-state 资产
- 当前参考点：
  - `acoustic_directional_targetstate_bridge_v1`
- 当前优先动作：
  - 继续做 generation-side bridge / target-state 结构升级
  - 不回头扫旧 `acoustic_contextual` 小 patch
  - 不回头扫 loss-side imitation 微调

### 主线 B：重新识别真正有效的 downstream handoff layer
- 当前正式口径：
  - 不再把新的上游 candidate 机械送回当前已判死的旧 `Stage5 no-res downstream`
- 但这不等于：
  - 永久停止一切 Stage5 验证
- 更准确的下一步应是：
  - 先形成 `downstream handoff candidates` 清单
  - 当前最高优先级候选是：
    - `Stage3 student-control packet v1`
  - 这条候选现在已经有最小实现与 smoke export
  - 并把
    - `proxy-acoustic / proxy-audio`
    作为进入新 Stage5 route 前的 cheap screen
  - 当前 cheap screen 结论是：
    - `packet v1` 已成立
    - 但结构增益还不够硬，暂不足以直接开启新的 Stage5 adapter
  - 每个候选都必须写清：
    - 所在层级
    - 预期承接机制
    - 最小验证实验
    - stop rule

## 当前推荐下一步
1. 以 `acoustic_directional_targetstate_bridge_v1` 作为新的 Stage3 reference 固定口径。
2. 不再继续重跑当前旧 `Stage5 no-res downstream` 作为默认承接层。
3. 当前新的默认实施顺序是：
   - 先用已实现的 `Stage3 student-control packet v1`
   - 再做 `proxy-acoustic / proxy-audio` cheap screen
   - 然后用 `named-control readiness negative gate` 卡住尚未完成的 named controls
   - 当前 screen 与 gate 的合并结论仍是：
     - Stage3 内部监督继续正向
     - 但 `F0 / vuv / aper` 仍未到 handoff-ready
   - 因此下一步继续补 `target-state / named-control generation-side completion`
     而不是直接进入新的 Stage5 adapter/scaffold smoke
4. 当前候选清单报告：
   - `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
5. 当前实现与 smoke：
   - `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
6. 当前关键边界：
   - `e_evt` 已可按 named-control candidate 导出
   - 但 `F0 / aper / E` 仍是 proxy/control status，不应误写成已完成的 Stage5-ready contract
7. 当前 cheap screen 报告：
   - `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
8. `packet calibration audit` 已完成，但“直接往 Stage3 loss 注入 deterministic target acoustic state”这条线已失败：
   - `docs/373_stage3_explicit_target_acoustic_state_supervision_ab_fail_report.md`
   - 当前结论是：
     - local state loss 可下降
     - 但共享主指标变差
     - 因此不继续扫 `teacher_f0_state / teacher_vuv_state / teacher_aper_state / teacher_energy_state`
9. `student_control_packet` 现在新增了 named-control negative gate：
   - `docs/374_stage3_student_control_packet_readiness_gate_report.md`
   - 当前最新 target-state bridge checkpoint 的结论是：
     - `e_evt / z_art` 可保留
     - `F0 / vuv / aper / E` 仍全部 auto-reject
     - 因此当前仍不允许开启新的 Stage5 handoff route
10. `teacher_labels` 现在也已完成 `target-state` 合同补齐：
   - `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
   - 当前新的 teacher asset 基线是：
     - `teacher_labels_eevt_directional_targetstate_round1_1`
   - Stage3 batch 现已优先读取 teacher payload 内置 `target_f0_hz / target_vuv / target_aper / target_energy`
11. 在这套 target-state-complete teacher asset 之上，当前 generation-side 最新 reference 已升级为：
   - `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
   - 当前结论是：
     - Stage3 `12-step / 24-step full-validation` 都继续正向
     - 但 `student_control_packet` 的 readiness gate 仍然不给放行
     - 所以这版收益暂时仍停留在 Stage3 内部监督层
12. 在新的 handoff family 通过更强 cheap screen 前，不再新增：
  - Stage5 同层 decode 小实验
  - Stage5 同层 semantic/timing consumer 小实验
  - 同类 objective / weight 微扫
13. 当前新的默认下一步改为：
  - 不继续做 naive direct state loss injection
  - 基于新的 `teacher_labels_eevt_directionaltargetstatebridge_round1_1`
    继续做更结构化的 `target-state / named-control generation-side completion`
  - 并以 `named-control readiness negative gate` 作为新的下游前置门禁
  - 尤其避免把“packet 可导出”或“local state MAE 下降”误判成“已经值得开新 Stage5 route”

## 关键参考报告
- `docs/355_post_buzz_fail_main_scheme_reevaluation_and_v2core_gap_report.md`
- `docs/356_stage3_teacher_eevt_v1_bootstrap_plumbing_and_short_loop_report.md`
- `docs/357_stage3_teacher_eevt_v1_vs_legacy_event_target_ab_short_loop_report.md`
- `docs/365_stage3_teacher_eevt_acoustic_bridge_ab_report.md`
- `docs/366_stage5_teacher_eevt_acoustic_bridge_downstream_fail_fast_report.md`
- `docs/367_stage3_teacher_fused_hidden_projection_ab_fail_report.md`
- `docs/368_stage3_teacher_eevt_directional_transition_bridge_ab_report.md`
- `docs/369_oneoff_evaluation_of_1md_recommendations.md`
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/373_stage3_explicit_target_acoustic_state_supervision_ab_fail_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
- `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`

## 维护规则
- 新实验细节默认写入独立编号报告，不再整段追加到本文档。
- 本文档只在以下情况更新：
  - 主线判断改变
  - 当前 best reference 改变
  - 下一步策略改变
  - 文档口径需要统一修正
- 若后续再次出现超长追记，应继续归档，不回到单文件堆历史的做法。
