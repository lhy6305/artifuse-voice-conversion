# 450 Stage3 event-family follow-ups and loss-side weight probe report

## 结论
- generation-side 继续修 `teacher_e_evt` 几何的两条 follow-up 都失败：
  - `directionaltargetstatehardbox12`
  - `directionaltargetstaterebalancehardbox12`
- loss-side 的 per-dim `event_channel_weight` 路线首次拿到了稳定的 Stage3 validation 正信号：
  - `evtfocus12` 优于 `vuvbalancedgate12`
  - `evtfocus24` 也优于 `vuvbalancedgate24`
- 但 `evtfocus24` 的 downstream packet 比 `vuvbalancedgate24` 更差，说明这条路线当前是在“拉低 teacher-supervised loss”的同时牺牲了 packet-facing 控制质量。
- 因此本轮不切换主线 reference：
  - 继续保留 `vuvbalancedgate24` 作为当前 packet-facing reference
  - 保留 loss-side per-dim weighting 能力与候选配置，作为后续更细粒度调权试验入口

## 本轮改动
- 更新：
  - `src/v5vc/streaming_student/losses.py`
- 新增：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_evtfocus_v1.json`
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_evtfocuslite_v1.json`
- 改动内容：
  - `semantic_supervision` 新增 `event_channel_weight_overrides`
  - Stage3 `teacher_event / teacher_event_prior` 支持按 `e_evt` 维度做显式通道加权
  - 训练/验证摘要新增：
    - `teacher_event_channel_weight_values`
    - `teacher_event_channel_weight_override_items`

## A. generation-side follow-up

### 1. `directionaltargetstatehardbox12`
- 资产：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstatehardbox_round1_1/`
  - `reports/training/streaming_student_loop_vuvbalancedgate_directionaltargetstatehardbox12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_directionaltargetstatehardbox12_round1_1/`
- 相对 `vuvbalancedgate12`，validation 变差：
  - `loss_total: 1.524679 -> 1.556115`
  - `loss_total_semantic_disabled_reference: 1.40554 -> 1.432333`
  - `loss_teacher_event: 0.441675 -> 0.467131`
  - `loss_teacher_event_prior: 0.510075 -> 0.522656`
- packet readiness 未改善：
  - 仍为 `f0=0 / vuv=1 / aper=2 / energy=3 / all_records_auto_reject=true`

### 2. `directionaltargetstaterebalancehardbox12`
- 资产：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstaterebalancehardbox_round1_1/`
  - `reports/training/streaming_student_loop_vuvbalancedgate_directionaltargetstaterebalancehardbox12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_directionaltargetstaterebalancehardbox12_round1_1/`
- 相对 `vuvbalancedgate12`，validation 进一步变差：
  - `loss_total: 1.524679 -> 1.56994`
  - `loss_total_semantic_disabled_reference: 1.40554 -> 1.443333`
  - `loss_teacher_event: 0.441675 -> 0.477447`
  - `loss_teacher_event_prior: 0.510075 -> 0.535363`
- packet readiness 仍未改善：
  - `f0=0 / vuv=1 / aper=2 / energy=3 / all_records_auto_reject=true`

## B. loss-side per-dim weighting

### 1. `evtfocus12`
- 配置：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_evtfocus_v1.json`
- 权重：
  - `0:1.2,1:1.15,2:1.15,3:0.9,4:0.85,5:1.1,7:1.15`
- 资产：
  - `reports/plans/streaming_student_supervision_vuvbalancedgate_evtfocus_round1_1/`
  - `reports/training/streaming_student_loop_vuvbalancedgate_evtfocus12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_evtfocus12_round1_1/`
- 相对 `vuvbalancedgate12`，validation 全面变好：
  - `loss_total: 1.524679 -> 1.505368`
  - `loss_total_semantic_disabled_reference: 1.40554 -> 1.389279`
  - `loss_teacher_event: 0.441675 -> 0.431132`
  - `loss_teacher_event_prior: 0.510075 -> 0.495981`
- 12-step packet 仅有极小幅数值波动，readiness 不变：
  - `f0=0 / vuv=1 / aper=2 / energy=3 / all_records_auto_reject=true`
- `target::chapter3_4_firefly_106` 的 `e_evt` 前 8 维均值从：
  - baseline12 `[0.221893, 0.216833, 0.260161, 0.673863, 0.335234, 0.234137, 0.287781, 0.264389]`
  - 变为 evtfocus12 `[0.213881, 0.208897, 0.252056, 0.657632, 0.335082, 0.227798, 0.294282, 0.255505]`
- 说明：
  - `dim3` 被压低
  - `dim6` 被抬高
  - 但 packet-facing 改善幅度不足以打开 readiness

### 2. `evtfocus24`
- 资产：
  - `reports/training/streaming_student_loop_vuvbalancedgate_evtfocus24_round1_1/`
- 最佳 checkpoint：
  - `reports/training/streaming_student_loop_vuvbalancedgate_evtfocus24_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate_evtfocus24_round1_1.step18.pt`
- 相对 `vuvbalancedgate24`，validation 仍然更好：
  - baseline24 `step24`
    - `loss_total = 0.919927`
    - `loss_total_semantic_disabled_reference = 0.832382`
    - `loss_teacher_event = 0.325852`
    - `loss_teacher_event_prior = 0.392491`
  - evtfocus24 `step24`
    - `loss_total = 0.903737`
    - `loss_total_semantic_disabled_reference = 0.819435`
    - `loss_teacher_event = 0.315265`
    - `loss_teacher_event_prior = 0.377579`
  - evtfocus24 `best step18`
    - `loss_total = 0.896387`

### 3. `evtfocus24` packet 对照
- 资产：
  - baseline24 packet
    - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate24_round1_1/`
  - evtfocus24 best packet
    - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_evtfocus24best_round1_1/`
- readiness summary：
  - baseline24：`f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
  - evtfocus24best：`f0=0 / vuv=1 / aper=3 / energy=1 / all_records_auto_reject=true`
