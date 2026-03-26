# 379 Stage3 parallel control branch bounded F0 fail 报告

## 本轮目的
- 在 `parallel_control_encoder_v1` 已经证明：
  - Stage3 主指标可继续改善
  - 但 `student_control_packet` 的 `F0` raw proxy correlation 会稳定反号
- 本轮继续验证：
  - 若只在并行 control branch 上把 `F0` 改成有物理边界的参数化，
    是否能修掉 handoff 侧最严重的 `F0` 方向错误

## 改动
- `src/v5vc/streaming_student/model.py`
  - `UnifiedStreamingFrontend` 新增：
    - `f0_parameterization_mode`
    - `f0_floor_hz`
    - `f0_ceil_hz`
  - 支持：
    - `unbounded_log_v1`
    - `bounded_log2_hz_v1`
  - `bounded_log2_hz_v1` 会把 `raw_coarse_log_f0`
    映射到 `[log2(f0_floor_hz), log2(f0_ceil_hz)]`
- `src/v5vc/streaming_student/plan_entry.py`
  - contract summary 补充 `f0_parameterization`
- 新 config：
  - `configs/streaming_student_stage_parallel_control_branch_boundedf0_v1.json`

## 验证
- `py_compile`
- 1-step smoke：
  - `reports/training/streaming_student_step_parallelcontrolbranch_boundedf0_smoke_round1_1/`
- 严格可比 12-step full-validation：
  - baseline:
    - `reports/training/streaming_student_loop_parallelcontrolbranch12_round1_1/`
  - candidate:
    - `reports/training/streaming_student_loop_parallelcontrolbranch_boundedf012_round1_1/`
- packet compare：
  - baseline:
    - `reports/runtime/streaming_student_downstream_control_packet_parallelcontrolbranch12_round1_1/streaming_student_downstream_control_packet.json`
  - candidate:
    - `reports/runtime/streaming_student_downstream_control_packet_parallelcontrolbranch_boundedf012_round1_1/streaming_student_downstream_control_packet.json`

## Stage3 结果
- parallel branch baseline:
  - `loss_total = 1.586973`
  - `loss_total_semantic_disabled_reference = 1.462965`
  - `loss_teacher_event_prior = 0.541574`
- bounded F0 candidate:
  - `loss_total = 1.631516`
  - `loss_total_semantic_disabled_reference = 1.511211`
  - `loss_teacher_event_prior = 0.512529`
- 判断：
  - `event_prior` 略有改善
  - 但整体 `loss_total` 与 `semantic_disabled_reference` 更差

## packet / readiness 结果
- 两边都仍是：
  - `all_records_auto_reject = true`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
- 更关键的是：
  - `F0` raw proxy correlation 依然稳定为负
  - 典型记录：
    - `target::chapter3_3_firefly_162`
      - baseline `f0_proxy_reference_corr = -0.481395`
      - bounded `-0.483697`
    - `target::chapter3_4_firefly_106`
      - baseline `-0.596322`
      - bounded `-0.594578`
- 说明：
  - 这条 bounded parameterization 只收紧了数值范围
  - 没有修掉方向错误
- 补充观察：
  - `f0_log_proxy_mean` 现在稳定落在接近 `log2(50~550Hz)` 的区间
  - 但“落在物理范围内”不等于“方向正确”

## 结论
- `bounded_log2_hz_v1` 不是当前问题的解法。
- 它解决的是：
  - 输出量纲
  - 输出边界
- 但当前更根本的问题仍是：
  - `F0` branch 的方向性与参考关系没有被正确学到
- 所以这条 parameterization 线应正式停掉，不再扫：
  - `f0_floor_hz / f0_ceil_hz`
  - `bounded/unbounded` 的小变体

## 下一步
- 当前如果继续，只能上到更强的：
  - `control-specific head family`
  - 或显式 `F0` control-state branch / sign-stable handoff design
- 不再继续扫：
  - `branch split v1` 小层数
  - `bounded F0` 小边界
  - 其他同层轻量 parameterization 小补丁
