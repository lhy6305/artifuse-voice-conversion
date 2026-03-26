# 378 Stage3 parallel control branch fail-fast 报告

## 本轮目的
- 在前一轮 `named_control handoff ablation` 已经证明：
  - `named_control_proxy_target_family`
  - 轻量 `detach`
  都不足以打开 readiness gate 之后，
  继续验证更明确的 `frontend/control branch split` 是否有价值。

## 改动
- `src/v5vc/streaming_student/model.py`
  - `UnifiedStreamingFrontend` 新增：
    - `named_control_branch_mode`
    - `named_control_branch_layers`
  - 新模式：
    - `shared_hidden_v1`
    - `parallel_control_encoder_v1`
  - 当开启 `parallel_control_encoder_v1` 时：
    - `coarse_log_f0`
    - `vuv_logits`
    - `aperiodicity`
    - `energy`
    来自并行 `control_encoder(hidden)`，
    不再直接复用 event-driving `shared_hidden`
- `src/v5vc/streaming_student/plan_entry.py`
  - scaffold/contract summary 补充 `control_hidden`
- 配置：
  - `configs/streaming_student_stage_parallel_control_branch_v1.json`

## 验证
- `py_compile`
- 1-step smoke：
  - `reports/training/streaming_student_step_parallelcontrolbranch_smoke_round1_1/`
- 严格可比 12-step full-validation：
  - baseline:
    - `reports/training/streaming_student_loop_namedcontrolproxyfamily_baseline12_round1_1/`
  - candidate:
    - `reports/training/streaming_student_loop_parallelcontrolbranch12_round1_1/`
- packet compare：
  - baseline:
    - `reports/runtime/streaming_student_downstream_control_packet_namedcontrolproxyfamily_baseline12_round1_1/streaming_student_downstream_control_packet.json`
  - candidate:
    - `reports/runtime/streaming_student_downstream_control_packet_parallelcontrolbranch12_round1_1/streaming_student_downstream_control_packet.json`

## Stage3 结果
- baseline:
  - `loss_total = 1.648929`
  - `loss_total_semantic_disabled_reference = 1.501041`
  - `loss_teacher_event = 0.449996`
  - `loss_teacher_event_prior = 0.695983`
  - `loss_teacher_vuv_proxy = 0.502114`
  - `loss_teacher_aper_proxy = 0.150279`
  - `loss_teacher_z_art = 0.101342`
- candidate:
  - `loss_total = 1.586973`
  - `loss_total_semantic_disabled_reference = 1.462965`
  - `loss_teacher_event = 0.451145`
  - `loss_teacher_event_prior = 0.541574`
  - `loss_teacher_vuv_proxy = 0.558809`
  - `loss_teacher_aper_proxy = 0.064293`
  - `loss_teacher_z_art = 0.048822`

## packet / readiness 结果
- gate summary 没有打开：
  - baseline:
    - `all_records_auto_reject = true`
    - `f0_ready_count = 0`
    - `vuv_ready_count = 0`
    - `aper_ready_count = 0`
    - `energy_ready_count = 0`
  - candidate:
    - `all_records_auto_reject = true`
    - `f0_ready_count = 0`
    - `vuv_ready_count = 0`
    - `aper_ready_count = 0`
    - `energy_ready_count = 0`
- 更关键的坏信号：
  - `F0` raw proxy correlation 变成了稳定负相关
  - 典型记录：
    - `target::chapter3_3_firefly_162`
      - baseline `f0_proxy_reference_corr = 0.490416`
      - candidate `f0_proxy_reference_corr = -0.481395`
    - `target::chapter3_4_firefly_106`
      - baseline `0.605708`
      - candidate `-0.596322`
- 同时：
  - `energy_stage5_norm_reference_mae` 有所改善
  - `aper_reference_mae` 也略有改善
  - 但 `vuv` 没过线，`F0` 甚至方向反了

## 判断
- 这是一条“有信息量但仍失败”的候选：
  - `parallel_control_encoder_v1` 说明更明确的 branch split 确实能改善部分 Stage3 主指标
  - 但它没有打开 handoff readiness
  - 还引入了更严重的 `F0` 符号翻转问题
- 所以它不能直接升格为新的 reference，也不能进入新的 Stage5 route

## 结论
- 当前已经可以更硬地说：
  - 简单的 `frontend/control branch split v1` 还不够
  - 下一步如果继续，必须上到更强的
    `control-specific head family / bounded F0 parameterization / explicit control-state branch`
  - 而不是继续扫：
    - proxy target family
    - 轻量 detach
    - branch split v1 的小层数/小超参
