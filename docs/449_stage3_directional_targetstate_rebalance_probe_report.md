# 449 Stage3 directional target-state rebalance probe report

## 结论
- 本轮按 `docs/390_stage5_adapter_contract_mismatch_diagnosis_and_next_route_report.md` 的主线建议，回到 Stage3 generation-side，测试一个最小的 `event-family` 分布回正候选：
  - 新 `teacher_e_evt` bridge mode：
    - `acoustic_directional_targetstate_rebalance_v1`
- 这个候选在 teacher-label 几何上确实做到了：
  - `dim0 / dim2` 小幅抬高
  - `dim3 / dim4` 明显压低
- 但严格可比 `12-step full-validation` 没有变好：
  - baseline `vuvbalancedgate12`：
    - `loss_total = 1.524679`
    - `loss_total_semantic_disabled_reference = 1.40554`
    - `loss_teacher_event = 0.441675`
    - `loss_teacher_event_prior = 0.510075`
  - candidate `directionaltargetstaterebalance12`：
    - `loss_total = 1.538285`
    - `loss_total_semantic_disabled_reference = 1.416358`
    - `loss_teacher_event = 0.451873`
    - `loss_teacher_event_prior = 0.522537`
- downstream packet cheap screen 也没有打开新门：
  - readiness summary 仍是：
    - `f0_ready_count = 0`
    - `vuv_ready_count = 1`
    - `aper_ready_count = 2`
    - `energy_ready_count = 3`
    - `all_records_auto_reject = true`
- 因此本候选在 `12-step` 即止损：
  - 不继续拉到 `24-step`
  - 不继续送 downstream handoff

## 本轮改动
- 更新：
  - `src/v5vc/event_semantics.py`
- 新增 bridge mode：
  - `acoustic_directional_targetstate_rebalance_v1`
- 设计目标：
  - 在当前 `acoustic_directional_targetstate_bridge_v1` 基础上，
    轻度压低 `voicing / aper`
  - 同时回拉 `frication / closure / burst`
  - 不改现有 `center_weighted_boundary_progressive_final_clause_v1` timing shaping

## teacher-label 几何 smoke
- smoke 资产：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstaterebalance_smoke_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directionaltargetstaterebalance_smoke_round1_1/`
- 示例记录：
  - `target::archive_firefly_1`
- 前 5 维均值对照：
  - baseline `directionaltargetstatebridge`
    - `[0.048274, 0.035698, 0.072455, 0.890147, 0.532799]`
  - candidate `directionaltargetstaterebalance`
    - `[0.052632, 0.039553, 0.082837, 0.842933, 0.477152]`
- 解读：
  - `dim0 / dim1 / dim2` 有抬升
  - `dim3 / dim4` 被压回
  - 说明这不是 metadata-only 变更

## 全量资产与 dry-run
- 全量 teacher-label：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_directionaltargetstaterebalance_round1_1/`
  - `reports/data/round1_1_streaming_student_teacher_labels_eevt_directionaltargetstaterebalance_round1_1/`
- 关键 metadata：
  - `teacher_e_evt_bridge_mode = acoustic_directional_targetstate_rebalance_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
- supervision dry-run：
  - `reports/plans/streaming_student_supervision_vuvbalancedgate_directionaltargetstaterebalance_round1_1/streaming_student_supervision_plan.json`
- dry-run 结论：
  - 新 teacher-label index 与当前 `balanced_vuv_gate` loss family 兼容

## 严格可比 12-step
- baseline：
  - `reports/training/streaming_student_loop_vuvbalancedgate12_round1_1/`
- candidate：
  - `reports/training/streaming_student_loop_vuvbalancedgate_directionaltargetstaterebalance12_round1_1/`

### validation 结果
- baseline：
  - `loss_total = 1.524679`
  - `loss_total_semantic_disabled_reference = 1.40554`
  - `loss_teacher_event = 0.441675`
  - `loss_teacher_event_prior = 0.510075`
  - `loss_teacher_vuv_proxy = 0.449655`
- candidate：
  - `loss_total = 1.538285`
  - `loss_total_semantic_disabled_reference = 1.416358`
  - `loss_teacher_event = 0.451873`
  - `loss_teacher_event_prior = 0.522537`
  - `loss_teacher_vuv_proxy = 0.449349`

### 判断
- `vuv proxy` 单项几乎持平，
  但共享主指标和 event 主监督都回退。
- 所以这不是值得继续放大的正向信号。

## packet cheap screen
- baseline：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate12_round1_1/streaming_student_downstream_control_packet.json`
- candidate：
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_directionaltargetstaterebalance12_round1_1/streaming_student_downstream_control_packet.json`

### readiness summary
- baseline 与 candidate 都保持：
  - `f0_ready_count = 0`
  - `vuv_ready_count = 1`
  - `aper_ready_count = 2`
  - `energy_ready_count = 3`
  - `all_records_auto_reject = true`

### 代表性 record 对照
- `target::chapter3_3_firefly_162`
  - `vuv_reference_mae: 0.153024 -> 0.152754`
  - `f0_proxy_reference_corr: 0.393434 -> 0.39332`
  - `f0_calibrated_log2_mae: 0.193859 -> 0.193841`
- `target::chapter3_3_firefly_138`
  - `vuv_reference_mae: 0.249191 -> 0.249072`
  - `f0_proxy_reference_corr: 0.120738 -> 0.120739`
  - `f0_calibrated_log2_mae: 0.428793 -> 0.428805`
- `target::chapter3_4_firefly_106`
  - `vuv_reference_mae: 0.269486 -> 0.269537`
  - `aper_calibrated_reference_mae: 0.50843 -> 0.50843`
  - `f0_proxy_reference_corr: 0.495049 -> 0.495015`

### sample-3 `e_evt` 前 8 维均值
- baseline：
  - `[0.210347, 0.201778, 0.251426, 0.683908, 0.314011, 0.217408, 0.293648, 0.261507]`
- candidate：
  - `[0.21241, 0.201618, 0.254624, 0.671453, 0.301176, 0.216802, 0.292374, 0.260993]`
- delta：
  - `[+0.002063, -0.00016, +0.003198, -0.012455, -0.012835, -0.000606, -0.001273, -0.000514]`

### 解读
- 这说明当前候选只打中了：
  - `dim0 / dim2` 小幅回升
  - `dim3 / dim4` 压低
- 但：
  - `dim1` 基本没动
  - `dim5 / dim6 / dim7` 反而也略降
- 所以它没有把 `front-8` 分布一起拉向更可交接的方向，
  只是在前 5 维里做了局部重排。

## 结论与下一步
- `acoustic_directional_targetstate_rebalance_v1` 不升级为新的 Stage3 reference。
- 这条线停在 `12-step`：
  - 不做 `24-step`
  - 不做 Stage5 smoke
- 当前更准确的结论是：
  - 仅靠前 5 维 bridge 再平衡，还不足以带来 `packet-facing` 改善
  - 后续若继续做 `event-family` 分布校准，
    更值钱的方向应覆盖完整前 8 维，
    尤其不能继续放着 `dim5-7` timing side 不管
