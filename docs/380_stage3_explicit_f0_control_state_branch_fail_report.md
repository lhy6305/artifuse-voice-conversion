# 380 Stage3 explicit F0 control-state branch fail-fast report

## 本轮目的
- 在已失败的
  - `parallel_control_encoder_v1`
  - `bounded_log2_hz_v1`
  之后，继续验证更强一档的
  `explicit F0 control-state branch`
  是否能解决当前 `F0` handoff 的方向性错误。
- 本轮仍遵循 fail-fast：
  - 先看严格可比 `12-step full-validation`
  - 再看 `student_control_packet` readiness / `F0` 对照
  - 不做新的 Stage5 route

## 实现内容
- 新增 `f0_control_branch_mode = explicit_state_branch_v1`
- 新增 `f0_correction_parameterization_mode = bounded_tanh_log2_delta_v1`
- 在 `StudentControlHeads` 中引入独立 `f0_branch_hidden`
- `f0_branch_input` 显式拼接：
  - `control_hidden`
  - `conditioning`
  - `coarse_log_f0`
  - `sigmoid(vuv_logits)`
  - `energy`
  - `sigmoid(event_prior_logits)`
- 新配置：
  - `configs/streaming_student_stage_parallel_control_branch_explicitf0_v1.json`
  - `configs/streaming_student_loss_weights_explicit_f0_branch_warmup_v1.json`

## 验证范围
- 使用仓库解释器：
  - `python.exe`
- 完成：
  - `py_compile`
  - 1-step smoke
  - 严格可比 `12-step full-validation` A/B
  - `student_control_packet` export

## 对照对象
- baseline：
  - `parallel_control_encoder_v1 + bounded_log2_hz_v1`
  - `reports/training/streaming_student_loop_boundedf0_f0warmup12_round1_1/logs/streaming_student_stage_loop_boundedf0_f0warmup12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_parallelcontrolbranch_boundedf012_round1_1/streaming_student_downstream_control_packet.json`
- candidate：
  - `explicit F0 branch + bounded_tanh_log2_delta_v1`
  - `reports/training/streaming_student_loop_explicitf0branch12_round1_1/logs/streaming_student_stage_loop_explicitf0branch12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_explicitf0branch12_round1_1/streaming_student_downstream_control_packet.json`

## 结果

### 1. Stage3 主指标基本打平，未形成净收益
- validation step12：
  - `loss_total = 1.636606 -> 1.637206`
  - `loss_total_semantic_disabled_reference = 1.516201 -> 1.51705`
  - `loss_teacher_event = 0.444191 -> 0.441962`
  - `loss_teacher_event_prior = 0.512212 -> 0.511707`
- 结论：
  - 主监督层面几乎完全打平
  - 没有出现足够硬的正向收益

### 2. `F0` 目标也没有变好
- validation step12：
  - `loss_teacher_f0_state = 0.337141 -> 0.343207`
  - `loss_log_f0_correction_l1 = 0.077472 -> 0.349218`
- 结论：
  - explicit F0 branch 没有压低 `teacher_f0_state`
  - 反而显著抬高了 correction 正则
  - 说明它更像是在放大局部修正自由度，而不是修正 handoff 方向

### 3. packet readiness 仍完全不开
- 两边 summary 一致：
  - `e_evt_ready_count = 3`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
  - `all_records_auto_reject = true`
- 结论：
  - 这条线没有把任何 named control 推过下游最低就绪线

### 4. `F0` 方向性错误仍在，而且略差
- `target::chapter3_3_firefly_162`
  - `f0_proxy_reference_corr = -0.483697 -> -0.50175`
- `target::chapter3_3_firefly_138`
  - `f0_proxy_reference_corr = -0.174299 -> -0.186037`
- `target::chapter3_4_firefly_106`
  - `f0_proxy_reference_corr = -0.594578 -> -0.614544`
- 同时 `f0_log_proxy_mean` 从约 `7.0` 飘到约 `8.0`
- 结论：
  - bounded 版本已经把数值范围收进合理区间
  - explicit F0 branch 仍没有修掉方向性反号
  - 甚至在采样记录上略差

## 判断
- `explicit F0 control-state branch` 正式 fail-fast 停线。
- 当前不能继续扫：
  - `f0_control_branch_layers`
  - `f0_correction_limit_log2`
  - `teacher_f0_state` 小权重
  - `bounded/unbounded delta` 同层微调

## 当前含义
- 问题已经进一步收敛为：
  - 单独把 `F0` 从 shared/control path 中再剥一层独立 head
    仍不足以修掉 named-control handoff 的结构错误。
- 这说明下一步若继续，必须上到更强的：
  - `control-specific head family`
  - 或更完整的 `explicit control-state branch`
- 而不是继续围绕 `F0` 单支路做局部修饰。

## 下一步
- 不开启新的 Stage5 route。
- 下一条候选应是：
  - 更完整的 `control-specific head family`
  - 明确把 `F0 / vuv / aper / E`
    从当前 event-driving shared path 里进一步结构解耦。
