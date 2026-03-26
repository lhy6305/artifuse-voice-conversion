# 376 Stage3 teacher_e_evt directional target-state bridge A/B 与 readiness 评估

## 本轮目的
- 在已完成 `teacher_labels_eevt_directional_targetstate_round1_1` 合同补齐后，继续评估：
  - generation-side `teacher_e_evt` 是否能进一步吸收 deterministic `target-state`
  - 这类上游正向是否已经开始穿透到 `student_control_packet` 的 named-control readiness

## 代码与资产变更
- `src/v5vc/event_semantics.py`
  - 新增 `teacher_e_evt_bridge_mode = acoustic_directional_targetstate_bridge_v1`
  - 在前 5 个 acoustic dims 上，把 `target_f0_hz / target_vuv / target_aper / target_energy` 纳入 generation-side bridge
- `src/v5vc/streaming_student/teacher_labels.py`
  - 修复 `export_single_record(...)` 中 `target_acoustic_state` use-before-assign
  - 先提取 target acoustic state，再构造 `teacher_e_evt`
- 新 full teacher asset：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstatebridge_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directionaltargetstatebridge_round1_1/`

## 验证链路
- `py_compile`
- smoke teacher-label export
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstatebridge_smoke_round1_1/`
- full teacher-label export
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstatebridge_round1_1/teacher_label_index.jsonl`
- supervision dry-run
  - `reports/plans/streaming_student_supervision_eevt_directionaltargetstatebridge_round1_1/streaming_student_supervision_plan.json`
- 1-step train smoke
  - `reports/training/streaming_student_step_eevt_directionaltargetstatebridge_smoke_round1_1/`
- 严格可比 Stage3 `12-step full-validation`
  - baseline:
    - `reports/training/streaming_student_loop_eevt_directionaltargetstate_baseline12_round1_1/`
  - candidate:
    - `reports/training/streaming_student_loop_eevt_directionaltargetstatebridge12_round1_1/`
- 严格可比 Stage3 `24-step full-validation`
  - baseline:
    - `reports/training/streaming_student_loop_eevt_directionaltargetstate_baseline24_round1_1/`
  - candidate:
    - `reports/training/streaming_student_loop_eevt_directionaltargetstatebridge24_round1_1/`
- `student_control_packet` readiness compare
  - baseline:
    - `reports/runtime/streaming_student_downstream_control_packet_directionaltargetstate_baseline24_round1_1/streaming_student_downstream_control_packet.json`
  - candidate:
    - `reports/runtime/streaming_student_downstream_control_packet_directionaltargetstatebridge24_round1_1/streaming_student_downstream_control_packet.json`

## smoke 几何检查
- smoke 样本显示这不是 metadata-only 变更：
  - 前 5 个 acoustic dims 出现稳定重塑
  - 典型现象是：
    - `p_voicing` 显著抬高
    - `p_stop_closure / p_burst / p_frication` 收紧
    - 后 3 个 timing dims 保持不变
- 说明这版 bridge 真正在 generation-side 改了 `teacher_e_evt` 几何，而不是只改 summary 或字段名

## Stage3 A/B 结果

### 12-step full-validation
- baseline:
  - `loss_total = 1.732503`
  - `loss_total_semantic_disabled_reference = 1.57394`
  - `loss_teacher_event = 0.504001`
  - `loss_teacher_event_prior = 0.728577`
- candidate:
  - `loss_total = 1.648929`
  - `loss_total_semantic_disabled_reference = 1.501041`
  - `loss_teacher_event = 0.449996`
  - `loss_teacher_event_prior = 0.695983`
- 判断：
  - 明显正向，不是短步数随机波动

### 24-step full-validation
- baseline:
  - `loss_total = 1.157747`
  - `loss_total_semantic_disabled_reference = 1.037303`
  - `loss_teacher_event = 0.417492`
  - `loss_teacher_event_prior = 0.548517`
  - `loss_teacher_z_art = 0.045499`
- candidate:
  - `loss_total = 1.044122`
  - `loss_total_semantic_disabled_reference = 0.939578`
  - `loss_teacher_event = 0.332711`
  - `loss_teacher_event_prior = 0.489258`
  - `loss_teacher_z_art = 0.064599`
- 判断：
  - generation-side `targetstate bridge` 在 Stage3 上继续成立
  - 主提升仍集中在 `teacher_event / teacher_event_prior / total`
  - `z_art` 不是同步全面变好，因此当前收益仍应解释为 event/target-state 几何改进，而不是所有 named controls 一起成熟

## student_control_packet readiness 结果
- baseline summary:
  - `e_evt_ready_count = 3`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 3`
  - `auto_reject_count = 3`
- candidate summary:
  - `e_evt_ready_count = 3`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 3`
  - `auto_reject_count = 3`
- 典型记录观察：
  - `vuv_prob_mean` 明显抬高
  - 个别 `vuv/aper` 参考误差有改善，但并不稳定
  - `f0_proxy_reference_corr` 与 `f0_calibrated_log2_mae` 没有跨过 gate
- 判断：
  - 这版 candidate 的正向仍主要停留在 Stage3 内部监督层
  - 还没有把 `F0 / vuv / aper` 推到新的 handoff-ready 区间
  - 因此 `named_control_readiness negative gate` 仍不放行

## 结论
- 本轮结论分两层：
  - 第一层：`acoustic_directional_targetstate_bridge_v1` 应升级为新的 Stage3 generation-side reference
  - 第二层：这不等于可以开新的 Stage5 handoff route
- 当前更准确的状态是：
  - `teacher_e_evt` generation-side 又前进了一步
  - 但 `student_control_packet_v1` 的 named controls 仍未完成
  - 所以下游 route 仍不能开启

## 下一步
- 不回头继续扫旧 `acoustic_directional_transition_bridge_v1`
- 不把这版 Stage3 正向机械送进新的 Stage5 route
- 下一步改为继续做：
  - `target-state / named-control generation-side completion`
  - 优先关注 `F0 / vuv / aper` 为什么在 packet gate 上仍长期不过线
  - 继续以 `named-control readiness negative gate` 作为下游前置门禁
