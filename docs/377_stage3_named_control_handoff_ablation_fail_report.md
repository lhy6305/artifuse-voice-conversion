# 377 Stage3 named-control handoff 消融失败报告

## 本轮目的
- 在 `teacher_labels_eevt_directionaltargetstatebridge_round1_1` 已成为当前 Stage3 reference 后，
  继续验证为什么 `student_control_packet` 的 `F0 / vuv / aper` 仍长期不过 readiness gate。
- 本轮只测两类最小结构候选：
  - `named_control_proxy_target_family = deterministic_target_state_v1`
  - student 分支前的轻量梯度解耦：
    - `detach_frontend_named_controls_for_student`
    - `detach_shared_hidden_for_student`

## 候选 A：`named_control_proxy_target_family = deterministic_target_state_v1`

### 改动
- `src/v5vc/streaming_student/losses.py`
  - 新增 `semantic_supervision.named_control_proxy_target_family`
  - 支持：
    - `teacher_e_evt_v1`
    - `deterministic_target_state_v1`
- `configs/streaming_student_loss_weights_namedcontrol_proxy_targetstate_v1.json`
  - 候选 override

### 验证
- supervision dry-run：
  - `reports/plans/streaming_student_supervision_namedcontrolproxytargetstate_round1_1/`
- 1-step smoke：
  - `reports/training/streaming_student_step_namedcontrolproxytargetstate_smoke_round1_1/`
- 严格可比 12-step full-validation：
  - baseline:
    - `reports/training/streaming_student_loop_namedcontrolproxyfamily_baseline12_round1_1/`
  - candidate:
    - `reports/training/streaming_student_loop_namedcontrolproxyfamily_targetstate12_round1_1/`

### 结果
- baseline:
  - `loss_total = 1.648929`
  - `loss_total_semantic_disabled_reference = 1.501041`
  - `loss_teacher_vuv_proxy = 0.502114`
  - `loss_teacher_aper_proxy = 0.150279`
- candidate:
  - `loss_total = 1.685598`
  - `loss_total_semantic_disabled_reference = 1.537627`
  - `loss_teacher_vuv_proxy = 0.715993`
  - `loss_teacher_aper_proxy = 0.197589`

### 判断
- 这条线 fail-fast 失败。
- 直接把 `vuv / aper` proxy target 从 `teacher_e_evt` 切到 deterministic target-state，
  在当前 scaffold 上没有改善 named-control 监督，反而整体更差。

## 候选 B：`detach_frontend_named_controls_for_student`

### 改动
- `src/v5vc/streaming_student/model.py`
  - 新增 `model.detach_frontend_named_controls_for_student`
  - 仅在喂给 student encoder 前，对
    - `coarse_log_f0`
    - `vuv_logits`
    - `aperiodicity`
    - `energy`
    对应的 frontend named controls 做 `detach`
- `src/v5vc/streaming_student/plan_entry.py`
  - contract summary 支持新开关
- `configs/streaming_student_stage_detach_named_controls_v1.json`
  - 候选 config

### 验证
- 1-step smoke：
  - `reports/training/streaming_student_step_detachnamedcontrols_smoke_round1_1/`
- 12-step full-validation：
  - `reports/training/streaming_student_loop_detachnamedcontrols12_round1_1/`
- packet compare：
  - baseline:
    - `reports/runtime/streaming_student_downstream_control_packet_namedcontrolproxyfamily_baseline12_round1_1/streaming_student_downstream_control_packet.json`
  - candidate:
    - `reports/runtime/streaming_student_downstream_control_packet_detachnamedcontrols12_round1_1/streaming_student_downstream_control_packet.json`

### 结果
- Stage3 validation：
  - baseline `loss_total = 1.648929`
  - candidate `loss_total = 1.657066`
- packet readiness：
  - 两边都是 `all_records_auto_reject = true`
  - `f0_ready_count / vuv_ready_count / aper_ready_count / energy_ready_count` 都没有打开

### 判断
- 这条轻量 detach 也不成立。
- 只切断 named-control 输入到 student encoder 的直接梯度，不足以改变 handoff readiness。

## 候选 C：`detach_shared_hidden_for_student`

### 改动
- `src/v5vc/streaming_student/model.py`
  - 新增 `model.detach_shared_hidden_for_student`
  - 在 `shared_hidden -> student_input` 这条链路上做 `detach`
- `src/v5vc/streaming_student/plan_entry.py`
  - contract summary 支持新开关
- `configs/streaming_student_stage_detach_shared_hidden_v1.json`
  - 候选 config

### 验证
- 1-step smoke：
  - `reports/training/streaming_student_step_detachsharedhidden_smoke_round1_1/`
- 12-step full-validation：
  - `reports/training/streaming_student_loop_detachsharedhidden12_round1_1/`
- packet compare：
  - `reports/runtime/streaming_student_downstream_control_packet_detachsharedhidden12_round1_1/streaming_student_downstream_control_packet.json`

### 结果
- baseline:
  - `loss_total = 1.648929`
  - `loss_total_semantic_disabled_reference = 1.501041`
  - `loss_teacher_event_prior = 0.695983`
- candidate:
  - `loss_total = 1.504664`
  - `loss_total_semantic_disabled_reference = 1.364074`
  - `loss_teacher_event_prior = 0.618278`
- 但 packet readiness 仍是：
  - `all_records_auto_reject = true`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
- 局部变化：
  - `F0 / energy` 某些记录略好
  - `vuv / aper` 没有实质跨线

### 判断
- 这条更强解耦值得保留为“有信息量的失败”：
  - 它说明 student event/z_art 对 frontend encoder 的反向拉扯，确实是一个结构因素
  - 但仅靠轻量 `detach` 仍不足以把 named controls 推到 handoff-ready

## 总结
- 本轮三条线都没有打开 `student_control_packet` 的 readiness gate。
- 结论比之前更明确：
  - 问题不只是 target family 选错
  - 也不只是加一个轻量梯度 stop 就能解决
- 当前更合理的下一步，不是继续扫这些小开关，而是上到更显式的：
  - `frontend named-control branch split`
  - 或 `control-specific encoder/head family split`

## 下一步
- 停止继续扫：
  - `named_control_proxy_target_family`
  - `detach_frontend_named_controls_for_student`
  - `detach_shared_hidden_for_student`
- 下一步改为：
  - 构建更明确的 `frontend/control branch split`
  - 让 `F0 / vuv / aper / E` 不再主要与 event-driving shared path 共用同一前端表征