- 三条代表记录都更差：
  - `target::chapter3_3_firefly_162`
    - `vuv_reference_mae: 0.107152 -> 0.127352`
    - `f0_proxy_reference_corr: 0.495445 -> 0.492961`
    - `f0_calibrated_log2_mae: 0.17472 -> 0.17685`
    - `aper_calibrated_reference_mae: 0.095282 -> 0.103395`
  - `target::chapter3_3_firefly_138`
    - `vuv_reference_mae: 0.207186 -> 0.226738`
    - `f0_proxy_reference_corr: 0.187293 -> 0.180436`
    - `f0_calibrated_log2_mae: 0.431756 -> 0.430857`
    - `aper_calibrated_reference_mae: 0.137007 -> 0.15062`
  - `target::chapter3_4_firefly_106`
    - `vuv_reference_mae: 0.255081 -> 0.282384`
    - `f0_proxy_reference_corr: 0.608869 -> 0.591935`
    - `f0_calibrated_log2_mae: 0.370633 -> 0.385433`
    - `aper_calibrated_reference_mae: 0.12198 -> 0.14272`
- `target::chapter3_4_firefly_106` 的 `e_evt` 前 8 维均值从：
  - baseline24 `[0.073131, 0.083895, 0.099891, 0.873734, 0.341261, 0.067271, 0.090491, 0.177699]`
  - 变为 evtfocus24best `[0.11429, 0.128388, 0.155542, 0.773086, 0.322777, 0.123117, 0.174383, 0.190914]`
- 这说明：
  - 通道加权确实把 `front-8` 几何往目标方向推了
  - 但当前推法没有转化成更好的 packet-facing 控制质量

### 4. `evtfocuslite12`
- 配置：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_evtfocuslite_v1.json`
- 权重：
  - `0:1.1,1:1.08,2:1.08,3:0.95,4:0.92,5:1.05,7:1.08`
- 资产：
  - `reports/training/streaming_student_loop_vuvbalancedgate_evtfocuslite12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_evtfocuslite12_round1_1/`
- 相对 baseline12 仍是正向，但弱于 `evtfocus12`：
  - `loss_total: 1.524679 -> 1.514739`
  - `loss_total_semantic_disabled_reference: 1.40554 -> 1.397181`
  - `loss_teacher_event: 0.441675 -> 0.436245`
  - `loss_teacher_event_prior: 0.510075 -> 0.502759`
- packet 仍然只是近似持平：
  - `f0=0 / vuv=1 / aper=2 / energy=3 / all_records_auto_reject=true`
- 因此它也不足以替换当前 reference。

## 最终判断
- 这一轮已经证明：
  - loss-side per-dim weighting 是真实可用的干预杠杆
  - 它能系统性改善 Stage3 teacher-supervised validation
  - 但“更像 target front-8 分布”并不自动等于“更好的 packet-facing readiness”
- 当前最稳妥的主线决策是：
  - 不把 `evtfocus` / `evtfocuslite` 提升为新的 packet-facing reference
  - 继续保留 `vuvbalancedgate24` 作为当前下游 handoff 参考
  - 后续若继续做 loss-side，需要把筛选标准从单纯 `loss_total` 扩展为：
    - `loss_total`
    - packet readiness
    - packet record-level numeric controls
