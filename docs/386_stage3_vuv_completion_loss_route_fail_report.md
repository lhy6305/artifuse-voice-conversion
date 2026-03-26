# 386 Stage3 vuv completion loss route fail report

## 本轮目的
- 既然 calibrated audit 已把主瓶颈收紧到 `vuv`，
  就做一个唯一还值得补的最小候选：
  - 在当前 `coarse_f0_state` repaired baseline 上，
    只保留 `teacher_vuv_state`
  - 不再混入 `aper / energy` state loss

## 候选
- override：
  - `configs/streaming_student_loss_weights_vuv_completion_v1.json`
- 对照对象：
  - baseline：
    - `reports/training/streaming_student_loop_controlfamily_coarsef024_round1_1/logs/streaming_student_stage_loop_controlfamily_coarsef024_round1_1.summary.json`
    - `reports/runtime/streaming_student_downstream_control_packet_controlfamily_coarsef048_round1_2/streaming_student_downstream_control_packet.json`
  - candidate：
    - `reports/training/streaming_student_loop_vuvcompletion24_round1_1/logs/streaming_student_stage_loop_vuvcompletion24_round1_1.summary.json`
    - `reports/runtime/streaming_student_downstream_control_packet_vuvcompletion24_round1_1/streaming_student_downstream_control_packet.json`

## 结果

### 1. 共享主指标仍略差
- candidate step24 validation：
  - `loss_total = 0.939777`
  - `loss_total_semantic_disabled_reference = 0.851904`
- 对照 baseline `coarsef024`：
  - `loss_total = 0.937981`
  - `loss_total_semantic_disabled_reference = 0.8501`
- 结论：
  - 这条 `vuv-only` 候选没有拿到共享主指标优势

### 2. `vuv` 没有被打开，反而退步
- calibrated packet 对照：
  - baseline：
    - `vuv_ready_count = 1`
  - candidate：
    - `vuv_ready_count = 0`
- 关键样本：
  - `chapter3_3_firefly_162`
    - `vuv_mae = 0.157896 -> 0.190837`
    - 从过门退回不过门
  - `chapter3_3_firefly_138`
    - `0.28295 -> 0.316853`
  - `chapter3_4_firefly_106`
    - `0.292217 -> 0.343857`
- 结论：
  - `teacher_vuv_state` 这条 loss-side 最小路线没有击中当前 `vuv` 病灶

### 3. 同时还拖累了 `F0`
- `F0 proxy corr`：
  - `0.523969 / 0.202658 / 0.633974`
  - 变成
  - `0.475612 / 0.170299 / 0.5923`
- 结论：
  - 这不是“只动了 vuv，其它不受影响”
  - 它反而让当前已修到一半的 `F0` 也略回退

### 4. `aper / energy` 没有因此得到额外价值
- candidate calibrated packet：
  - `aper_ready_count = 3`
  - `energy_ready_count = 3`
- 但这些提升已经在上一轮 mixed candidate 里出现过，
  不构成继续走 `vuv-only` 路线的理由

## 判断
- `vuv-only state loss` 应正式停线。
- 到这里可以更硬地写死：
  - loss-side `named-control completion` 这整条线
    不再继续
  - 包括：
    - mixed `vuv + aper + energy`
    - `vuv-only`

## 当前含义
- 剩余问题不该继续表述成：
  - “再加一点 deterministic state loss 就能过门”
- 更准确的说法应是：
  - `vuv` 的剩余病灶不在当前这层 loss-side 权重
  - 需要转去更明确的 `vuv contract / representation / target family`

## 下一步
- 不再继续：
  - `teacher_vuv_state` 小权重 sweep
  - `vuv + aper + energy` 组合小变体
- 下一步应转去：
  - `vuv` 的 contract-side / representation-side 路线
  - 不再停留在当前 loss-side completion
